# T18 — Round 1 rescue fetch: 51 books the owner rescued from the strange_type removals; fetch 13 pages each, gate, add to the Finder look folder. NO Google calls. (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for Anemi only (ANEMI_USER/ANEMI_PASS in env; never in files, argv or logs). No `.git` writes.
Inputs: docs/records/harvest/round1/rescues.json ("rescued": 51 books, keys resolve in docs/records/harvest/round1/selection.json; "stay_out" and "pending_owner_look_1880s" are NOT fetched);
the T16 machinery (greekocr/harvest/round1.py, scripts/harvest/round1.py, the fetcher, the page gate + T16 quality guards, manifest/summary formats).
Required:
1. Allocation: 13 pages per rescued book (16 if the book's decade is 1860 or 1870, which are thin), positions by the T16 rule (8–95% spread, seeded offsets, pilot pages
   excluded), same gate and replacement rule (≤2 tries), same receipts. Polite fetch with the existing rate state; resumable.
2. Outputs: docs/records/harvest/round1/rescue/manifest.json + summary.json in the T16 formats (every page: book, page, pdf sha, gate, replacement chain), and an
   UPDATED combined docs/records/harvest/round1/manifest_all.json = T16 accepted pages + rescue accepted pages (one list, each row tagged origin: "t16" | "rescue").
3. Finder look folder: add every accepted rescue page to docs/records/harvest/harvest_big/round1_look/accepted/<decade>s/RESCUED_<year>_<title40>_<id6>/pNNNN.png
   (200 dpi grayscale PNG, _REPL suffix for replacements), same naming as T16's folder (see its README.txt). Do not touch existing folders.
4. Report docs/records/harvest/round1/RESCUE_FETCH.md: per-decade/book table, failures by reason, fetch time. Tests (no network) for the rescue allocation and the
   combined manifest. INVENTORY (append; T17 may have written to it — re-read before writing, never overwrite its entries).
Last line exactly: `T18: done | books: <n> | pages_fetched: <n> | pages_accepted: <n> | replacements: <n> | fetch_minutes: <n> | tests: <n> passed`.
