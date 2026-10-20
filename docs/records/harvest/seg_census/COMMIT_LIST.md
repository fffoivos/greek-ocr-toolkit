# SEGCENSUS-1c exact commit list

Prepared for the lead. No git add/commit/index/ref write was executed. Review and commit (a), then (b), in this same worktree. Each linked pathspec file enumerates every exact path, one per line; no blanket git add or directory glob is used.

## (a) Capture: owner filter pipeline 0.2 source as of 18 Oct

Exact paths: **[capture_paths.txt](capture_paths.txt)** — 150 explicit paths matching capture_inventory.json. Includes geometry_observations.py, row_inclusion.py, pyproject.toml, line_pipeline modules, filtering assets and owner pipeline documentation. Already tracked identical 0.8 files may produce no staged diff. All 150 live destination hashes match the archived capture. The live capture includes 0.8 and has no exact Clariden snapshot match.

Lead commands, **not executed**:

```bash
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
git add --pathspec-from-file=docs/records/harvest/seg_census/capture_paths.txt
git diff --cached --stat
git commit -m "owner filter pipeline 0.2 source as of 18 Oct"
```

## (b) Package, diagnostics, split plumbing, jobs, config, tests and receipts

Exact paths: **[package_paths.txt](package_paths.txt)** — 564 explicit paths. Includes all 334 ordinary deploy payload files, manifests, package ID, schema, resources, follow-up commands, full-suite logs/XML and comparison helper, native/batch mock scripts and compact reproducible inputs, archived capture/diffs/remote evidence, hand-off and receipt. It also names scripts/harvest/filter_runtime/.gitignore. The production package lives under docs/harvest/seg_census/package/projects/; root capture modules remain the owner's source.

Lead commands, **not executed**:

```bash
git add --pathspec-from-file=docs/records/harvest/seg_census/package_paths.txt
git diff --cached --stat
git commit -m "SEGCENSUS-1c: prepare census_04 segmentation 0.8 and split-input plumbing"
```

Excluded: downloaded census03_baseline/, native runtime outputs mock_stage/, and 144 MB batch runtime mock_batch/. Bundle .gitignore records these boundaries; summaries and compact reproducible inputs are in the explicit commit list. The existing untracked root docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl is outside both commit lists. No historical CP5 evidence was copied or added in this run.

## Gitignored untracked payload files: exact verifier exemptions

These four inherited census_03 snapshot cache files are in the preserved 325-file baseline and deploy manifest. They are genuinely gitignored and remain untracked. They **must be copied** and named with --allow-untracked in the follow-up. Do not force-add them or exempt ordinary untracked source.

```text
docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/.pytest_cache/.gitignore
docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/.pytest_cache/CACHEDIR.TAG
docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/.pytest_cache/README.md
docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/.pytest_cache/v/cache/nodeids
```

[verifier_allow_untracked.txt](verifier_allow_untracked.txt) is the exact allow-list, checked with git check-ignore. [DEPLOY_PATHS.txt](DEPLOY_PATHS.txt) lists all **338** copy payload paths, including these four. [DEPLOY_SHA256SUMS](DEPLOY_SHA256SUMS) pins each file. The snapshot caches are inert; native runtime binaries remain separate inputs.

The local replay predictor scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict is a Mac symlink to sol-recut. It is explicitly gitignored, excluded from deployment, and requires **no verifier exemption**. Clariden Node, predictor, codec and Python binaries remain bound by the unchanged runtime manifest, not copied from this Mac.

## Exact follow-up verifier command

Use the unchanged ../greek-page-ocr-wave2/scripts/ops/verify_deploy.py after both lead commits and a separately authorized deploy preserving repository-relative paths under:

`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/bb1ea164338b3068/`

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

[FOLLOW_UP.md](FOLLOW_UP.md) also gives coordinator smoke/full submission command blocks for both split modes. The real finalized owner-approved split is a later dependency; no proposal is pinned. The verifier remains read-only and invokes test-only checks, never submission.

**Current state: no deploy, no VERIFY_OK, no remote per-file readback, no sbatch --test-only, no submission.** Expected SHA table and commit list are ready.
