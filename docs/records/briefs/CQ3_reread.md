# CQ3: CQ1 re-read in a fresh context (gpt-6.1-sol, medium; no .git writes). Prompt VERBATIM; scanner v4.3 as accepted.

**Why the first read is void.** CQ1's first read is VOID under the accepted scanner v4.3 (coordinator, 17 Oct): one unresolved path
remains, record 24, `cwd + "/zoom/batch1.png"` with `cwd` unbound. That call errored with ReferenceError and returned nothing. The rule
stands: unresolved means a violation, means void.
- Keep the void run's folder, answers and scans untouched as evidence.
- Do NOT score it.

**Do:**
1. **A fresh reader folder** `…/scratchpad/solcap_qual/cap1/r1b/`, byte-identical to the ORIGINAL pack.
   - Copy it from the build: the frozen `MANIFEST.r1.json` file list and hashes. Rebuild from the builder outputs if needed; never
     copy from the used r1 folder, which has zoom/ and answers.
   - Same items, same order, same prompt file, no edits.
   - Write `MANIFEST.r1b.json` and run the closure scan.
2. **The run script** `artifacts/cq1/RUN_CMD_r1b.sh`: the same as `RUN_CMD.sh`, but with `RD=…/r1b`, scanner v4.3 (the wrapper from
   CQ2), and answers going to `artifacts/cq1/answers/r1b.*`.
   - The control gate needs `lead_review.json` status verified, which it already is; same sheet sha.
3. **STOP after writing it.** The lead runs it. Sol cannot launch a nested reader from inside this sandbox reliably; if it can, still
   don't.

Last line: `CQ3 READY: r1b pack identical to frozen manifest <yes>; closure pass; run cmd artifacts/cq1/RUN_CMD_r1b.sh`.
