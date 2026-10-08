# T2 — O4d G1: ink-refined line extraction with baseline fit, two-line split and a scan-mode geometry gate (gpt-6.1-sol, xhigh)
Workspace = this repo (greek-ocr-toolkit). No `.git` writes (leave `T2_HANDOFF.json`). No network, no GPU. Follow docs/STANDARD.md.
Problem (owner, 8 Oct 2026; plan O4d): on bound 1850s scans the text-layer line boxes fail by geometry: (i) lines curl toward the gutter so a
straight box clips the top/bottom of words at one end and the neighbouring line intrudes there; (ii) one box spans two lines; (iii) the last
glyph is clipped at the right edge; (iv) end-of-line hyphens are dropped by the text layer (and by CLLG). The vendored extractor
(`greekocr/_vendor/bench/o4b_textlayer_lines.py`, admission flags unexplained_ink / missing_ink / ink_bbox_error / multiline_ink /
blank_ink / cross_column) was calibrated for born-digital glyph boxes; on scans it rejects every line (vouli_v6: 5,003/5,003 silver lines
admitted:false, all with unexplained_ink and ink_bbox_error > 0). Fixtures: tests/fixtures/o4d_lines/ (44 strips + index.json with the
owner's notes on the first lines: trailing up/down ends, neighbour intrusion, two lines in one box, clipped final ς, missing hyphen).
Build `greekocr.real.geometry` (typed API + tests):
1. `refine_line(page_image, box, *, pad) -> LineCrop`: ink connected components inside the (padded) box → drop components whose vertical
   centre lies on a second baseline cluster (neighbour) → fit a quadratic baseline to the bottoms of the remaining components (robust fit,
   e.g. RANSAC/Huber) → sample the strip along the curve (local rectification: for each column x take rows baseline(x)-ascent..+descent)
   → extend the box horizontally to the ink extents (recovers clipped glyphs) → return the rectified crop, the fitted curve, the kept/dropped
   components and diagnostics (curl amplitude in px, x-height estimate, n_baselines).
2. `split_multiline(box, components) -> [box, ...]`: two baseline clusters → two boxes (per-line text assignment left to the caller).
3. `scan_admission(diagnostics, *, profile='scan') -> Admission`: a geometry gate for scans with an OCR text layer: admit when
   n_baselines == 1, curl amplitude ≤ τ_curl, ink coverage of the strip within [a, b], no blank strip; `unexplained_ink`/`missing_ink`
   become diagnostics (not rejections) under profile 'scan'; profile 'born_digital' keeps the vendored rule. Thresholds are named constants
   with a short justification; record them in the Admission receipt.
4. `hyphen_at_line_end(crop, text) -> bool`: an ink component after the last glyph with hyphen geometry (short, thin, vertically centred on
   the x-height) when `text` has no trailing hyphen → flag `hyphen_missing_in_label`.
5. A page-level driver `refine_page_lines(pdf_page_image, text_layer_boxes) -> [LineCrop]` and a CLI `greekocr geometry refine`.
Tests: on the fixtures prove (a) the two-line fixture splits; (b) curled fixtures' rectified strips contain the ink at both ends (compare the
ink-row profile at the left and right 15% of the strip before/after); (c) the clipped-ς fixture extends; (d) hyphen detection on the hyphen
fixture; (e) scan_admission admits ≥ 80% of the 44 strips while born_digital admits none; (f) determinism. Document in docs/API.md and
docs/O4D_GEOMETRY.md (method, thresholds, what is NOT solved: page-level dewarp (G3) and Kraken segmentation (G2) are separate arms).
Last line exactly: `T2: done | tests: <n> passed`.
