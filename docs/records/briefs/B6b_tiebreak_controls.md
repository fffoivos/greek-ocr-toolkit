# B6b: re-deal the tiebreak folders with 10 controls each (gpt-6.1-sol, medium, network OFF; no .git writes)

**Lead ruling (owner Claude-usage pause):** B6 planted 159 controls next to 180 pending data cards, about half of every folder. Cap the
controls at **10 per folder** (about 20%). The gate keeps its rule (at most one control error per folder). The folders then hold about
220 cards in total instead of 339.

Do:
1. Keep B6's outputs. Write the new deal next to them as `artifacts/r2_resolve/{T2,T4}/tiebreak_v2/`.
2. Data cards are unchanged: the same 78 (T2) and 102 (T4) pending cards, with the resolver's re-randomised options and the private map
   kept outside the folders.
3. Control choice is deterministic, with seed 20261017:
   - 10 per folder, drawn from the scored controls only (never T2 `aeead432bc9a619c69e081b1`);
   - prefer polytonic, non-monotonic controls; give a head mix that covers breathing, accent, and at least one subscript or dialytika
     where available;
   - shuffle the controls into position;
   - record the selection rule and ids in the receipt.
4. Rebuild `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/r2read_{T2,T4}_r3/b00,b01` IN PLACE. They are unread (answers.jsonl empty): verify that first, or STOP.
   - The README is unchanged, except that it must not mention any model name.
   - Then run the leak scan, the hash receipt (`r3_deal_receipt_v2.json`), and empty answers files.
5. Check the resolver can consume the v2 deal. Dry-run each folder through the resolver's tiebreak path with synthetic answers in a
   temp dir; the controls gate must evaluate 10 per folder.
6. Update `docs/records/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md` with a v2 section: the counts table and the selection rule.

Last line: `B6b READY: folders 4; cards <n> (data 180, controls 40); leak scan pass; resolver dry-run pass`.
