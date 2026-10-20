#!/usr/bin/env python3
"""Score the sealed draw after two clean canonical blind reads; no reader launch."""
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent
SCANNER_VERSION='4.5.5'
SCANNER_SHA256='e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'
RUBRIC=('neighbour_whole_word','multi_line','rotated','horizontally_missegmented')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def load(p):return json.loads(Path(p).read_text())
def classify(answer):
 values=[answer[k] for k in RUBRIC]
 if any(v not in ('yes','no','uncertain') for v in values):raise ValueError('invalid rubric value')
 return 'flagged' if 'yes' in values else 'unresolved' if 'uncertain' in values else 'fine'
def score(answers,keys,decisions):
 table=[];controls=[];fp=Counter();reject_den=Counter();fn=Counter();states=Counter()
 seen=set()
 for bed in ('segeval1_a','segeval1_b'):
  key=keys[bed];aa=answers[bed]
  if [a['card_id'] for a in aa]!=key['order']:raise ValueError(bed+': missing, duplicate, extra, or reordered answers')
  for a in aa:
   m=key['items'][a['card_id']]
   if not isinstance(a.get('segmentation_detail'),str):raise ValueError('missing free-text segmentation_detail')
   if a.get('letters') not in ('y','n','u') or a.get('marks') not in ('y','n','na') or a.get('crop_ok') not in ('y','n') or not isinstance(a.get('errors'),list) or not isinstance(a.get('detail'),str):raise ValueError('invalid bsb answer')
   state=classify(a)
   if m['control']:
    expected=m['control_origin']['reference_verdict']
    wrong=[f for f in ('letters','crop_ok') if a[f]!=expected[f]]
    controls.append(dict(context=bed,card_id=a['card_id'],row_id=m['row_id'],errors=wrong,passed=not wrong));continue
   rid=m['row_id'];assert rid not in seen;seen.add(rid)
   r=decisions[rid];assert r==m or dict(r,control=False)==m
   decision=r['decision'];reason=r['segmentation']['reason'];states[decision+'|'+state]+=1
   if decision=='REJECT':
    reject_den[reason]+=1
    if state=='fine':fp[reason]+=1
   elif state=='flagged':
    for k in RUBRIC:
     if a[k]=='yes':fn[k]+=1
   table.append(dict(line_id=rid,crop='crops/'+rid+'.png',google_text=r['google_text'],decision=decision,reason=reason,context=bed,card_id=a['card_id'],reader_state=state,reader_answer=a))
 assert seen==set(decisions) and len(table)==150
 errors=Counter(c['context'] for c in controls if not c['passed'])
 return dict(study_counts=dict(states),false_positives=sum(fp.values()),false_positives_denominator=50,false_positives_by_reason={r:dict(false_positives=fp[r],drawn=n,rate=fp[r]/n) for r,n in sorted(reject_den.items())},false_negatives=states['ACCEPT|flagged'],false_negatives_denominator=100,false_negatives_by_rubric=dict(fn),unresolved={c:states[c+'|unresolved'] for c in ('REJECT','ACCEPT')},controls=controls,controls_valid=all(errors[bed]<=1 for bed in answers),interpretation='REJECT+fine is a false positive; ACCEPT+any yes is a false negative. Uncertain-only answers are unresolved. Rubric counts overlap. bsb marks/letters/crop_ok do not substitute for the owner crop rubric. No numerical proceed threshold was supplied.'),table

def validate_scan(scan,scan_path,answer_path):
 if scan.get('ok') is not True or scan.get('violations') != [] or scan.get('manifest_check_skipped') is not False or scan.get('scanner_version')!=SCANNER_VERSION:
  raise ValueError('missing VALID canonical v4.5.5 scan')
 custody=load(scan_path.parent/'r1.custody.json')
 if custody['answers_sha256']!=sha(answer_path) or custody['scan_sha256']!=sha(scan_path) or custody['scanner_sha256']!=SCANNER_SHA256:
  raise ValueError('scan/answer custody mismatch')
 if custody['verdict']!='VALID' or custody['scanner_version']!=SCANNER_VERSION or sha(Path(custody['scanner']))!=SCANNER_SHA256:
  raise ValueError('scanner custody mismatch')
 if sha(Path(custody['rollout']))!=custody['rollout_sha256'] or scan['rollout_sha256']!=custody['rollout_sha256'] or scan['rollout']!=custody['rollout']:
  raise ValueError('rollout custody mismatch')
 if sha(Path(custody['reader_dir']).parent/'MANIFEST.r1.json')!=custody['manifest_sha256']:
  raise ValueError('manifest custody mismatch')
 return dict(verdict='VALID',scanner_version=SCANNER_VERSION,scanner_sha256=SCANNER_SHA256,scan_sha256=sha(scan_path),custody_sha256=sha(scan_path.parent/'r1.custody.json'),previous_scans=custody['previous_scans'])

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('answers-a','answers-b','scan-a','scan-b'):p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 receipt=load(D/'draw_receipt.json');seal=D/'keys/sealed_decisions.jsonl'
 if sha(seal)!=receipt['seal_sha256']:raise ValueError('decision seal changed')
 decisions={r['row_id']:r for r in rows(seal)};assert len(decisions)==150
 keys={b:load(D/'keys'/f'{b}.json') for b in ('segeval1_a','segeval1_b')}
 scans={b:load(s) for b,s in zip(keys,(a.scan_a,a.scan_b))}
 verdicts={}
 for b,answer_path,scan_path in zip(keys,(a.answers_a,a.answers_b),(a.scan_a,a.scan_b)):
  verdicts[b]=validate_scan(scans[b],scan_path,answer_path)
 answers=dict(zip(keys,(rows(a.answers_a),rows(a.answers_b))))
 summary,table=score(answers,keys,decisions)
 for row in table:
  row['scan_verdict']='VALID';row['scan_custody']=verdicts[row['context']]
 summary.update(scan_verdicts=verdicts,seal_sha256=receipt['seal_sha256'],answer_hashes={b:sha(p) for b,p in zip(keys,(a.answers_a,a.answers_b))},scan_hashes={b:sha(p) for b,p in zip(keys,(a.scan_a,a.scan_b))})
 a.out.mkdir(parents=True,exist_ok=True)
 (a.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 (a.out/'owner_rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in table))
 with (a.out/'owner_sheet.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader()
  writer.writerows(dict(r,reader_answer=json.dumps(r['reader_answer'],ensure_ascii=False)) for r in table)
 print(json.dumps(summary,ensure_ascii=False,indent=2))
 return 0 if summary['controls_valid'] else 2
if __name__=='__main__':raise SystemExit(main())
