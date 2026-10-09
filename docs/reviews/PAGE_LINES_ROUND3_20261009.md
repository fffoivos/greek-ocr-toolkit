# Page-lines round 3 — 9 October 2026

The detector now separates faint overlays from dark print, continues collinear rule pieces, and uses persistent page gaps to separate columns and facing pages. Capitals, small bodies, descenders and detached marks supply different contacts to a joint six-guide fit. Missing classes are recorded as borrowed. Region seams use stable neighbours and bend around assigned ink.

**This remains a partial result.** The saved checks measure inferred component ownership, not manually labelled character truth. A smooth curve or a zero crossing count does not prove complete or pure OCR strips. Discounted candidates remain visible in JSON and review images; the public OCR-line API excludes them.

## Implementation and validation

- Pixel-only discovery and supplemental body-bottom groups retain capital headings. PDF boxes are provenance only; all 24 available Vouli hint reruns must have identical geometry.
- `page_font.py` classifies ink, associates marks, splits a fused upper mark at a narrow neck, and alternates one curve with robust class offsets. Compatible sizes supply missing font ratios. Gradual x-height variation is enabled only with distributed small-letter evidence. No third accent guide is asserted: there is no validated two-mode stack classification.
- Long thin rule pieces are fitted in page coordinates. Isolated glyph stems are vetoed as rules. Graphic frames/texture and repeated motifs are removed before rule continuation, avoiding extrapolating picture strokes across text.
- Baseline contacts still initialise shared column geometry with the existing crop tools. Local class fitting refines that initial shape; this is not a fully joint page-wide six-class optimisation. Font grouping currently uses type size, not a validated italic/typeface classifier.
- Regions share smooth constraints between overlapping neighbours. Where ownership interleaves incompatibly, the midpoint compromise can still cut ink; those cuts remain in the checks.
- Tests: see `.astra/tests-round3.log`; 12 new regressions cover all nine requested scenes, shared whitespace seams, indented reading order, and a connected table frame. Recognition is mocked by the existing contracts. The saved artifact and curl audits are separate from tests.

### Traced round-2 causes

For the missing running head, replaying `f405fe3` shows seed 2 (x 82–1099, y 73–284) peeling body lines at y 269, 217 and 166 with a fixed 21 px prior. On the next iteration the remaining head produces a projection peak at local y 53.4, but the crop fitter returns an unsupported band at page y 232.8 and zero letter bodies. `_discover` breaks there. The header pixels were neither absent nor masked; the fixed body-size prior and unsupported crop result stopped discovery. The supplemental body-bottom grouping recovers this capital band.

For the missing first word below the woodcut on `an-d6002cf45e4d-p000058`, replaying round 2 finds intact text components at x 300–616, y 2934–2987, but no rough seed intersecting that row left of x 700. The model starts at x 923, y 2964. The woodcut rule evidence constrains the whole rough horizontal zone, and the later ten-x-height extension cannot reach the beginning. Thus unmasked pixels alone were insufficient: the seed column cut and bounded extension caused the miss. The revised graphic exclusion and rule handling restore a seed along the last row.

The reproduction traces are retained in `.astra/work/trace-round2.log` and `.astra/work/trace-header.log`. Neither trace uses text-layer transcription as truth.

## Every owner case

| # | Page / place | New output and measured evidence | Status | Image |
|---:|---|---|---|---|
| 1 | `an-d6fd2cf2f618-p000047` — Four font guides | Class-conditioned joint fit; median per-line p90 distance in x-heights: baseline 0.080, meanline 0.089, font_top 0.153, font_bottom 0.204. 1403 active lines borrow at least one of these guides. Class assignments remain inferred. Independent font accuracy remains unresolved; the frozen page-level curl maximum regresses to 14.61 px. | **not fixed** | [case-01](../../.astra/out/cases/case-01.jpg) |
| 2 | `an-d6fd2cf2f618-p000047` — Accents split from letters | 1 active baselines in the reviewed accent/body band (y 805–858); indices [16]. Marks attach to a body line. | **fixed** | [case-02](../../.astra/out/cases/case-02.jpg) |
| 3 | `s2-49598b2e848ab1f0ee1e-p00001` — First line of s00014 cut | New line 9; top margin 2.03 x-heights; source/strip cutoff flag False. Page cutoff count 35. | **fixed** | [case-03](../../.astra/out/cases/case-03.jpg) |
| 4 | `s2-49598b2e848ab1f0ee1e-p00001` — Bottom of s00024 cut | New line 105; bottom margin 1.35 x-heights; source/strip cutoff flag True. Page cutoff count 35. | **improved** | [case-04](../../.astra/out/cases/case-04.jpg) |
| 5 | `an-d6fd2cf2f618-p000047` — Stamp over text | No separate active ring-lettering rows (0 candidates); faint ring row(s) [36] discounted. Text continues through the stamp, but 1 body line(s) extend beyond x 1120 ([32]); stamp influence is not fully removed. | **improved** | [case-05](../../.astra/out/cases/case-05.jpg) |
| 6 | `an-d6fd2cf2f618-p000047` — Stamp lettering made into lines | 0 active ring-lettering candidates; 1 faint candidates retained with a discount reason ([36]). The remaining short active line [35] is the printed catchword, verified in case-06. | **fixed** | [case-06](../../.astra/out/cases/case-06.jpg) |
| 7 | `s2-09f5dfca4af4d74173c6-p00005` — Faint page | 9 faint candidates explicitly discounted in the reviewed place; contrast/text range 0.15–0.57; 9 total discounted. Uniform fading is retained in the synthetic control. | **fixed** | [case-07](../../.astra/out/cases/case-07.jpg) |
| 8 | `s2-0ce9d1025b3f23c7119e-p00001` — Faint lines | 34 faint candidates explicitly discounted in the reviewed place; contrast/text range 0.09–0.50; 34 total discounted. Uniform fading is retained in the synthetic control. | **fixed** | [case-08](../../.astra/out/cases/case-08.jpg) |
| 9 | `s2-5ca02b142a2a3eaf078a-p00002` — Bottom-right ghosts | 4 faint candidates explicitly discounted in the reviewed place; contrast/text range 0.15–0.26; 4 total discounted. Uniform fading is retained in the synthetic control. | **fixed** | [case-09](../../.astra/out/cases/case-09.jpg) |
| 10 | `s2-d1ed1c2db37f431f4acb-p00001` — Bottom-left show-through | 2 faint candidates explicitly discounted in the reviewed place; contrast/text range 0.43–0.44; 7 total discounted. Uniform fading is retained in the synthetic control. | **fixed** | [case-10](../../.astra/out/cases/case-10.jpg) |
| 11 | `an-ef481610a820-p000181` — Jagged regions | Maximum adjacent-column region jump 0.070 x-heights (round 2: 14.4); 0 active overlap pairs. | **fixed** | [case-11](../../.astra/out/cases/case-11.jpg) |
| 12 | `s2-49598b2e848ab1f0ee1e-p00001` — Opposite-column connection | 0 active lines cross the owner-located boundary x≈1530 in y 1650–1900; 1 full-height gutters and 1 fitted rule paths; automatic crossings 0. Left/right column IDs: [0]/[1]. | **fixed** | [case-12](../../.astra/out/cases/case-12.jpg) |
| 13 | `s2-74cdb23a34ca4a6cd01e-p00002` — Missed bottom-left text | 8 active lines wider than 800 px in the reviewed corner, starts 29–193; 8 candidates there; page rule mask 0.61%. The last two printed rows are covered by [{'line': 81, 'x': [192, 1653], 'cut': True}, {'line': 82, 'x': [29, 1644], 'cut': True}]; the last region overextends into the left margin. Individual letter recall remains unlabelled. | **improved** | [case-13](../../.astra/out/cases/case-13.jpg) |
| 14 | `s2-3229200bf47ca465a42d-p00004` — Curled line starts | 32/32 broad lines now start left of x 170; median start 111 px; page cutoff count 21. Curl-tip completeness is not established by the start coordinate. | **improved** | [case-14](../../.astra/out/cases/case-14.jpg) |
| 15 | `an-1f8e7d022643-p000003` — Headpiece and decorated initials | 0 active headpiece lines (round 2: 10); 7 detected graphic regions. Case-15 also shows no active frame fragments; the letters inside decorated initials remain deferred. | **fixed** | [case-15](../../.astra/out/cases/case-15.jpg) |
| 16 | `an-1f8e7d022643-p000003` — Letter-spaced ΑΚΟΛΟΥΘΙΑ | 1 active heading line(s), x extents [(101, 1426)]; first Α and remaining capitals are judged at heading size. | **fixed** | [case-16](../../.astra/out/cases/case-16.jpg) |
| 17 | `an-3352d912f2e9-p000104` — Text printed over stamp | Former lines 27/28 now match [(26, 221, 1327), (27, 220, 1303)]; printed right end is about x 1290. Cutoff flags [True, True]. | **improved** | [case-17](../../.astra/out/cases/case-17.jpg) |
| 18 | `an-3352d912f2e9-p000104` — Drop capital (open problem) | Open problem, explicitly deferred: the first two body lines start at [(24, 297), (25, 326)]. No claim that the large Ε is assigned correctly. | **not fixed** | [case-18](../../.astra/out/cases/case-18.jpg) |
| 19 | `an-5c093c79d6bb-p000199` — Facing pages joined at top | 0 active lines cross the owner-located boundary x≈1670 in y 120–400; 2 full-height gutters and 4 fitted rule paths; automatic crossings 0. | **fixed** | [case-19](../../.astra/out/cases/case-19.jpg) |
| 20 | `an-9ea1564fcf4f-p000013` — Facing pages joined throughout | 0 active lines cross the owner-located boundary x≈1545 in y 220–1500; 7 full-height gutters and 4 fitted rule paths; automatic crossings 0. | **fixed** | [case-20](../../.astra/out/cases/case-20.jpg) |
| 21 | `an-d6fd2cf2f618-p000047` — Separate accent band | Class-conditioned joint fit; median per-line p90 distance in x-heights: accent_bottom 0.131, accent_top 0.228. 1247 active lines borrow at least one of these guides. Class assignments remain inferred. | **improved** | [case-21](../../.astra/out/cases/case-21.jpg) |
| 22 | `an-a73d22211479-p000301` — Broken column rule | 0 active lines cross the owner-located boundary x≈883 in y 300–2250; 1 full-height gutters and 1 fitted rule paths; automatic crossings 0. Left/right column IDs: [0]/[1]. | **fixed** | [case-22](../../.astra/out/cases/case-22.jpg) |
| 23 | `an-d6002cf45e4d-p000058` — Engraving, caption, initial and text | 0 active engraving candidates (round 2: 16); last text candidate 7 starts x 300; 0 possible broken pairs. Woodcut letter remains deferred. | **fixed** | [case-23](../../.astra/out/cases/case-23.jpg) |
| 24 | `an-d6fd2cf2f618-p000047` — Capital running head | 1 running-head line(s), indices [2]; tall-body counts [13]; meanline borrowed [True]. | **fixed** | [case-24](../../.astra/out/cases/case-24.jpg) |
| 25 | `an-d6fd2cf2f618-p000047` — Text lost under stamp | 7/7 body lines through the stamp reach x≥1050; right ends [1094, 1094, 1101, 1095, 1178, 1095, 1095]; 5 still carry a cutoff flag. | **improved** | [case-25](../../.astra/out/cases/case-25.jpg) |

## All 48 pages: checks 1–10

Guide is the median of measured per-guide p90 residuals in x-heights (full class and per-line values are in each checks JSON). Borrow counts active lines borrowing any guide. Extra = no-body / closer-than-half-pitch pairs. Cut = source boundary or strip edge. D = discounted candidates. Jump = largest active region step in x-heights. Miss = unassigned text-size components, including possible non-text. Graphic = active lines / rough segment boxes intersecting detected graphics, not a semantic ground-truth count. Broken covers both heading and general possible splits. Gaps counts nearest-neighbour seams that still disagree after all competing constraints; each gap magnitude is recorded in check 10. Stamp-truncated text still requires the named visual cases; no automatic semantic stamp-recall count is claimed.

| Page | Active | D | Guide | Borrow | Extra | Cut | Jump | Cross | Miss | Rule % | Graphic | Broken | Foreign | Overlap | Gaps |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `an-1be60011c435-p000215` | 73 | 1 | 0.141 | 30 | 0/2 | 35 | 0.094 | 0 | 159 | 0.49 | 0/0 | 0 | 30 | 0 | 1 |
| `an-1c6e1c0e929e-p000167` | 29 | 0 | 0.148 | 4 | 0/0 | 14 | 0.052 | 0 | 100 | 0.00 | 0/0 | 0 | 14 | 0 | 0 |
| `an-1f8e7d022643-p000003` | 18 | 3 | 0.089 | 6 | 0/0 | 9 | 0.050 | 0 | 44 | 0.04 | 0/1 | 0 | 8 | 0 | 0 |
| `an-2cfe28da5103-p000135` | 90 | 1 | 0.100 | 14 | 0/0 | 40 | 0.097 | 0 | 162 | 0.11 | 0/0 | 0 | 35 | 0 | 2 |
| `an-3352d912f2e9-p000104` | 26 | 9 | 0.109 | 11 | 0/0 | 16 | 0.052 | 0 | 241 | 0.94 | 0/1 | 0 | 15 | 0 | 1 |
| `an-466cffad2cba-p000323` | 25 | 0 | 0.112 | 2 | 0/0 | 4 | 0.041 | 0 | 7 | 0.02 | 0/0 | 0 | 2 | 0 | 0 |
| `an-5c093c79d6bb-p000199` | 75 | 4 | 0.110 | 21 | 0/1 | 13 | 0.037 | 0 | 174 | 1.40 | 0/0 | 0 | 9 | 0 | 0 |
| `an-778126cc8c2b-p000010` | 37 | 4 | 0.110 | 3 | 0/0 | 32 | 0.074 | 0 | 210 | 0.69 | 0/2 | 0 | 31 | 0 | 4 |
| `an-7a2b17a3fb0f-p000200` | 414 | 15 | 0.044 | 405 | 0/0 | 53 | 0.078 | 0 | 335 | 4.91 | 0/5 | 2 | 34 | 0 | 79 |
| `an-9ea1564fcf4f-p000013` | 84 | 4 | 0.171 | 14 | 0/2 | 51 | 0.082 | 0 | 406 | 1.40 | 0/0 | 0 | 49 | 0 | 6 |
| `an-a73d22211479-p000301` | 90 | 0 | 0.092 | 6 | 0/1 | 71 | 0.069 | 0 | 346 | 0.74 | 0/0 | 0 | 68 | 0 | 5 |
| `an-b1a643813945-p000054` | 31 | 1 | 0.081 | 11 | 0/0 | 20 | 0.051 | 0 | 129 | 0.08 | 0/0 | 0 | 17 | 0 | 0 |
| `an-c153f2c605b3-p000040` | 31 | 3 | 0.097 | 8 | 0/1 | 12 | 0.103 | 0 | 87 | 1.82 | 0/0 | 0 | 5 | 0 | 3 |
| `an-c2c2053cfc10-p000056` | 75 | 0 | 0.154 | 16 | 0/0 | 32 | 0.089 | 0 | 121 | 0.00 | 0/0 | 0 | 30 | 0 | 3 |
| `an-c8b96a901917-p000068` | 149 | 12 | 0.088 | 32 | 0/3 | 27 | 0.048 | 0 | 154 | 0.60 | 0/0 | 0 | 20 | 0 | 2 |
| `an-d6002cf45e4d-p000058` | 6 | 5 | 0.053 | 5 | 0/0 | 0 | 0.008 | 0 | 26 | 0.20 | 0/2 | 0 | 0 | 0 | 2 |
| `an-d6fd2cf2f618-p000047` | 35 | 2 | 0.119 | 4 | 0/0 | 21 | 0.065 | 0 | 173 | 0.00 | 2/1 | 0 | 25 | 0 | 1 |
| `an-d83e7a198ade-p000099` | 83 | 1 | 0.114 | 8 | 0/4 | 40 | 0.085 | 0 | 266 | 0.40 | 0/1 | 0 | 35 | 0 | 21 |
| `an-e46611ae2fcc-p000041` | 65 | 3 | 0.118 | 11 | 0/0 | 21 | 0.066 | 0 | 240 | 0.69 | 0/0 | 0 | 17 | 0 | 2 |
| `an-e74539ae215c-p000338` | 94 | 1 | 0.103 | 18 | 0/0 | 49 | 0.085 | 0 | 66 | 0.05 | 0/0 | 0 | 43 | 0 | 6 |
| `an-ef481610a820-p000181` | 34 | 7 | 0.156 | 9 | 0/1 | 28 | 0.070 | 0 | 471 | 0.51 | 0/0 | 0 | 27 | 0 | 9 |
| `an-fabf591ca801-p000067` | 80 | 2 | 0.126 | 19 | 0/4 | 22 | 0.068 | 0 | 62 | 0.34 | 0/0 | 0 | 17 | 0 | 1 |
| `an-fd4fa0018ae1-p000037` | 34 | 0 | 0.119 | 9 | 0/1 | 20 | 0.071 | 0 | 207 | 0.07 | 0/0 | 0 | 16 | 0 | 1 |
| `an-ffccc97c07de-p000152` | 36 | 9 | 0.149 | 23 | 0/5 | 25 | 0.070 | 0 | 224 | 0.44 | 0/0 | 0 | 16 | 0 | 15 |
| `s2-0683f98f964a6d41cb72-p00003` | 39 | 19 | 0.142 | 7 | 0/0 | 18 | 0.065 | 0 | 87 | 0.00 | 0/0 | 0 | 16 | 0 | 0 |
| `s2-09f5dfca4af4d74173c6-p00005` | 60 | 9 | 0.091 | 16 | 0/1 | 25 | 0.059 | 0 | 182 | 0.00 | 0/0 | 0 | 18 | 0 | 5 |
| `s2-0ce9d1025b3f23c7119e-p00001` | 30 | 34 | 0.230 | 4 | 0/2 | 29 | 0.064 | 0 | 532 | 0.03 | 0/0 | 0 | 25 | 0 | 5 |
| `s2-200e977f2dab5291c42c-p00035` | 268 | 49 | 0.022 | 266 | 0/34 | 41 | 0.077 | 0 | 262 | 6.16 | 0/0 | 1 | 38 | 0 | 60 |
| `s2-23a70964fda83cb7aeb1-p00003` | 125 | 9 | 0.110 | 12 | 0/0 | 72 | 0.048 | 0 | 601 | 0.38 | 0/0 | 0 | 74 | 0 | 0 |
| `s2-3229200bf47ca465a42d-p00004` | 42 | 6 | 0.152 | 9 | 0/2 | 21 | 0.076 | 0 | 212 | 0.93 | 0/0 | 0 | 19 | 0 | 1 |
| `s2-49598b2e848ab1f0ee1e-p00001` | 118 | 14 | 0.171 | 16 | 0/4 | 35 | 0.101 | 0 | 273 | 0.40 | 0/0 | 0 | 27 | 0 | 6 |
| `s2-5ca02b142a2a3eaf078a-p00002` | 41 | 4 | 0.105 | 2 | 0/0 | 22 | 0.027 | 0 | 133 | 0.14 | 0/0 | 0 | 23 | 0 | 0 |
| `s2-60f24a3d8a2d714767f2-p00003` | 129 | 0 | 0.144 | 17 | 0/4 | 66 | 0.098 | 0 | 137 | 0.33 | 0/1 | 0 | 60 | 0 | 5 |
| `s2-63f072d79585d71224b6-p00002` | 42 | 2 | 0.124 | 5 | 0/0 | 15 | 0.046 | 0 | 43 | 0.58 | 0/0 | 0 | 16 | 0 | 0 |
| `s2-658e6dcb48b540357a9d-p00001` | 35 | 48 | 0.097 | 12 | 0/1 | 18 | 0.042 | 0 | 184 | 0.00 | 0/0 | 0 | 14 | 0 | 1 |
| `s2-661ddf05c8865e7b2c45-p00009` | 125 | 37 | 0.176 | 8 | 0/0 | 47 | 0.054 | 0 | 267 | 0.79 | 0/0 | 0 | 45 | 0 | 0 |
| `s2-6f552c96213b4c24a071-p00003` | 38 | 10 | 0.125 | 8 | 0/0 | 17 | 0.055 | 0 | 100 | 0.07 | 0/0 | 0 | 17 | 0 | 0 |
| `s2-7247ee9b1bc2374b3980-p00001` | 100 | 19 | 0.093 | 23 | 0/2 | 53 | 0.066 | 0 / 14 reviewed | 406 | 0.08 | 0/0 | 0 | 52 | 0 | 25 |
| `s2-74cdb23a34ca4a6cd01e-p00002` | 130 | 59 | 0.124 | 14 | 0/3 | 98 | 0.064 | 0 | 1292 | 0.61 | 0/0 | 0 | 93 | 0 | 7 |
| `s2-77d1bd63d5babbe0df73-p00001` | 39 | 0 | 0.182 | 13 | 0/0 | 17 | 0.102 | 0 | 76 | 0.00 | 0/0 | 0 | 12 | 0 | 1 |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 356 | 32 | 0.022 | 356 | 0/61 | 47 | 0.026 | 0 | 455 | 8.34 | 0/0 | 0 | 36 | 0 | 84 |
| `s2-86865c33eef5932c013b-p00005` | 40 | 2 | 0.204 | 2 | 0/0 | 37 | 0.062 | 0 | 100 | 0.00 | 0/0 | 0 | 36 | 0 | 0 |
| `s2-93f8070059f938bda524-p00001` | 117 | 12 | 0.158 | 18 | 0/2 | 47 | 0.071 | 0 | 833 | 0.05 | 0/0 | 0 | 39 | 0 | 3 |
| `s2-9de6cda8f03f0fc60a58-p00005` | 96 | 1 | 0.130 | 12 | 0/3 | 68 | 0.071 | 0 / 37 reviewed | 213 | 0.05 | 0/0 | 2 | 64 | 0 | 40 |
| `s2-be269b8c315b16befc35-p00002` | 43 | 1 | 0.144 | 7 | 0/0 | 25 | 0.024 | 0 | 108 | 0.86 | 0/0 | 0 | 23 | 0 | 0 |
| `s2-d1ed1c2db37f431f4acb-p00001` | 82 | 7 | 0.170 | 18 | 0/5 | 67 | 0.068 | 0 / 43 reviewed | 1483 | 0.02 | 0/0 | 2 | 62 | 1 | 28 |
| `s2-dfcc21869afc140111ce-p00001` | 114 | 5 | 0.114 | 23 | 0/1 | 41 | 0.045 | 0 | 1163 | 0.21 | 0/0 | 0 | 36 | 0 | 2 |
| `s2-f9ec82212abc808325d7-p00010` | 38 | 18 | 0.185 | 6 | 0/0 | 19 | 0.059 | 0 | 102 | 0.11 | 0/0 | 0 | 18 | 0 | 0 |

## What does not work yet

The following case outcomes are incomplete or explicitly deferred:

- Case 1, `an-d6fd2cf2f618-p000047`: Class-conditioned joint fit; median per-line p90 distance in x-heights: baseline 0.080, meanline 0.089, font_top 0.153, font_bottom 0.204. 1403 active lines borrow at least one of these guides. Class assignments remain inferred. Independent font accuracy remains unresolved; the frozen page-level curl maximum regresses to 14.61 px.
- Case 4, `s2-49598b2e848ab1f0ee1e-p00001`: New line 105; bottom margin 1.35 x-heights; source/strip cutoff flag True. Page cutoff count 35.
- Case 5, `an-d6fd2cf2f618-p000047`: No separate active ring-lettering rows (0 candidates); faint ring row(s) [36] discounted. Text continues through the stamp, but 1 body line(s) extend beyond x 1120 ([32]); stamp influence is not fully removed.
- Case 13, `s2-74cdb23a34ca4a6cd01e-p00002`: 8 active lines wider than 800 px in the reviewed corner, starts 29–193; 8 candidates there; page rule mask 0.61%. The last two printed rows are covered by [{'line': 81, 'x': [192, 1653], 'cut': True}, {'line': 82, 'x': [29, 1644], 'cut': True}]; the last region overextends into the left margin. Individual letter recall remains unlabelled.
- Case 14, `s2-3229200bf47ca465a42d-p00004`: 32/32 broad lines now start left of x 170; median start 111 px; page cutoff count 21. Curl-tip completeness is not established by the start coordinate.
- Case 17, `an-3352d912f2e9-p000104`: Former lines 27/28 now match [(26, 221, 1327), (27, 220, 1303)]; printed right end is about x 1290. Cutoff flags [True, True].
- Case 18, `an-3352d912f2e9-p000104`: Open problem, explicitly deferred: the first two body lines start at [(24, 297), (25, 326)]. No claim that the large Ε is assigned correctly.
- Case 21, `an-d6fd2cf2f618-p000047`: Class-conditioned joint fit; median per-line p90 distance in x-heights: accent_bottom 0.131, accent_top 0.228. 1247 active lines borrow at least one of these guides. Class assignments remain inferred.
- Case 25, `an-d6fd2cf2f618-p000047`: 7/7 body lines through the stamp reach x≥1050; right ends [1094, 1094, 1101, 1095, 1178, 1095, 1095]; 5 still carry a cutoff flag.

Tables remain in scope as text pieces; no table structure is inferred. Current table-page diagnostics:

- `an-7a2b17a3fb0f-p000200`: 414 active candidates; 53 cutoff flags, 34 foreign-ink flags, 2 possible broken pairs, 0 detected boundary crossings. Zero crossings does not establish that every cell gap was detected.
- `s2-200e977f2dab5291c42c-p00035`: 268 active candidates; 41 cutoff flags, 38 foreign-ink flags, 1 possible broken pairs, 0 detected boundary crossings. Zero crossings does not establish that every cell gap was detected.
- `s2-831443dc5e6f1ccfbaf5-p00020`: 356 active candidates; 47 cutoff flags, 36 foreign-ink flags, 0 possible broken pairs, 0 detected boundary crossings. Zero crossings does not establish that every cell gap was detected.

The connected-table guard protects repeated text rows, but `an-7a2b17a3fb0f-p000200` still has a falsely excluded large region (x 719–1820, y 398–2113), visibly losing much of the left table. This is not fixed. The all-pairs overlap check passes independently of this missing-text error.

Full-height rule continuation can also split a heading that spans the columns above a table: the heading on `s2-200e977f2dab5291c42c-p00035` and the ΠΙΝΑΞ heading on `an-2cfe28da5103-p000135` remain fragmented. The named ΑΚΟΛΟΥΘΙΑ fix does not establish general heading recall.

Visual boundary failure on `s2-d1ed1c2db37f431f4acb-p00001`: 43 active candidates clearly cross the visible column divider near x 1620, indices [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 41, 43, 44, 52, 53, 54, 58, 59, 81, 84, 87]. No detected boundary protects this divider, so the automatic crossing count is falsely reassuring. Check 6 records the separate evaluation-only review reference and count; it does not alter the detector.

Visual boundary failure on `s2-9de6cda8f03f0fc60a58-p00005`: 37 active candidates clearly cross the visible column divider near x 1683, indices [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 23, 24, 25, 27, 30, 37, 48, 57, 60, 61, 62, 63, 64, 65, 66, 71, 72, 73, 78, 79, 80, 83, 89, 91, 93, 95, 96]. No detected boundary protects this divider, so the automatic crossing count is falsely reassuring. Check 6 records the separate evaluation-only review reference and count; it does not alter the detector.

Visual boundary failure on `s2-7247ee9b1bc2374b3980-p00001`: 14 active candidates clearly cross the visible column divider near x 1741, indices [38, 39, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83]. No detected boundary protects this divider, so the automatic crossing count is falsely reassuring. Check 6 records the separate evaluation-only review reference and count; it does not alter the detector.

On `s2-d1ed1c2db37f431f4acb-p00001`, case 10's faint ghost candidates are discounted but the columns remain joined. The independent saved-file audit also finds a real region overlap between candidates 84 and 87 (116 pixel columns, maximum depth 41.377 px); the zero-overlap requirement is therefore not met on all 48 pages.

- Scan-border check on `an-5c093c79d6bb-p000199`: 13 active candidates end left of x 480, indices [0, 1, 2, 3, 4, 6, 7, 10, 12, 13, 14, 15, 16]. Fold separation and scan-border rejection are distinct checks.
- Scan-border check on `an-9ea1564fcf4f-p000013`: 0 active candidates end left of x 400, indices []. Fold separation and scan-border rejection are distinct checks.

Other limitations: mirrored show-through is not recognised by letter shape; discounting uses relative contrast and body evidence. Dark stamp lettering and small ornaments can still resemble letters. Contrast filtering can leave unassigned faint true marks. Drop capitals are recorded as observed, not solved. Held-out pages were not accessed.

All 48 source/output bindings, per-line guide residuals, discount reasons and checks 1–10 are saved under `.astra/out/`. `cases/cases.json` is the machine-readable case table. The case images show only the new output.

## Validation receipt

Tests: 1262 passed. Hint reruns: 24/24 identical in the renderer's compared geometry arrays. API documentation regenerated (206 public callable entries; generated content unchanged).

Across 48 pages: 3961 active and 484 discounted candidates; 1600 cutoff flags, 1426 foreign-ink flags, 0 automatically detected crossings but 94 clear crossings at the three separately reviewed dividers, 1 overlap pair(s), 7 possible broken pairs, and 437 disagreeing seam pairs. The largest region step is 0.103 x-heights. Seam counts include distant rows with ordinary margins; inspect their recorded magnitudes and locations before treating every gap as a cutoff.

Saved-file audit: 48 pages; 0 pages with missing files, 0 invalid bands, 1 overlapping active pair(s). Every JPEG was decoded and every candidate strip accounted for, including wrapped table stacks. The detector/renderer hash matches the current source. The audit returns failure when overlaps remain.

Independent frozen curl contacts: 83/83 covered, worst baseline error 14.61 px. These contacts test geometry only, not character recall or strip purity. Round 2 reported 10.2 px at crop 23: the new maximum is a regression, despite passing the unchanged crop-tool tests. The page-level joint fit still needs better class and neighbouring-shape constraints.

Git staging was blocked by the sandbox when creating the worktree index lock. No commit was made. The requested fallback is `.astra/page-lines-round3.patch` with `.astra/commit-page-lines-round3.sh`; the script verifies the branch, base revision and file hashes, then commits with both required trailers. Nothing was pushed.
