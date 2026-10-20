"""Verify frozen local parent metadata and join the streamed segmentation evidence.

Only the small reduced table is saved; the 8 GB export never reaches the Mac.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

D = Path(__file__).resolve().parent
ROOT = D.parents[4]


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    receipt = json.loads((D.parent / 'draw_receipt.json').read_text())
    config = json.loads((ROOT / 'docs/harvest/line_pipeline/clariden/full-run-config.json').read_text())
    parents = {p['id']: p for p in config['parents']}
    metadata, inputs = {}, []
    for wave in ('W1', 'W2'):
        p = ROOT.parent / f'collect-v3-data/snapshots/{wave}_features_20261018_0524.jsonl'
        parent = f'collect-v3-{wave}-20261018-0524'
        h, n = hashlib.sha256(), 0
        with p.open('rb') as f:
            for line in f:
                h.update(line)
                m = json.loads(line)
                text = next(m[k] for k in ('old_label', 'text', 'label') if isinstance(m.get(k), str))
                crop = m['crop']
                for old, new in parents[parent]['path_map'].items():
                    if crop.startswith(old + '/'):
                        crop = new + crop[len(old):]
                key = parent, m['id']
                assert key not in metadata
                metadata[key] = dict(source=m['source'], primary_class=m['primary_class'],
                                     script_class=m['script_class'], wave=wave, raw_text=text,
                                     remote_crop=crop, parent_crop_sha256=m['crop_sha256'])
                n += 1
        assert h.hexdigest() == parents[parent]['sha256'] and n == parents[parent]['rows']
        inputs.append(dict(path=str(p), sha256=h.hexdigest(), rows=n))
    p = D.parent / 'keys/original_metadata.jsonl.gz'
    with gzip.open(p, 'rt') as f:
        for line in f:
            m = json.loads(line)
            if '_parent_receipt' in m:
                rec = m['_parent_receipt']
                expected = next(x for x in config['parents'] if x['path'] == rec['path'])
                assert rec['sha256'] == expected['sha256'] and rec['rows'] == expected['rows']
                inputs.append(rec)
                continue
            metadata[m['parent_id'], m['id']] = dict(
                source=m['source'], primary_class=m.get('primary_class', m['script_class']),
                script_class=m['script_class'], wave=m['wave'], raw_text=m['label'],
                remote_crop=m['remote_crop'], parent_crop_sha256=m.get('crop_sha256'))
    assert len(metadata) == 592466
    inputs.append(dict(path=str(p), sha256=sha(p), note='Frozen prior read-only metadata export; raw text individually rebound below'))
    print('Verified parent metadata: 592466 rows', flush=True)
    target = D / 'population_cells.jsonl.gz'
    temporary = target.with_suffix('.gz.tmp')
    with (D / 'ssh_export.stderr').open('wb') as err:
        process = subprocess.Popen(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                                    'clariden', 'python3 -B -'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=err)
        process.stdin.write((D / 'export_remote.py').read_bytes())
        process.stdin.close()
        count = 0
        with gzip.GzipFile(fileobj=process.stdout) as raw, io.TextIOWrapper(raw) as stream, \
                gzip.GzipFile(filename=str(temporary), mode='wb', mtime=0, compresslevel=6) as out:
            for line in stream:
                r = json.loads(line)
                if '_provenance' in r:
                    provenance = r['_provenance']
                    assert provenance['current'] == receipt['source']['current']
                    assert provenance['resolved_export'] == receipt['source']['resolved_export']
                elif '_receipt' in r:
                    export_receipt = r['_receipt']
                    for k, v in receipt['export_receipt'].items():
                        assert export_receipt[k] == v, (k, export_receipt[k], v)
                else:
                    m = metadata.pop((r['parent_id'], r['row_id']))
                    assert hashlib.sha256(m['raw_text'].encode()).hexdigest() == r['raw_text_sha256'], r['row_id']
                    if m['parent_crop_sha256']:
                        assert m['parent_crop_sha256'] == r['crop_sha256']
                    del m['parent_crop_sha256']
                    r.update(m)
                    r['text_characters'] = len(r['raw_text'].strip())
                    out.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n').encode())
                    count += 1
                    if count % 100000 == 0:
                        print(f'Reduced {count}/592466', flush=True)
        assert process.wait(timeout=30) == 0
    assert count == 592466 and not metadata and export_receipt['rows'] == count
    temporary.replace(target)
    (D / 'export_receipt.json').write_text(json.dumps(dict(
        provenance=provenance, export_receipt=export_receipt, metadata_inputs=inputs,
        reduced_rows=count, reduced_sha256=sha(target), reduced_bytes=target.stat().st_size,
        all_raw_text_hashes_verified=True, parent_crop_hashes_verified_where_present=True,
        remote_read_only=True, remote_command='ssh clariden python3 -B - < cells/export_remote.py'), indent=2) + '\n')
    print('Verified immutable export and saved reduced population', flush=True)


if __name__ == '__main__':
    main()
