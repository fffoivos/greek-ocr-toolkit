# Collector known issues

Recorded 18 October 2026 from SEG-CP3b/CP4b receipts. Both issues are **for a later fix**. This is documentation only; the live materialize imports `collect_v3/` code.

## Cached foreground and label planes disagree — for a later fix

Approximately 4% of cached pages have inconsistent foreground and label planes: the CP4b snapshot found 3/75 live g1b entries and 1/24 inherited CP3 entries inconsistent (4/99, about 4%). The isolated fallback duplicates the NLG page and is also inconsistent: including it gives 5/100 cache entries, representing four distinct page IDs. These are recorded snapshots, not a live population estimate.

Evidence in `../greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seg/`: `CP4_cache_audit.json` (per-entry hashes, pixel counts and rectangles), `CP4_RECEIPT.md` (B1 diagnosis and fallback), `CP4_preparation.jsonl`, and `CP3_RECEIPT.md` (NLG consistency rejection). Live discrepancies are 3,517 pixels on `ia_poly1850--6a9e5e4676cec552--s030`, 2,959 on `serbia--14aa26e071cf6dd8--s001`, and 1,742 on `serbia--6b577f99816f3331--s006`. NLG `nlg--6146c0455e0103d2--s001` has 41,068 label-without-foreground pixels in `[1102,0,1192,1724]`; the fallback reproduces the inherited payload hashes.

The recorded code inspection identifies `greekocr/pages/pixels.py:625` labeling foreground before lines 643–648 clear scan-edge foreground without updating labels. Strict geometry validation rejects inconsistent planes. CP4c drops affected crops under `geometry_unavailable`; this is a policy loss, not measured detection or a collector repair.

## Inverted row envelopes — for a later fix

The CP3b snapshot found **181 inverted rows (bottom < top) on 10 pages**, among **9,975 row records in 99 caches** (75 live g1b, 24 isolated CP3; 38 W1 and 61 W2). Four inverted rows also have zero-height columns; there are zero additional degenerate-only rows and zero nonpositive body-guide rows.

Evidence in `../greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seg/`: `CP3b_geometry_audit.json` (all payload hashes, minima and negative/zero column counts), `CP3_RECEIPT.md` (page counts and diagnosis), and `CP4_RECEIPT.md`. Example: `gazette_modern--0020420cfe156a73--s000`, `row-00077`, has 516/1,354 inverted columns; at x=327, top=1483.686 and bottom=1474.799 (−8.887 px).

`greekocr/pages/lines.py::_boundaries()` aggregates extended/smoothed seams without enforcing top < bottom afterward. Attribution to conflicting extended seams is an inference from the saved curves and code, not a rerun of intermediate seams. The adapter quarantines invalid target/crop/neighbour dependencies; CP4c counts resulting losses as `geometry_unavailable`. No curves were refitted or collector code changed.
