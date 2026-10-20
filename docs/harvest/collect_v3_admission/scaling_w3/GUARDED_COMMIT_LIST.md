# Guarded commit list — SCALE1C

Review only these exact paths under `docs/harvest/collect_v3_admission/scaling_w3/`:

- `scale.py`: bound crop resolver, subset census/release join, v_c resolver use, and pinned unchanged-tag-producer receipt compatibility.
- `test_scale.py`: real resolver, forbidden census fallback, binding failure and unchanged tag path tests; synthetic handoff verifies original crop output paths and old receipt compatibility.
- `fixtures/real_release.jsonl`: 40 unmodified REL3 rows matching existing census fixture keys.
- `check_real_crops.py`: repeatable read-only 60-crop resolver/open/hash check on Clariden.
- `REAL_CROP_RESULTS.json`: 60 resolved paths, expected/actual hashes, counts, fixture identities and tag reuse comparison.
- `SCALE1.md`: SCALE1C fix/audit, real-crop counts, receipt reuse, new package and exact coordinator block.
- `GUARDED_COMMIT_LIST.md`: this exact review allowlist.
- `VERIFY.sh`, `submit_tags.sh`, `submit_subsets.sh`, `tags.sbatch`, `subsets.sbatch`: new absolute package root only.
- `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`: regenerated manifests.
- `DEPLOY_READBACK.json`: local-only all-file remote hash comparison, old-root preservation, VERIFY results, deployed tests and crop probe.

Do not stage directories broadly. Preserve all unrelated pre-existing changes and untracked files. Do not include briefs, census05, seal02/, other harvest packages, geometry/row-inclusion code, pyproject.toml, logs or virtualenv. Existing real census fixture, vendor code/counts, inputs, README, benchmark, synthetic throughput and prior sample results remain byte-identical. Temporary fetched producer/receipt files stay outside git. Before any later staging, review `git diff` and exact untracked paths against this allowlist. No git add or git commit was run.
