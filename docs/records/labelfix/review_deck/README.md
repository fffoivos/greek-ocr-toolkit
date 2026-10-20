# Label-correction review deck

Preferred: `python -m greekocr.labelfix.deck_serve docs/records/labelfix/review_deck` and open
http://127.0.0.1:8765/index.html — every answer is then written immediately to
`docs/records/labelfix/decisions/<date>.jsonl` (no download needed; the header shows "server capture on").
Fallback: open `index.html` from disk (double-click; nothing is fetched); answers stay in the
browser's localStorage, which `python -m greekocr.labelfix.pull_firefox` can read from the Firefox
profile, or use "Download decisions". One batch per
rule: breathing, accent, subscript, marks_multi, final_grave, base_sub, final_sigma, constraint, accent#2, final_grave#2, base_sub#2, ink_decisive. Each card shows the native pixels of the line around one word (zoom 2–4×, pixel-exact),
the disputed letter boxed in red, the word underlined in blue, and ONE reading of that word.
Answer whether the print reads exactly as shown: `y` / `n` / `u` (uncertain, or neither reading).
Arrow keys move; decisions are saved in the browser (localStorage) as you go; "Download decisions"
writes `labelfix_decisions.json`; "Summary" computes precision per rule from your answers.

A batch of 100 cards takes about 6–10 minutes (3–5 s per card).

## What is hidden from you, and why

The reading shown is the proposed correction on about 100 × 70 % of the cards of a batch and
the existing Google label on the rest, drawn at random and never indicated. Mixed in are control
cards from the Wikisource three-way lines: up to 20 negative controls (a reading the human
transcription contradicts) and 10 positive controls (the human reading). The summary separates
them. So a `y` on a Google-shown card is not an error, and the negative controls measure your
false-yes rate.

| rule | accepted candidates available | correction/label cards | negative controls | positive controls |
|---|---:|---:|---:|---:|
| breathing | 36 | 36 | 18 | 1 |
| accent | 52 | 52 | 20 | 3 |
| subscript | 10 | 10 | 13 | 2 |
| marks_multi | 18 | 18 | 6 | 0 |
| final_grave | 343 | 100 | 2 | 10 |
| base_sub | 33 | 33 | 5 | 0 |
| final_sigma | 1 | 1 | 0 | 0 |
| constraint | 53 | 53 | 0 | 1 |
| accent#2 | 2 | 2 | 0 | 0 |
| final_grave#2 | 243 | 100 | 0 | 0 |
| base_sub#2 | 1 | 1 | 0 | 0 |
| ink_decisive | 42 | 42 | 20 | 4 |

## What the result means

Corrected labels are **derived**, not truth: they are Google's label rewritten where our
recogniser, a lexicon and the ink agree. A precision estimate from this deck is a check on that
derivation, and a test instrument whose labels were corrected by a model cannot be used to judge
that model (or any model trained with it): it would score the model's own habits as correct.
