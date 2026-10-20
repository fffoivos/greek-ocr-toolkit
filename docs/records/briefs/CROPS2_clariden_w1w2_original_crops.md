# CROPS2: byte-exact original W1/W2 crops on Clariden (gpt-6.1-sol, medium) — for the segmentation lead, to run AFTER the census rerun

**Owner/coordinator context (19 Oct):** experiment B needs the **original** W1/W2 crops as files on Clariden. Today the W1/W2 crop directories recorded in the rows do not exist there. The filter pipeline reconstructs W1/W2 crops **in memory** from the cached source pages and crop boxes (see `docs/records/harvest/collect_v3_admission/segeval1/cells/HANDOFF.md`, "W1/W2 runtime crops can be reconstructed in memory…"). This task makes them durable files, **byte-exact** to each row's recorded `crop_sha256`.

This is a **separate task from the census package**. It does not change any census verdict, tool or rule. It only materialises bytes. Leads never submit Clariden jobs: the coordinator verifies the deploy and submits.

## Scope
- **Rows:** every collect-v3 W1/W2 row in the census input (parent ids `collect-v3-W1-…`, `collect-v3-W2-…`; about 143k in census_03), or the rerun's equivalent. Keep a flag to restrict to the census ADMIT rows only (the owner's scope decision is pending; default = all W1/W2 rows).
- **Source:** the cached source pages already on Clariden that the pipeline uses (`crop_source_image` / `crop_source_sha256` + `crop_bbox` per row). Verify each source page's sha256 before cropping.

## Method: the existing reconstruction, unchanged
1. Reuse the pipeline's **existing** W1/W2 crop reconstruction function (the one the census runs in memory). Do not write a new cropper.
2. Encode exactly as the collector does (`collect_v3.storage.ensure_crop`: `convert('L').crop(crop_bbox)`, PNG `compress_level=3`).
3. **Check sha256 == `crop_sha256` for every row.**
4. **Output layout:** `$W/collect_v3_crops/<W1|W2>/<source>/<row_id>.png`, plus `crops_manifest.jsonl` (row_id, parent_id, source, class, relative path, sha256, bytes) and a receipt (counts, total bytes, failures, interpreter/libpng/zlib versions, the code sha).

## Byte-exactness gate (decides route a vs b)
- **Pilot first:** 500 rows, a uniform sample across sources, on one CPU job.
  - If **≥ 99.9% match**, run all rows; mismatches go to `failures.jsonl` and are reported, never kept.
  - If the match rate is lower, **stop.** Report the mismatch pattern: same pixels but different PNG bytes = an encoder difference, versus different pixels.
- On a stop, the coordinator falls back to **route (b)**: staging on the Mac with the collector .venv (byte-exact, proven on 28,798 W1 crops by CROPS1), then upload. That needs the owner's per-run go.
- **Pixel-identical but byte-different PNGs are NOT accepted** as originals. Report them; the owner decides.

## Tests
Sha equality on the pilot; deterministic paths; re-run idempotence (skip valid files); no census/admission files touched.

Write a guarded commit list. The last line must be exactly:
`CROPS2: done | pilot <k>/500 byte-exact | rows <n> materialised, failures <f> | bytes <GB> | path $W/collect_v3_crops | receipt <sha>`
