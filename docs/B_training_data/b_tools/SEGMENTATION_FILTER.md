# Segmentation filter — 0.13 (label 0.9-s5)

## Purpose

Screen an immutable Google-labelled crop for other rows, output length relative to measured ink, and vertical padding. A segmentation KEEP passes this screen; it does not certify the transcription or training admission. This is a B.b document for the documentation home `docs/B_training_data/b_tools/`, as mapped in `docs/cleanup_20261019/PLAN.md`.

Authority is the checked-in implementation and `docs/harvest/line_pipeline/tool_versions.json`. That manifest names numeric version **0.13**, label **0.9-s5**, with **13** documented iterations. `docs/records/harvest/seg_steps/NOTES_FOR_LATER_STEPS.md` records the owner's freeze and no further segmentation steps.

**Current band:** `segmentation-policy.js` uses inclusive **0.30–2.00** for ordinary and small crops. **History:** S4 used 0.50–1.50; the original `s5/BAND_PROPOSAL.md` was proposal evidence. SEG10 subsequently adopted 0.30–2.00 by coordinator decision under the owner's end-to-end mandate (19 October 21:34), not an owner ruling. PIPE032 records the thirteenth method iteration as numeric version 0.13, label 0.9-s5, without changing that band. See `s5_adopt/REPORT.md`; fitted owner marks do not establish independent generalization.

## Owner rules it implements, quoted

`docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md` quotes the owner:

> The rules are
> 1. detection of other lines, at least two words cutoff doesn't count
> 2. Comparison of de skewed lines' long sides normalized for height (the deskewed line's) with google output
> 3. And also height of deskewed line box x 1.5 + bounding box's height

> stop adding rules I didn't tell you to

The hand-off resolves rule 1 as **more than two whole neighbour words** or **any additional complete line** → DROP; exactly two pass. The later S1 operational whole-word rule is every detected body ≥95% visible. This differs from the earlier literal 100%-visible owner standard recorded in `docs/records/contexts/CONTEXT_20261019_segmentation_and_secondary.md`; the current code/manifest win. No target-cut veto or row-frame-taller-than-upright veto remains.

## Version history

| Version / record | Method change / status |
| --- | --- |
| 0.5 | Frozen crop/font comparison, before row-frame de-skew; saved census baseline. |
| 0.6 | Main text box measured in its detected row frame; flat-angle identity retained. |
| 0.7 | Crop-only inventory → gate → length; also added target-cut veto and taller-than-upright guard, subsequently rejected. |
| 0.8 | Exactly the three owner rules; removed those two vetoes. |
| 0.9-s1 | Whole group needs ≥1 detected body and every body ≥95% visible; horizontal-edge contact is diagnostic. |
| 0.9-s2 | Every crop with h>w turns 90° clockwise before detection and measurement; h≤w unchanged. Legacy `orientation_cw=270` encodes the physical clockwise turn. |
| 0.9-s3 | Non-straight main-row ink measured along the existing base curve in arc-length/normal coordinates; straight construction retains S2 arithmetic exactly. |
| 0.9-s4 | Google visible characters ≤8 and crop long/short≤6: all extracted components define the box; row-only no-main abstention defers to length/padding. Others retain S3. |
| s5 proposal (historical) | Fitted 0.30–2.00; gate re-report tie-selected 0.30–1.95, with 0.30–2.00 still tied. |
| 0.13 / label 0.9-s5 (current) | SEG10 coordinator adoption of one inclusive 0.30–2.00 band; PIPE032 numeric version normalization. S4 geometry, gate, mode 2 and padding 1.5 unchanged. |

The manifest also retains five earlier named generations (crop guides, font normalization, target-box normalization, whole-word tolerance, padding 1.5 heights); its iteration count is **13**, not a count of commits or claimed accuracy gains.

## Inputs

`NativeSegmenter` consumes a pipeline row with stable parent/id/split, immutable `raw_text`, `crop_sha256`, crop path or reconstructable source page plus exact crop bbox/hash, and script class for the frozen predictor. Reconstruction must reproduce the frozen crop PNG hash. Segmentation's character count is NFC non-whitespace code points excluding M*/C* categories; it is not the gate's Unicode letter count.

Assets are `greekocr/harvest/filtering_assets/{crop-tools.py,segmentation-policy.js,service.mjs,font-models.json}` and the vendored collector geometry. Optional source-row context supplies diagnostic neighbour observations; missing context does not itself block the crop-only rule.

## Algorithm in prose

`line_pipeline_native.py` verifies crop bytes, turns tall crops clockwise, runs the existing glyph extraction and `text_lines`, and retains orientation/frame provenance. The existing refocus path can rerun glyph extraction when a unique complete non-main row is found and the current main row has low visibility. The crop-only inventory assigns components to detected bands, records body visibility, words, cut evidence and completeness. Existing groups use a .35-x-height gap. The complete-neighbour proxy requires votes≥6, bodies≥6, visibility≥.9 and coverage≥.6. S1 whole groups require nonempty body membership and every body's mean/base-frame visibility≥.95. These are detector proxies, not lexical print truth.

Rule 1 runs first. An additional complete row or >2 whole neighbour words drops. Missing main row or unresolved direction can abstain; S4 small-crop orchestration defers the no-main abstention while preserving positive neighbour DROPs. Stage B is skipped when the gate does not pass.

For ordinary crops, main-row TEXT_ROLES ink defines the text box. S2 uses a de-skewed frame; S3 uses the existing base polyline's nearest feet, cumulative arc length s and signed normal n. It does not fit a new curve. Actual straight constructions use the original rotation arithmetic. The upright box remains the padding envelope. S4 small crops instead use the union of **every extracted component's axis-aligned bounds**, including marks, specks, rules and neighbour roles. Existing extraction already omits area<3 noise; S4 does not introduce a new noise filter. Width is passed as `long_side` and height as `short_side` for small crops, without sorting them; other crops use max/min frame extents.

The Rust streaming predictor `scripts/harvest/filter_runtime/src/main.rs` reads frozen JSON coefficients, selects the script model or pooled fallback, uses model index 2, evaluates `exp(clamp(sum([1, ln(long/short), 0] * coefficients), 0, 12)) - 1`, and never fits. Its Cargo package version **0.1.0** is separate from segmentation **0.13 (label 0.9-s5)**. Rule 2 compares `(characters+1)/(predicted+1)` inclusively with the checked-in **0.30–2.00** interval. Rule 3 requires `(crop_height-upright_box_height)/row_frame_height ≤1.5`; small crops use their all-component height for both box height and denominator.

## Outputs and reason codes

Native results carry tool version, row binding, raw-text SHA, verdict/reason, frame, measurements, warnings and detector/gate evidence. Verdicts are KEEP, DROP, UNCERTAIN; the pipeline handles uncertainty separately from a DROP.

| Result | Reason text / condition |
| --- | --- |
| Gate DROP | `gate: second complete line`; `gate: too many whole neighbour words` |
| Gate UNCERTAIN | `gate: no main row found`; `gate: reading direction unresolved` (S4 no-main deferral as above) |
| Length DROP | `length: Too little OCR output for the text box after height normalisation.`; corresponding `Too much` reason |
| Padding DROP | `length: Top and bottom padding together exceed 1.5 target-line heights.` |
| Measurement UNCERTAIN | No usable text box; unavailable prediction/character count; invalid interval; unavailable target height/padding |
| KEEP | `length: OCR length matches; vertical padding is within the selected allowance.` |

Main-cut spans, baseline crossings, optional context counts and curvature ambiguity remain diagnostics. They do not create extra rejection rules.

## Evidence: review sets and owner marks

The frozen main replay is **150 segeval1 + 888 calibration + 250 cells =1,288 cohort records**. The 150 are labelled from complete saved reader answers, using gate2's function: positive segmentation faults precede unknown flags, and `crop_overrun` alone is fine. There are 118 fine, 30 faulty and 2 unresolved. FP=DROP/fine, FN=KEEP/faulty, UNC=all UNCERTAIN. The 888 have only **135 rated rows** (78 KEEP, 57 DROP); the remaining 753 are unlabelled. Cells have no inferred truth.

| Version | 150 FP/FN/UNC | 888 agreement /135 | Explicit owner agreement /235 |
| --- | --- | --- | --- |
| 0.5 | 26/8/0 | 98 | not supplied in this replay table |
| 0.6 | 21/11/5 | 97 | not supplied |
| 0.7 | 59/8/11 | 65 | not supplied |
| 0.8 | 18/14/11 | 94 | 155 |
| s1 | 17/14/11 | 95 | 156 |
| s2 | 17/14/5 | 105 | 169 |
| s3 | 17/15/5 | 105 | 170 |
| s4 (historical) | 16/15/0 | 109 | 189 |
| s5 (current policy) | 4/19/0 | 117 | 209 |

The saved SEG10 replay also gives typology agreement **173/185**; after the content gate FP/FN changes **11/15 → 2/18**. False negatives increase **15→19** unfiltered and **15→18** after the gate. These are reused/fitted panels, not independent validation.

Sources: `s5_adopt/REPORT.md`, gate2 hand-off and `docs/records/harvest/seg_steps/s{1,2,3,4}/REPORT.md`. The older context pack's 0.8 FN=11 and gate hand-off's 0.7 FP=19/50 do not replace full-population **FN=14** and **FP=59**.

Explicit `owner_marks_20261019.jsonl` has **240 entries /235 distinct IDs**: gate 62, cells 152, deskew 26 entries, with five deskew IDs repeated in gate. Latest timestamp wins, file order breaks ties; score each ID once, UNCERTAIN as non-agreement. This snapshot has no conflicting KEEP/DROP duplicates. It remains separate from historical 150 labels and 888 ratings.

The small-segment review has **437 crops**, including 20 controls excluded from scoring, leaving **417 typology cards**. Only **185** have explicit marks from `small_segments/owner_marks_smallseg.jsonl`: agreement **0.8 131/185 → s3 147/185 → s4 160/185**. Marks occur on 119 word and 66 caps-display cards; no truth is invented for unmarked types. S4 main cells verdict counts are **230 KEEP /15 DROP /5 UNCERTAIN**, not an accuracy score.

S4's separate numeric-fit diagnostic is not adopted: primary numeric agreement was s3/text-font **111/144**, s4/text-font **127/144**, s4/short-numeric **132/144**. Non-numeric s3/text-font **120/157 → s4/text-font 137/157**. It does not license a numeric-specific predictor.

`s5/BAND_PROPOSAL.md` joins explicit marks and ratings into **533 judged IDs**, excludes 28 gate DROPs and five gate UNCERTAIN, and retains **500** (434 owner KEEP /66 DROP). Ten length-blind owner DROPs are outside the 490-row objective. End-to-end false drops/false keeps change **59/16 at .5–1.5 →10/24 at .30–2.00**; 59 lines change. Bounds rest on 1–3 neighbouring-grid witnesses; bootstrap upper bounds span 1.75–2.45. These are fitted, selected-population results.

After content gate 0.3 exclusions, `gate_rereport/REPORT.md` gives **137/819/213/284** surviving cohort rows. On these saved verdicts S4 has **11/15/0** FP/FN/UNC on 137; **77/91** rated agreement; **157/191** explicit mark agreement; **153/176** typology marked agreement; cells **205/3/5** KEEP/DROP/UNC. Band population shrinks **500→420**, changed lines **59→38**. Primary numeric best becomes s4/text-font **103/110**, versus short-numeric **102/110**; overall equal-cost selected band becomes .30–1.95, with .30–2.00 tied. This re-report ran no segmenter or readers and changed no policy.

## Tests

Historical evidence, not checks rerun by CLEAN5C: gate2 reports **157 passed**; S3 **177 passed**, including **1,184/1,184 straight-row identity**; S4 **189 passed** with all non-small native rows checked against S3. Relevant tests are `tests/test_seg_{gate,deskew,curve,small}.py`, `tests/test_line_pipeline.py`, and `scripts/harvest/verify_filter_parity.py`. S4 boundary tests include chars=8, aspect=6, turned crops, all-component membership, padding and positive gate DROPs without a main row. Stored source/receipt/readback hashes belong to their original runs; this documentation pass neither regenerates nor requalifies them.

## Known limitations

`ia_greek_latin--d94cfff6c5bd6428--s004-l0037` is the frozen curved-box failure: crop **523×53**, ink x support [22,502], 21 characters; S3 short side **79.4 px**, `sn_box` [21.75,−65.94,525.80,13.46]. It flips KEEP→DROP. S2 already measured ~62 px versus upright 49 px. The report lists tilted end normals/out-of-support geometry as possible causes, not a confirmed diagnosis. Bounding curve measurements to ink support and flagging `short_side_exceeds_crop_height` was proposed in `docs/records/briefs/SEG_S3b_curve_support.md` and **not run**. Do not describe that fix as implemented.

The Gazette l0120 witness is incorrectly inventoried as zero whole neighbour words despite the owner seeing >2; widening the band would expose a wrong KEEP. Accents in `129cff40-p000009-l0107` are detected as complete neighbour rows despite owner KEEP. A matching length cannot detect a wrong transcription of similar size. Sparse/reused owner panels and detector proxies do not establish generalization or full pixel correctness.

## Code paths

Active adapter/policy/predictor: `greekocr/harvest/line_pipeline_native.py`, `greekocr/harvest/filtering_assets/`, `scripts/harvest/filter_runtime/`. Supporting source geometry observations: `greekocr/harvest/{geometry_observations,row_inclusion,neighbour_words,orientation_screen,numeric_cells}.py`. `numeric_cells.py` is descriptive (original width≤200, height≤40, visible chars≤10), explicitly **not a segmentation policy input**; do not confuse it with S4 small crops or gate cells.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/OWNER_BRIEF.md`; `docs/cleanup_20261019/PLAN.md`.
- `docs/harvest/line_pipeline/tool_versions.json`; `docs/records/contexts/CONTEXT_20261019_segmentation_and_secondary.md`.
- `docs/records/harvest/collect_v3_admission/segeval1/{deskew,gate,gate2}/HANDOFF.md`.
- `docs/records/harvest/seg_steps/s1/REPORT.md`; `s2/REPORT.md`; `s3/REPORT.md`; `s4/REPORT.md`; `s5/BAND_PROPOSAL.md` (all under `docs/records/harvest/seg_steps/`).
- `docs/records/harvest/seg_steps/NOTES_FOR_LATER_STEPS.md`; `docs/records/harvest/seg_steps/gate_rereport/{REPORT.md,summary.json,validation.json}`.
- `greekocr/harvest/line_pipeline_native.py`; `greekocr/harvest/{geometry_observations,row_inclusion,neighbour_words,orientation_screen,numeric_cells}.py` (targeted source reads).
- `greekocr/harvest/filtering_assets/{crop-tools.py,segmentation-policy.js,service.mjs,font-models.json}`; `scripts/harvest/filter_runtime/{Cargo.toml,src/main.rs}`.
