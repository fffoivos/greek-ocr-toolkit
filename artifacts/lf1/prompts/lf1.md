You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder holds only items.jsonl and img/ before reading.
- CARDS means ./items.jsonl, OUT means ./answers.jsonl, ZOOM means ./zoom/; cards.jsonl in the preserved protocol is an alias for items.jsonl, not another file to create.
- See every crop with view_image. Use literal relative paths only in every view_image call; write each call explicitly, with no path loops or computed paths. Batch about 5 to 10 explicit calls per tool call.
- ImageMagick (magick) is installed. Write every zoom once under a new name in zoom/; use only -filter point, -resize, montage/append. No -rotate, no font paths.
- Create only answers.jsonl and zoom/**. Write answers with shell commands. No network or web search.
- Input clarification: one stored label word has Hebrew letters; its word_scripts entry is Hebrew. The label is unchanged.

# Protocol
The following qualified protocol body is preserved verbatim. Resolve its CARDS/OUT/ZOOM and cards.jsonl aliases using Environment above.

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

# LF1 owner questions (independent of the historical crop_ok)
Keep all protocol answer fields, but ignore marks for LF1 decisions. Historical crop_ok is evidence only because it is stricter about neighbour ink than the owner standard.
Answer every following question in owner_crop using yes, no, or uncertain. A yes records the named fault, not a replacement label.

## one_central_line
Owner wording: "there is exactly one central line of text".
Question: Does the crop violate this requirement?

## text_ne_visible_line
Owner wording: "the label matches the visible line exactly, neither more nor less (text running past the crop, omitted visible spans, letters cut through, merged lines = fault)".
Question: Does the crop violate this extent/segmentation requirement? Record character substitutions separately in letters/errors/where.

## other_complete_line
Owner wording: "no other line shows completely".
Question: Does another line show completely?

## gt2_whole_neighbour_words
Owner wording: "other lines show at most 2 WHOLE words (100% visible); cut neighbour words and partial letter bodies are allowed".
Question: Do other lines show more than 2 WHOLE words (100% visible)?

## turned_or_clipped
Owner wording: "Turned (rotated) or clipped crops fail."
Question: Is this crop turned (rotated) or clipped?

For a base-letter/digit/script/punctuation/hyphen text difference, add where as a list of {"label": "literal differing label substring", "printed": "what is printed"}. Use an empty string for an insertion/deletion side. Otherwise where is []. Do not use the marks field to decide a verdict.
You may add reading as evidence only; it never replaces google_text and never decides the verdict by itself.
Use segmentation_detail for crop evidence. Do not infer a crop fault solely from a character substitution.

# Done when
- answers.jsonl has exactly one valid JSON line per items.jsonl card, in the same order, with all preserved protocol fields and owner_crop/where.
- You have checked count and order once with a command.
- Reply with the protocol's short plain-text summary.
