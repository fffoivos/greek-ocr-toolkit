# SR-B1: Sol-reading packs, controls, leak scanner, answer mapper, ledger

You are the implementation worker for the "Sol reading" experiment. Work non-interactively: do not ask questions, make reasonable choices, record them in the receipt and finish in this turn. Read `docs/records/harvest/sol_reading/PLAN.md` first. It is the design; this brief is the build.

## Places
- Worktree (cwd, branch `opus/sol-reading`): `~/Projects/greek-ocr-toolkit-sol-reading`. All new code and outputs go under `docs/records/harvest/sol_reading/`.
- Pack root (outside every repository, writable): `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs` (call it PACK_ROOT).
- **Read-only sources** (never write there):
  - `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/efficiency/`: packs with PNGs (PNGs are git-ignored, so they exist only in this worktree), `keys/`, `score.py`, `build.py`, `build_owner39.py`, README.md.
  - `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/`: `verdicts/`, `yer_adjudication/`, `C1_REPORT.md`, `LABEL_CHECK_v2.md`.
  - `~/Projects/collect-v3-data/run/W1/c1/<set>/crops` and `<set>_key.json` (C1 card crops and keys).
  - Cached Opus reader outputs: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/eff/{out/*.jsonl,usage_log.tsv,agents.tsv}`, and owner39 answers at `…/efficiency/packs/owner39/<arm>/<reader>/answers.jsonl` where present.
  - R2 decks (owner39 controls): `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks/{T2,T4}/` (`blind/`, `private/`, `controls_proposed.json`), and the renderer `scripts/labelfix/r2_cards_prepare.py` there.
  - Owner truth: `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/`.
- Network off. Never push, never delete, never edit other worktrees.

## Tasks
1. **Git.** `git merge --ff-only sol/collect-v3` on `opus/sol-reading`. The branch is one commit behind, and the untracked `docs/records/harvest/sol_reading/` must survive. Report both SHAs.

2. **Opus reference copy.** Copy (do not move) the cached Opus outputs into `docs/records/harvest/sol_reading/opus_reference/`:
   - bsb and yer outputs for every arm;
   - `usage_log.tsv` and `agents.tsv`;
   - every owner39 `answers.jsonl` found, named `owner39_<arm>_<reader>.jsonl`.

   Write a sha256 manifest of the copies.

3. **Packs: `tools/build_packs.py`,** deterministic, seeded by `sol-reading:<bed>:<reader>`. It writes to `PACK_ROOT/<bed>/{r1,r2}/`. Private keys go to `docs/records/harvest/sol_reading/keys/<bed>.json`.
   - **Items.**
     - bsb: the 100 cards of `packs/bsb/E1/r1/cards.jsonl` plus 10 controls.
     - yer: the 59 items of `packs/yer/E1/r1/items.jsonl` plus 6 controls.
     - owner39: the 39 cards of `packs/owner39/E0a/r1/cards.jsonl` plus 4 controls. Ignore that folder's `answers.jsonl` and `zoom/`, which are Opus leftovers.
   - **Order.** r1 is a seeded random order of bed items and controls mixed. r2 is its exact reverse.
   - **Ids.** Every item gets a fresh opaque id (`k` + 10 hex). PNGs are copied (no links), with metadata stripped and RGB pixels unchanged, and named by content hash. Card fields keep exactly the public field set of the source pack (bsb: `card_id, crop, google_text, word_scripts`; yer: `item_id, crop, masked_text, slots`; owner39: the R2 public fields). Image paths are relative to the item file.
   - **owner39 options.** Permute the option letters A–D per card (seeded) and record the permutation in the key. `README.md` and `answer_schema.json` are copied byte-identical from the owner39 E0a pack.
   - **Controls.**
     - **bsb, 10:** from nlg poly1850 C1 cards (`verdicts/nlg__poly1850__*.jsonl` and the C1 crops) whose verdict is letters=y, marks=y, crop_ok=y. Seeded pick, no line shared with the bed. Recompute `word_scripts` after the edit.
       - 5 letter controls: in one word of ≥5 letters, replace one interior base letter that carries no mark with `π` (or with `λ` if it is `π`). Expected: letters=n.
       - 5 mark controls: remove the accent (U+0301, U+0300 or U+0342 after NFD; keep breathings) from one word of ≥5 letters, then NFC. Expected: marks=n.
     - **yer, 6:** from ia_russian cyrillic C1 cards that are not among the 59 yer lines. Mask with exactly the bed's masking rule: read how `yer_adjudication/items_*.jsonl` and `efficiency/build.py` produced `masked_text`/`slots`, and mirror it.
       - 3 items from pre-1918 lines whose masked slots are all Google ъ. Expected: ъ.
       - 3 items from lines with no ъ, ѣ, і or ѳ anywhere and masked slots that are all Google ь. Expected: ь.
     - **owner39, 4:** planted controls from the R2 T2/T4 private keys that are recorded as pixel-verified. Take a mix: at least one marked anchor and at least one where `literal` is the expected choice. Re-render or copy them so their `word_image`/`line_image` follow the owner39 E0 rendering (port the formula from `build_owner39.py`; do not import spell-check modules). The expected answer is the key's verified form. If no verified controls exist or the fields cannot be made identical, STOP that part and say so in the report.
   - **Lead review sheet.** Write one private contact sheet per bed of controls to `docs/records/harvest/sol_reading/keys/control_review/<bed>.png`, plus a `.md` listing each control id and its expected answer. Each tile shows the crop (yer: with the masked word boxed if geometry is available), the shown text and the expected answer. The lead pixel-checks these before any reader starts.

4. **Pack leak scan: `tools/scan_packs.py`.** Check each reader folder:
   - folder closure: only the item file, images, and for owner39 `README.md` and `answer_schema.json`;
   - no symlinks or hardlinks;
   - exact public field sets;
   - no source ids, line ids, `c\d{3}`/`a\d{3}` ids or truth strings in any file;
   - every PNG decodes, with no text metadata;
   - r2 is the exact reverse of r1.

   Write `PACK_ROOT/<bed>/<reader>/../MANIFEST.<reader>.json`, a sha256 list kept beside, not inside, the reader folder. Exit non-zero on any failure.

5. **Rollout leak scan: `tools/scan_rollout.py <rollout.jsonl> <reader_dir>`.** Codex code mode records every tool use as a `custom_tool_call` named `exec`. Its `input` is JavaScript calling `tools.view_image({path})` or `tools.exec_command({cmd})`; `function_call` and `local_shell_call` may also occur. The scanner:
   - extracts every path and command;
   - flags any absolute path outside `reader_dir`, any `..`, `~`, `$HOME` or `/Users/`, and the substrings `key`, `truth`, `verdict`, `Projects`, `sol_reading_packs/` + another reader's name, `opus_reference` and `MANIFEST` (case-insensitive) in inputs;
   - verifies the reader folder against its MANIFEST: originals unchanged; only `answers.jsonl` and `zoom/**` added.

   It outputs JSON (`ok`, `violations`, number of `view_image` calls, distinct images viewed, number of exec commands, final `total_token_usage`, `rate_limits`) and exits 2 on any violation. Test it on a synthetic rollout with a planted violation, and run it on the probe rollout `~/.codex/sessions/2026/10/17/rollout-2026-10-17T12-27-30-01a14930-13a7-7f61-b21f-ed58bc8d20b0.jsonl` with reader_dir `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/probe_img/A`. It must flag the canary `cat` of `…/scratchpad/canary_outside.txt`; that run has no MANIFEST, so skip that check with a flag.

6. **Answer mapper: `tools/map_answers.py <bed> <reader> <answers.jsonl>`.** It validates the answers:
   - one line per item, in order;
   - required fields;
   - yer slot coverage;
   - owner39 schema plus the head/transcription agreement rule as in `efficiency/score.py`.

   It then maps opaque ids back to the efficiency pack ids (bsb `c…`, yer `a…`, owner39 card ids) and the owner39 option letters back to the source letters. It writes:
   - `answers/<bed>/<reader>.mapped.jsonl` (bed items only), in the format `efficiency/score.py` accepts for `--verdict <bed> E1 r1` (bsb/yer) or `--verdict owner39 E0a r1`;
   - `answers/<bed>/<reader>.controls.json`, with per-control pass/fail against expected, plus the count of control errors.

   Test this with synthetic answers.

7. **Ledger: `tools/ledger.py add`.** Arguments: `--run <json line printed by run_read.sh>`, `--before "<limit_probe line>"`, `--after "<limit_probe line>"`, `--bed --reader --items N`. It appends a record to `docs/records/harvest/sol_reading/usage_ledger.json`:
   - bed, reader, items;
   - wall seconds;
   - input, cached input, output and reasoning tokens, total and per item;
   - tool calls;
   - weekly used before and after, and the delta;
   - credits balance before and after (parse from the run's `rate_limits_in_rollout` where present);
   - weekly points per 100 items;
   - the rollout path.

   It refuses duplicates. The launcher's output format is in `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/run_read.sh`, and the probe line format is in `…/scratchpad/limit_probe.log`. Test it with the probe lines.

8. **Tests and receipt.**
   - `tools/test_*.py` with stdlib `unittest`. Run them, and save the output to `docs/records/harvest/sol_reading/TEST_RESULTS_B1.txt`.
   - `docs/records/harvest/sol_reading/BUILD_RECEIPT_B1.json`: inputs with sha256; every reader folder with its item count, control ids and manifest sha; choices made.
   - Run `tools/scan_packs.py` on all 6 reader folders and include its output.

9. **Commit** on `opus/sol-reading`: everything under `docs/records/harvest/sol_reading/`, including the lead's PLAN.md, GUIDE_NOTES.md, `prompts/` and `briefs/`. PNGs stay outside the repo. Use the message `SR-B1: Sol-reading packs, controls, scanners, mapper, ledger` and end it with the line `Co-Authored-By: gpt-6.1-sol via Codex`. No push.

Python 3.11 with Pillow for PNG work: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B` (as in the efficiency README). Do not run any reader, and do not call codex.

Last line of your final message: `SR-B1 READY: <commit sha> packs=<n folders> controls bsb/yer/owner39=<n>/<n>/<n> tests=<pass>/<total>`, or `SR-B1 BLOCKED: <reason>`.
