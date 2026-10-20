
# SEGEVAL1 owner crop rubric
Keep the preceding bsb protocol verbatim. Additionally answer these independent
pixel questions for EVERY card in the same answer object, using "yes", "no", or
"uncertain", plus a free-text `segmentation_detail` explaining flags/uncertainty:
- `neighbour_whole_word`: Is a whole word of another printed line visible?
  Partial letters or word fragments alone do not count.
- `multi_line`: Are two or more complete printed lines visible?
- `rotated`: Is the text rotated or vertical?
- `horizontally_missegmented`: Does the end boundary clip a final letter of the
  target line? Judge the actual printed final letter, not a missing OCR character.
These are independent of bsb's stricter crop_ok. A few partial neighbour glyphs
alone do not fail the owner rubric. Do not infer a segmentation failure from a
transcription error. Describe uncertain evidence honestly.
