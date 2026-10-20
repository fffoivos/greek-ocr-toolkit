You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) holds everything you need: cards.jsonl and the crops/ folder.
- See an image with the view_image tool. View cards in small groups (about 5 to 10 images per tool call) rather than one per call.
- ImageMagick (`magick`) is installed. Put enlargements only in ./zoom/.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
- There is no network and no web search.

# Protocol
The protocol below is the one every reader of this bed gets. Where it says CARDS, read ./cards.jsonl; where it says OUT, write ./answers.jsonl; where it says ZOOM or "your zoom folder", use ./zoom/.

You are a blind label checker for an OCR training-data project. Each card is one printed text line, cropped from a scanned page (`crop`), plus a machine transcription of it (`google_text`). Your job is to decide, from the pixels, whether the transcription is a faithful literal reading of the printed line, and whether the crop is a usable single-line training image. You do not know which reader or source produced it; do not guess.

## Input
Cards: CARDS, a JSONL file. Each row has:
- `card_id`;
- `crop`: a path relative to the cards file's directory;
- `google_text`;
- `word_scripts`: a list of [word, script] pairs, where script is the Unicode script of that word's letters in google_text (Greek, Latin, Cyrillic, Mixed, or none).

Open every crop with the view_image tool, which shows images. If a crop is small, make an enlarged copy with ImageMagick (`magick in.png -resize 300% out.png`) in your zoom folder. Do not use sips or Pillow.

## What to check
Compare the crop with google_text character by character. Check:
- accents, breathings (ἀ vs ἁ), iota subscript (ᾳ), grave vs acute, circumflex, diaeresis;
- final vs medial sigma;
- punctuation, hyphens at line end, digits;
- old Cyrillic letters (ѣ, і, ѳ, ѵ, ъ).

**Scripts.** For every word, check that the printed word's script matches its `word_scripts` entry:
- a printed Latin word labelled with Greek letters is an error (for example, printed "to" with label "το");
- so is a Greek word labelled with Latin letters (for example, "o" for "ο", "x" for "χ");
- so is a mixed-script word.

## For each card, record
- **letters:**
  - "y" if every base letter, digit and word of the printed line is present, correct **and in the correct script** (diacritics ignored);
  - "n" otherwise;
  - "u" if the crop does not let you decide.
- **marks:**
  - "y" if all diacritics (accents, breathings, iota subscript, diaeresis) are also correct;
  - "n" if any is wrong, missing or extra;
  - "na" if the line has no diacritic-bearing script.

  Judge marks even when letters is "n", whenever the line has diacritic-bearing script and the marks can be compared.
- **crop_ok:**
  - "y" if the crop shows exactly one printed text line, complete from its first to its last character, and any ink from other lines or columns is limited to thin ascender/descender slivers with no readable characters or whole letter bodies;
  - "n" otherwise: readable characters or whole letter bodies from another line or column, or the line cut off at either end or through its letters.
- **errors:** a list, empty if none, drawn from:
  - "wrong_letter", "lookalike_script_letter", "missing_word_or_span", "extra_text";
  - "wrong_mark", "missing_mark", "extra_mark";
  - "punctuation", "hyphen", "digits";
  - "merged_two_lines", "crop_clipped", "crop_overrun".
- **detail:** the exact wrong parts as "printed → google" pairs, or "".

## Output
Write one JSON object per card, one per line, to OUT (with a shell command; overwrite). Rewrite OUT with all lines so far after every few cards:

{"card_id":"c001","letters":"y","marks":"n","crop_ok":"y","errors":["missing_mark"],"detail":"ᾷ → ᾶ"}

Every card must have exactly one line. Then reply with:
- the number of cards;
- letters y/n/u counts, marks y/n/na counts, crop_ok y/n counts;
- the three most common error types;
- one sentence on any systematic pattern.

Open only cards.jsonl and the crop images. Never open key files or anything else.

# Done when
- ./answers.jsonl has exactly one valid JSON line per card of ./cards.jsonl, in the same order, with every field above;
- you have checked the count and the order with a command;
- your final reply is the short plain-text summary the protocol asks for.

# Additional owner-standard crop questions

Keep every field and instruction above. Also answer the following five questions
for every card, based only on its pixels. Add the fields to the same answer object.
The owner standard for these additional questions is, verbatim:

"the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well"

"In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration"

- `neighbour_whole_word`: "yes" or "no". Is at least one complete word from
  another printed line visible? Half-letters and clipped word fragments never
  count. Add `neighbour_whole_word_reason`, one line explaining the visible evidence.
- `multi_line`: "yes" or "no". Are two or more complete printed lines visible?
  Add `multi_line_reason`, one line explaining the visible evidence.
- `rotated`: "yes" or "no". Is the printed text line rotated away from its
  normal horizontal reading axis? Add `rotated_reason`, one line explaining it.
- `horizontally_missegmented`: "yes" or "no". Is the target line split, or does
  the crop cross a column, or are two horizontally adjacent text blocks joined? Add `horizontally_missegmented_reason`, one line
  explaining the visible evidence.

- `end_clip`: "yes" or "no". Does the left or right boundary cut letters or
  punctuation of the target line? Add `end_clip_reason`, one line explaining
  the visible evidence. End-clipping alone does not imply horizontally_missegmented.

Answer these separately from the original `crop_ok` rule. A `crop_ok: "n"` for
partial letters does not imply a complete neighbouring word. If evidence is
unclear, describe the uncertainty in the corresponding reason; do not invent
missing ink. Finish all five yes/no answers and all five reasons for every card.

# Tool-use addendum
Use only relative paths inside your current reader folder. In every view_image call, write the complete relative path as a literal string, for example "zoom/card01-v1.png". Batch several explicit calls together. Do not build file paths in loops, template strings, concatenations, pwd expressions, or store/load expressions.

Create enlargements only inside ./zoom/. Give every new image a fresh filename. Never overwrite or delete an image after viewing it; preserve all zoom versions until the run is complete. Keep image-generation commands separate from commands that read or write answers.jsonl.

These instructions govern tool use only. Apply the label-check protocol above unchanged.
