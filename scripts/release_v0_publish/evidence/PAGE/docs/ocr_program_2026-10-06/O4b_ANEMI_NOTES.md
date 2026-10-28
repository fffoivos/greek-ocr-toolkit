# O4b Anemi page acquisition — 8 October 2026

The owner's decision at **10:50 Europe/Athens on 8 October 2026** admits Anemi scans for internal training and evaluation, including bulk acquisition. Every plan row and saved page receipt carries **`CC BY-NC-ND; internal use only`**. This is the owner's admission label and decision provenance; acquisition does not rewrite O4c's source rights evidence or its separate compatible-candidate ranking. Downloaded pages and the existing recorded excerpts must never be redistributed.

## Plan and counts

`scripts/fetch/o4b_anemi_pages.py plan` reads `docs/evidence/o4c/anemi.jsonl` and binds `anemi_prior_ranking.json` by hash. The latter contains a 39-document ranking signature, not individual ranking entries, so it is preserved as provenance and does not filter the newly admitted records.

Selection requires `grc` or `gre` in the language codes (including the retained source-filter `catalogue_languages` when a detail page spells out a language), publication year 1800–1950 inclusive, and a listed PDF. Printed language remains source-declared. Ranking is the 1800–1910 band first, then 1911–1950; within each band, year ascending, total declared pages ascending, and record ID. Unknown page totals sort last within their year.

The generated `out/o4b/anemi/plan.jsonl` has **6,529 catalogue records**, **7,599 distinct per-record PDF volumes**, and **1,152,688 known declared pages**. Thirteen repeated attachment links are removed from the original 7,612 file entries. Multiple volumes stay under one ranked catalogue record; equal titles alone are not deduplicated. `pages` sums distinct volumes and is null if any volume count is unknown. `estimated_pages` sums known counts. The one unresolved volume is an externally hosted PDF with no declared page count or Anemi page viewer; it stays visible in the plan and verification gaps and is not fetched through a fabricated viewer. `plan.meta.json` binds inputs, counts, and the plan SHA-256.

## What is acquired and its resolution

Full-document `/php/pdf_dump.php` downloads are CAPTCHA-gated and are never called. Each volume's ordinary `/php/pdf_pager.php` viewer publishes an iframe for `/php/pdf_split.php`. The fetcher validates the iframe's attachment filename against the canonical O4c source PDF and then requests **exactly one original page** with one-based `pageno` and `pagenum=1`. Local `page_index` is zero-based and `page_number` is one-based. Canonical O4c viewer links are used; the known erroneous bulk-inventory display links are not used.

The selected derivative is **`page_pdf`**, with no resizing or downsampling parameters. The viewer serves a PDF containing the page's scan raster. The original PDF response bytes are saved unchanged; there is no image rendering or recompression. A page PDF is preferable to the catalogue's thumbnail. No public lossless full-resolution image endpoint has been established by the recordings, so no TIFF URL or enlarged thumbnail URL is guessed.

The recorded 1809 Kaplani excerpt in `docs/evidence/o4c/fixtures/anemi_viewer_pages.pdf` contains original positions 2–4. Its first extracted page measures about **546 × 713.28 PDF points**, with a **2,275 × 2,972 pixel** principal scan image at **300 × 300 DPI** from its PDF placement. This is a fixture measurement, not a promise of equal resolution throughout the collection. Each acquired page is decoded to confirm exactly one page; its receipt records page dimensions, every exposed image's pixel dimensions and placement DPI, and the selected derivative. Source raster compression/losslessness and preservation-master resolution remain unverified. The PDF is preserved even if it has a text layer or several image objects.

## Rate, budgets, and credentials

The fetcher imports **`AnemiHTTP` and `authenticate` from O4c**. It uses the unchanged O4c user agent, verified TLS, in-memory cookies, robots checks, prohibited-path checks, shared `http.lock`, `rate_state.json`, and `transfer.jsonl`. Requests start at least **two seconds apart**, including login, robots, errors, and redirects; a longer robots crawl delay wins. There is one serial request/connection at a time. A destination `wave.lock` also prevents two waves writing the same directory simultaneously.

The default `--http-root` is `docs/evidence/o4c`, sharing O4c's actual rate state and transport ledger. Copy that state/ledger to the worker with the project and use the same root for all Anemi acquisition processes there. Do not run independent crawlers with separate rate roots against this host. O4c's nearly exhausted 1.5 GB discovery allowance is historical; the explicit O4b `--max-bytes` allowance is added to the existing ledger total for each invocation. Existing charges are retained. Robots, login, viewer metadata, unsuccessful/partial response payloads, and page payloads all consume the new allowance. Counts use O4c's charged body-byte definition; HTTP headers and TLS overhead are not included. Declared oversized bodies are refused before storage. Undeclared bodies are bounded by the remaining allowance and partial PDFs are not committed.

`--max-pages` limits **newly saved pages this invocation**, across all selected records/volumes. Previously SHA-verified pages consume neither page quota nor network bytes. `--wave N` always selects the first N plan records; repeating the command resumes their gaps. Increasing N extends the destination manifest. Changing the plan of an already represented record fails closed and requires a fresh destination. Zero budgets make no network requests. Unknown page counts remain explicit errors/gaps.

Only `ANEMI_USER` and `ANEMI_PASS` environment variables reach O4c's login function. There are no credential arguments or credential files. Login bodies, account banners, cookies, redirect locations, and raw exception text are not stored or printed. Viewer descriptor files contain only allowlisted public metadata. Authentication is deferred until a missing page needs network access; a fully verified resume needs no login. A privacy guard from the imported client checks selected record data and page receipts before writing or printing them.

## Worker commands

Run from the repository root on the **worker node**, with Python 3.11+ and `pypdfium2` installed. The Mac is used for code, the small plan, and fixture checks; no bulk acquisition was launched here.

```sh
python3 scripts/fetch/o4b_anemi_pages.py plan
python3 scripts/fetch/o4b_anemi_pages.py fetch \
  --wave 100 --max-pages 100000 --max-bytes 20000000000 \
  --dest /worker/storage/anemi-o4b
python3 scripts/fetch/o4b_anemi_pages.py verify /worker/storage/anemi-o4b
```

Supply secrets through stdin to the worker's shell, then export them only for the Python process. This example uses Bash locally to suppress terminal echo and avoids secrets in SSH argv, files, or shell history. Replace `worker-node`, the project path, and the destination with the real worker values. Do not enable shell tracing or terminal/session recording while entering credentials.

```bash
set +x
read -r -s -p 'Anemi user: ' ANEMI_USER; printf '\n'
read -r -s -p 'Anemi password: ' ANEMI_PASS; printf '\n'
printf '%s\n%s\n' "$ANEMI_USER" "$ANEMI_PASS" | ssh -T worker-node '
  set +x
  read -r ANEMI_USER
  read -r ANEMI_PASS
  export ANEMI_USER ANEMI_PASS
  cd /worker/projects/greek-page-ocr || exit 1
  python3 scripts/fetch/o4b_anemi_pages.py fetch \
    --wave 100 --max-pages 100000 --max-bytes 20000000000 \
    --dest /worker/storage/anemi-o4b
  result=$?
  unset ANEMI_USER ANEMI_PASS
  exit "$result"
'
unset ANEMI_USER ANEMI_PASS
```

The stdin protocol expects two newline-free credential lines. A secure in-memory credential producer can replace the local interactive reads and `printf`; the worker receives the same two lines.

## Receipts, resume, and verification

`DEST/wave_manifest.json` retains the selected record plans. Each `DEST/records/<record-hash>/record.json` identifies the catalogue record; each volume has a public `viewer.json` descriptor and `page-000001.pdf`, etc. Successful pages are committed via a `.part` file and atomic rename before appending to that record's `receipts.jsonl` and `DEST/ledger.jsonl`. Page receipts contain URL, HTTP status, bytes, SHA-256, UTC `fetched_at`, original position, volume binding, resolution, and rights. Failed/oversized page attempts retain bounded status/hash/byte receipts without saving partial PDFs; all HTTP attempts also remain in O4c's global transport ledger.

Resume verifies source/position binding, receipt schema, byte size, and current SHA-256. A missing or corrupt page is fetched again. An interruption between the record receipt and global page-ledger append is repaired on resume without fetching again. A torn receipt tail is retained and separated before the next append; an orphaned file without a successful receipt is fetched again. Verification re-hashes unique expected pages, reports missing/invalid positions, unknown page counts, unreceipted PDF files, and global page-ledger gaps. It returns nonzero if any gap remains and never contacts the network.

`ANEMI_PROGRESS record=<id> pages=<done>/<total> bytes=<n>` reports verified pages in that record and new wave transport bytes. `ANEMI_WAVE_DONE records=<n> pages=<n> bytes=<n>` reports completed selected records, newly acquired pages, and new charged transport bytes. `last_wave.json` additionally records selected records, skipped pages, stored page bytes, errors, and `stop_reason`. Page/byte budget stops are normal exits; acquisition errors are nonzero. Ctrl-C retains committed receipts for the next invocation.

## Offline checks

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  scripts/fetch/tests/test_o4b_anemi_pages.py
```

The fixture suite replays O4c's recorded robots/login form and SHA-bound PDF excerpt through O4c's actual rate/ledger transport, with network calls disabled. Its single-page test responses are extracted locally from the three recorded PDF pages; the iframe response is reconstructed from recorded viewer provenance. No account material is part of the fixtures. Tests cover selection/ranking and real plan counts, volume deduplication, external/unknown holdings, resolution/schema, SHA-based skip and corrupt-page retry, page/byte/zero budgets, historical ledger accounting, two-second spacing/user-agent, actual imported login, secret echoes/exceptions, multipage rejection, verification gaps, global-ledger repair, torn tails, manifest extension, and CLI output/exit status.

Validation result: **32 tests passed**, with the machine-readable result in `docs/evidence/o4b/tests.xml`. A live anonymous viewer metadata check succeeded on 8 October 2026 at 07:57:10 UTC: 9,726 charged bytes including robots, a 200 viewer response, and a matching published page-PDF filename. It acquired no page payload and performed no login.

The handoff is `O4B_ANEMI_HANDOFF.json`. This small live validation is recorded separately in `docs/evidence/o4b/live_viewer_check.json`; it does not certify a bulk wave or authenticated worker acquisition.
