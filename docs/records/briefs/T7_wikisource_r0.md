# T7: fresh Greek Wikisource polytonic harvest for locked test stratum R0 (i-b)

**Agent and budget.** gpt-6.1-sol, xhigh. ≤ 150 pages. Google ≤ USD 0.30. ≤ 90 min.

**Network: ON, limited to these hosts.**

| Host | Purpose |
|---|---|
| el.wikisource.org | pages and proofread text |
| upload.wikimedia.org | scan files |
| commons.wikimedia.org | file metadata |
| eu-documentai.googleapis.com | Google Document AI reads |
| oauth2.googleapis.com | Google credential refresh |

**Workspace.** This worktree, `~/Projects/greek-ocr-toolkit-sol-wsr0`, branch `sol/wikisource-r0` (from 4e95489d).
- Outputs: `docs/records/harvest/wikisource_r0/` only.
- Read-only: `docs/records/harvest/wikisource/`, the existing 15 Oct harvest of 20 books. It is present in this worktree.

**Separation from the live collection.** A separate collection (W1) is running from `~/Projects/collect-v3-data/run`. **Never read or write its ledger, its locks, or its limiter directory** (`~/Projects/collect-v3-data/shared-limiter`). This task gets its own:
- limiter directory, `docs/records/harvest/wikisource_r0/limiter/`;
- ledger, `docs/records/harvest/wikisource_r0/google/ledger.jsonl`.

## Purpose
These lines become a **locked test set**, stratum (i-b), for the spell-check and training tracks. **They never enter a training release.**

## Selection
Pick about **5 Greek Wikisource polytonic books**. Each must meet all of these:
- the Page: namespace has an attached scan, as a DjVu or PDF on Commons;
- the pages are **proofread or validated**: pagequality level 3 or 4;
- the text is polytonic Greek print;
- the book is NOT among the documents in `~/Projects/greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/binding/L1_input_documents.txt` (318 ids);
- the book is NOT among the 20 books in `docs/records/harvest/wikisource/`.

**Disjointness checks** must use every key you can resolve:
- document ids;
- the Index: page title;
- the Commons scan file name and its sha1;
- normalised title + author + year.

Resolve what the L1 ids point to: check how the toolkit maps `wikisource:` or `mixed:` document ids to books in the collection manifests under the main checkout's `docs/records/harvest/collection/` (read-only).

**The receipt must show zero intersection on every key.**

**Spread:**
- ≤ 150 scan pages in total;
- ≤ 40 pages per book;
- pages drawn uniformly, seeded, from the proofread pages of each book;
- prefer books from different decades and printers.

## Alignment: the P1b way
Reuse `greekocr/harvest/wikisource.py`: `strip_wikitext`, the conservative line alignment, and the template handling. **Do not write a new aligner.** It assigns human page text to physical lines using the line geometry from Google reads (the 15 Oct pipeline aligned about 22 labels per page).
- **Google reads only if the aligner needs them** for line geometry. These read the page image only, at USD 0.0015 per page.
- Reserve each read in this task's own ledger before the call. Stop at the hard cap of USD 0.30.
- Credentials: `GOOGLE_APPLICATION_CREDENTIALS` from the environment. Never print, copy or log it.
- Same processor binding as F2: project `ocr-ground-truth-20261008`, EU, processor `9a98b7aca3c19561`, version `pretrained-ocr-v2.1-2024-08-07`.

## Rules
- ≤1 request/s per host.
- Wikimedia User-Agent policy: the contact UA `greek-ocr-research/0.1 (foivos.karounos@gmail.com)`.
- Honour robots.txt and Retry-After.
- Use the API for metadata, with `maxlag` respected.
- **The label is the human proofread text, as printed.** Keep literal and NFC forms.
- An unresolved template excludes its line. That behaviour already exists.

## Output
Under `docs/records/harvest/wikisource_r0/`:
- `books.jsonl`: Index page, scan file with sha1, title, author, year, the pagequality distribution and the drawn pages;
- `pages.jsonl`: image hash and page geometry, meaning the Google line/token boxes when read;
- `lines.jsonl`: **line_id**, page, crop path and hash, human label (literal and NFC), and alignment evidence;
- `crops/`;
- `google/ledger.jsonl`;
- `RECEIPT.md`: books, pages and lines per book; the zero-intersection table against L1 and the 20 local books on each key; spend.

Commit with a guarded helper that excludes git-ignored paths. Do not commit images if the repo ignores them; list them with hashes instead.

The last line must be exactly:
`T7: done | books: <n> pages: <n> lines: <n> | L1 intersection: 0 on <k> keys | local-20 intersection: 0 | usd: <x>`
