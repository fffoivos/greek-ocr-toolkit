# S8a — Training-wave DEV: evidence, baseline and print-truth cards (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-s8`, branch `opus/spellcheck-s8`, head c6064650 = frozen SF4 gate). No
`.git` writes. Do not touch other worktrees (read-only use of `…-spellcheck-l1` files named below is fine). Local Python
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; ≤ 600 lines (+ ≤ 60 audit lines).
**No detector, reader or gate code changes in S8a** (S6/SF4 frozen as the baseline; S8b does the one bounded iteration later). Clariden only
to extract per-line saved evidence for these lines (streamed on the login node, ≤ a few minutes; else STOP). SSH transient errors retry ≤ 3;
auth/cert error STOP; never refresh the cert. No CTC/R1 inference on the Mac beyond what is saved — use saved alignments/predictions.

## Why (coordinator ruling, 17 Oct — direction decision step 3)
The complete gate holds 90% of training lines; after masking (L1M) the remaining driver is detector localisation/segmentation (clip+loc lines:
0/33 released by masking) — decisive for parliament. S8 = detector localisation and segmentation on the training-wave fonts, judged on a
print-adjudicated training-wave DEV: localisation_unknown and segmentation_uncertain rates and presence P/R. S8a builds that DEV.

## Inputs
- DEV ids: `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/S8_DEV/S8_DEV_ids.txt` (600: parliament 150, vouli 150,
  round1/round2/mixed 100 each; receipt beside it; sha256 abb2091211f79bfd…). Copy both into `docs/records/labelfix/spellcheck/S8_DEV/` here.
- Original crops/labels: v2 manifests (`docs/records/harvest/collection/v2/import_real_v2_train.jsonl`) + the harvest crop roots they reference.
- Masked crops for the 450 non-parliament lines: `~/Projects/collect-v3-data/v2_masked/s8_dev/` (sourcing lead; masked crops, ownership
  label maps 0–5, lines.jsonl, receipt). **May not exist yet** — build everything that does not need it; make the masked-detector step a
  one-command rerun (`--masked`) and state "masked pending" if absent. Parliament stays unmasked.
- Recogniser alignments + R1 arm A/B/E predictions for these lines: extract from Clariden (`labelfix_l1_20261017/output_3679313/` alignment +
  combined (A), `l1e_20261017/output_3679545/inference/` (B, E)); L1R sf4 decisions from `l1e_20261017/l1r_sf4_3679725/`.
- Audit lines (coordinator ruling 1): the 14 L1M masking-released corrections — `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/
  spellcheck/L1M_evidence/per_line.csv` (+ its evidence); a vouli seeded sample is added later by the same command (`--audit-add`).

## Do
1. **Baseline (frozen S6/SF4)** on all 600 originals and, where present, the masked crops: per line and per wave, letters, localisation_unknown,
   segmentation_uncertain, clipped_top/bottom, unnamed, components per letter; the frozen-gate ENSEMBLE_AB/PRESENCE outcome.
2. **Print-truth cards (S2 method, as `scripts/labelfix/owner_implicit_adjudication_prep.py` and the R0 card builder `scripts/labelfix/r0_prepare.py`
   do):** per WORD, the distinct mark-bearing forms proposed by any source — Google label, R1 arm A names on the recogniser letters, the
   detector-composed reading on the original crop, on the masked crop, and the frozen-gate AB outcome. A word gets a card when sources
   disagree; plus a seeded 5% sample of all-agree words (to measure the all-agree error), plus ≥ 8% planted controls with known answers.
   Card = word zoom (≤ 3×, no stretching) + full line strip + the candidate forms in random order + "none of these / unreadable". Sources hidden.
   `items_blind.json` + `items_key.json` (key out of the blind file). Truth convention: the ink, misprints included; elision apostrophe =
   U+2019; numeral keraia stays U+0374/U+0384 as printed.
3. **Audit cards** for the 14 L1M corrections (the changed word: original label form vs corrected form, random order, same card format), in a
   separate `audit/` set with its own controls.
4. **Count** cards per wave and source-disagreement type. If DEV cards exceed 2,000, STOP before rendering all and propose a seeded,
   wave-stratified subsample that keeps presence P/R estimable (state the expected CI).

## Deliverables
`docs/records/labelfix/spellcheck/S8a_REPORT.md` (inputs/receipts, baseline tables per wave, card counts, controls, what is pending), the card sets under
`docs/records/labelfix/spellcheck/S8_DEV/cards/` and `…/audit/`, last line:
`S8a READY: DEV 600 (masked <m>/450 | pending); baseline loc_unknown <a>% seg_uncertain <b>% (per wave …); cards DEV <c> (+controls <k>), audit <d> (+<e>); masked rerun <cmd>`.
