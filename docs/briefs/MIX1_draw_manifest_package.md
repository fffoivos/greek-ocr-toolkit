# MIX1: the CPU draw-manifest package for the M1–M4 arms of wave 3 (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**Goal:** one deployable CPU package that produces exact per-epoch draw manifests for the arms below. The coordinator submits. The rulings come from the coordinator on 20 Oct (owner may override); implement them as written. **If the data contradicts a ruling, or a ruling is ambiguous in the data, stop on that arm and report; build the others.**

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`. The background is in `docs/harvest/collect_v3_admission/scaling_w3/DATA_NEEDS.md`, artefacts A10–A14 and Q7–Q10.

## Bound inputs (sha-bound; the job hashes the big ones)
- **Real pool:** `ref_364871` from the SCALE1 subsets job 3705111 (attempt `scale1-c05-003`), bound by its `SUBSETS_RECEIPT.json` sha.
  - **The receipt has not landed yet.** Build and test everything else now. Make the subset receipt path + sha a required argument of VERIFY/submit, which reports `pending` until it is given.
  - When it lands, the lead sends a short follow-up to bind it and run the real-sample tests on it.
- **SCALE1 tags:** `$W/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json` (sha `e4a155eb…`).
- **benchmark 0.2 seal04:** `$W/benchmark_0.2/seal04/` (suite `9447f09c…`, receipt `34d024a7…`) for the exposure audit: editions, keys and crop shas of both panels.
- **A10, the E1 born-digital train shards** (19,657 rows, 5 shards, custody R4 in DATA_NEEDS). Replay rows come **only** from the train shards. Assert that the val 359 and the reserved 3,600 test rows are excluded.
- **A12, the synthetic v5 train shards** (190,486 rows, 47 shards, custody R5).
- **The wave-2 control binding:** draw budget **D = 428,872 per epoch**, 8 epochs, synthetic 50%; the same A12 shards. Locate the wave-2 ctrl recipe in greek-page-ocr (branch `sol/e4-wave2` a707a36, `briefs/E4_wave2_scale_brief.md`, and the E3/E4 mix definitions) and bind its sha.
- **The e4prep m1_mix definition** (`briefs/E4_prep_campaign1_brief.md` and its outputs, if they exist), for the M1 matching rule.

## Arms and rulings
- **M1, born-digital replay 10% (Q7).**
  - Replace 10 percentage points of the scanned real half with E1 train rows, matched by **script × length bucket**, where length bucket = `ceil(width/128)·128` as in e4prep m1_mix.
  - Strata with no born-digital support stay scanned. Report per stratum: removed scanned draws, replay draws, unsupported.
  - Synthetic stays 50%.
- **M2, synthetic fraction 40 / 50 / 60 plus curriculum (Q8).**
  - Integer allocation is by **largest remainder per epoch**, with the 8-epoch totals preserved exactly. The 50% arm has **1,715,488** synthetic draws in total.
  - Curriculum: **70% × 4 epochs then 30% × 4 epochs**. Assert that each image's cumulative exposure equals the 50% arm's, within ±1 draw per image.
  - Real pool = ref_364871. Same A12 shards, reweighted, **0 new images**.
- **M3, class reweighting (Q9).**
  - The script quota uses the **census content-gate's per-line dominant script**, not benchmark primary_class. Find that field in the census decision for both W1/W2 and v_c rows and cite it. If it is absent for a parent, stop on M3 and report.
  - Baseline Cyrillic share = the share measured in ref_364871. The target of 6% is reached by **draw repetition**, never by adding rows.
  - The **parliament 25% cap is applied to draws first**, then the other classes are renormalised.
  - Capped and uncapped are **separate manifests**.
- **M4, source temperature (Q10).**
  - Wave = collection parent/round. W1 is one wave and W2 is one wave. v_c rows are grouped by their original collection round from source metadata (anemi_round1, anemi_round2, anemi_mixed, parliament_proceedings_1975_2000, vouli_parliament_1850s, archive_*, openarchives_*, …).
  - **Document the wave table with counts.** Collapse `archive_*` / `openarchives_*` into one group each only if the source metadata gives no round; say which.
  - `p_i ∝ n_i^α` with α ∈ {1, 0.5}. The cap is applied after temperature. Keep a ledger of the post-temperature normalisation.

## Every manifest
- Per epoch: row IDs in order. Use the `[epoch, position, component, physical pool index, line_id]` form of E3/E4 if it fits the trainer; check `train/mix.py` in greek-page-ocr, read-only.
- Unique and repeat counts per component and class.
- An exposure audit against seal04 (edition, key, crop sha) and against the subset receipts.
- A receipt with input/output shas.

## Rule for real-data testing (VERIFY fails without the receipt)
Tonight three jobs failed because packages were tested only on synthetic fixtures. For **every bound file**, run the real code path over **≥ 1,000 real rows, or ≥ 20 per parent**, and re-hash **≥ 20 real crops/images per parent or shard family**: W1, W2, v_c, E1, synthetic v5. Record this in `REAL_SAMPLE_RECEIPT.json`. `VERIFY.sh package` must fail if that receipt is missing or does not cover every bound input. The ref_364871 part is completed in the follow-up.

## Package (sol-recut `docs/harvest/collect_v3_admission/mix1/`)
- Code; `mix1.sbatch` (CPU, normal partition, sized by the arithmetic: 8D = 3,430,976 entries per arm at about 16 B each, roughly 55 MB per arm); `submit_mix1.sh`; `VERIFY.sh` (package / inputs).
- Tests:
  - largest-remainder totals;
  - curriculum per-image exposure;
  - cap-then-renormalise;
  - temperature with cap;
  - unsupported M1 strata;
  - E1 val/test exclusion;
  - each exposure failure;
  - determinism.
- `MIX1.md`: rulings as implemented, wave table, the coordinator block, sizing, what is pending.
- Also list the **owner decisions left open** in `MIX1.md`: C2 target/codec, P1 pool eligibility, S3 needs S2 calibration, G audits. List them; do not decide them.

Deploy to a new `$W/scaling_w3/mix1_pkg/<sha8>/` and read every sha back. Run VERIFY package there, and VERIFY inputs (subset receipt pending).

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `mix1/` and this brief.

The last line must be exactly:
`MIX1: done | arms M1 <ok|stopped> M2 <ok|stopped> M3 <ok|stopped> M4 <ok|stopped> | real-sample receipt <k>/<n> inputs (ref_364871 pending) | package <root> VERIFY package ok | tests <n> passed | no jobs submitted`
