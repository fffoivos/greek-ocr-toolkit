# R2C2: resolver protocol fixes found on the first T2 answers (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r2cards`, branch `opus/r2-cards`, head 6130a4b8).
- No `.git` writes.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- **Do not modify any deck file** under `docs/records/labelfix/spellcheck/R2/decks/*/blind/`, and nothing in any reader folder: readers are still
  working. Edit only `scripts/labelfix/r2_cards_resolve.py`, its tests, and the private control key files named below.

The lead checked the 13 finished T2 reader batches (answers in
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/r2read_T2_r{1,2}/bNN/answers.jsonl`;
read-only for you, and only for testing). Two protocol defects showed up. Neither is reader carelessness.

## Defect 1: ownership on an UNMARKED anchor

All 79 T2 controls (and the T4 ones) expect `ownership_ok: true`, even when the anchor letter has no mark at all. Some readers correctly
answer `null` ("no mark, so ownership does not apply"). That fails them on 5–9 controls per batch, although form and heads are right,
and it would reject entire batches.

**Fix (a key/protocol fix, documented as such):**
- When the anchor's four heads are all `none`, in the answer or in the control expectation, ownership is **not applicable**. Normalise it
  to `None` both in control comparison and in the agreement signature. Otherwise true vs null creates spurious disagreements and
  tiebreaks on unmarked anchors.
- Update `private/controls_proposed.json` in T2 and T4: `expected_ownership_ok = null` for every control whose expected anchor heads are
  all none. Record `key_fix_20261017: "ownership not applicable on unmarked anchor"` per changed control.
- Keep `lead_verified` as it is.

## Defect 2: one inconsistent answer must not kill a batch

`normalise` raises for the whole file when one answer's head tuple contradicts its own transcription, or an index lies outside it. That
happened on about 13 answers across the 13 batches.

**Fix:**
- Per-card validation: an invalid answer becomes an **invalid vote** for that card, recorded with its reason. It is excluded from
  agreement, so the card goes to the tiebreak if the other reader's vote is valid. It is counted in the receipt and the usage table.
- An invalid answer on a CONTROL counts as a control failure (the gate stays strict).
- A batch is still rejected only by the control gate (> 1 control failure), never by one malformed data card.

## Tests and report

- Unit tests for both fixes with synthetic cards.
- Run the resolver's validation over the real finished T2 answer files, read-only, in a dry-run mode that writes NOTHING into the deck or
  reader folders: output under `artifacts/r2c2_dryrun/`. Report per batch: control results and invalid-answer counts, before vs after.
- Append "R2C2 resolver fixes" to `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md`.

Last line:
`R2C2 READY: ownership n/a rule; per-card invalid votes; controls changed T2 <a> / T4 <b>; dry-run batches passing gate <k>/<n>; tests <n> passed`.
