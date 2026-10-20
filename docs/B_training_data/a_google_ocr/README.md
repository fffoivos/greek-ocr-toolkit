# B.a — Google Document AI page reads

Reader references: [Document AI](readers/READERS_DOCAI.md), [Transkribus](readers/READERS_TRANSKRIBUS.md), and [Vision](readers/READERS_VISION.md).

Documentation for `cleanup/20261019`, inspected 19 October 2026. Repository paths below are relative to the repository root. Acquisition produces source-bound page responses and line observations; [B.c](../c_pipeline/README.md) defines the current filtering and correction sequence. Historical collector admission flags are not certificates for that sequence. Source populations, orthography and split restrictions are tabulated in [SOURCES.md](SOURCES.md).

## Reader and launch binding

`greekocr/readers/services/google_docai.py::DocAIReader` submits a single-page PNG, JPEG or TIFF through the Document AI REST `:process` endpoint. It hashes the actual image bytes, checks an optional expected SHA before making a call, and records the project, location, processor, processor version, quota project and OCR options in its binding. The CLI default version is `pretrained-ocr-v2.1-2024-08-07`; the low-level constructor permits `version=None`, which is explicitly an unpinned processor default. Do not infer a pinned version from that constructor alone.

The page-read family uses the saved T19 EU binding, normally with Greek hint and symbol output. `collect_v3/reader.py` is a separate paid-request adapter: its exact binding is `collect_v3/processor_binding.json`, with location `eu`, the same version, `enableSymbol=true`, and **empty language hints**. Cyrillic and mixed collections can therefore use automatic language detection; the Greek hint is not universal.

Supply credentials through the launch environment only: `GOOGLE_APPLICATION_CREDENTIALS` points to an ADC credentials file outside the repository. `DocAIReader._headers()` obtains ADC with the cloud-platform scope and the selected quota project; credentials are not a configuration payload or documentation artifact. The collector explicitly loads the environment-supplied file and also supports `COLLECT_V3_ACCESS_TOKEN` as an ephemeral environment alternative. `collect_v3/common.py` scrubs credential material; `reader.strip_response()` retains document text/geometry while removing embedded raster/content copies. This documentation run did not inspect credentials, contact a provider or launch a reader.

The reusable reader has **no automatic HTTP retries**. Its `read_batch()` concurrency is not a per-host rate limiter. Production collection must use the collection transport's limiter; merely setting reader concurrency to one does not establish one-second spacing.

## Receipts, reuse and cost

For `DocAIReader`, receipts are organized below `<receipts_dir>/<binding_sha256>/<image_sha256>-<version-or-default>/`. Each attempted response gets a UUID JSON file; successful reusable metadata goes in `cache.json`; `ledger.jsonl` records cache hits, successes and errors under a filesystem lock. Records bind raw-response SHA, image SHA, request/receipt IDs, latency, version/options, symbol confidence and billing state. Reuse verifies both the binding and saved raw-response hash. `fresh` bypasses reuse; it is a new potentially billable request. A transport failure can have unknown billing; the ledger retains that uncertainty.

`docai_manifest.py` freezes crop paths/hashes, `line_id`, cohort, explicit `gold_text` and separately labelled diagnostics. It supports `polytondb_gold300`, `o4d_lines`, `borndigital100`, and optional `o4d_sample400`. Exactly 300 gold-tier Polyton-DB rows are required. O4D layer/reader text is diagnostic; born-digital text becomes gold only through explicit `gold_text`. This is the crop-comparison interface, not the whole-book collector schema.

`docai_driver.py::run_manifest()` validates the manifest and worst-case budget before calls; writes `manifest.jsonl`, `predictions.jsonl`, the run-specific `ledger.jsonl`, `summary.json` and `REPORT.md`; and retains cumulative receipts under `receipts/`. Repeat passes bypass the cache. Strict comparison uses NFD without trimming or whitespace folding, and reader agreement is reported separately from supplied-gold accuracy.

The code's price constant is **USD 1.50/1,000 page units**. This is a recorded planning basis, not a current price lookup or invoice confirmation. Driver summaries distinguish successful page units, failed-billing-unknown units, cache hits, estimated cost and conservative attempted cost. Wave `cost_receipt.json` files record pre-request reservations, caps and reader counts. `collect_v3/ledger.py` instead uses SQLite WAL/FULL durability, one reservation per image SHA across tranches, and integer micro-USD accounting (1,500 per page). It commits before sending; an uncertain request without durable response is held for reconciliation, never automatically reread. Cached successful responses can be resumed without another paid request.

## Page-read scripts and source collectors

| Entry point | Scope and outputs |
|---|---|
| `scripts/harvest/page_reads.py` | T15 diagnostic: frozen 500 pilot lines grouped into 253 native pages, Vision/DocAI page-versus-crop comparison. `--prepare` binds/render-checks pages; `--run` makes the bounded paired reads; saved responses supply assignment, comparison and review artifacts under `docs/records/harvest/page_reads_v1/`. |
| `scripts/harvest/round1_reads.py` | T17 first three decades, 343 accepted pages. Frozen plans, paired Vision/DocAI reads, provider line layouts and anchored confidence; `build_round1_reads.py` constructs records and reviews. |
| `scripts/harvest/round1_reads_rest.py` | T19 remaining 1,189 pages, **DocAI only**. Rejects ambiguous historical attempts lacking parsed cache instead of silently rereading; `build_round1_reads_rest.py` preserves the earlier d1 fields and writes rest/all records, assignments, raw/cache inventories and receipts. |
| `scripts/harvest/compile_page_reads.py` | Offline review compiler: source-image SHA checks, one native-size page diptych per page, numbered boxes/text and `compile_receipt.json` with records/builder/font/raster hashes. It does not call OCR or apply training admission. |
| `scripts/harvest/vouli.py` | T21 local 1850s Vouli page rendering/gate, explicit DocAI reads and historical crop admission. |
| `scripts/harvest/parliament.py` + `greekocr/harvest/parliament*.py` | T23 public Parliament API, 1975–2000 proceedings, bounded PDF lifetime, page/source provenance, gate and saved-response reconstruction. |
| `scripts/harvest/openarchives.py` + `greekocr/harvest/openarchives.py` | T24c metadata-selected acquisitions, bounded one-PDF handling and page receipts. Its old bibliographic metadata must be read with O1/O2 corrections. |
| `scripts/harvest/mixed.py` + `greekocr/harvest/mixed.py` | T25 three parts: Anemi, repository material and IA/Latin material; distinct selection policies and provider receipts. |
| `scripts/harvest/cyrillic.py` + `greekocr/harvest/cyrillic.py` | T26 exact 13-item IA candidate scope, print/rights prerequisites, automatic-language DocAI, source-language gate. “Cyrillic” does not establish Russian orthography. |
| `scripts/harvest/wikisource.py` + `greekocr/harvest/wikisource.py` | T27 robots-aware discovery and saved transcription/scan processing. T27e imported 400 coordinator-supplied scan receipts; labels/alignment remain separate. |
| `scripts/harvest/round1.py`, `scripts/harvest/round2.py`, `scripts/harvest/_anemi_round1_fetcher.py` | Anemi selection, bounded page slots/replacements and internal page-PDF acquisition. The fetcher uses the O4c discovery/transport interface; it is not a generic public download service. |
| `collect_v3/run.py`, `runner.py`, `pipeline.py`, `routes/providers.py` | W1/W2 collector: IA JPEG, MDZ/BSB and NLG IIIF, OJS, official PDFs; frozen draws/exclusions, page responses, geometry and line-feature materialization. `storage.py`/`retention.py` retain reconstructable inputs and compact derivatives. |

Historical source scripts can enforce their original branch, source SHA, sibling-input and gate assumptions (for example `vouli.check_frozen()` requires `main`). They document reproducible historical runs; they are not unqualified launch commands for this integrated branch.

## Row custody and metadata contract

There are several schema generations; do not flatten them by discarding their original fields.

| Layer | Identity and evidence |
|---|---|
| Page response | Source item/book, source URL and acquisition receipt, PDF/page-image SHA and bytes, physical page index/volume position, render settings/native dimensions, raw-response path/SHA, reader binding and request/receipt ID. Page layouts, text anchors, tokens and symbols remain the transcription evidence. |
| T19 page line | `id=<page_id>-lNNNN`, `page_id`, `book`, `book_key`, `page`, year/decade/origin; provider-order `docai_index`, native `bbox`, page `image`/`image_sha256`; `docai_raw_text` versus stripped `docai_text`; `counted`, nullable `label`, confidence/minimum, anchored symbol indices/counts and flags. Three letters is the historical reporting count threshold, **not** the current content gate. |
| Crop/admitted wave row | Crop path and `crop_sha256`, crop box/source-page identity, source/licence/batch, script class, book split and provenance. Hash the encoded crop bytes, not a visually equivalent rerender. Keep page/book metadata through the manifest join when absent on a compact row. |
| collect-v3 feature | Stable `page_id` and line ID, `source`, `item`, sampled `page`, year, `bbox`, `crop_bbox`, crop path/SHA, `docai_line_index`, confidence; `old_label`, `fixed_label`, `rollback_label`, `token_drop_trace`, conventions and classifications. The raw response owns original Google text; assembled/convention labels are derived views. |
| Pipeline canonical row | `parent_id`, `id`, `source`, `book_id`, canonical `edition_id`, `page_id`, `split`, `raw_text`, `crop_sha256`, optional bound source/crop paths/coordinates and role. `line_pipeline_sources.py` records `raw_text_field`; defaults choose `old_label`, then `text`, then `label` for collect-v3, and `label` for v2. A v2 parent label can already contain historical cleaning; it must not be described as the unmodified provider response. |

Google symbol confidence belongs to line **text anchors**, not arbitrary overlapping boxes (`round1_reads.symbol_confidences`). `_response_geometry()` converts returned coordinates back to the native page frame and retains transformation evidence. Missing geometry is an explicit failure/hold boundary; a page transcription is not split by guesswork to fit crops.

## Collections and recorded denominators

| Collection | Recorded production or snapshot | Receipts/evidence |
|---|---|---|
| Round 1 d1 | 343 pages, 14,082 records; 13,283 counted; 7,801 original agreement labels. 343 DocAI + 343 Vision reservations, USD 1.029 combined estimate. | `docs/records/harvest/round1/reads_d1/{summary,receipt,cost_receipt}.json` |
| Round 1 rest / combined | Rest: 1,189 pages, 60,979 lines, USD 1.7835. Combined historical admission: 75,061 input lines, 1,532 pages, 130 books, 61,882 admitted crops. | `docs/records/harvest/round1/reads_rest/{summary,receipt,cost_receipt}.json`; `docs/records/harvest/round1/admission_summary.json` |
| Round 2 | 50 books fetched, 49 with accepted/read pages; 613 pages, 29,943 Google lines, 24,430 historical admitted crops; USD 0.9195. | `docs/records/harvest/round2/{READS.md,read_summary.json,admission_summary.json,cost_receipt.json}` |
| Collection v2 | **271,987** cleaned lines: train 214,436, dev 13,522, test 44,029. Derived from 293,439 pool-v1 rows, not additional observations to add to the source waves. | `docs/records/harvest/collection/v2/CLEAN_REPORT.md`, `manifest_v2_{train,dev,test}.json`; O2 metadata-only successor below. |
| collect-v3 frozen census parents | **W1 101,098 + W2 219,381 = 320,479** rows in `W{1,2}_features_20261018_0524.jsonl`; all initially unassigned. Later collector progress is not retroactively part of this snapshot. | `docs/records/harvest/seg_census/remote_evidence/config_receipt.json`, `census03_config.json`; `docs/records/harvest/collect_v3_admission/split1/input_verification.json` |
| Gazette, BSB and IA inside that snapshot | Gazette 148,547; BSB 33,090; IA poly1850 64,476, Greek–Latin 11,755, Russian 2,963. These are sums of raw snapshot source×class counts, **not** qualified training yields. | `docs/records/harvest/collect_v3_admission/split1/summary.json` |
| Earlier original-crop W2/Gazette admission | Gazette modern-scanned historical subset: 40,804 screened, 5,411 admitted; most losses included missing geometry. Historical BSB/IA strata have their own counts. All ADMW2/qualified-admission exports are superseded and parked. | `docs/records/harvest/collect_v3_admission/{w2_originals_v3_receipt.json,gazette_w2_originals_v3_receipt.json,HANDOFF_20261018_sourcing.md}` |

Snapshot W1 SHA: `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c`; W2 SHA: `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4`. Read the source receipt before substituting a later materialized file.

`docs/records/harvest/collect_v3/README.md` describes an offline W1d build (“nothing collected”), not the later live population. Conversely the sourcing handoff's BSB progress says 736/800 processed (729 read, 7 excluded), 64 deferred as of its 18 October update; SPLIT1 says 436 later BSB pages are outside the 05:24 snapshots and ten W2 BSB documents are partial. Neither is live status verified by this documentation run.

## Sourcing and review rules

Keep book/item identity and the sampled-book record, including zero-read or rejected-page outcomes; review **lines** against their crop and Google text. Do not replace books or redefine a denominator after seeing OCR output. Historical page eligibility and modern line filtering are different stages.

Use the shared per-host limiter at **≤1 request/second**, including redirects and credential-refresh HTTP hops where implemented. `collect_v3/transport.py::HostBucket` uses persistent POSIX locks across processes; honors deferred starts/Retry-After and host crawl delays; and enforces a conservative configurable MDZ rolling 24-hour image cap. This fallback cap is not a verified provider-issued live limit. Robots denial/unavailability and access control stop the relevant item/page and remain receipts; no bypass is part of the workflow. Public download retries in transport are bounded and distinct from the paid-reader no-retry rule.

Anemi is **internal training/evaluation only; never redistribute** (`_anemi_round1_fetcher.py`, `anemi-research-internal` wave metadata). Preserve per-item rights and separate scan rights from Wikisource contributor-text attribution. Availability, a successful read or a corrected title does not grant a new licence.

Vision, Transkribus and local readers are comparison/evidence tools, not alternate custody for Google page labels. Vision participated in T15/T17 comparison; rest and subsequent listed waves use DocAI. A comparison agreement is not human gold. The current line pipeline imports qualified result ledgers and exports pending queues; it does not launch any comparison reader implicitly.

## Verification boundary

Relevant offline tests are `tests/test_docai.py`, `test_page_reads.py`, `test_round1_reads.py`, `test_round1_reads_rest.py`, `test_compile_page_reads.py`, and `collect_v3/tests/`. They cover mocked service/ADC, image and receipt binding, text anchors/geometry, cache failures, raster compilation, resume, rate limiting and credential scrubbing. W1d's historical receipt reports 116 collector tests and 3,643-line/55-field replay parity with zero differences; this does not validate current collection totals or population OCR accuracy. No tests, OCR, collection or pipeline processing were executed for this document.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`; `docs/cleanup_20261019/PLAN.md`; `AGENTS.md`.
- `greekocr/readers/services/google_docai.py`; `docai_manifest.py`; `docai_driver.py` (same directory).
- `greekocr/harvest/readers.py`; `page_reads.py`; `round1_reads.py`; `line_pipeline_sources.py` (same directory).
- `scripts/harvest/page_reads.py`; `round1_reads.py`; `round1_reads_rest.py`; `build_round1_reads_rest.py`; `compile_page_reads.py`; `vouli.py`; `parliament.py`; `openarchives.py`; `mixed.py`; `cyrillic.py`; `wikisource.py`; `_anemi_round1_fetcher.py` (same directory).
- `greekocr/harvest/{parliament,openarchives,mixed,cyrillic,wikisource}.py` (source-policy sections).
- `collect_v3/{reader,pipeline,transport,ledger,config,common,exclusions}.py`; `collect_v3/routes/providers.py`; `collect_v3/processor_binding.json`.
- `docs/records/harvest/round1/reads_d1/{summary,receipt,cost_receipt}.json`; `docs/records/harvest/round1/reads_rest/{summary,receipt,cost_receipt}.json`; `docs/records/harvest/round1/admission_summary.json`.
- `docs/records/harvest/round2/{READS.md,read_summary.json,admission_summary.json,cost_receipt.json}`; `docs/records/harvest/wikisource/READS.md`.
- `docs/records/harvest/collection/v2/CLEAN_REPORT.md`; `docs/records/harvest/collect_v3/{README.md,KNOWN_ISSUES.md}`.
- `docs/records/harvest/collect_v3_admission/{w2_originals_v3_receipt.json,gazette_w2_originals_v3_receipt.json,HANDOFF_20261018_sourcing.md}`.
- `docs/records/harvest/collect_v3_admission/split1/{SPLIT_PROPOSAL.md,summary.json}`; `docs/records/harvest/seg_census/remote_evidence/{HANDOFF.md,census03_config.json}`.
- `tests/test_docai.py`; `tests/test_compile_page_reads.py` (test contracts).
