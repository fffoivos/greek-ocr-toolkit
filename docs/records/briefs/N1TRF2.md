# N1-TR-F2: apply lead rulings, final n1_v1_train (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

**Lead rulings** for the 2 agreed raised-dot cells (scratchpad `n1_review/n1tr/`):
- cell 1, `69846639273a60b797e93cb9-p000219-l0023` "100-300": printed **hyphen**, a range;
- cell 2, `39fbbdfd2c8030f211a318b7-p000138-l0012` "433-444": printed **hyphen**, a page range.

Both are `pixel_checked: true`; the printed value is the Google text unchanged. There are no edits.

Fill `lead_template.jsonl` and run `scripts/numerics/n1tr_finalize.sh --apply-lead`. Output `artifacts/n1/n1_v1_train.jsonl`:
- the label is unchanged for every row, because no raised dot was confirmed;
- dash-type tags and per-slot provenance are kept;
- holds: the unlocalised slots, plus the void-context positions.

Write the manifest and sha, register `n1_v1_train` in the LQB and re-score it. State the finding in `N1TR_REPORT.md`: among the 474
localised candidate slots in the v2 train rows, agreed reads found 83 hyphens/dashes, 215 baseline dots and 0 raised dots. The
raised-thousands-dot fault is concentrated in ELSTAT-type tables, which are not in the v2 train rows.

**Last line:** `N1TRF2 READY: n1_v1_train rows <n>; edits 0; tags <n>; holds <n>; sha256 <hex>; LQB registered <ok>`
