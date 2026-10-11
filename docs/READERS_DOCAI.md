# Google Document AI crop reader

The adapter uses `requests` and Application Default Credentials (`google-auth`),
with the Document AI REST API. It uses no Google Document AI client library.
Implementation and tests were built offline with a **synthetic recorded response**
and mocked credentials/transport. No live OCR calls were made by T8.

## Setup for the coordinator

Install the optional extra on the authorised worker:

```sh
python -m pip install -e '.[docai]'
gcloud auth application-default login
gcloud auth application-default set-quota-project ocr-ground-truth-20261008
```

The project needs billing and the Document AI API enabled. The runtime needs
processor processing permission and Service Usage Consumer on the quota project.
See the [R3 setup and ADC sources](research/COMMERCIAL_OCR_20261008.md).
The adapter sets `x-goog-user-project` explicitly; it defaults to the processing
project, or uses `--user-project` / `GOOGLE_CLOUD_QUOTA_PROJECT` when supplied.
It acquires credentials only for a fresh request, never for a cache hit.

The CLI defaults bind the coordinator's 8 October 2026 smoke-test configuration:

- Project: `ocr-ground-truth-20261008`; location: `eu`.
- Processor: `9a98b7aca3c19561` (`OCR_PROCESSOR`, display name `ocr-ground-truth`).
- Pinned version: `pretrained-ocr-v2.1-2024-08-07`.
- `processOptions.ocrConfig.enableSymbol=true`, `hints.languageHints=["el"]`.

Override these with `--project`, `--location`, `--processor-id`, `--version`,
`--language-hints`, `--no-symbols`, or the `GOOGLE_CLOUD_PROJECT`,
`DOCUMENTAI_LOCATION`, `DOCUMENTAI_PROCESSOR_ID`, `DOCUMENTAI_PROCESSOR_VERSION`
environment variables. The endpoint for a pinned version is:

```text
https://eu-documentai.googleapis.com/v1/projects/{P}/locations/eu/processors/{ID}/processorVersions/{VERSION}:process
```

## Frozen manifests

Build the 444-line core cohort (300 Polyton-DB + 44 owner + 100 born-digital):

```sh
greekocr readers docai manifest --fixtures-root tests/fixtures --out /tmp/docai444.jsonl
```

Build the separate 400-line diagnostic sample:

```sh
greekocr readers docai manifest --fixtures-root tests/fixtures --cohorts o4d_sample400 --out /tmp/docai-sample400.jsonl
```

`--cohorts` accepts `polytondb_gold300`, `o4d_lines`, `borndigital100`, and
`o4d_sample400` in any explicitly chosen combination. The default reports a
shortfall if born-digital's `index.json` has not been staged. It never substitutes
sample lines for missing core lines. Manifest output must be a new file.
Builders rebase old worker crop paths to staged local crops, hash their bytes,
preserve original metadata under `provenance`, and verify supplied crop hashes.
Polyton-DB uses the exact frozen gold IDs/transcripts and only joins precomputed
CLLG/ours diagnostics when line ID and crop hash match.

Each JSONL row contains:

```json
{"crop_path":"crops/line.png","line_id":"line-1","cohort":"owner44","gold_text":null,"diagnostics":{"layer_text":"layer transcription","cllg_text":"reader transcription","ours_text":null}}
```

Relative paths are resolved against the manifest's directory. Optional
`crop_sha256` is checked before starting and again on the bytes sent to the API.
Duplicate `(cohort, line_id)` entries are rejected. Only single-page PNG, JPEG or
TIFF crops are accepted, so a successful call represents one page.

Polyton-DB 300 is true gold. Owner 44 and sample 400 builders set `gold_text=null`
even if an index includes reader or layer text. For born-digital, only explicitly
supplied `gold_text` is scored; a generic `text` or `layer_text` is never promoted.
The staged born-digital source currently identifies an exact text layer; that
provenance does not establish the human review proposed in R3.

## Run and repeat

The coordinator can submit a single pass, or two fresh passes for determinism:

```sh
greekocr readers docai run --manifest /tmp/docai444.jsonl --out /tmp/docai444-run
greekocr readers docai run --manifest /tmp/docai444.jsonl --out /tmp/docai444-repeat --repeat 2
```

The default concurrency is four. `--repeat N` means **N total passes**, and values
above one force fresh requests in **every** pass, including the first. With one
pass, receipt caching is enabled unless `--fresh` is supplied. Cache reuse occurs
within the same receipts directory, including subsequent runs into the same
`--out`. No HTTP retries occur automatically. Choose concurrency according to
the project's quota; concurrency alone is not a request-per-minute limiter.

The report keeps **all** `document.text`, without trimming a terminal newline,
choosing one returned line, or repairing whitespace. `lines` uses Python
`splitlines()`: internal blank lines count, terminal LF adds no invented line,
empty text has zero lines. A neighbour line is a visible line-count anomaly and
also remains in the CER input.

Outputs:

- `manifest.jsonl`: resolved, hash-bound input snapshot.
- `predictions.jsonl`: one row per input and pass, including failures, exact text,
  line count, confidence spans, raw receipt path, request ID and latency.
- `REPORT.md` and `summary.json`: cohort/pass scores, coverage, anomalies,
  determinism, latency and cost estimates.
- `ledger.jsonl`: only this invocation's cache hits and service attempts.
- `receipts/ledger.jsonl`: cumulative receipt history across invocations.
- `receipts/{binding_sha256}/{crop_sha256}-{version}/{receipt_id}.json`: immutable
  raw JSON responses, with `cache.json` pointing to the latest successful receipt.

The cache key binds crop bytes, project, location, processor, version, quota
project and OCR options. Raw-receipt hashes are verified before reuse. Fresh
responses retain earlier receipt files. File locks prevent duplicate concurrent
cache fills and interleaved ledger writes. HTTP errors retain their raw JSON
(non-JSON bodies are wrapped as error evidence); transport failures have no raw
response and a null raw path. Failed responses never populate the cache.
Runs with missing readings retain the report and return CLI exit code 3.
Rerunning an output directory replaces its current report/predictions while
preserving cumulative receipts; use separate directories to keep run reports.

## Score definitions

The driver reuses `greekocr.score.score_readings`: NFD decomposition of both sides,
then pooled edits / pooled gold codepoints. Case, spaces, punctuation, combining
mark order, final sigma and all returned newlines remain strict. It reports
per-diacritic TP/FP/FN, precision, recall and F1, pooled mark F1, and aligned
Greek→Latin homoglyph substitutions. Undefined denominators are NA, never zero.
Scores are per cohort and pass; repeat passes are not pooled into extra gold lines.

Reader/layer comparisons are labelled **DIAGNOSTICS only**, with the comparison
text as reference. Agreement with CLLG, the layer or ours is never called accuracy.
Gold-null cohorts receive no gold accuracy metrics or gold homoglyph counts.
Failures remain missing, rather than receiving fabricated perfect scores.

Determinism compares every successful pair of passes for the same line: fraction
of **raw** texts identical, plus mean bidirectional strict NFD CER (the two
orientations are averaged because neither repeat is gold). Missing pairs are
excluded and their coverage is reported. Raw NFC/NFD differences can therefore
reduce exact identity while leaving repeat CER zero.

Token/symbol confidence entries contain `text`, `confidence`, `segments` (start/end
codepoint indices into raw `document.text`) and `page`. Anchors can have multiple
segments, and omitted `startIndex` means zero. Mean/min symbol confidence exclude
missing confidence values; no symbols means NA. These service values are not
calibrated diacritic correctness probabilities. Request ID comes from response
headers when present, otherwise null; the local receipt UUID is separate.

## Cost and data use

The supplied tariff estimate is USD 1.50 / 1,000 pages: one crop is one billed page,
irrespective of whether it returns one or multiple text lines. Thus 444 × 2 calls
estimate **USD 1.332**, and 400 × 2 estimate **USD 1.20**, before tax, credits, retries
or warmups. See the [R3 budget and pricing evidence](research/COMMERCIAL_OCR_20261008.md).
The driver enforces a default `--max-cost-usd 10` preflight cap against all planned
crop-page calls, conservatively ignoring potential cache hits. It records no
charge for cache hits and one estimated page for successful HTTP responses.
Billing for transport/HTTP failures is unknown and separately disclosed; the
conservative attempt estimate reserves one page for each. This ledger is a
planning estimate, not a verified invoice. Latency mean/p50/p95 use successful
fresh HTTP calls only, excluding ADC setup, local writes and cache hits. The
coordinator's 2.1-second smoke measurement is context, not a T8 benchmark.

**Document AI does not train on customer data by default**, according to the
[R3 report, Google Document AI data-handling section](research/COMMERCIAL_OCR_20261008.md),
citing [Google Document AI security and data use](https://docs.cloud.google.com/document-ai/docs/security)
(R3 source G5, checked 2026-10-08). R3 distinguishes synchronous in-memory
processing from batch temporary retention and metadata logging. This adapter
uses synchronous processing. Local raw receipts and prediction files retain
customer text; manage those files according to the dataset's rights and access
policy. This implementation relied on the local R3 evidence and coordinator
facts; it did not re-query the provider.

## Python and offline validation

```python
from greekocr.readers.services.google_docai import DocAIReader
reader = DocAIReader('ocr-ground-truth-20261008', 'eu', '9a98b7aca3c19561',
                     version='pretrained-ocr-v2.1-2024-08-07', receipts_dir='docai_receipts')
reading = reader.read('crop.png')
readings = reader.read_batch(['crop.png'], concurrency=4)
binding = reader.binding()
```

The Python constructor's `version=None` uses the processor's unpinned default;
its binding records null rather than claiming a known resolved version. The CLI
pins the smoke-test version. Use an explicit version for reproducible caching.
`fresh=True` can be set on the reader or on individual reads/batches.
For offline tests, inject a callable `transport(url, json=..., headers=...,
timeout=...)` and credentials implementing `before_request`; no real credentials
are needed. The synthetic response has two tokens and five symbols.

```sh
python -m pytest tests/test_docai.py -q
```

## T10 live empty-response handling

The failed-line audit on 11 October 2026 encountered an HTTP-success empty page
whose `document.text`, lines and symbols were omitted as default ProtoJSON
fields. The adapter now reads that form as empty text with no confidence values;
it still rejects missing text accompanied by nonempty text-bearing layout.
See [ProtoJSON default-value rules](https://protobuf.dev/programming-guides/json/#presence-and-default-values).
T10 recovered the original saved raw response without re-calling the crop and
retains the historical parse-error ledger. This does not change T8's offline-only
provenance. The audit CLI/report is documented in [API.md](API.md#failed-line-document-ai-audit-t10-prototype).
