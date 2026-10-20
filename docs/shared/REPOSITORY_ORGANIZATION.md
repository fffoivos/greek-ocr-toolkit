# Repository organization

[Documentation index](DOCUMENTATION_INDEX.md)

The owner's priorities are the three generations, the tests, and the charter/methodology. The repository entry points follow those, with architecture and current state as two supporting sections.

| Section | Durable entry point | Content |
|---|---|---|
| Generations | [Implementations](../A_ocr_development/reference/LINE_SEGMENTATION.md), [dated lineage](../records/research/round8/MODEL_GENERATIONS.md) | Original pixel model, small-detector stack, current revision; input/output contracts and historical relocations. |
| Tests and evidence | [Test guide](../A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md) | Test types, cohorts, reference limits, reproduction and where evidence lives. |
| Charter and methodology | [Method](../A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md), [original charter](../records/research/FAST_LINES_CHARTER_2026-10-10.md) | Physical features, explicit rendering, fast approximation, simplification and speed objectives. |
| Architecture | [Responsibility map](../A_ocr_development/reference/LINE_SEGMENTATION.md#the-four-geometry-concerns) | Actual producers/callers for rows, columns, skew, curl, font and ownership; which decisions must be replaced. |
| Current state and decisions | [Handoff](../records/research/round8/LOOP_HANDOFF.md), [roster](../records/research/round8/ROSTER.json) | Best checked source, active task, caps, outstanding cases and next prompt. |

The [final checked-runtime audit](../records/research/round8/AUDIT.md) is the evidence snapshot for `046bd52`: retained output, architecture, physical method and speed are assessed separately. Its companion records extend the existing research record; they are not another allocation tracker. The audit is complete pending independent acceptance; geometry/CURL/INK/Rust remain closed partial, FONT stays parked, and both owner field questions remain unallocated. Planner alone updates PLAN/ROSTER after review.

## Applied now: navigation and provenance

The root README and documentation index expose all five sections. The original page API guides are labelled by generation. The historical charter is preserved in a tracked document, so its core content no longer depends on an ignored `.astra` file being available. The existing charter file is not moved or modified. Future changes to method go in the current method guide and dated plan amendments; the archived source remains historical.

Existing reports retain their dates and claims, including rejected assumptions. Source paths and runtime imports remain stable. This is a local documentation change prepared for Git integration; it does not mean GitHub has been updated or any private evidence published.

## Fold architecture cleanup into the feature tasks

Do not create `gen1/`, `gen2/` and `gen3/` copies of the implementation. Generations describe lineage, and generation 3 currently modifies the same stack as generation 2. Compatibility aliases in the old glyph/page modules are not three independent algorithms.

Each font, curl or integration task updates its producer/consumer map and records the replaced policy. Once callers migrate, delete the obsolete runtime branch and its duplicate preparations. Preserve a useful explicit renderer as an offline reference; label it as such. No independent repository-wide code-moving task should compete with those edits.

Later module moves are justified only after the responsibilities are settled. The owning worker must migrate imports, public compatibility paths, tests, CLI/reproduction commands and source references together, then verify from a clean checkout. Directory tidiness cannot count as removing a duplicate physical definition.

## Keep the record navigable

- The handoff and roster carry current status. A full plan is a dated decision history with the newest governing amendment first.
- Prompts are inputs; worker reports are claims; independent checks adjudicate them. Link all three rather than silently rewriting a report to agree with the latest outcome.
- Keep current best checked head separate from latest attempted head, and accepted runtime separate from offline experiments.
- Each task updates its existing report/handoff and the relevant durable map. Do not create a second parallel project tracker or require rewriting all historical reports.
- Use repository-relative links for durable GitHub navigation. Absolute paths in coordinator records are execution locations and must be labelled local. Raw images, chats and private held-out data are not part of this navigation reorganization.

Validation for this pass checks Markdown links/anchors, JSON dependencies/caps and whitespace. Runtime tests and OCR are not run for documentation-only changes. Publishing, changing repository visibility or deleting worktrees is outside this pass.
