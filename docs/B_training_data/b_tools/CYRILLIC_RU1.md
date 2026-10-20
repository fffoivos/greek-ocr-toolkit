# Historical Russian hard-sign correction — RU1 / tool 0.3

## Purpose

Repair Google's word-final **ь→ъ** confusion where the printed historical Russian glyph is a hard sign. Preserve all other raw Google bytes. This is a label correction, not a general Cyrillic spell checker or modernization. The manifest `docs/harvest/line_pipeline/tool_versions.json` qualifies **cyrillic 0.3**, iterations `ru1_v1`, `ru1_v2_train`, `ru1_v3_edits`, scope historical Russian ь→ъ only. RU4 stages create a held-out counterpart; they do not add a fourth manifest tool generation.

## Owner rules it implements, quoted

`docs/records/labelfix/secondary/PLAN.md` records:

> Labels are the ink. Misprints stay. No correction may override the image.

> Anything uncertain becomes HOLD, never a guess.

The plan's RU1 rule is:

> Google ъ and non-final ь are never touched.

These are recorded standing rules, not a newly obtained ruling in CLEAN5C. The current integration adds an explicit applicability contract: declared Russian language **and** `historical_russian` orthography. Cyrillic script alone supplies neither.

## Version history

| Version / stage | Population / change / status |
| --- | --- |
| ru1_v1 / tool 0.1 | W1 ia_russian positions; two-reader decisions and lead rulings; parent w1_label. Later superseded for the v2 train task. |
| ru1_v2_train / tool 0.2 | v2 Cyrillic training application; parent collection_v2_train. |
| ru1_v3_train, superseded intermediate | Retained convention diffs through its parent; not the edits-only release to consume. |
| ru1_v3_edits / tool 0.3 | Exact raw import overlay, nine Russian train books; **451 ь→ъ**, **256 hold rows**. SHA `4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0`. |
| RU4E | Original nine-book test/dev selection had empty scope; preserved as a record. |
| RU4E2 | Actual test/dev Cyrillic selection: 3,552 test +411 dev rows in 13 books; 1,753 candidate positions in 1,359 lines; 16 contexts ×2 prepared. |
| RU4EF1 | Original contexts 23 VALID /5 VOID /4 FAILED; 274 edit_hard /698 keep_soft /781 held; nine replacement contexts prepared. |
| RU4EF2 | Six replacements valid; **409 edit_hard /1,094 keep_soft /250 holds**; r5 replacements prepared for three failed logical roles. |
| RU4EF3 / ru1_v3_test_edits | Sparse counterpart issued: **409 edits /354 edited rows**, **250 held positions /194 rows**; 548 output rows (470 test,78 dev). SHA `c4b3a248b660ce670e35a2ac9b9c4e5380f357f1ab3ec3c488de67de61a756a1`. |

The current LQB registry retains historical entries; existence of an old entry does not make it the manifest-selected release. Use `ru1_v3_edits`, not convention-inheriting `ru1_v3_train`.

## Inputs

Raw Google label, stable row ID and split, exact crop and parent hashes, declared language/orthography, candidate word-final code-point offsets, independent reader answers with context/coverage/control/scanner provenance, and lead rulings/audit. Same-book printed hard/soft reference glyphs are comparison evidence, not an orthographic prior treated as truth.

Train parent is `google_raw_v2_import` (SHA `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`). The test/dev overlay inherits explicitly registered raw test/dev splits, not the train population; its registry `parent_splits` determines the loader population.

## Algorithm in prose

Integration routes Cyrillic text, then checks applicability using `russian_eligible()`: a Russian language alias and `orthography_for(...,"cyrillic")=="historical_russian"`. Declared modern Russian/Serbian can produce verified no-change evidence; an uncertain historical declaration cannot be invented from OCR script.

The historical RU1 bed enumerates only Google-final-ь positions, presents isolated blind glyph questions, checks context controls/rollout cleanliness and joins by row+offset. `ru1_decide.py` is the **early v1 proposal combiner**, not a universal latest-release rule: it permits a hard proposal with two hard votes and at least one VALID context, and originally sends orthographic-prior disagreements to lead review. Its actual behavior must not be rewritten as if both contexts were always required VALID there. Later RU4 protocols require two admitted independent hard calls and preserve coverage gates. Missing, invalid, unviewed, conflicting or uncertain evidence yields holds/review rather than edits.

The lead compared the small flag at the top of ъ with same-book ь. The Google-derived orthographic prior was withdrawn as a review trigger after it reproduced Google's flattening error. Apply only ruled hard-sign offsets; never repair yat ѣ under RU1. V3 materialization overlays only the declared ь→ъ edits onto exact raw imports. Forward diff/inverse reconstruction and loader readback prove every untouched byte remains raw. Omitted sparse IDs inherit raw text. Held slots retain raw ь; a row may carry both accepted edits and holds.

The integrated result validator enforces only ь→ъ and word-final positions, binds tool version/digest, parent/id/split/crop/raw hash and rejects producer holds as successful corrections. Thus a historical sparse label can retain an accepted edit plus hold metadata, while the integrated pipeline may HOLD that row rather than admit it.

## Outputs and reason codes

Position decisions include `edit_hard`, `keep_soft`, lead_review/hold and provenance. Early proposal reasons include `missing_independent_reads`, `reader_disagreement`, `uncertain_read`, `only_void_hard_reads`, and historical `prior_disagreement`. Lead findings additionally preserve `hold_yat` and `hold_uncertain`; no yat repair is emitted. Release rows include parent text, corrected text, exact edits, holds, explicit status and basis. The integration rejects out-of-scope results with `RU1 requires Russian language and historical Russian orthography`, and explicit producer holds become `required_evidence_unresolved` with no applied pipeline edits.

## Evidence: review sets and owner marks

Initial C1 ink adjudication found **26/49 Google soft-sign positions wrong**, **0/26 hard signs wrong**. The lead's 27-position review ruled **23 hard /1 soft /2 yat /1 uncertain**. Among 21 prior disagreements, every decided hard sign agreed with the readers; this is why the Google-derived prior was withdrawn. Seeded audit: **30/30 edit_hard confirmed ъ**, **10/10 keep_soft confirmed ь**; about 10% is the rule-of-three upper false-edit bound for n=30, not proof of 99% precision.

These lead marks are recorded in `docs/records/labelfix/secondary/RU1_LEAD_REVIEW.md`, mapped to positions through the RU1-L sheet index. They are distinct from owner adoption; the owner-facing sheet explains shape comparisons rather than asking the owner to read Cyrillic. LQB's v1 score separates the **40 tier-B audit positions with zero errors** from **24 tier-B in-sample positions**; the 49 covered tier-A positions are in-sample for ru1_v1. Do not combine them into a fresh independent accuracy panel.

RU4EF3's lead audit confirms **30/30 sampled cells**. Its remaining unruled review positions retain raw Google. Per-edit provenance distinguishes individual audit checks from sampled-audit acceptance; it does not claim that all 409 edits received individual pixel rulings. The test/dev LQB re-score is unchanged on covered truth, with **zero covered test/dev ru1_yer truth items**: it cannot measure those 409 edits.

Wave-1c outcome, as recorded in `docs/records/labelfix/secondary/PLAN.md` §14 and `HANDOFF_20261018.md` (the detailed external experiment report was not independently read here): on **135 changed-label test rows**, CER **1.68%→1.25%**; ъ emitted at **144 corrected positions: 104→127/144**. Cyrillic class CER **1.199→1.174**, reported −0.026 pp and inside the control range. The preregistered H6 class rule remains **REFUTED**. This validates RU1 as a targeted label tool; it is not a class-CER lever or grounds for further RU experiments.

## Tests

Existing `tests/test_ru1_decide.py` covers candidate scope, independence, missing second reader, joins and prior disagreements. `tests/test_ru12.py` covers exact population/parent, untouched characters, protected slots, holds, manifests and sheet structure. `tests/test_ru4e.py`, `test_ru4e2.py`, `test_ru4ef1.py` cover scope, offset custody, pack/reader routing and finalization. RU4EF3 reports **34 protocol tests passed**, LQB registration and full parent loader readback; RU4E2 reports 29 RU protocol and 11 scanner passes. Its LQB investigation reports 69 pass/14 fail in an incompatible x86 environment versus 82 pass/one historical external-hash failure in a compatible environment. Those are historical results; this pass ran no tests or readers and did not alter old receipts.

## Known limitations

Only final ь→ъ is qualified; yat, variant т and general spelling remain separate/parked. The script gate does not license historical Russian edits in Serbian or other Cyrillic books. The prior was derived from faulty labels and cannot decide ink. Sampled audits are small; held rows and zero LQB counterpart coverage remain explicit. Historical receipt paths can name peer worktrees; integrated path availability is not a revalidation of their historical input hashes.

## Code paths

`greekocr/harvest/line_pipeline.py` (routing, applicability and validation); `scripts/secondary/ru1_decide.py`; later `scripts/secondary/ru4e*.py`, `ru4ef3.py` and score/finalization helpers; `greekocr/labelfix/lqb.py`; registry `docs/records/labelfix/lqb/versions.json`. Release artifacts are `artifacts/ru1/{ru1_v3_edits.jsonl,ru1_v3_test_edits.jsonl}` with manifests/SHA receipts.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/harvest/line_pipeline/tool_versions.json`.
- `docs/records/labelfix/secondary/{PLAN.md,HANDOFF_20261018.md,RU1_LEAD_REVIEW.md,RU4E_REPORT.md,RU4E2_REPORT.md,RU4EF1_REPORT.md,RU4EF2_REPORT.md,RU4EF3_REPORT.md}` (relevant scope, evidence and validation sections).
- `docs/records/briefs/RU12_label_version.md`; `scripts/secondary/ru1_decide.py`; `greekocr/harvest/line_pipeline.py`.
- `docs/records/labelfix/lqb/versions.json`; `docs/records/labelfix/lqb/{score_ru1_v3_train.json,score_ru1_v3_test_edits.json}` (yer coverage/counts); `greekocr/labelfix/lqb.py`.
- `tests/test_ru1_decide.py`; `tests/test_ru12.py` (targeted test-source reads).
