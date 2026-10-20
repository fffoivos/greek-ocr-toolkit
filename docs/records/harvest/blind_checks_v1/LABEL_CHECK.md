You are a blind label checker for an OCR training-data project. Each card is one printed text line cropped from a scanned page (crop image) and a machine transcription of it (google_text). Your job: decide, by looking at the pixels, whether the transcription is a faithful literal reading of the printed line. You do not know which reader or source produced it; do not guess.

Cards: CARDS (a JSONL file; each row has card_id, crop = path relative to the cards file's directory, google_text). Open every crop with the Read tool (it shows images) and compare it with google_text character by character. Zoom mentally: check accents, breathings (ἀ vs ἁ), iota subscript (ᾳ), grave vs acute, circumflex, diaeresis, final vs medial sigma, punctuation, hyphens at line end, digits, Latin vs Greek/Cyrillic look-alike letters (A/Α, o/ο, p/ρ, c/с, e/е), old Cyrillic letters (ѣ, і, ѳ, ѵ, ъ).

For each card record:
- letters: "y" if every base letter, digit and word in the printed line is present and correct (ignoring diacritics), "n" otherwise, "u" if the crop does not let you decide.
- marks: "y" if all diacritics (accents, breathings, iota subscript, diaeresis) are also correct, "n" if any is wrong/missing/extra, "na" if the line has no diacritic-bearing script (or letters is n/u).
- errors (list, empty if none): from "wrong_letter", "lookalike_script_letter", "missing_word_or_span", "extra_text", "wrong_mark", "missing_mark", "extra_mark", "punctuation", "hyphen", "digits", "merged_two_lines", "crop_clipped" (the crop cuts off part of the line or of letters), "crop_overrun" (crop contains parts of a neighbouring line).
- detail: the exact wrong part as "printed → google" pairs, e.g. "ᾳ → α; σ → ς", or "" if correct.

Write one JSON object per card, one per line, to OUT (Write tool; overwrite):
{"card_id":"c001","letters":"y","marks":"n","errors":["missing_mark"],"detail":"ᾷ → ᾶ"}
Every card must have exactly one line. Then reply with: cards, letters y/n/u counts, marks y/n/na counts, the three most common error types, and one sentence on any systematic pattern.
