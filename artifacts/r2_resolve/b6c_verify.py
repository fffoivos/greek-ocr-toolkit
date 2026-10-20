"""Read-only output validation, after r2_finalize_manifest.py completes."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from scripts.labelfix import r2_cards_resolve as R
from scripts.labelfix.r2_finalize_manifest import ROOT, leakage_check

base=ROOT/'artifacts/r2a_manifest'
receipt=json.loads((base/'receipt.json').read_text())
rows=R.read(base/'r2a_slots.jsonl')
assert hashlib.sha256((base/'r2a_slots.jsonl').read_bytes()).hexdigest()==receipt['manifest_sha256']
ids=[tuple(r['slot_id']) for r in rows]
assert len(ids)==len(set(ids))==receipt['slots']<=4000
assert len(R.read(base/'quarantined.jsonl'))==receipt['quarantined']
assert len(R.read(base/'excluded.jsonl'))==receipt['excluded']
roles=json.loads((ROOT/'docs/labelfix/spellcheck/R2/doc_roles.json').read_text())['documents']
witness={r['doc'] for r in R.read(ROOT/'docs/labelfix/spellcheck/R2/decks/T4/private/key.jsonl')}
assert leakage_check(rows,roles,witness)==0
pages=defaultdict(set)
for r in rows:
    assert r['provenance']=='native_print' and r['loss_weight']==1 and r['role']=='train'
    assert r['unknown']==[] and len(r['targets'])==4
    assert all(type(v) is int and 0<=v<n for v,n in zip(r['targets'],[3,4,2,2]))
    assert r['pool']=='native' and 'replaces' not in r
    assert len(r['slot_id'][0])==64 and type(r['slot_id'][1]) is int and r['slot_id'][1]>=0
    pages[(r['doc'],r['page'])].add(r['card_id'])
assert max(map(len,pages.values()))<=5
for sl,table in receipt['slices'].items():
    rr=[r for r in rows if r['slice']==sl]
    assert max(Counter(r['doc'] for r in rr).values(),default=0)*10<=len(rr)
    assert sum(r['polarity']=='negative' for r in rr)==table['negative']
    assert sum(r['polarity']=='positive' for r in rr)==table['positive']
for t in ('T2','T4'):
    b=ROOT/'artifacts/r2_resolve'/t/'final'
    yes,no=R.read(b/'resolved.jsonl'),R.read(b/'unresolved.jsonl')
    assert len(yes)+len(no)==800
    assert len({r['card_id'] for r in yes+no})==800
    assert all(r['status']=='resolved' and r['control'] is False for r in yes)
    assert all(r['status']=='unresolved' and r['control'] is False for r in no)
    g=json.loads((b/'gate.json').read_text())
    assert g['all_passed'] and all(v['control_errors']<=1 for v in g['per_folder'].values())
    for filename,digest in g['input_sha256'].items():
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest
assert (ROOT/'docs/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md').read_text().splitlines()[-1].endswith(receipt['manifest_sha256'][:12])
print('PASS: output partitions, schema, unique keys, hash readback, document/page caps, replacement/new semantics, roles/leakage and report binding')
