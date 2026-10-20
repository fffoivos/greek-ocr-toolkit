# RU1-S: rescore controls, final decisions, owner sheet HTML (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints, interpreters and allowed writes as the RU1 briefs. Inputs:
- r1 and r2 answers under `artifacts/ru1/answers/` (`ctxNN.*` and `ctxNN.r2.*`);
- `scripts/secondary/ru1_decide.py`;
- the lead's control review `docs/records/labelfix/secondary/RU1_CONTROL_REVIEW.md` (read it first);
- the plan `docs/records/labelfix/secondary/PLAN.md` §8, which gives the owner-sheet parameters.

**Do.**
1. **Rescoring in the mapper and combiner**, with tests.
   - The disputed control slot `ia_russian--d558bd3e803e7865--s003-l0032` slot 2 is excluded from control scoring.
   - A `u` on a control is an abstention: counted separately, not as a wrong sign.
   - Gate: more than 1 WRONG SIGN per reader-context → VOID.
   - Re-map r1 and r2, then re-run `ru1_decide.py`.
   - Report per reader-context: wrong signs, abstentions, VALID/VOID.
   - Report decision counts: edit_hard, keep_soft, lead_review (split by reason), and prior disagreements.
2. **Owner sheet** `artifacts/ru1/owner_sheet/ru1_sheet.html`.
   - Build it with `greekocr.adjudicate.owner_sheet.render(lines, spec)` from the cleanup worktree
     `~/Projects/greek-ocr-toolkit-cleanup` (opus/cleanup-1 ≥ 994456de0; read `owner_sheet.py` lines 78–160 and
     `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md`).
   - Run it under `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` with `PYTHONPATH=~/Projects/greek-ocr-toolkit-cleanup`.
     Do not modify the cleanup worktree.
   - **One card per LINE** that has ≥1 Google-final-ь position, doc id = W1 line id. Contents:
     - `image`: the line crop;
     - `zooms`: for each Google-final-ь position, a 4× word zoom and an 8× final-letter zoom, alt "word N" / "final N";
     - `rows`: `Google` (the W1 features `text`, never empty); `Proposed` (the label with ь → ъ applied ONLY at edit_hard
       positions); `Reads` (per position: word, r1 call, r2 call, decision, prior);
     - `tags`: the decision classes present (edit_hard / keep_soft / lead_review:<reason>), and the book;
     - `printed`: NOT prefilled. These are reader decisions, not adjudicated truth;
     - `group`: by the line's most severe decision (lead_review > edit_hard > keep_soft).
   - **spec:**
     - title "RU1 Hard Sign Decisions";
     - intro of at most 4 sentences: Google writes printed word-final ъ as ь in pre-1918 Russian; two blind Sol reads per position;
       an edit only on two ъ reads with no ь; Google's own ъ is never changed; please mark any wrong Proposed in the note or the
       Printed field;
     - groups in this order: "Needs a look" (lead_review), "Proposed ъ" (edit_hard), "Kept ь" (keep_soft, at most 40 lines, seeded
       sample `20261017:RU1S`; the full counts go in the group heading).
   - Write a summary `artifacts/ru1/owner_sheet/summary.json` (counts per group, sha256 of the HTML and of every input).
   - **Size:** the HTML must stay under 15 MB. Downscale zoom PNGs if needed, never below the native crop resolution, and report the
     size.
3. **Receipt and report.** Write `artifacts/ru1/RU1S_RECEIPT.json`, add a section "RU1-S" to `RU10_REPORT.md`, and run the tests.

**Last line:** `RU1S READY: r1 VALID <n>/4, r2 VALID <n>/4; edit_hard <n>, keep_soft <n>, lead_review <n> (<reasons>); prior disagreements <n>; sheet <path> <MB> MB, cards <n>; tests <n> passed`
