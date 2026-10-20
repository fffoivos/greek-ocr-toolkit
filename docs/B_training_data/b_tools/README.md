# B.b — correcting and filtering tools built on the segmenter

## Purpose

Index the tools that turn sourced Google OCR labels and segmenter evidence into reviewable correction/filter decisions. This directory is **tool documentation**, maintained in `docs/B_training_data/b_tools/` under the taxonomy in `docs/cleanup_20261019/PLAN.md`. B.a supplies page OCR; B.c organizes the exact pipeline; B.d owns review artifacts and publication. Those interfaces do not make a proposed tool adopted or a single-stage KEEP training admission.

| Document | Current identity | Scope / release boundary |
| --- | --- | --- |
| [SEGMENTATION_FILTER.md](SEGMENTATION_FILTER.md) | 0.13 (label 0.9-s5) | Three-rule filter, clockwise turns, curved measurement and small all-component boxes; current inclusive band 0.30–2.00 for all rows. Coordinator adoption; segmentation remains frozen. |
| [CONTENT_GATE.md](CONTENT_GATE.md) | 0.3; final eligibility 0.3 | Mixed-word DROP, unexpected-script HOLD, raw short-line exclusion and aligned cell exemption. |
| [POLYTONIC_SF7.md](POLYTONIC_SF7.md) | 0.7 /SF7 A | Mark correction candidate_pre_audit; full audit unresolved, no binding. |
| [CYRILLIC_RU1.md](CYRILLIC_RU1.md) | 0.3 /ru1_v3_edits | Historical Russian final ь→ъ; sparse raw-parent train and test/dev versions. |
| [NUMERICS_N1.md](NUMERICS_N1.md) | 0.3 /n1_v1_w1 | Assisted `-`/`.`→`·`; rejected automatic ink rule stays disabled. |
| [DASHES.md](DASHES.md) | 0.1 | Literal dash tags, no general repair. |
| [LABEL_QUALITY_BENCHMARK.md](LABEL_QUALITY_BENCHMARK.md) | Frozen truth_v1_1; scorer schema v1.2 | Per-class label comparison, exposure guards and version registry; not another corrector. |

## Owner rules it implements, quoted

`docs/cleanup_20261019/OWNER_BRIEF.md` defines this slot:

> tools built on top of (A)'s segmenter and so on (the ones we are working on now) for correcting and filtering these

`AGENTS.md` states:

> The owner reviews tool outputs line by line on review sheets.

> An owner-accepted tool implements exactly the rules the owner stated; agents never add guards, tests or thresholds on their own.

Every tool is **versioned, replayed on the frozen review sets and shown to the owner on a sheet before adoption**. This is the B.b documentation requirement of the historical CLEAN5C brief, supported by the repo's owner-sheet process and historical replay records; it is not evidence that every current candidate has already completed adoption. The recorded segmentation freeze is respected; documenting limitations does not reopen it.

## Version history

| Identity source | Meaning |
| --- | --- |
| `docs/harvest/line_pipeline/tool_versions.json` | Authoritative named method generations, component bindings and digests. 0.n is not commit count or an accuracy claim; rejected generations stay in history. |
| `docs/records/labelfix/lqb/versions.json` | Label artifacts, path/SHA, parent/overlay/field/population semantics and status. This is separate from tool method versions. |
| Per-tool reports and receipts | Original review population, marks, run inputs, tests and limits; historical results remain tied to their original evidence. |
| CLEAN5C documentation | Documentation only; no tool generation, adoption, artifact publication or new qualification is created. |

## Inputs

Immutable raw Google parents; exact row/split/crop IDs and hashes; metadata declarations; saved segmenter/readers/geometry; frozen version manifests; review sets, owner-mark snapshots and label truth. Correction artifacts carry explicit provenance and sparse inheritance. Read code and manifests before relying on older prose. When they conflict, these documents identify the discrepancy instead of editing behavior to make prose true.

## Algorithm in prose

For a change to B.b, identify the owner's exact rule and the method/release version, then bind inputs and the frozen comparison. Replay saved/native evidence under the appropriate tool protocol; preserve the reference populations and exposure rules. Decision tools use the 150/888/250/417 review sets with explicit scoring denominators where available. Label tools use the frozen per-class LQB plus tool-specific blind audits and controls; zero relevant truth coverage is reported as not measured. New thresholds, fitting or extra vetoes require an owner rule rather than an agent's initiative.

Present the saved result through `greekocr.adjudicate.owner_sheet`: crop and Google text together, evidence overlays, exactly the last two tool versions, owner mark on the outer frame and latest tool decision inside. Correction sheets show before/after changes and editable Printed; their KEEP means accept the proposed correction, DROP reject it. Blind read/adjudication decks are a different artifact and expose neither released text nor verdicts. Prior owner-marked lines come last with their prior mark; do not ask for redundant judgments.

Use stable IDs and preserve notes. Dump the artifact's marks before republishing; never write to its database on page load. Publish/review belongs to B.d and the coordinator's protocol; this documentation run creates no sheets, messages, uploads or database writes. Adoption follows the tool's actual gates and owner decision; a candidate release, successful test or clean receipt alone is insufficient.

## Outputs and reason codes

Filters emit their own verdict and reason; label tools emit changed/no-change/hold evidence and exact edit spans; dashes emit tag_only. The integrated pipeline binds all producer results and retains required unresolved evidence as HOLD. It composes validated edits against the raw parent, then applies final eligibility. Do not rename tool KEEP to ADMIT or a tag to a repair. Per-tool documents enumerate the actual status/reason vocabulary and artifact paths.

## Evidence: review sets and owner marks

The segmentation replay totals **1,288 cohort records** (150+888+250), with calibration truth on **135/888** only, **235 distinct explicit historical marks**, and a separate **417-card typology /185 marked** panel. Historical saved S4 agreement is **109/135**, **189/235**, and **160/185** before gate exclusions. Gate re-report changes the comparison populations to **137/819/213/284** and marked denominators **91/191/176**; it does not rerun or improve the segmenter.

SF7's current audit is **70 correct /30 pending of100**, not a passed full audit. RU1's wave-1c effect is targeted (**1.68→1.25%** on 135 changed rows), with class-CER gate refuted. N1's **63 lead-confirmed edits** are assisted, while its automatic candidate failed **0/5**. LQB truth_v1_1 has **61,463 items**, but relevant release coverage/exposure still determines what can be measured. Details and exact limitations belong to the linked tool pages.

## Tests

These documents describe existing tests and original receipts; current CLEAN6 execution is recorded in `docs/cleanup_20261019/ASTRA_CYCLE1_FIXES.md`. **No pipeline, tests, readers, fitting, training or git writes were run for CLEAN5C.** Documentation verification consists of checking the eight files, common template, source paths, internal links, quoted rules and recorded numbers. Historical counts are labelled by run rather than presented as current all-green integration results.

## Known limitations

Historical S4 used 0.50–1.50. SEG10 adopted the current inclusive 0.30–2.00 band by coordinator decision; PIPE032 records numeric version 0.13 with label 0.9-s5. See the segmentation guide for the fitted-population limits and increased false negatives. The d94cff curved short-side failure remains documented and unfixed. SF7 remains candidate_pre_audit. RU4/N1 lack LQB truth coverage of their released edits; this is not a clean independent benchmark win. LQB still has external peer-worktree imports and registry paths. Historical receipts retain original paths/hashes; cleanup must preserve retrievability with custody receipts before any approved relocation. The original CLEAN5C documentation run did not edit those evidence files.

## Code paths

Filters/integration: `greekocr/harvest/{line_pipeline.py,line_pipeline_native.py,filtering_assets/}` and `scripts/harvest/filter_runtime/`. Label correction/scoring: `greekocr/{labelfix,numerics}/`, `scripts/{labelfix,secondary,numerics,lqb}/`. Review: `greekocr/adjudicate/owner_sheet.py`; contract `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`. Code paths remain unchanged by this documentation work.

## Sources read

- `AGENTS.md`; `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`.
- `docs/harvest/line_pipeline/tool_versions.json`; `greekocr/harvest/line_pipeline.py`; `greekocr/harvest/filtering_assets/{segmentation-policy.js,service.mjs}`.
- `docs/records/harvest/seg_steps/{s4/REPORT.md,s5/BAND_PROPOSAL.md,NOTES_FOR_LATER_STEPS.md,gate_rereport/REPORT.md}`.
- `docs/records/labelfix/spellcheck/{SF7_RC1_LQB.md,SF7_AUDIT_OPUS_PREP.md}`; `artifacts/sf7_rc1/audit/final_score/final_score.json` (summary).
- `docs/records/labelfix/secondary/{PLAN.md,HANDOFF_20261018.md,N1G_GATE_FAIL.md,N1W1_REPORT.md,RU4EF3_REPORT.md}`.
- `docs/records/labelfix/lqb/{LQB_PLAN.md,LQB5_RECEIPT.json,versions.json}`; `greekocr/labelfix/lqb.py`.
