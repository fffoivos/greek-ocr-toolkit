# BENCH02E: bench02 fixes — slim export, Clariden interpreter and partition, candidate readout (gpt-6.1-sol, medium, network OFF, no spend)

The base is commit 9834244c7 (BENCH02D, `docs/harvest/collect_v3_admission/bench02/`). Fix only the items below. Keep every draw rule and the class precedence unchanged. Add no filters.

## Fixes
1. **The interpreter on Clariden.** `extract.sbatch` calls `python3`, which is Python 3.6 on Clariden; it fails on modern syntax.
   - Use the census environment: `python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/venv_l1/bin/python`, as census_03.sbatch does.
   - Assert `sys.version_info >= (3, 10)` at startup.
   - Run the tool's tests under a 3.10+ interpreter locally and record which one.
2. **Partition, per the coordinator:** `normal`, 1 node, a short time.
   - Measure the extract rate on the local sample (rows/s, both inputs streamed) and project it to 593k decisions + 593k diagnostics (≈ 9 + 7 GB).
   - Set `--time` to 3× that projection, rounded up to 15 min, ≤ 02:00.
   - Remove the xfer partition guard; the job must run under `normal`. Do not pass `--mem` (normal nodes are exclusive).
   - Write all output under an explicit `--output-dir` argument (absolute path on scratch), never relative to the submit directory.
   - Write the log to `$OUT/extract-%j.log` via a wrapper. If `#SBATCH --output` cannot take a variable, require `sbatch --output` on the command line and document it.
3. **Slim export (`tags.jsonl.gz` → the Mac):** tens of MB for all W1/W2 rows.
   - Keep: parent_id, row_id, crop_sha256, admitted, disposition, reasons (codes only), the split if present, and the **facets/evidence the classifier reads** (the exact fields listed in the BENCH02D availability table).
   - Drop: `final_text`, the full `final_inventory`, the duplicated `expectations` provenance strings, and any field the draw does not read.
   - Text-derived facets (character count, letter count, punctuation share, case inventory for the caps branch, script letter counts) stay as **numbers/flags**, never as text.
   - Measure bytes per row on the sample and project them to 320,479 rows. The target is ≤ 40 MB compressed. Report the projection.
4. **Candidate readout (new `readout` subcommand, runs on Clariden):**
   - Input: `candidates.jsonl` (ids only, from `draw`) and the census directory.
   - Output: `candidates_readout.jsonl`: final_text, raw text sha, crop_sha256, crop_source_image, crop_bbox, edits for exactly the candidate rows.
   - Same interpreter and partition rules as extract, with its own sbatch (`readout.sbatch`).
   - P6 needs text and crops for ≈ 3,700 lines only. The crop files themselves come from CROPS4 (`--include-heldout`), not from this tool.
5. **`draw` must not need `final_text`.** Long and short use the character and letter counts from the slim facets. Candidates carry ids, class, tags, rank and edition only.
6. **The census_03 dry run, prepared.** Write `run_dryrun_census03.md` with the exact commands for the coordinator to submit `extract.sbatch` against `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current/`, then `draw --dry-run` on the Mac. The 4,000-row census_02 sample was all bsb_poly1850, so it cannot show real class supply. This full dry run is the real test. Do not submit it.
7. **Docs:** update BENCH02D.md with the commands and a "BENCH02E changes" section. Keep the open questions list, unchanged in substance.

## Tests
- The existing 20 still pass.
- New tests:
  - the slim export drops text: no `final_text` key, and no string field longer than 64 characters apart from ids/shas;
  - draw gives identical candidates from slim vs full tags on the sample;
  - readout selects exactly the candidate ids;
  - the sbatch scripts use the venv_l1 path, partition normal, no `--mem`, and absolute outputs. Mock-run them with `srun`/`sbatch` stubbed.

Write a guarded commit list (bench02/ + this brief). The last line must be exactly:
`BENCH02E: done | slim export <bytes/row> B/row, projected <MB> MB for 320,479 rows | extract time limit <hh:mm> (rate <r> rows/s) | readout subcommand ok | interpreter <ver> | tests: <n> passed`
