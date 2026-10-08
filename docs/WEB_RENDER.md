# Rendered web pages as exact label data (O4e / T4)

`greekocr.real.sources.web_render` captures HTML with Playwright and Chromium,
without running OCR. The screenshot labels describe DOM text fragments in the
captured rendering. The PDF labels come independently from the vendored
`greekocr/_vendor/bench/o4b_textlayer_lines.py::pdf_pages` extractor. Neither
path makes a claim about real scanned documents or automatically grants reuse rights.

## Install and run

```sh
python -m pip install -e '.[web]'
python -m playwright install chromium
greekocr web render --sources example.html --max-pages 1 --dest rendered --offline --licence CC0-1.0
greekocr web records rendered
```

On a workspace that cannot write the default Playwright cache, install with
`PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright"` and keep that environment variable
set when rendering. The browser is an optional dependency. Importing the module,
reading source lists and converting existing captures do not launch a browser.

Live acquisition is explicit:

```sh
greekocr web render --sources wikipedia-featured wikisource --max-pages 4 --dest rendered
greekocr web render --sources news --max-pages 6 --dest news-rendered
greekocr web render --sources wikisource --category 'Αρχαία ελληνική ποίηση' --max-pages 3 --dest polytonic
```

Those live commands are examples for a permitted worker run. T4 development
used network only for installing Playwright/Chromium and the recorded Wikisource
fixture. Tests never fetch live sources. A sandbox can prevent an installed
Chromium from launching; browser-dependent tests then skip with the launch reason.

`--sources` accepts catalog names (comma-separated or separate arguments),
HTTP(S) URLs, HTML files and JSON manifests. A manifest is a list or
`{"pages": [...]}` / `{"sources": [...]}`; each entry is a path/URL string or a
mapping with `url` (or `path`), `licence` and optional `source`. Local paths in
manifests resolve relative to the manifest, independently of the working directory.
A mapping can supply `html` directly, with a logical source URL; no remote assets
are fetched for these recorded/generated inputs. `--licence` applies to direct
path/URL inputs; use per-entry licences in manifests. Missing licences remain
`unspecified; rights review required`.

The default viewport is 794 × 1123 CSS pixels, raster scale 2. Options include
`--viewport WIDTHxHEIGHT`, `--scale`, `--no-pdf`, `--no-screenshot`, `--allow-media`,
`--offline` and `--mastodon-instance`. `--max-pages` bounds the number rendered,
including source seeds. Multiple named sources are visited in round-robin order,
so their seed pages precede discovered article links. Random Wikipedia seeds can
resolve to the same article; captures are not deduplicated automatically.

`--interval` controls the per-origin rate (at least one second) and `--timeout`
sets request/navigation timeouts; rich pages may need longer navigation timeouts
because assets are fetched sequentially through the polite gate.

## Capture artifacts and receipts

Each input gets a new numbered/hash directory; existing page directories are
never overwritten by `render_pages`:

| File | Meaning |
| --- | --- |
| `source.html` | Original response bytes, local input bytes, or generated post HTML |
| `rendered.html` | Serialized DOM after stabilization, including capture CSS |
| `page.png` | Full-page screen rendering at the requested device scale |
| `page.pdf` | Chromium A4 print output, background enabled, no browser headers/footers |
| `dom.json` | Screen text nodes and their individual line fragments |
| `print_dom.json` | Independent continuous print DOM, at fractional A4 CSS width |
| `receipt.json` | URLs, UTC fetch time, status, title, lang, licence, UA, browser version, hashes, fonts and capture settings |
| `source.json` | Original public post JSON for a Mastodon-generated page |

PDF margins default to zero; the page's CSS margins and `@page` margin rules
still apply. A4 page size is requested even if the source declares another size.
Chromium embeds the fonts used in its PDF; `document.fonts` faces/statuses and
computed CSS font-family lists are saved in the receipt. System fallback faces
are not necessarily enumerated by `document.fonts`; the receipt does not identify
every resolved glyph font. File and generated HTML inputs have no HTTP status;
HTTP inputs preserve the final response status. For Mastodon-generated pages,
the status refers to the JSON API acquisition, and `api_url` / `api_final_url`
distinguish that response from the post's logical provenance URL.

`greekocr web records DIR` verifies every captured artifact checksum before
extracting labels. It writes `dom_records.jsonl`, PDF page rasters/crops,
`page_records/records.jsonl` and `page_records/agreement.json`. These are derived
outputs and can be regenerated; the original artifacts and receipts are retained.

## What is exact

For every body text node, the capture records its raw text, a stable traversal
ID and either its line IDs or an explicit exclusion reason. A node-wide
`Range.getClientRects()` determines fragments. Grapheme-sized ranges map text
onto those rectangles; offsets are UTF-16 offsets as used by the browser, so
combining marks and non-BMP characters are not split as unrelated glyphs. Lines
carry raw fragment text and NFC labels. Collapsed CSS whitespace is reduced to
its rendered space; `pre`, `pre-wrap` and `break-spaces` retain their whitespace.

DOM boxes are floating point `[left, top, right, bottom]` CSS rectangles plus
page scroll offsets. Multiplication by the capture scale places them in the
full-page PNG's top-origin coordinates. These are browser text/em rectangles,
not tight ink masks. The PDF extractor retains its PDF point boxes, tight glyph
boxes and padded crop boxes in its own 200 dpi page raster. All line records
carry `tier` and `label_tier` = `exact-rendered`, `provenance` = `web_render`,
`source_url` and `licence`.

## What is not exact or covered

Screen rendering and print rendering can reflow text. `print_dom.json` records
continuous print geometry; actual PDF pagination can move lines at page breaks,
apply `@page` margins, repeat fixed headers or split elements. The agreement
report joins adjacent inline DOM fragments for comparison, matches independent
PDF text after NFC and outer whitespace stripping, and computes IoU between PDF
glyph boxes and DOM em boxes converted to a common CSS coordinate system. DOM y
minus preceding A4 heights is an approximation under fragmentation. Reports
retain unmatched lines, low IoU and missing text layers; no PDF text is replaced
by DOM text. `pdf_text_agreement` and `dom_text_coverage` report both directions.
A good text match does not prove identical screen and print geometry.

The tier describes the origin of the labels, not an admission decision. Inspect
agreement before using PDF rows as exact supervision. Clipping is flagged at
screenshot boundaries; overlap/occlusion, overflow clipping, ligatures, missing
glyph fonts, soft hyphens, bidi, rotated/transformed text and unusual print CSS
can require additional review. Hidden nodes and non-content script/style nodes
are excluded explicitly. CSS text-transform and non-horizontal/LTR text are
excluded rather than given invented labels. CSS-generated content, list markers,
canvas, SVG text, form values, shadow DOM and iframe text are outside this text-node
capture. Such pixels can exist in the image without corresponding DOM labels.

Capture fixes locale (`el-GR`), timezone (`UTC`), light color scheme, reduced
motion and viewport; it disables animations/transitions, scripts and service
workers, then awaits `document.fonts.ready`. Consequently script-only content is
not initialized. Default image/media blocking removes network requests for those
resources; allowing media forces lazy images eager and awaits decoding. Layout
is exact for the resulting captured scene, which may differ from a fully loaded
interactive website. External stylesheets/fonts can be blocked by robots or fail;
blocked requests and reasons remain in the receipt. Raster determinism requires
the same HTML/assets, Chromium build, fonts and operating system. PDF timestamps
and receipt fetch times are not asserted byte deterministic.

Rendering is not scanning. Clean screen/PDF pixels omit paper texture, optical
distortion, bleed-through, blur and scanner noise. The `degrade_twins` hook looks
for vendored `page_degrade.py` with a label-preserving `degrade_twins` adapter. This
checkout has no such module, so it returns `status="unavailable"`, a reason and a
copy of the labels; it creates no purported twin. Future geometric degradation
must transform boxes together with the image; photometric degradation may retain
the original boxes. A module without a compatible adapter is also reported as
unavailable, without inventing a calling convention.

## Source catalog, transport and licence posture

`web_sources.source_catalog()` supplies metadata without I/O. `source_pages()`
yields Wikipedia random/featured seeds, Wikisource category pages and article
links, gov.gr, Greek EUR-Lex, three news front pages and same-origin links,
Greek-language Gutenberg catalog/ebook links and Mastodon public JSON posts.
Wikisource categories are caller-selectable; a seed does not guarantee a given
category exists or every linked work is polytonic. Generic same-origin link
discovery is bounded but does not classify every link as an article.

Mastodon selects only `visibility="public"`, preserves author attribution and
the post URL, and converts post HTML into escaped inert text with paragraph/line
breaks. That generated layout is an exact rendering of the saved post JSON; it
does not reproduce the originating site's timeline appearance.

All HTTP(S) navigation, assets, discovery and redirects use the same explicit
per-origin transport. It fetches robots.txt first, respects disallow,
crawl-delay/request-rate and waits at least one second between requests to each
origin. Missing robots (404/410) permits requests; inaccessible/other-error robots
fails closed. Redirect destinations are checked before retrieval. Responses have
timeouts, a byte limit and a redirect bound. Local HTML/recorded generated inputs
never fetch remote assets, and `offline=True` refuses remote inputs.

Licence tags are source hints supplied to receipts, not a rights determination.
Wikipedia/Wikisource attribution, revision and work-specific underlying rights
must be reviewed before distribution/training. Government/EU reuse terms can
have exclusions; news defaults to permission required. Public Mastodon posts are
not automatically licensed. Gutenberg availability does not establish public
domain status in every jurisdiction. Caller-supplied licence strings override
catalog hints for explicit manifest entries, without changing their provenance.

## Verification and recorded fixture

`tests/test_web_render.py` uses three authored offline HTML fixtures: polytonic
prose with combining marks, an administrative layout with inline styles, and a
news/post layout with preserved whitespace. Browser tests check all visible text
nodes, scaled geometry, receipt hashes, embedded PDF font streams, >=95% NFC line
agreement in both directions, and box/PNG determinism across two renders. They
skip only when Playwright/Chromium is absent or the environment prevents launch;
rendering/extraction failures after a successful launch fail the tests.

Source discovery, robots/redirect/rate behavior, direct DOM records, checksum
refusal, degradation and failed-label handling have independent offline tests.
`scripts/capture_web_fixture.py` is a separate explicit network action, never
called from tests. It records one polytonic Wikisource page with source HTML and
a capture receipt under `tests/web_fixtures/wikisource_capture/`, or writes a
skipped receipt if retrieval is unavailable. The receipt binds original response
bytes and status; it is acquisition evidence, not proof of Chromium rendering.
