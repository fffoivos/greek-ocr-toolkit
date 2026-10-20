REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
COMMIT=$(git -C "$REPO" rev-parse HEAD)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
REMOTE="$W/filter_pipeline_20261018/code/bb1ea164338b3068"
BUNDLE_REL=docs/harvest/seg_census
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
