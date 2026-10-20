# SEG step 4 — 0.9-s4

Small = saved Google characters ≤8 and crop long/short aspect ≤6, inclusively. After the unchanged S2 clockwise turn, every component returned by existing extraction contributes its axis-aligned bounds, including specks, dots, marks, rules and neighbour roles. No roles, x-height, row angle or curve enter this small box. Width is passed as long_side and height as short_side to the unchanged text-font predictor. Padding is (processed crop height − all-component box height) / that same box height. Non-small rows retain S3. No length exemption, numeric fit, extra threshold or heuristic enters the tool.

## Replay and unchanged scoring

S1 inputs, native adapter, source-context selection, frozen predictor and 120-second per-row timeout are reused unchanged. All 1,288 S3 native results match saved S3. The 150 are scored from their full saved reader answers using gate2 owner_state (positive faults precede unknowns), with DROP/fine = FP, KEEP/faulty = FN and every UNCERTAIN counted. The 888 use the same 135 explicit owner ratings; the 250 have no inferred labels. The 240 explicit owner-mark entries resolve to 235 IDs, latest timestamp then file order winning. No reader ran. The saved 0.8 baseline retains its historical 18/14/11 score.

| Metric | 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4 |
| --- | --- | --- | --- | --- | --- |
| 150 FP/FN/UNC | 18/14/11 | 17/14/11 | 17/14/5 | 17/15/5 | 16/15/0 |
| 888 rated agreement /135 | 94 | 95 | 105 | 105 | 109 |
| Owner marks agreement /235 | 155 | 156 | 169 | 170 | 189 |

| Set | Rows | Small | S3 → S4 transitions |
| --- | --- | --- | --- |
| segeval1 | 150 | 24 | {'KEEP->KEEP': 113, 'DROP->DROP': 28, 'UNCERTAIN->DROP': 5, 'DROP->KEEP': 4} |
| calibration | 888 | 149 | {'KEEP->KEEP': 768, 'UNCERTAIN->KEEP': 4, 'KEEP->DROP': 4, 'UNCERTAIN->UNCERTAIN': 4, 'DROP->DROP': 100, 'DROP->KEEP': 5, 'UNCERTAIN->DROP': 3} |
| cells | 250 | 149 | {'KEEP->KEEP': 209, 'UNCERTAIN->KEEP': 18, 'UNCERTAIN->DROP': 7, 'DROP->DROP': 5, 'KEEP->DROP': 3, 'DROP->KEEP': 3, 'UNCERTAIN->UNCERTAIN': 5} |

## Gate ruling

Rule 1 runs first. The byte-identical policy functions are reused by service orchestration. For a small crop with no main row, existing positive complete-row or >2-whole-word evidence still drops; otherwise the no-main abstention defers to all-ink length/padding. A missing S3 text box no longer blocks a crop that has extracted components. The S3 implementation has no separate live “neighbour extent unresolved” gate branch; source context is diagnostic and remains so. Empty component sets still have no measurable box.

Main replay: 37 row-machinery abstentions move: {'DROP': 15, 'KEEP': 22}. Typology: 51 move: {'KEEP': 33, 'DROP': 18}. Every one would remain UNCERTAIN without this ruling; see the per-row without_gate_ruling field in [small.jsonl](small.jsonl). These are cohort records; overlapping IDs are counted once per cohort.

## Every S3 → S4 verdict flip

Old/new boxes below are the actual Stage-B measurements (None means gate-blocked or unusable); supplemental S3 and all-component boxes are saved separately in flips.jsonl and never substituted into blocked tool evidence.

| Set | ID | Chars | A | S3 → S4 | Owner state / rating / mark | Old box / frame | New box / frame |
| --- | --- | --- | --- | --- | --- | --- | --- |
| segeval1 | lekythos--a0c4e6327052acfc--s002-l0089 | 1 | 1.2 | UNCERTAIN → DROP | fine; KEEP | [None, None] | [[1, 2, 17, 11], {'coordinates': 'processed_crop_all_components', 'corners': [[1, 2], [17, 2], [17, 11], [1, 11]], 'height': 9, 'length': 16}] |
| segeval1 | elstat--24e6586813212fd1--s001-l0357 | 2 | 2.0 | DROP → KEEP | fine; KEEP | [[9, 0, 13, 6], {'angle_deg': -87.39151758885076, 'corners': [[8.82228758136091, 5.90078758912806], [9.099212410871942, -0.17771241863909104], [13.227318624075064, 0.010356201552395916], [12.950393794564029, 6.088856209319547]], 'height': 4.1323880158313955, 'length': 6.084804820668037}] | [[9, 0, 32, 18], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 0], [32, 0], [32, 18], [9, 18]], 'height': 18, 'length': 23}] |
| segeval1 | elstat--d8fe6ab28d6113ba--s000-l0097 | 3 | 2.6315789473684212 | DROP → KEEP | fine; KEEP | [[9, 3, 20, 13], {'angle_deg': 22.249023657212362, 'corners': [[11.134513274336282, -0.21769911504424755], [21.608849557522127, 4.067256637168143], [17.24424778761062, 14.73628318584071], [6.769911504424776, 10.45132743362832]], 'height': 11.527266636379792, 'length': 11.316915055423959}] | [[9, 2, 45, 19], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 2], [45, 2], [45, 19], [9, 19]], 'height': 17, 'length': 36}] |
| segeval1 | gazette_modern--13a9303cfc83a9d4--s000-l0045 | 1 | 1.0625 | UNCERTAIN → DROP | unresolved; DROP | [None, None] | [[4, 6, 13, 10], {'coordinates': 'processed_crop_all_components', 'corners': [[4, 6], [13, 6], [13, 10], [4, 10]], 'height': 4, 'length': 9}] |
| segeval1 | gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | 1.0909090909090908 | UNCERTAIN → DROP | fine; KEEP | [None, None] | [[1, 7, 22, 16], {'coordinates': 'processed_crop_all_components', 'corners': [[1, 7], [22, 7], [22, 16], [1, 16]], 'height': 9, 'length': 21}] |
| segeval1 | gazette_modern--5158b7bf9def2bab--s000-l0012 | 1 | 1.875 | UNCERTAIN → DROP | unresolved; DROP | [None, None] | [[4, 3, 12, 7], {'coordinates': 'processed_crop_all_components', 'corners': [[4, 3], [12, 3], [12, 7], [4, 7]], 'height': 4, 'length': 8}] |
| segeval1 | gazette_modern--c4919950cda5532e--s000-l0030 | 6 | 3.4166666666666665 | DROP → KEEP | fine; DROP | [[18, 0, 51, 24], {'angle_deg': -2.686055879739369, 'corners': [[17.12375169360431, 0.32259845777877416], [50.51939657350598, -1.2441546690336267], [51.64507739591404, 22.749949028553402], [18.249432516012376, 24.316702155365803]], 'height': 24.020494781841958, 'length': 33.43237670739069}] | [[0, 0, 82, 24], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 0], [82, 0], [82, 24], [0, 24]], 'height': 24, 'length': 82}] |
| segeval1 | ia_poly1850--4ab77886725d9e1e--s035-l0035 | 6 | 3.0 | DROP → KEEP | fine; KEEP | [[2, 3, 60, 38], {'angle_deg': 19.08470632555438, 'corners': [[9.735205514197105, -4.357239163614842], [65.86054759287855, 15.06112695735753], [54.42913464661883, 48.10159792461142], [-1.6962074320626073, 28.683231803639046]], 'height': 34.96212126982374, 'length': 59.389620021154684}] | [[2, 3, 113, 39], {'coordinates': 'processed_crop_all_components', 'corners': [[2, 3], [113, 3], [113, 39], [2, 39]], 'height': 36, 'length': 111}] |
| segeval1 | nlg--3d6bd7bd688acb61--s024-l0003 | 1 | 4.583333333333333 | UNCERTAIN → DROP | fine; DROP | [None, None] | [[5, 3, 51, 9], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 3], [51, 3], [51, 9], [5, 9]], 'height': 6, 'length': 46}] |
| calibration | elstat--3b2d88122b3f037c--s000-l0628 | 2 | 1.8823529411764706 | UNCERTAIN → KEEP |  | [None, None] | [[10, 2, 26, 15], {'coordinates': 'processed_crop_all_components', 'corners': [[10, 2], [26, 2], [26, 15], [10, 15]], 'height': 13, 'length': 16}] |
| calibration | ia_russian--06528548147a3a3d--s002-l0005 | 2 | 3.027027027027027 | KEEP → DROP | KEEP | [[9, 0, 106, 36], {'angle_deg': -0.2264446813753687, 'corners': [[8.885808976676891, 0.10716140643311789], [105.89219817991702, -0.27622975176428], [106.03542889836882, 35.964289944419036], [9.029039695128695, 36.347681102616434]], 'height': 36.24080273515143, 'length': 97.00714682450302}] | [[9, 0, 106, 36], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 0], [106, 0], [106, 36], [9, 36]], 'height': 36, 'length': 97}] |
| calibration | gazette_modern--affc069208f11f21--s000-l0033 | 3 | 1.736842105263158 | UNCERTAIN → KEEP |  | [None, None] | [[6, 3, 30, 15], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 3], [30, 3], [30, 15], [6, 15]], 'height': 12, 'length': 24}] |
| calibration | elstat--24e6586813212fd1--s001-l0357 | 2 | 2.0 | DROP → KEEP | KEEP | [[9, 0, 13, 6], {'angle_deg': -87.39151758885076, 'corners': [[8.82228758136091, 5.90078758912806], [9.099212410871942, -0.17771241863909104], [13.227318624075064, 0.010356201552395916], [12.950393794564029, 6.088856209319547]], 'height': 4.1323880158313955, 'length': 6.084804820668037}] | [[9, 0, 32, 18], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 0], [32, 0], [32, 18], [9, 18]], 'height': 18, 'length': 23}] |
| calibration | elstat--4b280095ac934f7f--s001-l0131 | 6 | 3.269230769230769 | UNCERTAIN → KEEP |  | [None, None] | [[8, 4, 84, 24], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 4], [84, 4], [84, 24], [8, 24]], 'height': 20, 'length': 76}] |
| calibration | elstat--996d9f614c928993--s000-l0085 | 3 | 2.4375 | UNCERTAIN → DROP |  | [None, None] | [[6, 7, 33, 13], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 7], [33, 7], [33, 13], [6, 13]], 'height': 6, 'length': 27}] |
| calibration | ia_poly1850--bd7bfada1d31d9e4--s031-l0023 | 6 | 3.5 | DROP → KEEP | DROP | [[7, 0, 185, 75], {'angle_deg': 27.426284987236688, 'corners': [[45.34854640775177, -49.11775584127004], [203.28358167596485, 32.83993425934749], [159.9394977816194, 116.36534121161414], [2.0044625134063097, 34.40765111099661]], 'height': 94.10208932421114, 'length': 177.93408423289947}] | [[6, 0, 343, 98], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 0], [343, 0], [343, 98], [6, 98]], 'height': 98, 'length': 337}] |
| calibration | ia_greek_latin--202a95a447dece04--s000-l0126 | 4 | 1.2682926829268293 | KEEP → DROP |  | [[0, 4, 52, 41], {'angle_deg': 3.4215775095485657, 'corners': [[0.6430425767334285, 2.244780295904004], [54.125945413216854, 5.442463337009897], [51.975066157231424, 41.41703141711964], [-1.507836679251998, 38.21934837601374]], 'height': 36.03881005422181, 'length': 53.57841050878706}] | [[0, 0, 52, 41], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 0], [52, 0], [52, 41], [0, 41]], 'height': 41, 'length': 52}] |
| calibration | ia_russian--d558bd3e803e7865--s007-l0031 | 1 | 5.0 | UNCERTAIN → DROP |  | [None, None] | [[6, 3, 67, 12], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 3], [67, 3], [67, 12], [6, 12]], 'height': 9, 'length': 61}] |
| calibration | elstat--df38bce62200e7db--s000-l0095 | 3 | 2.55 | KEEP → DROP |  | [[8, 0, 17, 20], {'angle_deg': 87.47388308838046, 'corners': [[16.147852363479394, -0.3153464278005593], [17.044031944744226, 19.998057414202457], [8.810058277573923, 20.361320958342322], [7.913878696309087, 0.0479171163393044]], 'height': 8.241982938234894, 'length': 20.333162899317436}] | [[8, 0, 17, 20], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 0], [17, 0], [17, 20], [8, 20]], 'height': 20, 'length': 9}] |
| calibration | gazette_modern--3ff46b4e721f2046--s000-l0375 | 5 | 1.6770833333333333 | UNCERTAIN → DROP | KEEP | [None, None] | [[0, 0, 149, 96], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 0], [149, 0], [149, 96], [0, 96]], 'height': 96, 'length': 149}] |
| calibration | ia_greek_latin--54dae6633713c0a0--s005-l0003 | 6 | 4.08955223880597 | DROP → KEEP | KEEP | [[4, 0, 501, 25], {'angle_deg': 0.5582421896758863, 'corners': [[4.173831463283477, -4.84081213468761], [501.0097425476376, 9.492624546680872e-05], [500.7459595664145, 27.07288441691402], [3.910048482060347, 22.23197735598093]], 'height': 27.07407454128832, 'length': 496.85949414718124}] | [[0, 0, 547, 134], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 0], [547, 0], [547, 134], [0, 134]], 'height': 134, 'length': 547}] |
| calibration | ia_greek_latin--5f5319037ff4b70f--s000-l0028 | 7 | 1.8601036269430051 | KEEP → DROP | DROP; DROP | [[42, 47, 251, 148], {'angle_deg': 5.21854271716139, 'corners': [[42.96495664988069, 43.434794790023446], [257.84448463341255, 63.060483579782314], [249.67230906290038, 152.53674339424236], [34.79278107936855, 132.91105460448347]], 'height': 89.84868125876991, 'length': 215.77390761372862}] | [[11, 0, 359, 162], {'coordinates': 'processed_crop_all_components', 'corners': [[11, 0], [359, 0], [359, 162], [11, 162]], 'height': 162, 'length': 348}] |
| calibration | lekythos--9447d290d59a2411--s001-l0429 | 8 | 4.068627450980392 | UNCERTAIN → KEEP | KEEP | [None, None] | [[6, 0, 415, 102], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 0], [415, 0], [415, 102], [6, 102]], 'height': 102, 'length': 409}] |
| calibration | nlg--6146c0455e0103d2--s003-l0011 | 4 | 3.012987012987013 | DROP → KEEP | KEEP | [[7, 58, 231, 77], {'angle_deg': 0.41820994149709595, 'corners': [[7.058604155567394, 56.971230687266925], [231.1342567927544, 58.60681939264785], [230.99222163026107, 78.06563665423548], [6.916568993074051, 76.43004794885454]], 'height': 19.459335631188566, 'length': 224.08162185952347}] | [[5, 0, 231, 77], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 0], [231, 0], [231, 77], [5, 77]], 'height': 77, 'length': 226}] |
| calibration | ia_greek_latin--e3dff0a8a9829e59--s004-l0012 | 7 | 2.4571428571428573 | DROP → KEEP |  | [[51, 3, 136, 53], {'angle_deg': 4.780271015847579, 'corners': [[51.644980934276234, -1.7127218550459489], [139.4595220873231, 5.6308211717100285], [135.4253395470174, 53.87182519576835], [47.610798393970505, 46.52828216901237]], 'height': 48.40939059746279, 'length': 88.121060264309}] | [[11, 3, 172, 70], {'coordinates': 'processed_crop_all_components', 'corners': [[11, 3], [172, 3], [172, 70], [11, 70]], 'height': 67, 'length': 161}] |
| cells | gazette_modern--104e152774c2805f--s000-l0026 | 3 | 1.5714285714285714 | UNCERTAIN → KEEP | DROP | [None, None] | [[5, 3, 27, 19], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 3], [27, 3], [27, 19], [5, 19]], 'height': 16, 'length': 22}] |
| cells | gazette_modern--96035db0434dc980--s000-l0074 | 1 | 1.1538461538461537 | UNCERTAIN → DROP | KEEP | [None, None] | [[1, 4, 14, 10], {'coordinates': 'processed_crop_all_components', 'corners': [[1, 4], [14, 4], [14, 10], [1, 10]], 'height': 6, 'length': 13}] |
| cells | elstat--c4d30f00b317e558--s001-l0421 | 3 | 2.3333333333333335 | UNCERTAIN → KEEP | KEEP | [None, None] | [[6, 1, 29, 14], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 1], [29, 1], [29, 14], [6, 14]], 'height': 13, 'length': 23}] |
| cells | gazette_modern--079b57365772aa61--s000-l0006 | 2 | 1.2666666666666666 | UNCERTAIN → KEEP | KEEP | [None, None] | [[5, 4, 18, 13], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 4], [18, 4], [18, 13], [5, 13]], 'height': 9, 'length': 13}] |
| cells | gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | 2 | 1.1176470588235294 | UNCERTAIN → DROP | KEEP | [None, None] | [[6, 2, 16, 16], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 2], [16, 2], [16, 16], [6, 16]], 'height': 14, 'length': 10}] |
| cells | gazette_modern--24c7c93dc88ee822--s000-l0296 | 7 | 4.125 | UNCERTAIN → KEEP | KEEP | [None, None] | [[7, 0, 63, 14], {'coordinates': 'processed_crop_all_components', 'corners': [[7, 0], [63, 0], [63, 14], [7, 14]], 'height': 14, 'length': 56}] |
| cells | elstat--c5f7ea1f26d39839--s000-l0249 | 3 | 1.7777777777777777 | UNCERTAIN → KEEP | KEEP | [None, None] | [[4, 1, 29, 15], {'coordinates': 'processed_crop_all_components', 'corners': [[4, 1], [29, 1], [29, 15], [4, 15]], 'height': 14, 'length': 25}] |
| cells | gazette_modern--b00f99fd4af2363c--s000-l0008 | 4 | 1.894736842105263 | UNCERTAIN → KEEP | DROP | [None, None] | [[0, 0, 36, 19], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 0], [36, 0], [36, 19], [0, 19]], 'height': 19, 'length': 36}] |
| cells | elstat--c4d30f00b317e558--s001-l0401 | 2 | 1.8666666666666667 | UNCERTAIN → KEEP | KEEP | [None, None] | [[8, 2, 25, 14], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 2], [25, 2], [25, 14], [8, 14]], 'height': 12, 'length': 17}] |
| cells | gazette_modern--ec4326f197ce9481--s000-l0227 | 5 | 3.2142857142857144 | UNCERTAIN → KEEP | KEEP | [None, None] | [[6, 3, 43, 13], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 3], [43, 3], [43, 13], [6, 13]], 'height': 10, 'length': 37}] |
| cells | ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | 1 | 1.4166666666666667 | UNCERTAIN → KEEP | KEEP | [None, None] | [[8, 0, 27, 24], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 0], [27, 0], [27, 24], [8, 24]], 'height': 24, 'length': 19}] |
| cells | gazette_modern--4a2dc84c04c6d92d--s000-l0028 | 5 | 1.0571428571428572 | KEEP → DROP | KEEP | [[8, 7, 33, 31], {'angle_deg': 26.59778226721244, 'corners': [[21.01599575100116, 1.999437872465581], [35.001712490123, 9.0022860396973], [20.78240483707073, 37.40033270770469], [6.796688097948891, 30.397484540472973]], 'height': 31.75905799438133, 'length': 15.640976796870884}] | [[8, 7, 33, 31], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 7], [33, 7], [33, 31], [8, 31]], 'height': 24, 'length': 25}] |
| cells | gazette_modern--af7b153702818d6f--s000-l0015 | 1 | 1.0952380952380953 | UNCERTAIN → DROP |  | [None, None] | [[0, 5, 20, 15], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 5], [20, 5], [20, 15], [0, 15]], 'height': 10, 'length': 20}] |
| cells | serbia--527611a97c83a52d--s008-l0001 | 2 | 1.5416666666666667 | UNCERTAIN → KEEP | KEEP | [None, None] | [[9, 1, 33, 23], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 1], [33, 1], [33, 23], [9, 23]], 'height': 22, 'length': 24}] |
| cells | ia_poly1850--36dcee7ce4c29f8b--s035-l0026 | 3 | 1.641025641025641 | UNCERTAIN → KEEP | KEEP | [None, None] | [[11, 3, 62, 38], {'coordinates': 'processed_crop_all_components', 'corners': [[11, 3], [62, 3], [62, 38], [11, 38]], 'height': 35, 'length': 51}] |
| cells | elstat--e98a22201f0af549--s001-l0416 | 3 | 2.1176470588235294 | UNCERTAIN → KEEP | KEEP | [None, None] | [[6, 2, 31, 16], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 2], [31, 2], [31, 16], [6, 16]], 'height': 14, 'length': 25}] |
| cells | serbia--557369d8d117b91a--s000-l0226 | 4 | 1.8518518518518519 | DROP → KEEP | KEEP | [[8, 5, 49, 25], {'angle_deg': -28.81079374297299, 'corners': [[3.552783109404995, 9.095969289827238], [37.79462571976971, -9.737044145873298], [52.86948176583493, 17.671785028790808], [18.62763915547021, 36.504798464491344]], 'height': 31.280907939756275, 'length': 39.079229526978466}] | [[8, 5, 49, 25], {'coordinates': 'processed_crop_all_components', 'corners': [[8, 5], [49, 5], [49, 25], [8, 25]], 'height': 20, 'length': 41}] |
| cells | gazette_modern--d6092126b747cac8--s000-l0014 | 1 | 1.0 | KEEP → DROP | KEEP | [[7, 3, 17, 22], {'angle_deg': 39.0218849528064, 'corners': [[10.264077690250211, -0.02765370519306032], [25.10465497051511, 11.999397465688286], [13.035821974688318, 26.89153072532032], [-1.804755305576581, 14.864479554438972]], 'height': 19.16852531896484, 'length': 19.102164638556363}] | [[7, 3, 17, 22], {'coordinates': 'processed_crop_all_components', 'corners': [[7, 3], [17, 3], [17, 22], [7, 22]], 'height': 19, 'length': 10}] |
| cells | gazette_modern--b590ece7e2d52a5c--s000-l0050 | 1 | 1.2307692307692308 | UNCERTAIN → KEEP | KEEP | [None, None] | [[0, 4, 13, 13], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 4], [13, 4], [13, 13], [0, 13]], 'height': 9, 'length': 13}] |
| cells | elstat--3b2d88122b3f037c--s000-l0185 | 1 | 1.2 | DROP → KEEP | KEEP | [[6, 0, 14, 14], {'angle_deg': 0.0, 'corners': [[6, 0], [14, 0], [14, 14], [6, 14]], 'height': 14, 'length': 8}] | [[6, 0, 14, 14], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 0], [14, 0], [14, 14], [6, 14]], 'height': 14, 'length': 8}] |
| cells | ia_poly1850--a89bd2c9bdb1ca6d--s025-l0015 | 3 | 1.6 | UNCERTAIN → KEEP | KEEP | [None, None] | [[9, 2, 64, 38], {'coordinates': 'processed_crop_all_components', 'corners': [[9, 2], [64, 2], [64, 38], [9, 38]], 'height': 36, 'length': 55}] |
| cells | elstat--c4d30f00b317e558--s001-l0238 | 2 | 1.6 | UNCERTAIN → KEEP | KEEP | [None, None] | [[4, 2, 25, 19], {'coordinates': 'processed_crop_all_components', 'corners': [[4, 2], [25, 2], [25, 19], [4, 19]], 'height': 17, 'length': 21}] |
| cells | elstat--0a2c92120843658d--s001-l0216 | 1 | 1.4705882352941178 | UNCERTAIN → DROP | KEEP | [None, None] | [[7, 0, 16, 17], {'coordinates': 'processed_crop_all_components', 'corners': [[7, 0], [16, 0], [16, 17], [7, 17]], 'height': 17, 'length': 9}] |
| cells | gazette_modern--906c0a8f1bdc4787--s000-l0131 | 7 | 4.923076923076923 | UNCERTAIN → KEEP | KEEP | [None, None] | [[0, 2, 62, 13], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 2], [62, 2], [62, 13], [0, 13]], 'height': 11, 'length': 62}] |
| cells | gazette_modern--70ef76cb8b8c1897--s000-l0075 | 3 | 1.46875 | UNCERTAIN → KEEP | KEEP | [None, None] | [[10, 4, 42, 31], {'coordinates': 'processed_crop_all_components', 'corners': [[10, 4], [42, 4], [42, 31], [10, 31]], 'height': 27, 'length': 32}] |
| cells | gazette_modern--a8e70ef11baca460--s000-l0001 | 1 | 1.0714285714285714 | UNCERTAIN → DROP | KEEP | [None, None] | [[1, 5, 13, 11], {'coordinates': 'processed_crop_all_components', 'corners': [[1, 5], [13, 5], [13, 11], [1, 11]], 'height': 6, 'length': 12}] |
| cells | gazette_modern--00a5942b52d08f1e--s000-l0115 | 1 | 1.0476190476190477 | UNCERTAIN → DROP | KEEP | [None, None] | [[0, 5, 20, 16], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 5], [20, 5], [20, 16], [0, 16]], 'height': 11, 'length': 20}] |
| cells | ia_poly1850--26e14cb9c90b750f--s005-l0061 | 1 | 1.1025641025641026 | UNCERTAIN → DROP |  | [None, None] | [[0, 6, 42, 32], {'coordinates': 'processed_crop_all_components', 'corners': [[0, 6], [42, 6], [42, 32], [0, 32]], 'height': 26, 'length': 42}] |
| cells | gazette_modern--c262db73f08c25a0--s000-l0188 | 7 | 2.736842105263158 | DROP → KEEP |  | [[5, 0, 47, 17], {'angle_deg': -1.3547915059077311, 'corners': [[4.645448603867504, 0.008385133530923738], [46.740154028691755, -0.9871538201503789], [47.16378029148898, 16.92517665845907], [5.069074866664732, 17.92071561214037]], 'height': 17.91733915472531, 'length': 42.10647601748483}] | [[5, 0, 47, 17], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 0], [47, 0], [47, 17], [5, 17]], 'height': 17, 'length': 42}] |
| cells | gazette_modern--af3a940b646b3a7d--s000-l0196 | 7 | 3.611111111111111 | UNCERTAIN → KEEP |  | [None, None] | [[5, 0, 61, 18], {'coordinates': 'processed_crop_all_components', 'corners': [[5, 0], [61, 0], [61, 18], [5, 18]], 'height': 18, 'length': 56}] |
| cells | gazette_modern--0089276875b132d9--s000-l0025 | 3 | 1.2982456140350878 | KEEP → DROP |  | [[6, 3, 63, 54], {'angle_deg': 32.1807586198423, 'corners': [[28.58024912873139, -14.883546173258587], [74.84564581654044, 14.229635066025947], [41.57880816468627, 67.09584119657242], [-4.686588523122772, 37.98265995728789]], 'height': 62.462134433529016, 'length': 54.66318919118936}] | [[6, 3, 63, 54], {'coordinates': 'processed_crop_all_components', 'corners': [[6, 3], [63, 3], [63, 54], [6, 54]], 'height': 51, 'length': 57}] |

[Full flips with reasons and owner marks](flips.jsonl). Typology changes are in [typology_flips.jsonl](typology_flips.jsonl).

## Typology owner agreement

All 437 SHA-verified crops replayed for 0.8, S3 and S4. The 20 control=true rows are replayed but excluded from scoring; the other 417 exactly match card_manifest.json. 185 bed cards have explicit typology owner marks. Source: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/small_segments/owner_marks_smallseg.jsonl`; dump used: None. The available 20261019T1827 dump is not used because the preferred JSONL exists. Unmarked cards do not acquire inferred owner judgements.

| Version | Owner agreement / marked | Confusion (tool → owner KEEP/DROP) |
| --- | --- | --- |
| 08 | 131/185 | {'KEEP': {'KEEP': 131, 'DROP': 5}, 'DROP': {'KEEP': 13, 'DROP': 0}, 'UNCERTAIN': {'KEEP': 33, 'DROP': 3}} |
| s3 | 147/185 | {'KEEP': {'KEEP': 147, 'DROP': 8}, 'DROP': {'KEEP': 14, 'DROP': 0}, 'UNCERTAIN': {'KEEP': 16, 'DROP': 0}} |
| s4 | 160/185 | {'KEEP': {'KEEP': 160, 'DROP': 8}, 'DROP': {'KEEP': 13, 'DROP': 0}, 'UNCERTAIN': {'KEEP': 4, 'DROP': 0}} |

### Agreement by final_type

| final_type | Bed n | Owner n | 0.8 | S3 | S4 |
| --- | --- | --- | --- | --- | --- |
| abbrev_label | 46 | 0 | 0 | 0 | 0 |
| caps_display | 77 | 66 | 36 | 43 | 51 |
| cut_fragment | 18 | 0 | 0 | 0 | 0 |
| digits_letters | 5 | 0 | 0 | 0 | 0 |
| figure_ornament | 12 | 0 | 0 | 0 | 0 |
| foreign_script | 5 | 0 | 0 | 0 | 0 |
| handwriting | 18 | 0 | 0 | 0 | 0 |
| marker | 10 | 0 | 0 | 0 | 0 |
| multi_line | 31 | 0 | 0 | 0 | 0 |
| noise | 7 | 0 | 0 | 0 | 0 |
| number | 5 | 0 | 0 | 0 | 0 |
| part_of_line | 5 | 0 | 0 | 0 | 0 |
| punctuation | 53 | 0 | 0 | 0 | 0 |
| roman_lower | 2 | 0 | 0 | 0 | 0 |
| show_through | 2 | 0 | 0 | 0 | 0 |
| watermark | 2 | 0 | 0 | 0 | 0 |
| word | 119 | 119 | 95 | 104 | 109 |

### Agreement by final_class

| final_class | Bed n | Owner n | 0.8 | S3 | S4 |
| --- | --- | --- | --- | --- | --- |
| legit_text | 246 | 172 | 123 | 138 | 149 |
| non_text | 41 | 0 | 0 | 0 | 0 |
| out_of_scope_script | 5 | 0 | 0 | 0 | 0 |
| printed_nonletter | 50 | 0 | 0 | 0 | 0 |
| segmentation_fault | 75 | 13 | 8 | 9 | 11 |

### Owner DROPs: label-fault readback

These marks concern Google-output correctness. Their S4 verdicts below do not establish a box fault; the tool has no new label-correctness rule. Saved notes and final_text are shown literally. All eight receive KEEP. Four have explicit output-error notes and four have final_text=wrong, but these groups overlap on NOTE.; their union is seven. The remaining 1. ΡΑΓΙΟ has no note and final_text=match. The inputs therefore do not establish eight disjoint label-fault records, and no missing label judgement is inferred.

| ID | Text | Owner note | Saved final_text | S4 | Reason |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850--3496ab66cde251ee--s001-l0099 | NOTE. | wrong output | wrong | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| bsb_poly1850--d7db5a3b1eb289a3--s006-l0029 | νὴ τοὺς δ. | actual output is "νὴ τοὺς s." | match | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| gazette_modern--7c70c29daed80864--s000-l0006 | Η Άντρια | wrong output | minor | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| ia_poly1850--26e14cb9c90b750f--s000-l0041 | ch'uh văn. | wrong output | minor | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| serbia--90015698e9ce2250--s006-l0001 | БАЦИМА |  | wrong | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| gazette_modern--fc7c47be408bb952--s000-l0009 | 1. ΡΑΓΙΟ |  | match | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| gazette_modern--a426e6eea7b8e321--s000-l0082 | HARIAZ |  | wrong | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |
| gazette_modern--3696946a45969b03--s000-l0005 | IIIXX |  | wrong | KEEP | length: OCR length matches; vertical padding is within the selected allowance. |

### Length-exempt classes — diagnostic only

Classes come from the typology manifest, including punctuation-only, non-text, CJK and fault groups named in NOTE_steps45_length_exempt.md. Controls are excluded. The note cautions that owner-kept clipped/extra legitimate types are not a trustworthy fault core; no class changes a verdict.

| final_class | S4 verdict counts |
| --- | --- |
| legit_text | {'KEEP': 225, 'DROP': 18, 'UNCERTAIN': 3} |
| non_text | {'DROP': 14, 'KEEP': 27} |
| out_of_scope_script | {'DROP': 2, 'KEEP': 3} |
| printed_nonletter | {'KEEP': 21, 'UNCERTAIN': 6, 'DROP': 23} |
| segmentation_fault | {'DROP': 47, 'KEEP': 27, 'UNCERTAIN': 1} |

## Numeric-only or all-small: diagnostic 2×2

Population is the union of small crops with typology marks, owner_marks_20261019 marks or an explicit 888 rating, deduplicated by line_id. Explicit marks outrank ratings; latest explicit timestamp wins (Athens local strings converted to UTC for cross-source ordering, then file order). All conflicting decisions are listed below and in owner_conflicts.jsonl. Output type uses the unchanged `cells_opus/scripts/common.py::output_type(text)`, also underlying Q1: decimal digits plus its exact separator list or canonical uppercase Latin Roman numerals are numeric; otherwise ≥1 digit and ≤2 Unicode letters is mixed; the rest is non-numeric. Character count is the native saved-Google counting function, not a new count for fitting.

| ID | Chosen judgement | Conflicting sources |
| --- | --- | --- |
| bsb_poly1850--027215cc6d2a7e8a--s009-l0001 | {'sheet': 'small_segments (417, Q3 typology)', 'line_id': 'bsb_poly1850--027215cc6d2a7e8a--s009-l0001', 'owner_mark': 'KEEP', 'note': '', 'updated': '2026-10-19 18:21', 'source': 'typology', 'explicit': True} | [{'owner_mark': 'DROP', 'source': '888 rating', 'explicit': False, 'updated': '2026-10-18T16:36:33.815Z'}, {'sheet': 'small_segments (417, Q3 typology)', 'line_id': 'bsb_poly1850--027215cc6d2a7e8a--s009-l0001', 'owner_mark': 'KEEP', 'note': '', 'updated': '2026-10-19 18:21', 'source': 'typology', 'explicit': True}] |
| serbia--90015698e9ce2250--s006-l0001 | {'sheet': 'small_segments (417, Q3 typology)', 'line_id': 'serbia--90015698e9ce2250--s006-l0001', 'owner_mark': 'DROP', 'note': '', 'updated': '2026-10-19 18:22', 'source': 'typology', 'explicit': True} | [{'owner_mark': 'KEEP', 'source': '888 rating', 'explicit': False, 'updated': '2026-10-18T16:35:28.896Z'}, {'sheet': 'small_segments (417, Q3 typology)', 'line_id': 'serbia--90015698e9ce2250--s006-l0001', 'owner_mark': 'DROP', 'note': '', 'updated': '2026-10-19 18:22', 'source': 'typology', 'explicit': True}] |

### Local fits, refit separately per box

Only SHA-verifiable local small numeric crop IDs are fitted. Inputs include 150 + 888 + 250, all 437 typology crops including controls, and 134 additional cells_opus/crops IDs. Duplicates are fitted once. Contact sheets, report illustrations and the test_tmp SHA-mismatch fixture are not independent crop/text/hash inputs. The frozen census table was read only to recover hashes/text for that finite list of extra local PNGs; no census tool execution or fetch ran. All 1,103 paths in the four direct crop directories are accounted for: 1,089 match measured-pool SHA records, and the other 14 are nine-character numeric crops outside the definition. [Path-level coverage](local_crop_coverage.jsonl), [local inventory](local_crop_inventory.json), [extra measurements](extra_numeric.jsonl), [fit IDs](numeric_fits.json).

S3 ratio is its existing predictor input max(row-frame length,height)/min(length,height). S4 ratio is all-component width/height in the processed crop frame, including when width < height. The old text-font predictor retains its text-box fit. Both numeric lines use OLS ratio = a·chars + b with residual SD ddof=2 and unscaled median absolute deviation about the residual median, matching cells_opus. The without-owner fit excludes every ID with an explicit mark or rating and is used in the primary 2×2; the all-crops fit is also reported. Supplemental S3 boxes for gate-blocked crops are fit diagnostics only; their gate stays UNCERTAIN/DROP in the 2×2. A missing S3 text box contributes no S3 ratio.

| Box | Fit population | n | a | b | Residual SD | MAD | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s3 | all | 383 | 0.5231866042567721 | 0.4765284007779097 | 0.6448405385816924 | 0.3507542065713105 | {'segeval1': 14, 'calibration': 87, 'cells': 147, 'typology': 1, 'cells_opus': 134} |
| s3 | without_owner | 239 | 0.5641550865709398 | 0.3011069638055544 | 0.6260684780393301 | 0.3083452742163322 | {'segeval1': 7, 'calibration': 80, 'cells': 17, 'typology': 1, 'cells_opus': 134} |
| s4 | all | 383 | 0.5872679189545223 | 0.1888208255197327 | 0.5953123584588808 | 0.21657823489163142 | {'segeval1': 14, 'calibration': 87, 'cells': 147, 'typology': 1, 'cells_opus': 134} |
| s4 | without_owner | 239 | 0.6075394264552724 | 0.12114941993561201 | 0.6090634240364446 | 0.2053538607844202 | {'segeval1': 7, 'calibration': 80, 'cells': 17, 'typology': 1, 'cells_opus': 134} |
| crop dimensions | reference | 36307 | 0.46 | 0.787 | 0.634 | 0.236 | historical reference only |

Unique local small numeric crops: 383; sources: {'segeval1': 14, 'calibration': 87, 'cells': 147, 'typology': 1, 'cells_opus': 134}. Missing measurable boxes: S3 0, all-ink 0. Without-owner n<100 flags: S3 False, S4 False.

### Primary 2×2 (without-owner numeric fits)

For each box, pred = (ratio−b)/a is supplied to the unchanged rule-2 function, retaining its (chars+1)/(pred+1) 0.5–1.5 interval and its existing negative/unavailable prediction handling. Gate and padding stay exactly those of the box’s version. No numeric line is added to the tool. Each cell below shows n, agreement and all six tool-verdict × owner-verdict counts. Every numeric cell has n=144, so none has fewer than 30 numeric crops. Mixed cells have only three crops and are additionally marked indicative only. Other types are evaluated on their own output type; the numeric training-fit n is reported above.

### without_owner fit cells

| Type | Box / expected length | n | Agree | Numeric n | Flag | KEEP vs owner K/D | DROP vs owner K/D | UNC vs owner K/D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 | 111 | 144 |  | 108/0 | 8/3 | 22/3 |
| numeric | s4/text-font | 144 | 127 | 144 |  | 125/4 | 13/2 | 0/0 |
| numeric | s3/short-numeric | 144 | 111 | 144 |  | 108/0 | 8/3 | 22/3 |
| numeric | s4/short-numeric | 144 | 132 | 144 |  | 130/4 | 8/2 | 0/0 |
| mixed | s3/text-font | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s4/text-font | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s3/short-numeric | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s4/short-numeric | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| non-numeric | s3/text-font | 157 | 120 | 0 |  | 113/10 | 12/7 | 13/2 |
| non-numeric | s4/text-font | 157 | 137 | 0 |  | 127/9 | 11/10 | 0/0 |
| non-numeric | s3/short-numeric | 157 | 124 | 0 |  | 116/9 | 9/8 | 13/2 |
| non-numeric | s4/short-numeric | 157 | 137 | 0 |  | 128/10 | 10/9 | 0/0 |

### all fit cells

| Type | Box / expected length | n | Agree | Numeric n | Flag | KEEP vs owner K/D | DROP vs owner K/D | UNC vs owner K/D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 | 111 | 144 |  | 108/0 | 8/3 | 22/3 |
| numeric | s4/text-font | 144 | 127 | 144 |  | 125/4 | 13/2 | 0/0 |
| numeric | s3/short-numeric | 144 | 109 | 144 |  | 106/0 | 10/3 | 22/3 |
| numeric | s4/short-numeric | 144 | 131 | 144 |  | 129/4 | 9/2 | 0/0 |
| mixed | s3/text-font | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s4/text-font | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s3/short-numeric | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| mixed | s4/short-numeric | 3 | 3 | 0 | indicative only | 3/0 | 0/0 | 0/0 |
| non-numeric | s3/text-font | 157 | 120 | 0 |  | 113/10 | 12/7 | 13/2 |
| non-numeric | s4/text-font | 157 | 137 | 0 |  | 127/9 | 11/10 | 0/0 |
| non-numeric | s3/short-numeric | 157 | 123 | 0 |  | 115/9 | 10/8 | 13/2 |
| non-numeric | s4/short-numeric | 157 | 138 | 0 |  | 129/10 | 9/9 | 0/0 |

### Every box / expectation flip

All swaps below retain the owner mark and use the primary without-owner fits. The all-crops-fit swaps are also saved in two_by_two_flips.jsonl.

| Type | ID | Comparison | Owner | Before | After |
| --- | --- | --- | --- | --- | --- |
| non-numeric | lekythos--a0c4e6327052acfc--s002-l0089 | box at text-font | KEEP | UNCERTAIN | DROP |
| non-numeric | lekythos--a0c4e6327052acfc--s002-l0089 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | lekythos--a0c4e6327052acfc--s002-l0089 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | elstat--24e6586813212fd1--s001-l0357 | box at text-font | KEEP | DROP | KEEP |
| numeric | elstat--24e6586813212fd1--s001-l0357 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | elstat--d8fe6ab28d6113ba--s000-l0097 | box at text-font | KEEP | DROP | KEEP |
| numeric | elstat--d8fe6ab28d6113ba--s000-l0097 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--13a9303cfc83a9d4--s000-l0045 | box at text-font | DROP | UNCERTAIN | DROP |
| numeric | gazette_modern--13a9303cfc83a9d4--s000-l0045 | box at short-numeric | DROP | UNCERTAIN | DROP |
| numeric | gazette_modern--1456dcb167f23bfe--s000-l0027 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--1456dcb167f23bfe--s000-l0027 | box at short-numeric | KEEP | UNCERTAIN | DROP |
| non-numeric | gazette_modern--5158b7bf9def2bab--s000-l0012 | box at text-font | DROP | UNCERTAIN | DROP |
| non-numeric | gazette_modern--5158b7bf9def2bab--s000-l0012 | box at short-numeric | DROP | UNCERTAIN | DROP |
| non-numeric | gazette_modern--aeb6eb76fc7057f0--s000-l0050 | expectation at s3 | DROP | DROP | KEEP |
| non-numeric | gazette_modern--aeb6eb76fc7057f0--s000-l0050 | expectation at s4 | DROP | DROP | KEEP |
| non-numeric | gazette_modern--af3c2f9a667e8669--s000-l0004 | expectation at s3 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--af3c2f9a667e8669--s000-l0004 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--c4919950cda5532e--s000-l0008 | expectation at s3 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--c4919950cda5532e--s000-l0008 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | gazette_modern--c4919950cda5532e--s000-l0030 | box at text-font | DROP | DROP | KEEP |
| numeric | gazette_modern--c4919950cda5532e--s000-l0030 | box at short-numeric | DROP | DROP | KEEP |
| non-numeric | gazette_modern--e85649b67a7af9ab--s000-l0078 | box at short-numeric | DROP | DROP | KEEP |
| non-numeric | gazette_modern--e85649b67a7af9ab--s000-l0078 | expectation at s3 | DROP | KEEP | DROP |
| non-numeric | ia_poly1850--4ab77886725d9e1e--s035-l0035 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | ia_poly1850--4ab77886725d9e1e--s035-l0035 | box at short-numeric | KEEP | DROP | KEEP |
| non-numeric | nlg--3d6bd7bd688acb61--s024-l0003 | box at text-font | DROP | UNCERTAIN | DROP |
| non-numeric | nlg--3d6bd7bd688acb61--s024-l0003 | box at short-numeric | DROP | UNCERTAIN | DROP |
| non-numeric | ia_russian--06528548147a3a3d--s002-l0005 | box at text-font | KEEP | KEEP | DROP |
| non-numeric | ia_russian--06528548147a3a3d--s002-l0005 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | ia_poly1850--bd7bfada1d31d9e4--s031-l0023 | box at text-font | DROP | DROP | KEEP |
| numeric | ia_poly1850--bd7bfada1d31d9e4--s031-l0023 | box at short-numeric | DROP | DROP | KEEP |
| numeric | gazette_modern--3ff46b4e721f2046--s000-l0375 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--3ff46b4e721f2046--s000-l0375 | box at short-numeric | KEEP | UNCERTAIN | DROP |
| non-numeric | ia_greek_latin--54dae6633713c0a0--s005-l0003 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | ia_greek_latin--54dae6633713c0a0--s005-l0003 | box at short-numeric | KEEP | DROP | KEEP |
| non-numeric | ia_greek_latin--5f5319037ff4b70f--s000-l0028 | box at text-font | DROP | KEEP | DROP |
| non-numeric | ia_greek_latin--5f5319037ff4b70f--s000-l0028 | expectation at s3 | DROP | KEEP | DROP |
| non-numeric | lekythos--9447d290d59a2411--s001-l0429 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | lekythos--9447d290d59a2411--s001-l0429 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | nlg--6146c0455e0103d2--s003-l0011 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | nlg--6146c0455e0103d2--s003-l0011 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--104e152774c2805f--s000-l0026 | box at text-font | DROP | UNCERTAIN | KEEP |
| numeric | gazette_modern--104e152774c2805f--s000-l0026 | box at short-numeric | DROP | UNCERTAIN | KEEP |
| numeric | gazette_modern--96035db0434dc980--s000-l0074 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--96035db0434dc980--s000-l0074 | box at short-numeric | KEEP | UNCERTAIN | DROP |
| numeric | elstat--c4d30f00b317e558--s001-l0421 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0421 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--079b57365772aa61--s000-l0006 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--079b57365772aa61--s000-l0006 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--2e613d9290dd13d4--s000-l0017 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--2e613d9290dd13d4--s000-l0017 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | box at short-numeric | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--24c7c93dc88ee822--s000-l0296 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--24c7c93dc88ee822--s000-l0296 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c5f7ea1f26d39839--s000-l0249 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c5f7ea1f26d39839--s000-l0249 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--b00f99fd4af2363c--s000-l0008 | box at text-font | DROP | UNCERTAIN | KEEP |
| numeric | gazette_modern--b00f99fd4af2363c--s000-l0008 | box at short-numeric | DROP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0401 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0401 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--ec4326f197ce9481--s000-l0227 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--ec4326f197ce9481--s000-l0227 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--1450bd01ddded5ef--s000-l0062 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--1450bd01ddded5ef--s000-l0062 | expectation at s3 | KEEP | KEEP | DROP |
| numeric | gazette_modern--b6928cabb92b6656--s000-l0021 | box at short-numeric | KEEP | KEEP | DROP |
| numeric | gazette_modern--b6928cabb92b6656--s000-l0021 | expectation at s4 | KEEP | KEEP | DROP |
| numeric | ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--4a2dc84c04c6d92d--s000-l0028 | box at text-font | KEEP | KEEP | DROP |
| numeric | gazette_modern--4a2dc84c04c6d92d--s000-l0028 | box at short-numeric | KEEP | KEEP | DROP |
| numeric | serbia--527611a97c83a52d--s008-l0001 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | serbia--527611a97c83a52d--s008-l0001 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | ia_poly1850--36dcee7ce4c29f8b--s035-l0026 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | ia_poly1850--36dcee7ce4c29f8b--s035-l0026 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--e98a22201f0af549--s001-l0416 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--e98a22201f0af549--s001-l0416 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | serbia--557369d8d117b91a--s000-l0226 | box at text-font | KEEP | DROP | KEEP |
| numeric | serbia--557369d8d117b91a--s000-l0226 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--d6092126b747cac8--s000-l0014 | box at text-font | KEEP | KEEP | DROP |
| numeric | gazette_modern--d6092126b747cac8--s000-l0014 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | gazette_modern--6bc7acccf0163698--s000-l0268 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | gazette_modern--6bc7acccf0163698--s000-l0268 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | gazette_modern--b590ece7e2d52a5c--s000-l0050 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--b590ece7e2d52a5c--s000-l0050 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--3b2d88122b3f037c--s000-l0185 | box at text-font | KEEP | DROP | KEEP |
| numeric | elstat--3b2d88122b3f037c--s000-l0185 | expectation at s3 | KEEP | DROP | KEEP |
| numeric | ia_poly1850--a89bd2c9bdb1ca6d--s025-l0015 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | ia_poly1850--a89bd2c9bdb1ca6d--s025-l0015 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0238 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0238 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0501 | box at short-numeric | KEEP | DROP | KEEP |
| numeric | elstat--c4d30f00b317e558--s001-l0501 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | elstat--0a2c92120843658d--s001-l0216 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | elstat--0a2c92120843658d--s001-l0216 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | elstat--0a2c92120843658d--s001-l0216 | expectation at s4 | KEEP | DROP | KEEP |
| numeric | gazette_modern--906c0a8f1bdc4787--s000-l0131 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--906c0a8f1bdc4787--s000-l0131 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--70ef76cb8b8c1897--s000-l0075 | box at text-font | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--70ef76cb8b8c1897--s000-l0075 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--a8e70ef11baca460--s000-l0001 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--a8e70ef11baca460--s000-l0001 | box at short-numeric | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--00a5942b52d08f1e--s000-l0115 | box at text-font | KEEP | UNCERTAIN | DROP |
| numeric | gazette_modern--00a5942b52d08f1e--s000-l0115 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| numeric | gazette_modern--00a5942b52d08f1e--s000-l0115 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | bsb_poly1850--2032df1e3e983f1d--s005-l0136 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | bsb_poly1850--2032df1e3e983f1d--s005-l0136 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--4a698b178a4fb0b4--s000-l0051 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--4a698b178a4fb0b4--s000-l0051 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--bc8d29ca449f517b--s000-l0014 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--bc8d29ca449f517b--s000-l0014 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--c1b2194696b35bb5--s000-l0004 | expectation at s3 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--c1b2194696b35bb5--s000-l0004 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | lekythos--25feca8f4ab34ba0--s001-l0269 | box at short-numeric | KEEP | KEEP | DROP |
| non-numeric | lekythos--25feca8f4ab34ba0--s001-l0269 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | bsb_poly1850--2032df1e3e983f1d--s005-l0216 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | bsb_poly1850--2032df1e3e983f1d--s005-l0216 | box at short-numeric | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--a895f3d785bb13b6--s000-l0007 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--a895f3d785bb13b6--s000-l0007 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--1bf5621384b3760f--s000-l0325 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--1bf5621384b3760f--s000-l0325 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--d0e85d9b20a72ee9--s000-l0096 | box at short-numeric | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--d0e85d9b20a72ee9--s000-l0096 | expectation at s3 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--062232e99d367ea4--s000-l0179 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--062232e99d367ea4--s000-l0179 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--f02808c35dc0e3dc--s000-l0128 | box at short-numeric | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--f02808c35dc0e3dc--s000-l0128 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--47f5faa35e95a12d--s000-l0059 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--47f5faa35e95a12d--s000-l0059 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--7c311df92d90d541--s000-l0015 | box at short-numeric | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--7c311df92d90d541--s000-l0015 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--7f20c8792129c8f6--s000-l0062 | box at text-font | KEEP | UNCERTAIN | DROP |
| non-numeric | gazette_modern--7f20c8792129c8f6--s000-l0062 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--7f20c8792129c8f6--s000-l0062 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--c55126f090f187d9--s000-l0062 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--c55126f090f187d9--s000-l0062 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--232906bf221ad08d--s000-l0144 | expectation at s3 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--232906bf221ad08d--s000-l0144 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--6d58ca2e2dc41e69--s000-l0140 | box at text-font | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--6d58ca2e2dc41e69--s000-l0140 | expectation at s4 | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--73f0e4003296ba2e--s000-l0046 | box at short-numeric | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--73f0e4003296ba2e--s000-l0046 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--82987adc476899c2--s000-l0032 | box at text-font | KEEP | DROP | KEEP |
| non-numeric | gazette_modern--82987adc476899c2--s000-l0032 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--232906bf221ad08d--s000-l0083 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--232906bf221ad08d--s000-l0083 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--bfec7e90c86c19fa--s000-l0030 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--bfec7e90c86c19fa--s000-l0030 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--602c5ca63e940ad6--s000-l0006 | box at short-numeric | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--602c5ca63e940ad6--s000-l0006 | expectation at s4 | KEEP | KEEP | DROP |
| non-numeric | gazette_modern--b9f59878fb904d91--s000-l0138 | box at text-font | KEEP | UNCERTAIN | KEEP |
| non-numeric | gazette_modern--b9f59878fb904d91--s000-l0138 | box at short-numeric | KEEP | UNCERTAIN | KEEP |
| non-numeric | elstat--0877c813a8512b56--s000-l0114 | box at text-font | KEEP | KEEP | DROP |
| non-numeric | elstat--0877c813a8512b56--s000-l0114 | box at short-numeric | KEEP | KEEP | DROP |

For numeric, the greatest observed owner agreement is 132/144, in s4/short-numeric.

For mixed, the greatest observed owner agreement is 3/3, in s3/text-font, s4/text-font, s3/short-numeric, s4/short-numeric.

For non-numeric, the greatest observed owner agreement is 137/157, in s4/text-font, s4/short-numeric.

## Small-segment diagnostics

Main replay has 322 small cohort records; typology has 320. Ratios include diagnostic boxes on blocked rows where measurable; they do not change gate evidence.

| S3 | S4 | S3 reason | S4 reason | n |
| --- | --- | --- | --- | --- |
| KEEP | KEEP | length: OCR length matches; vertical padding is within the selected allowance. | length: OCR length matches; vertical padding is within the selected allowance. | 250 |
| DROP | DROP | length: Too much OCR output for the text box after height normalisation. | length: Too much OCR output for the text box after height normalisation. | 2 |
| UNCERTAIN | DROP | gate: no main row found | length: Too little OCR output for the text box after height normalisation. | 12 |
| DROP | KEEP | length: Top and bottom padding together exceed 1.5 target-line heights. | length: OCR length matches; vertical padding is within the selected allowance. | 2 |
| DROP | KEEP | length: Too much OCR output for the text box after height normalisation. | length: OCR length matches; vertical padding is within the selected allowance. | 7 |
| DROP | DROP | length: Too little OCR output for the text box after height normalisation. | length: Too little OCR output for the text box after height normalisation. | 3 |
| UNCERTAIN | KEEP | gate: no main row found | length: OCR length matches; vertical padding is within the selected allowance. | 22 |
| KEEP | DROP | length: OCR length matches; vertical padding is within the selected allowance. | length: Too little OCR output for the text box after height normalisation. | 1 |
| DROP | DROP | gate: too many whole neighbour words | gate: too many whole neighbour words | 4 |
| KEEP | DROP | length: OCR length matches; vertical padding is within the selected allowance. | length: Too much OCR output for the text box after height normalisation. | 6 |
| DROP | DROP | gate: second complete line | gate: second complete line | 3 |
| UNCERTAIN | DROP | gate: no main row found | length: Too much OCR output for the text box after height normalisation. | 3 |
| DROP | KEEP | length: Too little OCR output for the text box after height normalisation. | length: OCR length matches; vertical padding is within the selected allowance. | 3 |
| DROP | DROP | length: Top and bottom padding together exceed 1.5 target-line heights. | length: Too much OCR output for the text box after height normalisation. | 1 |
| DROP | DROP | length: Too little OCR output for the text box after height normalisation. | length: Too much OCR output for the text box after height normalisation. | 3 |

| Population | Distribution | n | Quantiles 0/10/25/50/75/90/95/99/100 |
| --- | --- | --- | --- |
| 1288 | s3_ratio | 322 | {'0': 1.0017062700935755, '10': 1.256997471103815, '25': 1.6121794871794872, '50': 2.462536920859262, '75': 3.772524756263492, '90': 4.676834313977889, '95': 5.350867744133882, '99': 10.935137415273255, '100': 34.92294882978627} |
| 1288 | all_ink_ratio | 322 | {'0': 0.36363636363636365, '10': 1.1196754563894524, '25': 1.5418669871794872, '50': 2.3833333333333333, '75': 3.733187134502924, '90': 4.58371846512614, '95': 4.874583333333333, '99': 6.1160000000000085, '100': 7.666666666666667} |
| 1288 | all_ink_over_s3_ratio | 322 | {'0': 0.04706542267200121, '10': 0.6061746258375026, '25': 0.9893257757308711, '50': 1.0, '75': 1.0142543163740274, '90': 1.1154162986886698, '95': 1.2342461351481577, '99': 1.7785456552329715, '100': 2.454806744858714} |
| typology | s3_ratio | 320 | {'0': 1.0, '10': 1.1400555090858469, '25': 2.1589684069511605, '50': 3.242613972176669, '75': 4.499672222476595, '90': 5.7094913926565125, '95': 7.561111111111112, '99': 17.05292464736251, '100': 34.92294882978627} |
| typology | all_ink_ratio | 320 | {'0': 0.45, '10': 1.06125, '25': 2.0532738095238092, '50': 3.0976190476190477, '75': 4.277777777777778, '90': 5.362169312169313, '95': 6.2, '99': 8.713000000000001, '100': 10.333333333333334} |
| typology | all_ink_over_s3_ratio | 320 | {'0': 0.04706542267200121, '10': 0.7169056982922876, '25': 0.9581176187968112, '50': 1.0, '75': 1.0171109325207373, '90': 1.1090054984450424, '95': 1.2095580437807274, '99': 1.9817607415652991, '100': 2.576345576345576} |

### Huge few-character witnesses

The four owner-named huge few-character witnesses are shown, together with any other small crop with processed short side at least 400 px (display diagnostic only). Source/processed sizes and all boxes are in small.jsonl.

| Set | ID | Text | Crop w×h | Processed w×h | Chars | A | S3 → S4 | All-ink box | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | gazette_modern--a895f3d785bb13b6--s000-l0150 | ποσό | 470×2217 | 2217×470 | 4 | 4.717021276595744 | DROP → DROP | [215, 0, 2210, 462] | gate: second complete line |
| calibration | ia_greek_latin--a232aaf9a41fe898--s001-l0012 | ***** | 439×427 | 439×427 | 5 | 1.0281030444964872 | DROP → DROP | [0, 0, 439, 427] | length: Too much OCR output for the text box after height normalisation. |
| calibration | ia_poly1850--3cbcc415675468a9--s034-l0001 | MELA OF 10 | 700×562 | 700×562 | 8 | 1.2455516014234875 | DROP → DROP | [0, 120, 700, 562] | gate: too many whole neighbour words |
| calibration | lekythos--3bfc4a385d61b883--s002-l0012 | Longine | 1302×1093 | 1302×1093 | 7 | 1.191216834400732 | DROP → DROP | [0, 0, 1276, 1085] | gate: second complete line |
| typology | ia_greek_latin--a232aaf9a41fe898--s001-l0012 | ***** | 439×427 | 439×427 | 5 | 1.0281030444964872 | DROP → DROP | [0, 0, 439, 427] | length: Too much OCR output for the text box after height normalisation. |
| typology | ia_poly1850--3cbcc415675468a9--s034-l0001 | MELA OF 10 | 700×562 | 700×562 | 8 | 1.2455516014234875 | DROP → DROP | [0, 120, 700, 562] | gate: too many whole neighbour words |
| typology | lekythos--3bfc4a385d61b883--s002-l0012 | Longine | 1302×1093 | 1302×1093 | 7 | 1.191216834400732 | DROP → DROP | [0, 0, 1276, 1085] | gate: second complete line |
| typology | gazette_modern--a895f3d785bb13b6--s000-l0150 | ποσό | 470×2217 | 2217×470 | 4 | 4.717021276595744 | DROP → DROP | [215, 0, 2210, 462] | gate: second complete line |

## Readback and source scope

| Check | Count |
| --- | --- |
| non_small_byte_identical | 966 |
| final_decision_readbacks | 3887 |
| gate_readbacks | 3887 |
| predictor_readbacks | 3514 |
| all_component_boxes_exact | 315 |
| local_crop_paths_inventory_accounted_for | 1103 |
| metadata_dependency_digests | 2 |
| tests passed | 189 |

Every non-small record has byte-identical canonical evidence, binding, frame, warnings, policy hash and final result compared with fresh S3 and saved S3; only tool_version and inherited elapsed seconds are excluded, exactly as in the earlier replay normalization. The three JS policy functions and their file hash are unchanged. Every final result, gate and available predictor result was independently read back. The all-component boxes and matching box/frame padding heights are checked directly.

Changed existing files (exhaustive scope guard):

- `greekocr/harvest/line_pipeline_native.py`
- `greekocr/harvest/filtering_assets/crop-tools.py`
- `greekocr/harvest/filtering_assets/service.mjs`
- `tests/test_seg_curve.py`
- `tests/test_seg_deskew.py`
- `docs/harvest/line_pipeline/tool_versions.json`
- `scripts/harvest/build_filter_versions.py`

New test: `tests/test_seg_small.py`. Existing historical row-frame tests explicitly isolate their historical path; curved/tall synthetic rows now use nine characters to remain outside S4. The new tests cover inclusive boundaries, every component including a diacritic and isolated extracted speck, actual turned crops, padding, and positive gate DROPs with no main row. All native non-small rows are checked against S3 as the population regression. Existing extraction omits area<3 noise; it is unchanged.

No .git writes, commits, pushes, reader runs, remote execution or network access. Package, seg09 and untracked census02 evidence match initial hashes. Metadata refreshes segmentation to 0.9-s4 and the existing census dependency fingerprint only; no census version bump or execution. The lead commits.

Reproduce with sibling sol-recut .venv/bin/python, -B, PYTHONPATH=. and PYTHONDONTWRITEBYTECODE=1: s4/prepare_versions.py; s4/replay.py; s4/replay.py typology; s4/extra_numeric.py; the test command recorded in tests_command.txt; s4/validate_report.py. Clear only generated replay.jsonl before a fresh full run (otherwise it resumes verified complete records). Never recreate initial_hashes.json or baseline/ after source changes.

[Summary](summary.json), [receipt](receipt.json), [scope guard](scope_guard.json), [main replay](replay.jsonl), [typology replay](typology_replay.jsonl), [small diagnostics](small.jsonl), [2×2 predictions](two_by_two_predictions.jsonl), [2×2 flips](two_by_two_flips.jsonl), [tests](tests.log).

SEG S4 READY: small 322 of 1288 replay (+320 typology); gate-abstain moved 37; 150 FP/FN/UNC 17/15/5 → 16/15/0; 888 rated agree 105 → 109/135; owner marks agree 170 → 189/235; typology owner agree 0.8 131 / s3 147 / s4 160 of 185; 2x2 best cell per type numeric:s4/short-numeric / mixed:s3/text-font,s4/text-font,s3/short-numeric,s4/short-numeric / non-numeric:s4/text-font,s4/short-numeric; flips 56; tests 189 passed
