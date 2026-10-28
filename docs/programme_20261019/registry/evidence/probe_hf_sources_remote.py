"""Read-only, bounded HF specification probe. Execute via SSH stdin, no jobs.

Only one book is queried in SQLite using the existing parent/source/book index.
Directory stat walks stop after eight seconds each; incomplete totals are labelled.
No source content is changed, no image payload is returned, no token is used.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import struct
import time
from datetime import datetime, timezone

W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
A = W/'census_06_20261020/attempts/full-split-002'
BOOK = 'bsb_poly1850--027215cc6d2a7e8a'
out = dict(at=datetime.now(timezone.utc).isoformat(), host=os.uname().nodename,
           scope='one indexed book; one 173 MB release scan; bounded stat walks; no jobs/writes',
           book_id=BOOK, files=[], trees=[], listings=[], book_rows=[])


def object_info(p, hash_bytes=False):
    p = Path(p)
    r = dict(path=str(p), exists=p.is_file())
    if r['exists']:
        r.update(bytes=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns)
        if hash_bytes:
            r['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
    return r


def tree(p, seconds=8):
    start = time.monotonic()
    r = dict(path=str(p), exists=p.is_dir(), files=0, bytes=0, complete=True,
             basis='logical regular-file sizes; no content hashes; symlinks excluded')
    for root, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if not (Path(root)/d).is_symlink()]
        for name in files:
            q = Path(root)/name
            if q.is_symlink():
                continue
            r['files'] += 1
            r['bytes'] += q.stat().st_size
            if time.monotonic()-start > seconds:
                r['complete'] = False
                break
        if not r['complete']:
            break
    r['seconds'] = time.monotonic()-start
    out['trees'].append(r)


before = (A/'CURRENT.json').read_bytes()
out['current'] = json.loads(before)
out['current_sha256'] = hashlib.sha256(before).hexdigest()
db = sqlite3.connect(f'file:{A}/ledger.sqlite?mode=ro', uri=True)
db.execute('PRAGMA query_only=ON')
db.execute('BEGIN')
out['ledger_generation'] = db.execute("select value from run where key='generation'").fetchone()[0]
query = 'select id,payload,split,edition from observations where parent=? and source=? and book=?'
out['query_plan'] = list(db.execute('EXPLAIN QUERY PLAN '+query, ('collect-v3-W1-20261018-0524','bsb_poly1850',BOOK)))
for wave in ('W1', 'W2'):
    parent = f'collect-v3-{wave}-20261018-0524'
    for rid, payload, split, edition in db.execute(query, (parent, 'bsb_poly1850', BOOK)):
        p = json.loads(payload)
        disp, encoded = db.execute('select disposition,payload from decisions where parent=? and id=?', (parent,rid)).fetchone()
        d = json.loads(encoded)
        assert d['run_binding_sha256'] == out['current']['run_binding_sha256']
        crop = W/f'collection_{wave.lower()}_originals'/p['source']/f'{rid}.png'
        c = object_info(crop, True)
        if c['exists']:
            assert c['sha256'] == p['crop_sha256'], (rid, 'crop mismatch')
            with crop.open('rb') as f:
                head = f.read(24)
            assert head[:8] == b'\x89PNG\r\n\x1a\n'
            c['dimensions'] = list(struct.unpack('>II', head[16:24]))
        out['book_rows'].append(dict(parent_id=parent, row_id=rid, split=split, edition_id=edition,
            page_id=p['page_id'], source=p['source'], book_id=p['book_id'],
            primary_class=p.get('primary_class'), raw_text=p['raw_text'], raw_text_field=p.get('raw_text_field'),
            crop_sha256=p['crop_sha256'], bbox=p['bbox'], crop_bbox=p['crop_bbox'],
            docai_line_index=p['docai_line_index'], google_line_contributors=p.get('google_line_contributors'),
            disposition=disp, reasons=d['reasons'], final_text=d['final_text'], edits=d.get('edits'),
            normalization=d.get('normalization'), routes={k:v.get('status') for k,v in d.get('routes',{}).items()},
            decision_sha256=hashlib.sha256(encoded.encode()).hexdigest(), crop=c))
db.rollback()
db.close()
assert (A/'CURRENT.json').read_bytes() == before
assert int(out['ledger_generation']) == out['current']['generation'] == 2
out['ledger_custody'] = 'live read-only transaction, g2 binding and unchanged CURRENT; not immutable-export proof'
keys = {(r['parent_id'],r['row_id']) for r in out['book_rows']}
release = W/'release_v4/rel4_c06_full_01/release_v4_admission.jsonl'
out['book_release_rows'] = []
h = hashlib.sha256(); count = 0
with release.open('rb') as f:
    for line in f:
        h.update(line); count += 1
        if BOOK.encode() not in line:
            continue
        r = json.loads(line)
        if (r['parent_id'],r['row_id']) in keys:
            out['book_release_rows'].append(r)
out['release_v4'] = dict(path=str(release), bytes=release.stat().st_size, rows=count, sha256=h.hexdigest())
out['release_v4_sf7_book'] = []
p = release.parent/'release_v4_sf7_edits.jsonl'
for line in p.open():
    if BOOK in line:
        out['release_v4_sf7_book'].append(json.loads(line))
for p in [A/'CURRENT.json', release.parent/'RELEASE_V4_RECEIPT.json', release.parent/'corrections_registry.json',
          W/'crops4_attempts/crops4_c06_full_01/upload_receipt.json',
          W/'benchmark_0.2/seal04/SEAL_RECEIPT.json',W/'benchmark_0.2/seal04/suite.json']:
    r = object_info(p, True)
    if p.exists(): r['content'] = json.loads(p.read_text())
    out['files'].append(r)
for p in [W/'greek-page-ocr/out/e1_run4/synthetic', W/'greek-page-ocr/out/e4/wave1b/v2-codec/old_v2/synthetic',
          W/'collection_v2/crops', W/'benchmark_0.2/seal04/images']:
    tree(p)
    if (p/'build_info.json').exists():
        r = object_info(p/'build_info.json', True); r['content'] = json.loads((p/'build_info.json').read_text());out['files'].append(r)
P = Path('/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code')
for p in [P/'out/e4/wave2_prep/inventory04', P/'out/e4/task2_ctrl_corr04']:
    tree(p)
for p in [P/'out/e4/wave2_prep/PREPARED.json',P/'out/e4/wave2_prep/INPUTS.bound.v4.seal04.json',P/'out/e4/wave2_prep/inventory04/ctrl_mix.json']:
    r=object_info(p,True)
    if p.exists():r['content']=json.loads(p.read_text())
    out['files'].append(r)
for p in [P/'out/e4/wave2_prep', W/'e4_wave2_rel3_20261020/preparation']:
    out['listings'].append(dict(path=str(p),exists=p.exists(),entries=[dict(name=x.name,dir=x.is_dir(),bytes=x.stat().st_size) for x in sorted(p.iterdir())] if p.is_dir() else []))
out['book_counts'] = dict(rows=len(out['book_rows']),status=dict(collections.Counter(r['disposition'] for r in out['book_rows'])),
                         crop_bytes=sum(r['crop'].get('bytes',0) for r in out['book_rows']),release_rows=len(out['book_release_rows']),
                         missing_crops_by_status=dict(collections.Counter(r['disposition'] for r in out['book_rows'] if not r['crop']['exists'])))
print(json.dumps(out, ensure_ascii=False))
