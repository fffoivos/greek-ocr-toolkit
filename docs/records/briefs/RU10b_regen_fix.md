# RU1-0b: crop regeneration fix + build the packs (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue RU1-0 (`docs/records/briefs/RU10_census_packs.md`, report `docs/records/labelfix/secondary/RU10_REPORT.md`, which ended BLOCKED with
`crop_unavailable 1146`). Same worktree, constraints and allowed writes as RU1-0.

**Cause, verified by the lead at 15:29.** The x86_64 Pillow interpreter re-encodes the PNG differently. The collector's own
interpreter regenerates byte-exactly:
- interpreter: `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (arm64, Python 3.11.3, Pillow 12.3.0);
- verified on the first ia_russian row: `storage.ensure_crop` on a row copy with `crop` redirected to the scratchpad returned without
  a hash error.

**Do.**
1. **Regenerate** every needed crop by calling `collect_v3.storage.ensure_crop` under that interpreter, ALWAYS on a row copy whose
   `crop` points into the scratchpad `ru1_cache/crops/`. Never write under `~/Projects/collect-v3-data/`. Hash failures stay
   `crop_unavailable` and are listed by id. Later image work (zooms, contact sheets) may use either interpreter, because the pack
   only needs the copied crop bytes. Record the interpreter path and the Pillow version in the receipt.
2. **Controls.**
   - The 19 C1 control lines: use the regenerated W1 crops.
   - The 40 v2 control lines that have no W1 id: use their saved adjudication crops (the files referenced in
     `yer_adjudication/items_*.jsonl`), copied after checking their sha256 against the recorded values. Key them by their existing
     source ids, with `w1_id: null`.

   All 59 lines (65 slots) are then usable as controls. Zero-slot lines may be used as controls too; they test the "unmarked final
   hard signs" field only and do not count toward the control gate.
3. **Modern spot check:** dropped. All 10 books are pre-1918. Record that in the report.
4. **Build** the 4 planned contexts (≤90 bed items plus ≈9 slot-bearing controls each, no repeat within a context). Run the copied
   `scan_packs.py` closure check, and write a `MANIFEST.r1.json` per context per HANDOVER §4.
5. **Update** `artifacts/ru1/RU10_RECEIPT.json` (as `RU10b_RECEIPT.json`, keeping the old one) and append a "RU1-0b" section to
   `docs/records/labelfix/secondary/RU10_REPORT.md`. Re-run the tests.

**Last line:** `RU10b READY: crops regenerated <n>/<n> (unavailable <n>); bed lines <n> slots <n> (Google-ь edit candidates <n>); controls <n> lines / <n> slots; contexts <n>; closure <ok|FAIL>; tests <n> passed`
