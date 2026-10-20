import hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path.cwd();ART=ROOT/'artifacts/ru1/ru3t'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
r=json.loads((ART/'RU3TF1_RECEIPT.json').read_text());out=Path(r['sheets']['path'])
b=json.loads((ART/'build.json').read_text())
assert all(sha(p)==h for p,h in {**b['inputs'],**b['pack_inputs']}.items())
assert all(sha(p)==h for p,h in r['outputs'].items())
assert not list((ROOT/'artifacts/ru1').glob('ru1_v3_train*'))
index=json.loads((out/'sheets_index.json').read_text())['items']
template=rows(out/'lead_review_template.jsonl')
assert len(index)==len(template)==1190
assert len({c['cell'] for c in index})==1190
assert Counter(c['decision'] for c in index if c['set']=='audit')==Counter(edit_hard=40,keep_soft=20)
assert Counter(c['set'] for c in template)==Counter(review=1130,audit=60)
assert len(rows(out/'review_template.jsonl'))==1130 and len(rows(out/'audit_template.jsonl'))==60
assert all(Counter(c['sheet'] for c in index)[s]<=10 for s in {c['sheet'] for c in index})
assert {c['sheet'] for c in index}=={p.name for p in out.glob('*.png')}
decisions=rows(ART/'decisions.jsonl')
missing={(d['row_id'],d['offset']) for d in decisions if d['reason']=='missing_independent_reads'}
assert missing=={(p['row_id'],p['offset']) for p in rows(ART/'fresh_r3_positions.jsonl')}
scans={p.name:json.loads(p.read_text()) for p in (ART/'answers').glob('*.scan.json')}
assert len(scans)==38 and all(s['scanner_version']=='v4.4-canonical' for s in scans.values())
invalid={k:dict(status=v['status'],reason=v.get('reason') or 'wrong_signs='+str(v['gate']['wrong_signs'])) for k,v in r['invalid_contexts'].items()}
assert len(r['contexts'])==38 and r['valid_contexts']==26
context_positions=rows(ART/'r3_context_positions.jsonl')
assert set(p['context'] for p in context_positions)==set(invalid)
for k in invalid:invalid[k]['positions']=sum(p['context']==k for p in context_positions)
mappings=json.loads((ART/'phase1/retained_geometry_mappings.json').read_text())
validation=dict(status='PASS',bound_inputs_unchanged=True,outputs_hashes_checked=True,canonical_scans=38,canonical_scan_failures=sum(not s['ok'] for s in scans.values()),context_status_counts=dict(Counter(v['status'] for v in r['contexts'].values())),invalid_contexts=invalid,decisions=dict(Counter(d['decision'] for d in decisions)),review_cells=1130,review_sheets=113,audit_cells=60,audit_sheets=6,fresh_r3_positions=len(missing),context_position_entries=len(context_positions),identity_mapped_rows=len(mappings),coverage_totals={k:sum(c[k] for c in r['coverage'].values()) for k in ('direct','derived','unviewed')},train_v3_absent=True,visual_reading=False)
(ART/'phase1/validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
r['validation']=validation
r['execution']+='; sheets resumed from saved combine using phase1/resume_sheets.py'
r['retained_geometry_mapping']=dict(path=str(ART/'phase1/retained_geometry_mappings.json'),sha256=sha(ART/'phase1/retained_geometry_mappings.json'),rows=len(mappings),method='identity codepoint mapping proven by equal lengths, identical alphabetic boundaries and unchanged target signs; retained Google text anchors checked')
r['phase1_helpers']={str(p):sha(p) for p in (ART/'phase1').glob('*.py')}
r['scan_evidence']={str(p):sha(p) for p in (ART/'answers').glob('*.scan.json')}
for p in [ART/'RU3TF1_RECEIPT.json',out/'RU3TF1_RECEIPT.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
readme='RU3TF1 phase 1 lead material\n\nReview: review_001.png through review_113.png (1,130 cells).\nAudit: audit_001.png through audit_006.png (40 edit_hard + 20 keep_soft).\nTemplates: review_template.jsonl, audit_template.jsonl, lead_review_template.jsonl.\nUse existing cell ids; lead is null and note is blank. No adjudication has been made.\nIndex and references: sheets_index.json, references.json, references/.\nFresh independent rereads: fresh_r3_positions.jsonl (1,100 unique positions).\nAll VOID/failed context positions: r3_context_positions.jsonl.\n\nExcluded contexts:\n'+''.join(f"- {k}: {v['status']}; {v['reason']}; {v['positions']} positions\n" for k,v in invalid.items())+'\nChecks: canonical v4.4 scans, original control gates, traced derived-view coverage, original combine, exact geometry, PNG decoding, index/template counts and bound-input/output hashes.\nReferences are comparison aids, not adjudicated truth; reference basis is recorded in references.json.\nEarlier same-length parent text substitutions use a proved identity offset mapping, recorded in RU3TF1_RECEIPT.json and per-cell geometry.\nNo new readings, network, browser, computer use, git writes, train-v3 output, registry changes or LQB scoring. No visual QA performed.\n'
(out/'README.txt').write_text(readme)
print(json.dumps(validation,ensure_ascii=False,indent=2))
