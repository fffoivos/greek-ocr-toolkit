# B6: resolve tranches T2 and T4 from the two-reader answers; tiebreak decks for actual disagreements only (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`opus/r2-cards`). No `.git` writes. Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
Owner rule (17 Oct, Claude-usage pause): tiebreak readers ONLY on real disagreements, **≤ 100 cards per reader context**.

## Inputs (read-only)

- **Decks:** `docs/records/labelfix/spellcheck/R2/decks/{T2,T4}` (blind + private + controls_proposed.json).
- **Reader answers** (all 32 batches complete, 110 cards each):
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/r2read_{T2,T4}_{r1,r2}/b00..b07/answers.jsonl`, with each batch's `cards.jsonl`.
  - Reader 2 saw reverse order; join by card id, never by position.
- **Resolver:** `scripts/labelfix/r2_cards_resolve.py` (R2C2, tests 167). Use it as is. If it needs a change, make the change minimal,
  add tests, and list it.

## Do

1. **Per-batch gate:** run `--dry-run` for each of the 32 batch answer files. Report controls pass/fail per batch. A failing batch is
   reported, NOT dropped silently.
2. **Two-reader resolution per tranche,** following the protocol (`docs/records/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md` on the
   main worktree):
   - controls gate first;
   - agreement → resolved;
   - disagreement (or one invalid vote) → the tiebreak set;
   - UNKNOWN preserved.

   Outputs go to `artifacts/r2_resolve/{T2,T4}/`: resolved.jsonl, tiebreak cards, gate.json, the opus_usage.json the resolver emits.
3. **Tiebreak decks:** the resolver's tiebreak deck (options re-randomised, its own private map OUTSIDE the blind folders). Deal it into
   isolated reader folders:
   - `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/r2read_{T}_r3/bNN/`, ≤ 100 cards each, same layout as the r1/r2 folders (cards.jsonl, img/, README.md, answer_schema.json,
     an empty answers.jsonl);
   - a leak scan of each folder (no key, truth, reader answers or Google text reachable);
   - a receipt with hashes.

   If a tranche has 0 disagreements, say so, and no folder.
4. **Usable-slot inventory per tranche,** counted both ways: resolved now, and pending tiebreak.
   - By head (breathing / accent / dialytika / subscript), by role (T2 supervision, T4 witness), and by the hallucination slices used in
     R2: capital/ALL-CAPS/numeral, ο/οι monotonic, -η subscript, crasis, ΐ, clipped top. Use the slice tags on the cards if present;
     otherwise "untagged".
5. **Card-quality notes** (counts with examples):
   - cards where a Google-derived base letter made an option impossible or misleading;
   - monotonic-heavy controls;
   - cards both readers marked unreadable / low confidence.

Opus usage per tranche: the agents' token counts were not recorded per batch. Report the resolver's `opus_usage.json` fields and mark
token totals "not recorded". Do not estimate them.

## Report

`docs/records/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md` + tests run (resolver suite).
Last line: `B6 READY: T2 resolved <n>/<880> tiebreak <n> (<k> folders); T4 resolved <n>/<880> tiebreak <n> (<k> folders); gates <ok|fail list>; resolver changed <no|yes: ...>`.
