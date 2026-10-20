# Real-line collection plan v1 — to the ceiling (14 Oct 2026)

Goal: assemble the ceiling of real, Google-labelled training lines for the Greek recogniser, per script class, plus
document-disjoint dev/test sets, using the round-1 pipeline (select → fetch → page gate → owner look in Finder →
Document AI page read → line admission → crops). Single reader: Document AI (owner, 14 Oct). Cost of reads is
USD 1.50 / 1,000 pages; the binding constraints are sourcing and the owner's look, not money.

## 1. Targets and gaps

| Class | Ceiling train | Dev + test (held-out books) | Have (admitted) | To collect | Pages (≈40 admitted lines/page) |
|---|---:|---:|---:|---:|---:|
| Polytonic 1850–1935 | 120,000 | 8,000 | 58,408 | 70,000 | 1,800 |
| Modern Greek, scanned | 100,000 | 5,500 | 0 (19,657 born-digital exist) | 105,000 | 2,700 |
| Greek with Latin inside | 40,000 | 3,500 | 1,147 (+3,657 born-digital) | 40,000 | 1,000 of targeted books (≈40 % mixed) + by-product |
| Latin only | 20,000 | 2,300 | 1,251 (+2,167 born-digital) | 20,000 | by-product of the above |
| Cyrillic | 20,000 | 2,300 | 0 (11 born-digital) | 22,000 | 550 |
| **Total** | **300,000** | **21,600** | **≈61,000** | **≈257,000** | **≈6,000** |

Ceiling rationale: 3.77 M-parameter CTC recogniser; gains per doubling of real lines fall under seed spread beyond
≈300 k real lines. The knee is measured, not assumed (wave 0 below). Synthetic stays at ≈ 1–2× the real pool.

Admission (memory: harvest_line_admission_checks): ≥10 letters; mean DocAI confidence ≥ 0.89; no tall box; ≤ ⅓
non-letters; script inventory per line; any Greek word with a non-Greek letter → line dropped; CJK/Thai/Lao/Tibetan/
Indic/Hebrew/Arabic anywhere → line dropped; majority-Latin lines → class `latin` (kept); DOT ABOVE → middle dot.
Hold-out: whole books, ≈15 % of books per class, chosen before training, never read by a model during selection.

## 2. Waves

Each wave = one fetch brief (T-fetch) → owner look in Finder (accept / NO_ folders) → one read brief (T-read) →
admission + crops (the T20 step, reused). Google spend per wave is stated; owner gates = spend, new source access,
licence stance.

| Wave | Class | Source and rights | Pages | Lines expected | Google USD | Owner look | Notes |
|---|---|---|---:|---:|---:|---|---|
| 0 | polytonic | round 1 (on disk) | 0 | 0 | 0 | none | T20: admission step, 20 held-out books, crops; plus an E2 data-scaling arm 25 k / 50 k / 100 k to locate the knee |
| 1 | polytonic | Vouli: 107 parliament volumes 1850s, 1,126 pages on disk, CC-BY | 1,126 | 45,000 | 1.70 | sample of 60 pages (pages already geometry-gated) | one printer; read whole pages, map to lines like T15 |
| 2 | polytonic | round 2: 50 new books — Anemi (research use, internal) 30 + Internet Archive PD 20 from the O4c ranking | 650 | 25,000 | 1.00 | 650 pages | diversity; 8 of the 50 books go straight to hold-out |
| 3 | modern scanned | Hellenic Parliament proceedings 1975–2000 (DSpace, CC-BY) | 1,200 | 48,000 | 1.80 | 1,200 pages | typewriter + phototypeset; 1975–1981 polytonic tagged separately |
| 4 | modern scanned | Open Archives via the HF dataset glossAPI/openarchives.gr (gated, we have access): `data/external_pdfs.parquet` = 561,271 direct PDF links over 140 repositories (IKEE 85k, uth_rep 50k, phdtheses 46k, ntua 43k, pergamos 42k …); the text shards' `pipeline_metadata.ocr_success` marks documents the glossAPI pipeline had to OCR (≈25 % in a sampled shard ≈ 44 k scanned documents) and `polytonic_ratio` / `page_count` / `percentage_greek` are per document; licence per repository | 1,500 | 60,000 | 2.25 | 1,500 pages | the backup box is not accessible (owner, 15 Oct); the links replace it. Pick scanned docs by `ocr_success`, download the bitstream, render 10–16 sampled pages, gate, look |
| 5 | mixed + Latin | Anemi dictionaries, grammars, journals (title filter) 40 books; repository theses (wave 4 sources): bibliography/footnote pages | 1,000 | 40,000 mixed + 20,000 Latin by-product | 1.50 | 1,000 pages | 20–40 % mixed per page; majority-Latin lines kept as `latin` |
| 6 | Cyrillic | Internet Archive ru/bg/sr scans 1800–1950 (PD; O4c ranked 14 docs, 4 false positives excluded) | 550 | 22,000 | 0.85 | 550 pages | scanned books only, no digital editions (Tolstoy CC0 uploads excluded) |
| 7 | test labels | Greek + Russian Wikisource proofread pages with Commons scans (PD) | 300 | 5,000 polytonic + 3,000 Cyrillic | 0.45 | 300 pages | human transcriptions = second label; test-only |
| | | **Total** | **6,300** | **≈270,000** | **≈9.6** | **≈5,300 pages** | |

Order of execution: 0 → 1 → 2 (polytonic complete) → 3 → 4 (modern) → 5 → 6 → 7. Wave 3 runs first; wave 4 after its crawl is
reviewed. Wave 7 can run any time after wave 2.

## 3. What each wave needs before it starts

- Wave 0: nothing (data on disk). Deliverables: `line_admission` step with per-rule counts, `holdout_books.json`,
  crops under harvest_big/round1/crops/, class-tagged records; E2 scaling-arm brief.
- Wave 1: Vouli crops/pages in glossapi-ocr-local/node_backup_20261008 (verified). Page images re-rendered at 200 dpi
  from data/raw/pdf_cache (same as the Mac extractor).
- Wave 2: O4c candidates.jsonl (Anemi 7,830 records catalogued; IA ranked) → exclusion of the 130 round-1 books;
  Anemi fetcher from T16 (Keychain creds, env-injected).
- Wave 3: parliament DSpace API (O4c S1 code), year filter 1975–2000, bitstream download; licence CC-BY recorded per item.
- Wave 4: join the HF shards' pipeline_metadata (ocr_success, page_count, polytonic_ratio, percentage_greek) to
  external_pdfs.parquet by filename/edm_url → ranked manifest of scanned documents; stratify by repository (≤40 pages per
  repository share) and decade from metadata_json; download bitstreams directly (HF token from Keychain for the tables,
  repositories are public); render sampled pages; licence per repository recorded. Thesis bibliography pages from the same
  documents feed wave 5.
  Selection filters (owner, 15 Oct): only rows whose recorded fetch answered 200 (status_code) — some links are dead; over-draw by
  one third and replace failed bitstreams at download time (round-1 replacement rule). Greek text only: percentage_greek ≥ 80,
  greek_badness_score ≈ 0, mojibake_badness_score = 0, is_empty false, char_count sane for the page count. Documents with
  latin_percentage 20–50 are NOT dropped: they are tagged as wave-5 (mixed-script) candidates. All pages still go through Google
  Document AI whole-page reads; nothing is line-extracted by us (decision 14 Oct).
- Wave 5: title-word filter over the Anemi catalogue (λεξικ, γραμματικ, περιοδικ, journal names) + repository theses' last 10 % of pages; mixed-share measured on the sampled page before fetch.
- Wave 6: IA download via the O4c media probe code; print review by the owner (scan vs digital edition).
- Wave 7: Wikisource API join (blocked by robots in O4c run — retry with the documented User-Agent, else manual list).

## 4. Pipeline fixed for all waves

1. Selection: ranked manifest with rights, year, sampled-page script ratio; page positions 8–95 % spread, seeded.
2. Fetch at 200 dpi grey PNG; T13c page gate (frozen sha) + photometric guards; spreads allowed (DocAI reads both halves).
3. Owner look: Finder folders `<wave>_look/accepted/<decade>s/<year>_<title40>_<id6>/pNNNN.png`; owner renames rejects `NO_…`.
4. Read: one DocAI call per page, raw response cached, at-most-once; cost cap per brief.
5. Admission + class tag + hold-out assignment; compiled page images (owner-approved format) per book for spot checks.
6. Crops cut from DocAI boxes (trim where boxes touch neighbours), records with `script_class`, word tags, source,
   licence, read_batch; data_provenance for the trainer.

## 5. Costs and time

- Google: ≈ USD 10 total. Codex: ≈ 2 briefs per wave, 14 briefs. Owner look: ≈ 5,300 pages across six sittings
  (round 1 was 1,500 pages). Elapsed: one wave per day when the owner looks the same day → about two weeks.
- No GPU until wave 0's scaling arm (one A100 session, ≈ USD 5).

## 6. Risks

- Anemi full-PDF downloads hit CAPTCHA; the T16 page fetcher path works — keep using it; Anemi stays internal-only.
- Repository licences for wave 4 are per repository and recorded, not adjudicated; ocr_success is the pipeline's routing
  decision, not a scan certificate — the page gate and the owner look still decide.
- Google invents scripts on damaged glyphs and swaps look-alikes silently — admission rules catch what we saw; new
  sources get the same character audit before any line is admitted.
- Vouli is one printer: never more than 40 % of the polytonic train pool from one source (per-source cap in mix.py).
- Test contamination: hold-out books fixed at selection time; label-text equality check against train (O5 rule).
