# OC1 + OC2: Opus card package for the 30 pending sf7 audit lines, plus the final audit scoring merge (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY; no reads.

**Context:** `docs/records/contexts/CONTEXT_20261019_spellcheck.md`; the audit state is in `artifacts/sf7_rc1/audit/` (OPUS_PENDING.md, AU1B/AU1C/AU1D
hand-offs, routing.json, lead_queue.jsonl, the SCORE scripts).
**Bar:** ≥ 83/100 line precision (SF7_PREREGISTRATION.md). Opus reads wait on the owner's go.

## OC1: the cards

**Targets:**
- (a) the 23 lines / 25 heads in OPUS_PENDING.md;
- (b) the capital heads of the 7 lines left unresolved because the capital context was VOID three times. Take them from the routing,
  the capital keys and the AU1D hand-off, and list them.

Total: 30 lines. Each head is one card, with every head of that slot asked (four heads), as in the R2 protocol.

**Protocol:** `docs/records/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md` and the greekocr.adjudicate deck/protocol on opus/cleanup-1
(`~/Projects/greek-ocr-toolkit-cleanup/greekocr/adjudicate/`; import it read-only, or vendor it with its sha).
- Two blind readers: reader 1 in a seeded order, reader 2 in the exact reverse.
- A tiebreak deck generated for disagreements and invalid votes only, with fresh option order.
- Ownership is null on an unmarked anchor; an invalid vote counts per card only.

**Each card shows:**
- the native full line crop with the target letter outlined;
- a 3× word zoom;
- the word's BASE letters with every mark removed, plus the anchor index;
- the four head questions (breathing, accent, dialytika, subscript, with unknown allowed), readability, ownership, confidence and a note.

**Never shown:** Google text, released text, source ids or the sampling stratum.

**Controls:** about 10% per reader folder (at least 4), drawn from lead-pixel-verified controls in
`~/Projects/greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks/{T2,T4}/` (lead_verified true; never T2 #61).
They must be disjoint from the audit lines' documents. Shuffle them into position.

**Folders:** `…/scratchpad/sf7_audit_opus/{r1,r2}/` with cards.jsonl, img/, README.md, answer_schema.json and an empty answers.jsonl.
- Keys go to `artifacts/sf7_rc1/audit/opus_keys/`, outside the folders.
- Run a leak scan over the folder contents and write a receipt with hashes.
- The receipt also states that Opus readers are Claude subagents, so isolation is by folder plus a file-allowlist instruction (as in
  T2/T4), and the Codex rollout scanner does not apply.
- `READER_PROMPT.md`: the exact instruction text the lead gives each Opus subagent (folder only, allowlisted files, transcribe the ink,
  write answers.jsonl, and the count check).

## OC2: the scoring merge (`artifacts/sf7_rc1/audit/FINAL_SCORE.sh` + test)

1. Resolve the Opus answers with `scripts/labelfix/r2_cards_resolve.py`: controls gate first, 2-of-2 else 2-of-3, UNKNOWN preserved.
2. Merge with the Sol part: accent context VALID, 70/70 lines correct as recorded; capital context VOID, so its heads come from Opus
   here.
3. **Per head:** is the released label right per the resolved print truth?
4. **Per line:** correct only if every scored head on the line is right. A still-unresolved head keeps its line PENDING, reported
   separately and never imputed.
5. **Final:** line precision against the bar, with a cluster-bootstrap interval and per-head and per-kind counts.
6. **Test** on synthetic answers: all agree, one disagreement → tiebreak, a control failure means the gate fails, unresolved stays
   PENDING.

Write `docs/records/labelfix/spellcheck/SF7_AUDIT_OPUS_PREP.md`.

Last line: `OC READY: cards <n> (lines 30, heads <n>), controls/folder <n>, folders r1/r2 leak-scan pass, reader prompt <path>, FINAL_SCORE tests <n> passed`.
