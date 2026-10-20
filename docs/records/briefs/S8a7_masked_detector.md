# S8a7 — Masked-crop detector on the S8 DEV, scored against the adjudicated truth (gpt-6.1-sol, xhigh, network OFF)

Workspace/rules: as S8a/S8a2/S8a4/S8a6 (read them). Head = this commit. Network OFF. No detector/reader/gate code changes (S6/SF4 detector
frozen as the baseline). **Do not modify** `S8_DEV/cards/`, `S8_DEV/private/cards/`, `S8_DEV/cards_private/`, `dev_truth.jsonl.gz` or the
S8a6 report: the adjudication is frozen. Write new outputs under `S8_DEV/masked/` and a new report.

## Inputs
Masked crops + ownership maps for the 450 non-parliament DEV lines: `~/Projects/collect-v3-data/v2_masked/s8_dev/` (441 masked, 9 left as
originals: 6 unmatched, 3 ambiguous; wrong-line guard 0/450; receipt + guard_note.json). Parliament stays unmasked (matching unsettled).
Saved runtime/evidence as in S8a4 (`evidence/remote.json.gz`). Truth: `S8_DEV/evidence/dev_truth.jsonl.gz` (S8a6).

## Do
1. Run `scripts/labelfix/s8_prepare.py --masked` (or its equivalent) writing ONLY under `S8_DEV/masked/`: masked baseline per wave
   (letters, localisation_unknown, segmentation_uncertain, clipped_top/bottom, unnamed, components/letter, frozen-gate AB/PRESENCE outcome),
   original → masked side by side.
2. **Score the masked detector against the existing truth** on the adjudicated words (same weighting as S8a6): detector presence P/R per wave
   and per family, original vs masked, with intervals. No new adjudication: words whose masked-detector form is a NEW candidate not in the
   adjudicated deck are listed as `delta_cards` (count per wave), not scored.
3. Per-wave verdict: does masking move detector presence (especially recall) and loc/seg? Separate 9 unmasked lines.

`docs/records/labelfix/spellcheck/S8a7_MASKED_DETECTOR.md`; last line:
`S8a7 RESULT: masked 441/450; detector presence P/R original→masked by wave …; loc_unknown …→…; seg_uncertain …→…; clipping …→…; AB kept …→…; delta cards <n>`.
