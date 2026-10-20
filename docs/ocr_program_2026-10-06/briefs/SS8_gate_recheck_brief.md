# SS8 — recompute Q1–Q3 without content-gate failures; add a gate flag to the SS7 key (read-only analysis)

You are Sol, executing for the small-segment analysis lead. The pipeline's content gate (expected scripts per document;
mixed-script words) recorded lines as suspicious but did not exclude them. The coordinator listed them by a plain Unicode-script
rule. Recompute the small-segment numbers without them and add a flag column to the key. No judging, no crop reading.

Worktree `~/Projects/greek-ocr-toolkit-sol-recut`. `B = docs/records/harvest/collect_v3_admission/segeval1`, `SS = B/small_segments`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
Write ONLY under `SS/gate_recheck/` (new files), plus new files `SS/small_population_key.v2.jsonl.gz`, `SS/tools/ss8_*.py`,
`SS/tests/test_ss8.py`. Do not modify any existing file (the SS1–SS7 tools, tables, `small_population_key.jsonl.gz`, census);
import the existing tools' functions instead of copying their logic. No git add/commit; no `codex`. Temp files only in
`SS/gate_recheck/tmp/`, removed before you finish.

## Inputs (read-only; sha256 each in the receipt)
- `SS/gate_recheck/foreign_mixed_ids_20261019.json` (sha256 74d8a280…6f58): `{"foreign": [1,006 row ids], "mixed": [1,698]}`.
  `gate_failed` = row id in either list; `gate_reason` = `foreign`, `mixed` or `both`.
- `B/cells/population_cells.jsonl.gz` (592,466 rows) and the inputs SS1/SS2 used (see `SS/q1/SS1_RECEIPT.json`,
  `SS/q2/SS2_RECEIPT.json`, `SS/briefs/SS1_q1_dimensions.md`, `SS/briefs/SS2_q2_origin.md`).
- `SS/tools/ss1_q1.py`, `SS/tools/ss2_q2.py`, `SS/q1/q1.json`, `SS/q1/owner_joined.jsonl`, `SS/q2/q2.json`.
- `SS/samples.jsonl`, `SS/q3/q3.json`, `SS/q3/Q3_TABLES.md`, `SS/q3/SS3_RECEIPT.json` (pool counts per source), `SS/q3/key_opus.jsonl`.
- `SS/small_population_key.jsonl.gz`, `SS/owner_marks_smallseg.jsonl`.

## 1. Reconcile the id list
Count gate_failed rows: in the census (expect 1,006 foreign / 1,698 mixed, report the overlap and any id not in the census);
in the key (expect 672 foreign + 37 mixed); in the 417 sheet bed rows of samples.jsonl (expect 18 + 3) and in the 20 controls;
in key_opus.jsonl (7 + 2); in owner_marks_smallseg.jsonl (0 + 1). Report each with mismatches named. For the sample rows
list line_id, final_type, final_class, Google text, gate_reason.

## 2. Q1 recompute (`gate_recheck/Q1_GATE.md` + `.json`)
Rerun the Q1 computations on the census minus gate_failed rows, with the same functions. Before / after / delta for:
- every candidate definition row of Q1 (rows inside, box_fail % inside and outside, owner good/bad inside and outside, owner-good
  0.5 false rejects inside), the recommended `chars ≤ 8 & A ≤ 6` in bold;
- the failure-rate-by-chars curves (nonnumeric+mixed and numeric) on correctly sized crops;
- the owner-judged line totals (362 unique; how many removed).

## 3. Q2 recompute (`gate_recheck/Q2_GATE.md` + `.json`)
For the recommended definition: source shares and density, wave shares, primary_class shares, book concentration (books for
50/80/95%, nonnumeric-only and baseline), page measures; before / after / delta.

## 4. Q3 recompute (`gate_recheck/Q3_GATE.md` + `.json`)
- T8 again with gate_failed rows removed from the 150-row inside_by_source sample and from the source pool weights (pool counts
  minus gate_failed small nonnumeric/mixed rows per source, from the key); before / after / delta per class and per final_type,
  Wilson intervals on the new unweighted shares; state the new n.
- Bed class counts (417 and inside 306) before / after.
- Legit-text and punctuation label_ok shares before / after.
- Owner sheet marks: KEEP/DROP before / after.

## 5. Key v2 — `SS/small_population_key.v2.jsonl.gz` (`tools/ss8_key_v2.py`)
Same rows, order and fields as `small_population_key.jsonl.gz`, plus `gate_failed` (bool) and `gate_reason` (null when false).
Deterministic gzip (mtime 0). Verify every v1 field is byte-identical per row.

## Tests (`SS/tests/test_ss8.py`)
Flag/reason assignment incl. `both`; v2 equals v1 plus the two fields; recompute with an empty exclusion list reproduces the
stored SS1/SS2/SS3 numbers exactly (this is the guard that the recompute is the same computation); reweighting arithmetic.

## Receipt `SS/gate_recheck/SS8_RECEIPT.json`
Inputs/outputs sha256, reconciliation, test results, census sha256 before = after.
Last line exactly: `SS8 READY: excluded <n> census rows (<k> small), key v2 <rows> rows, tables gate_recheck/Q{1,2,3}_GATE.md`
(or `SS8 FAILED: <reason>`).
