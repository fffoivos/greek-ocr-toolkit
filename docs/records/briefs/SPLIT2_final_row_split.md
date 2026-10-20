# SPLIT2: the final W1/W2 row split from SPLIT1 (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Decision, owner via coordinator, 19 Oct night:** SPLIT1 is **adopted exactly as proposed**. Every W1/W2 row takes its SPLIT1 `proposed_split` as its final `split`, with no changes. The forced editions stay test. This task converts it to the census split input (night plan step P1). It decides nothing.

**Rules:**
- Athens time, stamped from `date`.
- No pushes, no Clariden.
- Read-only: the SPLIT1 directory, `~/Projects/collect-v3-data`, and the other worktrees named below.
- A tool is exactly the rule above: add no extra filtering. Anything extra goes into the receipt as a diagnostic.

## Inputs (read-only)
- `docs/harvest/collect_v3_admission/split1/row_split_proposal.jsonl.gz` and `editions.jsonl` (commit d8286346). Verify their sha256 against `split1/COMMIT_SHA256SUMS.txt`.
- The schema: `~/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/seg_census/split_input.schema.json`. Required: parent_id, row_id, edition_id, `split` ∈ {train, dev, test}; optional `forced`. The schema's `$comment` says: unique (parent_id, row_id); one split per edition_id; the config is `split_input = {path, sha256}`; for .gz files the hash is over the **compressed** bytes.
- The consumer:
  - in the same worktree, `docs/records/harvest/seg_census/prepare_config.py`, `mock_split_stage.py` and `tests/test_census04.py`;
  - `greekocr/harvest/line_pipeline_sources.py`, whose `row_splits` lookup is keyed by `canonical([parent_id, row_id])`.
  Read them so that the file loads exactly as the census reads it.

## Do
1. Write `docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz`.
   - One object per SPLIT1 row: `{parent_id, row_id, edition_id, split, forced}`, with `split = proposed_split`.
   - Sort by (parent_id, row_id).
   - Use compact JSON (`separators=(',',':')`, `ensure_ascii=False`).
   - Make the gzip **deterministic**: mtime=0, no filename in the header, a fixed compresslevel. A rebuild must give the same sha256.
2. Write `split2/edition_map.jsonl`, one line per edition: edition_id, split, forced, forced reason (v2 split or locked-eval evidence, copied from editions.jsonl), member documents, rows per tranche, rows per class, gazette flag.
3. Write `split2/receipt.json`:
   - input shas;
   - the output sha256 over the compressed bytes, plus the uncompressed sha256;
   - row counts per split overall and per tranche (W1/W2) × source;
   - edition counts per split, forced editions and their rows;
   - the decision text above, the build time from `date`, the code sha and the interpreter.
   It must reconcile with SPLIT1 exactly:
   - rows 320,479 (W1 101,098; W2 219,381);
   - train 253,402, dev 7,007, test 60,070;
   - forced 99 editions / 52,468 rows, all test;
   - editions 1,359.
   Any difference is a stop: report it, do not adjust.
4. Write `split2/build_split2.py`, deterministic, plus `split2/test_split2.py`. The tests:
   - schema validation of every line;
   - unique (parent_id, row_id);
   - one split per edition;
   - forced editions are all test;
   - the counts reconcile with SPLIT1;
   - the rebuild is byte-identical;
   - **load-through:** the file goes through the census's own loader (prepare_config / mock_split_stage, imported read-only from the main-next worktree or re-invoked as the tests there do). Every row resolves to its split under the census key; report any row the loader cannot map.
5. Write `split2/SPLIT2.md`: what the file is, the census config snippet `{"split_input": {"path": "<deploy path>/row_split.jsonl.gz", "sha256": "<sha>"}}`, the counts table, and one note: the 436 BSB pages read after 05:24 are not in the 05:24 snapshots, so rows from any later snapshot have no split entry (they stay unassigned in the census).

Write a guarded commit list (split2/ only plus this brief). The last line must be exactly:
`SPLIT2: done | rows <n> | train/dev/test <a>/<b>/<c> | editions <e> (forced test <f>) | row_split.jsonl.gz sha256 <sha> | loader check <k>/<n> resolved | tests: <n> passed`
