# SEG-CP2b: fix round for SEG-CP2 (gpt-6.1-sol, medium, network OFF)

The SEG-CP2 review (`docs/records/reviews/SEG_CP2_review.md`) is a **FAIL**: 0 blocking, 1 high, acceptance 4/5 reproduced. Read it in full, plus the CP2 brief `docs/records/briefs/SEG_CP2_build.md` (whose constraints all still apply) and ASTRA-SEG1 plan item 2.

**Fix every blocking/high finding, and every medium finding that touches CP2 acceptance.** Above all, H1: the admission boundary must require a **positive qualification state and a valid source/code/geometry binding**. Unavailable, stale, unbound, unresolved or legacy measurements must never yield `passed=True` or a verified keep. They give an explicit unavailable/unresolved status, counted, and never activate the old F2 heuristic. Add the review's reproduced inputs as regression tests.

Do no CP3+ work. Make no publish actions, and do not touch admission files, the crops manifest or PNGs. The live run root is read only.

Update `seg/CP2_RECEIPT.md` and `seg/CP2_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP2b: done | findings fixed: <list> | acceptance: <k>/5 met | publish actions: 0 | tests: <n> passed`
