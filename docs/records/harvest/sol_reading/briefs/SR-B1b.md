# SR-B1b: two control fixes after the lead's pixel review

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Read `docs/records/harvest/sol_reading/keys/control_review/LEAD_REVIEW.md` and your own `REPORT_B1.md` and `README_B1.md` first. Network off. Do not run git: the lead commits, because the sandbox blocks `.git` writes. Do not call codex. Never delete outside the pack root.

1. **yer control k15896cc479.** Its expected answer becomes `{"1":"ь","2":"ь","3":"ъ","4":"ъ","5":"ъ"}`, with provenance `"lead pixel review 2026-10-17 12:41 (LEAD_REVIEW.md)"`. Change it at the source of truth that `tools/build_packs.py` uses (an override table in the builder or in a data file, not a hand edit of the key), so that a rebuild reproduces it. Update the yer review `.md`.

2. **owner39 controls.** Regenerate the `options` of the 4 controls with exactly the option generator used for the 39 bed cards: the fixed accent-head variation at the anchor, 4 options, ported in `efficiency/build_owner39.py`. Check that every bed card's options are reproduced by that generator. Then apply the same seeded A–D permutation scheme.
   - The expected form and heads stay as they are.
   - The expected choice becomes the option letter whose text equals the expected form exactly (NFC), else `literal`. For example, στάδιο should now be an option.
   - Re-render nothing else.
   - Rebuild the owner39 r1/r2 folders and the key deterministically. Re-run `tools/scan_packs.py` on all 6 folders. Add a scan check that every card in a bed has the same number of options.

3. **Contact sheets.** Keep them only under `docs/records/harvest/sol_reading/keys/control_review/`. The lead moved `PACK_ROOT/control_review` to `…/scratchpad/control_review_private` because it sat within reach of readers. Change `build_packs.py` so it never writes anything into PACK_ROOT except the bed folders and the MANIFESTs. Add a test that PACK_ROOT holds only `<bed>/{r1,r2,MANIFEST.r1.json,MANIFEST.r2.json}`.

4. **Tests and receipt.** Re-run all tests and write `TEST_RESULTS_B1b.txt`. Update `BUILD_RECEIPT_B1.json`, or add `BUILD_RECEIPT_B1b.json` with new manifests and shas.

Last line of your final message: `SR-B1b READY: tests=<pass>/<total> owner39 control choices=<list> scan=ok`, or `SR-B1b BLOCKED: <reason>`.
