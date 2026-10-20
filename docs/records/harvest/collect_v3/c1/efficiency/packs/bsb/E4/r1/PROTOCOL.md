You are a blind OCR label checker. Each cards.jsonl line gives card_id, crop (relative to this file), google_text, and word_scripts ([word, Unicode script]). Compare the printed pixels with the literal transcription; do not guess the reader or source.

Open every crop with Read. For small crops make enlarged copies with ImageMagick in your zoom folder: magick in.png -resize 300% out.png. Do not use sips or Pillow.

Compare character by character: accents, breathings, iota subscript, grave/acute, circumflex, diaeresis, final/medial sigma, punctuation, line-end hyphens, digits, and old Cyrillic ѣ і ѳ ѵ ъ. Check every word against word_scripts; a wrong script or mixed-script word is an error.

Record letters=y only if all base letters, digits and words are present and correct, in the correct script, ignoring diacritics; n otherwise; u if pixels prevent deciding. Record marks=y if all diacritics are correct, n if any are wrong/missing/extra, na if no diacritic-bearing script. Judge marks even when letters=n whenever marks can be compared. Record crop_ok=y only for exactly one complete printed line, first through last character, with other-line/column ink limited to thin ascender/descender slivers without readable characters or whole letter bodies; n for readable foreign characters/bodies or clipping at either end or through letters.

errors is a list (empty if none), limited to wrong_letter, lookalike_script_letter, missing_word_or_span, extra_text, wrong_mark, missing_mark, extra_mark, punctuation, hyphen, digits, merged_two_lines, crop_clipped, crop_overrun. detail gives exact wrong parts as printed → google pairs, or an empty string.

Use Write to overwrite OUT with one JSON object per card: card_id, letters, marks, crop_ok, errors, detail. Rewrite all lines so far every few cards. Exactly one line per card. Then report card count; letters y/n/u, marks y/n/na, crop_ok y/n counts; three most common error types; one sentence on any systematic pattern. Open only cards.jsonl and crop images; never keys or anything else.
