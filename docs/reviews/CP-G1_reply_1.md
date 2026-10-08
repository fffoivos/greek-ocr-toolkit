# CP-G1 reply 1 (implementer, 8 Oct 2026 15:15 Athens)

Cycle-1 verdict HOLD (gpt-6.1-sol, asserted from rollout; 6 HIGH, 2 MEDIUM). Every finding is fixed; none deferred.
In the same cycle three owner-requested changes landed (owner 14:55–15:10): bend-following band fit (line04's first
words had no underline), the ink variable redefined as letter completeness by the owner's rule (pieces in the middle
region; adjacent letters do not share middle-region columns), and double-line detection (line08). They replace the old
ink score entirely, so findings F3/F4 are answered both by the fix and by the new definition.

| Finding | Disposition | Fix and evidence |
|---|---|---|
| F1 [HIGH] mark recall conditioned on detection | Fixed | evaluate.py enumerates truth marks (connected MARK pixels ≥ 4 px): found / detected / fused-into-letter; neighbour scored per ink pixel; letters per truth glyph via glyph-id map. Regression `test_f1_lost_accents_count_as_misses` (erase every other accent → found = 0.5). Published 99.07 % retracted: separate accents 97.95 % found, 25.4 % of accents fused into their letter in these renders (evals_v4.txt). |
| F2 [HIGH] fabricated synthetic ink; marked capitals; rotated boxes | Fixed | synthetic.py draws only real graphemes; mark/letter truth from an aligned stripped rendering; unaligned graphemes and capitals with spacing marks → IGNORE (excluded from every metric); boxes from the final glyph-id map (rotation, bend, crop applied to the map). `test_f2_rendered_ink_is_only_the_real_graphemes`. Bodoni ἀ: 226 letter + 37 mark px = 263 full px, 0 fabricated. NotoSans-Bold Ἡ → unreliable. |
| F3 [HIGH] defect type assigned by sign, unrotated ink truth | Fixed | defect_kind / defect_intensity per pixel, rotated/bent/cropped with the image; broken_eval.py labels each letter box by the majority defect under its own truth pixels, 'mixed' reported separately. `test_f3_defect_maps_follow_rotation_and_bend`. |
| F4 [HIGH] ink measured outside the band | Fixed | ink state is now pieces in the middle region (letters.py) + middle-region contrast (ink.py). `test_f4_ink_state_ignores_ink_outside_the_middle_region` (reviewer's tail probe: scores identical). |
| F5 [HIGH] faint letters vanish | Fixed | binarise adds whole faint components (darker than paper − max(4σ, 15 % range, 10)) that hold no Sauvola ink; letters below FAINT × line contrast → state 'faint'. `test_f5_faint_letters_are_detected_and_flagged` (reviewer's 195/20 probe: 10 letters, 5 faint). Truth-letter coverage in evals: letters lost 1.0 % (eval_glyphs), 6.1 % under injected defects (broken_eval). |
| F6 [HIGH] font coverage incomplete; renderer not gated | Fixed | font_covers checks every grapheme (incl. spacing breathings); PROBE adds ᾿ ῾; render_truth_line raises UnsupportedText for main/neighbour/second text; eval scripts sample only covered text. GFSElpis now rejected ('᾿' renders empty). `test_f6_render_refuses_text_the_font_cannot_draw`. |
| F7 [MEDIUM] censored calibration | Fixed | mark_stats.py takes every small component outside the body regardless of role and prints a threshold sweep (mark_stats.txt). Above: 0.40 → own ink called neighbour 0.67 %, neighbour kept 1.65 % (0.30–0.40 equivalent). Below: 0.30 → 8.15 % / 1.20 %; the 8 % own-ink share is flat from 0.30 to 0.60 (not threshold-driven; disclosed). Thresholds unchanged. |
| F8 [MEDIUM] NaN in records | Fixed | residual None without support; `test_f8_records_are_strict_json_even_for_a_blank_crop` with allow_nan=False; build script dumps with allow_nan=False. |

Also found while fixing: a renderer realism bug (canvas widened to the neighbour text, so short main lines were mostly
neighbour ink) — canvas now follows the main line. Short main lines between full-width neighbours remain a real
failure mode; those fits are marked medium/low confidence (skew_eval_conf.txt: high-confidence max 0.515°).
