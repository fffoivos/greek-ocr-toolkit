"""Independent S8a6 normalization/estimand examples and evidence reaggregation."""
from greekocr.ops.data_root import input_path as _data_input
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
from scripts.labelfix import s8_score_truth as s

assert all(s.canonical('τ'+a) == s.canonical('τ’') for a in s.ELISION)
assert s.canonical('᾿Α') == s.canonical('Ἀ') and s.canonical('᾿Ά') == s.canonical('Ἄ')
assert s.canonical('ἄ') != s.canonical('ἂ') and s.canonical('τ’') != s.canonical('τ')
assert s.canonical('αʹ') != s.canonical('α’') and s.canonical('α΄') != s.canonical('α’')

def score(t, p, serial=None):
    r = dict(id='audit', truth=s.canonical(t), forms={'r1_A': p, 'detector_original': p})
    return s.score_presence(r, 'r1_A' if serial is None else 'detector_original', serial)[0]['counts']

a = score('άα', 'αά')
assert a['any']['TP'] == 0 and a['any']['FP'] == a['any']['FN'] == 1
assert score('πά', 'π')['any']['FN'] == 1 and score('π', 'πά')['any']['FP'] == 1
b = score('ἄ', 'α', [dict(base='α', evidence=dict(above=[dict(area=1)], below=[]))])
assert b['any']['TP'] == 1 and b['emitted_any']['FN'] == b['breathing']['FN'] == 1
h = [dict(weight=1, line_id='d1-p1', v=1), dict(weight=3, line_id='d2-p1', v=0)]
e = s.estimate(h, lambda r: r['v'], lambda r: 1, 42)
assert e['value'] == .25 and math.isclose(e['effective_event_n'], 1.6)
f = s.DEV/'evidence/dev_truth.jsonl.gz'
rr = [json.loads(x) for x in gzip.decompress(_data_input(f).read_bytes()).splitlines()]
meta, summary, data = rr[0], rr[-1], rr[1:-1]
assert len(data) == len({r['id'] for r in data}) == 1793
assert meta['protected_files_sha256'] == s.frozen()
assert all(hashlib.sha256((s.ROOT/p).read_bytes()).hexdigest() == digest for p, digest in meta['input_sha256'].items())
assert meta['script_sha256'] == s.sha(s.__file__)
assert meta['audit_sha256'] == s.sha(__file__)
assert s.sha(f) in s.REPORT.read_text() and s.REPORT.read_text().splitlines()[-1].startswith('S8 DEV TRUTH: adjudicated 978')
assert collections.Counter(r['status'] for r in data) == dict(resolved=976, UNKNOWN=2, control=84, excluded_control_construction_defect=1, unadjudicated=730)
assert sum(r['status'] == 'unadjudicated' and not r['control'] for r in data) == 671
assert all('word_correct' not in r and 'presence' not in r for r in data if r['status'] != 'resolved')
for w, ws in summary['waves'].items():
    known = [r for r in data if r['wave'] == w and r['status'] == 'resolved']
    den = sum(r['weight'] for r in known)
    for source in s.SOURCES:
        num = sum(r['weight']*r['word_correct'][source] for r in known)
        assert math.isclose(num/den, ws['word_accuracy']['all'][source]['value'])
    for source in ('detector_original', 'r1_A'):
        for family in s.KINDS:
            c = collections.Counter()
            for r in known:
                for slot in r['presence'][source]['slots']:
                    t, p = slot['truth_presence'][family], slot['prediction_presence'][family]
                    c['TP' if t and p else 'FP' if p else 'FN' if t else 'TN'] += r['weight']
            saved = ws['presence'][source][family]
            assert all(math.isclose(c[k], saved['counts'][k]['weighted'], abs_tol=1e-8) for k in ('TP', 'FP', 'FN', 'TN'))
    for failure in ws['failures'][:3]:
        assert len(failure['examples']) >= 3 and all(any(r['id'] == k for r in known) for k in failure['examples'][:3])
print('PASS: normalization, gaps/shifts, physical versus named presence, weighted ratio, 1793 states, 80 presence cells, all hashes, ranked examples')
