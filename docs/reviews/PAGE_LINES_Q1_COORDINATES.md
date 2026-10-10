# Q1: line coordinates and grouping

Structure is added over the frozen delivery geometry. Component row provenance is retained before table splitting; physical leaf, column, block, row, piece order and reading order are explicit. `join_pieces` rejects mixed addresses and any boundary intersection. Default delivery keeps table pieces and ordinary whole lines; `granularity="rows"` explicitly requests safe joined table lines.

**The no-crossing gate fails. This is not a completed Q1 acceptance.** Existing records are preserved, including diagnostic candidates and their intersections. No geometry fixes were applied; the before/after geometry change list is empty.

## Evidence and contract

- Baseline: `.astra/q1-baseline/` (162 line, cell and check files captured before edits). Each structure records the image and baseline SHA-256 hashes.
- All 54 page outputs are in `.astra/out/`: updated `.lines.json` and `.cells.json`, new `.structure.json`, `.structure.jpg`, and `.rows.json`. Unsafe rows are explicitly listed under `blocked_rows`, so the joined view cannot silently emit a crossing or claim completeness.
- Full per-record failures and annotation comparisons: [PAGE_LINES_Q1_COORDINATES.json](PAGE_LINES_Q1_COORDINATES.json), also written to `.astra/out/q1-structure-audit.json`.
- IDs are image-local. `lines.neighbours` uses line indices; `cells.neighbours` uses cell indices. Null means the end of the row. Discounted candidates receive addresses but are never rendered or joined.
- Each column references finite observed boundary paths; slanted rules retain their slopes. Overlapping observations are linked as separator tracks without replacing their measured paths. A block is a column-local prose/table/diagnostic group, not a semantic paragraph. These are conservative local column regions; complex tables remain fragmented. Reading-order indices traverse those inferred regions column by column, but human table reading order is not certified.
- Fold inference uses a wide image and a persistent central text separation. It is labelled inferred, not a scan-metadata fact. Callers can supply an explicit fold path or `fold=False`. Portrait spreads or unusual landscape single pages require that override.
- The crossing audit samples the **complete curved ribbon** against finite boundary centre paths; it also checks each delivered rectangle. The older detector check sampled three body offsets. Consequently these are conservative geometry/boundary conflicts, not all proven cut letters. New table rule paths are derived from the detector rule mask; provisional whitespace may also be wrong.
- The join guard splits proposed row groups before joining if their intervening gap crosses a stop. Original per-piece curve samples remain exact; only previously undefined gap samples are interpolated.
- Table word-splitting gaps are not automatically column boundaries. Whitespace needs persistent overlapping support windows, spanning text interrupts its extent, and rule proposals need continuous original ink. Separate component seeds may share a printed row when their facing baselines align inside one column; every source group remains in `row_sources`.

## Gates

| Gate | Result |
|---|---|
| complete_addresses | PASS |
| no_crossing | FAIL |
| geometry_unchanged | PASS |
| ordinary_exact | FAIL |
| executed_tests_pass | PASS |

10802 line records; 8546 delivered pieces; 5973 active rows; 1063 rows contain multiple pieces. Ordinary frozen whole-line geometry is unchanged for 3202/3202 rows; 3185/3202 can also be safely emitted by the join guard.

## Per-page results

Cross columns count active line ribbons, delivered boxes, and discounted diagnostic ribbons respectively. Every zero in the address/geometry columns is an exact record comparison, not a visual estimate.

| Page | Lines | Pieces | Leaves | Columns | Active rows | Multi-piece | Address errors | Geometry changes | Ordinary safely joined / total | Cross line/box/diagnostic | Blocked joins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| an-1436ae03653f-p000163 | 38 | 37 | 1 | 5 | 37 | 0 | 0 | 0 | 37/37 | 0/0/0 | 0 |
| an-1be60011c435-p000215 | 56 | 55 | 1 | 6 | 55 | 0 | 0 | 0 | 55/55 | 0/0/0 | 0 |
| an-1c6e1c0e929e-p000167 | 29 | 29 | 1 | 1 | 29 | 0 | 0 | 0 | 29/29 | 0/0/0 | 0 |
| an-1f8e7d022643-p000003 | 21 | 18 | 1 | 2 | 18 | 0 | 0 | 0 | 17/18 | 1/1/0 | 1 |
| an-2cfe28da5103-p000135 | 91 | 90 | 1 | 4 | 90 | 0 | 0 | 0 | 89/90 | 1/2/0 | 1 |
| an-3352d912f2e9-p000104 | 38 | 26 | 1 | 6 | 26 | 0 | 0 | 0 | 26/26 | 0/0/0 | 0 |
| an-466cffad2cba-p000323 | 25 | 25 | 1 | 1 | 25 | 0 | 0 | 0 | 25/25 | 0/0/0 | 0 |
| an-5c093c79d6bb-p000199 | 79 | 76 | 2 | 11 | 76 | 0 | 0 | 0 | 76/76 | 0/0/0 | 0 |
| an-778126cc8c2b-p000010 | 41 | 37 | 1 | 2 | 37 | 0 | 0 | 0 | 37/37 | 0/0/0 | 0 |
| an-7a2b17a3fb0f-p000200 | 1623 | 1262 | 2 | 111 | 688 | 281 | 0 | 0 | 3/3 | 31/26/3 | 31 |
| an-9ea1564fcf4f-p000013 | 89 | 84 | 2 | 6 | 84 | 0 | 0 | 0 | 84/84 | 0/2/0 | 0 |
| an-a3c2bdf81256-p000112 | 390 | 319 | 1 | 16 | 152 | 82 | 0 | 0 | 8/8 | 0/0/21 | 0 |
| an-a73d22211479-p000301 | 91 | 90 | 1 | 2 | 90 | 0 | 0 | 0 | 90/90 | 0/0/0 | 0 |
| an-b1a643813945-p000054 | 32 | 31 | 1 | 1 | 31 | 0 | 0 | 0 | 31/31 | 0/0/0 | 0 |
| an-c153f2c605b3-p000040 | 34 | 31 | 1 | 3 | 31 | 0 | 0 | 0 | 30/31 | 1/1/0 | 1 |
| an-c2c2053cfc10-p000056 | 75 | 75 | 2 | 7 | 75 | 0 | 0 | 0 | 75/75 | 0/0/0 | 0 |
| an-c8b96a901917-p000068 | 139 | 136 | 2 | 12 | 136 | 0 | 0 | 0 | 135/136 | 1/1/0 | 1 |
| an-d3237d690aa0-p000138 | 1402 | 1086 | 2 | 29 | 413 | 287 | 0 | 0 | 0/0 | 0/0/2 | 0 |
| an-d6002cf45e4d-p000058 | 10 | 6 | 1 | 2 | 6 | 0 | 0 | 0 | 6/6 | 0/0/0 | 0 |
| an-d6fd2cf2f618-p000047 | 37 | 35 | 1 | 1 | 35 | 0 | 0 | 0 | 35/35 | 0/0/0 | 0 |
| an-d83e7a198ade-p000099 | 84 | 83 | 2 | 12 | 83 | 0 | 0 | 0 | 76/83 | 7/7/0 | 7 |
| an-e46611ae2fcc-p000041 | 67 | 63 | 2 | 5 | 63 | 0 | 0 | 0 | 63/63 | 0/0/0 | 0 |
| an-e74539ae215c-p000338 | 95 | 94 | 1 | 2 | 94 | 0 | 0 | 0 | 94/94 | 0/0/0 | 0 |
| an-ef481610a820-p000181 | 41 | 34 | 1 | 3 | 34 | 0 | 0 | 0 | 34/34 | 0/0/0 | 0 |
| an-fabf591ca801-p000067 | 88 | 83 | 2 | 6 | 83 | 0 | 0 | 0 | 83/83 | 0/0/0 | 0 |
| an-fd4fa0018ae1-p000037 | 33 | 33 | 1 | 1 | 33 | 0 | 0 | 0 | 33/33 | 0/0/0 | 0 |
| an-ffccc97c07de-p000152 | 45 | 36 | 1 | 3 | 36 | 0 | 0 | 0 | 36/36 | 0/0/0 | 0 |
| s2-0683f98f964a6d41cb72-p00003 | 49 | 39 | 1 | 4 | 39 | 0 | 0 | 0 | 39/39 | 0/0/0 | 0 |
| s2-09f5dfca4af4d74173c6-p00005 | 69 | 60 | 1 | 4 | 60 | 0 | 0 | 0 | 59/60 | 1/1/0 | 1 |
| s2-0ce9d1025b3f23c7119e-p00001 | 65 | 35 | 1 | 2 | 35 | 0 | 0 | 0 | 35/35 | 0/0/2 | 0 |
| s2-200e977f2dab5291c42c-p00035 | 715 | 398 | 1 | 57 | 303 | 63 | 0 | 0 | 15/15 | 20/12/17 | 20 |
| s2-23a70964fda83cb7aeb1-p00003 | 134 | 125 | 1 | 3 | 125 | 0 | 0 | 0 | 125/125 | 0/0/0 | 0 |
| s2-3229200bf47ca465a42d-p00004 | 38 | 38 | 1 | 1 | 38 | 0 | 0 | 0 | 38/38 | 0/0/0 | 0 |
| s2-49598b2e848ab1f0ee1e-p00001 | 130 | 118 | 1 | 3 | 118 | 0 | 0 | 0 | 118/118 | 0/0/0 | 0 |
| s2-5ca02b142a2a3eaf078a-p00002 | 45 | 41 | 1 | 2 | 41 | 0 | 0 | 0 | 41/41 | 0/0/0 | 0 |
| s2-60f24a3d8a2d714767f2-p00003 | 129 | 129 | 1 | 4 | 129 | 0 | 0 | 0 | 128/129 | 1/1/0 | 1 |
| s2-63f072d79585d71224b6-p00002 | 51 | 45 | 1 | 4 | 45 | 0 | 0 | 0 | 45/45 | 0/0/0 | 0 |
| s2-6419488b7f8e69fd20da-p00001 | 1827 | 1460 | 1 | 145 | 713 | 185 | 0 | 0 | 95/95 | 16/15/9 | 16 |
| s2-658e6dcb48b540357a9d-p00001 | 83 | 35 | 1 | 3 | 35 | 0 | 0 | 0 | 34/35 | 1/1/0 | 1 |
| s2-661ddf05c8865e7b2c45-p00009 | 200 | 126 | 1 | 9 | 126 | 0 | 0 | 0 | 126/126 | 0/0/0 | 0 |
| s2-6f552c96213b4c24a071-p00003 | 42 | 38 | 1 | 2 | 38 | 0 | 0 | 0 | 37/38 | 1/1/0 | 1 |
| s2-7247ee9b1bc2374b3980-p00001 | 134 | 111 | 1 | 5 | 111 | 0 | 0 | 0 | 109/111 | 2/2/1 | 2 |
| s2-74cdb23a34ca4a6cd01e-p00002 | 144 | 130 | 1 | 3 | 130 | 0 | 0 | 0 | 130/130 | 0/0/0 | 0 |
| s2-77d1bd63d5babbe0df73-p00001 | 39 | 39 | 1 | 1 | 39 | 0 | 0 | 0 | 39/39 | 0/0/0 | 0 |
| s2-80513ae109b4f749ca58-p00003 | 467 | 378 | 1 | 12 | 167 | 82 | 0 | 0 | 20/20 | 0/0/11 | 0 |
| s2-831443dc5e6f1ccfbaf5-p00020 | 970 | 594 | 1 | 74 | 488 | 83 | 0 | 0 | 12/12 | 19/13/1 | 19 |
| s2-86865c33eef5932c013b-p00005 | 42 | 40 | 1 | 1 | 40 | 0 | 0 | 0 | 40/40 | 0/0/0 | 0 |
| s2-93f8070059f938bda524-p00001 | 129 | 117 | 1 | 2 | 117 | 0 | 0 | 0 | 117/117 | 0/0/0 | 0 |
| s2-9de6cda8f03f0fc60a58-p00005 | 123 | 123 | 1 | 4 | 123 | 0 | 0 | 0 | 123/123 | 0/1/0 | 0 |
| s2-be269b8c315b16befc35-p00002 | 44 | 43 | 1 | 4 | 43 | 0 | 0 | 0 | 43/43 | 0/0/0 | 0 |
| s2-d1ed1c2db37f431f4acb-p00001 | 124 | 116 | 1 | 2 | 116 | 0 | 0 | 0 | 116/116 | 0/0/0 | 0 |
| s2-dee99fdf5214acdc6f25-p00005 | 41 | 41 | 1 | 1 | 41 | 0 | 0 | 0 | 41/41 | 0/0/0 | 0 |
| s2-dfcc21869afc140111ce-p00001 | 119 | 115 | 1 | 2 | 115 | 0 | 0 | 0 | 115/115 | 0/0/0 | 0 |
| s2-f9ec82212abc808325d7-p00010 | 56 | 38 | 1 | 3 | 38 | 0 | 0 | 0 | 38/38 | 0/0/0 | 0 |

## Eight provisional table annotation checks

The available `text_elements` within annotated cells are used as printed-line proxies. Semantic table row numbers can cover several printed lines and independent panels; they are not copied into production row IDs. Missing elements and ambiguous overlaps include existing detector/annotation limitations. An annotation match is a diagnostic comparison, not certified table ownership.

| Page | Elements | Matched | Missing | Split over row IDs | Rows mixing cells (all / unique owners) | Ambiguous pieces | Matched pieces lacking table ID |
|---|---:|---:|---:|---:|---:|---:|---:|
| an-7a2b17a3fb0f-p000200 | 801 | 787 | 14 | 175 | 223/116 | 148 | 0 |
| an-a3c2bdf81256-p000112 | 88 | 88 | 0 | 52 | 24/9 | 16 | 2 |
| an-d3237d690aa0-p000138 | 455 | 446 | 9 | 217 | 215/67 | 253 | 0 |
| s2-200e977f2dab5291c42c-p00035 | 267 | 265 | 2 | 45 | 58/29 | 32 | 0 |
| s2-6419488b7f8e69fd20da-p00001 | 306 | 294 | 12 | 245 | 116/91 | 218 | 0 |
| s2-80513ae109b4f749ca58-p00003 | 66 | 66 | 0 | 41 | 14/5 | 13 | 0 |
| s2-831443dc5e6f1ccfbaf5-p00020 | 621 | 567 | 54 | 106 | 235/27 | 214 | 0 |
| s2-dee99fdf5214acdc6f25-p00005 | 24 | 24 | 0 | 4 | 7/0 | 7 | 24 |

## Owner cases

| Page | Fold x (top → bottom) | Active line/box crossings | Diagnostic crossings |
|---|---|---:|---:|
| an-5c093c79d6bb-p000199 | 1687.000 → 1687.000 | 0/0 | 0 |
| an-9ea1564fcf4f-p000013 | 1629.500 → 1629.500 | 0/2 | 0 |
| an-a73d22211479-p000301 | single | 0/0 | 0 |
| s2-0ce9d1025b3f23c7119e-p00001 | single | 0/0 | 2 |
| s2-9de6cda8f03f0fc60a58-p00005 | single | 0/1 | 0 |
| s2-d1ed1c2db37f431f4acb-p00001 | single | 0/0 | 0 |

## Every crossing and refused join

Line/piece indices below refer to the frozen output order. Exact boundary IDs and all provisional annotation element/cell/row IDs are in the machine-readable audit, without truncation.

### an-1f8e7d022643-p000003

- Active line indices: 1.
- Piece indices: 1.
- Diagnostic line indices: .
- Refused row IDs: row-00001.

### an-2cfe28da5103-p000135

- Active line indices: 46.
- Piece indices: 3, 45.
- Diagnostic line indices: .
- Refused row IDs: row-00046.

### an-7a2b17a3fb0f-p000200

- Active line indices: 366, 418, 419, 424, 426, 532, 652, 661, 829, 860, 870, 1033, 1036, 1059, 1076, 1102, 1126, 1131, 1134, 1161, 1169, 1266, 1269, 1281, 1360, 1404, 1414, 1429, 1437, 1522, 1564.
- Piece indices: 5, 57, 58, 63, 65, 171, 291, 499, 509, 672, 675, 715, 741, 765, 770, 773, 800, 808, 905, 908, 920, 999, 1068, 1076, 1161, 1203.
- Diagnostic line indices: 30, 39, 42.
- Refused row IDs: row-00389, row-00396, row-00388, row-00603, row-00366, row-00701, row-00621, row-00623, row-00503, row-00443, row-00509, row-00394, row-00839, row-00931, row-00720, row-00953, row-00947, row-01027, row-00836, row-00704, row-00791, row-00907, row-00849, row-00776, row-01007, row-00770, row-00937, row-00735, row-00755, row-00773, row-00786.

### an-9ea1564fcf4f-p000013

- Active line indices: .
- Piece indices: 3, 43.
- Diagnostic line indices: .
- Refused row IDs: .

### an-a3c2bdf81256-p000112

- Active line indices: .
- Piece indices: .
- Diagnostic line indices: 15, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 41, 44, 47, 50, 56, 59, 62.
- Refused row IDs: .

### an-c153f2c605b3-p000040

- Active line indices: 18.
- Piece indices: 18.
- Diagnostic line indices: .
- Refused row IDs: row-00018.

### an-c8b96a901917-p000068

- Active line indices: 1.
- Piece indices: 1.
- Diagnostic line indices: .
- Refused row IDs: row-00001.

### an-d3237d690aa0-p000138

- Active line indices: .
- Piece indices: .
- Diagnostic line indices: 126, 128.
- Refused row IDs: .

### an-d83e7a198ade-p000099

- Active line indices: 1, 2, 21, 50, 51, 52, 55.
- Piece indices: 0, 1, 20, 49, 50, 51, 54.
- Diagnostic line indices: .
- Refused row IDs: row-00002, row-00051, row-00052, row-00055, row-00050, row-00001, row-00021.

### s2-09f5dfca4af4d74173c6-p00005

- Active line indices: 66.
- Piece indices: 58.
- Diagnostic line indices: .
- Refused row IDs: row-00066.

### s2-0ce9d1025b3f23c7119e-p00001

- Active line indices: .
- Piece indices: .
- Diagnostic line indices: 0, 63.
- Refused row IDs: .

### s2-200e977f2dab5291c42c-p00035

- Active line indices: 332, 333, 368, 372, 374, 377, 401, 457, 470, 471, 473, 483, 485, 497, 553, 585, 607, 630, 705, 710.
- Piece indices: 15, 16, 55, 57, 84, 140, 153, 168, 180, 236, 313, 393.
- Diagnostic line indices: 160, 162, 164, 166, 168, 170, 172, 175, 176, 266, 307, 308, 309, 310, 311, 312, 313.
- Refused row IDs: row-00332, row-00419, row-00418, row-00611, row-00408, row-00421, row-00348, row-00351, row-00531, row-00353, row-00430, row-00615, row-00513, row-00428, row-00438, row-00356, row-00550, row-00333, row-00372, row-00488.

### s2-60f24a3d8a2d714767f2-p00003

- Active line indices: 66.
- Piece indices: 66.
- Diagnostic line indices: .
- Refused row IDs: row-00066.

### s2-6419488b7f8e69fd20da-p00001

- Active line indices: 462, 470, 479, 494, 682, 750, 1153, 1165, 1181, 1255, 1348, 1377, 1407, 1570, 1571, 1667.
- Piece indices: 95, 112, 127, 315, 383, 786, 798, 814, 888, 981, 1010, 1040, 1203, 1204, 1300.
- Diagnostic line indices: 270, 271, 272, 273, 274, 275, 276, 277, 278.
- Refused row IDs: row-00991, row-00462, row-00793, row-00475, row-00833, row-00879, row-00789, row-00799, row-00467, row-00591, row-01037, row-00911, row-00469, row-00557, row-00990, row-00892.

### s2-658e6dcb48b540357a9d-p00001

- Active line indices: 9.
- Piece indices: 4.
- Diagnostic line indices: .
- Refused row IDs: row-00009.

### s2-6f552c96213b4c24a071-p00003

- Active line indices: 37.
- Piece indices: 37.
- Diagnostic line indices: .
- Refused row IDs: row-00037.

### s2-7247ee9b1bc2374b3980-p00001

- Active line indices: 105, 128.
- Piece indices: 88, 107.
- Diagnostic line indices: 51.
- Refused row IDs: row-00105, row-00128.

### s2-80513ae109b4f749ca58-p00003

- Active line indices: .
- Piece indices: .
- Diagnostic line indices: 36, 37, 40, 41, 43, 51, 53, 56, 62, 65, 67.
- Refused row IDs: .

### s2-831443dc5e6f1ccfbaf5-p00020

- Active line indices: 472, 530, 542, 604, 606, 729, 762, 764, 784, 789, 816, 830, 833, 866, 875, 956, 957, 958, 960.
- Piece indices: 96, 154, 228, 230, 386, 408, 413, 454, 457, 499, 581, 582, 584.
- Diagnostic line indices: 52.
- Refused row IDs: row-00547, row-00549, row-00739, row-00770, row-00852, row-00676, row-00486, row-00853, row-00855, row-00694, row-00646, row-00724, row-00678, row-00698, row-00496, row-00779, row-00851, row-00442, row-00736.

### s2-9de6cda8f03f0fc60a58-p00005

- Active line indices: .
- Piece indices: 60.
- Diagnostic line indices: .
- Refused row IDs: .

## Validation

The test suite receipt is `.astra/q1-tests.xml` and `.astra/q1-tests.log`. The focused tests cover a synthetic two-column page, physical spread, split table row, slanted and finite rules, forged mixed joins, exact sample preservation, and discounted rendering. The integration tests also cover live table preparation, renderer sidecars, separate component seeds, and scale invariance.

Full suite: **2201 passed, 16 skipped, 0 failures, 0 errors** (2217 collected). The 16 browser cases require an unavailable Chromium executable; they were not executed. One existing Docling deprecation warning remains.

All 54 structure JPEGs decoded at their source dimensions. Three 18-page contact sheets were visually inspected, as were the six owner cases at larger size and selected table overlays. Those checks verify artifact presentation, not certified printed-row or table ownership.

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$PY" -m pytest -p no:cacheprovider --junitxml=.astra/q1-tests.xml -q
PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/generate_api_docs.py
PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/archive/review_line_structure.py
# Fresh detections also emit structure (not used to overwrite the frozen baseline):
PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/glyphs/render_page_line_segments.py --layout .astra/layout --out /tmp/q1-fresh
```

## Unresolved

The full-envelope no-crossing gate is not satisfied. Existing crossing records and uncertain table boundaries need adjudication before geometry corrections can be justified. Table annotation mismatches are enumerated in the audit; retaining pre-split row provenance alone does not certify a table grid. The eighth annotated page, `s2-dee99fdf5214acdc6f25-p00005`, has no retained table region in the frozen delivery, so its table text remains ordinary lines. This run did not change table discovery. Automatic fold inference remains a heuristic with an explicit metadata override.
