# N1-G: locked-eval gate for the frozen rule (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The 20 locked-eval readings (`n1e`, 10 contexts × r1/r2) are done. The rule is frozen (sha 90080b5a, N1R_REPORT.md).

**Phase 1, now.**
1. **Scans and gates.** Canonical v4.4 scans, control gates (>1 wrong → VOID; unsure dash cells accept any dash type), and the
   derived-view coverage rule. List VOID contexts.
2. **Truth candidates.** Two agreeing valid reads per slot. Disagreements and single reads → lead_review. The 36 unlocalized slots
   are listed and excluded from the gate.
3. **Lead sheets** in the scratchpad `n1_review/gate/`, ≤12 cells each, with raised and baseline references from the same document
   at the top of each sheet:
   - (a) every slot where the RULE says raised dot;
   - (b) every slot with a raised-dot truth candidate;
   - (c) every lead_review slot where Google wrote `-` or `.`.

   Write `gate_lead_template.jsonl`.
4. **Provisional gate** on the agreeing slots: raised-vs-hyphen precision, false edits on true ranges (hyphen/dash truth), recall
   and unsure rate. Mark it PROVISIONAL.

**Phase 2** (only after the lead fills the template and says go; implement and test it now):
- the final gate, with lead rulings applied;
- if it PASSES (precision ≥ 99%, 0 false edits on ranges), run `scripts/numerics/n1_apply_train.py` →
  `artifacts/n1/n1_v1_train.jsonl` + manifest + sha, register `n1_v1_train` in the LQB and re-score;
- if it FAILS, stop and report the failing slots.

Write the receipt `artifacts/n1/N1G_RECEIPT.json` and a section in `N1R_REPORT.md`.

**Last line:** `N1G PHASE1 READY: contexts VALID r1 <n>/10 r2 <n>/10; truth slots <n>, lead_review <n>; rule-raised <n>; provisional precision <x> (<k>/<n>), range false edits <n>; lead cells <n> on <n> sheets`
