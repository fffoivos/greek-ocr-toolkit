# T7 — greekocr.verify: readability checks on images (A) and text checks on readings (B), calibrated on samples (gpt-6.1-sol, xhigh)
Workspace = this repo. No `.git` writes (T7_HANDOFF.json). Network ON only for `codex exec` calls to the vision/text judge (model id
`gpt-6-luna`, Codex CLI 0.159.2; images via `codex exec -i <png> ...`; flags `-c features.remote_plugin=false -c features.apps=false
--ephemeral -c project_doc_max_bytes=0`, `--output-schema` for JSON) and for pip. Budget: ≤ 500 Luna calls in this job.
Owner (8 Oct 14:10): "we need to be checking (A) the images, e.g. with Luna, and (B) the lines: is the output even good Greek? ... our goal
is first to assess the readability of each image with reliable, automated, low-cost methods: skew, does the line trail upwards or downwards,
are the letters touching the limits of the line, letter clarity, are the letters obstructed by something, and other features I haven't
detected so far." The PDF text layer is NEVER a reference (it is another OCR); it may appear only as a labelled diagnostic column.
Samples: tests/fixtures/o4d_lines (44 strips + owner notes in index.json) and tests/fixtures/o4d_sample400 (400 crops; index.json has the
layer text and the CLLG reading per crop).
Build:
A. `greekocr.verify.image_checks(crop) -> ImageChecks` (CPU, < 20 ms per crop, numpy/scipy/Pillow): skew_deg (ink-row profile / Hough on
   baseline), trail {up, down, flat} with amplitude px (baseline y at the left vs right 15%), edge_touch {top, bottom, left, right} (ink on
   the border rows/cols), clarity (Laplacian variance, stroke-width consistency, contrast p10–p90), obstruction score (non-letter components:
   very large/long components, rules, blobs with low aspect regularity, bleed-through = faint mirrored ink), crowding (neighbour-line ink
   fraction in the top/bottom 20%), residual anomaly score (distance of the crop's feature vector from the sample distribution). Every field
   documented with its unit and a threshold suggestion. Reuse greekocr.real.geometry diagnostics where they exist.
A2. LOCALISATION (owner, 14:15): "we should also be able to say with accuracy which parts of the line have these issues, and to what
   intensity, as simple 2d functions." Every image check is a function of position along the line, not only a scalar:
   `readability_profile(crop) -> Profile` with per-column arrays (length = crop width, also downsampled to 64 bins): visible_fraction[x]
   (fraction of the expected glyph band that contains ink support; the band is estimated from the line's own letters where they are complete),
   clip_top[x], clip_bottom[x] (ink touching the border at that column), baseline_offset[x] (the trail), local_contrast[x], blur[x],
   obstruction[x] (foreign ink density), neighbour[x] (ink in the top/bottom margins); plus `quality_map` = a low-resolution 2-D map (e.g.
   16 rows × 64 cols) combining them, and `segments`: contiguous x-ranges where readability < threshold with their intensity. The per-line
   scalars in A are summaries of these functions. Required test (owner's example): fixture
   tests/fixtures/o4d_lines/regressions/s2-60f24a3d8a2d714767f2-p00003-l00024_old.png — a well-cut crop whose first letters are only about
   a quarter visible: the profile must mark the first ~20% of the width as unreadable (visible_fraction low, clip flagged) and the rest as
   readable. Provide `render_overlay(crop, profile) -> PNG` (the crop with the quality map/segments drawn) for the owner's artifact.
B. `greekocr.verify.vlm_annotate(crops, *, model='gpt-6-luna', schema=READABILITY_SCHEMA)`: one Codex call per crop (or small batches of
   ≤4 crops per call with numbered images) returning JSON: readable {yes, partly, no}, defects ⊂ {skew, trails_up, trails_down,
   touches_top, touches_bottom, cut_left, cut_right, blurred, low_contrast, obstructed, neighbour_intrusion, two_lines, empty, other},
   other_text (free), transcription_attempt (optional). Record receipts (model from the rollout, prompt sha, cost). Run it on the 44 + 400
   crops (≤ 500 calls) and store results in docs/verify/vlm_readability_sample.jsonl.
C. `greekocr.verify.text_checks(text) -> TextChecks`: is_greek_script ratio, lexicon_validity (ship a small Greek word list built from the
   fixtures' CLLG readings is NOT allowed; use a bundled frequency list if one exists in the vendor tree, else leave None and document),
   polytonic_consistency (breathing on initial vowels, accent per word, impossible mark stacks), garbage score (runs of consonants, mixed
   scripts inside a word, symbol density), and `llm_judge(text, model='gpt-6-luna')` returning {good_greek: yes/partly/no, problems: [...]}
   with a cached, ≤ 200-call run over the 400 CLLG readings → docs/verify/llm_text_judgements.jsonl.
D. `greekocr verify calibrate`: compare A's cheap features with B's VLM labels (and the owner's 7 notes): per defect, precision/recall of
   simple thresholds; write docs/verify/CALIBRATION.md with the confusion tables and the suggested thresholds; list defect categories the
   VLM named that A has no feature for ("other features not yet detected").
E. CLI: `greekocr verify images DIR`, `greekocr verify text FILE`, `greekocr verify vlm DIR`, `greekocr verify calibrate`.
Tests: offline for A/C/D (mock the Codex call for B); real calls only in the one-off runs above. Docs: docs/VERIFY.md.
Last line exactly: `T7: done | tests: <n> passed | vlm_calls: <n>`.
