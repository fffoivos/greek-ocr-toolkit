# Documentation index

## Owner's taxonomy

| Home | Scope |
|---|---|
| [A — OCR development](../A_ocr_development/README.md) | Recogniser/training and the slow pixel, R8 next-generation and R7 small-detector segmenters. |
| [B — training-data creation](../B_training_data/README.md) | Google page reads, correction/filter tools, the organising pipeline and review/publication. |
| [Shared](README.md) | Deploy, ops, verification, types, CLI, vendor custody and Clariden scripts. |
| [Records](../records/INDEX.md) | Dated reports, briefs, handoffs and evidence by track. |

## Line segmentation

The five entry points are:

| Section | Start here |
|---|---|
| **Three generations** | [Implementations and lineage](../A_ocr_development/reference/LINE_SEGMENTATION.md#the-three-generations) |
| **Tests and evidence** | [What we test, what it proves, and how to reproduce it](../A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md) |
| **Charter and methodology** | [Current method](../A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md) and [original charter](../records/research/FAST_LINES_CHARTER_2026-10-10.md) |
| **Architecture and responsibilities** | [Existing feature producers and consumers](../A_ocr_development/reference/LINE_SEGMENTATION.md#the-four-geometry-concerns) |
| **Current state and decisions** | [Checked state and next work](../records/research/round8/LOOP_HANDOFF.md) |

The [repository organization guide](REPOSITORY_ORGANIZATION.md) explains how code, reports and evidence fit these sections. Source paths stay stable during active work.

| Need | Read |
|---|---|
| Current checked work and next task | [Coordinator handoff](../records/research/round8/LOOP_HANDOFF.md) |
| Final checked-runtime accounting | [Audit](../records/research/round8/AUDIT.md), [full report](../records/research/round8/REPORT_R8-AUDIT-02-i1.md), [cost](../records/research/round8/AUDIT_COST.md) — retained gains and open goals assessed separately; independent acceptance pending |
| Compact context for a new Sol implementation worker | [Worker handoff](../records/research/round8/SOL_WORKER_HANDOFF.md), [coordinator transfer](../records/research/round8/SOL_TRANSFER.md) |
| Worker, branch, worktree and iteration allowance | [Roster](../records/research/round8/ROSTER.json) |
| Full plan and its dated amendments | [Round-8 plan](../records/research/round8/PLAN.md) |
| Font guides, edge curvature and deletion milestones | [Geometry completion plan](../records/research/round8/GEOMETRY_COMPLETION_PLAN.md) |
| Original page detector API | [Page guide](../A_ocr_development/reference/PAGES_GUIDE.md), [pipeline](../A_ocr_development/reference/PAGES_PIPELINE.md), [output records](../A_ocr_development/reference/PAGES_OUTPUT_FORMAT.md) |
| Original font/curve construction and lineage | [Owner algorithm](../A_ocr_development/reference/PAGE_LINES_ALGORITHM.md), [generation identification](../records/research/round8/MODEL_GENERATIONS.md) |
| Fast stack entry point and reproduction instructions | [Stack README](../../prototypes/fast_lines/stack/README.md) — its recorded metrics are historical; follow the handoff for current qualification |
| Architectural and physical-method reviews | [Mechanism review](../records/research/FAST_LINES_ROUND7_MECHANISM_REVIEW.md), [methodology review](../records/research/FAST_LINES_ROUND7_METHODOLOGY_REVIEW.md) |
| Rust ordering and measured pilot limits | [Completion plan](../records/research/round8/RUST_COMPLETION_PLAN.md), [measurement record](../records/research/round8/RUST_SPEED_ESTIMATE.json) |
| Earlier experimental ideas and results | [Research](../records/research/FAST_LINES_RESEARCH.md), [stack history](../records/research/FAST_LINES_STACK.md), [original Q7/Q8 experiments](../../prototypes/fast_lines/README.md) |

The handoff names the latest checked state; reports remain dated evidence. A task marked partial is not complete because a later report or port exists. Saved image/JSON evidence usually lives in the relevant worker's ignored `.astra/fast_lines/out/` directory; the report or roster identifies that worktree.

## Other toolkit work

| Area | Read |
|---|---|
| Package APIs and CLI | [API](../API.md), [repository README](../../README.md) |
| Coding/data contracts and validation | [Standard](../STANDARD.md), [validation](../records/verify_20261008/VALIDATION.md) |
| Vendored origins and module relocation history | [Inventory](../INVENTORY.md) |
| Earlier crop-level glyph/geometry work | [Glyph plan](../records/glyphs/GLYPHS_PLAN.md), [calibration](../records/glyphs/GLYPHS_CALIBRATION.md), [geometry](../A_ocr_development/reference/O4D_GEOMETRY.md) |
| Verification and metadata | [Verification](../VERIFY.md), [line metadata](../A_ocr_development/reference/LINE_METADATA.md) |
| Document AI reader | [Reader guide](../B_training_data/a_google_ocr/readers/READERS_DOCAI.md) |
| Rendering web evidence | [Web rendering](WEB_RENDER.md) |
| Page and crop research scripts | [Page scripts](../../scripts/pages/README.md), [glyph scripts](../../scripts/glyphs/README.md), [archived scripts](../../scripts/glyphs/archive/README.md) |

## Where things belong

| Location | Role |
|---|---|
| `greekocr/` | Installed package implementations and compatibility APIs. Presence here is not a claim that every detector case passes. |
| `prototypes/fast_lines/stack/` and its imported providers | Executable fast-lines research route. |
| Other `prototypes/fast_lines/` modules | Feature tools and experiments; some supply live callers. Check imports before treating a directory as obsolete. |
| `tests/` and prototype-local tests | Package contracts, fixtures and research regressions respectively. |
| `docs/` | Reusable API and navigation documentation. |
| `docs/records/research/` and `docs/records/reviews/` | Dated investigation, plans, reports and review evidence. Preserve provenance when superseding a conclusion. |
| `scripts/` | Existing reproduction, rendering and coordination tools; see their own inventories. |
| `.astra/` | Local coordination and generated evidence, often ignored and worktree-specific. Not a public data directory or another detector implementation. |

Keep durable entry points here and task progress in the handoff/roster. Record source/head and inputs with experimental results. Code-path moves must update actual callers and reproduction paths together; a directory rename alone does not consolidate an algorithm.
