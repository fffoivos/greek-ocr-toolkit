# T11 — Google Cloud Vision (document text detection, hints el + grc) on the same failed-lines catalogue; compare with Document AI (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google APIs; ADC already configured; quota project ocr-ground-truth-20261008; the
Vision API is enabled on that project). No `.git` writes. ~470 small calls (list price USD 1.50 / 1,000 images).

## Why
T10 (docs/harvest/DOCAI_FAILED_LINES_v1.md, commit b97713c) showed Document AI emits none of the early-print glyphs (ϗ ȣ ϛ ϲ ϝ ϙ ϡ) and
substitutes look-alikes silently. Cloud Vision's DOCUMENT_TEXT_DETECTION is a different model and its language list names Ancient Greek
(`grc`, experimental). Owner (12 Oct): "use the google model here". Measure it on the same catalogue, same report, so the two are comparable.

## Required
1. `greekocr/readers/services/google_vision.py`: a service reader with the same shape as google_docai.py (explicit factory, gated by env/ADC,
   `read(path)` returning NFD text; plus a rich call returning the full annotation: per block/paragraph/word/symbol text, boxes and
   confidence, detected languages). Feature DOCUMENT_TEXT_DETECTION with imageContext.languageHints = ['el', 'grc'] (make hints a
   parameter; record them in every receipt). Use the REST endpoint via google-auth ADC like the DocAI adapter does; no new heavy SDK unless
   already installed. Cache responses by crop sha256 under docs/harvest/vision_failed_lines/responses/; never re-call a cached crop.
2. Generalise `prototypes/harvest/google_failed_lines.py` with an `--engine {docai,vision}` option (default docai, unchanged behaviour), output
   dir per engine (docs/harvest/vision_failed_lines/), the same per-crop metrics (lines returned = Vision paragraphs/lines as returned, text
   per line, chars, chars/100px, mean & min symbol confidence, empty, Greek character set), the same characters table (ALL / Anemi / Vouli,
   with the rare-glyph rows), the same treatment-by-failure-type table and controls baseline. Include Anemi (owner authorised 11 Oct):
   run with `--include-anemi`.
3. Comparison report `docs/harvest/VISION_VS_DOCAI_v1.md`: per crop, the two engines' texts side by side with NFD CER between them;
   agreement rate on the controls; per failure type the two treatments; the rare-glyph table for both engines side by side; and a short
   list of crops where Vision emitted any of ϗ ȣ ϛ ϲ ϝ ϙ ϡ (or where the two disagree only on those positions). Raw CSV.
4. Review page `docs/harvest/vision_vs_docai_review.html` in the same format as docai_failed_lines_review.html (reuse the generator): one
   card per crop with the crop and BOTH readings + confidences; images as files beside the page; phone-width safe.
5. Cost receipt (calls, list price) in the report and receipt.json; stop and report on any permission/billing error (e.g. API not enabled).
6. Tests (no network): adapter request/response parsing from a stored sample, the engine switch, the comparison metrics. INVENTORY for fixtures;
   docs/API.md + docs/READERS_DOCAI.md (or a new READERS_VISION.md) entries.
Last line exactly: `T11: done | calls: <n> | rare_glyph_crops_vision: <n> | tests: <n> passed`.
