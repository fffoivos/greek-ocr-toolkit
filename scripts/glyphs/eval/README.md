# Glyph-model evaluation scripts

All take `DIR` = a directory holding `poly_lines.jsonl` (made by `extract_poly_lines.sh DIR`) and read fonts from
`~/Projects/greek-page-ocr/assets/fonts` (fonts passing `font_supports_polytonic`; italics and mono excluded; every
rendered text is checked with `font_covers`). Run from the repo root: `.venv/bin/python scripts/glyphs/eval/<script> DIR …`.
Truth comes from the renderer alone (letter-id map, true baseline and x-height, noise-free oracle ink); see
`greekocr/glyphs/evaluate.py`.

| script | arguments | seed | produces |
|---|---|---|---|
| common.py | — | — | font/text setup; renders restricted to covered text |
| mark_stats.py | DIR [N=250] | 5 | uncensored gap distributions + threshold sweep for NEIGHBOUR_GAP_ABOVE/BELOW |
| eval_glyphs.py | DIR N SEED P_NEIGHBOURS | as given (300 11 1 quoted) | marks, neighbour recall, letter boxes, letter states |
| broken_eval.py | DIR [N=150] | 2 | letter states under injected defects (fade/thin/break/thick), per-defect breakdown |
| double_eval.py | DIR [N=200] | 61 | double-line flag on crops with a full second line vs single crops with neighbour tips |
| skew_eval.py | DIR [N=200] | 31 | skew error on straight lines (all / high-confidence) and baseline error on bent lines |

Removed in the CP-G1 fixes: `ink_eval.py` (fitted weights of the old ink score, replaced by letter states) and
`xh_est.py` (one-off comparison behind the `substantial_letters` x-height switch; its result is quoted in
components.py). Historical numbers from before 8 Oct 15:00 are not reproducible with the current scripts.
