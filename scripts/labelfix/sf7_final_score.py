"""OC2: R2 controls-first resolution followed by the fixed 100-line scoring merge.
No inference, model invocation, network or git. Empty prepared answers report PENDING.
"""
import sys
sys.dont_write_bytecode=True
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'artifacts/sf7_rc1/audit';K=A/'opus_keys'
sys.path.insert(0,str(Path(__file__).parent));import r2_cards_resolve as R2
sys.path.insert(0,str(K/'vendor'));import numpy as np
from greekocr.ops.data_root import input_path as _data_input
from adjudicate.deck import leak_scan

def cluster_score(rows,numer,denom,replicates=10000):
 """Unweighted document cluster percentile bootstrap, matching AU1's audit unit.

 The target is the fixed 100-line audit, not population inclusion-weighted precision.
 PENDING lines are excluded and the interval scope is explicitly recorded.
 """
 if not rows:return dict(value=None,document_bootstrap95=None,replicates=replicates)
 docs=sorted({r['document'] for r in rows});matrix=np.zeros((len(docs),2))
 for i,d in enumerate(docs):
  group=[r for r in rows if r['document']==d];matrix[i]=[sum(numer(r) for r in group),sum(denom(r) for r in group)]
 rng=np.random.default_rng(20261019);counts=rng.multinomial(len(docs),np.full(len(docs),1/len(docs)),size=replicates);totals=counts@matrix
 rates=totals[:,0]/totals[:,1]
 return dict(value=float(matrix[:,0].sum()/matrix[:,1].sum()),document_clusters=len(docs),document_bootstrap95=np.quantile(rates,[.025,.975]).tolist(),replicates=replicates,seed=20261019,method='document-cluster percentile bootstrap; each audit line weight 1',degenerate=bool(np.ptp(rates)<1e-12))

def load(p):return json.loads(_data_input(Path(p)).read_text())
def sha(p):return hashlib.sha256(_data_input(Path(p)).read_bytes()).hexdigest()
def verify():
 for path,expected in load(K/'sources.json').items():
  # Upstream files are bound for provenance; execution only needs the sealed local copies.
  p=Path(path)
  if p.is_relative_to(ROOT):
   if sha(p)!=expected:raise ValueError('sealed input changed: '+str(p))
 config=load(K/'config.json');pack=Path(config['pack'])
 for path,expected in load(K/'build_receipt.json')['hashes'].items():
  p=Path(path)
  if p.name!='answers.jsonl' and sha(p)!=expected:raise ValueError('reader input changed: '+str(p))
 return pack

def counts(records,field):
 out={}
 for value in sorted({r[field] for r in records}):
  group=[r for r in records if r[field]==value];c=Counter(r['status'] for r in group)
  out[value]=dict(total=len(group),correct=c['CORRECT'],incorrect=c['INCORRECT'],pending=c['PENDING'])
 return out

def merge(truth,gate_passed,*,bootstrap=True):
 routing=load(A/'routing.json');sol=load(A/'score.json');targets=load(K/'target_heads.json');keys={k['head_id']:k for k in R2.read(K/'deck/private/key.jsonl') if not k['control']}
 assert set(keys)=={h['head_id'] for h in targets}
 assert sol['summary']['partial_line_precision']==dict(correct=70,denominator=70,value=1.0)
 assert any(c['status']=='VALID' and c['context'].startswith('accent_') for c in sol['contexts'])
 assert all(c['status']=='VOID' for c in sol['contexts'] if c['context'].startswith('capital_'))
 resolved={t['card_id']:t for t in truth};prior={h['head_id']:h for h in sol['heads']};heads=[]
 aliases={'smooth':'psili','rough':'dasia','subscript':'present','dialytika':'present'}
 for h in routing['heads']:
  x=dict(h,truth=None,released_right=None,status='PENDING',evidence=None)
  if h['head_id'] in keys:
   key=keys[h['head_id']];t=resolved.get(key['card_id']) if gate_passed else None
   if t:
    # Card-level status can be unresolved because another head is unknown.
    # Only this prespecified edit head is scored; unknown is never negative evidence.
    anchor=next((r for r in t['letter_heads'] if r['index']==key['anchor_index']),{})
    field='diaeresis' if h['head']=='dialytika' else h['head'];value=anchor.get(field,'unknown')
    ownership_na=t['ownership_ok'] is None and R2.unmarked(anchor)
    # Reject a changed/missing base inventory or moved anchor. Options are never truth.
    aligned=t.get('printed_form') is not None and R2.letters(t['printed_form'])==R2.letters(key['public']['base_letters'])
    if aligned and value!='unknown' and (t['ownership_ok'] is True or ownership_na) and t['readability'] in ('readable','partial'):
     x.update(truth=value,released_right=value==aliases.get(h['released_label'],h['released_label']),evidence='Opus:2-of-2-or-2-of-3')
  else:
   p=prior[h['head_id']]
   if h['route']!='Sol-accent' or p['status']!='SCORED' or type(p.get('released_right')) is not bool:raise ValueError('unsealed Sol observation')
   x.update(truth=p['reading'],released_right=p['released_right'],evidence='Sol:VALID-accent')
  if x['released_right'] is not None:x['status']='CORRECT' if x['released_right'] else 'INCORRECT'
  heads.append(x)
 byid={h['head_id']:h for h in heads};lines=[]
 for l in routing['lines']:
  hh=[byid[i] for i in l['heads']];pending=any(h['status']=='PENDING' for h in hh)
  kinds=sorted({h['kind'] for h in hh})
  lines.append(dict(audit_id=l['audit_id'],line_id=l['line_id'],document=l['doc'],weight=1.,heads=l['heads'],kind='+'.join(kinds),status='PENDING' if pending else 'CORRECT' if all(h['released_right'] for h in hh) else 'INCORRECT'))
 c=Counter(l['status'] for l in lines);scored=[l for l in lines if l['status']!='PENDING'];complete=c['PENDING']==0
 estimate=cluster_score(scored,lambda r:int(r['status']=='CORRECT'),lambda r:1,replicates=10000) if bootstrap else None
 summary=dict(frame_lines=100,correct=c['CORRECT'],incorrect=c['INCORRECT'],pending=c['PENDING'],scored=len(scored),resolved_line_precision=c['CORRECT']/len(scored) if scored else None,final_line_precision=c['CORRECT']/100 if complete else None,bar_correct_lines=83,line_precision_bar_pass=(c['CORRECT']>=83) if complete and gate_passed else None,controls_gate_passed=gate_passed,pending_never_imputed=True,cluster_bootstrap=estimate,interval_scope='complete audit' if complete else 'resolved lines only; not a final audit interval',per_head=counts(heads,'head'),per_kind=counts(heads,'kind'),per_line_kind=counts(lines,'kind'),release_authorized=False,full_preregistration_pass=None,line_class_constraint='Separate sf6 line-class comparison required by preregistration; not inferred from the 83/100 gate.')
 return dict(summary=summary,heads=heads,lines=lines)

def resolve(reader1,reader2,out,reader3=None):
 # The original R2 resolver expects image destination parents to exist.
 (out/'tiebreak/blind/img').mkdir(parents=True,exist_ok=True)
 truth,gates,_=R2.run(K/'deck',reader1,reader2,out,reader3)
 # Both original independent readers must pass. A third reader cannot rescue a failed gate.
 passed=all(gates[n]['accepted'] for n in ('reader1','reader2')) and (reader3 is None or gates['reader3']['accepted'])
 return truth,gates,passed

def stage_tiebreak(out,folder):
 src=out/'tiebreak/blind'
 if not (src/'cards.jsonl').exists():return None
 # Use neutral reader instructions; the upstream resolver's lead-facing header
 # explicitly names planted checks and is not part of this blind allowlist.
 expected={str(p.relative_to(src)):p.read_bytes() for p in src.rglob('*') if p.is_file()}
 expected['README.md']=(K/'deck/blind/README.md').read_bytes()
 if folder.exists():
  for name,data in expected.items():
   if not (folder/name).is_file() or (folder/name).read_bytes()!=data:raise ValueError('existing tiebreak assignment differs')
 else:
  folder.mkdir(parents=True)
  for name,data in expected.items():
   p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  (folder/'answers.jsonl').write_text('')
 scan=leak_scan(folder,['released_label','stratum','source_id','RB7-'])
 if not scan['passed']:raise ValueError('tiebreak leak scan failed')
 R2.dump(out/'tiebreak_receipt.json',dict(reader_folder=str(folder),cards=len(R2.read(folder/'cards.jsonl')),scan=scan,hashes={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='answers.jsonl'},private_keys=str(out/'tiebreak/private')))
 return str(folder)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reader1',type=Path);p.add_argument('--reader2',type=Path);p.add_argument('--reader3',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
 if a.out is None:a.out=A/'final_scores'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
 pack=verify();r1=a.reader1 or pack/'r1/answers.jsonl';r2=a.reader2 or pack/'r2/answers.jsonl'
 if a.out.exists():raise ValueError('output exists; use a fresh --out to preserve receipts')
 a.out.mkdir(parents=True)
 if not r1.read_text().strip() and not r2.read_text().strip() and not a.reader3:
  truth=[];gates={};passed=False
 else:
  truth,gates,passed=resolve(r1,r2,a.out/'resolution',a.reader3)
  if passed:stage_tiebreak(a.out/'resolution',pack/'r3')
 report=merge(truth,passed);report['controls_gate']=gates
 report['input_hashes']={str(x):sha(x) for x in (r1,r2,K/'sources.json',ROOT/'scripts/labelfix/sf7_final_score.py')}
 if a.reader3:report['input_hashes'][str(a.reader3)]=sha(a.reader3)
 R2.dump(a.out/'final_score.json',report)
 s=report['summary'];print(json.dumps(dict(output=str(a.out/'final_score.json'),**{n:s[n] for n in ('correct','incorrect','pending','final_line_precision','line_precision_bar_pass','controls_gate_passed')})))
 if gates and not passed:raise SystemExit(2)
if __name__=='__main__':main()
