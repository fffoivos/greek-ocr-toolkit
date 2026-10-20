# M2 — combined accent checker on the new-source blind cards

Measured offline on Mac CPU. Task launch head `e702e666efe23371af9b2dd81392e856509dee9f`; execution receipt at `5a47e622b831bf3f2cb724bf8e75cdc0571e2168`. **513 inventory cards / 13 cohorts; 473 Greek or mixed-script lines inferred / 12 cohorts; 40 Russian cards excluded.** This task made no detector, recognizer, reader or Git metadata writes. The shared checkout advanced externally by one unrelated brief (`docs/records/briefs/S7_toolkit_substitutions.md`); all protected inference code remained byte-identical. This is a transfer measurement on the existing blind cards, not a random population estimate.

**PRESENCE corrects 25/77 enumerated pairs, holds 40 and misses 12; FULL corrects 24, holds 41 and misses 12.** All 12 misses involve recognizer base-letter failures. On marks-correct controls, accepted changes affect 30 slots under PRESENCE and 15 under FULL. FULL reduces those changes while sending one additional known error to HOLD. Both modes have high line-level HOLD rates; this measurement does not establish safe automatic correction.

## Contract and denominators

- E3 `full_s0` supplies the text and CTC spans. The recognizer’s combining marks are discarded when rendering; R1 inputs use only crop pixels, spans and base identity. Neither Google text nor a blind verdict enters inference.
- S6 `reading.read_ink(filtered=False)` supplies segmentation, mark names/presence, elisions and opening quotes. R1-A uses `r1_extract.extract_line(evaluation=True)` and its exact wide font-size windows and mask. Both modes use R1 names. PRESENCE compares mark families (breathing/accent/dialytika/subscript); FULL compares complete mark-name sets.
- Missing R1 coverage, unknown detector localization, unnamed detected marks and disagreement are HOLD. Non-reader consonants carrying detector marks are HOLD. A HOLD retains a visible proposal and is never counted as corrected or as an accepted new error.
- `reading.apply_constraints` uses its current default rules and default `output="print"`: preserve printed proposals and flag K1 conflicts as HOLD, including held-back rule flags. No historical `normalised` deletion policy is substituted. S6 elisions/opening quotes are preserved in composition.
- Error unit: one explicit printed→Google mark-only word/fragment pair. There are **77 pairs**, covering 77 letter clusters with differing mark sets. Every arrow segment is preserved in [M2_pair_ledger.jsonl](M2_pair_ledger.jsonl); inseparable base-letter/span errors and punctuation-only pairs are excluded with reasons. Pairs on `marks: na` / `letters: n` cards remain included when the pair itself has identical bases.
- Each pair must have all its letters matched monotonically and without inserted recognizer letters inside the fragment. A recognizer letter failure is missed/unscorable. Otherwise any HOLD in the entire word/fragment makes the pair HOLD; correction requires all letter mark sets in that pair to equal the printed reference. Quotes/apostrophes remain explicit in the readings but are outside this combining-mark metric; a breathing recovery is not certification of punctuation recovery.
- Printed and Google sides are taken literally from the verdicts, with explanatory parentheses removed. The one `῞Ο` spacing-mark notation is converted to `Ὅ`. Acute/tonos canonically normalize under NFD. “Final” grave→acute includes the final accented syllable followed by consonants. The ο/η/ε type includes initial ἑ in a fragment such as ἑκα-.
- Marks-correct controls include every card whose verdict explicitly says `marks: y`, including two cards with base-letter errors elsewhere. An exact mark-stripped character alignment is used only after inference. Count changed accepted Greek letter slots, plus elementary added/removed marks; acute→grave is one changed slot and two elementary edits. Latin/Cyrillic diacritics are outside the Greek accent metric. HOLD proposals are reported separately. These are upper bounds on new errors conditional on the blind labels, not freshly adjudicated errors. Unmatched letters cannot be scored.
- HOLD percentages use the 473 inferred lines, and per-source inferred denominators; the 40 excluded Russian cards never inflate coverage. Crop-overrun/clipping flags and Google letter errors are retained as annotations. They do not suppress inference globally. Word/fragment letter failures are explicitly unscorable; no label-assisted repair or forced alignment is used.

## Source × error type × agreement mode

| Source | Type | Pairs | PRESENCE corrected / HOLD / missed | FULL corrected / HOLD / missed |
|---|---|---:|---:|---:|
| anemi_poly1850 | capital breathing lost/quote | 5 | 0 / 2 / 3 | 0 / 2 / 3 |
| anemi_poly1850 | other | 2 | 0 / 2 / 0 | 0 / 2 / 0 |
| bsb_mixed | breathing→acute on ο/η/ε | 1 | 1 / 0 / 0 | 1 / 0 / 0 |
| bsb_mixed | subscript dropped | 1 | 1 / 0 / 0 | 1 / 0 / 0 |
| bsb_mixed | other | 4 | 1 / 1 / 2 | 1 / 1 / 2 |
| bsb_poly1850 | capital breathing lost/quote | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| bsb_poly1850 | subscript dropped | 2 | 1 / 0 / 1 | 1 / 0 / 1 |
| bsb_poly1850 | other | 1 | 1 / 0 / 0 | 1 / 0 / 0 |
| gazette_modern | no enumerated mark pairs | 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| gazette_poly1900 | grave→acute final | 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| gazette_poly1900 | capital breathing lost/quote | 2 | 0 / 2 / 0 | 0 / 2 / 0 |
| gazette_poly1900 | other | 2 | 0 / 2 / 0 | 0 / 2 / 0 |
| ia_greek_latin | breathing→acute on ο/η/ε | 4 | 3 / 1 / 0 | 3 / 1 / 0 |
| ia_greek_latin | other | 9 | 3 / 4 / 2 | 2 / 5 / 2 |
| ia_poly1850 | grave→acute final | 1 | 1 / 0 / 0 | 1 / 0 / 0 |
| ia_poly1850 | subscript dropped | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| ia_poly1850 | other | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| ia_russian | no enumerated mark pairs | 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| kosmopolis_poly | grave→acute final | 3 | 2 / 0 / 1 | 2 / 0 / 1 |
| kosmopolis_poly | capital breathing lost/quote | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| kosmopolis_poly | other | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| lekythos_poly1900 | grave→acute final | 4 | 3 / 1 / 0 | 3 / 1 / 0 |
| lekythos_poly1900 | other | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| nlg_poly | capital breathing lost/quote | 5 | 0 / 5 / 0 | 0 / 5 / 0 |
| nlg_poly | subscript dropped | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| oa_poly1900 | grave→acute final | 8 | 2 / 4 / 2 | 2 / 4 / 2 |
| oa_poly1900 | capital breathing lost/quote | 4 | 1 / 3 / 0 | 1 / 3 / 0 |
| oa_poly1900 | other | 3 | 2 / 1 / 0 | 2 / 1 / 0 |
| pleias_poly1850 | grave→acute final | 2 | 1 / 1 / 0 | 1 / 1 / 0 |
| pleias_poly1850 | capital breathing lost/quote | 1 | 0 / 1 / 0 | 0 / 1 / 0 |
| pleias_poly1850 | other | 5 | 2 / 3 / 0 | 2 / 3 / 0 |
| POOLED | grave→acute final | 19 | 9 / 6 / 4 | 9 / 6 / 4 |
| POOLED | capital breathing lost/quote | 19 | 1 / 15 / 3 | 1 / 15 / 3 |
| POOLED | breathing→acute on ο/η/ε | 5 | 4 / 1 / 0 | 4 / 1 / 0 |
| POOLED | subscript dropped | 5 | 2 / 2 / 1 | 2 / 2 / 1 |
| POOLED | other | 29 | 9 / 16 / 4 | 8 / 17 / 4 |

Unlisted source/type combinations have zero enumerated pairs. The full five-type grid is in [M2_metrics.json](M2_metrics.json).

## Coverage, flags and HOLD

| Source | Inventory / inferred | Blind letter problem | Crop flags | Font admitted / vowel-ρ slots | PRESENCE HOLD lines | FULL HOLD lines |
|---|---:|---:|---:|---:|---:|---:|
| anemi_poly1850 | 40 / 40 | 6 | 10 | 955 / 957 (99.8%) | 35 (87.5%) | 35 (87.5%) |
| bsb_mixed | 40 / 40 | 15 | 0 | 404 / 404 (100.0%) | 30 (75.0%) | 30 (75.0%) |
| bsb_poly1850 | 33 / 33 | 3 | 4 | 722 / 722 (100.0%) | 27 (81.8%) | 27 (81.8%) |
| gazette_modern | 40 / 40 | 0 | 8 | 958 / 966 (99.2%) | 40 (100.0%) | 40 (100.0%) |
| gazette_poly1900 | 40 / 40 | 2 | 2 | 869 / 871 (99.8%) | 35 (87.5%) | 36 (90.0%) |
| ia_greek_latin | 40 / 40 | 3 | 1 | 292 / 293 (99.7%) | 24 (60.0%) | 27 (67.5%) |
| ia_poly1850 | 40 / 40 | 1 | 0 | 852 / 852 (100.0%) | 27 (67.5%) | 30 (75.0%) |
| ia_russian | 40 / 0 | 2 | 11 | 0 / 0 (—) | 0 (—) | 0 (—) |
| kosmopolis_poly | 40 / 40 | 1 | 18 | 785 / 787 (99.7%) | 26 (65.0%) | 26 (65.0%) |
| lekythos_poly1900 | 40 / 40 | 1 | 17 | 639 / 639 (100.0%) | 27 (67.5%) | 30 (75.0%) |
| nlg_poly | 40 / 40 | 3 | 11 | 870 / 870 (100.0%) | 30 (75.0%) | 30 (75.0%) |
| oa_poly1900 | 40 / 40 | 3 | 4 | 733 / 735 (99.7%) | 35 (87.5%) | 37 (92.5%) |
| pleias_poly1850 | 40 / 40 | 5 | 14 | 779 / 780 (99.9%) | 31 (77.5%) | 32 (80.0%) |
| POOLED | 513 / 473 | 45 | 100 | 8858 / 8876 (99.8%) | 367 (77.6%) | 380 (80.3%) |

All 473 eligible crops opened and ran. The 43 Greek/mixed cards with blind `letters: n/u` were inferred and flagged, with their mismatched reference letters excluded locally from change counts. The only entire-card skips are the 40 Cyrillic-cohort cards. This retains usable mark evidence in a card with a different letter problem elsewhere. Font-size admission measures the 16 R1 vowel/ρ base identities, not every consonant.

Font rejection reasons: {"width_outside_0.2_2.0_median_ctc": 17, "width_outside_0.1_2.0_pixel_height": 1}.

## Changes on marks-correct cards

| Source | Correct-mark cards | PRESENCE changed accepted slots / mark edits | FULL changed accepted slots / mark edits | PRESENCE HOLD reference marks / all HOLD slots | FULL HOLD reference marks / all HOLD slots |
|---|---:|---:|---:|---:|---:|
| anemi_poly1850 | 29 | 1 / 2 | 1 / 2 | 71 / 92 | 71 / 92 |
| bsb_mixed | 20 | 1 / 1 | 1 / 1 | 20 / 18 | 23 / 20 |
| bsb_poly1850 | 27 | 0 / 0 | 0 / 0 | 26 / 49 | 28 / 50 |
| gazette_modern | 40 | 10 / 20 | 5 / 10 | 171 / 269 | 181 / 279 |
| gazette_poly1900 | 34 | 4 / 7 | 2 / 3 | 73 / 125 | 81 / 131 |
| ia_greek_latin | 27 | 2 / 4 | 0 / 0 | 21 / 22 | 29 / 28 |
| ia_poly1850 | 36 | 4 / 8 | 4 / 8 | 52 / 61 | 63 / 67 |
| ia_russian | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| kosmopolis_poly | 33 | 1 / 2 | 1 / 2 | 36 / 40 | 36 / 40 |
| lekythos_poly1900 | 34 | 1 / 2 | 0 / 0 | 50 / 56 | 55 / 59 |
| nlg_poly | 35 | 1 / 2 | 0 / 0 | 35 / 57 | 38 / 59 |
| oa_poly1900 | 26 | 1 / 2 | 0 / 0 | 68 / 71 | 77 / 78 |
| pleias_poly1850 | 29 | 4 / 7 | 1 / 1 | 88 / 108 | 95 / 113 |
| POOLED | 370 | 30 / 57 | 15 / 27 | 711 / 968 | 777 / 1016 |

Across controls, PRESENCE changes accepted marks on 29 cards; FULL on 15. Of accepted changed slots, 28 / 30 (PRESENCE) and 14 / 15 (FULL) also have complete matching word bases. HOLD affects 711 printed-reference marks on 642 marked slots (PRESENCE), and 777 marks on 690 marked slots (FULL); the larger all-HOLD-slot counts also include originally bare letters. Including visible HOLD proposals, changed slots are 259 and 259; these are not accepted corrections. **251 reference Greek letters on controls are unscorable because the recognizer did not match them.** New-error upper bounds apply to mapped letters; they do not imply these unmatched letters were preserved.

## Twenty visual checks

Visual outcomes: {'yes': 14, 'uncertain': 3, 'no': 3}. Evidence: [panels 1](M2_visual/review_1.png), [2](M2_visual/review_2.png), [3](M2_visual/review_3.png), [4](M2_visual/review_4.png).

Twenty accepted changed words were selected deterministically, prioritizing blind mark-error cards and limiting repeated cards/sources. Crops were viewed directly; the review does not tune either model or any acceptance rule. This targeted check is not a precision estimate.

| # | Card | Mode | Google → proposal | Matches print? | Pixel observation |
|---:|---|---|---|---|---|
| 1 | t4c/bsb_mixed/c001 | PRESENCE | ή, → ἡ | yes | Curved breathing above eta; the proposal restores a breathing rather than an acute. |
| 2 | t4c/bsb_mixed/c008 | PRESENCE | δόξη, → δόξῃ | yes | Acute above omicron and a separate short iota below eta are visible. |
| 3 | t4c/bsb_poly1850/c013 | PRESENCE | σπειροειδή → σπειροειδῆ | yes | A horizontal curved circumflex is visible above final eta. |
| 4 | c0/ia_greek_latin/c004 | PRESENCE | έκα- → ἑκα | yes | The initial epsilon has a curved smooth breathing, not an acute stroke. |
| 5 | c0/ia_greek_latin/c009 | PRESENCE | άλλως → ἄλλως | yes | The initial alpha carries both a breathing lobe and an acute stroke. |
| 6 | c0/ia_poly1850/c025 | PRESENCE | Ἱερουσαλήμ → Ἱερουσαλὴμ | yes | The final eta accent slopes down to the right as a grave; the initial capital breathing remains. |
| 7 | c0/kosmopolis_poly/c020 | PRESENCE | μοναδικό → μοναδικὸ | yes | A distinct grave slopes down to the right above final omicron. |
| 8 | c0/kosmopolis_poly/c039 | PRESENCE | ξανθός, → ξανθὸς | yes | The accent over omicron has the grave direction, before final sigma. |
| 9 | t4c/lekythos_poly1900/c014 | PRESENCE | φωτεινή → φωτεινὴ | yes | The final eta has a faint but visible grave stroke. |
| 10 | t4c/lekythos_poly1900/c037 | PRESENCE | νεανική → νεανικὴ | yes | The final eta accent slopes as a grave. |
| 11 | t4c/oa_poly1900/c006 | PRESENCE | πουλί → πουλὶ | yes | The mark above final iota slopes as a grave. |
| 12 | t4c/oa_poly1900/c008 | PRESENCE | πειθούς → πειθοῦς | yes | A broad curved circumflex is visible over upsilon. |
| 13 | t4c/pleias_poly1850/c010 | PRESENCE | κάπως → κἄπως | yes | Two lobes/strokes above alpha support the printed breathing-plus-acute quirk. |
| 14 | t4c/pleias_poly1850/c028 | PRESENCE | τουλάχιστον → τοὐλάχιστον | uncertain | A compact detached blob lies above upsilon, but its shape does not resolve a breathing; neighbouring-line ink is present. |
| 15 | t4c/anemi_poly1850/c027 | PRESENCE | αὐ → αὑ | uncertain | The very small upsilon breathing is present, but these pixels do not resolve smooth versus rough confidently. |
| 16 | t4c/bsb_poly1850/c033 | PRESENCE | πρώτη → πρώτῃ | yes | A separate short subscript is visible below eta; omega retains its acute. |
| 17 | t4c/gazette_modern/c005 | PRESENCE | όπως → ὁπως | no | The initial omicron has the compact modern accent, with no visible curved breathing; replacing its acute with dasia is unsupported. |
| 18 | t4c/gazette_modern/c007 | PRESENCE | ένσταση → ἐνσταση | no | The initial epsilon has a compact modern accent; no distinct smooth breathing is visible. |
| 19 | t4c/gazette_poly1900/c015 | PRESENCE | ἀποτελεῖ → ἀποτελεί | no | The printed iota carries a clear curved circumflex; changing it to acute contradicts the crop. |
| 20 | t4c/gazette_poly1900/c018 | PRESENCE | ἐπόμενον → ἑπόμενον | uncertain | The initial epsilon breathing is a small nearly solid blob; its handedness is unresolved at native resolution. |

## Limits and reproducibility

The recognizer itself is out of domain on several crops. HOLD protects many disagreements but does not establish correctness when detector and reader agree incorrectly. New changes on blind marks-correct lines remain a direct limitation. Explicit printed→Google pairs are a lower bound: unenumerated Google errors are not included. Multiple pairs on one card and repeated books are dependent; no binomial confidence interval is claimed.

PRESENCE missed reasons: {"recognizer_base_letter_problem": 12}.

Runtime receipt: [M2_runtime_receipt.json](M2_runtime_receipt.json). Models, input manifests, crops, protected sources and alignments are SHA-256 bound; the run checked those inputs and protected code unchanged. E3 checkpoint `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663`; R1-A epoch 8, `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636`. The initial run newly aligned all 473 crops and completed recognition plus composition in 54.0 s; [its receipt](M2_initial_runtime_receipt.json) notes the original head-field timing issue. A bound-cache replay verifies the finalized wrapper and completed in 34.5 s, 4 Torch threads. No training or threshold fitting.

```sh
PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_run.py --launch-head e702e666efe23371af9b2dd81392e856509dee9f
PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_score.py
PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_verify.py
```

Validation: [M2_validation.json](M2_validation.json), PASS. It verifies model/input/crop/source hashes; exact launch-commit inference sources; 513/473/40 cardinalities; all sample admission and reading-letter identities; FULL acceptance contained in PRESENCE; pair/control aggregation; unchanged native review pixels; and byte-identical initial/replay runtime outputs.

Artifacts: [M2_lines.jsonl.gz](M2_lines.jsonl.gz) (all 513 cards, including skips, runtime evidence, Google references, per-mode text/HOLD/change lists); [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl); [M2_pair_ledger.jsonl](M2_pair_ledger.jsonl); [M2_metrics.json](M2_metrics.json); [M2_spotchecks.jsonl](M2_spotchecks.jsonl). Scripts: `scripts/labelfix/m2_run.py`, `scripts/labelfix/m2_score.py`, `scripts/labelfix/m2_review.py`, `scripts/labelfix/m2_verify.py`. Alignment cache: `.cache/labelfix/m2/align_s0.jsonl`.

M2 RESULT: 473 lines/12 sources; Google mark errors 77: PRESENCE corrected 25 HOLD 40 missed 12; FULL corrected 24 HOLD 41 missed 12; new changes on marks-correct cards PRESENCE 30 FULL 15; lines with HOLD PRESENCE 77.6% FULL 80.3%
