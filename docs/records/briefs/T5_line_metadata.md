# T5 — greekocr.annotate.line_features: rich per-line metadata for real lines (gpt-6.1-sol, xhigh). Workspace = this repo. No `.git` writes
(T5_HANDOFF.json). No network, no GPU; CPU-only numpy/scipy/Pillow (+ optional torch for the font classifier, lazily imported).
Owner (8 Oct 2026, 13:55): "we still need good metadata on the real lines so that we can manipulate those mixes: font, percent letters take in
the line, bg colour (off colouring), contrast between letters, n of letters in a line, year of writing, polytonic, and so on."
Design: ONE vocabulary shared with the synthetic lines (see the recipe fields in greekocr/_vendor + docs: font, severity, bg_type, polarity,
applied_ops, script_class) so mixes can be balanced on the same axes and the recipe can be fitted to real distributions.
Build:
1. `line_features(image, text=None, *, geometry=None) -> LineFeatures` (frozen dataclass, JSON-serialisable; every field documented):
   image: height_px, width_px, aspect, ink_coverage (dark fraction in the line band), background_level, background_rgb/cast (if RGB),
   contrast (ink median vs background median; local contrast p10/p90), stroke_width_px (distance-transform median), xheight_px,
   capheight_ratio, polarity, blur (Laplacian variance), noise (speckle count/small components), curl_px/skew_deg/clipped_edges (from the
   geometry diagnostics when given); text: n_chars, n_words, script_class (reuse the vendored line_categories rules), polytonic_mark_density,
   digit_ratio, punct_ratio, upper_ratio, language_guess (el/grc/en/fr/other, rule-based), lexicon_validity (fraction of words in a Greek
   lexicon file the caller supplies; None if absent).
2. `font_estimate`: a small classifier (CPU, torch optional) trained on synthetic line shards where the font is known: predicts font family
   id + style class {didot_greek_19c, modern_serif, sans, mono, script/other}; ships a training script over an existing synthetic shard
   directory and a fixture-sized model for tests (no real training in this job; document the training command).
3. `source_metadata(record, catalogue) -> dict`: year (from catalogue fields: parliament year, Anemi year, IA date, web fetched_at), collection,
   doc_type {proceedings, gazette, book, newspaper, web, born_digital_article}, licence/tier, page_position {header, footer, body, column_k}
   when geometry allows.
4. `annotate_records(records_jsonl, out_jsonl, *, catalogue=None, lexicon=None)` CLI `greekocr annotate lines`, and
   `distribution_report(out_jsonl) -> markdown` (`greekocr annotate report`): per source, histograms/quantiles of every numeric feature and
   counts of every categorical one, so the owner can see what a supply contains; the same report over a synthetic shard for comparison.
5. `strata.py`: stratum key = (script_class, polytonic, doc_type, year_bucket, contrast_bucket, ink_bucket, font_style); helpers to compute
   per-stratum counts and to produce sampling weights with floors (inputs to a future weighted mix).
Tests on tests/fixtures/o4d_lines (44 strips: features computed, ranges sane, determinism) + a synthetic-style fixture with known font.
Docs: docs/A_ocr_development/reference/LINE_METADATA.md (field table with derivation and units). Last line exactly: `T5: done | tests: <n> passed`.
