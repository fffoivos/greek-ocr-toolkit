# S8a2 — Resume S8a: fetch DEV evidence with the proven L1M extractor; baseline; cards; audit all 48 (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace/rules: as `docs/records/briefs/S8a_dev_evidence_cards.md` (read it; everything there still binds unless changed here). Head db6e0c20 (S8a
partial). Remove the fetch STOP marker only by superseding it with this brief's budget (record that in the fetch log).

## Changes from S8a (track lead, 17 Oct)
1. **Extraction: reuse the proven extractor.** `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence/fetch_selected.py`
   fetched selected evidence for 200 lines in 31 s and 60 lines in 25 s (its crop-key join fix included). Copy/adapt it; do not continue the S8a
   helper. Fetch ONLY recogniser alignments (the 159 not in the local C1 cache) and R1 A/B/E predictions + coverage for the 600 DEV lines.
   **Do NOT fetch the SF4 overlays**: recompose AB/PRESENCE locally with the frozen gate from the fetched runtime + the local S6 run, exactly as
   L1M did for its original-crop projection (check parity on the 14 audit lines against L1M's saved decisions).
2. **Budget:** login node, streaming, one core; ≤ 3 attempts, each ≤ 4 min; write per-stage partial results to your own remote scratch folder
   `…/labelfix_l1_20261017/s8_dev_extract/` (never inside L1/L1E/L1R outputs) and pull them, so a failed attempt keeps what it fetched. If still
   incomplete after that, STOP and report exactly which stage and which lines are missing (the coordinator would then submit a small debug job).
3. **Audit = all 48 released L1M lines** (coordinator): the 14 corrected (done) + the 34 released-unchanged (28 from the 200, 6 vouli), from
   `…-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence/` (200/ and vouli/ per-line records). For an unchanged line the claim is "Google's
   marks are right": card every mark-bearing word of the line whose form any source (Google, R1-A, detector original/masked) disputes, plus a
   seeded 20% of its undisputed mark-bearing words; same format, own controls. Raise the audit cap accordingly (≤ 48 lines).
4. Masked DEV crops (`~/Projects/collect-v3-data/v2_masked/s8_dev/`) may still be pending: run the original-crop baseline + cards now; `--masked`
   remains the rerun.

## Deliverables
Update `docs/records/labelfix/spellcheck/S8a_REPORT.md`; last line as in S8a, with `audit 48 lines <d> cards (+<e>)`.
