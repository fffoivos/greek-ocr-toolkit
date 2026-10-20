"""A0 estimates, with OA collection weights and capped page-length estimates."""
from f2lib import *
from collections import defaultdict,Counter
def one(source,frame,draw,vv,collection=None):
 N=len(frame);n=len(draw);passes=[v for v in vv if v.get('pass')];k=len(passes);ci=wilson(k,n);caps=[min(40,max(0,int(v['resolved_item'].get('page_count') or 0))) for v in passes]
 dates=defaultdict(list)
 for v,cap in zip(passes,caps):dates[period(v['resolved_item'].get('year'))].append(cap)
 r=dict(source=source,collection=collection,N=N,n=n,k=k,share=k/n if n else None,wilson95=ci,estimated_accessible_items=N*k/n if n else None,accessible_items_ci=[N*x for x in ci],observed_verified_items=k,mean_capped_pages_passed=sum(caps)/k if k else None,estimated_pages_capped40=N*sum(caps)/n if n else None,pages_40_ceiling=N*40*k/n if n else None,pages_40_ceiling_ci=[N*40*x for x in ci],period_estimates={key:dict(sample_verified_items=len(values),sample_capped_pages=sum(values),estimated_accessible_items=N*len(values)/n,estimated_capped_pages=N*sum(values)/n) for key,values in dates.items()},scope='Enumerated frame only; Wilson interval covers pass-share uncertainty, not catalogue completeness, page-length variation, or Google yield uncertainty.')
 return r
def build():
 result=[]
 sources=['openarchives','kosmopolis','pleias','pergamos','nlg-digital','elstat','government-gazette','lekythos','anemi']
 for source in sources:
  frame=rows(BASE/f'population_{source}.jsonl');draw=rows(BASE/f'draw_{source}.jsonl');vv=rows(BASE/f'verification_{source}.jsonl')
  if source=='openarchives':
   for col in sorted({r['collection_slug'] for r in frame}):
    ff=[r for r in frame if r['collection_slug']==col];dd=[r for r in draw if r['collection_slug']==col];ids={r['id'] for r in dd};result.append(one(source,ff,dd,[v for v in vv if v['item'] in ids],col))
  else:result.append(one(source,frame,draw,vv))
  p=BASE/'receipts'/f'census-{source}.json';d=json.loads(p.read_text());d.update(frame_sha256=sha(BASE/f'population_{source}.jsonl'),draw_sha256=sha(BASE/f'draw_{source}.jsonl'),verification_sha256=sha(BASE/f'verification_{source}.jsonl'),survey='survey.jsonl',seed=SEED)
  if source=='openarchives':
   parts=[x for x in result if x['source']==source]
   d.update(estimated_accessible_target_items=sum(x['estimated_accessible_items'] for x in parts),estimated_accessible_target_items_ci=None,verified_share=None,survey_estimator='sum N_collection * k_collection / n_collection; see marginal Wilson intervals in survey.jsonl; no pooled/joint 95% claim',pages_at_40_item_ceiling=sum(x['pages_40_ceiling'] for x in parts),pages_at_40_item_ceiling_ci=None)
  write(p,d)
 jsonl(BASE/'survey.jsonl',result)
 # Make per-decade catalogue totals explicit for the Gazette, including decades
 # absent from the single uniform 20-item random draw.
 frame=rows(BASE/'population_government-gazette.jsonl');draw=rows(BASE/'draw_government-gazette.jsonl');v={r['item']:r for r in rows(BASE/'verification_government-gazette.jsonl')}
 rows_=[]
 for decade in sorted({r['year']//10*10 for r in frame}):
  ff=[r for r in frame if r['year']//10*10==decade];dd=[r for r in draw if r['year']//10*10==decade];rows_.append(dict(decade=decade,N=len(ff),random_draw_items=len(dd),verified=sum(v.get(r['id'],{}).get('pass',False) for r in dd),qualification='no randomly verified item this decade' if not dd else 'represented in uniform source draw'))
 jsonl(BASE/'receipts/gazette-decades.jsonl',rows_)
 return result
if __name__=='__main__':
 for r in build():print(r['source'],r['collection'],r['N'],r['k'],r['n'],round(r['estimated_pages_capped40'],1))
