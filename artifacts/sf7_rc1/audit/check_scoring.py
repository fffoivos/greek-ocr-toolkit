"""Synthetic state-transition checks, entirely outside the reader packs."""
import tempfile
import driver as d
from build import *

def check():
 routing=load(A/'routing.json');observations={}
 for h in routing['heads']:
  if h['route']=='Opus-later':continue
  v={'accent':'none','breathing':'none','confidence':'high','note':'','context':'synthetic','item_id':'k0000000000'};v[h['head']]=h['released_label']
  observations[h['head_id']]={'initial':dict(v),'reread':dict(v)}
 old_a,old_obs,old_report=d.A,d.observations,d.write_report
 try:
  with tempfile.TemporaryDirectory(prefix='au1-score-fixture-') as td:
   d.A=Path(td);dump(d.A/'routing.json',routing);d.observations=lambda:(observations,[]);d.write_report=lambda *args:None
   d.score();s=load(d.A/'score.json');assert s['summary']['partial_line_precision']=={'correct':77,'denominator':77,'value':1.0};assert s['summary']['opus_pending_lines']==23;assert s['summary']['full_audit_pass'] is None
   assert all(l['status']=='PENDING' for l in s['lines'] if l['opus_pending_heads'])
   # A disagreement is not automatically resolved by either reader.
   h=next(h for h in routing['heads'] if h['route']=='Sol-accent');uid=h['head_id'];wrong='none' if h['released_label']!='none' else 'acute'
   observations[uid]['initial']['accent']=wrong;d.score();s=load(d.A/'score.json');assert next(x for x in s['heads'] if x['head_id']==uid)['status']=='NEEDS_LEAD'
   # A reviewed mismatch makes the whole resolved Sol-only line incorrect.
   dump(d.A/'lead_review.json',{uid:dict(verified=True,reviewer='synthetic fixture',reading=wrong,note='fixture')});d.score();s=load(d.A/'score.json');head=next(x for x in s['heads'] if x['head_id']==uid);assert head['released_right'] is False
   line=next(x for x in s['lines'] if x['line_id']==h['line_id']);assert line['sol_correct'] is False
   # VOID/missing contexts provide no observations, never zero-error votes.
   d.observations=lambda:({},[{'status':'VOID','context':'synthetic'}]);(d.A/'lead_review.json').unlink();d.score();s=load(d.A/'score.json');assert s['summary']['partial_line_precision']['denominator']==0
  print('PASS: all-head line conjunction, mixed-line PENDING, review-required flags, human mismatch, VOID exclusion')
 finally:d.A,d.observations,d.write_report=old_a,old_obs,old_report
if __name__=='__main__':check()
