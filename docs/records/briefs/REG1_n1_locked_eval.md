# REG1: register the N1 locked-eval lines as a release-exclusion class (gpt-6.1-sol, medium, network OFF, mechanical)

Write only under `docs/records/harvest/collect_v3/release_exclusions/`. A live W2 imports `collect_v3/`: never touch it.

**Input** (read-only), from the secondary-corrections lead:
- file `~/Projects/greek-ocr-toolkit-secondary/artifacts/n1/n1_locked_eval_line_ids_alt.txt` (branch opus/secondary-corrections b85a40e7c);
- expected sha256 `3d6f0d29edf728514f0721ded09b9f3df65cbe352f70814e8bcbe49f51c430fe`;
- 258 W1 ids: elstat 88, gazette 1982–85 78, gazette 1986–90 92;
- receipt `artifacts/n1/N1L_RECEIPT.json`.

## Do
1. **Verify the sha256** (stop on mismatch). Check that every id exists in `~/Projects/collect-v3-data/run/W1/features.jsonl` (read-only), and that the per-source counts match.
2. **Overlap checks**, reported in the class entry; none of them may be nonzero except as noted:
   - `release_admissions/w1_masked_1d.jsonl`, arm wave-1d: **must be 0, else STOP**;
   - arm release-v3-candidate: report;
   - existing exclusion classes: report. 6 rotated_crop overlaps are expected and harmless.
   - W2 rows, if `run/W2/features.jsonl` exists: report.
3. **Register:**
   - copy the file to `release_exclusions/n1_locked_eval_ids.txt` byte-identically;
   - add class `n1_locked_eval` to `release_exclusions.json`: file, n, sha256, owner `secondary-corrections lead (N1)`, provenance (branch, commit, receipt path), rule `locked evaluation lines (62 reserved documents); never admitted to training`, and the overlap results.
   - **Do not** modify `release_admissions/*` or the stratum gate. Note in the class entry that `w1_masked_1d_summary.json` binds the previous release_exclusions sha, and that the wave-1d overlap is 0.
4. **Tests:** sha, id existence, the overlap computation, and JSON validity.

The last line must be exactly:
`REG1: done | n1_locked_eval: 258 ids | wave-1d overlap: 0 | release_exclusions sha: <sha>`
