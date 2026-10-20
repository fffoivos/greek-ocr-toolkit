import gzip,json,sys
from collections import Counter
from pathlib import Path
R=Path.cwd();B=R/'docs/harvest/census05';S=B/'c_evidence'
sys.path.insert(0,str(B/'package/projects/greek-ocr-toolkit-pipe032'))
from greekocr.harvest.line_pipeline_sources import canonicalize
cfg=json.loads((B/'census05_config.json').read_text());audit=json.loads((B/'input_audit.json').read_text());metadata=json.loads(Path(audit['metadata']['path']).read_text())
assign={}
with gzip.open(audit['split']['path'],'rt') as f:
 for l in f:
  r=json.loads(l);assign[r['parent_id'],r['row_id']]=r
protected=set(cfg['final_policy']['heldout_crop_sha256']);observed=set();protected_editions=set(cfg['final_policy']['heldout_editions']);trainhits=[];byparent=Counter();count=0
for p in cfg['parents']:
 local=next(x['path'] for x in audit['parents'] if x['parent_id']==p['id'])
 with Path(local).open() as f:
  for l in f:
   r=canonicalize(json.loads(l),p,metadata);s=assign.get((p['id'],r['id']))
   if s:r.update(split=s['split'],edition_id=s['edition_id'])
   count+=1
   if r['split'] not in ('train','unassigned'):observed.add(r['crop_sha256'])
   if r['split']!='train':protected_editions.add(r['edition_id'])
   if r['split']=='train' and r['crop_sha256'] in protected:
    trainhits.append(dict(parent=p['id'],id=r['id'],crop_sha256=r['crop_sha256'],edition_id=r['edition_id']));byparent[p['id']]+=1
result=dict(rows=count,configured_protected=len(protected),observed_nontrain_crops=len(observed),configured_also_observed=len(protected&observed),configured_missing_from_readout=len(protected-observed),train_observations_in_configured_set=len(trainhits),train_hits_by_parent=dict(byparent),train_hits_not_in_observed=[r for r in trainhits if r['crop_sha256'] not in observed],train_hits_unprotected_by_either_readout_set=[r for r in trainhits if r['crop_sha256'] not in observed and r['edition_id'] not in protected_editions])
(S/'protection_recount.json').write_text(json.dumps(result,indent=2)+'\n');print({k:len(v) if isinstance(v,list) else v for k,v in result.items()},flush=True)
