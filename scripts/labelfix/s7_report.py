"""Build S7's negative qualification report from versioned evidence only."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter
import json
from pathlib import Path
from scripts.labelfix.s5_validate import read,write

O=Path('docs/records/labelfix/spellcheck');E=O/'S7_evidence'

def pct(v):return '—' if v is None else f'{100*v:.2f}%'
def pr(m):return f"{pct(m['precision'])} / {pct(m['recall'])}"
def fhu(m):return f"{m['fixed']} / {m['hold']} / {m['fail']}"
def table(rows):return ['| '+ ' | '.join(map(str,r))+' |' for r in rows]
def box_counts(d,scope=None):
 return {k:sum(v for key,v in d.items() if f' / {k} / ' in key and (scope is None or key.endswith(' / '+scope))) for k in ('lost','added','moved')}


def main():
 m=json.loads((E/'metrics.json').read_text());base=m['baseline'];after=m['accepted']
 old=json.loads((O/'S6_metrics.json').read_text());boxes=json.loads((E/'box_summaries.json').read_text())
 ds=read(E/'kind_disagreements.jsonl');receipt=json.loads((E/'receipt.json').read_text())
 mm={k:json.loads((E/f'm2_{k}/M2_metrics.json').read_text())['POOLED'] for k in ('scope_only','S1','S2','S3','accepted')}
 original_m2=json.loads((O/'M2_metrics.json').read_text())['POOLED']
 decision={k:dict(accepted=False,reasons=reason) for k,reason in {
  'S1':['More total owner kind disagreements','Lower held-out presence and fused recall','Strict owner-note losses'],
  'S2':['Lower pixel capital recall and combined capital precision','Lower held-out presence recall','Strict owner-note losses'],
  'S3':['No presence or kind-disagreement gain','Conservative coverage sends known corrections and fixed notes to HOLD']}.items()}
 (E/'qualification.json').write_text(json.dumps(dict(accepted=[],substitutions=decision),indent=2)+'\n')
 report=['# S7 — Toolkit geometry qualification','',
 '**No substitution qualified for the default.** S1 and S2 regress physical/owner instruments; S3 over-abstains. All candidates remain explicitly selectable for investigation with `read_ink(..., substitutions=[...])`; `QUALIFIED_GEOMETRY` is empty. The accepted-set run is a separate replay of the unchanged SF1 detector. The independent monotonic scope gate is implemented in the M2 combined-checker entry point.','',
 'Offline on Mac CPU; no `.git` writes, network, CTC/R1 forward passes, retraining, or model-asset changes. Launch HEAD: `efdf5756c513fc935d7302df4be85a0f9c084702`. There are 1,264 cached evaluation lines (666 held out / 598 DEV), 92 owner lines, and 473 cached Greek/mixed new-source cards. Original S6, SF1, CN1 and M2 measurement files are retained.','',
 'Acceptance requires no loss on the fixed presence/capital cohorts or strict complete-owner checks, no new unapproved box loss, and no increase in total owner kind disagreements. A disappeared disagreement is agreement, not an established correction. HOLD is never counted fixed. Negative qualification is not evidence against the toolkit owner rule; it rejects these adapters and feature decisions.','',
 '## Saved S6 and the launch runtime','',
 'The saved S6 table is not byte-equivalent to the already-installed SF1 runtime. A separate process executed the three original `ink`, `case`, and `reading` sources directly from the launch commit and reproduced **552 TP / 99 FP / 637 FN** pixel capitals and **1172 / 39 / 17** combined capitals. These equal the fresh baseline and accepted-set replay. The saved S6 capital table has 558 / 112 / 631 and 1172 / 48 / 17. This drift predates S7; it is not credited as a substitution result. See [original launch audit](S7_evidence/original_launch_baseline.json) and [instrument](../../../scripts/labelfix/s7_launch_baseline.py).','']
 report+=table([['metric','saved S6','launch SF1 control','accepted set'],['---','---','---','---'],
  ['pixel capitals P / R',pr(old['capitals']['S6_pixel']),pr(base['capitals']['pixel']),pr(after['capitals']['pixel'])],
  ['combined capitals P / R',pr(old['capitals']['S6']),pr(base['capitals']['combined']),pr(after['capitals']['combined'])],
  ['held-out presence P / R',pr(old['heldout']['presence']['all']['scores']['S6']),pr(base['heldout']['presence']['all']),pr(after['heldout']['presence']['all'])],
  ['fused presence recall',pct(old['heldout']['presence']['fused']['scores']['S6']['recall']),pct(base['heldout']['presence']['fused']['recall']),pct(after['heldout']['presence']['fused']['recall'])]])
 report+=['','Capital truth is the unchanged S5 agreement stratum: 18,960 slots / 1,189 capitals. The separate case-disagreement stratum has 753 slots. Held-out character truth remains 19,249 known / 1,176 UNKNOWN out of 20,425 slots; fused evaluation retains all 756 slots (651 known), and merged-accent evaluation retains all 590 slots (534 known). No ambiguous, fused, clipped or unlocalized slot is removed from these denominators. Presence P/R counts observed detections on the full fixed cohort; UNSEEN availability is reported separately, not awarded as correct absence.','']
 for variant in ('S1','S2','S3'):
  v=m[variant];b=base
  report += [f'## {variant} — rejected','', '; '.join(decision[variant]['reasons'])+'.','']
  vals=[['instrument','SF1 control',variant],['---','---','---'],
   ['original 80 disagreements remaining / all owner disagreements',f"{b['kind_disagreements']['remaining']} / {b['kind_disagreements']['all_owner_slots']}",f"{v['kind_disagreements']['remaining']} / {v['kind_disagreements']['all_owner_slots']}"],
   ['pixel capitals P / R',pr(b['capitals']['pixel']),pr(v['capitals']['pixel'])],
   ['combined capitals P / R',pr(b['capitals']['combined']),pr(v['capitals']['combined'])],
   ['753-slot pixel capital P / R',pr(b['capital_disagreement']['pixel']),pr(v['capital_disagreement']['pixel'])],
   ['753-slot combined capital P / R',pr(b['capital_disagreement']['combined']),pr(v['capital_disagreement']['combined'])]]
  for split in ('heldout','dev'):
   for cohort in ('all','fused','merged_accent'):
    vals.append([f'{split} {cohort} presence P / R',pr(b[split]['presence'][cohort]),pr(v[split]['presence'][cohort])])
   for key,label in [('ascender_false_marks','ascender false marks'),('below_shared_meanline','marks with pixels below S2 per-column meanline'),('unseen_slots','UNSEEN slots')]:
    vals.append([f'{split} {label}',b[split][key],v[split][key]])
  for group in ('review_v16','examples_v10','old59','old33','old56'):
   vals.append([f'strict detector {group}',f"{b['strict_detector'][group]['fixed']}/{b['strict_detector'][group]['n']}",f"{v['strict_detector'][group]['fixed']}/{v['strict_detector'][group]['n']}"])
   vals.append([f'combined {group} fixed / HOLD / unmet',fhu(b['owner'][group]['combined']),fhu(v['owner'][group]['combined'])])
  for prefix in ('','launch_to_'):
   key=variant+'_union' if not prefix else prefix+variant
   bc=box_counts(boxes[key]);vals.append([('saved S6' if not prefix else 'launch SF1')+' box lost / added / moved','—',f"{bc['lost']} / {bc['added']} / {bc['moved']}"])
  report+=table(vals)+['']
  if variant=='S1':
   report+=['`glyphs.letters.letter_boxes` runs after restricting native ink to the current middle band. Its split-or-unresolved boxes and complete parent sets are retained in reading geometry. Cached spans only map recognized letters onto these physical groups. Shared, missing and unresolved groups explicitly carry ambiguity/HOLD; the recognizer never chooses a physical split count. Unassigned physical groups remain in the line receipt, and every recognized letter remains in evaluation. Physical mapping totals: `'+json.dumps(v['physical_mapping'])+'`.','']
  elif variant=='S2':
   guide_rows=[];witnesses={}
   import gzip
   with gzip.open(_data_input(E/'S2_lines.jsonl.gz'),'rt') as f:
    for raw in f:
     l=json.loads(raw);g=l['shared_guides'];r=dict(line_id=l['line_id'],**g['decision'],provenance=g['provenance'])
     guide_rows.append(r)
     if l['line_id'] in ('602cc72e-p000155-l0009','602cc72e-p000113-l0030'):witnesses[l['line_id']]=r
   write(E/'guide_decisions.jsonl',guide_rows)
   report+=['The shared object uses toolkit per-x curvature and four guides. Class contacts from `pages.font.evidence` supply measured ascender/descender offsets; unavailable offsets remain explicitly fallback (no neighbouring-page evidence is available here to borrow). S6 lowercase-body support can change height and vertical gauge, never straighten the curve. Capital geometric features retain the frozen S5 model and its existing 0.4 supporting-probability threshold; no feature weight or model is trained. Overhead and subscript masks are clipped per column; capital side masks use the shared ascender/mean guides.','',
    'Per-line winners: `'+json.dumps(v['guide_winners'])+'`. Every decision and provenance is in [guide_decisions.jsonl](S7_evidence/guide_decisions.jsonl). Required witnesses:','']
   report+=table([['line','toolkit x-height','selected x-height','winner'],['---','---','---','---']]+[[lid,r['toolkit_xh'],r['selected_xh'],r['winner']] for lid,r in witnesses.items()])+['']
  else:
   report+=['S3 accepts crop validity and directional cut masks, adds toolkit body-cut spans, and records above/below coverage as OBSERVED or UNSEEN. Missing top/bottom mark-search extent is conservatively UNSEEN even without edge ink. A relevant UNSEEN zone preserves the visible proposal but holds its slot through both combined paths. This broad envelope is why it fails qualification: it does not recover ink, and on M2 it reduces PRESENCE correction from 25/77 to '+str(mm['S3']['modes']['PRESENCE']['errors'].get('corrected',0))+'/77. The adapter remains off; a narrower physically validated coverage policy is still needed.','']
 report+=['## Original 80 disagreements: who is supported','',
 'The ledger scores kind sets against the unchanged supported character print/adjudication or agreement-proxy truth. It does not convert owner uncertainty or unsupported marks into negative truth. The baseline has 67 known cases: R1 right in 62, detector right in 3, neither right in 2; 13 remain UNKNOWN. No new print adjudication is claimed. Every original slot remains in [kind_disagreements.jsonl](S7_evidence/kind_disagreements.jsonl).','']
 rows=[['variant','disappear','known disappeared / detector right','remaining known: detector / R1 / neither','remaining UNKNOWN','new disagreements'],['---','---','---','---','---','---']]
 for k in m:
  ss=[s for s in ds if s['variant']==k];remaining=[s for s in ss if s['remains']];resolved=[s for s in ss if not s['remains']]
  rows.append([k,len(resolved),f"{sum(s['truth'] is not None for s in resolved)} / {sum(s['detector_right'] is True for s in resolved)}",f"{sum(s['detector_right'] is True for s in remaining)} / {sum(s['r1_right'] is True for s in remaining)} / {sum(s['truth'] is not None and not s['detector_right'] and not s['r1_right'] for s in remaining)}",sum(s['truth'] is None for s in remaining),m[k]['kind_disagreements']['all_owner_slots']-len(remaining)])
 report+=table(rows)+['','## CN1 rerun with the accepted detector','',
 'The strict SF1/CN1 clauses, exact-name checks, missing-target rules, UNKNOWN preservation and complete-note HOLD gate are reused unchanged. All five original note instruments are included. Physical facets use detector evidence rather than displayed R1 names. Facets overlap and are not independent truth samples. Full per-note and per-clause records: [owner_checks.jsonl](S7_evidence/owner_checks.jsonl).','']
 rows=[['note set','strict detector fixed / n','combined fixed / HOLD / unmet','physical','naming','segmentation','punctuation','letter identity'],['---']*8]
 for g,q in after['owner'].items():
  d=after['strict_detector'][g];c=q['combined'];rows.append([g,f"{d['fixed']}/{d['n']}",fhu(c)]+[fhu(c['facets'][cat]) for cat in ('physical_presence','naming','segmentation','punctuation','letter_identity')])
 report+=table(rows)+['','Accepted combined HOLD: `'+json.dumps(after['hold_slots'])+'`. The same 80 kind disagreements remain; 9 K1 flags overlap 2 of them, giving 87 held slots. Print output has no constraint deletions. The existing unheld R1 naming regression on `384c3f89-p000053-l0021` is not corrected by S7.','',
 '## Box regression','',
 'The unmodified `scripts/labelfix/box_regression.py` was run for every candidate against saved S6 and against the fresh launch control. It was also run separately for the 49-note review and 57-note examples instruments, avoiding an interpretation based only on union-file overwrite order. Old slot identities and explicit zones are retained; ambiguous ownership stays unresolved.','']
 report+=table([['saved S6 → accepted: status / kind / scope','count'],['---','---']]+[[k,v] for k,v in boxes['accepted_union'].items()])
 launchbox=box_counts(boxes['launch_to_accepted']);implicit=box_counts(boxes['accepted_union'],'implicitly approved')
 report+=['',f"Launch SF1 → accepted: lost {launchbox['lost']}, added {launchbox['added']}, moved {launchbox['moved']}. Saved-S6 differences already present at launch are not attributed to a substitution. Implicitly approved saved-S6 box changes: lost {implicit['lost']}, added {implicit['added']}, moved {implicit['moved']}. The sole addition is the already-present launch recovery on `51fe7386-p000024-l0020`, start 13 / old slot 11, bbox `[370, 8, 386, 28]`; it is not an S7 gain. All statuses and native box receipts are in [box_summaries.json](S7_evidence/box_summaries.json) and the linked `boxes_*.json` sidecars.",'',
 '## M2 transfer and monotonic scope','',
 'The same 473 eligible cached cards are accounted for: **40 homogeneous monotonic lines excluded, 433 checked**, plus the original 40 Cyrillic exclusions in the 513-card inventory. The script class is inherited only from an independent pixel-reviewed homogeneous page annotation. Mixed Greek monotonic/polytonic pages and unknown classes remain eligible. No source-name heuristic, Google label, blind verdict, or recognizer combining mark determines scope. The manifest contains no reference text: [m2_script_classes.jsonl](S7_evidence/m2_script_classes.jsonl) and [annotation bindings](S7_evidence/m2_script_classes.receipt.json).','',
 'Both requested M2 scripts were rerun with every candidate and the accepted set. CTC spans, R1 predictions, extraction and checkpoints are hash-bound cached inputs; **zero CTC and R1 forward passes**. All 77 original mark-only error pairs remain in scoring. Excluded monotonic cards contain none of those 77 pairs. The gate excludes the two previously wrong modern accent→breathing spot checks before either polytonic reader runs.','']
 rows=[['detector / scope','PRESENCE corrected / HOLD / missed','capital-breathing corrected / 19','new changed slots on marks-correct cards','HOLD / original 473','HOLD / checked'],['---']*6]
 for k,q in [('M2 original',original_m2)]+[(k,mm[k]) for k in ('scope_only','S1','S2','S3','accepted')]:
  p=q['modes']['PRESENCE'];err=p['errors'];n=p['lines_with_HOLD'];capital=p['by_type']['capital_breathing_dropped_or_apostrophe'].get('corrected',0)
  rows.append([k,f"{err.get('corrected',0)} / {err.get('HOLD',0)} / {err.get('missed',0)}",capital,p['accepted_changed_slots'],f'{n}/473 ({pct(n/473)})',f"{n}/{q['inferred']} ({pct(n/q['inferred'])})"])
 report+=table(rows)+['',
 'The final 30→20 change reduction is entirely the scope gate; it is not a geometry improvement. These changes are conditional upper bounds from the blind marks-correct labels, not newly adjudicated errors. Final FULL: `'+json.dumps(mm['accepted']['modes']['FULL']['errors'])+'`, new changed slots '+str(mm['accepted']['modes']['FULL']['accepted_changed_slots'])+'. No 20-example queue is fabricated for candidates with fewer accepted changes; `--no-spotcheck-queue` skips only that optional queue, leaving every scoring assertion and denominator intact.','',
 '## Validation and reproduction','',
 'Validation: **241 passed; one unchanged HTTP fixture blocked by the sandbox**. All existing labelfix test sources and assertions are unchanged. The full test command is recorded in [pytest_full.txt](S7_evidence/pytest_full.txt); the unchanged HTTP capture integration fixture cannot bind a socket in this sandbox (`PermissionError: Operation not permitted`). The explicitly offline run is in [pytest_offline.txt](S7_evidence/pytest_offline.txt). The source-bound R1 scorer was rerun and its metrics/RESULT compared byte-for-byte with SF1 before refreshing its current-source receipt; historical receipt preserved in this evidence directory. [Verification](S7_evidence/verification.json) binds final source, assets, instruments and artifacts.','',
 '```sh',
 'export PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1',
 'PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
 '$PY -m scripts.labelfix.s7_launch_baseline',
 '$PY -m scripts.labelfix.s7_validate',
 '$PY -m scripts.labelfix.s7_m2_scope',
 '$PY -m scripts.labelfix.s7_m2_replay',
 '$PY -m scripts.labelfix.s7_box_regression',
 '$PY -m scripts.labelfix.s7_verify',
 '$PY -m scripts.labelfix.s7_report','```','',
 f"Qualification replay: {receipt['elapsed_seconds']:.1f} s on CPU; [final run log](S7_evidence/qualification_final.log). No performance/generalization claim is made. All candidates are rejected on these fixed instruments; the 80-slot detector weakness, low pixel-only capital recall and fused presence misses remain open.",'']
 p=mm['accepted']['modes']['PRESENCE'];held=p['lines_with_HOLD']
 report.append(f"S7 RESULT: accepted none; kind-disagreements 80→{after['kind_disagreements']['all_owner_slots']}; pixel-only capitals P/R {pr(old['capitals']['S6_pixel'])}→{pr(after['capitals']['pixel'])} (launch {pr(base['capitals']['pixel'])}); presence P/R {pr(old['heldout']['presence']['all']['scores']['S6'])}→{pr(after['heldout']['presence']['all'])}; fused R {pct(old['heldout']['presence']['fused']['scores']['S6']['recall'])}→{pct(after['heldout']['presence']['fused']['recall'])}; owner notes review_v16 35→{after['strict_detector']['review_v16']['fixed']}, examples_v10 33→{after['strict_detector']['examples_v10']['fixed']}; implicit box changes lost {implicit['lost']} added {implicit['added']}; CN1 combined review_v16 26→{after['owner']['review_v16']['combined']['fixed']}, examples_v10 25→{after['owner']['examples_v10']['combined']['fixed']}; M2 HOLD lines 77.6%→{pct(held/473)} ({pct(held/433)} of 433 checked), corrected 25/77→{p['errors'].get('corrected',0)}/77; regressions: no accepted geometry change; pre-existing saved-S6/SF1 drift and R1 naming error remain; S1/S2 physical losses and S3 over-abstention rejected; HTTP fixture sandbox-blocked.")
 (O/'S7_REPORT.md').write_text('\n'.join(report)+'\n')


if __name__=='__main__':main()
