# S8a4 — frozen baseline and DEV print-truth cards

**600 original-crop baselines complete.** **DEV: 1649 cards + 144 controls.** **Audit: 48 lines, 114 cards + 10 controls.** Masked DEV processing remains pending. Print adjudication and presence P/R are not yet complete.

## Inputs and evidence acceptance

- Worktree HEAD: `f1d7c83b4166440071d0b46ce26d8bd39c9bc9b8`. Frozen detector/reader/gate and model assets match `c6064650fa5451cbc3bd13197d7a31c0d3bbf33d` byte-for-byte; policy `sf4-release-v1`. [Frozen binding](S8_DEV/evidence/frozen_binding.json). No detector, reader or gate code changed; no git writes or other-worktree writes.
- DEV IDs: 600 distinct; SHA256 `abb2091211f79bfd1862727284931c89670a5527708376435eba64e2c0780faf`. Parliament/vouli 150 each; round1/round2/mixed 100 each. [Copied source receipt](S8_DEV/S8_DEV_receipt.json). [Native crop sources](S8_DEV/evidence/sources.json) contain 600 DEV and 48 disjoint audit lines.
- Debug job **3680506** was reported COMPLETED 0:0 in 5 min 12 s. Its fetched receipt records 304.46 s inside the extractor. S8a4 used only local files with network disabled and ran no reader inference.
- Verified payload SHA256: `fae3140ea1e789ca817d3eec3ec71ae5d47774cf43503b9fa0b25aa54d64e4a2`; request identity SHA256: `0d8a0ad72d0eb59d3ab47d8b81dc21f8e6341d1362b481823106957700238c5c`. [Request](S8_DEV/evidence/S8a3/request.json), [remote receipt](S8_DEV/evidence/S8a3/remote_receipt.json), [offline acceptance](S8_DEV/evidence/S8a4_evidence_acceptance.json).
- Acceptance checks the exact requested ID/crop joins, 600 runtimes, all A/B/E prediction/coverage positions, 600 recogniser/alignment text identities, all historical-A field hashes and flags, 166 requested fetched alignments plus 434 identical local records, 974 B/E shards, 418 selected A shards and four alignment inputs. Remote receipt: inference_runs 0 and input_writes 0. Selected historical A fields were compared exactly remotely; full remote shard hashes were not recomputed.
- The S8a2 extraction STOP is retained byte-for-byte as [extraction_stop_superseded_S8a3.json](S8_DEV/evidence/extraction_stop_superseded_S8a3.json). [extraction_stop.json](S8_DEV/evidence/extraction_stop.json) now cites the accepted successful receipt. Earlier fetch failures and missing-stage lists remain historical evidence, superseded by this acceptance.
- Audit source custody: [audit_input_custody.json](S8_DEV/evidence/audit_input_custody.json). Only selected saved L1M records are copied; the L1 worktree and original crops remain read only.

## Frozen original-crop baseline

**L1M parity: 14/14 detector serializations, AB 14/14 and PRESENCE 14/14.** Proposal text, detailed hold slots, status, label, changes and gate decisions match the saved original projections after JSON normalization. [Parity receipt](S8_DEV/evidence/L1M_original_projection_parity.json). These are method witnesses; remote SF4 overlays were not fetched for the 600 DEV lines.

Rates below count recogniser-indexed letter slots. Unnamed counts affected slots; blob counts, component histograms and affected-line counts are retained in [baseline_by_wave.json](S8_DEV/evidence/baseline_by_wave.json). [Per-line baseline](S8_DEV/evidence/baseline_per_line.jsonl) and compressed per-line caches retain crop hashes, detector serializations, AB/PRESENCE proposals and decisions. HOLD text is a candidate, not a released label.

| Crop / wave | Lines | Letters | Loc unknown | Seg uncertain | Clip top | Clip bottom | Unnamed | Components/letter | AB corrected/unchanged/hold | PRESENCE corrected/unchanged/hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| original / parliament | 150 | 6497 | 600 (9.24%) | 843 (12.98%) | 873 (13.44%) | 951 (14.64%) | 65 (1.00%) | 0.953 | 1/0/149 | 1/0/149 |
| original / vouli | 150 | 6493 | 88 (1.36%) | 190 (2.93%) | 890 (13.71%) | 908 (13.98%) | 89 (1.37%) | 1.033 | 0/4/146 | 0/2/148 |
| original / round1 | 100 | 4233 | 66 (1.56%) | 110 (2.60%) | 533 (12.59%) | 428 (10.11%) | 19 (0.45%) | 1.048 | 4/11/85 | 1/6/93 |
| original / round2 | 100 | 4210 | 58 (1.38%) | 118 (2.80%) | 514 (12.21%) | 402 (9.55%) | 26 (0.62%) | 1.023 | 2/19/79 | 1/10/89 |
| original / mixed | 100 | 4161 | 64 (1.54%) | 128 (3.08%) | 497 (11.94%) | 435 (10.45%) | 16 (0.38%) | 1.036 | 4/11/85 | 1/4/95 |
| original / ALL | 600 | 25594 | 876 (3.42%) | 1389 (5.43%) | 3307 (12.92%) | 3124 (12.21%) | 215 (0.84%) | 1.014 | 11/45/544 | 4/22/574 |

## DEV census and cards

**4942 connected word groups: 1473 disagreements and 3469 all-agree words.** All disagreements are selected, plus 176 all-agree words (ceil 5% independently per wave; seed `S8a-20261017<wave>`). The census retains unselected words and exact inclusion probabilities. [Word census](S8_DEV/evidence/word_census.jsonl), [card plan](S8_DEV/evidence/dev_plan.jsonl), [counts by wave/type/source partition and source pair](S8_DEV/evidence/card_counts.json).

Sources: Google label; saved R1 arm A mark names on recogniser letters; original S6; masked S6 when available; and the frozen SF4 AB proposal as one candidate source. Unscored A positions preserve recogniser marks. B/E saved evidence supports the frozen gate; E is diagnostic. R0 connected-word alignment retains letter, punctuation and boundary disagreements and reference-only words.

| Wave | Disagreements | All-agree 5% sample | Data cards | Elision/alias-only cards |
|---|---:|---:|---:|---:|
| parliament | 544 | 34 | 578 | 2 |
| vouli | 323 | 46 | 369 | 8 |
| round1 | 173 | 34 | 207 | 8 |
| round2 | 205 | 33 | 238 | 10 |
| mixed | 228 | 29 | 257 | 5 |

Overlapping disagreement types: {"mark_form": 1374, "mark_placement": 6, "letters_punctuation_or_boundary": 165}.

Full DEV plan: **1649 data cards + 144 controls**; rendered **1649 + 144**. Controls are at least 8% of the final set, rounded up. Actual fraction: 144/1793 = 8.03%.

Elision scoring: candidates follow the ink convention U+2019 for elision, with printed numeral keraia U+0374/U+0384 protected. Literal source forms are retained in private `raw_forms`. Every DEV word/card carries `elision_alias_only`, `alias_only`, `elision_presence_only` and `scoring_policy`; only differences removable by word-final elision canonicalization/removal qualify. Other accents, breathings, letters and numeral signs stay significant. These flags are private to avoid unblinding readers. SF5 is not applied to this baseline; the saved literal/canonical forms and flags allow later scoring under either elision policy.

Selected policy classes: {"ordinary": 1616, "elision_presence_only": 32, "alias_only": 1}. Alias-only source differences that canonicalize to agreement remain in the all-agree population with its sampling probability. The complete census records their flags even when unselected.

Open [DEV cards](S8_DEV/cards/index.html). Every card shows an original native full-line strip, a uniformly scaled word zoom at most 3x, randomly ordered distinct candidates and “none of these / unreadable”. `items_blind.json` contains no sources, control flags or truth. Answers are blank; private keys are outside the reader folder under `S8_DEV/private/cards/`.

Every planted DEV control was personally checked against its word pixels and full line before planting. [Verified controls](S8_DEV/evidence/controls_verified.json) identify exact review sheets and crop hashes. Controls use a separate seeded DEV pool and do not duplicate selected data words. Distractors remove a mark or swap acute/grave. Audit controls were also re-inspected before reuse. This is preparer verification, not independent print adjudication.

## Audit: all 48 released L1M lines

[Audit cards](S8_DEV/audit/index.html): **48 lines, 114 data cards + 10 controls**. All 14 corrected lines contribute their changed word; all 34 unchanged lines (28 from the 200-line population, six vouli) contribute every disputed mark-bearing word plus ceil 20% of each line’s undisputed mark-bearing words. Result: 14 changed-word, 41 disputed, 59 sampled undisputed cards. Seed `S8a-20261017audit20<line_id>`. [Audit census](S8_DEV/evidence/audit_word_census.jsonl), [counts](S8_DEV/evidence/audit_counts.json), [source selection](S8_DEV/evidence/audit_selection.json).

The original/corrected candidate is not assumed print truth. Four corrected audit cards are canonical elision aliases only, recorded privately. Original print washout, damage and foreign ink remain visible. Controls use the audit’s own pool; ten answers and full-line witnesses are in [audit_controls_verified.json](S8_DEV/evidence/audit_controls_verified.json). Existing independent-reader files under `audit_private/` are preserved.

Give readers only the appropriate `cards/` or `audit/` folder and separate blank answer copies. Keep this report, evidence, source flags and `private/` keys away from readers. Read ink literally, including misprints; do not regularize spelling or accents.

## Validation and pending work

Machine checks and raster review are recorded in [DEV validation](S8_DEV/evidence/dev_validation.json), [DEV visual review](S8_DEV/evidence/dev_visual_review.json), [audit validation](S8_DEV/evidence/audit_validation.json) and [audit visual review](S8_DEV/evidence/audit_visual_review.json). These cover selection, blindness, exact original pixels, uniform zoom geometry, candidate completeness, control identity and frozen-source custody. Card preparation does not establish data-card print truth.

Regression validation: **638 passed, one environment error** in 6.19 s. `test_capture.py::test_server_appends_each_decision_and_serves_static` could not bind its local HTTP socket (`PermissionError: Operation not permitted`). No test was bypassed or claimed passed. Headless local Chrome also failed to launch (`TargetClosedError`, SIGABRT); browser layout is unverified. Final raster QA inspected 58 DEV windows across all five waves, both selection types, elision policies and geometry extremes; all 144 DEV and ten audit controls were inspected separately. [Validation limits](S8_DEV/evidence/S8a4_checks.json).

Raster observations: original washout, foreign ink, clipped line-edge glyphs and source-label overruns remain visible. For example `item_3517b06fcd6c7312` retains a Google word extending beyond the visible original line; the full strip and none-of-these/transcription option let adjudicators reject it. No new pixels or inferred text were created.

After independent adjudication, estimate physical above/below/apostrophe presence P/R using inverse inclusion probabilities, excluding controls. Keep unreadable/unresolved cases unknown and use line/document cluster intervals. The all-agree sample measures shared error; neither agreement nor gate release proves print truth.

**Masked pending: 0/450.** S8a4 deliberately did not run `--masked`; the handoff is still being produced. Parliament stays unmasked. The rerun validates the completed receipt, crop and lines hashes, and ownership maps with dimensions matching the crops and labels 0–5; it reuses saved readers and recomputes detector/gate/card candidates. Additional masked controls require pixel review before planting.

Masked rerun: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/s8_prepare.py --masked`

S8a READY: DEV 600 (masked pending); baseline loc_unknown 3.42% seg_uncertain 5.43% (per wave loc/seg parliament 9.24/12.98%, vouli 1.36/2.93%, round1 1.56/2.60%, round2 1.38/2.80%, mixed 1.54/3.08%); cards DEV 1649 (+controls 144), audit 48 lines 114 cards (+10); masked rerun `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/s8_prepare.py --masked`
