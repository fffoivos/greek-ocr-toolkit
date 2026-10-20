# MIR1: diagnose a mirrored crop and scan for others (gpt-6.1-sol, medium, network OFF, read-only diagnosis)

The secondary-corrections lead reports that the crop of **`lekythos--dcfa99599048d352--s000-l0144`** is **mirrored left to right**: the printed line "Ἀνοικτόν 8.30-1 καὶ 3-7.30 μ.μ." appears reversed, while Google's label reads it correctly. They found it in an N1 glyph check.

Inputs (read-only; the live W2 Gazette collector is running, so never write the run root or take locks):
- `~/Projects/collect-v3-data/run/W1/features.jsonl`;
- `run/W1/pages/<page>.json`;
- the retained raster `run/cache/pages/…`;
- the saved Google response `run/responses/…`.

If a crop is regenerated, use only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (the byte-exact interpreter).

## Do
1. **This page.**
   - Is the whole page raster mirrored, or only this crop? Check the raster and several other rows on the same page; view them.
   - Does the Google response record a transform, a page orientation or a detected mirror for this page or line? Is the line's crop_bbox consistent with the response geometry?
   - Is the text in the image actually mirrored ink, i.e. show-through from the verso, or a mirrored scan?
   - Trace the page through the collector's route (lekythos source: download, raster conversion, `analyse`, crop) and say where a mirror could enter. Read code only; change nothing.
2. **Scan for others,** without visual reading of every crop. Find a cheap, deterministic signal and validate it on this witness. Candidates:
   - Google per-token/line orientation or transform fields;
   - per-row agreement between token x-order and label order;
   - the page-level response orientation.
   - Apply it to every W1 row (and to the W2 rows completed so far, read-only), report counts per source and page, and list the candidate ids.
   - **View** up to 10 candidates to confirm or reject the signal, and report precision on those.
3. **Report** in `docs/records/harvest/recut_v1/w1_masked/mirror/MIR1.md`: cause, scope (pages and rows), the detection signal and its validation, and a recommended exclusion rule (as a row-level class, like rotated_crop). **Write no exclusion.**

Leave a guarded commit list. The last line must be exactly:
`MIR1: done | cause: <page|crop|showthrough|unknown> | candidates: <n> rows on <p> pages | signal precision on viewed: <k>/<m> | recommended rule: <short>`
