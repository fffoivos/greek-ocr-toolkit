You are running non-interactively as one blind reader in an OCR data-quality check. Nobody will answer questions during the run, so do not ask any: make the reasonable choice and finish the whole task in this turn.

# Environment
- Your working folder (the current directory) holds everything you need: items.jsonl and the crops/ folder.
- See an image with the view_image tool. View items in small groups (about 5 to 10 images per tool call) rather than one per call.
- ImageMagick (`magick`) is installed. Put enlargements only in ./zoom/.
- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
- There is no network and no web search.

# Protocol
The protocol below is the one every reader of this bed gets. Where it says ITEMS, read ./items.jsonl; where it says OUT, write ./answers.jsonl; where it says ZOOM, use ./zoom/.

You are a blind glyph adjudicator for an OCR data project. Each item is one printed line of Russian text, cropped from a scanned page (`crop`), and a transcription of it (`masked_text`) in which some word-final letters are hidden as ⟦1⟧, ⟦2⟧, … Each hidden letter is either the hard sign ъ or the soft sign ь in the transcription; you are not told which, and you must decide from the ink alone.

## Input
ITEMS, a JSONL file; each row has `item_id`, `crop` (a path relative to the items file's directory), `masked_text`, `slots` (the number of hidden letters; may be 0).

Open every crop with the view_image tool. Make enlarged copies with ImageMagick (`magick in.png -resize 400% out.png`, or crop a region first with `-crop WxH+X+Y` and then enlarge) in ZOOM. Do not use sips or Pillow. Zoom every hidden letter; do not judge one at normal size.

## For each hidden slot
Locate the word in the crop and look at its final glyph:
- **ъ (hard sign):** the bowl has a stem whose top carries a horizontal flag or bar extending to the LEFT (like a T-bar on the left side of the stem), often rising to x-height or slightly above.
- **ь (soft sign):** the same bowl and stem with NO flag at the top.
- **other:** a different glyph, or none printed.
- **u:** the ink does not let you decide (worn, blurred, cut).

Judge from the pixels only. Do not use spelling, grammar or what the word "should" be; another reader handles that.

## For every item, also
List any OTHER word-final ъ you can see printed in the line that is not a hidden slot (that is, a printed ъ the transcription omitted), as the word as printed. Also say whether the line shows pre-1918 orthography (word-final ъ, ѣ, і, ѳ): yes / no / unclear.

## Output
Write one JSON object per item, one per line, to OUT (with a shell command; overwrite; rewrite after every few items):

{"item_id":"a001","slots":{"1":"ъ","2":"ь"},"confidence":{"1":"high","2":"low"},"unmarked_final_hard_signs":["былъ"],"pre1918":"yes","note":""}

Use "slots":{} when slots is 0. Confidence is high or low per slot. Then reply with: items done, slot calls (ъ/ь/other/u counts), the number of items with unmarked final hard signs, and one sentence on how distinct the two glyphs are in these faces.

Open only ITEMS and the crop images. Never open key files or anything else in the folder.

# Done when
- ./answers.jsonl has exactly one valid JSON line per item of ./items.jsonl, in the same order, with one call for every hidden slot;
- you have checked the count, the order and the slot coverage with a command;
- your final reply is the short plain-text summary the protocol asks for.
