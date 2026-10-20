# BENCH02F: apply the coordinator's rulings to the bench02 draw tool (gpt-6.1-sol, medium, network OFF, no spend)

The base is the BENCH02E commit (`docs/harvest/collect_v3_admission/bench02/`). Apply exactly these rulings (coordinator, 20 Oct, under the owner's night mandate). Change nothing else, keep the class precedence unchanged, and add no filters.

## Rulings
1. **Sizes:** the class table stands at **2,460 test / 615 dev**. 20% overdraw gives up to 3,690 checks (the P6 budget is 3,700). Remove the size discrepancy from the open questions; record the ruling.
2. **Absent evidence stays absent.** A class whose tag evidence census_05 does not carry is reported as a **deficit**, never substituted. This covers letter-spacing, ru/sr/bg/uk language where document metadata lacks it, and book-series identity. Census_05 **does** carry:
   - the **cell flag + aspect A** from gate 0.3, and the gate's **script inventory**;
   - **Serbian document ids** from CENSUS3: find the CENSUS3 Serbian document list (`sol/census-v2-serbian`, read-only via `git show sol/census-v2-serbian:<path>`, or the CENSUS3 docs) and use it as the `sr` language evidence for those documents only;
   - **edition identity** from `split2/edition_map.jsonl`.

   Map the gate 0.3 field names from the census_05 code in `~/Projects/greek-ocr-toolkit-main-next` (read-only: the gate/numeric_cells/line_pipeline modules and their tests). Name the exact decision/diagnostic paths in the adapter and in the availability table. If the code does not emit a field under any name, say so; do not guess.
3. **Thresholds:**
   - **degraded** = DocAI mean line confidence **< 0.89** OR ink density **below the 25th percentile of its source**. Both come from census evidence: the percentile is computed over the census_05 W1/W2 rows of that source, recorded in the draw plan. Find the ink-density field in the census_05 code. If none exists, the density branch is unavailable and only the confidence branch applies; report it.
   - **punctuation-heavy** = non-letter, non-digit, non-space characters **≥ 1/3 of non-space characters**, OR a leader/dash tag from N1 (`leader_runs` non-empty or `emdash_label_count > 0`, or the census_05 N1 tag field if named differently).
   - The slim export must carry these as numbers/flags: punctuation share, confidence, ink density.
4. **Dev fonts:** 13 small / 12 large (test stays 50/50; overdraw per subgroup as now).
5. **The extract job targets census_05.** One sbatch, with the census input directory as a single variable. Document two submit command blocks in `BENCH02D.md` and `run_dryrun_census03.md`:
   - **(a) the mechanics dry run on census_03**, the same sbatch with the input path set to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current`, output under a census_03 directory;
   - **(b) the real run on census_05**, path variable left for the coordinator.

   The census_03 run uses the dry-run pool rule (sole split reason). The census_05 run uses admitted rows only.

## Tests
- The existing tests pass.
- New tests:
  - degraded fires on confidence 0.88 and not on 0.89, and on the density p25 boundary per source;
  - punctuation-heavy at exactly 1/3 and just below, plus the leader/dash path;
  - dev fonts 13/12;
  - the Serbian id list gives `sr` only for listed documents;
  - the cell flag/A adapter on fixture rows with the census_05 field names;
  - a deficit is reported, never substituted, when evidence is absent.

Write a guarded commit list. The last line must be exactly:
`BENCH02F: done | rulings 1-5 applied | gate0.3 fields <names> | ink density field <name|absent> | serbian docs <n> | submit blocks census_03 + census_05 | tests: <n> passed`

## Also (lead)
- **Extract time limit:** BENCH02E set `--time=00:15:00` from a Mac rate of 6,359 rows/s. Clariden Lustre I/O for about 16 GB of streamed input is unmeasured, so set `--time=01:00:00` for extract and readout. The job stays one node on `normal`.
