"""Package CN1 score and box receipts into the final report and audit JSONL."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter
from pathlib import Path
import json
import subprocess
import time
from scripts.labelfix.s5_validate import read,write
from scripts.labelfix.owner_reading import digest,load_configuration
from greekocr.labelfix.text import clusters,nfd
O=Path('docs/records/labelfix/spellcheck');E=O/'CN1_evidence'
s=json.loads((E/'summary.json').read_text());summary=s['summary'];groups=['review_v16','examples_v10','old59','old33','old56']
checks=read(O/'CN1_checks.jsonl');notes=[r for r in checks if r['type']=='note'];diffs=[r for r in checks if r['type']=='note_difference'];holds=[r for r in checks if r['type']=='hold_slot']
a=json.loads((_data_input(E/'combined_boxes.json')).read_text());b=json.loads((_data_input(E/'s6_control_boxes.json')).read_text());saved={r['line_id']:r for r in read(E/'S6_scoring_lines.jsonl')};combined={r['line_id']:r for r in read(E/'combined_scoring_lines.jsonl')}
configs={p:load_configuration(E/p) for p in ['combined_config.json','s6_config.json']}
assert a['reading_configuration']==configs['combined_config.json']
counts=Counter()
for lid in a['lines']:
 x=a['lines'][lid];y=b['lines'][lid]
 assert x['raw_line_reading']==y['raw_line_reading']
 assert not x['line_reading']['removed_by_constraint']
 assert x['line_reading']['opening_quotes']==y['line_reading']['opening_quotes']
 counts['letters']+=len(x['line_reading']['slots']);counts['mark_boxes']+=len(x['boxes'])
 assert Counter((q['kind'],tuple(q['bbox'])) for q in x['boxes'])==Counter((q['kind'],tuple(q['bbox'])) for q in y['boxes'])
 for xs,ys in zip(x['line_reading']['slots'],y['line_reading']['slots']):
  for field in ['base','start','component_ids','bbox','evidence']:
   assert xs[field]==ys[field]
  counts['changed_part_sequences']+=xs['parts']!=ys['parts']
 counts['changed_reading_lines']+=x['reading']!=y['reading']
assert len(notes)==254 and len(holds)==87
for group,n in [('review_v16',49),('examples_v10',57),('old59',59),('old33',33),('old56',56)]:
 rs=[r for r in notes if r['note_set']==group];assert len(rs)==n
 for name in ['S6','combined','SF1_detector_control']:
  for r in rs:
   cs=r['systems'][name]['clauses'];assert all(c['status'] in ('fixed','HOLD','fail') for c in cs)
   assert r['systems'][name]['raw_fixed']==all(c['raw_fixed'] for c in cs)
  st=summary[group][name];assert st['fixed']+st['hold']+st['fail']==n
box={}
for name in ['saved_s6_to_combined','control_to_combined']:
 d=json.loads((E/f'box_regression_{name}.json').read_text());tot={k:sum(len(r[k]) for r in d['lines'].values()) for k in ['lost','added','moved']}
 box[name]=dict(type='box_regression',comparison=name,summary=d['summary'],box_counts=tot,changed_boxes=[dict(line_id=lid,change=k,box=q) for lid,r in d['lines'].items() for k in ['lost','added','moved'] for q in r[k]])
assert box['saved_s6_to_combined']['box_counts']==dict(lost=0,added=1,moved=0)
assert box['control_to_combined']['box_counts']==dict(lost=0,added=0,moved=0)
for receipt in ['combined_build_receipt.json','control_build_receipt.json','scoring_guard_receipt.json']:
 r=json.loads((E/receipt).read_text());assert not r['forbidden_calls']
raw_worse=[d for d in diffs if d['raw_direction']=='combined_worse'];raw_better=[d for d in diffs if d['raw_direction']=='combined_better'];worse=[d for d in diffs if d['direction']=='combined_worse'];better=[d for d in diffs if d['direction']=='combined_better'];deferred=[d for d in diffs if d['direction']=='S6_fixed_combined_HOLD']
assert len(worse)==1 and len(better)==2

def escaped(t):return str(t).replace('|','\\|').replace('\n',' / ')
def parts(v):return '+'.join(v) or 'none'
def change_cause(d):
 lid=d['line_id'];old={r['start']:r for r in saved[lid]['recogniser_slots']};new={r['start']:r for r in combined[lid]['recogniser_slots']}
 if lid=='51fe7386-p000024-l0020' and d['raw_direction']=='combined_better':
  return 'SF1 detector recovers source 5 above ε at start 13 / frozen slot 11; also present without R1. Detector drift, not an R1 naming gain.'
 if d['direction']=='combined_worse':
  return 'Unheld R1 names agree on breathing+accent kinds but change dasia+circumflex to psili+circumflex at start 41 / frozen slot 28; frozen truth and owner-approved S4/S6 require dasia.'
 starts=set(start for c in d['clauses'] for start in c['hold_starts'])
 for c in d['clauses']:
  for n in c['slots']:
   starts.update(r['start'] for r in new.values() if n in r['component_slots'])
 changes=[f"start {k}: {parts(old[k]['parts'])} → {parts(new[k]['parts'])}" for k in sorted(starts) if k in old and k in new and old[k]['parts']!=new[k]['parts']]
 if not changes:
  changes=[f"start {k}: K1 HOLD" for k in sorted(starts) if k in new and new[k].get('hold')]
 why='; '.join(changes) or 'Line-wide approved-name/presence predicate changes.'
 if any(c['hold_starts'] for c in d['clauses']):why+='; addressed output is HOLD, so no fixed/error award for those slots.'
 if d['note_set']=='examples_v10' and lid=='384c3f89-p000091-l0014':why+=' The raw whole_marks predicate reads zones from displayed names; its apparent gain has no detector box gain.'
 return why
for d in diffs:d['cause']=change_cause(d)
def punctuation(t):
 return ''.join(c.base for c in clusters(nfd(t)) if not c.base.isalpha() and not c.base.isspace())
display_differences=[]
for lid in a['lines']:
 control=b['lines'][lid]['reading'];result=a['lines'][lid]['reading']
 if punctuation(control)!=punctuation(result):
  display_differences.append(dict(type='rendered_punctuation_difference',line_id=lid,kind='quote',S6_control_reading=control,combined_reading=result,control_punctuation=punctuation(control),combined_punctuation=punctuation(result),note_sets=sorted({r['note_set'] for r in notes if r['line_id']==lid}),cause='combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs'))
assert len(display_differences)==5
write(E/'rendered_punctuation_differences.jsonl',display_differences)
checks=[r for r in checks if r['type'] in ('note','hold_slot')]+diffs+list(box.values())+display_differences
verification=dict(type='verification',owner_lines=92,**counts,head=configs['combined_config.json']['detector_commit'],network_guard_forbidden_calls=0,recognizer_forward_passes=0,r1_forward_passes=0,training=False,print_deletions=0,tests='12 passed, 30 deselected',complete_note_record_count=254,unique_hold_slots=87,rendered_quote_changed_lines=5,strict_raw_deltas=dict(worse_records=len(raw_worse),worse_unique_lines=len({d['line_id'] for d in raw_worse}),better_records=len(raw_better),better_unique_lines=len({d['line_id'] for d in raw_better})),hold_aware_deltas=dict(worse_records=len(worse),worse_unique_lines=len({d['line_id'] for d in worse}),better_records=len(better),better_unique_lines=len({d['line_id'] for d in better}),S6_fixed_combined_HOLD_records=len(deferred)))
checks.append(verification);write(O/'CN1_checks.jsonl',checks);write(E/'differences.jsonl',diffs);dump=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');dump(E/'verification.json',verification)
text=['# CN1 — combined system versus S6 on the owner’s notes','',
'Completed offline on `opus/spellcheck`, HEAD `'+configs['combined_config.json']['detector_commit']+'`, on 2026-10-17 (Europe/Athens). Measurement only: no reader/policy/model changes, `.git` writes, publishing, network use, recognition/R1 forward passes, or training. Both final page builds ran with socket-connect and recognizer-construction guards; neither guard was triggered. The required SF1 detector/shape/case reading path ran on the Mac CPU with cached alignments and saved R1-A predictions.','',
'**Combined does not establish an unheld naming improvement on this instrument.** It has one unheld naming regression. Its one unheld recovered-note line improves two old records, and that recovery is already present in the SF1 detector-only control. HOLD outputs are deferred outcomes, never counted as fixed or wrong.','',
'## Complete-note outcomes','',
'`F / H / U` means fixed / HOLD / unmet. “Unmet” includes unresolved wording or missing targets; it does not by itself prove a pixel-reading error. A complete note is fixed only when every original strict clause passes and no addressed mark output is held. An independent unmet clause keeps a note unmet even if another clause is held. The raw strict column evaluates the unchanged Boolean predicates before this HOLD gate; it is diagnostic and must not be presented as accepted fixes. Old59 retains its 59 slot-record units, rather than deduplicating their shared note lines.','',
'| instrument | combined F / H / U | S6 F / H / U | raw strict combined vs S6 |','|---|---:|---:|---:|']
for g in groups:
 c=summary[g]['combined'];v=summary[g]['S6'];text.append(f"| {g} ({c['n']}) | {c['fixed']} / {c['hold']} / {c['fail']} | {v['fixed']} / {v['hold']} / {v['fail']} | {c['raw_strict_fixed']}/{c['n']} vs {v['raw_strict_fixed']}/{v['n']} |")
text += ['',
'The hash-bound SF1 detector-only control includes the same print-preserving K1 policy as combined. This separates the one detector recovery and K1 abstentions from R1 naming:','',
'| set | SF1 detector control F/H/U | combined F/H/U | raw strict control vs combined |','|---|---:|---:|---:|']
for g in groups:
 c=summary[g]['combined'];v=summary[g]['SF1_detector_control']
 text.append(f"| {g} | {v['fixed']}/{v['hold']}/{v['fail']} | {c['fixed']}/{c['hold']}/{c['fail']} | {v['raw_strict_fixed']}/{v['n']} vs {c['raw_strict_fixed']}/{c['n']} |")
text += ['',f"There is **{len(worse)} combined-worse note record ({len({d['line_id'] for d in worse})} unique line), {len(better)} combined-better records ({len({d['line_id'] for d in better})} unique line), and {len(deferred)} S6-fixed → combined-HOLD records**. Excluding the HOLD gate yields {len(raw_worse)} worse / {len(raw_better)} better raw-predicate records; these include held displayed names and are not equivalent to accepted corrections.",'',
'## Clause split','',
'Each cell is **combined fixed/HOLD/unmet vs S6 fixed/HOLD/unmet, of n clauses**. Facets overlap: an old exact mark clause has a naming facet and a separate S6 physical-evidence facet; a union can test both segmentation and letter identity; an empty-note guard tests both name preservation and physical preservation. Counts are instrument evidence, not new independent print adjudication. Physical facets use the actual detector control evidence, so changing a held displayed name cannot fabricate a recovered blob. Naming keeps strict exact counts and Counter equality where the old instrument requires them.','',
'| set | physical presence | naming | segmentation | punctuation / apostrophe / quote | letter identity |','|---|---|---|---|---|---|']
catnames=['physical_presence','naming','segmentation','punctuation','letter_identity']
for g in groups:
 cells=[]
 for cat in catnames:
  c=summary[g]['combined']['facets'][cat];v=summary[g]['S6']['facets'][cat];assert c['n']==v['n']
  cells.append(f"{c['fixed']}/{c['hold']}/{c['fail']} vs {v['fixed']}/{v['hold']}/{v['fail']} ({c['n']})")
 text.append('| '+g+' | '+' | '.join(cells)+' |')
text += ['',
'The current review’s 14 segmentation clauses pass in both systems. The current examples’ five structural segmentation clauses and two base-only letter clauses also pass in both. Current punctuation is unchanged: review 1/2, examples 11/15. There is no letter-identity change: every serialized base, start, component ID and character box matches the detector control.','',
'The mixed complete-note guards (reported separately rather than hidden among physical clauses) are:','',
'| set | combined F/H/U | S6 F/H/U | unresolved owner-uncertainty clauses in both |','|---|---:|---:|---:|']
for g in groups:
 c=summary[g]['combined']['facets']['complete_note_guard'];v=summary[g]['S6']['facets']['complete_note_guard'];u=summary[g]['S6']['facets']['uncertainty']
 text.append(f"| {g} | {c['fixed']}/{c['hold']}/{c['fail']} | {v['fixed']}/{v['hold']}/{v['fail']} | {u['n']} |")
text += ['',
'## HOLD outcomes','',
'**87 unique character slots on 53 of the 92 owner lines are HOLD**: 80 mark-kind disagreements and 9 K1 print-preserving flags, with 2 slots in both groups. All 87 slot records, displayed and frozen slot IDs, raw detector parts, displayed combined parts, reasons and K1 receipts are in `CN1_checks.jsonl` (`type=hold_slot`). All printed parts are retained; there are zero constraint deletions. The same slot can appear in multiple note sets.','',
'| set | HOLD slots anywhere on its lines | distinct HOLD slots addressed by its clauses | notes deferred entirely to HOLD |','|---|---:|---:|---:|']
for g in groups:
 h=s['holds'][g];text.append(f"| {g} | {h['unique_slots']} | {h['targeted_unique_slots']} | {summary[g]['combined']['hold']} |")
text += ['',
'## Every changed note outcome','',
'One line per note record in the union of (a) raw strict success flips, (b) fixed ↔ unmet outcomes, and (c) S6-fixed → combined-HOLD outcomes. Repeated lines across instruments and repeated old59 slot records remain separate. The clause field identifies every changed clause; the cause distinguishes abstention from an unheld regression.','',
'| note set / line / note | changed clause(s), S6 → combined (raw predicate) | S6 reading | combined reading | cause |','|---|---|---|---|---|']
for d in diffs:
 clauses='; '.join(f"{c['kind']} {c['slots']} {c.get('value')}: {c['S6']} → {c['combined']} (raw {c['S6_raw']} → {c['combined_raw']})" for c in d['clauses'])
 cells=[f"{d['note_set']} #{d['note_index']} / `{d['line_id']}` / {d['note'] or '[empty, explicitly reviewed]'}",clauses,d['S6_reading'],d['combined_reading'],d['cause']]
 text.append('| '+' | '.join(escaped(v) for v in cells)+' |')
text += ['',
'## Box regression and detector drift','',
'`box_regression.py` was run on all 92 owner lines, including current review/examples notes for attribution.','',
'| comparison | lines | lost | added | moved | reading-changed lines |','|---|---:|---:|---:|---:|---:|']
for name,label in [('saved_s6_to_combined','saved S6 → combined'),('control_to_combined','fresh hash-bound SF1 detector → combined')]:
 d=json.loads((E/f'box_regression_{name}.json').read_text());tot=box[name]['box_counts'];changed=sum(v['reading_changed'] for v in d['lines'].values());text.append(f"| {label} | 92 | {tot['lost']} | {tot['added']} | {tot['moved']} | {changed} |")
text += ['',
'**The requested saved-S6 box identity is not exact.** The only difference is an added `above` box `[370, 8, 386, 28]` on `51fe7386-p000024-l0020`, source component 5, displayed character slot 9, frozen primary slot 11 (source slots `[11,10]`), recognizer start 13, ε in `ἐπέρασε`. Its lossless pixel runs are retained. The old serialized S6 evidence had no box there. The matcher reports the old reviewed owner unassigned because the historical sidecar has no certified two-dimensional mark zones; CN1 does not alias display slot 9 to frozen slot 9.','',
'Both fresh page builds contain the same 578 boxes, all 2,512 character bases/starts/component IDs/boxes, identical raw `LineReading` records, and identical per-character evidence including pixel runs. There are zero presence, segmentation or apostrophe-evidence differences attributable to the combination step. Opening-quote evidence is also identical, but the rendered quote glyphs differ on five lines (see below). R1 changes 92 part sequences on 61 lines. Against saved S6 the one detector recovery makes 62 reading-changed lines. The control isolates this pre-existing SF1 detector drift; it is not evidence of an R1 gain.','',
'## Rendered punctuation limitation of the required builder','',
'**The existing hash-bound combined builder does not fully preserve S6’s displayed opening quotes.** `read_ink` strips recognizer quote glyphs and inserts a quote only when detector evidence exists. `combine` calls `render_reading(LINE_TEXT[lid], slots)` again and skips that final quote step. It therefore drops two detected opening quotes and restores three unsupported recognizer quote glyphs, with unchanged boxes. A sixth line has only an extra space after a retained quote. This is measured output of the requested unchanged path, not a corrected implementation of the intended S6-quote composition.','',
'The strict `quote`/`leading_sign` clauses inspect `opening_quotes`, while `no_regression` compares marks/apostrophes but not rendered opening-quote text; these five display changes are consequently **outside the headline instrument’s combined-worse count of 1**. The punctuation facet table above is an evidence-instrument score and must not be read as proof of displayed-punctuation parity. All five witnesses are also serialized with `type=rendered_punctuation_difference`.','',
'| line / note sets | S6 detector-control reading | actual combined reading | cause |','|---|---|---|---|']
for d in display_differences:
 text.append('| '+' | '.join(escaped(v) for v in [d['line_id']+' / '+', '.join(d['note_sets']),d['S6_control_reading'],d['combined_reading'],d['cause']])+' |')
text += ['',
'## Instrument and provenance','',
'Current note clauses call `s6_notes.clause` with the S4 reviewed snapshot, reproducing S6 **35/49 and 33/57** exactly. Old33 and old56 use `r1_owner.evaluate`’s saved strict clause transcriptions, then call `r1_owner.clause`; old59 uses its exact unit-count and Counter-equality predicates and frozen v8 overlap mapping. For full-system scoring, `reader_scored` / `prediction_line_present` mean a serialized system output exists and are set symmetrically: the S6 fallback remains available where R1 has no head/prediction. Apostrophe/quote clauses route to `s6_notes.clause`; the old punctuation-dot clause uses the retained frozen slot’s below evidence. This prevents the R1-only “outside four heads” exclusion from incorrectly discarding S6’s punctuation in the combined system. No reader or instrument implementation was edited.','',
'Old strict counts therefore differ from the older permissive S6 legacy evaluator (47/59, 22/33, 32/56): CN1 retains exact count/name equality and the strict approved-name/UNKNOWN guards instead. The missing R1 line in the current 57-example set uses its S6 fallback and is not declared a missing combined prediction.','',
'Targeted held mark clauses are deferred; punctuation, letter identity and segmentation do not depend on R1 mark names. For line-wide guards, held character comparisons are excluded before checking the remaining outputs; a separate unheld failure still fails the note. The Boolean instrument outcome is retained as `raw_fixed`, and all hold-aware decisions and per-facet results remain independently inspectable. For example, the apparent raw `whole_marks` gain at `384c3f89-p000091-l0014` comes from zones derived from held displayed names, despite unchanged physical evidence, and earns no complete-note fix.','',
'The combined config binds the current detector commit, all SF1 reader source hashes, S4 shape and S5 case assets, explicit print constraint policy, actual R1-A `best.pt` SHA256 `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636`, and both supplied prediction-file hashes. Prediction receipts and actual checkpoint hashes were verified. The cached alignment file, input snapshots, note versions, adapter sources and exact generated HTML/sidecars are hashed in the measurement receipt. Prediction confidence remains UNKNOWN; no detector confidence is borrowed for R1 naming.','',
'Artifacts: [checks](CN1_checks.jsonl), [machine summary](CN1_evidence/summary.json), [verification](CN1_evidence/verification.json), [measurement receipt](CN1_evidence/measurement_receipt.json), [combined configuration](CN1_evidence/combined_config.json), [combined serialized readings and boxes](CN1_evidence/combined_boxes.json), [saved-S6 box diff](CN1_evidence/box_regression_saved_s6_to_combined.json), [detector-control box diff](CN1_evidence/box_regression_control_to_combined.json). The HTML files are local measurement artifacts and were neither published nor opened.','',
'## Reproduction and validation','',
'Use the specified interpreter, `PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`. Final guarded page-build arguments and elapsed times are saved verbatim in `combined_build_receipt.json` and `control_build_receipt.json`. To reproduce them without retyping their absolute prediction paths:','',
'```python',
'import json, os, subprocess',
'from pathlib import Path',
'py = "/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python"',
'env = dict(os.environ, PYTHONPATH=os.getcwd(), PYTHONDONTWRITEBYTECODE="1")',
'e = Path("docs/records/labelfix/spellcheck/CN1_evidence")',
'for file in ("combined_build_receipt.json", "control_build_receipt.json"):',
'    r = json.loads((e / file).read_text())',
'    subprocess.run([py, "-m", "scripts.labelfix.cn1_offline", str(e / file),',
'                    r["module"], *r["arguments"]], env=env, check=True)',
'subprocess.run([py, "-m", "scripts.labelfix.cn1_measure"], env=env, check=True)',
'```','',
'```sh',
'PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.box_regression docs/records/labelfix/spellcheck/CN1_evidence/saved_s6_boxes.json docs/records/labelfix/spellcheck/CN1_evidence/combined_boxes.json --notes docs/records/labelfix/spellcheck/owner_notes_review_v16_20261016.jsonl docs/records/labelfix/spellcheck/owner_notes_examples_v10_20261016.jsonl --out docs/records/labelfix/spellcheck/CN1_evidence/box_regression_saved_s6_to_combined.json',
'# Repeat with s6_control_boxes.json for the detector-control comparison.',
'PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.cn1_report',
'```','',
'Validation: **12 passed, 30 deselected** in the existing SF1 tests covering missing targets, exact approved/UNKNOWN name preservation, matching/containment/missing-line behavior, reader confidence separation and K1 HOLD propagation. Measurement assertions verify all five denominators, the saved S6 current totals, one-to-one frozen slot identity, page hashes, configuration/checkpoint/prediction receipts, zero print deletions, and identical fresh-control physical evidence. No broad model evaluation or training was run.','']
totals={}
for cat in catnames:
 totals[cat]={name:{k:sum(summary[g][name]['facets'][cat][k] for g in groups) for k in ['fixed','hold','fail','n']} for name in ['combined','S6']}
physical=totals['physical_presence'];naming=totals['naming'];seg=totals['segmentation'];pun=totals['punctuation'];letter=totals['letter_identity']
last='CN1 RESULT: complete notes combined vs S6 — '+ '; '.join(f"{g} {summary[g]['combined']['fixed']}/{summary[g]['combined']['n']} vs {summary[g]['S6']['fixed']}/{summary[g]['S6']['n']}" for g in groups)+f"; clause split (overlapping note-set facets) physical {physical['combined']['fixed']}/{physical['combined']['n']} vs {physical['S6']['fixed']}/{physical['S6']['n']}, naming {naming['combined']['fixed']}/{naming['combined']['n']} + {naming['combined']['hold']} HOLD vs {naming['S6']['fixed']}/{naming['S6']['n']}, segmentation {seg['combined']['fixed']}/{seg['combined']['n']} vs {seg['S6']['fixed']}/{seg['S6']['n']}, punctuation {pun['combined']['fixed']}/{pun['combined']['n']} vs {pun['S6']['fixed']}/{pun['S6']['n']}, letter identity {letter['combined']['fixed']}/{letter['combined']['n']} vs {letter['S6']['fixed']}/{letter['S6']['n']}; HOLD slots 87 (80 kind-disagreement, 9 K1, 2 overlap); combined-worse notes 1."
text.append(last);(O/'CN1_REPORT.md').write_text('\n'.join(text)+'\n')
(E/'result_line.txt').write_text(last+'\n')
receipt=json.loads((E/'measurement_receipt.json').read_text());receipt['sources'][str(Path(__file__))]=digest(Path(__file__));receipt['sources']['scripts/labelfix/cn1_report.py']=digest(Path(__file__));receipt['final_artifacts_sha256']={str(p):digest(p) for p in [O/'CN1_REPORT.md',O/'CN1_checks.jsonl',E/'summary.json',E/'verification.json',E/'box_regression_saved_s6_to_combined.json',E/'box_regression_control_to_combined.json']};receipt['measurement_started_utc']='2026-10-16 20:55:46 UTC';receipt['wall_seconds_since_first_clock']=time.time()-__import__('calendar').timegm(time.strptime('2026-10-16 20:55:46','%Y-%m-%d %H:%M:%S'));receipt['completion_time_utc']=time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime());dump(E/'measurement_receipt.json',receipt)
print(last);print('report lines',len(text),'checks',len(checks),'verification',json.dumps(verification,ensure_ascii=False))
