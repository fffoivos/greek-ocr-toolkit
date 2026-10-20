# SS7 — small-segment population key + owner typology marks for segmentation steps 4/5 (read-only build)

You are Sol, executing for the small-segment analysis lead. The owner adopted "small" = `chars ≤ 8 AND A ≤ 6`. Build two join
files for the segmentation lead, plus the tool that refreshes the second one. No judging, no reading of crops.

Worktree `~/Projects/greek-ocr-toolkit-sol-recut`. `B = docs/records/harvest/collect_v3_admission/segeval1`, `SS = B/small_segments`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
Write ONLY these new files: `SS/small_population_key.jsonl.gz`, `SS/owner_marks_smallseg.jsonl`, `SS/SS7_RECEIPT.json`,
`SS/tools/ss7_key.py`, `SS/tools/ss7_owner_marks.py`, `SS/tests/test_ss7.py`. Change nothing else (no tool code, no census, no
other segeval1 file); no git add/commit; no `codex`; temporary files only inside `SS/tools/` and removed before you finish.

## Inputs (read-only; sha256 each in the receipt)
- `B/cells/population_cells.jsonl.gz` — census, 592,466 rows (sha256 65dd9226…6dfc). Stream it.
- `SS/tools/ss1_q1.py` — import and reuse its `output_type`, rotation/A and `wave_group` functions; do not re-implement them.
- `SS/q1/SS1_RECEIPT.json`, `SS/q1/q1.json` — the recommended definition's counts to reconcile against.
- `B/owner_marks_20261019.jsonl` — the reference format: `sheet`, `line_id`, `owner_mark`, `note`, `updated`.
- `SS/sheet/card_manifest.json` — the 417 sheet cards (`line_id`, `doc_id` = `smallseg:<line_id>`).
- `SS/sheet/marks_dump/20261019T1827/notes/*.json` — the owner's sheet marks as dumped by the lead (one file per doc:
  `line_id`, `verdict` KEEP/DROP, `note`, `updated`; filename = `<doc_id>.json`). 185 files.

## 1. `SS/small_population_key.jsonl.gz` (`tools/ss7_key.py`)
One row per census row with `characters ≤ 8` and `A ≤ 6` (A = max(w,h)/min(w,h), via ss1_q1), sorted by `row_id`. Fields:
`row_id`, `chars` (`characters`), `text_characters`, `width_px`, `height_px`, `L`, `S`, `A` (round 4), `rotated` (h > w),
`output_type` (numeric/mixed/nonnumeric), `source`, `book` (`<source>--<16-hex>` prefix of row_id), `primary_class`,
`script_class`, `wave`, `verdict_05`, `reason_category` (ss1_q1 mapping), `crop_sha256`.
It must reconcile exactly with SS1: 59,002 rows; numeric 38,221 / nonnumeric 19,481 / mixed 1,300. If it does not, stop and
report `SS7 FAILED`. Gzip deterministically (mtime 0).

## 2. `SS/owner_marks_smallseg.jsonl` (`tools/ss7_owner_marks.py <dump_dir> <out>`)
One line per dumped mark, same keys and order as `owner_marks_20261019.jsonl`:
`{"sheet": "small_segments (417, Q3 typology)", "line_id": …, "owner_mark": KEEP|DROP, "note": …, "updated": …}`, sorted by
line_id, UTF-8, `ensure_ascii=False`. Refuse (non-zero exit, no output written) if: a filename's doc_id is not `smallseg:` +
the file's `line_id`; a line_id is not a card in `card_manifest.json`; a verdict is not KEEP/DROP; a line_id repeats. Print the
KEEP/DROP counts. The tool must be re-runnable by the lead on later dumps without changes. Run it once on the 20261019T1827 dump.

## Tests (`SS/tests/test_ss7.py`)
Key: the definition boundary (chars 8/9, A 6.0/6.0001, rotated crops use L/S), reconciliation counts, book prefix, sorted and
unique row_ids, deterministic gzip bytes. Marks: output keys equal the reference file's keys in order; each refusal case; sort
order; the 185-file dump gives 177 KEEP / 8 DROP.

## Receipt `SS/SS7_RECEIPT.json`
Inputs/outputs sha256, row counts (by output_type, by source), marks counts, test results, census sha256 before = after.
Last line exactly: `SS7 READY: key <n> rows SS/small_population_key.jsonl.gz, owner marks <m> (KEEP <k> / DROP <d>) SS/owner_marks_smallseg.jsonl`
(or `SS7 FAILED: <reason>`).
