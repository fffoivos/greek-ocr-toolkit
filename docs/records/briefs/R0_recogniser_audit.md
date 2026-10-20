# R0 — Recogniser audit: letters, positions, case, apostrophes (gpt-6.1-sol, xhigh) — phase R0a (GO 17 Oct, coordinator on the owner's behalf)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-r0` (branch `opus/spellcheck-r0`, head fabcd6d4 = SF1/S7 detector). No `.git` writes.
Do not touch other worktrees (an Astra review is reading `~/Projects/greek-ocr-toolkit-spellcheck`). Network OFF. Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with `PYTHONPATH=$PWD`. Mac CPU only. Cached alignments for the
666 held-out lines (`.cache/labelfix/align_s0.jsonl`); CTC forward passes (E3 `full_s0`, CPU) are allowed ONLY for the new locked set below
(≤ 600 crops). Measurement only: change no detector or recogniser code.

## Phases
- **R0a (this run):** draw the locked set; align it; every measurement that needs no new truth; build the blind adjudication cards; write
  the expected-truth placeholders. STOP after R0a with the cards ready.
- **R0b (track lead):** two blind Opus readers + planted controls adjudicate the cards (letters, case, apostrophes) against the pixels.
- **R0c (a follow-up Sol run):** score everything with the adjudicated truth, DATA/MODEL classification, the review page.

## The locked fresh-book test set (coordinator, binding)
Draw it from Wikisource held-out books that are NOT among the 666-line instrument's 14 books, NOT the 3 DEV books, and whose documents are
NOT in `L1_input_documents.txt` (copy it from `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/clariden/`, commit 6b91ebaa)
— print the zero-intersection receipt. Pool: `docs/records/harvest/harvest_big/wikisource/` (crops, google, wikitext/compiled human text) and
`~/Projects/greek-page-ocr/out/e3b/predictions/full_s0_wikisource_human.jsonl`. Target ≈ 300–500 complete polytonic lines from ≥ 5 books,
stratified by book, seeded (20261017). Write `R0_locked_set.jsonl` + `R0_locked_set_receipt.json` (book list, line count, seed, hashes).
**It is never used for tuning**: record that in the receipt; it judges L1 and wave 1c from now on (the 666 stay as the continuity instrument).

**Two strata (coordinator, 17 Oct):** (i) the Wikisource stratum above; (ii) a NEW-SOURCE stratum of 150–200 lines from the M2 blind-check
cards (`docs/records/labelfix/spellcheck/M2_lines.jsonl.gz` in the main worktree is read-only to you; the cards themselves are under
`~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/{t4c,c0}/`, with print verdicts), stratified by source, Greek/mixed
polytonic cards only (no Cyrillic, no monotonic). Because all 473 M2 cards were already measured and used as S7 qualification targets, SPLIT
them seeded (20261017, stratified by source): the locked half (150–200 lines) becomes stratum (ii) and must never again be used for any
selection; the remainder becomes `R0_newsource_dev.jsonl`, the development pool for policy work (e.g. ZONE+LEXICON per regime). Write both
lists, their line ids, and `R0_newsource_exclusion_ids.txt` (stratum (ii) line ids) for the sourcing lead's frozen exclusion manifest so they
never enter a training release. Both strata get zero-intersection receipts (against 666, DEV, L1 input, and each other) and the
never-tune statement. Cards for stratum (ii) are built like stratum (i), using the existing blind verdicts as an additional reference (never as
truth without pixel adjudication).

## Why (owner, 16 Oct 2026)
"we need to make sure the recognizer rocks as well." The recogniser (E3 `full_s0`) supplies letter identity and letter positions to both the
detector and the R1 mark reader; its errors cap both. Its known number (v2_test CER 1.37%) is measured against Google labels and mixes letters
with marks, so it does not tell us what the spell checker depends on.

## Coordinator additions (binding)
1. State the letter truth first (source, how many lines/slots have it) before any letter number; no letter number against Google labels.
2. Every failure type: DATA or MODEL, with counts and ≥ 3 example line ids, and the evidence for the verdict.
3. Span placement on ALL slots, reference = the detector's blobs where a slot is clean (one blob, one character); share of CTC span centres
   outside their blob, by script class and by font-size bucket.

## Adjudication cards (R0a builds them, R0b fills them)
For the locked set and for the 666: every word where the recogniser's letters (marks stripped, case kept) differ from the human text or from
Google; the 753 case-disagreement slots (sample ≥ 150, stratified by book); every elision apostrophe / quote position where recogniser,
Google and human disagree. Card = zoomed crop (≤ 3×) + full line + two or three candidate forms in random order, sources hidden, plus ≥ 8%
planted controls with known answers. Format as `scripts/labelfix/owner_implicit_adjudication_prep.py` does (items_blind.json + items_key.json);
keep the key out of the blind file.

## Measure
1. **Letters against the print, marks ignored.** STATE THE LETTER TRUTH before any number: the Wikisource three-way lines (Google, human,
   recogniser) where human and recogniser/Google letters differ are settled by pixels (blind adjudication in the S2 print-truth style, crop
   + two forms in random order, planted controls), plus the owner's notes where they speak to letters ("misread rho", "misread εις as one
   letter", "η classified as 1-2", "ξaνὰ" Latin a). Say how many of the 666 lines that leaves with full letter truth. **No letter number
   against Google labels.** Report letter error rate (base letters, NFD marks stripped, case kept and case folded), by error type
   (substitution / insertion / deletion / case / script mix-up such as Latin a for α), by book.
2. **Span placement on ALL slots.** Reference = the detector's letter blobs where a slot is clean (one blob, one recogniser character).
   Report the share of CTC spans whose centre falls outside their blob, by script class (greek_poly / modern / Latin) and by font-size bucket
   (pixel x-height terciles or fixed px buckets); separately count fused slots (several characters on one blob) and split slots, and the 715
   R1 held-out samples that map to no blob — why each does not map.
3. **Capital case.** On the 753 slots where S5's pixel case and the recogniser's case disagree: who is right, by pixel adjudication on a
   sample of ≥ 150 (stratified by book), and the extrapolated count.
4. **Elision apostrophes and quotes.** Where the print has an elision apostrophe (’) or quote mark (owner notes: "missed ellipsis/quote at
   k"; S4's apostrophe detector candidates), how often the recogniser emits one, and how often Google's label has one.

## Classify every failure type as DATA or MODEL
For each failure type: count, ≥ 3 example line ids, and the verdict **DATA** (the training labels lack it or are wrong, e.g. Google drops
elision apostrophes so the recogniser never saw them) or **MODEL** (labels are right but the recogniser fails, e.g. case or span placement),
with the evidence (e.g. label frequency of the symbol in `import_real_v2_train.jsonl`). The list must let the training track pick an arm:
which failures a wider model could fix, which need corrected labels (incl. the apostrophe detector as a label-correction source), which
need new data.

## Review page (owner's template)
Same template as the owner pages (`scratchpad/snap4/build_owner_s4.py` style: full line crop, line id, Google's line, our recogniser's line,
one autosaving note): draw each recogniser character's span as a thin box with its letter, so the owner can check positions by eye. ≤ 60
lines, chosen to cover each failure type. Write the HTML; the track lead publishes.

## Deliverables
`docs/records/labelfix/spellcheck/R0_REPORT.md`, machine-readable `R0_failures.jsonl` (one row per failure with type, DATA/MODEL, line id, slot),
the page HTML, last line:
`R0a READY: locked set (i) <n> lines / <b> books, (ii) <m> new-source lines / <s> sources (dev pool <d>); zero overlap with 666, DEV, L1 input, each other; cards <c> (+controls <k>); span placement outside-blob <z>%; R0 RESULT (after R0c): letter truth <n> lines; letter error <x>% (case-folded <y>%); spans outside blob <z>% (by script/size …); case disagreements recogniser right <a>%; apostrophes emitted <b>%; DATA types …; MODEL types …`.
