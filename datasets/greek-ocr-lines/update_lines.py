#!/usr/bin/env python3
"""Correct the transcription of real lines in fffoivos/greek-ocr-lines without re-uploading images.

Text and image of a line live in the same parquet shard. This tool rewrites only the shards that hold a
corrected line, and only their text columns (gt_nfc, gt_nfd, label_ids). Every other column, the images
included, stays byte-for-byte the same: before editing, each shard must re-encode to exactly its original
bytes with the same writer settings, and after editing every untouched cell is compared. Because the
images are unchanged, Xet storage deduplicates them and the upload is roughly the changed text, not the
shard (see README.md, "Updating").

Input: JSONL, one object per correction:
  {"line_id": "...", "old": "<current gt_nfc>", "new": "<corrected text>", "reason": "..."}
`old` is a guard: the edit is refused if the line no longer has that text.

  python update_lines.py corrections.jsonl --work DIR            # prepare + verify, no upload
  HF_TOKEN=... python update_lines.py corrections.jsonl --work DIR --commit [--tag v0.6]

Prepared shards and the new CORRECTIONS.jsonl are written under DIR/out. With --commit, one commit is made
on main with parent = the revision read at start (it fails if main moved), then read back.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

REPO = 'fffoivos/greek-ocr-lines'
CODEC = Path(__file__).resolve().parents[2] / 'greekocr' / 'train' / 'codec' / 'v2.1.json'
TEXT_COLS = ('gt_nfc', 'gt_nfd', 'label_ids')
WS = re.compile(r'\s+')


def load_codec(path=CODEC):
    c = json.loads(Path(path).read_text(encoding='utf-8'))
    return c['version'], {a['ch']: a['id'] for a in c['atoms']}


def encode(text, atoms):
    """Codec v2.1 policy: NFD, whitespace runs -> one space, one id per code point; unknown code point -> error."""
    nfd = WS.sub(' ', unicodedata.normalize('NFD', text)).strip()
    missing = sorted({ch for ch in nfd if ch not in atoms})
    if missing:
        raise ValueError('not in codec v2.1: ' + ', '.join(f'U+{ord(c):04X}' for c in missing))
    return unicodedata.normalize('NFC', nfd), nfd, [atoms[ch] for ch in nfd]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def write_like(table, src_md, out):
    """Same writer settings the release used (pyarrow, zstd, the shard's row-group size)."""
    import pyarrow.parquet as pq
    pq.write_table(table, out, compression='zstd', row_group_size=src_md.row_group(0).num_rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('corrections')
    ap.add_argument('--work', required=True)
    ap.add_argument('--repo', default=REPO)
    ap.add_argument('--revision', default='main')
    ap.add_argument('--commit', action='store_true', help='upload (needs HF_TOKEN)')
    ap.add_argument('--tag', help='tag the new commit, e.g. v0.6')
    a = ap.parse_args(argv)

    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem, hf_hub_download

    token = os.environ.get('HF_TOKEN') if a.commit else None
    if a.commit and not token:
        raise SystemExit('--commit needs HF_TOKEN in the environment')
    api, fs = HfApi(token=token), HfFileSystem(token=token)
    work, out = Path(a.work), Path(a.work) / 'out'
    out.mkdir(parents=True, exist_ok=True)
    parent = api.repo_info(a.repo, repo_type='dataset', revision=a.revision).sha
    print(f'parent {parent}', flush=True)

    edits = [json.loads(l) for l in Path(a.corrections).read_text(encoding='utf-8').splitlines() if l.strip()]
    ids = [e['line_id'] for e in edits]
    dup = [k for k, n in collections.Counter(ids).items() if n > 1]
    if dup:
        raise SystemExit(f'duplicate line_id in corrections: {dup[:5]}')
    codec_version, atoms = load_codec()

    # line_id -> split from the metadata table; real lines only (a synthetic image is rendered from its text:
    # fix the generator, not the label).
    meta = pq.read_table(hf_hub_download(a.repo, 'metadata/real_lines.parquet', repo_type='dataset',
                                         revision=parent, local_dir=work / 'dl'), columns=['line_id', 'split'])
    split_of = dict(zip(meta['line_id'].to_pylist(), meta['split'].to_pylist()))
    unknown = [i for i in ids if i not in split_of]
    if unknown:
        raise SystemExit(f'not a real line_id in {a.repo}@{parent[:12]}: {unknown[:5]}')

    # Find the shard of each line by reading only the line_id column of that split's shards.
    want = collections.defaultdict(set)
    for i in ids:
        want[split_of[i]].add(i)
    shard_of = {}
    for split, need in sorted(want.items()):
        for f in sorted(fs.ls(f'datasets/{a.repo}@{parent}/data/real/{split}', detail=False)):
            with fs.open(f) as fh:
                hit = need.intersection(pq.read_table(fh, columns=['line_id'])['line_id'].to_pylist())
            for i in hit:
                shard_of[i] = f.split(f'@{parent}/', 1)[1]
            need -= hit
            if not need:
                break
        if need:
            raise SystemExit(f'line_ids not found in data/real/{split}: {sorted(need)[:5]}')

    by_shard = collections.defaultdict(list)
    for e in edits:
        by_shard[shard_of[e['line_id']]].append(e)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    log, uploads = [], {}
    for shard, es in sorted(by_shard.items()):
        src = Path(hf_hub_download(a.repo, shard, repo_type='dataset', revision=parent, local_dir=work / 'dl'))
        md = pq.ParquetFile(src).metadata
        t = pq.read_table(src)
        probe = out / 'probe.parquet'
        write_like(t, md, probe)
        if sha256(probe) != sha256(src):
            raise SystemExit(f'{shard}: does not re-encode byte-identically with this pyarrow '
                             f'({pa.__version__}; shard written by {md.created_by}); use that version')
        probe.unlink()
        row = {v: k for k, v in enumerate(t['line_id'].to_pylist())}
        cols = {c: t[c].to_pylist() for c in TEXT_COLS}
        for e in es:
            r = row[e['line_id']]
            if cols['gt_nfc'][r] != e['old']:
                raise SystemExit(f"{e['line_id']}: current text {cols['gt_nfc'][r]!r} != old {e['old']!r}")
            if t['codec_version'][r].as_py() != codec_version:
                raise SystemExit(f"{e['line_id']}: codec {t['codec_version'][r].as_py()} != {codec_version}")
            nfc, nfd, lab = encode(e['new'], atoms)
            if nfd == cols['gt_nfd'][r]:
                raise SystemExit(f"{e['line_id']}: no change after normalisation")
            cols['gt_nfc'][r], cols['gt_nfd'][r], cols['label_ids'][r] = nfc, nfd, lab
            log.append({'line_id': e['line_id'], 'split': split_of[e['line_id']], 'shard': shard,
                        'old_gt_nfc': e['old'], 'new_gt_nfc': nfc, 'reason': e.get('reason'),
                        'date_utc': now, 'parent_commit': parent})
        for c in TEXT_COLS:
            t = t.set_column(t.schema.get_field_index(c), t.schema.field(c), pa.array(cols[c], t.schema.field(c).type))
        dst = out / shard
        dst.parent.mkdir(parents=True, exist_ok=True)
        write_like(t, md, dst)
        # Verify: every non-text column equal; text columns differ exactly on the edited rows.
        old, new = pq.read_table(src), pq.read_table(dst)
        assert old.schema.equals(new.schema, check_metadata=True) and old.num_rows == new.num_rows
        for c in old.column_names:
            if c not in TEXT_COLS:
                assert old[c].equals(new[c]), f'{shard}: column {c} changed'
        edited = {row[e['line_id']] for e in es}
        for c in TEXT_COLS:
            diff = set(pc.indices_nonzero(pc.invert(pc.equal(old[c], new[c]) if c != 'label_ids'
                       else pa.array([x == y for x, y in zip(old[c].to_pylist(), new[c].to_pylist())]))).to_pylist())
            assert diff <= edited, f'{shard}: {c} changed on unedited rows'
        uploads[shard] = dst
        print(f'{shard}: {len(es)} line(s) corrected, {dst.stat().st_size:,} B', flush=True)

    # The correction log on the Hub is append-only.
    try:
        prev = Path(hf_hub_download(a.repo, 'CORRECTIONS.jsonl', repo_type='dataset', revision=parent,
                                    local_dir=work / 'dl')).read_text(encoding='utf-8')
    except Exception as ex:  # first correction
        if 'EntryNotFound' not in type(ex).__name__ and '404' not in str(ex):
            raise
        prev = ''
    clog = out / 'CORRECTIONS.jsonl'
    clog.write_text(prev + ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in log), encoding='utf-8')
    print(json.dumps({'parent': parent, 'lines': len(log), 'shards': len(uploads)}), flush=True)
    if not a.commit:
        print(f'prepared under {out}; re-run with --commit to upload')
        return

    from huggingface_hub import CommitOperationAdd
    ops = [CommitOperationAdd(path_in_repo=p, path_or_fileobj=str(f)) for p, f in sorted(uploads.items())]
    ops.append(CommitOperationAdd(path_in_repo='CORRECTIONS.jsonl', path_or_fileobj=str(clog)))
    before = {e.path: e.blob_id for e in api.list_repo_tree(a.repo, repo_type='dataset', revision=parent,
                                                           recursive=True) if getattr(e, 'blob_id', None)}
    info = api.create_commit(a.repo, repo_type='dataset', operations=ops, parent_commit=parent,
                             commit_message=f'Correct {len(log)} line transcription(s) in {len(uploads)} shard(s)')
    after = {e.path: e for e in api.list_repo_tree(a.repo, repo_type='dataset', revision=info.oid,
                                                   recursive=True) if getattr(e, 'blob_id', None)}
    for p, f in uploads.items():
        assert after[p].lfs.sha256 == sha256(f), f'readback: {p} differs'
    changed = {p for p in after if before.get(p) != after[p].blob_id}
    assert changed <= set(uploads) | {'CORRECTIONS.jsonl'} and set(before) <= set(after), 'readback: unexpected paths'
    print(json.dumps({'commit': info.oid, 'readback': 'PASS'}))
    if a.tag:
        api.create_tag(a.repo, repo_type='dataset', tag=a.tag, revision=info.oid)
        assert api.repo_info(a.repo, repo_type='dataset', revision=a.tag).sha == info.oid
        print(f'tagged {a.tag}')


if __name__ == '__main__':
    sys.exit(main())
