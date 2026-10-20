You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) holds everything you need: items.jsonl and the img/ folder, README.md and answer_schema.json.
- See an image with the view_image tool. View the images of several items per tool call (for example the word and line images of the next 5 items) rather than one per call.
- ImageMagick (`magick`) is installed. Put any further enlargement only in ./zoom/.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
- There is no network and no web search. Open only items.jsonl, README.md, answer_schema.json and the images under img/ (and your own files in zoom/). Do not list, open or search any other file or folder.

# Task
Look at the letter marked in the image. Which breathing is printed on or before it (none / smooth ᾿ / rough ῾ / unreadable), and which accent (none / acute / grave / circumflex / unreadable)? A spacing compound before a capital (e.g. ῎Α) counts as printed on that capital. Do not infer from spelling or grammar; report only ink.

Each item gives a word zoom (3×) with one letter boxed, and the full native line strip. The box identifies the letter; marks immediately before or above it may lie outside the box. For each head, the option letters in breathing_options and accent_options are independently permuted per item. Select the option letter corresponding to the ink. The same question applies to every item.

# Output
Write ./answers.jsonl with exactly one JSON object per item, in the order of items.jsonl, using this fixed schema:
{"item_id":"k0123456789","breathing":"A","accent":"B","confidence":"high","note":""}
Use breathing option A–D and accent option A–E from that item's mappings. Confidence is high or low. Do not transcribe any word. Write incrementally, rewriting the file with all lines so far after every few items.

# Done when
- ./answers.jsonl has exactly one valid line per item of ./items.jsonl, in the same order;
- you have checked the count, order and option validity with a command;
- your final reply, in plain text, gives the number of items completed.

# CQ7 no-loop addendum (takes precedence over batching guidance above)
view each image with one explicit call, never iterate over paths in code
