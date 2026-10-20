# CQ1: build the Sol capitals-qualification pack (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY; no reading run.

**Purpose (coordinator-approved, 17 Oct):** test whether a one-reader Sol pass can label capital breathings and accents (including
compounds) well enough to top up the R2a capitals slice. The bar is **≥ 95% exact-tuple agreement with the two-reader truth and 0
invented breathings**. This decides option (a) vs (b) in `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/R2A_NEXT.md`.
It does not decide whether R2a-2 runs; that is the owner's call.

**Protocol:** follow the Sol-reading HANDOVER exactly:
`~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md` (§2 settings, §3 prompts, §4 pack layout and blinding,
§5 leak scan v4.2, §7 Codex budget rule). Copy its launchers and tools. Do not edit them in place. Set `S`/`W` for this track.

## Bed: 60 capital slots from T2 resolved truth

Source: `artifacts/r2_resolve/T2/final/resolved.jsonl` (two-reader / 2-of-3 truth; this worktree, commit 45c8c63ce).

Select, deterministically with seed 20261017, anchors whose printed base is an UPPERCASE Greek vowel or Ρ, with all of breathing and
accent decided:
- **30 positives:** a breathing and/or accent printed. Mix psili/dasia × none/acute/grave/circumflex, at least 8 compounds
  (breathing+accent).
- **30 negatives:** a bare capital, including capitals in ALL-CAPS words and numeral-adjacent capitals if available.
- **Diversity:** at most 3 per document.

**Excluded:**
- any slot in the R2a v2 manifest that will be TOP-UP-eligible later (taken from v2 only to qualify; it is fine to reuse T2 truth,
  but list the overlap);
- T4 documents entirely.

## Controls: 6, pixel-verified by the lead before any reader starts

Use LOWERCASE vowels from T2 resolved, with unmistakable marks, so they are not from the stratum under test. Make them look identical
to bed items: the same rendering and the same question form, about "the marked letter".

Write a control contact sheet (word zoom + letter zoom + the expected tuple) to `artifacts/cq1/control_review/controls.png` with an
index file, OUTSIDE the pack.

## Question (new prompt file; the grave-pass wrapper per GUIDE_NOTES, with a new body)

"Look at the letter marked in the image. Which breathing is printed on or before it (none / smooth ᾿ / rough ῾ / unreadable), and which
accent (none / acute / grave / circumflex / unreadable)? A spacing compound before a capital (e.g. ῎Α) counts as printed on that
capital. Do not infer from spelling or grammar; report only ink."

- The answer schema is a fixed JSON per item.
- Option order is permuted per item.
- NO Google text, no word transcription, no source ids.

**Rendering:** the word zoom (3×) with the target capital boxed, plus the full native line strip, as in the R2 cards.

## Pack

- `PACK_ROOT=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/solcap_qual`, one context: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/solcap_qual/cap1/r1/` with 66 items (60 bed + 6 controls) in seeded random order.
- **Keys** go OUTSIDE the pack: `artifacts/cq1/keys/` in this worktree.
- **Closure scan** with `tools/scan_packs.py`.
- Write the run command (the copied launcher's `run_bed`-style script, with the limit probe before and after, the reading run, leak
  scan v4.2 and scoring) to `artifacts/cq1/RUN_CMD.sh`. The lead runs it after the control review.
- The scoring script compares against the T2 tuples, reporting exact-tuple agreement, invented breathings, invented accents,
  unreadables, and the control result. It writes `artifacts/cq1/score.json`, and a 1-page `docs/records/labelfix/spellcheck/R2/CQ1_REPORT.md`
  is filled in after the run.

Last line: `CQ1 BUILD READY: bed 60 (pos 30/neg 30, compounds <n>), controls 6 (sheet <path>), pack closure pass, run cmd <path>`.
