# L1M — Masking foreign ink under frozen SF4

**Verdict: partial.** On the 200 held round1/round2/mixed lines, masking releases **42/200 ENSEMBLE_AB lines** (14 kept with a changed label) and **16/200 PRESENCE lines** (3 changed labels). Raw clipping flags fall 2269→650; localisation_unknown is 116→117 and segmentation_uncertain 240→237. Masking helps the clipping driver; it does not remove most complete-gate holds or improve the localisation driver in this sample.

**Coverage: 260 evaluated, with vouli reported separately.** Parliament is not sampled (two-column neighbour matching unsettled); **no projection to parliament**. Openarchives is also unsampled.

**Border attribution limitation:** The supplied r3 `lines.jsonl` carries row ownership summaries, fill component IDs, counts and a mask hash; it does **not** carry pixel ownership masks, mask paths or the centre curves needed for `_voronoi_keep`. The staged tree has crops, JSON and logs only. Every original clipping flag is mapped to its exact border pixels and native connected blob(s), but all blob ownership is **undecidable**. Removed does not prove neighbour-owned, and retained does not prove own-line. Consequently the requested 6-neighbour/6-own visual attribution check cannot be completed from this handoff; the twelve inspected panels instead cover six verdict flips and six persistent border flags. The paired detector/gate result is complete for the 200; semantic border attribution remains open.

## Frozen method and verification

- Detector: `reading.read_ink(ink.analyse(crop), alignment.prediction, alignment, S4_model, filtered=False)`; S5 case model; default qualified geometry is empty, as in the original S6 job. Both variants use the same original text and saved alignment.
- Gate: unmodified `release_gate.compose_runtime`, `sf4-release-v1`, and the frozen `l1_common.overlay` wrapper, including original-label edit guards and line HOLD semantics. Kept-and-corrected means a changed NFD label accepted by the gate, **not independently verified print truth**.
- Imports and assets are read-only from c6064650fa5451cbc3bd13197d7a31c0d3bbf33d. Every imported frozen Python source and both model assets were compared byte-for-byte with its committed blob; hashes and Python/library versions are in each receipt. No detector, gate, release, original crop or `.git` file was written.
- Original-crop gate decisions match frozen recomposition of saved detector evidence on **260/260 lines in both modes**. A/B/E predictions, A/B/E coverage, recogniser text and any saved K1 inputs have one identical content digest within each original/masked pair. No recogniser or reader inference ran.
- Counts below distinguish raw detector clipping predicates on all letter slots from SF4 clipping vetoes after zone relevance. Counts are slot incidences, not independent physical defects. Unnamed counts are slots with unnamed marks; separate blob counts and component IDs are saved per letter.
- Foreign-removal strata: none=0 audited foreign pixels removed, small=1–100, large=>100; unknown audit measurements remain separate. These descriptive thresholds were fixed before reading outcomes. Matching failures remain in all totals with unchanged crops.

## Staging and own-ink audit

| Wave | N | Mask applied | Crop changed | Match failed | Audit unmeasured | Own loss=0 | Own measured | Own lost px | Foreign removed px |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 80 | 79 | 72 | 1 | 2 | 76 | 78 | 11 | 8748 |
| round2 | 60 | 60 | 56 | 0 | 0 | 57 | 60 | 28 | 4518 |
| mixed | 60 | 60 | 46 | 0 | 2 | 57 | 58 | 15 | 3251 |
| vouli | 60 | 59 | 58 | 1 | 2 | 55 | 58 | 100 | 8246 |
| ALL evaluated | 260 | 258 | 232 | 2 | 6 | 245 | 254 | 154 | 24763 |

All 254 measured audits are retained: 245 have zero own-pixel loss, 9 have nonzero loss; 6 are unknown/unmeasured. The source audit statuses are {'owned': 254, 'cross_row': 4, 'invalid_detector_geometry_on_page': 2}; unmeasured means null own/foreign measurements, including cross-row and invalid-page-geometry cases. Total own loss is 154 pixels, foreign removal 24763 audited pixels. `mask_applied` includes successfully processed unchanged crops; it is not the crop-changed count.

## Paired raw detector counts

| Wave | N | Letters | localisation_unknown | segmentation_uncertain | clipped_top | clipped_bottom | unnamed | Component assignments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 80 | 3466 | 54→55 | 104→101 | 543→94 | 521→262 | 20→17 | 3621→3613 |
| round2 | 60 | 2714 | 22→22 | 46→46 | 389→80 | 303→86 | 16→14 | 2833→2834 |
| mixed | 60 | 2383 | 40→40 | 90→90 | 275→40 | 238→88 | 11→9 | 2493→2492 |
| vouli | 60 | 2729 | 18→18 | 76→76 | 348→104 | 330→108 | 46→47 | 2814→2812 |
| ALL evaluated | 260 | 11292 | 134→135 | 316→313 | 1555→318 | 1392→544 | 93→87 | 11761→11751 |

Localisation newly fails at 4 starts and clears at 3 starts. Net counts alone conceal these exchanges. Full per-line counts, per-letter component IDs/bboxes, histograms, native labels and flags are preserved in [evidence](L1M_evidence/200/).

| Crop | Native component IDs per letter | Letter slots |
| --- | --- | --- |
| original | 0 | 134 |
| original | 1 | 10555 |
| original | 2 | 603 |
| masked | 0 | 135 |
| masked | 1 | 10563 |
| masked | 2 | 594 |

Component assignments may count one fused native component for several letter partitions; zero means no native letter component was assigned, not no printed character.

## Complete frozen-gate outcomes

| Mode | Wave | N | Held | Kept changed | Kept unchanged |
| --- | --- | --- | --- | --- | --- |
| ENSEMBLE_AB | round1 | 80 | 80→63 | 0→5 | 0→12 |
| ENSEMBLE_AB | round2 | 60 | 60→44 | 0→8 | 0→8 |
| ENSEMBLE_AB | mixed | 60 | 60→51 | 0→1 | 0→8 |
| ENSEMBLE_AB | vouli | 60 | 60→54 | 0→0 | 0→6 |
| ENSEMBLE_AB | ALL evaluated | 260 | 260→212 | 0→14 | 0→34 |
| PRESENCE | round1 | 80 | 80→74 | 0→1 | 0→5 |
| PRESENCE | round2 | 60 | 60→55 | 0→2 | 0→3 |
| PRESENCE | mixed | 60 | 60→55 | 0→0 | 0→5 |
| PRESENCE | vouli | 60 | 60→58 | 0→0 | 0→2 |
| PRESENCE | ALL evaluated | 260 | 260→242 | 0→3 | 0→15 |

AB releases 48 lines and introduces 0 new line holds. Of the 42 newly kept base-sample lines, 40 have measured zero own-pixel loss, one has 1 own pixel lost (and is accepted as corrected), and one has an unmeasured audit. A/B agreement is a stability signal from readers sharing training data; the new accepted labels have not been scored against independent print truth.

### Exact slot HOLD reasons (all evaluated lines)

| Mode | Exact reason | Before | After |
| --- | --- | --- | --- |
| ENSEMBLE_AB | K1:C1:breathing_after_consonant_start:rule_held_back | 5 | 5 |
| ENSEMBLE_AB | K1:C1:breathing_not_initial:impossible_by_rule | 1 | 1 |
| ENSEMBLE_AB | K1:C3:two_accents:rule_held_back | 28 | 28 |
| ENSEMBLE_AB | K1:C4:circumflex_before_penult:impossible_by_rule | 3 | 3 |
| ENSEMBLE_AB | K1:C4:grave_not_final:impossible_by_rule | 7 | 7 |
| ENSEMBLE_AB | detector_clipped_bottom | 404 | 148 |
| ENSEMBLE_AB | detector_clipped_top | 979 | 230 |
| ENSEMBLE_AB | detector_localisation_unknown | 134 | 135 |
| ENSEMBLE_AB | detector_segmentation_uncertain | 316 | 313 |
| ENSEMBLE_AB | detector_unnamed_mark | 93 | 87 |
| ENSEMBLE_AB | edit_guard:unsupported_character:0 | 41 | 41 |
| ENSEMBLE_AB | edit_guard:unsupported_character:1 | 28 | 28 |
| ENSEMBLE_AB | edit_guard:unsupported_character:14 | 40 | 40 |
| ENSEMBLE_AB | edit_guard:unsupported_character:16 | 39 | 39 |
| ENSEMBLE_AB | edit_guard:unsupported_character:41 | 43 | 43 |
| ENSEMBLE_AB | edit_guard:unsupported_character:53 | 57 | 57 |
| ENSEMBLE_AB | edit_guard:unsupported_character:6 | 38 | 38 |
| ENSEMBLE_AB | edit_guard:unsupported_character:60 | 61 | 61 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:0 | 41 | 41 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:1 | 28 | 28 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:14 | 40 | 40 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:16 | 39 | 39 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:41 | 43 | 43 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:53 | 57 | 57 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:6 | 38 | 38 |
| ENSEMBLE_AB | edit_guard:unsupported_raw_character:60 | 61 | 61 |
| ENSEMBLE_AB | ensemble_ab_mark_set_disagreement | 30 | 30 |
| ENSEMBLE_AB | r1_B_evidence_UNKNOWN | 2 | 2 |
| ENSEMBLE_AB | r1_B_missing | 6 | 6 |
| ENSEMBLE_AB | r1_B_uncertainty:out_of_image_span | 2 | 2 |
| ENSEMBLE_AB | r1_B_unscored:width_outside_0.2_2.0_median_ctc | 6 | 6 |
| ENSEMBLE_AB | r1_evidence_UNKNOWN | 2 | 2 |
| ENSEMBLE_AB | r1_missing | 6 | 6 |
| ENSEMBLE_AB | r1_uncertainty:out_of_image_span | 2 | 2 |
| ENSEMBLE_AB | r1_unscored:width_outside_0.2_2.0_median_ctc | 6 | 6 |
| PRESENCE | K1:C1:breathing_after_consonant_start:rule_held_back | 5 | 5 |
| PRESENCE | K1:C1:breathing_not_initial:impossible_by_rule | 1 | 1 |
| PRESENCE | K1:C3:two_accents:rule_held_back | 28 | 28 |
| PRESENCE | K1:C4:circumflex_before_penult:impossible_by_rule | 3 | 3 |
| PRESENCE | K1:C4:grave_not_final:impossible_by_rule | 7 | 7 |
| PRESENCE | detector_clipped_bottom | 404 | 148 |
| PRESENCE | detector_clipped_top | 979 | 230 |
| PRESENCE | detector_localisation_unknown | 134 | 135 |
| PRESENCE | detector_segmentation_uncertain | 316 | 313 |
| PRESENCE | detector_unnamed_mark | 93 | 87 |
| PRESENCE | edit_guard:unsupported_character:0 | 41 | 41 |
| PRESENCE | edit_guard:unsupported_character:1 | 28 | 28 |
| PRESENCE | edit_guard:unsupported_character:14 | 40 | 40 |
| PRESENCE | edit_guard:unsupported_character:16 | 39 | 39 |
| PRESENCE | edit_guard:unsupported_character:41 | 43 | 43 |
| PRESENCE | edit_guard:unsupported_character:53 | 57 | 57 |
| PRESENCE | edit_guard:unsupported_character:6 | 38 | 38 |
| PRESENCE | edit_guard:unsupported_character:60 | 61 | 61 |
| PRESENCE | edit_guard:unsupported_raw_character:0 | 41 | 41 |
| PRESENCE | edit_guard:unsupported_raw_character:1 | 28 | 28 |
| PRESENCE | edit_guard:unsupported_raw_character:14 | 40 | 40 |
| PRESENCE | edit_guard:unsupported_raw_character:16 | 39 | 39 |
| PRESENCE | edit_guard:unsupported_raw_character:41 | 43 | 43 |
| PRESENCE | edit_guard:unsupported_raw_character:53 | 57 | 57 |
| PRESENCE | edit_guard:unsupported_raw_character:6 | 38 | 38 |
| PRESENCE | edit_guard:unsupported_raw_character:60 | 61 | 61 |
| PRESENCE | mark_kind_disagreement | 612 | 616 |
| PRESENCE | r1_evidence_UNKNOWN | 2 | 2 |
| PRESENCE | r1_missing | 6 | 6 |
| PRESENCE | r1_uncertainty:out_of_image_span | 2 | 2 |
| PRESENCE | r1_unscored:width_outside_0.2_2.0_median_ctc | 6 | 6 |

For the base 200, SF4-relevant clipping veto incidences are **1,073→283**, compared with raw clipping predicates **2,269→650**. Zone relevance explains the difference. [Per-wave exact slot counts](L1M_evidence/slot_hold_reasons.csv); [additional original-label line guards](L1M_evidence/line_guards.csv). Line guards are counted separately and still participate in held-line outcomes.

## Source-record strata

| Wave | Foreign removal | N | Localisation | Segmentation | Clipping | AB held |
| --- | --- | --- | --- | --- | --- | --- |
| round1 | none | 11 | 10→10 | 22→22 | 17→14 | 11→11 |
| round1 | small | 45 | 36→37 | 64→63 | 495→163 | 45→32 |
| round1 | large | 22 | 8→8 | 18→16 | 506→149 | 22→19 |
| round1 | unknown | 1 | 0→0 | 0→0 | 16→0 | 1→0 |
| round1 | matching_failed | 1 | 0→0 | 0→0 | 30→30 | 1→1 |
| round2 | none | 5 | 7→7 | 9→9 | 2→0 | 5→4 |
| round2 | small | 40 | 13→13 | 23→23 | 380→100 | 40→27 |
| round2 | large | 15 | 2→2 | 14→14 | 310→66 | 15→13 |
| mixed | none | 18 | 10→10 | 28→28 | 23→20 | 18→17 |
| mixed | small | 29 | 27→27 | 41→41 | 262→56 | 29→22 |
| mixed | large | 11 | 3→3 | 21→21 | 209→40 | 11→10 |
| mixed | unknown | 2 | 0→0 | 0→0 | 19→12 | 2→2 |
| vouli | none | 4 | 0→0 | 8→8 | 27→20 | 4→4 |
| vouli | small | 22 | 12→12 | 32→32 | 207→92 | 22→20 |
| vouli | large | 32 | 4→4 | 34→34 | 430→93 | 32→28 |
| vouli | unknown | 1 | 0→0 | 0→0 | 11→4 | 1→1 |
| vouli | matching_failed | 1 | 2→2 | 2→2 | 3→3 | 1→1 |
| ALL evaluated | none | 38 | 27→27 | 67→67 | 69→54 | 38→36 |
| ALL evaluated | small | 136 | 88→89 | 160→159 | 1344→411 | 136→101 |
| ALL evaluated | large | 80 | 17→17 | 87→85 | 1455→348 | 80→70 |
| ALL evaluated | unknown | 4 | 0→0 | 0→0 | 46→16 | 4→3 |
| ALL evaluated | matching_failed | 2 | 2→2 | 2→2 | 33→33 | 2→2 |

| Audit stratum | N | Localisation | New failed starts | AB held |
| --- | --- | --- | --- | --- |
| audit unknown | 6 | 2→2 | 0 | 6→5 |
| own loss >0 | 9 | 4→4 | 0 | 9→7 |
| own measured zero | 245 | 128→129 | 4 | 245→200 |

| Own-loss line | Wave | Own px lost | New localisation starts | AB |
| --- | --- | --- | --- | --- |
| 3cb3c1caf7324ded3b11c1e5-p000024-l0044 | round1 | 10 | [] | hold→hold |
| 3cb3c1caf7324ded3b11c1e5-p000034-l0043 | round1 | 1 | [] | hold→corrected |
| 3598ebd512fe5593fddcc4ed-p000024-l0084 | round2 | 5 | [] | hold→hold |
| 3598ebd512fe5593fddcc4ed-p000030-l0044 | round2 | 5 | [] | hold→hold |
| 3598ebd512fe5593fddcc4ed-p000057-l0081 | round2 | 18 | [] | hold→hold |
| b4266bf58120943ab8864b23-p002659-l0026 | mixed | 15 | [] | hold→hold |
| 2495f1aad484-p000001-l0111 | vouli | 15 | [] | hold→hold |
| 838d5080b03f-p000008-l0029 | vouli | 73 | [] | hold→unchanged |
| 8c8a53ab3dd7-p000006-l0010 | vouli | 12 | [] | hold→hold |

For the base 200, none of the six own-loss lines gains a new localisation failure. All four new failed starts are on measured-zero-loss lines. The mask can change thresholding, component roles and geometry even when this aggregate audit reports zero own-pixel loss; the saved counts do not establish the mechanism of each new failure.

## Border blobs: exhaustive mapping, ownership unresolved

| Wave | Edge | Flags before | After | New flags | Neighbour flags | Own flags | Undecidable flags | Unique edge blobs | Blobs edge fully cleared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | top | 543 | 94 | 1 | 0→0 | 0→0 | 543→94 | 545 | 462 |
| round1 | bottom | 521 | 262 | 0 | 0→0 | 0→0 | 521→262 | 500 | 234 |
| round2 | top | 389 | 80 | 2 | 0→0 | 0→0 | 389→80 | 372 | 298 |
| round2 | bottom | 303 | 86 | 2 | 0→0 | 0→0 | 303→86 | 245 | 172 |
| mixed | top | 275 | 40 | 1 | 0→0 | 0→0 | 275→40 | 247 | 223 |
| mixed | bottom | 238 | 88 | 0 | 0→0 | 0→0 | 238→88 | 204 | 126 |
| vouli | top | 348 | 104 | 5 | 0→0 | 0→0 | 348→104 | 302 | 220 |
| vouli | bottom | 330 | 108 | 3 | 0→0 | 0→0 | 330→108 | 284 | 195 |
| ALL evaluated | top | 1555 | 318 | 9 | 0→0 | 0→0 | 1555→318 | 1466 | 1203 |
| ALL evaluated | bottom | 1392 | 544 | 5 | 0→0 | 0→0 | 1392→544 | 1233 | 727 |

Blob attribution denominator: **2699 unique (line, crop-edge, native-label) blobs**, each counted once even if it triggers several letter flags. Confirmed neighbour 0 (0%), confirmed own 0 (0%), undecidable 2699 (100%). These zeros mean **no confirmed attribution**, not absence of neighbour/own ink. Flag and blob denominators are different; exact pixel lists and slot-to-blob joins are in `border_flags.jsonl.gz` and `border_blobs.jsonl.gz`.

**Interpretation required by the ownership contract:** Neighbour-owned border blobs would make their flag removal a legitimate consequence of masking. Own-line accents/breathings touching a tight top, or descenders touching the bottom, require crop padding at cut time; masking cannot restore missing own-line pixels. Both ownership counts are currently unmeasured (0 confirmed in either class). The measured own-pixel-loss audit is not a border-ownership map and cannot substitute for those numbers.

## Twelve-panel visual check

**Verdict flips, 12 panels:** [1–3](L1M_evidence/flip_panels/sheet_1.png), [4–6](L1M_evidence/flip_panels/sheet_2.png), [7–9](L1M_evidence/flip_panels/sheet_3.png), [10–12](L1M_evidence/flip_panels/sheet_4.png); [selection](L1M_evidence/flip_visual_selection.json). All twelve lines flip AB from hold to kept.

**Border check, 12 panels:** [1–3](L1M_evidence/panels/sheet_1.png), [4–6](L1M_evidence/panels/sheet_2.png), [7–9](L1M_evidence/panels/sheet_3.png), [10–12](L1M_evidence/panels/sheet_4.png); [selection](L1M_evidence/visual_selection.json). These cover six cleared and six persistent SF4-relevant border flags; ownership remains undecidable, so this is not the requested confirmed neighbour/own split.

Each composite shows the complete original/masked crop, a native-pixel zoom, and actual detector component pixels tinted inside their letter partitions. Boxes show the letter bounds; blue is other letters, magenta the target, red its clipping predicate window. Every selected flag is an active SF4 AB veto before masking; persistent examples remain active after masking.

I inspected all four final verdict-flip sheets and all four final border sheets, including the native-pixel zooms and tinted detector component pixels. The flip suite contains 12 distinct lines (four per wave). The border suite contains six cleared and six persistent SF4-relevant clipping predicates, with one top and one bottom example per wave in each group. These are targeted witnesses, not a random accuracy sample.

| Flip panel | Visible observation |
| --- | --- |
| 1 | Detached dark strokes at the top above the target iota/adjacent alpha vanish; the visible letter bodies and current accent remain. |
| 2 | An isolated top-edge speck over the `τοῦ` area vanishes; the visible circumflex and body remain. |
| 3 | Bottom-edge crumbs below the `κτῆμα` area disappear; the eta body remains. |
| 4 | Border debris disappears in an AB-corrected line whose audit reports **1 own pixel lost**. The zoom does not locate that lost pixel, so this accepted correction is not a demonstrated lossless mask. |
| 5 | A faint horizontal top-edge trace disappears while the visible grave above alpha remains. |
| 6 | Top-edge traces above the epsilon window disappear; the detached current accent remains visible. |
| 7 | A small bottom-edge trace below eta disappears. |
| 8 | On dark paper, bottom blobs disappear while the visible omega body remains; this is a contrast-sensitive witness. |
| 9 | A top dot disappears; the nearby breathing and upsilon body remain visible. |
| 10 | A tiny top-edge speck disappears although the source's *audited foreign-pixel removal* count is zero. This demonstrates that the source audit count and applied mask are different measurements. |
| 11 | Small bottom-edge traces below alpha disappear; the body remains visible. |
| 12 | A small bottom-edge trace disappears; the target alpha's body remains visible. |

| Persistent-border panel | Visible observation |
| --- | --- |
| 7 | Much of the heavy top-edge material disappears, but pale residual border material remains and the clipping predicate survives. |
| 8 | The crop visibly cuts through the lower body band; removing scattered specks leaves the bottom predicate active. |
| 9 | A tall adjacent letter shape reaches the top inside the target's clipping window and remains after masking. |
| 10 | The target eta's lower stroke reaches the bottom boundary and remains after masking. |
| 11 | On low-contrast paper, faint top-boundary material survives; the detector still flags the top. |
| 12 | Top-edge debris is removed, but the target's lower body reaches the crop bottom and the bottom veto persists. |

The six cleared-border panels repeat flip witnesses and were checked in the border suite as well. These images support the recorded disappearance/persistence of border ink and show why removing some debris need not clear a line. They do **not** establish `_voronoi_keep` ownership. All semantic neighbour/own attributions remain undecidable; the tight-cut examples are padding candidates, not confirmed own-line counts. I did not adjudicate the 14 new corrected labels against full-page print truth.


## Reading against the SF4 population census

Census input: [AB_SF4_SUMMARY.md](L1C_census_3679781/AB_SF4_SUMMARY.md), SHA-256 `5903ae968ff1aecb9f9e306f717c239ca8bd5cd21c03823c2bd6827fa84fa0f8`; [CENSUS.json](L1C_census_3679781/CENSUS.json), SHA-256 `08a1326e258926eb761f6546fdbd897156b6e1703f757ead3c77a01ff922b4b1`. The summary below is included verbatim to preserve the population context.

<details>
<summary>Full supplied census summary</summary>

# L1C census (job 3679781) — ENSEMBLE_AB under sf4-release-v1, per wave (lines)

Source: `CENSUS.json` (sha in `receipt.json`), L1R 3679725 outputs. "Clipping-only" = lines whose exact reason set ⊆ {clipped_top, clipped_bottom},
summed over the top-10 exact sets (a lower bound). "With X" = lines carrying reason X at any slot (not exclusive).

| Wave | Lines | Held | Clipping-only (≥) | with clipped_top | with localisation_unknown | with segmentation_uncertain | A/B disagreement | Sole reason, top 3 |
|---|---|---|---|---|---|---|---|---|
| parliament | 27,224 | 26,927 (98.9%) | 1,385 (5.1%) | 20,688 | 22,524 | 24,024 | 1,653 | clipped_top 547, clipped_bottom 183, seg_unc 84 |
| vouli | 23,088 | 22,389 (97.0%) | 6,338 (27.5%) | 19,927 | 6,681 | 9,943 | 1,575 | clipped_top 1,880, clipped_bottom 551, unnamed 148 |
| round1 | 43,869 | 37,901 (86.4%) | 12,883 (29.4%) | 29,544 | 10,779 | 16,074 | 4,277 | clipped_top 4,475, clipped_bottom 1,209, seg_unc 862 |
| round2 | 17,026 | 13,913 (81.7%) | 5,297 (31.1%) | 10,763 | 2,914 | 5,153 | 1,426 | clipped_top 1,916, clipped_bottom 511, seg_unc 381 |
| mixed | 13,227 | 11,465 (86.7%) | 4,081 (30.9%) | 8,844 | 3,355 | 5,101 | 1,252 | clipped_top 1,454, clipped_bottom 342, seg_unc 297 |
| openarchives | 235 | 194 | 113 | 120 | 0 | 38 | 16 | clipped_bottom 27, clipped_top 25, A/B 12 |
| ALL | 124,669 | 112,789 (90.5%) | 30,280 (24.3%) | 89,886 | 46,253 | 60,333 | — | — |

Top exact sets overall: {clipped_bottom, clipped_top} 17,160; {clipped_bottom, clipped_top, localisation_unknown, segmentation_uncertain} 10,379;
{clipped_top} 10,297; {clipped_top, localisation_unknown, segmentation_uncertain} 6,692; {clipped_bottom, clipped_top, unnamed} 4,760.

Reading: under sf4 the line-level driver is CLIPPING (72% of lines carry clipped_top), with localisation/segmentation second and dominant only
on parliament. This corrects the L1H pilot reading ("localisation_unknown dominates"), which counted slot entries on 1,024 rows under the
pre-SF4 gate. Clipping is exactly what neighbour-line ink at the crop border would produce, so the masking test measures the main driver.

</details>

The census counts detailed SF4 line reasons: 89,886 lines carry clipped_top; at least 30,280 are clipping-only. The older 1,024-row pilot counted broad pre-SF4 reason entries, which folded clipping into localisation_unknown. It cannot establish localisation as the SF4 population driver. This paired sample independently shows clipping falls sharply while localisation persists.

### Conditional projections (scenarios, not release authorisation)

For each wave and category, estimate = census known-category lower bound × observed sample fraction fully released by AB. Clipping-only means a nonempty exact reason set contained in {top,bottom}; clipping+localisation means at least one clipping reason and localisation_unknown, allowing other holds. Census category sizes below sum qualifying top-ten exact reason sets only, so they are lower bounds. Wilson 95% binomial intervals illustrate sampling uncertainty; they do not correct sample selection, clustered pages, missing ownership or census truncation. No extrapolation uses the overall 21% release rate.

| Wave | SF4 category | Known population ≥ | Sample N | Released | Conditional lines released | 95% scenario range |
| --- | --- | --- | --- | --- | --- | --- |
| round1 | clipping_only | 12883 | 26 | 16 | 7928 | 5,480–9,994 |
| round1 | clipping_plus_localisation | 3635 | 19 | 0 | 0 | 0–611 |
| round2 | clipping_only | 5297 | 27 | 14 | 2747 | 1,800–3,669 |
| round2 | clipping_plus_localisation | 870 | 5 | 0 | 0 | 0–378 |
| mixed | clipping_only | 4081 | 19 | 9 | 1933 | 1,115–2,787 |
| mixed | clipping_plus_localisation | 1070 | 9 | 0 | 0 | 0–320 |
| vouli | clipping_only | 6338 | 12 | 6 | 3169 | 1,608–4,730 |
| vouli | clipping_plus_localisation | 3685 | 9 | 0 | 0 | 0–1,102 |
| parliament | clipping_only | 1385 | 0 | 0 | no projection | unsampled |
| parliament | clipping_plus_localisation | 13926 | 0 | 0 | no projection | unsampled |
| openarchives | clipping_only | 113 | 0 | 0 | no projection | unsampled |
| openarchives | clipping_plus_localisation | 0 | 0 | 0 | no projection | unsampled |

Across the three evaluated waves, the clipping-only scenario sums to approximately **12,608** released lines out of the known 22,261 clipping-only lines, based on **39/72** sample releases. Clipping+localisation has **0/33** sample releases; its zero point estimates have wide uncertainty, not a proven zero population effect.

Assumptions: these pre-SF4-held sampled lines represent the same wave and exact SF4 reason category in the census; the sourcing matcher/mask quality, own-loss rate, reader coverage and other gate inputs transfer to that category; masking is applied without new ownership errors; and the frozen readers remain fixed as here. The sample was stratified by wave, not by SF4 reason set or foreign-ink amount, and excludes already-kept lines. These scenarios therefore do not measure population precision, final kept-label correctness, or the release effect of retraining/rerunning the readers. No estimate is made for parliament; vouli is pending until evaluated.

## Reproduce / append vouli

From the workspace root, with networking permitted only for the bounded selected Clariden extraction:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python docs/records/labelfix/spellcheck/L1M_evidence/run_pair.py --sample vouli
```

This requires a completed vouli receipt with all 60 selected records. It reuses the saved C1 alignments where available, fetches only missing selected evidence, saves vouli separately and rebuilds this report including both strata. It never reruns the 200 detector pairs unless explicitly requested with `--sample 200 --refresh`. If vouli staging is absent/incomplete, it reports pending and preserves the report.

## Evidence and limits

- [200-line run receipt](L1M_evidence/200/receipt.json), [per-line results](L1M_evidence/200/lines.jsonl.gz), [all per-letter records](L1M_evidence/200/slots.jsonl.gz), [detector, gate and overlays](L1M_evidence/200/details.jsonl.gz), native pixel arrays under `200/pixels/`.
- [Every original border flag](L1M_evidence/200/border_flags.jsonl.gz), [deduplicated border blobs with native pixel coordinates](L1M_evidence/200/border_blobs.jsonl.gz). These identify which blob caused which flag; ownership remains undecidable.
- [Validation receipt](L1M_evidence/validation.json), [staging inventory and record schema](L1M_evidence/staging_inventory.json), and [visual review](L1M_evidence/visual_review.md). Validation checks every original flag-to-blob join, every saved native blob pixel, all mode-to-overlay reason joins, both original-crop gate projections and the absent-vouli command.
- [Read-only Clariden extractor](L1M_evidence/fetch_selected.py), [fetch log](L1M_evidence/fetch_200_log.json), [selected evidence](L1M_evidence/remote_200.json.gz), [paired driver](L1M_evidence/run_pair.py), [report builder](L1M_evidence/build_report.py). The first extraction had a crop-key join error (full document IDs vs shortened crop directory IDs); it stopped after 41 seconds without output. The corrected extraction took 31 seconds. No auth/cert error occurred, no cert refresh, submission or remote write occurred. Full source-shard hashes were not recomputed; shard receipts were read and selected A fields compared exactly.
- All 200 lines were held under the original L1E gate and are also held under the recomputed SF4 baseline. One failed match and all unknown audits are included. No independent accuracy/precision claim follows from reader agreement or gate acceptance.
- Ownership percentages and the neighbour/own visual split require the missing saved pixel ownership masks/curves. That evidentiary limit cannot be repaired by relabelling removed pixels as foreign or retained pixels as own.

L1M RESULT: 260 lines (masked 258, matching-failed 2); localisation_unknown slots 134→135; segmentation_uncertain 316→313; clipping 2947→862 (border blobs neighbour 0% / own 0% / undecidable 100%); AB lines held 260/260→212/260, corrected 0→14 (released-unchanged 0→34); PRESENCE 260→242; verdict: partial

## Coordinator rulings on L1M (17 Oct, recorded by the track lead)
- **No L1 rerun on masked crops yet.** It waits for (a) the owner's go on masking all of v2 (a multi-hour Mac run he has not approved) and
  (b) the print audit of masking-released corrections (the 14 here + a seeded vouli sample; two blind readers + controls, S2 method), which
  is the precision number for masking-released lines and gates any rerun.
- **Ownership attribution** is re-measured when the sourcing lead's per-pixel ownership maps land (`l1e_sample_r4`, `l1e_sample_vouli_r2`):
  the applied mask = every ink pixel `_voronoi_keep` does not keep for this line (neighbour-above / neighbour-below / no detector row);
  the audit's "foreign" count is only components assigned to another row, which explains panel 10.
- **Padding at cut time** is the owner's decision; the number for it (lines whose own letter bodies touch the crop top/bottom, panels 8/10/12
  pattern) is counted on the 200 + 60 from those ownership maps.
- **S8** (detector localisation/segmentation on the training-wave DEV) goes now.

Note (track lead): the RESULT line's AB/PRESENCE figures were hand-corrected to the 260-line totals (the generator printed the 200-line values; vouli: AB 60→54, 0 corrected, 6 unchanged; PRESENCE 60→58).

## L1M2 — Border ownership and padding decision input (17 October 2026)

**Attribution is now measured against the supplied ownership maps.** All **2,699 original (line, edge, native-label) border blobs** and all **2,947 original slot-edge flags** are joined to aligned native ownership pixels. **100/260 lines** have retained class-1 pixels at an SF4-relevant crop edge; **27/260** have no other remaining ENSEMBLE_AB hold. These are the requested **map-based candidate counts**, not demonstrated successful recuts or a semantic certification that every retained class-1 speck is part of a letter. There are **zero class-5 pixels or flags** in these 260 maps.

The two `identity_ambiguous` maps label all foreground as class 1 (`keep_basis=identity_unmasked`), so they cannot certify own-row identity. Excluding them gives **98/260 attributed candidate lines** and still **27/260 sole-hold candidates**. The failed identities are `b963a5d59be557e9eef8498b-p000042-l0020` (round1, 12 relevant class-1 flags) and `17cbdf94881f-p000002-l0015` (vouli, 2 flags). Neither is a sole-hold candidate. The mandatory RESULT line below uses the literal supplied-class definition (100), with this qualification.

### Alignment, custody and frozen semantics

All 200 r4 and 60 vouli-r2 ownership PNGs are 8-bit `L`, have exactly the original/masked crop dimensions, and match their exported ownership hashes and class histograms. The original PNG hashes match the L1M source records. Each r4/vouli-r2 masked PNG is byte-identical to its r3/vouli predecessor, the matching `comparison.json` entry and the saved L1M masked hash (**260/260**); comparison `lines.jsonl` hashes match the original L1M run receipts. The class-2/3/4 union reproduces every applied mask hash, and no grayscale pixel changes outside that union. [Per-line alignment receipt](L1M_evidence/ownership/alignment.csv), [all input hashes](L1M_evidence/ownership/input_hashes.json).

No reader, `read_ink`, gate recomposition, detector-code edit or network access ran. Native ink/labels and crop-wide clipping x-height were reconstructed with the recorded `ink.analyse` + S5 `case.estimate_font` code/model on the 520 already-saved crop variants; both ink masks and component-label arrays are bit-identical to L1M. Every original clipping window reproduces exactly. SF4 relevance and all AB reasons/line guards come directly from the saved `sf4-release-v1` modes and overlays. The neighbouring checkout now differs in `release_gate.py`, `text.py` and `l1_common.py`; none of that current changed code was executed. The S5 model loader indirectly imports text constants, so the historical committed `text.py` was loaded in memory and verified against its L1M hash. [Analysis script](L1M_evidence/ownership/analyse.py), [run log](L1M_evidence/ownership/run.log).

### Exhaustive blob attribution

Each blob is classified over **all of its saved native pixels**, including class-0 pixels in the denominator. A class wins at **≥80%**; otherwise the blob is mixed. Class-0 majority also stays mixed/unattributed, because class 0 is background in the sourcing map rather than an own/foreign ink assertion. The complete six-way pixel counts/fractions and a separate edge-only split are saved for every blob. If a flag joins several blobs, it receives their class only when all blob classes agree; otherwise it is mixed. Flags are counted once. [All blob pixels and splits](L1M_evidence/ownership/border_blobs.jsonl.gz), [all original flags and joins](L1M_evidence/ownership/border_flags.jsonl.gz).

| Wave | Blobs | Above | Below | Unowned | Own | Ring | Mixed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 1045 | 159 | 66 | 102 | 311 | 0 | 407 |
| round2 | 617 | 71 | 43 | 86 | 131 | 0 | 286 |
| mixed | 451 | 64 | 30 | 75 | 71 | 0 | 211 |
| vouli | 586 | 64 | 46 | 131 | 118 | 0 | 227 |
| ALL | 2699 | 358 | 185 | 394 | 631 | 0 | 1131 |

Across 2,699 blobs: **543 neighbour (20.12%)**, **394 unowned (14.60%)**, **631 own (23.38%)**, **0 ring-abstained (0.00%)**, **1,131 mixed (41.90%)**. The denominator counts an original native component once per touched edge, exactly as L1M did; it is neither a flag count nor a character count. Class 0 accounts for 5,362/108,483 blob-pixel incidences (4.94%); those pixels are not silently reassigned to ink ownership.

### Before → after masking by original flag attribution

Each arrow tracks the **same original (line, slot start, edge) predicate**. A surviving predicate can be triggered by a different blob after masking. The `New` column adds newly flagged slots; therefore the six after columns plus `New` equal the actual masked total. Ring is 0→0 for every row. Full counts, including SF4 relevance, are in [flag transitions](L1M_evidence/ownership/flag_transitions.csv).

| Wave | Edge | Above | Below | Unowned | Own | Mixed | New | Raw total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | top | 133→7 | 0→0 | 43→0 | 61→61 | 306→25 | 1 | 543→94 |
| round1 | bottom | 0→0 | 67→3 | 43→0 | 233→233 | 178→26 | 0 | 521→262 |
| round2 | top | 65→2 | 0→0 | 44→0 | 67→67 | 213→9 | 2 | 389→80 |
| round2 | bottom | 0→0 | 55→0 | 44→0 | 76→76 | 128→8 | 2 | 303→86 |
| mixed | top | 60→4 | 0→0 | 43→5 | 9→9 | 163→21 | 1 | 275→40 |
| mixed | bottom | 0→0 | 32→1 | 34→5 | 66→66 | 106→16 | 0 | 238→88 |
| vouli | top | 72→5 | 0→0 | 67→3 | 55→55 | 154→36 | 5 | 348→104 |
| vouli | bottom | 0→0 | 52→2 | 75→4 | 64→64 | 139→35 | 3 | 330→108 |
| ALL | top | 330→18 | 0→0 | 197→8 | 192→192 | 836→91 | 9 | 1555→318 |
| ALL | bottom | 0→0 | 206→6 | 196→9 | 439→439 | 551→85 | 5 | 1392→544 |

Original own-class flags persist **631/631**; original neighbour flags persist **24/536** and unowned flags **17/393**. Mixed flags persist **176/1,387**. In all, **2,099 original flags clear**, **848 survive** and **14 new flags** yield 862 masked flags. Reclassifying each masked flag’s own native blobs separately gives **637 own, 225 mixed, 0 neighbour/unowned/ring**; this second accounting is in [independent before/after counts](L1M_evidence/ownership/flag_counts_independent.csv) and [every masked flag](L1M_evidence/ownership/masked_border_flags.jsonl.gz). Raw 2,947→862 and SF4-relevant 1,383→378 exactly reproduce the 260-line L1M results.

### Expectation test and exceptions with identities

The proposed expectation is **not universally true**. All 631 original own-class flags persist, and no own-class flag clears. However, **1,211 cleared flags are mixed**, often a neighbour/unowned split rather than a single ≥80% class. **217 surviving flags** have an original class outside own/ring: **18 above, 6 below, 17 unowned, 176 mixed**. Mixed is an attribution result, not a failure to join the blob. Every exception retains its full line ID, slot start, edge, blob keys, original and masked window and surviving original edge split in [the exception ledger](L1M_evidence/ownership/exceptions.jsonl.gz); [readable identity index](L1M_evidence/ownership/exceptions.md).

The 41 above/below/unowned exceptions occur on **22 lines**. Their masked windows contain class-0 detector ink in all 41 cases: **40 background-only, one background+class-1**. In 15 cases an original border pixel survives, always label 0; in 26 cases none of the originally flagging edge pixels remains, but other pixels now satisfy the predicate (two have a shifted window, 24 have the same window). This distinguishes persistence of a Boolean flag from persistence of the original foreign blob. It is directly verified against saved native masks and maps; identifying the cause of each threshold change would require a separate detector analysis. Example IDs: `8b231047fdbd96ec30e1eded-p000033-l0013:16:top`, `290a133b0e55593eb4ecdcfd-p000027-l0053:13:top`, `2495f1aad484-p000001-l0111:14:top`; all 41 identities are enumerated in the linked index.

### Padding number and extent estimate

A padding candidate requires an actual **masked detector-ink pixel with ownership label 1 at y=0 or y=H−1**, inside that masked slot’s exact narrow clipping window, with a saved **SF4-relevant clipping hold**. This is a direct pixel query, not a whole-blob majority test: a mixed blob can contain the touching own pixels. All remaining AB slot reasons and original-label line guards participate in the sole-hold test. Clearing only these own-contact clipping predicates must leave an empty overlay hold list. This is an accounting counterfactual; the gate was not modified.

| Wave | N | Own-contact holds | Class-1 lines | Nonambiguous lines | Sole AB hold | Pure-own sole hold | Component median xh | Component median px | Line-max median xh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 80 | 121 | 34 | 33 | 8 | 8 | 0.350 | 3.40 | 0.578 |
| round2 | 60 | 78 | 28 | 28 | 8 | 8 | 0.408 | 5.00 | 0.570 |
| mixed | 60 | 34 | 17 | 17 | 8 | 7 | 0.461 | 6.45 | 0.550 |
| vouli | 60 | 57 | 21 | 20 | 3 | 2 | 0.592 | 16.00 | 0.748 |
| 200 | 200 | 233 | 79 | 78 | 24 | 23 | 0.385 | 4.70 | 0.564 |
| ALL | 260 | 290 | 100 | 98 | 27 | 25 | 0.408 | 6.40 | 0.598 |

Thus the literal class-1 padding input is **100/260 lines and 27/260 sole remaining AB holds** (base 200: **79 and 24**; vouli: **21 and 3**). Of 378 masked SF4 clipping holds, 290 contain class-1 border ink and 88 do not. The remaining 73 of those 100 lines have at least one other hold. Twenty-five sole-hold lines have exclusively class-1 edge pixels in every held clipping window. The other two are `b4266bf58120943ab8864b23-p001333-l0060` (mixed wave) and `838d5080b03f-p000007-l0015` (vouli), which also contain class-0 edge ink. Padding alone is therefore not established to remove every residual on these two lines. The complete [line census](L1M_evidence/ownership/lines.csv) preserves all hold reasons and both sole-hold definitions.

**Padding proxy, not recoverable missing height:** for each touching component, restrict its pixels to retained class 1, then measure `max(0, meanline−min_y)` at the top or `max(0, max_y+1−baseline)` at the bottom. Divide by the saved slot evidence `xh`; coordinates use half-open pixel boxes. Deduplicate by `(line, edge, masked native label)` and take the maximum across qualifying slot bands sharing that component. This yields **321 component-edge observations**, median **0.408 x-height / 6.40 px**, IQR **0.138–0.611 x-height**, P90 **0.942 x-height**. Fifty-one observations have zero extent because the saved band already reaches/passes the cropped component edge; zero does not prove no padding is needed. [All component bounds and slot-specific measurements](L1M_evidence/ownership/padding_components.jsonl.gz).

Taking the largest proxy per candidate line (so many touching letters do not overweight a line) gives median **0.598 x-height / 8.25 px**, IQR **0.470–0.786 x-height**, P90 **1.162 x-height** over 100 lines. Excluding the two ambiguous identities leaves 304 component observations with median **0.400 x-height / 6.20 px**. The RESULT line uses the requested touching-component median, **0.408**, not the line-max median. These measure visible extent outside the fitted body band; the original crop does not contain the missing continuation, so neither value is a measured sufficient recut padding. No recut, re-read or actual release is claimed.

**Letter/mark qualification:** the supplied map’s class 1 means ink kept by the row policy, not independently adjudicated print truth. Inspection confirms the old panels 8/10/12 body-cut pattern (new panels 5/6/7) and an own accent at the top (new panel 8), but also finds retained isolated specks and ornamental/background strokes in class 1. In particular, `2f9e996ffbdaaa3b4a9dfdcf-p000049-l0019` (new panel 9) is not a clean letter-only witness. The 100/98 counts are therefore exact under the supplied ownership-label contract; they must not be presented as 100/98 semantically verified letter-body/mark cuts, nor 27 verified padding rescues. Establishing that stricter physical count would require adjudicating those ambiguous components, rather than silently changing their exported ownership labels. The twelve requested panels plus all 100 candidate-line thumbnails were inspected; [visual observations and limits](L1M_evidence/ownership/visual_review.md).

### Ring abstention and inspected panels

**Ring abstention: 0 original blobs, 0 original flags, 0 masked flags, 0 SF4-relevant flags**, both overall and in each wave/edge stratum. The label-5 pixel count is also zero across all 260 full maps. The last four requested panels therefore show **mixed** witnesses; there are no ring examples to fabricate. Ring-abstained border ink would be a masking-policy input, but it contributes none of this sample’s measured holds. Class-0 residuals are a separate category.

The **12 distinct lines** comprise four neighbour-cleared (one per wave), four own-persistent (including old panels 8/10/12) and four mixed (two persistent, two cleared). Each panel shows original grayscale, original tinted ownership and masked surviving ownership, using nearest-neighbour native-pixel zooms. [Panels 1–3](L1M_evidence/ownership/panels/sheet_1.png), [4–6](L1M_evidence/ownership/panels/sheet_2.png), [7–9](L1M_evidence/ownership/panels/sheet_3.png), [10–12](L1M_evidence/ownership/panels/sheet_4.png); [selection and native bounds](L1M_evidence/ownership/visual_selection.json).

### Reproduction and validation

From this workspace, use the specified local Python with `PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1` to run `L1M_evidence/ownership/analyse.py`, then `panels.py`, `write_section.py` and `validate.py` (paths relative to this report’s directory). The first three write only ownership evidence; `write_section.py` produces `appendix.md` and never regenerates this report. The section was appended once, preserving the original byte prefix. [Validation receipt](L1M_evidence/ownership/validation.json), [validation script](L1M_evidence/ownership/validate.py), [output hashes](L1M_evidence/ownership/SHA256SUMS.txt). The sample remains 200 + 60, with vouli separate; no population extrapolation or downstream rerun follows from this analysis.

L1M2 RESULT: border blobs 2699: neighbour 20.12% / unowned 14.60% / own 23.38% / ring-abstained 0.00% / mixed 41.90%; own-ink clipping lines 100/260, sole remaining AB hold 27/260 (per wave round1 34/80, sole 8/80; round2 28/60, sole 8/60; mixed 17/60, sole 8/60; vouli 21/60, sole 3/60); padding estimate median 0.408 x-height
