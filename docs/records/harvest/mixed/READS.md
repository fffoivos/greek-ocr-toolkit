# T25 — Wave 5 mixed and Latin reads

**81 sources; 1396 rendered / 782 gate-accepted / 782 Document AI-read pages; 46,515 lines; 33,114 admitted native crops.** USD 1.1730 reserved at the T19 list-price estimate, cap USD 2.00; zero Vision calls. 248 offline tests passed.

| Part | Sources selected | Sources with rendered pages | Sources read | Rendered | Accepted/read | DocAI lines | Admitted |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 40 | 40 | 39 | 582 | 444 | 23030 | 18486 |
| B | 40 | 40 | 36 | 602 | 268 | 9950 | 4840 |
| C | 1 | 1 | 1 | 212 | 70 | 13535 | 9788 |

A = Anemi dictionaries/grammars/journals; B = repository bibliography/middle pages; C = Internet Archive lexicon. Recorded rights for each B source are retained in books.json; repository licences are unverified. OCR routing metadata identifies candidates; it is not proof that every sampled page is a scan.

| Gate / photometric flag (overlapping counts) | A | B | C |
|---|---:|---:|---:|
| bad_darkest_percentile_contrast | 0 | 2 | 0 |
| bad_faintness_proxy | 0 | 2 | 0 |
| bad_ink_fraction | 7 | 2 | 2 |
| bend_scout | 40 | 6 | 10 |
| faint_components | 31 | 0 | 0 |
| faint_or_show_through_dominated | 0 | 13 | 0 |
| more_than_two_columns | 38 | 31 | 136 |
| non_body_page | 9 | 110 | 0 |
| rotated | 2 | 49 | 0 |
| table | 30 | 251 | 0 |

| Class | Train | Dev | Test | Total |
|---|---:|---:|---:|---:|
| greek_poly | 13741 | 270 | 2265 | 16276 |
| greek_mono | 2081 | 164 | 288 | 2533 |
| greek_latin_cs | 1007 | 229 | 2743 | 3979 |
| latin | 2484 | 475 | 7367 | 10326 |
| cyrillic | 0 | 0 | 0 | 0 |

| Part | Class | Train | Dev | Test |
|---|---|---:|---:|---:|
| A | greek_poly | 13679 | 270 | 2166 |
| A | greek_mono | 493 | 13 | 70 |
| A | greek_latin_cs | 507 | 215 | 30 |
| A | latin | 600 | 433 | 10 |
| A | cyrillic | 0 | 0 | 0 |
| B | greek_poly | 62 | 0 | 0 |
| B | greek_mono | 1588 | 151 | 159 |
| B | greek_latin_cs | 500 | 14 | 86 |
| B | latin | 1884 | 42 | 354 |
| B | cyrillic | 0 | 0 | 0 |
| C | greek_poly | 0 | 0 | 99 |
| C | greek_mono | 0 | 0 | 59 |
| C | greek_latin_cs | 0 | 0 | 2627 |
| C | latin | 0 | 0 | 7003 |
| C | cyrillic | 0 | 0 | 0 |

Greek-majority lines containing a whole Latin word of at least two letters are greek_latin_cs; Latin-majority lines are latin. Classification and every admission rule use the unchanged T20 module. Labels are normalized as T20, with spacing marks flagged rather than silently corrected.

Mixed-line share per page: Greek-majority plus a whole Latin word >=2 letters. Detected: all >=10-letter DocAI lines before confidence/quality/O5. Admitted: cs / all admitted lines on that page. Empty denominators excluded from distributions and counted separately.

| Part | Stage | Pages with denominator | Min | P10 | P25 | Median | P75 | P90 | Max | Mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | detected | 444 | 0.0% | 0.0% | 0.0% | 0.0% | 3.1% | 13.7% | 66.7% | 4.4% |
| A | admitted | 439 | 0.0% | 0.0% | 0.0% | 0.0% | 2.8% | 12.5% | 68.3% | 4.0% |
| B | detected | 268 | 0.0% | 0.0% | 0.0% | 4.4% | 21.1% | 37.8% | 77.8% | 12.8% |
| B | admitted | 221 | 0.0% | 0.0% | 0.0% | 2.3% | 25.0% | 40.0% | 84.6% | 13.2% |
| C | detected | 70 | 14.0% | 20.4% | 24.1% | 27.5% | 31.0% | 34.6% | 45.1% | 27.6% |
| C | admitted | 70 | 13.4% | 20.0% | 22.7% | 26.5% | 30.6% | 34.3% | 40.5% | 26.9% |

Empty admitted denominators: A: 5, B: 47, C: 0.

| Rejection reason (overlapping counts) | Lines |
|---|---:|
| short_line | 6927 |
| low_confidence | 4212 |
| tall_box | 617 |
| symbol_heavy | 6938 |
| foreign_script | 499 |
| mixed_word | 1091 |
| bad_page | 1945 |
| label_in_holdout | 15 |
| crop_geometry | 1 |

50 bad pages; 1 invalid crop geometries; 14850 crops trimmed at neighbour overlaps. Lost coordinate-frame pages: 0; empty responses: 0; responses without line layouts: 0.

Hold-out: A 6 sources (4 test / 2 dev), B 6 (5 test / 1 dev); C's only source is entirely test. Total 10 test / 3 dev, the nearest integer 3:1 allocation for 13 sources. All existing hold-out labels participate in O5. 15 new train lines dropped; 11 prior train lines excluded in the combined overlay. Use train_pool.jsonl for the combined training pool; earlier waves remain frozen. No normalized equal labels remain between that pool and any hold-out. Vouli contributes 21.89% of combined polytonic train lines (cap 40%).

Target 980 accepted pages; actual shortfall 198 after bounded neighbour replacements. Repository documents tried 88, downloaded/rendered 40, failed 48. No more than five selected documents per repository. Repository and IA PDFs were deleted after rendering; SHA-256, size, page count and download receipts remain.

Anemi unavailable volumes: 0. Volume failures and skipped candidates are distinguished from individual page requests in [anemi_unavailable_volumes.json](anemi_unavailable_volumes.json) and [slots.json](slots.json). A viewer stall recovered with a fresh authenticated client; [recovery evidence](anemi_recoveries.json) retains the observations without assuming a cause.

Native review confirmed two cross-column provider-line merges; 70 wide bboxes are flagged for review in [column_width_review.jsonl](column_width_review.jsonl). The heuristic flags do not change admission. See [visual QA](visual_qa.json) for source-linked examples and review limits.

All crop pixels and all compiled rasters were replay-validated. Those checks establish artifact fidelity, not transcription accuracy or perfect glyph ownership. At-most-once cached replay made zero new provider calls. T25 invoked no Git writes. The [Git audit](git_audit.json) records 2 external T24/T24b commits during this run; frozen data inputs still match.

[Selection](SELECTION.md), [admission summary](admission_summary.json), [hold-outs](holdout_books.json), [mixed shares](mixed_share.json), [validation](validation.json), [tests](tests.xml), [cost](cost_receipt.json), [inventory](inventory.json).

T25: done | sources: 40/40/1 | pages: 1396/782/782 | lines: 46515 | admitted: 33114 | cs: 3979 | latin: 10326 | poly: 16276 | mono: 2533 | usd: 1.17 | tests: 248 passed
