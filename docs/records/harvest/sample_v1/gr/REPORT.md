# F2-GR — page sampling and Google check

Generated 2026-10-16T18:46:53.274089+00:00. Branch `sol/funnel-gr`. Final cohort: **260 sampled / 256 passed machine checks / 256 successful Google reads; 20,687 pipeline-usable candidates.** Released training labels = **0**. The coordinator’s blind page and label adjudications remain pending.

**USD 0.4275 reserved for 285 unique attempts**, against USD 1.00. This includes 29 superseded/nonfinal attempts; final-cohort read denominators exclude those withdrawn pages, while their spend stays in the ledger. Reservations are at list price without a free-tier deduction, not invoice readback. [Ledger](google/ledger.jsonl); [pricing](receipts/pricing.json); [official price](https://cloud.google.com/products/document-ai/pricing).

The first ELSTAT census omitted `/Mag/` and pagination. It was withdrawn, the full frame was re-enumerated, and its random sample was repeated. The original 30 page selections and 29 paid reads remain identified in [the correction receipt](receipts/elstat-census-correction.json) and [the superseded manifest](receipts/superseded-elstat-book-only/pages_elstat.jsonl). They are not quietly refunded or treated as the final random sample.

**Material execution limits:** the single uniform Gazette draw contains no pre-1900 item, so the requested early-period page stratum is unqualified; no extra item was silently added against A0’s item limit. Anemi had 25 historical request starts below two seconds during an overlapping catalogue refresh; the shared host guard was then installed. [Pacing audit](receipts/anemi-pacing-audit.json). Its viewer requests stayed within 50. Whole-source supply remains unproven where only a lower-bound catalogue frame was established.

## Source results

`usable` means P1 content/confidence admission + codec v1 + G1b-negative + no exact crop/label duplicate. It does **not** mean physically adjudicated text. Local native checks found residual multi-row proposals that G1b clears. “Expected Google” is a **proposal after local unblinded spot review**, with the named failures retained; Y is provisional, and N can refer to unresolved raw-stream defects rather than every row being wrong.

| Source | Sampled / passed / excluded reason | Contact sheet | Read pages, final (+nonfinal attempts) | USD, all attempts | Lines | Admitted | Usable | Primary usable/read page | Notable Google failures seen | Proposed expected Google |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| openarchives | 30 / 29 / median_text_line_below_10px:1 | [sheet](contact_sheets/openarchives.jpg) | 29 (+0) | 0.0435 | 3,358 | 2,743 | 2,281 | num=1.03; head=1.31; modern=3.31; dialogue=5.24; mix=2.79; p1850=5.14; Latin=10.24; p1900=39.48; greek_poly=10.07; greek_mono=0.03 | watermark and neighbouring-row contamination in a retained proposal; parallel-language columns merged in raw Google lines | **N** — c011 remains usable despite a multi-row bibliographic crop and library-watermark contamination. Greek/Latin parallel-column c009/c026/c002 are withheld. |
| kosmopolis | 30 / 30 / none | [sheet](contact_sheets/kosmopolis.jpg) | 30 (+0) | 0.0450 | 1,331 | 1,228 | 987 | num=0.93; p1850=7.13; dialogue=3.70; greek_mono=0.43; mix=0.70; p1900=18.83; head=0.87; Latin=0.30 | raw cross-column mergers; inspected examples withheld, while selected usable single rows have plausible literal labels | **Y** — Provisional after screening: inspected usable c016/c020/c040/c025 are single physical rows and broadly match printed text. c015/c002 cross-column examples are withheld; marks still require blind adjudication. |
| pleias | 30 / 30 / none | [sheet](contact_sheets/pleias.jpg) | 30 (+0) | 0.0450 | 3,388 | 2,918 | 2,247 | p1850=54.33; dialogue=3.80; head=1.17; greek_mono=0.93; p1900=5.50; num=2.87; mix=1.03; Latin=0.03; greek_poly=5.23 | multi-row residuals after G1b; separate cross-column positives/unresolved rows retained but withheld | **N** — c018 is a multi-row label still marked usable; c021 also combines printed rows. Raw cross-column c005/c006 are withheld. |
| pergamos | 30 / 28 / median_text_line_below_10px:2 | [sheet](contact_sheets/pergamos.jpg) | 28 (+0) | 0.0420 | 1,615 | 1,301 | 891 | head=0.61; num=0.93; greek_poly=2.57; greek_mono=3.29; p1900=9.86; p1850=14.07; Latin=0.04; dialogue=0.46 | two or more printed rows inside one proposed line crop; inherited G1b clears these examples | **N** — Residual multi-row labels remain geometry-negative and usable: c023/c017/c013. Printed rows are merged; rare marks still need blind checking. |
| nlg-digital | 30 / 30 / none | [sheet](contact_sheets/nlg-digital.jpg) | 30 (+0) | 0.0450 | 1,246 | 1,171 | 915 | head=0.63; dialogue=2.03; p1850=14.30; greek_mono=0.20; num=0.60; p1900=9.30; Latin=0.20; mix=0.97; greek_poly=2.27 | raw cross-column mergers and a dot-run physical count requiring blind adjudication; the inspected cross-column examples are withheld | **Y** — Provisional after screening: the inspected usable single-line cards c007/c035 match their visible text broadly; cross-column examples c003/c025 are withheld. Dot counts and marks remain unqualified. |
| elstat | 30 / 29 / blank:1 | [sheet](contact_sheets/elstat.jpg) | 29 (+29) | 0.0870 | 9,705 | 8,182 | 5,798 | modern=4.45; head=0.76; dialogue=0.28; num=176.38; Latin=7.76; mix=7.93; p1900=2.38 | Multiple-footnote/row mergers, duplicated compris, repeated table-unit cells; numeric cell yields are pipeline candidates, not checked table transcriptions. | **N** — Corrected random sample: c030 duplicates the French phrase compris and combines multiple footnotes; c001/c026/c017 expose multi-row/footnote mergers. c031 combines repeated table-unit cells. The inspected body line c014 is plausible, but the raw table/footnote stream needs the blind check. |
| government-gazette | 30 / 30 / none | [sheet](contact_sheets/government-gazette.jpg) | 30 (+0) | 0.0450 | 3,811 | 2,867 | 2,232 | modern=18.27; head=4.30; dialogue=3.67; num=6.00; p1900=40.30; greek_mono=0.93; mix=0.83; Latin=0.10 | residual row-order/multi-row error in a G1b-negative candidate; separate cross-column raw errors | **N** — c028 retains two printed rows with reversed/combined reading order and remains usable. c004/c007 cross-column examples are withheld; no pre-1900 pilot leaf. |
| lekythos | 30 / 30 / none | [sheet](contact_sheets/lekythos.jpg) | 30 (+0) | 0.0450 | 6,449 | 6,043 | 4,708 | dialogue=12.03; p1900=134.83; head=3.30; greek_mono=2.90; num=1.20; mix=2.10; Latin=0.57 | raw paragraph/column mergers and clipped neighbouring ink; these inspected examples are geometry-unresolved or codec-rejected | **N** — Long cards c013/c017/c012 expose frequent cross-column mergers; these examples are withheld. Do not approve the raw line stream before the independent blind check. |
| anemi | 20 / 20 / none | [sheet](contact_sheets/anemi.jpg) | 20 (+0) | 0.0300 | 945 | 850 | 628 | head=1.10; p1850=23.15; dialogue=1.50; num=0.80; mix=3.60; Latin=1.10; greek_mono=0.15 | wrapped multi-language glossary entries merged into one line; c021 fails codec but similar c023/c020 clear geometry | **N** — c023/c020 join wrapped dictionary entries into single labels and remain usable. Source c020 has apparent lexical/mark disagreement; requires native adjudication. |

Primary legend: p1850 = polytonic **1850–1890**, p1900 = polytonic 1900–1982, modern = modern scanned Greek, mix = Greek with Latin, head = headings/caps, num = numerics/tables. Years 1891–1899 are auxiliary and never credited to the 1850–1890 target. Other auxiliary script classes remain visible in the machine-readable counts. [Source summaries](sources.jsonl); [all compact line dispositions](lines.jsonl); [local native witnesses and decisions](receipts/local-google-review.json).

## A0 catalogue supply survey

Seed **2026101602**, Python `random.Random(str(seed)+":"+source).sample(sorted(frame,id), min(20,N))`, without replacement. OA uses the same construction with `openarchives:<collection>` and one draw per collection. Frames and draws are hash-bound in each `receipts/census-<source>.json`. The Wilson interval is 95% and covers **leaf access + scan construction + target-script pass share**, not metadata completeness or label accuracy. A one-leaf diagnostic is not a whole-item print/script guarantee.

| Source / collection | Enumerated N; scope | Verified k/n; Wilson 95% | Estimated accessible target items (CI) | Estimated pages with actual per-item cap 40 | 40/item capacity ceiling (CI) |
|---|---|---|---|---:|---|
| openarchives/Dione | 24; enumerated lower bound | 0/20; 0.0%–16.1% | 0.0 (0.0–3.9) | 0.0 | 0.0 (0.0–154.7) |
| openarchives/deltion | 1; enumerated lower bound | 0/1; 0.0%–79.3% | 0.0 (0.0–0.8) | 0.0 | 0.0 (0.0–31.7) |
| openarchives/uoi | 25; enumerated lower bound | 4/20; 8.1%–41.6% | 5.0 (2.0–10.4) | 138.8 | 200.0 (80.7–416.0) |
| kosmopolis | 44; enumerated lower bound | 15/20; 53.1%–88.8% | 33.0 (23.4–39.1) | 1,271.6 | 1,320.0 (935.1–1,563.1) |
| pleias | 7,714; complete exposed frame | 18/20; 69.9%–97.2% | 6,942.6 (5,391.8–7,499.0) | 82,154.1 | 277,704.0 (215,673.1–299,961.5) |
| pergamos | 133; complete exposed frame | 15/20; 53.1%–88.8% | 99.8 (70.7–118.1) | 2,061.5 | 3,990.0 (2,826.5–4,724.9) |
| nlg-digital | 43; complete exposed frame | 20/20; 83.9%–100.0% | 43.0 (36.1–43.0) | 1,720.0 | 1,720.0 (1,442.9–1,720.0) |
| elstat | 615; complete exposed frame | 18/20; 69.9%–97.2% | 553.5 (429.9–597.9) | 22,140.0 | 22,140.0 (17,194.6–23,914.5) |
| government-gazette | 110,505; complete exposed frame | 19/20; 76.4%–99.1% | 104,979.8 (84,411.3–109,523.6) | 817,737.0 | 4,199,190.0 (3,376,452.9–4,380,942.2) |
| lekythos | 86; enumerated lower bound | 20/20; 83.9%–100.0% | 86.0 (72.1–86.0) | 2,124.2 | 3,440.0 (2,885.7–3,440.0) |
| anemi | 574; enumerated lower bound | 2/20; 2.8%–30.1% | 57.4 (16.0–172.8) | 2,296.0 | 2,296.0 (639.8–6,911.7) |

The page point estimate is `N/n × Σ min(40, page_count)` over passing random items, with failures contributing zero. The ceiling is `40 × N × pass share`; its interval reflects pass-share uncertainty only. Length variation and row-yield uncertainty are not included in that interval. **Lower-bound frames are not extrapolated to the entire repository.** Supplemental items used to reach six sampled items never enter the random-survey numerator or denominator. [Survey data](survey.jsonl).

| Source | How the population was obtained / remaining limit |
|---|---|
| openarchives | Per eligible collection: up to 60 seeded HF link-table records individually verified against own repository offered PDF path. Counts are catalogue-bound lower bounds; HF totals alone are not scanned-print supply. Overlap exclusions: 0. [frame](population_openarchives.jsonl), [draw](draw_openarchives.jsonl), [verification](verification_openarchives.jsonl). |
| kosmopolis | All 2047 unique issue URLs exposed by all 14 current journal archives were enumerated. The eligible date-qualified lower bound uses own issue-to-article citation_date bindings, including same-day F1 bindings for two Χρυσαλλίς issues. Repeated issue endpoint timeouts prevent whole-population 1850-1930 filtering. Overlap exclusions: 0. [frame](population_kosmopolis.jsonl), [draw](draw_kosmopolis.jsonl), [verification](verification_kosmopolis.jsonl). |
| pleias | All journal links on current home page; every linked archive page; unique published issue IDs. Article galleys are not counted as items. Overlap exclusions: 0. [frame](population_pleias.jsonl), [draw](draw_pleias.jsonl), [verification](verification_pleias.jsonl). |
| pergamos | Complete public-api/search of ArchivalBook, RareBook and PsachosBook; catalogue date 1850-1982; Greek print verified in random leaf; theses excluded. Overlap exclusions: 0. [frame](population_pergamos.jsonl), [draw](draw_pergamos.jsonl), [verification](verification_pergamos.jsonl). |
| nlg-digital | Unique own-catalogue monograph search results and per-item IIIF metadata; dates 1850-1982, Modern Greek language present; Ancient-Greek-only excluded. First 500 records if complete crawl exceeds bounded census. Overlap exclusions: 0. [frame](population_nlg-digital.jsonl), [draw](draw_nlg-digital.jsonl), [verification](verification_nlg-digital.jsonl). |
| elstat | All exposed year lists for catalogue series whose title contains Yearbook or Bulletin, every linked result-page pagination and detail page for 1930-1990, and all offered /Book/ and /Mag/ PDFs; unique volume/issue PDF IDs. Overlap exclusions: 1. [frame](population_elstat.jsonl), [draw](draw_elstat.jsonl), [verification](verification_elstat.jsonl). |
| government-gazette | Every year 1833-1990 through the current official UI public simplesearch API, no text filter; unique issue-type/year/number; per-year 12000 ceiling checked. Scanned status verified in random pages, not inferred from date. Overlap exclusions: 0. [frame](population_government-gazette.jsonl.gz), [draw](draw_government-gazette.jsonl), [verification](verification_government-gazette.jsonl). |
| lekythos | Complete exposed issue-PDF lists under Ελληνικά Γράμματα collection and F1 literary catalogue nodes, freshly fetched. Lower bound on all literary books/periodicals: catalogue-wide genre enumeration not established. Overlap exclusions: 0. [frame](population_lekythos.jsonl), [draw](draw_lekythos.jsonl), [verification](verification_lekythos.jsonl). |
| anemi | 574 unique eligible own-catalogue overview records after 15 overlap exclusions. Ten metadata pages over five decade searches; empty/total-less pages before reported totals prevent a complete-census claim. Earlier 194-item partial frame was superseded before the final draw. Overlap exclusions: 15. [frame](population_anemi.jsonl), [draw](draw_anemi.jsonl), [verification](verification_anemi.jsonl). |

Open Archives uses only the pinned fresh HF link table plus repository catalogue attachment bindings. No 15 October text-shard title/date/collection projection is used. ntua (75%) and hellanicus (66.7%) fail the coordinator’s F1 host-success ≥95% rule. Dione, uoi, deltion and rep_ihu pass that F1 gate, but fresh catalogue binding established no rep_ihu frame; Dione’s later robots preflight became unavailable and failed closed. See [collection/host decisions](receipts/oa-collections.json), [HF identity](../../funnel_v1/gr/receipts/hf-link-table.json), and [supplemental scanned items](receipts/supplemental-items-openarchives.jsonl). The three OA Wilson intervals are marginal per-collection intervals; they are not falsely added into one joint 95% interval.

Kosmopolis: 2,047 issue URLs across 14 periodicals were enumerated; only 44 date-qualified eligible issue records were established during the bounded date crawl. This is not 2,047 accessible 1850–1930 items. Pleias counts unique issues, not article PDFs. Printed-page ranges in each OJS issue map the selected issue leaf to an offered article galley. [Kosmopolis frame audit](receipts/kosmopolis-exposed-frame.json). Lekythos is the freshly enumerated literary collection/issue-PDF lower bound, not a census of every book in that repository. Anemi’s search returned empty/total-less pages before reported totals; its 574 eligible records are a documented partial frame.

## Gazette census by decade

All issue types returned by every official year query were enumerated; no guessed PDF URL supplies a catalogue count. The official download formula is used only after an issue appears in the catalogue. A decade without a random item has no decade-specific scan-share estimate.

| Decade | Catalogue N | Items in uniform draw | Verified passes |
|---|---:|---:|---:|
| 1830 | 317 | 0 | 0 |
| 1840 | 346 | 0 | 0 |
| 1850 | 547 | 0 | 0 |
| 1860 | 630 | 0 | 0 |
| 1870 | 658 | 0 | 0 |
| 1880 | 3,023 | 0 | 0 |
| 1890 | 2,363 | 0 | 0 |
| 1900 | 2,850 | 0 | 0 |
| 1910 | 3,365 | 2 | 2 |
| 1920 | 3,487 | 0 | 0 |
| 1930 | 7,089 | 1 | 0 |
| 1940 | 5,842 | 1 | 1 |
| 1950 | 6,142 | 0 | 0 |
| 1960 | 11,470 | 4 | 4 |
| 1970 | 20,338 | 4 | 4 |
| 1980 | 35,295 | 7 | 7 |
| 1990 | 6,743 | 1 | 1 |

## Period-specific measured yields

| Source | Period | Read pages | Usable | Disjoint primary rows/read page |
|---|---|---:|---:|---|
| openarchives | modern | 4 | 121 | num=2.25; head=1.00; modern=20.75; dialogue=4.25; mix=2.00 |
| openarchives | poly1850 | 10 | 321 | p1850=14.90; head=1.50; mix=2.60; dialogue=2.50; Latin=3.00; num=0.40; greek_poly=7.10; greek_mono=0.10 |
| openarchives | poly1900 | 10 | 1,329 | num=1.00; p1900=114.50; Latin=0.30; dialogue=10.50; head=1.90; mix=3.40; modern=1.30 |
| openarchives | pre1850 | 5 | 510 | greek_poly=44.20; num=1.40; Latin=52.80; dialogue=1.00; mix=2.60 |
| kosmopolis | poly1850 | 3 | 236 | num=1.33; p1850=71.33; dialogue=3.00; greek_mono=1.00; mix=1.33; head=0.33; Latin=0.33 |
| kosmopolis | poly1900 | 27 | 751 | p1900=20.93; dialogue=3.78; head=0.93; num=0.89; mix=0.63; greek_mono=0.37; Latin=0.30 |
| pleias | poly1850 | 25 | 1,892 | p1850=65.20; dialogue=3.60; head=1.32; greek_mono=0.96; mix=1.24; Latin=0.04; num=3.32 |
| pleias | poly1891_1899_aux | 2 | 169 | num=1.00; greek_poly=78.50; dialogue=3.50; greek_mono=1.50 |
| pleias | poly1900 | 3 | 186 | p1900=55.00; dialogue=5.67; num=0.33; greek_mono=0.33; head=0.67 |
| pergamos | poly1850 | 13 | 417 | head=0.62; p1850=30.31; num=0.46; Latin=0.08; dialogue=0.23; greek_mono=0.38 |
| pergamos | poly1891_1899_aux | 3 | 91 | head=1.33; num=1.33; greek_poly=24.00; greek_mono=3.67 |
| pergamos | poly1900 | 12 | 383 | p1900=23.00; head=0.42; greek_mono=6.33; num=1.33; dialogue=0.83 |
| nlg-digital | poly1850 | 14 | 511 | head=0.64; dialogue=2.21; p1850=30.64; greek_mono=0.36; num=0.64; Latin=0.43; mix=1.57 |
| nlg-digital | poly1891_1899_aux | 4 | 76 | num=0.50; greek_poly=17.00; dialogue=0.50; mix=0.25; head=0.75 |
| nlg-digital | poly1900 | 12 | 328 | head=0.58; num=0.58; p1900=23.25; greek_mono=0.08; dialogue=2.33; mix=0.50 |
| elstat | modern | 6 | 969 | modern=13.33; head=1.00; dialogue=0.50; num=140.50; Latin=5.50; mix=0.67 |
| elstat | poly1900 | 23 | 4,829 | mix=9.83; head=0.70; num=185.74; p1900=3.00; Latin=8.35; modern=2.13; dialogue=0.22 |
| government-gazette | modern | 12 | 731 | modern=45.67; head=5.33; dialogue=3.00; num=5.75; mix=1.08; Latin=0.08 |
| government-gazette | poly1900 | 18 | 1,501 | p1900=67.17; greek_mono=1.56; num=6.17; dialogue=4.11; head=3.61; mix=0.67; Latin=0.11 |
| lekythos | poly1900 | 30 | 4,708 | dialogue=12.03; p1900=134.83; head=3.30; greek_mono=2.90; num=1.20; mix=2.10; Latin=0.57 |
| anemi | poly1850 | 20 | 628 | head=1.10; p1850=23.15; dialogue=1.50; num=0.80; mix=3.60; Latin=1.10; greek_mono=0.15 |

## Per-class funnel

The first pair of columns preserves F1’s original bounded figures. Reconciliation applies the current OA host and NLG date/language scope and counts OJS **issues**, not articles, with ≤40 pages per item. Forward estimates use the measured **disjoint primary class yield once**. The A0 column is a planning projection over the enumerated frames and observed period strata; it is not qualified whole-source supply. A missing stratum is unmeasured, not proof of zero supply.

| Target class | F1 reported items → pages ≤40/item | Reconciled F1 items → pages | F1 pages × measured yield | A0 frame pages with measured class support → projected pipeline rows | Target |
|---|---:|---:|---:|---:|---:|
| poly1850 | 41 → 519 | 24 → 439 | 5,352 | 71,033 → 4,467,435 | 40,000 |
| poly1900 | 80 → 994 | 48 → 800 | 69,251 | 584,711 → 37,946,058 | 50,000 |
| modern_scanned | 40 → 1,035 | 25 → 973 | 4,268 | 287,418 → 12,186,161 | 40,000 |
| mixed_greek_latin | 0 → 0 | 0 → 0 | 0 | 914,154 → 949,014 | 20,000 |
| latin | 0 → 0 | 0 → 0 | 0 | 914,351 → 271,233 | 8,000 |
| cyrillic | 0 → 0 | 0 → 0 | 0 | 0 → 0 | 12,000 |
| headings_caps | 153 → 2,088 | 85 → 1,592 | 2,751 | 923,879 → 3,532,198 | 6,000 |
| numerics_tables | 44 → 1,007 | 44 → 1,007 | 162,791 | 931,643 → 9,173,464 | 10,000 |
| leaders_indices | 44 → 1,007 | 44 → 1,007 | 0 | 0 → 0 | 4,000 |
| dialogue_fiction | 55 → 601 | 23 → 578 | 6,003 | 931,523 → 3,422,337 | 12,000 |

These are conditional silver-pipeline counts, not released training counts or independent accuracy estimates. The page sample intentionally includes six front/back-band pages per non-Anemi source; the projections retain that pilot mix. The random items verify source eligibility, while page selection and supplemental cohorts do not establish a repository-wide row-yield confidence interval. True leaders remain distinct from arbitrary ≥5-dot ellipses; `DOTS:n` is Google’s silver count, not a physically adjudicated dot count. [Funnel data](class_funnel.jsonl).

## Blind hand-off and method custody

`blind_pages/` contains all 260 **final-cohort** ≤1600-px JPEGs in one seeded global shuffle. Give the checker only that directory; keep [the page key](blind_pages_key.json) hidden. Each `label_cards/<source>/cards.jsonl` has 40 shuffled admitted-line cards with native pixel crops and Google text; keep `label_cards/<source>_key.json` hidden. Cards include admitted rows that later fail codec/geometry, as requested; usability is recorded only in the separate keys. Native crop reconstruction verifies the original P1 crop hash. [All page records](pages.jsonl).

Google binding: ADC, `ocr-ground-truth-20261008`, EU processor `9a98b7aca3c19561`, `pretrained-ocr-v2.1-2024-08-07`, symbols enabled, no language hints. Every attempt is fsync-reserved before OAuth/provider network I/O; failed/ambiguous attempts are not retried or refunded locally. Embedded page images are stripped before saving provider responses. [Binding](receipts/processor-binding.json).

P1 admission uses confidence ≥0.89 with caps ≥3 letters, digit share ≥40%, literal dot-run/DOTS handling, tall-heading crops and the unchanged bad-page rule. Codec v1 is unchanged. G1b’s exact P1-bound source files were restored read-only from Git because its old worktree no longer exists. Initial execution imported the original sibling P1 files; the final runner imports hash-identical local copies through a path adapter. [Method identities](receipts/method-bindings.json); [geometry source restoration](receipts/geometry-source-restoration.json). No detector, recognizer, admission or codec implementation was changed. Primary allocation additionally withholds historical-Modern-Greek body quota credit from the two conservatively identified ancient/bilingual OA editions; pre-1900 Greek-mono OCR is not relabelled modern merely because marks were lost. [Allocation scope](receipts/primary-allocation-scope.json). Exact ID/URL/title overlap screening is not a certification of cross-repository edition identity.

PDFs are rendered grayscale at ≤200 dpi and ≤3500 px long side. Review JPEGs are ≤1600 px. A page/read is one published PDF page or canvas raster; some rasters contain a facing-page pair, which is disclosed rather than counted as two paid reads. PDF scan classification records image/text drawing objects, including hidden OCR behind opaque full-page scans. Published raster endpoints are scan candidates and retain their native source identity; source contact sheets provide visual format evidence. The detector supplies median line height and skew. Blank, cover/plate and handwriting suspicion fields are diagnostics rather than certified content labels. Selected low-resolution/blank/born-digital pages remain in sampled/excluded counts.

Current image storage: **543.7 MB**, below 600 MB. Transient line crops are reconstructed from native page rectangles for the selected cards; hashes, geometry and line ledgers remain. Only this output directory was cleaned. Superseded native rasters may be removed while their review witnesses/receipts and paid-read accounting remain. No CAPTCHA or access-control workaround, no credential file, no push, no training or publication.

## Validation and commit

[Validation receipt](receipts/validation.json) separates artifact checks from the retained task/quality exceptions. [Commit receipt](receipts/commit-status.json) records the actual commit outcome. If the managed worktree’s shared Git metadata rejects `index.lock`, the source-bound [commit helper](commit_gr.py) validates the final file manifest and commits only this hand-off from an ordinary owner shell; it never pushes.

F2-GR: done | sources: 9 pages: 260/256/256 usd: 0.4275 | usable/page: openarchives=78.66 kosmopolis=32.90 pleias=74.90 pergamos=31.82 nlg-digital=30.50 elstat=199.93 government-gazette=74.40 lekythos=156.93 anemi=31.40 | expected_google: 2Y/7N | commit: blocked
