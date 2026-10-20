# T13c — H1 Anemi pilot sample

**300 pages from all 150 target books; 500 sampled long lines from 142 books.** Tier 1: **188**; tier 2: **217**; tier 3: **82**; reader rejected: **13**. Google list-price reservations: **USD 1.500**.

Only Anemi; two contiguous middle pages per proposal book, across volumes. No Vouli and no text-layer third vote. Owner 12 October 01:20/01:35 instructions supersede the initial broad pilot. No training set was produced.

Frozen stack `52cee3bcc882e7426bdc1018d892cd9b1bf9feac`: all 256 exported files match canonical Git blobs ([receipt](pilot_v1/stack_verification.json)). Every line carries source catalogue, public page URL, page-PDF receipt/hash, stack commit and model/source hashes. Images are files under `harvest_big`, never embedded in JSONL.

## Yield by source and decade

| Source | Decade | Books | Pages | Found | Crop gates | Sampled | Tier 1 | Tier 2 | Tier 3 | Reader reject | Unread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Anemi | 1860 | 13 | 26 | 973 | 641 | 51 | 20 | 20 | 8 | 3 | 0 |
| Anemi | 1870 | 15 | 30 | 1374 | 794 | 51 | 18 | 21 | 7 | 5 | 0 |
| Anemi | 1880 | 23 | 46 | 1823 | 1384 | 80 | 44 | 26 | 10 | 0 | 0 |
| Anemi | 1890 | 24 | 48 | 2040 | 888 | 74 | 25 | 30 | 19 | 0 | 0 |
| Anemi | 1900 | 28 | 56 | 2769 | 1291 | 86 | 30 | 31 | 20 | 5 | 0 |
| Anemi | 1910 | 20 | 40 | 2302 | 1296 | 68 | 27 | 38 | 3 | 0 | 0 |
| Anemi | 1920 | 25 | 50 | 2711 | 1645 | 84 | 22 | 48 | 14 | 0 | 0 |
| Anemi | 1930 | 2 | 4 | 208 | 93 | 6 | 2 | 3 | 1 | 0 | 0 |
| Anemi | ALL | 150 | 300 | 14200 | 8032 | 500 | 188 | 217 | 82 | 13 | 0 |

Geometry rejects: 6168; unsampled lines: 13700. Found means final `Stack().items`; suppressed candidates are separate in page receipts. Crop-gate survivors include unselected candidates; only ranked sampling candidates receive the straightener/clipping check. Reader-tier columns apply only to the sample.

## Sampling and book coverage

Minimum width = 80% of the observed column text band. Short paragraph starts/ends, page/gutter-edge touches, tall rows, bend-trigger pages and table pages are excluded. Full-width paragraph interiors rank first; candidate order alternates the two pages. Three rounds cover each eligible book before fourth lines; rich books (≥12 pre-straightener candidates) receive at most one extra, round-robin by decade. Rejected straightener candidates are replaced before the sample is frozen. Selection never uses OCR agreement.

8 books yield zero; [every book and its selected count](pilot_v1/sampling.json). Empty books remain in the denominator. [Exact proposal and path receipt](pilot_v1/run_manifest.json).

| Zero-yield book | Year | Page gate flags |
| --- | --- | --- |
| [Στοιχειώδης εκκλησιαστική ιστορία Χάριν της εν τοις Ανωτέροις Εκπαιδευτηρίοις μαθητευούσης νεολαίας. /  υπό Α. Διομήδους Κυριακού, ... εγκρίσει της Ιεράς Συνόδου και συστάσει του Υπουργείου της Παιδείας.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2F5%2F3%2F3%2Fmetadata-86-0000375.tkl&do=250422.pdf&lang=en&pageno=1&pagestart=1&width=840.96+pts&height=595.2+pts&maxpage=65) | 1879 | bend_scout |
| [Ημερολόγιον Θέμιδος](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2F0%2F5%2F9%2Fmetadata-1789632919-167952-28557.tkl&do=000477188_w.pdf&lang=en&pageno=1&pagestart=1&width=270&height=404&maxpage=330) | 1891 | non_body_page |
| [Της εν Αθήναις Φιλεκπαιδευτικής Εταιρίας τα κατά το έτος 1894-1895 πεπραγμένα.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2F2%2Ff%2F9%2Fmetadata-181-0000153.tkl&do=74179.pdf&lang=en&pageno=1&pagestart=1&width=396&height=611&maxpage=127) | 1895 | non_body_page, rotated, table |
| [Χαλιμά, ήτοι, Χίλιαι και μια νύκτες :  αραβικά διηγήματα /  μετάφρασις εις την ελληνικήν υπό ****.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2F5%2F7%2F0%2Fmetadata-1602755091-147087-4253.tkl&do=000433232_01_w.pdf&lang=en&pageno=1&pagestart=1&width=468&height=651&maxpage=156) | 1899 | non_body_page |
| [260 δημώδη ελληνικά άσματα :  από του στόματος του ελληνικού λαού της Μικράς Ασίας, Θράκης, Μακεδονίας, Ηπείρου και Αλβανίας, Ελλάδος, Κρήτης, νήσων του Αιγαίου, Κύπρου και των παραλίων της Προποντίδος /  Συλλεγέντα και παρασημανθέντα (1888-1904) υπό Γεωργίου Δ. ΠαχτίκοOυ.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2Fa%2Fc%2F4%2Fmetadata-433-0000030.tkl&do=85347_w.pdf&lang=en&pageno=1&pagestart=1&width=1031&height=728&maxpage=245) | 1905 | non_body_page, table |
| [Ανά το Βυζάντιον :  Ήτοι (εντυπώσεις Αθηναίου εκ του εις Κωνσταντινούπολιν ταξειδίου του ¨Ομίλου των Εκδρομών¨ κατά Ιούλιον του 1905) /  Ι. Ζ. Καρακατσάνη.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2Fe%2F7%2Fc%2Fmetadata-0961dd984ee587a32c0d7d0a936cbf58_1239265128.tkl&do=144047_w.pdf&lang=en&pageno=1&pagestart=1&width=726&height=516&maxpage=57) | 1906 | bend_scout, table |
| [Ταχυμετρικόν Μνημόνιον - Σημειωματάριον νέου τύπου :  εγκριθέν υπό του Συμβουλίου των Δημοσίων Έργων /  Π. Χλημιντζά & Αντύπα Αντύπα.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2Fe%2Fc%2F8%2Fmetadata-77e13f64f0373d81f00c54985e5ac73c_1267002871.tkl&do=137308_w.pdf&lang=en&pageno=1&pagestart=1&width=841&height=595&maxpage=56) | 1907 | non_body_page, table |
| [Η ελληνικότης των νομών Προύσης και Σμύρνης /  Υπό Παντ. Μ. Κοντογιάννη.](https://anemi.lib.uoc.gr/php/pdf_pager.php?rec=%2Fmetadata%2F7%2Fe%2F2%2Fmetadata-1743861070-978723-22250.tkl&do=000095581_w.pdf&lang=en&pageno=1&pagestart=1&width=411&height=570&maxpage=227) | 1919 | table |

## Reader disagreement — sample noise proxy

| Source | Decade | Sampled | Paired OK | Usable pairs | Strict disagreement | After substitutions | 95% Wilson |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Anemi | 1860 | 51 | 51 | 48 | 58.3% | 58.3% | 44.3%–71.2% |
| Anemi | 1870 | 51 | 51 | 46 | 60.9% | 60.9% | 46.5%–73.6% |
| Anemi | 1880 | 80 | 80 | 80 | 45.0% | 45.0% | 34.6%–55.9% |
| Anemi | 1890 | 74 | 74 | 74 | 66.2% | 66.2% | 54.9%–76.0% |
| Anemi | 1900 | 86 | 86 | 81 | 63.0% | 63.0% | 52.1%–72.7% |
| Anemi | 1910 | 68 | 68 | 68 | 60.3% | 60.3% | 48.4%–71.1% |
| Anemi | 1920 | 84 | 84 | 84 | 73.8% | 73.8% | 63.5%–82.0% |
| Anemi | 1930 | 6 | 6 | 6 | 66.7% | 66.7% | 30.0%–90.3% |

Overall strict disagreement: **61.4%** over 487 usable pairs. Denominator excludes service errors and geometric list-return rejects. It does not measure accuracy or population noise.

Side-by-side pieces in one vertical band are joined in x order. Stacked bands are rejected. Foreign-script/punctuation garbage outside the main row is dropped; garbage inside the row obstructs the crop and rejects it. Raw texts, all boxes, dropped pieces and confidences remain recorded.

Tier 1 = exact NFD/whitespace agreement, including tagged documented substitutions; tier 2 = ≤2 NFD edits; tier 3 = both usable readings disagree, with no label. Empty/obstructed/garbage pairs are rejected. No third-vote tier applies.

## Character emissions by source

[Full raw character table](pilot_v1/characters.csv). Counts include raw output before list cleanup, including rejected reads.

| Source | Reader | Characters | Distinct | NFD combining marks | Greek letters |
| --- | --- | --- | --- | --- | --- |
| Anemi | docai | 28157 | 255 | 5218 | 21704 |
| Anemi | vision | 27507 | 227 | 5055 | 21697 |

Rare-glyph rows; zero means absent in this sample output.

| Source | Reader | ϗ | ȣ | ϛ | ϲ | Ϲ | ϝ | ϙ | ϡ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Anemi | docai | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Anemi | vision | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Rare substitution tags: **0 lines**. Whole-word DocAI κὶ/κὰ/κὴ → Vision καὶ and χείριςον → χείρισον/χείρισὸν only, as documented in [the engine comparison](VISION_VS_DOCAI_v1.md). Other differences must still match exactly for tier 1. These are expected glyph substitutions, not confirmed rare-ink labels; no broad sigma or accent folding.

## Google cost receipt

1000 single-crop request reservations, by reader `{'vision': 500, 'docai': 500}`. USD 0.0015 per request; no monthly free allowance deducted. Persisted cross-process reservations enforce both ≤1000 calls and USD 3. No montage and no implicit retry. Interrupted reserved attempts fail closed.

Rates checked 12 October 2026: [Vision pricing](https://cloud.google.com/vision/pricing), [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). This conservative receipt counts failures/ambiguous attempts; it is not a billing-console invoice. [Cost receipt](pilot_v1/cost_receipt.json). The archived earlier pilot reserved two calls (USD 0.003), separately retained in the run manifest.

## Timings per stage per page

[All page timings](pilot_v1/timings_per_page.csv) · [Native stack substage receipts](pilot_v1/page_gates.json).

| Stage | Mean s/page | Median | p95 | Total s |
| --- | --- | --- | --- | --- |
| render_s | 0.024 | 0.023 | 0.036 | 7.234 |
| stack_s | 0.243 | 0.200 | 0.486 | 72.773 |
| page_gates_s | 0.058 | 0.037 | 0.110 | 17.520 |
| crop_s | 0.036 | 0.033 | 0.093 | 10.680 |
| straighten_s | 0.062 | 0.045 | 0.171 | 18.503 |
| total_cpu_s | 0.425 | 0.372 | 0.770 | 127.523 |
| vision_elapsed_s | 1.536 | 1.686 | 2.953 | 460.899 |
| docai_elapsed_s | 2.763 | 3.208 | 5.100 | 828.915 |

Service times sum call elapsed times within each page; both readers and four crop pairs run concurrently, so these sums are not wall time. Straightener timings include replacement attempts. Rendering uses 200 dpi grayscale; `separate_lines(tight=True, margin=0.2)` preserves the raw polygon crop.

## Ten most common gate reasons

| Reason | Line flags |
| --- | --- |
| short_paragraph_boundary | 2246 |
| page_table | 1560 |
| width_under_80pct_band | 1324 |
| height_over_body_pitch | 1223 |
| page_bend_scout | 794 |
| outside_column_band | 769 |
| ornament_or_short_fragment | 617 |
| page_non_body_page | 524 |
| page_rotated | 370 |
| straightener_multiple_bands | 170 |

Page flags propagate to each excluded line; overlapping flags do not sum to rejects. Stack catalogue suppressions (frames/ornaments/seal rims/faintness) are counted separately per page. Reader rejection flags: `{'list_return': 11, 'obstructed': 9, 'stacked_bands': 2, 'garbage': 3}`.

## Failure modes and crop links

- `column_edge_touch`: [raw crop](pilot_v1/failure_images/anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0001.raw.png), unsampled gate example, page 100; `anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0001`.
- `curled_or_clipped_body_edge`: [raw crop](pilot_v1/failure_images/anemi-95a8decfdafb3b75d6549383-vfaa1064d-p000100-l0004.raw.png), unsampled gate example, page 100; `anemi-95a8decfdafb3b75d6549383-vfaa1064d-p000100-l0004`.
- `garbage`: [raw crop](pilot_v1/failure_images/anemi-eb66b11caf8af13f2b224e0a-v28811811-p000119-l0003.raw.png), [sample card](../../harvest/pilot_review.html#anemi-eb66b11caf8af13f2b224e0a-v28811811-p000119-l0003), page 119; `anemi-eb66b11caf8af13f2b224e0a-v28811811-p000119-l0003`.
- `height_over_body_pitch`: [raw crop](pilot_v1/failure_images/anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0013.raw.png), unsampled gate example, page 87; `anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0013`.
- `horizontal_pieces_joined`: [raw crop](pilot_v1/failure_images/anemi-c20219eff76f2fbc39f4c6fd-vaeb661a6-p000049-l0045.raw.png), [sample card](../../harvest/pilot_review.html#anemi-c20219eff76f2fbc39f4c6fd-vaeb661a6-p000049-l0045), page 49; `anemi-c20219eff76f2fbc39f4c6fd-vaeb661a6-p000049-l0045`.
- `list_return`: [raw crop](pilot_v1/failure_images/anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022.raw.png), [sample card](../../harvest/pilot_review.html#anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022), page 138; `anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022`.
- `obstructed`: [raw crop](pilot_v1/failure_images/anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022.raw.png), [sample card](../../harvest/pilot_review.html#anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022), page 138; `anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022`.
- `ornament_or_short_fragment`: [raw crop](pilot_v1/failure_images/anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0032.raw.png), unsampled gate example, page 87; `anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0032`.
- `outside_column_band`: [raw crop](pilot_v1/failure_images/anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0001.raw.png), unsampled gate example, page 38; `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0001`.
- `page_bend_scout`: [raw crop](pilot_v1/failure_images/anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000099-l0001.raw.png), unsampled gate example, page 99; `anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000099-l0001`.
- `page_edge_touch`: [raw crop](pilot_v1/failure_images/anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0001.raw.png), unsampled gate example, page 100; `anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0001`.
- `page_non_body_page`: [raw crop](pilot_v1/failure_images/anemi-10519e82bcdc24b1f02832d3-v1a53f83e-p000002-l0001.raw.png), unsampled gate example, page 2; `anemi-10519e82bcdc24b1f02832d3-v1a53f83e-p000002-l0001`.
- `page_rotated`: [raw crop](pilot_v1/failure_images/anemi-89e508dc4ec07dbe0a6f861e-v9c0b4015-p000063-l0001.raw.png), unsampled gate example, page 63; `anemi-89e508dc4ec07dbe0a6f861e-v9c0b4015-p000063-l0001`.
- `page_table`: [raw crop](pilot_v1/failure_images/anemi-0cb3f67240837f77ee728005-v02def8a2-p000020-l0001.raw.png), unsampled gate example, page 20; `anemi-0cb3f67240837f77ee728005-v02def8a2-p000020-l0001`.
- `reader_disagreement`: [raw crop](pilot_v1/failure_images/anemi-043b454a8c255b6690fd3777-v410b5b9f-p000039-l0026.raw.png), [sample card](../../harvest/pilot_review.html#anemi-043b454a8c255b6690fd3777-v410b5b9f-p000039-l0026), page 39; `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000039-l0026`.
- `short_paragraph_boundary`: [raw crop](pilot_v1/failure_images/anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0026.raw.png), unsampled gate example, page 87; `anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0026`.
- `small_type_furniture`: [raw crop](pilot_v1/failure_images/anemi-0cb3f67240837f77ee728005-v02def8a2-p000021-l0028.raw.png), unsampled gate example, page 21; `anemi-0cb3f67240837f77ee728005-v02def8a2-p000021-l0028`.
- `stacked_bands`: [raw crop](pilot_v1/failure_images/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107-l0058.raw.png), [sample card](../../harvest/pilot_review.html#anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107-l0058), page 107; `anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107-l0058`.
- `straightener_multiple_bands`: [raw crop](pilot_v1/failure_images/anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0025.raw.png), unsampled gate example, page 100; `anemi-052a7a91dd9752b856b9fd8a-v007a5d7d-p000100-l0025`.
- `taller_than_neighbours`: [raw crop](pilot_v1/failure_images/anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0080.raw.png), unsampled gate example, page 49; `anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0080`.
- `width_under_80pct_band`: [raw crop](pilot_v1/failure_images/anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0007.raw.png), unsampled gate example, page 87; `anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0007`.

Visual observations:

- Library/stamp-like watermark crosses the main text and survives the geometric/catalogue gates; readers may read or suppress it differently. Examples: [line 107](../../harvest/pilot_review.html#anemi-727f1e3f8d0a3a622943e9b1-v96f8cbde-p000065-l0003) ([crop](../../harvest/pilot_review_images/anemi-727f1e3f8d0a3a622943e9b1-v96f8cbde-p000065-l0003.straight.png)), [line 214](../../harvest/pilot_review.html#anemi-b4bb45a610fbcbc974b0eb32-v8f762ccc-p000032-l0002) ([crop](../../harvest/pilot_review_images/anemi-b4bb45a610fbcbc974b0eb32-v8f762ccc-p000032-l0002.straight.png)), [line 441](../../harvest/pilot_review.html#anemi-ca065d129a9bd4a73ad7a9a2-v115e8a73-p000163-l0003) ([crop](../../harvest/pilot_review_images/anemi-ca065d129a9bd4a73ad7a9a2-v115e8a73-p000163-l0003.straight.png)).
- Neighbour accents/letter fragments remain at a crop edge despite a single main fitted band. The 50% visible-neighbour threshold misses small slivers. Examples: [line 67](../../harvest/pilot_review.html#anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0041) ([crop](../../harvest/pilot_review_images/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0041.straight.png)), [line 68](../../harvest/pilot_review.html#anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0062) ([crop](../../harvest/pilot_review_images/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0062.straight.png)), [line 70](../../harvest/pilot_review.html#anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107-l0058) ([crop](../../harvest/pilot_review_images/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107-l0058.straight.png)).
- Greek and German parallel columns were fused into one horizontal row. Box-centre column inference and the same-band list join rule do not detect this semantic cross-column error. Examples: [line 177](../../harvest/pilot_review.html#anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038) ([crop](../../harvest/pilot_review_images/anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038.straight.png)), [line 178](../../harvest/pilot_review.html#anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024-l0011) ([crop](../../harvest/pilot_review_images/anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024-l0011.straight.png)), [line 179](../../harvest/pilot_review.html#anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024-l0012) ([crop](../../harvest/pilot_review_images/anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024-l0012.straight.png)).
- Relative width passes on a narrow poem/list band although the line contains few words. The 80% band rule does not guarantee long prose in absolute character count. Examples: [line 233](../../harvest/pilot_review.html#anemi-928e34aaaa78469aacd6c7ef-vdcf1df66-p000029-l0002) ([crop](../../harvest/pilot_review_images/anemi-928e34aaaa78469aacd6c7ef-vdcf1df66-p000029-l0002.straight.png)), [line 247](../../harvest/pilot_review.html#anemi-cc5059bc91ca2b178c20008c-v549fc824-p000026-l0027) ([crop](../../harvest/pilot_review_images/anemi-cc5059bc91ca2b178c20008c-v549fc824-p000026-l0027.straight.png)), [line 249](../../harvest/pilot_review.html#anemi-cc5059bc91ca2b178c20008c-v549fc824-p000026-l0042) ([crop](../../harvest/pilot_review_images/anemi-cc5059bc91ca2b178c20008c-v549fc824-p000026-l0042.straight.png)).
- Broken/faint ink and partly missing strokes remain in passing crops. A high darkest-percentile contrast can coexist with locally unreadable characters. Examples: [line 346](../../harvest/pilot_review.html#anemi-1c3c81f346537e276486e9fd-v770c6f3b-p000021-l0058) ([crop](../../harvest/pilot_review_images/anemi-1c3c81f346537e276486e9fd-v770c6f3b-p000021-l0058.straight.png)), [line 373](../../harvest/pilot_review.html#anemi-2c8742589d947f8d749c7ba2-v83646daf-p000024-l0028) ([crop](../../harvest/pilot_review_images/anemi-2c8742589d947f8d749c7ba2-v83646daf-p000024-l0028.straight.png)), [line 374](../../harvest/pilot_review.html#anemi-2c8742589d947f8d749c7ba2-v83646daf-p000024-l0030) ([crop](../../harvest/pilot_review_images/anemi-2c8742589d947f8d749c7ba2-v83646daf-p000024-l0030.straight.png)).
- Some passing straightened strips still show residual tilt/bend or uneven baselines; mean body-clipping diagnostics do not certify every letter edge. Examples: [line 353](../../harvest/pilot_review.html#anemi-f3cfa262eedab9cd43a9e412-v3391de81-p000152-l0008) ([crop](../../harvest/pilot_review_images/anemi-f3cfa262eedab9cd43a9e412-v3391de81-p000152-l0008.straight.png)), [line 355](../../harvest/pilot_review.html#anemi-f3cfa262eedab9cd43a9e412-v3391de81-p000153-l0023) ([crop](../../harvest/pilot_review_images/anemi-f3cfa262eedab9cd43a9e412-v3391de81-p000153-l0023.straight.png)), [line 498](../../harvest/pilot_review.html#anemi-cbe5e7b92d36edf08153017b-v3a0038ff-p000124-l0069) ([crop](../../harvest/pilot_review_images/anemi-cbe5e7b92d36edf08153017b-v3a0038ff-p000124-l0069.straight.png)).
- French, Latin, German and Italian quotations/text occur in the proposed Greek books. Latin script is allowed by the garbage rule; el+grc hints may be a mismatch. Examples: [line 46](../../harvest/pilot_review.html#anemi-b7a2ad096ab8ab67b203d3cd-v646bf5b0-p000061-l0019) ([crop](../../harvest/pilot_review_images/anemi-b7a2ad096ab8ab67b203d3cd-v646bf5b0-p000061-l0019.straight.png)), [line 117](../../harvest/pilot_review.html#anemi-bc780ca03714543a92331cd2-vb9d7a49c-p000181-l0021) ([crop](../../harvest/pilot_review_images/anemi-bc780ca03714543a92331cd2-vb9d7a49c-p000181-l0021.straight.png)), [line 207](../../harvest/pilot_review.html#anemi-238fe0dd99ba050f9501d778-v98c049fe-p000121-l0030) ([crop](../../harvest/pilot_review_images/anemi-238fe0dd99ba050f9501d778-v98c049fe-p000121-l0030.straight.png)), [line 310](../../harvest/pilot_review.html#anemi-c10815de32006dc7d7354073-vecd51f4c-p000030-l0025) ([crop](../../harvest/pilot_review_images/anemi-c10815de32006dc7d7354073-vecd51f4c-p000030-l0025.straight.png)), [line 487](../../harvest/pilot_review.html#anemi-2b1d2b5340150ddc135a2b1a-v94a9e1f7-p000094-l0041) ([crop](../../harvest/pilot_review_images/anemi-2b1d2b5340150ddc135a2b1a-v94a9e1f7-p000094-l0041.straight.png)).

Limitations:

- Agreement is provisional; both readers share a vendor and can share errors.
- Noise is strict NFD reader disagreement, not CER against ground truth. Wilson intervals ignore book clustering.
- Selection is purposive: long complete rows from middle pages, with three per eligible book and at most four. It estimates sample behaviour, not the full Anemi population.
- Some books supply zero passing lines on the two requested pages; no gate was relaxed to manufacture coverage.
- No independent third reader or rare-glyph gold/exposure denominator; zero emissions do not establish incapability.
- Page/column, table, clipping and neighbour gates are heuristic. Undetected clipping, stamps and faint ink can remain.
- Unsampled geometry survivors were not straightened or read. Cheap features unmeasured on early rejects are null; chars/100px requires a reader.
- External script and destination writes were denied by the filesystem sandbox; the tested local amended fetcher and repository harvest_big are used.
- Browser pixel QA is unavailable: headless Chrome launch failed (TargetClosedError); automatic approval review denied Firefox access, so visible handoff is unverified.

## Acquisition, outputs and verification

The source fetch script and requested external destination denied writes under the session sandbox. [Minimal upstream patch](../../harvest/pilot/o4b_anemi_pages.patch) · [executed amended copy](../../harvest/pilot/_fetch/o4b_anemi_pages.py). Actual source pages: `docs/records/harvest/harvest_big/anemi_wave3_sample_t13c/`; page/crop images: `docs/records/harvest/harvest_big/t13c/`. Plan/fetch/verify preserve hash-bound resumability and the ≥2-second transport rate. Credentials remain in memory/environment, never printed or written.

[All sampled cards](../../harvest/pilot_review.html) · [All found line records](pilot_v1/records.jsonl) · [Summary](pilot_v1/summary.json) · [Fetch verification](pilot_v1/anemi_verification.json) · [Tests](pilot_v1/tests.log) · [API](../../API.md) · [Inventory](../../INVENTORY.md).

Offline validation: **1275 tests passed** (harvest, Google-reader contracts and CLI/API/provenance tests). Artifact audit checks all 14,200 records, 500 gallery IDs, 1,000 crop image references, all reader image hashes and source-secret absence. [Artifact receipt](pilot_v1/artifact_validation.json).

Acquisition verification: 150/150 records, 300/300 pages, 37,296,232 saved PDF bytes; 60 pages reused from verified receipts and 240 newly fetched. New HTTP bodies total 29,936,103 bytes including descriptors/login/robots overhead.


## Fix 1 (offline re-gate)

12 October 2026. CP-H1 HIGH 1, HIGH 2, the table-border gate and the portable
test fixture are fixed in `greekocr/harvest`. This is an offline code/gate replay:
no pilot preparation, detector inference, acquisition, sampling or Google calls.
The stored **14,200 original records / 300 pages / 500 sampled lines** remain
unchanged, including every tier, label and reader response. The input JSONL is
still SHA-256 `108c3635a5ffc3a424f5810b9491639fdee047fcd926c7423a731ed415b6cbe4`.

Physical columns now use repeated page-ink gutters plus independent box
x-extent clusters. Duplicate detections on one row contribute one gutter vote;
a minority of fused boxes cannot stretch the column clusters into one band.
Fresh extraction splits polygons **before crop gating**. Each split uses the
polygon's own blank corridor at the page gutter, and its mask preserves the
original pixels. Splits that would cut ink are rejected. Original crops covering
more than one column by **>15% of each band width** receive `crosses_column`.
Reader joins carry page column coordinates, so pieces cannot be joined across
a gutter. The archived fused originals are rejected; proposed splits carry no
inherited labels.

The neighbour gate measures actual retained ink above and below the fitted main
body, independently of a fitted neighbour's visibility. It rejects when either
side occupies **>12% of crop rows** or its ink x-span covers **>30% of crop width**;
`neighbour_sliver` includes both measured fractions and the thresholds. Own
accents and descenders use the glyph fitter's component ownership. The table
gate now requires **both long horizontal/vertical rules and a repeated short-box
lattice aligned in x and y**. Rules alone, including a scan frame, do not qualify.
Reader orchestration refuses legacy samples without `H1-fix1` gate metadata and
neighbour measurements before constructing a reader.

| Measure | Before (stored pilot) | After Fix 1 |
| --- | ---: | ---: |
| Original records evaluated | 14,200 | 14,200 |
| Page table exclusions | 18 | 1 |
| Geometry/body-font survivors before straightening | 8,207 | 8,259 |
| Candidates checked by the straightener | 675 | 8,259 |
| Gate survivors | 8,032 | 6,126 |
| Gate rejects | 6,168 | 8,074 |
| Previously accepted originals newly rejected | — | 2,012 |
| Previously rejected originals now passing | — | 106 |
| Sampled lines rejected by geometry gates | 0 | 126 |

The net change is **+1,906 rejected originals**
(2,012 added minus 106 released).
The replay runs page/crop gates on every original and body-font/straightener/ink
gates on every geometry survivor. The original pilot straightened only the
candidates considered for its 500-line sample. Therefore the increased
`straightener_multiple_bands` and clipping counts also include previously
unchecked candidates; they are not all consequences of the new sliver rule.

Flag counts below overlap and must not be added to obtain total rejects.

| Gate flag | Before | After |
| --- | ---: | ---: |
| `column_edge_touch` | 51 | 54 |
| `crosses_column` | 0 | 146 |
| `curled_or_clipped_body_edge` | 5 | 52 |
| `height_over_body_pitch` | 1,223 | 1,221 |
| `neighbour_sliver` | 0 | 1,657 |
| `ornament_or_short_fragment` | 617 | 617 |
| `outside_column_band` | 769 | 925 |
| `page_bend_scout` | 794 | 794 |
| `page_edge_touch` | 59 | 59 |
| `page_non_body_page` | 524 | 524 |
| `page_rotated` | 370 | 370 |
| `page_table` | 1,560 | 143 |
| `short_paragraph_boundary` | 2,246 | 2,191 |
| `small_type_furniture` | 155 | 153 |
| `straightener_multiple_bands` | 170 | 913 |
| `taller_than_neighbours` | 141 | 141 |
| `width_under_80pct_band` | 1,324 | 1,292 |

Of the 126 sampled lines now rejected, the original
dispositions are tier 1 **39**, tier 2
**47**, tier 3 **32**, and reader-rejected
**8**. These are annotations, not revised tiers: the
historical 188 / 217 / 82 / 13 counts remain unchanged.

The reviewer examples `39efef08… p23 l38`, `p24 l11` and `p24 l12` now carry
`crosses_column`. `1697d5cc… p106 l41` carries `neighbour_sliver`: retained upper
ink occupies **5/32 = 15.625%** of crop rows and x-span **572/796 = 71.8593%**.
The `0cb3f672… p20` prose spread has rules but no lattice and no longer receives
`page_table`. The column fixtures preserve all **6,196 / 5,846** original dark
pixels (<200) across their split crops. On p24 the right split starts at x=562
to retain the first German letter, instead of trimming at median band x=565.

Outputs are separate from `pilot_v1/`:

- [All 14,200 gate annotations](fix1/post_fix1_gate.jsonl), each with
  `post_fix1_gate`; [500 sampled annotations](fix1/sampled_post_fix1_gate.json).
- [Before/after counts and code hashes](fix1/summary.json),
  [page gate replay](fix1/page_gates.json), [replay log](fix1/regate.log),
  [independent artifact recount/custody checks](fix1/verification.json).
- [Fixture inventory](../../../tests/fixtures/harvest_fix1/INVENTORY.md),
  [test log](fix1/tests.log), [scoped re-review](../reviews/CP-H1-FIX1.md).

The explicit portable bulk resolver maps old `docs/harvest/<suffix>` paths to
the supplied `pilot_t13c/<suffix>` archive. It fails on missing files or paths
escaping that root; no local links or absolute test-fixture dependencies are
required. The historical gallery's old image references have not been rewritten.
The archive remains the source for its images and raw responses.

Reproduction (from the repository; the external root is read-only input):

```sh
HARVEST_BULK="$HOME/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m greekocr.harvest.regate \
  --records "$HARVEST_BULK/pilot_v1/records.jsonl" \
  --page-gates docs/records/harvest/pilot_v1/page_gates.json \
  --bulk-root "$HARVEST_BULK" --out docs/records/harvest/fix1
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest
```

Verification: **119 passed, 2,359 deselected**. A separate recount
matched every sidecar ID, original gate, transition count and sampled annotation;
all source code hashes match the final replay. All **532 protected repository
pilot files** and **6,807 archived page/gallery/Google files** matched the
read-only snapshots. The existing Google ledger remains at 1,000 reservations,
500 per engine. No `.git` writes or scale-up were performed.

This implementation includes a scoped self re-review and regression verification;
independent CP-H1 recertification is still required before scale-up. The separate
rare-glyph exposure/CLLG qualification and conservative tilted-row height issue
remain as disclosed in CP-H1; Fix 1 makes no new claims about either.

## Fix 2 (offline re-gate)

Fix 2 uses each straightened line's fitted baseline and x-height with the existing glyph guide fitter to define its own zone: **accent_top − 0.15·xh through descender_bottom + 0.15·xh**. A component belongs to a neighbour only when its true ink centroid is outside that zone and its vertical extent overlaps no more than 25% of its own height. Reject when the neighbouring-component union occupies **at least 12% of crop rows AND spans at least 20% of crop width**, or when a neighbouring component retains actual ink inside the zone. Empty corners of component bounding rectangles do not establish contact. Guide samples, borrowed guides, component centroids/extents/overlap and union measurements are recorded in the sidecars. When either accent guide lacks support, the complete accent band borrows the existing fitter's prior; an imputed accent bottom is not mixed with a fused capital's top to shrink the zone.

Column bands are computed for consecutive physical rows with the same local column pattern. A continuous row spanning more than 70% of page width gets its own full-width region. A fused pair's outer width alone does not establish a spanning row: repeated gutters and independent left/right detections establish multi-column regions. Short continuations stay in their region; small ornaments and non-row shapes do not stretch its bands. Vertical gaps separate blocks such as headings and poem stanzas. Extraction splits before gating using the local region, crop gates use the same bands, and reader joins receive those local coordinates. The page-wide bands are a summary.

Long horizontal and vertical rules enclosing **at least two internal closed cells** now cause `page_table`, independently of the box-lattice test. Rule segments allow mild skew and require retained ink along their length. A page frame is not an internal cell lattice.

The replay evaluated all **14,200 stored originals / 300 pages**, with no detector run, new sampling, Google calls or changes to historical labels. Body-font and straightener/ownership gates ran on every geometry survivor; the original pilot only straightened candidates considered for its sample. New splits remain unlabelled and do not inherit their fused parent's reader output.

| Measure | Stored pilot | Fix 1 | Fix 2 |
| --- | ---: | ---: | ---: |
| Original records evaluated | 14,200 | 14,200 | 14,200 |
| Gate survivors | 8,032 | 6,126 | 7,545 |
| Gate rejects | 6,168 | 8,074 | 6,655 |
| Pages excluded as table | 18 | 1 | 12 |
| Previously accepted pilot originals newly rejected | — | 2,012 | 1,083 |
| Previously rejected pilot originals now passing | — | 106 | 596 |
| Sampled geometry rejects (of 500) | 0 | 126 | 37 |
| Tier-1 sampled geometry rejects (of 188) | 0 | 39 | 13 |

Relative to Fix 1, **1,606** rejected originals now pass and **187** previously passing originals now reject. The net rejection change is **-1,419** relative to Fix 1 and **+487** relative to the stored pilot.

Flag counts overlap; neither table below should be summed to obtain total rejected records.

| Gate flag over all originals | Stored pilot | Fix 1 | Fix 2 |
| --- | ---: | ---: | ---: |
| `column_edge_touch` | 51 | 54 | 52 |
| `crosses_column` | 0 | 146 | 38 |
| `curled_or_clipped_body_edge` | 5 | 52 | 62 |
| `height_over_body_pitch` | 1,223 | 1,221 | 1,213 |
| `neighbour_sliver` | 0 | 1,657 | 263 |
| `ornament_or_short_fragment` | 617 | 617 | 617 |
| `outside_column_band` | 769 | 925 | 724 |
| `page_bend_scout` | 794 | 794 | 794 |
| `page_edge_touch` | 59 | 59 | 59 |
| `page_non_body_page` | 524 | 524 | 524 |
| `page_rotated` | 370 | 370 | 370 |
| `page_table` | 1,560 | 143 | 829 |
| `short_paragraph_boundary` | 2,246 | 2,191 | 1,941 |
| `small_type_furniture` | 155 | 153 | 170 |
| `straightener_multiple_bands` | 170 | 913 | 948 |
| `taller_than_neighbours` | 141 | 141 | 140 |
| `width_under_80pct_band` | 1,324 | 1,292 | 1,231 |

For the **500 fixed sampled lines**, the number now rejected by each reason is:

| Reason | Fix 1 sampled rejects | Fix 2 sampled rejects | Fix 2 tier-1 rejects with this reason |
| --- | ---: | ---: | ---: |
| `crosses_column` | 14 | 5 | 3 |
| `neighbour_sliver` | 112 | 17 | 5 |
| `outside_column_band` | 14 | 5 | 3 |
| `page_table` | 0 | 6 | 2 |
| `short_paragraph_boundary` | 0 | 5 | 1 |
| `width_under_80pct_band` | 0 | 5 | 2 |

**Tier-1 rejections: 13 / 188**, compared with 39 after Fix 1. The expected near-zero count was not achieved; the remaining IDs and their exact reasons are listed in [verification.json](fix2/verification.json). All 37 current sampled geometry rejects comprise historical tier 1 **13**, tier 2 **15**, tier 3 **8**, and reader-rejected **1**. These annotations leave the historical **188 / 217 / 82 / 13** tiers and original labels unchanged.

Regression outcomes:

- `ffe26907… p159 l24` and `e28081a0… p93 l38` pass with no neighbour-ownership rejection. The cycle-2 own-accent and scan-grain controls also pass.
- The cycle-1 `1697d5cc… p106 l41` sliver rejects. The ownership-filtered neighbour union measures **4/32 = 12.5%** of crop rows and **414/796 = 52.0101%** of crop-width span, **95 pixels**, with actual zone contact. The former 158-pixel body-band mask included components that do not meet the new ownership rule.
- On `d163abb4… p112`, upper prose `l30–l37` passes intact; lower fused `l5/l8/l14/l16` splits in its glossary region without dark-pixel loss. The original cycle-1 physical-column cases still reject fused parents and split before gating.
- `8e3c482e… p24 l26/l27` stays intact without an invented column. Facing-page continuations, poetry blocks and prose beside illustration fragments have added regression fixtures.
- `d80c7cca… p49` now excludes as a table with **two closed cells**. The cycle-1 framed prose control still passes.

Outputs and custody:

- [All 14,200 annotations](fix2/post_fix2_gate.jsonl) and [500 sampled annotations](fix2/sampled_post_fix2_gate.json), each carrying `post_fix2_gate`, its local bands and original tier.
- [Counts and gate source-code hashes](fix2/summary.json), [page/region/rule replay](fix2/page_gates.json), [replay log](fix2/regate.log).
- [Independent artifact recount](fix2/verification.json), [before/after input-custody receipt](fix2/input_custody.json), [143-pass test log](fix2/tests.log).
- [Fixture inventory and hashes](../../../tests/fixtures/harvest_fix2/INVENTORY.md); six byte-identical archived pages and four polygon-masked controls, with the original Fix 1 controls reused.

Verification independently reparsed every annotation and matched all IDs, original gates, tier fields, transitions, sampled reason counts and final code hashes. All **532 protected pilot files**, **47,431 archived files** and **seven Fix 1 artifacts** match the pre-edit content snapshots; the input-custody receipt binds each entire relative-path/hash manifest. The original Google receipts/ledger remain covered by those unchanged snapshots. **No network calls, Google calls, pilot rerun or `.git` writes.** The regression suite passes **143 tests, 2,359 deselected**, using the requested command. This is offline geometry verification, not new reader qualification or independent CP-H1 recertification.

Reproduction:

```sh
HARVEST_BULK="$HOME/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m greekocr.harvest.regate \
  --records "$HARVEST_BULK/pilot_v1/records.jsonl" \
  --page-gates docs/records/harvest/pilot_v1/page_gates.json \
  --bulk-root "$HARVEST_BULK" \
  --previous-gates docs/records/harvest/fix1/post_fix1_gate.jsonl \
  --out docs/records/harvest/fix2
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest
```
