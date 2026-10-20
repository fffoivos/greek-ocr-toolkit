# B6c + R2M: resolve the third-reader tiebreaks, then build the R2a supervision manifest from T2 (gpt-6.1-sol, medium, network OFF; no .git writes)

Workspace: THIS worktree (`opus/r2-cards`). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.

## Part 1. B6c: final resolution

**Inputs:**
- reader-3 answers: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/r2read_{T2,T4}_r3/b00,b01/answers.jsonl`, all complete (T2 47+51, T4 60+62 = 220 cards);
- the v2 deal: `artifacts/r2_resolve/{T2,T4}/tiebreak_v2/` with its private map and `r3_deal_receipt_v2.json`.

**Do:**
1. Verify the folders against the v2 receipt: hashes, card membership, line counts, valid JSON.
2. Per-folder controls gate (10 each, at most one error), then the resolver's 2-of-3 resolution. Join by card id, never by position.
   UNKNOWN is preserved, and a card with no 2-of-3 majority stays UNRESOLVED (never forced).
3. Write `artifacts/r2_resolve/{T2,T4}/final/`:
   - `resolved.jsonl` (agreement + tiebreak);
   - `unresolved.jsonl`;
   - `gate.json`;
   - `opus_usage.json`. The lead supplies the per-folder tiebreak reader tokens: T2 b00 157,076; T2 b01 160,476; T4 b00 169,280;
     T4 b01 161,761 (subagent totals, including tool I/O).

## Part 2. R2M: R2a manifest from the resolved T2 supervision cards

Spec: `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_PLAN_20261017.md` §2a (slice table + admission rules) and
Addendum A (§ on R2a sources), read-only.

1. **Slots.** One slot per (card anchor) plus every `letter_heads` entry that both readers (or the 2-of-3 majority) gave with all four
   heads decided.
   - Any head UNKNOWN → quarantined, never zero-filled.
   - Key: `(crop hash, recogniser NFD start)`, deduplicated.
2. **Assign each slot to the §2a slice** (capitals/ALL-CAPS/numeral; ο/οι + monotonic; subscript α/η/ω; specks/foreign ink; exact-name
   contrasts) and to target-negative vs matched-positive, using the card's slice tags and the printed tuple.
   - Apply the diversity caps (≤10% of a slice per document, ≤5 target cards per page) deterministically, with seed 20261017.
   - Drop no slot silently: a capped slot goes to `excluded.jsonl` with its reason.
3. **Manifest** `artifacts/r2a_manifest/r2a_slots.jsonl`, in the training-slot format the R2 job consumes (see
   `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/INPUT_FORMATS.md`). Replacement semantics: a slot
   whose key exists in the old pool REPLACES that target and is never appended. Count replaced vs new slots against the frozen pool
   that the R2 package uses (look up its path in r2-prep's deploy files; read-only).
4. **Leakage check:** no manifest slot's document is in T4 (witness), validation or calibration (`docs/records/labelfix/spellcheck/R2/doc_roles.json`).
   Any hit = STOP.
5. **Report:** add a section to `docs/records/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md` with:
   - the slice × (negative, positive) table vs the §2a targets, showing deficits explicitly. The owner paused top-up reading, so the
     deficits stand; do not propose new cards;
   - documents per slice; quarantine and cap counts; replaced vs new;
   - the manifest sha256.

Tests for any new code (fixtures: an UNKNOWN head is quarantined, a duplicate key is counted once, the per-document cap, replacement
not append, the leakage STOP).

Last line: `B6c+R2M READY: T2 final <n>/800 (unresolved <n>), T4 final <n>/800 (unresolved <n>); gates <ok|fail>; R2a slots <n> (neg <n>/pos <n>; replaced <n>, new <n>; quarantined <n>); leakage 0; manifest sha <12>`.
