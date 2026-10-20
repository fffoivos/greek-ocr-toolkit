"""S3 exact readback, unchanged scoring, scope guard, overlay and receipt."""
from replay import *
from greekocr.harvest.predictor_path import predictor_binary
import ast,re,subprocess
from PIL import Image,ImageDraw,ImageFont

BASE=R.parent/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'
VERS=('08','s1','s2','s3')

def table(head,rs):
 def cell(a):return str(a).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(cell(a) for a in row)+' |' for row in rs])

def overlay(r):
 w=worker();c={};capture(w,c)
 try:
  s2.context(w,r);z=w(r['row']);assert s2.norm(z)==s2.norm(r['after'])
  g=c['g'];base=c['main'].base;cs=[a for a in c['components'] if a['role'] in w.crop_tools.TEXT_ROLES]
  yy,xx=np.nonzero(np.isin(g.labels,[a['index'] for a in cs]))
  ss,nn,half,amb=w.crop_tools.curve_coordinates(xx+.5,yy+.5,base)
  old=r['before']['evidence']['box_evidence']['row_frame'];new=z['evidence']['box_evidence']['row_frame']
  font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',14)
  pad=35;sn=new['sn_box'];height=int(np.ceil(sn[3]-sn[1]));width=max(g.width,int(np.ceil(sn[2]-sn[0]))+2*pad)
  canvas=Image.new('RGB',(width,g.height+height+180),'white');pen=ImageDraw.Draw(canvas)
  image=Image.open(r['row']['crop_path']).convert('RGB')
  if r['turned']:image=image.transpose(Image.Transpose.ROTATE_270)
  canvas.paste(image,(0,55));pen.text((8,5),r['line_id']+' | owner KEEP',font=font,fill='black')
  pen.text((8,27),'Red: detector base curve. Blue: S2 single-angle box.',font=font,fill='black')
  pen.line([(float(x),float(y)+55) for x,y in enumerate(base)],fill='red',width=2)
  pen.line([(float(x),float(y)+55) for x,y in old['corners']+old['corners'][:1]],fill='blue',width=2)
  ytop=g.height+110
  pen.text((8,g.height+73),'Unrolled selected ink (s, n); green: S3 pixel-cell box. n increases down.',font=font,fill='black')
  pixels=canvas.load()
  for s,n in zip(ss,nn):
   x=int(round(s-sn[0]+pad));y=int(round(n-sn[1]+ytop))
   if 0<=x<width and 0<=y<canvas.height:pixels[x,y]=(20,20,20)
  pen.rectangle((pad,ytop,pad+sn[2]-sn[0],ytop+sn[3]-sn[1]),outline='green',width=2)
  path=D/'overlays'/f"{r['line_id']}.png";path.parent.mkdir(exist_ok=True);canvas.save(path)
  dump(D/'witness_geometry.json',dict(base_curve=[[i,float(y)] for i,y in enumerate(base)],support=[c['main'].x0,c['main'].x1],degree=g.band.degree,old_row_frame=old,new_row_frame=new,components=cs,selected_ink_pixels=len(xx),ambiguous_foot_pixels=amb))
 finally:w.close()
 return str(path.relative_to(D))

def run():
 rs=read(D/'replay.jsonl');curves=read(D/'curvature.jsonl');assert len(rs)==len(curves)==1288
 marks=read(BASE/'owner_marks_20261019.jsonl');latest={}
 for i,m in enumerate(marks):
  old=latest.get(m['line_id'])
  if old is None or (m['updated'],i)>=(old['updated'],old['file_line']):latest[m['line_id']]=dict(m,file_line=i)
 write(D/'owner_marks_snapshot.jsonl',marks)
 assert len(marks)==240 and len(latest)==235
 w=worker();checks=Counter();straight=[]
 try:
  for r,c in zip(rs,curves):
   assert (r['cohort'],r['line_id'])==(c['cohort'],c['line_id'])
   assert r['before']['evidence']['gate']==r['after']['evidence']['gate']
   for key in ('before','after'):
    z=r[key];e=z['evidence'];decision=w.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=e))
    assert (decision['verdict'],decision['reason'])==(z['verdict'],z['reason'])
    gate=w.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=dict(e,gate_only=True)))
    assert gate==e['gate'];checks['gate_and_verdict_exact_readbacks']+=1
    if e['box_evidence']['available']:
     rf=e['box_evidence']['row_frame'];pred=w.predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=r['row'].get('script_class','pooled')))
     assert pred==e['box_evidence']['prediction'];checks['predictor_exact_readbacks']+=1
     p=e['padding_evidence'];assert p['row_frame_height']==rf['height']
     assert p['total_padding_line_heights']==(r['after']['frame']['height']-p['upright_box_height'])/rf['height']
   if c['straight']:
    assert s2.norm(r['before'])==s2.norm(r['after'])
    assert metrics(r['before'])==metrics(r['after'])
    encoded=lambda a:json.dumps(a,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    assert encoded(r['before']['evidence'])==encoded(r['after']['evidence'])
    straight.append(r);checks['straight_byte_identical']+=1
   assert c['before']==metrics(r['before']) and c['after']==metrics(r['after'])
 finally:w.close()
 summaries={}
 for name,n in [('segeval1',150),('calibration',888),('cells',250)]:
  pop=[r for r in rs if r['cohort']==name];assert len(pop)==n
  su=dict(rows=n,straight=sum(r['curve']['straight'] for r in pop),curved=sum(not r['curve']['straight'] for r in pop),transitions=dict(Counter(r['verdict_s2']+'->'+r['verdict_s3'] for r in pop)))
  if name=='segeval1':
   su['confusion']={v:s1.g.confusion([dict(r,verdict_09=r['verdict_'+v]) for r in pop],'09') for v in VERS}
   su['errors']={v:dict(FP=c['DROP']['fine'],FN=c['KEEP']['faulty'],UNC=sum(c['UNCERTAIN'].values())) for v,c in su['confusion'].items()}
   for r in pop:assert s1.g.owner_state(dict(reader_answer=r['reader_answer']))[0]==r['owner_standard_state']
  if name=='calibration':
   rated=[r for r in pop if r.get('owner_rating') and r['owner_rating'].get('decision') in ('KEEP','DROP')];assert len(rated)==135
   su['rated_agreement']={v:sum(r['verdict_'+v]==r['owner_rating']['decision'] for r in rated) for v in VERS}
   su['rated_confusion']={v:{ver:{mark:sum(r['verdict_'+v]==ver and r['owner_rating']['decision']==mark for r in rated) for mark in ('KEEP','DROP')} for ver in ('KEEP','DROP','UNCERTAIN')} for v in VERS}
  summaries[name]=su
 unique={}
 for r in rs:
  if r['line_id'] in unique:assert all(r['verdict_'+v]==unique[r['line_id']]['verdict_'+v] for v in VERS)
  unique[r['line_id']]=r
 assert set(latest)<=set(unique)
 marked=[r for rid,r in unique.items() if rid in latest];assert len(marked)==235
 owner=dict(entries=len(marks),distinct_ids=len(latest),agreement={v:sum(r['verdict_'+v]==latest[r['line_id']]['owner_mark'] for r in marked) for v in VERS},confusion={v:{ver:{mark:sum(r['verdict_'+v]==ver and latest[r['line_id']]['owner_mark']==mark for r in marked) for mark in ('KEEP','DROP')} for ver in ('KEEP','DROP','UNCERTAIN')} for v in VERS})
 flips=[]
 for r,c in zip(rs,curves):
  if r['verdict_s2']!=r['verdict_s3']:
   flips.append(dict(cohort=r['cohort'],line_id=r['line_id'],verdict_s2=r['verdict_s2'],verdict_s3=r['verdict_s3'],owner_standard_state=r.get('owner_standard_state'),owner_rating=r.get('owner_rating'),owner_mark=latest.get(r['line_id']),curve_deviation_px=c['max_chord_deviation_px'],before=c['before'],after=c['after'],reason_s2=r['before']['reason'],reason_s3=r['after']['reason']))
 write(D/'flips.jsonl',flips)
 changed=[c for c in curves if c['measurement_changed']];assert all(not c['straight'] for c in changed)
 vals=[c['max_chord_deviation_px'] for c in curves if c['available']]
 distribution=dict(count=len(vals),quantiles_px={str(p):float(np.percentile(vals,p)) for p in (0,25,50,75,90,95,99,100)},curved_quantiles_px={str(p):float(np.percentile([c['max_chord_deviation_px'] for c in curves if not c['straight']],p)) for p in (0,25,50,75,90,95,99,100)},detector_degrees=dict(Counter(str(c['detector_degree']) for c in curves)))
 witness_id='ia_poly1850--df8f2267db2b7275--s025-l0037';wr=unique[witness_id];assert latest[witness_id]['owner_mark']=='KEEP'
 witness=dict(line_id=witness_id,owner_mark=latest[witness_id],before=metrics(wr['before']),after=metrics(wr['after']),curve=wr['curve'],overlay=overlay(wr));dump(D/'witness.json',witness)
 # Every pre-existing tracked and protected evidence file, measured before edits.
 initial=json.loads((D/'initial_hashes.json').read_text());changed_source=[p for p,h in initial.items() if not (R/p).is_file() or sha(R/p)!=h]
 allowed=['greekocr/glyphs/components.py','docs/harvest/line_pipeline/tool_versions.json','greekocr/harvest/filtering_assets/crop-tools.py','greekocr/harvest/line_pipeline_native.py','scripts/harvest/build_filter_versions.py']
 assert sorted(changed_source)==sorted(allowed),changed_source
 oldv=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text());newv=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())
 assert [k for k in newv['tools'] if oldv['tools'][k]!=newv['tools'][k]]==['segmentation','census']
 for name in ('segmentation','census'):
  tool=newv['tools'][name]
  assert tool['digest']==hashlib.sha256(json.dumps(tool['components'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
  for p,h in tool['components'].items():
   rel=p.removeprefix('greek-ocr-toolkit-sol-recut/');local=R/rel
   if local.is_file():assert sha(local)==h,(name,rel)
 assert newv['tools']['census']['version']==oldv['tools']['census']['version']
 # Scope of old production functions is independently constrained through AST.
 def functions(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
 oldf=functions(D/'baseline/greekocr/harvest/filtering_assets/crop-tools.py');newf=functions(R/'greekocr/harvest/filtering_assets/crop-tools.py')
 assert [k for k in oldf if oldf[k]!=newf[k]]==['features_from_observation']
 assert set(newf)-set(oldf)=={'curve_coordinates','curve_tight_box'}
 # The native source delta is only explicit geometry arguments at Stage B.
 oldnative=(D/'baseline/greekocr/harvest/line_pipeline_native.py').read_text();newnative=(R/'greekocr/harvest/line_pipeline_native.py').read_text()
 assert newnative.replace(',\n                base_curve=main.base if main is not None else None, base_is_straight=(glyphs.band.curve_is_straight\n                    if glyphs.band.curve_is_straight is not None else glyphs.band.degree != 2)','')==oldnative
 oldcomponents=(D/'baseline/greekocr/glyphs/components.py').read_text()
 newcomponents=(R/'greekocr/glyphs/components.py').read_text()
 stripped=newcomponents.replace("    # Construction provenance only: degree=1 may also describe a mildly bent\n    # tracked polyline. Consumers must not flatten that geometry.\n    curve_is_straight: bool | None = None\n\n",'')
 stripped=re.sub(r'^ +curve_is_straight = (?:deg != 2|False|True)\n','',stripped,flags=re.MULTILINE)
 stripped=stripped.replace('Band(top, bottom, xh, len(support), support, deg, xh_source, curve_is_straight)','Band(top, bottom, xh, len(support), support, deg, xh_source)')
 assert stripped==oldcomponents,'detector algorithm source changed'
 guard=dict(status='PASS',changed_source_files=changed_source,new_test_files=['tests/test_seg_curve.py'],unchanged_initial_files=len(initial)-len(changed_source),protected_paths_unchanged=['docs/harvest/seg_census/package/','docs/harvest/seg09/','docs/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl'],all_js_unchanged=True,detector_geometry_and_decisions_unchanged=True,detector_construction_metadata_only=True,predictor_unchanged=True,census_version_unchanged=True,census_dependency_fingerprint_refreshed=True,git_writes=False,readers=0,network='OFF')
 dump(D/'scope_guard.json',guard)
 testslog=(D/'tests.log').read_text();assert 'failed' not in testslog;tests=int(re.search(r'(\d+) passed',testslog)[1])
 summary=dict(version='0.9-s3',cohorts=summaries,owner_marks=owner,straight_identity=dict(passed=len(straight),total=sum(c['straight'] for c in curves)),curvature=distribution,curved_rows_changed=len(changed),curved_unique_ids_changed=len({c['line_id'] for c in changed}),ambiguous_foot_pixels=sum(c['ambiguous_foot_pixels'] for c in curves),flips=len(flips),unique_flipped_ids=len({f['line_id'] for f in flips}),readback=dict(checks),tests=tests,witness=witness)
 dump(D/'summary.json',summary)
 inputs=[D.parent/'s1/replay.py',D.parent/'s2/replay.py',D.parent/'s2/replay.jsonl',BASE/'owner_marks_20261019.jsonl',BASE/'cells/population_cells.jsonl.gz',s1.S/'gate2/replay.py',predictor_binary()]
 dump(D/'input_hashes.json',{str(p):sha(p) for p in inputs});write(D/'crop_bindings.jsonl',[dict(cohort=r['cohort'],line_id=r['line_id'],path=r['row']['crop_path'],sha256=sha(r['row']['crop_path'])) for r in rs])
 err=lambda e:'/'.join(str(e[k]) for k in ('FP','FN','UNC'))
 e=summaries['segeval1']['errors'];rated=summaries['calibration']['rated_agreement'];agree=owner['agreement']
 last=f"SEG S3 READY: straight identity {len(straight)}/{summary['straight_identity']['total']}; witness l0037 ratio {witness['before']['ratio']} → {witness['after']['ratio']} ({witness['before']['verdict']} → {witness['after']['verdict']}); curved rows changed {len(changed)}; 150 FP/FN/UNC {err(e['s2'])} → {err(e['s3'])}; 888 rated agree {rated['s2']} → {rated['s3']}/135; owner marks agree {agree['s2']} → {agree['s3']}/235; flips {len(flips)}; tests {tests} passed"
 lines=['# SEG step 3 — 0.9-s3','','Main-row TEXT_ROLES ink is measured in the existing detector base curve’s arc-length/normal frame. Detector geometry and decisions, inventory, gate, predictor, length interval, padding formula and the S2 clockwise turn are unchanged. No fit, smoothing, tunable parameter, guard or decision threshold was added. All curvature and foot-ambiguity counts are diagnostics.','','## Geometry and exact straight identity','','`text_lines` supplies a per-x `base` array (the main band bottom); `skew_line` references that same array. The representation is not only an angle: it can contain the existing quadratic or locally tracked piecewise-linear bend. S3 joins successive supplied column samples as segments, projects each selected ink pixel centre onto every segment, and chooses its nearest foot. Cumulative segment lengths give s; signed nearest distance gives n (positive below the base). Equal-distance distinct feet select the first in curve order; shared vertices are one foot. The stored per-column domain is finite [0, width−1], with no new extrapolation.','','Each centre contributes the same 0.6 unit pixel-cell projected half extent, (|tangent.x|+|tangent.y|)/2, to each coordinate at its selected segment. The extrema of these cells give the s and n extents. Existing TEXT_ROLES selection is retained exactly; no component is reassigned or newly filtered. The upright box remains the padding envelope. Rule 2 receives the new extents through the unchanged max/min predictor call; rule 3 divides its unchanged padding numerator by the n extent.','','The detector now exposes only its existing construction provenance as Band.curve_is_straight. Actual straight/constant constructions use the original tight_box rotation and its original operation order; every tracked polyline uses its supplied samples even if the existing approximate degree flag is 1. No numerical tolerance is accepted. The preflight independently compared complete feature objects before the S3 replay; the replay/readback then compared canonical evidence bytes, result, frame, warnings, long side, short side, ratio and padding. Only the required tool_version differs. **'+str(len(straight))+'/'+str(len(straight))+' straight rows match S2 exactly.** Degree 1 in the detector can in principle mean approximately straight. S3 uses the actual construction provenance without fitting another curve. Construction metadata agrees with the degree flags on all 1,288 replay rows; a synthetic tracked degree-1 curve is explicitly tested in both horizontal and turned frames.','','## Replay and unchanged scoring','','The same S1 input builder, native adapter workflow, source-context selection, frozen predictor and 120-second per-row bound are reused. Fresh native S2 matches all 1,288 saved S2 records before any S3 replay. The 150 use the full saved reader answers and gate2 owner_state (positive faults win over unknowns); FP is DROP/fine, FN is KEEP/faulty, UNC is every UNCERTAIN. No reader ran. The 888 use only owner_rating.decision on the same 135 rated rows. Cells have no inferred labels. The 240 explicit mark entries yield 235 IDs, scored once with latest timestamp then file order winning.','','0.8 retains the saved S1 native baseline, including its historical 18/14/11 full-population score.','',table(['Metric','0.8','0.9-s1','0.9-s2','0.9-s3'],[['150 FP/FN/UNC',*[err(e[v]) for v in VERS]],['888 rated agreement /135',*[rated[v] for v in VERS]],['Owner marks agreement /235',*[agree[v] for v in VERS]]]),'',table(['Set','Rows','Straight','Curved','S2 → S3 transitions'],[[k,v['rows'],v['straight'],v['curved'],v['transitions']] for k,v in summaries.items()]),'']
 for v in VERS:
  lines += [f'### {v} confusion readback','',table(['150 verdict','fine','faulty','unresolved'],[[ver,*[summaries['segeval1']['confusion'][v][ver][label] for label in ('fine','faulty','unresolved')]] for ver in ('KEEP','DROP','UNCERTAIN')]),'',table(['888 verdict','owner KEEP','owner DROP'],[[ver,*[summaries['calibration']['rated_confusion'][v][ver][mark] for mark in ('KEEP','DROP')]] for ver in ('KEEP','DROP','UNCERTAIN')]),'',table(['Marked verdict','owner KEEP','owner DROP'],[[ver,*[owner['confusion'][v][ver][mark] for mark in ('KEEP','DROP')]] for ver in ('KEEP','DROP','UNCERTAIN')]),'']
 lines+=['## Owner-KEEP witness l0037','','`'+witness_id+'` — the owner mark is KEEP. No witness-specific rule or repair was applied.','',table(['Version','Long side','Short side','Ratio','Padding','Verdict'],[[v,*[witness[k][f] for f in ('long_side','short_side','ratio','padding','verdict')]] for v,k in [('0.9-s2','before'),('0.9-s3','after')]]),'',f"Supported base range: {witness['curve']['baseline_range_px']} px; maximum perpendicular chord deviation: {witness['curve']['max_chord_deviation_px']} px. The historical 41 px sag / 92 px box / 57 px line observation is owner context; the table contains fresh native measurements. The detector baseline contains local bends visible in red, and S3 preserves them exactly. Its 82.94 px n extent is not asserted to recover the observed 57 px line. The saved historical 150 owner-standard label is faulty while the explicit owner mark is KEEP: this flip increases historical FN by one and explicit marked agreement by one.",'',f"![Witness base, old box and unrolled box]({witness['overlay']})",'','[Exact witness measurements](witness.json), [full baseline and boxes](witness_geometry.json).','','## Curvature diagnostic','','Per-row chord deviation is the largest absolute perpendicular distance between the supplied baseline and its endpoint chord over the unchanged main-row support [x0,x1]. Every replay row is in [curvature.jsonl](curvature.jsonl), including blocked gates and the exact measurement changes. No deviation threshold affects a verdict. Counts refer to cohort records; overlapping IDs are separately counted in the summary.','',table(['Percentile','All rows, px','Detector-curved rows, px'],[[p,distribution['quantiles_px'][str(p)],distribution['curved_quantiles_px'][str(p)]] for p in (0,25,50,75,90,95,99,100)]),'',f"Detector degrees: {distribution['detector_degrees']}. Curved measurement changes: {len(changed)} records / {summary['curved_unique_ids_changed']} unique IDs. Ambiguous foot pixels: {summary['ambiguous_foot_pixels']}. Gate-blocked rows retain unavailable Stage-B measurement; their geometric deviations are still recorded.",'','### Every changed measurement','','Deltas are S3 − S2.','',table(['Set','ID','Chord deviation px','Δ long','Δ short','Δ ratio','Δ padding'],[[c['cohort'],c['line_id'],c['max_chord_deviation_px'],*[c['delta'][k] for k in ('long_side','short_side','ratio','padding')]] for c in changed]),'','## Every S2 → S3 verdict flip','',table(['Set','ID','S2','S3','Owner state / rating / latest mark','Chord deviation px','S2 reason','S3 reason'],[[f['cohort'],f['line_id'],f['verdict_s2'],f['verdict_s3'],'; '.join(str(a) for a in [f.get('owner_standard_state'),(f.get('owner_rating') or {}).get('decision'),(f.get('owner_mark') or {}).get('owner_mark')] if a) or 'unrated',f['curve_deviation_px'],f['reason_s2'],f['reason_s3']] for f in flips]),'','[Full flips with before/after measurements](flips.jsonl).','','## Readback, scope and receipt','',table(['Check','Count'],list(checks.items())+[['tests passed',tests]]),'','Every straight row has byte-identical canonical evidence and exact final result after excluding only tool_version and the inherited orientation seconds normalization (S2 produces no elapsed orientation fields here). [Straight evidence hashes](straight_readback.jsonl). Every gate/final result and available predictor result was independently recomputed from stored evidence.','','Changed existing source files (exhaustive):','',*[f'- `{p}`' for p in changed_source],'','New test file: `tests/test_seg_curve.py`. New evidence scripts and baseline copies live only under S3. In crop-tools only features_from_observation changes among existing functions; curve_coordinates and curve_tight_box are added. NativeSegmenter only passes the detector’s base array and construction flag to Stage B. components.py records which existing construction was selected; it changes no fitting, detector choices, geometry or roles. TEXT_ROLES, inventory, gate, orientation/refocus, all JS, predictor and all other initial files are unchanged. The segmentation fingerprint includes its changed native adapter. The census version remains 0.5; its existing dependency fingerprint for that same adapter is refreshed to avoid a stale source hash. No census execution occurred. Other tools’ metadata is unchanged.','','Tests reuse the sibling venv and historical test_line_pipeline.py read-only, with this checkout first on PYTHONPATH, bytecode/cache writes disabled, offline fixtures and a socket audit hook for replay/readback. Synthetic fixtures cover 0°, 1.2°, −3° exact straight boxes, known-radius circular arc length within 1 px, curve pixel-cell extents, ambiguous feet in curve order, h ≤ w and S2-turned crops, including a tracked nonlinear curve with the detector’s approximate degree-1 flag.','','[Scope guard](scope_guard.json), [initial hashes](initial_hashes.json), [input hashes](input_hashes.json), [crop bindings](crop_bindings.jsonl), [native replay](replay.jsonl), [summary](summary.json), [receipt](receipt.json), [tests](tests.log). Protected package, seg09 and untracked census02 evidence bytes match their before-change hashes. Network OFF; no readers, remote compute, .git writes, commits or pushes. The lead commits.','','Reproduce with the sibling sol-recut .venv/bin/python, -B and PYTHONPATH=.: s3/prepare_versions.py; s3/replay.py preflight; s3/replay.py run; s3/validate_report.py. Never recreate initial_hashes.json or baseline/ after changes.','',last]
 (D/'REPORT.md').write_text('\n'.join(lines)+'\n')
 git_env=dict(s1.os.environ,GIT_OPTIONAL_LOCKS='0')
 git_state={k:subprocess.check_output(['git',*args],cwd=R,env=git_env,text=True).strip() for k,args in [('branch',['branch','--show-current']),('head',['rev-parse','HEAD'])]}
 assert git_state['branch']=='opus/seg-census'
 receipt=dict(status='PASS',git_state=git_state,timestamp=subprocess.check_output(['date','+%Y-%m-%dT%H:%M:%S%z'],text=True).strip(),summary=summary,scope_guard=guard,source_sha256={p:sha(R/p) for p in allowed+['tests/test_seg_curve.py']},artifacts={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ('receipt.json','validation.log')},native_replay=json.loads((D/'replay_receipt.json').read_text()),identity_preflight=json.loads((D/'preflight_receipt.json').read_text()))
 dump(D/'receipt.json',receipt);print(last)
if __name__=='__main__':run()
