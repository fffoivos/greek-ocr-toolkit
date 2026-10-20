# CQ4d: swap the 7 lead-rejected controls, then RUN the CQ4c reads end to end (gpt-6.1-sol, medium). Reader runs ARE authorised in this brief; no .git writes.

**The lead's control review** (`artifacts/cq4/control_review/lead_review.json`, status verified): 33 controls verified, 7 rejected
(`verified: false`, with `rejected_reason`). The rejected ones are ambiguous blob marks.
- RUN_ALL currently refuses because not all 40 are verified. The rule stays: only verified controls may be in a pack.
- In every context that contains a rejected control, replace it with a verified control not already in that context (deterministic,
  seed 20261017).
- Keep every bed item, the item order, and the prompt byte-identical. Rebuild only those contexts' item files and manifests, then run
  the closure scans and `validate_build.py`.
- Record the swaps in the receipt.
- Change the RUN_ALL check from "all 40 verified" to "every control placed in a pack is verified", with a test.

**Then execute** (the owner gave GO for R2a-2 inputs; the coordinator authorised the Sol reads):
1. `bash artifacts/cq4/RUN_ALL.sh` (initial contexts; the probe, ≥78% refusal, canonical v4.4 scan and controls gate apply as built);
2. `bash artifacts/cq4/BUILD_REREAD.sh`;
3. `bash artifacts/cq4/RUN_ALL.sh --phase reread`;
4. `bash artifacts/cq4/AGGREGATE.sh`.

A VOID context is recorded and never scored. Continue to the next one.

**Report** in `docs/records/labelfix/spellcheck/R2/CQ4_REPORT.md`:
- per set (W-CAP, top-up): slots read, resolved, quarantined to the lead queue;
- the class counts (marked/bare, compounds);
- the re-read agreement rate;
- VOID contexts with their causes;
- Codex weekly before and after.

The lead queue and contact sheet are at `artifacts/cq4/lead_queue.jsonl` and `.png`.

Last line: `CQ4d READY: swaps <n>; contexts run <n> (VOID <n>); W-CAP resolved <n>/300 (marked <n>, bare <n>); top-up resolved <n> (neg <n>/pos <n>); re-read agreement <pct>; lead queue <n>; Codex <a>%→<b>%`.
