"""S5 evaluation-only accounting. Never builds or publishes owner pages."""
import os
for k in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
import json,gzip,hashlib
from pathlib import Path
from collections import Counter
from s5_notes import evaluate
from s4_report import read,pc
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd,clusters,tokenize
from greekocr.labelfix.linemetric import score_slots,mark_set
from greekocr.labelfix.markshape import load_model
O=Path('docs/labelfix/spellcheck')
def main():
 rows=read(O/'S5_lines.jsonl.gz');before=read(O/'S4_lines.jsonl.gz');bb={l['line_id']:l for l in before};m=json.loads((O/'S5_metrics.json').read_text());sources={l['line_id']:l for l in load_three_way(0)}
 assert [l['line_id'] for l in rows]==[l['line_id'] for l in before]
 checks=evaluate(rows,before)
 for key,name in [('examples','owner_examples_expectations.jsonl'),('review','S5_review_expectations.jsonl'),('earlier','S5_owner_expectations.jsonl')]:
  (O/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in checks[key]))
 caps=[];eligible=[]
 for l in rows:
  if l['dev']:continue
  src=sources[l['line_id']];pairs=pair_tokens(nfd(src['google']),nfd(src['model']))
  agreement={}
  for g,r in pairs:
   if r is None:continue
   gc,rc=clusters(g.core),clusters(r.core)
   if len(gc)!=len(rc):continue
   for j,(a,b) in enumerate(zip(gc,rc)):
    if a.base==b.base and a.base.isalpha():agreement[(g.index,j)]=a.base
  for s in l['slots']:
   base=agreement.get((s['word'],s['char']))
   if base is None:continue
   truth=base.isupper();a=s.get('case_class')=='capital';b=base.isupper() or (s['bbox'][3]-s['bbox'][1]>=1.25*s['before_evidence']['xh'] and s['bbox'][1]<s['before_evidence']['meanline']-.2*s['before_evidence']['xh'])
   eligible.append(dict(line_id=l['line_id'],slot=s['slot'],truth=truth,before=b,after=a,pixel=s.get('pixel_class')=='capital',recogniser_upper=s.get('recogniser_base','').isupper(),case_disagreement=s.get('case_disagreement')))
   if truth and s['truth'] and any(k!='apostrophe' for k,v in s['truth']):caps.append(s)
 def det(key):
  tp=sum(e['truth'] and e[key] for e in eligible);fp=sum(not e['truth'] and e[key] for e in eligible);fn=sum(e['truth'] and not e[key] for e in eligible)
  return dict(tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
 m['capital_detection']=dict(n=len(eligible),capitals=sum(e['truth'] for e in eligible),before=det('before'),after=det('after'),pixel=det('pixel'),disagreements=sum(e['case_disagreement'] is True for e in eligible),disagreement_denominator=sum(e['case_disagreement'] is not None for e in eligible))
 (O/'S5_capital_truth.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in eligible))
 m['capital_marks']={key:score_slots([dict(s,detected=s[key],unknown_kinds=[]) for s in caps])['total'] for key in ('before','detected')}
 m['capital_naming']={key:dict(n=len(caps),correct=sum(set(map(tuple,s['truth']))==set(map(tuple,s[key])) for s in caps),accuracy=sum(set(map(tuple,s['truth']))==set(map(tuple,s[key])) for s in caps)/len(caps) if caps else None) for key in ('before','detected')}
 m['owner']={k:dict(before=sum(e.get('s4_fixed',e.get('before_fixed',False)) for e in rs),after=sum(e['fixed'] for e in rs),n=len(rs)) for k,rs in checks.items()}
 ownerids={e['line_id'] for rs in checks.values() for e in rs}
 changed=[dict(line_id=l['line_id'],before=bb[l['line_id']]['reading'],after=l['reading']) for l in rows if l['line_id'] in ownerids and l['reading']!=bb[l['line_id']]['reading']]
 (O/'S5_changed_owner_lines.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in changed))
 bands=[dict(line_id=l['line_id'],slot=s['slot'],base=s.get('recogniser_base'),case=s.get('case_class'),band=s.get('height_band'),old_meanline=s['before_evidence']['meanline'],meanline=s['evidence']['meanline'],band_source=s['evidence'].get('band_source')) for l in rows if l['line_id'] in ownerids for s in l['slots']]
 (O/'S5_owner_bands.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in bands))
 # Supplementary C1 diagnostic is explicitly in-sample for S4 mark naming.
 samples=read(O/'S4_training_samples.jsonl.gz');dia=[s for s in samples if s['source']=='C1' and 'dialytika' in s['label']]
 model=load_model(Path('docs/labelfix/markshape_model_S4.json'));pred=model.probs([s['x'] for s in dia]).argmax(1)
 m['dialytika_C1_training_diagnostic']=dict(n=len(dia),correct=sum(model.classes[p]==s['label'] for p,s in zip(pred,dia)),independent=False)
 regress=[]
 for split,b,a in [('held-out',m['before'],m['after']),('DEV',m['dev_before'],m['dev_after'])]:
  for k in ['total']+list(b['by_kind']):
   bc=b['total'] if k=='total' else b['by_kind'][k];ac=a['total'] if k=='total' else a['by_kind'][k]
   for key in ('precision','recall','f1'):
    if bc[key] is not None and ac[key] is not None and ac[key]<bc[key]-1e-12:regress.append(f'{split} {k} {key} {pc(bc[key])}→{pc(ac[key])}')
 lost=[f"{e['line_id']}:{e['v8_slot']}" for e in checks['earlier'] if e['s4_fixed'] and not e['fixed']]
 if lost:regress.append('owner expectations lost '+','.join(lost))
 empties=[e['line_id'] for e in checks['examples']+checks['review'] if not e['note'] and not e['fixed']]
 if empties:regress.append('empty-note regression '+','.join(empties))
 m['regressions']=regress
 (O/'S5_metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 L=['# S5 — case-aware detector candidate','',
 'CPU only, offline, cached alignments, zero CTC forward passes. Changes remain in the worktree; no git writes or owner-page builds. Start HEAD `28aac666bf8e5c0e0e4cafdfd549712af2a7ed6a`. Baseline first: `S5_baseline_owner_checks.json` was written before detector changes: S4 27/56 examples, 22/33 review notes, 46/59 earlier expectations. Baseline comes from the frozen S4 line predictions and S4 model; aggregate TP/FP/FN equality is asserted. Every S4 line, component slot, unknown truth, and held-out book is retained in order.','',
 'Runtime reads recogniser letters and pixel marks only. The C1 pixel classifier uses baseline-relative height, width, descender depth, stroke thickness, occupancy, holes and an 8×8 shape grid. Agreement labels include case. The recogniser contributes a bounded case prior; raw pixel class, probability, recogniser case and disagreement remain visible. Reading preserves the recogniser base characters even when case disagrees. Every letter/large component receives a case class; ambiguous character ownership remains flagged.','',
 'Word bands use complete lowercase-body components, excluding classified capitals, ascenders and descenders. A word with fewer than two reliable bodies borrows the line body band; a line without four reliable bodies keeps the frozen band and records the fallback. Runs with at least 80% classified capitals receive their own height band. Capitals use their own top for the mark zone and left-gap search; recognised vowels retain attached-mark extraction even when their body shape is descender-like (notably eta). This avoids confusing a descender body with absence of a top mark.','',
 'The first DEV audit showed over-vetoing of joined marks on eta and accented vowels classified as ascenders. That veto was narrowed to non-vowel bodies. No model or thresholds were fitted to held-out marks. The result remains a candidate; the requested no-regression and naming goals are assessed below.','',
 '## Frozen held-out table: 666 lines, 14 books','', '| kind | S4 P | S5 P | S4 R | S5 R | S4 F1 | S5 F1 |','|---|---:|---:|---:|---:|---:|---:|']
 for k,b,a in [('total',m['before']['total'],m['after']['total'])]+[(k,b,m['after']['by_kind'][k]) for k,b in m['before']['by_kind'].items()]:L.append(f"| {k} | {pc(b['precision'])} | {pc(a['precision'])} | {pc(b['recall'])} | {pc(a['recall'])} | {pc(b['f1'])} | {pc(a['f1'])} |")
 cd=m['capital_detection'];cn=m['capital_naming'];cm=m['capital_marks']
 L += [f"| capital detection P | {pc(cd['before']['precision'])} | {pc(cd['after']['precision'])} | — | — | — | — |",f"| capital detection R | — | — | {pc(cd['before']['recall'])} | {pc(cd['after']['recall'])} | — | — |",f"| marks-at-capitals naming accuracy | {pc(cn['before']['accuracy'])} | {pc(cn['detected']['accuracy'])} | — | — | — | — |",'',f"Capital truth: {cd['n']} held-out slots where Google and recogniser base letters agree exactly, including case, ignoring marks; {cd['capitals']} capitals. This is the requested agreement stratum, not recogniser uppercase used as truth by itself. Raw pixel-only P/R {pc(cd['pixel']['precision'])}/{pc(cd['pixel']['recall'])}; pixel/recogniser disagreements {cd['disagreements']}/{cd['disagreement_denominator']}. Slot receipt: `S5_capital_truth.jsonl`. Capital marked-slot support {cn['before']['n']}; mark P/R {pc(cm['before']['precision'])}/{pc(cm['before']['recall'])} → {pc(cm['detected']['precision'])}/{pc(cm['detected']['recall'])}. Naming accuracy requires the entire mark set, counting missed sets wrong.",'',
 '## Class balance and S4 regressions','', 'Hypothesis tested before detector edits and rejected: C1 has more dialytika and compounds proportionally than DEV. No rebalance on that unsupported premise. Counts are all available samples before bounding; S4 also uses square-root inverse-frequency weighting. Existing S4 mark weights are retained, so the old naming regressions are not claimed recovered by retraining. Dialytika predictions now require the physical two-dot shape.','', '| class | DEV | C1 | total |','|---|---:|---:|---:|']
 counts=json.loads((O/'S5_class_balance.json').read_text())
 for cls in sorted(counts['total']):L.append(f"| {cls} | {counts['DEV'].get(cls,0)} | {counts['C1'].get(cls,0)} | {counts['total'][cls]} |")
 L+=['',f"DEV dialytika support is 3 slots; held-out is 4. Supplementary C1 agreement naming diagnostic: {len(dia)} slots, {m['dialytika_C1_training_diagnostic']['correct']} exact classifications. These samples were used to train S4; this is explicitly an in-sample shape diagnostic, not independent accuracy. No new crops or held-out books were fitted.",'','| regression check | S3 | S4 | S5 |','|---|---:|---:|---:|']
 s4=json.loads((O/'S4_metrics.json').read_text())
 for title,old,b,a in [('DEV compound P',.930,m['dev_before']['by_kind']['compound']['precision'],m['dev_after']['by_kind']['compound']['precision']),('psili+circumflex P',.769,m['per_class']['psili+circumflex']['before_precision'],m['per_class']['psili+circumflex']['precision']),('circumflex R',.967,m['per_class']['circumflex']['before_recall'],m['per_class']['circumflex']['recall']),('DEV dialytika P',1.,m['dev_before']['by_kind']['dialytika']['precision'],m['dev_after']['by_kind']['dialytika']['precision'])]:L.append(f'| {title} | {pc(old)} | {pc(b)} | {pc(a)} |')
 L+=['','These are classifier/feature-context failures, not rare-class scarcity: S4 retained 730 psili+circumflex, 1,729 circumflex, 450 dialytika fit examples. Feature normalisation and whole-set/per-blob composition can change a label despite identical physical evidence. Per-class exact-set results and the complete before/after evidence are retained in `S5_metrics.json` and `S5_lines.jsonl.gz`.','',
 'One-line causes of the named S4 losses (unchanged frozen truth):','',
 '- `602cc72e-p000155-l0009:11`: the attached tall oblique at bbox [478,8,489,30] is named psili rather than printed grave; localisation recovered the blob, but naming lost the expectation.',
 '- `8b6b0de9-p000008-l0001:12`: the fused attached blob [417,4,442,26] is named dasia+circumflex rather than dasia+acute; the subscript is retained, so this is accent identity, not missing mark detection.',
 '- `384c3f89-p000182-l0031:8`: S4 names the two blobs dasia+grave where frozen truth says psili+circumflex; S3 was already wrong, but S4 introduced a different false identity, violating the S3 empty-note preservation gate. The S5 baseline preservation gate separately compares against S4.','',
 '## Per-class held-out exact sets','', '| class | support | S4 P/R | S5 P/R |','|---|---:|---|---|']
 for cls,c in m['per_class'].items():L.append(f"| {cls} | {c['support']} | {pc(c['before_precision'])}/{pc(c['before_recall'])} | {pc(c['precision'])}/{pc(c['recall'])} |")
 L+=['','## Ascender false marks','', '| split | slots | S4 | S5 |','|---|---:|---:|---:|']
 for split,c in m['ascender'].items():L.append(f"| {split} | {c['n']} | {c['before']} ({pc(c['before']/c['n'])}) | {c['after']} ({pc(c['after']/c['n'])}) |")
 L+=['','## All owner checks','', 'All 56 current example records and all 33 review notes are checked; review `printed` prefills are never read. The original 59 preserve their v8 overlap resolution. Examples resolve letter-component slots against both S2 and S3; differing resolutions and qualitative ambiguous notes fail certification rather than invent truth. Empty notes require no lost true mark or new false identity against S4.','', '| set | S4 | S5 |','|---|---:|---:|']
 for k,v in m['owner'].items():L.append(f"| {k} | {v['before']}/{v['n']} | {v['after']}/{v['n']} |")
 for key in ['examples','review']:
  L+=['',f'### {key}: every note','', '| line | note | S4 → S5 |','|---|---|---|']
  for e in checks[key]:L.append(f"| {e['line_id']} | {e['note'].replace(chr(10),' ')} | {e['before_fixed']} → {e['fixed']} |")
 L+=['','### Earlier 59 expectations','', '| line:slot | S4 → S5 |','|---|---|']
 for e in checks['earlier']:L.append(f"| {e['line_id']}:{e['v8_slot']} | {e['s4_fixed']} → {e['fixed']} |")
 L+=['','## Owner height-band changes','', 'Every owner slot, class, old/new meanline, word x-height, and fallback reason is recorded in `S5_owner_bands.jsonl`. Per-line ranges below exclude unavailable ownership.','', '| line | S4 xh | S5 word xh range | capital bands |','|---|---:|---|---:|']
 for lid in sorted(ownerids):
  ss=[e for e in bands if e['line_id']==lid and e['band']]
  if ss:L.append(f"| {lid} | {ss[0]['band']['old_xh']:.2f} | {min(e['band']['xh'] for e in ss):.2f}–{max(e['band']['xh'] for e in ss):.2f} | {sum(e['band_source']=='capital_height' for e in ss)} |")
 L+=['','## Changed independent owner readings','']
 for e in changed:L.append(f"- `{e['line_id']}`: {e['before']} → {e['after']}")
 L+=['','## Qualification and verification','', 'Requested owner strings are not silently relabelled. The retained frozen print instrument, owner diagnosis and native-crop witnesses are reported separately; changing case geometry alone does not establish Ἦ/Ἤ or rough/smooth breathing correctness. Remaining literal naming failures are open. This is not a qualified replacement if any required regression or owner gate remains unmet. Test logs: `S5_pytest.txt`, `S5_pytest_runnable.txt`. The capture test requires a localhost bind forbidden by this sandbox and cannot pass here.','', 'Regressions: '+('; '.join(regress) or 'none in reported S4 comparisons')+'.','']
 own=m['owner'];asc=m['ascender']['held-out'];b,a=m['before']['total'],m['after']['total']
 L.append(f"S5 RESULT: capital detection P {pc(cd['after']['precision'])}/R {pc(cd['after']['recall'])}; marks at capitals R {pc(cm['before']['recall'])}→{pc(cm['detected']['recall'])} naming {pc(cn['before']['accuracy'])}→{pc(cn['detected']['accuracy'])}; held-out P {pc(b['precision'])}→{pc(a['precision'])} R {pc(b['recall'])}→{pc(a['recall'])}; ascender false {asc['before']}/{asc['n']}→{asc['after']}/{asc['n']}; owner notes {own['examples']['after']}/56 + {own['earlier']['after']}/59 (S4 {own['examples']['before']}/56, 46/59); regressions: "+('; '.join(regress) or 'none')+'.')
 (O/'S5_REPORT.md').write_text('\n'.join(L)+'\n');print(L[-1])
if __name__=='__main__':main()
