# SEGCENSUS-1 (b1 + b2): capture the filter-pipeline source, build the census package with segmentation 0.8, mock-test, deploy and verify (gpt-6.1-sol, medium, network ON for read-only Clariden checks and the deploy copy only; no .git writes; no Slurm submission; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`, created from `sol/seg-cells` (22f0caf7). It
contains the 0.8 implementation 410f4566 as an ancestor. The lead commits; you cannot write `.git`.

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md` (the owner's standing rules are
  binding: a tool is exactly the owner's rules; never add a guard, test or threshold);
- `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`;
- the pipeline design `~/Projects/ocr-review-sites-20261018/docs/FILTER_PIPELINE_IMPLEMENTATION_20261018.md`;
- `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/` (untracked docs; read only).

**Clariden:** read-only checks (ssh `clariden`; `$W` as the pipeline docs define it). If ssh or authentication fails, STOP and
report: the certificate is owner-gated. Never submit, cancel or modify a job. Never write outside the new deploy directory in step 5.

## b1. Source capture: the owner filter pipeline 0.2 as of 18 Oct

1. **Copy into this worktree** from `~/Projects/greek-ocr-toolkit-sol-recut`, byte for byte:
   - the three modified tracked files `greekocr/harvest/geometry_observations.py`, `greekocr/harvest/row_inclusion.py` and
     `pyproject.toml`;
   - the untracked `greekocr/harvest/line_pipeline*.py` (`line_pipeline.py`, `_adapters`, `_census`, `_native`, `_parallel`);
   - `greekocr/harvest/filtering_assets/`;
   - `docs/harvest/line_pipeline/`.

   Do NOT modify the sol-recut worktree.
   - Where a file also exists on `opus/seg-census` (from the Sol segmentation branches), DO NOT overwrite it blindly. List every
     conflict with both shas and a unified diff summary, and keep the branch version for the segmentation stage's own files
     (0.8 must stay byte-identical to 410f4566). The lead rules on any other conflict.
2. **Byte-check** the captured set against the Clariden code snapshots `$W/filter_pipeline_20261018/code/<hash>/`. For each
   `<hash>`: list it, then compare per-file sha256. Report which snapshot hash matches the capture exactly, which files differ and
   how, and which snapshot census_03 (job 3695426) ran. Get that from its job script/receipt under `$W/filter_pipeline_20261018`.
3. Write `docs/records/harvest/seg_census/SOURCE_CAPTURE.md` and `source_capture.json`: file list, shas, the matching snapshot hash, and
   the census_03 snapshot.

## b1. Census package, one variable

4. **The package equals the census_03 pipeline** (the exact snapshot that ran job 3695426) with ONLY the segmentation stage
   replaced by 0.8:
   - policy sha256 `e5b635ff9a04cc66f454a68e01ce9773229672e655b3ee08296ee5c0d149ee15`;
   - segmentation digest `512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd`;
   - from 410f4566 / the sol/seg-gate2 line.

   Everything else is byte-identical to census_03:
   - the polytonic 0.7 (sf7), RU1 0.3 and N1 0.2 stages, the merge and admission logic, the inputs and the config;
   - record every stage's hash.

   Also:
   - **Defects.** State which of census_02's four integration defects census_03 fixed (from its receipts or docs), and confirm
     the fixes are in the package.
   - **Diagnostics only**, recorded per row in the evidence and NEVER read by any verdict: the 0.8 de-skewed box long side,
     height and ratio; the saved character count; `is_cell` / `is_small_image` / `is_numeric_output` from the SEG-CELLS-1 pure
     function (on this branch); and the frozen 0.5 verdict and reason for the diff. Add a test proving that removing or altering
     every diagnostic leaves every verdict unchanged.
   - **Job kinds.** Give each job kind (filter shard, correction shard, merge/admission, and anything else), with partition,
     time, nodes and CPUs per kind, taken from census_03's measured runtimes plus margin, with the evidence. The smoke run uses
     `E4_SMOKE=1` on a small slice of each kind; the full run uses `E4_SMOKE=0`. The output root is a NEW directory under
     `$W/filter_pipeline_20261018/census_04_seg08/`; never reuse or overwrite census_02/03.

## b2. Mock test, deploy, verify

5. **Local mock end to end** through the exact job scripts and entry points:
   - the 150 + 888 segeval lines (`segeval1` replay inputs) through the packaged segmentation stage. Every verdict must equal
     gate2's `replay_segeval1.jsonl` / `replay_calibration.jsonl` byte-for-byte;
   - a ~200-row slice through the whole pipeline (all stages), with a mock that exercises the sbatch working directory and the
     output-root paths.
6. **Deploy** the package to a NEW Clariden directory `$W/filter_pipeline_20261018/code/<new-hash>/`, a copy only. Find the toolkit's
   `scripts/ops/verify_deploy.py` (search the repo and worktrees; read its usage) and run it until it prints `VERIFY_OK`. Do a
   per-file sha comparison of remote vs local. Run `sbatch --test-only` for each job kind (smoke settings). That is a dry check, not
   a submission.
7. **Hand-off:** `docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md`, containing:
   - the source capture result;
   - the package composition table (stage | version | hash);
   - the defects-fixed confirmation;
   - the job-kind resource table;
   - the mock results;
   - `VERIFY_OK` and the sha table;
   - the exact smoke and full submit commands for the coordinator, NOT run.

   Also write a receipt. Tests must pass. Respect the owner rules: no new rule, guard or threshold anywhere.

**Last line:** `SEGCENSUS1 READY: capture matches snapshot <hash> (<n> files; diffs <n>); census_03 snapshot <hash>; package = census_03 + seg 0.8 only (stages <list>); defects fixed <4/4>; mock 150 <n>/150 888 <n>/888 exact, slice <ok>; deploy <hash> VERIFY_OK; test-only <ok per kind>; tests <n> passed`
