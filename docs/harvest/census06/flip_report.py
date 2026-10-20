"""Stream two completed publications; compare ADMIT and admitted_train membership."""
import argparse,collections,hashlib,json,sqlite3,tempfile
from pathlib import Path

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(p):
 with p.open() as f:
  for s in f:
   if s.strip():yield json.loads(s)
def key(r):
 b=r.get('binding',r);return b['parent_id'],b['id']
def generation(run):
 c=json.loads((run/'CURRENT.json').read_text());assert c['status']=='completed'
 g=(run/'generations'/c['export_id']).resolve();assert g.parent==(run/'generations').resolve()
 assert sha(g/'summary.json')==c['summary_sha256']
 s=json.loads((g/'summary.json').read_text());assert s['complete'] is True
 for name,e in s['outputs'].items():assert sha(g/(name+'.jsonl'))==e['sha256']
 return g,c

def report(before,after,out):
 before,after,out=map(lambda p:Path(p).resolve(),(before,after,out))
 assert all(out!=p and p not in out.parents for p in (before,after)), 'output must be outside both runs'
 out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=out) as tmp:
  db=sqlite3.connect(str(Path(tmp)/'index.sqlite'))
  db.execute('CREATE TABLE r(side INTEGER,parent TEXT,id TEXT,admit INTEGER,train INTEGER,status TEXT,edit INTEGER,reason TEXT,PRIMARY KEY(side,parent,id))')
  receipts=[]
  for side,run in enumerate((before,after)):
   g,c=generation(run);receipts.append(dict(run=str(run),current=c,decisions_sha256=sha(g/'decisions.jsonl'),admitted_train_sha256=sha(g/'admitted_train.jsonl')))
   for d in rows(g/'decisions.jsonl'):
    p,i=key(d);r=d.get('routes',{}).get('polytonic',{})
    db.execute('INSERT INTO r VALUES (?,?,?,?,?,?,?,?)',(side,p,i,int(d['disposition']=='ADMIT'),0,r.get('status','missing'),int(bool(r.get('edits'))),r.get('evidence',{}).get('reason','')))
   seen=set()
   for r in rows(g/'admitted_train.jsonl'):
    p,i=key(r);assert (p,i) not in seen,'duplicate train export';seen.add((p,i))
    q=db.execute('UPDATE r SET train=1 WHERE side=? AND parent=? AND id=? AND admit=1',(side,p,i));assert q.rowcount==1,'invalid train member'
   db.commit()
   assert json.loads((run/'CURRENT.json').read_text())==c,'publication changed'
  missing=db.execute('SELECT parent,id FROM r WHERE side=0 EXCEPT SELECT parent,id FROM r WHERE side=1').fetchone()
  added=db.execute('SELECT parent,id FROM r WHERE side=1 EXCEPT SELECT parent,id FROM r WHERE side=0').fetchone()
  assert missing is None and added is None,'row membership differs'
  counts=collections.Counter();totals=collections.Counter()
  unresolved={'required_evidence_unresolved','unresolved','failed','proposal_only'}
  for p,a,b,t,u,s,v,e,f,sr,vr in db.execute('SELECT a.parent,a.admit,b.admit,a.train,b.train,a.status,b.status,a.edit,b.edit,a.reason,b.reason FROM r a JOIN r b ON a.parent=b.parent AND a.id=b.id WHERE a.side=0 AND b.side=1'):
   totals[p]+=1
   reason='polytonic hold' if s in unresolved or v in unresolved else 'polytonic edit' if e or f else 'kept_unverified: '+vr if v=='kept_unverified' else 'kept_unverified: '+sr if s=='kept_unverified' else 'other'
   for metric,x,y in [('ADMIT',a,b),('admitted_train',t,u)]:
    if x!=y:counts[p,metric,str(x)+' -> '+str(y),reason]+=1
  result=dict(schema='census06-flip-report-v1',parents=[dict(parent=p,rows=n) for p,n in sorted(totals.items())],flips=[dict(parent=p,metric=m,transition=t,reason=r,rows=n) for (p,m,t,r),n in sorted(counts.items())],receipts=receipts,reason_note='Descriptive route attribution, not causal inference; missing results carry canonical unresolved status.',membership_identical=True)
  (out/'flip_report.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(report(a.before,a.after,a.out)))
