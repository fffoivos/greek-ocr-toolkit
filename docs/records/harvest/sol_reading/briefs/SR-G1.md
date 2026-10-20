# SR-G1: grave/acute bed (word crop + letter zoom), one-reader pack

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading` (branch `opus/sol-reading`), and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/grave/` and `PACK_ROOT/grave/` (PACK_ROOT = `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs`). Reuse your SR-B1/B2/B3 tools and conventions: opaque ids, content-hash PNGs, closure scan, MANIFEST beside the folder, private key under `docs/records/harvest/sol_reading/grave/keys/`, nothing else in PACK_ROOT. Pillow: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`.

Purpose: test whether Sol can see the printed accent on one syllable, after it missed 3/3 printed-grave/label-acute errors in the bsb line checks.

## Items
Strata: `nlg__poly1900`, `lekythos__poly1900`, `kosmopolis__poly1900`. Sources (read-only):
- `docs/records/harvest/collect_v3/c1/c1_results.json` (`<stratum>.mark_errors`);
- `docs/records/harvest/collect_v3/c1/verdicts/<stratum>__{a,b}.jsonl`;
- the C1 card crops and keys under `~/Projects/collect-v3-data/run/W1/c1/<stratum>/` (and `_key.json`);
- the saved Google responses or token geometry used by `collect_v3/c1/efficiency/build.py` (E2) and your `tools/geometry.py`.

1. **Positives (truth = grave).** Every pair in `mark_errors[].detail` of the three strata where the printed form has U+0300 and the Google form is identical except U+0301 at that position, after NFD. The lead counted 26 (nlg 9, lekythos 11, kosmopolis 6). Record your count and every pair. The anchor letter is the vowel carrying the accent.
2. **Negatives (truth = acute).** Per stratum, the same number as the positives. Pick words whose LAST vowel carries U+0301, from cards whose C1 verdict is marks=y (and letters=y), so the reader checked them as correct. Seeded pick (`sol-grave:neg:<stratum>`); at most one word per line; no line shared with a positive. Prefer words of ≥4 letters.
3. **Controls, 6 (about 10%).** From the same marks=y cards, seeded: 3 words with a circumflex on the last or penultimate vowel (truth = circumflex), and 3 words of ≥4 letters whose final vowel is unaccented (anchor = that final vowel; truth = none).
4. **Geometry.** Locate the word and anchor glyph in the C1 crop exactly as `efficiency/build.py` E2 does: response transforms, tokens fully inside `crop_bbox`, alignment to the machine text, symbol boxes for glyphs. An item with no exact aligned geometry is NOT approximated. Replace it with the next seeded candidate of the same class and stratum, and list the replacement in the receipt.
5. **Rendering** (port the owner39 E2 formulas; no ink synthesis):
   - word image: word x-range ± 6 px, full crop height, 3× LANCZOS;
   - letter image: anchor glyph x-range ± max(6, w/2), full crop height, 8× NEAREST.

## Pack (`PACK_ROOT/grave/r1/`)
`items.jsonl` in seeded random order (`sol-grave:r1`), with public fields only:
- `item_id`;
- `word_image`;
- `letter_image`;
- `word_bare`: the word's base letters with ALL diacritics removed (NFD, drop the combining marks, NFC), punctuation stripped;
- `anchor_index`: counts letters only, from 0;
- `anchor_base`.

Plus `img/`. No Google text, no truth, no source ids, no stratum names. Run `tools/scan_packs.py`-equivalent checks, extended for this bed: the only folder entries are `items.jsonl` and `img/`; field set exact; no ids or truth strings; PNGs clean.

## Private outputs
- `grave/keys/key.json`: id → stratum, line id, card id, the word as printed per C1 (for positives the printed form from the pair; for negatives and controls the label form), class, truth accent, and geometry.
- `grave/keys/control_review/{positives,negatives,controls}.png`, contact sheets for the lead's pixel check. Each tile shows the letter image (scaled to at most 300 px high), the word image, the item id and the expected accent. 6 tiles per row, a 1600 px wide sheet; split into several files if needed.
- `grave/BUILD_RECEIPT.json`: inputs with sha256, counts per class and stratum, replacements, manifest sha.
- `grave/tools/score_grave.py <answers.jsonl>`: validates one answer per item in order, with `accent` ∈ {acute, grave, circumflex, none, unreadable}. It reports per class and per stratum: the confusion matrix, accuracy, unreadable count and control passes. It also reports line-level detection for the positive lines: a positive is detected iff answered grave. It also reports false-alarm rate on negatives = answered grave.
- Tests (`grave/tools/test_grave.py`): synthetic answers, labelled synthetic.

Last line: `SR-G1 READY: items=<n> (pos <n>, neg <n>, ctrl <n>) replacements=<n> tests=<p>/<t>`, or `SR-G1 BLOCKED: <reason>`.
