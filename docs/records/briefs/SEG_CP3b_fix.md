# SEG-CP3b: fix round for SEG-CP3 (gpt-6.1-sol, medium, network OFF)

The SEG-CP3 review (`docs/records/reviews/SEG_CP3_review.md`) is a **FAIL**: 1 blocking, acceptance 2/4. Read it in full, plus `docs/records/briefs/SEG_CP3_build.md` (all its constraints still apply), ASTRA-SEG1 plan items 2–3, and the CP2 adapter.

## B1: the page gazette_modern--0020420cfe156a73--s000 cannot load
Saved `row-00077` has bottom − top = −8.887 px, so six merge witnesses are unresolved (l0039, l0138, l0141, l0146, l0162, l0228).

1. **Diagnose:** what row-00077 is (its curve, owned components, label/line, neighbours), why its bounds invert, and whether any other recorded W1/W2 page has inverted or degenerate rows (count them across the whole geometry cache, read-only).
2. **Resolve** with the plan's own mechanisms only. Pick the one the evidence supports, and justify it:
   - **(a) Row-level unavailability.** The invalid row is marked `invalid_geometry` explicitly, counted and reported; the page stays loadable for its valid rows. Any witness whose target or neighbour **is** that row (or whose crop it intersects) stays unresolved and is never counted as detected or KEEP.
   - **(b) The CP2 fallback.** "Fallback preparation … at most once per source-bound page and explicitly counted", using the existing toolkit pipeline into a separate cache **outside the run root**, with full identity binding. Use it only if it yields a valid row.

   Do not silently drop the row, exclude witnesses, or weaken validation for other rows/pages.
3. **Rerun** the original CP3 denominators: 22 KEEP, 7 C1, 6 gallery, planted controls.

## M1: the live-root no-write assurance
The `W2/crops` and `cache/g1b` directory mtime changes come from the **running collector `materialize --tranche W2`** (started 00:20, writes and discards crops and g1b caches). Show that with evidence: the process start time and command (`ps`), and those directories' changes over a window during which no SEG code runs. Narrow the receipt's assurance to what is measured: "no write by SEG code; live root changed by the collector materialize (pid …)".

Do no CP4+ work. Make no publish actions.

Update `seg/CP3_RECEIPT.md` and `seg/CP3_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP3b: done | B1: <a|b> (<short>) | inverted rows in cache: <n> | acceptance: <k>/4 met | KEEP 22/22? | C1 <x>/7 | gallery <y>/6 | planted FP <z> | publish actions: 0 | tests: <n> passed`
