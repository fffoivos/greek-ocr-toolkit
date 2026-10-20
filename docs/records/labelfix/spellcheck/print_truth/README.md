# Print truth (189 words), adjudication record

**Blinding label: KEY-IN-REACH (not opened per transcripts).** Coordinator ruling 17 Oct: this adjudication carries the label. It stays valid, but the owner must know.

Readers: 8 Opus readers (4 batches × 2) plus 1 tiebreak. They were handed the scratch folder `adj/batchN.json` + `adj/img/`. `key_SEALED.json` sat in that same folder, beside `items_public.json`, `build.py` and the other readers' answer files. The 8 main prompts did not forbid opening keys. The session transcripts show no reader opened the key: two readers ran `ls adj/ | head`, and the 10-line cut stopped one entry before `key_SEALED.json`.

Full evidence: `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_blinding.md` §1 (and the table row 1).

## 1. 189-word print truth

- **Readers.** Eight "Blind print reader bN rM" agents (b0–b3 × r1/r2) plus "Blind print reader tiebreak" (a59d5277…), in session `b1155dbd…`, 16 Oct 20:03–20:26.
- **Handed.** Prompt: "Items: /private/tmp/claude-501/…/b1155dbd…/scratchpad/adj/batch0.json (a JSON list of {id, image, A, B}) … Write your answers … to …/adj/answers_b0_r1.jsonl". Items contain only `id, image, A, B`.
- **Key location.** The folder `scratchpad(b1155)/adj/` holds `key_SEALED.json`. It maps each item to `line_id`, `google`, `human`, `kind`, `cluster`. The same folder holds `items_public.json`, `build.py`, `reconcile.py` and the other readers' `answers_*.jsonl`. The copy in `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/print_truth/` was not the copy handed to readers.
- **Instruction.** The eight main prompts say nothing about keys or other files. Only the tiebreak prompt says "Do not open any other answers_* file in that folder."
- **Evidence.** Reader b0 r1 (af9942…) ran `cd …/adj/; ls | head`. Reader b2 r2 (abc769…) ran `ls …/adj/ | head`. Both results end at `… build.py | crops | crops_r2 | img | items_public.json`; `head` cut the list before `key_SEALED.json`. No reader's tool calls name `key_SEALED`, `items_public`, `build.py` or `reconcile.py`. Each reader names only its own batch and answers file. b0 r1's final message: "I did not open the existing answers_b0_r2.jsonl in that folder, so my reading stayed independent."
- **Verdict.** Key-in-reach (not opened per transcripts). The main prompts carried no prohibition.

