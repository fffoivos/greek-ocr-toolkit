"""Exact readback, unchanged scoring, owner diagnostics and S4 report/receipt."""
from replay import *
from greekocr.harvest.predictor_path import predictor_binary
import numpy as np,re,subprocess,datetime
from zoneinfo import ZoneInfo
VERS=('08','s1','s2','s3','s4');VERDICTS=('KEEP','DROP','UNCERTAIN');LABELS=('KEEP','DROP')
common=module('cells_output_common',BASE/'cells_opus/scripts/common.py')

def table(head,rs):
 def cell(a):return str(a).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(cell(a) for a in row)+' |' for row in rs])

def stamp(m):
 s=m.get('updated','')
 if not s:return 0.
 dt=datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
 if dt.tzinfo is None:dt=dt.replace(tzinfo=ZoneInfo('Europe/Athens'))
 return dt.timestamp()

def latest_marks(ms):
 latest={}
 for i,m in enumerate(ms):
  old=latest.get(m['line_id'])
  if old is None or (stamp(m),i)>=(stamp(old),old['file_line']):latest[m['line_id']]=dict(m,file_line=i)
 return latest

def typ_marks():
 p=SS/'owner_marks_smallseg.jsonl'
 if p.exists():return read(p),dict(source=str(p),dump_used=None,available_dump=str(SS/'sheet/marks_dump/20261019T1827'),selection='owner_marks_smallseg.jsonl exists; dump not used')
 folders=sorted((SS/'sheet/marks_dump').glob('*'));folder=folders[-1];out=[]
 for p in sorted((folder/'notes').glob('*.json')):
  m=json.loads(p.read_text());out.append(dict(m,line_id=m.get('line_id',p.stem.removeprefix('smallseg:'))))
 return out,dict(source='notes/*.json',dump_used=str(folder))

def confusion(rows,pred,label):
 return {v:{m:sum(pred(r)==v and label(r)==m for r in rows) for m in LABELS} for v in VERDICTS}

def score(rows,pred,label):
 c=confusion(rows,pred,label)
 return dict(n=len(rows),agreement=c['KEEP']['KEEP']+c['DROP']['DROP'],confusion=c)

def all_ratio(g):
 b=g['all_box'];return (b[2]-b[0])/(b[3]-b[1]) if b else None

def old_ratio(g):
 f=g['s3_frame'];return max(f['length'],f['height'])/min(f['length'],f['height']) if f else None

def quantiles(xs):
 xs=[x for x in xs if x is not None and np.isfinite(x)]
 return dict(n=len(xs),quantiles={str(p):float(np.percentile(xs,p)) for p in (0,10,25,50,75,90,95,99,100)} if xs else {})

def fit(rows,box,exclude):
 getter=old_ratio if box=='s3' else all_ratio
 sel=[r for r in rows if r['line_id'] not in exclude and getter(r['geometry']) is not None]
 x=np.array([r['chars'] for r in sel]);y=np.array([getter(r['geometry']) for r in sel]);a,b=np.polyfit(x,y,1);res=y-(a*x+b)
 return dict(n=len(sel),a=float(a),b=float(b),residual_SD=float(res.std(ddof=2)),MAD=float(np.median(np.abs(res-np.median(res)))),ids=[r['line_id'] for r in sel],source_counts=dict(Counter(r['cohort'] for r in sel)))

def box_detail(z,g,old=False):
 e=z['evidence'];b=e['box_evidence']
 return dict(measured=b.get('bbox'),row_frame=b.get('row_frame'),diagnostic_s3_box=g.get('s3_box') if old else None,diagnostic_all_ink_box=g['all_box'])

def flip(r,marks):
 return dict(cohort=r['cohort'],line_id=r['line_id'],text=r['row']['raw_text'],chars=r['chars'],A=r['A'],owner_standard_state=r.get('owner_standard_state'),owner_rating=r.get('owner_rating'),owner_mark=marks.get(r['line_id']),old_verdict=r['before']['verdict'],new_verdict=r['after']['verdict'],old_reason=r['before']['reason'],new_reason=r['after']['reason'],old_box=box_detail(r['before'],r['geometry'],True),new_box=box_detail(r['after'],r['geometry']))

def run():
 rs=read(D/'replay.jsonl');ts=read(D/'typology_replay.jsonl');extra=read(D/'extra_numeric.jsonl');assert len(rs)==1288 and len(ts)==437
 assert [sum(r['cohort']==c for r in rs) for c in ('segeval1','calibration','cells')]==[150,888,250]
 ms=read(BASE/'owner_marks_20261019.jsonl');marks=latest_marks(ms);assert len(ms)==240 and len(marks)==235
 tm,mark_source=typ_marks();tmarks=latest_marks(tm);write(D/'owner_marks_snapshot.jsonl',ms);write(D/'typology_owner_marks_snapshot.jsonl',tm)
 cards=json.loads((SS/'sheet/card_manifest.json').read_text());bed=[t for t in ts if not t['manifest']['control']];assert len(bed)==417 and len(cards)==417
 assert {c['line_id'] for c in cards}=={t['line_id'] for t in bed}
 for t in ts:
  m=t['manifest'];assert sha(t['row']['crop_path'])==m['crop_sha256']
  assert t['chars']==m['chars'],(t['line_id'],'chars differ')
 checks=Counter();w=worker();oldw=worker('s3')
 try:
  for r in rs:
   assert sha(r['row']['crop_path'])==r['row']['crop_sha256']
   if not r['small']:
    assert canonical(norm(r['before']))==canonical(norm(r['after']))
    assert canonical(r['before']['evidence'])==canonical(r['after']['evidence']);checks['non_small_byte_identical']+=1
  zs=[(r['before'],r['row'],False) for r in rs]+[(r['after'],r['row'],r['small']) for r in rs]+[(t['versions'][v],t['row'],v=='s4' and t['small']) for t in ts for v in ('08','s3','s4')]
  for z,row,small in zs:
   service=w if z['tool_version']=='0.9-s4' else oldw
   e=z['evidence'];dec=service.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=e))
   assert (dec['verdict'],dec['reason'])==(z['verdict'],z['reason']);checks['final_decision_readbacks']+=1
   gate=service.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=dict(e,gate_only=True)))
   assert gate==e['gate'];checks['gate_readbacks']+=1
   b=e['box_evidence']
   if b['available']:
    f=b['row_frame'];a,c=(f['length'],f['height']) if small else (max(f['length'],f['height']),min(f['length'],f['height']))
    pred=w.predictor.call(dict(long_side=a,short_side=c,script=row.get('script_class','pooled')))
    assert pred==b['prediction'];checks['predictor_readbacks']+=1
    p=e['padding_evidence'];assert p['row_frame_height']==f['height']
    if small:assert p['row_frame_height']==p['upright_box_height']
  for r in rs:
   if not r['small']:continue
   b=r['after']['evidence']['box_evidence']
   if b['available']:
    assert b['bbox']==r['geometry']['all_box'];checks['all_component_boxes_exact']+=1
 finally:w.close();oldw.close()
 cohorts={}
 for c in ('segeval1','calibration','cells'):
  pop=[r for r in rs if r['cohort']==c];s=dict(n=len(pop),small=sum(r['small'] for r in pop),transitions=dict(Counter(r['verdict_s3']+'->'+r['verdict_s4'] for r in pop)))
  if c=='segeval1':
   s['confusion']={v:s1.g.confusion([dict(r,verdict_09=r['verdict_'+v]) for r in pop],'09') for v in VERS}
   s['errors']={v:dict(FP=x['DROP']['fine'],FN=x['KEEP']['faulty'],UNC=sum(x['UNCERTAIN'].values())) for v,x in s['confusion'].items()}
  if c=='calibration':
   rated=[r for r in pop if r.get('owner_rating') and r['owner_rating'].get('decision') in LABELS];assert len(rated)==135
   s['rated']={v:score(rated,lambda r:r['verdict_'+v],lambda r:r['owner_rating']['decision']) for v in VERS}
  cohorts[c]=s
 unique={r['line_id']:r for r in rs};assert set(marks)<=set(unique)
 marked=[unique[k] for k in marks];owner={v:score(marked,lambda r:r['verdict_'+v],lambda r:marks[r['line_id']]['owner_mark']) for v in VERS}
 flips=[flip(r,marks) for r in rs if r['verdict_s3']!=r['verdict_s4']];write(D/'flips.jsonl',flips)
 # Typology: score only explicit typology marks and exclude controls.
 judged=[t for t in bed if t['line_id'] in tmarks];typ={}
 for v in ('08','s3','s4'):
  groups={}
  for field in ('final_type','final_class'):
   groups[field]={}
   for group in sorted({t['manifest'][field] for t in bed}):
    members=[t for t in bed if t['manifest'][field]==group];j=[t for t in members if t['line_id'] in tmarks]
    groups[field][group]=dict(bed_n=len(members),**score(j,lambda t:t['versions'][v]['verdict'],lambda t:tmarks[t['line_id']]['owner_mark']))
  typ[v]=dict(overall=score(judged,lambda t:t['versions'][v]['verdict'],lambda t:tmarks[t['line_id']]['owner_mark']),groups=groups)
 drops=[dict(line_id=t['line_id'],text=t['row']['raw_text'],owner=tmarks[t['line_id']],final_text=t['manifest']['final_text'],final_type=t['manifest']['final_type'],verdict=t['versions']['s4']['verdict'],reason=t['versions']['s4']['reason']) for t in judged if tmarks[t['line_id']]['owner_mark']=='DROP']
 exempt={g:dict(Counter(t['versions']['s4']['verdict'] for t in bed if t['manifest']['final_class']==g)) for g in sorted({t['manifest']['final_class'] for t in bed})}
 typflips=[]
 for t in ts:
  if t['versions']['s3']['verdict']!=t['versions']['s4']['verdict']:
   typflips.append(flip(dict(t,before=t['versions']['s3'],after=t['versions']['s4']),tmarks))
 write(D/'typology_flips.jsonl',typflips)
 # Owner union. Explicit mark always outranks a rating; timestamp then file order
 # breaks ties between explicit marks. Keep every conflicting source for audit.
 candidates={}
 for r in rs:
  rating=(r.get('owner_rating') or {})
  if rating.get('decision') in LABELS:candidates.setdefault(r['line_id'],[]).append(dict(owner_mark=rating['decision'],source='888 rating',explicit=False,updated=rating.get('updated','')))
 for source,entries in [('owner_marks_20261019',ms),('typology',tm)]:
  for m in entries:candidates.setdefault(m['line_id'],[]).append(dict(m,source=source,explicit=True))
 judgments={};conflicts=[]
 for rid,entries in candidates.items():
  chosen=max(enumerate(entries),key=lambda it:(it[1]['explicit'],stamp(it[1]),it[0]))[1];judgments[rid]=chosen
  if len({m['owner_mark'] for m in entries})>1:conflicts.append(dict(line_id=rid,chosen=chosen,judgments=entries))
 pool={}
 for r in rs:pool[r['line_id']]=dict(r,versions=dict(s3=r['before'],s4=r['after']))
 for t in ts:
  if t['line_id'] in pool:
   assert t['row']['crop_sha256']==pool[t['line_id']]['row']['crop_sha256']
   assert all(t['versions'][v]['verdict']==pool[t['line_id']]['versions'][v]['verdict'] for v in ('s3','s4'))
  else:pool[t['line_id']]=t
 for r in extra:assert r['line_id'] not in pool;pool[r['line_id']]=r
 coverage=[]
 opus_samples={r['line_id']:r for r in read(BASE/'cells_opus/samples.jsonl')}
 for directory in ('crops','cells/samples','cells_opus/crops','small_segments/crops'):
  for p in sorted((BASE/directory).glob('*.png')):
   if p.stem in pool:
    assert sha(p)==pool[p.stem]['row']['crop_sha256']
    coverage.append(dict(path=str(p),line_id=p.stem,status='SHA-verified in measured pool'))
   else:
    m=opus_samples[p.stem];chars=s1.character_count(m['text']);A=max(m['width'],m['height'])/min(m['width'],m['height'])
    assert not (chars<=8 and A<=6 and common.output_type(m['text'])=='numeric')
    coverage.append(dict(path=str(p),line_id=p.stem,status='outside small numeric definition',chars=chars,A=A,type=common.output_type(m['text'])))
 write(D/'local_crop_coverage.jsonl',coverage)
 checks['local_crop_paths_inventory_accounted_for']=len(coverage)
 numeric=[r for r in pool.values() if r['small'] and common.output_type(r['row']['raw_text'])=='numeric']
 fits={box:{'all':fit(numeric,box,set()),'without_owner':fit(numeric,box,set(judgments))} for box in ('s3','s4')}
 dump(D/'numeric_fits.json',fits)
 population=[r for r in pool.values() if r['small'] and r['line_id'] in judgments];assert all('versions' in r for r in population)
 small_conflicts=[c for c in conflicts if c['line_id'] in {r['line_id'] for r in population}];write(D/'owner_conflicts.jsonl',small_conflicts)
 # Reuse the native service for each expectation swap, retaining its own gate,
 # box, padding and the existing negative/unavailable-prediction handling.
 a,b=worker('s3'),worker();cells=[]
 try:
  for fit_kind in ('without_owner','all'):
   for r in population:
    predictions={}
    for box,service in [('s3',a),('s4',b)]:
     z=r['versions'][box];predictions[box+'/text-font']=z['verdict'];e=json.loads(json.dumps(z['evidence']))
     if e['box_evidence']['available']:
      ratio=old_ratio(r['geometry']) if box=='s3' else all_ratio(r['geometry']);f=fits[box][fit_kind];pred=(ratio-f['b'])/f['a']
      e['box_evidence']['predictions'][2]=pred
     d=service.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=e))
     predictions[box+'/short-numeric']=d['verdict']
    cells.append(dict(line_id=r['line_id'],type=common.output_type(r['row']['raw_text']),chars=r['chars'],A=r['A'],text=r['row']['raw_text'],owner=judgments[r['line_id']],fit=fit_kind,predictions=predictions,geometry=r['geometry']))
 finally:a.close();b.close()
 write(D/'two_by_two_predictions.jsonl',cells)
 matrix={}
 for kind in ('without_owner','all'):
  matrix[kind]={}
  for typ0 in ('numeric','mixed','non-numeric'):
   pop=[c for c in cells if c['fit']==kind and c['type']==typ0];matrix[kind][typ0]={key:dict(score(pop,lambda r:r['predictions'][key],lambda r:r['owner']['owner_mark']),numeric_n=len(pop) if typ0=='numeric' else 0,indicative_only=len(pop)<30) for key in ('s3/text-font','s4/text-font','s3/short-numeric','s4/short-numeric')}
 comparisons=[('box at text-font','s3/text-font','s4/text-font'),('box at short-numeric','s3/short-numeric','s4/short-numeric'),('expectation at s3','s3/text-font','s3/short-numeric'),('expectation at s4','s4/text-font','s4/short-numeric')]
 swaps=[dict(comparison=label,from_cell=k0,to_cell=k1,before=r['predictions'][k0],after=r['predictions'][k1],**{k:r[k] for k in ('line_id','type','chars','A','text','owner','fit')}) for r in cells for label,k0,k1 in comparisons if r['predictions'][k0]!=r['predictions'][k1]]
 write(D/'two_by_two_flips.jsonl',swaps)
 best={typ0:[k for k,v in group.items() if v['agreement']==max(q['agreement'] for q in group.values())] for typ0,group in matrix['without_owner'].items()}
 # Per-small measurements and gate ruling counterfactual (diagnostic only).
 small=[]
 for r in rs+ [dict(t,before=t['versions']['s3'],after=t['versions']['s4']) for t in ts]:
  if not r['small']:continue
  old,new=r['before'],r['after'];g=r['geometry'];ratio0=old_ratio(g);ratio1=all_ratio(g)
  moved=old['verdict']=='UNCERTAIN' and (old['evidence']['gate']['reason']=='gate: no main row found' or 'No usable text box' in old['reason']) and new['evidence']['gate']['verdict']=='PASS' and new['evidence']['box_evidence']['available']
  small.append(dict(cohort=r['cohort'],line_id=r['line_id'],text=r['row']['raw_text'],width=r.get('width',r.get('manifest',{}).get('width')),height=r.get('height',r.get('manifest',{}).get('height')),processed_width=g['processed_width'],processed_height=g['processed_height'],chars=r['chars'],A=r['A'],before=old['verdict'],after=new['verdict'],old_reason=old['reason'],new_reason=new['reason'],s3_box=box_detail(old,g,True),s4_box=box_detail(new,g),s3_box_ratio=ratio0,all_ink_ratio=ratio1,all_ink_over_s3_ratio=ratio1/ratio0 if ratio0 else None,gate_abstain_moved=moved,without_gate_ruling='UNCERTAIN' if moved else new['verdict']))
 write(D/'small.jsonl',small)
 smallmain=[s for s in small if s['cohort']!='typology'];smalltyp=[s for s in small if s['cohort']=='typology']
 moved=[s for s in smallmain if s['gate_abstain_moved']];movedtyp=[s for s in smalltyp if s['gate_abstain_moved']]
 transitions=Counter((s['before'],s['after'],s['old_reason'],s['new_reason']) for s in smallmain)
 distributions={name:dict(s3_ratio=quantiles([s['s3_box_ratio'] for s in ss]),all_ink_ratio=quantiles([s['all_ink_ratio'] for s in ss]),all_ink_over_s3_ratio=quantiles([s['all_ink_over_s3_ratio'] for s in ss])) for name,ss in [('1288',smallmain),('typology',smalltyp)]}
 huge=[s for s in small if s['text'] in ('*****','Longine','MELA OF 10','ποσό') or min(s['processed_width'],s['processed_height'])>=400]
 # All initial files outside the S4 output are compared, including untracked evidence.
 initial=json.loads((D/'initial_hashes.json').read_text());changed=[]
 for p,h in initial.items():
  if not (R/p).is_file() or sha(R/p)!=h:changed.append(p)
 allowed=['docs/harvest/line_pipeline/tool_versions.json','greekocr/harvest/line_pipeline_native.py','greekocr/harvest/filtering_assets/crop-tools.py','greekocr/harvest/filtering_assets/service.mjs','scripts/harvest/build_filter_versions.py','tests/test_seg_curve.py','tests/test_seg_deskew.py']
 assert set(changed)==set(allowed),(changed,allowed)
 current={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and '.git' not in p.parts and D not in p.parents and '__pycache__' not in p.parts}
 added=current-set(initial);assert added=={'tests/test_seg_small.py'},added
 guard=dict(status='PASS',changed_existing_files=changed,new_test_files=sorted(added),unchanged_initial_files=len(initial)-len(changed),protected_paths_unchanged=['docs/harvest/seg_census/package/','docs/harvest/seg09/','untracked census02 evidence'],policy_functions_byte_identical=True,predictor_unchanged=True,detector_unchanged=True,network='OFF',readers=0,git_writes=False)
 vp=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 prior=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 for name,info in vp.items():
  if name not in ('segmentation','census'):assert info==prior[name]
  if name in ('segmentation','census'):
   assert hashlib.sha256(json.dumps(info['components'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==info['digest']
 assert vp['segmentation']['version']=='0.9-s4' and vp['census']['version']==prior['census']['version']
 checks['metadata_dependency_digests']=2
 dump(D/'scope_guard.json',guard)
 testslog=(D/'tests.log').read_text();assert 'failed' not in testslog;tests=int(re.search(r'(\d+) passed',testslog)[1])
 summary=dict(version='0.9-s4',cohorts=cohorts,owner_marks=owner,typology=dict(rows=437,controls=20,scored_bed=417,marked=len(judged),source=mark_source,results=typ,owner_drops=drops,length_exempt_diagnostic=exempt,flips=len(typflips)),small=dict(main=len(smallmain),typology=len(smalltyp),gate_abstain_moved=len(moved),typology_gate_abstain_moved=len(movedtyp),moved_verdicts=dict(Counter(s['after'] for s in moved)),typology_moved_verdicts=dict(Counter(s['after'] for s in movedtyp)),counterfactual='All moved records would remain UNCERTAIN without the ruling',distributions=distributions),numeric=dict(unique_local_small_numeric=len(numeric),fits=fits,source_counts=dict(Counter(r['cohort'] for r in numeric))),two_by_two=dict(population=len(population),conflicts=len(small_conflicts),matrix=matrix,best=best),flips=len(flips),tests=tests,readback=checks)
 dump(D/'summary.json',summary)
 err=lambda x:'/'.join(str(x[k]) for k in ('FP','FN','UNC'))
 errors=cohorts['segeval1']['errors'];rated=cohorts['calibration']['rated']
 last=f"SEG S4 READY: small {len(smallmain)} of 1288 replay (+{len(smalltyp)} typology); gate-abstain moved {len(moved)}; 150 FP/FN/UNC {err(errors['s3'])} → {err(errors['s4'])}; 888 rated agree {rated['s3']['agreement']} → {rated['s4']['agreement']}/135; owner marks agree {owner['s3']['agreement']} → {owner['s4']['agreement']}/235; typology owner agree 0.8 {typ['08']['overall']['agreement']} / s3 {typ['s3']['overall']['agreement']} / s4 {typ['s4']['overall']['agreement']} of {len(judged)}; 2x2 best cell per type "+' / '.join(t+':'+','.join(best[t]) for t in ('numeric','mixed','non-numeric'))+f"; flips {len(flips)}; tests {tests} passed"
 lines=['# SEG step 4 — 0.9-s4','','Small = saved Google characters ≤8 and crop long/short aspect ≤6, inclusively. After the unchanged S2 clockwise turn, every component returned by existing extraction contributes its axis-aligned bounds, including specks, dots, marks, rules and neighbour roles. No roles, x-height, row angle or curve enter this small box. Width is passed as long_side and height as short_side to the unchanged text-font predictor. Padding is (processed crop height − all-component box height) / that same box height. Non-small rows retain S3. No length exemption, numeric fit, extra threshold or heuristic enters the tool.','','## Replay and unchanged scoring','','S1 inputs, native adapter, source-context selection, frozen predictor and 120-second per-row timeout are reused unchanged. All 1,288 S3 native results match saved S3. The 150 are scored from their full saved reader answers using gate2 owner_state (positive faults precede unknowns), with DROP/fine = FP, KEEP/faulty = FN and every UNCERTAIN counted. The 888 use the same 135 explicit owner ratings; the 250 have no inferred labels. The 240 explicit owner-mark entries resolve to 235 IDs, latest timestamp then file order winning. No reader ran. The saved 0.8 baseline retains its historical 18/14/11 score.','',table(['Metric',*[{'08':'0.8'}.get(v,'0.9-'+v) for v in VERS]],[['150 FP/FN/UNC',*[err(errors[v]) for v in VERS]],['888 rated agreement /135',*[rated[v]['agreement'] for v in VERS]],['Owner marks agreement /235',*[owner[v]['agreement'] for v in VERS]]]),'',table(['Set','Rows','Small','S3 → S4 transitions'],[[c,s['n'],s['small'],s['transitions']] for c,s in cohorts.items()]),'','## Gate ruling','','Rule 1 runs first. The byte-identical policy functions are reused by service orchestration. For a small crop with no main row, existing positive complete-row or >2-whole-word evidence still drops; otherwise the no-main abstention defers to all-ink length/padding. A missing S3 text box no longer blocks a crop that has extracted components. The S3 implementation has no separate live “neighbour extent unresolved” gate branch; source context is diagnostic and remains so. Empty component sets still have no measurable box.','',f"Main replay: {len(moved)} row-machinery abstentions move: {dict(Counter(s['after'] for s in moved))}. Typology: {len(movedtyp)} move: {dict(Counter(s['after'] for s in movedtyp))}. Every one would remain UNCERTAIN without this ruling; see the per-row without_gate_ruling field in [small.jsonl](small.jsonl). These are cohort records; overlapping IDs are counted once per cohort.",'','## Every S3 → S4 verdict flip','','Old/new boxes below are the actual Stage-B measurements (None means gate-blocked or unusable); supplemental S3 and all-component boxes are saved separately in flips.jsonl and never substituted into blocked tool evidence.','',table(['Set','ID','Chars','A','S3 → S4','Owner state / rating / mark','Old box / frame','New box / frame'],[[f['cohort'],f['line_id'],f['chars'],f['A'],f['old_verdict']+' → '+f['new_verdict'],'; '.join(str(x) for x in [f['owner_standard_state'],(f['owner_rating'] or {}).get('decision'),(f['owner_mark'] or {}).get('owner_mark')] if x),[f['old_box']['measured'],f['old_box']['row_frame']],[f['new_box']['measured'],f['new_box']['row_frame']]] for f in flips]),'','[Full flips with reasons and owner marks](flips.jsonl). Typology changes are in [typology_flips.jsonl](typology_flips.jsonl).','','## Typology owner agreement','',f"All 437 SHA-verified crops replayed for 0.8, S3 and S4. The 20 control=true rows are replayed but excluded from scoring; the other 417 exactly match card_manifest.json. {len(judged)} bed cards have explicit typology owner marks. Source: `{mark_source['source']}`; dump used: {mark_source['dump_used']}. The available 20261019T1827 dump is not used because the preferred JSONL exists. Unmarked cards do not acquire inferred owner judgements.",'',table(['Version','Owner agreement / marked','Confusion (tool → owner KEEP/DROP)'],[[v,str(typ[v]['overall']['agreement'])+'/'+str(len(judged)),typ[v]['overall']['confusion']] for v in ('08','s3','s4')]),'']
 for field in ('final_type','final_class'):
  lines+=['### Agreement by '+field,'',table([field,'Bed n','Owner n','0.8','S3','S4'],[[g,typ['s4']['groups'][field][g]['bed_n'],typ['s4']['groups'][field][g]['n'],*[typ[v]['groups'][field][g]['agreement'] for v in ('08','s3','s4')]] for g in typ['s4']['groups'][field]]),'']
 lines+=['### Owner DROPs: label-fault readback','','These marks concern Google-output correctness. Their S4 verdicts below do not establish a box fault; the tool has no new label-correctness rule. Saved notes and final_text are shown literally. All eight receive KEEP. Four have explicit output-error notes and four have final_text=wrong, but these groups overlap on NOTE.; their union is seven. The remaining 1. ΡΑΓΙΟ has no note and final_text=match. The inputs therefore do not establish eight disjoint label-fault records, and no missing label judgement is inferred.','',table(['ID','Text','Owner note','Saved final_text','S4','Reason'],[[x['line_id'],x['text'],x['owner'].get('note',''),x['final_text'],x['verdict'],x['reason']] for x in drops]),'','### Length-exempt classes — diagnostic only','','Classes come from the typology manifest, including punctuation-only, non-text, CJK and fault groups named in NOTE_steps45_length_exempt.md. Controls are excluded. The note cautions that owner-kept clipped/extra legitimate types are not a trustworthy fault core; no class changes a verdict.','',table(['final_class','S4 verdict counts'],list(exempt.items())),'','## Numeric-only or all-small: diagnostic 2×2','','Population is the union of small crops with typology marks, owner_marks_20261019 marks or an explicit 888 rating, deduplicated by line_id. Explicit marks outrank ratings; latest explicit timestamp wins (Athens local strings converted to UTC for cross-source ordering, then file order). All conflicting decisions are listed below and in owner_conflicts.jsonl. Output type uses the unchanged `cells_opus/scripts/common.py::output_type(text)`, also underlying Q1: decimal digits plus its exact separator list or canonical uppercase Latin Roman numerals are numeric; otherwise ≥1 digit and ≤2 Unicode letters is mixed; the rest is non-numeric. Character count is the native saved-Google counting function, not a new count for fitting.','',table(['ID','Chosen judgement','Conflicting sources'],[[c['line_id'],c['chosen'],c['judgments']] for c in small_conflicts]),'','### Local fits, refit separately per box','','Only SHA-verifiable local small numeric crop IDs are fitted. Inputs include 150 + 888 + 250, all 437 typology crops including controls, and 134 additional cells_opus/crops IDs. Duplicates are fitted once. Contact sheets, report illustrations and the test_tmp SHA-mismatch fixture are not independent crop/text/hash inputs. The frozen census table was read only to recover hashes/text for that finite list of extra local PNGs; no census tool execution or fetch ran. All 1,103 paths in the four direct crop directories are accounted for: 1,089 match measured-pool SHA records, and the other 14 are nine-character numeric crops outside the definition. [Path-level coverage](local_crop_coverage.jsonl), [local inventory](local_crop_inventory.json), [extra measurements](extra_numeric.jsonl), [fit IDs](numeric_fits.json).','','S3 ratio is its existing predictor input max(row-frame length,height)/min(length,height). S4 ratio is all-component width/height in the processed crop frame, including when width < height. The old text-font predictor retains its text-box fit. Both numeric lines use OLS ratio = a·chars + b with residual SD ddof=2 and unscaled median absolute deviation about the residual median, matching cells_opus. The without-owner fit excludes every ID with an explicit mark or rating and is used in the primary 2×2; the all-crops fit is also reported. Supplemental S3 boxes for gate-blocked crops are fit diagnostics only; their gate stays UNCERTAIN/DROP in the 2×2. A missing S3 text box contributes no S3 ratio.','',table(['Box','Fit population','n','a','b','Residual SD','MAD','Sources'],[[box,kind,*[fits[box][kind][k] for k in ('n','a','b','residual_SD','MAD')],fits[box][kind]['source_counts']] for box in ('s3','s4') for kind in ('all','without_owner')]+[['crop dimensions','reference',36307,.460,.787,.634,.236,'historical reference only']]),'',f"Unique local small numeric crops: {len(numeric)}; sources: {dict(Counter(r['cohort'] for r in numeric))}. Missing measurable boxes: S3 {len(numeric)-fits['s3']['all']['n']}, all-ink {len(numeric)-fits['s4']['all']['n']}. Without-owner n<100 flags: S3 {fits['s3']['without_owner']['n']<100}, S4 {fits['s4']['without_owner']['n']<100}.",'','### Primary 2×2 (without-owner numeric fits)','','For each box, pred = (ratio−b)/a is supplied to the unchanged rule-2 function, retaining its (chars+1)/(pred+1) 0.5–1.5 interval and its existing negative/unavailable prediction handling. Gate and padding stay exactly those of the box’s version. No numeric line is added to the tool. Each cell below shows n, agreement and all six tool-verdict × owner-verdict counts. Every numeric cell has n=144, so none has fewer than 30 numeric crops. Mixed cells have only three crops and are additionally marked indicative only. Other types are evaluated on their own output type; the numeric training-fit n is reported above.','']
 for kind in ('without_owner','all'):
  lines+=['### '+kind+' fit cells','',table(['Type','Box / expected length','n','Agree','Numeric n','Flag','KEEP vs owner K/D','DROP vs owner K/D','UNC vs owner K/D'],[[t,k,s['n'],s['agreement'],s['numeric_n'],'indicative only' if s['indicative_only'] else '',*[str(s['confusion'][v]['KEEP'])+'/'+str(s['confusion'][v]['DROP']) for v in VERDICTS]] for t,group in matrix[kind].items() for k,s in group.items()]),'']
 lines+=['### Every box / expectation flip','','All swaps below retain the owner mark and use the primary without-owner fits. The all-crops-fit swaps are also saved in two_by_two_flips.jsonl.','',table(['Type','ID','Comparison','Owner','Before','After'],[[s['type'],s['line_id'],s['comparison'],s['owner']['owner_mark'],s['before'],s['after']] for s in swaps if s['fit']=='without_owner']),'']
 for t,keys in best.items():
  n=matrix['without_owner'][t][keys[0]]['n'];agree=matrix['without_owner'][t][keys[0]]['agreement'];lines+=[f"For {t}, the greatest observed owner agreement is {agree}/{n}, in "+', '.join(keys)+'.','']
 lines+=['## Small-segment diagnostics','',f"Main replay has {len(smallmain)} small cohort records; typology has {len(smalltyp)}. Ratios include diagnostic boxes on blocked rows where measurable; they do not change gate evidence.",'',table(['S3','S4','S3 reason','S4 reason','n'],[[*key,n] for key,n in transitions.items()]),'',table(['Population','Distribution','n','Quantiles 0/10/25/50/75/90/95/99/100'],[[name,kind,q['n'],q['quantiles']] for name,ds in distributions.items() for kind,q in ds.items()]),'','### Huge few-character witnesses','','The four owner-named huge few-character witnesses are shown, together with any other small crop with processed short side at least 400 px (display diagnostic only). Source/processed sizes and all boxes are in small.jsonl.','',table(['Set','ID','Text','Crop w×h','Processed w×h','Chars','A','S3 → S4','All-ink box','Reason'],[[s['cohort'],s['line_id'],s['text'],str(s['width'])+'×'+str(s['height']),str(s['processed_width'])+'×'+str(s['processed_height']),s['chars'],s['A'],s['before']+' → '+s['after'],s['s4_box']['diagnostic_all_ink_box'],s['new_reason']] for s in huge]),'','## Readback and source scope','',table(['Check','Count'],list(checks.items())+[['tests passed',tests]]),'','Every non-small record has byte-identical canonical evidence, binding, frame, warnings, policy hash and final result compared with fresh S3 and saved S3; only tool_version and inherited elapsed seconds are excluded, exactly as in the earlier replay normalization. The three JS policy functions and their file hash are unchanged. Every final result, gate and available predictor result was independently read back. The all-component boxes and matching box/frame padding heights are checked directly.','','Changed existing files (exhaustive scope guard):','',*[f'- `{p}`' for p in changed],'','New test: `tests/test_seg_small.py`. Existing historical row-frame tests explicitly isolate their historical path; curved/tall synthetic rows now use nine characters to remain outside S4. The new tests cover inclusive boundaries, every component including a diacritic and isolated extracted speck, actual turned crops, padding, and positive gate DROPs with no main row. All native non-small rows are checked against S3 as the population regression. Existing extraction omits area<3 noise; it is unchanged.','','No .git writes, commits, pushes, reader runs, remote execution or network access. Package, seg09 and untracked census02 evidence match initial hashes. Metadata refreshes segmentation to 0.9-s4 and the existing census dependency fingerprint only; no census version bump or execution. The lead commits.','','Reproduce with sibling sol-recut .venv/bin/python, -B, PYTHONPATH=. and PYTHONDONTWRITEBYTECODE=1: s4/prepare_versions.py; s4/replay.py; s4/replay.py typology; s4/extra_numeric.py; the test command recorded in tests_command.txt; s4/validate_report.py. Clear only generated replay.jsonl before a fresh full run (otherwise it resumes verified complete records). Never recreate initial_hashes.json or baseline/ after source changes.','','[Summary](summary.json), [receipt](receipt.json), [scope guard](scope_guard.json), [main replay](replay.jsonl), [typology replay](typology_replay.jsonl), [small diagnostics](small.jsonl), [2×2 predictions](two_by_two_predictions.jsonl), [2×2 flips](two_by_two_flips.jsonl), [tests](tests.log).','',last]
 (D/'REPORT.md').write_text('\n'.join(lines)+'\n')
 inputs=[BASE/'owner_marks_20261019.jsonl',SS/'owner_marks_smallseg.jsonl',SS/'samples.jsonl',SS/'sheet/card_manifest.json',SS/'NOTE_steps45_length_exempt.md',SS/'SMALL_SEGMENTS.md',SS/'q1/Q1_TABLES.md',BASE/'cells_opus/scripts/common.py',BASE/'cells_opus/scripts/analyse.py',BASE/'cells_opus/size_vs_output.md',BASE/'cells/population_cells.jsonl.gz',D.parent/'s3/replay.jsonl',predictor_binary()]
 dump(D/'input_hashes.json',{str(p):sha(p) for p in inputs if p.exists()})
 write(D/'crop_bindings.jsonl',[dict(cohort=r['cohort'],line_id=r['line_id'],path=r['row']['crop_path'],sha256=sha(r['row']['crop_path'])) for r in rs+ts+extra])
 git_env=dict(s1.os.environ,GIT_OPTIONAL_LOCKS='0')
 git_state={k:subprocess.check_output(['git','--no-optional-locks',*args],cwd=R,env=git_env,text=True).strip() for k,args in [('branch',['branch','--show-current']),('head',['rev-parse','HEAD'])]}
 assert git_state['branch']=='opus/seg-census'
 receipt=dict(status='PASS',git_state=git_state,timestamp=datetime.datetime.now(ZoneInfo('Europe/Athens')).isoformat(),summary=summary,scope_guard=guard,source_sha256={p:sha(R/p) for p in changed+sorted(added)},artifacts={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ('receipt.json','validation.log')},network='OFF via S1 socket audit hook',readers=0,git_writes=False,native_replay=json.loads((D/'replay_receipt.json').read_text()))
 dump(D/'receipt.json',receipt);print(last)
if __name__=='__main__':run()
