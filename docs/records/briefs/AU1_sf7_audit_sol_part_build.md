# AU1: build the Sol part of the blind sf7-rc1 audit (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY; the lead runs the readers.

**Frame:** `artifacts/sf7_rc1/audit100_frame.jsonl` (100 corrected lines of release A, uniform, seed 20261017).
**Release:** `artifacts/sf7_rc1/release_edits_only_A.jsonl` (per-edit slot, kind and head).
**Preregistration:** `docs/records/labelfix/spellcheck/SF7_PREREGISTRATION.md` (the audit bar: line precision ≥ 83/100, the sf6 audit baseline).

**Reader routing (coordinator ruling):**
- **Sol now:**
  - (1) accent-type edits on lowercase letters (acute / grave / circumflex / none), using the HANDOVER grave word pass. Use the prompt
    `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/prompts/grave.md` VERBATIM; its question already asks for the
    printed accent type on one marked letter;
  - (2) edits on capitals (breathing and/or accent), using the CQ1 capitals prompt VERBATIM
    (`~/Projects/greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq1/` prompt file), with the compound re-read rule.
- **Opus after the Claude reset (NOT built now; list only):** lowercase breathing, subscript and dialytika edits, as two-reader four-head
  cards.

**Do:**
1. **Classify every edit** in the 100 frame lines into (1), (2) or Opus-later. An edit that changes both a lowercase breathing and an
   accent counts as Opus-later for the breathing part and Sol (1) for the accent part; score each head separately. Write
   `artifacts/sf7_rc1/audit/routing.json` with the per-head counts.
2. **Build packs.** Follow HANDOVER §4 exactly: opaque ids, content-hash PNGs, word zoom + line strip, no Google text and no release text
   shown, seeded order, ≤90 items + 10 controls per context, keys outside the packs.
   - Controls: for (2), reuse the lead-verified CQ4 pool (`~/Projects/greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq4/control_review/lead_review.json`,
     verified only). For (1), reuse the lead-verified grave-pass controls listed in HANDOVER §9 (`grave/keys/control_review/LEAD_REVIEW.md`).
   - Pack root: `…/scratchpad/sf7_audit/` (`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit`).
3. **Scripts:**
   - `artifacts/sf7_rc1/audit/RUN.sh`: the probe, the read, the canonical scanner BY HASH (use whatever sha is canonical when it runs:
     read it from HANDOVER.md, assert it, and record it), the controls gate, the probe; a VOID context is recorded;
   - `REREAD.sh` (the compound re-read rule for (2));
   - `SCORE.sh`: per head, is the released label right per the Sol reading; per line, correct only if every Sol-scored head on it is
     right, with Opus-later heads marked PENDING. A partial line precision is reported with the PENDING lines counted separately; it is
     never imputed.
4. **Report** `docs/records/labelfix/spellcheck/SF7_AUDIT_PARTIAL.md`, holding the plan and counts now and the results after the lead runs it.

Last line: `AU1 BUILD READY: frame lines 100; heads Sol-accent <n>, Sol-capital <n>, Opus-later <n>; contexts <n>; run cmd <path>`.
