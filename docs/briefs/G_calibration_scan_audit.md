# G-AUDIT: read-only calibration-scan audit: legacy renderer inputs vs the benchmark's sources and fonts (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` only; report only, no package, no jobs)

**The coordinator's ruling** on DATA_NEEDS Q4–Q6 (`docs/harvest/collect_v3_admission/scaling_w3/DATA_NEEDS.md` §G):
- do **only** the calibration-scan audit now, as a read-only report: what the legacy renderer inputs cover versus the benchmark's sources and fonts;
- the ablation shards (A8) and the twins (A9) wait for the S1 results;
- build nothing for them.

## Audit
1. **Legacy renderer inputs (DATA_NEEDS A6, R3):**
   - recipes, font list (files + shas + family/style/weight), text-source manifests, appearance band;
   - find them through DATA_NEEDS' references and the synthetic custody chain: MIX1's A12 = `$P/e4/wave1b/v2-codec/old_v2/synthetic` ← `$P/e1_run4/synthetic` (`P=$W/greek-page-ocr/out`), its `build_info.json` recipe shas `2f228950…`/`76cef226…`;
   - also the linefactory/synthetic-provenance rule in `~/Projects/greek-page-ocr`.
   - Read only, with small reads.
2. **The benchmark** (seal04: `$W/benchmark_0.2/seal04/benchmark_v02_{test,dev}.jsonl`, suite `9447f09c…`):
   - its sources/editions, classes and scripts, and the typographic features the G track targets (TRAINING_DIRECTIONS Track G and DATA_NEEDS §G):
     - orthography-specific capital marks;
     - bold/condensed/letter-spaced caps;
     - old-style numerals;
     - light-on-dark;
     - leader dots;
   - **as far as recorded metadata allows.** Do not run any reader or OCR over images.
3. **The coverage matrix:** for each benchmark source/class/script and each G feature, is it covered by the legacy renderer's fonts and recipes? Mark each **yes / partial / no / unknown**, with the evidence path.
   - Name the fonts that cover each feature.
   - List gaps (features or scripts without a qualified face), plus faces present in renderer inputs but never sampled by the recipes.
4. **Exposure:**
   - do any renderer text-source manifests contain benchmark reference text? Use MIX1's text-exposure method (exact NFC/whitespace match + any ≥ 30-char shared substring vs the 2,690 seal04 references; reuse MIX1's audit code);
   - report hits per text source.
   - Old exclusion manifests predate seal04 (DATA_NEEDS), so say whether they cover it.
5. **The real-statistics measurement strata (A7):** list what a later calibration-scan measurement would need (train-only crops per stratum, from release v3/v4 tags). Only list it; measure nothing.

## Output
`docs/harvest/collect_v3_admission/scaling_w3/g_audit/G_AUDIT.md` + `coverage_matrix.csv` + `exposure_hits.json` + `evidence/` (small witnesses with shas). The report:
- states what is unknown without inventing;
- gives every number with its source;
- ends with the open decisions Q4–Q6 that the S1 results must inform.

Touch nothing outside `g_audit/` and this brief. Run no Clariden jobs; reads on the login node only. Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`G-AUDIT: done | renderer inputs <fonts n, recipes n, text sources n> | coverage yes/partial/no/unknown <a>/<b>/<c>/<d> over <cells> | exposure hits <n> (<sources>) | gaps <k> | no jobs`
