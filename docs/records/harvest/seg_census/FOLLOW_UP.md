# Follow-up deployment verification and coordinator submission commands

Prepared only. None of the commands below ran in SEGCENSUS-1c. The lead must first commit both reviewed path lists. A separate brief authorizes the new remote copy and verification; submission remains coordinator-controlled.

## Read-only verifier after the follow-up deploy

The remote copy must preserve repository-relative paths under the new root, including the four gitignored snapshot cache files. Use `DEPLOY_PATHS.txt` as a files-from inventory, with the same repository-relative layout. The package ID is `bb1ea164338b3068` (SHA256 prefix of DEPLOY_SHA256SUMS, not a Git commit).

Run locally **after** the lead commits and a follow-up deploys:

```bash
REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
COMMIT=$(git -C "$REPO" rev-parse HEAD)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
REMOTE="$W/filter_pipeline_20261018/code/bb1ea164338b3068"
BUNDLE_REL=docs/records/harvest/seg_census
BUNDLE="$REMOTE/$BUNDLE_REL"
allow=()
while IFS= read -r path; do allow+=(--allow-untracked "$path"); done < "$REPO/$BUNDLE_REL/verifier_allow_untracked.txt"
for kind in regression parity census; do
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B \
    "$REPO/../greek-page-ocr-wave2/scripts/ops/verify_deploy.py" \
    --repo "$REPO" --commit "$COMMIT" \
    --sha-file "$BUNDLE_REL/DEPLOY_SHA256SUMS" --remote-root "$REMOTE" \
    --sbatch "$BUNDLE_REL/jobs/$kind.sbatch" \
    --sbatch-args="--export=ALL,W=$W,CENSUS04_BUNDLE=$BUNDLE,E4_SMOKE=1,CENSUS04_ATTEMPT=verify-mode-i" \
    "${allow[@]}" --out "/private/tmp/segcensus04-verify-$kind.json"
done
```

This is the exact read-only wave2 verifier; it checks committed bytes, dirty tracked files, per-file remote SHA256 and `sbatch --test-only`. Do not weaken it. Each kind must return a real `VERIFY_OK` in the follow-up. The present receipt is **NOT_DEPLOYED / NOT_VERIFIED**, with no remote SHA table or test-only result claimed. The manifest contains the expected SHA table for all deploy files.

For mode ii test-only verification later, append `,CENSUS04_SPLIT_FILE=/absolute/finalized-split.jsonl.gz,CENSUS04_SPLIT_SHA256=<actual-sha256>` to `--export`; pin real values from the finalized owner-approved sourcing input. No proposal file is selected by default.

## Coordinator commands on Clariden after verified deployment

The following shell setup and function are literal command definitions, **not executed here**. The output parent/log directory must exist before Slurm opens its logs; this future mkdir is confined to the new census_04 root.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS04_BUNDLE="$W/filter_pipeline_20261018/code/bb1ea164338b3068/docs/harvest/seg_census"
RUN_ROOT="$W/filter_pipeline_20261018/census_04_seg08"
mkdir -p "$RUN_ROOT/logs"
submit_census04() {
  local regression parity
  regression=$(sbatch --parsable --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS04_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS04_BUNDLE/jobs/parity.sbatch")
  sbatch --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS04_BUNDLE/jobs/census.sbatch"
}

# Mode (i): no split input pinned. Smoke first; inspect its publication before full.
unset CENSUS04_SPLIT_FILE CENSUS04_SPLIT_SHA256 CENSUS04_CONFIG
export E4_SMOKE=1 CENSUS04_ATTEMPT=smoke-mode-i-001
submit_census04
# Separate coordinator action only after successful smoke review:
export E4_SMOKE=0 CENSUS04_ATTEMPT=full-mode-i-001
submit_census04

# Mode (ii), LATER, after the owner-approved finalized split file exists:
# Set these two variables to the actual absolute path and compressed-file hash.
: "${CENSUS04_SPLIT_FILE:?set finalized split path}"
: "${CENSUS04_SPLIT_SHA256:?set finalized split SHA256}"
export CENSUS04_SPLIT_FILE CENSUS04_SPLIT_SHA256
export E4_SMOKE=1 CENSUS04_ATTEMPT=smoke-mode-ii-001
submit_census04
# Separate coordinator action only after successful mode-ii smoke review:
export E4_SMOKE=0 CENSUS04_ATTEMPT=full-mode-ii-001
submit_census04
```

Use a new attempt suffix for a changed input binding. The immutable census_03 inputs and output remain untouched. Split assignment supplies input identity; all ordinary segmentation, correction, eligibility and leakage checks still apply. A pinned train assignment does not guarantee admission, and dev/test rows retain evaluation diagnostics.
