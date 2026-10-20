# T7b Greek Wikisource R0, stratum (i-b)

**Status: COMPLETE.**

These artifacts are exclusively a locked test stratum for the spell-check and training tracks. Every book, page and line has `training_release_allowed=false` and `train_pool_eligible=false`. No training release or collection manifest was modified.

| Book | Author | Year | Pages | Aligned lines |
|---|---|---:|---:|---:|
| [Η Βάρβιτος](https://el.wikisource.org/wiki/Μεταγραφή:Η_Βάρβιτος.pdf) | Ιωάννης Καρασούτσας | 1860 | 30 | 475 |
| [Λυρικά ποιήματα, Αναμνήσεις](https://el.wikisource.org/wiki/Μεταγραφή:Manussos.djvu) | Αντώνιος Μανούσος | 1876 | 30 | 139 |
| [Διονύσου Διθύραμβοι](https://el.wikisource.org/wiki/Μεταγραφή:Διονύσου_Διθύραμβοι.djvu) | Φρίντριχ Νίτσε | 1917 | 23 | 378 |
| [Τα έργα του Λορέντσου Μαβίλη](https://el.wikisource.org/wiki/Μεταγραφή:Τα_έργα_του_Λορέντσου_Μαβίλη_(1922).djvu) | Λορέντζος Μαβίλης | 1922 | 11 | 117 |
| [Τὰ Οὐράνια](https://el.wikisource.org/wiki/Μεταγραφή:Σαραντάρης,_Γιώργος._Τα_ουράνια.pdf) | Γιώργος Σαραντάρης | 1934 | 22 | 137 |

Total: **5 books, 116 selected scan pages, 1246 aligned human lines**. Each book contributes at most 30 pages. The full proofread population is retained in `books.jsonl`; draws use `random.Random(seed + ':' + book_key).sample` without replacement, uniformly from every quality-3/4 page. Books with fewer than 30 eligible pages contribute all eligible pages. Seed: `T7-wikisource-r0-20261017`.

There are 138 physical page images in this task, including 17 provisional prose images and five ancillary title/imprint pages. Prose candidates were set aside because their source uses paragraph rather than printed-line breaks; no Google reads were used for that decision. This is below the 150-page cap. Only the 116 final selected pages occur in `pages.jsonl`.

Printer/publisher spread: Η Βάρβιτος — ΤΥΠΟΙΣ Π. ΣΟΥΤΣΑ ΚΑΙ Δ. ΚΤΕΝΑ.; Λυρικά ποιήματα, Αναμνήσεις — Τύποις ελληνικής ανεξαρτησίας; Διονύσου Διθύραμβοι — Τὰ Γράμματα, Ἀλεξάντρεια; Τα έργα του Λορέντσου Μαβίλη — Στέφανος Πάργας, Βιβλιοπωλείο και εκδόσεις των "Γραμμάτων"; Τὰ Οὐράνια — unrecorded. The 1917 and 1922 books share the Γράμματα imprint; printer diversity is partial, not five independently established printers.

## Disjointness

The 318 L1 IDs were resolved through the main checkout’s read-only `collection/import_real_all.jsonl` and `collection/admitted_all.jsonl`, then joined to saved wave selection/plan metadata. Importer IDs normally use `wave:book_key`; the repaired Liddell–Scott lexicon uses `mixed:page_id`, so its `-pNNNNNN` suffix is collapsed and confirmed against `admitted_all.book_key`. All 318 IDs have source and title mappings. No L1 ID has a Wikisource source. The 40 mixed IDs resolve to 33 Anemi books, six OpenArchives books and the Liddell–Scott lexicon.

Wikisource IDs use the existing eight-character SHA-256 of `el:<Commons filename>`. Commons source backlinks additionally recover Anemi record paths and their 24-character IDs, which are checked under the round1, round2 and mixed namespaces. No off-allowlist source host was contacted.

| Key | R0 coverage (books) | L1 coverage (documents) | L1 intersection | Local-20 coverage (books) | Local-20 intersection |
|---|---:|---:|---:|---:|---:|
| document_id | 5/5 | 318/318 | 0 | 20/20 | 0 |
| index_title | 5/5 | 0/318 | 0 | 20/20 | 0 |
| commons_filename | 5/5 | 0/318 | 0 | 20/20 | 0 |
| scan_sha1 | 5/5 | 0/318 | 0 | 20/20 | 0 |
| title_author_year | 5/5 | 159/318 | 0 | 17/20 | 0 |
| title_year | 5/5 | 311/318 | 0 | 20/20 | 0 |
| title_only | 5/5 | 318/318 | 0 | 20/20 | 0 |
| upstream_source_url | 3/5 | 184/318 | 0 | 13/20 | 0 |

Zero means zero intersection among resolved keys; it does not mean missing keys were invented. L1 has no recorded Commons/Index identities, 159 document bibliographies yield an author plus year, and seven parliamentary documents have no recorded year. The title-only guard covers all 318 L1 documents; title+year covers 311. Normalization folds Unicode accents, case, underscores and punctuation, and includes catalogue title aliases before author/subtitle separators. Full Commons scan SHA-1 and SHA-256 were independently computed from downloaded original bytes for all five selected scans and all 20 local Greek scans. Detailed mappings, input hashes, coverage and empty intersection arrays are in `exclusions/`.

## Alignment and custody

`harvest.py` calls the unchanged `greekocr/harvest/wikisource.py` stripper, template rules and monotone conservative aligner at similarity 0.65. Only one-to-one blocks can produce labels; unresolved templates, split/merge blocks and skipped lines do not. A second execution of the exact stripper with whitespace-only normalization retains pre-NFC Unicode; its NFC must equal the shared stripper result. Original raw wikitext, its hash and revision headers remain bound to each page.

Native inspection showed leading poem indentation colons absent from print (e.g. Βάρβιτος scan page 14). Those source lines are excluded without changing their labels; their original and NFC text remain in page evidence. Labels with no Greek character are excluded. No spelling or accent correction is derived from OCR.

T7b native crop inspection additionally excludes 3 specifically witnessed source/print discrepancies (omitted terminal punctuation; one iota-subscript/adscript difference). `qa/source_line_rejections.json` retains their original candidate records and crop hashes. These are finite source-quality exclusions after shared alignment; no human label or shared alignment rule was edited. Unlisted source/print differences may remain because visual inspection is sampled.

T7b reads each of the 116 fixed drawn page images once, using the requested EU processor/version, and reserves USD 0.0015 in this task’s `google/ledger.jsonl` before each call. Reservations survive interruptions; automatic retries of an ambiguous read are prohibited. `pages.jsonl` retains line/token boxes, returned dimensions, native coordinate mapping and raw-response hashes. Crops use the native line box with four horizontal and two vertical pixels of bounded padding. `lines.jsonl` carries literal and NFC human labels, crop hashes and alignment traces. ADC discovery uses `google.auth.default()`; an environment override takes precedence. No credentials or credential paths are recorded.

## Network, budget and validation

T7’s original `RUN_POLICY.json`, selection and exclusion receipts remain unchanged. T7b’s own deadline (within 60 minutes), 116-call limit and USD 0.30 cap are in `T7B_POLICY.json`; `T7B_INPUTS.json` binds the reused selection, exclusions, human text and drawn images. Both phases use this task’s own `limiter/` directory. T7 Wikimedia acquisition used the contact User-Agent `greek-ocr-research/0.1 (foivos.karounos@gmail.com)`, robots checks and Retry-After handling. T7b performs no Wikimedia requests or redraws. Public request receipts are in `network_receipts.jsonl`. No W1 ledger, lock or limiter was accessed.

**Metadata API limitation:** both live Wikimedia robots files disallow the standard `/w/api.php?action=query` endpoint. The robots-permitted `mobileview` API action was attempted with `maxlag=5`; both sites returned `badvalue` because that action has been retired. Metadata therefore uses permitted Index/Commons HTML and raw page reads. No disallowed API request was sent. The requested API-only metadata method could not be completed; the error receipts and robots bodies are preserved locally.

Google: **116 reservations, 116 successful reads, USD 0.1740 reserved**, hard cap USD 0.30. One request per fixed drawn page; failed or ambiguous requests remain reserved. This is list-price accounting, not a billing-invoice claim. Credential contents, paths, tokens and refresh headers are never copied or logged.

Validation: seeded draw; quality; input immutability; zero intersections; image/scan/raw/crop hashes; exact crop pixels; unchanged alignment policy; literal/NFC/source custody; locked test flags; network allowlist and rates; reservation cap; 239 fixed input hashes; exactly one reserved, uncached Google request per page; response geometry recomputed from raw evidence. Shared policy tests: **135 passed** (`policy_tests.txt`). Source policy and the existing 15 October harvest have no tracked changes. `validation.json` records `complete=true`. Timing is recorded in `T7B_COMPLETION.json`.

Binary scans, page images, crops, raw Google responses and limiter caches are local ignored evidence. `SHA256SUMS` inventories them by repository-relative path and hash; none is force-added. `commit_guard.py --check` validates the pinned parent, branch, file hashes, ignored-path exclusions and an empty index. `--commit` stages only that reviewed set and stops on a protected index.lock, with no alternate index or unguarded retry.

**Commit not created:** the guarded helper passed its read-only checks, then `git add` failed because the sandbox cannot create the worktree `index.lock` (`Operation not permitted`). No retry, alternate index, staging or commit occurred. The reviewed helper and `COMMIT_MANIFEST.json` are ready for execution in a context with Git metadata write access.

## Alignment per page

Mean aligned human lines per drawn page: **10.7414** (1246/116). Overall acceptance: 1246/2588 Google physical line boxes (48.15%). 8 pages produced zero accepted labels. The per-page rate uses all returned physical line boxes, including page numbers and non-Greek headings. Exclusions retain the unchanged template, one-to-one and similarity rules.

| Page | Aligned | Google lines | Aligned / Google lines |
|---|---:|---:|---:|
| df94dc99-p000007 | 0 | 8 | 0.00% |
| df94dc99-p000014 | 15 | 25 | 60.00% |
| df94dc99-p000025 | 12 | 29 | 41.38% |
| df94dc99-p000030 | 15 | 30 | 50.00% |
| df94dc99-p000035 | 18 | 28 | 64.29% |
| df94dc99-p000037 | 20 | 29 | 68.97% |
| df94dc99-p000041 | 19 | 30 | 63.33% |
| df94dc99-p000042 | 17 | 26 | 65.38% |
| df94dc99-p000047 | 22 | 29 | 75.86% |
| df94dc99-p000054 | 15 | 26 | 57.69% |
| df94dc99-p000063 | 9 | 27 | 33.33% |
| df94dc99-p000064 | 12 | 28 | 42.86% |
| df94dc99-p000071 | 15 | 24 | 62.50% |
| df94dc99-p000095 | 27 | 32 | 84.38% |
| df94dc99-p000117 | 22 | 28 | 78.57% |
| df94dc99-p000118 | 26 | 31 | 83.87% |
| df94dc99-p000121 | 7 | 28 | 25.00% |
| df94dc99-p000131 | 24 | 29 | 82.76% |
| df94dc99-p000137 | 24 | 32 | 75.00% |
| df94dc99-p000148 | 11 | 28 | 39.29% |
| df94dc99-p000152 | 15 | 27 | 55.56% |
| df94dc99-p000153 | 11 | 21 | 52.38% |
| df94dc99-p000154 | 15 | 24 | 62.50% |
| df94dc99-p000167 | 19 | 31 | 61.29% |
| df94dc99-p000170 | 19 | 26 | 73.08% |
| df94dc99-p000171 | 24 | 28 | 85.71% |
| df94dc99-p000175 | 15 | 25 | 60.00% |
| df94dc99-p000190 | 15 | 27 | 55.56% |
| df94dc99-p000191 | 11 | 26 | 42.31% |
| df94dc99-p000205 | 1 | 64 | 1.56% |
| bf4f6c1b-p000008 | 5 | 19 | 26.32% |
| bf4f6c1b-p000016 | 3 | 17 | 17.65% |
| bf4f6c1b-p000023 | 4 | 19 | 21.05% |
| bf4f6c1b-p000029 | 1 | 11 | 9.09% |
| bf4f6c1b-p000038 | 0 | 11 | 0.00% |
| bf4f6c1b-p000039 | 4 | 23 | 17.39% |
| bf4f6c1b-p000044 | 3 | 20 | 15.00% |
| bf4f6c1b-p000047 | 4 | 20 | 20.00% |
| bf4f6c1b-p000048 | 4 | 17 | 23.53% |
| bf4f6c1b-p000050 | 5 | 17 | 29.41% |
| bf4f6c1b-p000054 | 4 | 19 | 21.05% |
| bf4f6c1b-p000067 | 4 | 18 | 22.22% |
| bf4f6c1b-p000071 | 4 | 19 | 21.05% |
| bf4f6c1b-p000076 | 5 | 19 | 26.32% |
| bf4f6c1b-p000077 | 3 | 21 | 14.29% |
| bf4f6c1b-p000081 | 6 | 29 | 20.69% |
| bf4f6c1b-p000085 | 9 | 33 | 27.27% |
| bf4f6c1b-p000089 | 1 | 31 | 3.23% |
| bf4f6c1b-p000096 | 0 | 14 | 0.00% |
| bf4f6c1b-p000102 | 10 | 31 | 32.26% |
| bf4f6c1b-p000105 | 9 | 32 | 28.12% |
| bf4f6c1b-p000114 | 9 | 31 | 29.03% |
| bf4f6c1b-p000115 | 9 | 33 | 27.27% |
| bf4f6c1b-p000121 | 5 | 27 | 18.52% |
| bf4f6c1b-p000127 | 14 | 31 | 45.16% |
| bf4f6c1b-p000144 | 5 | 26 | 19.23% |
| bf4f6c1b-p000170 | 3 | 22 | 13.64% |
| bf4f6c1b-p000172 | 2 | 27 | 7.41% |
| bf4f6c1b-p000174 | 2 | 27 | 7.41% |
| bf4f6c1b-p000175 | 2 | 27 | 7.41% |
| e90ad4c2-p000001 | 11 | 15 | 73.33% |
| e90ad4c2-p000003 | 1 | 24 | 4.17% |
| e90ad4c2-p000004 | 0 | 34 | 0.00% |
| e90ad4c2-p000005 | 2 | 32 | 6.25% |
| e90ad4c2-p000006 | 0 | 18 | 0.00% |
| e90ad4c2-p000007 | 12 | 23 | 52.17% |
| e90ad4c2-p000008 | 24 | 30 | 80.00% |
| e90ad4c2-p000009 | 24 | 31 | 77.42% |
| e90ad4c2-p000010 | 21 | 30 | 70.00% |
| e90ad4c2-p000011 | 23 | 27 | 85.19% |
| e90ad4c2-p000012 | 22 | 28 | 78.57% |
| e90ad4c2-p000013 | 25 | 35 | 71.43% |
| e90ad4c2-p000014 | 26 | 30 | 86.67% |
| e90ad4c2-p000015 | 22 | 26 | 84.62% |
| e90ad4c2-p000016 | 15 | 20 | 75.00% |
| e90ad4c2-p000017 | 22 | 27 | 81.48% |
| e90ad4c2-p000018 | 20 | 25 | 80.00% |
| e90ad4c2-p000019 | 16 | 25 | 64.00% |
| e90ad4c2-p000020 | 19 | 21 | 90.48% |
| e90ad4c2-p000021 | 18 | 23 | 78.26% |
| e90ad4c2-p000022 | 20 | 28 | 71.43% |
| e90ad4c2-p000023 | 17 | 28 | 60.71% |
| e90ad4c2-p000024 | 18 | 26 | 69.23% |
| 45855dfb-p000016 | 1 | 16 | 6.25% |
| 45855dfb-p000029 | 1 | 3 | 33.33% |
| 45855dfb-p000031 | 2 | 2 | 100.00% |
| 45855dfb-p000033 | 30 | 41 | 73.17% |
| 45855dfb-p000041 | 6 | 16 | 37.50% |
| 45855dfb-p000043 | 2 | 2 | 100.00% |
| 45855dfb-p000044 | 0 | 5 | 0.00% |
| 45855dfb-p000054 | 17 | 37 | 45.95% |
| 45855dfb-p000080 | 10 | 24 | 41.67% |
| 45855dfb-p000081 | 29 | 39 | 74.36% |
| 45855dfb-p000086 | 19 | 21 | 90.48% |
| a3114593-p000001 | 3 | 5 | 60.00% |
| a3114593-p000003 | 4 | 4 | 100.00% |
| a3114593-p000004 | 0 | 2 | 0.00% |
| a3114593-p000005 | 9 | 14 | 64.29% |
| a3114593-p000006 | 7 | 9 | 77.78% |
| a3114593-p000007 | 6 | 9 | 66.67% |
| a3114593-p000008 | 10 | 13 | 76.92% |
| a3114593-p000009 | 10 | 12 | 83.33% |
| a3114593-p000010 | 9 | 17 | 52.94% |
| a3114593-p000011 | 5 | 8 | 62.50% |
| a3114593-p000012 | 6 | 8 | 75.00% |
| a3114593-p000013 | 7 | 9 | 77.78% |
| a3114593-p000014 | 3 | 7 | 42.86% |
| a3114593-p000015 | 8 | 10 | 80.00% |
| a3114593-p000016 | 7 | 9 | 77.78% |
| a3114593-p000017 | 10 | 12 | 83.33% |
| a3114593-p000018 | 8 | 12 | 66.67% |
| a3114593-p000019 | 17 | 19 | 89.47% |
| a3114593-p000020 | 6 | 11 | 54.55% |
| a3114593-p000021 | 1 | 43 | 2.33% |
| a3114593-p000022 | 1 | 3 | 33.33% |
| a3114593-p000024 | 0 | 3 | 0.00% |

## Visual inspection

Inspected 20 initial candidate crop/label pairs across all five books: lowest and median alignment similarity, longest label, and seeded random. Three witnessed source/print discrepancies were excluded, leaving 17 inspected emitted lines. Sheets paste native pixels without resampling. This sampled inspection does not certify every glyph, source punctuation mark, or crop edge across the harvest.

- `r0-ws-45855dfb-p000031-l0001`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-45855dfb-p000029-l0003`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-45855dfb-p000041-l0005`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-45855dfb-p000086-l0012`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-a3114593-p000001-l0004`: Native imprint has a visible full stop after 1934; the human source omits it. Candidate excluded; label unchanged.
- `r0-ws-a3114593-p000009-l0009`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-a3114593-p000008-l0010`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-a3114593-p000019-l0012`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-bf4f6c1b-p000008-l0002`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-bf4f6c1b-p000105-l0025`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-bf4f6c1b-p000127-l0005`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-bf4f6c1b-p000081-l0015`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-df94dc99-p000154-l0004`: Native heading has visible adscript iotas and a final full stop; the human source uses iota-subscript capitals and omits the full stop. Candidate excluded; label unchanged.
- `r0-ws-df94dc99-p000030-l0024`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-df94dc99-p000191-l0005`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-df94dc99-p000175-l0003`: Native heading has a visible final full stop after ΕΡΜΗΣ; the human source omits it. Candidate excluded; label unchanged.
- `r0-ws-e90ad4c2-p000009-l0027`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-e90ad4c2-p000005-l0028`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
- `r0-ws-e90ad4c2-p000010-l0021`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample. Small traces of adjacent-row ink occur at the crop edge under the frozen two-pixel vertical padding policy.
- `r0-ws-e90ad4c2-p000023-l0025`: Corresponding printed line and human wording observed in native crop; no additional source discrepancy identified in this sample.
