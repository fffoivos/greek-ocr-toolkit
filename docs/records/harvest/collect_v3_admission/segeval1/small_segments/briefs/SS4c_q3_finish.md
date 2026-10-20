# SS4c — finish the type2 packs: heredoc replay fixture, launcher, mapper, tests

You are Sol. Follow-up to SS4b (read `SS/q3/SS4b_RECEIPT.json`, `SS/briefs/SS4b_q3_repack.md`, `SS/briefs/SS4_q3_packs.md`; all
constraints still hold; do not start reading runs; do not modify or fork the scanner).
Worktree `~/Projects/greek-ocr-toolkit-sol-recut`; `SS = docs/records/harvest/collect_v3_admission/segeval1/small_segments`.

## Lead's reading of SS4b
The fixture used a bare `magick montage` shell command, which the canonical scanner skips by design. The readers' real idiom is a
Python heredoc that reads the item file and calls `subprocess.run(['magick', ...])`. In `SS/q3/answers/t01.run2_VOID.scan.json`
the scanner DID replay those heredocs (status `replayed`); they failed only with `FileNotFoundError: 'cards.jsonl'`, because the
replay seeds `items.jsonl` + `img/` only. The bed's prompt now also forbids overwriting zoom files, so plain byte matches suffice
when the reader complies.

## Do
1. Replace the fixture with the readers' idiom, copied from run 2's recorded commands (rollout path in
   `t01.run2_VOID.scan.json`), with `cards.jsonl` → `items.jsonl` and `crops/` → `img/`:
   - (a) heredoc builds `zoom/group01.png` and the reader views it;
   - (b) a second heredoc overwrites `zoom/group01.png` and the reader views it again;
   - (c) a no-overwrite variant: two montages under new names, each viewed once.
   Run the canonical scanner in place on each and record the outcome; keep the two negative fixtures (pwd view, absolute font
   path). Report the outcomes; **do not stop** on (b) failing as long as (c) passes. Stop only if (c) fails.
2. Finish what SS4b left: `run_type.sh` / `run_type.py` / `map_type.py` / closure check on `type2` (`SS/q3/keys/type2.json`),
   prompt `SS/prompts/type.md` verbatim, results to `SS/q3/answers/<ctx>.*`; the SS4 tests adapted to type2 plus the fixture
   tests. Run them.
3. Update `SS/q3/SS4b_RECEIPT.json` → write `SS/q3/SS4c_RECEIPT.json` (fixture outcomes, launcher/tool sha256, tests).

Last line exactly: `SS4c READY: type2 5 contexts, fixtures a=<ok|VOID> b=<ok|VOID> c=<ok|VOID> neg=<VOID,VOID>, launcher <path>`
(or `SS4c FAILED: <reason>`).
