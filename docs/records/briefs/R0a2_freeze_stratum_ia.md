# R0a2 — Freeze locked stratum (i-a) (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-r0` (branch `opus/spellcheck-r0`, head b7fd49ba). No `.git` writes. Network OFF. Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; CTC forward passes (E3 `full_s0`,
CPU) allowed on these ≤ 133 lines only. Do not touch other worktrees. Do NOT read `docs/records/labelfix/spellcheck/R0_adjudication_private/` or
anything that would reveal card answers; R0b (blind readers) is running on `R0_cards/` — do not modify `R0_cards/`.

## Coordinator ruling (17 Oct)
Stratum (i) = option (c): freeze the 133 eligible fresh Wikisource lines now as **(i-a)**; (i-b) will come from a new harvest later.

## Do
1. Re-run R0a's own eligibility logic (`scripts/labelfix/r0_prepare.py`) deterministically to produce the explicit list of the 133 lines
   (books 81d8091c 1, 309ff6cf 10, f7c74d15 122). Write `R0_locked_set.jsonl` (line id, book, crop path + sha256, human text, Google label)
   and update `R0_locked_set_receipt.json`: status FROZEN_IA, seed 20261017, books + counts, **"Ἀστέρια (f7c74d15) supplies 122/133 lines:
   stratum (i-a) is dominated by one book"**, zero-intersection receipts against the 666, DEV, L1_input_documents, stratum (ii), and the
   never-tune statement. Also write `R0_locked_ia_ids.txt` (line ids) for the sourcing lead's release-exclusion manifest.
2. CTC-align the 133 crops (E3 `full_s0`, CPU, same code path as the 666 cache) → `.cache/labelfix/r0/align_locked_ia.jsonl` + receipt.
3. Build their adjudication cards exactly like R0a's (same generator, same blind/key separation, same control rate) into a SEPARATE deck
   `docs/records/labelfix/spellcheck/R0_cards_ia/` (+ private key under `R0_adjudication_private/ia/` — write it, don't read the existing one).
4. Span-placement census for the 133 lines as in R0a.

## Deliverables
Files above, a short section appended to `R0_REPORT.md`, last line:
`R0a2 READY: stratum (i-a) <n> lines / 3 books (Ἀστέρια <k>); zero overlap with 666, DEV, L1 input, (ii); cards <c> (+controls <m>); spans outside blob <z>%`.
