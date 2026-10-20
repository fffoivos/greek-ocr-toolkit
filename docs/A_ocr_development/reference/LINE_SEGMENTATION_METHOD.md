# Line segmentation: charter and method

[Documentation index](../../shared/DOCUMENTATION_INDEX.md) · [Generations and code](LINE_SEGMENTATION.md) · [Tests and evidence](LINE_SEGMENTATION_TESTS.md)

This is the current reading guide, incorporating the owner's 12 October clarification. The [10 October charter](../../records/research/FAST_LINES_CHARTER_2026-10-10.md) is preserved as a dated source, including its historical status and timings. The [original font-line algorithm](PAGE_LINES_ALGORITHM.md) describes the earlier box-guided construction; the later pixel-only detector has its own input contract. Read the [generation record](../../records/research/round8/MODEL_GENERATIONS.md) before reusing either.

## Two objectives that must meet

The owner's architecture objective:

> basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes

The physical objective is to base the fast heuristics on features we understand and can draw on the page. Both objectives are required: a better picture without a runtime consumer is an experiment; a shared helper that preserves conflicting definitions is not physical consolidation.

## The physical construction

Paddle supplies initial localisations and text-likelihood maps. Its polygons are not character boxes, font guides or a complete row census. Native ink components supply character-like bodies and marks; their geometry is analysed without requiring character recognition. Components may be fragmented or joined, so a connected component is not automatically a complete character.

Existing tools establish candidate rows, associate components with them, distinguish body/ascender/descender/mark evidence, and fit the font guides. The principal guides are font top, meanline, baseline and font bottom, with accent guides where supported. Missing classes and borrowed measurements remain explicit. Four curves drawn around a box are not four measured font lines.

Shared page geometry explains skew and bend. Facing guides propose boundaries between neighbouring rows; complete native ink and finite layout boundaries verify the resulting crop. A whitespace separator can refine or check that boundary. It does not supply a missing font model or repair a wrong row identity by itself.

## Edge curvature: the concrete target

The owner describes modelling the blank paper and its geometry in space, so any lines drawn on it can be projected into the observed image. A text row located on that surface should inherit its bend. The subsequent practical clarification is:

> Right our idea is mostly to target the edge of the page, where actual curvature presents due to book structure, and have a heuristic that actually detects it, if any

The immediate target is a lightweight detection of edge curl, its onset and displacement, using reliable interior geometry and observations from neighbouring rows. Render a family of virtual parallel lines through the page, including between actual text rows: straight/skewed where supported and curved where the shared bend is evidenced. Then use that same geometry to continue rows and font guides beyond clipped boxes.

A full 3D reconstruction is not a prerequisite. A smooth displacement mesh is not, by itself, evidence that the paper bends. Straight and skewed pages are negative controls; unsupported observations remain unknown. Column boundaries limit text extent but do not automatically create independent paper surfaces. Separate leaves may require separate geometry. Perfect completion of every row is not a prerequisite to measuring the curl from reliable observations.

## Method for each change

1. Name the physical feature and the existing producer and consumer being changed.
2. Render it explicitly using the original detector or an existing feature tool, with compatible inputs. Inspect it on native pixels and record where the reference is wrong too.
3. Use that construction directly if cheap enough, or compare a faster heuristic against it. The comparison must test the claimed feature, not merely final polygon equality.
4. Connect the result to a real caller and remove the displaced decision in its verified scope. List callers migrated and old paths remaining.
5. Check changed crops, whole letters/marks, negative controls, generalization controls and actual cost. Preserve the original owner comments and their identities.

The [mechanism review](../../records/research/FAST_LINES_ROUND7_MECHANISM_REVIEW.md) asks what decisions exist and compete. The [methodology review](../../records/research/FAST_LINES_ROUND7_METHODOLOGY_REVIEW.md) asks what physical evidence justifies them. Neither review substitutes for the other.

## Input and speed boundaries

The original `pages.lines._discover` expects rough pixel regions supplied by its own preparation; tight Paddle polygons must not be placed into `PixelPage.boxes`. Reuse its useful calculations through their actual input contracts. Do not mistake the rejected Paddle-seeded adapter for the original detector.

Share observations only while image, region, scale, threshold and label provenance match. Row membership, font borrowing, source decisions and exclusion votes must be recomputed when their inputs change. Existing print-source uncertainty cannot be resolved by changing geometry labels.

The charter's target remains negligible correction overhead on clean pages and under one second of corrections per page. Byte equality is useful for exact refactors. A quality-preserving algorithm change may alter polygons and still improve the system; it needs native review. Rust speeds an implementation, not the validity of its geometry. Current task order and progress belong in the [handoff](../../records/research/round8/LOOP_HANDOFF.md), not in this durable method document.


## Conditional native extent after an accepted partition

R8-GEOM-03 i3 preserves the original scout/window/whole-word/valley admission. `confirmed_partition` passes its exact unchanged vector-piece body/word census to `whole_children` with the same full native strip/mask/CC8/transform context. Whole membership and final rint/inclusive raster are certified in both strip and original-page frames; changed source/forbidden/ownership decisions remain fresh. Unknown is the existing atomic vector split, not invented rows or a new mask/row model. The builder is a second consumer of the tight raster envelope and finite native refinement, with legacy native mark ties shared instead of copied.

13 October FONT-03 i1 correction: this certificate covers admitted membership, not all possible own-row marks outside the parent/attachment reach. The rejected 3229 upper B child omits its own κατ’ apostrophe; a strict physical expected failure pins that CURL prerequisite. Returned polygons are now independently rasterised on original pixels in the constructor and13-phase tests. Restoring the vector return fails14 physical assertions. A73d's mark-only refinement is experimental and withdrawn: a valid new seam alone cannot qualify final crop/mark ownership after reconciliation. The offline `round6_rows` pilot explicitly disables completion because it lacks runtime source refresh. See [FONT i1 report](../../records/research/round8/REPORT_R8-FONT-03-i1.md).

13 October FONT-03 i2 correction: a73d147 is D's grave (track3/body77), not C's own mark. The attempted guide/class input adapter proposes correct lower-row ownership on three witnesses, but original `font.evidence` also extracts letter apex/stem pixels as fused accent contacts. Three strict native-class xfails pin this first input failure. Separate original-page inner-seam and printed-rule duplicates, and the non-field straddling reconcile witness, remain unqualified. The adapter is offline evidence only; no live guide provider, membership change or ownership-priority repair is retained. See [FONT i2 report](../../records/research/round8/REPORT_R8-FONT-03-i2.md).

[Final report](../../records/research/round8/REPORT_R8-GEOM-03-i3.md): one lower final B row gains neighbour exclusion on3229p2; its upper field-owned row remains partial. Request R remains four retained rows with three left unknowns. CLOSED PARTIAL is administrative closure after3/3, not the full row/column gate or a font/curl/speed solution.
