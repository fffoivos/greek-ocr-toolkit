# T4c — web_render is still too slow: profile each step on a real page and fix (gpt-6.1-sol, xhigh). Workspace = this repo. No `.git` writes.
Network ON (needed: render ONE real page here, Chromium is installed on this Mac; `playwright install chromium` if the venv lacks the browser).
Evidence (node, 8 Oct 16:15, after T4b): `greekocr web render --sources https://el.wikipedia.org/wiki/Κέρκυρα --max-pages 1 --timeout 120`
→ status timeout "per-page watchdog exceeded" after 241 s; the Greece article at --timeout 30 the same. Plain Playwright on the same node:
launch 0.5 s, goto(load) 1.0 s, fonts.ready instant, page.pdf() ~1–2 s (2.7 MB) — ~/work/pw_test.py. So the renderer's own page work
(DOM line extraction? per-text-node Range.getClientRects via many evaluate round trips? full-page screenshot at scale? waiting on
something that never resolves?) is the problem.
Required:
1. Instrument `render_pages` with per-step timings written into each page receipt (`timings`: goto, fonts, dom_lines, screenshot, pdf,
   records) and print them on the WEB_PAGE line. Profile on one real page (el.wikipedia Κέρκυρα) with timeout 180; report the numbers.
2. Fix the slow step(s): the DOM line extraction must be ONE `page.evaluate` that walks text nodes and returns all line rects as JSON
   (no per-node round trips); the screenshot must be a single full-page capture at the configured scale (default scale 1.5, cap the page
   height, e.g. 20,000 px, and record truncation); print-to-PDF once; no waits on 'networkidle'; `fonts.ready` awaited with a 5 s cap.
3. Target: a typical Wikipedia article renders (PDF + PNG + DOM lines + receipt) in < 15 s on this Mac; re-run the same page and report.
4. Keep the tests non-hanging (browser tests capped at 60 s; skip without Chromium). Run the suite.
Last line exactly: `T4C: done | page_seconds: <n> | tests: <n> passed`.
