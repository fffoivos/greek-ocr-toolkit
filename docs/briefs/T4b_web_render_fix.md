# T4b — web_render: stop proxying subresources through the polite client; per-page watchdog; non-hanging tests (gpt-6.1-sol, xhigh)
Workspace = this repo. No `.git` writes (T4B_HANDOFF.json). No network except for ONE optional live check if Chromium is installed.
Evidence (node greek-ocr-e2, 8 Oct 16:00): `greekocr web render --sources <wikipedia url> --max-pages 1 --timeout 20` produces nothing for
>100 s (also with --allow-media); py-spy shows the main thread idle in Playwright's event loop. Playwright itself works on the node
(launch 0.5 s, goto 1.0 s, fonts.ready, pdf ok — ~/work/pw_test.py). Cause in greekocr/real/sources/web_render.py lines ~171–199: the
`context.route('**/*')` handler fetches every subresource through `_PoliteHTTP` (blocking I/O with a ≥1 s per-origin interval) inside the
sync Playwright callback, so a page with dozens of subresources serialises into minutes and blocks the event loop. Also the test module
tests/test_web_render.py hangs instead of skipping on the Mac (killed after 7 min).
Fix:
1. Route handler: never perform blocking HTTP inside it. Media/images abort when block_media; everything else `route.continue_()` so Chromium
   fetches directly. The polite interval applies to top-level navigations only (per origin), via the existing client's rate state, BEFORE
   `page.goto`. robots.txt is checked per origin for the page URL only. Record subresource counts/bytes from Chromium's response events
   (page.on('response')) instead of proxying.
2. Per-page watchdog: `page.goto(..., timeout=timeout*1000)`, fonts.ready awaited with the same timeout via `page.wait_for_function` or
   evaluate with timeout; any page exceeding 2×timeout is abandoned with a receipt row (status 'timeout') and the loop continues.
3. Progress: print one line per page to stdout (`WEB_PAGE n/N status url bytes`) and `WEB_WAVE_DONE pages=<n> failed=<n>` at the end; flush.
4. Tests: skip cleanly when Chromium is absent (launch inside a try with timeout=10000 → pytest.skip), every browser test wrapped in a
   60 s hard cap (threading timer or pytest-timeout if available), fixtures served from local files only (no external fonts: use
   file:// pages with system fonts). Keep the recorded-transport tests.
5. Run the suite; if Chromium is installed here, render ONE local fixture end to end and report the time.
Last line exactly: `T4B: done | tests: <n> passed`.
