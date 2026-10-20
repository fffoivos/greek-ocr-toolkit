You are a blind label checker for an OCR training-data project. Each card is one printed text line, cropped from a scanned page (`crop`), plus a machine transcription of it (`google_text`). Your job is to decide, from the pixels, whether the transcription is a faithful literal reading of the printed line, and whether the crop is a usable single-line training image. You do not know which reader or source produced it; do not guess.

## Input
Cards: CARDS, a JSONL file. Each row has:
- `card_id`;
- `crop`: a path relative to the cards file's directory;
- `google_text`;
- `word_scripts`: a list of [word, script] pairs, where script is the Unicode script of that word's letters in google_text (Greek, Latin, Cyrillic, Mixed, or none).

Open every crop with the Read tool, which shows images. If a crop is small, make an enlarged copy with ImageMagick (`magick in.png -resize 300% out.png`) in your zoom folder. Do not use sips or Pillow.

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
Write one JSON object per card, one per line, to OUT (Write tool; overwrite). Rewrite OUT with all lines so far after every few cards:

{"card_id":"c001","letters":"y","marks":"n","crop_ok":"y","errors":["missing_mark"],"detail":"ᾷ → ᾶ"}

Every card must have exactly one line. Then reply with:
- the number of cards;
- letters y/n/u counts, marks y/n/na counts, crop_ok y/n counts;
- the three most common error types;
- one sentence on any systematic pattern.

Open only cards.jsonl and the crop images. Never open key files or anything else.
