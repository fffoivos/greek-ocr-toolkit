You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) holds everything you need: items.jsonl and the img/ folder.
- See an image with the view_image tool. View cards in small groups (about 5 to 10 images per tool call) rather than one per call.
- Give view_image literal relative paths only, written out in full (e.g. `zoom/group01.png`, `img/<name>.png`). Never build an image path from `pwd`, an absolute path, a variable or a loop.
- Write every zoom image once, under a new name; never overwrite or delete a file in ./zoom/.
- Use only these ImageMagick operations: `-filter point`, `-resize`, and `montage` / `-append` / `+append` to tile crops. Do not use `-rotate` or any other transform: judge rotation by eye.
- Use no absolute path anywhere, fonts included: if you label a montage, give ImageMagick a font name (e.g. `-font Helvetica`), not a font file path.
- ImageMagick (`magick`) is installed. Put enlargements only in ./zoom/.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder. The only files you may create are ./answers.jsonl and images under ./zoom/; run any helper code inline (heredoc), never save it as a file.
- There is no network and no web search.

# Protocol
Where it says CARDS, read ./items.jsonl; where it says OUT, write ./answers.jsonl; where it says ZOOM, use ./zoom/.

You are typing small crops for an OCR training-data project. Each card is one small crop cut from a scanned page (`crop`) by a line segmenter, plus the machine transcription Google produced for it (`google_text`). Most of these crops hold only a few characters. Your job is to say, from the pixels, **what the crop shows**, and whether the transcription and the crop are right. You do not know the source; do not guess it.

## Input
CARDS is a JSONL file. Each row has `card_id`, `crop` (path relative to the cards file's directory) and `google_text`.

Open every crop with the view_image tool. These crops are small: make an enlarged copy of each group with ImageMagick (`magick in.png -filter point -resize 400% zoom/x.png`, or a montage of several crops) in ZOOM before deciding. Do not use sips or Pillow.

## For each card, record

**type**: exactly one of the codes below. Choose by what the ink in the crop is, not by the Google text.
- `word`: one or more complete printed words in lower or mixed case, including a line tail or a hyphenated word part that is a complete short printed line ("ζουμε:", "zations", "ανέρ-").
- `caps_display`: words in capitals or display type: a heading, name, signature in capitals, table header; often letter-spaced, large, inverse or outlined ("Α Θ Η Ν Α", "ΧΡΗΣΗ 1989").
- `abbrev_label`: an abbreviation, reference or label, with or without a number ("ver. 51.", "Luc. 11.", "Αριθ. 2939", "Δρχ.", "Члан 35.").
- `marker`: a single printed letter or a short list/section marker ("α)", "β.", "§", "*", "Β").
- `roman_lower`: a lower-case Roman numeral ("xviii", "iv.").
- `digits_letters`: digits mixed with letters or units that is not an abbreviation or reference ("12α", "5 χλμ", "3η").
- `number`: only digits and number punctuation (the crop shows a number; use this even if Google read letters).
- `punctuation`: printed marks with no letters or digits: leader dots, ditto marks, dashes, rules, quotes, asterisks, "%".
- `noise`: blobs, specks, scattered dots, stains or a near-blank crop; no printed character.
- `handwriting`: handwritten marks: signature, scribble, note.
- `foreign_script`: printed text in a script other than Greek, Latin or Cyrillic (e.g. CJK, Arabic, Hebrew).
- `figure_ornament`: part of a map, figure, ornament, logo or stamp.
- `watermark`: a digitisation mark ("Digitized by Google", "Google").
- `show_through`: mirrored or faint text from the other side of the page.
- `cut_fragment`: the crop edge cuts through letters, so the ink is a piece of a word or line.
- `multi_line`: two or more printed lines, with readable characters, are inside the crop.
- `part_of_line`: the crop holds a longer printed line (or more) than google_text covers; google_text is only part of what is printed.
- `other`: none of these; describe it in `detail`.

**text**: compare google_text with the print, character by character:
- `match`: every character is right (accents and breathings included where you can see them);
- `minor`: letters right, but a mark, a space or a punctuation sign differs;
- `wrong`: a letter, digit or word is wrong, missing or extra, or the script is wrong (e.g. Latin "o" for Greek "ο");
- `not_text`: the crop has no printed characters (noise, figure, blank), so the transcription cannot be right;
- `unreadable`: the pixels do not let you decide.

**crop**:
- `ok`: the crop holds exactly the printed item, complete, with no readable characters from another line or item;
- `clipped`: the crop cuts the item at an edge;
- `extra`: the crop also holds readable characters or whole letter bodies from another line, column or item;
- `na`: not text (type noise, figure_ornament, show_through or blank).

**rotated**: `yes` if the printed characters are turned 90° or upside down in the crop, `no` otherwise.

**detail**: for `text` = wrong or minor, the differing parts as "printed → google" pairs; for `other`, a short description; otherwise "".

## Output
Write one JSON object per card, one per line, to OUT (with a shell command; overwrite). Rewrite OUT with all lines so far after every few cards:

{"card_id":"k0123456789","type":"word","text":"match","crop":"ok","rotated":"no","detail":""}

Every card must have exactly one line. Then reply with:
- the number of cards;
- counts per type, per text value and per crop value;
- one sentence on any systematic pattern.

Open only items.jsonl and the crop images. Never open key files or anything else.

# Done when
- ./answers.jsonl has exactly one valid JSON line per card of ./items.jsonl, in the same order, with every field above, and every value from the lists above;
- you have checked the count, the order and the values with a command;
- your final reply is the short plain-text summary the protocol asks for.
