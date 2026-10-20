# F1-GR — Greek institutions funnel verification

Run date: 2026-10-16T17:39:00.190363+00:00. Branch `sol/funnel-gr`. No Google requests, collection admission, cloud compute or spend. No push.

**Commit status:** the managed worker could not create the shared worktree `index.lock`, which lies outside its writable roots. No worker commit exists. [commit-blocker.json](receipts/commit-blocker.json) records the refusal; `python3 docs/records/harvest/funnel_v1/gr/commit_gr.py` is the guarded owner-side commit command. A source-bound patch is supplied under ignored `bulk/F1-GR.patch`.

**Readout:** individual access is fresh-decode evidence; all supply counts below are bounded, enumerated lower bounds. A catalogue total or a plausible URL is never counted as an accessible item. No source has demonstrated the complete usable-row quota.

Pages/min is **decoded witness pages per minute** in the first continuous cohort containing ≥50 decoded pages over ≥5 items. Gaps above 60 seconds split exploratory runs; sources without such a cohort use pooled active segments and are marked in `rate_benchmark`. Intervening polite waits and catalogue work remain included. The full wall-span rate is retained in JSONL. Whole-PDF rates and sizes are separate. A PDF download is one network fetch even when several pages are rendered. Timing includes the local render; this is not an OCR throughput measurement. Sequential and concurrency-three cohorts are separated in machine-readable metrics.

| source | access path Y/N | pages/min | success % | failure modes | blocker | candidate items with page access per period (and target class) | overlap with collected/test | proposed decision + one-line reason | alternative named |
|---|---|---:|---:|---|---|---|---|---|---|
| Open Archives / HF | Y | 28.19 | 58.0 | robots/refused preflight: 10, HTML/non-PDF (includes restricted-resource pages): 24, PDF above probe byte bound: 3, HTTP 403: 2, HTTP 401: 8, HTTP 500: 8 | Resolve and bind the text-shard metadata correctly; host-specific verified subsets only. [receipt](receipts/oa-projection-rebinding.json) | all access {'unknown': 17, '1950': 1, '1980': 1, '1970': 2, '1930': 2, '1960': 1, '2010': 22, '2020': 14, '1900': 4, '1920': 3, '1940': 1, '1910': 3, '1850': 1, '2000': 3, '1990': 1}; new target {'1950': 1, 'unknown': 1, '1980': 1, '1930': 2, '1960': 1, '2020': 11, '1900': 4, '2010': 4, '1920': 3, '1940': 1, '1910': 3, '1850': 1, '2000': 2}; classes {'poly1900': 16, 'headings': 35, 'modern': 17, 'poly1850': 1} | {'no exact match; edition unresolved': 74, 'collected': 2} | alternative — Resolve and bind the text-shard metadata correctly; host-specific verified subsets only. | ELSTAT and Pergamos scanned print |
| Kosmopolis | Y | 67.65 | 100.0 | none in media sample | Only a bounded issue/article cohort is qualified. Counted unit: 20 articles in 2 issues / 1 periodicals, not 20 volumes. [receipt](candidates_kosmopolis.jsonl) | all access {'1860': 20}; new target {'1860': 17}; classes {'poly1850': 17, 'headings': 17, 'dialogue': 17} | {'no exact match; edition unresolved': 20} | continue-partial — Only a bounded issue/article cohort is qualified. Counted unit: 20 articles in 2 issues / 1 periodicals, not 20 volumes. | Pleias / Lekythos literary periodicals |
| Pleias | Y | 65.23 | 100.0 | none in media sample | Short article PDFs work; volume-scale supply is not established. Counted unit: 20 articles in 2 issues / 1 periodicals, not 20 volumes. [receipt](candidates_pleias.jsonl) | all access {'1900': 20}; new target {'1900': 19}; classes {'poly1900': 19, 'headings': 19, 'dialogue': 19} | {'no exact match; edition unresolved': 20} | continue-partial — Short article PDFs work; volume-scale supply is not established. Counted unit: 20 articles in 2 issues / 1 periodicals, not 20 volumes. | Kosmopolis / Lekythos |
| Pergamos (UoA) | Y | 41.17 | 100.0 | none in media sample | Printed books work; typed-thesis sample is born digital; sampled volumes below quota. [receipt](candidates_pergamos.jsonl) | all access {'1860': 5, '1880': 8, '1900': 3, '1910': 7, '1890': 1, '2010': 1}; new target {'1860': 5, '1880': 8, '1900': 3, '1910': 7, '1890': 1}; classes {'poly1850': 13, 'headings': 24, 'poly1900': 10} | {'no exact match; edition unresolved': 25} | continue-partial — Printed books work; typed-thesis sample is born digital; sampled volumes below quota. | NLG IIIF / Kosmopolis |
| NLG digital library | Y | 40.30 | 100.0 | none in media sample | IIIF works; mixed-language/Ancient Greek content needs item selection. [receipt](candidates_nlg-digital.jsonl) | all access {'1670': 1, '1910': 5, '1890': 6, '1800': 1, '1960': 1, '1870': 2, '1880': 1, '1690': 1, '1900': 1, '1790': 1, '1850': 1, '1830': 1, '1840': 2}; new target {'1670': 1, '1910': 3, '1890': 5, '1800': 1, '1960': 1, '1870': 2, '1880': 1, '1690': 1, '1900': 1, '1790': 1, '1850': 1}; classes {'headings': 18, 'poly1900': 5, 'poly1850': 4} | {'no exact match; edition unresolved': 24} | continue-partial — IIIF works; mixed-language/Ancient Greek content needs item selection. | Pergamos printed books |
| NLG newspapers | N | 0.00 | 0.0 | HTTP 404: 1 | No fresh page raster; stale viewer link and unavailable issue frames. [receipt](receipts/nlg-newspapers-blocker.json) | all access {}; new target {}; classes {} | {} | alternative — No fresh page raster; stale viewer link and unavailable issue frames. | NLG digitalcollections@nlg.gr; Kosmopolis / Lekythos |
| ELSTAT dlib | Y | 9.37 | 100.0 | none in media sample | Scanned yearbooks work; later yearbook is born digital; 1859 is not yearbook start. [receipt](receipts/elstat-yearbook-years.json) | all access {'1930': 9, '1950': 6, '1960': 4, '1970': 1, '1980': 1, '1990': 1, '2000': 1, '2010': 1}; new target {'1930': 9, '1950': 6, '1960': 4, '1970': 1, '1980': 1, '1990': 1, '2000': 1}; classes {'numerics': 23, 'leaders': 23, 'modern': 23} | {'no exact match; edition unresolved': 24} | continue-partial — Scanned yearbooks work; later yearbook is born digital; 1859 is not yearbook start. | Historic ΦΕΚ / Pergamos |
| ΦΕΚ / Government Gazette | Y | 254.51 | 95.5 | robots/refused preflight: 1 | Historic scans verified; only sampled issues count as supply. [receipt](candidates_government-gazette.jsonl) | all access {'1830': 2, '1840': 1, '1850': 2, '1860': 1, '1870': 1, '1880': 1, '1890': 1, '1900': 2, '1910': 1, '1920': 1, '1930': 1, '1940': 1, '1950': 2, '1960': 1, '1970': 1, '1980': 1, '1990': 1}; new target {'1830': 2, '1840': 1, '1850': 2, '1860': 1, '1870': 1, '1880': 1, '1890': 1, '1900': 2, '1910': 1, '1920': 1, '1930': 1, '1940': 1, '1950': 2, '1960': 1, '1970': 1, '1980': 1, '1990': 1}; classes {'numerics': 21, 'headings': 21, 'leaders': 21, 'poly1850': 6, 'poly1900': 11} | {'no exact match; edition unresolved': 21} | continue-partial — Historic scans verified; only sampled issues count as supply. | ELSTAT / official ET Museum–Library contact |
| Bank of Greece | Y | 96.60 | 83.3 | truncated/incomplete body: 1 | Sampled reports are born digital; historical scanned-report route remains unqualified. [receipt](receipts/bank-of-greece-blocker.json) | all access {'2000': 1, '2010': 4}; new target {}; classes {} | {'no exact match; edition unresolved': 5} | alternative — Sampled reports are born digital; historical scanned-report route remains unqualified. | ELSTAT scanned reports / BoG library historical digitisation enquiry |
| Psifiothiki (AUTh) | N | 0.00 | 0.0 | robots/refused preflight: 1 | robots.txt disallows *.pdf; no PDF requested after refusal. [receipt](receipts/robots/f3f8394354db2442.json) | all access {}; new target {}; classes {} | {} | alternative — robots.txt disallows *.pdf; no PDF requested after refusal. | Pergamos / NLG IIIF printed books |
| Lekythos (University of Cyprus) | Y | 116.37 | 100.0 | none in media sample | Literary print scans verified; bounded issue cohort below class quota. [receipt](candidates_lekythos.jsonl) | all access {'1920': 12, '1930': 7}; new target {'1920': 12, '1930': 7}; classes {'poly1900': 19, 'dialogue': 19, 'headings': 19} | {'no exact match; edition unresolved': 19} | continue-partial — Literary print scans verified; bounded issue cohort below class quota. | Pleias / Kosmopolis |
| Medusa (Veria) | N | — | — | not sampled / blocked before media | JavaScript shell and empty published content responses; no page/PDF route verified. [receipt](receipts/medusa-blocker.json) | all access {}; new target {}; classes {} | {} | alternative — JavaScript shell and empty published content responses; no page/PDF route verified. | Provider-supported export/IIIF; Pergamos / NLG printed books |
| Anemi | Y | 25.68 | 100.0 | none in media sample | 50-page cap completed; five measured books already collected; no new supply census. [receipt](receipts/anemi-run.json) | all access {'1860': 5}; new target {}; classes {} | {'collected': 5} | continue-partial — 50-page cap completed; five measured books already collected; no new supply census. | Kosmopolis / Pleias / Pergamos for new editions |
| Gennadius | N | — | — | not sampled / blocked before media | On-demand scanning is not an existing machine acquisition route. [receipt](receipts/prior/gennadius/source-assessment.json) | all access {}; new target {}; classes {} | {} | drop — On-demand scanning is not an existing machine acquisition route. | Pergamos / NLG IIIF Greek print |
| Laskaridis Travelogues | N | — | — | not sampled / blocked before media | No existing printed-Greek-prose machine route established. [receipt](receipts/prior/laskaridis-travelogues/source-assessment.json) | all access {}; new target {}; classes {} | {} | drop — No existing printed-Greek-prose machine route established. | Kosmopolis / Pleias Greek prose |

## Per-class supply at ≤40 pages per item

These are candidate **pages**, not usable or labelled rows. Class tags are source/format leads; headings, numerics, leaders and dialogue still need the later page/line pilot. Unbound document metadata, retained test matches and already-collected books are excluded from new-item totals. Cross-repository edition equivalence remains a screening limitation. The same item can appear in several classes; these rows are not additive. `poly1850` uses 1850–1890 inclusive; `poly1900` uses 1900–1982 inclusive.

| target class | new candidate sources | candidate items | pages available at ≤40/item | item gate / status |
|---|---|---:|---:|---|
| poly1850 | {'openarchives': 1, 'kosmopolis': 17, 'pergamos': 13, 'nlg-digital': 4, 'government-gazette': 6} | 41 | 519 | 112 items required; partial |
| poly1900 | {'openarchives': 16, 'pleias': 19, 'pergamos': 10, 'nlg-digital': 5, 'government-gazette': 11, 'lekythos': 19} | 80 | 994 | 98 items required; partial |
| modern | {'openarchives': 17, 'elstat': 23} | 40 | 1035 | 80 items required; partial |
| Greek+Latin | No verified new supply in this track | 0 | 0 | 50 items required; unproven |
| Latin | No verified new supply in this track | 0 | 0 | usable-row quota unmeasured; unproven |
| Cyrillic | No verified new supply in this track | 0 | 0 | 30 items required; unproven |
| numerics | {'elstat': 23, 'government-gazette': 21} | 44 | 1007 | usable-row quota unmeasured; partial |
| headings | {'openarchives': 35, 'kosmopolis': 17, 'pleias': 19, 'pergamos': 24, 'nlg-digital': 18, 'government-gazette': 21, 'lekythos': 19} | 153 | 2088 | usable-row quota unmeasured; partial |
| leaders | {'elstat': 23, 'government-gazette': 21} | 44 | 1007 | usable-row quota unmeasured; partial |
| dialogue | {'kosmopolis': 17, 'pleias': 19, 'lekythos': 19} | 55 | 601 | usable-row quota unmeasured; partial |

Known exact raster overlap: **22** cross-item groups in [exact-page-overlap.json](receipts/exact-page-overlap.json), including article PDFs sharing a boundary page. These known duplicates are subtracted before the 40-page cap, and wholly duplicated short items are excluded from new supply. Rescans and unseen pages are not asserted distinct. Fetch-rate counts still include the requests actually made.


## Script verification

A manual check uses one fresh decoded leaf per listed sampled item, bound to JPEG hashes in [script-review.json](receipts/script-review.json). The two demonstrated unreliable mixed pools meet the ≥20-item check: Open Archives and NLG digital. A Greek catalogue tag is not treated as proof of the script on every leaf.

| source | sampled items | Greek visibly present | verified share |
|---|---:|---:|---:|
| anemi | 5 | 4 | 80.0% |
| bank-of-greece | 5 | 5 | 100.0% |
| elstat | 24 | 24 | 100.0% |
| government-gazette | 21 | 21 | 100.0% |
| kosmopolis | 20 | 20 | 100.0% |
| lekythos | 19 | 19 | 100.0% |
| nlg-digital | 20 | 18 | 90.0% |
| openarchives | 36 | 32 | 88.9% |
| pergamos | 24 | 24 | 100.0% |
| pleias | 20 | 20 | 100.0% |

Open Archives includes an English leaf, a Latin leaf, an uncertain poster and a non-Greek manuscript counterexample. NLG includes two English leaves. Anemi’s five-book cap includes a French-only sampled leaf in a bilingual volume; the cap was not expanded. These are leaf-script observations, not whole-volume language or within-line mixing classifications.


## Routes, rate details and rights

| source | verified pattern / stopping point | authentication | median / p90 s per decoded page | median original bytes per decoded page | PDFs/min; MB/PDF; pages/PDF; first-page seconds |
|---|---|---|---:|---:|---|
| Open Archives / HF | Repository item → direct PDF from revision-pinned external_pdfs.parquet; cached text projection is not identity-safe. | cached HF login for table; repository PDFs public | 1.08 / 3.28 | 1114025 | 2.46; 1.19; 8; 2.96 |
| Kosmopolis | /index.php/<journal>/issue/view/<issue> → article/view/<article>/<galley> → article/download/<article>/<galley>/<file> | none | 0.40 / 0.66 | 579345 | 19.05; 2.13; 4; 1.62 |
| Pleias | /index.php/kritiki/issue/view/<issue> → article/view/<article>/<galley> → article/download/<article>/<galley>/<file> | none | 0.47 / 1.60 | 1304676 | 1.32; 3.17; 2; 2.11 |
| Pergamos (UoA) | /item/uoadl:<id> → public-api/search published Page.webFile → /public-api/files/uoadl/<file-id>/payload-inline | none for published files | 0.98 / 1.05 | 129062 | 0.15; 3.29; 377; 0.65 |
| NLG digital library | /nlg-repo/dl/el/browse/<item> → /nlg-repo/dl/el/iiifmetadata/<item> → published IIIF canvas image @id | none | 0.96 / 1.34 | 740592 | 0.00; —; —; — |
| NLG newspapers | /ns/ftr.asp → POST /ns/search.asp → obsolete www.nlg.gr/digitalnewspapers/ns/pdfwin_ftr.asp; current /ns/pages_ftr.asp reports unavailable | none | — / — | — | 0.00; —; —; — |
| ELSTAT dlib | http://dlib.statistics.gr/portal/page/portal/ESYE/categoryyears → yeararticles → showdetails?p_id=<id> → /Book/<code>.pdf | none | 1.93 / 16.46 | 7184094 | 3.26; 66.71; 534; 15.65 |
| ΦΕΚ / Government Gazette | search.et.gr official UI getFekLink → https://ia37rg02wpsa01.blob.core.windows.net/fek/<issue:02>/<year>/<year><issue:02><number:05>.pdf | none | 0.16 / 0.47 | 85307 | 12.94; 0.31; 4; 0.92 |
| Bank of Greece | Governor report page → publication catalogue static PDF links → /Publications/ekthdkth<year>.pdf | none | 0.48 / 1.02 | 730223 | 3.15; 7.30; 361; 4.61 |
| Psifiothiki (AUTh) | /collection/Rare Books → /record/<id> → /record/<id>/files/<name>.pdf (robots-disallowed) | none | — / — | — | 0.00; —; —; — |
| Lekythos (University of Cyprus) | /archive/item/<id> → /archive/download/<published-uuid>.pdf | none | 0.24 / 1.14 | 2671930 | 34.55; 25.74; 24; 1.14 |
| Medusa (Veria) | Current Iguana books page → published Vfocus Session/staticContent services returned empty bodies; no printed item media path | none | — / — | — | —; —; —; — |
| Anemi | logged-in catalogue pdf_pager.php iframe → pdf_split.php?filename=<published-path>&pageno=<n>&pagenum=1 | held account; environment only; memory-only cookies | 2.01 / 2.33 | 76260 | 25.68; 0.08; 1; 2.01 |
| Gennadius | No fetch, per brief; existing inventory describes on-demand scanning | not probed | — / — | — | —; —; —; — |
| Laskaridis Travelogues | No fetch, per brief; existing inventory is illustration-oriented | not probed | — / — | — | —; —; —; — |

Every candidate records scan rights, text rights, published licence string (null when not recovered), access-terms URL, restriction flags and overlap evidence. Rights were recorded without acting as an acquisition gate. Public access is not treated as a reuse licence. The original declarations are preserved in the copied inventory source assessments; per-item overrides are retained verbatim as metadata.

Anemi’s fresh terms receipt records: “Systematic storage or printing of the whole content of the digital items is strictly forbidden.” The owner decides rights. The test used held account credentials only in memory, no `pdf_dump.php`, no CAPTCHA solving, and exactly 50 ordinary one-page viewer responses over five books. See [terms](receipts/anemi-terms.json), [run](receipts/anemi-run.json), and [transport](receipts/anemi-transfer.jsonl).

Psifiothiki’s `*.pdf$` robots rule was honoured. No query-string trick, mirror path, login, or access-control workaround was used to fetch those PDFs. NLG newspapers: [official digital collections contact](https://digitalcollections.nlg.gr/nlg-repo/dl/el/about.html), `digitalcollections@nlg.gr`; no message sent. Medusa: request a supported current item export/page interface from Veria Public Library; no request sent.

## Open Archives: identity, hosts and physical construction

The fresh HF table is pinned by revision and hash in [hf-link-table.json](receipts/hf-link-table.json). The 15 October cached text metadata projection contains unrelated title/date/collection and direct-PDF combinations. [Exact URL rebinding](receipts/oa-projection-rebinding.json) maps its first 60 fresh PDFs to **five**, rather than the ten projection labels. The unbound title/date/ocr_success population is never counted as dated new scanned supply. Additional directly link-table-bound probes are separate in [oa-external-physical.jsonl](receipts/oa-external-physical.jsonl).

Physically decoded, link-table-bound distinct PDFs: **76 across 13 collections**. This is a deliberately bounded access/format sample, not a random population scan-share estimate.

| actual HF collection | distinct decoded PDFs | scanned body verified | all sampled pages scanned | born-digital content | uncertain / mixed construction |
|---|---:|---:|---:|---:|---:|
| Dione | 6 | 6 (100.0%) | 6 | 0 | 0 |
| apothesis | 2 | 0 (0.0%) | 0 | 2 | 0 |
| deltion | 2 | 2 (100.0%) | 0 | 0 | 0 |
| ekke | 2 | 0 (0.0%) | 0 | 1 | 1 |
| elocus | 2 | 0 (0.0%) | 0 | 2 | 0 |
| hellanicus | 6 | 6 (100.0%) | 6 | 0 | 0 |
| ktisis | 2 | 0 (0.0%) | 0 | 2 | 0 |
| makedonika | 2 | 0 (0.0%) | 0 | 0 | 2 |
| ntua | 36 | 27 (75.0%) | 27 | 9 | 1 |
| pergamos | 6 | 0 (0.0%) | 0 | 5 | 1 |
| psepheda | 2 | 0 (0.0%) | 0 | 2 | 0 |
| rep_ihu | 6 | 4 (66.7%) | 4 | 1 | 1 |
| uoi | 2 | 2 (100.0%) | 2 | 0 | 0 |

Fresh repository catalogue rebinding verified an exact offered PDF-attachment path and title for **48/60** earlier documents. Those fresh catalogue dates, where present, replace the discarded projection dates; the old pipeline `ocr_success/page_count/polytonic_ratio` binding remains unresolved. See [catalogue rebinding receipts](receipts/oa-catalogue-rebinding).

| decade (pre-2000 first) | decoded scanned-body documents | new class candidates after overlap/script screening | capped candidate pages |
|---|---:|---:|---:|
| 1850 | 1 | 1 | 40 |
| 1900 | 4 | 4 | 4 |
| 1910 | 3 | 3 | 3 |
| 1920 | 3 | 3 | 23 |
| 1930 | 2 | 2 | 13 |
| 1940 | 1 | 1 | 1 |
| 1950 | 1 | 1 | 40 |
| 1960 | 1 | 1 | 13 |
| 1970 | 1 | 0 | 0 |
| 1980 | 1 | 1 | 8 |
| 2000 | 2 | 2 | 53 |
| 2010 | 5 | 4 | 30 |
| 2020 | 11 | 11 | 32 |
| unknown / unbound | 11 | 1 | 40 |

Construction test: recursively enumerate PDF page objects, record text drawing-object counts/render modes and placed image bounds. A full-page image covers ≥85% of the page bounds. With no text objects it is scanned; with only invisible (render mode 3) text it is scanned with hidden OCR. Render-mode-0 OCR is also hidden when every text object is drawn **before** a decoded opaque image that covers every text bound. This refinement is bound to identical PDF hashes in [physical-rechecks.jsonl](receipts/physical-rechecks.jsonl). Visible text above an image and ambiguous constructions remain uncertain. EKT-generated DOI metadata covers are reported separately from the scanned body and excluded from candidate scanned-page counts. Dynamically regenerated PDFs whose hashes changed were not substituted into earlier witnesses. `ocr_success` never supplies the scan label. Each rendered page has its source-PDF hash, physical object evidence and retained JPEG hash.

| host (Open Archives probes only) | route attempts / qualified success | success % | complete PDF HTTP responses / non-redirect attempts | decoded pages/min | PDFs/min | median MB/PDF | median / p90 s/page |
|---|---:|---:|---:|---:|---:|---:|---:|
| anaktisis.uowm.gr | 8 / 0 | 0.0 | 0 / 8 | 0.00 | 0.00 | — | — / — |
| apothesis.eap.gr | 2 / 2 | 100.0 | 0 / 2 | 88.27 | 29.42 | 7.21 | 0.18 / 0.22 |
| dias.library.tuc.gr | 8 / 0 | 0.0 | 0 / 8 | 0.00 | 0.00 | — | — / — |
| dione.lib.unipi.gr | 6 / 6 | 100.0 | 8 / 9 | 74.76 | 24.92 | 3.36 | 0.69 / 1.21 |
| dspace.aua.gr | 8 / 0 | 0.0 | 0 / 8 | 0.00 | 0.00 | — | — / — |
| dspace.lib.ntua.gr | 48 / 36 | 75.0 | 40 / 52 | 28.35 | 1.88 | 1.32 | 1.85 / 3.40 |
| dspace.lib.uom.gr | 4 / 2 | 50.0 | 2 / 4 | 34.91 | 11.64 | 1.04 | 0.42 / 0.43 |
| ejournals.epublishing.ekt.gr | 6 / 6 | 100.0 | 13 / 13 | 35.52 | 11.84 | 5.76 | 0.96 / 1.34 |
| elocus.lib.uoc.gr | 2 / 2 | 100.0 | 2 / 2 | 5.13 | 1.71 | 4.29 | 11.11 / 15.39 |
| hellanicus.lib.aegean.gr | 9 / 6 | 66.7 | 0 / 0 | 19.14 | 14.36 | 0.03 | 2.56 / 2.58 |
| ikee.lib.auth.gr | 8 / 0 | 0.0 | 0 / 0 | 0.00 | 0.00 | — | — / — |
| ir.lib.uth.gr | 1 / 0 | 0.0 | 0 / 0 | 0.00 | 0.00 | — | — / — |
| ktisis.cut.ac.cy | 2 / 2 | 100.0 | 2 / 2 | 40.72 | 13.57 | 4.87 | 0.98 / 1.07 |
| olympias.lib.uoi.gr | 2 / 2 | 100.0 | 4 / 4 | 44.15 | 14.72 | 25.50 | 1.06 / 1.17 |
| pergamos.lib.uoa.gr | 6 / 6 | 100.0 | 6 / 6 | 65.42 | 21.81 | 0.62 | 0.85 / 1.34 |
| polynoe.lib.uniwa.gr | 1 / 0 | 0.0 | 0 / 0 | 0.00 | 0.00 | — | — / — |
| repository.academyofathens.gr | 4 / 0 | 0.0 | 0 / 4 | 0.00 | 0.00 | — | — / — |
| repository.ihu.gr | 6 / 6 | 100.0 | 0 / 0 | 19.97 | 19.97 | 0.32 | 2.81 / 3.52 |

Concurrency 3: 18 PDF fetches, 17 decoded successes; host starts still spaced at least one second. HTTP 429/503 and Retry-After, if any, are in the HTTP ledger. A short clean run cannot establish a production throttle ceiling.

## Protocol and validation record

The [exact start-timestamp audit](receipts/pacing-exact-start-audit.json) retains **166** historical intervals below the requested spacing; **95** were short by over 1 ms. The minimum was **0.949 seconds**, from a Dione robots.txt request to a PDF start. This run therefore does **not** receive a clean strict-pacing certificate. Historical rate measurements are descriptive. The limiter was corrected to serialize actual starts per host with a 100-ms margin. A fresh bounded concurrency-three check is recorded in [concurrency3-v2.json](receipts/concurrency3-v2.json); no old timing evidence was removed. The earlier Ahrefs-only Crawl-delay overapplication, which caused waiting rather than excessive request rate, is recorded separately in [rate-parser-correction.json](receipts/rate-parser-correction.json).

One separate diagnostic HEAD request to Bank of Greece robots.txt used curl’s default User-Agent instead of the required contact UA; it fetched no page body. This is recorded in [operator-diagnostics.json](receipts/operator-diagnostics.json). It is a protocol deviation, not hidden inside the instrumented acquisition ledger.

The native macOS TLS fallback kept certificate verification enabled. Raw PDF originals were discarded after measuring bytes/hashes and decoding witnesses; grayscale JPEGs remain under the 400-MB page-image cap. HF metadata-library calls and web-search discovery are outside the repository HTTP timing benchmark. Media attempts include failed route/preflight attempts and hash-bound construction rechecks; full HTTP discovery counts remain in the ledger. See [validation.json](receipts/validation.json) for artifact consistency and the retained pacing exception.

## Supply boundaries and owner questions

- Approve or revise the proposed source decisions before step 2; this report does not authorise collection.
- Open Archives needs a correctly identity-bound text-shard projection before its large `ocr_success`, date and polytonic-ratio counts can be trusted. Freshly decoded documents with unknown dates remain unknown; no decade population is extrapolated.
- ELSTAT’s catalogue year list starts at 1930. The 1859 date concerns the wider historical publication collection. Pre-1930 historical-series supply is not counted as yearbooks.
- Decide which published per-item rights and retention conditions to use; Anemi’s systematic-storage notice remains explicitly recorded.
- Cross-repository edition identity remains open where no exact ID/URL/title overlap was found. Test matches are flagged and excluded from proposed new supply.
- Within-line Greek+Latin, Cyrillic and Latin usable-row supply is not established by this Greek track. Ancient Greek script and facing-language columns are not automatically the requested modern prose or within-line mixing.
- Later page sampling and Google-output checks remain separate, unperformed steps. Candidate page totals are not usable-row forecasts.
