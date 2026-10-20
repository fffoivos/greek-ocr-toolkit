# Google Cloud Vision document text reader

T11 uses the synchronous [Vision REST endpoint](https://docs.cloud.google.com/vision/docs/reference/rest/v1/images/annotate), `DOCUMENT_TEXT_DETECTION`, and `imageContext.languageHints=["el","grc"]`. Google lists [Ancient Greek (`grc`) as experimental](https://docs.cloud.google.com/vision/docs/languages), checked 11 October 2026. The service model is the provider's unpinned default; its resolved version is not exposed in the receipt.

The adapter reuses the existing optional `docai` dependencies (`requests` and `google-auth`). No Vision SDK is installed or required. No cloud request occurs at import, factory construction or cache reuse. ADC must already be configured, the Vision API enabled, billing available, and the principal permitted to consume the quota project. `x-goog-user-project` is always explicit.

```python
from greekocr.readers.services.google_vision import load_google_vision
reader = load_google_vision(enabled=True, user_project='ocr-ground-truth-20261008')
text_nfd = reader.read('crop.png')
reading = reader.read_annotation('crop.png')
```

The factory also accepts `GREEKOCR_ENABLE_GOOGLE_VISION=1` and `GOOGLE_CLOUD_QUOTA_PROJECT`. Direct `VisionReader(...)` construction is an explicit service opt-in; ADC remains lazy. The failed-lines CLI itself is the explicit opt-in for its selected engine. `language_hints` is configurable as a sequence, including an empty sequence, and is recorded in every request receipt and cache envelope. Changing options for an already cached SHA fails instead of resubmitting it.

`read()` returns NFD text with whitespace and all newlines preserved. `read_annotation()` returns a `VisionReading` with raw text, unchanged `fullTextAnnotation`, flattened blocks/paragraphs/words/symbols (text, bounding boxes, reported confidence, detected languages, property and hierarchy address), lines and confidence summaries. Symbol confidence summaries exclude missing values rather than using zero. Detected languages retain their hierarchy level and address. Coordinates are provider image coordinates; original vertices and omitted zero coordinates are preserved.

Vision has no layout-line object. The audit preserves paragraph boundaries and splits inside paragraphs only at reported symbol LINE_BREAK, EOL_SURE_SPACE and HYPHEN. SPACE and SURE_SPACE are retained, and prefix breaks are honoured. HYPHEN is a structural line break whose hyphen is absent from symbol text; no glyph is invented. Line confidence is the enclosing paragraph's confidence, explicitly labelled, not a native Vision line confidence. If paragraphs are missing but raw text exists, the metrics label the splitlines fallback. The raw full annotation text remains authoritative for CER and character counts. [Provider schema](https://docs.cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse).

## Catalogue audit and comparison

```sh
.venv/bin/python scripts/harvest/google_failed_lines.py --engine vision --include-anemi
.venv/bin/python scripts/harvest/google_failed_lines.py --engine vision --include-anemi --offline
```

`--engine` defaults to `docai`, retaining the existing DocAI runner, paths and defaults. Vision defaults to hints `el grc`; override with `--language-hints`. `--out` is the parent report directory, with Vision data under `vision_failed_lines/`. Comparison reads existing `docai_failed_lines/` responses and verifies crop identity and raw metrics; it never makes a DocAI request. Anemi is included only with the explicit flag (owner authorised 11 October 2026). Native source pages and held-out data are untouched. The review page uses local crop files and the existing T10 card generator.

A unique image SHA costs at most one attempted request. Vision caches envelopes at `responses/<crop_sha256>.json`; original response bytes, attempts and cumulative ledger remain in `adapter_receipts/`. Cache hits verify the binding, response hash and original raw-file hash before use. File locks prevent simultaneous duplicate fills. An unresolved/failed attempt permanently stops that SHA instead of retrying it. Permission, billing, HTTP, embedded response and transport errors stop the run immediately, retaining partial metrics, report and cost receipt. Tokens and authorization headers are never saved. Offline misses fail before ADC. Reports are diagnostics of inter-engine agreement, not OCR accuracy.

The [official pricing](https://cloud.google.com/vision/pricing) lists US$1.50/1,000 Document Text Detection image-feature units after the first 1,000 free monthly units. Receipts estimate the base list price without assuming remaining free allowance, credits, taxes or discounts. Failed outcomes are disclosed as unknown; an estimate is not an invoice.

```sh
.venv/bin/python -m pytest tests/test_google_vision.py tests/test_google_failed_lines.py tests/test_docai.py -q
.venv/bin/python scripts/harvest/validate_vision_comparison.py
```

Tests use synthetic stored JSON and mocked credentials/transport, never network. Fixtures and hashes are recorded in [INVENTORY.md](../../../INVENTORY.md). See [API.md](../../../API.md#cloud-vision-service-reader-t11), [comparison report](../../../records/harvest/VISION_VS_DOCAI_v1.md), and [review](../../../harvest/vision_vs_docai_review.html).
