# T4b — fix duplicate-interleave in row assembly, then a merged-line admission screen calibrated on blind-checked cards (gpt-6.1-sol, xhigh, network OFF, no spend, ≤ 90 min)

**Workspace and access**
- Write outputs only under `docs/records/harvest/screen_v1/`, in this worktree `~/Projects/greek-ocr-toolkit-sol-funnel-gr`.
- Read-only on `~/Projects/greek-ocr-toolkit-sol-funnel-{ia,intl}` and on `~/Projects/greek-ocr-toolkit` (the main checkout; another agent works there).
- No Google or other provider calls; everything needed is on disk.

## Measured problem
Blind Opus checks covered 640 Google label cards, 40 per source, from the F2 samples `sample_v1/{ia,intl,gr}`. Two defects make usable lines wrong:
- **(b) Interleaved duplicate words on clean single-row crops.**
  - Example: card `gr/openarchives c014`. The crop shows `τῶφλι τῆς μυστικῆς ἀνεμόσκαλας τοῦ Ἰακώβ.`; the label reads `τῶφλι τῆς τῆς μυ μυστικῆς κυστικῆς ἀνεμόσκαλας τοῦ οῦ Ἰακώβ.`
  - The page `openarchives--hf-1ac7969a077332d2-48a986cf--000019` has no PDF text operators.
  - Working cause: two overlapping Google readings of the same ink, merged by our row assembly. **This is our bug, so it gets fixed, not screened.**
  - Cards with this pattern: OA 7, ELSTAT 4, Gazette 3, Pleias 3, Anemi 3. Find them from the blind `detail`/`errors` and the label text.
- **(a) Multi-row or multi-column crops.**
  - Two printed rows, or two side-by-side columns, sit inside one crop, and Google's label contains both. Blind codes: `merged_two_lines`, or `crop_overrun` together with `extra_text`.
  - G1b does not catch it. On Gazette, Pergamos and OA, usable G1b-negative cards are *less* accurate than all admitted cards (letters-y 36%, 36%, 50%).

## Inputs
- **Blind verdicts:** `docs/records/harvest/blind_checks_v1/{ia,intl,gr}_labels_<set>.jsonl`.
  - Fields: card_id, letters y/n/u, marks y/n/na, errors[], detail ("printed → google").
  - Checker instructions are in `LABEL_CHECK.md`.
- **Card ↔ line binding:**
  - GR: `sample_v1/gr/label_cards/<source>_key.json`; GR cards use the fields `card` and `text`.
  - INTL: `sample_v1/intl/label_cards_keys/<set>.json`.
  - IA: `sample_v1/ia/label_cards_key.json`, keyed `<class>/<card>`.
- **Per track:** `lines.jsonl`, page records, page images under `bulk/`, and Google responses under `google/docai|parsed`.
- **Code:** P1 row assembly and G1b are bound in each track's receipts.

## Do, in this order
1. **Fix (b) in row assembly.**
   - Trace at least the 20 interleave cards (7+4+3+3+3) to the Google tokens/lines and the assembly step, with token ids and boxes.
   - Implement the fix as a new function beside the shipped code; do not modify the shipped file. Rule: when a Google token/line box overlaps a box already assigned on the same row by more than a stated IoU, drop it or merge it. State the IoU and why.
   - Re-assemble every line on all affected pages from the existing Google responses, with no new reads. Show for each of the 20 cards: old label → new label → whether it now matches the blind checker's printed reading.
   - Report how many lines change in each track and source, overall. Show 10 random changed lines that were *not* among the cards, so collateral changes are visible.
   - All later steps use the fixed labels.
2. **Merged-line screen (a): an admission check only.**
   - Reject the crop. Never re-cut or repair it.
   - Inputs are only the existing crop pixels, the label and the Google geometry. No new reads.
   - Candidate features:
     - crop height ÷ page median row height;
     - ink-row peaks in the horizontal projection;
     - label characters ÷ crop ink width in x-heights, compared with the page median;
     - number of Google lines/paragraphs contributing tokens;
     - an internal x-gap or column rule.
3. **Calibrate and test.**
   - Positive = a blind card with letters `n` and errors including `merged_two_lines`, `extra_text` or `crop_overrun`.
   - Use a seeded 50/50 split stratified by source. Set thresholds on the calibration half only. Report on the held-out half:
     - precision and recall;
     - per source, letters-y on surviving usable cards, before → after, with Wilson 95% intervals;
     - per source, the share of usable rows removed, computed over the full `lines.jsonl`;
     - usable rows/read page per class after the fix and screen, with a page-bootstrap 95% CI.
   - **Government Gazette is the priority case**: it is the only route to the 40k modern-scanned target. Give it its own paragraph, covering what survives, how accurate it is, and the rows per page for modern and poly1900.
4. **Marks as a separate column.** For every polytonic source, give marks-y on the usable cards after steps 1–2, Wilson 95%, from the blind `marks` field.
   - A source under 90% marks is tagged `marks_correction_required`. Its rows carry that tag in `features.jsonl`.
   - Known weak sources: ELSTAT 66%, Pergamos 65%, Lekythos 70%. Lekythos is the largest polytonic supply, so report its marks errors by type (grave→acute, circumflex→acute, breathing dropped).
5. **Text-side convention checks.** Count lines and apply each check over all usable lines per source:
   - **ſ → s.** Accepted as a glyph-variant convention. Count lines where the blind detail or page script shows ſ; if that is not determinable, say so.
   - **Roman numerals in Greek/Cyrillic look-alikes.**
     - Deterministic fix only when the whole token maps to `^[IVXLCMD]+$` through a one-to-one look-alike table (Ι→I, Χ→X, …; state the table). Otherwise exclude the line.
     - Report how many lines take each branch.
   - **Line-end hyphen dropped.**
     - Exclude a line when its label ends on a word fragment with no hyphen and the next line on the same page and column starts lowercase. This is a text-side test, with no ink work.
     - Report counts.
   - **Em dash changed to a hyphen.** Accept it; count it.
6. **Verdict.** Make no claim beyond 40 cards per source. Say which sources reach ≥90% letters-y on surviving usable cards and which do not, and why.

## Hand-off
Write these under `docs/records/harvest/screen_v1/`:
- `REPORT.md`: step 1 first, then a per-source table (letters before→after, marks, rows removed, rows/page per class), then the Gazette paragraph and the convention counts;
- `assembly_fix.py`;
- `screen.py`;
- `features.jsonl` (one row per line in all three tracks, with fixed label, screen decision and tags);
- `card_eval.jsonl`;
- `receipts/`.

Commit if git allows; otherwise leave a guarded commit helper. The last line must be exactly:
`T4b: done | interleave fix: <n> cards fixed of 20, lines changed <x>% | screen P/R test: <p>/<r> | letters ≥90% after: <list> | marks <90%: <list> | gazette letters after: <a>% rows/page modern <m> | usable rows removed: <x>%`
