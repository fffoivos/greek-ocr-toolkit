# Page lines, round 2 — 9 October 2026

**Status: PARTIAL.** Code, 48-page artifacts and audits are delivered; the clean one-line OCR acceptance test is not met on every real page.

The pipeline starts with pixel regions bounded by rules and persistent gutters. The existing crop fitter finds all bands inside each region. Letter contacts are pooled into shared geometry; actual bottoms refine the fit so capital tops cannot pull it upward. Facing font lines define a shared midpoint boundary. Original pixels are unrolled with a fixed x-height position. Optional text-layer rectangles record provenance only.

Implementation and measurement definitions: [PAGE_LINE_SEGMENTS.md](../PAGE_LINE_SEGMENTS.md). The original crop implementations are unchanged. The default Docling native-line path is unchanged; its opt-in detector path consumes these strips.

All **1,250/1,250** requested and added tests pass, including the frozen 40-crop set, curl set, provenance/API contracts and Docling contracts. The recognizer is mocked in integration tests. All **48** saved page sets pass the independent array/image audit. All **24** Vouli hint comparisons have exactly identical geometry.

Assigned component ink retained: **99.092%** over the development pages. This is not detection recall or OCR accuracy. Cut flags include ink excluded by a curved seam before whitening, even if white padding keeps the raster edge blank. Raw raster-edge counts and unassigned body-component counts are in the JSON.

## Per-page checks

Seg = pixel segments; Multi = segments referenced by more than one final line; Edge = dark ink touching the delivered top/bottom raster edge; Cut = source-boundary/window cuts or delivered raster-edge ink; Foreign = regions containing another line's assigned component; Cross = detected rule/gutter crossings; Overlap = positive region intersections; Broken = aligned disjoint pairs without a detected stop. Cut/Foreign/Broken are algorithmic diagnostics, not independent manual labels.

| Page | Seg | Lines | Multi | Edge | Cut | Foreign | Cross | Overlap | Broken |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| an-1be60011c435-p000215 | 31 | 56 | 18 | 7 | 31 | 30 | 0 | 0 | 0 |
| an-1c6e1c0e929e-p000167 | 10 | 29 | 6 | 1 | 19 | 19 | 0 | 0 | 0 |
| an-1f8e7d022643-p000003 | 35 | 30 | 10 | 5 | 16 | 15 | 0 | 0 | 7 |
| an-2cfe28da5103-p000135 | 28 | 87 | 16 | 4 | 47 | 44 | 0 | 0 | 0 |
| an-3352d912f2e9-p000104 | 37 | 36 | 11 | 8 | 23 | 22 | 0 | 0 | 0 |
| an-466cffad2cba-p000323 | 21 | 25 | 4 | 0 | 3 | 3 | 0 | 0 | 0 |
| an-5c093c79d6bb-p000199 | 64 | 77 | 20 | 13 | 28 | 19 | 0 | 0 | 0 |
| an-778126cc8c2b-p000010 | 38 | 93 | 24 | 23 | 77 | 82 | 0 | 0 | 4 |
| an-7a2b17a3fb0f-p000200 | 366 | 552 | 140 | 67 | 312 | 294 | 0 | 0 | 22 |
| an-9ea1564fcf4f-p000013 | 59 | 96 | 19 | 20 | 73 | 64 | 0 | 0 | 0 |
| an-a73d22211479-p000301 | 14 | 82 | 11 | 5 | 80 | 78 | 0 | 0 | 2 |
| an-b1a643813945-p000054 | 12 | 28 | 5 | 5 | 24 | 20 | 0 | 0 | 0 |
| an-c153f2c605b3-p000040 | 41 | 42 | 17 | 13 | 35 | 25 | 0 | 0 | 3 |
| an-c2c2053cfc10-p000056 | 38 | 78 | 21 | 2 | 30 | 30 | 0 | 0 | 0 |
| an-c8b96a901917-p000068 | 116 | 128 | 22 | 8 | 35 | 29 | 0 | 0 | 0 |
| an-d6002cf45e4d-p000058 | 40 | 24 | 6 | 13 | 14 | 4 | 0 | 0 | 1 |
| an-d6fd2cf2f618-p000047 | 18 | 43 | 9 | 3 | 34 | 35 | 0 | 0 | 1 |
| an-d83e7a198ade-p000099 | 54 | 100 | 16 | 7 | 56 | 48 | 0 | 0 | 0 |
| an-e46611ae2fcc-p000041 | 29 | 63 | 18 | 4 | 36 | 33 | 0 | 0 | 0 |
| an-e74539ae215c-p000338 | 43 | 91 | 25 | 12 | 70 | 61 | 0 | 0 | 0 |
| an-ef481610a820-p000181 | 39 | 66 | 22 | 36 | 56 | 54 | 0 | 0 | 7 |
| an-fabf591ca801-p000067 | 33 | 75 | 19 | 12 | 43 | 39 | 0 | 0 | 0 |
| an-fd4fa0018ae1-p000037 | 11 | 34 | 7 | 1 | 16 | 12 | 0 | 0 | 0 |
| an-ffccc97c07de-p000152 | 35 | 48 | 21 | 19 | 33 | 26 | 0 | 0 | 5 |
| s2-0683f98f964a6d41cb72-p00003 | 31 | 45 | 11 | 2 | 21 | 20 | 0 | 0 | 0 |
| s2-09f5dfca4af4d74173c6-p00005 | 65 | 60 | 15 | 12 | 32 | 21 | 0 | 0 | 0 |
| s2-0ce9d1025b3f23c7119e-p00001 | 96 | 93 | 31 | 49 | 67 | 50 | 0 | 0 | 1 |
| s2-200e977f2dab5291c42c-p00035 | 146 | 266 | 69 | 24 | 126 | 146 | 0 | 0 | 4 |
| s2-23a70964fda83cb7aeb1-p00003 | 88 | 163 | 37 | 2 | 115 | 121 | 0 | 0 | 2 |
| s2-3229200bf47ca465a42d-p00004 | 23 | 39 | 14 | 5 | 17 | 17 | 0 | 0 | 0 |
| s2-49598b2e848ab1f0ee1e-p00001 | 36 | 120 | 22 | 0 | 45 | 45 | 0 | 0 | 0 |
| s2-5ca02b142a2a3eaf078a-p00002 | 36 | 55 | 15 | 5 | 39 | 39 | 0 | 0 | 1 |
| s2-60f24a3d8a2d714767f2-p00003 | 37 | 121 | 28 | 7 | 85 | 86 | 0 | 0 | 0 |
| s2-63f072d79585d71224b6-p00002 | 22 | 47 | 10 | 0 | 30 | 30 | 0 | 0 | 0 |
| s2-658e6dcb48b540357a9d-p00001 | 46 | 66 | 20 | 9 | 39 | 40 | 0 | 0 | 1 |
| s2-661ddf05c8865e7b2c45-p00009 | 57 | 125 | 32 | 6 | 71 | 66 | 0 | 0 | 0 |
| s2-6f552c96213b4c24a071-p00003 | 27 | 35 | 9 | 5 | 22 | 16 | 0 | 0 | 0 |
| s2-7247ee9b1bc2374b3980-p00001 | 94 | 177 | 42 | 2 | 129 | 125 | 0 | 0 | 4 |
| s2-74cdb23a34ca4a6cd01e-p00002 | 123 | 231 | 67 | 18 | 182 | 163 | 0 | 0 | 13 |
| s2-77d1bd63d5babbe0df73-p00001 | 24 | 40 | 9 | 0 | 16 | 14 | 0 | 0 | 0 |
| s2-831443dc5e6f1ccfbaf5-p00020 | 155 | 400 | 68 | 29 | 102 | 115 | 0 | 0 | 3 |
| s2-86865c33eef5932c013b-p00005 | 17 | 52 | 11 | 13 | 48 | 47 | 0 | 0 | 2 |
| s2-93f8070059f938bda524-p00001 | 114 | 187 | 56 | 31 | 129 | 126 | 0 | 0 | 8 |
| s2-9de6cda8f03f0fc60a58-p00005 | 61 | 122 | 28 | 3 | 85 | 79 | 0 | 0 | 0 |
| s2-be269b8c315b16befc35-p00002 | 45 | 54 | 12 | 0 | 32 | 32 | 0 | 0 | 0 |
| s2-d1ed1c2db37f431f4acb-p00001 | 85 | 164 | 56 | 49 | 142 | 138 | 0 | 0 | 3 |
| s2-dfcc21869afc140111ce-p00001 | 62 | 134 | 32 | 14 | 115 | 112 | 0 | 0 | 2 |
| s2-f9ec82212abc808325d7-p00010 | 20 | 39 | 12 | 2 | 27 | 26 | 0 | 0 | 0 |
| **Total** | 2722 | 4818 | 1193 | 575 | 2907 | 2760 | 0 | 0 | 96 |

## Independent curl contacts

The frozen crop pixels were verified to match their registered locations on the page exactly. The nearest corresponding detected line is evaluated; this is a geometry check, not a detection-recall score.

| Frozen crop | Covered contacts | Median error px | Maximum error px |
|---|---:|---:|---:|
| 17 | 9/9 | 0.40 | 1.61 |
| 18 | 8/8 | 1.03 | 1.57 |
| 21 | 10/10 | 1.14 | 2.10 |
| 23 | 10/10 | 0.93 | 10.19 |
| 25 | 10/10 | 1.39 | 2.32 |
| 29 | 11/11 | 0.65 | 1.95 |
| 30 | 8/8 | 1.34 | 2.71 |
| 32 | 8/8 | 0.87 | 2.10 |
| 35 | 9/9 | 0.98 | 1.70 |

## What remains wrong

* `an-1f8e7d022643-p000003`: the ornamental title border still produces false text bands. Decorative initials can also lose part of their extent.
* `an-d6002cf45e4d-p000058`: some engraving details still receive lines; illustration rejection is incomplete.
* `an-778126cc8c2b-p000010` and `an-ef481610a820-p000181`: bleed-through, staining and stamps still confuse line identity and introduce extra bands.
* `an-d83e7a198ade-p000099`: the small-type footnote columns are not separated reliably. Zero detected-stop crossings does not establish that every true column boundary was detected.
* `an-7a2b17a3fb0f-p000200`, `s2-200e977f2dab5291c42c-p00035`, and `s2-831443dc5e6f1ccfbaf5-p00020`: table pieces remain imperfect; some small cells are missed or split and some neighbouring ink remains. No table structure is inferred.
* `s2-09f5dfca4af4d74173c6-p00005`, `s2-0ce9d1025b3f23c7119e-p00001`, `s2-74cdb23a34ca4a6cd01e-p00002`, `s2-d1ed1c2db37f431f4acb-p00001`, and `s2-dfcc21869afc140111ce-p00001`: faint dense print still produces weak/extra bands. The measurements do not establish OCR-ready purity.
* `an-ffccc97c07de-p000152`: connected Arabic-script words are less reliable than the Greek body text; some pieces are split or missed.
* `s2-49598b2e848ab1f0ee1e-p00001`: the bottom-contact refinement improves the reviewed capital starts, but the left-end contacts of frozen crop 23 remain outside the crop tool's 6-pixel maximum-error criterion. The crop-level regression itself still passes unchanged.
* Midpoint seams can cut tight accents/descenders. The output deliberately reports those pixels rather than concealing the problem with extra white padding or component erasure. Spatial lane IDs and reading order remain approximate in changing layouts.

No held-out pages were inspected. The other OCR text in the optional hint files was not used as a reference. This round is a reproducible implementation and review result, not a claim that the clean-line goal is solved.

## Artifacts and reproduction

The 48 source-size overlays, fixed-scale unrolled sheets, pixel segment JSON, final line JSON and per-page checks are in `.astra/out/`. `artifact_audit.json` binds their hashes; `curl_contacts.json` binds the frozen contact audit. These large artifacts are local/ignored; this report and its companion JSON are part of the code handoff.

Use the commands in `docs/PAGE_LINE_SEGMENTS.md`; all runs here used the brief's venv Python, `PYTHONDONTWRITEBYTECODE=1`, and pytest `-p no:cacheprovider`. No background job, network push or OCR model inference was launched.
