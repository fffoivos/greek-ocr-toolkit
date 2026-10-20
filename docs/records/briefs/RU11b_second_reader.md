# RU1-1b: second-reader packs, decision combiner, review sheets (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints, interpreters and allowed writes as RU1-0/RU1-0b. Read `docs/records/labelfix/secondary/RU10_REPORT.md` and the r1
outputs in `artifacts/ru1/answers/` (`ctxNN.jsonl`, `.mapped.jsonl`, `.controls.json`, `.scan.json`).

**State after r1 (lead, 17 Oct).**
- Leak scans are clean in all 4 contexts.
- The control gate VOIDED ctx01 and ctx02 (2 errors each); ctx03 and ctx04 are VALID.
- Controls overall: 70/75. Errors: true ъ → ь ×2, true ь → ъ ×2, true ъ → u ×1.
- Bed: Google ъ → ъ 458/458. Google final ь → ъ 162, ь 241, other 2.
- A 2/13 false-ъ rate on true-ь controls is too high for a one-reader edit.

**Lead ruling, the edit rule for ь → ъ.**
- An edit needs **two ъ reads from two independent contexts, at least one of which passed its control gate, and no ь read.**
- A read from a VOID context counts only as a corroborating vote.
- Any r1/r2 disagreement, any `u`/`other`, and any position with only void-context ъ reads goes to `lead_review`.
- Google ъ and pre_hyphen slots are never edited.

**Do.**
1. **r2 packs.**
   - For each `ctxNN`, build `PACK_ROOT/ctxNN/r2/` with the same items in the exact reverse order. Use fresh opaque item ids, and new
     content-hash copies of the same bytes are fine.
   - Same controls. A `MANIFEST.r2.json` per context. Keys go to `artifacts/ru1/keys/ctxNN.r2.json`.
   - Run closure on all 8 reader folders.
2. **Launcher.**
   - `scripts/secondary/reading/run_bed.sh` takes an optional reader argument (`r1` default, `r2`), with per-reader answer, scan,
     mapped and controls file names (`ctxNN.r2.*`).
   - Keep the probe, the 78% refusal and the ledger.
   - Add a test or dry-run check that `r1` paths are unchanged.
3. **Combiner** (`scripts/secondary/ru1_decide.py`, with tests).
   - Joins r1 and r2 per (row id, offset) and applies the edit rule above.
   - Outputs `artifacts/ru1/decisions.jsonl`, one row per Google-final-ь position, with:
     - `decision` ∈ {edit_hard, keep_soft, lead_review};
     - both reads, their contexts and gate status, and the prior;
     - `prior_disagreement` (an edit_hard where the prior is ь_only, or a keep_soft where the prior is ъ_only), counted and listed;
       these also go to lead_review.
   - Test on fixtures covering: agree-ъ in valid contexts, agree-ъ with one void, both void, disagreement, `u`, `other`, a Google ъ
     slot, and pre_hyphen.
4. **Failed-control sheet, now.**
   - For the 5 failed control slots, render a contact sheet `ru1_failed_controls.png` in the scratchpad `ru1_review/`.
   - Each cell has: the line crop; a word crop at 4× and a final-letter crop at 8× (from Google symbol boxes, or for v2 lines from the
     masked offset on the saved crop); the control truth; the r1 call; and the source id.
   - Also include 3 correctly read ъ controls and 3 correctly read ь controls from the same books, as visual anchors, marked as such.
   - The lead uses it to check the control truth itself.
5. **Review-sheet builder.** It is used after r2 for lead_review positions:
   - same cell layout, with the r1/r2 calls and the prior;
   - ≤12 cells per sheet;
   - `sheets_index.json`.

   Test it on fixtures only now.
6. Write the receipt `artifacts/ru1/RU11b_RECEIPT.json` and a section "RU1-1b" in `RU10_REPORT.md`. Run the tests.

**Last line:** `RU11b READY: r2 packs 4 (closure ok <n>/8); launcher reader arg <ok>; combiner tests <n> passed; failed-control sheet <path>; review builder <ok>`
