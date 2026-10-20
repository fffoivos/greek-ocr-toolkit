# T27e — Wikisource dual-label test collection

**Status: complete.** Selected 20 Greek + 10 Russian works, 300 + 100 pages. Fetched transcriptions: 300 Greek / 100 Russian pages, 4078 source lines. Scan pages read: 300 / 100; Google lines 14967; aligned 2030; admitted/cropped 12356.

## T27e local scan inputs

The 15 Oct 09:40 coordinator decision supplies the scan of record under `harvest_big/wikisource/thumbs/<page_id>.jpg`. No Wikimedia request was made during T27e: no image request, image API, new selection or transcription fetch. The saved API robots denials and category/index HTML fallback from T27 remain the discovery evidence. The import verified 400 JPEG byte counts and SHA-256 hashes against the supplied [receipts](../../../harvest/harvest_big/wikisource/thumbs/receipts.jsonl), and checked each URL against its selected scan file and scan-page number. Unavailable receipts: 0; requested widths: `{"3840": 400}`. [Unavailable pages](unavailable_pages.json) lists only coordinator receipts marked failed. Each JPEG was converted to greyscale and downscaled without upsampling so its long side is at most 3500 px. The original dimensions, delivered dimensions and exact horizontal/vertical scale are recorded in [manifest.json](manifest.json). PNG 200-dpi metadata is nominal; these thumbnails do not establish physical scan dpi. The frozen gate flagged 29 pages; all obtained pages, including flagged ones, were read. Historical failed HTTP attempts remain unchanged as evidence from earlier attempts.

Gate flags (overlapping): `{"non_body_page": 9, "bad_ink_fraction": 4, "faint_or_show_through_dominated": 3, "table": 15, "faint_components": 1}`. Geometry extraction errors: 0.

## Labels and alignment

The scan licence field carries the recorded Commons PD statement; contributor transcription text has a separate CC-BY-SA-4.0 attribution field. NFC and whitespace normalization preserve historical spelling and accents. Known formatting wrappers are removed; unknown templates carry a visible sentinel and cannot supply gold. The 90 Russian `ВАР`/`ВАР2` wrappers select the first, historical spelling branch, verified against the supplied scans (Balmont scan page 86 and Satirikon scan page 16). Poem-only `№` line counters absent from the print are removed; indentation/spacing templates supply no text. All 400 original saved transcriptions and raw wikitext remain byte-identical; [cleaned_transcriptions/](cleaned_transcriptions/) contains separately derived text and the variant decisions. Cross-page hyphenation templates retain the printed fragment and starting-page hyphen; decisions are logged. Literal end-of-line hyphens remain. Source paragraph breaks and poem rows are retained; prose paragraphs are never reflowed into Google rows. Consequently much prose may be unalignable.

Global monotone sequence alignment uses character Levenshtein similarity (minimum 0.65), skipped-line cost 0.45 and split/merge penalty 0.25. Only 1:1 blocks receive human_label and CER; split/merged and unmatched blocks remain unaligned. CER is total NFC character edits / human characters across aligned lines before admission. It is conditional on alignability and similarity, not an unbiased estimate over all print or all Google lines. Mark classes below are full-line CER cohorts containing that NFD mark in the human label; classes overlap. No-mark cohorts and absent languages have undefined CER.

| Language / mark cohort | Google lines | Aligned | Aligned share | Human chars | Edits | CER |
|---|---:|---:|---|---:|---:|---|
| el | 11175 | 1737 | 15.54% | 49219 | 2425 | 4.93% |
| el / breathings | 1293 | 1293 | 100.00% | 40628 | 2078 | 5.11% |
| el / iota_subscript | 197 | 197 | 100.00% | 6658 | 388 | 5.83% |
| el / perispomeni | 803 | 803 | 100.00% | 26172 | 1272 | 4.86% |
| el / grave | 1054 | 1054 | 100.00% | 33237 | 1558 | 4.69% |
| el / dialytika | 14 | 14 | 100.00% | 427 | 39 | 9.13% |
| ru | 3792 | 293 | 7.73% | 9503 | 188 | 1.98% |
| ru / breathings | 0 | 0 | not measured | 0 | 0 | not measured |
| ru / iota_subscript | 0 | 0 | not measured | 0 | 0 | not measured |
| ru / perispomeni | 0 | 0 | not measured | 0 | 0 | not measured |
| ru / grave | 0 | 0 | not measured | 0 | 0 | not measured |
| ru / dialytika | 0 | 0 | not measured | 0 | 0 | not measured |

### Per-work coverage

| Lang | Work | Pages | Google lines | Aligned | Aligned share | CER | Admitted |
|---|---|---:|---:|---:|---:|---:|---:|
| el | Διήγησις ακριβής όπως εβαπτίσθη το των Ρώσσων Έθνος | 15 | 369 | 12 | 3.25% | 0.82% | 294 |
| el | Διηγήματα | 15 | 510 | 19 | 3.73% | 5.09% | 418 |
| el | Διονύσου πλους | 15 | 461 | 264 | 57.27% | 6.41% | 306 |
| el | Ελεγεία και Σάτιρες | 15 | 223 | 157 | 70.40% | 1.79% | 169 |
| el | Η Α. Θ. Παναγιότης ο Άνθιμος ο Ζ. εν Καλύμνω | 15 | 466 | 3 | 0.64% | 3.81% | 430 |
| el | Η εθνική ημών μουσική | 15 | 440 | 6 | 1.36% | 2.06% | 408 |
| el | Λόγια της πλώρης | 15 | 495 | 9 | 1.82% | 7.45% | 409 |
| el | Ο Κόδρος | 15 | 259 | 178 | 68.73% | 2.06% | 203 |
| el | Περί νομίσματος και της κτητικής δυνάμεως των πολύτιμων μετάλλων κατά τους βυζαντινούς χρόνους | 15 | 609 | 24 | 3.94% | 2.27% | 493 |
| el | Περί του Ανατολικού ζητήματος | 15 | 466 | 9 | 1.93% | 6.16% | 416 |
| el | Σύνταγμα της Κρητικής Πολιτείας | 15 | 455 | 70 | 15.38% | 8.81% | 345 |
| el | Argonautica | 15 | 616 | 384 | 62.34% | 5.21% | 470 |
| el | Ἀτθίδες Αὖραι | 15 | 397 | 247 | 62.22% | 6.94% | 245 |
| el | Fables | 15 | 452 | 76 | 16.81% | 2.70% | 368 |
| el | Αριστοτέλης Βαλαωρίτης | 15 | 435 | 20 | 4.60% | 3.35% | 360 |
| el | Ἀστέρια | 15 | 288 | 159 | 55.21% | 3.27% | 173 |
| el | Αττικά ή περί δήμων Αττικής εν οις και περί τινων μερών του Άστεως | 15 | 466 | 15 | 3.22% | 6.15% | 361 |
| el | Βίοι Πελοποννησίων ανδρών | 15 | 413 | 15 | 3.63% | 1.85% | 380 |
| el | Εστία Αριθμός 658 | 15 | 1685 | 19 | 1.13% | 11.62% | 1480 |
| el | Εστία Αριθμός 659 | 15 | 1670 | 51 | 3.05% | 11.14% | 1502 |
| ru | Анна Каренина , том I | 10 | 397 | 4 | 1.01% | 7.59% | 333 |
| ru | Синее с золотом | 10 | 415 | 28 | 6.75% | 6.39% | 276 |
| ru | Полное собраніе стиховъ. Томъ четвертый. Только Любовь , том 04 | 10 | 240 | 218 | 90.83% | 1.23% | 221 |
| ru | Список трудов | 10 | 327 | 6 | 1.83% | 5.43% | 192 |
| ru | Ледяной плен | 10 | 275 | 2 | 0.73% | 0.00% | 261 |
| ru | Война; Аринушка; На передовых позициях; Вблизи Перемышля | 10 | 694 | 26 | 3.75% | 4.64% | 604 |
| ru | Новые словечки и старые слова | 10 | 278 | 2 | 0.72% | 0.00% | 254 |
| ru | Биографический очерк ребёнка | 10 | 400 | 2 | 0.50% | 0.00% | 349 |
| ru | О происхождении видов | 10 | 428 | 0 | 0.00% | not measured | 398 |
| ru | Дешевая юмористическая библіотека Новаго Сатирикона, Выпускъ 2-3 | 10 | 338 | 5 | 1.48% | 0.83% | 238 |

## Admission and train contamination

Frozen T20 admission remains byte-identical. The pipeline reads and visibly flags frozen page gate failures; post-read bad_page uses the standard T20 rule. No T27 row can have split=train or train_pool_eligible=true. All source works are held out, including unaligned and rejected labels.

Admission uses only the Google reading. An admitted unaligned crop retains `human_label=null`; it is not independent human gold. For human-reference evaluation, filter `alignment=aligned`. The full set remains test/dev only.

Aligned admitted crops: 1717; neighbour-trimmed crops: 2283.

| Class | Dev | Test |
|---|---:|---:|
| greek_poly | 866 | 7920 |
| greek_mono | 49 | 194 |
| greek_latin_cs | 9 | 103 |
| latin | 2 | 95 |
| cyrillic | 192 | 2926 |

Rejection reasons: short_line: 1972, low_confidence: 1307, tall_box: 172, symbol_heavy: 1449, mixed_word: 23, foreign_script: 28, bad_page: 2.

The O5 audit scanned 74 JSONL/JSON files, including 18 populated train pools/admitted inventories. This includes the T28 collection JSONL exports and `manifest_train.json`, whose training split is implicit in its filename. It reserved 16693 distinct labels from the available human transcriptions and Google readings. Collisions: 259 file occurrences / 29 distinct source+line IDs. Every collision is listed for removal in [prior_train_exclusions.jsonl](prior_train_exclusions.jsonl); [label_in_holdout.json](label_in_holdout.json) binds every scanned file. Prior snapshots were read only. No trainer should consume a listed collision.

| Train file | Train rows | Collisions |
|---|---:|---:|
| docs/records/harvest/collection/admitted_all.jsonl | 228464 | 19 |
| docs/records/harvest/collection/import_real_all.jsonl | 228464 | 19 |
| docs/records/harvest/collection/import_real_train.jsonl | 228464 | 19 |
| docs/records/harvest/collection/rejected_global.jsonl | 22 | 10 |
| docs/records/harvest/cyrillic/admitted.jsonl | 12786 | 0 |
| docs/records/harvest/cyrillic/train_pool.jsonl | 201794 | 26 |
| docs/records/harvest/mixed/admitted.jsonl | 19313 | 1 |
| docs/records/harvest/mixed/train_pool.jsonl | 189008 | 26 |
| docs/records/harvest/openarchives/admitted.jsonl | 19797 | 2 |
| docs/records/harvest/openarchives/train_pool.jsonl | 221589 | 28 |
| docs/records/harvest/parliament/admitted.jsonl | 67527 | 0 |
| docs/records/harvest/parliament/train_pool.jsonl | 169696 | 25 |
| docs/records/harvest/round1/admitted.jsonl | 49951 | 12 |
| docs/records/harvest/round2/admitted.jsonl | 19693 | 13 |
| docs/records/harvest/round2/train_pool.jsonl | 102176 | 26 |
| docs/records/harvest/vouli/admitted.jsonl | 32535 | 1 |
| docs/records/harvest/vouli/train_pool.jsonl | 82484 | 13 |
| docs/records/harvest/collection/manifest_train.json | 228464 | 19 |

| Colliding line ID | Label |
|---|---|
| 0bff55647d1c2acd1caa8bf3-p000057-l0040 | ΑΝΕΠΙΣΤΗΜΙΟ |
| 8b206cd5e2c3714cf6bdff88-p000010-l0036 | ΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 53e3db8de066783d632e29c5-p000157-l0001 | ΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 53e3db8de066783d632e29c5-p000200-l0002 | ΚΕΦΑΛΑΙΟΝ Β΄. |
| 453f156dc6352286456a08cb-p000073-l0004 | ΚΕΦΑΛΑΙΟΝ ΣΤ΄. |
| f22ded41f8be8f26ddeb3bb2-p000070-l0001 | ΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| cc5059bc91ca2b178c20008c-p000005-l0024 | ΠΑΝΕΠΙΣΤΗΜΙΟΝ ΚΡΗΤΗΣ |
| 8b231047fdbd96ec30e1eded-p000038-l0024 | Βιβλιοθήκη Πανεπ. Κρήτης |
| 8c926ffa3b1b2be056e56b7e-p000054-l0003 | ΚΕΦΑΛΑΙΟΝ ΣΤ΄. |
| b884229506d8010671cc515f-p000066-l0003 | ΚΕΦΑΛΑΙΟΝ Β΄. |
| b884229506d8010671cc515f-p000086-l0002 | ΚΕΦΑΛΑΙΟΝ Β΄. |
| b884229506d8010671cc515f-p000166-l0002 | ΚΕΦΑΛΑΙΟΝ Ε΄. |
| b884229506d8010671cc515f-p000188-l0002 | ΚΕΦΑΛΑΙΟΝ ΣΤ΄. |
| dc390fceb64d9bb60a12d6b8-p000060-l0007 | ΚΕΦΑΛΑΙΟΝ Ε΄. |
| 7056dabdb0d8a5db4a0976f8-p000082-l0058 | ΚΕΦΑΛΑΙΟΝ Ε΄. |
| 6d957fa757c72e1408f65dde-p000253-l0026 | Μ. Ρ. ΚΟΥΝΔΟΥΡΟΣ |
| 6d957fa757c72e1408f65dde-p000338-l0020 | Μ. Ρ. ΚΟΥΝΔΟΥΡΟΣ |
| 66844409-p000070-l0007 | νομισμάτων. |
| a38045f531c81af524934fb8-p000020-l0036 | ΚΕΦΑΛΑΙΟΝ Ε΄. |
| 1495fc2311427a558abbfd88-p000023-l0056 | Κόραξ καὶ ἀλώπηξ. |
| 1495fc2311427a558abbfd88-p000040-l0028 | ΣΗΜΕΙΩΣΕΙΣ |
| 0907df739607faca673d2169-p000005-l0001 | ΠΙΝΑΞ ΠΕΡΙΕΧΟΜΕΝΩΝ |
| 5be5bc5b3ea6-p000013-l0030 | Περὶ συντάξεως τῆς Πολιτείας. |
| 5a69150abb15eb1006f5a3ba-p000586-l0003 | ΣΗΜΕΙΩΣΕΙΣ |
| a300f5e1c3f6a38d97201791-p000152-l0060 | ΠΕΡΙΕΧΟΜΕΝΑ |
| a300f5e1c3f6a38d97201791-p000201-l0021 | ΠΕΡΙΕΧΟΜΕΝΑ |
| a300f5e1c3f6a38d97201791-p000247-l0094 | ΠΕΡΙΕΧΟΜΕΝΑ |
| a300f5e1c3f6a38d97201791-p000633-l0011 | ΠΕΡΙΕΧΟΜΕΝΑ |
| 08a508c2-p000084-l0018 | ΠΕΡΙΕΧΟΜΕΝΑ |

This audit covers all resolved human source lines and every obtained Google label, including rejected and unaligned lines.

## Cost, validation and limitations

USD 0.6000 reserved; cap USD 0.80; 400 Document AI attempts; zero Vision calls. 227 offline tests passed, including unchanged T20 admission, Greek/Russian wikitext fixtures and split/merge alignment fixtures. The Google path reuses T21 at-most-once image-SHA reservations, native bbox inversion and symbol confidence, with automatic language detection and no implicit provider retries.

Page PNGs are grey, at most 3500 px on the long side, never upsampled, with nominal 200-dpi delivery metadata; physical source dpi must not be inferred from that metadata. Any 1920/1280 px fallback is recorded explicitly and falls below the original 2000 px target under the coordinator exception. Embedded `document.pages[*].image.content` is removed before raw responses are saved. Compiled scan / Google / human triptychs are under `harvest_big/wikisource/compiled/<lang>/<year>_<title40>/pNNNN.jpg`; unaligned human panels are marked explicitly. Native greyscale crops retain original-resolution pixels from the delivered PNG. Template encounter counts include discarded modern variant arguments; only unresolved sentinels surviving in the selected text prevent alignment. Unresolved template counts: `{"simpleleader block/s": 3, "simpleleader": 76, "simpleleader block/e": 3, "εικόνα": 5, "largeinitial": 3, "3*d": 10, "---": 11, "акут": 7, "гравис": 4, "3*": 2, "эпиграф": 2, "опечатка": 4, "αστεράκι": 5, "roman": 131, "ё": 304, "градус": 2, "нп": 3, "якорь": 2, "σλβτ": 2, "namespacenumber": 1, "#ifeq:⟦unresolved template⟧": 1, "poemx1": 2, "ы": 2, "angbr": 7, "=": 10, "float right": 1, "во": 2, "мби": 12, "right2": 2, "разделитель": 4, "χρώμα": 1}`. Hyphenation events retained: 189. All HTTP response bodies, robots files and raw source wikitext are frozen under harvest_big/wikisource.

[Validation](validation.json) checks all 400 raw text hashes, held-out work assignment, prior train file hashes and Git metadata. The 586 timestamped crawler requests have minimum recorded spacing 1.050047 s; 8 initial bootstrap receipts have no request-start timestamp. Workflow completion: `true`. Validation checked 400 local JPEGs, 400 grey page images, 12356 native crop rasters and 400 compiled image hashes. T27e Wikimedia requests: 0; transcription refetches: 0.

[Git metadata audit](git_metadata_audit.json): all snapshotted Git metadata is unchanged during T27e.

## Visual spot checks

[Visual QA](visual_qa.json) records four native crop views and three compiled triptychs, including a visible Greek Π/Γ substitution and Russian ъ/ь confusion. [Variant branch audit](variant_branch_audit.json) records the two original-scan checks and all 90 branch diagnostics. These are sample checks; exhaustive crop-pixel equality verifies extraction provenance, not universal physical-row or transcription correctness.

T27e: done | works: 20/10 | pages: 300/100 | lines: 14967 | aligned: 2030 | admitted: 12356 | cer_el: 4.93% | cer_ru: 1.98% | usd: 0.60 | tests: 227 passed
