# T19 — Round-1 page reads, everything not yet read: Document AI ONLY (decided 14 Oct), all accepted pages of decades 1890–1930 plus every rescued book's pages (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Document AI; ADC). NO Cloud Vision calls — Vision is dropped as a reader (owner, 14 Oct). No `.git` writes. Cost cap USD 3.00.
Scope: docs/records/harvest/round1/manifest_all.json rows with harvest_accepted=true that are NOT in docs/records/harvest/round1/reads_d1/records.jsonl (page_id) — expected 1,189 pages:
origin "t16" pages of decades 1890–1930 and all origin "rescue" pages (any decade). Read nothing twice.
Required:
1. One DocAI call per page (T17 bindings, cache + budget discipline, at-most-once, raw responses under docs/records/harvest/harvest_big/round1/google/). Line set = DocAI
   line layouts in provider order, native bboxes (T15 inverse transform where a transform is reported). Per-line DocAI text, mean/min symbol confidence, symbol
   count, letter count, flags (short_line, tall_box = height > 1.7 × page median counted-line height, low_confidence = mean < 0.89).
2. Output docs/records/harvest/round1/reads_rest/: records.jsonl (same fields as reads_d1 minus the Vision/tier fields — set vision_text null, tier null, label = docai_text
   for counted lines), per-page assignment files, summary.json (per decade/book: pages, lines, counted, tall, low-confidence, mean confidence), receipt.json.
   Also docs/records/harvest/round1/records_all.jsonl = reads_d1 rows (unchanged) + reads_rest rows, each tagged read_batch "d1" | "rest".
3. Compiled images, exactly the owner-approved format of docs/records/harvest/harvest_big/round1/reads_d1_compiled (see its README.txt; builder logic: left = page with
   green numbered boxes, red box when tall; right = same-size white panel with each line's DocAI text drawn at its box position, ONE type size per page = the 25th
   percentile of the per-line fitted sizes capped at 0.95 × median counted-line height, lines that overflow shrink individually; red text = mean confidence < 0.89;
   40 px white margin, grey rule between; JPEG q85) into docs/records/harvest/harvest_big/round1/reads_rest_compiled/<decade>s/[RESCUED_]<year>_<title40>_<id6>/pNNNN.jpg.
   Put the builder in scripts/harvest/compile_page_reads.py so it can be rerun on any records file; regenerate reads_d1_compiled with it too and confirm byte-level
   layout equivalence on 3 pages (same canvas size, same text positions ±1 px).
4. Report docs/records/harvest/round1/READS_REST.md: tables, cost, failures (lost/empty pages, transforms). Tests (no network) for the scope selection (no re-reads), flags
   and the compile builder. INVENTORY.
Last line exactly: `T19: done | pages: <n> | lines: <n> | counted: <n> | tall: <n> | low_conf: <n> | calls: <n> | usd: <x.xx> | tests: <n> passed`.
