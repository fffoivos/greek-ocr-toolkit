from pathlib import Path
import json,hashlib,datetime,subprocess
D=Path('docs/harvest/census05'); E=D/'b_evidence'; W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'; remote=W+'/census_05_20261020/code/17b0eb1ca7fe81a7'; bundle=remote+'/'+str(D)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ver={k:json.loads((D/f'verify-{k}.json').read_text()) for k in ['regression','parity','census','readout']}
assert all(j['verdict']=='VERIFY_OK' for j in ver.values())
rb=json.loads((E/'readback.json').read_text()); assert len(rb)==178 and all(r['match'] for r in rb)
tests=json.loads((E/'test_only.json').read_text()); assert len(tests)==8 and all(t['exit_code']==0 for t in tests)
assert (E/'remote_final_scope.log').read_text().splitlines()==['NO_ATTEMPTS_OR_LOGS','167','6']
baseline=W+'/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json'
assert sha(D/'census03_summary.json')=='b187a2e7a0e218b433aa28dbc96d31f0c8f7e7e373b35027ba366b0467894fe3'
base_read=json.loads((E/'baseline-mock-readout/readout.json').read_text()); assert base_read['baseline'] and all(i['status']=='PASS' for i in base_read['invariants'].values())
s=(D/'FOLLOW_UP.md').read_text(); commands=s.split('## Coordinator smoke and full chains')[1].split('```bash\n')[1].split('```')[0].replace('mkdir -p "$RUN_ROOT/logs"','mkdir -p "$RUN_ROOT/attempts" "$RUN_ROOT/logs"').replace('DEBUG_TIME_FROM_CENSUS05_B','00:10:00')
(E/'coordinator_commands.sh').write_text('# FINAL COORDINATOR COMMANDS — NOT EXECUTED BY CENSUS05-B\n'+commands)
table='| Mode | Kind | Exit | Scheduler response |\n|---|---|---:|---|\n'
for t in tests:
 response=' '.join(l.strip() for l in (t['stdout']+t['stderr']).splitlines() if l.startswith('sbatch:'))
 table+=f"| {t['mode']} | {t['kind']} | {t['exit_code']} | {response} |\n"
head='''\n\n## B: deploy + verify

Completed 2026-10-20; no submission. HEAD `0736754c12dc6240fed2557df2a8ab68bb5f8841` descends from `a09642bd4`; the sole extra commit touches only `docs/briefs/CENSUS05_B_deploy.md`. Branch `opus/seg-census`. Pre-existing untracked `docs/harvest/seg09/` preserved. No Git mutation commands used. All B artifacts are under this directory.

'''
head+=f'Remote root: `{remote}`; bundle: `{bundle}`. New empty destinations were checked before copying. Repository-relative paths preserved. [Readback](b_evidence/readback.json): **173/173 deployed files and inputs match** (167 payload + 6 inputs), plus **5/5 standing cyrillic ledgers** hashed in place; no cyrillic copies. [Raw remote hashes](b_evidence/remote_sha256sum.txt), [deployment command receipts](b_evidence/deploy_commands.json). Remote scope check: 167 code files, 6 inputs, no attempts or logs ([receipt](b_evidence/remote_final_scope.log)).\n\n'
head+='Verifier block executed unchanged from FOLLOW_UP.md before tracked handoff edits; no allow-list, exemption, script change or credential repair. Outputs:\n\n```text\n'+''.join(f'{k}: VERIFY_OK (verify-{k}.json)\n' for k in ver)+'```\n\n'
head+='[Live partition/accounting evidence](b_evidence/remote_inspection.log): debug MaxTime **01:30:00**, DefaultTime 00:45:00, MinNodes 0, MaxNodes 4, State UP. Every job requests 1 node/1 task. Smoke uses **00:10:00** for each kind. [Measured mock smoke](b_evidence/smoke_timing.json): 200 rows / 0.844411542 s = 236.851334 rows/s; 600 s allows over 700 times that duration. Native observations are saved and corrections synthetic: this is a scheduling basis, not remote throughput qualification. The first timing invocation used incompatible system NumPy; its failure log is retained, then the prescribed sol-recut venv completed the run. Regression evidence is 2.86 s; retained native parity is 60.62 s. Coordinator must review real smoke before full.\n\n'
head+=f'Census_03 baseline **found**: `{baseline}`, 130590 bytes, SHA256 `{sha(D/"census03_summary.json")}`; copied only as [census03_summary.json](census03_summary.json). CURRENT.json identifies this completed generation and identical hash. No remote decisions downloaded. Committed readout `--baseline` parsed it against the 200-row mock: [log](b_evidence/baseline_parse.log), [readout](b_evidence/baseline-mock-readout/readout.json), 14/14 invariants PASS; mock-versus-production deltas are parser evidence only. `sacct -j 3695426`: ocr_filter_census03, normal, COMPLETED, 1 node/288 allocated CPUs, 01:49:40 elapsed / 04:00:00 limit; principal Python step 01:49:19, 256 CPUs.\n\n'
head+='All following responses are **test-only predictions**, not submitted jobs. Exact commands, environment and stdout/stderr: [test_only.json](b_evidence/test_only.json). Smoke debug/00:10:00; full retains each script’s normal partition and times regression/parity 00:05:00, census 04:00:00, readout 00:30:00. Both modes bind the deployed split; full binds the found baseline. No dependencies were fabricated for dry checks.\n\n'+table
head+='\nFinal literal coordinator commands below are **unexecuted**, for owner-required Astra review and coordinator approval before submission. Create attempts/logs only at that stage. Run the smoke chain, stop for review, then separately run the full block after its gates.\n\n```bash\n'+commands+'```\n\n'
head+='The readout submission in each chain points to the deployed `jobs/readout.sbatch`, which invokes the deployed `readout/census_readout.py`, derives version 0.3.2 from deployed package code, and writes a sibling `<attempt>.readout/`. Exact expanded full readout command inside that allocation (unexecuted):\n\n```bash\n'
head+=f'''PYTHONPATH="{bundle}/package/projects/greek-ocr-toolkit-pipe032" \\
  "{W}/venv_l1/bin/python" -B "{bundle}/readout/census_readout.py" \\
  --expect-pipeline-version 0.3.2 \\
  --run "{W}/census_05_20261020/attempts/full-split-001" \\
  --out "{W}/census_05_20261020/attempts/full-split-001.readout" \\
  --baseline "{baseline}" --expect-rows 592466
```

[B receipt](B_RECEIPT.json) and [Astra review inputs](REVIEW_INPUTS.md). No real smoke, production census, or remote readout was run by B.
'''
with (D/'HANDOFF_CENSUS05.md').open('a') as f:f.write(head)
# Review one-page index: full identities, no implied deployment of local evidence.
paths=['DEPLOY_SHA256SUMS','PROJECTS_SHA256','package_id.json']+[f'verify-{k}.json' for k in ver]+['b_evidence/readback.json','regression_tests.log','readout_version_tests.log','parity/source_receipt.json','parity/replay-01.jsonl.gz','parity/replay-02.jsonl.gz','native_parity_audit.json','parity_policy_audit.json','b_evidence/test_only.json','census05_config.json','config_diff.json','config_diff.patch','corrections/report.json','INPUTS.json','input_audit.json','readout/census_readout.py','jobs/readout.sbatch','readout/readout.sbatch','mocks/smoke-mode-i/readout.json','mocks/smoke-mode-ii/readout.json','mocks/full-mode-ii/readout.json','b_evidence/baseline-mock-readout/readout.json']
deployed={r['local_path']:r['remote_path'] for r in rb if r['kind']=='code'}
review=f'''# CENSUS05 Astra review inputs

Bundle root `{D}` → `{bundle}`; package **17b0eb1ca7fe81a7**, 167 files. Root identity is SHA256 of DEPLOY_SHA256SUMS, `{sha(D/'DEPLOY_SHA256SUMS')}`; PROJECTS_SHA256 binds 154 source paths. “Local only” means evidence was not copied to Clariden. All paths below are repository-relative; hashes cover file bytes.

| Repository path | Remote path where deployed | SHA256 |
|---|---|---|
'''
for p in paths:
 full=str(D/p); review+=f'| `{full}` | `{deployed.get(full,"local only")}` | `{sha(full)}` |\n'
review+='''
Cited package test logs report 360 passed / 0 failed / 9 skipped plus 20 readout tests passed (380 distinct passes). Cited parity results record 150/150 and 888/888 exact verdict and reason; no new native parity run is claimed. Cited mocks contain 200 rows and 14/14 invariants PASS. `test_only.json` contains the four smoke and four full responses, exit 0; these are scheduler dry checks. Config diff/report identify `routes_out_of_scope: ["polytonic"]`, four unbound polytonic ledgers, five regenerated N1 ledgers with empty changed-record/status-moving lists, and split2 binding in INPUTS/input audit and submit environment. Deployed input identities and five standing cyrillic identities are in readback.json.

Code identity: check bundle/manifest, PROJECTS_SHA256, four VERIFY_OK receipts and per-file remote readback.
Config: check the census_04 diff, route scope, component roots and unbound polytonic ledgers.
Corrections: check five regenerated N1 ledgers, moving-status lists and five standing cyrillic hashes.
Split: check split2 SHA256, 320479 assignments and explicit full submit-time binding.
Job settings: check dry responses, debug 00:10:00, normal per-kind limits, afterok chain and sibling readout paths before submission.
'''
(D/'REVIEW_INPUTS.md').write_text(review)
receipt=dict(task='CENSUS05-B',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),head='0736754c12dc6240fed2557df2a8ab68bb5f8841',package_id='17b0eb1ca7fe81a7',remote_root=remote,deployed_files=167,new_inputs=6,readback_deployed_ok=173,readback_deployed_total=173,standing_cyrillic_ok=5,verify={k:j['verdict'] for k,j in ver.items()},test_only={m:[t['kind'] for t in tests if t['mode']==m and t['exit_code']==0] for m in ['smoke','full']},debug_max_time='01:30:00',smoke_time='00:10:00',baseline=dict(remote_path=baseline,bytes=130590,sha256=sha(D/'census03_summary.json'),parse='PASS 14/14'),job_submitted=False,coordinator_commands_executed=False,remote_attempts_or_logs_created=False,artifacts={})
for p in paths+['HANDOFF_CENSUS05.md','REVIEW_INPUTS.md','b_evidence/remote_inspection.log','b_evidence/deploy_commands.json','b_evidence/smoke_timing.json','b_evidence/coordinator_commands.sh','b_evidence/remote_final_scope.log','census03_summary.json']:
 receipt['artifacts'][str(D/p)]=sha(D/p)
(D/'B_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('HANDOFF + REVIEW_INPUTS + B_RECEIPT written')
