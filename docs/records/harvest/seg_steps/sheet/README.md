# SEG final owner sheet (local, unpublished)

Open `seg09_sheet.html`. The copied renderer is byte-identical to review worktree HEAD `19347b5a8a89bdb36391c2baf03ace3a3b0a4c11`; its three file hashes are in `receipt.json`.

Rebuild offline:

```
../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/sheet/build.py
python3 -B docs/records/harvest/seg_steps/sheet/verify.py
```

The builder only reads saved results and crop bytes; it imports no segmentation or reader module. `verify.py` checks the rendered document and attempts local headless screenshots without downloads. No publication, database seeding or git operation is part of either command.

There are 238 changed lines: 28 now disagree, 77 newly agree and 133 have no owner judgement. The 59 proposal lines overlap those by 18; each shared card appears once in the final proposal section. The union is 279 cards. The group totals in the ready line refer to the changed set; proposed-band is its complete, overlapping set.

Saved-evidence limits:

- 49 typology cards have a combined 0.8-to-s3 change with no individual s1/s2/s3 flip record. Their attribution is explicitly unresolved; seven also have a known s4 flip. No missing intermediate verdict was inferred.
- Curved box outlines map the saved unrolled bounds back along the saved sampled base polyline. The full per-pixel base was not saved, so the visual outline is approximate. The numbers are the exact saved measurements.
- Gate-blocked small crops can show saved diagnostic all-component bounds, labelled accordingly. They do not replace unavailable Stage-B measurements.
- The package accepts plain-text intro content. The score and 2×2 tables use the saved report's pipe-delimited rows with line breaks; the renderer is unchanged.
- Headless Chrome closed on launch and local headless Firefox aborted with SIGABRT. Screenshot and visual layout verification are unavailable in this session; structural verification and the package's offline JS runtime check passed. See `browser_check.log` and `runtime_check.log`.

Owner marks are shown only as historical text. The sheet never seeds marks into `seg09:<line_id>`; it reads existing documents and saves only after an owner action.

SEG SHEET READY: cards 279 (disagree 28, newly agree 77, unjudged 133; proposed-band 59); html 3.80 MB; crop sha 279/279; no-load-write ok; screenshot unavailable
