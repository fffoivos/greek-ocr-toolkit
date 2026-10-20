# CROPS4C receipt

Prepared and deployed 2026-10-20. Base: CROPS4B commit `fafbaca7c3ee1cc73f78e065eb2e74244447a644`, deployed `add0b5f8`. No jobs submitted, no spend, no staging or commit. Network was restricted to read-only `ssh clariden` and the final deployment `rsync`. Nothing was run against census_06. The final census_06 id/manifest remain pending after sf7 binding.

New root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/9a3b80c1`.

Deploy identity (SHA256 of DEPLOY_SHA256SUMS bytes): `9a3b80c149ed689d08f88cdbdb0f00f561d58ed51b7008f144ecea85feb5e9a1`. Eleven deployed files, including the manifest itself, were hashed remotely and compared to the local payload. The payload was copied into an immutable temporary directory, absence of the destination was checked read-only, and `rsync -a --ignore-existing /tmp/crops4c-deploy/9a3b80c1/ clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/9a3b80c1/` returned 0. No older package roots were modified.

## Diff versus CROPS4B

- Reuse `PROJECTS_SUMS` with submit-time alias `CENSUS_MANIFEST`; no census06 manifest is packaged. Check its full `PROJECTS_SHA256`, and for the submit-time alias check that `PROJECTS_SUMS_ROOT`'s basename equals the first 16 hex digits. Retain complete checksum validation and module-in-manifest membership. These existing checks plus the requested new assertions are shared in `binding_checks.sh`, sourced before either job step and by the coordinator.
- Assert the imported native module's SHA through `RECONSTRUCTION_SHA256`, default `e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7`. Keep the existing code-tree import boundary. No new admission/materialisation gates.
- **materialise_crops.py changed:** a red test proved the receipt lacked per-tranche counts (`KeyError: per_tranche`, retained in `crops4/TEST_RED_PER_TRANCHE.log`). Added only per-tranche accumulation and receipt serialization (five added lines and one changed receipt line). Selection, smoke gate, reconstruction, byte checks, exclusive publication, failure exit, and skip/mismatch policy are unchanged. New SHA: `710213d0e53cb1bb077b09c065ac2978a3635a1997213f0dca232f2ce5cbfeb4`; base SHA `1484848073febf529472e89a7621afd02d1da2678476fbd07404ad336c9c0e73`.
- Batch default becomes 90 minutes, with 45-minute smoke override in the coordinator block. Added `VERIFY.sh --deploy-only` for the requested light login-node verification; ordinary VERIFY behavior is retained.
- Retained byte-identical `census05_DEPLOY_SHA256SUMS`: `997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb`. Updated docs, tests, manifests, logs and guarded handoff list.

## Validation

`~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/harvest/collect_v3_admission/crops4/test_crops4.py` exited 0: **23 tests passed**. All original 16 pass. Seven added tests cover census06-layout unpinned manifest input with 500/500 smoke and rejection of an old census05 smoke; manifest SHA mismatch; code-directory mismatch; default production reconstruction SHA rejection for the distinct mock module before VERIFY/materialisation; TRANCHE=all existing/new and repeat counts per tranche; a mismatching pre-existing file preserved with nonzero wrapper exit and failed receipt; deploy-only verification without census inputs.

In the all-tranche fixture, 502 pre-existing byte-identical crops are skipped and two new crops are written (one W1, one W2); a repeat skips all 504. Bytes, inode and modification time of every pre-existing crop remain equal. The mismatch test preserves all three for the conflict file. Local scheduler execution uses only the existing srun stub. Production default is never changed for mocks; they explicitly supply their different native SHA. TEST_RESULTS records the actual resolved interpreter and independent 20/500-binding samples; the 500-row gate itself includes 480 named aliases. `bash -n` passed for all three shell files; `git diff --check` and the final commit guard passed.

## Remote VERIFY and census05 regression

The first light check was accidentally started while rsync was in flight and failed on missing files; it made no writes. Its output is preserved in `crops4/REMOTE_VERIFY_INCOMPLETE.log`. After rsync exited 0, the final read-only check below exited 0. Full final stdout/stderr (including all 167 census05 checks) is in `crops4/REMOTE_VERIFY.log`. No census input parsing or full materialisation VERIFY was run on the login node.

```bash
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B="$W/crops4_package/9a3b80c1"
export PYTHON="$W/venv_l1/bin/python"
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PYTHONDONTWRITEBYTECODE=1
bash "$B/VERIFY.sh" --deploy-only
export K="$W/census_05_20261020/code/997b7d2ab5a8775b"
export CENSUS_PROJECTS="$K/docs/harvest/census05/package/projects"
export CENSUS_CODE="$CENSUS_PROJECTS/greek-ocr-toolkit-pipe032"
export PROJECTS_SUMS="$B/census05_DEPLOY_SHA256SUMS"
export PROJECTS_SUMS_ROOT="$K"
export PROJECTS_SHA256=997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb
unset CENSUS_MANIFEST RECONSTRUCTION_SHA256
source "$B/binding_checks.sh"
echo 'CENSUS05_REGRESSION_OK 167/167 BINDING_GUARD_OK reconstruction e7dbe6c4'
cd "$B"
while IFS= read -r name; do
  case "$name" in ''|'#'*) continue;; esac
  sha256sum "$name"
done < DEPLOY_PATHS.txt
```

Final output (package checks, success markers and every deployed SHA; the 167 repetitive census05 `: OK` lines are omitted here and retained in the log):

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
binding_checks.sh: OK
PYTHON 3.12.15
PIL 12.3.0
VERIFY_DEPLOY_OK crops4 9a3b80c1
RECONSTRUCTION_OK e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7
CENSUS05_REGRESSION_OK 167/167 BINDING_GUARD_OK reconstruction e7dbe6c4
710213d0e53cb1bb077b09c065ac2978a3635a1997213f0dca232f2ce5cbfeb4  materialise_crops.py
d89da77575b141db8e528ecda45b6eac2c9498f5f84a52cdb8020198467fd52a  crops4.sbatch
fdc15f7e6b24df89849ee59b35522ee879e34b129ea275c91697a602e418fc2a  VERIFY.sh
44ef32eef308da22c8f19708e1e36bd22b7ee03bf0104a9cadfd26c5ce2ffe16  CROPS4.md
dc349c97bd688229868d5f219ecec3246c3c99cea1cfe484d43131034d1c1996  test_crops4.py
ad72a2e6b9e761fcec1e52e1769757c59d77d7d49c5a7097d971d60ff9f588e7  TESTS.log
ff30a2423f2a576b4ac3a9446c6d33a122ab883d7c2033b645b25fc3c5ba6bf4  TEST_RESULTS.json
7406551f44312caf5a0ad70639c5cec0018546e1d2c2c22aa813091e74dde771  DEPLOY_PATHS.txt
9a3b80c149ed689d08f88cdbdb0f00f561d58ed51b7008f144ecea85feb5e9a1  DEPLOY_SHA256SUMS
997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb  census05_DEPLOY_SHA256SUMS
b70cb4a0bca977ba324b740f9b99a7837f0389da5a7e9f6a685246f20d19abfb  binding_checks.sh
```

The census05 regression used the CROPS4B env block with only B changed to the new root, CENSUS_MANIFEST unset, and the pinned reconstruction default. All 167 checks, module membership, and imported SHA passed. The original checksum/path defaults remain available. No census05 attempt/output tree was written.

## Exact coordinator block (documentation only; not executed)

Run only after the census06 readout and final sf7-bound deployment. Replace the two explicit placeholders; do not use the pre-binding code id. The manifest supplies the exact repository-relative component path, so the block does not guess its census package-directory spelling. Existing full outputs remain `$W/collection_w{1,2}_originals/<source>/<row_id>.png`.

```bash
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export B="$W/crops4_package/9a3b80c1"
export CENSUS_ATTEMPT="$W/census_06_20261020/attempts/full-split-002"
# Replace both placeholders from the FINAL sf7-bound census06 deployment/readout.
export K="$W/census_06_20261020/code/<PENDING: census_06 code id>"
export CENSUS_MANIFEST="$K/DEPLOY_SHA256SUMS"
export PROJECTS_SHA256='<PENDING: manifest sha>'
export PROJECTS_SUMS="$CENSUS_MANIFEST" PROJECTS_SUMS_ROOT="$K"
# Derive the exact component path from the final manifest; keep the pipe032 component prefix.
MODULE_REL=$(awk '$2 ~ /\/package\/projects\/greek-ocr-toolkit-pipe032\/greekocr\/harvest\/line_pipeline_native\.py$/ {print $2}' "$CENSUS_MANIFEST")
export CENSUS_CODE="$K/${MODULE_REL%/greekocr/harvest/line_pipeline_native.py}"
export CENSUS_PROJECTS="$(dirname "$CENSUS_CODE")"
export PYTHON="$W/venv_l1/bin/python"
export PYTHONPATH="$CENSUS_CODE"
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export RECONSTRUCTION_SHA256=e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export CROPS4_PACKAGE="$B/crops4.sbatch"
export TRANCHE=W2 INCLUDE_HELDOUT=1
# Light pre-submit checks: no census selection/parsing on login node.
bash "$B/VERIFY.sh" --deploy-only
source "$B/binding_checks.sh"
# The sourced checks authenticate the manifest SHA, code-dir id, every manifest
# file, module membership and imported reconstruction SHA. Job repeats them.
export MODE=smoke ATTEMPT=crops4_c06_smoke_01
mkdir -p "$W/crops4_attempts/$ATTEMPT"
SMOKE_JOB=$(sbatch --parsable --export=ALL --time=00:45:00 \
  --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$CROPS4_PACKAGE")
SMOKE_JOB=${SMOKE_JOB%%;*}
export SMOKE_JOB
printf 'SMOKE_JOB=%s\n' "$SMOKE_JOB"
```

```bash
# After the recorded smoke has completed successfully, in the same shell:
export SMOKE_RECEIPT="$W/crops4_attempts/crops4_c06_smoke_01/upload_receipt.json"
"$PYTHON" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["status"]=="ok" and r["selected"]==r["byte_exact"]==500; print("SMOKE_OK 500/500")' "$SMOKE_RECEIPT"
export MODE=full ATTEMPT=crops4_c06_full_01 TRANCHE=all INCLUDE_HELDOUT=1
mkdir -p "$W/crops4_attempts/$ATTEMPT"
sbatch --export=ALL --dependency="afterok:${SMOKE_JOB:?recorded smoke job ID}" \
  --time=01:30:00 --output="$W/crops4_attempts/$ATTEMPT/slurm-%j.log" "$CROPS4_PACKAGE"
```

The dependency is `afterok:<smoke>` through the captured numeric SMOKE_JOB. Smoke and full both bind `census_06_20261020/attempts/full-split-002`, the same final code manifest, native SHA and heldout scope. The unchanged full gate verifies complete smoke provenance, selection and all 500 smoke files; only tranche changes from W2 to all. Any mismatch preserves the existing file, makes status failed and exits nonzero. Review failed receipts/logs; do not overwrite/delete conflicts.

## Time limits and expected skip ratio

Read-only sources: `sacct -j 3704831,3704856 --format=JobID,State,Elapsed,Timelimit -n -P`, plus `$W/crops4_attempts/crops4_c05_{full_01,w1_full_01}/upload_receipt.json` and their `slurm-3704831.log` / `slurm-3704856.log` (both log tails empty). Both jobs were COMPLETED with 90-minute limits.

| Prior job | Elapsed | VERIFY step | Materialise step | Receipt seconds | selected | written | skipped_valid |
|---|---:|---:|---:|---:|---:|---:|---:|
| W2 3704831 | 24:13 | 06:47 | 17:19 | 1038.521 | 139488 | 139488 | 0 |
| W1 3704856 | 20:36 | 06:00 | 14:27 | 866.124 | 68779 | 42518 | 26261 |

Elapsed arithmetic: 1453 + 1236 = **2689s = 44m49s**. Receipt materialisation arithmetic: 1038.521 + 866.124 = **1904.645s = 31m44.645s**. VERIFY steps total 407 + 360 = **767s = 12m47s**. One all-tranche job can share input selection work, but will still read source pages, existing crop hashes, and the final checksum pass; skipped crops do not make it free.

There are **208267** prior byte-exact selected crops (139488 + 68779), including those W1 already skipped. Conditional on those admissions being retained and the files remaining identical, expected census06 skip fraction is **208267 / N06**, with N06 pending. Using the supplied W1+W2 all-row inventory only as a conservative ceiling, 219381 + 101098 = 320479, gives **64.99%–100% skipped**, and at most 112212 new rows; this is an estimate, not a census06 measured result. Exact skip counts come from the new per-tranche receipt.

Full limit **90m** rounds above 2 × 44m49s = **89m38s** (2.008× the measured combined elapsed), covering extra admissions/I/O; it does not assume the conditional skip saving. A simple all-row scaling is 44m49s × 320479/208267 ≈ 68m58s, also below 90m, but is not a throughput guarantee. Smoke limit **45m** has ample headroom over the prior 6–7-minute VERIFY steps plus 500 materialisations; the large admitted/heldout input parsing still occurs. No timings or skip rate were measured against census06.

## REL4 binding handoff

After full succeeds, REL4 must pin paths and full SHA256s of the new package DEPLOY_SHA256SUMS, final census06 DEPLOY_SHA256SUMS (PROJECTS_SHA256 + code id), census06 CURRENT.json and its immutable generation/summary, and `crops4_c06_full_01/upload_receipt.json`, `crops_manifest.jsonl`, `crops_sha256.txt`, `sha256check.log` and the matching smoke receipt. Keep `prepared-check.log` as evidence of manifest/module checks. The final census manifest hash is checked by the wrapper and retained via these deployment bindings/logs; it is not a newly invented field in materialiser context.

Require receipt status=ok, mode=full, context.tranche=all, context.include_heldout=true, output_base=W, sha256check_exit=0, mismatches=failures=0, byte_exact=selected=written+skipped_valid; reconcile per_tranche W1/W2 selected/written/skipped_valid/mismatches/failures/bytes with aggregates. Bind selection_sha256, train_selected, heldout_selected and the row identities/relative paths/expected crop hashes in the manifest and checksums. Context must bind census_code, code_sha256, reconstruction_module/function/file/SHA (e7dbe6c4…), interpreter/path/SHA, codec/path/SHA, and `inputs` hashes for CURRENT, summary, admitted_train, decisions and evaluation_diagnostics to census06. REL4 must enforce its own byte-exact checks for every crop it releases, including newly admitted rows; older census05 receipts do not replace this receipt.

## Guarded commit handoff

`crops4/COMMIT_LIST.json` binds the exact files under crops4 plus this receipt and `docs/briefs/CROPS4C_bind_census06.md`; `crops4/COMMIT_LIST.md` lists them. Run the guard immediately before staging. No git add or git commit was run. Other worktree changes, release_v4, census06 and older remote roots were left untouched.

CROPS4C: done | crops4 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/crops4_package/9a3b80c1 VERIFY_DEPLOY_OK 9a3b80c1 | census_06 manifest submit-time bound (pending id) | reconstruction e7dbe6c4 pinned | TRANCHE all skip-existing tested | census_05 path regression ok | tests 23 passed | no jobs submitted
