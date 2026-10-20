# REG3: register the LQB truth ids as a release-exclusion class (gpt-6.1-sol, medium, network OFF, mechanical)

Write only under `docs/records/harvest/collect_v3/release_exclusions/`. A live W2 imports `collect_v3/`: never touch it.

## Input (read-only)
- **ids:** `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1_exclusion_ids.txt` (opus/secondary-corrections 0b3834f6a), 1,476 line ids: the LQB truth items flagged exclude_from_training. T2 supervision lines are deliberately not in it.
- **truth file:** `truth_v1.jsonl`, sha256 `d2cdc75c5b0e529c4b7ddd20ea85f778e9da105c3f1cad4afb318d3c438ca34f`.

## Do
1. Record the ids file's sha256 and count (expect 1,476), and the truth file's sha (it must match).
2. Classify each id by id space:
   - W1 collector id (`~/Projects/collect-v3-data/run/W1/features.jsonl`);
   - W2 id (`run/W2/features.jsonl` if present);
   - v2 line id (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`);
   - existing exclusion-class ids.
   Report the counts per space and any unmatched ids. Unmatched ids are still registered, but listed.
3. Overlap: `release_admissions/w1_masked_1d.jsonl` per arm. **If any id is in arm wave-1d: STOP and report** (wave 1d is preregistered). Report the release-v3-candidate overlaps.
4. Register class `lqb_truth_v1`:
   - copy the file byte-identically to `release_exclusions/lqb_truth_v1_ids.txt`;
   - add the class entry: n, sha256, owner `secondary-corrections lead (LQB)`, provenance (branch, commit, truth sha), rule `LQB benchmark truth; never trains`, and the id-space and overlap results.
5. Tests: sha, counts, overlap, JSON validity.

The last line must be exactly:
`REG3: done | lqb_truth_v1: <n> ids (<per space>) | wave-1d overlap: <0|STOP> | release_exclusions sha: <sha>`
