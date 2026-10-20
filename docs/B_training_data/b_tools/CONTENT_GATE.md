# Content gate — 0.3

## Purpose

Exclude raw labels with a mixed-script word, hold unexpected scripts for review, and exclude short ordinary lines before spending work on segmentation/correction. The authoritative method versions are **content_gate 0.3** and **final_eligibility 0.3** in `docs/harvest/line_pipeline/tool_versions.json`; `PIPELINE_VERSION` is 0.3.2 in code. A gate pass alone is not ADMIT.

## Owner rules it implements, quoted

`AGENTS.md` states:

> An owner-accepted tool implements exactly the rules the owner stated; agents never add guards, tests or thresholds on their own.

`docs/harvest/line_pipeline/gate03/REPORT_part3.md` records the **14 Oct owner homoglyph ruling**:

> Any Greek word containing a Latin, Cyrillic or other-script letter drops the whole line automatically.

That report gives ΚΕΦΑΛΑΙΟN, Δαβій, Fιδον and λόγoς as examples, forbids a look-alike correction/model pass, and identifies the earlier repair-and-admit path as a deviation. The current implementation generalizes its mixed-word check across scripts: even if Greek and Latin are both expected in the document, a single mixed word drops. Unexpected scripts without mixed words HOLD. The gate reports record ordinary/headings minima 10/4 letters and the >1 letter-or-digit cell/numeric exemption as owner rules; they do not provide a separate verbatim owner transcript for those amendments.

## Version history

| Version | Documented generation |
| --- | --- |
| 0.1 | First integrated graph implementation. |
| 0.2 | Review fixes for composed coverage, producer binding and atomic exports. |
| 0.3, part 1 | Mixed-script word DROP and other unexpected-script HOLD before segmentation and all correction routes. |
| 0.3, part 2 | Shared raw-text short-line check; ordinary <10 letters, headings <4; cells/numeric lines exempt with alnum>1. |
| final eligibility 0.3, part 3 | Align cell length/shape handling: alnum>1 is the only cell length/shape check; remove final numeric-shape/nonletter-fraction rejections for cells. |

Parts 1–3 are amendments within the manifest's third generation, not invented patch versions. Part-2 prose about cells still failing final shape checks is superseded by part 3 and current `final_eligibility()`.

## Inputs

The row includes stable parent/id, source/book/edition/page, split, immutable raw Google text, crop hash and dimensions (`crop_bbox` or a bound crop path). Metadata provides declared languages, scripts, orthography, provenance, optional per-script orthographies, allowed characters and role. `expectations()` resolves **page override > book declaration > provenance-bound source policy**; declared metadata must be complete. It does not infer language or historical Russian from Cyrillic OCR.

The codec contributes NFD atoms and codec-aware letter scripts. Role precedence is `expected.content_role > row.content_role > row.primary_class > prose`. Policy defaults are prose_min_letters=10 and heading_min_letters=4; heading role is exactly `headings_caps`.

## Algorithm in prose

`inventory()` reuses admission word and letter primitives, adds codec-aware script counts, and lists words whose letters vote for more than one script. `content_issues()` also records unexpected characters and minority-Latin majority-language issues, but only mixed-word and unexpected-script issues form the first early-exclusion block. Mixed words have DROP priority; unexpected scripts are retained as supporting evidence in the same result. With no mixed word, unexpected script produces HOLD.

Next, `short_line_exclusion()` uses **raw** text and rotation-free original crop aspect `max(width,height)/min(width,height)`. A≤6 defines a gate cell, without S4's ≤8-character condition. Count alnum using Unicode L* or Nd code points. Cells with alnum≤1 DROP; cells with >1 pass this check. If dimensions cannot be resolved, HOLD. For A>6, a `numerics_tables` role or `numeric_text()` grammar exempts the letter minimum if alnum>1; otherwise DROP numeric_shape. All remaining lines need ≥10 letters, or ≥4 for headings.

`numeric_text()` admits decimal digits plus its literal separator/whitespace set, or a nonempty canonical uppercase Latin Roman numeral with optional final `.` or `)`. This grammar is distinct from both N1's ASCII-digit token/slot grammar and descriptive `numeric_cells.classify_cell()` (which also handles Unicode Romans and Greek iota aliases). No new script substitutions occur.

Both `Pipeline.evaluate()` and census preparation call the shared early helper before segmentation/cache scheduling. Final eligibility reuses the raw length helper after composition, preventing an ordinary short raw line from being rescued by a correction. Current final eligibility bypasses numeric minimum/shape and nonletter fraction **only for A≤6 cells**. Non-cell numerics_tables still need ≥4 digits and ≥60% allowed numeric shape; other non-cells retain the nonletter-fraction test. Codec encodability, content, confidence, CTC and held-out-edition checks remain applicable to cells.

## Outputs and reason codes

| Disposition | Reason / evidence |
| --- | --- |
| DROP | `mixed_script_word`, with exact offending words; optional unexpected-script evidence follows. |
| HOLD | `unexpected_script`, with scripts, script counts and offending characters. |
| DROP | `short_line`, with role, letter count and minimum. |
| DROP | `single_character_cell`, with alnum and aspect. |
| DROP | `numeric_shape` for non-cell numeric alnum≤1 in the early gate. |
| HOLD | `cell_status_unresolved` when crop aspect cannot be established. |
| No early exclusion | Continue to segmentation and required correction routes. |

Early results record `content_gate.excluded`; every correction route is `not_run_due_to_prior_exclusion` and there is no segmentation stage. Other suspicious content can still use the evidence-backed content-repair interface; mixed words cannot be repaired into admission under this ruling.

## Evidence: review sets and owner marks

`docs/records/harvest/seg_steps/gate_rereport/REPORT.md` re-evaluates saved text/metadata only. The finite sets resolve through source policy with **zero unresolved expectations**; 1,744 distinct header-backed paths were SHA-verified. Counts below use actual precedence and count overlapping cohort entries, not a disjoint population.

| Set | Before | Mixed DROP | Unexpected HOLD | Remaining short/cell/numeric DROP | After |
| --- | ---: | ---: | ---: | ---: | ---: |
| segeval1 | 150 | 1 | 2 | 10 | 137 |
| calibration | 888 | 10 | 10 | 49 | 819 |
| cells | 250 | 0 | 1 | 36 | 213 |
| typology | 417 | 3 | 23 | 107 | 284 |
| Explicit owner marks | 235 | 1 | 2 | 41 | 191 |
| Rated calibration | 135 | 2 | 5 | 37 | 91 |
| Marked typology | 185 | 1 | 3 | 5 | 176 |

These exclusions change segmentation-score denominators; they are not a newly adjudicated gate-accuracy score. Surviving S4 agreement is **157/191** explicit marks, **77/91** calibration ratings and **153/176** typology marks. Part 3's finite final-eligibility comparison changes 155 reason lists, all cells, and **124 outcomes** to diagnostic ELIGIBLE (5/51/48/20 by the four sets); this is not an admission forecast after corrections.

The by-book unexpected-scripts record is `docs/records/harvest/seg_steps/gate_rereport/UNEXPECTED_SCRIPTS_BY_BOOK.md`, backed by saved row decisions and raw-script evidence. It keys **source × book × script**, reports actual helper outcomes, whole-script tokens, mixed words, raw examples, and diagnostic classes (a) plausible language/apparatus, (b) letter confusion, (c) noise candidate. Script groups overlap; borderline classifications are not pixel verification. Examples:

| Source/book/script | Recorded rows / outcome | What the record establishes |
| --- | --- | --- |
| archive_b24878935 / no book key / Cyrillic | 123 HOLD | Whole tokens; interpretation unresolved from raw OCR. |
| archive_bub_gb_Cmg6AQAAIAAJ / no book key / Cyrillic | 5 HOLD | Bibliographic text can plausibly contain real script words; no declaration changed. |
| serbia / e46187046efbc139 / Latin | 208 HOLD | 207 rows have whole multi-letter Latin tokens; possible apparatus needs metadata review. |
| bsb_poly1850 / 027215cc6d2a7e8a / Arabic | 3 HOLD | Sparse fragments, diagnostic noise candidate only. |

`CODEC_QUESTIONS.md` separates **º (17 rows, 6 books), ª (16 rows, 3 books), µ (2 rows, 2 books)** from language/script claims. The codec currently votes these as `other`; legitimate Latin ordinal contexts can still HOLD or, within a mixed word, DROP. MICRO SIGN versus Greek μ remains a representation/printed-glyph question. No normalization or substitution was made. Consult the full source tables for exact IDs; the examples above are not exhaustive.

## Tests

Existing `tests/test_content_gate.py` checks early precedence with downstream adapters that raise, mixed words even when both scripts are expected, exact script evidence, zero native attempts/cache entries on exclusion, 9/10 and 3/4 boundaries, A=6 in both orientations, raw Unicode counts, missing dimensions, and final cell alignment with other safeguards retained. `gate03/REPORT_part2.md` reports 33 gate +59 segmentation passes, with 20 pre-existing pipeline failures from an external missing worker path. Part 3 reports **236 passed /0 failed** in the final combined requested suite, against its 222-pass baseline, and documents the explicit cell fixture needed for rescue-by-edit. These are historical reports, not tests run here. `gate_rereport/validation.json` reports PASS, 592,466 census rows scanned for metadata/text outcomes, zero segmentation/reader runs and 80 sheet removals.

## Known limitations

Expected scripts require accurate provenance-bound declarations. A HOLD can be real apparatus, not OCR noise; raw script presence cannot settle printed glyph identity. The gate intentionally drops homoglyph words rather than guessing. Codec classification can make ordinals/micro signs appear foreign. Missing dimensions HOLD. Finite-set diagnostic eligibility omits the full production/correction context; it must not be presented as ADMIT counts. The historical gate re-report's .30–1.95 fitted optimum did not itself change the historical .50–1.50 defaults. SEG10 later adopted 0.30–2.00; the current segmentation identity is 0.13 (label 0.9-s5).

## Code paths

`greekocr/harvest/line_pipeline.py`: `expectations`, `inventory`, `content_issues`, `crop_aspect`, `numeric_text`, `short_line_exclusion`, `content_gate_exclusion`, `final_eligibility`; `greekocr/harvest/line_pipeline_census.py`/`line_pipeline_parallel.py` consume early exclusions. Current version identity is in `docs/harvest/line_pipeline/tool_versions.json`.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`.
- `greekocr/harvest/line_pipeline.py`; `greekocr/harvest/numeric_cells.py`; `tests/test_content_gate.py`.
- `docs/harvest/line_pipeline/tool_versions.json`; `docs/harvest/line_pipeline/gate03/{REPORT.md,REPORT_part2.md,REPORT_part3.md}`.
- `docs/records/harvest/seg_steps/gate_rereport/{REPORT.md,summary.json,validation.json,CODEC_QUESTIONS.md}`.
- `docs/records/harvest/seg_steps/gate_rereport/UNEXPECTED_SCRIPTS_BY_BOOK.md` (table introduction and cited source/book entries).
