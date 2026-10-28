# O4a — Wikisource sourcing tool, 6 October 2026

**Cycles 2 and 3 below record the real-fixture fixes and offline replays on 7 October.**
The original Cycle 1 notes are retained as historical context.

Implemented `bench/source_wikisource.py` for `el`, `ru`, `uk`, `bg`, and `sr`.
**Offline unit-tested tool; no live supply result, real-scan qualification, owner
verification, sealed benchmark, or publishable corpus is claimed.** No network,
installs, training, sub-agents, or git history changes were used in this task.

## Why this source

The O4/F04 plan requires deliberate historical Greek and Cyrillic sourcing. O1's
current notes report 3,507 polytonic-feature candidates across 12 documents and 125
Cyrillic candidates across 8 documents, both with zero compliant capped-pool rows.
Polytonic characters alone do not establish historical publication. This tool uses
Index date/year fields for era evidence and keeps unknown/ambiguous dates explicit.
It does not change the existing 2% document cap or select/seal a benchmark.

## Coordinator commands — network-enabled environment only

Run from `~/Projects/greek-page-ocr` using the specified interpreter:

```sh
PYTHON=~/Projects/glossapi-development/.venv-exp/bin/python
"$PYTHON" -m bench.source_wikisource --lang el --max-pages 300 --out bench/runs/O4a_el
"$PYTHON" -m bench.source_wikisource --lang ru --max-pages 300 --out bench/runs/O4a_ru
"$PYTHON" -m bench.source_wikisource --lang uk --max-pages 300 --out bench/runs/O4a_uk
"$PYTHON" -m bench.source_wikisource --lang bg --max-pages 300 --out bench/runs/O4a_bg
"$PYTHON" -m bench.source_wikisource --lang sr --max-pages 300 --out bench/runs/O4a_sr
```

Equivalent requested entry point: `python -m bench.source_wikisource --lang el
--max-pages 300 --out bench/runs/O4a_el`, etc., with this venv active. These commands
were **not run live** here. Start with a 1–3-page smoke on each site before a full
run; inspect the pinned Page transcription against its actual image.

Defaults: up to 1,000 Index pages visited, 10 eligible page attempts per Index,
300 eligible page attempts total, only quality 3/4 processed. Completed cached
pages consume the same limits on resume, so rerunning an identical command does
not append 300 new pages. Increase limits to extend a run. Failed eligible page
attempts also consume the limit, bounding bad-source retry costs. Other quality
levels remain in the visited discovery inventory. The inventory is of existing
Page pages and can be truncated; it is not a complete inventory of every scanned
leaf or every work on the site.

Use `--index 'Index:ACTUAL_FILE.djvu'` (repeatable) to target a verified work; local
namespace titles work, and bare file basenames get the discovered Index namespace.
Do not use the artificial fixture titles. `--pages-per-index 3` increases source
diversity, but fetching 300 pages still does not establish the ≥50 eligible
documents required by the O1 cap. Default listing order is the site's allpages
order; no claim is made that this is a representative historical sample. Check
`summary.json` for documents, era, quality, failures and usable supply.

Add `--user-agent 'GreekPageOCR-O4a/1.0 (research; YOUR_REAL_CONTACT)'` for a live
coordinator run. The built-in agent is descriptive but has no invented contact.
All API calls include `maxlag=5`; one serial HTTP limiter enforces at least one
second between request starts across APIs, images, retries, and redirects. 429,
maxlag and transient failures respect Retry-After/exponential backoff. Each request
has a 120-second timeout and at most four retries. Run these language commands
serially if using the same coordinator/IP; independent processes do not share a
rate limiter. Keep commands on an authorised processing worker if required by the
Mac's execution policy.

**Runtime estimate, not measured live:** DjVu normally needs one imageinfo query
and one image download per selected page, plus Index/Page listing and one file
metadata query per work. For 300 pages / about 30 works, roughly 660 new requests
imply an approximately 11-minute request-start lower bound. Budget 15–45 minutes
per language for transfers, CPU segmentation and ordinary retries; sparse sites,
thumbnail failures and maxlag can take longer or supply fewer than 300 pages.
PDFs download once per book and render each selected leaf locally at 200 dpi;
their bandwidth/CPU cost depends on file sizes. Cache-only resume is usually much
shorter but verifies hashes of all committed crops. No live runtime or supply
projection has been validated.

## API, images, and resolution

Siteinfo discovers canonical Index/Page namespace IDs and local names. The
ProofreadPage `meta=proofreadpageinfo` API is requested where supported; a plain
siteinfo fallback handles absent extension metadata. Standard paginated
`generator=allpages`, `prop=revisions`, `rvslots=main` obtains Index wikitext and
existing Page revisions under each index-file prefix. Quality is taken from the
Page's `<pagequality level="3|4">` header, not inferred from a category. Raw body,
revision IDs, timestamp and last editor are pinned in the page receipt.

File metadata uses `prop=imageinfo` with `url|size|mime|mediatype|metadata|extmetadata`
(plus SHA1, timestamp and uploader). A missing local file triggers Commons lookup.
PDFs use `pypdfium2` to render the physical scan leaf `/N` at `200/72` pixels per
PDF point; the original PDF is cached and SHA256-bound. This certifies render
resolution, not the inherent resolution of embedded scan pixels.

DjVu uses the API thumbnail with `iiurlwidth` and
`iiurlparam=pageN-WIDTHpx`. It first requests at least 4,000 px and at least the
file's reported original width; a larger attested physical page width also raises
the request. Thumbnail failures try descending 4,000/2,500/2,000/1,280/1,024 widths
bounded by that request. Every attempt, returned width, original width and scale
is recorded. Pixels are never enlarged locally. File-level width/DPI can differ
between leaves of a mixed-size volume; reported metadata DPI is therefore flagged
for manual page checking. Unknown DPI, effective resolution below 200, or a
thumbnail exceeding reported native width blocks `candidate_eligible`.

For a **single verified, uniform-size volume**, `--page-width-inches NUMBER` lets
the coordinator attest the actual physical width and calculate thumbnail DPI.
Do not add a guessed width to broad multi-work commands. Resolution controls are
bound into `config.json`; use a fresh output directory when changing them. The
default commands deliberately report unqualified DjVu resolution rather than
silently promising ≥200 dpi for a source with missing metadata.

## Text, segmentation, alignment and admission

The cleaner removes noinclude headers/footers, pagequality tags, comments,
references, links and common formatting markup. It retains nonempty source line
breaks, NFC text and literal end-of-line hyphenation; it never reflows paragraphs,
adds missing hyphens, or joins words. Common formatting/lang templates are
unwrapped. Unknown/nested-unparsed templates or complex markup (tables/math/score)
retain review evidence and block automatic labels. This is a conservative cleaner,
not a complete MediaWiki template expander.

`hyphenation.joined_by_editors` is **null/unknown unless independently established**.
The print comparison required to answer this cannot be inferred from the
transcription alone. HWS/HWE templates yield their printed fragments and record
the editor's joined-word/transclusion arguments separately; a joined transclusion
does not prove that the Page-body transcription joined printed lines. Count
mismatch is recorded as an alignment issue, not claimed as proof of editor
normalisation. Manual comparison is required before exact labels can be sealed.

Line detection reuses `bench.extract_lines.scan_rows` and the repository's
projection/diacritic-band merge; it does not fork O1's detector or schema. It adds
8-connected-component filtering (under 3-pixel specks and near-full-page borders
or rules), tight unions, component counts, and a wide-gap column warning. Original
scan pixels remain in crops and go through O1 `ink_diagnostics` and `overlaps`.
This first scan path assumes horizontal, mostly single-column print: no deskew,
curvature correction or trained detector. Synthetic detection tests measure line
count and boxes; real-scan accuracy remains unmeasured.

Alignment is monotone dynamic programming with text length (combining marks do
not add characters), image width, order and skip penalties. Confidence is an
**uncalibrated heuristic**, not a probability or CER estimate. Per-line proposals,
indices, lengths, unmatched indices and page mean confidence are retained.
Count mismatch or any skipped alignment caps confidence below 0.5. The default
label threshold is 0.75; complex text and detected columns also block labels.
Blocked/low-confidence visual candidates still have crops and proposal evidence,
but `text=''`, so the unchanged O1 `admit` rejects them as `no_text`.

Every detected line uses `real-lines/o1-v1`, O1 features/geometry keys, and **the
same `bench.admission.admit` and named counters**, including control/PUA/duplicate
rules. Duplicates are scoped to the source work, as O1 scopes them to a document.
`bbox_pdf` for thumbnails is the O1 200-dpi geometry adapter, explicitly marked
with `bbox_pdf_basis`; it is not asserted to be original PDF geometry. Crop PNGs,
rejected candidates and overlapping rejection counters are retained. No dictionary
is enabled by default; `--lexicon FILE` feeds the existing dictionary rule.

Two distinct supply counts are intentional:

- `admitted`: O1 text/geometry rules passed; does not certify rights, resolution,
  transcription fidelity or gold status.
- `candidate_eligible`: admitted, quality 3/4, and no recorded source warning.
  Still `status=pending`, with licence review and owner verification outstanding.

Filter on `candidate_eligible` when constructing a provisional supply input for
`bench.pools`; preserve all records and denominators alongside that input. Existing
O1 tools that only filter `admitted` do not apply the extra resolution/source gates.
Neither count establishes publishable lineage. Heading/body size and font style
are left unknown; the detector cannot infer those native-PDF metadata fields.

## Output and resume contract

- `cache/*.body` + `cache/*.json`: content-addressed URL responses with exact raw
  bodies, URL, headers/status, SHA256, fetch timestamp and User-Agent. Failures and
  redirect bodies are preserved under `cache/attempts/`; transient API failures
  never poison the success cache. Redirect aliases point to the cached final body.
- `images/*.png`: rendered/downloaded page images.
- `pages/*.json`: page records, raw/clean transcription, provenance, resolution,
  detection and alignment diagnostics, line counts, record/crop hashes and commit
  marker. These are the page-level coverage receipts.
- `records/*.jsonl`: all O1-compatible candidate rows; `crops/WORK/*.png` includes
  rejected lines. One records file per page; `doc` remains stable across its work.
- `summary.json`: language × era × quality supply, distinct documents, overlapping
  admission counters, page warning counts, visited Index inventory and errors.
- `config.json`, `site.json`: source-code/settings hashes and namespace/rights data.

Page receipt commit markers are written last, with atomic replacement of records
and receipts. A resume checks records, page image and every crop hash before
skipping a page. Missing/corrupt artifacts are rebuilt from cache; previous
admitted hashes restore the per-work duplicate state. Code, language, confidence,
resolution or lexicon changes require a fresh `--out`. Stop limits/index selection
may change, but summaries describe the current selection; older unselected files
can remain in the directory. Use a fresh output for a different selection intended
for downstream globbing, or select only the current `summary.json.page_ids`.

Repeat a live command to resume network-enabled work. To strictly replay only
already cached inputs:

```sh
"$PYTHON" -m bench.source_wikisource --lang el --max-pages 300 --out bench/runs/O4a_el --offline
```

Offline cache misses never call a transport. Increasing limits can introduce new
uncached requests and requires a network-enabled resume. Cache is intentionally an
immutable source snapshot; start a new output directory to refresh live revisions.
Page failures are recorded and produce exit status 1; empty qualified supply can
exit 0 and must be detected in the summary. A single process should own an output
directory; concurrent writers to the same directory are unsupported.

## Licence and attribution

Text licence is the live site's `rightsinfo`; scan licence is Commons/local
`extmetadata` (`LicenseShortName`, URL, usage terms, artist, credit, attribution,
copyright and attribution requirement). These are separate licences. The tool
stores all raw file licence metadata and never infers public domain from the year
alone. Missing licence metadata is flagged. Nonempty metadata is evidence, not an
automatic copyright determination or publishable-lineage approval.

Line provenance links the work/Index, exact Page revision, page history (full
contributor attribution), last editor, file description, uploader/timestamp and
file SHA1; page/PDF images and output artifacts are SHA256-bound. Preserve those
links and the applicable attribution/share-alike notices when redistributing text
or derived datasets. Review scan ownership and licence compatibility separately
before training any publishable weights. No external messages/submissions were
sent and no licence approval was obtained.

## Executed validation and remaining gap

The fixture tree contains two API-shaped JSON envelopes, one PIL page PNG and one
transcription per language, plus a reproducible generator and provenance record.
**These are modeled offline fixtures, not recorded Wikisource responses.** No
recordings were supplied/found in the repo and network was prohibited. The precise
requested recorded-fixture/real-scan acceptance condition remains pending with
the network-enabled coordinator; these tests do not qualify live API semantics.

Executed from the repository using the requested Python:

```sh
"$PYTHON" bench/tests/fixtures/wikisource/make_fixtures.py
"$PYTHON" -m pytest bench/tests/test_source_wikisource.py bench/tests/test_admission.py bench/tests/test_tools.py -q
"$PYTHON" -m bench.source_wikisource --help
```

The combined suite passed **75 tests**. The sourcing suite contributes 36 cases,
including five language end-to-end cases, PIL polytonic segmentation and diacritic
retention, length/order alignment, same-count skips, paragraph/line mismatch,
unknown templates, existing PUA/control/duplicate rules and overlapping counters,
empty/column pages, API continuation/extension/Commons fallbacks, maxlag/429 and
redirect caching/rate limits, malformed-JSON retries, PDFium 200-dpi rendering, thumbnail fallback, DPI and
licence warnings, limits/source diversity, expanded runs, offline CLI replay and
corrupt-crop repair. Those tests use injected transports; no live HTTP is called.
The five synthetic page cases each produced 3 admitted eligible pending lines
under an artificial attested width, **15 total synthetic lines**, with confidence
above 0.9. This is a functional result, not historical supply or verified gold.

Before reporting live supply, the coordinator must retain genuine response/page
fixtures for each language, inspect image-to-Page association and ≥200-dpi evidence,
measure segmentation/alignment on actual scan samples, resolve normalised line
breaks/hyphenation manually, and review licences. O2 owner verification and sealing
remain separate tasks.

## Cycle 2 — real recorded responses, 7 October 2026

This section supersedes Cycle 1's synthetic-only validation and no-reflow
limitations above. Worked entirely offline on the coordinator's
`bench/runs/O4a_el_probe/` and `bench/runs/O4a_ru_probe/`; no network, installs,
sub-agents or git-history changes. Did not edit `bench/extract_lines.py`,
`bench/admission.py` or `bench/pools.py`. No admission API change was needed: the
scan/PDF geometry adapter and label gate live in `source_wikisource.py`, and the
existing `admit` still supplies the named rejection counters.

What was wrong and what changed:

- Greek uses actual namespace IDs **102 / 100**, local names **Μεταγραφή / Σελίδα**.
  Canonical namespace discovery already worked and remains unchanged. Recorded
  discovery still yields **Ἀτθίδες Αὖραι**, **1883**. Its DjVu page JPEGs were
  rejected solely because `thumb.wikimedia.org` was absent from the allowlist.
  Both thumbnail hosts now work. Media URL cleanup removes `utm_*` and known
  analytics IDs, preserving width/page/render query arguments and the `1920px`
  path. Old tracked cache entries remain readable. The recorded API sometimes
  advertises `thumbwidth=4000` while selecting a `1280px` URL: try a 1920px render
  before that lower bucket, retain fallback, and use decoded pixel dimensions
  for resolution rather than trusting the advertised width. No local upsampling.
- Russian bodies generally contain paragraphs, not one transcription line per
  printed line. Global count mismatch used to cap every alignment below 0.5,
  and the label gate cleared every `text`. Common Russian formatting templates
  were also incorrectly unknown. Cleanup now handles `razr/razr2/razs`, `цсл`,
  `ВАР` (printed first argument), `опечатка` (printed erroneous first argument),
  spacing/size/alignment templates, acute/grave marks and `ё`. `Перенос` keeps
  the printed start plus hyphen; **`Перенос2` keeps the second, continuation
  argument**. Noinclude headers/footers remain excluded; unknown templates still
  block labels. Paragraph boundaries and raw revision evidence are retained.
- Added paragraph reflow when the visual indentation groups match **every** source
  paragraph and paragraph ink/text width scales agree within the explicit gate.
  Estimate nonspace glyph widths with the existing DejaVu Serif font and distribute
  text by cumulative image ink width, selecting existing word boundaries. A first
  review exposed short-word drift in this width-only proposal; a separate scan
  word-count and relative-word-width signature now rejects those cases. Detected
  end hyphens, including strokes touching the preceding glyph, and inferred
  within-word breaks block both adjoining lines. Missing anchors, internal
  suspicious bands, body references/footnotes removed from transcription, unknown
  markup and persistent column gutters also block automatic labels. Proposals,
  character spans, word counts, width errors, per-line confidence and
  `alignment_block_reason` remain inspectable even when `text` is cleared.
- Detection now filters long scan scratches/rules and out-of-frame specks, assigns
  components by their vertical centres to prevent expansion into neighbouring
  lines, and requires a repeated gutter before calling a page multi-column.
  This reduces false column warnings on isolated headers/short lines. Genuine
  column pages remain blocked; there is no claimed two-column reading-order
  solution, deskew or OCR-based semantic comparison.

The baseline actually supplied on disk differs from the task's reported 1,815
Russian candidates: its selected 30-page summary and receipts total **1,101**.
The following comparison uses those immutable on-disk artifacts. Segmentation
changed, so candidate denominators differ; all 30 original page IDs and original
image hashes are preserved by replay.

| Recorded selection | Before | Cycle 2 |
| --- | ---: | ---: |
| Russian processed pages / documents | 30 / 5 | 30 / 5 |
| Russian detected candidates | 1,101 | 1,114 |
| Russian admitted pending candidates | 0 | **80** |
| Russian rejected candidates | 1,101 | 1,034 |
| Russian candidate_eligible / verified gold | 0 / 0 | **0 / 0** |
| Greek processed pages / admitted | 0 / 0 | **0 / 0** |
| New HTTP requests in either replay | — | **0** |

Top Russian O1 rejection counts (overlapping, not a partition):

| Reason | Before | Cycle 2 |
| --- | ---: | ---: |
| no_text | 1,101 | **1,034** |
| overlapping_lines | 77 | 26 |
| ink_bbox_mismatch | 1 | 13 |
| aspect_ratio | 15 | 7 |
| crop_height | 43 | 3 |
| multiline_ink | 16 | 3 |

Page diagnostics: 12 pages have unaligned printed references, 5 have internal
nonbody bands, 4 have paragraph-anchor count mismatch. Nine have no page alignment
failure, including the empty-body page (which supplies no text); eight contribute
admitted lines. Six retain unknown-template flags. Remaining noise and geometry
failures are retained in the denominator, including untranscribed artwork/noise.

**Confidence is an uncalibrated alignment heuristic, not text correctness.**
The default threshold remains 0.75. The 40-line contact-sheet inspection found
that widths can establish matching line boundaries while editor spelling or
punctuation differs: e.g. `ru-a4a4e574991bc672-p0011-l0031` has recorded
`усиливающегося` versus printed `усиливающагося`. The tool preserves the pinned
transcription; it does not silently correct it. All paragraph-reflow pages retain
`line_count_mismatch` in source flags, so **candidate_eligible remains zero** even
for the 80 geometrically admitted, aligned pending candidates. Exact transcription
fidelity, owner review, resolution/rights suitability and gold sealing remain
unresolved. Do not feed these as verified exact labels.

Artifacts:

- `bench/runs/O4a_ru_cycle2/summary.json`, `pages/`, `records/`, `crops/`: final
  30-page replay; page images reference the unchanged original probe images.
- `bench/runs/O4a_ru_cycle2/contact_sheets/sheet-01.png` through `sheet-04.png`:
  **40 admitted lines**, image plus full aligned text, IDs and confidence.
  `index.html` provides individual crops; `lines.json` supplies their provenance.
  All four final PNG sheets were visually inspected here; coordinator review is
  still pending.
- `bench/runs/O4a_el_cycle2/summary.json`: 30 eligible attempts, 0 processed pages,
  0 HTTP requests, 70 API cache hits. Exit status **1** is expected because image
  payloads are absent. Greek has **zero recorded PNGs and no cached downloaded
  page-image bytes**, so no Greek contact-sheet PNG can be produced offline.
- `bench/tests/fixtures/wikisource_recorded/`: real Greek siteinfo/index responses,
  an identified imageinfo excerpt with URL fields unchanged, and two real Russian
  page/transcription excerpts plus unchanged PNGs. `provenance.json` distinguishes
  excerpts from complete responses and binds original paths/response/image hashes.

Exact executed offline commands (output directories were fresh):

```sh
PYTHON=~/Projects/glossapi-development/.venv-exp/bin/python
"$PYTHON" -m bench.source_wikisource --lang ru --replay-from bench/runs/O4a_ru_probe --out bench/runs/O4a_ru_cycle2 --contact-sheet-lines 40
"$PYTHON" -m bench.source_wikisource --lang el --replay-from bench/runs/O4a_el_probe --out bench/runs/O4a_el_cycle2 --contact-sheet-lines 40
"$PYTHON" -m pytest bench/tests/test_source_wikisource.py bench/tests/test_admission.py bench/tests/test_tools.py -q
```

**82 tests passed** (43 sourcing cases). Tests include real namespace/discovery
and thumbnail URLs, tracking removal with width preservation, 1920px preference,
old tracked-cache compatibility, Russian template continuation, actual paragraph
reflow, actual short-word drift rejection, plus the complete recorded 30-page
replay with HTTP forbidden and a 40-line contact-sheet/receipt integrity check.
Greek URL/download tests use an injected JPEG for transport; this is not a claim
that real Greek page-image bytes were available or downloaded.

To repeat the offline replay, choose a **new** `--out` (e.g.
`bench/runs/O4a_ru_cycle2_replay2`); `--replay-from` always forbids network and
requires a fresh output. The recorded probe is never rewritten.

Exact coordinator live rerun commands, **not executed here**:

```sh
PYTHON=~/Projects/glossapi-development/.venv-exp/bin/python
"$PYTHON" -m bench.source_wikisource --lang el --max-pages 30 --out bench/runs/O4a_el_cycle2_live --contact-sheet-lines 40
"$PYTHON" -m bench.source_wikisource --lang ru --max-pages 30 --out bench/runs/O4a_ru_cycle2_live --contact-sheet-lines 40
```

Run serially with fresh output directories; optionally add the coordinator's real
contact User-Agent. Do not reuse the old probe's code-bound config or invent an
attested physical width for unrelated DjVu volumes.

## Cycle 3 — Greek alignment on recorded real pages, 7 October 2026

Worked offline on the coordinator's `bench/runs/O4a_el_probe2/`: **30 genuine
downloaded images, 5 documents, 589 detected candidates**, initially all rejected
as `no_text`. No network, installs, sub-agents or git history changes. The original
probe was not rewritten. Hash checks confirm `bench/extract_lines.py`,
`bench/admission.py` and `bench/pools.py` are unchanged.

Diagnosis: the recorded `Σελίδα:` bodies predominantly contain `<poem>` with
explicit verse breaks, colon indentation, and Greek formatting aliases. The
cleaner treated colons as unsupported lists and aliases as unknown templates.
Extra printed folios, running headers and scan dirt caused line-count mismatch;
the paragraph fallback then mistook stanzas/verse indentation for prose anchors
and blocked labels globally. Namespace discovery was already correct.

Changes in `bench/source_wikisource.py`:

- Preserve explicit poem boundaries and newlines, remove indentation colons only
  inside poems, unwrap known `κέντρο`, `δεξιά`, `κσγ`, `κενό στα γράμματα`, size,
  and block formatting. Remove known spacing/rule templates without generating
  text. Retain printed `fr` verse numbers. Only unwrap the exact single-cell
  `align=center` table wrapper; complex tables, `iwpage`, unparsed and unknown
  templates remain blocked. Headers/footers in noinclude remain excluded.
- Route explicit verse to monotone DP with independent scan word counts and
  relative word widths. Every source line must have a placement; additional
  visual bands may remain unlabelled. Per-line gates require RMS log word-width
  error ≤0.18, maximum residual ≤0.45, line-width log error ≤0.25 and alternative
  placement cost margin ≥0.35. Ambiguous or mismatched proposals stay inspectable
  with confidence below 0.5; the unchanged label threshold is 0.75. A missing
  printed end hyphen blocks that verse label. No verse reflow or invented hyphens.
- Preserve Cycle 2's paragraph reflow and word-signature fallback for prose.
  Removed body references block automatic labels in either path. NFC preserves
  polytonic accents; no accent stripping, spelling correction or word joining.
- Add `orthography_flag` plus evidence in each page receipt and line provenance.
  It counts Greek letters with breathings, grave, circumflex or iota subscript
  via canonical decomposition. For sufficiently long lowercase Greek text,
  absence of those marks before 1982 yields `possible_modernisation` and an extra
  source warning. Acute alone is not polytonic evidence. Short/uppercase titles
  and unknown eras receive separate uncertainty flags. This is a transcription
  heuristic, not evidence of printed orthography or editor intent.

Final executed replay, identical candidate denominator and original image hashes:

| Measure | Probe2 before | Cycle 3 after |
| --- | ---: | ---: |
| Processed pages / documents | 30 / 5 | 30 / 5 |
| Detected candidates | 589 | 589 |
| Admitted pending lines | 0 | **248** |
| Rejected candidates | 589 | **341** |
| Candidate eligible / verified gold | 0 / 0 | **0 / 0** |
| Pages contributing admitted lines | 0 | **21** |

O1 rejection counters overlap; they are not a partition of the 341 rejections:

| Reason | Before | After |
| --- | ---: | ---: |
| no_text | 589 | **326** |
| overlapping_lines | 33 | 33 |
| aspect_ratio | 23 | 23 |
| ink_bbox_mismatch | 11 | 11 |
| control | 0 | 9 |
| crop_height | 8 | 8 |
| near_duplicate | 0 | 3 |
| multiline_ink | 1 | 1 |

The 326 unlabelled candidates include 109 markup-blocked bands, 86 word-count
mismatches, 55 extra visual bands, 26 paragraph-anchor mismatches, 20 internal
nonbody bands, 13 on the page with too many source lines, 8 word-width mismatches,
8 untranscribed end-hyphen detections and 1 outside the prose body. Fifteen of the
263 labelled proposals fail other O1 rules. Nine control rejections come from
recorded tabs; the cleaner deliberately preserves non-newline controls for O1.

All 30 pages retain `dpi_unknown`; 24 retain `thumbnail_exceeds_file_width`, and
27 retain `line_count_mismatch`. These are still pending alignment candidates,
not eligible exact labels. Orthography results: 25
`polytonic_present_review_required`, 3 `insufficient_greek_text`, 2
`insufficient_case_evidence`. No page triggered `possible_modernisation`; that
does **not** exclude modernised spelling. Polytonic transcriptions can still
modernise historical forms or punctuation. Visual review found punctuation
differences, e.g. `el-c6e556f977ffbb89-p0012-l0007` includes a transcription comma
after `καταίβω` absent in the scan. Keep pinned transcription unchanged; exact
fidelity and editor modernisation require manual print comparison.

Artifacts in `bench/runs/O4a_el_cycle3/`: `summary.json`, `pages/`, `records/`,
`crops/`, and `validation.json`. `contact_sheets/sheet-01.png` through
`sheet-04.png` contain **40 admitted lines** with crops, full text, IDs and
confidence; `index.html` and `lines.json` retain individual review/provenance.
All four final PNG sheets were visually inspected here. This was a qualitative
boundary/punctuation review, not a CER measurement or gold verification.

Added four unchanged real Greek PNGs and source/transcription excerpts under
`bench/tests/fixtures/wikisource_recorded/`; `provenance.json` binds the original
receipt/image hashes. Tests cover actual verse cleanup and placement, extra
folio/noise bands, source-line shortage, ambiguity, missing hyphens, unknown
markup, body-reference blocking, NFC orthography evidence, retained Russian
prose fallback, full offline Greek replay, contact sheets and receipt integrity.

Executed commands using the existing interpreter (no installs):

```sh
PYTHON=~/Projects/glossapi-development/.venv-exp/bin/python
"$PYTHON" -m bench.source_wikisource --lang el --replay-from bench/runs/O4a_el_probe2 --out bench/runs/O4a_el_cycle3_trial --contact-sheet-lines 40
"$PYTHON" -m bench.source_wikisource --lang el --replay-from bench/runs/O4a_el_probe2 --out bench/runs/O4a_el_cycle3 --contact-sheet-lines 40
"$PYTHON" -m pytest bench/tests/test_source_wikisource.py bench/tests/test_admission.py bench/tests/test_tools.py -q
```

The final replay exited **0**, reported **0 HTTP requests**, no errors and
**8.90 seconds** runtime. The combined final suite passed **90 tests**. Separate
artifact validation verified all 30 original and all 30 replay receipts/crop
hashes, identical source image hashes/resolution evidence, matching code hashes,
and 40 distinct review-line IDs. No live fetch or source qualification is claimed.

## Scale — 7 October 2026

**Targets not reached. Live sourcing was blocked by the execution environment.**
All five Python Wikisource site probes failed DNS resolution (`[Errno 8] nodename
nor servname provided, or not known`); the initial 20 failed attempts and their bodies/receipts
are retained under `bench/runs/O4a_scale_2026-10-07/cache/attempts/`. The JavaScript
fetch also failed, the web tool could not retrieve the API/category pages, and
no enabled browser was available. There were **zero successful new live downloads**.
A final Greek/Russian reachability check also failed the same DNS lookup
(4 more cached failed attempts, `final_network_probe.json`; 24 total).
No network destination outside Wikisource/Commons was contacted.

The usable fallback was the immutable coordinator cache from `O4a_el_probe2`
and `O4a_ru_probe`, copied with SHA256 verification into the **single shared
`O4a_scale_2026-10-07/cache/`**. `cache_imports.json` records the original paths,
hashes and fetch timestamps. These are old recorded observations, not current
Wikisource availability. Cached supply was exhausted; the run stopped because
new sourcing was inaccessible, before the 90-minute ceiling (approximately
17 minutes for implementation, processing, review and reporting). This is an
explicit environmental stop, not a claim that either requested target was met.
`execution.json` records the timing and failed-probe evidence.

The authoritative output is **`bench/runs/O4a_scale_2026-10-07/final/`**.
The parent directory also retains the first attempt and its successful offline
resume; those are not additional supply and must not be globbed into the pool.

| Family | Requested lines / works | Processed pages | Candidates | Admitted target-script lines | Contributing works / editions | Line shortfall |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| Greek | 3000 / 40 | 29 | 576 | **248** | **3 / 3** | 2752 |
| Cyrillic | 1500 / 40 | 129 | 5080 | **330** | **1 / 3** | 1170 |

Greek remains **248**, equal to Cycle 3. Its denominator is 576 instead of 589:
the ambiguous-year Komotini postcard (13 candidates, no admitted lines) was
excluded by the era gate. Russian grew from Cycle 2's 80 to **330 Cyrillic lines**
(+250), by rendering more pages of the already cached complete PDFs. Russian
has 332 admitted rows in total; two predominantly Latin lines are excluded from
the Cyrillic target and its supply file. All scripts together: **580 admitted /
5,656 candidates**, 5,076 rejected, **0 candidate-eligible / 0 verified gold**.

### Discovery committed before scan requests

`--scale` completes discovery for every selected language and writes its
`discovery.json` and `discovery.md` before requesting any scan. Revision-shaped
Page objects are embedded in the manifest, so download/admission uses the exact
recorded transcription and quality tag. Only levels **3 (proofread) / 4
(validated)**, numeric scan pages and explicitly dated **1800–1930 editions**
enter scale processing. The year describes the printed edition, not the ancient
author. Typeface age is inferred for selection from that edition year and remains
a visual-review item; it is not automatically certified from the year.

Live discovery enumerates Index metadata, groups serials/volumes, and explores
one edition per work before returning to other editions; title-based genre hints
support variety but are explicitly unverified. Scans are sampled in rounds over
work groups. Metadata and every status page count precede the media phase.
Incomplete cached pagination is marked **lower bound**, requiring an unbroken
initial-to-terminal continuation chain before a count is labelled complete.

The full pre-download inventories list **47 Greek Index files and 50 Russian
Index files**, not 97 distinct qualified works:
[Greek inventory](../../bench/runs/O4a_scale_2026-10-07/final/el/discovery.md),
[Russian inventory](../../bench/runs/O4a_scale_2026-10-07/final/ru/discovery.md).
Of these, 38 Greek / 46 Russian editions have an admitted-era metadata year,
but the cache proves Q3/Q4 pages for only **4 Greek works / 1 Russian work**.
Other catalog entries with zero *observed* pages remain unassessed; they are not
proved empty or unproofread. Ukrainian, Bulgarian and Serbian have no recorded
site/status inventory here and could not be queried live: availability is
**unknown**, not zero. Legal/scientific/religious titles exist in the Greek Index
metadata, but no qualifying Page observations for them were available in this
cache. No genre diversity is claimed for the admitted collection.

The following are the actual observed Q3/Q4 candidate editions, listed before
downloads in the manifests. Counts describe existing Page revisions encountered,
not a complete physical-volume page count. `partial` is a lower bound.

| Site | Exact Index file / edition | Year | Pages observed | Q3 | Q4 | Coverage | Era accepted? |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| el | `Athides Aurai Georgios Vizyinos.djvu` | 1883 | 50 | 0 | 49 | partial | yes |
| el | `Manussos.djvu` | 1876 | 50 | 24 | 18 | partial | yes |
| el | `Homère - Odyssée, I-IV, traduction Sommer, juxta, 1886.djvu` | 1886 | 6 | 3 | 0 | complete | yes |
| el | `1910-1920 Gumurdjina Komotini Thrace.djvu` | ambiguous | 1 | 1 | 0 | complete | no |
| el | `Hesiodi Carmina (1908).djvu` | 1908 | 100 | 5 | 2 | partial | yes |
| ru | `1870, Russkaya starina, Vol 1. №1-6.pdf` | 1870 | 50 | 44 | 6 | partial | yes |
| ru | `1870, Russkaya starina, Vol 2. №7-12 and table of contents vol. 1-2.pdf` | 1870 | 50 | 28 | 0 | partial | yes |
| ru | `1871, Russkaya starina, Vol 3. №1-6.pdf` | 1871 | 63 | 1 | 0 | complete | yes |
| ru | `1872, Russkaya starina, Vol 6. №7-12 and table of contents vol. 5,6.pdf` | 1872 | 2 | 2 | 0 | complete | yes |
| ru | `1874, Russkaya starina, Vol 9. №1-4.pdf` | 1874 | 50 | 48 | 0 | partial | yes |

### Per-edition processing and rejection accounting

`admitted` below includes all scripts; `target` counts labels with at least half
of their alphabetic characters in the requested script. Work grouping merges
**all Russkaya starina volumes into one work**, including the 40 catalogued
volumes; they cannot masquerade as 40 works or enter different proposed splits.
The three contributing Greek groups are *Ἀτθίδες Αὖραι*, *Λυρικά ποιήματα,
Αναμνήσεις*, and *Hesiodi Carmina*. *Οδύσσεια I–IV* contributes no admitted rows.
Every individual named rejection counter and alignment block is in
`final/summary.json.works`; counters overlap and are not a partition.

| Site / edition | Pages | Candidates | Admitted | Target | Failed image attempts | Nonzero rejection counters |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| el / `Athides Aurai Georgios Vizyinos.djvu` | 10 | 174 | 107 | 107 | 39 | crop_height=3, aspect_ratio=10, overlapping_lines=9, ink_bbox_mismatch=6, near_duplicate=3, no_text=64 |
| el / `Manussos.djvu` | 10 | 208 | 105 | 105 | 32 | aspect_ratio=10, overlapping_lines=14, ink_bbox_mismatch=1, multiline_ink=1, no_text=100 |
| el / `Homère - Odyssée, I-IV, traduction Sommer, juxta, 1886.djvu` | 3 | 85 | 0 | 0 | 0 | no_text=85 |
| el / `Hesiodi Carmina (1908).djvu` | 6 | 109 | 36 | 36 | 1 | control=9, crop_height=1, aspect_ratio=2, overlapping_lines=6, ink_bbox_mismatch=3, no_text=64 |
| ru / `1870, Russkaya starina, Vol 1. №1-6.pdf` | 50 | 1965 | 125 | 123 | 0 | aspect_ratio=8, overlapping_lines=30, ink_bbox_mismatch=8, multiline_ink=3, no_text=1840 |
| ru / `1870, Russkaya starina, Vol 2. №7-12 and table of contents vol. 1-2.pdf` | 28 | 1117 | 53 | 53 | 0 | crop_height=1, aspect_ratio=1, overlapping_lines=25, multiline_ink=1, no_text=1064 |
| ru / `1871, Russkaya starina, Vol 3. №1-6.pdf` | 1 | 18 | 0 | 0 | 0 | crop_height=3, aspect_ratio=5, overlapping_lines=9, ink_bbox_mismatch=12, no_text=18 |
| ru / `1872, Russkaya starina, Vol 6. №7-12 and table of contents vol. 5,6.pdf` | 2 | 63 | 0 | 0 | 0 | overlapping_lines=2, no_text=63 |
| ru / `1874, Russkaya starina, Vol 9. №1-4.pdf` | 48 | 1917 | 154 | 154 | 0 | aspect_ratio=3, overlapping_lines=25, ink_bbox_mismatch=6, multiline_ink=3, no_text=1763 |

All 129 Russian Q3/Q4 pages in the cache processed successfully. Greek attempted
all 101 era-qualified Q3/Q4 observations: **29 processed / 72 cache misses**
(39 Athides, 32 Manussos, 1 Hesiod). There are 75 final summary errors: these
72 missing-image attempts plus the 3 languages with no recorded siteinfo. Exit
status **1** is intentional for that incomplete supply. Final sourcing made
**0 HTTP requests** and took approximately **41 seconds**.

The largest alignment blocks were:

| Block | Greek bands | Russian bands |
| --- | ---: | ---: |
| `printed_references_unaligned` | 0 | 1995 |
| `paragraph_anchor_count_mismatch` | 26 | 835 |
| `internal_nonbody_band` | 20 | 649 |
| `word_signature_count_mismatch` | 86 | 362 |
| `possible_print_hyphenation` | 0 | 417 |
| `markup_flags` | 109 | 173 |
| `word_signature_width_mismatch` | 8 | 181 |
| `paragraph_width_scale_inconsistent` | 0 | 70 |
| `outside_anchored_body` | 1 | 56 |
| `untranscribed_visual_band` | 55 | 0 |
| `anchored_word_boundaries` | 0 | 10 |
| `untranscribed_print_hyphen` | 8 | 0 |

### Codec, orthography, pools and split groups

The existing O1 geometry/admission rules and **0.75** confidence threshold were
retained. Added a whole-label codec-v2 gate after admission's separator/lunate
label policy: unsupported atoms produce `codec_unknown`, preserving both
`text_raw` and normalized `text`; no UNK replacement or inventory extension.
All 580 admitted rows encode/decode exactly under the frozen codec. No extra
codec rejection was needed for this recorded selection. Every page retains raw
wikitext and cleaned transcription, every crop retains its proposed text and
alignment evidence, and all original label variants remain available. Printed
text is not invented where a visual transcription has not been made.

Page-level `orthography_flag` remains a **transcription risk heuristic**. Greek
pages: 24 `polytonic_present_review_required`, 3 `insufficient_greek_text`,
2 `insufficient_case_evidence`. Russian pages: 128
`historical_forms_present_review_required`, 1 `insufficient_cyrillic_text`.
The Cyrillic heuristic now detects Russian legacy letters/final hard signs and
flags possible modernisation when a sufficiently long pre-reform Russian or
Bulgarian transcription lacks historical signals; Ukrainian/Serbian absence
is kept uncertain. Historical letters elsewhere on a page do not prove that
all its words/punctuation match print. The review below found local differences
despite historical/polytonic flags.

`final/pools/el.supply.jsonl` contains **248** pending lines from 3 work groups;
`cyrillic.supply.jsonl` contains **330** from 1. Stable work hashes propose
train/dev/test membership, with every edition of a work in one group. Cross-work
duplicate labels are quarantined; none occurred here. Cross-site translations,
composite collections and title aliases still require identity review before
sealing a split. `doc` is the work ID in pool rows; `edition_doc` preserves the
original scan edition ID. These are pending source-disjoint planning files.

The existing **strict ≤2% per-source cap** was applied at **work**, rather than
edition, level. That cap requires at least **50 contributing works**, stronger
than the requested 40-work discovery target. Consequently both capped `.jsonl`
pools are **empty**. This is sparse supply, not a usable balanced training pool.
No gold sealing or training took place.

| Family | Pending test (lines / works) | Pending dev | Pending train | Capped pool |
| --- | --- | --- | --- | ---: |
| Greek | 0 / 0 | 105 / 1 | 143 / 2 | 0 |
| Cyrillic | 0 / 0 | 330 / 1 | 0 / 0 | 0 |

### Contact-sheet inspection: 3 × 40 per family

Produced **six sheets, 240 distinct sampled line IDs**. All six original full
PNGs were visually inspected; the final six PNGs are SHA256-identical to those
inspected images (`final/validation.json`). Individual crops for the examples
below were also viewed. Greek sampling covers all 3 contributing works (42,
42, 36 lines); every sheet contains all three. Cyrillic sampling covers all
3 contributing editions (42, 26, 52 lines) but **only one distinct work**; every
sheet includes all three editions. The requested across-40-work review diversity
could not be met. Sampling uses round-robin work groups and stable hashed IDs,
not repeated copies of the same lines.

[Greek sheets / individual review](../../bench/runs/O4a_scale_2026-10-07/final/review/el/contact_sheets/index.html)
and [Cyrillic sheets / individual review](../../bench/runs/O4a_scale_2026-10-07/final/review/cyrillic/contact_sheets/index.html)
retain full labels, IDs, confidence, both text variants and pinned provenance.
`lines.json` records exact sheet membership. Sheet filenames are `sheet-01.png`
through `sheet-03.png`, **40 lines each**, in each contact-sheet directory.

Visual findings: polytonic accents and Cyrillic legacy letters are visibly
retained, and most sampled crops show a plausible single printed line with
matching line boundaries. Greek Manussos type is heavily inked; Athides has
weak/faded letter strokes; Hesiod's crops have grey scan backgrounds and italic
letterforms. Those conditions limit exact character review. No obvious gross
line-order shift, clipped whole word or adjacent full text line was seen in these
samples. This qualitative inspection is **not** a CER measurement or label
certification. Clear differences remain:

| Line ID | Pinned label fragment | Observed crop fragment | Defect |
| --- | --- | --- | --- |
| `el-c6e556f977ffbb89-p0012-l0007` | `καταίβω,` | `καταίβω` | Extra transcription comma (Greek sheet 2). |
| `ru-0794838327d81941-p0120-l0027` | `Пугачёва...` | `Пугачева....` | Added diaeresis and altered dot count (Cyrillic sheet 1). |
| `ru-a4a4e574991bc672-p0124-l0038` | `цѣлью,` | `цѣлью.` | Comma versus period (Cyrillic sheet 1). |

`final/review/defects.json` adds manual per-line `orthography_flag` annotations,
keeps `text_raw`, `text`, the observed print transcription for these **individual
crops only**, their pinned Page revisions and crop hashes. The observations do
not establish editor intent or authorise changing source text, and do not rewrite
admission or pools. In particular the added ё is an observed editorial accent
difference, not proof of a wholesale spelling reform. These are further reasons
for keeping all rows pending.

### Reproducibility and licensing

`final/provenance.json` lists each processed work/edition, exact Index revision,
**every numeric page and Page revision ID**, quality level, revision URL, file
name, file timestamp, file SHA1, image/record SHA256, orthography flag, and separate
text/scan licence metadata. `pages/` additionally retains raw Page wikitext,
last editor and page-history attribution links; `records/` carries that provenance
for every line. `config.json` hashes the sourcing, codec, pool, admission,
segmentation and geometry code. No live revision was substituted for a recorded
one. The processed filenames and Index revisions are:

| Site | Exact Commons file name | Index revision | Year | Recorded scan licence |
| --- | --- | ---: | ---: | --- |
| el | `Athides Aurai Georgios Vizyinos.djvu` | [111713](https://el.wikisource.org/w/index.php?title=%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CF%81%CE%B1%CF%86%CE%AE%3AAthides+Aurai+Georgios+Vizyinos.djvu&oldid=111713) | 1883 | Public domain |
| el | `Manussos.djvu` | [142608](https://el.wikisource.org/w/index.php?title=%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CF%81%CE%B1%CF%86%CE%AE%3AManussos.djvu&oldid=142608) | 1876 | Public domain |
| el | `Homère - Odyssée, I-IV, traduction Sommer, juxta, 1886.djvu` | [129623](https://el.wikisource.org/w/index.php?title=%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CF%81%CE%B1%CF%86%CE%AE%3AHom%C3%A8re+-+Odyss%C3%A9e%2C+I-IV%2C+traduction+Sommer%2C+juxta%2C+1886.djvu&oldid=129623) | 1886 | Public domain |
| el | `Hesiodi Carmina (1908).djvu` | [142636](https://el.wikisource.org/w/index.php?title=%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CF%81%CE%B1%CF%86%CE%AE%3AHesiodi+Carmina+%281908%29.djvu&oldid=142636) | 1908 | Public domain |
| ru | `1870, Russkaya starina, Vol 1. №1-6.pdf` | [5524509](https://ru.wikisource.org/w/index.php?title=%D0%98%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%3A1870%2C+Russkaya+starina%2C+Vol+1.+%E2%84%961-6.pdf&oldid=5524509) | 1870 | Public domain |
| ru | `1870, Russkaya starina, Vol 2. №7-12 and table of contents vol. 1-2.pdf` | [5688571](https://ru.wikisource.org/w/index.php?title=%D0%98%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%3A1870%2C+Russkaya+starina%2C+Vol+2.+%E2%84%967-12+and+table+of+contents+vol.+1-2.pdf&oldid=5688571) | 1870 | Public domain |
| ru | `1871, Russkaya starina, Vol 3. №1-6.pdf` | [5688572](https://ru.wikisource.org/w/index.php?title=%D0%98%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%3A1871%2C+Russkaya+starina%2C+Vol+3.+%E2%84%961-6.pdf&oldid=5688572) | 1871 | Public domain |
| ru | `1872, Russkaya starina, Vol 6. №7-12 and table of contents vol. 5,6.pdf` | [5688575](https://ru.wikisource.org/w/index.php?title=%D0%98%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%3A1872%2C+Russkaya+starina%2C+Vol+6.+%E2%84%967-12+and+table+of+contents+vol.+5%2C6.pdf&oldid=5688575) | 1872 | Public domain |
| ru | `1874, Russkaya starina, Vol 9. №1-4.pdf` | [5519156](https://ru.wikisource.org/w/index.php?title=%D0%98%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%3A1874%2C+Russkaya+starina%2C+Vol+9.+%E2%84%961-4.pdf&oldid=5519156) | 1874 | Public domain |

All **nine processed scan files** advertise **Public domain** and `Copyrighted=False`
in the recorded file metadata. The scale gate excludes absent/conflicting or
non-PD metadata *before downloading media* and inventories the failure; no
non-PD scan entered this collection. This is recorded licence evidence, not a
new copyright adjudication. Unprocessed files have no claimed licence review.
Athides has a date discrepancy: Index year **1883**, Commons
`DateTimeOriginal` **1884**; both original values are preserved, without silently
choosing an edition year. Greek/Russian text rightsinfo advertises **CC BY-SA
4.0** separately from the PD scans, with its site-specific licence URL. Preserve
revision/history attribution and share-alike notices on redistribution.

Greek resolution remains uncertified: all 29 pages carry `dpi_unknown`, 23 have
`thumbnail_exceeds_file_width`. All Russian PDFs were rendered at **200 dpi**
from PDF point geometry; their embedded scan's native effective resolution is
not certified. All 129 Russian pages and 26 Greek pages retain line-count mismatch
flags. These sources have **zero candidate-eligible / verified-gold lines**.

### Executed validation and resume

The combined suite passed **195 tests, 1 skipped** (the optional unrelated audit
replay is absent). New tests cover phase ordering without scan requests, exact
status/year filtering, unknown language supply, whole-label codec rejection,
PD gating before media, deadline-bounded Retry-After, gap-aware continuation
coverage, cache import integrity/receipt repair, serial work identity, cross-work
duplicate quarantine, work rather than edition caps, deterministic 3 × 40 sheets,
and an HTTP-forbidden resume. Live scale integration is **not** certified because
network access failed.

Independent `final/validation.json` checks passed for **all 158 page receipts,
5,656 crop/record candidates, all 580 admitted codec round trips, pinned revision
IDs, Q3/Q4/era selection, pool hashes, and pairwise disjoint proposed work groups**.
The first attempt resumed with identical counts, page IDs and pool hashes in
approximately **1.3 seconds**, zero HTTP requests. The authoritative final output
also resumed with identical counts, IDs, work reports, errors and pool hashes,
zero HTTP requests (`final_resume.log`, `validation.json`). Rebuilding under the final
code reproduced the same labels/provenance/crop hashes and byte-identical sheets;
pool file hashes differ between output directories because absolute crop paths
are part of their records. Original coordinator runs were not changed.

Exact commands (existing interpreter, no installs or sub-agents):

```sh
PYTHON=~/Projects/glossapi-development/.venv-exp/bin/python
SCALE=bench/runs/O4a_scale_2026-10-07
# Import and list recorded sources BEFORE scans (executed on the parent attempt).
"$PYTHON" -m bench.source_wikisource --scale --out "$SCALE" --offline --discover-only \
  --import-cache bench/runs/O4a_el_probe2 --import-cache bench/runs/O4a_ru_probe
# Authoritative final run; all downloads/recordings share the parent cache.
"$PYTHON" -m bench.source_wikisource --scale --out "$SCALE/final" --cache-dir "$SCALE/cache" \
  --offline --max-pages 3000 --pages-per-index 100 --wall-minutes 70
"$PYTHON" -m pytest bench/tests/test_source_wikisource_scale.py \
  bench/tests/test_source_wikisource.py bench/tests/test_admission.py \
  bench/tests/test_tools.py bench/tests/test_codec_v2.py -q
```

To extend this exact output once the environment has network access, retain the
same code/settings and cache and explicitly extend the incomplete discovery
manifest (this network-enabled command was **not successfully executed here**):

```sh
"$PYTHON" -m bench.source_wikisource --scale --out "$SCALE/final" --cache-dir "$SCALE/cache" \
  --extend-discovery --max-indexes 500 --max-pages 3000 --pages-per-index 100 \
  --greek-target 3000 --cyrillic-target 1500 --work-target 40 --wall-minutes 85
```

Requests remain serial at the default **1 request/second**, including API,
media, redirects and retries, with a 30-second transport timeout and deadline
checks. Successful responses are immutable and hashed; failed responses are
retained; page commits are atomic and resumes verify records/images/crops.
Stops/targets can be increased, while code/label/image-setting drift requires a
fresh output directory. `--extend-discovery` fills uncached continuations without
refreshing already cached responses; changed committed revision identities are
rejected. The next required progress is genuine Q3/Q4 discovery for additional
works and missing Greek images, including live Ukrainian/Bulgarian/Serbian
inspection. None of that missing supply is represented as completed here.
