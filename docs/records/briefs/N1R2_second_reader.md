# N1-R2: second reader packs, two-read combiner, raised-dot lead sheet (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as N1-S. Read `docs/records/labelfix/secondary/N1S_REPORT.md` first.

**State (lead, 17 Oct).**
- Calibration was 82/82, but in bed contexts the reader made 9 control errors in 7 contexts, and ctx04/05/07 are VOID.
- 3 errors were **baseline dot → raised dot** and 1 was **nothing → raised dot**: false raised dots, the N1 false-edit direction.
- **Ruling: a single read is not truth for N1.** Every slot needs two reads, and every raised-dot call gets the lead's pixel check.

**Do.**
1. **r2 packs** for all 7 contexts:
   - same items, exact reverse order, fresh opaque ids, fresh per-item option-letter permutations;
   - same controls;
   - `PACK_ROOT/ctxNN/r2/`, a `MANIFEST.r2.json` and keys `artifacts/n1/keys/ctxNN.r2.json`;
   - closure on all 14 reader folders.

   `run_n1.sh` takes `r2`, writing `ctxNN.r2.*`; run a dry-run check.
2. **Combiner** (`scripts/numerics/n1_decide.py`, with tests). Per bed slot, join r1 and r2.
   - Truth candidate = two agreeing reads from contexts that each pass the gate.
   - An r1 read from a VOID context counts only as a second vote, never as the first; the same goes for r2.
   - Disagreement, unreadable or other, or only one valid read → `lead_review`.
   - Then apply the N1 edit rule: Google `-` or `.` → `·` only when the truth candidate is a raised dot AND the grammar position is
     thousands. Otherwise there is no edit.
   - Output `artifacts/n1/decisions.jsonl` and a summary.
3. **Lead raised-dot sheet** (build it now from r1, and again after r2).
   - Every bed slot that ANY read called raised dot, plus all bed slots in the 'Hyphen printed as raised dot' sheet group, go on
     contact sheets in the scratchpad `n1_review/raised/`.
   - ≤12 cells each, showing the marked zoom large, the line small, a cell number, the Google glyph and all reads so far.
   - Also show 2 approved raised-dot controls and 2 baseline-dot controls from the same document at the top of each sheet, as
     references.
   - Write `sheets_index.json` and an empty `artifacts/n1/lead_raised_template.jsonl`.
4. **Receipt** `artifacts/n1/N1R2_RECEIPT.json` and a section "N1-R2" in `N1S_REPORT.md`.

**Last line:** `N1R2 READY: r2 packs 7 (closure <n>/14); combiner tests <n> passed; raised-dot lead cells <n> on <n> sheets`
