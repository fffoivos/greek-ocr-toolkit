# T15 — Real pages: read the pilot pages whole with both readers, map the returned lines onto our 500 sampled lines, compare with the crop-alone reads (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Vision + Document AI; ADC). No `.git` writes. Cost cap USD 2.00.
Context: T14/T14b/T14c (docs/records/harvest/MONTAGE_v1.md): readers are deterministic on single crops but every fabricated montage layout changes 20–47% of readings and
flush stacks make DocAI merge adjacent lines. Owner (13 Oct): "what if we add real pages" — read the real page, the only context that is genuine.
Pilot evidence: glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/pilot_v1/{records.jsonl, pages/*.json, google/}; page PDFs under
docs/records/harvest/harvest_big/anemi_wave3_sample_t13c/records/<book>/<version>/page-NNNNNN.pdf (one page each); the 500 sampled lines = records with sampled=true
(docs/records/harvest/pilot_v1/sampling.json); each record has page-coordinate polygon/bbox, and the sampled ones have straighten info + straight_crop + cached reads.
Required:
1. Page set: the pages that contain the 500 sampled lines (expected ≈ 250–300). Render each page exactly as the pilot did (same renderer, DPI and sha as
   pages/*.json; verify by hash where the pilot recorded one). Send the UNSTRAIGHTENED full page image, one call per page per reader (≤ 600 calls, ≈ USD 0.90),
   with the T14 cache/budget discipline (reservations, raw responses under docs/records/harvest/harvest_big/page_reads_v1/).
2. Mapping: DocAI line boxes / Vision symbol-break lines (existing helpers) → our sampled line polygons in page coordinates. Assign by ≥70% of the returned box
   height inside the line's polygon band AND horizontal overlap ≥ 50% of the shorter width; a returned box touching two of our lines = merged (count, never guess);
   side-by-side pieces joined in x order (list-return rule); zero = lost; ≥2 = split. Record every assignment under docs/records/harvest/page_reads_v1/assignments/.
3. Compare per reader: page read vs cached crop-alone read on the 500 lines — exact NFD identity %, letters+marks identity %, merged/lost/split counts, mean
   symbol confidence page vs crop. Then the HARVEST metric: tier-1 rate (Vision == DocAI exact) and "letters agree" rate (the pilot merge rule) in page mode vs
   crop mode on the same 500 lines. Report both by decade and by page_class.
4. Blind check for the owner: 30 lines where page read ≠ crop read (stratified: 10 where only Vision differs, 10 only DocAI, 10 both), review page
   docs/records/harvest/page_reads_v1/blind_review.html with the straight crop image (inlined base64), and for each reader the two readings in RANDOM A/B order with the
   key in blind_key.json (not shown on the page). Also inline the 10 most-changed lines side by side with the page region (±2 lines) so context is visible.
5. Report docs/records/harvest/PAGE_READS_v1.md: tables of 3, cost receipt, the mapping method, failure examples, and a verdict on whether page mode is a usable
   substitute for crop mode for the harvest (cost 1 call/page vs 1 call/line), stated as measurements — the accuracy judgement belongs to the owner's blind check.
6. Tests (no network) for the page→line mapping (merged/lost/split, side-by-side join, polygon bands) and the blind-page builder. INVENTORY.
Last line exactly: `T15: done | pages: <n> | page_vs_crop_exact_vision: <pct> | page_vs_crop_exact_docai: <pct> | merged_lost_vision: <n>/<n> | merged_lost_docai: <n>/<n> | tier1_crop: <pct> | tier1_page: <pct> | calls: <n> | tests: <n> passed`.
