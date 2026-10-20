"""Verify SEGEVAL-2 evidence without new reads or network access."""
import hashlib
import importlib.util
import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def rows(p): return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
spec=importlib.util.spec_from_file_location('score',D/'segeval1_score.py');score=importlib.util.module_from_spec(spec);spec.loader.exec_module(score)
s=load(D/'scored/summary.json');old=load(D/'scored/v4.4/summary.json');rr=rows(D/'scored/owner_rows.jsonl')
seal=rows(D/'keys/sealed_decisions.jsonl');assert {r['line_id'] for r in rr}=={r['row_id'] for r in seal};assert len(rr)==150
assert sha(D/'keys/sealed_decisions.jsonl')==s['seal_sha256']==load(D/'draw_receipt.json')['seal_sha256']
metrics=['study_counts','false_positives','false_positives_by_reason','false_negatives','false_negatives_by_rubric','unresolved','controls']
assert all(s[k]==old[k] for k in metrics)
assert (s['false_positives'],s['false_positives_denominator'],s['false_negatives'],s['false_negatives_denominator'])==(29,50,5,100)
assert s['controls_valid'] and len(s['controls'])==10 and all(c['passed'] for c in s['controls'])
assert sum(v['false_positives'] for k,v in s['false_positives_by_reason'].items() if 'OCR output' in k)==27
assert sum(v['drawn'] for k,v in s['false_positives_by_reason'].items() if 'OCR output' in k)==43
readers={}
for bed in ('segeval1_a','segeval1_b'):
 scan_path=D/f'scan/v4.5.5/{bed}/r1.scan.json';c=load(scan_path.parent/'r1.custody.json');scan=load(scan_path)
 verdict=score.validate_scan(scan,scan_path,D/f'answers/{bed}/r1.jsonl')
 assert s['scan_verdicts'][bed]==verdict
 assert sha(D/f'scan/{bed}/r1.scan.json')==c['previous_scans'][0]['scan_sha256']
 assert sha(D/'pack_closure.json')==c['pack_closure_sha256']
 for name,h in c['scanner_dependencies'].items():assert sha(Path(c['scanner']).parent/name)==h
 for row in rr:
  if row['context']==bed:assert row['scan_verdict']=='VALID' and row['scan_custody']==verdict
 context=next(json.loads(l)['payload'] for l in Path(c['rollout']).read_text().splitlines() if json.loads(l).get('type')=='turn_context')
 assert context['model']=='gpt-6.1-sol' and context['effort']=='medium' and context['sandbox_policy']['network_access'] is False
 readers[bed]=dict(model=context['model'],effort=context['effort'],network_access=False,verdict='VALID',violations=scan['violations'],manifest_check_skipped=scan['manifest_check_skipped'])
assert (D/'SEGEVAL2_HANDOFF.md').read_text().splitlines()[-1]=='SEGEVAL2: done | scans: a VALID b VALID | FP 29/50 (length rules 27/43) | FN 5/100 | commit bundle'
receipt=dict(ok=True,study_rows=150,unique_ids=150,seal_verified=True,unchanged_v44_metrics=True,controls_passed=10,false_positives=29,length_rule_false_positives=27,length_rule_denominator=43,false_negatives=5,unresolved=s['unresolved'],contexts=readers,scoring_tests=8,new_reads=0,artifacts={str(f.relative_to(D)):sha(f) for f in [D/'segeval1_score.py',D/'test_score.py',D/'scored/summary.json',D/'scored/owner_rows.jsonl',D/'scored/owner_sheet.csv',D/'SEGEVAL1_RESULT.md',D/'SEGEVAL2_HANDOFF.md',D/'scan/verdicts.json']})
(D/'segeval2_verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
