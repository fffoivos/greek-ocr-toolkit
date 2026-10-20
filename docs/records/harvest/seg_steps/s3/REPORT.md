# SEG step 3 — 0.9-s3

Main-row TEXT_ROLES ink is measured in the existing detector base curve’s arc-length/normal frame. Detector geometry and decisions, inventory, gate, predictor, length interval, padding formula and the S2 clockwise turn are unchanged. No fit, smoothing, tunable parameter, guard or decision threshold was added. All curvature and foot-ambiguity counts are diagnostics.

## Geometry and exact straight identity

`text_lines` supplies a per-x `base` array (the main band bottom); `skew_line` references that same array. The representation is not only an angle: it can contain the existing quadratic or locally tracked piecewise-linear bend. S3 joins successive supplied column samples as segments, projects each selected ink pixel centre onto every segment, and chooses its nearest foot. Cumulative segment lengths give s; signed nearest distance gives n (positive below the base). Equal-distance distinct feet select the first in curve order; shared vertices are one foot. The stored per-column domain is finite [0, width−1], with no new extrapolation.

Each centre contributes the same 0.6 unit pixel-cell projected half extent, (|tangent.x|+|tangent.y|)/2, to each coordinate at its selected segment. The extrema of these cells give the s and n extents. Existing TEXT_ROLES selection is retained exactly; no component is reassigned or newly filtered. The upright box remains the padding envelope. Rule 2 receives the new extents through the unchanged max/min predictor call; rule 3 divides its unchanged padding numerator by the n extent.

The detector now exposes only its existing construction provenance as Band.curve_is_straight. Actual straight/constant constructions use the original tight_box rotation and its original operation order; every tracked polyline uses its supplied samples even if the existing approximate degree flag is 1. No numerical tolerance is accepted. The preflight independently compared complete feature objects before the S3 replay; the replay/readback then compared canonical evidence bytes, result, frame, warnings, long side, short side, ratio and padding. Only the required tool_version differs. **1184/1184 straight rows match S2 exactly.** Degree 1 in the detector can in principle mean approximately straight. S3 uses the actual construction provenance without fitting another curve. Construction metadata agrees with the degree flags on all 1,288 replay rows; a synthetic tracked degree-1 curve is explicitly tested in both horizontal and turned frames.

## Replay and unchanged scoring

The same S1 input builder, native adapter workflow, source-context selection, frozen predictor and 120-second per-row bound are reused. Fresh native S2 matches all 1,288 saved S2 records before any S3 replay. The 150 use the full saved reader answers and gate2 owner_state (positive faults win over unknowns); FP is DROP/fine, FN is KEEP/faulty, UNC is every UNCERTAIN. No reader ran. The 888 use only owner_rating.decision on the same 135 rated rows. Cells have no inferred labels. The 240 explicit mark entries yield 235 IDs, scored once with latest timestamp then file order winning.

0.8 retains the saved S1 native baseline, including its historical 18/14/11 full-population score.

| Metric | 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 |
| --- | --- | --- | --- | --- |
| 150 FP/FN/UNC | 18/14/11 | 17/14/11 | 17/14/5 | 17/15/5 |
| 888 rated agreement /135 | 94 | 95 | 105 | 105 |
| Owner marks agreement /235 | 155 | 156 | 169 | 170 |

| Set | Rows | Straight | Curved | S2 → S3 transitions |
| --- | --- | --- | --- | --- |
| segeval1 | 150 | 132 | 18 | {'KEEP->KEEP': 112, 'DROP->DROP': 32, 'UNCERTAIN->UNCERTAIN': 5, 'DROP->KEEP': 1} |
| calibration | 888 | 806 | 82 | {'KEEP->KEEP': 772, 'UNCERTAIN->UNCERTAIN': 11, 'DROP->DROP': 104, 'KEEP->DROP': 1} |
| cells | 250 | 246 | 4 | {'KEEP->KEEP': 212, 'UNCERTAIN->UNCERTAIN': 30, 'DROP->DROP': 8} |

### 08 confusion readback

| 150 verdict | fine | faulty | unresolved |
| --- | --- | --- | --- |
| KEEP | 97 | 14 | 0 |
| DROP | 18 | 10 | 0 |
| UNCERTAIN | 3 | 6 | 2 |

| 888 verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 50 | 4 |
| DROP | 22 | 44 |
| UNCERTAIN | 6 | 9 |

| Marked verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 141 | 7 |
| DROP | 26 | 14 |
| UNCERTAIN | 34 | 13 |

### s1 confusion readback

| 150 verdict | fine | faulty | unresolved |
| --- | --- | --- | --- |
| KEEP | 98 | 14 | 0 |
| DROP | 17 | 10 | 0 |
| UNCERTAIN | 3 | 6 | 2 |

| 888 verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 51 | 4 |
| DROP | 21 | 44 |
| UNCERTAIN | 6 | 9 |

| Marked verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 142 | 7 |
| DROP | 25 | 14 |
| UNCERTAIN | 34 | 13 |

### s2 confusion readback

| 150 verdict | fine | faulty | unresolved |
| --- | --- | --- | --- |
| KEEP | 98 | 14 | 0 |
| DROP | 17 | 16 | 0 |
| UNCERTAIN | 3 | 0 | 2 |

| 888 verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 54 | 5 |
| DROP | 21 | 51 |
| UNCERTAIN | 3 | 1 |

| Marked verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 150 | 10 |
| DROP | 29 | 19 |
| UNCERTAIN | 22 | 5 |

### s3 confusion readback

| 150 verdict | fine | faulty | unresolved |
| --- | --- | --- | --- |
| KEEP | 98 | 15 | 0 |
| DROP | 17 | 15 | 0 |
| UNCERTAIN | 3 | 0 | 2 |

| 888 verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 54 | 5 |
| DROP | 21 | 51 |
| UNCERTAIN | 3 | 1 |

| Marked verdict | owner KEEP | owner DROP |
| --- | --- | --- |
| KEEP | 151 | 10 |
| DROP | 28 | 19 |
| UNCERTAIN | 22 | 5 |

## Owner-KEEP witness l0037

`ia_poly1850--df8f2267db2b7275--s025-l0037` — the owner mark is KEEP. No witness-specific rule or repair was applied.

| Version | Long side | Short side | Ratio | Padding | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0.9-s2 | 1310.0513843951387 | 92.04469555045573 | 1.5024007041150793 | 0.043457148465522795 | DROP |
| 0.9-s3 | 1334.5220414662963 | 82.94480889936673 | 1.3391192498745175 | 0.048224838336212494 | KEEP |

Supported base range: 41.450556344836045 px; maximum perpendicular chord deviation: 37.26369867867917 px. The historical 41 px sag / 92 px box / 57 px line observation is owner context; the table contains fresh native measurements. The detector baseline contains local bends visible in red, and S3 preserves them exactly. Its 82.94 px n extent is not asserted to recover the observed 57 px line. The saved historical 150 owner-standard label is faulty while the explicit owner mark is KEEP: this flip increases historical FN by one and explicit marked agreement by one.

![Witness base, old box and unrolled box](overlays/ia_poly1850--df8f2267db2b7275--s025-l0037.png)

[Exact witness measurements](witness.json), [full baseline and boxes](witness_geometry.json).

## Curvature diagnostic

Per-row chord deviation is the largest absolute perpendicular distance between the supplied baseline and its endpoint chord over the unchanged main-row support [x0,x1]. Every replay row is in [curvature.jsonl](curvature.jsonl), including blocked gates and the exact measurement changes. No deviation threshold affects a verdict. Counts refer to cohort records; overlapping IDs are separately counted in the summary.

| Percentile | All rows, px | Detector-curved rows, px |
| --- | --- | --- |
| 0 | 0.0 | 0.21251833549220453 |
| 25 | 3.552354603562183e-15 | 1.7407496020321895 |
| 50 | 3.5527107172860274e-15 | 2.5276153572140454 |
| 75 | 7.105411114797582e-15 | 3.461686149099485 |
| 90 | 1.4210838641760123e-14 | 7.2408316941317095 |
| 95 | 1.9981180513729073 | 11.21779338294067 |
| 99 | 6.205959640315965 | 36.777299509421866 |
| 100 | 91.2657955360527 | 91.2657955360527 |

Detector degrees: {'2': 104, '1': 1113, '0': 71}. Curved measurement changes: 94 records / 94 unique IDs. Ambiguous foot pixels: 0. Gate-blocked rows retain unavailable Stage-B measurement; their geometric deviations are still recorded.

### Every changed measurement

Deltas are S3 − S2.

| Set | ID | Chord deviation px | Δ long | Δ short | Δ ratio | Δ padding |
| --- | --- | --- | --- | --- | --- | --- |
| segeval1 | bsb_poly1850--b948a3efe20973e7--s003-l0031 | 1.9787746223512146 | 0.283560999304882 | 0.3205270722135367 | 0.00679271056999009 | -0.0003948234835453174 |
| segeval1 | gazette_modern--9701a3a500ecbd85--s000-l0139 | 2.008533743923056 | 0.4357764245546605 | -1.3396078570690158 | -0.05064582799130335 | 0.013052297402142254 |
| segeval1 | ia_greek_latin--a232aaf9a41fe898--s003-l0031 | 5.597133704300793 | 0.01846368131714371 | -3.2973635690252934 | -0.046549124663791464 | 0.007432137119288779 |
| segeval1 | gazette_modern--6efb0af18300ce89--s000-l0085 | 2.933913264520847 | 0.3187134902212847 | -0.34710218183861485 | -0.01300670429569295 | 0.0 |
| segeval1 | gazette_modern--6f46fd6e4c22cb5c--s000-l0046 | 3.4207533362417446 | -0.13256358673424984 | 1.2848636668446076 | 0.04000038028479325 | -0.0017952454429205345 |
| segeval1 | gazette_modern--80e8a42cbf8e629f--s000-l0091 | 1.8471449843508583 | 0.15477136175854866 | -0.9247573579465325 | -0.028324212036541563 | 0.0073880346674723985 |
| segeval1 | gazette_modern--9aa01acfc4b8b0a7--s000-l0100 | 5.471206287401872 | -0.5948179131625011 | 1.7987936149850867 | 0.057277459332900404 | 0.0 |
| segeval1 | gazette_modern--f70d3880d50f1644--s000-l0042 | 3.3487950491231193 | -0.20119999413816458 | 0.9247281749535716 | 0.02833829002392063 | -0.004962326166974701 |
| segeval1 | ia_poly1850--bd7bfada1d31d9e4--s017-l0021 | 2.8060622823494135 | -0.49779296160318154 | 2.4674639238414997 | 0.03940377321426447 | -0.0024368369947763424 |
| segeval1 | ia_poly1850--c3f3a531e277da9a--s027-l0018 | 3.0071416937066275 | 0.3248152024245883 | 0.20762451041223073 | 0.0026545887137925384 | -0.00041962724831698384 |
| segeval1 | ia_poly1850--df8f2267db2b7275--s025-l0037 | 37.26369867867917 | 24.470657071157575 | -9.099886651088994 | -0.16328145424056184 | 0.0047676898706896995 |
| segeval1 | be486d8c-p000025-l0044 | 3.3805387729645906 | 0.47571633648885836 | -0.8460723218941482 | -0.014978925271025734 | 0.001526014251662211 |
| segeval1 | 32aae9fec147d3b483deb96e-p000052-l0057 | 1.8672953091512252 | 0.0011234708324536768 | -1.0842726166982537 | -0.03180600700044067 | 0.0 |
| segeval1 | 5a69150abb15eb1006f5a3ba-p000152-l0026 | 6.435054777031299 | -0.6809451102910771 | -0.13395254927318234 | -0.003480858998864411 | 0.0007880320524850104 |
| segeval1 | 7c411292-p000031-l0062 | 2.8842785435091076 | 0.43681713591740845 | -2.055661434492123 | -0.022540090281073955 | 0.0027868626390759044 |
| segeval1 | 7cb612112b4f28a4f704a9cb-p000081-l0054 | 2.991867802193243 | 0.35354973930213873 | -2.226351421324985 | -0.06775611298310247 | 0.012276536613485128 |
| segeval1 | 827d2345ad77e5cdec320e80-p000059-l0014 | 7.293522961817781 | 1.6425830353880428 | -1.9252641678352589 | -0.05419211749127806 | 0.011461710227089528 |
| calibration | gazette_modern--9aa6f70b8b633618--s000-l0030 | 5.3070880707268095 | -1.0664994909286634 | 5.048010247788881 | 0.1539120797072706 | -0.008208793243396698 |
| calibration | gazette_modern--9aa6f70b8b633618--s000-l0022 | 5.281503120794798 | 0.17190916478864438 | 3.2761069085904424 | 0.09835782643607627 | 0.0 |
| calibration | ia_greek_latin--6886a59734933bc1--s005-l0020 | 21.050393036769627 | 7.760608206190454 | 4.155537970078797 | 0.06748094463865484 | -0.004553692209900567 |
| calibration | ia_poly1850--46ab3c0b8fc0ae1a--s004-l0022 | 1.4318515412259294 | -0.5834055405662184 | -0.8726032714263638 | -0.013647160213930976 | 0.0021442901985124496 |
| calibration | ia_poly1850--46ab3c0b8fc0ae1a--s004-l0021 | 2.5285217610355883 | -0.3747430507376066 | -1.1478586074424797 | -0.016694270034610437 | 0.0016261421812520105 |
| calibration | ia_russian--06528548147a3a3d--s005-l0031 | 3.584484587672706 | -0.5333942532422498 | 0.742979186581735 | 0.008138735397299257 | -0.00019042137236955498 |
| calibration | bsb_poly1850--b948a3efe20973e7--s001-l0018 | 1.8759253191585334 | 0.45003132228816867 | 1.0136123046917902 | 0.023757519430014584 | -0.004341358312365873 |
| calibration | ia_greek_latin--d15eca050847acdb--s001-l0030 | 1.8144352354162312 | -0.39870491920589757 | 1.3406826829561354 | 0.027767114706665152 | -0.005191492241121143 |
| calibration | ia_poly1850--ebcfd6056abfa776--s029-l0073 | 2.9618430626248466 | -0.36341104391692625 | 1.854188582343248 | 0.028345796304041104 | -0.006341240419880018 |
| calibration | bsb_poly1850--9f1e10e4cc7f1532--s005-l0014 | 2.0699665293806944 | -0.5105302922297597 | -0.7317952523335407 | -0.018087804010813557 | 0.004654455854788714 |
| calibration | gazette_modern--2e558566e47e6fd8--s000-l0082 | 2.3761683528663893 | 0.7022341335989495 | 0.5760634618946838 | 0.018645124148037873 | -0.0038806418813988053 |
| calibration | gazette_modern--2e558566e47e6fd8--s000-l0043 | 4.436101829777384 | 0.0570435309369941 | 2.7848681821583234 | 0.09638026470252292 | -0.016240769977964642 |
| calibration | ia_greek_latin--f42ec9d8d21af31b--s000-l0038 | 2.710533986072447 | 0.4944557054228653 | 1.0127024529035467 | 0.024321056661207763 | -0.007502751508849548 |
| calibration | ia_poly1850--4ab77886725d9e1e--s008-l0041 | 9.475616951216614 | -1.7567993108432347 | 5.2910739534814795 | 0.12671118908436596 | 0.0 |
| calibration | ia_poly1850--4ab77886725d9e1e--s036-l0042 | 2.119849878165741 | 0.392393137707586 | -1.1361203357857974 | -0.022144889549056135 | 0.002214969076818188 |
| calibration | serbia--1bf6b218b99d4dbb--s001-l0027 | 5.510877301959868 | 0.19298895422036821 | 0.45709981957123347 | 0.011831407539412142 | -0.002861544706050795 |
| calibration | bsb_poly1850--0ab5fcea9a6fd52e--s000-l0005 | 1.6487456899260466 | -0.04086852083082704 | -0.7135611954720673 | -0.01563382779157274 | 0.0025723257599900295 |
| calibration | elstat--996d9f614c928993--s001-l0047 | 1.680256139799407 | -0.004493109144732443 | 0.18212350118407272 | 0.005176488512364186 | 0.0 |
| calibration | ia_greek_latin--a8c58d8eb21f93c8--s003-l0025 | 2.6593298170288033 | -0.07575013735822722 | 2.0256328539651065 | 0.026717523043671365 | -0.001960637866347162 |
| calibration | serbia--e7b131c2df11f090--s006-l0003 | 1.704455556455299 | -0.09958294048357175 | -0.5680128336697337 | -0.01815031637553144 | 0.0 |
| calibration | ia_greek_latin--4c566bb4c3c16e52--s003-l0017 | 1.7418828466336578 | -0.29434913054399203 | -0.2430175167220483 | -0.0041495003262570496 | 0.00046686391275241323 |
| calibration | bsb_poly1850--2fdb06c3a8566781--s005-l0042 | 1.9517116728669406 | 0.47616358628283706 | -0.8679183773852372 | -0.022023706950821675 | 0.0030973045941406485 |
| calibration | bsb_poly1850--2fdb06c3a8566781--s007-l0043 | 0.9784699914293267 | -0.1982523189851122 | -0.5505008189886595 | -0.013468386199819826 | 0.0024731386935291644 |
| calibration | bsb_poly1850--1c417ec1fdb5d021--s003-l0027 | 3.17286480982758 | -0.29612780706020203 | 1.6342765186787602 | 0.03564436713032215 | -0.0013298520525823754 |
| calibration | elstat--88112979c8a843cb--s000-l0101 | 1.3870462586415464 | 1.5903698276176925 | 0.6235419310138735 | 0.013394432830944436 | -0.010893915875990257 |
| calibration | gazette_modern--373df37127d6baab--s000-l0093 | 1.7535757679524635 | 0.3087818270249727 | -0.8761614550399237 | -0.034643549574970844 | 0.0033506873295781336 |
| calibration | gazette_modern--373df37127d6baab--s000-l0025 | 2.1961193814621125 | -0.2589295080517786 | 0.8616834943835734 | 0.031096926141612302 | -0.0020204281283040526 |
| calibration | serbia--6b577f99816f3331--s008-l0027 | 2.9558465587432696 | 0.45180978124585636 | -1.9419078851308065 | -0.06227855689329653 | 0.026806889405993628 |
| calibration | elstat--0877c813a8512b56--s001-l0038 | 1.13974180232921 | 1.5482658472824369 | -0.4177007326684681 | -0.031646547854229046 | 0.003923000378557001 |
| calibration | gazette_modern--a6017e7aff42d648--s000-l0109 | 3.1899369499610235 | -0.27157560453747465 | -0.7013964872366643 | -0.023460247361211994 | 0.0025545485161067027 |
| calibration | ia_greek_latin--202a95a447dece04--s000-l0020 | 1.1839465490012144 | 0.0017185914572337424 | -1.3010549866974088 | -0.03182269563322648 | 0.006185936510515189 |
| calibration | ia_poly1850--3bfe0ab3a504d025--s014-l0008 | 1.331385846332892 | -0.5092623113901027 | -0.7492165814792315 | -0.012290240977494093 | 0.003057085800524051 |
| calibration | ia_poly1850--3bfe0ab3a504d025--s013-l0010 | 1.7373498682277844 | -0.501311475447892 | -0.33469972879996845 | -0.007282661986306893 | 0.001934344015255135 |
| calibration | ia_poly1850--3bfe0ab3a504d025--s037-l0001 | 2.9844912154030716 | 0.06709331775471128 | 1.3993604992198527 | 0.02067148031779864 | -0.0072548222132517715 |
| calibration | ia_poly1850--09f9190274fc82bd--s011-l0017 | 2.222942422698628 | -0.3217890402077046 | 0.9255719118426384 | 0.013687131125933671 | 0.0 |
| calibration | ia_poly1850--09f9190274fc82bd--s013-l0028 | 1.3921817020664173 | -0.3279903360139542 | 0.28881071199904085 | 0.004309031134201224 | -0.00041746113868322554 |
| calibration | ia_poly1850--09f9190274fc82bd--s011-l0025 | 2.604640773828355 | -0.4495549562036558 | -0.9189027500534763 | -0.013361246116066816 | 0.0 |
| calibration | ia_poly1850--09f9190274fc82bd--s013-l0014 | 3.2577092421451335 | -0.5846800842898574 | 0.39529849766938696 | 0.0061611985771534705 | 0.0 |
| calibration | ia_poly1850--09f9190274fc82bd--s037-l0012 | 3.298031979524189 | 0.45693165843772476 | -2.4391939463857355 | -0.03443483636428213 | 0.005762793526906923 |
| calibration | gazette_modern--5d71db439801932b--s000-l0086 | 2.1679293550969474 | -0.43979464838196236 | 0.8480452433894001 | 0.030655526639564945 | -0.0031099908217521177 |
| calibration | bsb_poly1850--9342f9a56a4065cd--s003-l0007 | 3.0232890462887965 | -0.2291974946267601 | 0.6397861830229701 | 0.013607298972398096 | -0.000725661988190629 |
| calibration | gazette_modern--87da5b7ac6461e37--s000-l0045 | 1.842556797400831 | 0.22734593402674363 | 0.6709363951679208 | 0.020937087566544 | -0.006165892553290475 |
| calibration | ia_greek_latin--d94cfff6c5bd6428--s004-l0037 | 18.95703382387393 | -7.798144890407912 | 17.183110344421607 | 0.32567414519099636 | -0.01391418062398983 |
| calibration | ia_greek_latin--d94cfff6c5bd6428--s001-l0022 | 3.2975094255540944 | -1.1513656024432066 | -1.8341660997121778 | -0.03185306310074987 | 0.0018308789124716757 |
| calibration | ia_poly1850--41e90f3ba967f920--s038-l0004 | 2.3944897269714867 | 0.6325178009456067 | 1.7216859692744606 | 0.02775242217401286 | -0.00347404277059446 |
| calibration | ia_poly1850--41e90f3ba967f920--s003-l0005 | 3.805710898346502 | -0.5317145757940125 | -0.5896533793523417 | -0.007862742398584754 | 0.0008525132211924941 |
| calibration | ia_russian--d558bd3e803e7865--s003-l0012 | 1.7971187995988724 | -0.10136185487704097 | -1.4923419882551912 | -0.01683124522780033 | 0.001080078727300808 |
| calibration | ia_russian--d558bd3e803e7865--s002-l0004 | 7.8153957338068 | -0.5088222946080805 | -0.7482229706891133 | -0.0077334699801199225 | 0.0008306024548172114 |
| calibration | bsb_poly1850--fe51c7e60c92453d--s022-l0033 | 2.991382084083532 | 0.4099525242745585 | -1.5020135186381154 | -0.027612900140832508 | 0.003496850383154157 |
| calibration | bsb_poly1850--fe51c7e60c92453d--s024-l0035 | 2.76356145038801 | -0.2942123611195484 | 0.07480610996814363 | 0.0018821054195277132 | -0.00027000056551759744 |
| calibration | elstat--2983ce8660f4b1e0--s001-l0308 | 1.7448699091915838 | -1.499785843034914 | 1.3422079271170375 | 0.05780666888402286 | -0.015777746484406607 |
| calibration | bsb_poly1850--78e60e644817036d--s001-l0011 | 1.4391389648741546 | -0.5231207546660244 | -0.053220468269053356 | -0.0006006447840937179 | 0.0001817869324824417 |
| calibration | ia_poly1850--29e9490734cc1653--s026-l0003 | 1.6729818454773915 | 0.0026434763337874756 | -0.32419369534243003 | -0.007278219094568383 | 0.0007789060285064014 |
| calibration | bsb_poly1850--a87b687458352fcb--s019-l0020 | 2.179954554611903 | -0.0735222195288543 | 0.1455267787939576 | 0.003283493575621299 | -0.0008418146533538673 |
| calibration | elstat--5f85f8679b2fe3c7--s000-l0215 | 0.8580888254032544 | 0.0966113129144901 | -0.2319639583649291 | -0.008586600552705992 | 0.0037047017602285237 |
| calibration | elstat--5f85f8679b2fe3c7--s000-l0262 | 1.300556183555963 | 0.38786066766090244 | -0.436969449039303 | -0.016753664453955763 | 0.005608235468915479 |
| calibration | elstat--5f85f8679b2fe3c7--s000-l0204 | 0.7681971698063991 | 0.6234520413549376 | 0.6720402661823321 | 0.01996951496519417 | -0.0069369766274701705 |
| calibration | gazette_modern--83c3182a4175392a--s000-l0311 | 2.010234905523103 | -1.4827964632240196 | 1.4888868562355029 | 0.028762110941318753 | -0.0022052230325513567 |
| calibration | gazette_modern--e418f19baeb555e0--s000-l0026 | 2.516986178071506 | -0.08914639543513658 | -0.2337443338051628 | -0.0007501935692408174 | 0.002676932037665558 |
| calibration | ia_greek_latin--d53eaf7b3036014c--s004-l0001 | 1.9349376750873861 | -0.4362419066067105 | 3.4344843049000247 | 0.03299042981291095 | -1.0383005900825388 |
| calibration | ia_greek_latin--e02bf39b0ef9974e--s007-l0001 | 1.6587222775661261 | -0.2257794515301157 | 0.7818778956954588 | 0.006780611260426894 | -0.0030749481597305284 |
| calibration | ia_poly1850--63f57af8d450f3e8--s009-l0033 | 2.993573965489691 | -0.2910624145024485 | 0.6368332546625766 | 0.001750825994817351 | -0.0005736495330692787 |
| calibration | ia_poly1850--c3f3a531e277da9a--s014-l0019 | 7.117885402864206 | -0.14470489022937727 | -2.4250593983660664 | -0.053214230177634825 | 0.003554606103755492 |
| calibration | ia_russian--61f76a57b26f9b13--s001-l0005 | 91.2657955360527 | 145.17840147825336 | 8.229860471026157 | 0.004303809740520581 | 0.0 |
| calibration | ia_russian--6cfc00f06e0f7241--s003-l0003 | 2.177914528053177 | -0.09398293194556118 | -1.76968836360696 | -0.016647611762310888 | 0.009149429980525758 |
| calibration | lekythos--3bfc4a385d61b883--s002-l0046 | 2.5267089533925025 | -0.6208354375601175 | -2.9220906099578627 | -0.08026541985180347 | 0.02289060251666994 |
| calibration | nlg--f4b52df5f8130047--s034-l0008 | 5.2040027701869995 | -2.0042326222949214 | -1.0906917061635966 | -0.00416332862753066 | 0.0039034960003359598 |
| calibration | bsb_poly1850--767e91eee85d9120--s002-l0001 | 2.634509978247534 | -1.927967033182 | -2.4558639760057837 | -0.060158297956763085 | 0.013773137865880775 |
| calibration | ia_greek_latin--21e262e35c91b839--s004-l0034 | 4.312613797213927 | 3.021070402047883 | 1.538058625392047 | 0.025154111900624665 | -0.006748450784916482 |
| calibration | ia_russian--03b43bc5289ad8ce--s005-l0011 | 10.892189779617125 | -1.7950947698029722 | -0.14848959323681044 | -0.0014163213857703028 | 0.00040755858048277527 |
| calibration | elstat--b22485837ca574d8--s001-l0160 | 10.0585610751426 | 1.1182973325898047 | -5.72996375205318 | -0.2932346429073194 | 0.020286432637201868 |
| calibration | ia_russian--d83b48ac6a21756e--s005-l0011 | 4.239682576014403 | -0.003448352463124138 | 0.27050947844517736 | 0.009509836980334585 | -0.005496956906541062 |
| calibration | bsb_poly1850--97801b0bc5afce27--s005-l0001 | 1.8214458808117115 | -0.6286106997355319 | 0.8222526213477259 | 0.027059817854348633 | -0.004511116809119503 |
| cells | gazette_modern--8be5ea8687d970a3--s000-l0107 | 1.238801154898951 | 1.277382322943879 | 0.5684192697457657 | 0.016643983688545916 | -0.010276316994880408 |
| cells | 4c949ab8ae19e68be5a06c43-p000062-l0028 | 0.5112624267088401 | -0.23680794278905637 | 0.8652460968324078 | 0.026926236017156602 | -0.004491448428015854 |
| cells | aa816f48-p000084-l0026 | 0.21251833549220453 | 0.09593375664999826 | 0.19752552727672068 | 0.0063650950096213466 | -0.002335505018313977 |
| cells | 94fbbe22-p000026-l0004 | 1.342079123949337 | 0.49538771984904884 | 0.3098576225792016 | 0.006143299250357059 | -0.0013173231109739197 |

## Every S2 → S3 verdict flip

| Set | ID | S2 | S3 | Owner state / rating / latest mark | Chord deviation px | S2 reason | S3 reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| segeval1 | ia_poly1850--df8f2267db2b7275--s025-l0037 | DROP | KEEP | faulty; KEEP | 37.26369867867917 | length: Too much OCR output for the text box after height normalisation. | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | ia_greek_latin--d94cfff6c5bd6428--s004-l0037 | KEEP | DROP | unrated | 18.95703382387393 | length: OCR length matches; vertical padding is within the selected allowance. | length: Too much OCR output for the text box after height normalisation. |

[Full flips with before/after measurements](flips.jsonl).

## Readback, scope and receipt

| Check | Count |
| --- | --- |
| gate_and_verdict_exact_readbacks | 2576 |
| predictor_exact_readbacks | 2398 |
| straight_byte_identical | 1184 |
| tests passed | 177 |

Every straight row has byte-identical canonical evidence and exact final result after excluding only tool_version and the inherited orientation seconds normalization (S2 produces no elapsed orientation fields here). [Straight evidence hashes](straight_readback.jsonl). Every gate/final result and available predictor result was independently recomputed from stored evidence.

Changed existing source files (exhaustive):

- `docs/harvest/line_pipeline/tool_versions.json`
- `greekocr/glyphs/components.py`
- `greekocr/harvest/filtering_assets/crop-tools.py`
- `greekocr/harvest/line_pipeline_native.py`
- `scripts/harvest/build_filter_versions.py`

New test file: `tests/test_seg_curve.py`. New evidence scripts and baseline copies live only under S3. In crop-tools only features_from_observation changes among existing functions; curve_coordinates and curve_tight_box are added. NativeSegmenter only passes the detector’s base array and construction flag to Stage B. components.py records which existing construction was selected; it changes no fitting, detector choices, geometry or roles. TEXT_ROLES, inventory, gate, orientation/refocus, all JS, predictor and all other initial files are unchanged. The segmentation fingerprint includes its changed native adapter. The census version remains 0.5; its existing dependency fingerprint for that same adapter is refreshed to avoid a stale source hash. No census execution occurred. Other tools’ metadata is unchanged.

Tests reuse the sibling venv and historical test_line_pipeline.py read-only, with this checkout first on PYTHONPATH, bytecode/cache writes disabled, offline fixtures and a socket audit hook for replay/readback. Synthetic fixtures cover 0°, 1.2°, −3° exact straight boxes, known-radius circular arc length within 1 px, curve pixel-cell extents, ambiguous feet in curve order, h ≤ w and S2-turned crops, including a tracked nonlinear curve with the detector’s approximate degree-1 flag.

[Scope guard](scope_guard.json), [initial hashes](initial_hashes.json), [input hashes](input_hashes.json), [crop bindings](crop_bindings.jsonl), [native replay](replay.jsonl), [summary](summary.json), [receipt](receipt.json), [tests](tests.log). Protected package, seg09 and untracked census02 evidence bytes match their before-change hashes. Network OFF; no readers, remote compute, .git writes, commits or pushes. The lead commits.

Reproduce with the sibling sol-recut .venv/bin/python, -B and PYTHONPATH=.: s3/prepare_versions.py; s3/replay.py preflight; s3/replay.py run; s3/validate_report.py. Never recreate initial_hashes.json or baseline/ after changes.

SEG S3 READY: straight identity 1184/1184; witness l0037 ratio 1.5024007041150793 → 1.3391192498745175 (DROP → KEEP); curved rows changed 94; 150 FP/FN/UNC 17/14/5 → 17/15/5; 888 rated agree 105 → 105/135; owner marks agree 169 → 170/235; flips 2; tests 177 passed


## Known limitation (recorded 19 Oct after the owner froze the filter; no code change)

**The curved-line short side can exceed the crop height.**

**Witness:** `ia_greek_latin--d94cfff6c5bd6428--s004-l0037`, owner "should not have been dropped; the box is wrong".
- **Text:** 21 chars, bold wide Latin.
- **Crop:** 523×53 px, ink support x ∈ [22, 502].
- **Verdicts:** 0.8 gave ratio 1.23, KEEP. Step 3 flipped it to DROP, "too much OCR output".

**What goes wrong:**
- The detector's degree-2 base and ascender curves bend sharply at the left end, under "Σ.".
- The unrolled (s, n) box goes below the crop:
  - `row_frame.height` 79.4 px on a 53 px crop;
  - `sn_box` [21.75, −65.94, 525.80, 13.46], so the s-extent runs past the 523 px crop width.
- The 0.9-s2 de-skewed frame already gave 62 px, against an upright box of 49 px.

**Likely causes, not diagnosed:**
- the curve is evaluated or extrapolated outside the ink support;
- the normals tilt in the end bend, so ordinary ink projects to a large |n|;
- the lower "Σ." is read as curvature by the fit.

**Fix idea, not implemented:** keep the owner's rule but bound it to the ink.
- Long side = arc length of the base curve over the ink support only.
- Short side = the ascender-to-descender extent along that support, with every foot point inside the support and no
  extrapolation.
- Add a diagnostic flag `short_side_exceeds_crop_height`. A short side larger than the crop is a measurement error.
- Brief written but not run: `docs/records/briefs/SEG_S3b_curve_support.md`.

**Status:** the owner accepted 0.9-s4 plus content gate 0.3 as good enough on 19 Oct and asked not to review it again. This
case stays a known limitation.
