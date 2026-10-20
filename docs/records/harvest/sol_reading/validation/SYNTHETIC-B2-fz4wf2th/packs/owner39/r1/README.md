# Printed word reading

Transcribe what is printed, including misprints. Do not normalise spelling.
Use word pixels and the full native line to decide mark ownership. The zoom
retains context on both sides; read the central word. Anchor indexes count
letters only, from zero; punctuation does not count.

Options are generated from base letters, varying one head at the anchor.
Other printed marks may be absent from the options: choose `literal` and
transcribe the COMPLETE word exactly whenever no option is exact. You may
always use literal transcription. Choose `unreadable` for an unreadable/cut word.

For the anchor give breathing (none/psili/dasia/unknown), accent
(none/acute/grave/circumflex/unknown), diaeresis and subscript
(none/present/unknown). Include `letter_heads` for every other letter you can
decide, with zero-based index and all four heads. Never infer an invisible head.
Use unknown for undecided heads; do not guess from spelling.
Give readability readable/partial/unreadable, ownership_ok true/false/null,
confidence high/medium/low, and a short note. Mark ownership means ink owned
by this letter, rather than another line, a neighbour, or a speck.

Use cards.jsonl in order for reader 1 and cards_reverse.jsonl for reader 2.
Readers work independently. Repeated views share witness_group and are ONE
source word, never independent statistical witnesses. Do not compare answers.
The coordinator must verify the private control key before any reader starts.
Answer files are JSONL, one answer per card, following answer_schema.json.
