# RU4E-F1: finalise phase 1 (gpt-6.1-sol, medium, network OFF; no .git writes; no blind glyph-READER runs, no browser or computer-use; reading local files is allowed)

All 32 RU4E-2 contexts are DONE. Run `scripts/secondary/ru4e2_finalize.sh` up to the lead material:
- v4.4 scans, gates, derived-view coverage, combine;
- for VOID/invalid contexts: build fresh r3 (and r4 where both readers are invalid) packs with their driver
  (`run_ru4e2_r3_all.sh`, 70% stop) and finaliser routing, and list them;
- lead sheets in the scratchpad `ru1_review/ru4e2/`: an audit of 20 edit_hard + 10 keep_soft, seeded, with same-book references,
  plus a template.

Do not write `ru1_v3_test_edits` yet.

**Last line:** `RU4EF1 READY: contexts valid <n>/32 (void <list>); edit_hard <n>, keep_soft <n>, lead_review <n> (<reasons>); r3 contexts <n> (items <n>, est <pts>); audit cells 30`
