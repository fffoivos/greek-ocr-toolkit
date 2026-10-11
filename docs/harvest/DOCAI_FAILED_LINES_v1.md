# Document AI treatment of known R7 line-finder failures — v1

## Controls baseline (first)

101 permitted control crop IDs (85 distinct images); 80 Anemi current-output controls withheld. These are owner-verified marks, not gold OCR transcripts.

Returned layout lines: `{1: 75, 2: 18, 3: 4, 4: 4}`. Empty rate: 0.000. Mean symbol confidence: median 0.940, p05 0.812, p95 0.985. Minimum symbol confidence: median 0.491.

Characters/100 px: min 1.554, p05 2.439, p25 3.678, median 3.939, p75 4.337, p95 4.983, max 6.957.

## Scope, cache and measurement contract

Status: **complete**. The two catalogues contain 452 current-output crop IDs; 174 are withheld. The whole supplied crop directory contains 707 files, including **277 withheld Anemi files** (marked crops included). Marked-region images are not harvest inputs and were not sent. 17 additional current-output crops were derived from exact historical-number mappings. No Anemi file or page was submitted.

295 crop IDs measured from 236 distinct image SHA-256 values. Byte-identical crops share one request. Crop statistics are crop-ID weighted; character counts are unique-call weighted. Controls and multi-line catalogues share 11 distinct image hashes. An overlapping neighbour can be a clean crop even within a partly fixed multi-line mark; mark-level labels do not establish that every current-output crop is defective. These samples are development pages, not the held-out set. No harvest was made.

Processor binding: `{"location":"eu","options":{"ocrConfig":{"enableSymbol":true,"hints":{"languageHints":["el"]}}},"processor":"9a98b7aca3c19561","project":"ocr-ground-truth-20261008","user_project":"ocr-ground-truth-20261008","version":"pretrained-ocr-v2.1-2024-08-07"}`. Crop bytes, processor/options, response hash, request/receipt IDs and raw responses are retained in `docai_failed_lines/responses/<crop_id>.json`; the adapter's original receipts and ledger are also retained. A changed cache binding or an unresolved prior attempt stops the run; there is no fresh/retry switch.

Adapter parsing recoveries: 1. A successful empty page can omit default `document.text` and repeated line/symbol fields under [ProtoJSON default-value rules](https://protobuf.dev/programming-guides/json/#presence-and-default-values). The adapter now accepts that empty form. The original rejected receipt/error ledger remains intact; recovery reads its saved raw bytes and makes no API call.

Line count uses the API layout `document.pages[0].lines`, not the adapter's text-newline heuristic. A missing lines field uses an explicitly labelled fallback. Total characters excludes CR/LF but includes spaces, punctuation and combining code points. Density is that count / image width × 100. Confidence is over symbols with reported confidence; absence is null, not zero. Greek-character sets use Unicode names; exact raw characters and NFD marks are counted separately.

Operational exposure rule: multiple returned layout lines, empty text, or mean/minimum symbol confidence below the corresponding controls' p05 (0.812 mean; 0.241 minimum). These thresholds are diagnostics, not validated filters. A layout-line return can split a single curved printed row into spatial pieces; it is not proof of two printed rows. Single-line outputs without these signals are **silent candidates**, not proof of correct or incorrect transcription. Truncation/appending cannot be established from confidence or density alone: compare crop, owner observation and text in the review page. Baseline false alarms are 27/101 controls; owner controls sometimes include complete neighbours.

## Treatment by failure type

| Catalogue type | n measured / withheld crops | Page comments (Anemi withheld) | Layout-line distribution | Empty rate | Mean conf median (p05) | Min conf median | Chars/100px median (p05–p95) | Density below/above controls p05–p95 | Exposed / silent candidates | Verdict |
| --- | ---: | ---: | --- | ---: | --- | ---: | --- | --- | --- | --- |
| `missed_line` | 0 / 0 | 15 (9) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | No crop for missing ink: no Google signal; line-finder-side recovery required |
| `missed_words_in_row` | 0 / 0 | 1 (0) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | No crop for missing ink: no Google signal; line-finder-side recovery required |
| `line_start_missed` | 2 / 0 | 1 (0) | `{1: 2}` | 0.000 | 0.880 (0.847) | 0.256 | 3.944 (3.811–4.077) | 0 / 0 | 1 / 1 | Google absorbs it silently — candidates: 1; exposed: 1 |
| `missed_word_after_gap` | 0 / 0 | 1 (1) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `curl_end_cut` | 7 / 0 | 7 (0) | `{1: 6, 5: 1}` | 0.000 | 0.954 (0.823) | 0.601 | 3.946 (3.749–5.961) | 0 / 1 | 1 / 6 | Google absorbs it silently — candidates: 6; exposed: 1 |
| `multi_line_segment` | 178 / 94 | 8 (0) | `{0: 6, 1: 66, 2: 47, 3: 32, 4: 12, 5: 10, 6: 3, 7: 1, 9: 1}` | 0.034 | 0.923 (0.788) | 0.366 | 4.334 (3.103–7.523) | 7 / 59 | 112 / 66 | Google absorbs it silently — candidates: 66; exposed: 112 |
| `misaligned_crop` | 1 / 0 | 1 (0) | `{1: 1}` | 0.000 | 0.942 (0.942) | 0.377 | 4.136 (4.136–4.136) | 0 / 0 | 0 / 1 | Google absorbs it silently — candidates: 1; exposed: 0 |
| `faint_ghost_kept` | 5 / 0 | 7 (3) | `{0: 1, 1: 4}` | 0.200 | 0.765 (0.550) | 0.455 | 3.030 (0.182–3.332) | 2 / 0 | 3 / 2 | Google absorbs it silently — candidates: 2; exposed: 3 |
| `crop_extends_over_faint` | 3 / 0 | 2 (0) | `{0: 1, 1: 2}` | 0.333 | 0.635 (0.553) | 0.279 | 2.700 (0.270–2.911) | 1 / 0 | 3 / 0 | Google exposes it |
| `crosses_column` | 0 / 0 | 1 (1) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `frame_or_ornament_boxed` | 0 / 0 | 9 (9) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `stamp_or_watermark_boxed` | 0 / 0 | 3 (3) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `blob_boxed` | 0 / 0 | 1 (0) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `spread_or_columns_as_one_geometry` | 0 / 0 | 2 (2) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `fragment_crop` | 0 / 0 | 2 (0) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |
| `unclear_owner_intent` | 0 / 0 | 1 (0) | `{}` | — | — (—) | — | — (—–—) | 0 / 0 | 0 / 0 | Not measured: withheld or no reliably located crop; no Google verdict inferred |

Density outside the controls’ p05–p95 is descriptive, not an exposure signal: fonts, crop scales and short fragments differ. Types with silent candidates need line-finder-side geometry/ink filters or exclusions; Google confidence is not a crop-completeness check. Missing input is invisible to OCR. Counts for associated page-comment types overlap other types and must not be summed. Withheld-crop counts apply only to labelled crops in the two catalogues; unlocated page-comment regions have unknown crop counts, even when their whole Anemi page is withheld. Full distribution quantiles, unique-image counts and per-crop evidence are in the linked JSON/CSV.

## Page-comment coverage

Named current-owner regions are accepted only when saved R6 item geometry **and** display-number order match R7 exactly. The historical polygon is intersected with its exact R7 counterpart (share 1.0); the full output polygon is cropped from native grayscale pixels. Existing matching catalogue crops are reused. No old R4 number is guessed from today's order. Broad comments and types without a region remain page-level; their coverage is reported below, with Google evidence restricted to the two crop catalogues.

| Comment | Page | Types | Binding / scope | Crop IDs measured |
| --- | --- | --- | --- | ---: |
| O01 | `s2-3229200bf47ca465a42d-p00004` | missed_line | no_unambiguous_region; two-catalogue evidence only | 0 |
| O02 | `s2-3229200bf47ca465a42d-p00005` | curl_end_cut | exact_R6_region_intersected_with_R7 | 3 |
| O03 | `s2-3229200bf47ca465a42d-p00006` | missed_line, missed_words_in_row, multi_line_segment | no_unambiguous_region; two-catalogue evidence only | 0 |
| O04 | `s2-49598b2e848ab1f0ee1e-p00001` | missed_line, line_start_missed | exact_R6_region_intersected_with_R7 | 2 |
| O05 | `s2-49598b2e848ab1f0ee1e-p00004` | missed_line, curl_end_cut | exact_R6_region_intersected_with_R7 | 4 |
| O06 | `s2-49598b2e848ab1f0ee1e-p00005` | multi_line_segment | exact_R6_region_intersected_with_R7 | 2 |
| O07 | `s2-44b5cf9e0d680b361091-p00002` | misaligned_crop, multi_line_segment | exact_R6_region_intersected_with_R7 | 1 |
| O08 | `an-ef481610a820-p000150` | faint_ghost_kept | withheld_anemi_page | 0 |
| O09 | `an-ef481610a820-p000151` | faint_ghost_kept | withheld_anemi_page | 0 |
| O11 | `s2-93f8070059f938bda524-p00001` | faint_ghost_kept, crop_extends_over_faint | exact_R6_region_intersected_with_R7 | 6 |
| O12 | `s2-86865c33eef5932c013b-p00026` | crop_extends_over_faint | exact_R6_region_intersected_with_R7 | 2 |
| O13 | `an-c8b96a901917-p000155` | crosses_column | withheld_anemi_page | 0 |
| O15 | `an-ffccc97c07de-p000354` | missed_word_after_gap | withheld_anemi_page | 0 |
| O16 | `an-d83e7a198ade-p000099` | missed_line | withheld_anemi_page | 0 |
| O17 | `an-ef481610a820-p000181` | missed_line | withheld_anemi_page | 0 |
| O18 | `an-00f143ecce59-p000258` | missed_line | withheld_anemi_page | 0 |
| O19 | `an-1ba3fdb1436b-p000035` | missed_line | withheld_anemi_page | 0 |
| O20 | `an-00f143ecce59-p000192` | missed_line, stamp_or_watermark_boxed | withheld_anemi_page | 0 |
| O21 | `an-7792a3301892-p000059` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| O22 | `an-7792a3301892-p000104` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| O23 | `an-c99f1c450f55-p000025` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| C01 | `s2-86865c33eef5932c013b-p00005` | curl_end_cut | no_unambiguous_region; two-catalogue evidence only | 0 |
| C02 | `s2-86865c33eef5932c013b-p00007` | curl_end_cut | no_unambiguous_region; two-catalogue evidence only | 0 |
| C03 | `an-e259bbf5081c-p000198` | spread_or_columns_as_one_geometry | withheld_anemi_page | 0 |
| C04 | `an-c8b96a901917-p000068` | spread_or_columns_as_one_geometry | withheld_anemi_page | 0 |
| C05 | `an-7792a3301892-p000154` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-03 | `an-7792a3301892-p000107` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-05 | `an-7792a3301892-p000104` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-09 | `an-1be60011c435-p000215` | stamp_or_watermark_boxed | withheld_anemi_page | 0 |
| R4-10 | `s2-7534648e60694be1d180-p00018` | unclear_owner_intent | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-11 | `s2-032eaf8e6b3b83918feb-p00004` | multi_line_segment, fragment_crop | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-12 | `s2-922e617957fca8dfafd0-p00001` | blob_boxed | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-15 | `s2-86865c33eef5932c013b-p00026` | faint_ghost_kept, multi_line_segment | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-16 | `an-00f143ecce59-p000258` | missed_line | withheld_anemi_page | 0 |
| R4-18 | `an-ef481610a820-p000150` | faint_ghost_kept | withheld_anemi_page | 0 |
| R4-22 | `an-7792a3301892-p000059` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-24 | `an-7792a3301892-p000154` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-28 | `an-00f143ecce59-p000192` | missed_line | withheld_anemi_page | 0 |
| R4-30 | `an-e74539ae215c-p000338` | stamp_or_watermark_boxed | withheld_anemi_page | 0 |
| R4-43 | `an-ef481610a820-p000181` | missed_line | withheld_anemi_page | 0 |
| R4-45 | `s2-93f8070059f938bda524-p00001` | faint_ghost_kept | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-49 | `an-c99f1c450f55-p000025` | frame_or_ornament_boxed | withheld_anemi_page | 0 |
| R4-50 | `an-1ba3fdb1436b-p000035` | missed_line | withheld_anemi_page | 0 |
| R4-51 | `s2-0ce9d1025b3f23c7119e-p00001` | faint_ghost_kept | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-52 | `s2-3229200bf47ca465a42d-p00006` | multi_line_segment | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-55 | `s2-49598b2e848ab1f0ee1e-p00001` | missed_line | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-57 | `s2-49598b2e848ab1f0ee1e-p00004` | curl_end_cut, multi_line_segment | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-63 | `s2-3229200bf47ca465a42d-p00004` | missed_line | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-71 | `s2-86865c33eef5932c013b-p00005` | curl_end_cut | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-72 | `s2-49598b2e848ab1f0ee1e-p00005` | multi_line_segment, fragment_crop | no_unambiguous_region; two-catalogue evidence only | 0 |
| R4-73 | `s2-86865c33eef5932c013b-p00007` | curl_end_cut | no_unambiguous_region; two-catalogue evidence only | 0 |

## Visual checks of the returned-line signal

- [s2-200e977f2dab5291c42c-p00035.mark18.r7item18](docai_failed_lines_review.html#s2-200e977f2dab5291c42c-p00035.mark18.r7item18): The crop contains the printed numbers 36 and 37 in two rows. Google exposes the multi-row input with two returned lines despite high confidence. Returned text: `36 / 37`; mean symbol confidence 0.983. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-3229200bf47ca465a42d-p00004.mark0.r7item26](docai_failed_lines_review.html#s2-3229200bf47ca465a42d-p00004.mark0.r7item26): The crop shows one bent printed row. Google splits it into three layout lines (spatial fragments). This is a false alarm for interpreting returned-line count as printed-row count. Returned text: `Εἰς τοῦτο συνεφώνησε, μετά / τίνα / συζήτησιν, καὶ ὁ Πρόε`; mean symbol confidence 0.954. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-3229200bf47ca465a42d-p00004.mark18.r7item27](docai_failed_lines_review.html#s2-3229200bf47ca465a42d-p00004.mark18.r7item27): The inspected output crop is a clean neighbouring row. Its plausible single-line output is not confirmed label noise despite its multi-line mark association. Returned text: `προταχθῇ ἐν αὐτῇ τὸ νομοσχέδιον περί τροποποιήσεως τοῦ`; mean symbol confidence 0.956. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-3229200bf47ca465a42d-p00005.comment.r7item20](docai_failed_lines_review.html#s2-3229200bf47ca465a42d-p00005.comment.r7item20): Owner O02 identifies missing curled-end characters at historical #13. Google returns one plausible Greek line at high confidence without any exposure signal or a missing-content marker. The crop alone cannot establish which text lies outside its right edge; the owner observation establishes the crop-completeness defect. Returned text: `προηγουμένῃ ἀποφάσει τοῦ Ὑπουργικοῦ Συμβουλίου`; mean symbol confidence 0.955. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-3229200bf47ca465a42d-p00005.comment.r7item19](docai_failed_lines_review.html#s2-3229200bf47ca465a42d-p00005.comment.r7item19): Owner O02 identifies missing curled-end characters at #14. Google confidently transcribes the visible row ending in περὶ as one line with no exposure signal. The missing endpoint is invisible to this crop-only reader. Returned text: `ποιήσηται τὰς ἀναγκαίας ἐπιστημονικὰς μελέτας περὶ`; mean symbol confidence 0.970. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item126](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item126): Owner O11 labels #1 as faint/ghost. The visible crop is mirrored pale text; Google emits Cyrillic ТОПИАХН with low mean confidence. This instance is exposed by the calibrated confidence rule. Returned text: `ТОПИАХН`; mean symbol confidence 0.523. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item121](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item121): Owner O11 labels #89 as faint/ghost. The crop mixes pale left ink with a legible Greek phrase. Google emits 1ο Βουλευτὴς ἐκ Γόρτυνος as one line, with no exposure signal. This is a silent risk under the owner classification; the observation does not supply a gold transcript. Returned text: `1ο Βουλευτὴς ἐκ Γόρτυνος`; mean symbol confidence 0.864. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item7](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item7): Owner O11 labels #117 as faint/ghost. Google emits the short numeric text 08,8 as one line with no exposure signal. A plausible numeral is not a front-ink certificate. Returned text: `08,8`; mean symbol confidence 0.827. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item1](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item1): Owner O11 labels #126 as faint/ghost. Google emits 1003 from the pale fragment, with low mean symbol confidence; the confidence rule exposes this instance. Returned text: `1003`; mean symbol confidence 0.703. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item0](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item0): Owner O11 labels #127 as faint/ghost. Google returns empty text and zero lines. Empty output exposes this instance. Returned text: ``; mean symbol confidence —. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-93f8070059f938bda524-p00001.comment.r7item125](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item125): Owner O11 says #5 extends over faint characters. The crop has pale left ink beside Άρθρον 10. Google returns χος "Άρθρον 10 with low mean confidence; stray left content is included but this instance has an exposure signal. Returned text: `χος "Άρθρον 10`; mean symbol confidence 0.727. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-86865c33eef5932c013b-p00026.comment.r7item41](docai_failed_lines_review.html#s2-86865c33eef5932c013b-p00026.comment.r7item41): Owner O12 says #9 extends over faint words. The crop contains strongly sloped dark central text and pale trailing ink. Google returns nothing. This is exposed by empty output, which also shows that visible real text can be lost. Returned text: ``; mean symbol confidence —. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-86865c33eef5932c013b-p00026.comment.r7item36](docai_failed_lines_review.html#s2-86865c33eef5932c013b-p00026.comment.r7item36): Owner O12 says #40 extends over faint words. Google returns one garbled line from the dark central phrase plus pale endpoint ink; both mean and minimum confidence are low. This instance is exposed. Returned text: `Αχ Ελαια Ενθύϊνώς κατύο.`; mean symbol confidence 0.544. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11): Owner O04 identifies the missed word before #75. Google returns one fluent visible fragment starting ἥτις, with no exposure signal. It cannot certify or restore a first word outside the crop; line-finder-side completeness checking is required. Returned text: `ἥτις εἶναι ἓν ἐκ τῶν εὐγενεστέρων έλα-`; mean symbol confidence 0.916. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2): Owner O04 identifies the missed word before #90. This small tilted crop returns θυπουργός παρεδέ as one line, but a low minimum symbol confidence provides an exposure signal. The endpoint omission itself is still a geometry defect. Returned text: `θυπουργός παρεδέ`; mean symbol confidence 0.843. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).
- [s2-44b5cf9e0d680b361091-p00002.comment.r7item9](docai_failed_lines_review.html#s2-44b5cf9e0d680b361091-p00002.comment.r7item9): Owner O07 identifies #123 as misaligned. The crop includes a vertical rule at the left and clipped neighbouring ink along its upper edge. Google returns one confident line starting with an extra |, with no exposure signal. This observed appended rule character is absorbed silently and needs a line-finder-side geometry/ink filter. Returned text: `\|ἐκεῖνοι οἵτινες ἀπεχώρησαν τοῦ Βουλευτηρίου καὶ ἔρριψαν κατὰ`; mean symbol confidence 0.942. Each observation is hash-bound in [visual_findings.json](docai_failed_lines/visual_findings.json).

These samples calibrate the signal; the complete crop review remains available to the owner.


## Representative returned outputs

These are signal-only examples, selected deterministically from measured crop IDs. They show what Google returned, not gold-text correctness. View the linked crop against its owner observation.

| Type | Crop / Google signal | Returned lines | Mean / minimum symbol confidence |
| --- | --- | --- | --- |
| `line_start_missed` | [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2) · exposed | θυπουργός παρεδέ | 0.843 / 0.185 |
| `line_start_missed` | [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11) · silent candidate | ἥτις εἶναι ἓν ἐκ τῶν εὐγενεστέρων έλα- | 0.916 / 0.328 |
| `curl_end_cut` | [s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item19](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item19) · exposed | - ٠٠٠٠٠م, να, κοσμον ως ανύρματα εις / κρά παιδία˙ ἀλλὰ μέχρι τῆς ἐποχῆς ἐκείνης ὀφείλομεν ν / .. / V / -Ad | 0.776 / 0.250 |
| `curl_end_cut` | [s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item116](docai_failed_lines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item116) · silent candidate | διανύσωσιν εὐκοπώτερον τὸν περὶ τῆς ὑπάρξεως ἀγῶνα, | 0.962 / 0.733 |
| `multi_line_segment` | [s2-200e977f2dab5291c42c-p00035.mark18.r7item18](docai_failed_lines_review.html#s2-200e977f2dab5291c42c-p00035.mark18.r7item18) · exposed | 36 / 37 | 0.983 / 0.981 |
| `multi_line_segment` | [s2-3229200bf47ca465a42d-p00004.mark18.r7item27](docai_failed_lines_review.html#s2-3229200bf47ca465a42d-p00004.mark18.r7item27) · silent candidate | προταχθῇ ἐν αὐτῇ τὸ νομοσχέδιον περί τροποποιήσεως τοῦ | 0.956 / 0.472 |
| `misaligned_crop` | [s2-44b5cf9e0d680b361091-p00002.comment.r7item9](docai_failed_lines_review.html#s2-44b5cf9e0d680b361091-p00002.comment.r7item9) · silent candidate | \|ἐκεῖνοι οἵτινες ἀπεχώρησαν τοῦ Βουλευτηρίου καὶ ἔρριψαν κατὰ | 0.942 / 0.377 |
| `faint_ghost_kept` | [s2-93f8070059f938bda524-p00001.comment.r7item126](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item126) · exposed | ТОПИАХН | 0.523 / 0.394 |
| `faint_ghost_kept` | [s2-93f8070059f938bda524-p00001.comment.r7item121](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item121) · silent candidate | 1ο Βουλευτὴς ἐκ Γόρτυνος | 0.864 / 0.291 |
| `crop_extends_over_faint` | [s2-93f8070059f938bda524-p00001.comment.r7item125](docai_failed_lines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item125) · exposed | χος "Άρθρον 10 | 0.727 / 0.341 |

## Characters actually emitted

The [complete characters table](docai_failed_lines/characters.csv) includes every raw emitted code point and its count for ALL calls and each present source. Counts include whitespace. [characters.json](docai_failed_lines/characters.json) also stores Greek-only sets and NFD counts. Absence here is not proof that the processor cannot recognise a glyph: no glyph-level ground truth or exposure count is supplied.

### ALL — 236 unique calls

Raw emitted Greek set: `΄ΆΐΑΒΓΔΕΖΗΘΙΚΛΜΝΟΠΡΣΤΥΧάέήίαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώἀἁἂἄἅἐἑἓἔἕἘἙἠἡἢἣἤἥἦἧἩἰἱἴἵἶἷὀὁὅὉὐὑὕὖὙὠὡὤὰὲὴὶὸὺὼᾳᾶᾷ᾽᾿ῃῆῇῖῦῳῶῷ`.

| Requested character | Code point | Raw count / appeared | NFD count |
| --- | --- | ---: | ---: |
| ϗ | U+03D7 | 0 / no | 0 |
| ȣ | U+0223 | 0 / no | 0 |
| ϛ | U+03DB | 0 / no | 0 |
| ϲ | U+03F2 | 0 / no | 0 |
| Ϲ | U+03F9 | 0 / no | 0 |
| ϝ | U+03DD | 0 / no | 0 |
| ϙ | U+03D9 | 0 / no | 0 |
| ϡ | U+03E1 | 0 / no | 0 |
| ͅ | U+0345 | 0 / no | 33 |
| ʹ | U+02B9 | 0 / no | 0 |
| ͵ | U+0375 | 0 / no | 0 |

NFD combining marks attached to Greek letters:

| Mark | Code point / name | Count |
| --- | --- | ---: |
| ◌̀ | U+0300 COMBINING GRAVE ACCENT | 390 |
| ◌́ | U+0301 COMBINING ACUTE ACCENT | 705 |
| ◌̈ | U+0308 COMBINING DIAERESIS | 4 |
| ◌̓ | U+0313 COMBINING COMMA ABOVE | 363 |
| ◌̔ | U+0314 COMBINING REVERSED COMMA ABOVE | 184 |
| ◌͂ | U+0342 COMBINING GREEK PERISPOMENI | 348 |
| ◌ͅ | U+0345 COMBINING GREEK YPOGEGRAMMENI | 33 |

### Vouli — 236 unique calls

Raw emitted Greek set: `΄ΆΐΑΒΓΔΕΖΗΘΙΚΛΜΝΟΠΡΣΤΥΧάέήίαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώἀἁἂἄἅἐἑἓἔἕἘἙἠἡἢἣἤἥἦἧἩἰἱἴἵἶἷὀὁὅὉὐὑὕὖὙὠὡὤὰὲὴὶὸὺὼᾳᾶᾷ᾽᾿ῃῆῇῖῦῳῶῷ`.

| Requested character | Code point | Raw count / appeared | NFD count |
| --- | --- | ---: | ---: |
| ϗ | U+03D7 | 0 / no | 0 |
| ȣ | U+0223 | 0 / no | 0 |
| ϛ | U+03DB | 0 / no | 0 |
| ϲ | U+03F2 | 0 / no | 0 |
| Ϲ | U+03F9 | 0 / no | 0 |
| ϝ | U+03DD | 0 / no | 0 |
| ϙ | U+03D9 | 0 / no | 0 |
| ϡ | U+03E1 | 0 / no | 0 |
| ͅ | U+0345 | 0 / no | 33 |
| ʹ | U+02B9 | 0 / no | 0 |
| ͵ | U+0375 | 0 / no | 0 |

NFD combining marks attached to Greek letters:

| Mark | Code point / name | Count |
| --- | --- | ---: |
| ◌̀ | U+0300 COMBINING GRAVE ACCENT | 390 |
| ◌́ | U+0301 COMBINING ACUTE ACCENT | 705 |
| ◌̈ | U+0308 COMBINING DIAERESIS | 4 |
| ◌̓ | U+0313 COMBINING COMMA ABOVE | 363 |
| ◌̔ | U+0314 COMBINING REVERSED COMMA ABOVE | 184 |
| ◌͂ | U+0342 COMBINING GREEK PERISPOMENI | 348 |
| ◌ͅ | U+0345 COMBINING GREEK YPOGEGRAMMENI | 33 |

Internet Archive: **no current-output crop in this catalogue**, so no per-source measurement. Anemi is withheld.

## Cost receipt

**236 API calls**: 236 successful, 0 errors; 236 known successful one-page units, 0 units with unknown billing outcome. Estimated base list-price cost: **US$0.3540** at US$1.50/1,000 pages. [Google Enterprise Document OCR pricing](https://cloud.google.com/products/document-ai/pricing) checked 11 October 2026. The pricing page also shows a free allowance; this conservative list-price estimate does not assume its remaining balance, credits, discounts or taxes and is not an invoice.

[Machine-readable receipt](docai_failed_lines/receipt.json) · [Raw per-crop CSV](docai_failed_lines/crops.csv) · [Metrics](docai_failed_lines/metrics.json) · [Summary](docai_failed_lines/summary.json) · [Comment-region provenance](docai_failed_lines/page_comment_coverage.json) · [Visual review](docai_failed_lines_review.html)

## Verification and visual-review limit

59 offline tests passed. The [artifact validator](../../scripts/harvest/validate_google_failed_lines.py) recomputes every crop metric and the character table from raw responses, checks all image hashes/cards/links/CSV IDs, and confirms at most one API call per SHA. Offline regeneration added no calls. [Verification receipt](docai_failed_lines/validation.json).

The responsive CSS constrains images and long text to the available width. Actual desktop and phone viewport rendering remains unverified: the local headless browser could not launch in this sandbox, and automatic approval review rejected Firefox access because computer use was not approved for that app. Sixteen native crop/response samples were inspected visually; this is not a browser layout check.
