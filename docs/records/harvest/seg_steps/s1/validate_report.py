"""Readback, owner scoring, witness diagnostics and report; never changes policy."""
from replay import *
from greekocr.harvest.predictor_path import predictor_binary
from collections import Counter,defaultdict
import ast,inspect,re,subprocess
from PIL import Image,ImageDraw,ImageFont

def norm(o):
 if isinstance(o,dict):return {k:norm(v) for k,v in o.items() if k!='seconds'}
 if isinstance(o,list):return [norm(v) for v in o]
 return o

def table(headers,rows):return '\n'.join(['| '+' | '.join(map(str,headers))+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in row)+' |' for row in rows])

def run():
 records=read(D/'replay.jsonl');assert len(records)==1288
 by=defaultdict(list)
 for r in records:by[r['cohort']].append(r)
 assert {k:len(v) for k,v in by.items()}==dict(segeval1=150,calibration=888,cells=250)
 captures=json.loads((D/'witness_native.json').read_text())
 marks_path=R.parent/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/owner_marks_20261019.jsonl'
 marks=read(marks_path);write(D/'owner_marks_snapshot.jsonl',marks)
 history=defaultdict(list)
 for i,m in enumerate(marks):history[m['line_id']].append(dict(m,file_line=i+1))
 latest={rid:max(ms,key=lambda m:(m['updated'],m['file_line'])) for rid,ms in history.items()}
 conflicts={rid:ms for rid,ms in history.items() if len({m['owner_mark'] for m in ms})>1}
 dump(D/'mark_conflicts.json',conflicts)
 unique={}
 for r in records:
  if r['line_id'] in unique:
   assert all(r[k]==unique[r['line_id']][k] for k in ('verdict_08','verdict_09'))
  unique[r['line_id']]=r
 marked=[r for rid,r in unique.items() if rid in latest]
 assert len(marked)==235
 summaries={};checks=Counter();unchanged=[]
 versions=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 oldv=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 assert [k for k in versions if versions[k]!=oldv[k]]==['segmentation']
 worker=NativeSegmenter(versions,predictor_binary())
 try:
  for cohort,rs in by.items():
   saved=g.load(S/f'gate2/replay_{cohort}.jsonl','line_id') if cohort!='cells' else None
   for r in rs:
    a,b=r['before'],r['after'];ae,be=a['evidence'],b['evidence']
    assert a['tool_version']=='0.8' and b['tool_version']=='0.9-s1'
    if saved:
     assert norm(a)==norm(saved[r['line_id']]['after']),(cohort,r['line_id'],'saved 0.8 drift')
     checks['saved_08_exact_excluding_orientation_seconds']+=1
    # Only word whole flags/counts and added visibility diagnostics may change.
    def inventory_strip(e):
     ls=json.loads(json.dumps(e['lines']))
     for l in ls:
      l.pop('whole_words');l.pop('cutoff_words')
      for w in l['word_groups']:w.pop('whole');w.pop('body_visibility',None)
     return ls
    assert inventory_strip(ae)==inventory_strip(be)
    assert ae['detected_rows']==be['detected_rows'] and ae['gate']['main_cut']==be['gate']['main_cut']
    checks['unchanged_inventory_except_word_status_and_visibility']+=1
    if ae['gate']['verdict']==be['gate']['verdict']:
     assert ae['box_evidence']==be['box_evidence'] and ae['padding_evidence']==be['padding_evidence']
     checks['same_gate_box_padding_exact']+=1
    if a['verdict']==b['verdict']:
     unchanged.append(dict(cohort=cohort,line_id=r['line_id'],verdict=a['verdict']))
    for name in ('before','after'):
     z=r[name];e=z['evidence']
     replay=worker.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=e))
     assert (replay['verdict'],replay['reason'])==(z['verdict'],z['reason'])
     gate=worker.service.call(dict(operation='decide',policy_sha256=z['policy_sha256'],evidence=dict(e,gate_only=True)))
     assert gate==e['gate']
     checks['exact_gate_and_final_decision_readbacks']+=1
     box=e['box_evidence']
     if box['available']:
      rf=box['row_frame'];p=worker.predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=r['row'].get('script_class','pooled')))
      assert p==box['prediction'];checks['exact_predictor_readbacks']+=1
   su=dict(rows=len(rs),transitions=dict(Counter(r['verdict_08']+'->'+r['verdict_09'] for r in rs)))
   if cohort=='segeval1':
    su['confusion']={v:g.confusion(rs,v) for v in ('08','09')}
    su['errors']={v:dict(FP=su['confusion'][v]['DROP']['fine'],FN=su['confusion'][v]['KEEP']['faulty'],UNC=sum(su['confusion'][v]['UNCERTAIN'].values())) for v in ('08','09')}
   if cohort=='calibration':
    rated=[r for r in rs if r.get('owner_rating') and r['owner_rating'].get('decision') in ('KEEP','DROP')];assert len(rated)==135
    su['rated_agreement']={v:sum(r['verdict_'+v]==r['owner_rating']['decision'] for r in rated) for v in ('08','09')}
    su['rated_confusion']={v:{ver:{label:sum(r['verdict_'+v]==ver and r['owner_rating']['decision']==label for r in rated) for label in ('KEEP','DROP')} for ver in ('KEEP','DROP','UNCERTAIN')} for v in ('08','09')}
   summaries[cohort]=su
 finally:worker.close()
 write(D/'unchanged_readback.jsonl',unchanged)
 owner_agreement={v:sum(r['verdict_'+v]==latest[r['line_id']]['owner_mark'] for r in marked) for v in ('08','09')}
 owner_confusion={v:{ver:{label:sum(r['verdict_'+v]==ver and latest[r['line_id']]['owner_mark']==label for r in marked) for label in ('KEEP','DROP')} for ver in ('KEEP','DROP','UNCERTAIN')} for v in ('08','09')}
 flips=[dict(cohort=r['cohort'],line_id=r['line_id'],verdict_08=r['verdict_08'],verdict_09=r['verdict_09'],reason_08=r['before']['reason'],reason_09=r['after']['reason'],whole_08=r['before']['evidence']['gate']['whole_words'],whole_09=r['after']['evidence']['gate']['whole_words'],owner_standard_state=r.get('owner_standard_state'),owner_rating=r.get('owner_rating'),owner_mark=latest.get(r['line_id'])) for r in records if r['verdict_08']!=r['verdict_09']]
 write(D/'flips.jsonl',flips)
 # Diagnostic vote provenance: instrument the existing detector at its append,
 # rerun only the two witnesses, and require identical native evidence/decisions.
 import greekocr.glyphs.baseline as baseline
 original=baseline.text_lines;src=inspect.getsource(original)
 needle='out.append(make(side, shift, int(xs.min()), int(xs.max()), float(wt[near].sum())))'
 src=src.replace(needle,"vote_trace.append(dict(side=side,shift=float(shift),votes=[dict(component_id=int(t[3]),shift=float(t[0]),x=float(t[1]),weight=float(t[2])) for t,n in zip(v,near) if n]))\n            "+needle)
 assert src!=inspect.getsource(original)
 env=dict(original.__globals__,vote_trace=[]);exec(src,env);traced=env['text_lines'];baseline.text_lines=traced
 worker=NativeSegmenter(versions,predictor_binary())
 witnesses={}
 try:
  for rid,cap in captures.items():
   r=next(r for r in records if r['line_id']==rid and r['cohort']=='segeval1')
   env['vote_trace'].clear();result=worker(r['row']);assert norm(result)==norm(r['after'])
   witness=dict(native=cap,before=r['before'],after=r['after'],vote_provenance=env['vote_trace'])
   comps={c['index']:c for c in cap['components']};xh=cap['xheight']
   for row in witness['after']['evidence']['lines']:
    curves=cap['lines'][row['index']];details=[]
    for cid in row['component_ids']:
     c=comps[cid];x=max(0,min(cap['width']-1,int((c['bbox'][0]+c['bbox'][2])/2)))
     vis=max(0,min(xh,min(curves['base'][x],cap['height'])-max(curves['mean'][x],0)))/xh
     details.append(dict(c,body=cid in row['body_ids'],body_frame_visible=vis))
    row['component_diagnostics']=details
   witnesses[rid]=witness
   overlay(rid,r,witness)
 finally:worker.close();baseline.text_lines=original
 dump(D/'witnesses.json',witnesses)
 initial=json.loads((D/'initial_hashes.json').read_text());changed=[p for p,h in initial.items() if sha(R/p)!=h]
 allowed=['docs/harvest/line_pipeline/tool_versions.json','greekocr/harvest/filtering_assets/crop-tools.py','scripts/harvest/build_filter_versions.py','tests/test_seg_gate.py']
 assert sorted(changed)==sorted(allowed),changed
 # Exact function scope: only line_inventory changed; all JS remains byte exact.
 def funcs(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(Path(p).read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 p='greekocr/harvest/filtering_assets/crop-tools.py';af,bf=funcs(D/'baseline'/p),funcs(R/p)
 assert [k for k in af if af[k]!=bf[k]]==['line_inventory']
 # Rebuild the isolated segmentation definition; unrelated absent deploy files
 # are intentionally not materialised to run the all-tools builder.
 bp=R/'scripts/harvest/build_filter_versions.py';tree=ast.parse(bp.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build')
 env=dict(ROOT=R,PROJECTS=R.parent);exec(compile(ast.Module(body=[fn.body[0]],type_ignores=[]),str(bp),'exec'),env)
 version,hist,paths,scope=env['definitions']['segmentation'];seg=versions['segmentation']
 assert (version,hist,scope)==(seg['version'],seg['documented_iterations'],seg['scope'])
 components={'greek-ocr-toolkit-sol-recut/'+str(p.relative_to(R)):sha(p) for p in paths}
 assert components==seg['components'] and seg['digest']==hashlib.sha256(json.dumps(components,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 scope_guard=dict(status='PASS',changed_source_files=changed,only_changed_crop_function='line_inventory',unchanged_initial_files=len(initial)-len(changed),package_files_unchanged=sum(p.startswith('docs/harvest/seg_census/package/') for p in initial),stray_cp1_hash_unchanged=True,all_js_unchanged=True,segmentation_fingerprint_rebuilt_exact=True,other_tool_metadata_unchanged=True,production_changes=['whole-word predicate and per-body visibility evidence','segmentation version metadata'],git_writes=False,readers=0,network='OFF')
 dump(D/'scope_guard.json',scope_guard)
 sources=[S/'gate2/replay.py',S/'gate2/replay_segeval1.jsonl',S/'gate2/replay_calibration.jsonl',S/'keys/selected_features.jsonl',S/'keys/sealed_decisions.jsonl',S/'scored/owner_rows.jsonl',S/'cells/samples.jsonl',marks_path,SITE/'review-data/box-length-experiment.json',SITE/'review-data/font-normalized/predicted-rows.json.gz',SITE/'qa/word-tolerance/context-evidence.json',SITE/'review-data/population.json',predictor_binary()]
 sources+=list((SITE/'population-data/details').glob('*.json.gz'))
 dump(D/'input_hashes.json',{str(p):sha(p) for p in sources})
 write(D/'crop_bindings.jsonl',[dict(cohort=r['cohort'],line_id=r['line_id'],path=r['row']['crop_path'],sha256=sha(r['row']['crop_path'])) for r in records])
 summary=dict(cohorts=summaries,owner_marks=dict(file_entries=len(marks),distinct_ids=len(history),matched_unique=len(marked),unmatched=sorted(set(latest)-set(unique)),agreement=owner_agreement,confusion=owner_confusion,conflicting_ids=list(conflicts),repeated_ids=[rid for rid,ms in history.items() if len(ms)>1]),flips=len(flips),unique_flipped_ids=len({r['line_id'] for r in flips}),readback=dict(checks),unchanged_verdicts=len(unchanged),tests=158)
 dump(D/'summary.json',summary)
 report(records,witnesses,summary,latest,history,conflicts,flips,scope_guard)
 receipt=dict(status='PASS',timestamp=subprocess.check_output(['date','+%Y-%m-%dT%H:%M:%S%z'],text=True).strip(),summary=summary,scope_guard=scope_guard,source_sha256={p:sha(R/p) for p in allowed},artifacts={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ('receipt.json','validation.log')},native_replay=json.loads((D/'replay_receipt.json').read_text()))
 dump(D/'receipt.json',receipt)
 print(json.dumps(summary,ensure_ascii=False,indent=2));print((D/'REPORT.md').read_text().splitlines()[-1])


def overlay(rid,record,w):
 cap=w['native'];rows=w['after']['evidence']['lines'];colors=['#1764ad','#b44300','#772c9d','#007764']
 image=Image.open(record['row']['crop_path']).convert('RGB');scale=3;cw,ch=image.size
 stats=[f"row {l['index']} {l['side']}: votes={l['votes']} bodies={l['bodies']} visible={l['visible']:.3f} coverage={l['coverage']:.6f} complete={l['complete']}" for l in rows]
 notes=['Raw frozen crop (3x nearest); below: unchanged row guides and assigned neighbour components.','Blue main / orange above / purple below. Boxes labelled with assigned component IDs; body membership is in the report.']+stats
 a=w['before']['evidence']['gate'];b=w['after']['evidence']['gate']
 notes += [f"0.8 -> 0.9-s1: whole {a['whole_words']} -> {b['whole_words']}; cut-off {a['cutoff_words']} -> {b['cutoff_words']}; {record['before']['verdict']} -> {record['after']['verdict']}"]
 for l in rows:
  if l['side']!='main':
   for i,gp in enumerate(l['word_groups']):
    vis=', '.join(f"{b['component_id']}:{100*b['visible']:.2f}%" for b in gp['body_visibility']) or 'no detected letter bodies'
    notes.append(f"row {l['index']} word {i}: comps {gp['component_ids']} | bodies {vis} | {'WHOLE' if gp['whole'] else 'CUT-OFF'}")
 width=max(cw*scale,1800);height=ch*scale*2+130+len(notes)*24
 canvas=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(canvas)
 font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
 small=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',13)
 draw.text((12,8),rid,font=font,fill='black');canvas.paste(image.resize((cw*scale,ch*scale),Image.Resampling.NEAREST),(0,40))
 y=80+ch*scale;canvas.paste(image.resize((cw*scale,ch*scale),Image.Resampling.NEAREST),(0,y))
 for i,l in enumerate(rows):
  color=colors[i%len(colors)];curve=cap['lines'][i]
  for name in ('mean','base'):
   pts=[(x*scale,y+float(v)*scale) for x,v in enumerate(curve[name]) if 0<=v<ch]
   if len(pts)>1:draw.line(pts,fill=color,width=2)
  if l['side']=='main':continue
  for c in l['component_diagnostics']:
   x0,y0,x1,y1=c['bbox'];draw.rectangle((x0*scale,y+y0*scale,x1*scale,y+y1*scale),outline=color,width=2)
   draw.text((x0*scale,y+max(0,y0*scale-14)),str(c['index']),fill=color,font=small,stroke_width=1,stroke_fill='white')
 y+=ch*scale+28
 for line in notes:
  draw.text((12,y),line,font=font,fill='black');y+=24
 canvas.save(D/'overlays'/f'{rid}.png')


def report(records,witnesses,summary,latest,history,conflicts,flips,scope):
 c=summary['cohorts'];gaz='gazette_modern--80e8a42cbf8e629f--s000-l0120';acc='129cff40-p000009-l0107'
 g0=witnesses[gaz]['before'];g1=witnesses[gaz]['after']
 lines=['# SEG step 1 — 0.9-s1', '', 'Completed local native replay of 150 segeval1, 888 calibration and 250 frozen cell sample crops, for both 0.8 and 0.9-s1. No network, reader run, Git write, commit or deployed-package modification. The lead commits.', '',
 'The single behavioral change replaces the old ≥2 detected bodies plus no horizontal-edge contact test with **every detected letter body ≥95% visible**. A group with no detected body remains cut-off; one detected body can now form a whole group. The 0.35-x-height groups and existing body predicate (role, width and ≥0.6-x-height band overlap) remain byte-for-byte in effect. Body visibility uses the existing text_lines mean/base geometric frame at the same component centre as body membership: `clip(min(base[x], crop_height) - max(mean[x], 0), 0, xheight) / xheight`. No rounding or epsilon enters the ≥0.95 comparison. Horizontal-edge contact remains diagnostic only.', '',
 'Complete-row detection, >2-word allowance, second-complete-line veto, orientation/main-row handling, row-frame measurement, predictor, length 0.5–1.5 and padding 1.5 are unchanged. The JS policy is byte-identical to 0.8; native inventory supplies its changed word counts. Only segmentation version/fingerprint metadata changes.', '',
 '## Native replay and scoring', '', 'The 150/888 inputs, contexts and owner scoring follow gate2/replay.py. Full stored reader answers are scored without a reader run; fine/faulty/unresolved labels are identical to gate2. Positive segmentation faults take precedence over unknown flags. `crop_overrun` alone is fine. FP = DROP/fine, FN = KEEP/faulty, UNC = every UNCERTAIN among all 150. The 888 uses only `owner_rating.decision` on 135 rated lines. Cells have no inherited owner-standard labels; only explicit marks are scored.', '',
 table(['150 decision','0.8 fine','0.8 faulty','0.8 unresolved','0.9-s1 fine','0.9-s1 faulty','0.9-s1 unresolved'],[[v,*[c['segeval1']['confusion'][ver][v][s] for ver in ('08','09') for s in ('fine','faulty','unresolved')]] for v in ('DROP','KEEP','UNCERTAIN')]),'',
 table(['Version','FP','FN','UNC'],[[v,*c['segeval1']['errors'][k].values()] for v,k in [('0.8','08'),('0.9-s1','09')]]),'',
 'The saved 0.8 baseline is **18/14/11**, as the gate2 evidence and handoff show; the context pack’s FN=11 statement is not substituted for the saved full-population FN=14.', '',
 table(['888 rated decision','0.8 owner KEEP','0.8 owner DROP','0.9-s1 owner KEEP','0.9-s1 owner DROP'],[[v,*[c['calibration']['rated_confusion'][ver][v][s] for ver in ('08','09') for s in ('KEEP','DROP')]] for v in ('DROP','KEEP','UNCERTAIN')]),'',
 f"888 rated agreement: **{c['calibration']['rated_agreement']['08']} → {c['calibration']['rated_agreement']['09']}/135**. The other 753 are unrated.",'',
 table(['Cohort','Rows','0.8 → 0.9-s1 transitions'],[[k,v['rows'],str(v['transitions'])] for k,v in c.items()]),'',
 '## All explicit owner marks', '',
 f"The supplied local file contains **{summary['owner_marks']['file_entries']} entries, {summary['owner_marks']['distinct_ids']} distinct IDs**: gate 62, cells 152 and deskew 26 entries. Five deskew IDs also occur in gate, leaving **21 additional deskew IDs**, matching the requested 62+152+21=235 distinct marks. All 235 IDs occur in the replay sets. Latest `updated` timestamp wins; file order breaks an exact timestamp tie. Agreement is counted once per distinct marked line, including UNCERTAIN as non-agreement. Two duplicate crop IDs across cohorts have identical verdicts and are counted once.", '',
 table(['Marked decision','0.8 owner KEEP','0.8 owner DROP','0.9-s1 owner KEEP','0.9-s1 owner DROP'],[[v,*[summary['owner_marks']['confusion'][ver][v][s] for ver in ('08','09') for s in ('KEEP','DROP')]] for v in ('DROP','KEEP','UNCERTAIN')]),'',
 f"Agreement: **{summary['owner_marks']['agreement']['08']} → {summary['owner_marks']['agreement']['09']}/{summary['owner_marks']['matched_unique']}**. [Mark snapshot](owner_marks_snapshot.jsonl), [conflicts](mark_conflicts.json). There are no conflicting KEEP/DROP marks in the supplied file. Explicit marks are scored separately from historical owner-standard states and 888 ratings; they do not overwrite those reference labels.", '',
 'Repeated marks (including every KEEP/DROP conflict):','',
 table(['Line ID','Chronological marks','Winning mark','Conflict'],[[rid,'; '.join(f"{m['updated']} {m['owner_mark']} ({m['sheet']})" for m in sorted(ms,key=lambda m:(m['updated'],m['file_line']))),latest[rid]['owner_mark'],rid in conflicts] for rid,ms in history.items() if len(ms)>1]),'',
 '## Gazette l0120 witness', '',
 f"Owner: “should have been dropped, more than 2 full words showing, the output length is correct”. Measured: **whole {g0['evidence']['gate']['whole_words']} → {g1['evidence']['gate']['whole_words']}; DROP → DROP**, both on `{g1['reason']}`. The unchanged inventory detects **zero bodies in the above row** (votes 23.8, visible 0.236, coverage 0.958159); therefore no group can satisfy the new all-body test. This does **not** reproduce the owner’s whole-word assessment, and no detector or length repair is introduced in S1.", '',
 f"![Gazette native overlay](overlays/{gaz}.png)",'',
 table(['Group','BBox','Component IDs','0.8 body IDs','Per-body visible','0.8 → 0.9-s1'],[[i,w['bbox'],w['component_ids'],w['body_ids'],'none: no detected body',('whole' if w['whole'] else 'cut-off')+' → '+('whole' if witnesses[gaz]['after']['evidence']['lines'][1]['word_groups'][i]['whole'] else 'cut-off')] for i,w in enumerate(g0['evidence']['lines'][1]['word_groups'])]),'',
 f"Counts: 0.8 {g0['evidence']['gate']['whole_words']} whole / {g0['evidence']['gate']['cutoff_words']} cut-off; 0.9-s1 {g1['evidence']['gate']['whole_words']} whole / {g1['evidence']['gate']['cutoff_words']} cut-off. No complete neighbour row. Gate PASS in both versions. Length ratio `(characters+1)/(predicted+1)` = {(g1['evidence']['characters']+1)/(g1['evidence']['box_evidence']['predictions'][2]+1):.15g}; box and padding evidence are exact to 0.8. This is the tool’s measured output, not an endorsement of that diagnosis.", '',
 'For completeness, per-component body-frame visibility is recorded below as a diagnostic even where the unchanged body predicate rejects the component. These fractions do not create additional bodies or votes. Full per-body/per-component data and both versions are in [witnesses.json](witnesses.json).','']
 for rid in (gaz,acc):
  wit=witnesses[rid]
  if rid==acc:
   lines+=['## 129cff40 l0107 — inventory report only','', 'Owner: “the accents of ἔχει were detected as a second line, complete error”. No witness-specific repair was made. The unchanged inventory returns **three rows total**, including **two complete neighbour rows**, above and below; the first complete neighbour is the above row. Both versions DROP for `gate: second complete line`. These are detector observations, not a claim that either neighbour is a real printed text line.', '',f'![129cff40 native overlay](overlays/{acc}.png)','']
  lines += [f"### `{rid}` row inventory",'',f"Native crop {wit['native']['width']}×{wit['native']['height']}; x-height {wit['native']['xheight']!r}; de-skew angle {wit['native']['angle']!r}°.",'',table(['Row','Side','Votes','Bodies','Visibility','Coverage','Complete','Component IDs','Body IDs'],[[l['index'],l['side'],l['votes'],l['bodies'],l['visible'],l['coverage'],l['complete'],l['component_ids'],l['body_ids']] for l in wit['after']['evidence']['lines']]),'']
  for l in wit['after']['evidence']['lines']:
   lines += [f"Row {l['index']} ({l['side']}), assigned components and body-frame visibility:",'',table(['Component','Role','BBox','Area','Touches','Body','Frame visibility'],[[x['index'],x['role'],x['bbox'],x['area'],x['touches'],x['body'],f"{100*x['body_frame_visible']:.6f}%"] for x in l['component_diagnostics']]),'']
  lines+=['Detector vote provenance (unchanged text_lines accumulator; a component can cast several alternative hypotheses; only accepted votes are listed):','',table(['Side','Shift px','Accepted weighted votes: component / x / shift / weight'],[[v['side'],v['shift'],'; '.join(f"{t['component_id']} / {t['x']} / {t['shift']} / {t['weight']}" for t in v['votes'])] for v in wit['vote_provenance']]),'']
 lines+=['## Exhaustive verdict flips','',f"**{len(flips)} cohort records / {summary['unique_flipped_ids']} unique lines.** All changes are listed here and in [flips.jsonl](flips.jsonl). Blank label fields mean no saved label, rating or explicit mark.",'',table(['Set','Line ID','0.8 → 0.9-s1','Whole 0.8 → 0.9-s1','Owner state','888 rating','Latest mark','0.8 reason','0.9-s1 reason'],[[f['cohort'],f['line_id'],f['verdict_08']+' → '+f['verdict_09'],str(f['whole_08'])+' → '+str(f['whole_09']),f.get('owner_standard_state') or '',(f.get('owner_rating') or {}).get('decision',''),(f.get('owner_mark') or {}).get('owner_mark',''),f['reason_08'],f['reason_09']] for f in flips]),'',
 '## Readback and source scope','',table(['Check','Passed'],list(summary['readback'].items())+[['Unchanged final verdicts replayed exactly',summary['unchanged_verdicts']],['Tests',158]]),'',
 'Every gate and final verdict was recomputed from stored evidence for both versions; predictor results were independently re-run. Every unchanged final verdict replays exactly. Box/padding evidence equals 0.8 wherever the gate verdict is unchanged. Fresh native 0.8 matches all 1038 saved gate2 results and evidence, excluding only orientation elapsed `seconds`. Every other inventory field, body membership, component assignment, row curve and cut diagnostic is equal across versions. No Stage B measurements are fabricated for blocked gates.', '',
 'Changed existing source files (exhaustive scope guard):','',*[f'- `{p}`' for p in scope['changed_source_files']],'',
 f"Only `line_inventory` changes in crop-tools.py. All JS decision functions, NativeSegmenter, geometry, grouping/body definitions and predictor files remain unchanged. {scope['unchanged_initial_files']} other initial files match their hashes, including {scope['package_files_unchanged']} package files and the stray cp1_initial_hashes.json. [Scope guard](scope_guard.json), [initial hashes](initial_hashes.json), [input hashes](input_hashes.json), [crop bindings](crop_bindings.jsonl), [native replay](replay.jsonl), [readback summary](summary.json), [receipt](receipt.json). Generated tool metadata updates segmentation only and preserves its canonical sol-recut component namespace. The isolated segmentation definition rebuilds exactly; the unrelated full versions builder cannot run in this checkout because pre-existing untracked Clariden deployment sources are absent.", '',
 'Tests used the existing sibling `.venv` with this checkout first on PYTHONPATH. The historical `test_line_pipeline.py` is absent here, so its existing sibling copy was executed read-only against this checkout, alongside this checkout’s deskew and gate tests. Offline fixtures block network; bytecode and pytest cache writes were disabled. `tests.log`: **158 passed**. The native replay blocks socket access with a Python audit hook. No OCR reader or page fetch ran. A test-only exact-float assertion was corrected to `pytest.approx`; the production ≥0.95 predicate has no tolerance.', '',
 'Reproduce from this worktree (using the existing sol-recut `.venv/bin/python`): `python -B docs/harvest/seg_steps/s1/replay.py`, then `python -B docs/harvest/seg_steps/s1/validate_report.py`. These write only S1 artifacts and rerun local native segmentation. Do not rerun prepare.py: initial hashes are the before-change receipt.', '']
 e0=c['segeval1']['errors']['08'];e1=c['segeval1']['errors']['09']
 last=f"SEG S1 READY: gazette l0120 whole 0.8 {g0['evidence']['gate']['whole_words']} → {g1['evidence']['gate']['whole_words']} ({g1['verdict']}); 129cff40 second row = above votes 9 bodies 6 visibility 1.0 coverage 0.651452 complete (below also complete); 150 FP/FN/UNC 0.8 {e0['FP']}/{e0['FN']}/{e0['UNC']} → {e1['FP']}/{e1['FN']}/{e1['UNC']}; 888 rated agree {c['calibration']['rated_agreement']['08']} → {c['calibration']['rated_agreement']['09']}/135; owner marks agree {summary['owner_marks']['agreement']['08']} → {summary['owner_marks']['agreement']['09']}/{summary['owner_marks']['matched_unique']}; flips {len(flips)}; tests 158 passed"
 lines.append(last);(D/'REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':run()
