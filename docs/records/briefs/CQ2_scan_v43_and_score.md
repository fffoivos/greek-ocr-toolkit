# CQ2: CQ1 leak-scan resolution (v4.3 wrapper) and scoring (gpt-6.1-sol, medium, network OFF; no .git writes; no new reading)

**The CQ1 read finished,** and `artifacts/cq1/RUN_CMD.sh` stopped with "CQ1 VOID: leak scan failed". Scan:
`artifacts/cq1/answers/r1.scan.json`. Rollout:
`~/.codex/sessions/2026/10/17/rollout-2026-10-17T18-40-41-01a14a85-bfd9-75e3-b20f-a79f924d6dbf.jsonl`.
- 17 violations, all `/zoom/batchN.png` or `/zoom/detail24.png`.
- The reader stored its own folder as `store("base","/private/tmp/…/scratchpad/solcap_qual/cap1/r1")` and viewed `load("base")+"/zoom/batchN.png"`.
- The scanner (v4.2) does not resolve a `load(name)` + string-literal concatenation, so it read the fragment as an absolute path.
- The images match the reader's own files 15/15.

**HANDOVER v4.1** already rules that "literal base/store/load bindings" are resolved, so this looks like a scanner gap, not a leak. But
a scanner change is the coordinator's ruling. Do the following, and mark the result PROVISIONAL until the lead reports the coordinator's
decision.

1. **A v4.3 wrapper** (a new file next to `artifacts/cq1/tools/`; do not edit v4.2): resolve `load(NAME) + "literal"` and
   `load(NAME)+'literal'` concatenations, using the reader's recorded `store(NAME, "literal")` bindings, before the absolute-path test.
   - Only literal store values count. Anything unresolvable is still a violation.
   - Every other rule is unchanged: image provenance, manifest, forbidden names, the font allowance.
2. **Tests:** this rollout passes, with 17 resolved and listed as `template_resolutions`. A synthetic `store("base","/Users/x")` +
   `load("base")+"/keys/k.json"` still fails. A load with no store fails.
3. **Re-scan the CQ1 rollout with v4.3.** Write `artifacts/cq1/answers/r1.scan_v43.json`, recording the replay of each resolution.
4. **If, and only if, v4.3 passes:** run the CQ1 scoring step from `RUN_CMD.sh` as written (controls gate first, then the bed against
   the T2 tuples).
   - Report exact-tuple agreement (bar ≥ 95%), invented breathings (bar 0), invented accents, missed marks, unreadables (routed to
     review, never auto-scored as right) and the control result.
   - Report per positives, negatives and compounds.
   - Write `artifacts/cq1/score.json` and `docs/records/labelfix/spellcheck/R2/CQ1_REPORT.md`, with every disagreement listed (item, T2 tuple,
     Sol tuple, line id via the keys), so the lead can pixel-check them.
   - Include the Codex weekly before/after: 41.0% after the read.

Last line: `CQ2 READY (PROVISIONAL, scanner v4.3 pending ruling): scan v4.3 <pass|fail>; controls <k>/6; exact tuple <n>/60 (<pct>); invented breathings <n>; invented accents <n>; unreadable <n>; verdict vs bar <QUALIFIED|NOT QUALIFIED>`.
