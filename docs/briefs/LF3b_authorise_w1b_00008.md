# LF3b: add candidate_w1b_00008 to the authorised attempt-3 list (gpt-6.1-sol, medium; network OFF; no .git writes; no reading)

The coordinator's GO of 20 Oct ~06:27 ("then the VOID re-reads") authorises one extra fresh read for W1b contexts that VOID twice; the
only one is `candidate_w1b_00008` (attempts 1 and 2 VOID). `run.py` refuses it because `EXTRA_CONTEXTS` names only the two W2 contexts.

Change only: add `candidate_w1b_00008` to `EXTRA_CONTEXTS` in `artifacts/lf1/tools/run.py`, with its authorisation recorded per context
(W2 pair: "coordinator 20 Oct ~06:20 (VOID is a reader-process failure)"; w1b_00008: "coordinator 20 Oct ~06:27 GO (then the VOID
re-reads)"), so each attempt-3 receipt carries its own source. Update the tests that pin the set; all tests pass. No other change.

Final line: `LF3b READY: tests N passed; extra-attempt set 3` or `LF3b STOPPED: <reason>`.
