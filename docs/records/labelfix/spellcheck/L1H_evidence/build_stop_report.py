"""Report a stopped login-node run without presenting pilot counts as a census."""
import ast, csv, hashlib, json, pathlib
E=pathlib.Path(__file__).resolve().parent
P=json.loads((E/'schema_probe.json').read_text()); stop=json.loads((E/'aggregation.json').read_text())
assert not stop['complete']
W=['round1','round2','parliament','vouli','mixed','openarchives'];M=['presence','full','ensemble_ab']
f=lambda n:f'{n:,}'
pct=lambda n,d:f'{100*n/d:.1f}%'
def table(heads,rows):return '\n'.join(['| '+' | '.join(heads)+' |','| '+' | '.join(['---']*len(heads))+' |',*['| '+' | '.join(map(str,row))+' |' for row in rows]])
manifest={m:P['manifests'][m]['data'] for m in M}
N=sum(manifest['ensemble_ab']['counts_by_status'].values())
rows=[]
for m in M:
 r=manifest[m]
 for w in [*W,'ALL']:
  s=r['coverage_per_wave'][w] if w!='ALL' else r['counts_by_status']
  total=s.get('total',sum(s.get(k,0) for k in ('corrected','unchanged','hold','out_of_scope')))
  kept=s['corrected']+s['unchanged']
  rows.append([m.upper(),w,total,s['hold'],kept,s['corrected'],s['unchanged'],s['out_of_scope']])
with (E/'status_by_wave.csv').open('w',newline='') as out:
 wr=csv.writer(out);wr.writerow(['mode','wave','lines','held','kept','corrected','unchanged','out_of_scope']);wr.writerows(rows)
(E/'release_manifests.json').write_text(json.dumps(P['manifests'],ensure_ascii=False,indent=2)+'\n')
ids=sorted({s['line_id'] for s in P['schema_samples'].values()})
(E/'sample_ids.txt').write_text(''.join(x+'\n' for x in ids))
with (E/'samples.jsonl').open('w') as out:
 for m,s in P['schema_samples'].items():out.write(json.dumps({'mode':m,'sample_type':'schema_only_first_overlay_line','projection':s},ensure_ascii=False,separators=(',',':'))+'\n')
# Explicit nulls are not zero counts.
with (E/'pending_tables.csv').open('w',newline='') as out:
 wr=csv.writer(out);wr.writerow(['mode','wave','held_lines_manifest','slot_counts_per_detail','sole_reason_lines','top_10_reason_sets','status'])
 for r in rows:
  if r[1]!='ALL':wr.writerow([r[0],r[1],r[3],None,None,None,'NOT_COMPUTED_LOGIN_BUDGET_STOP'])
for source in P['source_readback']:
 assert hashlib.sha256(source['text'].encode()).hexdigest()==source['sha256']
 for m in M:
  matching=[v for k,v in manifest[m]['policy_binding']['sources'].items() if source['path'].endswith(k)]
  assert matching==[source['sha256']]
for name in ('aggregate.py','aggregate_login_attempt.py','build_report.py','build_stop_report.py'):
 ast.parse((E/name).read_text(),filename=name)
validation={'complete':False,'stop':stop,'counts_source':'remote release manifests read by schema_probe.py (probe.py)',
 'census_counts_available':False,'sample_record_projections':len(P['schema_samples']),'sample_unique_ids':len(ids),'images_transferred':0,
 'network_hosts':'Clariden via existing ela ProxyJump only','remote_aggregation_exit_code':124,
 'no_job_submission':True,'no_gate_or_detector_changes':True,'no_git_writes':True,
 'overlay_sha256_independently_verified':False,'source_sha256_independently_verified_in_returned_evidence':False,
 'gate_source_readback_sha256_matches_release_policy':True,
 'script_sha256':{name:hashlib.sha256((E/name).read_bytes()).hexdigest() for name in ('probe.py','aggregate_login_attempt.py','aggregate.py','build_report.py')}}
(E/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
coverage=[]
for w in [*W,'ALL']:
 rr={r[0]:r for r in rows if r[1]==w}
 coverage.append([w,f(rr['ENSEMBLE_AB'][2]),*[f(rr[m.upper()][3])+' / '+f(rr[m.upper()][4]) for m in M],pct(rr['ENSEMBLE_AB'][3],rr['ENSEMBLE_AB'][2])])
statusrows=[[r[0],r[1],f(r[3]),'Not computed','Not computed'] for r in rows if r[1]!='ALL']
setrows=[[r[0],r[1],'Not computed — stopped before full census output'] for r in rows if r[1]!='ALL']
lines=['# L1H — Complete-gate HOLD attribution (stopped; reason tables incomplete)','',
 '**Status: incomplete, stopped at the login-node budget.** The requested exact reason/sole-reason and top-ten reason-set tables were not produced. No gate or detector was changed, and no job was submitted.','',
 'The live release manifests confirm **ENSEMBLE_AB holds 112,605 / 124,669 lines (90.3%) and keeps 12,064 (9.7%)**. PRESENCE holds 118,364 (94.9%) and keeps 6,305; FULL holds 118,726 (95.2%) and keeps 5,943. These are manifest counts, not a successful independent recount of all three overlays.','',
 '## Stop condition','',
 f'The pilot timed JSON decoding on 1,024 rows per mode and projected {sum(v["projected_full_seconds"] for v in P["pilot"].values()):.1f} seconds for all three overlays. The one-process census added hashing, source joins, deduplication and reason-set counters. Its last forecast was **{stop["forecast_s"]:.1f} seconds (4.50 minutes)** at FULL row **{stop["rows"]:,}**, above the conservative **240-second limit chosen for this run**. It exited with code 124 at that forecast; the 240-second alarm was not reached. The user specified a few minutes of one core, not an exact numerical cap.','',
 'The log shows AB through 120,000 rows, then PRESENCE through 120,000 rows, then the FULL forecast stop. The script only emits a completed census after all modes and invariants pass, so partial in-memory AB/PRESENCE counters were not returned. There are no usable full-population reason counts in the returned evidence. No second aggregation pass was attempted after the stop.','',
 '## Verified release coverage by wave','',
 table(['Wave','Lines','PRESENCE held / kept','FULL held / kept','AB held / kept','AB held %'],coverage),'',
 '## Table 1 — Requested slot and sole-reason line counts','',
 '**Unavailable.** The table below records the missing results explicitly; “Not computed” is not zero. Once the coordinator runs the prepared script in a small allocation, the report formatter will produce one exact-detail table per mode with six wave columns, each containing `slots / sole-reason lines`, and separate ALL totals.','',
 table(['Mode','Wave','Held lines (manifest)','Slots per exact reason','Lines held for that exact reason alone'],statusrows),'',
 '## Table 2 — Requested top-ten line reason sets','',
 '**Unavailable.** No population reason-set rankings can be inferred from the schema pilot or release-status totals.','',
 table(['Mode','Wave','Top 10 exact reason sets and line counts'],setrows),'',
 '## Pilot and schema evidence','',
 'The overlay stores a broad `hold_slots[].reason` and a more specific `hold_slots[].detail`. The first sampled line records `detector_clipped_top` and a mode-specific disagreement detail, while its broad reason calls clipping `localisation_unknown`. The analysis must use detailed strings for the main attribution, retaining the broad mapping as a separate view.','',
 table(['Mode','Pilot rows','Decode s','Projected complete decode s','Pilot broad reason-entry counts'],[[m.upper(),v['rows'],f'{v["elapsed_s"]:.3f}',f'{v["projected_full_seconds"]:.1f}','; '.join(k+'='+f(n) for k,n in v['reason_counts'].items())] for m,v in P['pilot'].items()]),'',
 'These pilot counts describe only the first 1,024 rows per file and are neither joined to wave nor a random sample. They do not establish the top reasons or sole-reason line counts for the complete gate.','',
 '## Sample IDs','',
 'Schema-only sample ID:','',*['- `'+i+'`' for i in ids],'',
 'The pilot returned three mode projections for this one unique line, including gate-decision evidence and the first three HOLD entries. The projections are in [samples.jsonl](L1H_evidence/samples.jsonl), with the complete ID list in [sample_ids.txt](L1H_evidence/sample_ids.txt). **No crops were transferred (0 images)**. This line is a schema witness, not an adjudicated or representative HOLD sample. The transfer stayed below 200 sampled records and 200 images; no full overlays or source manifest were copied to the Mac.','',
 '## Prepared method and checks','',
 'The prepared aggregator joins overlay `line_id` to source `id`/`wave` on Clariden, with one process and no scientific-library threads. It counts distinct `(line_id, start, letter, detail)` slot/reason keys. A line is sole-reason only when the union of all its detailed HOLD reasons is exactly that one reason. Exact sorted reason sets partition held lines. Top tens rank by descending count, then lexical set order.','',
 'The intended completed run checks compressed overlay SHA-256 against every manifest, source SHA-256, unique identical mode populations, every source/wave join, every wave/status total, HOLD/status consistency, and partition/deduplication invariants. **Those full-run checks cannot be claimed as completed from the returned stop receipt.** The pilot did read the current manifests and the gate/recomposition source snapshots; both source hashes match the policy binding recorded in those manifests.','',
 'The completed-run formatter preserves every exact reason string, including edit-guard offsets, and exports supplementary broad-reason and family views (`K1:*`, `edit_guard:*`, reader uncertainty prefixes). It does not infer neighbour ink or gate correctness. Line-level guard failures can be repeated across slots, so slot counts are not independent physical-defect counts.','',
 'Part (2) remains dropped: no masking experiment, neighbour-ink classification, detector-blob scan, detector rerun, quality assessment or gate recommendation was performed. The requested `DIRECTION_DECISION_20261017.md` reference was absent from this checkout and the two explicit Clariden documentation paths checked; no unrelated verification worktree was accessed.','',
 '## Data identity','',
 f'- Release root: `{P["release"]}`.',
 '- Mode overlays: `overlay_presence.jsonl.gz`, `overlay_full.jsonl.gz`, `overlay_ensemble_ab.jsonl.gz`; pre-SF4 job 3679545.',
 '- Wave join source intended by the prepared script: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/import_real_v2_train.jsonl` (same source identity as the locally symlinked manifest).',
 '- Source SHA-256 **recorded in the manifests**: `'+manifest['ensemble_ab']['source_sha256']+'`.',
 '- Release policy SHA-256: `'+manifest['ensemble_ab']['policy_binding']['sha256']+'`.','',
 table(['Mode','Overlay SHA-256 recorded in live manifest'],[[m.upper(),'`'+manifest[m]['overlay_sha256']+'`'] for m in M]),'',
 '## Coordinator handoff','',
 'The next step requires the coordinator’s small allocation under the user’s stop-and-report rule. [aggregate.py](L1H_evidence/aggregate.py) is ready to run there: it retains the 240-second forecast/alarm on a login node and removes that login limit only when `SLURM_JOB_ID` is present. It has not been launched in an allocation. Its output should replace `L1H_evidence/aggregation.json`; then run `build_report.py` locally to produce the requested full tables and compact CSVs. No submission command was executed.','',
 'The exact script used for the stopped attempt is preserved separately as [aggregate_login_attempt.py](L1H_evidence/aggregate_login_attempt.py). Local work was limited to report/evidence files; `.git`, gates, detectors and the other verification worktrees were not modified.','',
 '## Evidence index','',
 '- [Stop receipt](L1H_evidence/aggregation.json) and [execution log](L1H_evidence/aggregation_ssh.log).',
 '- [Live manifest projections](L1H_evidence/release_manifests.json), [coverage CSV](L1H_evidence/status_by_wave.csv), and [explicit pending-table CSV](L1H_evidence/pending_tables.csv).',
 '- [Schema/timing pilot](L1H_evidence/schema_probe.json), [pilot script](L1H_evidence/probe.py), and [pilot SSH log](L1H_evidence/probe_ssh.log).',
 '- SHA-bound [gate source readback](L1H_evidence/release_gate_source_readback.py) and [recomposition source readback](L1H_evidence/l1r_recompose_source_readback.py), evidence only.',
 '- [Validation and scope receipt](L1H_evidence/validation.json), [prepared aggregator](L1H_evidence/aggregate.py), and [completed-run report formatter](L1H_evidence/build_report.py).','',
 'L1H RESULT: AB held 90.3%: top reasons NOT COMPUTED (login-budget stop); per-wave sole-reason lines NOT COMPUTED (all six waves); PRESENCE/FULL held 94.9% / 95.2%, kept 6,305 / 5,943; reason census INCOMPLETE.']
(E.parent/'L1H_REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'report':str(E.parent/'L1H_REPORT.md'),'complete':False,'status_rows':len(rows),'sample_ids':ids,'images':0}))
