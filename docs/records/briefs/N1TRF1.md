# N1-TR-F1: finalise phase 1 (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

All 12 N1-TR reader contexts are DONE (`artifacts/n1/n1tr/answers/*.attempt.json`). Run `scripts/numerics/n1tr_finalize.sh` (first
invocation, without `--apply-lead`):
- v4.4 scans, gates and the derived-view coverage rule;
- the two-read combine;
- the lead sheet of every agreed raised-dot slot, with same-document references, in the scratchpad `n1_review/n1tr/`, plus a
  template.

If a context fails its scan or gate, list it, and do not widen anything. Report the counts: agreed raised, agreed hyphen/dash,
agreed baseline dot, disagreements, holds.

**Last line:** `N1TRF1 READY: contexts valid <n>/12; agreed raised <n>, hyphen/dash <n>, baseline <n>, other <n>; holds <n>; lead cells <n> on <n> sheets`
