# Transkribus service reader

T12 uses public PyLaia model **19th-century Greek 8.0**, ID **148525**.
The model ID is a parameter, not a hidden fixed model choice. The model’s own
published validation CER is not a reference for these Anemi crops.
[Model card](https://www.transkribus.org/models/19th-century-greek-8.0).

## Authentication and API

The reader obtains credentials only from `TRANSKRIBUS_USERNAME` and
`TRANSKRIBUS_PASSWORD`. It never writes or logs their values. Access and refresh
tokens remain in memory; refresh uses `grant_type=refresh_token` before expiry.
The token endpoint is
`https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token`,
with `client_id=processing-api-client`.

The verified processing endpoint for this run is
`https://transkribus.eu/processing/v1/processes`. The current guides also describe
the v2 API; their reference presently links to a staging host. The reader permits
only official processing hosts and records the exact URL in its cache binding.
No arbitrary result URL receives the bearer token, and redirects are disabled.

- POST one base64 PNG/JPEG/TIFF image per process, with
  `config.textRecognition.htrId`.
- GET `/processes/{processId}` until FINISHED; fail on FAILED, CANCELLED,
  unknown status, or the bounded wait (default 180 seconds).
- GET `/processes/{processId}/page` for PAGE XML, retaining both JSON and XML
  in the SHA envelope.

[Processing schema](https://transkribus.eu/processing/v1/openapi.json),
[current recognition guide](https://docs.transkribus.org/processing/text-recognition),
[authentication](https://docs.transkribus.org/start/auth). Checked 12 October 2026.

## Layout modes and returned confidence

`mode="default"` omits preliminary layout and explicitly supplies
`config.lineDetection.modelId=49272`, the layout model used in the published
legacy API example, with the other detection parameters left at defaults. The
layout model ID is configurable. The legacy service returned zero lines on
three Anemi probes with that explicit model. Omitting `lineDetection` or passing
an empty block also returned zero lines; those earlier probes are labelled
separately and are not presented as proof that detection ran.
`mode="single_line"` supplies one region and one line spanning the
whole image, with a horizontal baseline at 75% of image height. This uses the
documented `content.regions[].lines` input; image bytes are unchanged.

Explicit detection returned no text on all three paired Anemi probes, so T12’s
main comparison uses supplied single-line geometry. This is not an accuracy
claim. Some failed crops contain multiple printed rows or curved text: imposing
one line can damage their readings, and its line count cannot expose that defect.
The paired detection results are retained under `default_layout/responses/`;
earlier omitted/empty-block probes are under `omitted_layout/` and
`empty_line_detection/`. These additional probes and their charges remain in
the receipt.

PAGE TextLine/TextEquiv supplies text and confidence when present. Words and
Glyph elements supply word/character confidence when present. Primary TextEquiv
is selected by lowest index; region reading order is honoured with DOM fallback.
No word or line confidence is relabelled as character confidence. All missing
confidence stays null. The live PyLaia PAGE outputs in this run do not supply
confidence. `Reading.text` is NFD; `raw_text`, report text and glyph counts preserve
the emitted code points. JSON content can also be parsed when PAGE is unavailable
to an offline caller.

## Credit guard, calls and cache

`GET https://transkribus.eu/TrpServer/rest/credits` with `onlyActive=true` and
`includeExpired=false` exposes `overallBalance`. No account identity or raw
credit package list is saved. Unknown or invalid balances never authorize a job.

The minimum floor is **50 credits**. Every pending and next page reserves a
conservative **1 credit**, against a fresh balance query before submission.
HTTP 402/429, a failed process, or a measured charge above that reservation stops
new submissions. Already accepted jobs are drained without adding new paid jobs.
The queue has six one-image jobs by default and a hard maximum of eight; Anemi
fully drains before any Vouli submission.

For queued jobs, `GET /TrpServer/rest/jobs/{processId}/creditTransactions` records
only the matching job ID, debit, cost factor, page count and timestamp. Account
snapshots may overlap jobs; per-page cost comes from the debit, not that snapshot
difference. Sequential pilot charges were measured by before/after balances.
All credits, calls and reconciliation are in the receipt; no currency estimate
is substituted for measured credits.
[Credit API schema](https://transkribus.eu/TrpServer/rest/openapi.json),
[API credit policy](https://docs.transkribus.org/start/credits).

Cache: `docs/records/harvest/transkribus_failed_lines/responses/<crop-sha256>.json`.
The image SHA, model, layout mode, language model, endpoint and raw response SHA
must match. Byte-identical crop IDs share one response and charge. A durable
attempt precedes submission. A saved process ID can be resumed without another
submission; a prior attempt with no process ID is never automatically repeated.
The runner retains that crop as unresolved and can continue independent crops.
Its separate `--retry-unresolved` opt-in permits one recovery attempt, preserving
the original under `prior_attempts/` and reserving an extra maximum charge for
each unknown original submission. A second recovery retry is disabled. T12 used
this bounded recovery for one HTTP 502 and one interrupted submission to finish
the authorized catalogue test; any charged but unassigned original process is
included separately in account reconciliation.

```python
from greekocr.readers.services.transkribus import TranskribusReader
reader = TranskribusReader(model_id=148525, responses_dir="responses", mode="single_line")
reading = reader.read("crop.png", offline=True)
```

## Catalogue CLI and three-way metrics

```sh
.venv/bin/python scripts/harvest/google_failed_lines.py --engine transkribus --include-anemi
.venv/bin/python scripts/harvest/google_failed_lines.py --engine transkribus --include-anemi --offline
```

Anemi requires the explicit opt-in. Offline mode makes zero network calls and
rebuilds from available hash-checked responses. The 469 inputs are exactly the
452 current-output catalogue crops plus the same 17 bound comment crops used
by T10/T11; source pixels, production page code and held-out pages are untouched.

The three-way comparison recomputes every engine’s crop metrics from its stored
response. NFD CER is pairwise disagreement with first-engine denominator;
reverse and mean bidirectional values are also saved. Majority agreement means
at least two of three agree, reported raw, NFD, and with CR/LF removed without
collapsing spaces. Missing engine results are excluded from common-cohort
metrics, with coverage stated. Controls and unique-image views are separate.
None of these engines is a reference. Rare-glyph emission does not prove the
correct glyph was read.

[Report](../../../records/harvest/THREE_ENGINES_v1.md) ·
[Review](../../../harvest/three_engines_review.html) ·
[Raw CSV](../../../records/harvest/transkribus_failed_lines/three_engines.csv) ·
[Receipt](../../../records/harvest/transkribus_failed_lines/receipt.json).

## Offline checks

`tests/test_transkribus.py` covers stored OAuth/PAGE/JSON/credit samples, refresh,
null confidence, Unicode, cache hash and model binding, the floor, depleted
credits, bounded waits, uncertain submissions, pending-job reservations,
duplicate SHA reuse, offline replay, engine selection and three-way metrics.
HTTP is mocked and real environment credentials never enter the fixtures.
