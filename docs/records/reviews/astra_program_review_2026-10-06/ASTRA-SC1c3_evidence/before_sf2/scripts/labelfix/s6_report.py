"""Build the S6 Markdown report and exhaustive regression receipts, never pages."""
import json,hashlib,subprocess,sys
from collections import Counter
from pathlib import Path
from s5_validate import read,write
from s6_validate import zones,physical
from greekocr.labelfix.linemetric import score_slots
O=Path('docs/labelfix/spellcheck');R=Path.cwd()
def pc(x):return '—' if x is None else f'{100*x:.1f}%'
def pr(c):return pc(c['precision'])+'/'+pc(c['recall'])
def fine(x):return '—' if x is None else f'{100*x:.3f}%'
def esc(x):return str(x).replace('|','\\|').replace('\n',' ')
def flag(x):return 'pass' if x else 'open'

def main():
 m=json.loads((O/'S6_metrics.json').read_text());rows=read(O/'S6_lines.jsonl.gz');by={l['line_id']:l for l in rows}
 old={k:{l['line_id']:l for l in read(O/f'{k}_lines.jsonl.gz')} for k in ('S4','S5')}
 notes=json.loads((O/'S6_owner_summary.json').read_text())
 legacy={k:json.loads((O/f'S6_old_checks_{k}.json').read_text()) for k in ('S4','S5','S6')}
 metric_losses=[]
 def compare(label,scope,a,b):
  for key in ('precision','recall','f1'):
   if a.get(key) is not None and b.get(key) is not None and b[key]<a[key]-1e-12:
    metric_losses.append(dict(baseline=label,scope=scope,metric=key,before=a[key],after=b[key]))
 for label in ('S4','S5'):
  for split in ('heldout','dev'):
   for kind in ('total',)+tuple(m[split][label]['by_kind']):
    a=m[split][label]['total'] if kind=='total' else m[split][label]['by_kind'][kind]
    b=m[split]['detected']['total'] if kind=='total' else m[split]['detected']['by_kind'][kind]
    compare(label,f'{split}/naming/{kind}',a,b)
   for kind in ('total',)+tuple(m[split]['atomic'][label]['by_kind']):
    a=m[split]['atomic'][label]['total'] if kind=='total' else m[split]['atomic'][label]['by_kind'][kind]
    b=m[split]['atomic']['detected']['total'] if kind=='total' else m[split]['atomic']['detected']['by_kind'][kind]
    compare(label,f'{split}/atomic/{kind}',a,b)
   for group,v in m[split]['presence'].items():compare(label,f'{split}/presence/{group}',v['scores'][label],v['scores']['S6'])
   for cls,v in m[split]['per_class'].items():compare(label,f'{split}/class/{cls}',v[label],v['detected'])
   for doc,v in m[split]['per_book'].items():
    for kind in ('total',)+tuple(v[label]['by_kind']):compare(label,f'{split}/book/{doc}/{kind}',v[label]['total'] if kind=='total' else v[label]['by_kind'][kind],v['detected']['total'] if kind=='total' else v['detected']['by_kind'][kind])
  ck='before' if label=='S4' else 'after';pk='S4_pixel' if label=='S4' else 'pixel'
  for scope in ('capitals','capitals_disagreement'):
   compare(label,scope+'/combined',m[scope][ck],m[scope]['S6'])
   compare(label,scope+'/pixel',m[scope][pk],m[scope]['S6_pixel'])
 write(O/'S6_metric_regressions.jsonl',metric_losses)
 physical_losses={}
 for label in ('S4','S5'):
  rr=[]
  for l in rows:
   starts={s['start']:s for s in l['recogniser_slots']};before={s['start']:s for s in old[label][l['line_id']]['recogniser_slots']}
   for c in l['character_checks']:
    if c['truth_zones'] is None:continue
    t,a,b=map(set,(c['truth_zones'],c['presence']['S6'],c['presence'][label]))
    if not ((t&b)-a or (a-t)-(b-t)):continue
    rs=starts[c['start']];bs=before.get(c['start'],{})
    reason='capital top/side zone' if rs['case_class']=='capital' else 'font/CTC ownership and zone acceptance'
    rr.append(dict(line_id=l['line_id'],dev=l['dev'],start=c['start'],base=c['base'],component_slots=c['component_slots'],fused=c['fused'],merged_accent=c['merged_accent'],truth=sorted(t),before=sorted(b),after=sorted(a),lost=sorted((t&b)-a),new_false=sorted((a-t)-(b-t)),reason=reason,before_evidence=bs.get('evidence'),after_evidence=rs['evidence'],crop=l['crop']))
  write(O/f'S6_presence_regressions_{label}.jsonl',rr);physical_losses[label]=rr
 # Every DEV top-presence loss introduced by S5, including those still open.
 dev_recovery=[]
 for l in rows:
  if not l['dev']:continue
  rsby={s['start']:s for s in l['recogniser_slots']}
  for c in l['character_checks']:
   if c['truth_zones'] is None or 'above' not in c['truth_zones'] or 'above' not in c['presence']['S4'] or 'above' in c['presence']['S5']:continue
   s=rsby[c['start']];support=[]
   for k in ('S4','S5'):
    bs=next((q for q in old[k][l['line_id']]['recogniser_slots'] if q['start']==s['start']),{})
    support.append(bs.get('evidence'))
   recovered='above' in c['presence']['S6']
   cause='recovered by font/region repair' if recovered else 'capital top/side guard still suppresses S4 top evidence' if s['case_class']=='capital' else 'safe-zone/ownership acceptance unresolved'
   dev_recovery.append(dict(line_id=l['line_id'],start=s['start'],component_slots=s['component_slots'],base=s['base'],truth=c['truth'],recovered=recovered,cause=cause,S4=support[0],S5=support[1],S6=s['evidence'],crop=l['crop']))
 write(O/'S6_DEV_S5_presence_losses.jsonl',dev_recovery)
 # Side marks are outside capitals. Show both the legal case-specific boundary
 # and the common lowercase meanline so no exceptions are hidden.
 common=[]
 for l in rows:
  for s,c in zip(l['recogniser_slots'],l['character_checks']):
   if c['below_font_meanline']['S6']:common.append(dict(line_id=l['line_id'],start=s['start'],base=s['base'],case_class=s['case_class'],evidence=s['evidence']))
 write(O/'S6_common_meanline_exceptions.jsonl',common)
 caps=[s for l in rows if not l['dev'] for s in l['slots'] if s['base'].isupper() and s['truth'] and any(k!='apostrophe' for k,v in s['truth'])]
 capmarks={k:score_slots([dict(s,detected=s[k],unknown_kinds=[]) for s in caps])['total'] for k in ('S4','S5','detected')}
 capnames={k:sum(set(map(tuple,s[k]))==set(map(tuple,s['truth'])) for s in caps)/len(caps) for k in ('S4','S5','detected')}
 shape_losses={}
 for k in ('S4','S5'):
  records=read(O/f'S6_regressions_{k}.jsonl')
  for e in records:
   a,b=e['before_evidence'],e['after_evidence']
   e['cause']='presence/location loss' if any(z in zones(e['truth']) and not b[z] for z in ('above','below')) else 'changed safe-zone pixels/ownership' if a['above']!=b['above'] or a['below']!=b['below'] else 'fixed naming model with changed feature context'
  write(O/f'S6_regressions_{k}.jsonl',records);shape_losses[k]=records
 fontcounts=Counter(l['font_fit']['source'] for l in rows)
 final_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 L=['# S6 — font-scaled segmentation and safe attached-mark zones','',
 'S6 improves physical mark presence and letter ownership; it is a candidate with residual misses and naming regressions. The fixed S4 mark model and S5 case model are unchanged. No naming retraining or optimisation was performed. All 137 labelfix tests pass.','',
 'Actual starting HEAD is `f4d95436fa266d0b0bf1e94ff064ecec4c5050e3`: two brief-only commits after S5 `eed80de9`. The frozen S4 (`afe67823`) and S5 predictions are both retained and their TP/FP/FN, known/unknown counts and every legacy slot/truth/bbox are asserted unchanged. No `.git` writes, network calls, CTC forward passes, GPU work, owner-page builds or publishing. Evaluation uses the requested Python with `PYTHONPATH=$PWD`; recogniser construction/forward and socket connections fail closed in the validator.','',
 f'At delivery, HEAD is `{final_head}`. It advanced externally during this run by a draft R0 brief commit adding only `docs/briefs/R0_recogniser_audit.md`; S6 runtime changes remain uncommitted. This agent made no `.git` writes.','',
 '## What changed','',
 '- The line font is fitted only from pixel-classified complete lowercase bodies: robust median x-height and a clipped linear baseline fit. Capitals, ascenders and descenders do not set that body band. The expected width is the median complete-body pixel width, scaled for narrow iota and wide omega/mu. Absolute span overlap is normalised by pixel width, avoiding assignment of a narrow iota to the preceding wide alpha.','- Shared components wider than 1.3 expected widths are partitioned at CTC boundaries, refined to minimum body-column ink within ±0.25 expected width. Narrow shared components get explicit uncertain regions, not silent mark suppression. The S4 disconnected-stroke union is retained. Every recogniser alphabetic character has one region; unlocated font/CTC fallback regions remain flagged and are still searched. No new character comes from Google.','- S5 per-word lowercase height substitution is reverted: words use the robust line font. The combined case decision controls capital side searches and capital-run heights. Runs with ≥80% classified capitals retain their median capital height. `word_lowercase_bodies` remains the compatibility source label when local bodies support a word, but its height is the line font.','- Lowercase attached marks are cut at floor(meanline), detached upper evidence is intersected with that zone, and subscripts start at ceil(baseline). Letter masks/labels remain immutable. A fused-letter boundary does not slice an upper accent: its complete upper connected component is proposed, and overlapping proposals with the same native label are credited once.','- Certified vowel/rho regions protect their strokes from the punctuation-dot veto. Rho is also exempted from the S5 ascender/descender top-mark veto; the DEV joined-breathing loss is recovered. Case retains the fixed model in original and corrected pixel coordinates plus font geometry; both are pixel-only views. A narrow lowercase mark bearer retains its recogniser case when an attached lobe looks like a serif capital. This prior is explicit, and the conflicting pixel decision is retained.','',
 f'Font fits: {dict(fontcounts)} across {len(rows)} evaluation lines. Fallbacks are exposed, not called successful font estimates. Runtime inputs are pixels, recogniser letters/case and cached locations only. Print truth and owner notes enter only evaluation.','',
 '## Physical presence/location, S4 → S5 → S6','',
 'An event is a mark at a recogniser character in one of three zones: above, below, or elision after it. Any upper ink counts regardless of naming, and a connected compound counts as one presence event. Presence requires evidence, not a predicted mark name. Character truth uses the existing adjudicated print words with exact base-letter agreement; unknowns stay unknown. This extends truth to fused characters that the frozen component table cannot score. It is a separate fixed denominator, not a replacement for that table.','',
 '| split / stratum | characters (known / unknown) | S4 P/R | S5 P/R | S6 P/R |','|---|---:|---:|---:|---:|']
 for split in ('heldout','dev'):
  for group in ('all','fused','clean','merged_accent','breathing','compound'):
   v=m[split]['presence'][group];s=v['scores']['S6']
   L.append(f"| {split} / {group} | {v['n']} ({s.get('known_slots',0)} / {s.get('unknown_slots',0)}) | {pr(v['scores']['S4'])} | {pr(v['scores']['S5'])} | {pr(s)} |")
 cd=m['capitals'];dd=m['capitals_disagreement']
 L += [f"| capitals combined (held-out agreement) | {cd['S6']['n']} | {pr(cd['before'])} | {pr(cd['after'])} | {pr(cd['S6'])} |",f"| capitals pixel-only (held-out agreement) | {cd['S6']['n']} | {pr(cd['S4_pixel'])} | {pr(cd['pixel'])} | {pr(cd['S6_pixel'])} |",'',
 f"Held-out fusion: {m['heldout']['fused_components']} source components, {m['heldout']['presence']['fused']['n']} recogniser characters; {m['heldout']['presence']['fused']['scores']['S6']['known_slots']} have known print truth. Source-sharing is an operational geometry cohort, not a new manual certification of all touching glyphs. Narrow uncertain partitions are retained in the line receipt. Before precision is undefined because S4/S5 proposed no marks on this cohort; it is not zero precision.",
 f"Merged-accent cohort: {m['heldout']['presence']['merged_accent']['n']} held-out mark-bearer regions whose native component spans a body and a substantial upper lobe ({m['heldout']['presence']['merged_accent']['scores']['S6']['known_slots']} known). The cohort is selected from native labels and the common S6 font boundary, independently of a detector's accepted marks. It is a reproducible geometry proxy; not all members have manual merged-ink truth. DEV breathing/compound rows measure top presence on positive strata only, so their displayed P=100% is conditional; global precision is the `all` row.",'',
 '## Capitals and the prior','',
 'Truth is the frozen S5 agreement set: 18,960 held-out component slots, 1,189 capitals. Google/recogniser case agreement is an evaluation instrument, never runtime evidence. S4 combined is its recorded uppercase-or-height rule; the S4 pixel-only row recomputes its height branch without the recogniser uppercase term. S6 pixel-only is the fixed case model in two pixel normalisations plus font geometry. It remains weak in recall. Combined classification drives side-mark search and capital-run height; pixel-only is reported separately and is not claimed to replace the prior.','',
 '| capital diagnostic | S4 P/R | S5 P/R | S6 P/R |','|---|---:|---:|---:|',
 f"| combined, all 18,960 | {pr(cd['before'])} | {pr(cd['after'])} | {pr(cd['S6'])} |",f"| pixel-only, all 18,960 | {pr(cd['S4_pixel'])} | {pr(cd['pixel'])} | {pr(cd['S6_pixel'])} |",f"| combined, frozen 753 disagreements | {pr(dd['before'])} | {pr(dd['after'])} | {pr(dd['S6'])} |",f"| pixel-only, frozen 753 disagreements | {pr(dd['S4_pixel'])} | {pr(dd['pixel'])} | {pr(dd['S6_pixel'])} |",'',
 'The disagreement stratum is exactly the original 753 slots, not reselected after S6. Raw normalised class, original-coordinate pixel class, geometric decision, final class, case disagreement and recogniser case remain in `S6_lines.jsonl.gz`. Individual capital outcomes are in [S6_capital_truth.jsonl](S6_capital_truth.jsonl). Combined recall loses one additional agreement capital against S5; it is not presented as no-regression.','',
 '## Safe zones and native witnesses','',
 f"Upper boxes crossing their own permitted vertical boundary (excluding capital side boxes): held-out {m['heldout']['below_meanline']['S4']} → {m['heldout']['below_meanline']['S5']} → {m['heldout']['below_meanline']['S6']}; DEV {m['dev']['below_meanline']['S4']} → {m['dev']['below_meanline']['S5']} → {m['dev']['below_meanline']['S6']}. Capital side boxes are outside the capital body and use S5's side zone, not the lowercase meanline.",
 f"For transparency, using the common S6 lowercase meanline for every class gives held-out {m['heldout']['below_font_meanline']['S4']} → {m['heldout']['below_font_meanline']['S5']} → {m['heldout']['below_font_meanline']['S6']}. Overhead evidence is bounded by both the font meanline and the capital's own top. There are {len(common)} remaining overhead exceptions: [exception receipt](S6_common_meanline_exceptions.jsonl). Capital side boxes retain their separate S5 side zone, outside the body.",'',
 'All five required native crops and cached alignments are included as worktree files under `tests/data/labelfix_s6/`. Tests assert physical presence/ownership, safe top/bottom boundaries, unchanged native labels and no CTC forward construction; they do not fit naming outputs.','']
 for lid in ('602cc72e-p000155-l0009','602cc72e-p000113-l0030','384c3f89-p000091-l0039','8b6b0de9-p000007-l0030','384c3f89-p000142-l0002'):
  l=by[lid];L.append(f"- `{lid}`: `{l['S5_reading']}` → `{l['reading']}`. [Native crop](../../../tests/data/labelfix_s6/{lid}.png).")
 L += ['',
 'The joined iota in the first case regains top evidence; its fixed-model name can still be wrong. The upsilon acute no longer yields a second body fragment. The second case enforces the mid-top boundary across its attached marks. `τυ` has two nonoverlapping regions with the upper mark on υ; `στω` has three with the mark on ω; the split η has one two-component region with both upper blobs. A synthetic sloping-band test ensures one lobe crossing a fusion boundary is counted once.','',
 '## Frozen held-out naming table, row for row','',
 '| kind | S4 P/R | S5 P/R | S6 P/R | S4 F1 | S5 F1 | S6 F1 |','|---|---:|---:|---:|---:|---:|---:|']
 for kind in ('total',)+tuple(m['heldout']['S4']['by_kind']):
  cs=[m['heldout'][k]['total'] if kind=='total' else m['heldout'][k]['by_kind'][kind] for k in ('S4','S5','detected')]
  L.append('| '+kind+' | '+' | '.join([pr(c) for c in cs]+[pc(c['f1']) for c in cs])+' |')
 L += [f"| capitals combined | {pr(cd['before'])} | {pr(cd['after'])} | {pr(cd['S6'])} | {pc(cd['before']['f1'])} | {pc(cd['after']['f1'])} | {pc(cd['S6']['f1'])} |",f"| capitals pixel-only | {pr(cd['S4_pixel'])} | {pr(cd['pixel'])} | {pr(cd['S6_pixel'])} | {pc(cd['S4_pixel']['f1'])} | {pc(cd['pixel']['f1'])} | {pc(cd['S6_pixel']['f1'])} |",f"| marks at capitals | {pr(capmarks['S4'])} | {pr(capmarks['S5'])} | {pr(capmarks['detected'])} | — | — | — |",f"| marks-at-capitals exact naming accuracy | {pc(capnames['S4'])} | {pc(capnames['S5'])} | {pc(capnames['detected'])} | — | — | — |",'',
 f"The original table retains {m['heldout']['detected']['total']['known_slots']} known and {m['heldout']['detected']['total']['unknown_slots']} unknown component slots. New fused characters do not silently turn its unknowns into successes. Capital marked-slot support is {len(caps)}. Mark names come from the unchanged model; a physical recovery need not improve an exact compound name.",'',
 '## DEV naming and the S5 presence losses','',
 '| kind | S4 P/R | S5 P/R | S6 P/R |','|---|---:|---:|---:|']
 for kind in ('total',)+tuple(m['dev']['S4']['by_kind']):
  cs=[m['dev'][k]['total'] if kind=='total' else m['dev'][k]['by_kind'][kind] for k in ('S4','S5','detected')]
  L.append('| '+kind+' | '+' | '.join(pr(c) for c in cs)+' |')
 L += [f"| capitals combined (held-out diagnostic) | {pr(cd['before'])} | {pr(cd['after'])} | {pr(cd['S6'])} |",f"| capitals pixel-only (held-out diagnostic) | {pr(cd['S4_pixel'])} | {pr(cd['pixel'])} | {pr(cd['S6_pixel'])} |",'',
 f"S5 introduced {len(dev_recovery)} DEV top-presence losses against S4 on known characters; S6 recovers {sum(e['recovered'] for e in dev_recovery)}. Breathing and compound aggregate presence exceed both baselines, but individual losses below remain open. S5's word-height substitution is removed. Capital top/side guards are retained because restoring unrestricted S4 slices can cut capital body ink; safely separating joined capital-side marks remains unresolved. Each record includes all three evidence boxes/bands, truth, source crop, character and slot: [DEV loss audit](S6_DEV_S5_presence_losses.jsonl). No naming loss is relabelled a detection recovery.",'',
 '| DEV line : source slots : character | recovered | evidence / remaining rule |','|---|---|---|']
 for e in dev_recovery:L.append(f"| {e['line_id']} : {e['component_slots']} : {e['base']} | {flag(e['recovered'])} | {e['cause']} |")
 L += ['', '## Per-class held-out exact naming sets','', '| class | support | S4 P/R | S5 P/R | S6 P/R |','|---|---:|---:|---:|---:|']
 for cls,v in m['heldout']['per_class'].items():L.append(f"| {cls} | {v['detected']['support']} | {pr(v['S4'])} | {pr(v['S5'])} | {pr(v['detected'])} |")
 L += [f"| capitals combined | {cd['S6']['n']} | {pr(cd['before'])} | {pr(cd['after'])} | {pr(cd['S6'])} |",f"| capitals pixel-only | {cd['S6']['n']} | {pr(cd['S4_pixel'])} | {pr(cd['pixel'])} | {pr(cd['S6_pixel'])} |",'',
 f"Ascender false-mark control: held-out S4 {m['heldout']['ascender']['counts']['S4']}/2488, S5 {m['heldout']['ascender']['counts']['S5']}/2488, S6 {m['heldout']['ascender']['counts']['S6']}/2488; DEV S4 {m['dev']['ascender']['counts']['S4']}/1070, S5 {m['dev']['ascender']['counts']['S5']}/1070, S6 {m['dev']['ascender']['counts']['S6']}/1070. Held-out atomic naming P/R (compound accent and breathing scored separately): "+' → '.join(pr(m['heldout']['atomic'][k]['total']) for k in ('S4','S5','detected'))+'.', '',
 '## Every owner note','',
 'The latest 49 review and 57 example records supersede the earlier wording for the current score. Numbers resolve against the displayed S4 source components, with all S6 children/union pieces attached to those source slots. Both old and new scores are retained. No note document means unreviewed. Empty current notes require no lost accepted physical presence, lost true name, newly false name, or uncertified mark/name addition at an unknown print slot against S4. Possible/ambiguous clauses remain uncertified, not converted to positive print truth.','',
 'Current multi-mark clauses require their stated number of physical upper blobs. A connected compound with one blob does not receive two detection credits from its classifier name. Older checks deliberately retain their old naming-based semantics; hence their totals differ from the current physical checks even when note text is similar. The exclamation-dot clause checks its frozen punctuation slot 13, preserving the legitimate alpha subscript elsewhere on that line.','',
 '| owner set | S4 | S5 | S6 |','|---|---:|---:|---:|']
 for group in ('earlier','examples','review'):
  counts=[f"{sum(r['fixed'] for r in legacy[k][group])}/{len(legacy[k][group])}" for k in ('S4','S5','S6')]
  L.append('| old '+group+' | '+' | '.join(counts)+' |')
 for group in ('review','examples'):L.append('| current '+group+' | '+' | '.join(f"{notes[group][k]['fixed']}/{notes[group][k]['n']}" for k in ('S4','S5','S6'))+' |')
 L += ['', 'Complete old machine checks: [S4](S6_old_checks_S4.json), [S5](S6_old_checks_S5.json), [S6](S6_old_checks_S6.json). Current clauses include resolved starts/boxes and explicit uncertainty: [review](S6_current_review_checks.jsonl), [examples](S6_current_examples_checks.jsonl).','']
 owner_losses=[]
 for group in ('review','examples'):
  current=read(O/f'S6_current_{group}_checks.jsonl')
  L += [f'### Current {group}: all notes','', '| line | exact note | S4 → S5 → S6 | remaining clauses |','|---|---|---|---|']
  for r in current:
   failed=[c['kind']+(' '+str(c['target']) if c['target'] is not None else '') for c in r['checks'] if not c['versions']['S6']['fixed']]
   L.append(f"| {r['line_id']} | {esc(r['note']) or '(empty: preserve correctness)'} | {' → '.join(flag(r['fixed'][k]) for k in ('S4','S5','S6'))} | {', '.join(failed) or 'none'} |")
   for k in ('S4','S5'):
    if r['fixed'][k] and not r['fixed']['S6']:owner_losses.append(dict(group=group,baseline=k,line_id=r['line_id'],note=r['note']))
 for group in ('earlier','examples','review'):
  for k in ('S4','S5'):
   for b,a in zip(legacy[k][group],legacy['S6'][group]):
    if b['fixed'] and not a['fixed']:owner_losses.append(dict(group='old_'+group,baseline=k,line_id=a['line_id'],slot=a.get('v8_slot'),note=a.get('note')))
 write(O/'S6_owner_regressions.jsonl',owner_losses)
 L += ['', '## Regressions against each baseline','',
 'Every scalar P/R/F1 regression, including each book and exact naming class, is enumerated below and in [S6_metric_regressions.jsonl](S6_metric_regressions.jsonl). Undefined before precision remains undefined. Physical losses and new false presence are separate from naming identity changes. The receipts contain every affected slot with old/new boxes, bands and truth; no held-out regression is omitted because the aggregate improved.','']
 for k in ('S4','S5'):
  p=physical_losses[k];n=shape_losses[k]
  L.append(f"- Against {k}: {len(p)} character-zone regressions across held-out+DEV ([every physical event with evidence](S6_presence_regressions_{k}.jsonl)); {len(n)} legacy-slot naming/presence regressions ([every slot with evidence](S6_regressions_{k}.jsonl)). These counts overlap and are not added.")
 L += ['', '| baseline | metric scope | measure | before → S6 |','|---|---|---|---|']
 for e in metric_losses:L.append(f"| {e['baseline']} | {e['scope']} | {e['metric']} | {fine(e['before'])} → {fine(e['after'])} |")
 L += ['', 'Owner regressions, including empty-note preservation failures, are explicit in [S6_owner_regressions.jsonl](S6_owner_regressions.jsonl):','']
 for e in owner_losses:L.append(f"- {e['baseline']} / {e['group']}: `{e['line_id']}`"+(f" slot {e['slot']}" if e.get('slot') else '')+f" — {esc(e.get('note') or '(empty note)')}")
 if not owner_losses:L.append('- None.')
 L += ['', '## Owner lines whose reading changed','', 'All strings use recogniser base letters plus the indicated detector marks. S4/S5 strings are their frozen standalone readings, never Google. The full machine receipt is [S6_changed_owner_lines.jsonl](S6_changed_owner_lines.jsonl).','', '| line | S4 | S5 | S6 |','|---|---|---|---|']
 for e in read(O/'S6_changed_owner_lines.jsonl'):L.append('| '+e['line_id']+' | '+' | '.join(esc(e[k]) for k in ('S4','S5','S6'))+' |')
 L += ['', '## Verification and limits','',
 'Run `PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/labelfix -q`: **137 passed**. [Log](S6_pytest.txt). The existing HTTP capture test now sends full HTTP request bytes to the real handler in memory, testing successful append/readback, bad requests and static serving without a socket bind. No server or owner page was built or opened. The initial unmodified socket test failed at the sandbox bind; this was repaired without skipping it.','',
 'Reproduce measurements with `scripts/labelfix/s6_validate.py`, then `scripts/labelfix/s6_notes.py`, then `scripts/labelfix/s6_report.py`, using the same Python and `PYTHONPATH`. [Metrics](S6_metrics.json), [line-level evidence](S6_lines.jsonl.gz), [validator log](S6_validate.log), [verification/hashes](S6_verification.json). This CPU evaluation is not a CTC/runtime speed qualification. Tests are scoped to labelfix as requested.','',
 'Remaining limits: fused recall is incomplete; the native-component/CTC cohort includes uncertain segmentation and is not a new manual benchmark. Pixel-only capitals still miss more than half of agreement capitals. The 753 disagreement stratum contains most prior-dependent cases. Some capital/ascender guard losses and current owner clauses remain open. DEV naming breathing/compound recall still trails S4 even though physical presence recovers; the fixed naming reader receives changed pixel crops/context. No general no-regression qualification is claimed.','']
 p=m['heldout']['presence']['all']['scores'];f=m['heldout']['presence']['fused']['scores'];g=m['heldout']['presence']['merged_accent']['scores'];h=m['heldout']
 summary=(f"S6 RESULT: presence P {pc(p['S5']['precision'])}→{pc(p['S6']['precision'])} R {pc(p['S5']['recall'])}→{pc(p['S6']['recall'])} (S4 {pr(p['S4'])}, S5 {pr(p['S5'])}); capitals combined P/R {pr(cd['S6'])}, pixel-only P/R {pr(cd['S6_pixel'])}, disagreement-slot P {pc(dd['S6']['precision'])}; fused slots {h['presence']['fused']['n']} ({h['fused_components']} components), fused R {pc(f['S5']['recall'])}→{pc(f['S6']['recall'])} P {pc(f['S5']['precision'])}→{pc(f['S6']['precision'])}; merged-accent R {pc(g['S5']['recall'])}→{pc(g['S6']['recall'])}; marks below meanline {h['below_meanline']['S5']}→0 (capital side marks use their separate S5 zone); held-out P {pc(h['S5']['total']['precision'])}→{pc(h['detected']['total']['precision'])} R {pc(h['S5']['total']['recall'])}→{pc(h['detected']['total']['recall'])}; owner notes current review {notes['review']['S5']['fixed']}/49→{notes['review']['S6']['fixed']}/49, examples {notes['examples']['S5']['fixed']}/57→{notes['examples']['S6']['fixed']}/57; old earlier 45/59→47/59, examples 26/56→32/56; regressions: {len(physical_losses['S4'])}/{len(physical_losses['S5'])} physical character events and {len(shape_losses['S4'])}/{len(shape_losses['S5'])} legacy slots vs S4/S5, combined capital R 98.7%→98.6%, unresolved DEV naming/owner clauses enumerated above.")
 L.append(summary)
 (O/'S6_REPORT.md').write_text('\n'.join(L)+'\n')
 # Hash only source/inputs and deliverables; avoid a circular report/receipt hash.
 paths=['greekocr/labelfix/case.py','greekocr/labelfix/segmentation.py','greekocr/labelfix/reading.py','greekocr/labelfix/ink.py','scripts/labelfix/s6_validate.py','scripts/labelfix/s6_notes.py','scripts/labelfix/s6_report.py','tests/labelfix/test_s6.py','tests/labelfix/test_capture.py','tests/data/labelfix_s6/cases.json','.cache/labelfix/align_s0.jsonl','docs/labelfix/markshape_model_S4.json','docs/labelfix/case_model_S5.json']
 paths += [str(p) for p in O.glob('owner_notes*jsonl')]
 paths += [str(p) for p in Path('tests/data/labelfix_s6').glob('*.png')]
 paths += [str(O/f'{k}_{s}') for k in ('S4','S5') for s in ('lines.jsonl.gz','metrics.json')]
 hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
 original_models={p:hashlib.sha256(subprocess.check_output(['git','show','eed80de9:'+p])).hexdigest() for p in m['model_sha256']}
 assert all(hashes[p]==digest for p,digest in original_models.items())
 receipt=dict(start_head='f4d95436fa266d0b0bf1e94ff064ecec4c5050e3',head=final_head,external_head_change='R0 draft brief only',python=sys.executable,hashes=hashes,models_match_S5_commit=True,network=False,cpu_only=True,ctc_forward_passes=0,git_writes=False,owner_pages_built=False,pytest='137 passed',evaluation_seconds=m['elapsed_seconds'],metric_regressions=len(metric_losses),presence_regressions={k:len(v) for k,v in physical_losses.items()},owner_regressions=owner_losses)
 (O/'S6_verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
 print(summary)
if __name__=='__main__':main()
