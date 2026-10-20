# Page lines round 4, part 2: ordinary pages — 9 October 2026

Column stops now use direct slanted-stroke evidence and narrower persistent gutters. Continued strokes are checked before extending through letter bodies. A coherent faint tail is separated from a dark prefix before contrast scoring; uniformly faded text and isolated light letters are retained. Unsupported ornament bands are discounted before OCR delivery and rendering. The existing four font guides and two accent guides retain their joint per-line shape fit. OpenCV, already used by the table path, is now declared as a core dependency for slanted-stroke detection.

**Partial result.** The report distinguishes changed measurements from complete glyph recovery. Orientation and drop capitals are deferred. No held-out page was accessed. The 54 source PNGs and part-1 JSON/image outputs were preserved with hashes in `.astra/previous_round4_part1/receipt.json` before this run.

## Every requested case

“Unchanged” means the named issue was re-measured on the new output; it does not assert that all ink on that page is correct. Fixed refers to the named test, not whole-page OCR quality. Coordinates are review coordinates, used only by this evaluation script. Owner-position crossings require more than 0.75 x-heights on each side of the reference at the median baseline; both old and new outputs use this same test, so counts can differ from the original review’s fixed-pixel tolerance.

| Case | Page and exact place | New result and measurement | Status | New image |
|---|---|---|---|---|
| R3-26 | `s2-0ce9d1025b3f23c7119e-p00001` — Joined columns and faint halves | Owner-position crossings 12 → 0 (indices []); automatic crossings 0; active 30 → 35; 29 faint candidates discounted. Αριθ. 302 prefix: [(6, 284, 709, 0.9375)]; separately discounted tail: [(5, 716, 1691, 0.2562)]. Tuple = index/start/end/relative contrast. Faint-letter purity elsewhere remains unlabelled. | **fixed** | [view](../../../.astra/out/cases/r3-case-26.jpg) |
| R3-27 | `s2-93f8070059f938bda524-p00001` — Good reference to preserve | Exact line records equal to part 1: True; 117 active / 12 discounted; widest active 1450 px; cuts 47; foreign 39; crossings/overlaps/broken 0/0/0. | **unchanged** | [view](../../../.astra/out/cases/r3-case-27.jpg) |
| R3-29 | `s2-9de6cda8f03f0fc60a58-p00005` — Joined across the slanted solid rule | Owner-position crossings 31 → 1 (indices [0]); automatic crossings 0; active 96 → 123; 0 faint candidates discounted. Crossings use the review’s slanted path, separately from detected boundaries. Body-only joins below y 250: 30 → 0. The centred page number 485 above the rule is an intentional crossing of the extrapolated reference, verified on the image. | **fixed** | [view](../../../.astra/out/cases/r3-case-29.jpg) |
| R3-30 | `s2-d1ed1c2db37f431f4acb-p00001` — Joined across the differently slanted rule | Owner-position crossings 43 → 0 (indices []); automatic crossings 0; active 82 → 116; 8 faint candidates discounted. Crossings use the review’s slanted path, separately from detected boundaries. | **fixed** | [view](../../../.astra/out/cases/r3-case-30.jpg) |
| R3-31 | `s2-3229200bf47ca465a42d-p00004` — Missing first characters, old lines 32–46 | Old row → new row: start x = 32→24: 98, 33→25: 97, 34→26: 96, 35→27: 107, 36→28: 95, 37→29: 94, 38→30: 94, 39→31: 139, 40→32: 93, 41→33: 92, 42→34: 91, 43→35: 90, 44→36: 88, 45→37: 88. 12/14 start in the review’s approximate first-letter range (85–100 px, allowing 5 px). Page cuts 21 → 16. Old row 46 was already discounted at the bottom edge. Start position alone does not certify curl fit or every glyph. | **improved** | [view](../../../.astra/out/cases/r3-case-31.jpg) |
| R3-32 | `an-1436ae03653f-p000163` — Ornamental border, old s00039 | Active border candidates 2 → 1 (indices [37]); discounted candidates [36], reasons ['non-text: almost no letter bodies in component band']. The long reviewed band is removed; any remaining short edge fragment is still a failure. Discounted candidates have no cells or drawn guides. | **improved** | [view](../../../.astra/out/cases/r3-case-32.jpg) |
| R2-01 | all 54 pages; example `an-d6fd2cf2f618-p000047` — Four font guides | All 54 pages: median class-contact p90 residuals (x-heights): baseline 0.048, meanline 0.067, font_top 0.113, font_bottom 0.177; 5796 active lines borrow one of these guides. Six guides share one fitted shape and gradual scale; class truth and page-wide joint optimisation remain unvalidated. | **not fixed** | [view](../../../.astra/out/cases/r2-case-01.jpg) |
| R2-02 | `an-d6fd2cf2f618-p000047` — Accents split from letters | 1 active baselines in y 805–858: [16]. Accent marks are assigned to bodies; no independent accent-row crop is intended. | **unchanged** | [view](../../../.astra/out/cases/r2-case-02.jpg) |
| R2-03 | `s2-49598b2e848ab1f0ee1e-p00001` — First line of s00014 cut | New line 7, baseline y 900.8; top margin 2.03 x-heights; cutoff flag False; page cut flags 35 → 35. | **fixed** | [view](../../../.astra/out/cases/r2-case-03.jpg) |
| R2-04 | `s2-49598b2e848ab1f0ee1e-p00001` — Bottom of s00024 cut | New line 103, baseline y 2569.6; bottom margin 1.35 x-heights; cutoff flag True; page cut flags 35 → 35. | **not fixed** | [view](../../../.astra/out/cases/r2-case-04.jpg) |
| R2-05 | `an-d6fd2cf2f618-p000047` — Stamp over text | 0 active ring-lettering candidates; 1 discounted short candidates; short active IDs [35]. 1 text lines overextend beyond x 1120; stamp influence remains. | **unchanged** | [view](../../../.astra/out/cases/r2-case-05.jpg) |
| R2-06 | `an-d6fd2cf2f618-p000047` — Stamp lettering made into lines | 0 active ring-lettering candidates; 1 discounted short candidates; short active IDs [35]. The candidate near y 1820 is the printed catchword; rotation-based stamp classification is deferred. | **unchanged** | [view](../../../.astra/out/cases/r2-case-06.jpg) |
| R2-07 | `s2-09f5dfca4af4d74173c6-p00005` — Faint page | 9 faint candidates discounted in the named place; relative contrast 0.15–0.57; 9 total discounts. Faint letters inside active crops are not independently labelled. | **unchanged** | [view](../../../.astra/out/cases/r2-case-07.jpg) |
| R2-08 | `s2-0ce9d1025b3f23c7119e-p00001` — Faint lines | 29 faint candidates discounted in the named place; relative contrast 0.09–0.39; 30 total discounts. Column crossings 12 → 0. Faint letters inside active crops are not independently labelled. | **improved** | [view](../../../.astra/out/cases/r2-case-08.jpg) |
| R2-09 | `s2-5ca02b142a2a3eaf078a-p00002` — Bottom-right ghosts | 4 faint candidates discounted in the named place; relative contrast 0.15–0.26; 4 total discounts. Faint letters inside active crops are not independently labelled. | **unchanged** | [view](../../../.astra/out/cases/r2-case-09.jpg) |
| R2-10 | `s2-d1ed1c2db37f431f4acb-p00001` — Bottom-left show-through | 4 faint candidates discounted in the named place; relative contrast 0.34–0.43; 8 total discounts. Column crossings 43 → 0. Visual review still finds a false line on the bottom printed rule: [(61, 4213.8), (122, 4234.9)] (index, baseline y); its crop includes show-through. Faint letters inside active crops are not independently labelled. | **improved** | [view](../../../.astra/out/cases/r2-case-10.jpg) |
| R2-11 | `an-ef481610a820-p000181` — Jagged regions | Maximum boundary step 0.0701 x-heights; 0 overlaps (owner round 2 maximum 14.4). | **unchanged** | [view](../../../.astra/out/cases/r2-case-11.jpg) |
| R2-12 | `s2-49598b2e848ab1f0ee1e-p00001` — Opposite-column connection | 0 active crossings at reviewed x≈1530, y 1650–1900; indices []; automatic page crossings 0; broken pairs 0. | **fixed** | [view](../../../.astra/out/cases/r2-case-12.jpg) |
| R2-13 | `s2-74cdb23a34ca4a6cd01e-p00002` — Missed bottom-left text | 8 → 8 broad rows below y 4030; starts 29–193 px; 8 active candidates there; page rule mask 0.89%. Individual first/last letters remain unlabelled. | **unchanged** | [view](../../../.astra/out/cases/r2-case-13.jpg) |
| R2-14 | `s2-3229200bf47ca465a42d-p00004` — Curled line starts | 32/32 broad lines start left of x 170; median start 100.0 px. See round-3 case 31 for every bottom-row match and the remaining curl error. | **improved** | [view](../../../.astra/out/cases/r2-case-14.jpg) |
| R2-15 | `an-1f8e7d022643-p000003` — Headpiece and decorated initials | 0 active headpiece rows (round 2: 10); IDs []; 7 detected graphics. Decorated/drop initials remain deferred. | **unchanged** | [view](../../../.astra/out/cases/r2-case-15.jpg) |
| R2-16 | `an-1f8e7d022643-p000003` — Letter-spaced ΑΚΟΛΟΥΘΙΑ | 1 active ΑΚΟΛΟΥΘΙΑ heading rows; extents [(101, 1426)]; the first Α must remain with the rest. | **unchanged** | [view](../../../.astra/out/cases/r2-case-16.jpg) |
| R2-17 | `an-3352d912f2e9-p000104` — Text printed over stamp | Text rows in stamp area: [(27, 297, 1333), (28, 326, 1333), (29, 221, 1343), (30, 220, 1303)]; 4 cut flags. Printed ends are approximately x 1290; endpoint coverage is not proof of letter completeness. Ends extend farther into the stamp than part 1 (up to x 1343, previously 1328); this is not certified text recovery. | **not fixed** | [view](../../../.astra/out/cases/r2-case-17.jpg) |
| R2-18 | `an-3352d912f2e9-p000104` — Drop capital (open problem) | Open problem, deliberately deferred: the two-line Ε is not assigned as a drop capital. The 2 active paragraph rows here start at [(27, 297), (28, 326)] (index, x pixels), to its right. No drop-capital code change; the current crop is included for review. | **not fixed** | [view](../../../.astra/out/cases/r2-case-18.jpg) |
| R2-19 | `an-5c093c79d6bb-p000199` — Facing pages joined at top | 0 active crossings at reviewed x≈1670, y 120–400; indices []; automatic page crossings 0; broken pairs 0. | **fixed** | [view](../../../.astra/out/cases/r2-case-19.jpg) |
| R2-20 | `an-9ea1564fcf4f-p000013` — Facing pages joined throughout | 0 active crossings at reviewed x≈1545, y 220–1500; indices []; automatic page crossings 0; broken pairs 0. | **fixed** | [view](../../../.astra/out/cases/r2-case-20.jpg) |
| R2-21 | all 54 pages; example `an-d6fd2cf2f618-p000047` — Separate accent band | All 54 pages: median class-contact p90 residuals (x-heights): accent_bottom 0.120, accent_top 0.206; 4944 active lines borrow one of these guides. Six guides share one fitted shape and gradual scale; class truth and page-wide joint optimisation remain unvalidated. | **unchanged** | [view](../../../.astra/out/cases/r2-case-21.jpg) |
| R2-22 | `an-a73d22211479-p000301` — Broken column rule | 0 active crossings at reviewed x≈883, y 300–2250; indices []; automatic page crossings 0; broken pairs 0. | **fixed** | [view](../../../.astra/out/cases/r2-case-22.jpg) |
| R2-23 | `an-d6002cf45e4d-p000058` — Engraving, caption, initial and text | 0 → 0 active engraving candidates; last body row 6, start x 300; 0 broken pairs. The woodcut initial remains deferred. | **unchanged** | [view](../../../.astra/out/cases/r2-case-23.jpg) |
| R2-24 | `an-d6fd2cf2f618-p000047` — Capital running head | 1 running-head rows, IDs [2]; tall-body counts [13]; mean guide borrowed [True]. | **unchanged** | [view](../../../.astra/out/cases/r2-case-24.jpg) |
| R2-25 | `an-d6fd2cf2f618-p000047` — Text lost under stamp | Text rows in stamp area: [(28, 74, 1094), (29, 73, 1094), (30, 75, 1101), (31, 75, 1095), (32, 128, 1178), (33, 76, 1095), (34, 76, 1095)]; 5 cut flags. Printed ends are approximately x 1095; endpoint coverage is not proof of letter completeness.  | **unchanged** | [view](../../../.astra/out/cases/r2-case-25.jpg) |

## All 54 pages against part 1

Each vector is part 1 → part 2. G = median per-guide p90 residual / borrowed lines. E = no-body / close pairs. C = cut flags. D = discounts (not a badness score). J = maximum boundary step in x-heights. X = detected / fixed-position review crossings; the separate slanted review checks are in the cases above and checks JSON. M = unassigned text-size components / pixels, including possible non-text. N = graphic line / rough-segment intersections. B = broken pairs. F/O/S = foreign ink / overlaps / seam gaps. These checks use inferred components, not independent character labels. Every increase, including a changed denominator or numerical guide residual, is flagged.

| Page | G | E | C | D | J | X | M | N | B | F/O/S | Any worse? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `an-1436ae03653f-p000163` | 0.1025/8→0.1025/7 | 0/0→0/0 | 5→4 | 0→1 | 0.0586→0.0317 | 0/0→0/0 | 103/28061→109/33081 | 0/0→0/0 | 0→0 | 2/0/0→2/0/0 | **YES** |
| `an-1be60011c435-p000215` | 0.1407/30→0.1481/17 | 0/2→0/0 | 35→27 | 1→1 | 0.0942→0.0956 | 0/0→0/0 | 159/15324→168/15953 | 0/0→0/0 | 0→1 | 30/0/1→26/0/1 | **YES** |
| `an-1c6e1c0e929e-p000167` | 0.1476/4→0.1476/4 | 0/0→0/0 | 14→14 | 0→0 | 0.0517→0.0517 | 0/0→0/0 | 100/5599→100/5599 | 0/0→0/0 | 0→0 | 14/0/0→14/0/0 | No |
| `an-1f8e7d022643-p000003` | 0.0893/6→0.0893/6 | 0/0→0/0 | 9→9 | 3→3 | 0.0495→0.0495 | 0/0→0/0 | 44/7334→44/7334 | 0/1→0/1 | 0→0 | 8/0/0→8/0/0 | No |
| `an-2cfe28da5103-p000135` | 0.0998/14→0.0998/14 | 0/0→0/0 | 40→40 | 1→1 | 0.0972→0.0972 | 0/0→0/0 | 162/9569→162/9569 | 0/0→0/0 | 0→0 | 35/0/2→35/0/2 | No |
| `an-3352d912f2e9-p000104` | 0.1086/11→0.1074/11 | 0/0→0/0 | 16→16 | 9→12 | 0.0516→0.0539 | 0/0→0/0 | 241/35916→249/36877 | 0/1→0/1 | 0→0 | 15/0/1→15/0/1 | **YES** |
| `an-466cffad2cba-p000323` | 0.1116/2→0.1116/2 | 0/0→0/0 | 4→4 | 0→0 | 0.0414→0.0414 | 0/0→0/0 | 7/567→7/567 | 0/0→0/0 | 0→0 | 2/0/0→2/0/0 | No |
| `an-5c093c79d6bb-p000199` | 0.1104/21→0.1096/22 | 0/1→0/1 | 13→13 | 4→3 | 0.0366→0.0366 | 0/0→0/0 | 174/13182→178/13604 | 0/0→0/0 | 0→0 | 9/0/0→9/0/1 | **YES** |
| `an-778126cc8c2b-p000010` | 0.1105/3→0.1105/3 | 0/0→0/0 | 32→32 | 4→4 | 0.0745→0.0745 | 0/0→0/0 | 210/24676→210/24676 | 0/2→0/2 | 0→0 | 31/0/4→31/0/4 | No |
| `an-7a2b17a3fb0f-p000200` | 0.0435/1256→0.0435/1256 | 123/6→123/6 | 39→39 | 429→361 | 0.0010→0.0009 | 307/0→307/0 | 2/108→2/108 | 0/0→0/0 | 404→404 | 218/293/0→218/293/0 | No |
| `an-9ea1564fcf4f-p000013` | 0.1713/14→0.1682/16 | 0/2→0/1 | 51→51 | 4→5 | 0.0821→0.1082 | 0/0→0/0 | 406/22280→389/21869 | 0/0→0/0 | 0→0 | 49/0/6→47/0/1 | **YES** |
| `an-a3c2bdf81256-p000112` | 0.0167/309→0.0167/309 | 42/1→42/1 | 6→6 | 71→71 | 0.0138→0.0138 | 48/0→48/0 | 3/234→3/234 | 0/0→0/0 | 132→132 | 60/92/0→60/92/0 | No |
| `an-a73d22211479-p000301` | 0.0923/6→0.0923/6 | 0/1→0/1 | 71→71 | 0→1 | 0.0687→0.0687 | 0/0→0/0 | 346/25665→346/25665 | 0/0→0/0 | 0→0 | 68/0/5→67/0/5 | No |
| `an-b1a643813945-p000054` | 0.0813/11→0.0813/11 | 0/0→0/0 | 20→20 | 1→1 | 0.0509→0.0509 | 0/0→0/0 | 129/10695→129/10695 | 0/0→0/0 | 0→0 | 17/0/0→17/0/0 | No |
| `an-c153f2c605b3-p000040` | 0.0972/8→0.0972/8 | 0/1→0/1 | 12→12 | 3→3 | 0.1034→0.1034 | 0/0→0/0 | 87/18818→87/18818 | 0/0→0/0 | 0→0 | 5/0/3→5/0/3 | No |
| `an-c2c2053cfc10-p000056` | 0.1537/16→0.1537/16 | 0/0→0/0 | 32→32 | 0→0 | 0.0885→0.0885 | 0/0→0/0 | 121/8607→121/8607 | 0/0→0/0 | 0→0 | 30/0/3→30/0/3 | No |
| `an-c8b96a901917-p000068` | 0.0877/32→0.0874/20 | 0/3→0/1 | 27→19 | 12→3 | 0.0477→0.0477 | 0/0→0/0 | 154/26539→145/24910 | 0/0→0/0 | 0→0 | 20/0/2→17/0/1 | No |
| `an-d3237d690aa0-p000138` | 0.0000/1081→0.0000/1081 | 158/7→158/7 | 46→46 | 316→316 | 0.0000→0.0000 | 185/0→185/0 | 28/4878→28/4878 | 0/0→0/0 | 721→721 | 369/469/0→369/469/0 | No |
| `an-d6002cf45e4d-p000058` | 0.0531/5→0.0531/5 | 0/0→0/0 | 0→0 | 5→4 | 0.0077→0.0077 | 0/0→0/0 | 26/7928→23/6856 | 0/2→0/2 | 0→0 | 0/0/2→0/0/2 | **YES** |
| `an-d6fd2cf2f618-p000047` | 0.1186/4→0.1186/4 | 0/0→0/0 | 21→21 | 2→2 | 0.0654→0.0654 | 0/0→0/0 | 173/21389→173/21389 | 2/1→2/1 | 0→0 | 25/0/1→25/0/1 | No |
| `an-d83e7a198ade-p000099` | 0.1143/8→0.1143/8 | 0/4→0/4 | 40→40 | 1→1 | 0.0853→0.0853 | 0/0→0/0 | 266/23085→264/22884 | 0/1→0/1 | 0→0 | 35/0/21→35/0/21 | No |
| `an-e46611ae2fcc-p000041` | 0.1178/11→0.1167/9 | 0/0→0/0 | 21→18 | 3→4 | 0.0655→0.0655 | 0/0→0/0 | 240/16225→240/16380 | 0/0→0/0 | 0→0 | 17/0/2→16/0/0 | **YES** |
| `an-e74539ae215c-p000338` | 0.1032/18→0.1032/18 | 0/0→0/0 | 49→49 | 1→1 | 0.0849→0.0849 | 0/0→0/0 | 66/4721→66/4721 | 0/0→0/0 | 0→0 | 43/0/6→43/0/6 | No |
| `an-ef481610a820-p000181` | 0.1559/9→0.1559/9 | 0/1→0/1 | 28→28 | 7→7 | 0.0701→0.0701 | 0/0→0/0 | 471/69846→471/69846 | 0/0→0/0 | 0→0 | 27/0/9→27/0/9 | No |
| `an-fabf591ca801-p000067` | 0.1258/19→0.1239/22 | 0/4→0/3 | 22→22 | 2→5 | 0.0676→0.0545 | 0/0→0/0 | 62/6670→71/7600 | 0/0→0/0 | 0→0 | 17/0/1→18/0/1 | **YES** |
| `an-fd4fa0018ae1-p000037` | 0.1189/9→0.1192/8 | 0/1→0/1 | 20→20 | 0→0 | 0.0709→0.0709 | 0/0→0/0 | 207/13782→204/13602 | 0/0→0/0 | 0→0 | 16/0/1→16/0/1 | **YES** |
| `an-ffccc97c07de-p000152` | 0.1493/23→0.1526/24 | 0/5→0/5 | 25→23 | 9→9 | 0.0699→0.0705 | 0/0→0/0 | 224/48936→229/48336 | 0/0→0/0 | 0→0 | 16/0/15→17/0/15 | **YES** |
| `s2-0683f98f964a6d41cb72-p00003` | 0.1420/7→0.1420/7 | 0/0→0/0 | 18→18 | 19→10 | 0.0649→0.0649 | 0/0→0/0 | 87/8807→82/8246 | 0/0→0/0 | 0→0 | 16/0/0→16/0/0 | No |
| `s2-09f5dfca4af4d74173c6-p00005` | 0.0914/16→0.0914/16 | 0/1→0/1 | 25→25 | 9→9 | 0.0586→0.0586 | 0/0→0/0 | 182/15636→182/15636 | 0/0→0/0 | 0→0 | 18/0/5→18/0/5 | No |
| `s2-0ce9d1025b3f23c7119e-p00001` | 0.2296/4→0.1968/4 | 0/2→0/0 | 29→29 | 34→30 | 0.0643→0.0591 | 0/0→0/0 | 532/64653→561/68452 | 0/0→0/0 | 0→0 | 25/0/5→26/0/0 | **YES** |
| `s2-200e977f2dab5291c42c-p00035` | 0.0153/395→0.0147/393 | 83/5→83/5 | 20→20 | 317→317 | 0.0231→0.0128 | 119/0→119/0 | 45/15222→48/16235 | 0/0→0/0 | 25→26 | 104/129/0→104/129/0 | **YES** |
| `s2-23a70964fda83cb7aeb1-p00003` | 0.1097/12→0.1097/12 | 0/0→0/0 | 72→72 | 9→9 | 0.0476→0.0476 | 0/0→0/0 | 601/66492→601/66492 | 0/0→0/0 | 0→0 | 74/0/0→74/0/0 | No |
| `s2-3229200bf47ca465a42d-p00004` | 0.1519/9→0.1632/6 | 0/2→0/0 | 21→16 | 6→0 | 0.0762→0.0809 | 0/0→0/0 | 212/22107→176/16913 | 0/0→0/0 | 0→0 | 19/0/1→17/0/0 | **YES** |
| `s2-49598b2e848ab1f0ee1e-p00001` | 0.1713/16→0.1713/16 | 0/4→0/4 | 35→35 | 14→12 | 0.1011→0.1011 | 0/0→0/0 | 273/34432→271/34310 | 0/0→0/0 | 0→0 | 27/0/6→27/0/6 | No |
| `s2-5ca02b142a2a3eaf078a-p00002` | 0.1054/2→0.1054/2 | 0/0→0/0 | 22→22 | 4→4 | 0.0273→0.0273 | 0/0→0/0 | 133/22415→124/21345 | 0/0→0/0 | 0→0 | 23/0/0→23/0/0 | No |
| `s2-60f24a3d8a2d714767f2-p00003` | 0.1440/17→0.1440/17 | 0/4→0/4 | 66→66 | 0→0 | 0.0983→0.0983 | 0/0→0/0 | 137/13136→137/13136 | 0/1→0/1 | 0→0 | 60/0/5→60/0/5 | No |
| `s2-63f072d79585d71224b6-p00002` | 0.1243/5→0.1233/8 | 0/0→0/0 | 15→15 | 2→6 | 0.0464→0.0279 | 0/0→0/0 | 43/5599→46/6022 | 0/0→0/0 | 0→0 | 16/0/0→16/0/0 | **YES** |
| `s2-6419488b7f8e69fd20da-p00001` | 0.0000/1459→0.0000/1459 | 195/26→195/27 | 73→72 | 368→367 | 0.2694→0.2694 | 305/0→305/0 | 19/6460→19/6460 | 0/0→0/0 | 489→489 | 398/568/0→397/568/0 | **YES** |
| `s2-658e6dcb48b540357a9d-p00001` | 0.0969/12→0.0969/12 | 0/1→0/1 | 18→18 | 48→48 | 0.0420→0.0420 | 0/0→0/0 | 184/34690→184/34690 | 0/0→0/0 | 0→0 | 14/0/1→14/0/1 | No |
| `s2-661ddf05c8865e7b2c45-p00009` | 0.1761/8→0.1780/9 | 0/0→0/0 | 47→46 | 37→74 | 0.0543→0.0543 | 0/0→0/0 | 267/32108→322/41306 | 0/0→0/0 | 0→0 | 45/0/0→45/0/0 | **YES** |
| `s2-6f552c96213b4c24a071-p00003` | 0.1247/8→0.1247/8 | 0/0→0/0 | 17→17 | 10→4 | 0.0546→0.0546 | 0/0→0/0 | 100/9444→96/9153 | 0/0→0/0 | 0→0 | 17/0/0→17/0/0 | No |
| `s2-7247ee9b1bc2374b3980-p00001` | 0.0928/23→0.0863/19 | 0/2→0/0 | 53→57 | 19→23 | 0.0658→0.0658 | 0/14→0/0 | 406/64989→403/60144 | 0/0→0/0 | 0→0 | 52/0/25→54/0/17 | **YES** |
| `s2-74cdb23a34ca4a6cd01e-p00002` | 0.1236/14→0.1225/15 | 0/3→0/3 | 98→95 | 59→14 | 0.0638→0.0895 | 0/0→0/0 | 1292/194100→1254/188319 | 0/0→0/0 | 0→0 | 93/0/7→92/0/5 | **YES** |
| `s2-77d1bd63d5babbe0df73-p00001` | 0.1815/13→0.1815/13 | 0/0→0/0 | 17→17 | 0→0 | 0.1025→0.1025 | 0/0→0/0 | 76/5129→76/5129 | 0/0→0/0 | 0→0 | 12/0/1→12/0/1 | No |
| `s2-80513ae109b4f749ca58-p00003` | 0.0167/352→0.0167/352 | 57/9→57/9 | 24→24 | 89→89 | 0.0384→0.0384 | 51/0→51/0 | 5/769→5/769 | 0/0→0/0 | 374→374 | 165/159/0→165/159/0 | No |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 0.0176/590→0.0176/590 | 110/6→110/6 | 23→23 | 388→376 | 0.0450→0.0450 | 157/0→157/0 | 6/1520→6/1520 | 0/0→0/0 | 62→62 | 127/146/0→127/146/0 | No |
| `s2-86865c33eef5932c013b-p00005` | 0.2039/2→0.2039/2 | 0/0→0/0 | 37→37 | 2→2 | 0.0621→0.0621 | 0/0→0/0 | 100/12955→100/12955 | 0/0→0/0 | 0→0 | 36/0/0→36/0/0 | No |
| `s2-93f8070059f938bda524-p00001` | 0.1583/18→0.1583/18 | 0/2→0/2 | 47→47 | 12→12 | 0.0713→0.0713 | 0/0→0/0 | 833/82936→833/82936 | 0/0→0/0 | 0→0 | 39/0/3→39/0/3 | No |
| `s2-9de6cda8f03f0fc60a58-p00005` | 0.1302/12→0.1232/16 | 0/3→0/1 | 68→65 | 1→0 | 0.0715→0.0551 | 0/37→0/8 | 213/26976→143/10846 | 0/0→0/0 | 2→0 | 64/0/40→60/0/5 | **YES** |
| `s2-be269b8c315b16befc35-p00002` | 0.1439/7→0.1439/7 | 0/0→0/0 | 25→25 | 1→1 | 0.0237→0.0237 | 0/0→0/0 | 108/17589→108/17589 | 0/0→0/0 | 0→0 | 23/0/0→23/0/0 | No |
| `s2-d1ed1c2db37f431f4acb-p00001` | 0.1702/18→0.1234/18 | 0/5→0/1 | 67→77 | 7→8 | 0.0685→0.0542 | 0/43→0/0 | 1483/197275→1417/157086 | 0/0→0/0 | 2→0 | 62/1/28→77/0/5 | **YES** |
| `s2-dee99fdf5214acdc6f25-p00005` | 0.1153/5→0.1153/5 | 0/0→0/0 | 21→21 | 0→0 | 0.0458→0.0458 | 0/0→0/0 | 33/3622→33/3622 | 0/0→0/0 | 0→0 | 20/0/3→20/0/3 | No |
| `s2-dfcc21869afc140111ce-p00001` | 0.1143/23→0.1145/23 | 0/1→0/1 | 41→43 | 5→4 | 0.0454→0.0454 | 0/0→0/0 | 1163/128874→1181/130204 | 0/0→0/0 | 0→0 | 36/0/2→38/0/2 | **YES** |
| `s2-f9ec82212abc808325d7-p00010` | 0.1847/6→0.1847/6 | 0/0→0/0 | 19→19 | 18→18 | 0.0595→0.0595 | 0/0→0/0 | 102/9290→102/9286 | 0/0→0/0 | 0→0 | 18/0/0→18/0/0 | No |

### Every worsened measurement

- `an-1436ae03653f-p000163`: unassigned_body_components 106→112, unassigned_text_size_components 103→109, unassigned_text_size_ink 28061→33081.
- `an-1be60011c435-p000215`: broken_line_pairs 0→1, unassigned_body_components 161→171, guide_p90_median 0.1407405539→0.1480877244, maximum_jump 0.0942359129→0.09564855107, unassigned_text_size_components 159→168, unassigned_text_size_ink 15324→15953.
- `an-3352d912f2e9-p000104`: unassigned_body_components 246→255, maximum_jump 0.05157304487→0.05387990114, unassigned_text_size_components 241→249, unassigned_text_size_ink 35916→36877, lost_assigned_ink_fraction 0.001111782589→0.001221564063.
- `an-5c093c79d6bb-p000199`: strip_edge_touch_lines 2→3, unassigned_body_components 178→183, borrowed_lines 21→22, unassigned_text_size_components 174→178, unassigned_text_size_ink 13182→13604, seam_gaps 0→1.
- `an-9ea1564fcf4f-p000013`: borrowed_lines 14→16, maximum_jump 0.08214157644→0.1082347422.
- `an-d6002cf45e4d-p000058`: maximum_jump 0.007728012314→0.007728187742.
- `an-e46611ae2fcc-p000041`: unassigned_body_components 247→248, unassigned_text_size_ink 16225→16380.
- `an-fabf591ca801-p000067`: foreign_ink_lines 17→18, unassigned_body_components 63→82, borrowed_lines 19→22, unassigned_text_size_components 62→71, unassigned_text_size_ink 6670→7600, lost_assigned_ink_fraction 0.001443934868→0.001471727343.
- `an-fd4fa0018ae1-p000037`: guide_p90_median 0.1189304664→0.1191909416, lost_assigned_ink_fraction 0.001311479936→0.001311873839.
- `an-ffccc97c07de-p000152`: foreign_ink_lines 16→17, unassigned_body_components 228→234, guide_p90_median 0.1492645402→0.1525936386, borrowed_lines 23→24, maximum_jump 0.06985718268→0.07049223069, unassigned_text_size_components 224→229, lost_assigned_ink_fraction 0.04802753557→0.04873477255.
- `s2-0ce9d1025b3f23c7119e-p00001`: foreign_ink_lines 25→26, strip_edge_touch_lines 12→13, unassigned_body_components 533→562, unassigned_text_size_components 532→561, unassigned_text_size_ink 64653→68452.
- `s2-200e977f2dab5291c42c-p00035`: broken_line_pairs 25→26, unassigned_body_components 48→50, unassigned_text_size_components 45→48, unassigned_text_size_ink 15222→16235.
- `s2-3229200bf47ca465a42d-p00004`: guide_p90_median 0.1519435672→0.1631914647, maximum_jump 0.07618013413→0.08090432813.
- `s2-63f072d79585d71224b6-p00002`: unassigned_body_components 45→48, borrowed_lines 5→8, unassigned_text_size_components 43→46, unassigned_text_size_ink 5599→6022.
- `s2-6419488b7f8e69fd20da-p00001`: close_pairs 26→27.
- `s2-661ddf05c8865e7b2c45-p00009`: unassigned_body_components 272→331, guide_p90_median 0.1760692599→0.1779757818, borrowed_lines 8→9, unassigned_text_size_components 267→322, unassigned_text_size_ink 32108→41306.
- `s2-7247ee9b1bc2374b3980-p00001`: cut_ink_lines 53→57, foreign_ink_lines 52→54, source_boundary_cut_lines 53→57.
- `s2-74cdb23a34ca4a6cd01e-p00002`: borrowed_lines 14→15, maximum_jump 0.06379808457→0.08952551537.
- `s2-9de6cda8f03f0fc60a58-p00005`: borrowed_lines 12→16.
- `s2-d1ed1c2db37f431f4acb-p00001`: cut_ink_lines 67→77, foreign_ink_lines 62→77, source_boundary_cut_lines 67→76.
- `s2-dfcc21869afc140111ce-p00001`: cut_ink_lines 41→43, foreign_ink_lines 36→38, source_boundary_cut_lines 41→43, unassigned_body_components 1163→1182, guide_p90_median 0.1142683112→0.1145246211, unassigned_text_size_components 1163→1181, unassigned_text_size_ink 128874→130204, lost_assigned_ink_fraction 0.001326414623→0.001344763413.

## Table preservation

See [table-preservation.json](../../../.astra/out/table-preservation.json) for all eight pages: current piece geometry against part 1, element-by-element coverage, crossing pieces, and fresh model forwards. The offline acceptance harness and actual DocumentConverter label-injection pipeline were rerun. Recognition remains substituted with labels.

Part-1 acceptance preservation: **8/8 pass**. This preserves the existing partial table result; it does not turn the part-1 failures into passes.

| Page | Complete elements | Crossing pieces | Final missing labels | Wrong owners | Preserved? |
|---|---|---|---|---|---|
| `an-7a2b17a3fb0f-p000200` | 430→430 | 114→114 | 1→1 | 942→942 | True |
| `an-a3c2bdf81256-p000112` | 40→40 | 0→0 | 310→310 | 0→0 | True |
| `an-d3237d690aa0-p000138` | 359→359 | 68→68 | 0→0 | 1240→1240 | True |
| `s2-200e977f2dab5291c42c-p00035` | 124→124 | 20→20 | 74→74 | 246→246 | True |
| `s2-6419488b7f8e69fd20da-p00001` | 56→56 | 47→47 | 6→6 | 968→968 | True |
| `s2-80513ae109b4f749ca58-p00003` | 47→47 | 1→1 | 0→0 | 827→827 | True |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 308→308 | 180→180 | 0→0 | 302→302 | True |
| `s2-dee99fdf5214acdc6f25-p00005` | 23→23 | 6→6 | 24→24 | 0→0 | True |

## What does not work yet

- Guide residuals measure inferred classes. They do not certify correct small-letter, capital, accent or descender labels. The fit is joint per line, regularised by neighbouring baseline geometry; it is not a fully joint six-class page-wide optimisation.
- Contrast splitting handles coherent spatial changes, including a dark prefix followed by a faint tail. Faint ink interleaved or superimposed with foreground letters and stamp removal remain unresolved; no independent semantic purity count is claimed.
- Curl recovery can retain more first-letter ink while still misfitting a first-letter baseline or retaining margin ink. Inspect the named line matches and images; endpoint changes alone are not an acceptance gate.
- Boundary cuts, foreign ink, unassigned text-size components and possible broken rows remain. 21/54 pages have at least one worse measurement; all are listed above. Case 10 still includes a false crop on the bottom printed rule, with show-through inside it.
- Ornament rejection is conservative morphology and support analysis. Repeated shapes resembling actual letters cannot be identified reliably without further evidence.
- The overall-review question about per-letter ink states remains open: line JSON contains component class counts, not per-letter intact/merged/broken/faint records.
- Part-1 table failures remain open. Orientation and drop-capital handling were not implemented. No character recognition, CER or held-out generalisation test was run.

## Validation and reproduction

Full suite: **2031 passed, 16 skipped, 0 failed; 2047 collected**. [Log](../../../.astra/out/tests-nontable.log).

Nine new parametrised synthetic checks cover ±0.5°/±1° rules with level neighbouring rows, a faint half opposite dark text, a dark prefix with a faint tail in the same column, curled starts beside a binding shadow, repeated solid non-letter shapes with real-text controls, and false continuation through separated letter stems. All artifact sets are checked for finite curves, page-unit boxes, valid image streams and exclusion of discounted candidates from cells. The renderer skips discounts for both overlays and strips.

Use `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` from this worktree, with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`:

```sh
python scripts/generate_api_docs.py
python -m pytest -p no:cacheprovider --junitxml=.astra/out/tests-nontable.xml
python scripts/glyphs/render_page_line_segments.py --layout .astra/layout
python scripts/glyphs/archive/evaluate_tables_round4.py
python scripts/glyphs/archive/integrate_docling_tables_round4.py
python scripts/glyphs/archive/score_tables_round4.py
python scripts/glyphs/archive/check_tables_part2.py
python scripts/glyphs/archive/review_page_lines_round4_nontable.py
```

API regeneration produced 211 public entries and no API diff. No public signature changed. Foreground execution only; no push or model download. Machine-readable results: [case records](../../../.astra/out/cases-nontable.json), [all-page regression](../../../.astra/out/regression-nontable.json).

## Commit handoff

No commit was made: the sandbox refused creation of the worktree `index.lock` during `git add` (`Operation not permitted`). The requested fallback is [the patch](../../../.astra/page-lines-round4-nontable.patch) and [the commit script](../../../.astra/commit-page-lines-round4-nontable.sh). The patch is replayed against HEAD files in a temporary directory and checked byte-for-byte. The script verifies branch `astra/page-lines-4`, base `376ab5d`, an empty index, file hashes and reverse patch applicability before committing the explicit file list with the requested Co-Authored-By and Claude-Session footers. It does not push. [Validation receipt](../../../.astra/round4-nontable-patch-validation.json).
