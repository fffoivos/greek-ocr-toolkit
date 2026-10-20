# S6 — font-scaled segmentation and safe attached-mark zones

S6 improves physical mark presence and letter ownership; it is a candidate with residual misses and naming regressions. The fixed S4 mark model and S5 case model are unchanged. No naming retraining or optimisation was performed. All 137 labelfix tests pass.

Actual starting HEAD is `f4d95436fa266d0b0bf1e94ff064ecec4c5050e3`: two brief-only commits after S5 `eed80de9`. The frozen S4 (`afe67823`) and S5 predictions are both retained and their TP/FP/FN, known/unknown counts and every legacy slot/truth/bbox are asserted unchanged. No `.git` writes, network calls, CTC forward passes, GPU work, owner-page builds or publishing. Evaluation uses the requested Python with `PYTHONPATH=$PWD`; recogniser construction/forward and socket connections fail closed in the validator.

At delivery, HEAD is `3995aba0cbd24a71cac8168521a292a3645cb8e1`. It advanced externally during this run by a draft R0 brief commit adding only `docs/records/briefs/R0_recogniser_audit.md`; S6 runtime changes remain uncommitted. This agent made no `.git` writes.

## What changed

- The line font is fitted only from pixel-classified complete lowercase bodies: robust median x-height and a clipped linear baseline fit. Capitals, ascenders and descenders do not set that body band. The expected width is the median complete-body pixel width, scaled for narrow iota and wide omega/mu. Absolute span overlap is normalised by pixel width, avoiding assignment of a narrow iota to the preceding wide alpha.
- Shared components wider than 1.3 expected widths are partitioned at CTC boundaries, refined to minimum body-column ink within ±0.25 expected width. Narrow shared components get explicit uncertain regions, not silent mark suppression. The S4 disconnected-stroke union is retained. Every recogniser alphabetic character has one region; unlocated font/CTC fallback regions remain flagged and are still searched. No new character comes from Google.
- S5 per-word lowercase height substitution is reverted: words use the robust line font. The combined case decision controls capital side searches and capital-run heights. Runs with ≥80% classified capitals retain their median capital height. `word_lowercase_bodies` remains the compatibility source label when local bodies support a word, but its height is the line font.
- Lowercase attached marks are cut at floor(meanline), detached upper evidence is intersected with that zone, and subscripts start at ceil(baseline). Letter masks/labels remain immutable. A fused-letter boundary does not slice an upper accent: its complete upper connected component is proposed, and overlapping proposals with the same native label are credited once.
- Certified vowel/rho regions protect their strokes from the punctuation-dot veto. Rho is also exempted from the S5 ascender/descender top-mark veto; the DEV joined-breathing loss is recovered. Case retains the fixed model in original and corrected pixel coordinates plus font geometry; both are pixel-only views. A narrow lowercase mark bearer retains its recogniser case when an attached lobe looks like a serif capital. This prior is explicit, and the conflicting pixel decision is retained.

Font fits: {'pixel_lowercase_bodies': 1243, 'frozen_line_fallback': 21} across 1264 evaluation lines. Fallbacks are exposed, not called successful font estimates. Runtime inputs are pixels, recogniser letters/case and cached locations only. Print truth and owner notes enter only evaluation.

## Physical presence/location, S4 → S5 → S6

An event is a mark at a recogniser character in one of three zones: above, below, or elision after it. Any upper ink counts regardless of naming, and a connected compound counts as one presence event. Presence requires evidence, not a predicted mark name. Character truth uses the existing adjudicated print words with exact base-letter agreement; unknowns stay unknown. This extends truth to fused characters that the frozen component table cannot score. It is a separate fixed denominator, not a replacement for that table.

| split / stratum | characters (known / unknown) | S4 P/R | S5 P/R | S6 P/R |
|---|---:|---:|---:|---:|
| heldout / all | 20425 (19249 / 1176) | 98.5%/89.4% | 98.6%/89.0% | 98.7%/95.4% |
| heldout / fused | 756 (651 / 105) | —/0.0% | —/0.0% | 97.0%/60.5% |
| heldout / clean | 19669 (18598 / 1071) | 98.5%/92.8% | 98.6%/92.5% | 98.7%/96.8% |
| heldout / merged_accent | 590 (534 / 56) | 95.4%/89.0% | 96.5%/85.9% | 95.4%/93.5% |
| heldout / breathing | 927 (927 / 0) | 100.0%/92.0% | 100.0%/91.7% | 100.0%/97.0% |
| heldout / compound | 478 (478 / 0) | 100.0%/92.7% | 100.0%/92.1% | 100.0%/96.4% |
| dev / all | 11921 (11149 / 772) | 97.1%/80.8% | 97.2%/79.5% | 97.6%/91.8% |
| dev / fused | 1256 (1173 / 83) | —/0.0% | —/0.0% | 96.5%/77.3% |
| dev / clean | 10665 (9976 / 689) | 97.1%/89.1% | 97.2%/87.7% | 97.6%/93.3% |
| dev / merged_accent | 622 (582 / 40) | 93.8%/80.1% | 95.0%/73.2% | 93.3%/87.8% |
| dev / breathing | 560 (560 / 0) | 100.0%/85.2% | 100.0%/82.0% | 100.0%/91.6% |
| dev / compound | 157 (157 / 0) | 100.0%/82.2% | 100.0%/79.6% | 100.0%/91.1% |
| capitals combined (held-out agreement) | 18960 | 36.6%/100.0% | 95.6%/98.7% | 96.1%/98.6% |
| capitals pixel-only (held-out agreement) | 18960 | 13.8%/27.8% | 83.2%/45.3% | 83.3%/46.9% |

Held-out fusion: 370 source components, 756 recogniser characters; 651 have known print truth. Source-sharing is an operational geometry cohort, not a new manual certification of all touching glyphs. Narrow uncertain partitions are retained in the line receipt. Before precision is undefined because S4/S5 proposed no marks on this cohort; it is not zero precision.
Merged-accent cohort: 590 held-out mark-bearer regions whose native component spans a body and a substantial upper lobe (534 known). The cohort is selected from native labels and the common S6 font boundary, independently of a detector's accepted marks. It is a reproducible geometry proxy; not all members have manual merged-ink truth. DEV breathing/compound rows measure top presence on positive strata only, so their displayed P=100% is conditional; global precision is the `all` row.

## Capitals and the prior

Truth is the frozen S5 agreement set: 18,960 held-out component slots, 1,189 capitals. Google/recogniser case agreement is an evaluation instrument, never runtime evidence. S4 combined is its recorded uppercase-or-height rule; the S4 pixel-only row recomputes its height branch without the recogniser uppercase term. S6 pixel-only is the fixed case model in two pixel normalisations plus font geometry. It remains weak in recall. Combined classification drives side-mark search and capital-run height; pixel-only is reported separately and is not claimed to replace the prior.

| capital diagnostic | S4 P/R | S5 P/R | S6 P/R |
|---|---:|---:|---:|
| combined, all 18,960 | 36.6%/100.0% | 95.6%/98.7% | 96.1%/98.6% |
| pixel-only, all 18,960 | 13.8%/27.8% | 83.2%/45.3% | 83.3%/46.9% |
| combined, frozen 753 disagreements | 93.9%/100.0% | 92.4%/98.1% | 94.6%/98.0% |
| pixel-only, frozen 753 disagreements | 12.5%/0.9% | 0.0%/0.0% | 18.6%/3.3% |

The disagreement stratum is exactly the original 753 slots, not reselected after S6. Raw normalised class, original-coordinate pixel class, geometric decision, final class, case disagreement and recogniser case remain in `S6_lines.jsonl.gz`. Individual capital outcomes are in [S6_capital_truth.jsonl](S6_capital_truth.jsonl). Combined recall loses one additional agreement capital against S5; it is not presented as no-regression.

## Safe zones and native witnesses

Upper boxes crossing their own permitted vertical boundary (excluding capital side boxes): held-out 471 → 473 → 0; DEV 525 → 514 → 0. Capital side boxes are outside the capital body and use S5's side zone, not the lowercase meanline.
For transparency, using the common S6 lowercase meanline for every class gives held-out 453 → 436 → 0. Overhead evidence is bounded by both the font meanline and the capital's own top. There are 0 remaining overhead exceptions: [exception receipt](S6_common_meanline_exceptions.jsonl). Capital side boxes retain their separate S5 side zone, outside the body.

All five required native crops and cached alignments are included as worktree files under `tests/data/labelfix_s6/`. Tests assert physical presence/ownership, safe top/bottom boundaries, unchanged native labels and no CTC forward construction; they do not fit naming outputs.

- `602cc72e-p000155-l0009`: `Εὔνουχος καἰ ιερεύς.` → `Εὔνουχος καὶ ἵερεύς.`. [Native crop](../../../../tests/data/labelfix_s6/602cc72e-p000155-l0009.png).
- `602cc72e-p000113-l0030`: `Ἀστρολὄγος ἐξιὼν ἒκἁστοτε ἒσπέρας ἔθος εἶχε τοὺς` → `Ἀστρολογος ἐξιὼν ἑκάστοτε ἑσπέρας ἔθος εῖχε τοὺς`. [Native crop](../../../../tests/data/labelfix_s6/602cc72e-p000113-l0030.png).
- `384c3f89-p000091-l0039`: `ἠείδει· οὶος δὲ κατὰ πλατυ βόσκετο τἳφος.` → `ἠείδει· οὶος δὲ κατὰ πλατὺ βόσκετο τἳφος.`. [Native crop](../../../../tests/data/labelfix_s6/384c3f89-p000091-l0039.png).
- `8b6b0de9-p000007-l0030`: `κοιλάδας, εἰς λῃστων σκηνάς·` → `κοιλάδας, εἰς λῃστῶν σκηνάς·`. [Native crop](../../../../tests/data/labelfix_s6/8b6b0de9-p000007-l0030.png).
- `384c3f89-p000142-l0002`: `ηντινα τήνδ’ ὀνόμηνας ἀριγνώτην γεγαυῖαν` → `ἥντινα τήνδ’ ὀνόμηνας ἀριγνώτην γεγαυῖαν`. [Native crop](../../../../tests/data/labelfix_s6/384c3f89-p000142-l0002.png).

The joined iota in the first case regains top evidence; its fixed-model name can still be wrong. The upsilon acute no longer yields a second body fragment. The second case enforces the mid-top boundary across its attached marks. `τυ` has two nonoverlapping regions with the upper mark on υ; `στω` has three with the mark on ω; the split η has one two-component region with both upper blobs. A synthetic sloping-band test ensures one lobe crossing a fusion boundary is counted once.

## Frozen held-out naming table, row for row

| kind | S4 P/R | S5 P/R | S6 P/R | S4 F1 | S5 F1 | S6 F1 |
|---|---:|---:|---:|---:|---:|---:|
| total | 93.5%/91.9% | 93.7%/91.6% | 93.8%/92.1% | 92.7% | 92.7% | 92.9% |
| accent | 95.8%/94.8% | 95.7%/94.6% | 96.0%/94.8% | 95.3% | 95.2% | 95.4% |
| breathing | 94.4%/93.5% | 94.2%/93.1% | 94.1%/93.7% | 93.9% | 93.7% | 93.9% |
| compound | 80.5%/89.1% | 80.9%/88.2% | 80.5%/89.1% | 84.6% | 84.4% | 84.6% |
| subscript | 97.7%/44.7% | 97.7%/44.7% | 97.7%/45.7% | 61.3% | 61.3% | 62.3% |
| dialytika | 0.0%/0.0% | —/0.0% | 100.0%/25.0% | 0.0% | 0.0% | 40.0% |
| apostrophe | 99.4%/81.1% | 99.4%/81.1% | 99.4%/81.1% | 89.3% | 89.3% | 89.3% |
| capitals combined | 36.6%/100.0% | 95.6%/98.7% | 96.1%/98.6% | 53.5% | 97.1% | 97.3% |
| capitals pixel-only | 13.8%/27.8% | 83.2%/45.3% | 83.3%/46.9% | 18.4% | 58.7% | 60.0% |
| marks at capitals | 92.0%/86.0% | 94.2%/87.1% | 94.2%/87.1% | — | — | — |
| marks-at-capitals exact naming accuracy | 86.0% | 87.1% | 87.1% | — | — | — |

The original table retains 18229 known and 2647 unknown component slots. New fused characters do not silently turn its unknowns into successes. Capital marked-slot support is 93. Mark names come from the unchanged model; a physical recovery need not improve an exact compound name.

## DEV naming and the S5 presence losses

| kind | S4 P/R | S5 P/R | S6 P/R |
|---|---:|---:|---:|
| total | 94.3%/91.2% | 94.2%/89.2% | 94.6%/90.2% |
| accent | 94.5%/96.5% | 94.6%/95.3% | 94.7%/96.2% |
| breathing | 96.3%/90.8% | 95.7%/86.9% | 95.6%/88.9% |
| compound | 87.1%/88.4% | 81.0%/83.3% | 87.8%/83.3% |
| subscript | 100.0%/67.3% | 100.0%/65.5% | 97.4%/67.3% |
| dialytika | 11.1%/33.3% | —/0.0% | —/0.0% |
| apostrophe | 100.0%/36.9% | 100.0%/36.9% | 100.0%/36.9% |
| capitals combined (held-out diagnostic) | 36.6%/100.0% | 95.6%/98.7% | 96.1%/98.6% |
| capitals pixel-only (held-out diagnostic) | 13.8%/27.8% | 83.2%/45.3% | 83.3%/46.9% |

S5 introduced 36 DEV top-presence losses against S4 on known characters; S6 recovers 15. Breathing and compound aggregate presence exceed both baselines, but individual losses below remain open. S5's word-height substitution is removed. Capital top/side guards are retained because restoring unrestricted S4 slices can cut capital body ink; safely separating joined capital-side marks remains unresolved. Each record includes all three evidence boxes/bands, truth, source crop, character and slot: [DEV loss audit](S6_DEV_S5_presence_losses.jsonl). No naming loss is relabelled a detection recovery.

| DEV line : source slots : character | recovered | evidence / remaining rule |
|---|---|---|
| 8b6b0de9-p000017-l0032 : [6] : ι | pass | recovered by font/region repair |
| 8b6b0de9-p000011-l0019 : [15] : ρ | pass | recovered by font/region repair |
| 2793d64c-p000021-l0005 : [4] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 8b6b0de9-p000009-l0004 : [3] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000307-l0011 : [6] : Ε | open | capital top/side guard still suppresses S4 top evidence |
| 8b6b0de9-p000017-l0018 : [3] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000077-l0002 : [1] : Ε | open | capital top/side guard still suppresses S4 top evidence |
| 2793d64c-p000043-l0004 : [18] : υ | pass | recovered by font/region repair |
| 2793d64c-p000072-l0016 : [7, 8] : ε | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000133-l0012 : [1] : Ε | open | capital top/side guard still suppresses S4 top evidence |
| 8b6b0de9-p000016-l0013 : [5] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000318-l0016 : [1] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000303-l0022 : [1] : Η | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000022-l0017 : [3] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 2793d64c-p000033-l0005 : [19] : ε | open | safe-zone/ownership acceptance unresolved |
| 2793d64c-p000047-l0010 : [3] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000318-l0003 : [3] : ι | pass | recovered by font/region repair |
| 2793d64c-p000068-l0024 : [19] : ι | pass | recovered by font/region repair |
| 2793d64c-p000070-l0021 : [9, 10] : ε | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000318-l0012 : [4] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000318-l0020 : [1] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000303-l0010 : [1] : Η | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000302-l0010 : [1] : Ε | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000022-l0006 : [4] : Ω | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000041-l0003 : [3] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000178-l0021 : [3] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000133-l0013 : [1] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 2793d64c-p000047-l0008 : [5] : ω | pass | recovered by font/region repair |
| 2793d64c-p000047-l0008 : [25] : υ | pass | recovered by font/region repair |
| 02a3a2a6-p000046-l0020 : [1] : Ε | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000318-l0015 : [11] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000046-l0014 : [1] : Ω | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000041-l0007 : [23] : ι | pass | recovered by font/region repair |
| 02a3a2a6-p000029-l0012 : [1] : Α | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000029-l0003 : [1] : Ο | open | capital top/side guard still suppresses S4 top evidence |
| 02a3a2a6-p000029-l0003 : [13] : Α | open | capital top/side guard still suppresses S4 top evidence |

## Per-class held-out exact naming sets

| class | support | S4 P/R | S5 P/R | S6 P/R |
|---|---:|---:|---:|---:|
| acute | 1418 | 99.2%/95.6% | 99.0%/95.4% | 99.3%/95.3% |
| acute+subscript | 2 | 100.0%/50.0% | 100.0%/50.0% | 100.0%/50.0% |
| circumflex | 303 | 87.1%/89.1% | 86.2%/88.4% | 87.0%/90.8% |
| circumflex+subscript | 39 | 100.0%/41.0% | 100.0%/41.0% | 100.0%/43.6% |
| dasia | 223 | 88.3%/91.0% | 87.8%/90.1% | 87.1%/90.6% |
| dasia+acute | 102 | 87.0%/98.0% | 87.0%/98.0% | 84.9%/99.0% |
| dasia+acute+subscript | 0 | —/— | —/— | —/— |
| dasia+circumflex | 18 | 55.6%/55.6% | 52.6%/55.6% | 52.4%/61.1% |
| dasia+circumflex+subscript | 3 | 50.0%/33.3% | 50.0%/33.3% | 50.0%/33.3% |
| dasia+grave | 7 | 11.6%/71.4% | 10.9%/71.4% | 10.4%/71.4% |
| dasia+grave+subscript | 0 | —/— | —/— | —/— |
| dialytika | 1 | 0.0%/0.0% | —/0.0% | 100.0%/100.0% |
| dialytika+acute | 3 | 0.0%/0.0% | —/0.0% | —/0.0% |
| grave | 661 | 98.4%/95.5% | 98.4%/95.2% | 98.8%/95.9% |
| none | 14228 | 99.2%/99.6% | 99.1%/99.6% | 99.2%/99.7% |
| psili | 646 | 97.1%/94.0% | 96.8%/93.8% | 97.1%/94.6% |
| psili+acute | 268 | 94.5%/95.9% | 95.9%/95.1% | 95.5%/95.5% |
| psili+acute+subscript | 1 | —/0.0% | —/0.0% | —/0.0% |
| psili+circumflex | 40 | 71.4%/50.0% | 78.3%/45.0% | 80.0%/50.0% |
| psili+circumflex+subscript | 0 | —/— | —/— | —/— |
| psili+grave | 11 | 36.8%/63.6% | 36.8%/63.6% | 40.0%/54.5% |
| psili+grave+subscript | 0 | —/— | —/— | —/— |
| psili+subscript | 0 | —/— | —/— | —/— |
| subscript | 49 | 100.0%/49.0% | 100.0%/49.0% | 100.0%/49.0% |
| capitals combined | 18960 | 36.6%/100.0% | 95.6%/98.7% | 96.1%/98.6% |
| capitals pixel-only | 18960 | 13.8%/27.8% | 83.2%/45.3% | 83.3%/46.9% |

Ascender false-mark control: held-out S4 10/2488, S5 10/2488, S6 9/2488; DEV S4 2/1070, S5 4/1070, S6 1/1070. Held-out atomic naming P/R (compound accent and breathing scored separately): 93.0%/92.6% → 93.2%/92.2% → 93.4%/92.8%.

## Every owner note

The latest 49 review and 57 example records supersede the earlier wording for the current score. Numbers resolve against the displayed S4 source components, with all S6 children/union pieces attached to those source slots. Both old and new scores are retained. No note document means unreviewed. Empty current notes require no lost accepted physical presence, lost true name, newly false name, or uncertified mark/name addition at an unknown print slot against S4. Possible/ambiguous clauses remain uncertified, not converted to positive print truth.

Current multi-mark clauses require their stated number of physical upper blobs. A connected compound with one blob does not receive two detection credits from its classifier name. Older checks deliberately retain their old naming-based semantics; hence their totals differ from the current physical checks even when note text is similar. The exclamation-dot clause checks its frozen punctuation slot 13, preserving the legitimate alpha subscript elsewhere on that line.

| owner set | S4 | S5 | S6 |
|---|---:|---:|---:|
| old earlier | 46/59 | 45/59 | 47/59 |
| old examples | 27/56 | 26/56 | 32/56 |
| old review | 22/33 | 21/33 | 22/33 |
| current review | 14/49 | 14/49 | 36/49 |
| current examples | 29/57 | 28/57 | 33/57 |

Complete old machine checks: [S4](S6_old_checks_S4.json), [S5](S6_old_checks_S5.json), [S6](S6_old_checks_S6.json). Current clauses include resolved starts/boxes and explicit uncertainty: [review](S6_current_review_checks.jsonl), [examples](S6_current_examples_checks.jsonl).

### Current review: all notes

| line | exact note | S4 → S5 → S6 | remaining clauses |
|---|---|---|---|
| 02a3a2a6-p000046-l0014 | accent of 8 missed | open → open → open | mark 8 |
| 02a3a2a6-p000046-l0025 | (empty: preserve correctness) | pass → pass → pass | none |
| 177b717d-p000013-l0009 | missed one at 13 | open → open → open | mark 13 |
| 177b717d-p000072-l0001 | fused letters at 33 and missed  | open → open → pass | none |
| 177b717d-p000097-l0007 | (empty: preserve correctness) | pass → pass → open | no_regression |
| 177b717d-p000097-l0010 | (empty: preserve correctness) | pass → pass → pass | none |
| 177b717d-p000104-l0007 | missed at 23 | open → open → pass | none |
| 2793d64c-p000048-l0004 | iota is missed at 19 | open → open → open | subscript 19 |
| 2793d64c-p000048-l0010 | possible iota at 24 | open → open → open | uncertain 24 |
| 2793d64c-p000070-l0010 | 22 delta is detected | pass → pass → pass | none |
| 2793d64c-p000070-l0014 | (empty: preserve correctness) | pass → pass → pass | none |
| 2793d64c-p000072-l0007 | missed at 4 and possibly 24 | open → open → open | mark 4, uncertain 24 |
| 384c3f89-p000030-l0021 | ellipsis at 22 missed | pass → pass → pass | none |
| 384c3f89-p000030-l0029 | (empty: preserve correctness) | pass → pass → open | no_regression |
| 384c3f89-p000053-l0010 | missed at 18 and 24 | open → open → pass | none |
| 384c3f89-p000053-l0021 | (empty: preserve correctness) | pass → pass → pass | none |
| 384c3f89-p000053-l0028 | missed at 32 | open → open → pass | none |
| 384c3f89-p000059-l0027 | missed ellispis at 21 | open → open → open | apostrophe 21 |
| 384c3f89-p000068-l0036 | (empty: preserve correctness) | pass → pass → open | no_regression |
| 384c3f89-p000091-l0011 | fused letters at 3 and missed accent | open → open → pass | none |
| 384c3f89-p000091-l0039 | τυ merged and accent missed at second letter of 20 | open → open → pass | none |
| 384c3f89-p000121-l0024 | 15 is 2 letters and accent missed there | open → open → pass | none |
| 384c3f89-p000142-l0002 | split eat at 1-2 and missed 2 accents | open → open → pass | none |
| 384c3f89-p000170-l0031 | fused letters at 22 and missed accent | open → open → pass | none |
| 384c3f89-p000179-l0022 | missed at 28 | open → open → open | mark 28 |
| 384c3f89-p000182-l0006 | missed at 26 | open → open → pass | none |
| 384c3f89-p000183-l0005 | fused letters at 26 and missed accent | open → open → pass | none |
| 384c3f89-p000205-l0005 | missed sub at 13, and 1 of 2 at 1 | open → open → open | subscript 13, mark 1 |
| 51fe7386-p000024-l0015 | (empty: preserve correctness) | pass → pass → pass | none |
| 51fe7386-p000024-l0020 | missed at 4 | open → open → pass | none |
| 602cc72e-p000113-l0016 | missed at 3 | open → open → pass | none |
| 602cc72e-p000113-l0030 | maek sure the accent boxes are above mid-top font height | open → open → pass | none |
| 602cc72e-p000155-l0009 | care is required to not detect within the height of letters since the ink of accents and chars are merged and they might look like more than one where there is only once. | open → open → pass | none |
| 602cc72e-p000167-l0027 | missed 1 at 1, 6, 10, and 14 | open → open → open | mark 1 |
| 8b6b0de9-p000004-l0028 | 2 letters fused at 5 and misesd accent there | open → open → pass | none |
| 8b6b0de9-p000007-l0030 | 3 letters fused at 15 and missed accent there | open → open → pass | none |
| 8b6b0de9-p000008-l0001 | missed at 7 | open → open → pass | none |
| 8b6b0de9-p000008-l0002 | dot of exclamation mark is detected | pass → pass → pass | none |
| 8b6b0de9-p000008-l0019 | missed accent at 2 | open → open → pass | none |
| 8b6b0de9-p000008-l0024 | missed at 3 | open → open → pass | none |
| 8b6b0de9-p000011-l0007 | random dot under 9 | pass → pass → pass | none |
| 8b6b0de9-p000011-l0014 | fused letters at 4 and 6, missed their accents | open → open → pass | none |
| 8b6b0de9-p000021-l0007 | (empty: preserve correctness) | pass → pass → pass | none |
| 9c1dca9b-p000005-l0017 | missed at 9 (capital) | open → open → open | mark 9 |
| 9c1dca9b-p000015-l0051 | fused letters at 3 and accent missed at 26 | open → open → pass | none |
| 9c1dca9b-p000015-l0057 | 3 fused letters at 12 and missed accent | open → open → pass | none |
| 9c1dca9b-p000015-l0060 | 3 fused letters at 7 and missed accent missed at 15 | open → open → pass | none |
| 9c1dca9b-p000015-l0065 | missed 8 | pass → pass → pass | none |
| 9c1dca9b-p000015-l0067 | missed at 2 | open → open → pass | none |
### Current examples: all notes

| line | exact note | S4 → S5 → S6 | remaining clauses |
|---|---|---|---|
| 02a3a2a6-p000041-l0005 | unified λο  missed at 24, subscirpt at 28 | open → open → open | subscript 28 |
| 02a3a2a6-p000046-l0014 | missed ellipsis at 8 | open → open → open | apostrophe 8 |
| 02a3a2a6-p000307-l0003 | missed ellispis at 2, 15 | open → open → open | apostrophe 2 |
| 02a3a2a6-p000318-l0014 | missed at 1, 17 | open → open → open | mark 1 |
| 02a3a2a6-p000318-l0017 | missed at 2 (confusion due to capital theta at 1) | pass → pass → pass | none |
| 177b717d-p000017-l0012 | missed at 11, 12 | pass → open → open | mark 12 |
| 177b717d-p000097-l0010 | missed at 2, 5 | pass → pass → pass | none |
| 2793d64c-p000033-l0022 | missed at 1, ellispis at 11 | open → open → open | mark 1 |
| 2793d64c-p000070-l0010 | missed at 17 | pass → pass → pass | none |
| 384c3f89-p000030-l0010 | missed quote and 2 accents at 1 | open → open → open | mark 1 |
| 384c3f89-p000030-l0029 | missed ellipsis or quote at 1  why the questionamrk at 23?  | pass → pass → pass | none |
| 384c3f89-p000050-l0016 | classified 2 accents as 1 at 5, missed at 19 | open → open → open | mark 5 |
| 384c3f89-p000050-l0027 | missed accent at 16, missed elipsis at 29 | open → open → open | mark 16 |
| 384c3f89-p000053-l0023 | (empty: preserve correctness) | pass → pass → open | no_regression |
| 384c3f89-p000068-l0028 | missed ellipsis at 27, | pass → pass → pass | none |
| 384c3f89-p000068-l0036 | missed ellipsis at 6, and 2 accens at 7 missed 1 at 30 | open → open → open | mark 7 |
| 384c3f89-p000091-l0014 | missed all accents except 1 | open → open → open | whole_marks |
| 384c3f89-p000091-l0027 | missed 2 accents at 1, and classified eta as 1-2 | open → open → pass | none |
| 384c3f89-p000091-l0029 | missed ellipsis at 14 | pass → pass → pass | none |
| 384c3f89-p000096-l0004 | missed second aaccent at 15 | pass → pass → pass | none |
| 384c3f89-p000096-l0010 | (empty: preserve correctness) | pass → pass → pass | none |
| 384c3f89-p000096-l0031 | missed elipsis at 4 | open → open → open | apostrophe 4 |
| 384c3f89-p000121-l0023 | missed ellipsis at 34 and 2 accents at 35 | open → open → open | mark 35 |
| 384c3f89-p000142-l0010 | missed subscript at 14 | open → open → open | subscript 14 |
| 384c3f89-p000142-l0014 | missed at 9 | pass → pass → pass | none |
| 384c3f89-p000170-l0024 | missed subscript at 12 | open → open → open | subscript 12 |
| 384c3f89-p000182-l0023 | missed ellipsis at 3 | pass → pass → pass | none |
| 384c3f89-p000182-l0031 | (empty: preserve correctness) | pass → pass → open | no_regression |
| 384c3f89-p000183-l0009 | missed second accent at 9 | pass → pass → pass | none |
| 384c3f89-p000183-l0020 | missed sub at 21 | open → open → open | subscript 21 |
| 384c3f89-p000183-l0022 | missed ellipsis at 20 | pass → pass → pass | none |
| 51fe7386-p000024-l0015 | missed quote at 1,  missed at 2, 29 | open → open → open | quote 1 |
| 51fe7386-p000024-l0016 | missed 2 at 6, 1 at 11, 1 at 36 | open → open → open | mark 6 |
| 51fe7386-p000026-l0016 | missed at 1, 25, 12 | pass → pass → pass | none |
| 602cc72e-p000113-l0009 | missed at 1, 9, 10, 12 | pass → pass → pass | none |
| 602cc72e-p000167-l0027 | missed at 6, 10 , 14 | pass → pass → pass | none |
| 602cc72e-p000353-l0006 | missed at 6, 10, 14 | pass → pass → pass | none |
| 8b6b0de9-p000004-l0011 | missed at 2 at 6 | open → open → open | ambiguous |
| 8b6b0de9-p000004-l0029 | missed at 1, 4, 18 | open → open → pass | none |
| 8b6b0de9-p000007-l0011 | missed at 1 and 2, 4 | open → open → open | mark 1 |
| 8b6b0de9-p000007-l0021 | missed at 4, 18 | open → open → pass | none |
| 8b6b0de9-p000007-l0030 | missed letter classification for στω, and accent at omega | open → open → pass | none |
| 8b6b0de9-p000008-l0001 | missed at 7, 12 | open → open → pass | none |
| 8b6b0de9-p000008-l0002 | missed 9  misread εις as one 1 letter | open → open → pass | none |
| 8b6b0de9-p000008-l0019 | missed at 17 | pass → pass → pass | none |
| 8b6b0de9-p000009-l0024 | missed at 9, 11 | pass → pass → pass | none |
| 8b6b0de9-p000011-l0014 | missed accent at 13 | pass → pass → pass | none |
| 8b6b0de9-p000012-l0006 | missed at 17 | pass → pass → pass | none |
| 8b6b0de9-p000016-l0013 | missed at 3, 5 | open → open → open | mark 3 |
| 8b6b0de9-p000016-l0029 | misread rho at 7 and 21 | pass → pass → pass | none |
| 8b6b0de9-p000018-l0023 | missed accent at 2, missatributed lamba at 6-7 | pass → pass → pass | none |
| 8b6b0de9-p000018-l0026 | missed at 2 | open → open → pass | none |
| 8b6b0de9-p000021-l0012 | missed identified accent as part of capital T at 1 | pass → pass → pass | none |
| 8b6b0de9-p000021-l0028 | missed at 10 | pass → pass → pass | none |
| 9c1dca9b-p000005-l0017 | missed at 9, 14, 23, 27 | open → open → open | mark 9 |
| 9c1dca9b-p000015-l0062 | missed at 9 | pass → pass → pass | none |
| 9c1dca9b-p000015-l0065 | missed at 8 | pass → pass → pass | none |

## Regressions against each baseline

Every scalar P/R/F1 regression, including each book and exact naming class, is enumerated below and in [S6_metric_regressions.jsonl](S6_metric_regressions.jsonl). Undefined before precision remains undefined. Physical losses and new false presence are separate from naming identity changes. The receipts contain every affected slot with old/new boxes, bands and truth; no held-out regression is omitted because the aggregate improved.

- Against S4: 68 character-zone regressions across held-out+DEV ([every physical event with evidence](S6_presence_regressions_S4.jsonl)); 167 legacy-slot naming/presence regressions ([every slot with evidence](S6_regressions_S4.jsonl)). These counts overlap and are not added.
- Against S5: 51 character-zone regressions across held-out+DEV ([every physical event with evidence](S6_presence_regressions_S5.jsonl)); 142 legacy-slot naming/presence regressions ([every slot with evidence](S6_regressions_S5.jsonl)). These counts overlap and are not added.

| baseline | metric scope | measure | before → S6 |
|---|---|---|---|
| S4 | heldout/naming/breathing | precision | 94.438% → 94.124% |
| S4 | heldout/naming/breathing | f1 | 93.948% → 93.908% |
| S4 | heldout/atomic/accent | recall | 94.578% → 94.508% |
| S4 | heldout/presence/merged_accent | precision | 95.444% → 95.434% |
| S4 | heldout/class/acute | recall | 95.557% → 95.346% |
| S4 | heldout/class/circumflex | precision | 87.097% → 87.025% |
| S4 | heldout/class/dasia | precision | 88.261% → 87.069% |
| S4 | heldout/class/dasia | recall | 91.031% → 90.583% |
| S4 | heldout/class/dasia+acute | precision | 86.957% → 84.874% |
| S4 | heldout/class/dasia+circumflex | precision | 55.556% → 52.381% |
| S4 | heldout/class/dasia+grave | precision | 11.628% → 10.417% |
| S4 | heldout/class/psili+acute | recall | 95.896% → 95.522% |
| S4 | heldout/class/psili+grave | recall | 63.636% → 54.545% |
| S4 | heldout/book/wikisource:177b717d/breathing | precision | 96.639% → 96.610% |
| S4 | heldout/book/wikisource:177b717d/breathing | recall | 89.147% → 88.372% |
| S4 | heldout/book/wikisource:177b717d/breathing | f1 | 92.742% → 92.308% |
| S4 | heldout/book/wikisource:22fda82b/total | recall | 65.116% → 61.628% |
| S4 | heldout/book/wikisource:22fda82b/total | f1 | 61.538% → 60.571% |
| S4 | heldout/book/wikisource:22fda82b/accent | recall | 70.175% → 64.912% |
| S4 | heldout/book/wikisource:22fda82b/accent | f1 | 65.041% → 63.793% |
| S4 | heldout/book/wikisource:22fda82b/breathing | precision | 73.333% → 57.895% |
| S4 | heldout/book/wikisource:22fda82b/breathing | f1 | 62.857% → 56.410% |
| S4 | heldout/book/wikisource:22fda82b/compound | precision | 44.444% → 40.000% |
| S4 | heldout/book/wikisource:22fda82b/compound | f1 | 53.333% → 50.000% |
| S4 | heldout/book/wikisource:263438a3/total | precision | 72.000% → 64.000% |
| S4 | heldout/book/wikisource:263438a3/total | recall | 72.000% → 64.000% |
| S4 | heldout/book/wikisource:263438a3/total | f1 | 72.000% → 64.000% |
| S4 | heldout/book/wikisource:263438a3/accent | precision | 81.818% → 75.000% |
| S4 | heldout/book/wikisource:263438a3/accent | f1 | 72.000% → 69.231% |
| S4 | heldout/book/wikisource:263438a3/breathing | precision | 58.333% → 50.000% |
| S4 | heldout/book/wikisource:263438a3/breathing | recall | 87.500% → 62.500% |
| S4 | heldout/book/wikisource:263438a3/breathing | f1 | 70.000% → 55.556% |
| S4 | heldout/book/wikisource:263438a3/compound | precision | 100.000% → 50.000% |
| S4 | heldout/book/wikisource:263438a3/compound | f1 | 66.667% → 50.000% |
| S4 | heldout/book/wikisource:384c3f89/accent | precision | 98.994% → 98.927% |
| S4 | heldout/book/wikisource:384c3f89/accent | recall | 97.748% → 97.682% |
| S4 | heldout/book/wikisource:384c3f89/accent | f1 | 98.367% → 98.301% |
| S4 | heldout/book/wikisource:4ad622a4/breathing | precision | 66.667% → 33.333% |
| S4 | heldout/book/wikisource:4ad622a4/breathing | recall | 66.667% → 33.333% |
| S4 | heldout/book/wikisource:4ad622a4/breathing | f1 | 66.667% → 33.333% |
| S4 | heldout/book/wikisource:4f60b077/total | precision | 93.333% → 93.103% |
| S4 | heldout/book/wikisource:4f60b077/total | recall | 90.323% → 87.097% |
| S4 | heldout/book/wikisource:4f60b077/total | f1 | 91.803% → 90.000% |
| S4 | heldout/book/wikisource:4f60b077/accent | precision | 95.455% → 95.238% |
| S4 | heldout/book/wikisource:4f60b077/accent | recall | 95.455% → 90.909% |
| S4 | heldout/book/wikisource:4f60b077/accent | f1 | 95.455% → 93.023% |
| S4 | heldout/book/wikisource:51fe7386/total | precision | 84.270% → 81.522% |
| S4 | heldout/book/wikisource:51fe7386/total | f1 | 82.418% → 81.081% |
| S4 | heldout/book/wikisource:51fe7386/accent | precision | 95.455% → 91.176% |
| S4 | heldout/book/wikisource:51fe7386/accent | recall | 86.301% → 84.932% |
| S4 | heldout/book/wikisource:51fe7386/accent | f1 | 90.647% → 87.943% |
| S4 | heldout/book/wikisource:602cc72e/compound | precision | 46.667% → 38.462% |
| S4 | heldout/book/wikisource:602cc72e/compound | recall | 70.000% → 50.000% |
| S4 | heldout/book/wikisource:602cc72e/compound | f1 | 56.000% → 43.478% |
| S4 | heldout/book/wikisource:9c1dca9b/total | precision | 81.319% → 76.344% |
| S4 | heldout/book/wikisource:9c1dca9b/total | recall | 77.083% → 73.958% |
| S4 | heldout/book/wikisource:9c1dca9b/total | f1 | 79.144% → 75.132% |
| S4 | heldout/book/wikisource:9c1dca9b/accent | precision | 91.379% → 89.286% |
| S4 | heldout/book/wikisource:9c1dca9b/accent | recall | 79.104% → 74.627% |
| S4 | heldout/book/wikisource:9c1dca9b/accent | f1 | 84.800% → 81.301% |
| S4 | heldout/book/wikisource:9c1dca9b/breathing | precision | 61.538% → 57.692% |
| S4 | heldout/book/wikisource:9c1dca9b/breathing | recall | 76.190% → 71.429% |
| S4 | heldout/book/wikisource:9c1dca9b/breathing | f1 | 68.085% → 63.830% |
| S4 | heldout/book/wikisource:9c1dca9b/compound | precision | 50.000% → 37.500% |
| S4 | dev/naming/total | recall | 91.193% → 90.209% |
| S4 | dev/naming/total | f1 | 92.699% → 92.362% |
| S4 | dev/naming/accent | recall | 96.513% → 96.184% |
| S4 | dev/naming/accent | f1 | 95.477% → 95.431% |
| S4 | dev/naming/breathing | precision | 96.273% → 95.588% |
| S4 | dev/naming/breathing | recall | 90.820% → 88.867% |
| S4 | dev/naming/breathing | f1 | 93.467% → 92.105% |
| S4 | dev/naming/compound | recall | 88.406% → 83.333% |
| S4 | dev/naming/compound | f1 | 87.770% → 85.502% |
| S4 | dev/naming/subscript | precision | 100.000% → 97.368% |
| S4 | dev/naming/subscript | f1 | 80.435% → 79.570% |
| S4 | dev/naming/dialytika | recall | 33.333% → 0.000% |
| S4 | dev/naming/dialytika | f1 | 16.667% → 0.000% |
| S4 | dev/atomic/total | recall | 91.401% → 90.190% |
| S4 | dev/atomic/total | f1 | 92.787% → 92.352% |
| S4 | dev/atomic/accent | recall | 96.140% → 95.416% |
| S4 | dev/atomic/accent | f1 | 95.136% → 94.929% |
| S4 | dev/atomic/breathing | precision | 94.864% → 94.563% |
| S4 | dev/atomic/breathing | recall | 90.923% → 88.308% |
| S4 | dev/atomic/breathing | f1 | 92.852% → 91.329% |
| S4 | dev/atomic/subscript | precision | 100.000% → 97.368% |
| S4 | dev/atomic/subscript | f1 | 80.435% → 79.570% |
| S4 | dev/atomic/dialytika | recall | 33.333% → 0.000% |
| S4 | dev/atomic/dialytika | f1 | 16.667% → 0.000% |
| S4 | dev/presence/merged_accent | precision | 93.824% → 93.319% |
| S4 | dev/class/acute | precision | 99.255% → 98.955% |
| S4 | dev/class/acute | recall | 95.827% → 95.396% |
| S4 | dev/class/circumflex | precision | 91.030% → 90.698% |
| S4 | dev/class/circumflex | recall | 96.479% → 96.127% |
| S4 | dev/class/circumflex+subscript | precision | 90.909% → 87.500% |
| S4 | dev/class/dasia | precision | 97.183% → 95.804% |
| S4 | dev/class/dasia | recall | 90.196% → 89.542% |
| S4 | dev/class/dasia+acute | precision | 89.744% → 85.000% |
| S4 | dev/class/dasia+acute | recall | 92.105% → 89.474% |
| S4 | dev/class/dialytika | recall | 33.333% → 0.000% |
| S4 | dev/class/grave | precision | 98.016% → 97.817% |
| S4 | dev/class/grave | recall | 96.484% → 96.289% |
| S4 | dev/class/none | precision | 98.015% → 97.861% |
| S4 | dev/class/psili | precision | 97.015% → 95.770% |
| S4 | dev/class/psili | recall | 90.782% → 88.547% |
| S4 | dev/class/psili+acute | precision | 96.970% → 96.721% |
| S4 | dev/class/psili+acute | recall | 91.429% → 84.286% |
| S4 | dev/class/psili+circumflex | precision | 81.818% → 80.000% |
| S4 | dev/class/psili+circumflex | recall | 75.000% → 66.667% |
| S4 | dev/book/wikisource:02a3a2a6/total | precision | 98.503% → 97.775% |
| S4 | dev/book/wikisource:02a3a2a6/total | recall | 92.465% → 89.783% |
| S4 | dev/book/wikisource:02a3a2a6/total | f1 | 95.389% → 93.609% |
| S4 | dev/book/wikisource:02a3a2a6/accent | precision | 98.846% → 97.897% |
| S4 | dev/book/wikisource:02a3a2a6/accent | recall | 99.037% → 98.651% |
| S4 | dev/book/wikisource:02a3a2a6/accent | f1 | 98.941% → 98.273% |
| S4 | dev/book/wikisource:02a3a2a6/breathing | precision | 99.242% → 99.153% |
| S4 | dev/book/wikisource:02a3a2a6/breathing | recall | 96.324% → 86.029% |
| S4 | dev/book/wikisource:02a3a2a6/breathing | f1 | 97.761% → 92.126% |
| S4 | dev/book/wikisource:02a3a2a6/compound | precision | 93.182% → 92.500% |
| S4 | dev/book/wikisource:02a3a2a6/compound | recall | 87.234% → 78.723% |
| S4 | dev/book/wikisource:02a3a2a6/compound | f1 | 90.110% → 85.057% |
| S4 | dev/book/wikisource:02a3a2a6/subscript | precision | 100.000% → 90.000% |
| S4 | dev/book/wikisource:02a3a2a6/subscript | f1 | 81.818% → 78.261% |
| S4 | dev/book/wikisource:02a3a2a6/dialytika | recall | 50.000% → 0.000% |
| S4 | dev/book/wikisource:02a3a2a6/dialytika | f1 | 50.000% → 0.000% |
| S4 | dev/book/wikisource:2793d64c/total | recall | 89.335% → 87.673% |
| S4 | dev/book/wikisource:2793d64c/accent | recall | 94.409% → 92.903% |
| S4 | dev/book/wikisource:2793d64c/breathing | precision | 95.570% → 94.268% |
| S4 | dev/book/wikisource:2793d64c/breathing | recall | 90.964% → 89.157% |
| S4 | dev/book/wikisource:2793d64c/breathing | f1 | 93.210% → 91.641% |
| S4 | dev/book/wikisource:2793d64c/compound | recall | 84.615% → 79.487% |
| S4 | dev/book/wikisource:2793d64c/compound | f1 | 80.488% → 78.481% |
| S4 | dev/book/wikisource:8b6b0de9/total | precision | 93.973% → 93.253% |
| S4 | dev/book/wikisource:8b6b0de9/accent | precision | 94.312% → 92.665% |
| S4 | dev/book/wikisource:8b6b0de9/accent | f1 | 95.097% → 94.612% |
| S4 | dev/book/wikisource:8b6b0de9/breathing | precision | 94.819% → 94.527% |
| S4 | dev/book/wikisource:8b6b0de9/compound | recall | 92.308% → 90.385% |
| S4 | dev/book/wikisource:8b6b0de9/compound | f1 | 91.429% → 91.262% |
| S4 | capitals/combined | recall | 100.000% → 98.570% |
| S4 | capitals_disagreement/combined | recall | 100.000% → 97.988% |
| S4 | capitals_disagreement/combined | f1 | 96.852% → 96.274% |
| S5 | heldout/naming/breathing | precision | 94.200% → 94.124% |
| S5 | heldout/naming/compound | precision | 80.855% → 80.522% |
| S5 | heldout/presence/merged_accent | precision | 96.482% → 95.434% |
| S5 | heldout/class/acute | recall | 95.416% → 95.346% |
| S5 | heldout/class/dasia | precision | 87.773% → 87.069% |
| S5 | heldout/class/dasia+acute | precision | 86.957% → 84.874% |
| S5 | heldout/class/dasia+circumflex | precision | 52.632% → 52.381% |
| S5 | heldout/class/dasia+grave | precision | 10.870% → 10.417% |
| S5 | heldout/class/psili+acute | precision | 95.865% → 95.522% |
| S5 | heldout/class/psili+grave | recall | 63.636% → 54.545% |
| S5 | heldout/book/wikisource:22fda82b/accent | recall | 68.421% → 64.912% |
| S5 | heldout/book/wikisource:22fda82b/accent | f1 | 65.000% → 63.793% |
| S5 | heldout/book/wikisource:22fda82b/breathing | precision | 58.824% → 57.895% |
| S5 | heldout/book/wikisource:263438a3/total | precision | 68.000% → 64.000% |
| S5 | heldout/book/wikisource:263438a3/total | recall | 68.000% → 64.000% |
| S5 | heldout/book/wikisource:263438a3/total | f1 | 68.000% → 64.000% |
| S5 | heldout/book/wikisource:263438a3/accent | precision | 81.818% → 75.000% |
| S5 | heldout/book/wikisource:263438a3/accent | f1 | 72.000% → 69.231% |
| S5 | heldout/book/wikisource:263438a3/breathing | precision | 53.846% → 50.000% |
| S5 | heldout/book/wikisource:263438a3/breathing | recall | 87.500% → 62.500% |
| S5 | heldout/book/wikisource:263438a3/breathing | f1 | 66.667% → 55.556% |
| S5 | heldout/book/wikisource:384c3f89/total | precision | 97.638% → 97.422% |
| S5 | heldout/book/wikisource:384c3f89/total | f1 | 96.164% → 96.060% |
| S5 | heldout/book/wikisource:384c3f89/accent | precision | 99.194% → 98.927% |
| S5 | heldout/book/wikisource:384c3f89/accent | recall | 97.748% → 97.682% |
| S5 | heldout/book/wikisource:384c3f89/accent | f1 | 98.466% → 98.301% |
| S5 | heldout/book/wikisource:384c3f89/breathing | precision | 98.764% → 98.611% |
| S5 | heldout/book/wikisource:384c3f89/breathing | f1 | 99.147% → 99.070% |
| S5 | heldout/book/wikisource:384c3f89/compound | precision | 88.503% → 88.298% |
| S5 | heldout/book/wikisource:4ad622a4/breathing | precision | 66.667% → 33.333% |
| S5 | heldout/book/wikisource:4ad622a4/breathing | recall | 66.667% → 33.333% |
| S5 | heldout/book/wikisource:4ad622a4/breathing | f1 | 66.667% → 33.333% |
| S5 | heldout/book/wikisource:4f60b077/total | precision | 93.333% → 93.103% |
| S5 | heldout/book/wikisource:4f60b077/total | recall | 90.323% → 87.097% |
| S5 | heldout/book/wikisource:4f60b077/total | f1 | 91.803% → 90.000% |
| S5 | heldout/book/wikisource:4f60b077/accent | precision | 95.455% → 95.238% |
| S5 | heldout/book/wikisource:4f60b077/accent | recall | 95.455% → 90.909% |
| S5 | heldout/book/wikisource:4f60b077/accent | f1 | 95.455% → 93.023% |
| S5 | heldout/book/wikisource:51fe7386/total | precision | 84.091% → 81.522% |
| S5 | heldout/book/wikisource:51fe7386/total | f1 | 81.768% → 81.081% |
| S5 | heldout/book/wikisource:51fe7386/accent | precision | 95.385% → 91.176% |
| S5 | heldout/book/wikisource:51fe7386/accent | f1 | 89.855% → 87.943% |
| S5 | heldout/book/wikisource:51fe7386/compound | precision | 28.571% → 25.000% |
| S5 | heldout/book/wikisource:51fe7386/compound | f1 | 44.444% → 40.000% |
| S5 | heldout/book/wikisource:602cc72e/compound | precision | 46.154% → 38.462% |
| S5 | heldout/book/wikisource:602cc72e/compound | recall | 60.000% → 50.000% |
| S5 | heldout/book/wikisource:602cc72e/compound | f1 | 52.174% → 43.478% |
| S5 | heldout/book/wikisource:9c1dca9b/total | precision | 81.319% → 76.344% |
| S5 | heldout/book/wikisource:9c1dca9b/total | recall | 77.083% → 73.958% |
| S5 | heldout/book/wikisource:9c1dca9b/total | f1 | 79.144% → 75.132% |
| S5 | heldout/book/wikisource:9c1dca9b/accent | precision | 91.379% → 89.286% |
| S5 | heldout/book/wikisource:9c1dca9b/accent | recall | 79.104% → 74.627% |
| S5 | heldout/book/wikisource:9c1dca9b/accent | f1 | 84.800% → 81.301% |
| S5 | heldout/book/wikisource:9c1dca9b/breathing | precision | 61.538% → 57.692% |
| S5 | heldout/book/wikisource:9c1dca9b/breathing | recall | 76.190% → 71.429% |
| S5 | heldout/book/wikisource:9c1dca9b/breathing | f1 | 68.085% → 63.830% |
| S5 | heldout/book/wikisource:9c1dca9b/compound | precision | 50.000% → 37.500% |
| S5 | dev/naming/breathing | precision | 95.699% → 95.588% |
| S5 | dev/naming/subscript | precision | 100.000% → 97.368% |
| S5 | dev/atomic/subscript | precision | 100.000% → 97.368% |
| S5 | dev/presence/merged_accent | precision | 95.000% → 93.319% |
| S5 | dev/class/acute | precision | 99.104% → 98.955% |
| S5 | dev/class/acute | recall | 95.540% → 95.396% |
| S5 | dev/class/circumflex+subscript | precision | 90.909% → 87.500% |
| S5 | dev/class/dasia | precision | 97.059% → 95.804% |
| S5 | dev/class/grave | precision | 97.980% → 97.817% |
| S5 | dev/class/psili | precision | 96.000% → 95.770% |
| S5 | dev/class/psili+acute | recall | 87.143% → 84.286% |
| S5 | dev/book/wikisource:02a3a2a6/accent | precision | 98.062% → 97.897% |
| S5 | dev/book/wikisource:02a3a2a6/compound | recall | 80.851% → 78.723% |
| S5 | dev/book/wikisource:02a3a2a6/compound | f1 | 85.393% → 85.057% |
| S5 | dev/book/wikisource:02a3a2a6/subscript | precision | 100.000% → 90.000% |
| S5 | dev/book/wikisource:02a3a2a6/subscript | f1 | 81.818% → 78.261% |
| S5 | dev/book/wikisource:2793d64c/total | recall | 87.950% → 87.673% |
| S5 | dev/book/wikisource:2793d64c/accent | recall | 93.118% → 92.903% |
| S5 | dev/book/wikisource:2793d64c/breathing | precision | 95.513% → 94.268% |
| S5 | dev/book/wikisource:2793d64c/breathing | recall | 89.759% → 89.157% |
| S5 | dev/book/wikisource:2793d64c/breathing | f1 | 92.547% → 91.641% |
| S5 | dev/book/wikisource:2793d64c/compound | recall | 82.051% → 79.487% |
| S5 | dev/book/wikisource:8b6b0de9/total | precision | 93.309% → 93.253% |
| S5 | dev/book/wikisource:8b6b0de9/accent | precision | 93.578% → 92.665% |
| S5 | capitals/combined | recall | 98.654% → 98.570% |
| S5 | capitals_disagreement/combined | recall | 98.142% → 97.988% |

Owner regressions, including empty-note preservation failures, are explicit in [S6_owner_regressions.jsonl](S6_owner_regressions.jsonl):

- S4 / review: `177b717d-p000097-l0007` — (empty note)
- S5 / review: `177b717d-p000097-l0007` — (empty note)
- S4 / review: `384c3f89-p000030-l0029` — (empty note)
- S5 / review: `384c3f89-p000030-l0029` — (empty note)
- S4 / review: `384c3f89-p000068-l0036` — (empty note)
- S5 / review: `384c3f89-p000068-l0036` — (empty note)
- S4 / examples: `177b717d-p000017-l0012` — missed at 11, 12
- S4 / examples: `384c3f89-p000053-l0023` — (empty note)
- S5 / examples: `384c3f89-p000053-l0023` — (empty note)
- S4 / examples: `384c3f89-p000182-l0031` — (empty note)
- S5 / examples: `384c3f89-p000182-l0031` — (empty note)
- S4 / old_earlier: `51fe7386-p000024-l0020` slot 11 — missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript
- S5 / old_earlier: `51fe7386-p000024-l0020` slot 11 — missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript
- S4 / old_examples: `177b717d-p000017-l0012` — missed at 11, 12
- S4 / old_review: `51fe7386-p000024-l0020` — missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript

## Owner lines whose reading changed

All strings use recogniser base letters plus the indicated detector marks. S4/S5 strings are their frozen standalone readings, never Google. The full machine receipt is [S6_changed_owner_lines.jsonl](S6_changed_owner_lines.jsonl).

| line | S4 | S5 | S6 |
|---|---|---|---|
| 02a3a2a6-p000046-l0014 | Ὠς νὰ τὸν βγάλω πεταχτός, | Ως νὰ τὸν βγάλω πεταχτός, | Ως νὰ τὸν βγάλω πεταχτός, |
| 02a3a2a6-p000307-l0003 | κι ἀνασκομπόνει στ’ ἁψηλα | κι ἀνασκομπόνει στ’ ἁψηλα | κι ἀνασκομπόνει στ’ ἁψηλὰ |
| 02a3a2a6-p000318-l0014 | ει Οριστε; Τόσο φειδωλοὶ | ει Οριστε; Τόσο φειδωλοὶ | ει Ορίστε; Τόσο φειδωλοὶ |
| 177b717d-p000017-l0012 | Ταράζει καὶ ἡ ἀνάσα σου τὰ μαῦρα τῆς Στυγὸς | Ταράζει καὶ ἡ ανάσα σου τὰ μαῦρα τῆς Στυγὸς | Ταράζει καὶ ἡ ανάσα σου τὰ μαῦρα τῆς Στυγὸς |
| 177b717d-p000072-l0001 | Μιὰ κωμωδία ἣ πλάση Του σὰν εἶναι φρικαλεα, | Μιὰ κωμωδία ἣ πλάση Του σὰν ειναι φρικαλεα, | Μιὰ κωμωδία ἣ πλάση Του σὰν εἶναι φρικαλέα, |
| 177b717d-p000097-l0007 | ὀ Σηκουάνας πὄχει πνίξει, | ὀ Σηκουάνας πὄχει πνίξει, | ὀ Σηκουάνας πὄχεἵ πνίξει, |
| 177b717d-p000104-l0007 | ἡ ἀνάμνησή τους ζωηρὴ ἀπομενει. | ἡ ἀνάμνησή τους ζωηρὴ ἀπομενει. | ἡ ἀνάμνησή τους ζωηρὴ ἀπομένει. |
| 2793d64c-p000072-l0007 | μηδ’ ανανδρίας κραυγὴν εκβάλη. | μηδ’ ανανδρίας κραυγὴν εκβάλη. | μηδ’ ανανδριας κραυγην εκβαλη. |
| 384c3f89-p000030-l0029 | “Ει μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, | “Ει μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, | “Εἰ μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, |
| 384c3f89-p000053-l0010 | ἐνναέται τιμαῖς ἡρωισι κυδαινουσιν. | ἐνναέται τιμαῖς ἡρωισι κυδαινουσιν. | ἐνναέται τιμαῖς ἡρωίσι κυδαίνουσιν. |
| 384c3f89-p000053-l0023 | Κύζικον ἐν κονίησι και αἵματι πεπτηῶτα. | Κύζικον ἐν κονίησι και αἵματι πεπτηῶτα. | Κύζικον ἐν κονίησι καὶ αἵματι πεπτηῶτα. |
| 384c3f89-p000053-l0028 | ἣ θέμις, α̈́μ πεδίον λειμώνιον, ἔνθ’ ἔτι νυν περ | ἣ θέμις, άμ πεδίον λειμώνιον, ἔνθ’ ἔτι νυν περ | ἣ θέμις, άμ πεδίον λειμώνιον, ἔνθ’ ἔτι νὓν περ |
| 384c3f89-p000068-l0036 | αὔτως δ’ Ἄρητος μενεδήιον Εὐρύτου υια | αὔτως δ’ Ἄρητος μενεδήιον Εὐρύτου υια | αὔτως δ’ Ἄρητος μενεδήιον Εὐρύτου υἵα |
| 384c3f89-p000091-l0011 | τὣ νυν ἥντιν ἐγὼ τῖσαι χάριν ἄρκιός εἰμι, | τὣ νυν ἥντιν ἐγὼ τῖσαι χάριν ἄρκιός εἰμι, | τὣ νὓν ἥντιν ἐγὼ τῖσαι χάριν ἄρκιός εἰμι, |
| 384c3f89-p000091-l0027 | ηρί γε μὴν ἐπι νῆα κατήισαν ἐγκονέοντες· | ηρί γε μὴν ἐπι νῆα κατήισαν ἐγκονέοντες· | ῆρί γε μὴν ἐπὶ νῆα κατήισαν ἐγκονέοντες· |
| 384c3f89-p000091-l0039 | ἠείδει· οὶος δὲ κατὰ πλατυ βόσκετο τἳφος. | ἠείδει· οὶος δὲ κατὰ πλατυ βόσκετο τἳφος. | ἠείδει· οὶος δὲ κατὰ πλατὺ βόσκετο τἳφος. |
| 384c3f89-p000096-l0031 | τόσσ ἐπὶ γαιαν ἵησι παρὲξ ἕθεν ἄνδιχα βαλλων. | τόσσ ἐπὶ γαιαν ἵησι παρὲξ ἕθεν ἄνδιχα βαλλων. | τόσσ ἐπὶ γαῖαν ἵησι παρὲξ ἕθεν ἄνδιχα βάλλων. |
| 384c3f89-p000121-l0024 | οιος, ἐπεὶ μεσσηγυς ἔτ’ αὐτόθι νεῦσε λιπέσθαι | οιος, ἐπεὶ μεσσηγυς ἔτ’ αὐτόθι νεῦσε λιπέσθαι | οιος, ἐπεὶ μεσσηγὺς ἔτ’ αὐτόθι νεῦσε λιπέσθαι |
| 384c3f89-p000142-l0002 | ηντινα τήνδ’ ὀνόμηνας ἀριγνώτην γεγαυῖαν | ηντινα τήνδ’ ὀνόμηνας ἀριγνώτην γεγαυῖαν | ἥντινα τήνδ’ ὀνόμηνας ἀριγνώτην γεγαυῖαν |
| 384c3f89-p000170-l0031 | Μάκριν τ’ εἰσαφίκανε, Διωνυσοιο τιθήνην, | Μάκριν τ’ εἰσαφίκανε, Διωνυσοιο τιθήνην, | Μάκριν τ’ εἰσαφίκανε, Διωνύσοιο τιθήνην, |
| 384c3f89-p000182-l0006 | νῆα δ’ ἐυκραὴς ἄνεμος φέρεν. αιψα δὲ νῆσον | νῆα δ’ ἐυκραὴς ἄνεμος φέρεν. αιψα δὲ νῆσον | νῆα δ’ ἐυκραὴς ἄνεμος φέρεν. αἳψα δὲ νῆσον |
| 384c3f89-p000182-l0031 | σχέτλιος. ἣ τέ οἱ αιψα καταυτόθι νόστον ἀπηύρων, | σχέτλιος. ἣ τέ οἱ αιψα καταυτόθι νόστον ἀπηύρων, | σχέτλιος. ἣ τέ οἱ αἲψα καταυτόθι νόστον ἀπηύρων, |
| 384c3f89-p000183-l0005 | κύντερα μιξοδίησιν ἁλὸς ῥαιστηρια νηῶν. | κύντερα μιξοδίησιν ἁλὸς ῥαιστηρια νηῶν. | κύντερα μιξοδίησιν ἁλὸς ῥαιστήρια νηῶν. |
| 384c3f89-p000183-l0020 | ἄλλοτε παρβολάδην, ναυτησι δὲ χάρμα τέτυκται· | ἄλλοτε παρβολάδην, ναυτησι δὲ χάρμα τέτυκται· | ἄλλοτε παρβολάδην, ναύτησι δὲ χάρμα τέτυκται· |
| 384c3f89-p000183-l0022 | Ἄργῴη περὶ νηί, Θέτις δ’ ἴθυνε κέλευθον. | Ἀργῴη περὶ νηί, Θέτις δ’ ἴθυνε κέλευθον. | Ἀργῴη περὶ νηί, Θέτις δ’ ἴθυνε κέλευθον. |
| 51fe7386-p000024-l0016 | Τὴν ειδε ποῦ κοκκινιζε σὰν ντροπαλὴ παρθένο, | Τὴν ειδε ποῦ κοκκινιζε σὰν ντροπαλὴ παρθένο, | Τὴν ειδε ποῦ κοκκίνιζε σὰν ντροπαλὴ παρθένο, |
| 51fe7386-p000024-l0020 | Και δὲν ἐπέρασε καιρὸς, χρὁνοι πολλοὶ καὶ μῆνες | Και δὲν ἐπέρασε καιρὸς, χρὁνοι πολλοὶ και μῆνες | Καὶ δὲν ἐπερασε καιρὸς, χρόνοι πολλοὶ καὶ μῆνες |
| 51fe7386-p000026-l0016 | Ἐμπρὸς τρισκότειδο καἶ πἷσω ἐχθροι. | Ἐμπρὸς τρισκότειδο καἶ πἷσω ἐχθροι. | Ἐμπρ͂ὂς τρ͂ἰσκότειδο καἶ πἷσω ἐχθροι. |
| 602cc72e-p000113-l0009 | *Ἄρκτος καὶ ἁλώπῆξ. | *Αρκτος καὶ ἁλώπῆξ. | *Αρκτος καὶ ἁλώπηξ. |
| 602cc72e-p000113-l0016 | Ἀροτἢς καὶ λύκος. | Ἀροτἢς καὶ λύκος. | Ἀρότης καὶ λύκος. |
| 602cc72e-p000113-l0030 | Ἀστρολὄγος ἐξιὼν ἒκἁστοτε ἒσπέρας ἔθος εἶχε τοὺς | Ἀστρολὄγος ἐξιὼν ἒκἁστοτε ἒσπέρας ἔθος εἶχε τοὺς | Ἀστρολογος ἐξιὼν ἑκάστοτε ἑσπέρας ἔθος εῖχε τοὺς |
| 602cc72e-p000155-l0009 | Εὔνουχος καἰ ἶερεύς. | Εὔνουχος καἰ ιερεύς. | Εὔνουχος καὶ ἵερεύς. |
| 602cc72e-p000353-l0006 | Χελιδὼν καὶ κορωνῆ | Χελιδὼν καὶ κορωνῆ | Χελιδὼν καὶ κορωνη |
| 8b6b0de9-p000004-l0028 | βῆμα την ἔκρουε βαρύ | βῆμα την ἔκρουε βαρύ | βῆμα τὴν ἔκρουε βαρύ |
| 8b6b0de9-p000004-l0029 | αντηχουν αγριοι χοροι | αντηχουν αγριοι χοροι | ἀντήχουν ἄγριοι χοροὶ |
| 8b6b0de9-p000007-l0021 | Εις σὲ προσπλέκει ἡ Κλωθω | Εις σὲ προσπλέκει ἡ Κλωθω | Εἰς σὲ προσπλέκει ἡ Κλωθὠ |
| 8b6b0de9-p000007-l0030 | κοιλάδας, εἰς λῃστων σκηνάς· | κοιλάδας, εἰς λῃστων σκηνάς· | κοιλάδας, εἰς λῃστῶν σκηνάς· |
| 8b6b0de9-p000008-l0001 | Καὶ εις τὸν ᾇδην μετὰ σοῦ, | Καὶ εις τὸν ᾇδην μετὰ σοῦ, | Καὶ εἰς τὸν ᾷδην μετὰ σοῦ, |
| 8b6b0de9-p000008-l0002 | “εις ᾷδου ἂν ἡγῆσαι ! | “εις ᾷδου ἂν ἡγῆσαι ! | εἰς ᾷδου ἂν ἡγῆσαι ! |
| 8b6b0de9-p000008-l0019 | εις στεναγμὸν διακαῆ, | εις στεναγμὸν διακαῆ, | εἰς στεναγμὸν διακαῆ, |
| 8b6b0de9-p000008-l0024 | και ἑκατόμβας τελετῆς, | και ἑκατόμβας τελετῆς, | καὶ ἑκατόμβας τελετῆς, |
| 8b6b0de9-p000011-l0014 | τὸ ευγενες του χεἰλος. | τὸ ευγενες του χεἰλος. | τὸ εὐγενές του χεῖλος. |
| 8b6b0de9-p000012-l0006 | και σκοτεινοτερον νυκτὸς | και σκοτεινοτερον νυκτὸς | καὶ σκοτεινότερον νυκτὸς |
| 8b6b0de9-p000016-l0013 | και εἰς πᾶν δένδρον φωλεὰ | και εις πᾶν δένδρον φωλεὰ | και εἰς πᾶν δένδρον φωλεὰ |
| 8b6b0de9-p000016-l0029 | και τὸ προπέμπουσι χοροὶ | και τὸ προπέμπουσι χοροὶ | καὶ τὸ προπέμπουσι χοροὶ |
| 8b6b0de9-p000018-l0026 | Δεν ειναι ἄνθρωποι, οὺρὰ | Δεν ειναι ἄνθρωποι, οὺρὰ | Δἐν εἷναι ἄνθρωποι, οὺρὰ |
| 8b6b0de9-p000021-l0012 | Τί ἂν ὁ βιος διαρκῇ | Τί ἂν ὁ βιος διαρκῇ | Τί ἂν ὁ βἳος διαρκῇ |
| 9c1dca9b-p000015-l0051 | Κυθηροις διαμἑνων κ. Ἐμμανουὴλ Μορμορης. | Κυθηροις διαμἑνων κ. Ἑμμανουὴλ Μορμορης. | Κυθἤροις διαμένων κ. Ἑμμανουὴλ Μόρμορης. |
| 9c1dca9b-p000015-l0057 | “και καλὸς ξεφαντωτης. | “και καλὸς ξεφαντωτης. | καὶ καλὸς ξεφαντωτἡς. |
| 9c1dca9b-p000015-l0060 | Στοὺς σαραντ’ ἁνθεῖ και δένει | Στοὺς σαραντ’ ἁνθεῖ και δένει | Στοὺς σαράντ’ ἁνθεῖ καἰ δένει |
| 9c1dca9b-p000015-l0062 | Στοὐς πενῆντα γιὰ βουλη | Στοὐς πενῆντα γιὰ βουλη | Στοὐς πενῆντα γιὰ βουλὴ |
| 9c1dca9b-p000015-l0067 | μονο τὰ ψωμιὰ χαλᾷ. | μονο τὰ ψωμιὰ χαλᾷ. | μὁνο τὰ ψωμιὰ χαλᾷ. |

## Verification and limits

Run `PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/labelfix -q`: **137 passed**. [Log](S6_pytest.txt). The existing HTTP capture test now sends full HTTP request bytes to the real handler in memory, testing successful append/readback, bad requests and static serving without a socket bind. No server or owner page was built or opened. The initial unmodified socket test failed at the sandbox bind; this was repaired without skipping it.

Reproduce measurements with `scripts/labelfix/s6_validate.py`, then `scripts/labelfix/s6_notes.py`, then `scripts/labelfix/s6_report.py`, using the same Python and `PYTHONPATH`. [Metrics](S6_metrics.json), [line-level evidence](S6_lines.jsonl.gz), [validator log](S6_validate.log), [verification/hashes](S6_verification.json). This CPU evaluation is not a CTC/runtime speed qualification. Tests are scoped to labelfix as requested.

Remaining limits: fused recall is incomplete; the native-component/CTC cohort includes uncertain segmentation and is not a new manual benchmark. Pixel-only capitals still miss more than half of agreement capitals. The 753 disagreement stratum contains most prior-dependent cases. Some capital/ascender guard losses and current owner clauses remain open. DEV naming breathing/compound recall still trails S4 even though physical presence recovers; the fixed naming reader receives changed pixel crops/context. No general no-regression qualification is claimed.

S6 RESULT: presence P 98.6%→98.7% R 89.0%→95.4% (S4 98.5%/89.4%, S5 98.6%/89.0%); capitals combined P/R 96.1%/98.6%, pixel-only P/R 83.3%/46.9%, disagreement-slot P 94.6%; fused slots 756 (370 components), fused R 0.0%→60.5% P —→97.0%; merged-accent R 85.9%→93.5%; marks below meanline 473→0 (capital side marks use their separate S5 zone); held-out P 93.7%→93.8% R 91.6%→92.1%; owner notes current review 14/49→36/49, examples 28/57→33/57; old earlier 45/59→47/59, examples 26/56→32/56; regressions: 68/51 physical character events and 167/142 legacy slots vs S4/S5, combined capital R 98.7%→98.6%, unresolved DEV naming/owner clauses enumerated above.
