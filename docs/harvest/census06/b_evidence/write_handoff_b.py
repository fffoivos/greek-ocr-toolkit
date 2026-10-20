"""Assemble handoff only from completed B receipts; seal exact lead commit allowlist."""
from pathlib import Path
import json,hashlib,shlex
R=Path.cwd();D=R/'docs/harvest/census06';E=D/'b_evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads((E/'deployment_summary.json').read_text());commands=json.loads((E/'verification_commands.json').read_text());cleanup=json.loads((E/'cleanup_receipt.json').read_text())
assert len([r for r in commands if r['label'].startswith('test-only-') and r['exit_code']==0])==8
assert (E/'verifier_identity.json').exists()
text='''

## B: committed deploy, readback and scheduler test-only (2026-10-20)

Deployed committed package `de597753a70a5d6d` from the untouched clean detached worktree `~/Projects/greek-ocr-toolkit-census06-verify`, HEAD `cf1db4dd48690544f4a88c208a082a0af4e5a4f7`, to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/`. The destination was empty/absent; each input destination was absent. The guarded transfer refused existing inputs and used no overwrite. `restore_inputs.py` restored or verified exact archive-derived numerics bytes without overwriting. No write occurred under census05. A's “not deployed” statements above describe A's historical endpoint.

Remote readback: **180/180 payload files, 6/6 inputs, 5/5 standing cyrillic ledgers**. Tables: `b_evidence/payload_readback.sha256`, `inputs_readback.sha256`, `cyrillic_readback.sha256`; command records: `deployment_commands.json`; summary: `deployment_summary.json`. Standing cyrillic ledgers were rehashed in place, read-only, under `filter_pipeline_20261018/prepared/87407ec7430a375f/`.

Input destinations (prefix `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/`):

| Destination basename | Bytes | SHA256 |
| --- | ---: | --- |
'''
for r in summary['inputs']:text+=f"| `{Path(r['remote_path']).name}` | {r['bytes']} | `{r['sha256']}` |\n"
text+='''
The unchanged external verifier printed **VERIFY_OK ×4**, using the clean lead commit and the census05-D argument pattern adapted to census06. Receipts/logs were written directly into this repo's new `b_evidence/`, outside the verifier's source worktree. The source worktree stayed clean. **No `--allow-untracked` exemptions were used.** The unchanged verifier itself calls only `sbatch --test-only`; account `a0140`, normal partition and packaged times came from the hash-verified sbatch directives. `verifier_identity.json` seals the external verifier bytes.

| Kind | Receipt | SHA256 |
| --- | --- | --- |
'''
for kind in ['regression','parity','census','readout']:
 p=E/('verify-'+kind+'.json');assert json.loads(p.read_text())['verdict']=='VERIFY_OK';text+=f'| {kind} | `b_evidence/{p.name}` | `{sha(p)}` |\n'
text+='''
Additional scheduler tests passed **smoke 4/4 and full 4/4**. Every explicit test command used `--account=a0140`; smoke used debug/00:30:00, full used normal with regression/parity 00:05:00, census 04:00:00, readout 00:30:00. Debug live limits: MaxTime 01:30:00, MaxNodes 4; 00:30:00 fits. These independent test-only checks validate each chain member; no fictitious dependency IDs were supplied. The packaged chain's three afterok links were inspected. Scheduler “Job … to start” responses are test-only predictions, not submitted jobs.

Exact test-only command lines executed through `ssh clariden` (all responses retained in `b_evidence/test-only-*.log` and `verification_commands.json`):

```bash
'''
for r in commands:
 if r['label'].startswith('test-only-'):text+=r['argv'][-1]+'\n'
text+='''```

SF7 stays **PENDING for all five parents**. `bind-pending.log` records `bind_sf7.py --check-only --work …` with no files: argparse refuses the missing required PATH/SHA bindings before creating anything. There is no separate `--pending` CLI option. `submit-pending.log` records the deployed `submit_chain.sh` refusal with `sf7-binding PENDING`; its guard runs before mkdir or any sbatch. `binding-state.log` confirms all five pending parents. No attempt, binding work directory, reader call, allocation or paid workload was started.

Coordinator block, **review only; no commands below were executed in B**. This supersedes the pre-binding coordinator example above. Supply the actual five full files and shas; do the large binding/coverage scan in the coordinator's CPU allocation. The existing `bind_sf7.sbatch` expands the supplied JSON into the exact per-parent `bind_sf7.py <file> <sha>` invocation shown below, then the binder rebuilds and redeploys a new code id.

```bash
'''+(E/'coordinator_commands.sh').read_text()+'''```

**After SF7 changes the package id, re-run** the bound-package lead review/commit and clean-source check, payload readback against its new manifests, input readback including the five SF7 files and existing six inputs, standing cyrillic checks, all four unchanged verifier calls against that real commit/new code root, and all eight smoke/full scheduler test-only checks. Check binding_state --submit and run the real SF7 head test. Then run the actual smoke chain, review outcomes/timing, separately authorize the full afterok chain, sibling readout at `--expect-pipeline-version 0.3.3`, and dependent flip_report. B's pre-binding verifier and scheduler receipts cannot qualify the new package. The unchanged six inputs need rehashing, not overwriting or copying again.

Cleanup (only the coordinator-authorized pytest basetemps; `b_evidence/cleanup_receipt.json`):

| Deleted directory | Allocated KiB | Regular-file bytes |
| --- | ---: | ---: |
'''
for r in cleanup['deleted']:text+=f"| `{Path(r['path']).name}/` | {r['allocated_KiB']} | {r['regular_file_bytes']} |\n"
text+=f"\nTotal deleted: **{cleanup['total_allocated_KiB']:,} KiB** allocated ({cleanup['total_regular_file_bytes']:,} regular-file bytes). No new pytest basetemp was created in B. Logs/XML, baseline, mock_batch, corrections, archives and all other data were preserved. No Git staging/commit or jobs submitted.\n\nLead commit handoff: `COMMIT_LIST_B.md`, exact paths `B_COMMIT_PATHS.txt`, byte seal `B_COMMIT_SHA256SUMS`; run `b_evidence/guard_b.py` before staging under separate lead authority.\n"
p=D/'CENSUS06.md';assert '\n## B: committed deploy' not in p.read_text();p.write_text(p.read_text()+text)
(D/'COMMIT_LIST_B.md').write_text('''# Guarded CENSUS06-B commit list

The lead commits; B ran no git add or git commit. Review the new B section in CENSUS06.md and the complete b_evidence receipts, scripts and unexecuted coordinator block.

Use only the exact repository-relative paths in B_COMMIT_PATHS.txt (one literal path per line), never recursive directory staging. B_COMMIT_SHA256SUMS seals every listed file except itself. The read-only guard checks the exact allowlist/seal, unchanged committed payload bytes, the untouched clean worktree at cf1db4dd4, four VERIFY_OK receipts with zero exemptions, and deleted basetemps:

```bash
.venv/bin/python -B docs/harvest/census06/b_evidence/guard_b.py
```

The allowlist includes the modified CENSUS06.md and new B files only. No A payload, input ledger/archive, baseline/mock data, unrelated dirty file, .git path or clean verifier worktree is authorized. Preserve ignored inputs/archives separately. Before staging, review each diff; any edited B file requires deliberate seal regeneration and another guard run. No stage/commit command is executed or inferred here. Coordinator job commands remain unexecuted review material, and SF7 is PENDING.
''')
paths=['docs/harvest/census06/CENSUS06.md','docs/harvest/census06/COMMIT_LIST_B.md','docs/harvest/census06/B_COMMIT_PATHS.txt','docs/harvest/census06/B_COMMIT_SHA256SUMS']+[str(p.relative_to(R)) for p in E.iterdir() if p.is_file()]
paths=sorted(paths);(D/'B_COMMIT_PATHS.txt').write_text('\n'.join(paths)+'\n')
(D/'B_COMMIT_SHA256SUMS').write_text(''.join(sha(R/p)+'  '+p+'\n' for p in paths if not p.endswith('/B_COMMIT_SHA256SUMS')))
print('B handoff and seal written',len(paths),'paths')
