# CROPS4B receipt

Recorded 2026-10-20 05:26:52 EEST (Athens time from `date`). Deployed and verified; no jobs submitted, no spend, no commit. Network use was limited to `ssh clariden` and `rsync`. Remote writes were confined to the new versioned directory; nothing was overwritten or deleted. Previous roots `5f4d275a` and `c9bb1bb0` were left untouched. Unrelated worktree changes were preserved.

Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8`

Deploy SHA256 (hash of DEPLOY_SHA256SUMS bytes): `add0b5f8886023eb9b086916f320608e644a42ea1ad0c2137bb63ab08d46a96b`

The exact DEPLOY_PATHS payload was placed in a temporary Git index, archived from tree `1c8f6cef4f58c1766a7ae827d06f159a0047bb62` without a commit, extracted, and transferred with `rsync -a --ignore-existing`. The deployment manifest excludes itself; all ten deployed files, including the manifest itself, were read back and matched locally.

## Change and validation

Added configurable code root, checksum file and checksum root with the original defaults, an absolute checksum-file path before changing directory, and the requested reconstruction binding guard. The census05 manifest is byte-identical to the segcensus lead's local file: SHA256 `997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb`, 167 entries. `materialise_crops.py` is unchanged (SHA256 `1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73`); no new admission gates were added.

Local test command (exit 0):

```bash
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/harvest/collect_v3_admission/crops4/test_crops4.py > docs/harvest/collect_v3_admission/crops4/TESTS.log 2>&1
```

All 16 tests passed: the original 14, a census05 repository-relative manifest outside the projects tree with an end-to-end 500/500 smoke, and unlisted CENSUS_CODE rejection before verification or materialisation. Scheduler calls in local tests used the existing local stub only. `TEST_RESULTS.json` records the actual interpreter. `bash -n`, `git diff --check`, and `guard_commit.py` passed (`GUARD_OK 14 paths; no staging or commit performed`). The guard's historical whole-package allowlist is broader than the changed-file handoff below.

Per-file deployed hashes:

```text
1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73  materialise_crops.py
2f72ddd414b39e9928f29f86ecfff50f0dfc666c9c19d4252824b67ed421cabf  crops4.sbatch
5b022b7707c4bc890b620744bd036bfd8d27bd8b38f4e03120ffae21749dde78  VERIFY.sh
9ecc0445c254ea171a34a5c73d531c15e72c96f5610ba23e34a89faa3e063d15  CROPS4.md
b10141aee58ba702fa387ec3793a6641cdb3579fc3fe885b076f1c519f95eb3e  test_crops4.py
a48ec1c9c423ac7ce6f7ba43b4e5ac5ac902ffa5307da39b1dfde9036452aa92  TESTS.log
9ced11e9ff21c27e2f962a01ac17b107e2f31d4c3a99235bbdbd44f46653fbd2  TEST_RESULTS.json
aed76b92c4f58866a6bd1d96f3fd7276f2849551c1f27847667cac6b80e3be1f  DEPLOY_PATHS.txt
add0b5f8886023eb9b086916f320608e644a42ea1ad0c2137bb63ab08d46a96b  DEPLOY_SHA256SUMS
997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb  census05_DEPLOY_SHA256SUMS
```

Batch-script diff:

```diff
diff --git a/docs/harvest/collect_v3_admission/crops4/crops4.sbatch b/docs/harvest/collect_v3_admission/crops4/crops4.sbatch
index 707bb488a..7bd07115a 100755
--- a/docs/harvest/collect_v3_admission/crops4/crops4.sbatch
+++ b/docs/harvest/collect_v3_admission/crops4/crops4.sbatch
@@ -26,12 +26,18 @@ export PYTHON="${PYTHON:-$W/venv_l1/bin/python}"
 export LD_PRELOAD="${CODEC_PRELOAD-$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng}"
 # Empty preload is allowed only by an explicit local mock invocation; production default must exist.
 [[ -z "$LD_PRELOAD" || -f "$LD_PRELOAD" ]]
-export PYTHONPATH="$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut"
+export PYTHONPATH="${CENSUS_CODE:-$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut}"
+PROJECTS_SUMS="${PROJECTS_SUMS:-$CENSUS_PROJECTS/SHA256SUMS}"
+PROJECTS_SUMS_ROOT="${PROJECTS_SUMS_ROOT:-$CENSUS_PROJECTS}"
+PROJECTS_SUMS="$(cd "$(dirname "$PROJECTS_SUMS")" && pwd)/$(basename "$PROJECTS_SUMS")"
 checksum() {
   if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi
 }
-[[ "$(checksum "$CENSUS_PROJECTS/SHA256SUMS" | cut -d' ' -f1)" == "$PROJECTS_SHA256" ]]
-(cd "$CENSUS_PROJECTS" && checksum -c SHA256SUMS) >"$A/prepared-check.log" 2>&1
+[[ "$(checksum "$PROJECTS_SUMS" | cut -d' ' -f1)" == "$PROJECTS_SHA256" ]]
+(cd "$PROJECTS_SUMS_ROOT" && checksum -c "$PROJECTS_SUMS") >"$A/prepared-check.log" 2>&1
+# Bind the reconstruction module selected for import to an entry in the checked manifest.
+MODULE_REL="$("$PYTHON" -B -c 'import os,sys; print(os.path.relpath(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])))' "$PYTHONPATH/greekocr/harvest/line_pipeline_native.py" "$PROJECTS_SUMS_ROOT")"
+awk -v path="$MODULE_REL" 'substr($0,67)==path {found=1} END {exit !found}' "$PROJECTS_SUMS" || { echo "reconstruction module not in PROJECTS_SUMS: $MODULE_REL" >&2; exit 1; }
 ARGS=(--census-attempt "$CENSUS_ATTEMPT" --census-code "$PYTHONPATH" --work-root "$W" --attempt "$A" --tranche "${TRANCHE:-W2}" --mode "$MODE")
 if [[ "${INCLUDE_HELDOUT:-0}" == 1 ]]; then ARGS+=(--include-heldout); fi
 if [[ "$MODE" == full ]]; then ARGS+=(--smoke-receipt "${SMOKE_RECEIPT:?500/500 smoke receipt required}"); fi
```

## Remote commands and verbatim output

No `VERIFY.sh` or `--verify-only` was run on Clariden. The quiet census manifest check produced no output and exited 0; the following success marker is from the enclosing shell. The import used the required codec, Python and code root.

### Exclusive new directory

Exit code: 0

```bash
ssh clariden bash -s
set -eu
test ! -e /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8 && test ! -L /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8
mkdir /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8
```

Verbatim combined stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

### Transfer archive payload

Exit code: 0

```bash
rsync -a --ignore-existing /tmp/crops4b-p9itwhgp/payload/ clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8/
```

Verbatim combined stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

### Light checks and every-file readback

Exit code: 0

```bash
ssh clariden bash -s
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8
cd "$B"
sha256sum -c DEPLOY_SHA256SUMS
export PYTHON="$W/venv_l1/bin/python"
codec="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
test -f "$PYTHON" && test -x "$PYTHON"
test -f "$codec" && test -r "$codec"
export PYTHONDONTWRITEBYTECODE=1 LD_PRELOAD="$codec"
"$PYTHON" -B -c 'import sys,PIL; assert sys.version_info >= (3,10); print("PYTHON",sys.version.split()[0]); print("PIL",PIL.__version__)'
printf 'CODEC_READABLE %s\n' "$codec"
printf 'VERIFY_DEPLOY_OK crops4 add0b5f8\n'
sha256sum materialise_crops.py crops4.sbatch VERIFY.sh CROPS4.md test_crops4.py TESTS.log TEST_RESULTS.json DEPLOY_PATHS.txt DEPLOY_SHA256SUMS census05_DEPLOY_SHA256SUMS
export K="$W/census_05_20261020/code/997b7d2ab5a8775b"
export CENSUS_PROJECTS="$K/docs/harvest/census05/package/projects"
export PYTHONPATH="$CENSUS_PROJECTS/greek-ocr-toolkit-pipe032"
export PROJECTS_SUMS="$B/census05_DEPLOY_SHA256SUMS" PROJECTS_SUMS_ROOT="$K"
[[ "$(sha256sum "$PROJECTS_SUMS" | cut -d' ' -f1)" == 997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb ]]
(cd "$K" && sha256sum --check --quiet "$PROJECTS_SUMS")
echo 'CENSUS05_MANIFEST_OK 167/167 (quiet check exited 0)'
"$PYTHON" -B -c 'import hashlib,pathlib; import greekocr.harvest.line_pipeline_native as m; p=pathlib.Path(m.__file__); h=hashlib.sha256(p.read_bytes()).hexdigest(); print(m.__file__); print(h); assert h=="e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7"'
MODULE_REL="$("$PYTHON" -B -c 'import os,sys; print(os.path.relpath(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])))' "$PYTHONPATH/greekocr/harvest/line_pipeline_native.py" "$PROJECTS_SUMS_ROOT")"; awk -v path="$MODULE_REL" 'substr($0,67)==path {found=1} END {exit !found}' "$PROJECTS_SUMS" || { echo "reconstruction module not in PROJECTS_SUMS: $MODULE_REL" >&2; exit 1; }
echo BINDING_GUARD_OK
```

Verbatim combined stdout/stderr:

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
census05_DEPLOY_SHA256SUMS: OK
PYTHON 3.12.15
PIL 12.3.0
CODEC_READABLE /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng
VERIFY_DEPLOY_OK crops4 add0b5f8
1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73  materialise_crops.py
2f72ddd414b39e9928f29f86ecfff50f0dfc666c9c19d4252824b67ed421cabf  crops4.sbatch
5b022b7707c4bc890b620744bd036bfd8d27bd8b38f4e03120ffae21749dde78  VERIFY.sh
9ecc0445c254ea171a34a5c73d531c15e72c96f5610ba23e34a89faa3e063d15  CROPS4.md
b10141aee58ba702fa387ec3793a6641cdb3579fc3fe885b076f1c519f95eb3e  test_crops4.py
a48ec1c9c423ac7ce6f7ba43b4e5ac5ac902ffa5307da39b1dfde9036452aa92  TESTS.log
9ced11e9ff21c27e2f962a01ac17b107e2f31d4c3a99235bbdbd44f46653fbd2  TEST_RESULTS.json
aed76b92c4f58866a6bd1d96f3fd7276f2849551c1f27847667cac6b80e3be1f  DEPLOY_PATHS.txt
add0b5f8886023eb9b086916f320608e644a42ea1ad0c2137bb63ab08d46a96b  DEPLOY_SHA256SUMS
997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb  census05_DEPLOY_SHA256SUMS
CENSUS05_MANIFEST_OK 167/167 (quiet check exited 0)
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py
e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7
BINDING_GUARD_OK
```

## Coordinator command blocks

Documentation only; not executed. Run the first block on Clariden to perform the light checks and submit smoke. Run the second block in the same shell after the smoke job completes successfully; it checks 500/500 and submits full with the recorded smoke job dependency. No login-node census parsing is included.

```bash
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8
export CENSUS_ATTEMPT="$W/census_05_20261020/attempts/full-split-001"
export K="$W/census_05_20261020/code/997b7d2ab5a8775b"
export CENSUS_PROJECTS="$K/docs/harvest/census05/package/projects"
export CENSUS_CODE="$CENSUS_PROJECTS/greek-ocr-toolkit-pipe032"
export PROJECTS_SUMS="$B/census05_DEPLOY_SHA256SUMS"
export PROJECTS_SUMS_ROOT="$K"
export PROJECTS_SHA256=997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb
export PYTHON="$W/venv_l1/bin/python"
export TRANCHE=W2
export INCLUDE_HELDOUT=1
export CROPS4_PACKAGE="$B/crops4.sbatch"
export PYTHONPATH="$CENSUS_CODE"
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PYTHONDONTWRITEBYTECODE=1
# Pre-submit light checks only.
sha256sum "$PROJECTS_SUMS"
[[ "$(sha256sum "$PROJECTS_SUMS" | cut -d' ' -f1)" == "$PROJECTS_SHA256" ]]
(cd "$K" && sha256sum --check --quiet "$PROJECTS_SUMS")
MODULE_REL="$("$PYTHON" -B -c 'import os,sys; print(os.path.relpath(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])))' "$PYTHONPATH/greekocr/harvest/line_pipeline_native.py" "$PROJECTS_SUMS_ROOT")"; awk -v path="$MODULE_REL" 'substr($0,67)==path {found=1} END {exit !found}' "$PROJECTS_SUMS" || { echo "reconstruction module not in PROJECTS_SUMS: $MODULE_REL" >&2; exit 1; }

export MODE=smoke ATTEMPT=crops4_c05_smoke_01
mkdir -p "$W/crops4_attempts/$ATTEMPT"
SMOKE_JOB=$(sbatch --parsable --export=ALL --time=00:45:00 --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$CROPS4_PACKAGE")
SMOKE_JOB=${SMOKE_JOB%%;*}
export SMOKE_JOB
printf 'SMOKE_JOB=%s\n' "$SMOKE_JOB"
```

After smoke completes successfully, in the same shell:

```bash
"$PYTHON" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["status"]=="ok" and r["selected"]==r["byte_exact"]==500; print("SMOKE_OK 500/500")' "$W/crops4_attempts/crops4_c05_smoke_01/upload_receipt.json"
export MODE=full ATTEMPT=crops4_c05_full_01
export SMOKE_RECEIPT="$W/crops4_attempts/crops4_c05_smoke_01/upload_receipt.json"
mkdir -p "$W/crops4_attempts/$ATTEMPT"
sbatch --export=ALL --dependency="afterok:${SMOKE_JOB:?recorded smoke job ID}" --time=01:30:00 --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$CROPS4_PACKAGE"
```

Time limits: CROPS3's 9.3 s/1,000 crops implies about 34 minutes for 219,381 W2 crops before heldout and I/O overhead; decisions 10.2 GB + admitted_train 7.9 GB + diagnostics 2.5 GB = 20.6 GB are hashed/parsed in both job VERIFY and selection, motivating 45 minutes for smoke and 90 minutes for full.

## Files for the lead to commit (10)

- `docs/harvest/collect_v3_admission/CROPS4B_RECEIPT.md`
- `docs/harvest/collect_v3_admission/crops4/COMMIT_LIST.json`
- `docs/harvest/collect_v3_admission/crops4/COMMIT_LIST.md`
- `docs/harvest/collect_v3_admission/crops4/DEPLOY_PATHS.txt`
- `docs/harvest/collect_v3_admission/crops4/DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/crops4/TESTS.log`
- `docs/harvest/collect_v3_admission/crops4/TEST_RESULTS.json`
- `docs/harvest/collect_v3_admission/crops4/census05_DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/crops4/crops4.sbatch`
- `docs/harvest/collect_v3_admission/crops4/test_crops4.py`

No staging or commit performed. The supplied CROPS4B brief is excluded from this changed-file handoff.

CROPS4B: done | crops4 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/add0b5f8 VERIFY_DEPLOY_OK add0b5f8 | census05 manifest 997b7d2a 167/167 OK | reconstruction e7dbe6c4 import ok | tests 16 passed | no jobs submitted | files to commit 10
