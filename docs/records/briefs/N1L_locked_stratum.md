# N1-L: lock the N1 evaluation stratum (gpt-6.1-sol, medium, network OFF; no .git writes; Mac CPU only; no images opened)

You work in the worktree `~/Projects/greek-ocr-toolkit-secondary` (branch `opus/secondary-corrections`). Plan:
`docs/records/labelfix/secondary/PLAN.md` §2 and `docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md` (coordinator condition 1). The step-0 outputs
are in `artifacts/n1/` (`census.json`, `frame_step1.jsonl`, `locked_eval_docs.json`). The report is `docs/records/labelfix/N1_STEP0_REPORT.md`.

**Read-only inputs.**
- `~/Projects/collect-v3-data/run/W1/features.jsonl`. This is a LIVE collector root: read only. Never create, take or touch
  `run.lock`, and write nothing under `~/Projects/collect-v3-data/`.
- The wave-1d preregistered admissions `w1_masked_1d.jsonl`. Find it under
  `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/`, or search that worktree. Do not modify it.
- The existing exclusion files in `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/`, for format
  reference only. Do not modify them; registration is the sourcing lead's job.

**Do.**
1. **Verify the frozen inputs.** Check the sha256 of `frame_step1.jsonl` and `locked_eval_docs.json` against the hashes recorded in
   `census.json` or the step-0 receipt. Stop on a mismatch.
2. **Write the lock files in `artifacts/n1/`:**
   - `n1_locked_eval_line_ids.txt`: the sorted, unique W1 `id` (features.jsonl `id` field) of every line that carries a
     `partition == "locked_eval"` slot. One id per line, LF, no header.
   - `n1_reserved_docs.txt`: the reserved-document list (`source:item`) from `locked_eval_docs.json`.
   - `n1_reserved_doc_line_ids.txt`: every W1 `id` belonging to a reserved document, every page. This is the fitting-exclusion list:
     no N1 fitting may read these lines.
3. **Checks.** Write all results to the receipt.
   - (a) Every locked id exists in features.jsonl, and its source is elstat or gazette.
   - (b) Per-source slot counts are 100/100/100.
   - (c) No locked or reserved-document line appears in any `partition == "step1"` row, and no step1 document is reserved.
   - (d) No C1 card line is in the locked set.
   - (e) Overlap counts of `n1_locked_eval_line_ids.txt` with: the wave-1d rows (by W1 id), and each existing exclusion id file.
4. **If the wave-1d overlap in 3(e) is above 0:** also write `artifacts/n1/frame_locked_alt.jsonl`. It is a deterministic alternative
   locked draw, seed `20261017:N1L:alt`. It uses the same reserved documents, the same per-source quotas (100 each, 90 observed
   separator/table candidates + 10 remaining, as in step 0) and the same row schema, and it excludes wave-1d rows. Write
   `n1_locked_eval_line_ids_alt.txt` beside it. Do NOT modify `frame_step1.jsonl` or `locked_eval_docs.json`. The lead chooses which
   lock to register.
5. **Guard module.** Add `greekocr/numerics/locks.py` with:
   - `load_locks(dir) -> Locks`;
   - `Locks.is_locked_line(id)`;
   - `Locks.is_reserved_line(id)`;
   - `Locks.assert_fit_rows(ids)`, which raises if any id is reserved.

   Add tests in `tests/test_numeric_locks.py` using small fixtures. Run them together with `tests/test_numeric_tokens.py` using
   `python3 -m pytest --noconftest -q` (the conftest needs Torch, which is not needed here).
6. **Receipt.** Write `artifacts/n1/N1L_RECEIPT.json`. It holds the inputs with sha256, the outputs with sha256 and line counts, every
   check result, the overlap table, and the pytest summary.

**Constraints.**
- Allowed writes: `artifacts/n1/` (new files only), `greekocr/numerics/locks.py`, `tests/test_numeric_locks.py`, and a short report
  `docs/records/labelfix/secondary/N1L_REPORT.md`.
- Do not touch `greekocr/labelfix/` or any other package.
- Do not open, decode or render images.

**Last line:** `N1L READY: locked lines <n> (elstat <n>, gazette82 <n>, gazette86 <n>); reserved docs <n>, reserved lines <n>; overlap 1d <n>, other exclusions <n>; alt <written|not needed>; locked sha256 <hex>; tests <n> passed`
