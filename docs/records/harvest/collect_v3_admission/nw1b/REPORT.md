# NW1b owner calibration and application

No OCR reading, recognizer, network call, payment, masking, PNG deletion, or write/lock in the live run root. Native geometry and the existing foreign-ink ownership measure only. Interpreter: `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.

## Truth and scope

The 22 KEEP labels come verbatim from the NW1b brief. Seven owner issue IDs are explicitly named. The manifest at collect commit `83aaab5d` contains six `merged_multi_line` witnesses; their union with those seven IDs and the other gallery `screen_merged` cards (excluding explicit owner KEEP overrides) contains **ten distinct DROP cards**, including all three-line witnesses. The manifest does not uniquely identify an eighth owner issue: sg1-05 (Gazette l0128) and sg1-06 (Gazette l0146) are both additional merged witnesses; both are included, with neither invented as an owner-labelled eighth.

The gallery also has `screen_merged: true` on half-line examples, including an explicit owner KEEP. Owner labels take precedence. All six full-line merged witnesses and every gallery `screen_merged` witness are measured. The additional flagged half-line witness (sg1-07) is DROP under the explicit request to include every gallery screen_merged card; this uses its screen flag, not checker wording. BORDERLINE is not gating.

The retained matcher uses native body-centre LineFits; foreign ink comes directly from `_foreign_mask` with frozen ownership parameters `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. The NW1 horizontal graph uses positive vertical overlap and the existing recut `GAP_STOP` (3 x-heights). Half-only components at crop boundaries are excluded. NW1b evaluates the **median height of the whole run**, without pre-filtering individual heights. Measurements include every candidate run before admission thresholds.

## Gate

Defaults (4 components, 3 xh width, .6 median height): standalone P=0.714286, R=1.000000; TP=10, FP=4, FN=0, TN=18; union P=0.625000, R=1.000000; TP=10, FP=6, FN=0, TN=16.

Selected {'min_components': 10, 'min_width_xh': 3.0, 'min_height_xh': 0.6}: standalone **P=1.000000, R=1.000000; TP=10, FP=0, FN=0, TN=22**. Standalone gate passes: 0/22 KEEP false drops and 10/10 DROP detections.

Combined with the existing screen_merged flags: P=0.714286, R=1.000000; TP=10, FP=4, FN=0, TN=18. Its four KEEP false drops are already caused by screen_merged. The combined full confusion gate fails; the task is qualified through the passing standalone screen. No claim is made that screen_merged has zero owner false drops.

Every one of the 27 nearby settings fails. Search then expanded on the same positive lattice: 1 component, .5 width xh, .1 height xh. Distance is L1 in those units, with ties resolved by fewer changed thresholds then numeric order. After 228 settings, (10, 3, .6) is the nearest passing lattice setting (distance 6). All lattice settings at smaller distance are covered; settings outside the enumerated positive bounds have distance greater than 6. This is a lattice result, not a claim of a nearest real-valued threshold.

Existing screen_merged KEEP false drops: `gazette_modern--54876940c2de96c3--s000-l0062`, `gazette_modern--836a4d5d06d0f16d--s000-l0045`, `ia_poly1850--36dcee7ce4c29f8b--s004-l0062`, `kosmopolis--109d033afd51aea6--s000-l0019`.

## Every measured card

Run notation is **components / width in x-heights / median height in x-heights**. The table reports every connected candidate run; `none` means none after half-only exclusion. Raw components, half-only flags, crop boxes, x-height, all runs and gallery IDs are in `measurements.jsonl`. Width and median are displayed rounded only; decisions use full precision. All 33 cards matched native lines.

| Row ID | Truth | Measured runs (n / width / median) | NW selected | screen_merged | Union |
|---|---|---|---|---|---|
| `bsb_poly1850--e18cacecef3b4590--s005-l0076` | keep | 3 / 2.965562 / 0.323516; 2 / 2.642046 / 0.485274; 2 / 2.534207 / 0.593112; 1 / 1.132305 / 1.186225; 1 / 0.377435 / 0.539193 | keep | False | keep |
| `bsb_poly1850--e18cacecef3b4590--s007-l0061` | keep | 1 / 0.244973 / 0.551188 | keep | False | keep |
| `gazette_modern--0020420cfe156a73--s000-l0039` | drop | 34 / 40.235505 / 1.023604; 31 / 34.566315 / 1.023604; 1 / 0.472433 / 0.236216; 1 / 0.314955 / 0.393694; 1 / 0.314955 / 0.629910 | drop | False | drop |
| `gazette_modern--0020420cfe156a73--s000-l0138` | drop | 30 / 27.592074 / 0.935325; 29 / 38.971856 / 1.091212; 1 / 0.389719 / 0.623550; 1 / 0.311775 / 0.155887 | drop | True | drop |
| `gazette_modern--0020420cfe156a73--s000-l0141` | drop | 30 / 27.592074 / 0.935325; 29 / 38.971856 / 1.091212; 1 / 0.389719 / 0.623550; 1 / 0.311775 / 0.155887 | drop | True | drop |
| `gazette_modern--0020420cfe156a73--s000-l0146` | drop | 35 / 42.743400 / 1.012139; 21 / 28.262029 / 1.012139; 1 / 0.467141 / 0.622855; 1 / 0.389284 / 0.622855; 1 / 0.389284 / 0.622855 | drop | False | drop |
| `gazette_modern--0020420cfe156a73--s000-l0162` | drop | 31 / 40.339715 / 1.010436; 17 / 23.861835 / 1.088162; 1 / 0.777258 / 1.088162; 1 / 0.310903 / 0.466355 | drop | False | drop |
| `gazette_modern--0020420cfe156a73--s000-l0228` | drop | 26 / 43.168985 / 1.255474 | drop | False | drop |
| `gazette_modern--0d0b2233a81e355c--s000-l0019` | keep | 1 / 0.327981 / 0.409976; 1 / 0.163990 / 0.163990 | keep | False | keep |
| `gazette_modern--1f7db88d63c02afa--s000-l0287` | drop | 15 / 48.653336 / 1.010978; 14 / 34.373266 / 0.947792; 8 / 7.076849 / 0.189558; 6 / 34.120521 / 0.821420; 5 / 15.543793 / 1.010978; 1 / 5.307637 / 0.631862; 1 / 0.505489 / 0.252745; 1 / 0.252745 / 0.126372 | drop | True | drop |
| `gazette_modern--4b5e54c14bfb5810--s000-l0031` | keep | 1 / 0.493030 / 0.493030; 1 / 0.328687 / 0.328687; 1 / 0.164343 / 0.246515 | keep | False | keep |
| `gazette_modern--54876940c2de96c3--s000-l0062` | keep | 3 / 4.510030 / 0.410003; 1 / 0.328002 / 0.410003; 1 / 0.328002 / 0.410003; 1 / 0.328002 / 0.328002; 1 / 0.246002 / 0.410003; 1 / 0.246002 / 0.492003; 1 / 0.082001 / 0.082001 | keep | True | drop |
| `gazette_modern--5af16c5d518d2ebb--s000-l0059` | keep | none | keep | False | keep |
| `gazette_modern--5af16c5d518d2ebb--s000-l0128` | drop | 44 / 41.787411 / 0.789588 | drop | True | drop |
| `gazette_modern--5af16c5d518d2ebb--s000-l0131` | keep | 1 / 0.598577 / 0.266034; 1 / 0.332543 / 0.332543 | keep | False | keep |
| `gazette_modern--7f0595fd3a453e0b--s000-l0025` | keep | 8 / 12.424271 / 0.771922; 8 / 8.601418 / 1.102746; 1 / 0.588131 / 0.220549; 1 / 0.441098 / 1.029230; 1 / 0.441098 / 1.029230; 1 / 0.220549 / 0.441098 | keep | False | keep |
| `gazette_modern--836a4d5d06d0f16d--s000-l0045` | keep | 4 / 5.793495 / 0.601922; 2 / 1.881005 / 0.451441; 1 / 0.451441 / 0.451441; 1 / 0.451441 / 0.451441; 1 / 0.376201 / 0.451441; 1 / 0.376201 / 0.601922; 1 / 0.225721 / 0.526681 | keep | True | drop |
| `gazette_modern--f375bcf80bc8fca3--s000-l0025` | keep | 8 / 11.010636 / 0.873257; 8 / 8.049155 / 0.721387; 3 / 4.859867 / 0.683419; 1 / 0.455613 / 0.607483 | keep | False | keep |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0032` | borderline | 6 / 10.092805 / 0.604877; 5 / 3.698391 / 0.933239; 3 / 5.703126 / 0.449337; 3 / 3.041667 / 0.725852; 2 / 3.491005 / 0.656724; 2 / 2.350379 / 0.483902; 2 / 1.970171 / 0.518466; 2 / 1.728220 / 0.483902; 2 / 1.278883 / 0.449337; 1 / 0.414773 / 0.414773; 1 / 0.380208 / 0.449337 | keep | False | keep |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0062` | keep | 1 / 0.721644 / 0.811850; 1 / 0.586336 / 0.541233; 1 / 0.405925 / 0.405925; 1 / 0.360822 / 0.225514; 1 / 0.360822 / 0.360822 | keep | True | drop |
| `ia_poly1850--63f57af8d450f3e8--s003-l0021` | keep | 1 / 0.487465 / 0.522284; 1 / 0.383008 / 0.452646; 1 / 0.348189 / 0.278552; 1 / 0.348189 / 0.452646; 1 / 0.348189 / 0.452646; 1 / 0.313370 / 0.348189 | keep | False | keep |
| `ia_poly1850--c39403323b6d5d89--s005-l0007` | keep | 1 / 0.343698 / 0.294599; 1 / 0.294599 / 0.294599 | keep | False | keep |
| `ia_poly1850--c39403323b6d5d89--s005-l0031` | keep | 1 / 0.400000 / 0.450000; 1 / 0.350000 / 0.200000; 1 / 0.300000 / 0.300000; 1 / 0.300000 / 0.300000; 1 / 0.050000 / 0.050000 | keep | False | keep |
| `ia_poly1850--f806d3f10b2ecf9c--s003-l0050` | keep | 3 / 1.191103 / 0.220575; 1 / 0.441149 / 0.308804; 1 / 0.352919 / 0.308804 | keep | False | keep |
| `ia_russian--61f76a57b26f9b13--s004-l0002` | keep | none | keep | False | keep |
| `ia_russian--6cfc00f06e0f7241--s007-l0003` | keep | none | keep | False | keep |
| `kosmopolis--109d033afd51aea6--s000-l0019` | keep | 9 / 10.065904 / 0.649413; 4 / 2.516476 / 0.324707; 3 / 6.737662 / 0.405883; 1 / 0.568237 / 0.324707; 1 / 0.405883 / 0.324707; 1 / 0.405883 / 0.568237 | keep | True | drop |
| `kosmopolis--62ca52b56ebe780a--s005-l0028` | keep | 1 / 0.090546 / 0.090546 | keep | False | keep |
| `kosmopolis--62ca52b56ebe780a--s005-l0051` | drop | 13 / 26.428100 / 0.905072; 8 / 14.028615 / 0.633550; 4 / 9.593762 / 0.497790; 1 / 3.258259 / 0.814565; 1 / 0.814565 / 0.271522; 1 / 0.452536 / 0.452536; 1 / 0.452536 / 0.452536; 1 / 0.362029 / 0.543043; 1 / 0.271522 / 0.090507; 1 / 0.090507 / 0.090507 | drop | True | drop |
| `kosmopolis--ecc23d7812913d0a--s005-l0011` | keep | 1 / 0.846154 / 0.923077; 1 / 0.461538 / 0.538462; 1 / 0.461538 / 0.538462; 1 / 0.307692 / 0.538462 | keep | False | keep |
| `nlg--1144074169f43992--s006-l0032` | keep | 1 / 0.233449 / 0.058362 | keep | False | keep |
| `nlg--3d6bd7bd688acb61--s006-l0005` | keep | none | keep | False | keep |
| `nlg--6146c0455e0103d2--s001-l0006` | drop | 18 / 17.211629 / 0.819601; 10 / 10.163057 / 0.601041; 3 / 4.589768 / 0.327841; 3 / 3.442326 / 0.601041; 1 / 0.273200 / 0.437121 | drop | True | drop |

Full-line merged subset: neighbour_words 6/6; existing screen_merged 2/6; union 6/6. The gallery flags do not support the assertion that screen_merged already drops every merged card.

BORDERLINE is **keep** at the selected setting. Its largest run is 6 components / 10.092805 xh width / .604877 xh median height; another run is 5 / 3.698391 / .933239. Defaults would drop it. It does not affect threshold selection.

## Nearby grid

| Components | Width xh | Median xh | NW FP/22 | NW TP/10 | NW P | NW R | Union FP/22 | Union TP/10 | Union P | Union R |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 2.5 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 2.5 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 2.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.0 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.0 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.0 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.5 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.5 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 3 | 3.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 2.5 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 2.5 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 2.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.0 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.0 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.0 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.5 | 0.5 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.5 | 0.6 | 4 | 10 | 0.714286 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 4 | 3.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 2.5 | 0.5 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 2.5 | 0.6 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 2.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.0 | 0.5 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.0 | 0.6 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.0 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.5 | 0.5 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.5 | 0.6 | 3 | 10 | 0.769231 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |
| 5 | 3.5 | 0.7 | 2 | 10 | 0.833333 | 1.000000 | 6 | 10 | 0.625000 | 1.000000 |

## W1 application

Application pending; published admission and crop manifests remain unchanged.

## Review of NW1 and ADM5b dependencies

Kept the frozen ownership adapter, page image hash checks, page-grouped cache, matcher, pure admission decision wiring, receipt provenance, ID-row CLI support, source verification and non-deleting crop retention. Corrected individual-height filtering to whole-run median, corrected component-native-label selection to use the current connected label, replaced the checker-derived C1 calibration with owner truth, and recalibrated CLI defaults. Old NW1 calibration/reissue entry points now refuse to run because their truth is superseded. Their old files and partial cache remain historical and excluded from the new commit list, except the two disabled entry points.

`tests/test_adm5b_schema.py` and `greekocr/_vendor/codec/v2.json` are included in the guarded commit list. ADM5b needs the vendored v2 inventory because `load_codec()` defaults to it; its exact SHA-256 is tested. Neither requested file is ignored (`git check-ignore --no-index` returns 1). No ignore exception was needed. NW1/NW1b derived caches are ignored, and staged PNGs remain ignored by the existing crop directory rule. The schema test now recognizes the NW1b receipt version and its four existing neighbour provenance fields. The untracked ADM5c variant tests are retained in the list as relevant regression coverage; unrelated census outputs and other worktree changes are excluded.

The guarded list binds reviewed paths, SHA-256, branch, HEAD and an empty index. Its guard is read-only. No staging or commit was attempted.
