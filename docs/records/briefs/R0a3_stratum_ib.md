# R0a3 — Draw the clean Wikisource locked stratum (i-b) (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-r0` (branch `opus/spellcheck-r0`, head at launch, after R0c). No `.git` writes. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; CTC forward passes (E3
`full_s0`, CPU) allowed on the drawn lines only (≤ 500 crops). Do not touch other worktrees.

## Input
The sourcing lead's T7 harvest: `~/Projects/greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0/` (branch `sol/wikisource-r0`, commit db011b01;
read-only): 5 books / 116 pages / 1,246 aligned human-label lines — `lines.jsonl` (line_id, label literal + NFC, alignment evidence), `crops/`,
`pages.jsonl` (Google geometry), `RECEIPT.md`. All 1,246 are already in the release-exclusion manifest as `locked_eval_ib_wikisource`.

Note from the sourcing lead: (i-b) line ids carry an `r0-ws-` prefix (e.g. `r0-ws-e90ad4c2-p…`); match books on the bare 8-character
hashes 45855dfb, e90ad4c2, bf4f6c1b, df94dc99, a3114593 (in row `id` and `doc`) when computing intersections. Their pre-check: 0 rows of
these books in import_real_v2_{train,dev,test}.jsonl — reproduce it, don't just cite it.

## Do
1. Draw 300–500 complete polytonic lines, seeded 20261017, stratified by book (state per-book counts; no book > 40% if avoidable), using
   R0a's admission rules (`scripts/labelfix/r0_prepare.py`). Write `R0_locked_ib.jsonl`, `R0_locked_ib_ids.txt`, and add (i-b) to
   `R0_locked_set_receipt.json`: zero-intersection receipts against the 666, DEV, L1_input_documents, stratum (ii), (i-a), the 20 local
   Wikisource books, AND **collection v2 val** (`import_real_v2_dev.jsonl`) — print each; never-tune statement; label "clean locked Wikisource
   stratum".
2. Google labels: from the harvest's Google geometry/text if present (say what you used); human text from `lines.jsonl`.
3. CTC-align the drawn crops → `.cache/labelfix/r0/align_locked_ib.jsonl` + receipt; span-placement census as in R0a.
4. Build the blind card deck exactly like R0a's into `docs/records/labelfix/spellcheck/R0_cards_ib/` (private key under `R0_adjudication_private/ib/`),
   ≥ 8% planted controls. **Plus MARK cards (coordinator: (i-b) is the comparison set for L1/wave 1c, so it needs mark print truth, the S2
   way):** for every word where the mark sets of Google, the human text, R1-A (run R1-A on these lines' windows on CPU with the unchanged
   extraction; it is ≤ 500 lines) or the S6 detector differ, a card with the zoom, the full line and the distinct marked forms (≤ 3, random
   order, sources hidden), plus planted mark controls. Keep letter and mark cards in one deck but label kinds in the private key.

## Deliverables
Files above, an `R0_REPORT.md` section, last line:
`R0a3 READY: stratum (i-b) <n> lines / 5 books (<per-book counts>); zero overlap with 666, DEV, L1 input, (ii), (i-a), local books, v2 val; cards <c> (+controls <k>); spans outside blob <z>%`.
