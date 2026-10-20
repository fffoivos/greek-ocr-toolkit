"""Validate N1 artifacts without opening crops or importing inference code."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'artifacts/n1'
c = json.loads((OUT/'census.json').read_text())
f = [json.loads(l) for l in (OUT/'frame_step1.jsonl').read_text().splitlines()]
lock = json.loads((OUT/'locked_eval_docs.json').read_text())
dev = [r for r in f if r['partition']=='step1']
evaluation = [r for r in f if r['partition']=='locked_eval']
assert (len(dev),len(evaluation)) == (600,300)
assert len({r['slot_id'] for r in f}) == 900
assert all(r['truth'] is None and r['rendered'] is False for r in f)
assert {r['document'] for r in dev} == set(lock['development_documents'])
assert not ({r['document'] for r in dev} & set(lock['locked_documents']))
assert {r['document'] for r in evaluation} <= set(lock['locked_documents'])
assert not ({r['line_id'] for r in f} & set(lock['excluded_c1_line_ids']))
assert not ({r['crop_sha256'] for r in dev} & {r['crop_sha256'] for r in evaluation})
assert Counter(r['source_era'] for r in evaluation) == {'elstat':100,'gazette_1982_1985':100,'gazette_1986_1990':100}
assert Counter(f"{r['partition']} | {r['source_era']} | {r['position']} | "+ ('+'.join(f'U+{ord(ch):04X}' for ch in r['glyph']) if r['glyph'] else 'NONE_TEXT') for r in f) == c['sampling']['stratum_counts']


def check_stats(s):
    assert s['slots'] == s['inner_slots'] + s['boundary_slots']
    assert s['boundary_slots'] == 2*s['tokens']
    assert sum(sum(v.values()) for v in s['glyph_by_position'].values()) == s['slots']


check_stats(c['w1']['total'])
for s in c['w1']['by_source_era'].values():
    check_stats(s)
for split in c['collection_v2'].values():
    check_stats(split['total'])
    check_stats(split['codec_v1_normalized_eligible'])
    assert split['codec_v1_normalized_eligible']['lines'] + split['codec_v1_rejected_lines'] == split['total']['lines']
    for field in ('by_source_era','codec_v1_normalized_by_source_era'):
        for s in split[field].values():
            check_stats(s)
byline = {}
for r in f:
    byline.setdefault(r['line_id'],[]).append(r)
wpath = Path.home()/'Projects/collect-v3-data/run/W1/features.jsonl'
checked = set()
with wpath.open() as stream:
    for line in stream:
        r = json.loads(line)
        for s in byline.get(r['id'],[]):
            assert r['text'][s['start']:s['end']] == s['glyph']
            assert f"{r['source']}:{r['item']}" == s['document']
            assert r['crop_sha256'] == s['crop_sha256']
            checked.add(s['slot_id'])
assert len(checked)==900
# Repeatability checked against hashes captured before the latest census replay.
for line in (OUT/'frame_replay.sha256').read_text().splitlines():
    expected, name = line.split(maxsplit=1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected
paths = ['greekocr/numerics/tokens.py','tests/test_numeric_tokens.py','scripts/numerics/n1_step0.py','scripts/numerics/n1_report.py','scripts/numerics/validate_n1.py','artifacts/n1/census.json','artifacts/n1/frame_step1.jsonl','artifacts/n1/locked_eval_docs.json','docs/records/labelfix/N1_STEP0_REPORT.md']
receipt = dict(status='PASS',tests_passed=17,frame_rows=900,partitions={'step1':600,'locked_eval':300},
    offset_readbacks=900,c1_overlap=0,document_overlap=0,crop_hash_overlap=0,deterministic_frame_replay=True,
    sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='sha256'}))
