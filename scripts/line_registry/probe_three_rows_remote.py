"""Read-only Clariden probe, run via SSH stdin; three keys, no jobs or writes."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
A = W/'census_06_20261020/attempts/full-split-002'
KEYS = [
    ('collect-v3-W1-20261018-0524', 'bsb_poly1850--027215cc6d2a7e8a--s000-l0001'),
    ('collect-v3-W2-20261018-0524', 'bsb_poly1850--91657e0569fe07c8--s014-l0001'),
    ('collection-v2-train', '66112e132fd96ac8e30e5328-p000016-l0004')]
before = (A/'CURRENT.json').read_bytes()
cur = json.loads(before)
db = sqlite3.connect(f'file:{A}/ledger.sqlite?mode=ro', uri=True, timeout=8)
db.execute('PRAGMA query_only=ON')
db.execute('BEGIN')
generation = db.execute("select value from run where key='generation'").fetchone()[0]
assert int(generation) == cur['generation'] == 2
rows = []
for parent, rid in KEYS:
    obs = db.execute('select payload,split,edition,page from observations where parent=? and id=?', (parent, rid)).fetchall()
    assert len(obs) == 1
    encoded, split, edition, page = obs[0]
    p = json.loads(encoded)
    disp, decision = db.execute('select disposition,payload from decisions where parent=? and id=?', (parent,rid)).fetchone()
    d = json.loads(decision)
    assert d['run_binding_sha256'] == cur['run_binding_sha256']
    if parent.startswith('collect-v3'):
        wave = parent.split('-')[2].lower()
        crop = W/f'collection_{wave}_originals'/p['source']/f'{rid}.png'
    else:
        crop = Path(p['crop_path'])
    b = crop.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    assert sha == p['crop_sha256']
    legacy = None
    if parent == 'collection-v2-train':
        records = W/'greek-ocr-toolkit/docs/harvest/round1/records_all.jsonl'
        with records.open() as f:
            for i, line in enumerate(f, 1):
                if i > 600:
                    break
                record = json.loads(line)
                if record['id'] == rid:
                    legacy = dict(record=record,path=str(records),line=i,
                                  record_sha256=hashlib.sha256(line.encode()).hexdigest())
                    break
        assert legacy is not None
    rows.append(dict(parent_id=parent,row_id=rid,split=split,edition_id=edition,page_id=page,
        observation=p,observation_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
        disposition=disp,decision=d,decision_sha256=hashlib.sha256(decision.encode()).hexdigest(),
        crop=dict(path=str(crop),bytes=len(b),sha256=sha),legacy=legacy))
db.rollback()
db.close()
assert (A/'CURRENT.json').read_bytes() == before
print(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),host=os.uname().nodename,
    scope='three indexed g2 observations/decisions and exact existing crop bytes; no jobs/writes',
    current=cur,current_sha256=hashlib.sha256(before).hexdigest(),rows=rows),ensure_ascii=False))
