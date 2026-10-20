**Commercial and hosted OCR for independent Greek verification — 8 October 2026**

**Enable Google Document AI Enterprise Document OCR first**, pinned to `pretrained-ocr-v2.1-2024-08-07` in `eu`. It offers a practical route to text plus word/symbol confidence at a small sample cost. Its historical-polytonic accuracy is **unknown**: this is a recommendation for the first experiment, not a finding that it beats CLLG. Cloud Vision's explicit experimental Ancient Greek support does not transfer automatically to Document AI. [G1; checked 2026-10-08][G1], [G3; checked 2026-10-08][G3], [G4; checked 2026-10-08][G4], [V1; checked 2026-10-08][V1]

This report and the adjacent [JSON table](COMMERCIAL_OCR_20261008.json) cover 17 engine/deployment choices. All source checks and engineering assessments are dated **2026-10-08**. Dates attached to references mean **access/check date**, not publication; known publication/update dates appear in the source register. “Unknown” means the consulted sources did not settle the point. A language listing is not a polytonic accuracy guarantee; a vendor/model-card score is not a reproduced benchmark. Integration times, token budgets and prioritisation are estimates. No accounts, credentials, cloud billing or OCR endpoints were activated; no sample images were uploaded.

**What the workspace currently establishes**

- Recorded E2 result: CLLG 1.30% strict NFD CER and 0.992 pooled mark F1 on 300 real polytonic gold lines from Gazette/Appian; Parliament was excluded as Vouli-shared. This research did not rerun it. [R4; checked 2026-10-08][R4]
- Tesseract 4 grc at 33% CER is the research brief's stated baseline, not a new measurement. [R1; checked 2026-10-08][R1]
- Existing google/azure/mistral entries are gated service stubs requiring both environment configuration and an explicit factory. Their current read method returns NFD text only; confidence persistence is additional integration work. [R2; checked 2026-10-08][R2], [R8; checked 2026-10-08][R8]
- The 44-entry parliament fixture index contains layer and CLLG readings; owner_notes is empty and no separate human gold transcript field is present. Treat the user's owner-checked status as needing its authoritative transcript bound to these IDs. [R5; checked 2026-10-08][R5], [R6; checked 2026-10-08][R6]
- The current E2 bake-off is a 300-real + 300-synthetic procedure with selection/overlap gates. It is not already a 444-line, three-cohort hosted test command. [R3; checked 2026-10-08][R3]

The 300-line result is the incumbent comparison. The 44 parliament lines need their authoritative owner transcripts attached to the recorded IDs before they become a reproducible scored cohort. The 100 modern lines still need a frozen, human-checked manifest. A hosted reader must see pixels only, not the PDF text layer or another reader's proposed answer. These are test-design requirements, not new results. [R1; checked 2026-10-08][R1], [R3; checked 2026-10-08][R3], [R5; checked 2026-10-08][R5], [R6; checked 2026-10-08][R6]

**Ranked shortlist**

This ranks usefulness of the **next experiment**, balancing independence, confidence, setup and cost. Training-set independence remains unproven for proprietary models; vendor diversity is only a proxy.

| Rank | Reader | Reason to test / main uncertainty |
|---|---|---|
| 1 | Google Document AI Enterprise OCR | Versioned EU endpoint, word/symbol confidence, low sample cost; explicit polytonic support and accuracy unknown. [G1; checked 2026-10-08][G1], [G3; checked 2026-10-08][G3], [G4; checked 2026-10-08][G4], [G11; checked 2026-10-08][G11] |
| 2 | Google Cloud Vision Document Text Detection | Explicit experimental `grc`; word/symbol confidence. Same vendor as #1, so do not count their agreement as two independent votes. [V1; checked 2026-10-08][V1], [V6; checked 2026-10-08][V6] |
| 3 | Transkribus Greek 8.0, model 148525 | Strongest directly relevant public-model claim; tariff/API/confidence and training-book overlap unresolved. [TR1; checked 2026-10-08][TR1], [TR2; checked 2026-10-08][TR2], [TR4; checked 2026-10-08][TR4], [TR5; checked 2026-10-08][TR5], [TR8; checked 2026-10-08][TR8] |
| 4 | Mistral OCR 4.1 | Independent vendor, word scores, easy image API; verify marks, Markdown extraction and privacy settings. [M1; checked 2026-10-08][M1], [M3; checked 2026-10-08][M3], [M8; checked 2026-10-08][M8], [M10; checked 2026-10-08][M10] |
| 5 | Azure prebuilt Read | Cheap independent vendor baseline for modern/mixed pages; no explicit ancient support found. [A1; checked 2026-10-08][A1], [A2; checked 2026-10-08][A2], [A4; checked 2026-10-08][A4] |
| 6 | Gemini 2.5 Pro; Flash as cheaper paired probe | Some historical-document evidence for Pro, but no native optical char/word confidence; exploratory adjudication only. [P2; checked 2026-10-08][P2], [L1; checked 2026-10-08][L1], [L2; checked 2026-10-08][L2] |

ABBYY Engine/Vantage need product-specific confirmation and commercial access. Textract lacks Greek support. The closed ABBYY Cloud OCR SDK is not a candidate. Hosted CLLG is the same reader; Logios/Kalchas has a known Polyton-DB independence problem. Typorama may help with specialist or human verification, but is not a verified line OCR API. [B1; checked 2026-10-08][B1], [B5; checked 2026-10-08][B5], [B6; checked 2026-10-08][B6], [T1; checked 2026-10-08][T1], [R4; checked 2026-10-08][R4], [H1; checked 2026-10-08][H1], [H3; checked 2026-10-08][H3]

**Cost units and comparison**

For page-billed OCR, **1,000 individually submitted line crops are 1,000 images/pages**, not 1,000 divided by a guessed number of lines per page. Sending full pages may amortise cost, but changes segmentation, context and the experiment. Prices below exclude tax and optional features unless stated. Do not assume unused free quota.

| Reader | Per 1,000 page images | Per 1,000 separate line images | Basis |
|---|---:|---:|---|
| Document AI | USD 1.50 | USD 1.50 | Paid small-volume tier; free quota discussed below. [G4; checked 2026-10-08][G4] |
| Cloud Vision | USD 1.50 | USD 1.50 | One OCR feature only. [V2; checked 2026-10-08][V2] |
| Azure Read | USD 1.50 | USD 1.50 | West Europe S0 retail meter. [A4; checked 2026-10-08][A4] |
| Mistral OCR 4.1 | USD 4.00 | USD 4.00, subject to image-unit smoke test | Eligible batch USD 2.00; no annotation add-on. [M1; checked 2026-10-08][M1], [M6; checked 2026-10-08][M6] |
| Textract | USD 1.50 | USD 1.50 | Oregon illustration, not verified EU quote; no Greek. [T1; checked 2026-10-08][T1], [T2; checked 2026-10-08][T2] |
| Transkribus Greek 8.0 | EUR 59.50–119 conditional | Same conditional range | API recognition credits only; unresolved old/current tariffs, subscription/layout extra. [TR4; checked 2026-10-08][TR4], [TR6; checked 2026-10-08][TR6], [TR11; checked 2026-10-08][TR11] |
| ABBYY Engine / Vantage | Unknown | Unknown | Current quote and licence required. [B4; checked 2026-10-08][B4], [B8; checked 2026-10-08][B8] |
| Hosted eScriptorium / Logios / Typorama | Unknown | Unknown | Operator/access/project dependent. [E1; checked 2026-10-08][E1], [H1; checked 2026-10-08][H1], [H3; checked 2026-10-08][H3] |

**Provider details**

All latency entries are unmeasured for our images. Published quotas do not imply a per-line latency guarantee. A confidence number is not a calibrated probability of a correct Greek diacritic.

**Google Document AI — Enterprise Document OCR**

- **Coverage.** **Model:** OCR_PROCESSOR; pin pretrained-ocr-v2.1-2024-08-07, stable GA, in eu. Do not assume preview versions are available in EU. **Ancient/polytonic:** Unknown: explicit ancient/polytonic support not found in this processor's list. Cloud Vision's grc listing is a different product. **Modern Greek:** Greek el is listed. **Mixed scripts:** Greek, Latin and Cyrillic languages are listed; accuracy on mixed historical lines is unmeasured. [G1; checked 2026-10-08][G1], [G11; checked 2026-10-08][G11], [V1; checked 2026-10-08][V1]
- **Interface.** **Input:** Raster line crops or page images; PDFs also accepted. Use PNG and disable native PDF parsing for independent visual verification. **Confidence:** Token/word and symbol Layout.confidence, 0–1; enableSymbol=true. Symbol confidence is not separately calibrated for every NFD combining mark. **Output:** JSON Document.text with text anchors, reading order, blocks/paragraphs/lines/tokens/symbols and polygons. [G2; checked 2026-10-08][G2], [G3; checked 2026-10-08][G3]
- **Cost and access.** **Price:** USD 1.50/1,000 paid pages at the small-volume tier; same for 1,000 separately submitted line images. Excludes optional OCR add-ons, storage and tax. **Free/trial:** Live pricing table lists first 1,000 pages/month free. Existing account consumption/eligibility not checked. [G4; checked 2026-10-08][G4]
- **Operation.** **Limits:** EU/US default 120 online requests/minute/project/processor type. Sync: 40 MB, 15 pages (30 with imageless mode); one crop is comfortably below page limits. **Latency:** Online synchronous endpoint; per-line p50/p95 and actual throughput unknown. Quota is not a latency promise. **Repeatability:** Version pin is available; bit-identical output is not guaranteed in consulted documentation. Measure two calls. [G6; checked 2026-10-08][G6], [G7; checked 2026-10-08][G7], [G1; checked 2026-10-08][G1]
- **Data handling.** **Training/retention:** Customer documents are not used to train models. Synchronous processing is in memory; batch temporary copies have a one-day failsafe deletion. Metadata logging and customer storage are separate. **EU:** Create eu processor and use eu-documentai.googleapis.com. Confirm chosen version's regional availability. [G5; checked 2026-10-08][G5], [G8; checked 2026-10-08][G8], [G11; checked 2026-10-08][G11]
- **Evidence and fit.** **Accuracy evidence:** No independent historical Greek CER benchmark found for this processor in the consulted sources; our 300/44/100 evaluation remains necessary. **Harness effort:** Estimated 3–5 hours after access: existing google service slot, but explicit module:factory adapter is missing; text-only read contract also needs raw confidence capture. Add regional/version-bound request, anchors and error accounting. [G1; checked 2026-10-08][G1], [P1; checked 2026-10-08][P1], [P2; checked 2026-10-08][P2], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Google Cloud Vision — DOCUMENT_TEXT_DETECTION**

- **Coverage.** **Model:** DOCUMENT_TEXT_DETECTION; current service backend. A frozen dated OCR-weight version was not established. **Ancient/polytonic:** Ancient Greek grc explicitly listed as experimental, with no regular evaluation guarantee. This is a support signal, not evidence of accurate polytonic marks. **Modern Greek:** Greek el listed as supported. **Mixed scripts:** Multiple languages in one image; Greek/Latin/Cyrillic listed. DOCUMENT_TEXT_DETECTION autodetects the full language set. [V1; checked 2026-10-08][V1], [V3; checked 2026-10-08][V3]
- **Interface.** **Input:** Image line crops or pages; document/PDF workflows also available. Start with identical PNG crops. **Confidence:** Word and symbol confidence 0–1 in fullTextAnnotation; symbol-level is not necessarily separate per-combining-mark confidence. **Output:** JSON full text, page/block/paragraph/word/symbol hierarchy, boxes and detected breaks; symbol sequence follows reading order. [V3; checked 2026-10-08][V3], [V6; checked 2026-10-08][V6]
- **Cost and access.** **Price:** USD 1.50/1,000 charged TEXT_DETECTION or DOCUMENT_TEXT_DETECTION units at small volume; 1,000 separate lines cost the same as 1,000 page images. Request only one OCR feature. **Free/trial:** First 1,000 units/month free; availability depends on account usage. [V2; checked 2026-10-08][V2]
- **Operation.** **Limits:** Default 1,800 requests/minute and 1,800 text-detection images/minute; up to 16 images in a synchronous request. Image limit 20 MB; JSON request 10 MB. **Latency:** Synchronous image API; small-line p50/p95 unknown. **Repeatability:** No bit-identical or immutable OCR-weight guarantee established; repeat requests and record date, endpoint and returned metadata. [V5; checked 2026-10-08][V5], [V3; checked 2026-10-08][V3]
- **Data handling.** **Training/retention:** Content is not used for training. Online images are processed in memory, not persisted to disk. Async copies have failsafe cleanup after a few hours; metadata logging is separate. **EU:** EU OCR endpoint eu-vision.googleapis.com and regional requests are documented; default global endpoint is not equivalent. [V4; checked 2026-10-08][V4], [V3; checked 2026-10-08][V3]
- **Evidence and fit.** **Accuracy evidence:** Explicit experimental grc support, but no comparable strict-NFD historical Greek CER found. **Harness effort:** Estimated 3–5 hours: new service identity/configuration entry and adapter; extract fullTextAnnotation plus word/symbol spans. Not the existing google Document AI adapter. [V1; checked 2026-10-08][V1], [P1; checked 2026-10-08][P1], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Transkribus — 19th-century Greek 8.0 (148525)**

- **Coverage.** **Model:** Public PyLaia model 148525, published 2024-08-08. Noscemus GM6 is a secondary public model for historical Latin print containing Greek passages. **Ancient/polytonic:** Greek/Ancient Greek explicitly listed. Legacy description says all diacritics retained but normalizes some historical ligatures; current model-page metadata conflicts with legacy training-page count. **Modern Greek:** Model tagged Greek and intended for nineteenth-/twentieth-century print; modern born-digital performance unknown. **Mixed scripts:** Greek model's Latin/Cyrillic coverage unknown. Noscemus is relevant to Latin/Greek pages; Cyrillic suitability not established. [TR1; checked 2026-10-08][TR1], [TR3; checked 2026-10-08][TR3], [TR2; checked 2026-10-08][TR2]
- **Interface.** **Input:** Beta API accepts one JPEG/PNG/TIFF image per request, up to 20 MB. Crop-as-page is an integration hypothesis to smoke-test; layout/line detection may be needed. **Confidence:** Recognition API guide does not establish per-character or per-word confidence availability for model 148525. Inspect actual PAGE/JSON before promising the required interface. **Output:** Async PAGE XML or JSON, with regions/lines, baselines, ordering and words where available; result download retained for 24 hours. [TR5; checked 2026-10-08][TR5], [TR7; checked 2026-10-08][TR7], [TR8; checked 2026-10-08][TR8]
- **Cost and access.** **Price:** Current web rate says recognition 1 credit/page; developer API is 50% of web credits. At EUR 59.50/250 purchased credits, 1,000 images imply EUR 119 marginal recognition; older printed-text tariff implies EUR 59.50 instead. Unresolved EUR 59.50–119 range, plus layout, subscription and pack rounding; same for 1,000 line images. **Free/trial:** Web Free: 50 credits/month. Scholar: EUR 99/year with 900 credits/year (display includes 20% Austrian VAT). API docs say Scholar or higher; pricing page says Organisation/Scholar coming soon. Do not assume free API access. [TR4; checked 2026-10-08][TR4], [TR6; checked 2026-10-08][TR6], [TR11; checked 2026-10-08][TR11], [TR5; checked 2026-10-08][TR5]
- **Operation.** **Limits:** Fair-use throttling and HTTP 429; numeric TPS not published in consulted beta guide. Terms §10.1(d) restrict infrastructure benchmarks/capacity tests; obtain clarification before throughput/load benchmarking. **Latency:** Queued asynchronous processing; per-line latency/queue delay unknown. Not a one-call synchronous OCR endpoint. **Repeatability:** Pin htrId=148525 and language-model/layout settings. Bit-identical API responses unverified. [TR7; checked 2026-10-08][TR7], [TR10; checked 2026-10-08][TR10], [TR5; checked 2026-10-08][TR5], [TR8; checked 2026-10-08][TR8]
- **Data handling.** **Training/retention:** Terms say API input images are deleted after processing; results last 24 hours. Service-improvement licence and retained backups/nonpersonal material mean no blanket no-training/instant-erasure promise; general opt-out unknown. **EU:** Terms identify processing/storage in Austria and Germany. [TR10; checked 2026-10-08][TR10], [TR5; checked 2026-10-08][TR5]
- **Evidence and fit.** **Accuracy evidence:** Model card claims 0.93% validation CER, 24,836 lines/187,561 words; live page says 413 training pages, legacy description 894. Not our gold split or NFD protocol; book-level overlap and normalization must be checked. **Harness effort:** Estimated 4–8 hours after access: new engine entry, OIDC bearer token, job submit/poll/download, PAGE/JSON parser and confidence discovery. Developer auth uses processing-api-client. Account and tariff uncertainty may exceed one day. [TR1; checked 2026-10-08][TR1], [TR2; checked 2026-10-08][TR2], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8], [TR9; checked 2026-10-08][TR9]

**Mistral OCR 4.1**

- **Coverage.** **Model:** Use GA mistral-ocr-4-1, not latest alias or retired OCR 4.0. GA announced 2026-08-31. **Ancient/polytonic:** No explicit ancient/polytonic guarantee found; Greek language listing does not establish historical diacritic fidelity. **Modern Greek:** Greek is listed. **Mixed scripts:** Greek, Latin and Cyrillic languages are listed; mixed-line accuracy remains unmeasured. [M1; checked 2026-10-08][M1], [M2; checked 2026-10-08][M2], [M5; checked 2026-10-08][M5]
- **Interface.** **Input:** image_url supports image URLs/base64; document_url supports page documents. A line PNG can be submitted as one image. **Confidence:** Current API supports confidence_scores_granularity='word', including word scores and page aggregates. No character confidence documented. **Output:** JSON pages with Markdown text; include_blocks supplies paragraph/block boxes and labels in reading order. Do not assume every word score has a matching word box. [M3; checked 2026-10-08][M3], [M4; checked 2026-10-08][M4]
- **Cost and access.** **Price:** OCR 4.1: USD 4/1,000 pages; USD 2 via eligible batch discount. Separately submitted line images have the same assumed unit count; verify usage_info in smoke test. Annotations cost extra. **Free/trial:** A usable OCR-specific free allowance was not verified; do not budget promotional credits. [M1; checked 2026-10-08][M1], [M6; checked 2026-10-08][M6], [M7; checked 2026-10-08][M7]
- **Operation.** **Limits:** Limits depend on model and organisation tier; console shows RPS/TPM. Uploaded files up to 512 MB. No universal OCR lines/second allowance verified. **Latency:** Sync OCR available; measured line latency and a Greek-specific latency SLA unknown. Batch discount trades against completion time. **Repeatability:** No OCR seed/temperature control or identical-response guarantee established in current schema; repeat same image/model. [M7; checked 2026-10-08][M7], [M4; checked 2026-10-08][M4], [M6; checked 2026-10-08][M6]
- **Data handling.** **Training/retention:** Explicitly disable training use in Studio privacy controls; do not infer default no-training from PAYG. Approved ZDR covers stateless /v1/ocr, not files/batch; separate opt-out is still needed. Uploaded files otherwise last up to 30 days; standard request-content TTL unknown. **EU:** Documentation says EU data centres by default; bind deployment/account and DPA before relying on that for a specific workload. [M8; checked 2026-10-08][M8], [M9; checked 2026-10-08][M9], [M10; checked 2026-10-08][M10], [M7; checked 2026-10-08][M7]
- **Evidence and fit.** **Accuracy evidence:** Vendor multilingual results include Greek, but no comparable independent historical-polytonic strict-NFD CER found. **Harness effort:** Estimated 2–4 hours: existing mistral slot still needs a factory, image/base64 request, word-score capture and a fixed Markdown-to-transcript policy. Avoid annotation prompts that rewrite text. [M6; checked 2026-10-08][M6], [P1; checked 2026-10-08][P1], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Azure AI Document Intelligence — prebuilt Read**

- **Coverage.** **Model:** prebuilt-read, API 2024-11-30 (v4.0). API version is not proof of immutable recognition weights. **Ancient/polytonic:** No explicit ancient/polytonic entry found. **Modern Greek:** Greek el is listed. **Mixed scripts:** Multilingual Greek/Latin/Cyrillic coverage; mixed historical accuracy not measured. [A2; checked 2026-10-08][A2], [A1; checked 2026-10-08][A1]
- **Interface.** **Input:** Page documents or raster images, including line crops subject to image limits. Rasterize born-digital input to avoid comparing embedded-text extraction. **Confidence:** Per-word confidence 0–1; no per-character OCR confidence established. **Output:** JSON content, pages, lines, words, spans and polygons; preserve service sequence/offsets rather than sorting boxes by x alone. [A2; checked 2026-10-08][A2]
- **Cost and access.** **Price:** West Europe official retail API: S0 Read Pages USD 1.50/1,000 pages at base tier. One independent line-image request is one page for this comparison. **Free/trial:** F0 allows 500 pages/month; account availability unverified. Insufficient for 888 calls without a second month or paid usage. [A4; checked 2026-10-08][A4], [A3; checked 2026-10-08][A3]
- **Operation.** **Limits:** S0 default 15 analyze requests/second, 50 result GETs/second; F0 1/second. F0 4 MB/two pages; S0 500 MB/2,000 pages. **Latency:** Asynchronous analyze/poll API; actual p50/p95 and polling overhead unknown. **Repeatability:** No identical-output guarantee established. Pin API version and repeat calls, logging model metadata. [A5; checked 2026-10-08][A5], [A2; checked 2026-10-08][A2]
- **Data handling.** **Training/retention:** Analysis input/results retained up to 24 hours; DeleteAnalyzeResult permits earlier deletion. Consulted product privacy page does not by itself establish a blanket training opt-out/default clause; confirm applicable Microsoft DPA, rather than treating absence as permission. **EU:** Processing/storage follow the resource region; create West Europe or another supported EU resource. [A6; checked 2026-10-08][A6]
- **Evidence and fit.** **Accuracy evidence:** No comparable published historical Greek CER found in the consulted language/product sources. **Harness effort:** Estimated 2–4 hours: existing azure slot needs an explicit factory, analyze/poll/delete lifecycle, word spans/confidence and page-bound error handling. [A1; checked 2026-10-08][A1], [A2; checked 2026-10-08][A2], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Amazon Textract — DetectDocumentText**

- **Coverage.** **Model:** DetectDocumentText; unsuitable language coverage for this task. **Ancient/polytonic:** Unsupported: Greek is absent from the six supported languages. **Modern Greek:** Unsupported. **Mixed scripts:** English, French, German, Italian, Portuguese and Spanish only; no Greek/Cyrillic support. [T1; checked 2026-10-08][T1]
- **Interface.** **Input:** JPEG/PNG/PDF/TIFF; a line image is possible. Synchronous processing: 10 MB, single-page PDF/TIFF. **Confidence:** Word/line Block confidence on 0–100 scale; no character scores. **Output:** JSON words/lines, polygons and relationships. General page reading order may require Layout features beyond plain DetectDocumentText. [T1; checked 2026-10-08][T1], [T4; checked 2026-10-08][T4]
- **Cost and access.** **Price:** Oregon example: USD 1.50/1,000 pages below 1 million/month; same arithmetic for 1,000 line images. EU region price must be checked separately. **Free/trial:** Pricing advertises free-tier access; current account-specific allowance and eligibility not established here. [T2; checked 2026-10-08][T2]
- **Operation.** **Limits:** API and region-specific quotas; account TPS not checked. Do not extrapolate another region's quota. **Latency:** Sync/async APIs exist; Greek workload latency unmeasured and not worth qualification while Greek is unsupported. **Repeatability:** No identical-result guarantee established; model-version metadata should be recorded if ever tested. [T5; checked 2026-10-08][T5], [T1; checked 2026-10-08][T1], [T4; checked 2026-10-08][T4]
- **Data handling.** **Training/retention:** AWS may use content for service improvement; opt out with the AWS Organizations AI-services policy. Without opt-out, improvement copies may cross regions. General deletion requires support; exact content TTL unknown. **EU:** EU regions are available, but choose one and apply the improvement opt-out; region choice alone does not settle secondary use. [T3; checked 2026-10-08][T3]
- **Evidence and fit.** **Accuracy evidence:** No relevant supported-Greek accuracy claim. **Harness effort:** Estimated 2–4 hours for a new AWS adapter/entry, IAM setup and block parsing, but not justified for this Greek bake-off. [T1; checked 2026-10-08][T1], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**ABBYY FineReader Engine 12 SDK**

- **Coverage.** **Model:** Licensed SDK, distinct from FineReader desktop, retired Cloud OCR SDK and Vantage. **Ancient/polytonic:** Unknown: Engine language enumeration lists Greek, but an explicit Greek (ancient)/polytonic language was not verified. Require exact SKU/version/language ID and raw test output. **Modern Greek:** Greek is explicitly listed. **Mixed scripts:** Greek, Latin and Cyrillic script recognition documented; polytonic combination fidelity unmeasured. [B1; checked 2026-10-08][B1], [B4; checked 2026-10-08][B4], [B5; checked 2026-10-08][B5]
- **Interface.** **Input:** SDK image/document processing; line crops feasible with recognition-region configuration. Not a hosted REST reader out of the box. **Confidence:** Character confidence and recognition hypotheses exposed. ABBYY cautions that variant confidence is not a general calibrated recognition-quality probability; word-confidence semantics need SDK validation. **Output:** SDK text/layout exports; exact boxes, reading-order and char-to-export alignment depend on selected API/export format. [B4; checked 2026-10-08][B4], [B2; checked 2026-10-08][B2], [B3; checked 2026-10-08][B3]
- **Cost and access.** **Price:** Current SDK licence/deployment quote required; no verified USD/EUR per 1,000 pages or lines. **Free/trial:** No current free production allowance verified; request evaluation licence terms. [B4; checked 2026-10-08][B4]
- **Operation.** **Limits:** Licence, runtime and deployment dependent; no universal hosted TPS. **Latency:** Unknown until licensed SDK is run on the target host. **Repeatability:** Pin SDK build, language resources and recognition options; repeatability must still be measured. [B4; checked 2026-10-08][B4], [B1; checked 2026-10-08][B1]
- **Data handling.** **Training/retention:** Local SDK processing can keep documents on the chosen host. Licensing telemetry, support uploads, training use and retention are contract/configuration questions, not a universal cloud policy. **EU:** Achievable through an EU-controlled deployment; this does not establish an ABBYY-hosted EU service. [B4; checked 2026-10-08][B4]
- **Evidence and fit.** **Accuracy evidence:** No comparable historical-polytonic Greek CER found in the reviewed vendor specifications. **Harness effort:** Estimated 1–3 engineering days after licensing/runtime access, plus deployment work; platform binding and confidence alignment are more substantial than a REST factory. [B1; checked 2026-10-08][B1], [B4; checked 2026-10-08][B4], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**ABBYY Cloud OCR SDK (retired)**

New customer registration ended 2023-01-01; service shutdown 2024-08-30, per ABBYY support notice updated 2025-09-04. [B5; checked 2026-10-08][B5] All current procurement fields—input, output, confidence, pricing, quota, latency, residency and integration—are not applicable to a new deployment. Do not transfer old SDK prices or Ancient Greek claims to Vantage.

**ABBYY Vantage**

- **Coverage.** **Model:** Current successor candidate, with tenant/skill/API-version qualification required; public v1 docs are legacy evidence. **Ancient/polytonic:** Explicit Ancient Greek/polytonic support not verified. **Modern Greek:** Greek appears in an ABBYY-hosted partner specification; confirm current OCR skill/language selection before relying on it. **Mixed scripts:** Partner language specification covers Greek/Latin/Cyrillic; exact mixed-script skill behaviour unknown. [B5; checked 2026-10-08][B5], [B7; checked 2026-10-08][B7], [B8; checked 2026-10-08][B8], [B6; checked 2026-10-08][B6]
- **Interface.** **Input:** Document transaction API; crop-as-page and minimum image requirements need a tenant smoke test. **Confidence:** OCR confidence granularity not established for current output. Extracted-field confidence is not word/char OCR confidence; legacy schema even marks one confidence property unimplemented. **Output:** Legacy docs describe JSON/OCR output formats and transaction results; verify raw text, boxes and reading order in the current OCR skill. [B8; checked 2026-10-08][B8], [B9; checked 2026-10-08][B9], [B7; checked 2026-10-08][B7]
- **Cost and access.** **Price:** Quote required; current cost per 1,000 pages/line images and minimum commitment unknown. **Free/trial:** Current trial credits/free production tier not verified. [B7; checked 2026-10-08][B7], [B8; checked 2026-10-08][B8]
- **Operation.** **Limits:** Tenant/licence and API quotas unknown. **Latency:** Asynchronous transactions; no measured crop latency or public applicable SLA established. **Repeatability:** Version/skill pinning and repeated-result behaviour need contract/tenant verification. [B8; checked 2026-10-08][B8]
- **Data handling.** **Training/retention:** Archived 2023 terms mention 14-day transactions, but that is not a current retention commitment. Current training use, opt-out, deletion and logging terms remain unknown. **EU:** Legacy docs expose vantage-eu.abbyy.com; obtain a specifically EU tenant and current processing/subprocessor commitment. [B10; checked 2026-10-08][B10], [B8; checked 2026-10-08][B8]
- **Evidence and fit.** **Accuracy evidence:** No comparable public historical Greek benchmark verified. **Harness effort:** Estimated 4–8 hours after tenant/skill access for OAuth, transactions and export parsing; confidence discovery and commercial onboarding may take longer. [B6; checked 2026-10-08][B6], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Hosted eScriptorium / Kraken**

- **Coverage.** **Model:** eScriptorium is a platform used by separate institutional/community hosts, not one uniform paid OCR service. A D4Science hosted instance is publicly visible; access entitlement was not tested. **Ancient/polytonic:** Depends entirely on installed recognition model. Hosting CLLG again would reproduce the current model rather than add an independent reader. **Modern Greek:** Model dependent; platform support is not a Greek accuracy claim. **Mixed scripts:** Model/codec dependent, including Cyrillic; verify installed weights and character inventory. [E1; checked 2026-10-08][E1], [E2; checked 2026-10-08][E2], [R4; checked 2026-10-08][R4], [E3; checked 2026-10-08][E3]
- **Interface.** **Input:** Page workflow with segmentation and recognition; crop-as-page is feasible but host/API compatibility must be checked. **Confidence:** Local native Kraken adapter exposes character scores; whether a particular hosted API/export preserves them is unknown. No universal hosted word-confidence contract. **Output:** Text/layout annotation workflow with export; exact PAGE/ALTO/JSON export and confidence fields must be inspected on the selected deployment. [E3; checked 2026-10-08][E3], [R7; checked 2026-10-08][R7], [E2; checked 2026-10-08][E2]
- **Cost and access.** **Price:** No universal price/1,000 pages or lines. Open-source software does not imply free hosted compute; institutional quota or operator quote needed. **Free/trial:** Host-specific eligibility/access; none verified for this user. [E1; checked 2026-10-08][E1], [E2; checked 2026-10-08][E2]
- **Operation.** **Limits:** Host queue, hardware and policy dependent; no verified quota. **Latency:** Unknown; model, segmentation, accelerator and queue dependent. **Repeatability:** Can potentially bind exact model/runtime hashes; only if host exposes them. Repeatability remains a measurement. [E1; checked 2026-10-08][E1], [E2; checked 2026-10-08][E2], [E3; checked 2026-10-08][E3], [R7; checked 2026-10-08][R7]
- **Data handling.** **Training/retention:** Training use, opt-out, document visibility, retention and deletion are operator-specific; no universal eScriptorium policy established. **EU:** Unknown for the selected workload until operator infrastructure/terms are confirmed; an EU institution's domain alone is insufficient. [E1; checked 2026-10-08][E1], [E2; checked 2026-10-08][E2]
- **Evidence and fit.** **Accuracy evidence:** Published historical Greek/Latin work supports specialist Kraken models, but it does not certify a particular hosted instance or prove independence from CLLG. **Harness effort:** Estimated 1–2 days after access: host-specific token auth, upload/segmentation/recognition/export workflow and model/hash discovery; new service entry. [P3; checked 2026-10-08][P3], [R4; checked 2026-10-08][R4], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Logios / Kalchas (Greek academic lead)**

- **Coverage.** **Model:** Logios is described in a 2025 paper; Kalchas is the associated open-source recognition family. A currently provisioned public hosted API was not verified. **Ancient/polytonic:** Kalchas explicitly targets polytonic Greek line recognition. **Modern Greek:** Greek focus documented, but modern born-digital sample accuracy not established. **Mixed scripts:** Exact Latin/Cyrillic coverage is model/codec dependent and unverified here. [H1; checked 2026-10-08][H1], [H2; checked 2026-10-08][H2]
- **Interface.** **Input:** Kalchas expects segmented horizontal line images; it is not itself a complete page OCR pipeline. **Confidence:** Current hosted word/character confidence interface not verified; local reader currently returns text. **Output:** Local line text established; hosted boxes, reading order and formats unknown. [H2; checked 2026-10-08][H2], [R2; checked 2026-10-08][R2], [H1; checked 2026-10-08][H1]
- **Cost and access.** **Price:** Current hosted price/1,000 pages or lines unknown; an academic paper is not a commercial offer. **Free/trial:** Hosted quota/access not verified. [H1; checked 2026-10-08][H1]
- **Operation.** **Limits:** Hosted rate limits unknown. **Latency:** Hosted latency unknown. **Repeatability:** Local revision/weights can be pinned; hosted version/control unknown. [H1; checked 2026-10-08][H1], [R2; checked 2026-10-08][R2], [H2; checked 2026-10-08][H2]
- **Data handling.** **Training/retention:** Hosted training use, opt-out and retention terms not verified. **EU:** Unknown; Greek academic affiliation alone does not prove EU-hosted processing. [H1; checked 2026-10-08][H1]
- **Evidence and fit.** **Accuracy evidence:** Local E2 notes identify Polyton-DB overlap/memorization for Kalchas; its near-zero score on that cohort is not independent verification. **Harness effort:** Local Kalchas path already exists, but a Logios hosted API requires discovery and an adapter. Effort cannot be bounded without an API contract. [R4; checked 2026-10-08][R4], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Realiscape / Typorama (Greek industry service)**

- **Coverage.** **Model:** Managed OCR/digitisation service; underlying engine/version and API availability undisclosed in consulted page. **Ancient/polytonic:** Vendor explicitly offers old-style/polytonic Greek OCR. **Modern Greek:** Modern monotonic Greek service offered. **Mixed scripts:** Latin/Cyrillic capabilities for the proposed job not verified. [H3; checked 2026-10-08][H3]
- **Interface.** **Input:** Scan/document service; raw line-image API acceptance unknown. **Confidence:** No public character/word confidence interface verified. **Output:** Machine-only text versus human-corrected deliverables, boxes and reading order need a written specification. [H3; checked 2026-10-08][H3]
- **Cost and access.** **Price:** Quote required; price/1,000 pages and 1,000 separate lines unknown. **Free/trial:** No published free API tier verified. [H3; checked 2026-10-08][H3]
- **Operation.** **Limits:** No public API rate limit verified. **Latency:** Project turnaround, not an established API latency; unknown for small samples. **Repeatability:** Unknown; human intervention and proprietary engine changes may affect repeatability. [H3; checked 2026-10-08][H3]
- **Data handling.** **Training/retention:** Training use, subcontractors, opt-out and deletion/retention terms require a project agreement. **EU:** Execution/storage location unverified; Greek business presence is insufficient evidence. [H3; checked 2026-10-08][H3]
- **Evidence and fit.** **Accuracy evidence:** Vendor advertises over 99.5% accuracy; no disclosed matched gold set, strict-NFD protocol, or separation from human correction. Not comparable to 1.3% CLLG CER. **Harness effort:** No bounded adapter estimate without an API. Could supply separately labelled human-reviewed reference text under a managed service agreement. [H3; checked 2026-10-08][H3], [R4; checked 2026-10-08][R4], [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]

**Vision LLMs: shared limits and model-specific costs**

- **Input.** Image crops or page images are usable through vision APIs. Exact resize/tokenization varies by model; preserve image bytes and record billed image/input tokens. [L2; checked 2026-10-08][L2], [O3; checked 2026-10-08][O3], [C2; checked 2026-10-08][C2]
- **Confidence.** No calibrated OCR character/word confidence interface established for these vision models. Generated certainty, token log-probabilities and structured JSON are not optical confidence. [L2; checked 2026-10-08][L2], [O3; checked 2026-10-08][O3], [C2; checked 2026-10-08][C2]
- **Output.** Text or prompted JSON; boxes and reading order generated by a language model require validation. Do not treat invented coordinates as native OCR geometry. [L2; checked 2026-10-08][L2], [O3; checked 2026-10-08][O3], [C2; checked 2026-10-08][C2]
- **Determinism.** Fix model snapshot where offered, prompt, image and decoding controls. Temperature zero, if supported, is an experimental setting, not a proof of deterministic OCR; two-call consistency is an empirical metric. [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2], [P1; checked 2026-10-08][P1]
- **Greek/script coverage.** No explicit accuracy guarantee for ancient/polytonic print was found for these selected models. Modern Greek and Greek/Latin/Cyrillic transcription must be tested; general multilingual ability is not a marks benchmark. [L2; checked 2026-10-08][L2], [O3; checked 2026-10-08][O3], [C2; checked 2026-10-08][C2]
- **Latency.** All selected vision-model p50/p95 line latencies are unknown for this workload; output/reasoning token volume and provider scheduling matter. [L1; checked 2026-10-08][L1], [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2], [C1; checked 2026-10-08][C1]
- **Cost scenario.** Illustrative, not measured: a line call uses 1,000 billable input tokens plus 150 output tokens; a page call 3,000 plus 1,500. Cost/1,000 calls=(Tin*input_USD_per_million+Tout*output_USD_per_million)/1,000. Include prompt/image and any billed reasoning tokens; no caching/batch discount assumed. [L1; checked 2026-10-08][L1], [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2], [C1; checked 2026-10-08][C1]

| Model | Input / output USD per million tokens | Illustrative USD / 1,000 page calls | Illustrative USD / 1,000 line calls |
|---|---:|---:|---:|
| Gemini 2.5 Pro (vision) [L1; checked 2026-10-08][L1] | 1.25 / 10 | 18.750 | 2.750 |
| Gemini 2.5 Flash (vision) [L1; checked 2026-10-08][L1] | 0.3 / 2.5 | 4.650 | 0.675 |
| GPT-5.2 (vision) [O1; checked 2026-10-08][O1] | 1.75 / 14 | 26.250 | 3.850 |
| GPT-5.4 (vision) [O2; checked 2026-10-08][O2] | 2.5 / 15 | 30.000 | 4.750 |
| Claude Sonnet 5.5 (vision) [C1; checked 2026-10-08][C1] | 2 / 10 | 21.000 | 3.500 |

Those are **token scenarios**, not quoted OCR page tariffs. They cannot establish a model's true Greek OCR cost before recording actual usage. For all five, modern Greek and mixed Greek/Latin/Cyrillic accuracy on our sample is unverified. New adapters are estimated at 2–4 hours each after account access, with confidence kept null. [L1; checked 2026-10-08][L1], [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2], [C1; checked 2026-10-08][C1], [R2; checked 2026-10-08][R2], [R8; checked 2026-10-08][R8]

**Gemini 2.5 Pro / Flash**

gemini-2.5-pro; selected because the requested model has historical-document benchmark evidence. Rates shown for prompts at most 200k tokens. [L1; checked 2026-10-08][L1] gemini-2.5-flash; distinct from Flash Image and from Pro. No transfer of Pro benchmark scores. [L1; checked 2026-10-08][L1]

- **Training and retention.** Paid-service prompts/responses are not used to improve Google products. Free service normally differs, but EEA/UK/Switzerland users receive paid-service data handling even on free quota. Abuse/security retention remains; exact TTL not verified. [L4; checked 2026-10-08][L4]
- **Residency.** Gemini Developer API terms permit global processing/caching; no strict EU residency established. Vertex AI is a separate deployment/contract with its own regional controls and retention exceptions. [L4; checked 2026-10-08][L4], [L5; checked 2026-10-08][L5]
- **Free tier.** Pricing lists free access for Gemini 2.5 Pro/Flash, with account/model limits; available quota was not checked. [L1; checked 2026-10-08][L1]
- **Rate limits.** RPM, TPM and requests/day vary by model/project/tier; use live project quotas, not copied historical free-tier numbers. [L3; checked 2026-10-08][L3]
- **Greek evidence.** CHURRO evaluates Gemini 2.5 Pro on multilingual historical documents and places it close to CHURRO in aggregate. This does not establish Greek-only strict-NFD CER, and does not validate Flash or these three cohorts. [P2; checked 2026-10-08][P2]

**GPT-5.x vision**

Use dated snapshot gpt-5.2-2025-12-11 for a reproducible configuration; accepts image input. [O1; checked 2026-10-08][O1] gpt-5.4; record returned model identifier and prefer an available dated snapshot. Price is for the standard small-context tier. [O2; checked 2026-10-08][O2]

- **Training and retention.** API content is not used for training by default. Standard abuse-monitoring logs may last up to 30 days; store=false does not remove that policy. Eligible ZDR and application/file retention are separate controls. [O4; checked 2026-10-08][O4]
- **Residency.** Eligible European regional projects can use eu.api.openai.com; documented Europe scope includes EEA/Switzerland. Confirm model/endpoint eligibility and ZDR requirements; ordinary global projects are not automatically EU-resident. [O4; checked 2026-10-08][O4]
- **Free tier.** Selected model documentation does not support a free API tier; do not assume a ChatGPT subscription supplies API credits. [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2]
- **Rate limits.** Model and account-tier rate limits apply; actual project allocation not checked. [O1; checked 2026-10-08][O1], [O2; checked 2026-10-08][O2]
- **Greek evidence.** No comparable independent historical Greek CER found for the selected GPT-5.x snapshots. Vision documentation warns about small text and non-Latin text. [O3; checked 2026-10-08][O3], [P1; checked 2026-10-08][P1]

**Claude vision**

claude-sonnet-5-5, current documented model selected for this survey. Not a claim that older Claude releases cannot read Greek. [C1; checked 2026-10-08][C1]

Sonnet 5.5 rejects non-default temperature/top_p/top_k (HTTP 400); do not send temperature=0. Fix supported effort/thinking settings and repeat the identical image/prompt. [C1; checked 2026-10-08][C1]

- **Training and retention.** Commercial API data is not used for training without permission; standard inputs/outputs are deleted within 30 days, subject to stated exceptions. Approved ZDR is a separate arrangement; file/stateful features differ. [C4; checked 2026-10-08][C4], [C5; checked 2026-10-08][C5]
- **Residency.** Direct API documentation offers global or US inference, not an explicit EU-only direct endpoint. Bedrock/Vertex regional deployments require separate model and contract verification. [C3; checked 2026-10-08][C3]
- **Free tier.** No generally available free production API allowance verified; promotional credits are not assumed. [C1; checked 2026-10-08][C1]
- **Rate limits.** Current account/model quota not checked; no numeric TPS promise made. [C1; checked 2026-10-08][C1]
- **Greek evidence.** No comparable independent historical Greek CER benchmark found for the selected Claude model. [C1; checked 2026-10-08][C1], [P1; checked 2026-10-08][P1]

**How much accuracy evidence actually transfers**

- Transkribus Greek 8.0's 0.93% is a model-card validation result, with unresolved training-page metadata and normalization. It cannot be ranked numerically against this workspace's CLLG 1.30%. [TR1; checked 2026-10-08][TR1], [TR2; checked 2026-10-08][TR2], [R4; checked 2026-10-08][R4]
- Reading or Guessing? (2026-05-26) examines open-weight VLMs on 90 pages from 30 Ancient Greek editions and documents visually ungrounded transcription. It does not supply GPT/Gemini/Claude-specific CER. [P1; checked 2026-10-08][P1]
- CHURRO (EMNLP 2025) includes Gemini 2.5 Pro in broad historical-document evaluation. Aggregate multilingual normalized edit scores are not strict-NFD historical Greek CER. [P2; checked 2026-10-08][P2]
- Romanello et al. (2021) report roughly 7% versus 13% CER for specialist Kraken/Ciaconna versus Tesseract on Greek-heavy commentaries; dataset, model and protocol differ from this task. [P3; checked 2026-10-08][P3]
- Patrologia Graeca research (2026-03-10) reports 1.05% CER/4.69% WER for a dedicated pipeline on nineteenth-century Greek/Latin material. It is not a commercial API result or a comparison on our lines. [P4; checked 2026-10-08][P4]
- No reviewed source establishes performance on this workspace's curled parliament scans. Page-level dewarping and line recognition must be assessed separately. [R1; checked 2026-10-08][R1], [P1; checked 2026-10-08][P1], [P3; checked 2026-10-08][P3]

Treat normalised historical spellings, expanded ligatures and silently corrected accents as errors under our strict protocol. A hosted model can be useful despite a worse overall CER if it reliably catches different CLLG errors; two models confidently agreeing on the same wrong accent provide no verification. This is the decision criterion proposed here, not a measured advantage.

**One-day test plan — 444 unique lines, two calls per reader**

This is a proposed workday **after authorised access is available**. It includes one implemented reader as the minimum deliverable. It does not pretend that all seventeen engines, commercial onboarding and missing ground truth can be completed in one day.

| Cohort | Lines | Admission condition |
|---|---:|---|
| Existing Polyton-DB gold | 300 | Exact frozen IDs/crops/transcripts and existing exclusions; no convenient resampling. [R3; checked 2026-10-08][R3], [R4; checked 2026-10-08][R4] |
| Owner-checked parliament | 44 | Bind authoritative owner corrections to fixture IDs. If unavailable, run only an explicitly unscored diagnostic cohort; never use layer/CLLG as gold. [R5; checked 2026-10-08][R5], [R6; checked 2026-10-08][R6] |
| Modern born-digital | 100 | Human-check and freeze text, then rasterize; select some legitimate Latin and available Cyrillic spans before seeing predictions. No hidden PDF text supplied. [R1; checked 2026-10-08][R1] |

The following schedule, allocations and metrics are proposed engineering choices dated 2026-10-08.

| Time | Work / completion evidence |
|---|---|
| Hours 0–1 | Freeze 444-line manifest/rights/provenance/GT and original-resolution crops. Bind available owner corrections; predeclare script/mark/curl strata. If GT unavailable, label shortfall. |
| Hours 1–4 | Implement and smoke-test recommended DocAI factory on an authorised worker, preserving raw JSON/confidence and unit usage. Verify 10 non-test lines and one missing/failed request path. Existing harness requires a separate cohort driver or scoped extension. |
| Hours 4–6 | Run two complete 444-line passes with fixed version/options, shuffled order and no client result-cache reuse. Reuse exact-image/version CLLG predictions if receipt-bound; otherwise rerun CLLG on permitted compute. Add ready Azure/Mistral/Vision adapters only within remaining time. |
| Hours 6–7 | Score all cohorts separately and pooled as secondary; inspect disagreements blind to engine labels, confidence/error coupling, failure counts and repeat-call differences. |
| Hours 7–8 | Produce evidence-bound comparison, request/usage cost ledger and a keep/qualify/reject decision. No production replacement based only on a language listing or 44-line aggregate. |

Freeze input bytes, SHA-256, source document/page, line ID, crop coordinates, scan resolution, gold text and NFD text. Preserve original-resolution accents with fixed padding; disclose resizing/deskewing. Stratify results by source, marks, Greek/Latin/Cyrillic mixing and curled/straight scans. A minimum-size cloud padding transform must not clip marks. For a separate optional page-context experiment, use 10–20 source pages and report layout/reading-order effects separately from the 444 crop scores.

Start with DocAI plus receipt-bound CLLG readings. Add Azure or Mistral only if their factories are ready; add Vision to probe explicit `grc`, but identify its shared vendor. Transkribus needs tariff/access/confidence clarification and training-book checks before inclusion. Its terms also restrict infrastructure benchmarks/capacity testing, so do not turn this sample accuracy evaluation into a load test without clarification. [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [TR1; checked 2026-10-08][TR1], [TR4; checked 2026-10-08][TR4], [TR5; checked 2026-10-08][TR5], [TR8; checked 2026-10-08][TR8], [TR10; checked 2026-10-08][TR10]

Run two separately submitted passes, shuffled independently, with identical image bytes and fixed parameters. Disable client-side result-cache reuse; preserve service request IDs, returned model/version, UTC timestamp, request options, raw result, extracted literal text, confidence and billed usage. Begin serially or with two in-flight requests; obey Retry-After. Do not retry a wrong answer merely to choose the better transcription.

For vision models, the fixed proposed prompt is:

> Transcribe only the visible text exactly, preserving Greek diacritics, case, punctuation, spacing, and script. Do not modernize, translate, complete, or correct the text. Return only the transcription.

No gold, CLLG answer, title or retrieval context goes into the prompt. Record supported decoding/thinking settings; Sonnet 5.5 rejects `temperature=0`. [C1; checked 2026-10-08][C1]

Measure:

- **Strict NFD CER.** sum Levenshtein(NFD(prediction),NFD(gold)) / sum len(NFD(gold)); preserve case, spaces, punctuation, combining marks and final sigma; no NFKC, transliteration, accent stripping, trimming or whitespace collapse.
- **Mark F1.** Use existing frozen base/mark alignment and categories: pooled micro 2TP/(2TP+FP+FN), plus acute/grave/circumflex, breathing, diaeresis and iota-subscript breakdown. Marks on wrong base positions cannot count as correct. Null if denominator zero.
- **Greek → Latin homoglyphs.** Aligned Greek-GT to Latin-prediction substitutions using frozen explicit homoglyph map; report count and per 1,000 Greek base letters. Genuine Latin GT is not an error. Report Cyrillic confusions separately.
- **Two-call determinism.** Two independently submitted requests with identical bytes/version/options; raw-text exact match and NFD-text exact match, changed-line rate and inter-call CER; preserve request IDs/timestamps.
- **Confidence usefulness.** Retain native level, scale, raw spans and boxes; score word/symbol error-versus-confidence and disagreement recall at human-review budgets. Do not invent char confidence from word scores or turn one NFC-symbol confidence into independent NFD-mark probabilities.
- **Independence in observed errors.** CLLG-wrong/new-correct and CLLG-correct/new-wrong counts, joint-wrong agreement, marks and script errors; coverage and disagreement precision/recall matter more than agreement alone.
- **Operational cost/latency.** Complete-request p50/p95, total wall time, queue/poll overhead, billed pages/image/input/output/reasoning tokens, retries, currency and minimum subscription spend. Remote wall time is not local CPU ms/line.
- **Coverage and failures.** Publish successful-output scores plus failure-aware scores (missing prediction treated as empty), missing count and total denominator. Never omit failed lines silently.
- **Uncertainty.** Paired bootstrap by source document when enough documents exist; mark small document/44-line intervals as weak. Do not tune prompts/confidence thresholds on these evaluation labels then report the same score as held out.

Reuse the frozen existing scorer for the 300-line comparable result. A separate cohort driver or scoped harness extension is required for 44/100 and repeat-call/confidence output; do not silently change E2's existing 300+300 selection rule. Missing/failed requests must remain visible. [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3]

**Day-one budget (calculated, before free tiers):** 444 × 2 = 888 images per reader. DocAI: **USD 1.332**; Azure: **USD 1.332**; Mistral: **USD 3.552**, assuming its image counts as one page. Those three together: **USD 6.216**, before retries, tax and warmups. Ten extra DocAI smoke calls add USD 0.015. An optional Vision pass-pair adds USD 1.332. Propose a USD 10 core usage cap, enforced by the test runner; cloud budget alerts alone are not a hard stop. This cap is a planning value, not a charge already authorised or incurred. [G4; checked 2026-10-08][G4], [V2; checked 2026-10-08][V2], [A4; checked 2026-10-08][A4], [M1; checked 2026-10-08][M1]

A fresh unused 1,000-unit Google allowance could cover the 888 calls, but do not assume it remains available. Azure's 500-page F0 allowance does not cover both passes. Transkribus pack/subscription costs are separate; a cheap marginal credit rate is not the amount required to open the account. Record invoice/usage exports and actual credits rather than converting estimates into “measured cost.” [G4; checked 2026-10-08][G4], [V2; checked 2026-10-08][V2], [A3; checked 2026-10-08][A3], [TR4; checked 2026-10-08][TR4], [TR6; checked 2026-10-08][TR6]

**Decision at hour eight:** retain CLLG as the incumbent. Require full coverage, no unexplained script conversion, stable repeated outputs and useful complementary corrections before admitting a new verification reader. Report strict CER, mark F1 and joint-wrong agreements per cohort; do not let 100 easy modern lines hide a historical regression. Keep confidence thresholds descriptive until calibrated on separate labels. A replacement or automatic accept/reject policy needs a held-out decision after this screening.

**One engine to enable first: exact setup**

The following are **future operator instructions**, not actions performed in this research. Cloud accounts/credentials were not inspected. The factory and 444-line driver still need a separately scoped implementation.

1. In an authorised Google Cloud project, ensure billing is active and enable the **Document AI API** (`documentai.googleapis.com`). The setup operator needs permissions to enable services; the OCR runtime does not need project Owner. [G8; checked 2026-10-08][G8], [G10; checked 2026-10-08][G10]
2. Open **Document AI → Processor Gallery → Enterprise Document OCR → Create processor**. Choose **EU** (`eu`), not a US/global default. Record the project ID and processor ID. Select/verify `pretrained-ocr-v2.1-2024-08-07`; call that explicit version, not an auto-updated default. [G1; checked 2026-10-08][G1], [G9; checked 2026-10-08][G9], [G11; checked 2026-10-08][G11]
3. Grant the runtime identity **`roles/documentai.apiUser`** for the intended resource/project. For local user ADC, also grant **Service Usage Consumer** (`serviceusage.services.use`) on the quota project. Use an approved existing identity or ADC; keep any credential file outside the repository. [G8; checked 2026-10-08][G8], [G10; checked 2026-10-08][G10], [G13; checked 2026-10-08][G13]
4. On the authorised worker, a user-ADC route is shown below. Substitute the actual project and processor values. If using a pre-existing workload/service identity, point to its approved credential configuration instead of performing a user login. These commands have **not** been executed. [G12; checked 2026-10-08][G12], [G13; checked 2026-10-08][G13], [R2; checked 2026-10-08][R2]

```sh
export GOOGLE_CLOUD_PROJECT='YOUR_ACTUAL_PROJECT_ID'
export DOCUMENTAI_PROCESSOR_ID='YOUR_ACTUAL_PROCESSOR_ID'
export DOCUMENTAI_LOCATION='eu'
gcloud auth application-default login
gcloud auth application-default set-quota-project "$GOOGLE_CLOUD_PROJECT"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
export DOCUMENTAI_PROCESSOR_VERSION='pretrained-ocr-v2.1-2024-08-07'
```

Use the actual ADC path if `CLOUDSDK_CONFIG` or the platform changes it. The first four environment names are the existing harness gate. `DOCUMENTAI_PROCESSOR_VERSION` is a **proposed adapter input**, not a variable the current harness already validates. No long-lived service-account key needs to be created merely to run this user-ADC test. [R2; checked 2026-10-08][R2], [G8; checked 2026-10-08][G8]

5. Implement an actual factory whose argument is the service name and whose return value is a callable `Path -> str`. Bind `kind: service`, `service: google`, `factory: <actual module>:<actual factory>`, and explicitly enable `--service` in the appropriate driver. Save raw JSON/word/symbol confidence through a companion result path; the current `Service.read` returns text only. Do not present a placeholder module as installed. [R2; checked 2026-10-08][R2], [R3; checked 2026-10-08][R3], [R8; checked 2026-10-08][R8]
6. Authenticate the regional, version-specific synchronous request with the configured ADC identity. Use this endpoint and body shape, replacing placeholders with exact PNG bytes encoded as base64. Initially omit language hints and premium OCR features. [G2; checked 2026-10-08][G2], [G3; checked 2026-10-08][G3]

```text
POST https://eu-documentai.googleapis.com/v1/projects/{PROJECT_ID}/locations/eu/processors/{PROCESSOR_ID}/processorVersions/pretrained-ocr-v2.1-2024-08-07:process
Authorization: Bearer <access token from the configured ADC identity>
Content-Type: application/json
x-goog-user-project: {PROJECT_ID}
```

```json
{
  "rawDocument": {
    "mimeType": "image/png",
    "content": "<base64 of the exact PNG bytes>"
  },
  "processOptions": {
    "ocrConfig": {
      "enableSymbol": true,
      "enableNativePdfParsing": false
    }
  }
}
```

For direct REST with user credentials, the quota-project header makes billing attribution explicit; supported auth libraries may supply it from ADC. [G13; checked 2026-10-08][G13]

7. Check ten non-test lines before the benchmark: request success, expected image unit, EU/version binding, `document.text`, and `document.pages[].tokens[]` / `symbols[]` with layout text anchors, polygons and confidence. Keep the raw string before NFD conversion; preserve offsets against that raw string and map to NFD explicitly. A precomposed accented symbol can expand into multiple code points, so its one score must not become several supposedly independent probabilities. Record malformed/empty output as a failure. [G2; checked 2026-10-08][G2], [G3; checked 2026-10-08][G3], [R2; checked 2026-10-08][R2]
8. Only after the response/adapter checks pass, run the two frozen-cohort passes and inspect complementary errors against CLLG. The milestone is **a real, receipt-bound response and confidence capture**, not merely populated environment variables. The present research has not claimed that milestone.

**Source register**

All sources were accessed or local files inspected on **2026-10-08**. “Publication/update unknown” is deliberate. Local sources are workspace evidence rather than external accuracy publications. Dynamic prices, model availability and policies require rechecking at execution; the JSON preserves the exact distinctions used in this report.

- **G1** — [Document AI processors, languages and versions](https://docs.cloud.google.com/document-ai/docs/processors-list). Checked 2026-10-08; publication/update unknown.
- **G2** — [Enterprise Document OCR options](https://docs.cloud.google.com/document-ai/docs/enterprise-document-ocr). Checked 2026-10-08; publication/update unknown.
- **G3** — [Document AI Document schema](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document). Checked 2026-10-08; publication/update unknown.
- **G4** — [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Checked 2026-10-08; publication/update unknown.
- **G5** — [Document AI security and data use](https://docs.cloud.google.com/document-ai/docs/security). Checked 2026-10-08; publication/update unknown.
- **G6** — [Document AI quotas](https://docs.cloud.google.com/document-ai/quotas). Checked 2026-10-08; publication/update unknown.
- **G7** — [Document AI limits](https://docs.cloud.google.com/document-ai/limits). Checked 2026-10-08; publication/update unknown.
- **G8** — [Document AI setup](https://docs.cloud.google.com/document-ai/docs/setup). Checked 2026-10-08; publication/update 2026-10-08.
- **G9** — [Create a Document AI processor](https://docs.cloud.google.com/document-ai/docs/create-processor). Checked 2026-10-08; publication/update unknown.
- **G10** — [Document AI IAM roles](https://docs.cloud.google.com/iam/docs/roles-permissions/clouddocumentai). Checked 2026-10-08; publication/update unknown.
- **G11** — [Document AI regions](https://docs.cloud.google.com/document-ai/docs/regions). Checked 2026-10-08; publication/update unknown.
- **V1** — [Cloud Vision OCR language support](https://docs.cloud.google.com/vision/docs/languages). Checked 2026-10-08; publication/update unknown.
- **V2** — [Cloud Vision pricing](https://cloud.google.com/vision/pricing). Checked 2026-10-08; publication/update unknown.
- **V3** — [Cloud Vision OCR and regional endpoints](https://docs.cloud.google.com/vision/docs/ocr). Checked 2026-10-08; publication/update unknown.
- **V4** — [Cloud Vision data usage](https://docs.cloud.google.com/vision/docs/data-usage). Checked 2026-10-08; publication/update unknown.
- **V5** — [Cloud Vision quotas](https://docs.cloud.google.com/vision/quotas). Checked 2026-10-08; publication/update unknown.
- **V6** — [Cloud Vision text, word and symbol schema](https://docs.cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse). Checked 2026-10-08; publication/update unknown.
- **A1** — [Azure Read language support](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support/ocr?view=doc-intel-4.0.0). Checked 2026-10-08; publication/update unknown.
- **A2** — [Azure prebuilt Read](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/read?view=doc-intel-4.0.0). Checked 2026-10-08; publication/update unknown.
- **A3** — [Azure Document Intelligence pricing](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/). Checked 2026-10-08; publication/update unknown.
- **A4** — [Azure retail price API, West Europe Document Intelligence](https://prices.azure.com/api/retail/prices?%24filter=contains%28productName%2C%20%27Document%20Intelligence%27%29%20and%20armRegionName%20eq%20%27westeurope%27). Checked 2026-10-08; publication/update unknown. Read-only retail API query; S0 Read Pages, USD 1.50 / 1K at tierMinimumUnits=0; effectiveStartDate=2022-03-01. This date is the meter's effective date, not the retrieval date.
- **A5** — [Azure Document Intelligence service limits](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits?view=doc-intel-4.0.0). Checked 2026-10-08; publication/update unknown.
- **A6** — [Azure Document Intelligence data privacy](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security). Checked 2026-10-08; publication/update unknown.
- **M1** — [Mistral OCR 4.1 model](https://docs.mistral.ai/models/ocr-4-1). Checked 2026-10-08; publication/update unknown.
- **M2** — [Mistral changelog](https://docs.mistral.ai/resources/changelogs). Checked 2026-10-08; publication/update unknown. OCR 4.1 GA entry dated 2026-08-31; avoid retired OCR 4.0.
- **M3** — [Mistral OCR inputs, confidence and blocks](https://docs.mistral.ai/studio/document-processing/basic_ocr). Checked 2026-10-08; publication/update unknown.
- **M4** — [Mistral OCR API schema](https://docs.mistral.ai/api/endpoint/ocr). Checked 2026-10-08; publication/update unknown.
- **M5** — [Mistral language support](https://docs.mistral.ai/resources/languages). Checked 2026-10-08; publication/update unknown.
- **M6** — [Mistral OCR 4 announcement and batch pricing](https://mistral.ai/news/ocr-4/). Checked 2026-10-08; publication/update unknown.
- **M7** — [Mistral limits and storage](https://docs.mistral.ai/resources/known-limitations). Checked 2026-10-08; publication/update unknown.
- **M8** — [Mistral training-data use](https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models). Checked 2026-10-08; publication/update 2026-08-31.
- **M9** — [Mistral commercial terms](https://legal.mistral.ai/terms/commercial-terms-of-service/). Checked 2026-10-08; publication/update unknown.
- **M10** — [Mistral zero data retention](https://docs.mistral.ai/admin/monitor-comply/zero-data-retention). Checked 2026-10-08; publication/update unknown.
- **T1** — [Textract supported languages and document limits](https://docs.aws.amazon.com/textract/latest/dg/limits-document.html). Checked 2026-10-08; publication/update unknown.
- **T2** — [Textract pricing](https://aws.amazon.com/textract/pricing/). Checked 2026-10-08; publication/update unknown.
- **T3** — [Textract FAQ: data use and regions](https://aws.amazon.com/textract/faqs/). Checked 2026-10-08; publication/update unknown.
- **T4** — [Textract Block schema](https://docs.aws.amazon.com/textract/latest/APIReference/API_Block.html). Checked 2026-10-08; publication/update unknown.
- **T5** — [Textract regional quotas](https://docs.aws.amazon.com/general/latest/gr/textract.html). Checked 2026-10-08; publication/update unknown.
- **B1** — [FineReader Engine 12 language names](https://help.abbyy.com/en-us/finereaderengine/12/user_guide/specifications_langnames/). Checked 2026-10-08; publication/update unknown.
- **B2** — [FineReader Engine character-confidence semantics](https://help.abbyy.com/en-us/finereaderengine/12/user_guide/apireference_plaintext_charconfidence/). Checked 2026-10-08; publication/update unknown.
- **B3** — [FineReader Engine recognition hypotheses](https://help.abbyy.com/en-us/finereaderengine/12/user_guide/guidedtour_voting/). Checked 2026-10-08; publication/update unknown.
- **B4** — [FineReader Engine specifications](https://help.abbyy.com/en-us/finereaderengine/12/user_guide/introduction_shortspecifications/). Checked 2026-10-08; publication/update unknown.
- **B5** — [ABBYY Cloud OCR SDK end of life](https://support.abbyy.com/hc/en-us/articles/11263047306131-End-of-Life-EXTENDED-ABBYY-Cloud-OCR-SDK-August-30-2024). Checked 2026-10-08; publication/update 2025-09-04.
- **B6** — [ABBYY-hosted Vantage partner language specification](https://distrib.abbyy.com/PartnerSkills/Incture/Cherywork_ABBYY_Vantage_AP_Automation.pdf). Checked 2026-10-08; publication/update unknown. Partner document, not a current Vantage SKU guarantee.
- **B7** — [Vantage v1 output formats](https://help.abbyy.com/en-us/vantage/1/developer/developer_outputformats/). Checked 2026-10-08; publication/update unknown. Legacy v1 documentation; current tenant output must be checked.
- **B8** — [Vantage v1 single API processing](https://help.abbyy.com/en-us/vantage/1/developer/developer_howto_processing_singleapi/). Checked 2026-10-08; publication/update unknown.
- **B9** — [Vantage extracted-object confidence caveat](https://help.abbyy.com/en-us/vantage/1/developer/developer_jsonexport_extractedobject/). Checked 2026-10-08; publication/update unknown.
- **B10** — [Archived ABBYY cloud terms](https://www.abbyy.com/legal/cloud-terms-of-service-24-03-2023/). Checked 2026-10-08; publication/update 2023-03-24. Historical terms, not proof of current retention.
- **TR1** — [Transkribus 19th-century Greek 8.0 model](https://www.transkribus.org/models/19th-century-greek-8.0). Checked 2026-10-08; publication/update 2024-08-08. Live plural-path page reports 413 training pages, 24,836 lines, 187,561 words, model 148525, validation CER 0.93%.
- **TR2** — [Older Greek 8.0 model description](https://www.transkribus.org/model/19th-century-greek-8.0). Checked 2026-10-08; publication/update unknown. Search-indexed legacy description redirects to TR1; reports 894 pages/seven books and transcription normalizations. Conflicts with current 413-page metadata.
- **TR3** — [Transkribus Noscemus historical Latin/Greek public model](https://www.transkribus.org/models/print-latin-texts-15-th-19th-htr). Checked 2026-10-08; publication/update 2023-06-06.
- **TR4** — [Transkribus pricing](https://www.transkribus.org/pricing). Checked 2026-10-08; publication/update unknown.
- **TR5** — [Transkribus developer API overview](https://docs.transkribus.org/). Checked 2026-10-08; publication/update unknown. Beta documentation; API access conflicts with pricing page.
- **TR6** — [Transkribus API credits](https://docs.transkribus.org/start/credits). Checked 2026-10-08; publication/update unknown.
- **TR7** — [Transkribus API rate limits](https://docs.transkribus.org/start/rate-limits). Checked 2026-10-08; publication/update unknown.
- **TR8** — [Transkribus API text recognition](https://docs.transkribus.org/processing/text-recognition). Checked 2026-10-08; publication/update unknown.
- **TR9** — [Transkribus API authentication](https://docs.transkribus.org/start/auth). Checked 2026-10-08; publication/update unknown.
- **TR10** — [Transkribus terms](https://legal.transkribus.org/terms). Checked 2026-10-08; publication/update unknown.
- **TR11** — [Older Transkribus subscription FAQ](https://www.transkribus.org/subscription-faqs). Checked 2026-10-08; publication/update unknown. Older printed-text tariff conflicts with current generic pricing; not a settled quote.
- **L1** — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). Checked 2026-10-08; publication/update unknown.
- **L2** — [Gemini image understanding](https://ai.google.dev/gemini-api/docs/image-understanding). Checked 2026-10-08; publication/update unknown.
- **L3** — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits). Checked 2026-10-08; publication/update unknown.
- **L4** — [Gemini API terms](https://ai.google.dev/gemini-api/terms). Checked 2026-10-08; publication/update unknown.
- **L5** — [Vertex AI retention and model training](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention). Checked 2026-10-08; publication/update unknown.
- **O1** — [GPT-5.2 model, snapshot and pricing](https://developers.openai.com/api/docs/models/gpt-5.2). Checked 2026-10-08; publication/update unknown.
- **O2** — [GPT-5.4 model and pricing](https://developers.openai.com/api/docs/models/gpt-5.4). Checked 2026-10-08; publication/update unknown.
- **O3** — [OpenAI vision capabilities and limitations](https://developers.openai.com/api/docs/guides/images-vision). Checked 2026-10-08; publication/update unknown.
- **O4** — [OpenAI API data controls and residency](https://developers.openai.com/api/docs/guides/your-data). Checked 2026-10-08; publication/update unknown.
- **C1** — [Claude Sonnet 5.5 overview and pricing](https://platform.claude.com/docs/en/models/sonnet-5-5/overview). Checked 2026-10-08; publication/update 2026-09-28.
- **C2** — [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision). Checked 2026-10-08; publication/update unknown.
- **C3** — [Claude data residency](https://platform.claude.com/docs/en/manage-claude/data-residency). Checked 2026-10-08; publication/update unknown.
- **C4** — [Claude API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention). Checked 2026-10-08; publication/update unknown.
- **C5** — [Anthropic commercial retention policy](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data). Checked 2026-10-08; publication/update 2026-07-01.
- **E1** — [eScriptorium getting started](https://escriptorium.eu/getting_started/). Checked 2026-10-08; publication/update unknown.
- **E2** — [D4Science hosted eScriptorium](https://escriptorium.d4science.org/). Checked 2026-10-08; publication/update unknown.
- **E3** — [eScriptorium quick start](https://escriptorium.readthedocs.io/en/latest/quick-start/). Checked 2026-10-08; publication/update unknown.
- **E4** — [eScriptorium API user tokens](https://escriptorium-tutorial.readthedocs.io/en/latest/users/). Checked 2026-10-08; publication/update unknown.
- **H1** — [Logios paper](https://arxiv.org/abs/2506.21474). Checked 2026-10-08; publication/update 2025-06-26.
- **H2** — [Kalchas primary repository](https://github.com/kperi/Kalchas). Checked 2026-10-08; publication/update unknown.
- **H3** — [Typorama commercial OCR service](https://www.typorama.gr/OCR-Services). Checked 2026-10-08; publication/update unknown.
- **P1** — [Reading or Guessing? Ancient Greek visual grounding study](https://arxiv.org/html/2605.27750v1). Checked 2026-10-08; publication/update 2026-05-26.
- **P2** — [CHURRO historical document recognition](https://aclanthology.org/2025.emnlp-main.1763/). Checked 2026-10-08; publication/update 2025.
- **P3** — [Classical-commentary OCR comparison](https://arxiv.org/abs/2110.06817). Checked 2026-10-08; publication/update 2021-10-13.
- **P4** — [Patrologia Graeca OCR study](https://arxiv.org/abs/2603.09470). Checked 2026-10-08; publication/update 2026-03-10.
- **R1** — [Research brief](../briefs/R3_commercial_ocr_research.md). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R2** — [Service environment gates and factory contract](../../../greekocr/_vendor/bench/e2_teachers.py). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R3** — [Existing bake-off cohorts and scoring](../../../greekocr/_vendor/bench/e2_bakeoff.py). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R4** — [Recorded E2 baseline and overlap exclusions](../../origins/greek-page-ocr/docs/ocr_program_2026-10-06/E2_NOTES.md). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R5** — [Parliament fixture index](../../../tests/fixtures/o4d_lines/index.json). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R6** — [Verification state](../../VERIFY.md). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R7** — [Native CLLG confidence adapter](../../../greekocr/_vendor/bench/e2_native.py). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.
- **R8** — [Service wrapper](../../../greekocr/readers/services.py). Checked 2026-10-08; publication/update unknown. Local source inspected read-only; no git commands.

- **G12** — [Local Application Default Credentials setup](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment). Checked 2026-10-08; publication/update 2026-10-08.

[G12]: https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment
- **G13** — [ADC quota project and Service Usage Consumer permission](https://docs.cloud.google.com/docs/authentication/troubleshoot-adc). Checked 2026-10-08; publication/update 2026-10-07.

[G13]: https://docs.cloud.google.com/docs/authentication/troubleshoot-adc
[G1]: https://docs.cloud.google.com/document-ai/docs/processors-list
[G2]: https://docs.cloud.google.com/document-ai/docs/enterprise-document-ocr
[G3]: https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document
[G4]: https://cloud.google.com/products/document-ai/pricing
[G5]: https://docs.cloud.google.com/document-ai/docs/security
[G6]: https://docs.cloud.google.com/document-ai/quotas
[G7]: https://docs.cloud.google.com/document-ai/limits
[G8]: https://docs.cloud.google.com/document-ai/docs/setup
[G9]: https://docs.cloud.google.com/document-ai/docs/create-processor
[G10]: https://docs.cloud.google.com/iam/docs/roles-permissions/clouddocumentai
[G11]: https://docs.cloud.google.com/document-ai/docs/regions
[V1]: https://docs.cloud.google.com/vision/docs/languages
[V2]: https://cloud.google.com/vision/pricing
[V3]: https://docs.cloud.google.com/vision/docs/ocr
[V4]: https://docs.cloud.google.com/vision/docs/data-usage
[V5]: https://docs.cloud.google.com/vision/quotas
[V6]: https://docs.cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse
[A1]: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support/ocr?view=doc-intel-4.0.0
[A2]: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/read?view=doc-intel-4.0.0
[A3]: https://azure.microsoft.com/en-us/pricing/details/document-intelligence/
[A4]: https://prices.azure.com/api/retail/prices?%24filter=contains%28productName%2C%20%27Document%20Intelligence%27%29%20and%20armRegionName%20eq%20%27westeurope%27
[A5]: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits?view=doc-intel-4.0.0
[A6]: https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security
[M1]: https://docs.mistral.ai/models/ocr-4-1
[M2]: https://docs.mistral.ai/resources/changelogs
[M3]: https://docs.mistral.ai/studio/document-processing/basic_ocr
[M4]: https://docs.mistral.ai/api/endpoint/ocr
[M5]: https://docs.mistral.ai/resources/languages
[M6]: https://mistral.ai/news/ocr-4/
[M7]: https://docs.mistral.ai/resources/known-limitations
[M8]: https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models
[M9]: https://legal.mistral.ai/terms/commercial-terms-of-service/
[M10]: https://docs.mistral.ai/admin/monitor-comply/zero-data-retention
[T1]: https://docs.aws.amazon.com/textract/latest/dg/limits-document.html
[T2]: https://aws.amazon.com/textract/pricing/
[T3]: https://aws.amazon.com/textract/faqs/
[T4]: https://docs.aws.amazon.com/textract/latest/APIReference/API_Block.html
[T5]: https://docs.aws.amazon.com/general/latest/gr/textract.html
[B1]: https://help.abbyy.com/en-us/finereaderengine/12/user_guide/specifications_langnames/
[B2]: https://help.abbyy.com/en-us/finereaderengine/12/user_guide/apireference_plaintext_charconfidence/
[B3]: https://help.abbyy.com/en-us/finereaderengine/12/user_guide/guidedtour_voting/
[B4]: https://help.abbyy.com/en-us/finereaderengine/12/user_guide/introduction_shortspecifications/
[B5]: https://support.abbyy.com/hc/en-us/articles/11263047306131-End-of-Life-EXTENDED-ABBYY-Cloud-OCR-SDK-August-30-2024
[B6]: https://distrib.abbyy.com/PartnerSkills/Incture/Cherywork_ABBYY_Vantage_AP_Automation.pdf
[B7]: https://help.abbyy.com/en-us/vantage/1/developer/developer_outputformats/
[B8]: https://help.abbyy.com/en-us/vantage/1/developer/developer_howto_processing_singleapi/
[B9]: https://help.abbyy.com/en-us/vantage/1/developer/developer_jsonexport_extractedobject/
[B10]: https://www.abbyy.com/legal/cloud-terms-of-service-24-03-2023/
[TR1]: https://www.transkribus.org/models/19th-century-greek-8.0
[TR2]: https://www.transkribus.org/model/19th-century-greek-8.0
[TR3]: https://www.transkribus.org/models/print-latin-texts-15-th-19th-htr
[TR4]: https://www.transkribus.org/pricing
[TR5]: https://docs.transkribus.org/
[TR6]: https://docs.transkribus.org/start/credits
[TR7]: https://docs.transkribus.org/start/rate-limits
[TR8]: https://docs.transkribus.org/processing/text-recognition
[TR9]: https://docs.transkribus.org/start/auth
[TR10]: https://legal.transkribus.org/terms
[TR11]: https://www.transkribus.org/subscription-faqs
[L1]: https://ai.google.dev/gemini-api/docs/pricing
[L2]: https://ai.google.dev/gemini-api/docs/image-understanding
[L3]: https://ai.google.dev/gemini-api/docs/rate-limits
[L4]: https://ai.google.dev/gemini-api/terms
[L5]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention
[O1]: https://developers.openai.com/api/docs/models/gpt-5.2
[O2]: https://developers.openai.com/api/docs/models/gpt-5.4
[O3]: https://developers.openai.com/api/docs/guides/images-vision
[O4]: https://developers.openai.com/api/docs/guides/your-data
[C1]: https://platform.claude.com/docs/en/models/sonnet-5-5/overview
[C2]: https://platform.claude.com/docs/en/build-with-claude/vision
[C3]: https://platform.claude.com/docs/en/manage-claude/data-residency
[C4]: https://platform.claude.com/docs/en/manage-claude/api-and-data-retention
[C5]: https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data
[E1]: https://escriptorium.eu/getting_started/
[E2]: https://escriptorium.d4science.org/
[E3]: https://escriptorium.readthedocs.io/en/latest/quick-start/
[E4]: https://escriptorium-tutorial.readthedocs.io/en/latest/users/
[H1]: https://arxiv.org/abs/2506.21474
[H2]: https://github.com/kperi/Kalchas
[H3]: https://www.typorama.gr/OCR-Services
[P1]: https://arxiv.org/html/2605.27750v1
[P2]: https://aclanthology.org/2025.emnlp-main.1763/
[P3]: https://arxiv.org/abs/2110.06817
[P4]: https://arxiv.org/abs/2603.09470
[R1]: ../briefs/R3_commercial_ocr_research.md
[R2]: ../../../greekocr/_vendor/bench/e2_teachers.py
[R3]: ../../../greekocr/_vendor/bench/e2_bakeoff.py
[R4]: ../../origins/greek-page-ocr/docs/ocr_program_2026-10-06/E2_NOTES.md
[R5]: ../../../tests/fixtures/o4d_lines/index.json
[R6]: ../../VERIFY.md
[R7]: ../../../greekocr/_vendor/bench/e2_native.py
[R8]: ../../../greekocr/readers/services.py

R3: done | recommended: Google Document AI Enterprise Document OCR
