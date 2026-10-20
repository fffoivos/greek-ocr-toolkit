# Blind reader protocol, R2 word cards (current practice, 17 Oct 2026)

Used for the R2 T2/T4 decks: two Opus readers per card, reader 2 in reverse order, a third reader on disagreement, about 10% planted
pixel-verified controls, at most one control error per batch.

## Files the readers get

All of them sit in an isolated copied folder, with no key anywhere above it:
- `README.md` and `answer_schema.json`, from `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks/T2/blind/`;
- `cards.jsonl` (`card_id`, `word_image`, `line_image`, `anchor_index`, `anchor_base`, options, extra options);
- `img/`.

## Card rendering

The word zoom is at a uniform integer scale of 1–3×, with the full native line beside it. The renderer is
`~/Projects/greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_prepare.py`.

For the 39-card sheet, the owner-page version used:
- the full line;
- the word at 3× (LANCZOS) over the word's slot-bbox union ± 6 px, full height;
- the letter at 8× (NEAREST) over the slot bbox ± max(6, w/2), full height.

The renderer is `R2_evidence/page_builders/build_r1a_errors.py`. Per-card crop path, slot, letter bbox and word bbox are in
`R2_evidence/reader_errors_39_card_inputs.json`.

## Reader prompt (verbatim, T4 version, which adds two rules learned on T2)

You are a blind reader of printed Greek words (careful, literal transcription of ink). Work ONLY inside this folder: <BATCH_DIR>
Open only: README.md, answer_schema.json, cards.jsonl, and the PNG files under img/ that the cards name. Do not open, list or search any
other file or folder (not the parent folder, not other batches, not any key, answer or private file). Do not use web search. Any temporary
file (enlargements, helper scripts) goes ONLY into a new subfolder zoom/ of THIS folder; never write anywhere else. [Reader 2 only: (The
README mentions cards_reverse.jsonl for reader 2: your cards.jsonl is already in your assigned order; use it as given.)]

Read README.md and answer_schema.json first. Then go through cards.jsonl IN ITS GIVEN ORDER. For each card, look at img/<word_image> (the
word zoom; read the central word). Open img/<line_image> (the full native line) whenever mark ownership, a cut, or context is unclear; also
open any paired view images listed (they are repeated views of the same word). Transcribe what is PRINTED, misprints included; never
correct spelling or infer a mark from grammar. The options vary only one head at the anchor letter and usually lack the word's other marks,
so choose "literal" with the complete exact word whenever no option is exactly what is printed. For the anchor letter (anchor_index counts
letters only, from 0) give all four heads; give letter_heads for every other letter you can decide.

Rules:
1. Every head you set to a value must agree with your transcription. Any head you cannot decide from the ink is "unknown" (if you must
   still write some form in the transcription, the "unknown" head marks it as unconfirmed).
2. ownership_ok: true/false only when the anchor letter carries a mark (does that mark's ink belong to this letter, not a neighbour line,
   speck or show-through?). Set ownership_ok to null when the anchor letter has no mark.
3. A mark is "none" only if the area is clearly visible and blank.

Write your answers to answers.jsonl in this same folder: exactly one JSON object per card, in the same order as cards.jsonl, following
answer_schema.json (card_id, choice, transcription when literal, anchor_heads, letter_heads, readability, ownership_ok, confidence, note;
set usage to {"input_tokens":0,"output_tokens":0}). Write incrementally. Some cards are planted checks; treat every card the same. When
finished, verify the line count and order, then reply with: cards answered, literal count, unreadable count, and hard cards.

## Resolver

`~/Projects/greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_resolve.py` (R2C2: ownership not applicable on unmarked anchors;
per-card invalid votes; controls gate; re-randomised tiebreak; 2-of-3).

## Measured cost (T2 pilot)

110 cards per batch, about 10–16 min, 145–230k agent tokens per batch.
