# T20 — Wave 0 of the collection plan: line admission, script classes, held-out books, crops for round 1 (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network OFF. No Google calls. No `.git` writes. Read docs/records/harvest/COLLECTION_PLAN_v1.md §1 and §4 first.
Input: docs/records/harvest/round1/records_all.jsonl (75,061 DocAI lines over 1,532 pages / 130 books; fields as in docs/records/harvest/round1/reads_rest/records.jsonl),
page images docs/records/harvest/harvest_big/round1/images/<book_key>-<page6>.png (200 dpi grey), manifest docs/records/harvest/round1/manifest_all.json.
Required:
1. `greekocr/harvest/admission.py` — pure, tested functions:
   a. `inventory(text)` → counts of Greek letters, Latin letters, Cyrillic letters, other-script letters (by Unicode block/name), digits, Greek
      punctuation, other symbols; and the list of "mixed words": split on whitespace, `=`, `-`, `/`, parentheses and punctuation; a word is mixed when its
      letters come from ≥2 of {Greek, Latin, Cyrillic, other}. Roman numerals (only I V X L C and Greek Ι Χ) are NOT mixed.
   b. `admit(record)` → `(admitted: bool, script_class: str|None, reasons: list[str], label: str|None)` applying, in this order, each rule adding its reason
      (report ALL failing reasons, not just the first):
      - `short_line`: < 10 letters (Unicode category L).
      - `low_confidence`: mean DocAI confidence < 0.89.  - `tall_box`: flag present.  - `symbol_heavy`: non-letter, non-space chars > ⅓ of non-space chars.
      - `foreign_script`: any letter outside Greek/Latin/Cyrillic (CJK, Hangul, Thai, Lao, Tibetan, Devanagari, Gujarati, Bengali, Hebrew, Arabic …).
      - `mixed_word`: any mixed word (ΚΕΦΑΛΑΙΟN, Δαβій, Fιδον, δυτικοβо) → drop; no correction.
      - `bad_page`: the page has > 50 % of its ≥10-letter lines below 0.89 or > 30 % tall boxes (compute per page first).
      Script class of an admitted line by letter majority: `greek_poly` (any Greek letter with breathing/iota-subscript/perispomeni/grave in NFC — i.e. U+1F00–1FFF
      or combining U+0313/0314/0342/0345/0300 after NFD), `greek_mono`, `greek_latin_cs` (Greek majority AND ≥1 whole Latin word of ≥2 letters), `latin`
      (Latin majority), `cyrillic` (Cyrillic majority). Label = NFC(docai_text), whitespace collapsed, U+02D9 DOT ABOVE → U+00B7 middle dot, spacing
      U+1FBF/U+1FBD/U+0384 that stand alone between letters left unchanged (recorded as `has_spacing_mark` for a later label-rule decision).
2. Held-out books: choose 20 of the 130 round-1 books with a seeded draw (seed 20261015) stratified by decade (≥2 per decade present), preferring books with
   ≥ 300 admitted lines; 15 → split `test`, 5 → split `dev`; everything else `train`. Write docs/records/harvest/round1/holdout_books.json (book_key, title, year,
   decade, split, admitted lines). Then the O5 rule: any train line whose label equals a test or dev label (NFC, whitespace-collapsed) is dropped with reason
   `label_in_holdout`; count it.
3. Crops: for every admitted line cut the DocAI bbox from the page PNG. Trim where boxes touch: if the bbox overlaps the vertical extent of the previous or
   next line's bbox on the same page by more than 15 % of its own height, cut at the midpoint of the overlap. Pad 2 px top/bottom and 4 px left/right inside the
   page. Save grey PNG at native resolution to docs/records/harvest/harvest_big/round1/crops/<book_key>/p<page6>-l<line4>.png (gitignored path). Record path, sha256,
   width, height, trimmed flag.
4. Outputs: docs/records/harvest/round1/admitted.jsonl (one row per admitted line: id, page_id, book_key, year, decade, split, script_class, label, has_spacing_mark,
   confidence, bbox, crop path/sha/size, trimmed, source "anemi_round1", licence "anemi-research-internal", read_batch); docs/records/harvest/round1/rejected.jsonl
   (id, reasons, docai_text); docs/records/harvest/round1/admission_summary.json (counts per reason — a line can carry several —, per class × split, per decade,
   crop size stats, label_in_holdout count, bad pages list); docs/records/harvest/round1/ADMISSION.md (tables + 30 example rejected lines per reason with their text,
   and 10 example mixed words); a contact sheet docs/records/harvest/harvest_big/round1/admission_sheet/<class>.jpg with 60 random admitted crops + labels per class
   (one type size, label under the crop) for the owner's after-the-fact look.
5. Tests (no network, synthetic records) for inventory, every admit rule, class assignment, hold-out stratification, label_in_holdout, crop trimming geometry.
   INVENTORY. Also append a `## Wave 0` section to docs/records/harvest/collection/EXECUTION_STATE.md with the counts.
Last line exactly: `T20: done | admitted: <n> | rejected: <n> | train: <n> | dev: <n> | test: <n> | poly: <n> | mono: <n> | cs: <n> | latin: <n> | cyr: <n> | crops: <n> | tests: <n> passed`.
