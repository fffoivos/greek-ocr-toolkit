# Glyph-model evaluation scripts (8 Oct 2026)

All take `DIR` = a directory holding `poly_lines.jsonl` (made by `extract_poly_lines.sh DIR`) and read fonts from
`~/Projects/greek-page-ocr/assets/fonts` (only fonts passing `font_supports_polytonic`; italics and mono excluded).
Run from the repo root with `.venv/bin/python scripts/glyphs/eval/<script> DIR ...`.

| script | arguments | produces |
|---|---|---|
| common.py | — | fonts (gate + italics/mono excluded), text, renders restricted to covered text |
| eval_glyphs.py | DIR N SEED P_NEIGHBOURS | truth-enumerated marks, neighbour pixels, letter boxes (`summarise`) |
| mark_stats.py | DIR | gap distributions (accent vs neighbour ink) used to set NEIGHBOUR_GAP_ABOVE/BELOW (seed 5) |
| xh_est.py | DIR | x-height estimator comparison against render truth + three real crops |
| skew_eval.py | DIR | skew angle error vs the known render rotation (200 lines, seed 31) |
| ink_eval.py | DIR | ink-score fit on seed 1 (150 lines) and test on seed 2 (150 lines): AUCs per defect kind |

Numbers quoted in docs/GLYPHS_PLAN.md and the review page come from: `eval_glyphs.py DIR 300 11 1`, `skew_eval.py DIR`,
`ink_eval.py DIR`. Thresholds were set on other seeds (mark_stats seed 5; ink weights seed 1).
