# L1 — Corrected labels at scale: Clariden outline (for the coordinator; not submitted)

## Goal
Produce label OVERLAYS for every polytonic training line of collection v2, from our combined accent checker, for wave 1c. Original
labels stay untouched. The overlays come in two variants:
- **PRESENCE:** a change is accepted when the detector and R1 agree on which mark kinds are present; names come from R1.
- **FULL:** a change is accepted only when the mark sets are identical.

Owner rules:
- Transcribe what is printed; a correction is accepted only when two pixel signals agree.
- HOLD never enters labels.

## Input
- The `greek_poly` rows of `docs/records/harvest/collection/v2/import_real_v2_train.jsonl`: 124,669 lines.
  - 91,469 are already aligned (C1 job 3678590).
  - 33,200 need the same C1 alignment job first (debug partition, about 2 min, unchanged scripts, a new selection file).
- Excluded and verified as receipt counts (intersection must be 0):
  - the 666 held-out lines, the 3 DEV books and all 27 non-DEV Wikisource books;
  - v2_test, wikisource_human, e1_real_test;
  - the locked fresh-book set from R0, once drawn.
- Monotonic lines are out of scope. M2 showed the polytonic checker turns modern accents into breathings. Lines are excluded by script class, with the S7 pixel rule when S7 is accepted; the count is reported.

## System (frozen and hash-bound; detector version decided at submission)
1. Recogniser letters and CTC spans: E3 `full_s0`, from the C1 alignments.
2. Detector, which supplies presence, segmentation, apostrophes and quotes. The version is the best one qualified at submission: S6 (SF1 state) now, S7 if it passes its qualification against S6. CPU; there is no GPU path.
3. Mark names: R1-A (`output_3678928/A/best.pt`, sha 719a06…). GPU inference on R1's font-size windows, the same extraction code as the R1 job.
4. Constraint check: K1 runs print-preserving. An impossible-by-rule mark is FLAGGED and its slot goes to HOLD; nothing is ever deleted.
5. Both agreement variants are computed per line in one pass.

## Output (per variant, keyed by line_id)
`overlay_<variant>.jsonl.gz`, one row per input line:
- `line_id`;
- `original_label_sha256`;
- `status`: `corrected`, `unchanged`, `hold` or `out_of_scope`;
- `label`: the corrected label (equals the original when unchanged; absent for hold or out of scope);
- `changes`: a list of `{start, letter, from, to, evidence}`;
- `hold_slots`: a list of `{start, letter, reason: kind_disagreement | k1_flag | localisation_unknown | recogniser_letter_problem}`;
- `detector_version`, `r1_sha`, `policy_sha`.

Plus `release_<variant>.json`, the data-release manifest the E4 driver binds:
- release name: `v2-corrected-presence` or `v2-corrected-full`;
- the overlay sha256 and the source label-file sha256;
- counts by status and per source wave;
- exclusion receipts and the code commit.

**HOLD lines are dropped from the corrected release.** Because the release is smaller than ctrl, wave 1c needs a **ctrl-subset arm** (the same kept lines with their ORIGINAL labels) as well as ctrl and the corrected arms. Without it, label quality and data size are confounded.

## Compute (one node; recommend the debug partition, 1 h limit, account a0140)

| Step | Work | Estimate |
|---|---|---|
| Alignment | The remaining 33,200 lines, as the C1 job does | about 1 min of GPU |
| Detector | 124,669 lines on CPU. Mac rate from M2 is about 0.11 s/line including recognition, so the detector alone is under 0.1 s/line. 64 worker processes on the node's CPUs | about 4 min |
| R1 inference | About 2.8 M vowel/ρ windows: extraction about 10–15 min (as in the R1 job), inference at more than 30k samples/s on one GPU | about 2 min |
| Composition | Composition, both variants, receipts | a few min |
| Total | | about 25–35 min wall; under 1 node-hour |

Before submission:
1. A CPU mock on 192 lines with the exact entry points. Its output must equal the local combined reading on the held-out instrument lines.
2. A sha256 deploy list.
3. `sbatch --test-only`.

## Expected yield (measured, not assumed)

| Measurement | PRESENCE | FULL |
|---|---|---|
| Held-out Wikisource: lines held | 7.5% | 36.5% |
| Held-out Wikisource: Google mark errors corrected | 48/80 | 43/80 |
| Held-out Wikisource: new errors | 5 | 3 |
| New sources (M2, S6 detector): lines held | 77.6% | 80.3% |
| New sources (M2, S6 detector): Google mark errors corrected | 25/77 | 24/77 |

With the S6 detector the corrected release would keep few new-source lines. **Recommendation:** submit L1 only after S7's qualification. If S7 brings the M2 hold rate down, L1 uses it; otherwise L1 runs with S6 and the coverage is stated per source. L1 also reports its own per-source hold rate, so wave 1c can weight or stratify.

## Judged by
Wave 1c, as the coordinator set it: arms ctrl / ctrl-subset / PRESENCE / FULL, 3 seeds each. Judged on the locked fresh-book set from R0, with the 666 held-out lines as the continuity instrument. v2_test stays Google-labelled and is reported, but it does not judge marks.
