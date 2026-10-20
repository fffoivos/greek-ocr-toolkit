# OS3: follow-up to OS2, Google-row mapping fix from the coordinator (gpt-6.1-sol, medium, network OFF; no .git writes)

The coordinator found a defect in his first render: the Google row was empty.
- **Cause:** C1 `cards.jsonl` has no `line_id`, and its text field is `google_text`.
- **His fix (republished to the same URLs):**
  - the line id comes from the card crop's sha256, matched against W1 `features.jsonl` `crop_sha256` (5,326 cards map);
  - the text comes from `google_text`, falling back to the features text.
- **Patched builder:** `docs/records/owner_sheets/inputs/coordinator_build_sheets_v2.py`. It reads his map, copied to
  `docs/records/owner_sheets/inputs/coordinator_labelmap.json`.

Apply the same mapping to OS2's specs and builder (`scripts/review/build_owner_sheets_v2.py`, `docs/records/owner_sheets/*/spec.json`):
1. **Recompute the map yourself** from the C1 cards' crop sha256 and W1 `~/Projects/collect-v3-data/run/W1/features.jsonl`
   `crop_sha256`, and check it against the coordinator's map: same card → line-id pairs, and a count of 5,326. Report any difference. Use
   the recomputed map; it must equal his.
2. **Never an empty Google row:** every card has non-empty Google text (google_text, then features text). A card where both are empty
   is listed and kept out of the sheet. The test fails on any empty row.
3. **Doc ids:** identical to the coordinator's current build for every card he has. Re-run OS2's continuity check against the build
   that `coordinator_build_sheets_v2.py` produces.
4. Re-render `artifacts/owner_sheets/v2/*.html`, update `docs/records/owner_sheets/OS2_REPORT.md` with an OS3 section, and run the tests.

Last line: `OS3 READY: map pairs <n> (= coordinator <yes>); empty Google rows 0; doc ids identical <yes>; cards A <n> B <n>; tests <n> passed`.
