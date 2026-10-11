# T13b — H1 pilot SAMPLE overnight (owner: AT MOST 500 LINES, long complete lines only): Vouli + later Anemi books → fast lines (stack@52cee3b) → gates → straighten → Vision + Document AI labels → tiers, yield and noise tables, review page of ALL sampled lines (gpt-6.1-sol, xhigh)
OWNER RULE (12 Oct 01:20): "you are not supposed to make the whole set now! just sample the lines, 500 at most, make sure you use long complete lines." So: run the
line finder on the pages, apply the gates, then SAMPLE ≤ 500 lines in total (≈150 Vouli + ≈350 Anemi, stratified by book/decade), choosing LONG COMPLETE
body lines: width ≥ 0.8 × the column band width, not the first/last line of a paragraph if it is short, not touching page/column edges, passing every
gate. Only the sampled lines go to Google (≤ 1,000 calls, ≈ USD 1.5). Everything else below applies to the sample.
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Anemi page viewer at the polite rate; Google Vision + Document AI; ADC configured). No `.git` writes.
This Mac runs it (owner expects results in the morning): keep CPU jobs short (the stack is ~0.35 s/page; 500 pages ≈ 3 min); Google spend CAP for this task: USD 3 list price (single-crop calls only; no montage needed at this size). STOP and report at the cap. Credentials: ANEMI_USER / ANEMI_PASS are in your environment (never print,
log or write them). Plan: ~/Projects/glossapi-development/docs/experiments/glossapi_improvement_20261006/PLAN_GLOSSAPI_v3_20261007.md §H1
(read it: gates, tiers, rare-glyph rule, list-return rule, sampling rule). Reports of the engine tests: docs/harvest/*.md.

## Inputs
- Line finder: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/prototypes/fast_lines/stack` at commit 52cee3b (worktree HEAD is
  later: run with `git -C <worktree> show 52cee3b:...` exported to a temp dir, or `git worktree`-free checkout of that path into
  docs/harvest/pilot/_stack_52cee3b/, and record the commit on every line). Call: `Stack()('page.png')` → polygons per line (`docs/research/FAST_LINES_STACK.md`
  in that worktree). The toolkit venv has onnxruntime 1.31.0; the stack's ONNX models are under the worktree's `.astra/fast_lines/onnx/`.
- Vouli pages: 20 pages sampled across the 107 PDFs in ~/Projects/greek-page-ocr/data/raw/pdf_cache/ (render with bench/extract_lines.py SCALE = 200/72,
  grayscale, exactly as the extractor does; keep the InVision text-layer lines per page from pypdfium2 as the weak third vote).
- Anemi wave-3 SAMPLE: 30 books × 5 pages (middle of the book) from ~/Projects/greek-page-ocr/docs/evidence/o4c/anemi_wave3_proposal.json
  (choose 30 of the 150 spread over the decades 1860–1930), fetched with ~/Projects/greek-page-ocr/scripts/fetch/o4b_anemi_pages.py
  (plan/fetch/verify; polite, resumable, receipts). It currently fetches whole records in ranking order: ADD a `--records <json>` and a
  `--page-range middle:5` option (minimal, tested, in that repo's script — you may edit that file; commit nothing). Dest:
  ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/anemi_wave3_sample/. 150 pages, ~20 MB. Internal-only licence
  (CC BY-NC-ND): crops may go to Google (owner 11 Oct).
## Pipeline (write it as `greekocr/harvest/` package + `greekocr harvest pilot` CLI; one JSONL record per line; every record carries provenance)
1. Page gates: skip rotated pages (box-angle histogram), table pages (box lattice / long rules), pages where the stack's bend scout fires; keep
   body pages (one or two columns). Record the gate decision per page.
2. Lines from the stack; crop gates: height ≤ 1.5 × the page's body line pitch; not touching a curled edge; not far taller than neighbours;
   inside a column band; drop frames/ornaments/stamps by the catalogue heuristics. Record each gate per line.
3. Straighten + tight crop (greekocr.glyphs: separate_lines(tight=True, margin=0.2) or the equivalent entry point in greekocr/glyphs; if it
   needs page+box use it that way; keep the raw polygon crop too).
4. Readers: Vision (hints el+grc) and Document AI on the straightened crop; InVision text layer for Vouli lines where a text-layer line overlaps
   ≥ 60% of the crop. Apply the list-return rule (pieces side by side in one vertical band → join; stacked bands → reject; garbage pieces →
   drop/obstructed). Labels: tier 1 = Vision and DocAI agree exactly (NFD, whitespace-normalised); tier 2 = they differ by ≤ 2 NFD edits or
   one agrees with the text layer; tier 3 = disagree (keep both readings, no label); rejected = empty/obstructed/garbage. Rare-glyph note:
   where DocAI wrote "κὶ" and Vision "καὶ" (and similar substitution pairs listed in docs/harvest/VISION_VS_DOCAI_v1.md), count as agreement
   with the tag `rare_glyph_substitution` and keep Vision's reading.
5. Per-line metadata (T5 line features where cheap): width, height, x-height estimate, chars/100px, faintness proxy (darkest-percentile
   contrast), source, book/decade, page class, stack commit, gate flags, readers' confidences.
## Deliverables (morning)
- `docs/harvest/PILOT_v1.md`: yield table per source and decade (pages → lines found → survived gates → tier 1 / 2 / 3 / rejected), reader
  disagreement rate per source/decade (the noise estimate), the characters table per source (rare-glyph rows), cost receipt (calls, USD),
  timings per stage per page, the 10 most common gate reasons with counts, and a frank list of failure modes seen with crop links.
- `docs/harvest/pilot_review.html`: ALL sampled lines (≤ 500), grouped by source and decade, each card: straightened crop (+ raw crop
  toggle), both readings, tier, gate flags, text-layer line if any; images as files beside the page; phone-width safe; the review generator
  style of scripts/glyphs/pages_review.html.
- `docs/harvest/pilot_v1/records.jsonl` (all lines, all fields; images referenced by path under harvest_big, not embedded), `summary.json`.
- Tests (no network): gates on synthetic pages, tiering logic incl. the substitution rule, list-return geometry rule, record schema. INVENTORY; API.md.
Last line exactly: `T13B: done | pages: <n> | lines_found: <n> | tier1: <n> | tier2: <n> | cost_usd: <x> | tests: <n> passed`.
