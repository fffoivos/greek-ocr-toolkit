# SEAL02: the benchmark 0.2 seal package (P7), built on Clariden, with VERIFY (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**Goal:** a deployable package that, once the inputs below exist, builds **one sealed `suite.json` v0.2** on Clariden, and that the 0.1 scorer can score. The coordinator submits; you submit nothing.

**Spec:** programme §3.4 (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md`):
- references = the corrected labels of the unflagged lines;
- images (sha256), tags, draw plan, Sol check receipts;
- one `suite.json` version.

The fair-comparison contract of benchmark 0.1 stays as it is: same IDs, literal references, exact pixels, strict NFD CER plus the other measures, failed reads scored as empty, and `diagnostic_only` when exposure is unknown (§3.5). See `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/benchmark_v01/README.md`.

## Inputs (bind each by sha256; the build fails closed if any is missing or differs)
1. **The final list (LF1-checked).** It does not exist yet. The spell-check lead produces it from candidates v3, under the coordinator's ruling:
   - rank ≤ quota per split/class[/subgroup] is in quota;
   - a flagged line is replaced from the reserve, in rank order, within the same split, class and source.

   Its producer is `~/Projects/greek-ocr-toolkit-spellcheck/artifacts/lf1/tools/prod_finalize.py`, currently a stop stub; read `LF2_PROD_PREP.md` and `PROD_PLAN.md` there, read-only.
   - **Define the minimal interface this package consumes**, as `seal02/FINAL_LIST.schema.json`. One row per sealed line: `parent_id`, `row_id`, `split`, `quota_scope`, `lf1_verdict` (must be `OK`), `replaces` (key or null), and the LF1 receipt reference.
   - Also accept the final-list receipt: file sha, LF1 `verdicts.jsonl` sha, flagged/REPLACED/UNFILLED counts.
   - Write it so prod_finalize can emit it directly. Name it in the report so the coordinator can hand it to the spell-check lead.
   - Provide a **mock final list** built from candidates v3's in-quota rows (`lf1_verdict` `OK`, flagged as MOCK) for tests and the VERIFY dry path only.
2. **Candidates v3:** sol-recut `docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl` (sha `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`), plus `draw_plan.json` (sha `8007e93f…`) and `counts.json`. These supply the tags, classes, quota scopes and draw plan.
3. **References:** `bench02/census05_readout/candidates_readout.jsonl` (sha `929e231ce84ace1faa25ffed6b82010c75bc6b105828c3f311e3e5b75c150973`), with fields final_text, edits and raw_text_sha256. The reference is `final_text` exactly, the pipeline's corrected label. Sol's LF1 readings are evidence and never a reference.
4. **Images:** CROPS4 outputs on Clariden, `$W/collection_w2_originals/<source>/<row_id>.png` and `$W/collection_w1_originals/...` (W2 job 3704831; W1 job 3704856, chained). Bind each image by the row's `crop_sha256`, re-hashed at build time. Also bind the CROPS4 `upload_receipt.json` of each run (status ok, 0 mismatches). A sealed row whose image hash differs, or is missing, fails the build. Copy the images into the suite directory by sha, as 0.1 does if it fits.
5. **Census provenance:** census_05 attempt `$W/census_05_20261020/attempts/full-split-001` (CURRENT.json, summary sha `096b18a8…`), and the tags receipt `bench02/census05/tags.jsonl.receipt.json`.

## Reuse benchmark 0.1
The deployed 0.1 code is at `$W/benchmark_20261019/code/f4a70c1489d47af9/`:
- `bench/benchmark_suite.py`, `benchmark_build.py` and `score.py`, `scripts/clariden/benchmark_candidates.sbatch`, and `SHA256SUMS`.

Its local origin is greek-page-ocr (`bench/`, `docs/ocr_program_2026-10-06/benchmark_v01/`). `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.
1. Read the 0.1 suite format and the scorer's input contract.
2. **If the 0.2 suite can be expressed in that format**, a panel `benchmark_v02_test` / `benchmark_v02_dev` with per-row class/facets, reuse the 0.1 code unchanged, by sha, and write only the minimal adapter that emits its input.
3. If not, write the minimal adapter and state exactly which 0.1 field or assumption does not fit.
4. Do not modify 0.1 code. Do not re-score anything.

## Package (sol-recut `docs/harvest/collect_v3_admission/seal02/`)
- `build_suite02.py`: join, verify and emit.
  - `suite.json` v0.2: version, input shas, per-row id, split, class/scope, tags, reference, image path and sha, LF1 receipt ref;
  - per-class counts against quota; deficits carried as reported (no padding);
  - `SEAL_RECEIPT.json`.
- `seal02.sbatch`:
  - normal partition, 1 node, the CPU count and time sized from measured local timing (state the arithmetic);
  - `$W/venv_l1/bin/python`;
  - output to a new `$W/benchmark_0.2/<attempt>/`;
  - `--output` absolute.
- `VERIFY.sh`, with two modes:
  - **package:** DEPLOY_SHA256SUMS, interpreter, imports;
  - **inputs:** every bound sha and every image that exists, light enough for the login node. Measure it: 3,341 PNG hashes is fine. Reading a census file is not.
- `submit_seal.sh`: absolute paths, no defaults that point at the mock.
- Tests:
  - full mock build end to end, with local temp images;
  - a reference must equal readout `final_text` byte for byte;
  - a missing or mismatched image fails;
  - a non-OK verdict fails;
  - a replacement must match split, class and source;
  - deterministic suite bytes;
  - 0.1 scorer accepts the suite (if reused).
- `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`.

Deploy to the new `$W/benchmark_0.2/pkg/<sha8>/` with every sha read back. Run VERIFY package mode there. Run inputs mode against what exists now: candidates, readout and census, plus the W2/W1 crops if their jobs are done; otherwise report "pending". Run nothing else remotely.

## Report
Write `seal02/SEAL02.md`:
- the 0.1 fit decision (in one paragraph);
- the schema for the spell-check lead;
- the exact coordinator command block: VERIFY, submit, and what to check in the receipt;
- what remains pending (the LF1 final list, the crops);
- the sbatch sizing.

Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`SEAL02: done | 0.1 format <reused|adapter> | package <root> VERIFY package ok | inputs bound <k>/<n> (pending <list>) | tests <n> passed | no jobs submitted`
