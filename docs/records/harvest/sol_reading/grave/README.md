# SR-G1 private build notes

The one-reader public pack is `PACK_ROOT/grave/r1/`. Its only entries are
`items.jsonl` and `img/`. `PACK_ROOT/grave/MANIFEST.r1.json` binds all public
files. All keys, source identities, reference labels, review sheets and
synthetic answers stay here, outside PACK_ROOT.

The 26 mandatory printed-grave / label-acute pairs are listed individually in
`BUILD_RECEIPT.json` (`positive_pairs`): NLG 9, Lekythos 11, Kosmopolis 6.
Negatives have the same counts; each stratum contributes one circumflex and
one unaccented control. Selection uses both available C1 verdicts: all verdicts
for a selected negative/control card must have `letters=y` and `marks=y`.
Negative candidates of at least four letters take priority after seeded
shuffle. Selected negatives/controls use distinct lines, disjoint from all
positive lines. Crop quality verdicts are not an added selection restriction.

Geometry reuses the local E2 port: inverse response transforms, tokens fully
inside crop_bbox, exact normalized machine-text alignment, and symbol boxes.
No estimated geometry is admitted. Rendering ports owner39 E2, including the
integer half-width padding. No ink is added, removed, or normalized.

`keys/key.json` is an ordered item-id-to-private-record map. `printed_word`
comes from the printed side of a positive pair or the checked C1 label for
other items; `label_token` preserves the original machine token and punctuation.
The key includes exact word/symbol and render boxes, source hashes and response
paths. Reference accents have not been independently re-adjudicated here.

Lead pixel-review sheets (1600 px wide, six tiles per row) are in
`keys/control_review/{positives,negatives,controls}.png`, with `_2` continuations
for positives and negatives. Each tile has the item id, expected accent,
letter close-up, and word crop. Lead review remains distinct from build QA.

Run tools with this interpreter (all runs are offline):

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/records/harvest/sol_reading/grave/tools/test_grave.py
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/records/harvest/sol_reading/grave/tools/score_grave.py /absolute/path/to/answers.jsonl
```

An answer is exactly `{"item_id":"<public id>","accent":"grave","confidence":"high","note":""}`;
all four fields are required, confidence is `high` or `low`, and note is a string;
allowed accents are `acute`, `grave`, `circumflex`, `none`, `unreadable`.
Supply exactly one answer per item in public order. Unreadable answers remain
in the accuracy denominator. A positive line is detected if any of its
positive items is answered grave; all 26 current positive lines are distinct.
The negative false-alarm numerator counts only answers of grave.

`keys/synthetic/` contains clearly labelled synthetic fixtures and reports,
including perfect, all-acute, all-grave, and all-unreadable answers. They are
test data, not Sol observations. The test suite also covers malformed answers,
line aggregation, renderer pixels, PNG metadata, hashes, and public closure.


SR-G2 adds `touches_punct`, derived from the C1 source key's `literal_label`,
with line ID and the item's 1-based word index checked against the printed word
(letters compared without accents). It is true when punctuation
`, . ; · : ! ? » ) …` immediately follows the word, or the word ends at a
line-end hyphen (including a split word); a bare line ending is false.
The private key retains the flag, source line text and source file path;
the scorer rederives and validates the flags on every CLI run.
Every summary includes denominators and all metrics, including confidence,
with overall, class, stratum and stratum-by-class views, also repeated for
each punctuation flag. Zero denominators have null rates, never zero rates.
`RESULTS_TABLE.md` and `answers/grave/r1.score.json` contain actual r1 results;
`keys/synthetic/` remains explicitly synthetic.
