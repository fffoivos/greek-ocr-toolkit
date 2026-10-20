# SG2: missing-box page strips + the 19% provenance (gpt-6.1-sol, medium, network OFF, read-only inputs, low priority)

This tops up SG1. Write only under `docs/records/harvest/collect_v3/segmentation_gallery/`. Never touch `collect_v3/`.

1. **Provenance of "Google line boxes cover only 81% of printed rows on 50 pages"** (page numbers, headings, one-word lines, two-column debates missed). It comes from the Sol geometry audit of 16 Oct, branch `sol/label-geometry`, G1/G1d, a missed-rows census.
   - Find it read-only: `git -C ~/Projects/greek-ocr-toolkit log --all --oneline | grep -i -E "geometry|G1d|missed"`, then `git show <commit>:<path>` for the census and receipt files. Do not check out anything.
   - Record the commit, path and line in `counts.json` → `v2_wide.printed_rows_without_google_box`. If it is not found, keep "not found" and list what you searched.
2. **3–4 page strips** from those 50 pages, using a page raster on this Mac (harvest_big or the census's paths):
   - show printed rows with **no Google box** and at least one **merged box**;
   - draw Google's line boxes in one colour and mark the missed rows in another.
   - Add them to `examples.jsonl` with type `no_google_box`, update `index.html`, and keep the total PNG bytes under 6 MB.

The last line must be exactly:
`SG2: done | provenance: <commit:path|not found> | no-box strips: <n> | png bytes total: <n>`
