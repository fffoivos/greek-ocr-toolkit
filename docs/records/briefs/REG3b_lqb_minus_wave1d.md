# REG3b: register lqb_truth_v1 minus the 11 wave-1d rows (gpt-6.1-sol, medium, network OFF, mechanical)

**Coordinator ruling after REG3 (blocked; see `docs/records/harvest/collect_v3/release_exclusions/REG3_blocked.json`):**
- Register the LQB truth list **without** the 11 ids that are wave-1d rows (`release_admissions/w1_masked_1d.jsonl`, arm wave-1d).
- Those 11 stay in wave 1d, which is preregistered and already training. The LQB marks them in-sample through its own guard.

## Do
1. Inputs: the REG3 inputs (`~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1_exclusion_ids.txt`, sha recorded in REG3_blocked.json; truth sha d2cdc75c…). Remove exactly the 11 wave-1d ids and verify that the overlap is now 0.
2. Write `release_exclusions/lqb_truth_v1_ids.txt` (1,465 ids expected) and `lqb_truth_v1_wave1d_in_sample_ids.txt` (the 11, for the record; **not** an exclusion).
3. Add class `lqb_truth_v1` to `release_exclusions.json`: n, sha256, owner `secondary-corrections lead (LQB)`, provenance (source file and its sha, truth sha), rule `LQB benchmark truth; never trains; 11 wave-1d rows kept in-sample per coordinator ruling (listed separately)`, plus the id-space counts and overlaps.
4. Tests: count, overlap 0 with wave-1d, JSON validity, and that the source file minus the 11 equals the registered file.

The last line must be exactly:
`REG3b: done | lqb_truth_v1: <n> ids | wave-1d overlap: 0 | in-sample listed: 11 | release_exclusions sha: <sha>`
