# T15 — Native real-page reads

**253 pages, 500 frozen sampled lines, 506 successful calls.** Page vs crop exact NFD identity: Vision **43.0%**, DocAI **53.4%**. Strict cross-reader tier-1 yield moves from **37.6%** in crop mode to **27.6%** in page mode.

These measurements describe transcription preservation, mapping and harvest yield; they do not establish which reading is accurate. [Blind owner review](page_reads_v1/blind_review.html) contains 30 changed lines and 10 largest changes with native context. The separate blind key is deliberately unlinked from that page.

## Preservation and confidence

| Cohort | Reader | Lines | Exact NFD | Letters+marks | Merged | Lost | Split | Rejected | Crop symbol mean (n) | Page symbol mean (n) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALL | vision | 500 | 43.0% (215) | 49.2% (246) | 105 | 112 | 18 | 151 | 0.882120 (23455) | 0.880657 (22617) |
| ALL | docai | 500 | 53.4% (267) | 60.2% (301) | 108 | 139 | 9 | 175 | 0.942050 (23607) | 0.941925 (21919) |
| decade 1860 | vision | 51 | 31.4% (16) | 35.3% (18) | 13 | 14 | 4 | 20 | 0.866203 (2432) | 0.864669 (2303) |
| decade 1860 | docai | 51 | 43.1% (22) | 51.0% (26) | 13 | 18 | 2 | 23 | 0.934531 (2431) | 0.931570 (2209) |
| decade 1870 | vision | 51 | 43.1% (22) | 52.9% (27) | 13 | 10 | 7 | 16 | 0.884198 (2419) | 0.880456 (2208) |
| decade 1870 | docai | 51 | 49.0% (25) | 58.8% (30) | 16 | 16 | 1 | 20 | 0.941555 (2419) | 0.942847 (2059) |
| decade 1880 | vision | 80 | 50.0% (40) | 53.8% (43) | 18 | 20 | 3 | 25 | 0.881123 (3779) | 0.879535 (3749) |
| decade 1880 | docai | 80 | 53.8% (43) | 56.2% (45) | 18 | 26 | 3 | 29 | 0.945961 (3806) | 0.946490 (3640) |
| decade 1890 | vision | 74 | 45.9% (34) | 55.4% (41) | 12 | 17 | 0 | 19 | 0.882865 (3214) | 0.880157 (3078) |
| decade 1890 | docai | 74 | 51.4% (38) | 60.8% (45) | 12 | 22 | 1 | 24 | 0.937394 (3235) | 0.937406 (3003) |
| decade 1900 | vision | 86 | 41.9% (36) | 47.7% (41) | 24 | 12 | 4 | 28 | 0.883256 (4129) | 0.882389 (4069) |
| decade 1900 | docai | 86 | 53.5% (46) | 59.3% (51) | 22 | 18 | 1 | 33 | 0.938399 (4153) | 0.937762 (4001) |
| decade 1910 | vision | 68 | 44.1% (30) | 50.0% (34) | 10 | 19 | 0 | 20 | 0.885697 (3284) | 0.885389 (3305) |
| decade 1910 | docai | 68 | 54.4% (37) | 61.8% (42) | 10 | 19 | 0 | 21 | 0.948105 (3345) | 0.948012 (3132) |
| decade 1920 | vision | 84 | 42.9% (36) | 47.6% (40) | 11 | 17 | 0 | 19 | 0.886531 (3969) | 0.885298 (3682) |
| decade 1920 | docai | 84 | 64.3% (54) | 71.4% (60) | 13 | 17 | 1 | 21 | 0.945517 (3989) | 0.946019 (3703) |
| decade 1930 | vision | 6 | 16.7% (1) | 33.3% (2) | 4 | 3 | 0 | 4 | 0.887022 (229) | 0.895195 (223) |
| decade 1930 | docai | 6 | 33.3% (2) | 33.3% (2) | 4 | 3 | 0 | 4 | 0.945268 (229) | 0.943975 (172) |
| body_1column | vision | 300 | 44.0% (132) | 50.0% (150) | 57 | 69 | 15 | 92 | 0.880268 (13999) | 0.878864 (13679) |
| body_1column | docai | 300 | 54.7% (164) | 60.7% (182) | 59 | 88 | 8 | 107 | 0.941010 (14071) | 0.940532 (13334) |
| body_2column | vision | 200 | 41.5% (83) | 48.0% (96) | 48 | 43 | 3 | 59 | 0.884863 (9456) | 0.883402 (8938) |
| body_2column | docai | 200 | 51.5% (103) | 59.5% (119) | 49 | 51 | 1 | 68 | 0.943585 (9536) | 0.944088 (8585) |

All 500 lines stay in the identity denominators, including mapping failures and the 13 originally rejected crop pairs. Exact comparison is NFD on the cleaned readings, preserving internal whitespace and glyphs. Letters+marks uses the unchanged T14b apostrophe-unification helper, retains case and combining marks, and ignores punctuation, numbers and word boundaries. Empty==empty is possible in preservation but never earns HARVEST agreement.

Symbol means weight every reported assigned symbol equally; counts differ with transcription and geometry. Page symbols use the same polygon rule independently of line assignment, so their confidence can remain measurable for a merged/lost line. These means are not accuracy estimates or paired symbol calibration.

## HARVEST yield on the same lines

| Cohort | Mode | Lines | Usable pairs | Tier-1 strict exact | Letters agree | Pilot tier-1 including substitutions |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ALL | crop | 500 | 487 | 37.6% (188) | 50.4% (252) | 37.6% (188) |
| ALL | page | 500 | 312 | 27.6% (138) | 36.4% (182) | 27.6% (138) |
| decade 1860 | crop | 51 | 48 | 39.2% (20) | 52.9% (27) | 39.2% (20) |
| decade 1860 | page | 51 | 24 | 13.7% (7) | 21.6% (11) | 13.7% (7) |
| decade 1870 | crop | 51 | 46 | 35.3% (18) | 49.0% (25) | 35.3% (18) |
| decade 1870 | page | 51 | 29 | 21.6% (11) | 31.4% (16) | 21.6% (11) |
| decade 1880 | crop | 80 | 80 | 55.0% (44) | 63.8% (51) | 55.0% (44) |
| decade 1880 | page | 80 | 50 | 36.2% (29) | 45.0% (36) | 36.2% (29) |
| decade 1890 | crop | 74 | 74 | 33.8% (25) | 44.6% (33) | 33.8% (25) |
| decade 1890 | page | 74 | 50 | 36.5% (27) | 43.2% (32) | 36.5% (27) |
| decade 1900 | crop | 86 | 81 | 34.9% (30) | 45.3% (39) | 34.9% (30) |
| decade 1900 | page | 86 | 50 | 19.8% (17) | 26.7% (23) | 19.8% (17) |
| decade 1910 | crop | 68 | 68 | 39.7% (27) | 58.8% (40) | 39.7% (27) |
| decade 1910 | page | 68 | 47 | 33.8% (23) | 44.1% (30) | 33.8% (23) |
| decade 1920 | crop | 84 | 84 | 26.2% (22) | 40.5% (34) | 26.2% (22) |
| decade 1920 | page | 84 | 60 | 28.6% (24) | 39.3% (33) | 28.6% (24) |
| decade 1930 | crop | 6 | 6 | 33.3% (2) | 50.0% (3) | 33.3% (2) |
| decade 1930 | page | 6 | 2 | 0.0% (0) | 16.7% (1) | 0.0% (0) |
| body_1column | crop | 300 | 293 | 39.7% (119) | 51.0% (153) | 39.7% (119) |
| body_1column | page | 300 | 184 | 29.3% (88) | 37.0% (111) | 29.3% (88) |
| body_2column | crop | 200 | 194 | 34.5% (69) | 49.5% (99) | 34.5% (69) |
| body_2column | page | 200 | 128 | 25.0% (50) | 35.5% (71) | 25.0% (50) |

HARVEST denominators include every line. Agreement requires two service-OK, nonempty, non-rejected readings. Strict tier-1 is exact NFD equality as requested; letters agree is the T14b letters+marks equality. The additional pilot tier-1 column runs the original `core.tier` rule with whitespace normalization and only its documented substitutions. This avoids silently conflating strict equality, punctuation-free agreement and pilot substitution acceptance. Pilot whitespace-exact counts are also retained in summary.json.

## Rendering, mapping and custody

The supplied PDFs and native PNGs were relocated into the external pilot archive. Read-only resolution uses their `/harvest_big/` suffix; resolved paths and hashes are in [manifest.json](page_reads_v1/manifest.json). All 253 PDFs match their recorded SHA-256 fetch receipts and sampled-record PDF hashes. All 253 re-rendered PNGs are byte-identical to archived native pilot PNGs. Pilot page JSON records PDF hashes and render parameters, but no independent PNG hash; the surviving native PNG is the additional byte-identity check. Renderer: pypdfium2 5.14.0 / PDFium 156.0.8076.0; scale 200/72, grayscale L, PNG compress_level=1, PDF page index 0. No straightening, scaling, cropping or synthetic layout is applied to submitted pages.

DocAI line layout boxes (paragraph fallback only if no lines) and Vision symbol-break line unions are extracted by the unchanged T14 helpers. Coordinates are in the original rendered page pixels. Targets are exactly the sampled polygons on each page; unsampled returned lines remain unassigned. For a returned rectangle and target polygon, horizontal overlap must be ≥50% of the shorter projected width. Vertical overlap is the mean height of the returned box inside the polygon band over their shared x span: exact polygon clipping integrates sloped bands, divided by shared width and returned box height. Width outside the polygon does not dilute this height fraction. The threshold is ≥70%. Edge-only contact has zero overlap. Any returned box with positive polygon intersection with two sampled targets marks every touched target merged, even when only one meets the thresholds; no merged box is assigned or guessed. Zero uniquely assigned boxes is lost; ≥2 is split. Flags are independent. Side-by-side pieces use the unchanged pilot list-return rule in x order; stacked/obstructed readings retain rejection. Each of the 506 [assignment files](page_reads_v1/assignments/) includes all returned boxes, overlaps, symbols, withheld boxes, raw-response hash and target results.

DocAI returned one page in a deskewed frame (2097×1545 pixels versus submitted 2017×1430), with a recorded affine transform. Its reported polygon vertices are mapped back through the inverse matrix before forming native-page line/symbol rectangles. The other 252 DocAI pages have matching native dimensions and no transforms. Every assignment records native/returned dimensions, conversion status and inverse matrix; transformed pieces also retain their reported bbox. No image or raw response is changed. This uses the [Document AI recorded image transforms](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document#Page), and the one-page inverse was checked against native ink with a review overlay. Eight offline cases cover float32/float64 matrices, normalized-only vertices, transform composition, singular/nonfinite refusal and frame mismatch without a transform.

Mapping cannot detect merges involving only an unsampled neighbor. This is a stated limit of the sampled-target rule; the blind context panels expose neighboring physical rows. The sample covers body_1column and body_2column pages only, and is book-balanced rather than a population sample.

Same pilot reader bindings: Vision DOCUMENT_TEXT_DETECTION, el+grc, provider default unpinned; DocAI EU processor 9a98b7aca3c19561, pretrained-ocr-v2.1-2024-08-07, el, symbols enabled. The previous single-crop controls were deterministic, but time-separated cached baselines and an unpinned Vision model remain a limitation.

## Failure examples

Merged is the requested conservative **box-touch flag**, not proof that a provider transcribed two physical lines as one. This distinction matters on genuine pages: a correct-looking line rectangle can touch the padded polygon of its neighbor, and the axis-aligned box of a rotated watermark can touch multiple sampled polygons. Both are withheld by the specified rule.

| Reader | Merged boxes | No target meets both thresholds | One qualified target + another touch | ≥2 qualified targets |
| --- | ---: | ---: | ---: | ---: |
| vision | 81 | 21 | 60 | 0 |
| docai | 93 | 32 | 61 | 0 |

Review overlays use green for the target polygon, amber for other sampled polygons, and red for returned line rectangles. They are never sent to OCR. Failure examples are selected outside the blind cards; lost examples preferentially have no merge flag.

- vision merged: `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0004`; assigned boxes=0; flags=['empty']; [native geometry overlay](page_reads_v1/failure_images/vision-merged.png), [raw-bound mapping](page_reads_v1/assignments/anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038.vision.json). First returned-box overlaps=[{'anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0004': {'height': 0.0857, 'horizontal': 1.0}, 'anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0006': {'height': 0.9546, 'horizontal': 1.0}}]. Crop="ποῦ ἀφροκοπᾷ τὸ νερόν, πλένουν αἱ πλαστικαὶ κόραι τοῦ δρυμοῦ."; page="".
- vision lost: `anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0011`; assigned boxes=0; flags=['empty']; [native geometry overlay](page_reads_v1/failure_images/vision-lost.png), [raw-bound mapping](page_reads_v1/assignments/anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049.vision.json). First returned-box overlaps=[{'anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0011': {'height': 0.1953, 'horizontal': 1.0}}]. Crop="σταται ἀλλ᾽ ἁπλῶς συμπληρούται ὑπὸ τῆς κατὰ μῆκος"; page="".
- vision split: `anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022`; assigned boxes=3; flags=['list_return', 'obstructed']; [native geometry overlay](page_reads_v1/failure_images/vision-split.png), [raw-bound mapping](page_reads_v1/assignments/anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138.vision.json). First returned-box overlaps=[{'anemi-0bff55647d1c2acd1caa8bf3-vff5eb426-p000138-l0022': {'height': 0.9333, 'horizontal': 1.0}}]. Crop=""; page="Εἰς Βενετίαν ἐνθυμεῖσαι τοῦ Δανδόλου τὸν ἐρα-\nσου.\n-".
- docai merged: `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0004`; assigned boxes=0; flags=['empty']; [native geometry overlay](page_reads_v1/failure_images/docai-merged.png), [raw-bound mapping](page_reads_v1/assignments/anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038.docai.json). First returned-box overlaps=[{'anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0004': {'height': 0.1514, 'horizontal': 0.2462}, 'anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0006': {'height': 0.1475, 'horizontal': 0.2764}}]. Crop="ποῦ ἀφροκοπᾷ τὸ νερόν, πλένουν αἱ πλαστικαὶ κόραι τοῦ δρυμοῦ."; page="".
- docai lost: `anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0011`; assigned boxes=0; flags=['empty']; [native geometry overlay](page_reads_v1/failure_images/docai-lost.png), [raw-bound mapping](page_reads_v1/assignments/anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049.docai.json). First returned-box overlaps=[{'anemi-0550c3c52f2b388255690d5a-vb62dffa6-p000049-l0011': {'height': 0.1667, 'horizontal': 1.0}}]. Crop="σταται ἀλλ᾽ ἁπλῶς συμπληροῦται ὑπὸ τῆς κατὰ μῆκος"; page="".
- docai split: `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038`; assigned boxes=2; flags=['list_return', 'horizontal_pieces_joined']; [native geometry overlay](page_reads_v1/failure_images/docai-split.png), [raw-bound mapping](page_reads_v1/assignments/anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023.docai.json). First returned-box overlaps=[{'anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038': {'height': 0.9361, 'horizontal': 1.0}}]. Crop="λιπεν ἡ ζῶσα πηγὴ νέων δημιουρ· fertigkeit vermehrte sich so-"; page="λιπεν ἡ ζῶσα πηγὴ νέων δημιουρ· fertigkeit vermehrte sich so-".

## Cost and verdict

**506 reserved calls, USD 0.7590 conservative list-price receipt, cap USD 2.00.** 253 successful calls per reader; zero crop calls and zero retries. Rate USD 0.0015 per page/image, checked 13 October 2026 against [Vision pricing](https://cloud.google.com/vision/pricing) and [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Free monthly allowances are not deducted; this is not a billing invoice. [Persistent cost receipt](page_reads_v1/cost_receipt.json). Raw responses, adapter receipts, reservations and page images are under ignored `docs/records/harvest/harvest_big/page_reads_v1/`.

Reservations precede network I/O under locks; all attempts stay reserved, including ambiguous failures. Successful responses are reused; failed/interrupted reservations are never automatically retried. The exact 506-call ceiling is stricter than the requested ≤600. Three pages may be in flight; DocAI starts share the T14 rate lock. Offline rebuild and validation make no service calls and need no ADC.

For this sparse sample, page mode uses 253 vs 500 calls per reader: **49.4% fewer calls**, USD 0.759 vs USD 1.500 for both readers. Per 1,000 sampled lines: USD 0.759 per reader / USD 1.518 combined vs crop USD 1.500 / USD 3.000. Reading every eligible line on these pages could amortize page costs further; that coverage was not measured.

**Measured substitution verdict:** page mode changes 57.0% of Vision readings and 46.6% of DocAI readings, with merged/lost 105/112 and 108/139. It therefore does not meet the earlier ≥97% preservation / zero merged-lost gate for a drop-in crop substitute. Strict tier-1 yield changes by -10.0 percentage points; letters-agreement yield changes by -14.0 points. Its usability as an accuracy-changing harvest alternative remains for the owner's blind check. Agreement alone cannot establish correctness.

## Blind review and validation

Exactly 10 Vision-only, 10 DocAI-only and 10 both-changed lines selected from candidate pools {'vision_only': 102, 'docai_only': 50, 'both': 183}; stable sorted IDs, seed 15, shuffled card order and independent reader A/B order. The HTML contains inlined native straight crops, escaped readings and local downloadable choices, with no key/source/stratum labels. The top ten are ranked by summed NFD edit count (ties by ID), each with a separate native page region ±2 detected rows in the same column; context coordinates and row IDs are only in blind_key.json. The review is a purposive change sample, not a random accuracy estimate.

Offline tests cover polygon slopes and horizontal overlap, exact threshold boundaries, edge contact, merged/lost/split independence, side-by-side joins, rejected stacked pieces, symbol assignment, empty/rejected HARVEST pairs, blinded stratification, deterministic independent A/B order, HTML escaping and inlined context. [Test receipt](page_reads_v1/tests.xml), [offline replay](page_reads_v1/validation.json), [source/data inventory](page_reads_v1/inventory.json), [Git metadata audit](page_reads_v1/git_audit.json). Replay verifies every assignment, metric, baseline/raw/cache hash, reservation and review card. Browser layout QA status is recorded separately in gallery_qa.json.
