# E3 results — data-scaling knee and warm-start versus scratch on collection v2 (16 Oct 2026)

Evidence: `out/e3b/report.json` (sha256 `32e93f48…63bf0`), `out/e3b/REPORT.md`, `out/e3g/RESULTS_DIGEST.md`, `out/e3g/verification.json` (298,148 checks, 0 failed; 326 files copied from Clariden, 0 sha mismatches). Reviews: `reviews/ASTRA-E3mix_review_1.md` (gpt-6-astra, mix ↔ results), `reviews/ASTRA-E3dir_review_1.md` (literature + directions). Execution ledger: `E3_EXECUTION_STATE.json`; engineering notes: `E3_NOTES.md` (E3a–E3g).

## Design
Ten arms on Clariden (CSCS a0140, GH200, zero cash): scratch `s025 / s050 / s100 / full` × seeds 0,1 and `full_r01` (PP-OCRv5 donor warm-start, `e2_r01` architecture) × seeds 0,1. Every arm: 8 epochs × 428,872 draws, effective batch 64, AdamW lr 1e-4 wd 0.05, OneCycle, NFD head, codec v1; 50% v5 synthetic / 50% real per epoch. Real half = collection v2 (scanned harvest, Google Document AI labels, v2 anomaly clean-up): 207,851 train rows after codec; parliament capped at 25% of real. R01 arms train at micro-batch 32 × accum 2 (disclosed recipe difference; OOM at 64). Instruments: `v2_test` 42,038 scanned lines from 92 held-out books; `wikisource_human` 1,392 human-transcribed lines (el 1,264 / ru 128); `e1_real_test` 3,600 born-digital lines; `synthetic_heldout` 2,399. Verdict rule: improvement > max seed range of the compared arms.

## Headline (CER, mean of two seeds; seed range in brackets)

| Arm | v2_test | wikisource_human | e1_real_test | synthetic_heldout |
|---|---:|---:|---:|---:|
| s025 | 1.980% [0.062] | 3.802% [0.012] | 1.099% [0.048] | 0.623% [0.033] |
| s050 | 1.723% [0.071] | 3.608% [0.004] | 1.122% [0.022] | 0.633% [0.042] |
| s100 | 1.518% [0.025] | 3.452% [0.153] | 1.095% [0.049] | 0.598% [0.024] |
| full | **1.368% [0.017]** | **3.334% [0.014]** | **1.063% [0.012]** | 0.541% [0.059] |
| full_r01 | 1.656% [0.007] | 3.371% [0.060] | 1.343% [0.049] | 0.540% [0.179] |

Driver verdicts: v2_test s100→full **still improving** (gain 0.150 pp vs threshold 0.025); wikisource_human **knee** under the rule (0.118 vs 0.153, last step unresolved; every earlier step resolved); e1_real_test and synthetic_heldout flat/unresolved (scanned data neither helps nor hurts clean documents — no E1-style collapse). Warm-start: **scratch improves** on v2_test (−0.288 pp) and e1_real_test (−0.280 pp); unresolved on the human and synthetic instruments. Both R01 seeds select epoch 8 (val 1.70% / 1.64% vs scratch 1.40% / 1.39%); R01 costs 6.2× the wall time (29,100 s vs 4,700 s per arm).

Versus the previous models: E1 run 4's best mixture arm scored 1.84% on `e1_real_test` after training on that pool; E3 full scores 1.06% without ever seeing it.

## Where the errors are (full, seed 0, v2_test: 34,278 edits / 2,489,622 atoms)
- **By class:** polytonic 1.58% (78% of edits), monotonic 0.72%, Cyrillic 1.87%, Greek+Latin 1.54%, Latin 1.55%. Every class still improves at every scale step above its seed range.
- **By source:** Vouli 1850s 4.31%, Anemi dictionaries/journals 2.88%, Anemi round 1 1.53%, round 2 1.52%, Wikisource scans 1.26%, parliament 1.12%, Open Archives 0.31%.
- **By line type:** all-caps 4.12%, punctuation-heavy 3.25%, dotted leaders 2.97%, numerics 2.71%, mixed-script 1.64%, long 1.52%, hyphenated 1.00%.
- **By mark (mark error per occurrence):** dialytika 15.2% (834), iota subscript 13.6% (4,966), rough breathing 7.7%, perispomeni 4.6%, smooth breathing 4.6%, grave 4.2%. On the human set iota subscript **worsened** from s100 to full (13.8/14.4 → 15.5/16.6%) while improving on Google-labelled lines — a label-source effect to test (ASTRA-E3mix §3c/3f).
- **Crop/label mismatch (post-hoc, coordinator recount):** 1,188 lines (2.8%) whose prediction length differs from the label by ≥3 NFD atoms carry **15,011 edits = 44% of all edits**; 10% of Vouli and dictionary-wave lines are such cases. The Opus residual analysis (16 Oct) attributes ≈30% of all edits to labels that are fragments of, or extend beyond, the cropped line. The two worst sources are therefore largely a line-cutting problem, not a print problem. Fixing labels alone bounds v2_test CER near 1.0%.
- **Geometry-clean instrument (16 Oct, detector-based audit, 4,372 test lines excluded):** full CER 0.854% / 0.839% (seeds 0/1) vs 1.377% / 1.360% on all lines; Vouli 1.81%, mixed 1.39%, parliament 0.64%, round1 1.09%, round2 0.75%. The audit is not model-based; both instruments are reported from here on.
- **Script confusion** is rare (≈120 cross-script swaps in 62k mixed-script atoms).

## Correction (16 Oct, 21:10): wave-4 "openarchives" metadata
The sourcing lead's O1 audit (greek-ocr-toolkit sol/source-inventory c22d7a78, docs/harvest/oa_rebind_v1/FINDING.md) found that all 89 Open Archives books carry wrong catalogue metadata (titles, collections and dates paired wrongly in the 15 Oct shard cache); images, labels, ids, crops and splits are untouched, zero lines change. Corrected dates: 1 book from the 1960s, 7 from the 2000s, 62 from the 2010s, 19 from the 2020s. So the "openarchives" slices above (0.31% CER; 4,680 test lines; 19,625 train rows) are 2000–2020 scanned documents, not historical modern print, and parliament 1975–2000 is the collection's only pre-2000 modern scanned source. Source caps were exceeded (Pergamos 18, Hellanicus 17, IHU 13 books against a cap of 10). The scaling and warm-start verdicts are unaffected; period and source-balance readings must use the corrected metadata.

## Confounds (from ASTRA-E3mix, accepted)
Two seeds only; the s100→full step changes parliament weighting (≈31% → 25% of real) so it is scale + reweighting; R01 differs in architecture, micro-batching and a frame-repeat time-axis adapter, so the warm-start verdict is on the package, not on initialisation; real labels are silver (Google); 8.1% of real draws per epoch are repeats; Cyrillic scope excludes codec-rejected pre-reform letters; v2_test shares source domains with training though no book; custody: jobA/jobB readouts ran after a recorded source rebind (commit c9af062), jobC none.

## Decisions taken
1. Scratch compact + NFD + 50% synthetic remains the reference; R01 is not a production candidate.
2. Scanned-data scaling continues: no knee on the primary instrument.
3. Next experiments (one variable each, three seeds, fresh control): label-only correction (2,000 lines), codec v2 A/B/C, 10% born-digital replay — per `reviews/ASTRA-E3dir_review_1.md` §3 — plus the line-cutting repair that the residual analysis puts first. The data plan and training directions are in `DATA_PLAN_v2_20261016.md` and `TRAINING_DIRECTIONS_20261016.md`.

## Cost
16.0 GH200 node-hours on a0140 (jobC 10.0, scratch waves 4.1, prepare/rehearsals/probe 0.7, finish 0.2, aggregate 0.8). Cash: none. The abandoned Prime Intellect pod of 15 Oct (≈ USD 175) produced nothing used here.
