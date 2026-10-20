
# Additional owner-standard crop questions

Keep every field and instruction above. Also answer the following four questions
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
- `horizontally_missegmented`: "yes" or "no". Is a horizontal line split, or does
  the crop cross a column? Add `horizontally_missegmented_reason`, one line
  explaining the visible evidence.

Answer these separately from the original `crop_ok` rule. A `crop_ok: "n"` for
partial letters does not imply a complete neighbouring word. If evidence is
unclear, describe the uncertainty in the corresponding reason; do not invent
missing ink. Finish all four yes/no answers and all four reasons for every card.
