# Census_03 full dry run — prepared, not submitted

The census_02 sample has 4,000 bsb_poly1850 rows only. Its zero eligible test/dev candidates cannot establish real class supply. This full census_03 `--dry-run` tests mechanics and diagnostic supply; it still uses only the sole split-identity reason and does not qualify or seal a benchmark.

(a) Mechanics dry run on census_03. On Clariden, from the deployed repository root (the same bench02 files must be deployed), run:

```bash
B="$(pwd)/docs/harvest/collect_v3_admission/bench02"
CENSUS=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current
OUT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census03
bash "$B/submit_job.sh" extract "$CENSUS" "$OUT"
```

This wrapper creates `$OUT` and invokes `sbatch --export=ALL --output="$OUT/extract-%j.log" "$B/extract.sbatch" --census-dir "$CENSUS" --output-dir "$OUT"`. It exports the absolute `BENCH02_DIR` because Slurm executes a spooled copy of the batch script. The job requests account a0140, partition normal, one node, one task/CPU and **01:00:00** for both extract and readout; no `--mem`. Both batch jobs use the census `venv_l1/bin/python`, with Python >=3.10 asserted at tool startup. Do not bypass the wrapper without setting `BENCH02_DIR` and supplying **absolute `sbatch --output`** explicitly: `#SBATCH` does not expand `$OUT`.

After the coordinator verifies completion and both join rates in `tags.jsonl.receipt.json`, copy **only** `$OUT/tags.jsonl.gz` and `$OUT/tags.jsonl.receipt.json` to `docs/harvest/collect_v3_admission/bench02/census03/` on the Mac. Transfer is a coordinator action, not executed here. Then from this checkout root on the Mac:

```bash
B="$(pwd)/docs/harvest/collect_v3_admission/bench02"
A="$(dirname "$B")"
P="${PROJECTS_ROOT:-$HOME/Projects}"
python3 -V  # must be >=3.10; locally verified: Python 3.11.3
python3 -B "$B/bench02_draw.py" draw \
 --tags "$B/census03/tags.jsonl.gz" \
 --split "$A/split2/row_split.jsonl.gz" \
 --editions "$A/split1/editions.jsonl" "$A/split2/edition_map.jsonl" \
 --features "$P/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl" "$P/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl" \
 --v2 "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl" "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl" "$P/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl" \
 --exclusions "$P/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/release_exclusions.json" \
 --dry-run --output "$B/census03/dryrun"
```

Review `COUNTS.md`, `counts.json` and `draw_plan.json`: class supply and deficits, evidence availability, split/exclusion effects, language/font subgroups, caps and unknown series. If census_03 schemas differ, report unavailable evidence; do not invent mappings, add filters or change precedence.

For P6, the coordinator copies `candidates.jsonl` back to an absolute scratch path and runs readout on Clariden:

```bash
# In the same deployed repository, with B, CENSUS and OUT as above:
CANDIDATES="$OUT/candidates.jsonl"
bash "$B/submit_job.sh" readout "$CENSUS" "$OUT/readout" "$CANDIDATES"
```

Output: `$OUT/readout/candidates_readout.jsonl`; log: `$OUT/readout/readout-%j.log`. This selects exactly the candidate `(parent_id,row_id)` keys and fails on missing/duplicate records or mismatched crop bindings. Decisions supply final_text, raw_text_sha256, crop_sha256 and edits; diagnostics supply crop_source_image and crop_bbox. No crops are opened or generated. P6 needs approximately 3,700 lines; crop files come separately from **CROPS4 `--include-heldout`**. The class quotas are 2,460 test / 615 dev; nominal overdraw is 3,690. Dev fonts are 13 small / 12 large; per-subgroup ceiling gives 16/15 dev candidates and 3,691 total targets, within the 3,700 P6 budget.


(b) Real run on census_05, using the **same** `extract.sbatch` and a single census input directory. The coordinator supplies the completed, receipt-pinned input path:

```bash
: "${CENSUS05:?set to the completed census_05 directory}"
B="$(pwd)/docs/harvest/collect_v3_admission/bench02"
OUT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census05
bash "$B/submit_job.sh" extract "$CENSUS05" "$OUT"
```

After receipt verification, transfer only the slim tags and receipt into Mac `bench02/census05/`, then run `bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh`. That real run passes no `--dry-run`: **admitted rows only**. The census_03 dry run uses the sole split reason; neither invocation adds filters. Readout uses the matching census directory. Extract and readout each request one hour on one `normal` node: Mac throughput does not measure roughly 16 GB of Clariden Lustre I/O. No command here was submitted.
