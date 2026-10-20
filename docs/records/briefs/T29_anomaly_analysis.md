# T29 — Data analysis of the collected pool: anomaly detectors per aspect, book profiles, ranked suspicious books with dossiers for an LLM adjudication pass (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network OFF. No Google calls. No `.git` writes. Read docs/records/harvest/collection/COLLECTION_REPORT.md first.
Input: docs/records/harvest/collection/admitted_all.jsonl (293,439 admitted lines; fields incl. wave, source, book/doc key, year, script_class, split, label, confidence,
bbox, crop path/size) plus, for page context, each wave's records.jsonl (all Google lines incl. rejected) and rejected.jsonl; page PNGs and crops under
docs/records/harvest/harvest_big/<wave>/. Owner (15 Oct): "set up the specs for different aspects and try to detect anomalies … content, length, style … target
language, other scripts, mixed-script words … suspicious books can use passes from LLMs to return a decision."
Principle: every detector reports a measured distribution and flags outliers relative to the right reference group (the line's script class, and for
per-book scores the class's book population), never a hand-picked constant unless stated. Flags are additive and explain themselves (`reason` strings with the
measured value and the reference quantile).
Required:
1. `greekocr/harvest/analysis.py` — line-level features, one row per admitted line (and the same for rejected lines, tagged), written to
   docs/records/harvest/analysis/line_features.jsonl.gz:
   LANGUAGE / SCRIPT: letter shares per script (Greek, Latin, Cyrillic, other); residual other-script characters; mixed-script words (should be zero after
   admission — count anyway); Greek-vs-Latin word count; language guess of the line (el / la-fr-de-en-it by a small function-word list per language / ru-bg-sr
   by Cyrillic function words / unknown); for Greek: polytonic mark density (marks per Greek letter), monotonic-tonos-only share, katharevousa vs demotic cue
   words (a short list: e.g. ὑπό/υπό, ἐν, τῆς/της endings -ις/-εως vs -η/-ης, εἰς vs σε), final-sigma errors (σ at word end, ς mid-word), spacing-apostrophe
   (U+1FBF/1FBD/0384/2019) count, hyphen at line end.
   CONTENT: digit share, punctuation share, symbol share, all-caps share, token count, mean word length, longest token, repeated-character runs (≥4 same),
   numeric-table pattern (≥3 numbers separated by spaces), bibliographic pattern (year in parentheses, "pp.", "Bd.", "vol."), running-title / page-number
   pattern (short, all-caps or digits at page top/bottom — use bbox position relative to page height).
   LENGTH / GEOMETRY: label length (chars), crop width/height, chars per 100 px of width, box height relative to the page's median counted-line height,
   box width relative to page text width, vertical position, box aspect; alignment of the box with its page's column structure (uses the T20 page bbox set).
   LABEL QUALITY PROXIES: mean/min confidence, Google symbol count vs label length mismatch, out-of-vocabulary share where the vocabulary is built from the
   pool itself: word support = number of distinct books (across all waves) containing the NFC-lowercased word; OOV = support ≤ 1; also a second OOV against
   the Wikisource human transcriptions' vocabulary (docs/records/harvest/wikisource/) for polytonic lines.
   DUPLICATES: exact duplicate labels across books (list the pairs; running titles and formulae are expected, long sentences are not); near-duplicate pages
   (two-page spreads read twice, left/right halves: same source, adjacent pages, label-set Jaccard ≥ 0.6).
2. Page profiles (docs/records/harvest/analysis/page_profiles.jsonl): per read page, aggregates of the above incl. admitted/rejected ratio, reason mix, line-count vs
   wave median, column count, share of lines whose language guess ≠ the book's majority language, share of digit-heavy lines.
3. Book / document profiles (docs/records/harvest/analysis/book_profiles.jsonl + BOOK_PROFILES.md table): per source key, the distributions (median, p10, p90) of every
   line feature, the page-level aggregates, and z-scores against the book population OF THE SAME SCRIPT CLASS. Hard flags regardless of z: majority language ≠
   expected for the wave (e.g. a French book in a Greek wave), > 2 % lines with other-script residue, any mixed-script words, polytonic class with mark density
   below the class p5, confidence median below class p5, OOV share above class p95, chars-per-100-px outside [class p2, class p98], duplicate-page pairs,
   > 30 % digit-heavy lines, > 30 % running-title/page-number lines.
4. Suspicion score and ranking: combine |z| over the aspects (one score per aspect: language, script, content, length/geometry, style, label-quality,
   duplication) → `suspicion` = count of aspects beyond 2σ + hard flags; rank books; docs/records/harvest/analysis/ANOMALIES.md with: per-aspect histograms (as tables),
   the top-60 suspicious books/documents with their reasons, per-wave anomaly rates, and 20 example lines for each hard-flag type (text + crop path).
5. Dossiers for an LLM adjudication pass (NOT run here): for each of the top-60 books plus every hard-flag book (cap 120),
   docs/records/harvest/analysis/dossiers/<rank>_<source>_<key>/: dossier.json (metadata, scores, reasons, 40 sample lines = 20 random admitted + 20 most anomalous with
   label, confidence, features, crop path), sheet.jpg (those 40 crops stacked with their labels under them, one type size, numbered), page.jpg (one compiled page
   image of the book from the wave's compiled folder, copied), and a plain-text `question.md` asking the adjudicator for one of: KEEP / DROP_BOOK /
   DROP_PATTERN (with a regex or rule) / RELABEL (what is systematically wrong) and a confidence — the adjudicator sees sheet.jpg and page.jpg.
6. Tests (no network; synthetic lines) for each detector family, the OOV vocabulary, the z-score reference grouping, duplicate detection, the dossier builder.
   INVENTORY. `## Analysis` in docs/records/harvest/collection/EXECUTION_STATE.md. Keep memory bounded: stream the jsonl, never load all crops.
Last line exactly: `T29: done | lines: <n> | books: <n> | hard_flag_books: <n> | top_suspicious: <n> | dossiers: <n> | dup_pages: <n> | tests: <n> passed`.
