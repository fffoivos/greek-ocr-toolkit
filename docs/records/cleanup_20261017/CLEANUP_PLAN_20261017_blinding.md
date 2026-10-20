# Blinding appendix: could the blind readers reach the answer key?

Read-only audit, 17 Oct 2026. Sources: the reader subagent transcripts (`~/.claude/projects/-Users-foivoskarounos-zamparloukos/<session>/subagents/agent-*.jsonl` and `.meta.json`), the coordinator transcripts that launched them, and the directories as they stand on disk. Times are Athens time.

**How I checked.** For every reader I pulled (a) the prompt it was given, (b) every file path that appears in its tool calls, (c) every `ls`/`find`/`Glob`/`Grep` call, and (d) every tool result that printed a key-like file name. I also recorded the reader's primary working directory, which the harness shows to each agent. All readers were **Claude Opus subagents** (`"model":"opus"` in every meta file). The Codex/Sol sessions that touch these decks are card builders and scorers (R0a/R0c, S8a–S8a7, L1A2, W1*), not readers. No Sol reader was found.

**Verdict labels.**
- "key not in reach": the folder the reader was pointed at holds no key. The key sits in a separate (sibling) private folder and is reachable only by typing its path.
- "key-in-reach": the key file, or the label text, sits in the same folder as the items, in the reader's working directory, or one level above the image folder.

Reading a key is possible in every case, because all readers have full filesystem access. "Opened" means a transcript shows the key being read.

| # | Adjudication | Readers (Opus) | Handed | Key relative to that | Prompt forbade key? | Key actually read? | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 189-word print truth (16 Oct ~20:00) | 8 (4 batches × 2) + 1 tiebreak | `scratchpad(b1155)/adj/batchN.json` + `adj/img/P###.png` | `key_SEALED.json` in the **same folder** (with `items_public.json`, `build.py`, other readers' `answers_*`) | No for the 8 main readers; tiebreak: "Do not open any other answers_* file" | No. Two readers ran `ls adj/ \| head`; the 10-line cut stopped at `items_public.json`, just before `key_SEALED.json` | **key-in-reach (not opened per transcripts)** |
| 2 | Implicit S4→S6 (16 Oct 23:00 / 23:25) | 2 + 2 (two rounds) | `scratchpad(b1155)/adj_s6/items_blind.json`; round 2 `crit6/adj_s6/items_blind_todo.json` | `items_key.json` in the **same folder** (the prep script writes both there); round-2 parent `crit6/` also holds `owner_sheet.html`, `s4_review.html`, `implicit_regressions_s6.json` | Yes, all 4 ("no key files, no other reader's answers") | No; no listings | **key-in-reach (not opened per transcripts)** |
| 3 | Yer ъ/ь (17 Oct 09:41–09:48) | 1 orthographic-prior reader + 2 ink readers (one ink reader per item) | `scratchpad(8014)/adj_yer/{prior_items,items_a,items_b}.jsonl` + `INK.md`/`PRIOR.md`; crops under `c1/ia_russian__cyrillic/crops` and `v2/ia_russian/crops` | `key.json` (holds `google_text`, i.e. the hidden letters) in the **same folder**; the C1 `cards_*.jsonl` and `v2/.../cards.jsonl` sit one level above the crop folders | Yes ("Never open key files or anything else in the folder") | No. The prior reader's `ls adj_yer/` printed `key.json`, and it did not open it | **key-in-reach (not opened per transcripts)** |
| 4a | R0b word decks (main, i-a, i-b) + tiebreaks (17 Oct 01:40–02:40) | main 8 + tiebreak 1; i-a 2; i-b 4 + tiebreak 1 | `scratchpad(b1155)/r0b/{batchN,ia,ib1,ib2,tiebreak,ib_tiebreak}.json`; PNGs in `greek-ocr-toolkit-spellcheck-r0/docs/labelfix/spellcheck/R0_cards*/img/` | Key `R0_adjudication_private/items_key.json` (+`ia/`, `ib/`) is a **sibling** of `R0_cards*`, not in the handed folder; `R0_cards*/index.html` has no key fields. The 8 main readers' working directory = the `-r0` repo root | Yes, all ("no keys, no other answers" / "Open nothing else") | No. Two i-b readers listed `scratchpad/r0b/` and saw other decks' answer and merge files (`r0b_merge.json`, `ia_merge.json`), and did not open them | **key not in reach** (sibling private folder; reachable by path; not opened) |
| 4b | R0 whole-line deck (17 Oct 02:24–02:44) | 2 + 1 tiebreak | `scratchpad(b1155)/wl/wl_blind.json`, `wl_tiebreak.json` | `wl_key.json` in the **same folder** (holds only stratum/line_id/img, no text). The img paths name book/page/line, and their folders hold the label text: `wikisource_r0/lines.jsonl`, `t4c/<set>/cards.jsonl`, `c0/<set>_key.json` | Yes ("Open no other file" / "Open nothing else") | No | **key-in-reach (not opened per transcripts)** |
| 5 | S8 DEV print-truth deck (17 Oct 05:10–05:31) | wave 1: 8 (2 × 4 ranges); cut deck: 16 (2 × 8 ranges); tiebreak 1 | `S8_DEV/cards/items_blind.json` / `items_blind_cut.json` + `cards/img/`; tiebreak: `cards_private/tiebreak/items_tb.json` | Key `S8_DEV/private/cards/items_key.json`, a **sibling** private folder. Readers wrote into `cards_private/readers/`, which holds the other readers' answers but no key. Working directory = `-s8` repo root | Yes ("nothing named *key*, private/, cards_private/ except your own output file, … other readers' files") | No. One reader (cut reader 2, items 450–539) ran `ls cards_private/readers/` and saw the other readers' file names; it did not open them | **key not in reach** (not opened; one listing of the readers' folder) |
| 6a | L1A audit (`S8_DEV/audit`, 124 items; 17 Oct 04:28–04:36) | 4 (2 × 2 ranges) + tiebreak 1 | `S8_DEV/audit/items_blind.json` + `audit/img/`; tiebreak `audit_private/tiebreak/items_tb.json` | Key `S8_DEV/private/audit/items_key.json` (sibling) | Yes | No | **key not in reach** (not opened) |
| 6b | L1A2 audit100 (17 Oct 07:04–07:06) | 4 (2 × 2 ranges) + tiebreak 1 | `S8_DEV/audit100/items_blind.json` + images; tiebreak `audit100_private/tiebreak/items_tb.json` | Key `S8_DEV/private/audit100/items_key.json` (sibling) | Yes | No | **key not in reach** (not opened) |
| 7 | C1 label check (17 Oct 08:46–10:17) | 28, one per half-deck (14 sets × halves a/b; each card read by one reader) | `scratchpad(8014)/c1/<set>/cards_{a,b}.jsonl` + `c1/LABEL_CHECK_v2.md`; `crops` is a **symlink** to `~/Projects/collect-v3-data/run/W1/c1/<set>/crops` | Key `~/Projects/collect-v3-data/run/W1/c1/<set>_key.json` is the **parent of the symlink target**. For the two bsb readers the working directory was that key folder (164 `*_key.json`) | Yes ("Never open key files or anything else") | No. One reader's `ls -la` printed the symlink target path | **key-in-reach (not opened per transcripts)** |

No adjudication shows a key file actually opened by a reader.

---

## 1. 189-word print truth

- **Readers.** Eight "Blind print reader bN rM" agents (b0–b3 × r1/r2) plus "Blind print reader tiebreak" (a59d5277…), in session `b1155dbd…`, 16 Oct 20:03–20:26.
- **Handed.** Prompt: "Items: /private/tmp/claude-501/…/b1155dbd…/scratchpad/adj/batch0.json (a JSON list of {id, image, A, B}) … Write your answers … to …/adj/answers_b0_r1.jsonl". Items contain only `id, image, A, B`.
- **Key location.** The folder `scratchpad(b1155)/adj/` holds `key_SEALED.json`. It maps each item to `line_id`, `google`, `human`, `kind`, `cluster`. The same folder holds `items_public.json`, `build.py`, `reconcile.py` and the other readers' `answers_*.jsonl`. The copy in `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/print_truth/` was not the copy handed to readers.
- **Instruction.** The eight main prompts say nothing about keys or other files. Only the tiebreak prompt says "Do not open any other answers_* file in that folder."
- **Evidence.** Reader b0 r1 (af9942…) ran `cd …/adj/; ls | head`. Reader b2 r2 (abc769…) ran `ls …/adj/ | head`. Both results end at `… build.py | crops | crops_r2 | img | items_public.json`; `head` cut the list before `key_SEALED.json`. No reader's tool calls name `key_SEALED`, `items_public`, `build.py` or `reconcile.py`. Each reader names only its own batch and answers file. b0 r1's final message: "I did not open the existing answers_b0_r2.jsonl in that folder, so my reading stayed independent."
- **Verdict.** Key-in-reach (not opened per transcripts). The main prompts carried no prohibition.

## 2. Implicit S4→S6 adjudication

- **Readers.** Round 1: "Blind reader 1: S6 changes" (a8baf6a7…) and "Blind reader 2: S6 changes" (a606f75d…), 16 Oct 23:00. Round 2: "Blind reader 1/2: combined changes" (aca3165c…, ac672c07…), 23:25.
- **Handed.** Round 1: `scratchpad(b1155)/adj_s6/items_blind.json` (67 items: `id, img, line_img, A, B`). Round 2: `scratchpad(b1155)/crit6/adj_s6/items_blind_todo.json`.
- **Key location.** `items_key.json` in the same folder in both rounds. It adds `line, word, s4, s6, note, control`. `scripts/labelfix/owner_implicit_adjudication_prep.py` lines 53–54 write `{S}/adj_s6/items_key.json` and `{S}/adj_s6/items_blind.json` side by side. In round 2 the parent `crit6/` also holds `owner_sheet.html`, `s4_review.html`, `s4_examples.html`, `options_examples.html`, `implicit_regressions_s6.json` and `prior_printed.json`.
- **Instruction.** Present in all four prompts:
  - "Do not read any other file in that directory (no key files, no other reader's answers)."
  - "Open no other file in that directory besides the items file and the images it lists."
  - "Open no other file in that directory or its parents (no key files, no other answers)."
  - "Open nothing else in that directory or its parents besides the items file and its images."
- **Evidence.** The file tokens in all four transcripts are only `items_blind*.json`, `img/…png` and the reader's own `readerN.jsonl`. The one "keys" token is Python `d[0].keys()`. There were no directory listings.
- **Verdict.** Key-in-reach (not opened per transcripts).

## 3. Yer (ъ/ь) adjudication

- **Readers.** In sourcing-lead session `8014ea5c…`, 17 Oct ~09:41–09:48:
  - "Yer orthographic prior reader" (a01a1083…): 31 items, text only;
  - "Yer ink adjudication part a" (a4cdc517…): 30 items;
  - "Yer ink adjudication part b" (a7e9cd65…): 29 items.

  Each item had one ink reader. The working directory for all three was `~/Projects/greek-ocr-toolkit-sol-collect`.
- **Handed.** "Read the instructions at …/8014ea5c…/scratchpad/adj_yer/INK.md … ITEMS = …/adj_yer/items_a.jsonl". Crops came from `scratchpad(8014)/c1/ia_russian__cyrillic/crops/` (a symlink into `~/Projects/collect-v3-data/run/W1/c1/ia_russian__cyrillic/crops`) and from `scratchpad(8014)/v2/ia_russian/crops/`.
- **Key location.**
  - `adj_yer/key.json`, in the same folder. It holds `card_id`, `google_text` and slots, which reveal the hidden letters.
  - The label text also sits one level above the crop folders: `c1/ia_russian__cyrillic/cards_{a,b}.jsonl` and `v2/ia_russian/cards.jsonl`, both with `google_text`.
  - The C1 key `~/Projects/collect-v3-data/run/W1/c1/ia_russian__cyrillic_key.json` (`literal_label`) sits above the symlink target.
  - The repo copy `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/` (`INK.md`, `PRIOR.md`, `key.json` together) mirrors this layout.
- **Instruction.** INK.md: "Open only ITEMS and the crop images. Never open key files or anything else in the folder." PRIOR.md: "Open only ITEMS; never open any other file."
- **Evidence.** The prior reader ran `cat …/prior_items.jsonl; ls …/adj_yer/`. The result printed "INK.md | items_a.jsonl | items_b.jsonl | key.json | prior_items.jsonl | PRIOR.md", so it saw the key's name. Its later calls name only `PRIOR.md`, `prior_items.jsonl` and `prior.jsonl`. The ink readers name only `INK.md`, their own items/ink file, crop PNGs and their zoom PNGs. No `cards_*.jsonl`, `key.json` or `collect-v3-data` access by any of the three.
- **Verdict.** Key-in-reach (not opened per transcripts). The prior reader saw `key.json` listed.

## 4. R0

### 4a. R0b word decks

- **Readers.** All in session `b1155dbd…`, 17 Oct 01:40–02:40:
  - main deck: "R0b batch1–4 reader1/2" (8), plus "R0b tiebreak reader (17 cards)";
  - (i-a): "R0b (i-a) deck reader1/2";
  - (i-b): "(i-b) deck half1/half2 reader1/2" (4), plus "(i-b) tiebreak reader (14 cards)".

  The 8 main readers' working directory was `~/Projects/greek-ocr-toolkit-spellcheck-r0`. The i-b readers used `…-spellcheck`; the tiebreak and i-a readers used the memory folder.
- **Handed.** `scratchpad(b1155)/r0b/batch1.json` and siblings. Items are `id, img, line_img, A, B[, C]`. The images are absolute paths into `~/Projects/greek-ocr-toolkit-spellcheck-r0/docs/labelfix/spellcheck/R0_cards{,_ia,_ib}/img/`.
- **Key location.** `docs/records/labelfix/spellcheck/R0_adjudication_private/items_key.json` (plus `ia/`, `ib/`, `readers/`, `readers_ib/`) is a sibling of `R0_cards*`, two levels above the img folders. `scratchpad/r0b/` holds no key. During later rounds it did hold other readers' answers and merges (`r0b_merge.json` 01:48, `ia_merge.json` 01:50, `ib_merge.json` 02:36). A grep of `R0_cards*/index.html` finds no `line_id`, `candidate_sources` or `control` fields. The `R0_cards/README.md` itself says: "Keep `R0_adjudication_private/` … away from readers."
- **Instruction.** Present in every prompt. Examples: "Do not open any other file in or near that directory (no keys, no other answers)." "Open nothing else in that directory or its parents besides the items file and its images." "Open no other file."
- **Evidence.** The (i-b) half1 reader2 (a7634f9f…) and half2 reader2 (af09d21f…) ran `cd …/scratchpad/r0b/ && … ls`. The output listed `… ia_merge.json | ia_r1.jsonl | ia_r2.jsonl | ia.json | ib1.json | ib2.json | mk_b2r2.py | r0b_merge.json | tiebreak_r3.jsonl …`. Those are other decks' answers, not their own deck's. No reader names any of those files, `items_key`, `R0_adjudication_private` or `index.html` in a later call. The other readers listed only `R0_cards*/img/`.
- **Verdict.** Key not in reach of the handed folders (it sits in a sibling private folder, reachable by path). Not opened.

### 4b. R0 whole-line deck

- **Readers.** "Whole-line transcription reader1/2" (ac514889…, a9135bfe…) and "Whole-line tiebreak transcriber (16)" (a1ebfd4d…), 17 Oct 02:24–02:44.
- **Handed.** `scratchpad(b1155)/wl/wl_blind.json` (`id, img` only) and `wl_tiebreak.json`.
- **Key location.**
  - `wl_key.json` is in the same folder (also together in the repo copy `docs/records/labelfix/spellcheck/R0_wholeline/`). It holds `stratum, line_id, img, id`, with no truth text.
  - The img paths reveal book/page/line, e.g. `…sol-wsr0/docs/harvest/wikisource_r0/crops/df94dc99/r0-ws-df94dc99-p000175-l0005.png`. The Wikisource/Google label text for that `line_id` sits in `wikisource_r0/lines.jsonl`, one level above `crops/`. The 50 wikisource_r0 items are all of this kind.
  - The 13 t4c items have `blind_checks_v1/t4c/<set>/cards.jsonl` (with `google_text`) next to their `crops/`.
  - The 12 c0 items have `blind_checks_v1/c0/<set>_key.json` and earlier readers' `<set>_out.jsonl` one level above `<set>/crops/`.
- **Instruction.** "Open no other file." / "Open nothing else."
- **Evidence.** All file tokens are the reader's own `wl_*` files, zoom scripts and the listed PNGs. The "key"/"keys" tokens are Python dict calls. No access to `lines.jsonl`, `cards.jsonl` or `*_key.json`.
- **Verdict.** Key-in-reach (not opened per transcripts). The label text is reachable by path from each image.

## 5. S8 DEV print-truth deck

- **Readers.** Session `b1155dbd…`, 17 Oct 05:10–05:31:
  - "DEV reader 1/2, items 0-89 … 270-359": 8 readers;
  - "DEV cut reader 1/2, items 0-89 … 630-702": 16 readers;
  - "DEV tiebreak reader, 42 items".

  Working directory: `~/Projects/greek-ocr-toolkit-spellcheck-s8` for wave 1; the memory folder for the cut and tiebreak readers.
- **Handed.** "Read-only inputs: …/S8_DEV/cards/items_blind.json and images under …/S8_DEV/cards/img/" (cut deck: `items_blind_cut.json`). Outputs went to `S8_DEV/cards_private/readers/r{1,2}_*.jsonl`. The tiebreak reader read `cards_private/tiebreak/items_tb.json`.
- **Key location.** `S8_DEV/private/cards/items_key.json` (with `forms.google`, `r1_A`, …), a sibling of `cards/`. Contents of `cards/`: `index.html` (no key fields found), `state.json`, `answers_blank.json`, `README.md`, `cut_receipt.json` (indices and counts only). `cards_private/readers/` holds all readers' answers but no key. The tiebreak reader's folder `cards_private/tiebreak/` is next to it.
- **Instruction.** "Open NO other file or folder (nothing named *key*, private/, cards_private/ except your own output file, evidence/, reports, other readers' files)." Tiebreak: "Read only …/items_tb.json and the two image paths … open no other files."
- **Evidence.** "DEV cut reader 2, items 450-539" (ab741deb…) ran `… ls …/S8_DEV/cards_private/readers/ 2>&1 | head`. The result showed `r1_000.jsonl | r1_090.jsonl | … | r2_000.jsonl | r2_090.jsonl`. That listing broke the "cards_private/" instruction, but the reader opened none of those files: its only `.jsonl` token is its own `r2_cut_450.jsonl`. No reader names `private/cards`, `items_key` or `index.html`.
- **Verdict.** Key not in reach (sibling private folder). Not opened. One reader listed the other readers' answer folder without opening it.

## 6. L1A audits

### 6a. L1A audit (`S8_DEV/audit`)

- **Readers.** "Blind reader 1/2, audit items 0-61 / 62-123" (4) and "Tiebreak reader, 4 audit items", 17 Oct 04:28–04:36. Working directory: `~/Projects/greek-ocr-toolkit-spellcheck`. `L1A_AUDIT_REPORT.md` line 7 identifies this deck: "key `S8_DEV/private/audit/items_key.json`".
- **Handed.** `S8_DEV/audit/items_blind.json` + `audit/img/`, with output to `audit_private/readers/`.
- **Key location.** `S8_DEV/private/audit/items_key.json` (sibling).
- **Instruction.** "Do NOT open any other file or folder (in particular nothing named *key*, private/, evidence/, reports, or other readers' outputs)." Reader 2 was additionally told it "never see[s] their answers".
- **Evidence.** Only own files and the listed images. No listings of the private or readers folders.
- **Verdict.** Key not in reach. Not opened.

### 6b. L1A2 audit100

- **Readers.** "Audit100 reader 1/2, items 0-54 / 55-109" (4) and "Audit100 tiebreak, 9 items", 17 Oct 07:04–07:06.
- **Handed.** `S8_DEV/audit100/items_blind.json` + images. Contents of `audit100/`: `answers_blank.json`, `index.html`, `items_blind.json`, `README.md`, `img/`.
- **Key location.** `S8_DEV/private/audit100/items_key.json` (sibling).
- **Instruction.** "Open NO other file or folder (nothing named *key*, private/, audit100_private/ except your own output file, evidence/, reports, other readers' files)."
- **Evidence.** None of the 5 transcripts names `private/audit100` or `items_key`. The single tool result naming a readers file shows only the reader's own `r2_b.jsonl`.
- **Verdict.** Key not in reach. Not opened.

## 7. C1 label check

- **Readers.** 28 "C1 check <set> half a/b" agents in session `8014ea5c…`, 17 Oct 08:46–10:17: 14 sets × 2 halves. The halves are disjoint (e.g. nlg poly1900: 50 + 50 cards, overlap 0), so each card had one reader.
- **Handed.** "Read the instructions at …/scratchpad/c1/LABEL_CHECK_v2.md … CARDS = …/c1/nlg__poly1900/cards_a.jsonl … Crop paths are relative to the cards file's directory." Each card carries `google_text` by design, because the task is to check the label.
- **Key location.**
  - `scratchpad(8014)/c1/<set>/crops` is a symlink: `crops -> /Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/<set>/crops`.
  - The key `<set>_key.json` sits in `~/Projects/collect-v3-data/run/W1/c1/`, the parent of the symlink target. That folder holds 164 key files, with `line_id, source, primary_class, tags` (e.g. `"marks_correction_required"`), `source_marks` and `literal_label`.
  - The two bsb poly1850 readers (a17ac5d7…, a7048c6b…) had `cwd = /Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1`. Their primary working directory was the key folder itself.
  - The other 26 readers' working directory was `~/Projects/greek-ocr-toolkit-sol-collect`, which also holds `docs/records/harvest/collect_v3/rev2_final_replay/W1/c1/*_key.json` from an earlier replay. For bsb those keys differ from the run keys (`cmp`: DIFF).
- **Instruction.** LABEL_CHECK_v2.md: "Open only cards.jsonl and the crop images. Never open key files or anything else."
- **Evidence.**
  - No reader names any `*_key.json` or `collect-v3-data` path in a call.
  - The two bsb readers worked only with `cd …/scratchpad/c1/bsb_poly1850__poly1850/ && …` on `cards_*.jsonl` and `crops/`.
  - "C1 check gazette measured half b" (a465aac6…) ran `ls` in its set folder. The result showed "crops -> /Users/…/collect-v3-data/run/W1/c1/gazette_modern__modern_scanned__measured_1986_1990/crops", so that reader saw where the key folder is.
  - "C1 check serbia cyrillic half a" (a655536a…) reported: "When I enlarged the whole crops folder, that also made enlargements of crops that belong to cards_b; I did not look at them."
- **Verdict.** Key-in-reach (not opened per transcripts). For two readers it was in their working directory; for all 28 it was one folder above the resolved crop folder.

---

*Not covered.* Owner-facing HTML decks were not read by any reader in these seven adjudications. The other sourcing-lead blind checks (C0, T4c, "Blind label check/page check" on 16 Oct) and the geometry/alignment/delta adjudications in session `db202b49…` were outside the list.
