# Readability calibration (docs/records/glyphs/GLYPHS_CALIBRATION.md)

1. `calib_strips.py OUT_DIR TEXT_DIR [LINES_PER_CONDITION]` — synthetic strips, one controlled degradation each
   (v2 conditions: clean, accent_cut, top_cut, tail_cut, bottom_cut, fade, thin, break, thick, skew) + manifest.jsonl.
2. An OCR reader writes `predictions_<reader>.jsonl` (line_id, text) next to the manifest (CLLG / E1 were run on the
   GPU node by the coordinator).
3. `calib_measure.py OUT_DIR` — the glyph tools' measurements of every strip → measurements.jsonl.
4. `calib_analyse.py OUT_DIR predictions_<reader>.jsonl` — CER by condition and by measured level; limits.

Data of the 8 Oct run: ~/Projects/glossapi-ocr-local/experiments/glyphs_calib/strips_v{1,2}{,_straight,_tight_*}/.
