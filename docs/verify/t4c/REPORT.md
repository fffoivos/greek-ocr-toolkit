# T4c renderer timings and bounded capture

Implementation is finished; real-page speed validation remains blocked. Both the
instrumented baseline and final Κέρκυρα commands used `--max-pages 1 --timeout 180`
on this Mac. Installed Chromium could not launch in the execution sandbox:

```text
bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.72510: Permission denied (1100)
```

The CLI returned `Chromium unavailable or cannot start: BrowserType.launch: Target
page, context or browser has been closed`. Neither command reached navigation or
created a page receipt. The final command failed in 0.774 seconds; that is launch
failure time, **not page render time**. No per-step real-page numbers or <15-second
success are claimed. The reported node timeouts supplied in the brief are prior
evidence, not measurements from this run.

| Receipt timing (seconds) | Instrumented baseline | Final rerun |
| --- | --- | --- |
| `goto` | Not reached | Not reached |
| `fonts` | Not reached | Not reached |
| `dom_lines` | Not reached | Not reached |
| `screenshot` | Not reached | Not reached |
| `pdf` | Not reached | Not reached |
| `records` | Not reached | Not reached |
| Complete page | Unavailable | Unavailable |

## Changes

- All six timings are accumulated in success/failure receipts and printed on
  `WEB_PAGE`, with partial time retained when a step is cancelled.
- `fonts.ready` is awaited directly with a five-second Python cap. Detached
  readiness flags and animation-frame polling have been removed. The capture does
  not wait for `networkidle`.
- DOM extraction remains one browser evaluation for each layout: screen and
  independent print. The walk caches styles/ancestor visibility, avoids per-glyph
  queries for ordinary single-line nodes, and finds ordinary wrapped line boundaries
  by binary search over grapheme offsets. Preserved whitespace and unusual
  fragmentation retain conservative mapping in the same evaluation.
- One PNG capture uses scale 1.5 by default, `full_page=True`, and a top-origin clip
  at 20,000 CSS pixels. `--max-page-height` configures the cap. The
  `screenshot_capture` receipt records the original/captured height and truncation.
  Full DOM and the single A4 PDF remain complete; exported DOM rows outside the PNG
  are flagged as clipped.
- Receipt assembly no longer waits for every `response.finished()`. Response-size
  queries run concurrently with at most a one-second wait per query; unavailable
  sizes stay null and count as unmeasured.

The old per-grapheme walk, RAF readiness polling and unbounded response completion
waits were identified by code inspection. Their contribution to the node's
observed slowdown cannot be established without a successful live profile.

## Verification

Full suite: **1,832 passed, 16 skipped**, 15 existing deprecation warnings, in
40.67 seconds. All 16 skips are browser tests whose bounded probe could not launch
Chromium. Browser tests and browser fixture setup retain their 60-second hard caps.

Recorded browser tests verify one screenshot/PDF call, one DOM extraction per
layout, scale/cap/truncation receipt fields, a five-second font cap despite a
180-second page timeout, concurrent cancellation of unfinished size queries,
timings on interrupted work, and wave continuation. The additional real-browser
fixture checks wrapped combining marks, non-BMP characters and PNG clipping; it
was skipped with the other browser tests. Thus rendered geometry and PDF agreement
were not reverified in a live browser here.

Python compilation and the read-only diff whitespace check passed. No `.git`
writes were made.

Evidence: [summary.json](summary.json), [before-profile.json](before-profile.json),
[before.log](before.log), [after-profile.json](after-profile.json),
[after.log](after.log), [pytest-results.xml](pytest-results.xml),
[pytest.log](pytest.log), [web-tests.xml](web-tests.xml).

## Pending real-page validation

Run from a normal terminal that can launch the installed Chromium, using a fresh
destination because captures are never overwritten:

```sh
PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright" .venv/bin/greekocr web render \
  --sources 'https://el.wikipedia.org/wiki/Κέρκυρα' --max-pages 1 --timeout 180 \
  --dest /tmp/greekocr-t4c-live
```

Its `WEB_PAGE` line and receipt provide the six timings and page seconds. A
successful complete capture under 15 seconds is still required to confirm the
performance target.
