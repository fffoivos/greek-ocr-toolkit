# DEPLOY1 receipt

Recorded 2026-10-20 00:14:30 EEST (Athens time from local `date`). **Deployed; verification blocked by missing shared interpreter. Do not submit yet.** No jobs, allocations, commits, staging or pushes were performed. All remote mutations were package-directory creation and file copies into the two new versioned roots; no existing remote package was overwritten or removed and no runtime repair was attempted.

Source branch: `sol/recut-v1`; HEAD: `e86fa153476d3e4731f8d17186fdbf565a43f6cd`. Both package directories were clean before additions. HEAD includes CROPS4 commit `157153fbe`. Unrelated dirty/untracked paths were preserved.

The brief contains both a commit-first rule and an explicit working-tree archive exception. This run uses that exception only for the three new bench02 deployment files. Existing bench02 payloads were checked byte-for-byte against HEAD. A temporary Git repository containing exactly DEPLOY_PATHS entries supplied tree `10d65b1745db5ae9155b8b52880c669cb304652d` to `git archive`; no commit was created. CROPS4 was archived directly from HEAD using its exact DEPLOY_PATHS entries. Archives excluded dry-run data and unrelated worktree changes.

A deploy SHA is the SHA256 of that package's DEPLOY_SHA256SUMS bytes; the directory suffix is its first eight hexadecimal characters. Each manifest excludes itself to avoid self-reference; the complete per-file lists below include the manifest's own hash. Remote SHA256 readback of **every deployed file**, including each manifest, exactly matched local bytes.

The lead must commit only the additions listed at the end, and the three bench02 files in that commit must match the recorded hashes. Existing deployed payload hashes must also match the lead's resulting tree. That future commit match has **not** been established by this run.

## bench02

Deployed root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/e2b58493`

Deploy SHA256: `e2b584935a70e0bae3634120aa3bc2df681b3004c817d1f93904f6c059c38ff7`

Remote VERIFY exit code: `1`. All 11 manifest entries passed. The script then failed its required interpreter existence/executable check. Python version and `bench02_draw.py --help` therefore did not run; no `VERIFY_OK` was printed. The separate read-only preflight below confirmed census input readability.

Complete per-file hashes (repository-relative paths):

```text
b2f33bfa6bc2f9a8122e348eb058b807a62d354be56143db25fde9f96711da6c  docs/harvest/collect_v3_admission/bench02/bench02_draw.py
077fbfbc120ed205b80abc8e33c6020892621867566f1cff84671521e0174160  docs/harvest/collect_v3_admission/bench02/extract.sbatch
7fd6e98de83ac3ed696989bbafc54782ad386ab5465ed9f570935f54bd0f2b7a  docs/harvest/collect_v3_admission/bench02/readout.sbatch
8bb14f33621c0c5331808aedfcfaec734f24120d42fd3eadc0d35f99e685285a  docs/harvest/collect_v3_admission/bench02/job_common.sh
7891484293752e0beca5c8665c1126649ebf62447bffbd82ab9d807b20ed9ece  docs/harvest/collect_v3_admission/bench02/submit_job.sh
7e418ec6b16157179d2a3619349d14d0e850dd1168f0574bdf0fe425c61e019e  docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh
90ef155eec4946a00e39c32b2d439feb69c2a5ffd9d8a04f9c37f980ef0b3f12  docs/harvest/collect_v3_admission/bench02/BRIEF.md
572d5b1fa6ec46ac0a44642183e103b53dd9759a128f32e7dc797fd020a3cd24  docs/harvest/collect_v3_admission/bench02/BENCH02D.md
e371edebbf8eb290e54b7c5afc1c0878c843e3920cffca98411dc089ac2f9cc7  docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md
e7a665dddc4b3c287a2edc9d04e4cb7627352c0f271a0470310612d703e6d1bd  docs/harvest/collect_v3_admission/bench02/VERIFY.sh
ec88690eefec1831e4ec17885055726c383ce83d4f34b79214bea911b8f08702  docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt
e2b584935a70e0bae3634120aa3bc2df681b3004c817d1f93904f6c059c38ff7  docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

Command run on Clariden:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/e2b58493 && bash docs/harvest/collect_v3_admission/bench02/VERIFY.sh /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current
```

Verbatim combined SSH stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
docs/harvest/collect_v3_admission/bench02/bench02_draw.py: OK
docs/harvest/collect_v3_admission/bench02/extract.sbatch: OK
docs/harvest/collect_v3_admission/bench02/readout.sbatch: OK
docs/harvest/collect_v3_admission/bench02/job_common.sh: OK
docs/harvest/collect_v3_admission/bench02/submit_job.sh: OK
docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh: OK
docs/harvest/collect_v3_admission/bench02/BRIEF.md: OK
docs/harvest/collect_v3_admission/bench02/BENCH02D.md: OK
docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md: OK
docs/harvest/collect_v3_admission/bench02/VERIFY.sh: OK
docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt: OK
```

Exact coordinator submission line, **documentation only; blocked until the required interpreter is restored and VERIFY passes**:

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/e2b58493 && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh extract $W/filter_pipeline_20261018/attempts/census_03/current $W/filter_pipeline_20261018/bench02/census03
```

The output directory was absent at both preflights. Recheck its absence immediately before future submission. This is the census_03 mechanics extract, not the census_05 benchmark draw.

## CROPS4

Deployed root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/c9bb1bb0`

Deploy SHA256: `c9bb1bb097c3979f8d60cb5f8c7e73e58d5b6a00d0cf74c7d9449e2fe524b63e`

Package-level check exit code: `1`. All eight manifest entries passed; the codec file exists and is readable. The required venv Python is missing, so **VERIFY_DEPLOY_OK was not printed**. Full CROPS4 VERIFY was deliberately not invoked: it additionally requires completed census_05 and its pinned prepared-code identity. No full `VERIFY_OK` is claimed.

Complete per-file hashes (relative to the deployed CROPS4 root):

```text
1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73  materialise_crops.py
ee30191b6374cc6a7a56d69852f405035373f1c451ecec066021b1811d32e9df  crops4.sbatch
5b022b7707c4bc890b620744bd036bfd8d27bd8b38f4e03120ffae21749dde78  VERIFY.sh
1d185040cadf1675d41120a8e26e54d1ba065d55dea39030f6741512ca1194f7  CROPS4.md
45523e6b807cb1c6a18c8c2b0e44d8ddd53c7f707806260d4b73b65f32bf2a01  test_crops4.py
db7dc2929fa89fc41f46e6e702dc01544ac1bfacd1febf201c09bab6b1d88fa7  TESTS.log
6e7942f60c088c000e8591796f0e3f5325ad7599234aa1493a3ca7f76e59eb20  TEST_RESULTS.json
a21d9c7417762831d13318dfb4b129fccc25588892299518fda511bd5a100697  DEPLOY_PATHS.txt
c9bb1bb097c3979f8d60cb5f8c7e73e58d5b6a00d0cf74c7d9449e2fe524b63e  DEPLOY_SHA256SUMS
```

Package-level command run on Clariden:

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/c9bb1bb0
sha256sum -c DEPLOY_SHA256SUMS
python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python
codec=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng
rc=0
if test -f "$python" && test -x "$python"; then echo PYTHON_PRESENT; else echo "MISSING_PYTHON $python"; rc=1; fi
if test -f "$codec" && test -r "$codec"; then echo CODEC_PRESENT; else echo "MISSING_CODEC $codec"; rc=1; fi
test "$rc" -eq 0
printf 'VERIFY_DEPLOY_OK crops4 c9bb1bb0\n'
```

Verbatim combined SSH stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
materialise_crops.py: OK
crops4.sbatch: OK
VERIFY.sh: OK
CROPS4.md: OK
test_crops4.py: OK
TESTS.log: OK
TEST_RESULTS.json: OK
DEPLOY_PATHS.txt: OK
MISSING_PYTHON /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python
CODEC_PRESENT
```

Coordinator commands from CROPS4.md, with the deployed root filled in. These are **not executed**. After the interpreter is restored, repeat package-level checks. Run these commands only after completed census_05; `CENSUS_PROJECTS` and `PROJECTS_SHA256` must be copied from that job's actual verified launch binding. Their values remain unknown; do not use the placeholders literally.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B="/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/c9bb1bb0"
export CENSUS_ATTEMPT="$W/filter_pipeline_20261018/attempts/census_05"
export CENSUS_PROJECTS=/REPLACE_WITH_CENSUS05_PREPARED_PROJECTS
export PROJECTS_SHA256=REPLACE_WITH_CENSUS05_PINNED_SHA256SUMS_HASH
export PYTHON="$W/filter_pipeline_20261018/venv_l1/bin/python"
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PYTHONPATH="$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut"
export TRANCHE=W2 INCLUDE_HELDOUT=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
export ATTEMPT=crops4_verify_01
mkdir -p "$W/crops4_attempts/$ATTEMPT/tmp"
export TMPDIR="$W/crops4_attempts/$ATTEMPT/tmp"
[[ "$(sha256sum "$CENSUS_PROJECTS/SHA256SUMS" | cut -d' ' -f1)" == "$PROJECTS_SHA256" ]]
(cd "$CENSUS_PROJECTS" && sha256sum --check --quiet SHA256SUMS)
bash "$B/VERIFY.sh" --census-attempt "$CENSUS_ATTEMPT" \
  --census-code "$PYTHONPATH" --work-root "$W" \
  --attempt "$W/crops4_attempts/$ATTEMPT" --include-heldout
# Successful stdout is exactly: VERIFY_OK <selected_rows> <distinct_source_pages>
# Hash-check detail goes to stderr; failure prints no VERIFY_OK.

export MODE=smoke ATTEMPT=crops4_smoke_01
mkdir -p "$W/crops4_attempts/$ATTEMPT"
# SBATCH copies its script into a spool directory; retain the deployed package location:
export CROPS4_PACKAGE="$B/crops4.sbatch"
SMOKE_JOB=$(sbatch --parsable --export=ALL \
  --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$B/crops4.sbatch")
# Wait for successful smoke completion and review its receipt and sha256check.log.
export SMOKE_RECEIPT="$W/crops4_attempts/$ATTEMPT/upload_receipt.json"
"$PYTHON" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["status"]=="ok" and r["selected"]==r["byte_exact"]==500; print("SMOKE_OK 500/500")' "$SMOKE_RECEIPT"

export MODE=full ATTEMPT=crops4_full_01
mkdir -p "$W/crops4_attempts/$ATTEMPT"
sbatch --export=ALL --dependency="afterok:${SMOKE_JOB%%;*}" \
  --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$B/crops4.sbatch"
```

## Final read-only preflight

Exit code: `1`. This checks runtime, census input readability and output absence without creating the output directory.

Verbatim combined SSH stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
2026-10-20 00:13:51 EEST
CENSUS03_OUTPUT_ABSENT
CENSUS_INPUT_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/decisions.jsonl
CENSUS_INPUT_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/evaluation_diagnostics.jsonl
MISSING_PYTHON /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python
```

## Exact files for the lead to commit (4)

- `docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt`
- `docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/bench02/VERIFY.sh`
- `docs/harvest/collect_v3_admission/DEPLOY1_RECEIPT.md`

Only the first three files belong to bench02 additions; the fourth is this receipt. Do not stage the supplied untracked brief or any unrelated paths. No deployment file was changed after archiving. Local `bash -n` and `git diff --check` passed.

The requested success footer cannot truthfully be emitted: both required verification markers are blocked by the missing shared Python.

DEPLOY1: blocked | bench02 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/e2b58493 VERIFY_FAILED e2b58493 | crops4 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/c9bb1bb0 VERIFY_DEPLOY_FAILED c9bb1bb0 | no jobs submitted | files to commit 4
