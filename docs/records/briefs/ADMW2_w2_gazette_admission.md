# ADMW2: W2 + Gazette admission files with the accepted screens, on existing geometry; staged crops; a re-runnable builder (gpt-6.1-sol, medium, network OFF, no reading)

**Coordinator ruling:** the SEG screens are **accepted as they stand** (aa3d9067; ASTRA-SEG2 re-review running on a clean checkout of aa3d9067). **Do not rewrite history**; new commits are fine.

Produce the W2 and Gazette admission files now on **whatever geometry exists**. Rows with no geometry are `geometry_unavailable` (fail closed), so the final file becomes a **re-run** once the owner decides the full-population geometry run (b).

## Inputs (read-only; never the live run root, where a BSB collector run is live)
- `~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl` and `W1_features_20261018_0524.jsonl`. Verify the shas against `SHA256_20261018_0524.txt`.
- `release_exclusions.json` (sol-collect, read-only), the registered line-level classes.
- **Geometry:** every existing prepared cache — CP3_geometry, CP4_geometry, CP7 gate caches (r1 + r2), and `~/Projects/collect-v3-data/geometry_prep/` if present (it is not yet) — through the CP2 adapter with full identity binding. Plus the live `run/cache/g1b` entries, read-only and only when hash-valid.

## Build
1. **Pre-screen population (ADM4 rule on W2):** W2 rows with `candidate_usable == true` in the W2-qualified strata (W2C1, ed074681):
   - bsb_poly1850 poly1850; ia_poly1850 poly1850; nlg poly1850 / poly1900 / greek_poly; serbia cyrillic; elstat numerics_tables;
   - gazette_modern modern_scanned with gazette_stratum `measured_1986_1990`;
   - plus headings_caps across these sources (CAPS4 qualified it in W1; state that the W2 caps are carried by that ruling).

   Remove the registered exclusion classes.
2. **Admission:** `greekocr.harvest.admission` at the **accepted version** (the one in aa3d9067): text rules, merged, neighbour_words, orientation (regional, unknown → admit), geometry_unavailable fail-closed, and the edge_clip_candidate diagnostic (non-gating, counted).
3. **Outputs** in `docs/records/harvest/collect_v3_admission/`:
   - `w2_originals_v3_admission.jsonl` (per row) + `_admitted.jsonl` + `_receipt.json`;
   - `gazette_w2_originals_v3_*` as the Gazette subset view (the same rows, a separate file for the owner's Gazette admission);
   - gzip any file over 50 MB and record the sha of the uncompressed file.
4. **Counts per source × class:** pre-screen n; dropped per rule (text rules / merged / neighbour_words / orientation / geometry_unavailable); admitted n; **unavailable share**; orientation_unknown n; edge_clip_candidate n.
5. **Stage crops** for the admitted rows with `stage_crops.py`: the same tree, `crops/<source>/<row_id>.png`, extend `crops_manifest.jsonl`, the byte-exact interpreter only. Watch the disk: about 11 GB free, so stop below 10 GB.
6. **Re-runnable builder:** `build_release_admission.py --tranche W1|W2|all --geometry <dirs…>`. Rerunning it after (b) regenerates the same files with full geometry. Also run it for **W1** now, as `w1_originals_v3_screened_*` (the same rules), so the final release file is purely a re-run. Keep the existing `w1_originals_v3_admitted.jsonl` untouched.

Tests: population filters; exclusions; deterministic outputs; that no geometry gives unavailable, never keep; the staged crop sha equals crop_sha256; the counts reconcile.

Write `ADMW2_RECEIPT.md` and the commit list. The last line must be exactly:
`ADMW2: done | W2 pre-screen <n> -> admitted <a> (geometry_unavailable <u>, <pct>%) | gazette W2 <n> -> <a> | W1 screened <n> -> <a> (unavailable <u>) | staged <s> crops (<GB>) | builder ready | tests: <n> passed`
