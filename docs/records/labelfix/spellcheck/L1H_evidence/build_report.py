"""Format already-aggregated evidence locally; never reads a bulk data source."""
import collections, csv, hashlib, json, pathlib
E=pathlib.Path(__file__).resolve().parent
A=json.loads((E/'aggregation.json').read_text()); assert A['complete']
W=list(A['wave_order']); M=['presence','full','ensemble_ab']; AB=A['modes']['ensemble_ab']['waves']['ALL']
fmt=lambda n:f'{n:,}'
pct=lambda n,d:f'{100*n/d:.1f}%'
def table(headers,rows):
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',*['| '+' | '.join(map(str,r))+' |' for r in rows]])
def writecsv(name,heads,rows):
 with (E/name).open('w',newline='') as f:
  w=csv.writer(f);w.writerow(heads);w.writerows(rows)
def ordered(c):return sorted(c,key=lambda k:(-c[k],k))
def rc(mode,w,p='raw'):return A['modes'][mode]['waves'][w]
rows=[]
for m in M:
 for w in [*W,'ALL']:
  c=rc(m,w); s=c['status']; total=sum(s.values())
  rows.append([m.upper(),w,total,s.get('hold',0),s.get('corrected',0),s.get('unchanged',0),s.get('out_of_scope',0),c['unique_held_slots'],c['reason_entries'],c['duplicate_slot_reason_entries']])
writecsv('status_by_wave.csv',['mode','wave','lines','held','corrected','unchanged','out_of_scope','unique_held_slot_keys','hold_reason_entries','duplicate_raw_slot_reason_entries'],rows)
for p in ['raw','broad','family']:
 rows=[];sets=[]
 for m in M:
  for w in [*W,'ALL']:
   c=rc(m,w)
   for r in ordered(c[p+'_slots']): rows.append([m.upper(),w,r,c[p+'_slots'][r],c[p+'_lines'].get(r,0),c[p+'_sole'].get(r,0)])
   for rank,s in enumerate(c[p+'_sets'],1): sets.append([m.upper(),w,rank,json.dumps(s['reasons'],ensure_ascii=False),s['lines'],rank<=10])
 writecsv(p+'_reasons_by_wave.csv',['mode','wave','reason','unique_slot_reason_count','lines_with_reason','sole_reason_lines'],rows)
 writecsv(p+'_reason_sets.csv',['mode','wave','rank','reason_set_json','lines','top_10'],sets)
(E/'sample_ids.txt').write_text(''.join(k+'\n' for k in A['samples']))
with (E/'samples.jsonl').open('w') as f:
 for v in A['samples'].values():f.write(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
(E/'reason_dictionary.json').write_text(json.dumps(A['raw_to_broad'],ensure_ascii=False,indent=2)+'\n')
# Detach samples from the aggregate copy used for convenient inspection.
summary={'complete':A['complete'],'created_utc':A['created_utc'],'host':A['host'],'elapsed_s':A['elapsed_s'],'cpu_s':A['cpu_s'],
 'maxrss_kib':A['maxrss_kib'],'sample_line_count':A['sample_line_count'],'invariants':A['invariants'],
 'source':A['source'],'overlays':{m:{k:v for k,v in A['modes'][m].items() if k not in ('waves','manifest')} for m in M}}
(E/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
N=sum(AB['status'].values());H=AB['status']['hold']; kept=N-H
allocated=bool(A.get('slurm_job_id'))
execution_context=('inside coordinator allocation '+str(A['slurm_job_id'])) if allocated else 'on a login node with a 240-second alarm and forecast stop'
crop_receipt=E/'crop_receipt.json'
crop_note=('Sample crop paths and hashes are recorded in `crop_receipt.json`.' if crop_receipt.exists() else 'No sample images were transferred by this aggregator; only crop references are included.')
lines=['# L1H — Recorded complete-gate HOLD reasons by wave','',
 f'Analysis of the **pre-SF4 L1E job 3679545** release: **ENSEMBLE_AB holds {fmt(H)} / {fmt(N)} lines ({pct(H,N)}) and keeps {fmt(kept)} ({pct(kept,N)})**. This is the fixed release identified below; no gate or detector was rerun or changed.','',
 '## Main findings','']
for r in ordered(AB['raw_lines'])[:6]:
 lines.append(f'- `{r}`: {fmt(AB["raw_slots"][r])} slot/reason occurrences, {fmt(AB["raw_lines"][r])} held lines containing it, and **{fmt(AB["raw_sole"].get(r,0))} lines held for this exact reason alone**.')
sole=sum(AB['raw_sole'].values());multi=H-sole
lines+=['',f'Exact singleton reason sets account for {fmt(sole)} held AB lines ({pct(sole,H)} of held lines); {fmt(multi)} held lines have two or more distinct detailed reasons. Counts of lines containing different reasons overlap. A sole-reason count describes this recorded release; it does not establish that changing a gate is safe or predict a recomputed release.','',
 '## Release coverage','',
 table(['Wave','Lines','PRESENCE held / kept','FULL held / kept','AB held / kept','AB held %'],[
  [w,fmt(sum(rc('ensemble_ab',w)['status'].values())),*[' / '.join(fmt(z) for z in (rc(m,w)['status'].get('hold',0),sum(rc(m,w)['status'].get(s,0) for s in ('corrected','unchanged')))) for m in M],pct(rc('ensemble_ab',w)['status'].get('hold',0),sum(rc('ensemble_ab',w)['status'].values()))] for w in [*W,'ALL']]),'',
 '## Table 1 — Slot counts and lines held for that reason alone','',
 'Each wave cell is **slots / sole-reason lines**. “Slots” counts distinct `(line_id, start, letter, detail)` keys; a slot may contribute to several reasons. “Sole” means the union of all recorded `hold_slots[].detail` values across the whole held line is exactly that one value. All detailed reason strings are retained, including edit-guard offsets. `ALL` covers the selected 124,669-line release, not all source-manifest lines.','']
for m in M:
 c=rc(m,'ALL'); reasons=ordered(c['raw_slots'])
 lines += [f'### {m.upper()}','',table(['Recorded `detail`','ALL slots','ALL sole',*[w+' slots / sole' for w in W]],[
  ['`'+r+'`',fmt(c['raw_slots'][r]),fmt(c['raw_sole'].get(r,0)),*[f'{fmt(rc(m,w)["raw_slots"].get(r,0))} / {fmt(rc(m,w)["raw_sole"].get(r,0))}' for w in W]] for r in reasons]),'']
lines+=['### AB reason-family view','',
 'This supplementary view unions `K1:*`, `edit_guard:*`, and each reader’s uncertainty prefix before counting. It is separate from the exact-reason table: a line with two different edit-guard details can be sole-family while having no sole exact reason. Family slots are deduplicated after union.','',
 table(['Reason or family','ALL slots','ALL sole-family',*[w+' slots / sole' for w in W]],[
  ['`'+r+'`',fmt(AB['family_slots'][r]),fmt(AB['family_sole'].get(r,0)),*[f'{fmt(rc("ensemble_ab",w)["family_slots"].get(r,0))} / {fmt(rc("ensemble_ab",w)["family_sole"].get(r,0))}' for w in W]] for r in ordered(AB['family_slots'])]),'',
 '## Table 2 — Top 10 line reason sets','',
 'Each row is the exact, sorted set of distinct detailed reasons on a held line, irrespective of how many slots repeat them. Sets partition held lines. Top-ten ranking is by line count, then lexical reason-set order to break ties. Remaining sets are combined only in the explicitly labelled remainder row. Complete distributions are in `raw_reason_sets.csv` and `aggregation.json`.','']
for m in M:
 lines += [f'### {m.upper()}','']
 for w in [*W,'ALL']:
  c=rc(m,w); ss=c['raw_sets']; h=c['status'].get('hold',0)
  rr=[[i,' + '.join('`'+r+'`' for r in s['reasons']),fmt(s['lines']),pct(s['lines'],h)] for i,s in enumerate(ss[:10],1)]
  tail=sum(s['lines'] for s in ss[10:])
  if tail:rr.append(['—',f'All other {len(ss)-10} reason sets',fmt(tail),pct(tail,h)])
  lines += [f'**{w} — {fmt(h)} held lines; {len(ss)} distinct sets**','',table(['Rank','Exact reason set','Lines','% held'],rr),'']
lines+=['## Samples','',
 f'{A["sample_line_count"]} unique illustrative line IDs were selected during the remote pass. Selection is deterministic first occurrence in the frozen overlay order for mode/wave HOLD examples and AB reason targets or singleton sets, capped at 60 unique lines. This is an audit sample, not a random quality sample. The schema pilot also returned one line ID (shared across its three modes). All transferred record projections remain below the 200-record limit.','',
 'The sample projections preserve every HOLD entry for the modes seen after selection. An ID selected in a later mode can lack an earlier mode projection. `sample_ids.txt` is the complete ID list; `samples.jsonl` includes selection tags, source crop references, exact reasons and original-label hashes. '+crop_note,'',
 table(['Wave','Sample IDs'],[[w,'<br>'.join('`'+k+'`' for k,s in A['samples'].items() if s['wave']==w)] for w in W]),'',
 '## Method, identity and limits','',
 f'- Executed one standard-library Python process on `{A["host"]}`. The complete aggregation took **{A["elapsed_s"]:.2f} s wall / {A["cpu_s"]:.2f} s CPU**, {execution_context}. The aggregation script submits no jobs and performs no inference, detector work, remote data writes or certificate refresh.',
 f'- Source join: `{A["source"]["path"]}`; SHA-256 `{A["source"]["sha256"]}`; {fmt(A["source"]["rows"])} unique source IDs. All overlay IDs joined to one of the six requested waves; the selected population is identical across modes. No full manifest or overlay was copied to the Mac.',
 f'- Overlay root: `{A["release"]}`. Compressed overlay hashes were computed during streaming and exactly matched the release manifests. Status counts and every wave/status count matched those manifests. File size, modification time and inode remained stable during each read.',
 '- HOLD iff `hold_slots` is nonempty was checked on every row. Exact reason-set distributions sum to held lines, singleton sets equal sole-reason counts, and slot/reason totals reconcile with HOLD entries after duplicate removal.',
 '- Primary attribution uses the recorded `detail`, not an inferred label from detector flags. The overlay’s broad `reason` collapses detector clipping, localisation and other conditions into `localisation_unknown`; `reason_dictionary.json` preserves the mapping. `broad_reasons_by_wave.csv` and `broad_reason_sets.csv` provide that alternate recorded view.',
 '- Slot counts are evidence-key counts, not independently adjudicated physical glyphs. Line-level edit-guard failures can be copied to many slot entries; their slot counts therefore do not measure independent defects. Sole-reason counts use whole-line unions and are not inflated by that repetition.',
 '- The SHA-bound gate source readback shows relevant-zone clipped-edge checks and R1/peer coverage checks. Raw clipping flags on irrelevant slots are not automatically HOLD reasons. AB compares A/B mark sets; PRESENCE compares detector/A mark families; FULL compares detector/A exact sets. These mode semantics explain reason naming, not printed-text correctness.',
 '- This is a census of recorded decisions, not an assessment of whether edge ink belongs to the target or a neighbour, whether a crop is actually incomplete, or whether held lines are wrong. Part (2) was dropped: no neighbour-ink classification, masking experiment, detector-blob scan, or downstream quality claim is included.',
 '- The requested `DIRECTION_DECISION_20261017.md` reference was absent from this checkout and the two explicit Clariden release worktrees checked. The report follows the requested slot/sole-line and top-ten reason-set semantics; the unrelated verification worktrees were not read.',
 '- Local work consisted of evidence scripts, compact aggregate/sample output, crop copies and report formatting. No `.git` writes or operational source edits were made. The gate readback files are evidence snapshots only.','',
 table(['Mode','Compressed overlay SHA-256'],[[m.upper(),'`'+A['modes'][m]['overlay_sha256']+'`'] for m in M]),'',
 'Policy binding: `'+A['modes']['ensemble_ab']['manifest']['policy_binding']['sha256']+'`. The full aggregate and manifest projections are in [aggregation.json](L1H_evidence/aggregation.json); execution and invariant receipt in [validation.json](L1H_evidence/validation.json).','',
 '## Evidence index','',
 '- [Exact reason counts by wave](L1H_evidence/raw_reasons_by_wave.csv), including lines with each reason and sole-reason lines.',
 '- [Exact reason-set distribution](L1H_evidence/raw_reason_sets.csv), all sets with rank and a top-ten flag.',
 '- [Family counts](L1H_evidence/family_reasons_by_wave.csv), [family sets](L1H_evidence/family_reason_sets.csv), and [status coverage](L1H_evidence/status_by_wave.csv).',
 '- [Sample IDs](L1H_evidence/sample_ids.txt), [sample record projections](L1H_evidence/samples.jsonl). Crop paths are source references unless a separate crop receipt is present.',
 '- [Read-only aggregation script](L1H_evidence/aggregate.py), [execution log](L1H_evidence/aggregation_ssh.log), [pilot](L1H_evidence/schema_probe.json), and SHA-bound [gate source readback](L1H_evidence/release_gate_source_readback.py).','']
top='; '.join(f'{r} {fmt(AB["raw_slots"][r])} slots/{fmt(AB["raw_sole"].get(r,0))} sole' for r in ordered(AB['raw_slots'])[:3])
solewave='; '.join(w+' '+(', '.join(r+'='+fmt(rc('ensemble_ab',w)['raw_sole'][r]) for r in ordered(rc('ensemble_ab',w)['raw_sole'])) or 'none') for w in W)
pf='; '.join(m.upper()+' '+fmt(rc(m,'ALL')['status']['hold'])+'/'+fmt(N)+' held ('+pct(rc(m,'ALL')['status']['hold'],N)+'), '+fmt(N-rc(m,'ALL')['status']['hold'])+' kept' for m in ('presence','full'))
lines.append('L1H RESULT: AB held 90.3%: top reasons '+top+'; per-wave sole-reason lines '+solewave+'; PRESENCE/FULL '+pf+'.')
(E.parent/'L1H_REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'report':str(E.parent/'L1H_REPORT.md'),'raw_reason_count':len(A['raw_to_broad']),'report_lines':len(lines),'samples':A['sample_line_count'],'ab_sole':sole,'ab_multi':multi},ensure_ascii=False))
