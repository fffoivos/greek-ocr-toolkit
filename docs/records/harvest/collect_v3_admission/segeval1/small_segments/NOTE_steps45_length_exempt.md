# Small crops where length should not decide (for steps 4/5, as a diagnostic, not a rule)

Small = `chars ≤ 8 AND A ≤ 6` (adopted 19 Oct): 59,002 rows; numeric 38,221, nonnumeric 19,481, mixed 1,300.
These counts come from the Q3 typology: 417 crops typed by Sol, with my eye on 209 of them (`samples.jsonl`, `final_class`). The population estimate covers the 19,377-row non-numeric pool (`q3/Q3_TABLES.md` T8; 150-row source-weighted sample, unweighted 95% Wilson intervals in brackets). Numeric small rows (38,221) were not typed.

| group | why length should not decide | sample bed (417 / 306 inside) | pool estimate | Google label right or minor |
|---|---|---:|---:|---:|
| punctuation-only (ditto marks, leader dots, dashes, quotes) | no letters, so the length comparison has nothing to count | 50 / 39 | 15% (11–23) ≈ 3,000 | 88% |
| non-text (handwriting, figures/stamps/ornaments, specks) | not printed text; any Google output is wrong | 41 / 33 | 8% (4–13) ≈ 1,500 | 15% |
| foreign script (CJK) | out of scope | 5 / 4 | 1% ≈ 270 | — |
| segmentation fault | the crop is wrong; text length cannot fix it | 75 / 38 | 10% (6–16) ≈ 2,000 | 32% |

The segmentation-fault group, split by type in the bed: multi_line 31, cut_fragment 18, part_of_line 5, and 21 legitimate-type crops that Sol called clipped or extra (word 7, caps 6, abbrev 5, punct 3).

**Owner caveat (sheet marks, 185 so far):** the owner kept all 13 marked crops of that last kind (words or capitals with a clipped/extra crop), so treat those 21 as legitimate. The trustworthy fault core is cut_fragment + multi_line + part_of_line: 54 in the bed, ≈ 6% of the pool (≈ 1,200). The owner has not yet marked the fault, non-text or punctuation groups.

**Computable from the tool's own output:** only punctuation-only. 50 of the 53 punctuation crops have Google text with no letter or digit (Unicode L/N). That test also catches 4 non-text, 1 fault and 1 legitimate crop. Non-text, CJK and the faults need pixels, so report them from the sample ids, not as a census count.

What length does decide: the legitimate small text, ≈ 65% of the pool (words 39%, abbreviations/labels 13%, capitals 11%, markers 6%). The owner kept 164 of the 172 marked crops of this kind; of the 8 drops, 7 are wrong Google text (owner note "wrong output" or reader text=wrong) and 1 ('1. ΡΑΓΙΟ') has no note.

**Update (SS9, owner admission rule gate 0.3 part 2):**
- Punctuation-only small cells are now excluded before segmentation (`single_character_cell`). Of the 50 bed rows of that class, the rule removes 36 and the gate 3; the other 11 are border rows outside the small definition.
- Of the 14,300 nonnumeric survivors, the groups where length should not decide are segmentation faults (≈ 10%, core cut_fragment + multi_line) and non-text (≈ 5%).
- CJK is gone with the gate.
- Use `small_population_key.v3.jsonl.gz` `survivor` to restrict to the admitted small set.
