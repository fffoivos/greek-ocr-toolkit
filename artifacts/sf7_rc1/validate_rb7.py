import json,sys,hashlib,random,collections
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE));from build_rb7 import rows,sha,dump,RAW,SEL
policy=json.load(open(BASE/'output_3687228/receipt.json'))['policy']
for name,want in policy['sources'].items():assert sha(BASE.parents[1]/name)==want
assert sha(BASE.parents[1]/'docs/labelfix/spellcheck/SF7_PREREGISTRATION.md')==policy['preregistration_sha256']
receipt=json.load(open(BASE/'RELEASE_RECEIPT.json'));scores=json.load(open(BASE/'lqb_scores.json'));raw={r['id']:r['label'].encode() for r in rows(RAW)};selected={r['id'] for r in rows(SEL)}
p=BASE/'release_edits_only_A.jsonl';assert sha(p)==receipt['sha256'];assert sha(BASE/'lqb_scores.json')==receipt['lqb_scores_sha256'];assert receipt['status']=='candidate_pre_audit' and not receipt['bound']
release=list(rows(p));assert len(release)==receipt['row_count']==605;assert sum(len(r['edits']) for r in release)==receipt['edit_count']==665
for r in release:
 lid=r['line_id'];a=raw[lid];b=r['text'].encode();assert lid in selected and a!=b and r['parent']=='google_raw_v2_import';out=[];inverse=[];x0=y0=0
 for q in r['byte_patches']:
  x,x1,y,y1=(q[k] for k in ('raw_byte_start','raw_byte_end','output_byte_start','output_byte_end'));assert x>=x0 and y>=y0 and a[x0:x]==b[y0:y];assert a[x:x1]==q['before'].encode() and b[y:y1]==q['after'].encode();out.extend([a[x0:x],b[y:y1]]);inverse.extend([b[y0:y],a[x:x1]]);x0,y0=x1,y1
 out.append(a[x0:]);inverse.append(b[y0:]);assert b''.join(out)==b and b''.join(inverse)==a
 assert all(set(['slot','kind','head','rule','signals','variant','policy_digest','source_job']).issubset(e) and e['byte_patches'] for e in r['edits'])
truth=Path.home()/'Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb';excluded={r['line_id'] for n in ['truth_v1.jsonl','truth_v1_1.jsonl'] for r in rows(truth/n)}
for path in receipt['audit']['audit100_files']:
 q=Path(path)
 excluded.update(r['line_id'] for r in (json.load(open(q)) if q.suffix=='.json' else rows(q)) if not r.get('control',False))
frame=list(rows(BASE/'audit100_frame.jsonl'));ids=[r['line_id'] for r in frame];eligible=sorted(r['line_id'] for r in release if r['line_id'] not in excluded)
assert len(frame)==len(set(ids))==100 and not set(ids)&excluded;assert ids==random.Random(20261017).sample(eligible,100);assert sha(BASE/'audit100_frame.jsonl')==receipt['audit']['frame_sha256'];assert len(eligible)==515
sf6={r['line_id']:r for r in rows(BASE/'compact_sf6.jsonl')};sx=list(rows(BASE.parents[0]/'sx1/sf6_release_extract_lqb_v2.jsonl'));audit=0
for r in sx:
 s=r['modes']['ENSEMBLE_AB'];b=sf6[r['line_id']]
 assert (s['status']=='HOLD')==(b['status']=='hold')
 if s['status']!='HOLD':assert s['label']==b['label']
 if 'audit100' in r['truth_sets']:assert b['status']=='corrected';audit+=1
assert audit==99
assert scores['choice']['variant']=='A' and scores['choice']['tie'] and scores['views']['tier_AB']['versions']['A']['precision']==1
paths=['output_3687228/READBACK_RECEIPT.json','lqb_scores.json','RELEASE_RECEIPT.json','release_edits_only_A.jsonl','audit100_frame.jsonl','release_summary.json','build_rb7.py','score_rb7.py','convert_rb7.py','report_rb7.py']
dump(BASE/'VALIDATION_RECEIPT.json',dict(status='passed',checks=['21 local policy source hashes and preregistration match the completed job','605 exact-parent byte patch/inverse reconstructions','665 edits have complete provenance and byte spans','all edited IDs selected and all rows differ','audit frame exactly seeded uniform draw from 515 eligible IDs','all truth/audit100 excluded','all 101 SX1b ENSEMBLE_AB statuses/labels identical including 99 corrected audit rows','choice A on exact precision tie','release and score hashes match receipt'],sha256={n:sha(BASE/n) for n in paths},report_sha256=sha(BASE.parents[1]/'docs/labelfix/spellcheck/SF7_RC1_LQB.md')))
print('PASS: exact bytes, provenance, hashes, selection, seeded exclusions, SX1b baseline and choice')
