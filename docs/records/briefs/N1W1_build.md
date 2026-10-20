# N1-W1: two-read N1 on the admitted W1 ELSTAT numerics rows — packs, driver, finaliser (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The coordinator ruled that the raised-dot fault is ELSTAT-specific, so the correction targets the ELSTAT numerics_tables rows that
enter training. The rule is the same as N1-TR: Google `-`/`.` → U+00B7 only on two agreeing raised-dot reads AND the lead's pixel
check; never on ranges; every other outcome is a recorded hold.

**Do.**
1. **Find the admission file** `w1_originals_v3_admitted` (sol/collect-v3, `release_admissions/` or its documented path; read
   only). Select the ELSTAT numerics_tables rows, about 1,312 passing rows.
   - Candidates: every slot where Google wrote `-` or `.` inside a 4+-digit token.
   - Exclude lines in release_exclusions (`n1_locked_eval` included).
   - Localise each slot with the collector's exact symbol geometry (W1 responses, as in N1-C). Unlocalised slots are listed as holds.
2. **Packs** with sep2, r1/r2, ≤100 items per context, about 10% approved controls with ≥1 raised-dot control each.
   - Root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1w1/`.
   - Keys in `artifacts/n1/n1w1/`; closure on every pack.
   - Driver `scripts/secondary/reading/run_n1w1_all.sh`, like the N1-TR driver (probe before each context, stop at 70%, answers
     under `artifacts/n1/n1w1/answers/`).
   - Finaliser `n1w1_finalize.sh`, like the N1-TR one: a lead sheet of every agreed raised dot, with **same-document references
     from the approved controls where possible**, then `--apply-lead` → `artifacts/n1/n1_v1_w1.jsonl` + manifest + sha + LQB
     registration.

   Bind each pipeline's own copy of any shared helper (copy rather than share), so that another pipeline's edits never break it.
3. **Report** the candidate count, localised count, contexts and a Codex estimate in `docs/records/labelfix/secondary/N1W1_REPORT.md`, plus
   the receipt. Do NOT run readings.

**Last line:** `N1W1 READY: rows <n>; candidates <n>, localised <n>; contexts <n> ×2; est <pts> pts; closure <ok>; driver dry-run <ok>; tests <n> passed`
