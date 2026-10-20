# SEG-CP4b: fix round for SEG-CP4 (gpt-6.1-sol, medium, network OFF)

The SEG-CP4 review (`docs/records/reviews/SEG_CP4_review.md`) is a **FAIL**: 1 blocking, 3 high, acceptance 1/5 reproduced. Read it in full, plus `docs/records/briefs/SEG_CP4_build.md` (all its constraints and the owner standard still apply), ASTRA-SEG1 plan items 2–4, and the committed CP2/CP3 code.

**Fix every finding, using the existing toolkit tools only:**
- **B1:** `nlg--6146c0455e0103d2--s001-l0006` is unavailable (`invalid_source_frame_or_labels`, because the cached foreground and label planes disagree).
  - Diagnose it, and count such pages across the cache, read-only.
  - Resolve it with the plan's mechanism: the CP2 **fallback preparation**, at most once per source-bound page, explicitly counted, using the existing toolkit pipeline into a separate cache **outside the run root**, with full identity binding.
  - Never remove it from D. Never count unavailable as detected.
  - Required: D 9/9 and 0 unresolved required witnesses, or an honest statement of why not.
- **H1:** the union must not bypass partial-word rejection.
  - Reconcile CP3 supported-row inclusion with incomplete local groups: a neighbour row counts as an included complete row only if it is complete within the crop, per CP3's own row evidence.
  - Assert the **union** on all fragment controls, and report the standalone and union numbers separately.
  - Keep CP3's acceptance: rerun KEEP 22/22, C1 7/7, gallery 6/6, planted FP 0.
- **H2:** check letter completeness against the **full assigned native component ink and parent provenance**, not the `letter_boxes()` middle-region extent. Resolve shared-parent split letters explicitly. Add the reviewer's top-stroke control.
- **H3:** native short words (tokens 549/567 `Ο`, 652 `ο`).
  - Use the recorded word geometry and full native components (H2) so that complete visible short words resolve.
  - If a native case remains genuinely undecidable from the evidence, keep it unresolved and say so. Do not force it.

No CP5+ work. No publish actions.

Update `seg/CP4_RECEIPT.md` and `seg/CP4_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP4b: done | findings fixed: <list> | acceptance: <k>/5 met | KEEP FP <n>/22 | DROP <a>/9 (union) | fragment drops union <b>/<n> | short native <c>/3 | unresolved required <d> | CP3 rerun ok? | publish actions: 0 | tests: <n> passed`
