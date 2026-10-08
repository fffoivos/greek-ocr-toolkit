# T4 authored fixtures and recorded source

`polytonic.html`, `government.html` and `news.html` are local test documents,
with authored fixture text/layout tagged CC0-1.0. They use installed system fonts
and make no network requests. The polytonic fixture includes decomposed combining
marks; the other layouts exercise inline text nodes and preserved whitespace.

`wikisource_capture/source.html` is the original response body from the single
authorized capture. `capture_receipt.json` records the URL, UTC acquisition time,
HTTP status, robots/rate posture, user agent and SHA-256. Its source-specific
licence hint is not the authored fixtures' CC0 tag. The receipt is acquisition
evidence; Chromium rendering of that snapshot has not been validated in the
current sandbox. Tests read it offline and verify its digest.
