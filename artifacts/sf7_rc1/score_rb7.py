"""Read-only LQB method reuse with union alignment and atomic mark P/R."""
import sys,importlib.util,json,collections,itertools,functools
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent; PEER=Path.home()/'Projects/greek-ocr-toolkit-secondary'; LQB=PEER/'docs/labelfix/lqb'
spec=importlib.util.spec_from_file_location('lqb_ro',PEER/'greekocr/labelfix/lqb.py');lqb=importlib.util.module_from_spec(spec);spec.loader.exec_module(lqb)
import numpy as np
names=('google','sf6','A','B')
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def rows(p):return [json.loads(l) for l in p.open()]
@functools.lru_cache(None)
def predictions(truth,text):
 ts=lqb.letters(truth);ls=lqb.letters(text)
 a=[dict(line_id='toy',doc='toy',print_slots=[dict(id=str(i),base=c[0],targets=lqb.factors(c),unknown=[]) for i,c in enumerate(ts)])]
 b=[dict(line_id='toy',start=i,base=c[0],factors=lqb.factors(c)) for i,c in enumerate(ls)]
 return {int(r['id']):r['prediction'] for r in lqb.union_scorer().union_records(a,b) if not r['inserted_prediction']}
def evaluate(r,text):
 s=r['slot'];h=lqb.HEADS.index(s['head']);k=s['kind']
 if k=='scoped_mark':
  text=lqb.scoped_bases(r['context']['reference'],text,s['start'],s['end'])
  if text is None:return None
  pred=predictions(r['context']['printed_word'],text)[s['letter']][h]
 elif k=='word_letter':
  ws=text.split();w=ws[s['word']] if s['word']<len(ws) else ''
  pred=predictions(r['context']['printed_word'],w)[s['letter']][h]
 else:
  ls=lqb.letters(text);pred=lqb.factors(ls[s['index']])[h] if s['index']<len(ls) else 0
 y=r['target'];err=int(pred!=y)
 return np.array([int(pred==y and y>0),int(pred!=y and pred>0),int(pred!=y and y>0),err,1],dtype=float)
def used(r):
 # Propagate frozen gate/reader lineage. SF7's preregistration also explicitly
 # cites the substitution60 owner review; metadata has not tagged it yet.
 tags={'SF7','quote_alias','sf6_release','sf6_gate','S6','R1-A'}
 return bool(tags.intersection(r['used_by'])) or r['provenance']['set']=='substitution60'
def metrics(a):
 a=np.asarray(a);s=a.sum(0) if len(a) else np.zeros(5);tp,fp,fn,e,n=s
 return dict(items=int(n),errors=int(e),opportunities=int(n),tp=int(tp),fp=int(fp),fn=int(fn),precision=float(tp/(tp+fp)) if tp+fp else None,recall=float(tp/(tp+fn)) if tp+fn else None,head_accuracy=float(1-e/n) if n else None)
def boot(items,values,pair=None,stratified=False):
 docs=collections.defaultdict(lambda:np.zeros(10 if pair else 5))
 waves={}
 for r,v in zip(items,values):
  d=r['doc_id'];wave=r.get('context',{}).get('wave',d.split(':')[0]);waves[d]=wave
  docs[d]+=v
 if not docs:return {'documents':0,'replicates':4000,'valid_precision_replicates':0,'precision_ci95':None,'recall_ci95':None,'head_error_delta_ci95':None}
 keys=sorted(docs);m=np.array([docs[k] for k in keys]);rng=np.random.default_rng(20261017);p=[];rec=[];err=[]
 groups=collections.defaultdict(list)
 for i,k in enumerate(keys):groups[waves[k] if stratified else 'all'].append(i)
 for b in range(4000):
  t=sum((m[rng.choice(g,len(g),replace=True)].sum(0) for g in groups.values()),np.zeros(m.shape[1]))
  def rate(s):
   tp,fp,fn,e,n=s;return (tp/(tp+fp) if tp+fp else np.nan,tp/(tp+fn) if tp+fn else np.nan,e/n if n else np.nan)
  x=rate(t[:5]);y=rate(t[5:]) if pair else None
  p.append(y[0]-x[0] if pair else x[0]);rec.append(y[1]-x[1] if pair else x[1]);err.append(100*(y[2]-x[2]) if pair else x[2])
 def ci(x):
  x=np.array(x);x=x[np.isfinite(x)];return np.quantile(x,[.025,.975]).tolist() if len(x) else None
 return dict(documents=len(keys),documents_per_wave=dict(collections.Counter(waves.values())),replicates=4000,seed=20261017,method='document-within-wave percentile bootstrap' if stratified else 'document-cluster percentile bootstrap',valid_precision_replicates=int(np.isfinite(p).sum()),precision_ci95=ci(p),recall_ci95=ci(rec),head_error_delta_ci95=ci(err) if pair else None)
truth,flagsha=lqb.load_truth(LQB/'truth_v1_1.jsonl');marks=[r for r in truth if r['class']=='marks']
assert lqb.sha256(LQB/'truth_v1_1.jsonl')==json.load(open(LQB/'truth_v1_1.manifest.json'))['sha256']
google={r['line_id']:r['google_text'] for r in rows(LQB/'google_truth_v1_1.jsonl')}
releases={v:{r['line_id']:r for r in rows(BASE/f'compact_{v}.jsonl')} for v in names[1:]}
texts={'google':google}
for v in names[1:]:texts[v]={lid:r['label'] for lid,r in releases[v].items() if r['status'] in ('corrected','unchanged')}
selected=set(releases['A']);assert selected==set(releases['B'])==set(releases['sf6'])
marks=[r for r in marks if r['line_id'] in selected]
print('selected truth',len(marks),'lines',len({r['line_id'] for r in marks}),'in sample',sum(used(r) for r in marks),flush=True)
# Same common guard for every model prevents credit from SF7 fitting items.
result=dict(schema='rb7-lqb-marks-v1',truth_path=str(LQB/'truth_v1_1.jsonl'),truth_sha256=lqb.sha256(LQB/'truth_v1_1.jsonl'),google_sha256=lqb.sha256(LQB/'google_truth_v1_1.jsonl'),flags_sha256=flagsha,method_source_sha256=lqb.sha256(PEER/'greekocr/labelfix/lqb.py'),precision_definition='atomic micro TP/(TP+FP), exact nonzero mark identity; wrong-positive is FP and FN; union alignment reused from LQB/r2 scorer',in_sample_guard=dict(shared_tags=['SF7','quote_alias','sf6_release','sf6_gate','S6','R1-A'],additional_set='substitution60: directly cited by binding SF7 preregistration',excluded_items=sum(used(r) for r in marks)),selection_truth_items=len(marks),selection_truth_lines=len({r['line_id'] for r in marks}),views={})
E={}
for v in names:
 for r in marks:
  if r['line_id'] not in texts[v]:continue
  # error() is also evaluated on the original complete text below.
  val=evaluate(r,texts[v][r['line_id']])
  if val is not None:
   assert lqb.error(r,texts[v][r['line_id']])==(int(val[3]),1)
   E[v,r['truth_id']]=val
for scope,tiers in [('tier_A',['A']),('tier_B',['B']),('tier_C',['C']),('tier_AB',['A','B']),('all_tiers',['A','B','C'])]:
 subset=[r for r in marks if r['tier'] in tiers and not used(r) and r.get('rate_eligible') is not False]
 view=dict(truth_items=len(subset),truth_lines=len({r['line_id'] for r in subset}),versions={},paired={})
 for v in names:
  rr=[r for r in subset if (v,r['truth_id']) in E];vv=[E[v,r['truth_id']] for r in rr]
  out=metrics(vv);out.update(lines=len({r['line_id'] for r in rr}),uncovered_items=len(subset)-len(rr),cluster=boot(rr,vv),by_head={})
  for h in lqb.HEADS:
   hh=[r for r in rr if r['slot']['head']==h];out['by_head'][h]=metrics([E[v,r['truth_id']] for r in hh])
  view['versions'][v]=out
 for a,b in itertools.combinations(names,2):
  rr=[r for r in subset if (a,r['truth_id']) in E and (b,r['truth_id']) in E];va=[E[a,r['truth_id']] for r in rr];vb=[E[b,r['truth_id']] for r in rr]
  ma,mb=metrics(va),metrics(vb)
  view['paired'][a+'→'+b]=dict(items=len(rr),lines=len({r['line_id'] for r in rr}),a=ma,b=mb,precision_delta=(mb['precision']-ma['precision']) if ma['precision'] is not None and mb['precision'] is not None else None,recall_delta=(mb['recall']-ma['recall']) if ma['recall'] is not None and mb['recall'] is not None else None,cluster=boot(rr,[np.concatenate([x,y]) for x,y in zip(va,vb)],True),sample_types=dict(collections.Counter(r['sample_type'] for r in rr)))
 result['views'][scope]=view
ab=result['views']['tier_AB']['versions'];pa,pb=ab['A']['precision'],ab['B']['precision']
assert pa is not None and pb is not None,'No defined choice precision: report blocker rather than inventing a tie'
chosen='B' if pb>pa else 'A';result['choice']=dict(variant=chosen,rule='Higher released-label atomic marks precision on tier A/B, common in-sample guard, ties A',A=pa,B=pb,tie=pa==pb,paired=result['views']['tier_AB']['paired']['A→B'])
# Also retain explicit SF7 metadata-only guard sensitivity and in-sample counts.
result['guard_sensitivity']={}
for v in names:
 rr=[r for r in marks if r['tier'] in ('A','B') and not lqb.sample_used(r,'SF7') and r.get('rate_eligible') is not False and (v,r['truth_id']) in E]
 result['guard_sensitivity'][v]=dict(metrics([E[v,r['truth_id']] for r in rr]),lines=len({r['line_id'] for r in rr}))
# Saved card weights are used verbatim; never renormalize after coverage exclusions.
weighted={'versions':{},'paired':{},'scope':'Covered S8_DEV only, not the full DEV population', 'weights':'fixed context.card_weight; document bootstrap independently within wave'}
subset=[r for r in marks if r['provenance']['set']=='S8_DEV' and not used(r)]
def wm(vv):
 s=np.asarray(vv).sum(0) if len(vv) else np.zeros(5);tp,fp,fn,e,n=s
 return dict(weighted_tp=float(tp),weighted_fp=float(fp),weighted_fn=float(fn),weighted_errors=float(e),weighted_opportunities=float(n),precision=float(tp/(tp+fp)) if tp+fp else None,recall=float(tp/(tp+fn)) if tp+fn else None,error_rate=float(e/n) if n else None)
for v in names:
 rr=[r for r in subset if (v,r['truth_id']) in E];vv=[E[v,r['truth_id']]*r['context']['card_weight'] for r in rr]
 weighted['versions'][v]=dict(wm(vv),unweighted_items=len(rr),lines=len({r['line_id'] for r in rr}),cluster=boot(rr,vv,stratified=True))
for a,b in itertools.combinations(names,2):
 rr=[r for r in subset if (a,r['truth_id']) in E and (b,r['truth_id']) in E]
 va=[E[a,r['truth_id']]*r['context']['card_weight'] for r in rr];vb=[E[b,r['truth_id']]*r['context']['card_weight'] for r in rr]
 ma,mb=wm(va),wm(vb)
 weighted['paired'][a+'→'+b]=dict(items=len(rr),lines=len({r['line_id'] for r in rr}),a=ma,b=mb,precision_delta=mb['precision']-ma['precision'] if ma['precision'] is not None and mb['precision'] is not None else None,recall_delta=mb['recall']-ma['recall'] if ma['recall'] is not None and mb['recall'] is not None else None,cluster=boot(rr,[np.concatenate([x,y]) for x,y in zip(va,vb)],True,True))
result['weighted_dev']=weighted
common=[r for r in marks if r['tier'] in ('A','B') and not used(r) and r.get('rate_eligible') is not False and all((v,r['truth_id']) in E for v in names)]
result['common_four_way']=dict(items=len(common),lines=len({r['line_id'] for r in common}),versions={v:dict(metrics([E[v,r['truth_id']] for r in common]),cluster=boot(common,[E[v,r['truth_id']] for r in common])) for v in names})
dump(BASE/'lqb_scores.json',result);print('choice',chosen,'scores',[(v,ab[v]['precision'],ab[v]['recall'],ab[v]['items'],ab[v]['lines']) for v in names],flush=True)
