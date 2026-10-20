You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) holds everything you need: items.jsonl and the img/ folder.
- See an image with the view_image tool. View the images of several items per tool call (for example the word and letter images of the next 5 items) rather than one per call.
- ImageMagick (`magick`) is installed. Put any further enlargement only in ./zoom/.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
- There is no network and no web search. Open only items.jsonl and the images under img/ (and your own files in zoom/). Do not list, open or search any other file or folder.

# Task
Each item is one printed Greek word from a scanned page (late 19th to 20th century polytonic print). Fields:
- `word_image`: the word, enlarged 3×;
- `letter_image`: one letter of that word, enlarged 8×;
- `word_bare`: the word's letters with every accent and breathing removed, to tell you which word it is;
- `anchor_index` and `anchor_base`: which letter to judge. The index counts letters only, from 0.

For the anchor letter, decide from the ink which accent is printed on it:
- **acute:** a stroke rising from lower left to upper right (´);
- **grave:** a stroke falling from upper left to lower right (`);
- **circumflex:** a tilde-like curve or an inverted breve (῀);
- **none:** no accent on this letter, with the area above it clearly visible and blank;
- **unreadable:** the ink does not let you decide (worn, broken, cut, or a mark of unclear direction).

Judge the direction of the stroke from the pixels only. Breathings (the small hooks ᾿ ῾) are not accents; ignore them, except to make sure you are not reading a breathing as an accent. In this period both acute and grave are common on a word's last syllable, and the spelling does not tell you which one was printed, so do not infer from grammar, position or habit. When the stroke is short, look at which end is higher.

# Output
Write ./answers.jsonl with exactly one JSON object per item, in the order of items.jsonl:

{"item_id":"k0123456789","accent":"grave","confidence":"high","note":""}

Here `accent` is one of acute, grave, circumflex, none, unreadable, and `confidence` is high or low. Write incrementally, rewriting the file with all lines so far after every few items.

# Done when
- ./answers.jsonl has exactly one valid line per item of ./items.jsonl, in the same order;
- you have checked the count and the order with a command;
- your final reply, in plain text, gives the number of items and the counts per accent value.
