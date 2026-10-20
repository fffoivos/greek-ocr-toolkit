# Label Quality Benchmark — LQB

## Purpose

Compare every label-tool version against frozen **per-class print truth**, keeping changed-label quality separate from recogniser CER and from segmentation acceptance. LQB is the common measurement instrument for B.b correction tools, not another correction algorithm. Segmentation and the content gate additionally need their own decision/owner-mark review sets; LQB does not replace those geometry/admission instruments.

## Owner rules it implements, quoted

`docs/records/labelfix/lqb/LQB_PLAN.md` quotes the owner's question:

> OK there are errors but are they more or less.

The plan's scoring rule answers this without construction-sample credit:

> The scorer reports such items separately as "in-sample", so a version is never credited for fixing what it was tuned on.

This is the plan's implementation requirement, not a second verbatim owner quotation. The repo-wide `AGENTS.md` rule remains:

> Extra measurements go into the evidence record as diagnostics and onto a sheet as a question for the owner.

## Version history

| Truth / scoring record | Change and status |
| --- | --- |
| LQB1 / truth_v1 | Frozen assembly from existing pixel-adjudicated sources; 39,508 items, 1,499 exclusion IDs; explicit source gaps. |
| LQB2 | Alternative exclusion list and immutable truth training-flag sidecar; label-score parity; not a rewrite of truth. |
| LQB3 / score v2 | Expanded SF6 release extraction and baseline; selected-sample audit delta, not population performance. |
| LQB4 / truth_v1_1 preparation | Adds DEV and substitution truth; custody/preflight records retained. |
| LQB5 / score v2.2 | Final truth_v1_1 **61,463 items**, SHA `b54e238ccfd89df91cabf5255ad8c9b8b26701304fb0bf552f12e4baf435fa5b`; later release re-scores use this frozen truth. |
| Current scorer schema | `lqb-score-v1.2` in code; distinct from truth revisions and report filenames such as score_v2_4.json. |

The manifest does not assign a 0.n correction-tool version to LQB. Do not derive one from its report count or truth filename.

## Inputs

Frozen JSONL truth items keyed by line/class/slot, printed answer, provenance, tier, readers and `used_by`; a manifest/SHA and training-flags sidecar; registry `docs/records/labelfix/lqb/versions.json` with version path, SHA, parent, field mapping, overlay/population semantics, status, optional supplemental sources and `trained_on` lineage. Raw parents, post-convention labels, sparse correction overlays and admission subsets are distinct inputs. A path named by a historical receipt must remain retrievable and hash-correct before replay; its presence in documentation is not enough.

Truth sources include locked ia/ib strata where pixel truth exists, C1 adjudication, owner cards/notes, RU1 lead rulings/audit, approved N1 controls/rulings and capitals evidence. The initial inventory has **38,852 marks /60 capitals /467 ru1_yer /24 letters /103 n1_separator /2 ru2_yat**. Initial tiers: **39,001 A /169 B /338 C**. Later truth_v1_1 adds **21,892 S8_DEV heads +63 substitution60 items** to reach 61,463. Reference transcriptions alone are not promoted to pixel truth.

## Algorithm in prose

`greekocr.labelfix.lqb` loads immutable truth and applies validated line-level training flags in memory. Tier A means owner or two blind Opus readers; B is lead pixel ruling; C is agreeing Sol readers and stays separate from A/B headlines. The scorer reports each class/tier separately and exposes the four marks heads (breathing, accent, dialytika, subscript). Supported classes are marks, letters, n1_separator, ru1_yer, ru2_yat, superscript, dash, lunate, lookalike, capitals and crop; unsupported coverage is “not measured,” not zero error.

Version loading verifies each file hash. Sparse overlays inherit their explicit raw parent, with test/dev `parent_splits` loaded from separately SHA-bound raw split files. IDs outside declared parent splits and conflicting supplemental text fail. Admission `inherit_label` restricts the parent population; it does not enlarge it. Historical worktree paths in the registry are real runtime dependencies until explicitly relocated and rebound.

Each truth item is classified as construction/training **in_sample**, rate-ineligible **regression_only**, eligible headline or uncovered. `sample_used()` uses exact `used_by` tags, the N1 `n1_*` wildcard, and explicit training-arm lineage; parent cycles/malformed training declarations fail. Merely renaming a label version does not make exposed truth independent. Paired deltas require both versions to cover the same eligible item and exclude exposure on either side.

Marks use exact per-head identities and the reader union scorer; letters use scoped edit distance; separator/dash slots distinguish baseline/raised dots, comma, hyphen/en/em dash, space/nothing/other. UNKNOWN and inserted/unmatched scope behavior stay explicit. The declared `crop` class always returns unavailable measurement in `error()`: label text cannot measure physical crop correctness. Unit errors and opportunity counts are class-specific; do not combine arbitrary class denominators into one accuracy number.

Per-class errors/opportunities and Wilson intervals accompany paired deltas. The fixed bootstrap uses **4,000** document-cluster resamples, seed **20261017**, preserving within-document pairs. `uniform` and `locked_stratum` can support population claims only when declared eligible. `enriched` and `decision_audit` samples stay selected-sample descriptions; mixed sample types split their reports rather than inheriting a population rate. The scoreboard uses the owner-sheet renderer with the baseline first and printed truth prefilled; historical structural validation is not browser-layout proof.

## Outputs and reason codes

Score JSON schema `lqb-score-v1.2` records truth/flags hashes, training arms, version summaries, paired results and sample-type breakdowns. Each class/tier has status measured/not measured, truth_items, headline/in_sample/regression_only counts and uncovered items. Counts expose items, errors, opportunities, errors_per_100 and intervals. “not measured,” zero opportunities and null intervals are meaningful missing-coverage outputs, not passes. Scoreboard HTML/cards/build/validation receipts are presentation artifacts, not new truth or adoption.

## Evidence: review sets and owner marks

| Tool / evidence | What is measured | Limit |
| --- | --- | --- |
| RU1 v1 | Tier-B audit **40 positions /0 errors**; separate 24 tier-B in-sample positions. Initial Google tier-A covered 49 soft-sign positions has 26 errors. | The construction-visible 49 tier-A positions remain in-sample for RU1; small audit does not prove a 99% population gate. |
| RU1 test/dev counterpart | `score_ru1_v3_test_edits.json` with same-population raw test/dev baseline. | No covered test/dev ru1_yer truth, so **409 edits are not measured** by LQB. |
| N1 W1 | Frozen 103 separator items retain **33 errors**, all in-sample; zero edited W1 rows overlap truth. | Zero eligible paired separator headline items; no held-out improvement claim. |
| SF6 LQB5 audit100 | **87→16 head errors /2,232 heads** on the decision-audit sample. | Selected corrected-line audit, not a population estimate. |
| SF6 LQB5 DEV | Only **2/391** certified lines covered; covered-subset weighted delta −0.044 pp. | Full DEV population delta undefined; bootstrap degenerate. |
| SF6 substitution60 | **0/57** certified lines covered. | Release delta not measured. |
| SF7 A/B choice | A **604 heads /20 lines**, B **564 /19**, both 100% tier-A/B precision; fixed tie selects A. | Four-way common 536 heads /18 lines are all unchanged, so no correction-gain measurement. |
| Dashes 0.1 | Literal tags, no standalone corrected-label version in the registry. | No general dash repair delta to claim. |

LQB is how a proposed label tool is compared with its parent: register exact bytes and lineage, replay the same frozen truth, show paired and native coverage, separate construction exposure, then present the saved results for owner review. Successful registration is not adoption, and a score over no relevant truth does not qualify a release. The owner-sheet decision/correction marks are separately preserved under stable IDs; they must not be silently converted into independent benchmark truth without provenance/tier/exposure review.

## Tests

`tests/test_lqb.py` covers paired deltas, fixed-seed whole-document resampling, in-sample separation, C-tier isolation, missing/unfetched versions, regression-only scope, union marks, scoped letter errors, partial dash truth, selected-sample rate suppression, overlays/admission populations, flags and training lineage cycles. `tests/test_lqb3.py` retains historical source/output custody assertions. LQB1b reports **41 passed**, LQB2 **54**, LQB3 **83**, LQB5 **113**; these are each run's recorded evidence, not current integration-suite results.

RU4E2's environment audit found 14 LQB failures in one x86/NumPy/SciPy setup; a compatible arm64 environment passed 82/83, with one historical release-exclusion hash drift. It expressly did not rewrite expected hashes to hide that failure. This documentation run did not execute scoring, tests, source imports or peer-worktree dependencies.

## Known limitations

Truth is frozen and per-class but coverage is uneven. Construction exposure, trained models, sampling design and edition/word scope constrain independence; class names alone do not certify an untouched benchmark. The live scorer still dynamically imports the union scorer from `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/scripts/labelfix/r2_score.py` and statistics from `~/Projects/greek-ocr-toolkit-cleanup/greekocr/adjudicate/score.py`; registry paths also name peer worktrees. Current code wins over any claim that integration has made LQB self-contained. No path repair was authorized in CLEAN5C.

Bulk truth files and sheets may exceed cleanup's 5 MB policy; `PLAN.md` requires custody outside git with receipts, not deletion of the frozen truth. This document neither relocates nor claims fresh hash verification of those artifacts. Historical scoreboard receipts explicitly say layout not verified; successful structural checks are not visible UI validation.

## Code paths

`greekocr/labelfix/lqb.py`; assembly/version/scoreboard helpers in `scripts/lqb/`; `docs/records/labelfix/lqb/{versions.json,truth_v1_1.jsonl,truth_v1_1_flags.jsonl}` and manifests/scores/receipts; `tests/test_lqb.py`, `tests/test_lqb3.py`. SF7 choice uses its specific guarded scoring in `artifacts/sf7_rc1/lqb_scores.json`, explained by `SF7_RC1_LQB.md`; do not substitute the general registry's historical SF6 entries for that preregistered comparison.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`.
- `docs/records/labelfix/lqb/{LQB_PLAN.md,LQB1_RECEIPT.json,LQB2_RECEIPT.json,LQB3_RECEIPT.json,LQB5_RECEIPT.json,versions.json}` (inventory, lineage, coverage and validation fields).
- `greekocr/labelfix/lqb.py`; `tests/test_lqb.py` (targeted scoring/test-source reads).
- `docs/records/labelfix/lqb/{score_ru1_v3_train.json,score_ru1_v3_test_edits.json}` (yer counts/coverage).
- `docs/records/labelfix/secondary/{N1W1_REPORT.md,RU1_LEAD_REVIEW.md,RU4E2_REPORT.md,RU4EF3_REPORT.md}`; `docs/records/labelfix/spellcheck/SF7_RC1_LQB.md`.
- `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` (owner-sheet contract).
