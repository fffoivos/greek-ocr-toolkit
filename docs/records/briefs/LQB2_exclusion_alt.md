# LQB2: exclusion list without wave-1d rows (gpt-6.1-sol, medium, network OFF; no .git writes)

The sourcing lead blocked registration of `docs/records/labelfix/lqb/truth_v1_exclusion_ids.txt`: 11 of its ids are preregistered wave-1d rows.
The list is in `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/REG3_blocked.json` (sol/collect-v3
0a75c2e8; read only). That file also reports 12 unmatched ids.

**Lead ruling.** The 11 truth items stay in truth_v1 but carry `in_training: "wave-1d"`. They leave the exclusion list, and the scorer
reports them in the in-sample column for any version trained on wave-1d. Label-version scores are unaffected. truth_v1.jsonl itself
is NOT rewritten; the flag goes into a sidecar `truth_v1_flags.jsonl`, read by the scorer, with tests.

**Do.**
1. Write `docs/records/labelfix/lqb/truth_v1_exclusion_ids_alt.txt` = the original ids minus those 11, and record its sha.
2. Explain the 12 unmatched ids (id space, source set) and list them in the report. Keep them in the alt list only if they are valid
   line ids in some registered id space.
3. Write the sidecar, add scorer support and tests, and add a section "LQB2" to `SCORE_v1.md`.

**Last line:** `LQB2 READY: alt ids <n> sha256 <hex>; removed 11 (1d); unmatched 12 explained (<kept n>/<dropped n>); tests <n> passed`
