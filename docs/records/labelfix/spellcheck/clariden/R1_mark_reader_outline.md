# R1 — purpose-built mark reader: Clariden training outline (for the coordinator; not submitted)

Owner GO 16 Oct 2026: a reader trained to name the marks of each letter from pixels. Letter identity and positions come from our
recogniser (cached CTC alignments), never from Google. Google contributes labels only where Google and our recogniser agree.

## Input
- **Per letter, not per line.** One sample = one vowel or ρ position from our recogniser's reading (the CTC character span from the
  cached alignment).
- **What is cropped:** a window of the line crop at full line height (so marks above, beside and below are inside). It runs from
  1.5 line-heights left of the span to 0.75 right of it. The left margin is wide on purpose: marks before a capital sit there.
  Resized to 64 × 128 px grey, plus a second channel that marks the recogniser span, so the network knows which letter is asked.
- **No ink analysis:** no ink.py heuristics, no x-height fit. The window is pure pixels plus the span, so it does not inherit our
  detector's rules, and the SciPy ink stack is not needed on Clariden.
- **Also input:** the recogniser's base letter as a 64-d embedding (identity only, marks stripped; case kept). Arm B drops it.

## Targets
Factorised heads instead of one 22-way softmax, so classes never or barely seen still compose:

| Head | Values |
|---|---|
| Breathing | none / psili / dasia |
| Accent | none / acute / grave / circumflex |
| Dialytika | 0 / 1 |
| Subscript | 0 / 1 |

Scored as the composed class set, as in S2–S5. Elision apostrophe is not a head in R1 (the tokenizer strips it from agreement words);
it stays with the detector.

## Label source (counted 16 Oct from C1 job 3678590)
- **C1 selection:** 91,469 Greek-poly training lines (all 61,469 compound-bearing ones plus 30,000 others), 316 documents.
- **Agreement words:** 729,125, where Google's NFD core equals our recogniser's (case and marks included).
- **Vowel/ρ positions inside them: 2,057,665.** Of these, 817,251 are marked and 1,240,414 unmarked.
- **Class counts:**

  | Class | Count | Class | Count |
  |---|---:|---|---:|
  | acute | 236,466 | psili+acute | 34,343 |
  | grave | 190,865 | dasia+acute | 26,360 |
  | psili | 125,673 | psili+circumflex | 13,537 |
  | circumflex | 107,122 | circumflex+subscript | 7,030 |
  | dasia | 57,759 | psili+grave | 5,085 |
  | subscript | 7,803 | dasia+circumflex | 2,285 |
  | dialytika | 1,293 | dasia+grave | 1,098 |
  | dialytika+acute | 233 | dasia+circumflex+subscript | 218 |

  Under 50 each: acute+subscript, psili+subscript and the three-mark subscript sets.
- **Letter case:** 87,552 capital letters vs 3.61 M lowercase.
- **Filters:**
  - The span must overlap exactly one letter column, judged from the alignment alone. Expected loss is about 5%; the actual count
    comes from the extraction job.
  - Lines whose recogniser confidence is under 0.5 are dropped.
- **Optional extension:** align the other 33,200 Greek-poly lines first (same C1 job, about 2 min on the debug partition) to reach
  about 2.7 M positions. Recommended only if dialytika or the subscript compounds stay under 2k.
- **Known bias:**
  - Our recogniser was trained on Google labels, so Google and the recogniser can share a mistake. Agreement therefore does not mean
    the label is correct.
  - That is why scoring is only against print truth (below), never against agreement.
- **Split by document:** 300 documents train, 16 validation (early stopping only, chosen by seed 20261016). The 14 held-out Wikisource
  books and the 3 DEV books are outside C1 by construction.
- **Sampling:** class-balanced per head with a cap. Compound and rare classes are oversampled to ≥ 5% of each batch; "none" is
  downsampled to 40%.

## Architecture
A small ResNet: 2-channel 64×128 input → 4 stages (32/64/128/192 channels, 2 blocks each) → global average pool. This is
concatenated with the letter embedding, then a 256-unit MLP feeds the 4 heads. About 1.6 M parameters, bf16. The loss is the sum of
per-head cross-entropies, weighted per class.

## Compute (one node, 4 × GH200)

| Step | Work | Wall-clock |
|---|---|---|
| 1. Extract | From the 91,469 E3-staged crops into uint8 shards: 2.06 M × 64×128 ≈ 17 GB on scratch. CPU multiprocessing on the node; no transfer from the Mac. | ~15 min |
| 2. Train 4 arms, one per GPU, 15 epochs each | A = full; B = no letter embedding; C = narrower window (0.75 line-height left); D = natural class frequencies (no balancing). 30 M samples per arm at about 15k samples/s/GPU. | ~35 min/arm, in parallel |
| 3. Score | Best checkpoint per arm on the 666 held-out lines (pre-extracted on the Mac: about 20k positions, inference only). | small |

- **Total:** about 1.25 node-hours ≈ 5 GPU-hours. One normal-partition job, 2 h limit, account a0140. Debug's 1:30 is too tight with
  extraction included.
- **Before submission:**
  1. A CPU mock on 192 crops (extraction + 50 training steps).
  2. A SHA-256 check of the deployed files.
  3. `sbatch --test-only`.

  The coordinator submits.

## Held-out evaluation (unchanged instrument)
- **Lines:** the same 666 held-out lines from 14 books, the same print-truth labels, and the same per-letter scoring as S2–S5. Reader
  outputs map to slots through `reading.recogniser_slots`.
- **The table:** S4's table row for row, plus S5's capital rows (capital detection P/R, naming at capitals).
- **Owner notes:** checked against the reader's line reading. That means all 56 example notes, the 59 earlier slot expectations and
  the 33 review-page notes.

## What "better than S5" means
R1 replaces the detector's mark naming only if ALL of these hold on the 666 lines:

1. Overall mark F1 ≥ S5 + 2.0 points, with precision ≥ S5's.
2. No mark class with ≥ 50 held-out slots loses more than 2 points of precision.
3. Compound recall ≥ S5's, and recall of marks at capitals ≥ S5's.
4. Disagreements with Google: of positions where R1 differs from Google, the share that print truth confirms is ≥ S5's.
5. Owner-note checks met ≥ S5's count.
6. **Implicit-approval changes** (owner rule, 16 Oct 22:50): on the owner's reviewed lines, marks lost + false marks added at
   slots his note does not name, settled by blind pixel adjudication, ≤ the baseline's on the same lines
   (`scripts/labelfix/owner_implicit_changes.py`). All readings pass through `constraints` first; "removed by constraint" is its own line.

Otherwise the reader goes in as a second opinion:

- **Where the reader and the detector agree:** the reading becomes a correction candidate.
- **Where they disagree:** the line goes on HOLD.
- **What gets measured:** how much each mode gains on point 4.
