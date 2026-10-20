# Label Quality Benchmark: polytonic-marks inputs, by reference (17 Oct 2026, spell-check track)

For the LQB built by the secondary-corrections lead. These are paths and sha256 only; nothing is re-run. Read everything read-only and
copy what you need. Truth convention throughout: **what is printed** (misprints included), the four heads
`(breathing, accent, dialytika, subscript)` in `r1_common.HEADS` order, and UNKNOWN kept as UNKNOWN.

## Truth rows

| Set | Path | sha256 | Truth method | Use in the LQB |
|---|---|---|---|---|
| Print truth, 189 words | `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/print_truth_s0.json` (built from `print_truth/` answers + `key_SEALED.json`) | e8f2067b… (key_SEALED ba2de6a3…, items_public b9326de5…) | Two blind Opus readers + tiebreak; lead-pixel-checked controls | Word-level marks truth. **Blinding note:** the key sits in the repo, within reach of any tool run there (`print_truth/README.md`). Score from it, but never tune on it. |
| 39 owner cards + notes | `…/R2_evidence/reader_errors_39_owner_final.json`, `reader_errors_39_card_inputs.json`, `owner_sheet_notes_20261017.jsonl`, `OWNER_REMARKS_20261017.md` | 22f55fe1…, 488b493a…, d7c525b1…, 82f214de… | Owner reviewed all 39: 38 left as shown, 1 corrected (ἤγε → ἦγε, overlay v1.1) | Selected ON reader errors, so not a random sample. Use it as a regression set, never for a rate. |
| Substitution sample, 60 | `…/R2_evidence/substitution_sample_60.json` | 49794714… | Owner review: agree 20/20, other mark 19/20, no-ink 17/20 | Per-tier substitution precision of sf6. |
| Release audit, 100 lines | `…/docs/labelfix/spellcheck/L1A2_AUDIT100_RESULT.md` (+ cards `L1A2_CARDS.md`) | 5d7b8c45… | Owner line review of sf6 releases: 83/100 right | Line-level release precision. 13/17 wrong lines add an iota subscript. |
| S8 DEV adjudicated (600 lines, 1,793 items) | `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz` (branch opus/spellcheck-s8 2e1efb3be) | bbfba150… | Two-reader adjudicated items; 144 control items and 673 unresolved are excluded (R2A_DIGEST §e) | DEV marks accuracy. Already used as an R2a evaluation set, never as training data. |
| T4 witnesses (791 resolved word cards) | `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/artifacts/r2_resolve/T4/final/resolved.jsonl` (opus/r2-cards 45c8c63ce) | 3815e244… | Two blind Opus readers + 2-of-3 tiebreak; controls gated | **Not training data** (witness role, documents disjoint from training). The primary marks set. |
| T2 resolved (790 cards) | `…/r2cards/artifacts/r2_resolve/T2/final/resolved.jsonl` | a3d0214f… | Same as T4 | **Training data for the R2a arm.** Manifest: `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/artifacts/r2a_manifest/r2a_slots_v2.jsonl`, 20b24e0f…, 1,572 slots. R2a was not adopted, so the release model never trained on T2, but treat T2 as **contaminated for any R2a-family repair**. Recommendation: leave it out of the LQB, or score it only for raw Google vs sf6. |

## Release and census

- **sf6 release (R1-A, PRESENCE/FULL overlays, 124,669 selected lines):** on Clariden at
  `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729`.
  - Selection: `…/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl`, sha256 `ee6c51bd…`.
  - Receipt sha256: `c7cfcc85…`.
  - Policy: `sf6-release-v1`, digest `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`.
- **Census of the release:**
  - `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/L1C_census_3679781/` (the HOLD census);
  - the SQ1 quote/breathing census `~/Projects/greek-ocr-toolkit-spellcheck/artifacts/sq1/census.json` (b961df88…), which also
    records the release paths and shas above.

## Scorer entry point

`~/Projects/greek-ocr-toolkit-spellcheck-r2prep/scripts/labelfix/r2_score.py`, sha256 `59c8a9ab…` (opus/r2-prep 6a08c6bbd, R2S).
- `union_records(...)` aligns predictions with truth slots.
- `summarize(...)` gives the four-head micro P/R/F1.
- R2S rule: recogniser letters with no truth slot are UNKNOWN (excluded), never "unmarked".
- Overlay v1.1 must be applied symmetrically to every arm: `…/r2prep/docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json`.
- Examples of paired per-item ledgers and the document-cluster bootstrap: `…/r2prep/scripts/labelfix/r2a_digest.py`.
