# REG4: register the 60 LQB truth v1.1 ids (gpt-6.1-sol, medium, network OFF, mechanical)

The input is `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1_1_exclusion_ids_new.txt` (opus/secondary-corrections, latest commit; record the commit and the sha256). It holds 60 new ids from truth v1.1 (substitution60). The DEV items are already in eval_only_dev.

## Do (as REG3b)
1. Check the count (60), classify the ids by id space, and check overlap with every existing class (report it) and with `release_admissions/w1_masked_1d.jsonl` per arm.
2. **The standing coordinator ruling applies:** any wave-1d overlap ids are kept in-sample, not excluded. List them in `lqb_truth_v1_1_wave1d_in_sample_ids.txt` and remove them from the registered list.
3. Register class `lqb_truth_v1_1`: file `lqb_truth_v1_1_ids.txt`, n, sha256, owner `secondary-corrections lead (LQB v1.1)`, provenance, and rule `LQB benchmark truth v1.1 additions; never trains`.
4. Tests: count, overlap, JSON validity.

The last line must be exactly:
`REG4: done | lqb_truth_v1_1: <n> ids | wave-1d in-sample: <k> | release_exclusions sha: <sha>`
