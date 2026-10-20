# RU4E-F3: fold r5, apply the lead audit, write ru1_v3_test_edits (gpt-6.1-sol, medium, network OFF; no .git writes; no blind glyph-READER runs, no browser or computer-use; reading local files is allowed)

The r5 replacement round is complete (`artifacts/ru1/ru4e2/driver_r5_exec.log`).
1. Re-combine with r5 (v4.4 scans, gates, coverage). Any still-VOID context: its positions stay hold. No more rounds.
2. Apply the lead audit `docs/records/labelfix/secondary/RU4E_LEAD_AUDIT.md` (30/30 confirmed: `lead_audit_confirmed`).
   - Every remaining lead_review position → hold, which keeps Google's ь.
   - The review PNG cells are NOT ruled (a cost decision) → hold.
3. **Write `artifacts/ru1/ru1_v3_test_edits.jsonl`, edits-only.**
   - Contents: rows with ≥1 edit plus hold rows. Text = the raw Google import text, byte-identical, except the ь→ъ characters. Split
     (test/dev) per row; per-edit provenance.
   - Verify per row that the diff equals the listed edits.
   - Manifest + sha.
   - LQB registration `ru1_v3_test_edits` (parent `google_raw_v2_import`), and a re-score.
   - Report the count of edits inside the wave-1c scored slice (the 1,742 Cyrillic test ids from the RU4E-2 report).

**Last line:** `RU4EF3 READY: rows <n> (test <n>, dev <n>); edits <n> (in wave1c slice <n> on <n> rows); holds <n>; sha256 <hex>; LQB <ok>`
