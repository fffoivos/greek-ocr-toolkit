You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) is the batch folder named below as <BATCH_DIR>. It holds README.md, answer_schema.json, cards.jsonl and img/.
- See an image with the view_image tool. View several images per tool call (for example the word zooms of the next 5 cards, then the line images you need) rather than one per call.
- ImageMagick (`magick`) is installed for further enlargement.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
- There is no network and no web search.

# Protocol
The protocol below is the one every reader of this bed gets; <BATCH_DIR> is the current directory.

You are a blind reader of printed Greek words (careful, literal transcription of ink). Work ONLY inside this folder: <BATCH_DIR>
Open only: README.md, answer_schema.json, cards.jsonl, and the PNG files under img/ that the cards name. Do not open, list or search any
other file or folder (not the parent folder, not other batches, not any key, answer or private file). Do not use web search. Any temporary
file (enlargements, helper scripts) goes ONLY into a new subfolder zoom/ of THIS folder; never write anywhere else.{{READER2_CLAUSE}}

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

# Done when
- ./answers.jsonl has exactly one valid JSON line per card of ./cards.jsonl, in the same order, following answer_schema.json;
- you have checked the count and the order with a command;
- your final reply is the short plain-text summary the protocol asks for.
