set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
REL=docs/harvest/census05
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
REMOTE=$W/census_05_20261020/code/17b0eb1ca7fe81a7
BUNDLE=$REMOTE/$REL
COMMIT=$(git -C "$REPO" rev-parse HEAD)
for kind in regression parity census readout; do
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B \
    "$REPO/../greek-page-ocr-wave2/scripts/ops/verify_deploy.py" \
    --repo "$REPO" --commit "$COMMIT" \
    --sha-file "$REL/DEPLOY_SHA256SUMS" --remote-root "$REMOTE" \
    --sbatch "$REL/jobs/$kind.sbatch" \
    --sbatch-args="--export=ALL,W=$W,CENSUS05_BUNDLE=$BUNDLE,E4_SMOKE=1,CENSUS05_ATTEMPT=verify-smoke,CENSUS05_EXPECT_ROWS=200" \
    --out "$REPO/$REL/verify-$kind.json"
done
