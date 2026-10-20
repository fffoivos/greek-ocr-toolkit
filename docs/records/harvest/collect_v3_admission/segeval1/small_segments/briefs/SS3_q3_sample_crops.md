# SS3 — Q3 sample: draw ~390 non-numeric small crops, reconstruct byte-exact, propose controls (no reading)

You are Sol, executing for the small-segment analysis lead. Draw a seeded stratified sample, reconstruct the crops byte-exact
from local data, and build contact sheets for the lead's eye. Do not type, read or judge the crops.

Worktree: `~/Projects/greek-ocr-toolkit-sol-recut` (branch `sol/recut-v1`). `B = docs/records/harvest/collect_v3_admission/segeval1`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
- Write ONLY under `B/small_segments/q3/`, `B/small_segments/crops/`, `B/small_segments/tools/` (new files only; do not edit
  `ss1_q1.py`, `ss2_q2.py`) and `B/small_segments/tests/` (new files only). Change nothing else; no git add/commit; no network;
  no Clariden; no page-cache writes.
- **At most 300 newly reconstructed crops.** Existing crops are reused by copy after a sha256 check.
- Reuse, by import, the SS1 functions in `B/small_segments/tools/` (rotation `L,S,A`, output type, chars) and the recorded
  reconstruction route of SEG-CELLS-1b: `B/cells/materialise_1b.py` + `B/cells/HANDOFF.md` §1b — page cache
  `~/Projects/collect-v3-data/run/cache/pages/<sha>.jpg`, W1/W2 feature snapshots for the boxes, and
  `greekocr.harvest.line_pipeline_native.reconstructed_crop` + `digest_bytes`, with `digest_bytes(png) == crop_sha256` checked
  before writing. A row that cannot be reconstructed byte-exact is replaced by the next seeded row of the same stratum; log every
  replacement and its reason.

## Population
Census `B/cells/population_cells.jsonl.gz`. **Small** = `chars ≤ 8 and A ≤ 6` (`D_rec`) (on rotated dims, as in SS1). Q3 covers small rows whose
output type is `nonnumeric` or `mixed` (SS1 definitions). Report the pool size per stratum.

## Strata (seed 20261019; `random.Random(seed + stratum_index)`; order rows by row_id before sampling)
1. **opus** — every crop typed in `B/cells_opus/samples.jsonl` (sets `typology_uniform` and the owner supplement; 179 rows if the
   file says so; report the actual count and the sets). Copy their PNGs from `B/cells_opus/crops/` (or the paths recorded there)
   after the sha256 check against the census `crop_sha256`. Keep the Opus `type` and `note` in the KEY only (see below).
   Record whether each row is inside or outside the definition above.
2. **inside_by_source** — 150 new rows inside the definition, nonnumeric only, not in stratum 1: allocate per `source`
   proportionally to the pool, with a floor of 4 for every source with ≥ 20 pool rows (cap at the pool size), rounding by the
   largest remainder so the total is exactly 150.
3. **mixed** — 30 new mixed rows inside the definition (proportional by source, no floor).
4. **rotated** — 25 new nonnumeric rows inside the definition with `height_px > width_px`.
5. **border_outside** — 45 new nonnumeric rows just outside the definition: nonnumeric rows with (`9 ≤ chars ≤ 12` and `A ≤ 8`) or (`chars ≤ 8` and `6 < A ≤ 12`), 25 from the first group and 20 from the second.
6. **owner** — every owner-judged line (`B/small_segments/q1/owner_joined.jsonl`) that is nonnumeric/mixed and inside the
   definition and not already drawn; take existing crops where one exists locally (search `B/crops/`, `B/cells/samples/`,
   `B/cells_opus/crops/`, `~/Projects/ocr-review-sites-20261018/population-images/`), otherwise reconstruct; report the count.

## Outputs
- `crops/<line_id>.png` for every sampled row (reconstructed or copied; sha256-verified).
- `q3/sample.jsonl`: one row per crop: line_id, stratum, crop_path (absolute), crop_sha256, verified (bool), how (copied /
  reconstructed + page sha), raw_text, chars, output type, width_px, height_px, rotated, L, S, A, xheight_px, source, book (row_id prefix before `--s`; for ids without `--s`, the prefix before `-p<digits>-l<digits>`),
  wave, primary_class, script_class, verdict_05, reason_05 category (SS1 mapping), inside (bool).
- `q3/key_opus.jsonl`: line_id → Opus type and note (stratum 1 only). This file is a KEY: it must never be copied into any reader
  folder later.
- `q3/control_candidates.jsonl` + contact sheets `q3/control_sheets/cc_NN.png`: 30 candidate controls drawn from stratum 1 only,
  5 each from the Opus types `word_or_phrase`, `heading_caps_display`, `punctuation_only`, `noise_non_text`,
  `abbreviation_reference_label`, `multi_line_crop` (fewer if the type has fewer; then fill from `cut_fragment`,
  `text_covers_part_of_crop`). Contact sheet: 6 crops per sheet, each crop scaled to fit 900×220 px without upscaling beyond 4×,
  aspect kept, a 1 px red frame at the crop edge, and under each crop: index, line_id, Google text, Opus type. The lead
  pixel-verifies these before any reading.
- `q3/SS3_RECEIPT.json`: inputs with sha256, per-stratum pool sizes and drawn counts, replacements with reasons, counts copied vs
  reconstructed (reconstructed must be ≤ 300), unique pages used with their sha256 checks, script sha256, test result.

## Tests (`tests/test_ss3_sample.py`)
Largest-remainder allocation with the floor and caps on a toy pool (sums exactly to the target); seeded draw reproducible;
replacement keeps the stratum; a sha mismatch is refused (never written); the key file is never referenced by the sample file
writer.

## Report
Final message: pool sizes, drawn counts per stratum, replacements, reconstructed count, verified count (must equal the total).
Last line exactly: `SS3 READY: q3/sample.jsonl (<n> crops, <k> reconstructed), control sheets q3/control_sheets/, receipt
q3/SS3_RECEIPT.json` (or `SS3 FAILED: <reason>`).
