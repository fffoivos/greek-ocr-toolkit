# SR-G2: score the grave/acute run

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/grave/` and `docs/records/harvest/sol_reading/answers/grave/`.

The reader's prompt (`docs/records/harvest/sol_reading/prompts/grave.md`) asked for `{"item_id","accent","confidence","note"}`. `grave/tools/score_grave.py` rejected the answers ("Answer fields must be exactly item_id and accent").

1. **Scorer schema.** Accept exactly the prompt's schema: required `item_id` and `accent`, with `confidence` ∈ {high, low} and `note` (string). Reject unknown fields, a wrong order or wrong counts, as before. Update the tests.

2. **Punctuation split.** Add a per-item flag `touches_punct`: true if, in the C1 line text (from the key's source line), the word is immediately followed by punctuation (`, . ; · : ! ? » ) …`) or by a line-end hyphen, or if the word is hyphen-split at line end. Report every metric overall and separately for `touches_punct` = true/false, per class (positive grave / negative acute / controls) and per stratum. Explain in one line how the flag was derived.

3. **Score `answers/grave/r1.jsonl`** and write the output to `answers/grave/r1.score.json`. Then write `grave/RESULTS_TABLE.md`, plain tables with denominators:
   - the confusion matrix (truth × answer);
   - recall of grave on positives;
   - false-grave rate on negatives;
   - acute-correct on negatives;
   - controls;
   - unreadable counts;
   - the punctuation split;
   - per stratum;
   - the low-confidence share per class.

   Also list every wrong item: id, stratum, printed word (key), truth, answer, confidence, note, touches_punct.

4. Run the tests and write `grave/TEST_RESULTS_G2.txt`.

Last line: `SR-G2 READY: grave recall <x>/<n>, false-grave <x>/<n>, controls <x>/<n>`, or `SR-G2 BLOCKED: <reason>`.
