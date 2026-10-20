from pathlib import Path
import json,hashlib
D=Path('docs/harvest/census05');E=D/'c_evidence';pkg=json.loads((D/'package_id.json').read_text());pid=pkg['package_id'];remote='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/'+pid;bundle=remote+'/'+str(D)
custody='gitignored; durable copy at the data root, receipt `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archive_receipt.json`, checksums `../corrections/ARCHIVES_SHA256SUMS`, archives `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archives/`'
p=D/'HANDOFF_CENSUS05.md';s=p.read_text().replace('The **35 committed gzip chunks** in corrections/archives/ restore those exact full files, with compressed/uncompressed hash checks in archive_receipt.json.', 'The **35 gzip chunks** are '+custody+'. All 35 compressed hashes match `corrections/archive_receipt.json`; see `c_evidence/archives.json`.')
changes='''Changes since the Astra review:

- H1: `readout/census_readout.py` mirrors packaged `line_pipeline_census.py:167–171`; configured crops union observed dev/test crops, plus existing protected editions. `test_astra_config_only_crop` reproduces the one-row witness: leaks 1, exit 1; without configuration: leaks 0, exit 0.
- L1: `admitted_train_equals_eligible` mirrors packaged `line_pipeline_census.py:204–214`, using inventory train split and ADMIT decisions, exact row content hashes and unique identities. The subset invariant stays. `test_astra_missing_export` (three eligible decisions, empty export) fails with exit 1. `test_export_equality` also covers duplicates and changed row contents.
- M2: `readout/test_census_readout.py` finds its own repository root, skips absent historical fixtures with their paths in the reason, and writes all outputs and receipts to `tmp_path`. Synthetic successful exports now contain every eligible row. Tests: **28 passed in 31.23s** (0 failed, 0 skipped); packaged regression: **360 passed, 9 skipped in 3.11s** (0 failed). Logs in `c_evidence/`.
- M3: `INPUTS.json`, this handoff and `REVIEW_INPUTS.md` record durable archive custody; `c_evidence/archives.json` verifies **35/35** hashes against the original receipt and data-root checksum list.

`readout_fix.patch` targets `docs/records/harvest/census05/readout/` and supersedes `readout_version.patch`: it includes both the prior pipeline-version fix and these changes (including the prior wrapper change). No pipeline source changes. The 154 CODE_SHA-identical files and PROJECTS_SHA256 are byte-identical; DEPLOY_PATHS.txt was regenerated with identical bytes. The deployed payload changes only `readout/census_readout.py`; tests change locally but were never part of the deploy manifest. Updated manifests are DEPLOY_SHA256SUMS, additive_files.json and package_id.json.
'''
commands=(D/'b_evidence/coordinator_commands.sh').read_text().replace('17b0eb1ca7fe81a7',pid).replace('00:10:00','00:30:00').replace('FINAL COORDINATOR COMMANDS — NOT EXECUTED BY CENSUS05-B','C COORDINATOR COMMANDS — NOT EXECUTED; REQUIRE VERIFY_OK AND REVIEW')
(E/'coordinator_commands.sh').write_text(commands)
section=f'''\n\n## C: readout fix + redeploy

New package **{pid}**, 167 files; bundle `{bundle}`. No submission and no .git writes. Old B evidence and command block above remain historical. C smoke uses **--partition=debug --time=00:30:00** for all four kinds; full retains the packaged limits.

{changes}
Deployment completed into the new empty destination only. `c_evidence/readback.json`: **178/178** hashes match (167 payload, six unchanged inputs rehashed in place, five standing Cyrillic ledgers). No input copies or writes to the old package. Four unchanged verifier invocations and eight scheduler dry checks have receipts in `c_evidence/`; verifier status must be read there, not inferred from readback. The verifier requires a lead commit: it rejects tracked dirty files and payload bytes differing from HEAD. C must not be marked READY until all four are VERIFY_OK after the lead commits.

Mock readout last lines (synthetic generations, not production):

```text
'''+''.join((E/('mock-'+n+'.log')).read_text() for n in ['smoke-mode-i','smoke-mode-ii','full-mode-ii'])+'''```

Coordinator commands prepared only; require a successful unchanged verifier and owner review before actual submission:

```bash
'''+commands+'```\n'
if '\n\n## C: readout fix + redeploy' in s:s=s.split('\n\n## C: readout fix + redeploy')[0]
p.write_text(s+section)
p=D/'FOLLOW_UP.md';s=p.read_text();s=s.replace('# Census_05 follow-up — commands prepared, never executed','# Census_05 follow-up — C readout fix and new deployment');s=s.replace('No deploy, remote verification, test-only check, Slurm submission or reader run has occurred.', 'The C deployment and local readouts have occurred; see the C section in HANDOFF_CENSUS05.md and c_evidence/. No Slurm submission has occurred. The earlier B recipe below is historical; do not execute its input-copy steps for C.');s=s.replace('Compressed correction chunks are commit artifacts for reproducibility, outside DEPLOY_PATHS;', 'Compressed correction chunks are '+custody+', outside DEPLOY_PATHS;');s=s.replace('Apply readout_version.patch','Apply readout_fix.patch (superseding readout_version.patch)');s+='\n\n## C: readout fix + redeploy\n\n'+section.split('## C: readout fix + redeploy\n',1)[1];p.write_text(s)
# Retain historical B table explicitly labelled; current C table below carries fresh identities.
p=D/'REVIEW_INPUTS.md';old=p.read_text();old=old.replace('# CENSUS05 Astra review inputs','# Historical B review inputs (superseded by C below)',1)
paths=['DEPLOY_SHA256SUMS','PROJECTS_SHA256','package_id.json','INPUTS.json','readout/census_readout.py','readout/test_census_readout.py','readout_fix.patch','c_evidence/readback.json','c_evidence/archives.json','c_evidence/witnesses.json','c_evidence/readout_tests.log','c_evidence/regression_tests.log','c_evidence/package_comparison.json']
current=f'# CENSUS05-C review inputs\n\nCurrent package **{pid}**, bundle `{bundle}`, 167 files. Manifest SHA256 `{pkg["deploy_manifest_sha256"]}`.\n\n'+changes+'\nArchive custody: '+custody+'.\n\n| File | SHA256 |\n|---|---|\n'
for n in paths:current+=f'| `{n}` | `{hashlib.sha256((D/n).read_bytes()).hexdigest()}` |\n'
current+='\nCurrent receipts: `c_evidence/verify-{regression,parity,census,readout}.json` and `c_evidence/test_only.json`. The unchanged verifier requires the lead commit and all four VERIFY_OK before READY. No submission.\n\n'
p.write_text(current+old)
