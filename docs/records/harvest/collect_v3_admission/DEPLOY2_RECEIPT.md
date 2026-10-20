# DEPLOY2 receipt

Recorded 2026-10-20 00:17:23 EEST (Athens time from local `date`). **Both packages deployed and verified.** No jobs, allocations, staging, commits, pushes or paid services were used. Network access was limited to `ssh clariden` and `rsync`. Local batch-script tests used stubs; no scheduler submission was executed. Remote writes were limited to creating the two new versioned package directories and copying package files. No remote files were overwritten or deleted; DEPLOY1 roots `bench02_pkg/e2b58493` and `crops4_package/c9bb1bb0` were left untouched.

Source branch: `sol/recut-v1`; HEAD: `e86fa153476d3e4731f8d17186fdbf565a43f6cd`. DEPLOY2 explicitly authorizes working-tree corrections and no commit. Following DEPLOY1’s archive exception, each exact DEPLOY_PATHS payload was copied to a temporary Git repository, added to its temporary index, and archived with `git archive` from a tree object without creating a commit. The extracted archives supplied deployment bytes. Archive trees: bench02 `bc87969717f60f96818d197463d7511790eab7ed`; CROPS4 `b3cf2b50c2e01eef409ac5676cad3c9f7eabaaf1`. Unrelated dirty/untracked files were preserved.

The only source/document edits were replacement of `filter_pipeline_20261018/venv_l1` with `venv_l1` in the six paths listed below; the codec path is unchanged. CROPS4 `VERIFY.sh` already uses the supplied `$PYTHON` and needed no edit. Existing DEPLOY1 receipts and briefs remain historical records. Test artifacts, deployment manifests and CROPS4 guard hashes were regenerated as requested. A deploy SHA is SHA256 of DEPLOY_SHA256SUMS bytes, with its first eight hex characters naming the directory. Each manifest excludes itself; per-file lists below include its own hash. Remote readback matched every file including each manifest.

## Path correction evidence

Command run before and after:

```bash
grep -rn venv_l1 docs/harvest/collect_v3_admission/bench02 docs/harvest/collect_v3_admission/crops4
```

Before:

```text
docs/harvest/collect_v3_admission/bench02/BENCH02D.md:108:`extract.sbatch` requests account a0140, partition **normal**, one node, one task/CPU, **01:00:00**, no memory option. The wrapper supplies the absolute log path `$OUT/extract-%j.log` through `sbatch --output` and exports the deployed `BENCH02_DIR` for Slurm's spooled script. Both jobs use `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python`; the tool asserts Python >=3.10 at startup. No partition probe or job submission was performed. SQLite stores only slim diagnostic evidence and seen keys in a temporary database beneath the output directory, so neither full multi-GB file is loaded into memory. It streams each input and joins by both identity fields, reports both join rates, and removes the temporary database on normal completion.
docs/harvest/collect_v3_admission/bench02/VERIFY.sh:7:python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python
docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md:14:This wrapper creates `$OUT` and invokes `sbatch --export=ALL --output="$OUT/extract-%j.log" "$B/extract.sbatch" --census-dir "$CENSUS" --output-dir "$OUT"`. It exports the absolute `BENCH02_DIR` because Slurm executes a spooled copy of the batch script. The job requests account a0140, partition normal, one node, one task/CPU and **01:00:00** for both extract and readout; no `--mem`. Both batch jobs use the census `venv_l1/bin/python`, with Python >=3.10 asserted at tool startup. Do not bypass the wrapper without setting `BENCH02_DIR` and supplying **absolute `sbatch --output`** explicitly: `#SBATCH` does not expand `$OUT`.
docs/harvest/collect_v3_admission/bench02/job_common.sh:16:python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python
docs/harvest/collect_v3_admission/bench02/test_bench02e.py:130:                self.assertIn('SRUN:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python',out)
docs/harvest/collect_v3_admission/crops4/CROPS4.md:36:export PYTHON="$W/filter_pipeline_20261018/venv_l1/bin/python"
docs/harvest/collect_v3_admission/crops4/crops4.sbatch:25:export PYTHON="${PYTHON:-$W/filter_pipeline_20261018/venv_l1/bin/python}"
```

After:

```text
docs/harvest/collect_v3_admission/bench02/BENCH02D.md:108:`extract.sbatch` requests account a0140, partition **normal**, one node, one task/CPU, **01:00:00**, no memory option. The wrapper supplies the absolute log path `$OUT/extract-%j.log` through `sbatch --output` and exports the deployed `BENCH02_DIR` for Slurm's spooled script. Both jobs use `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`; the tool asserts Python >=3.10 at startup. No partition probe or job submission was performed. SQLite stores only slim diagnostic evidence and seen keys in a temporary database beneath the output directory, so neither full multi-GB file is loaded into memory. It streams each input and joins by both identity fields, reports both join rates, and removes the temporary database on normal completion.
docs/harvest/collect_v3_admission/bench02/VERIFY.sh:7:python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md:14:This wrapper creates `$OUT` and invokes `sbatch --export=ALL --output="$OUT/extract-%j.log" "$B/extract.sbatch" --census-dir "$CENSUS" --output-dir "$OUT"`. It exports the absolute `BENCH02_DIR` because Slurm executes a spooled copy of the batch script. The job requests account a0140, partition normal, one node, one task/CPU and **01:00:00** for both extract and readout; no `--mem`. Both batch jobs use the census `venv_l1/bin/python`, with Python >=3.10 asserted at tool startup. Do not bypass the wrapper without setting `BENCH02_DIR` and supplying **absolute `sbatch --output`** explicitly: `#SBATCH` does not expand `$OUT`.
docs/harvest/collect_v3_admission/bench02/job_common.sh:16:python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
docs/harvest/collect_v3_admission/bench02/test_bench02e.py:130:                self.assertIn('SRUN:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python',out)
docs/harvest/collect_v3_admission/crops4/CROPS4.md:36:export PYTHON="$W/venv_l1/bin/python"
docs/harvest/collect_v3_admission/crops4/crops4.sbatch:25:export PYTHON="${PYTHON:-$W/venv_l1/bin/python}"
```

## Local validation

```bash
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/harvest/collect_v3_admission/bench02/run_tests.py
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/harvest/collect_v3_admission/crops4/test_crops4.py > docs/harvest/collect_v3_admission/crops4/TESTS.log 2>&1
```

Both commands exited 0. Bench02: **34 passed**, filesystem audit: 141 write operations checked; outside writes: 0. CROPS4: **14 passed**, with 20/20 independent originals byte exact and the independent 500-row rate fixture passing. The requested interpreter resolves to the shared toolkit environment; TEST_RESULTS.json truthfully records its `sys.executable` as `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`. Local timings are not Clariden throughput qualification.

```text

----------------------------------------------------------------------
Ran 34 tests in 12.070s

OK
Filesystem audit: 141 write operations checked; outside writes: 0
```

Full CROPS4 output is in `crops4/TESTS.log`; regenerated measurements are in `crops4/TEST_RESULTS.json`. After regeneration, `python3 -B docs/harvest/collect_v3_admission/crops4/guard_commit.py` printed `GUARD_OK 13 paths; no staging or commit performed`. `bash -n` passed for both changed shell files plus both VERIFY scripts; `git diff --check` passed. The CROPS4 guard covers its original 13-path package scope; the DEPLOY2 handoff list below also includes bench02 and this receipt.

## Deployment creation and transfer

The following SSH command exited 0; exclusive `mkdir` followed absence checks for both destinations:

```bash
set -eu
test ! -e /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519 && test ! -L /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519
test ! -e /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a && test ! -L /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a
mkdir /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519
mkdir /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a
```

Verbatim combined SSH stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

Each extracted archive was transferred with `rsync -a --ignore-existing <extracted-payload>/ clariden:<new-root>/`; both exited 0. No --delete or overwrite option was used. Verbatim combined rsync stdout/stderr:

```text
bench02:
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
crops4:
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

## bench02

Deployed root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519`

Deploy SHA256: `9e779519a7be15c5f4ddac981d7a7a89c5860005dcef9270b9a3f70a35a69782`

Complete per-file hashes (repository-relative paths):

```text
b2f33bfa6bc2f9a8122e348eb058b807a62d354be56143db25fde9f96711da6c  docs/harvest/collect_v3_admission/bench02/bench02_draw.py
077fbfbc120ed205b80abc8e33c6020892621867566f1cff84671521e0174160  docs/harvest/collect_v3_admission/bench02/extract.sbatch
7fd6e98de83ac3ed696989bbafc54782ad386ab5465ed9f570935f54bd0f2b7a  docs/harvest/collect_v3_admission/bench02/readout.sbatch
2378d662d3ad28adb227785ff6ef4bd65c2de77587ae9a51acda0ab79097fc7d  docs/harvest/collect_v3_admission/bench02/job_common.sh
7891484293752e0beca5c8665c1126649ebf62447bffbd82ab9d807b20ed9ece  docs/harvest/collect_v3_admission/bench02/submit_job.sh
7e418ec6b16157179d2a3619349d14d0e850dd1168f0574bdf0fe425c61e019e  docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh
90ef155eec4946a00e39c32b2d439feb69c2a5ffd9d8a04f9c37f980ef0b3f12  docs/harvest/collect_v3_admission/bench02/BRIEF.md
3a4432cf84e87a85b070220bc5e9f4f279938ead303fe1e5f3834d80df0be98e  docs/harvest/collect_v3_admission/bench02/BENCH02D.md
e371edebbf8eb290e54b7c5afc1c0878c843e3920cffca98411dc089ac2f9cc7  docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md
3040f02c64358e07c652b65ea4d114cc86ff9c646f82cd9ad4e6aee7f23a8bd9  docs/harvest/collect_v3_admission/bench02/VERIFY.sh
ec88690eefec1831e4ec17885055726c383ce83d4f34b79214bea911b8f08702  docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt
9e779519a7be15c5f4ddac981d7a7a89c5860005dcef9270b9a3f70a35a69782  docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

Remote check exit code: **0**. Command passed to `ssh clariden bash -s`:

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519
bash docs/harvest/collect_v3_admission/bench02/VERIFY.sh /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current
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
usage: bench02_draw.py [-h] {extract,readout,draw} ...

Offline BENCH02 draw, slim extraction and candidate readout (Python >=3.10).

positional arguments:
  {extract,readout,draw}

options:
  -h, --help            show this help message and exit
VERIFY_OK bench02 9e779519
```

Remote hash readback command (exit 0):

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519
sha256sum docs/harvest/collect_v3_admission/bench02/bench02_draw.py docs/harvest/collect_v3_admission/bench02/extract.sbatch docs/harvest/collect_v3_admission/bench02/readout.sbatch docs/harvest/collect_v3_admission/bench02/job_common.sh docs/harvest/collect_v3_admission/bench02/submit_job.sh docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh docs/harvest/collect_v3_admission/bench02/BRIEF.md docs/harvest/collect_v3_admission/bench02/BENCH02D.md docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md docs/harvest/collect_v3_admission/bench02/VERIFY.sh docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

Verbatim combined SSH stdout/stderr; all entries matched local bytes:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
b2f33bfa6bc2f9a8122e348eb058b807a62d354be56143db25fde9f96711da6c  docs/harvest/collect_v3_admission/bench02/bench02_draw.py
077fbfbc120ed205b80abc8e33c6020892621867566f1cff84671521e0174160  docs/harvest/collect_v3_admission/bench02/extract.sbatch
7fd6e98de83ac3ed696989bbafc54782ad386ab5465ed9f570935f54bd0f2b7a  docs/harvest/collect_v3_admission/bench02/readout.sbatch
2378d662d3ad28adb227785ff6ef4bd65c2de77587ae9a51acda0ab79097fc7d  docs/harvest/collect_v3_admission/bench02/job_common.sh
7891484293752e0beca5c8665c1126649ebf62447bffbd82ab9d807b20ed9ece  docs/harvest/collect_v3_admission/bench02/submit_job.sh
7e418ec6b16157179d2a3619349d14d0e850dd1168f0574bdf0fe425c61e019e  docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh
90ef155eec4946a00e39c32b2d439feb69c2a5ffd9d8a04f9c37f980ef0b3f12  docs/harvest/collect_v3_admission/bench02/BRIEF.md
3a4432cf84e87a85b070220bc5e9f4f279938ead303fe1e5f3834d80df0be98e  docs/harvest/collect_v3_admission/bench02/BENCH02D.md
e371edebbf8eb290e54b7c5afc1c0878c843e3920cffca98411dc089ac2f9cc7  docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md
3040f02c64358e07c652b65ea4d114cc86ff9c646f82cd9ad4e6aee7f23a8bd9  docs/harvest/collect_v3_admission/bench02/VERIFY.sh
ec88690eefec1831e4ec17885055726c383ce83d4f34b79214bea911b8f08702  docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt
9e779519a7be15c5f4ddac981d7a7a89c5860005dcef9270b9a3f70a35a69782  docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

Exact coordinator submission line for the **census_03 mechanics extract**, documentation only; not executed:

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519 && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh extract $W/filter_pipeline_20261018/attempts/census_03/current $W/filter_pipeline_20261018/bench02/census03
```

The output directory was absent at the final read-only preflight below. Recheck absence immediately before submission.

## CROPS4

Deployed root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a`

Deploy SHA256: `5f4d275a93b96743bc43b76a20509b626d6076ff63f2a0567c3d38143eac36bb`

Complete per-file hashes (relative to deployed CROPS4 root):

```text
1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73  materialise_crops.py
88c5aa1ce988e2ea2d3fb0e35fdefa0f3565b28a58875156f03267f1d794ccaa  crops4.sbatch
5b022b7707c4bc890b620744bd036bfd8d27bd8b38f4e03120ffae21749dde78  VERIFY.sh
9ecc0445c254ea171a34a5c73d531c15e72c96f5610ba23e34a89faa3e063d15  CROPS4.md
45523e6b807cb1c6a18c8c2b0e44d8ddd53c7f707806260d4b73b65f32bf2a01  test_crops4.py
9b87c209ee5f11e7cf90dd5771671ac8255d073c278414f2d783946f2b5e2fc4  TESTS.log
fed39c9e6c6180af8c86c5c6d35d6f750a180053210670fc374829b563b8d63c  TEST_RESULTS.json
a21d9c7417762831d13318dfb4b129fccc25588892299518fda511bd5a100697  DEPLOY_PATHS.txt
5f4d275a93b96743bc43b76a20509b626d6076ff63f2a0567c3d38143eac36bb  DEPLOY_SHA256SUMS
```

Remote check exit code: **0**. Command passed to `ssh clariden bash -s`:

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a
sha256sum -c DEPLOY_SHA256SUMS
python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
codec=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng
test -f "$python" && test -x "$python"
test -f "$codec" && test -r "$codec"
export PYTHONDONTWRITEBYTECODE=1 LD_PRELOAD="$codec"
"$python" -B -c 'import sys,PIL; assert sys.version_info >= (3,10); print("PYTHON",sys.version.split()[0]); print("PIL",PIL.__version__)'
printf 'CODEC_READABLE %s\n' "$codec"
printf 'VERIFY_DEPLOY_OK crops4 5f4d275a\n'
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
PYTHON 3.12.15
PIL 12.3.0
CODEC_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng
VERIFY_DEPLOY_OK crops4 5f4d275a
```

Remote hash readback command (exit 0):

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a
sha256sum materialise_crops.py crops4.sbatch VERIFY.sh CROPS4.md test_crops4.py TESTS.log TEST_RESULTS.json DEPLOY_PATHS.txt DEPLOY_SHA256SUMS
```

Verbatim combined SSH stdout/stderr; all entries matched local bytes:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73  materialise_crops.py
88c5aa1ce988e2ea2d3fb0e35fdefa0f3565b28a58875156f03267f1d794ccaa  crops4.sbatch
5b022b7707c4bc890b620744bd036bfd8d27bd8b38f4e03120ffae21749dde78  VERIFY.sh
9ecc0445c254ea171a34a5c73d531c15e72c96f5610ba23e34a89faa3e063d15  CROPS4.md
45523e6b807cb1c6a18c8c2b0e44d8ddd53c7f707806260d4b73b65f32bf2a01  test_crops4.py
9b87c209ee5f11e7cf90dd5771671ac8255d073c278414f2d783946f2b5e2fc4  TESTS.log
fed39c9e6c6180af8c86c5c6d35d6f750a180053210670fc374829b563b8d63c  TEST_RESULTS.json
a21d9c7417762831d13318dfb4b129fccc25588892299518fda511bd5a100697  DEPLOY_PATHS.txt
5f4d275a93b96743bc43b76a20509b626d6076ff63f2a0567c3d38143eac36bb  DEPLOY_SHA256SUMS
```

Only **package-level** CROPS4 verification was run. Full CROPS4 VERIFY still requires completed census_05 and its verified prepared-code identity; no full `VERIFY_OK` is claimed.

Coordinator commands from CROPS4.md, with the new root and corrected interpreter path filled in. **Documentation only; none executed.** `CENSUS_PROJECTS` and `PROJECTS_SHA256` remain unknown: replace their placeholders with census_05’s actual verified launch binding before running. The deployment copy has already completed; use this versioned root.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B="/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a"
export CENSUS_ATTEMPT="$W/filter_pipeline_20261018/attempts/census_05"
export CENSUS_PROJECTS=/REPLACE_WITH_CENSUS05_PREPARED_PROJECTS
export PROJECTS_SHA256=REPLACE_WITH_CENSUS05_PINNED_SHA256SUMS_HASH
export PYTHON="$W/venv_l1/bin/python"
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

Exit code: **0**. Command:

```bash
set -eu
TZ=Europe/Athens date '+%Y-%m-%d %H:%M:%S %Z'
test ! -e /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census03
test ! -L /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census03
echo CENSUS03_OUTPUT_ABSENT
for name in decisions.jsonl evaluation_diagnostics.jsonl; do
  path=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/$name
  test -f "$path" && test -r "$path"
  : < "$path"
  printf 'CENSUS_INPUT_READABLE %s\n' "$path"
done
```

Verbatim combined SSH stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
2026-10-20 00:16:42 EEST
CENSUS03_OUTPUT_ABSENT
CENSUS_INPUT_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/decisions.jsonl
CENSUS_INPUT_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/evaluation_diagnostics.jsonl
```

## Exact files for the lead to commit (13)

- `docs/harvest/collect_v3_admission/bench02/BENCH02D.md`
- `docs/harvest/collect_v3_admission/bench02/job_common.sh`
- `docs/harvest/collect_v3_admission/bench02/test_bench02e.py`
- `docs/harvest/collect_v3_admission/bench02/VERIFY.sh`
- `docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt`
- `docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/crops4/CROPS4.md`
- `docs/harvest/collect_v3_admission/crops4/crops4.sbatch`
- `docs/harvest/collect_v3_admission/crops4/TESTS.log`
- `docs/harvest/collect_v3_admission/crops4/TEST_RESULTS.json`
- `docs/harvest/collect_v3_admission/crops4/DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/crops4/COMMIT_LIST.json`
- `docs/harvest/collect_v3_admission/DEPLOY2_RECEIPT.md`

The list includes the three still-untracked bench02 deployment additions inherited from DEPLOY1. The historical DEPLOY1 receipt remains a separate prior handoff; it was not edited here. Do not stage the supplied DEPLOY2 brief or unrelated paths. No source or deployment artifact was changed after archiving. The lead’s future commit must preserve all recorded deployment hashes; no future commit match is claimed.

Hashes of additional handoff files outside the deployed payload (this receipt excludes its own self-hash):

```text
3631fcd2f0f0ae097662ddeb55eed1e77da0f2a83158bf4b615a68deaf165f56  docs/harvest/collect_v3_admission/bench02/test_bench02e.py
9c6e69f8072777923163ba7757ee097f4fed4176d94dada8c0b7c3279f962ef3  docs/harvest/collect_v3_admission/crops4/COMMIT_LIST.json
```

DEPLOY2: done | bench02 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/9e779519 VERIFY_OK 9e779519 | crops4 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/5f4d275a VERIFY_DEPLOY_OK 5f4d275a | tests bench02 34 crops4 14 passed | no jobs submitted | files to commit 13
