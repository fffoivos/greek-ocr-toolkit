# SEG final sheet: replace the intro text only (gpt-6.1-sol, medium, network OFF; no .git writes; NO publish)

In `docs/records/harvest/seg_steps/sheet/build.py`, replace the `intro=` string (built around lines 191–215, including the pipe-delimited
score and 2×2 tables) with EXACTLY the text below. Keep the line breaks: the renderer joins lines with `<br>`. Change nothing else:
- no card content, groups or ids;
- not the vendor files.

Then rebuild (`../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/sheet/build.py`), run `verify.py`, and
update `receipt.json` and the README line counts if they change. The card manifest must be byte-identical to before.

```
Every line whose verdict changed between 0.8 and the new tool (0.9-s4), in the 150, 888 and 250 sets and the 417 small crops. 279 cards. The last section shows the lines the proposed length band would change (not adopted).
The five changes: (1) a neighbour word counts only if every letter is ≥95% visible; (2) crops taller than wide are turned 90° right; (3) curved lines are measured along their curve; (4) small crops (≤8 Google characters, at most 6× longer than tall) are measured from all their ink; (5) proposed length band 0.30–2.00 instead of 0.5–1.5, not adopted.
Agreement with your judgements, 0.8 → new tool: your 235 marks 155 → 189; your 135 ratings 94 → 109; your 185 small-crop marks 131 → 160. On the 150: wrongly dropped 18 → 16, wrongly kept 14 → 15, undecided 11 → 0.
Small crops, numeric only or all? Box from all ink helps both: numbers 111 → 127 of 144, letters 120 → 137 of 157. A separate expected length for numbers adds 5 more on numbers only (132). Mixed: 3 crops, indicative only.
Your earlier mark on each line is shown as text ("Owner mark"); this sheet starts unmarked and never saves on load.
Outer border = your mark (green KEEP, red DROP). Inner frame = new tool (green KEEP, red DROP, amber UNCERTAIN).
Overlays (b): green = main line; orange dashed = other rows; red box = whole neighbour word; grey dashed = cut-off word; magenta = the box the tool measured.
Keys: ↑ ↓ move · SPACE marks KEEP/DROP · b boxes · z zoom · Esc leaves the note.
```

**Last line:** `SEG SHEET INTRO READY: html <MB>; cards <n> unchanged <yes>; verify <ok>`
