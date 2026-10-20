# KR1b: rebuild the kosmo2 c2 context for a re-run after a VOID scan (gpt-6.1-sol, medium, network OFF, mechanical)

The kosmo2 c2 reading was **VOID**: scanner v4 found 2 violations, "absolute path outside reader_dir" with path `/zoom/$`, at rollout records 22 and 44. The reader built image paths as a JS template string, `${pwd}/zoom/NN.png`, where pwd is its own folder. This is likely a false positive of the literal-string rule, but the rule voids the run regardless. c1 is clean and stands.

## Do
1. Build a **fresh** context `c2b` with the **same 55 items as c2** (50 bed cards + 5 controls) under PACK_ROOT `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c2b/`.
   - Use a new seeded order (`kr1b:kosmo:c2b`) and fresh opaque ids. Leave the c2 folder untouched, as evidence.
   - Keys go to `docs/records/harvest/recut_v1/w1_masked/kosmo2/keys/`. Write a manifest and run a closure scan.
2. Write the launch line for c2b with the same launchers. Record in the README that c2 is VOID (reason quoted) and that c2b replaces it.
3. Write `docs/records/harvest/recut_v1/w1_masked/kosmo2/SCANNER_NOTE.md` for the Sol-reading lead. It quotes the two records, explains why the path resolves inside the reader folder, and suggests the scanner resolve `${pwd}`-style template paths instead of flagging the literal `/zoom/$`. Do not change the scanner.

The last line must be exactly:
`KR1b: done | c2b: 55 items | closure: clean | launch line ready`
