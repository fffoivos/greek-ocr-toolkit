# Adjudication-efficiency experiment: cached for later review (17 Oct 2026, ~12:15)

**The owner stopped the experiment to save Claude usage** (no refresh for about 40 h). The conclusion is kept and the rest is cached. Scoring by Sol (Codex usage, not Claude) can be done later from the files below.

## Conclusion
- **E1 (all cards of a bed in one reader context) cuts tokens per card by about 40% with no visible quality loss:**
  - BSB: about 2,400 tokens per card at 50 per context, against about 1,330 at 100 per context. E1 reads letters 96, crop_ok 94, marks 90, against the C1 reference 96 / 95 / 92.
  - yer: about 3,500 tokens per item at about 30 per context, against about 2,200 at 59 per context.
  - **Adopted for future card checks: 100 cards per reader context**, reader count per item unchanged.
  - Formal scoring (agreement with truth within the E0a–E0b variance) is still to run.
- **E2 (word and letter crops only, no full line): rejected.**
  - It costs about the same per card.
  - It loses the crop judgement: one BSB reader passed every crop.
  - It has a build defect: the letter close-up targets the token's last glyph in hyphenated words (yer a025, a020).
  - Zero-slot yer items get no image at all.
- **E3 (compact prompt) and E4 (E1 + E3): not completed.** Images dominate the tokens, so the expected gain over E1 is small (<5%). These partial runs stopped early, and part of their token use is the pause-and-resume exchange.
- **owner39 bed: not completed.** Only partial E0 runs exist (5, 13, 8 and 7 of 39 cards). Measuring our readers' error against the owner's sheet remains open.

## Files
- Packs: `packs/` (PNGs local and manifest-bound). Keys and truth: `keys/`. Scorer: `score.py`.
- Reader outputs (scratchpad, uncommitted): `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/eff/out/` for the bsb and yer beds; owner39 answers are in `packs/owner39/<arm>/<reader>/answers.jsonl`.
- Usage: `scratchpad/eff/usage_log.tsv`, measured from agent results; there is no cached/uncached split. Total: 2,371,792 tokens over 29 reader runs (19 complete, 10 partial).
- Complete runs:
  - bsb: E0a ×2, E0b ×2, E1, E2 ×2
  - yer: E0a ×2, E0b ×2, E1, E2 ×2
- Pending truth fix before scoring: owner39 card `384c3f89-p000059-l0013:s33` is printed ἦγε, tuple [1,3,0,0] (overlay v1.1, opus/r2-prep 17f913a0f).
- The paused readers can be resumed (agent ids in `scratchpad/eff/agents.tsv`), but that resume is not planned.
