# REL3: the release v3 train export package (P8), built on Clariden, with VERIFY (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**Goal:** a deployable package that builds **release v3 train**. The coordinator submits; you submit nothing.

**Spec:**
- NIGHT_PLAN P8: "Release v3 train = admitted − benchmark editions; edits-only corrections registered; admission receipts; W2 original crops uploaded to Clariden with hash receipt".
- Programme §4 (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md`): release v3 = the admitted, filtered **W1/W2** rows, minus the benchmark editions. The arms *add* and *add_corr* consume it, and add_corr applies registered corrections (ru1_v3_edits, n1_v1_w1, sf7 if audited) by row id.

Coordinator wording for this package:
- admitted_train minus the SPLIT2 test/dev editions, minus the benchmark candidates;
- corrections edits-only and registered;
- admission receipts and sha.

Rule from earlier work: a label version holds **only corrected rows over the raw Google import** (edits-only).

## Facts (lead, read-only)
- **census_05:** `$W/census_05_20261020/attempts/full-split-001` (`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`).
  - CURRENT.json export `g1-6283e1bcdf124516b599f8028ad910be`, summary sha `096b18a8…`.
  - `admitted_train.jsonl` is 7.9 GB and covers all parents; `admission_records.jsonl` is 10.4 GB.
  - Code: `$W/census_05_20261020/code/997b7d2ab5a8775b/`, manifest sha `997b7d2a…`.
- **The census_05 tags (bench02):** 168,637 W1/W2 rows admitted as train; dev 3,364 and test 36,266 admitted.
- **SPLIT2:** sol-recut `docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz` (sha `7b27ab9b…8b82`) and `edition_map.jsonl`; 1,359 editions; test 148, dev 52.
- **Benchmark candidates:** `bench02/census05/candidates_v3.jsonl` (sha `0432c56f…34c2`, 3,341 rows); readout `bench02/census05_readout/candidates_readout.jsonl` (sha `929e231c…0973`).
- **Crops:**
  - W2: CROPS4 job 3704831 → `$W/collection_w2_originals/`;
  - W1: job 3704856 → `$W/collection_w1_originals/`. The 18 Oct tree has 28,798 files; the lead sampled 299 and all match census_05 crop_sha256.
  - Each run writes `$W/crops4_attempts/<attempt>/{upload_receipt.json,crops_manifest.jsonl,crops_sha256.txt}`; the attempt names are crops4_c05_full_01 and the W1 full attempt.

## First: inventory (read-only, small reads only)
On Clariden, read with `head`, never by parsing whole multi-GB files on the login node:
- one W1/W2 `admitted_train` row and one `admission_records` row;
- the summary.json output list.

Locally, read the census05 code (segcensus `docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline*.py`) to learn:
- how the admitted label is formed (raw Google text vs `final_text`/`edits`, and which correction tools/versions are applied in census_05, e.g. Cyrillic/numerics/content repair; the polytonic correction was out of scope for this census);
- what provenance each edit carries.

Locate, read-only, the registered external correction versions named in §4 (`ru1_v3_edits`, `n1_v1_w1`, sf7): their file, sha and row-id keying. Search the toolkit worktrees' docs and records.

Record all of this in `release_v3/INVENTORY.md`. **If the edit provenance is ambiguous, stop and report; do not invent a registry.**

## Package (sol-recut `docs/harvest/collect_v3_admission/release_v3/`)
`build_release_v3.py` streams the inputs, holding only compact keys in memory, and emits to a new `$W/release_v3/<attempt>/`:
- **`release_v3_admission.jsonl`** containing:
  - **which rows:** W1/W2 rows from census_05 `admitted_train`, after these exclusions, each reported as a count:
    1. any row whose edition (SPLIT2 edition_map) is a dev/test edition: assert 0, by construction;
    2. any row whose key is in the benchmark candidates: assert 0;
    3. any row whose `crop_sha256` equals a benchmark candidate's: an exact-pixel duplicate; report and drop;
    4. any row without a byte-exact crop in the CROPS4 manifests (W1 or W2): report and drop. The release must be fully image-backed.
  - **fields per row:** parent_id, row_id, source, edition_id, split=train, crop relative path + crop_sha256, the label exactly as admitted, raw_text_sha256, and the admission decision reference.
- **`release_v3_edits.jsonl`, edits-only:** only rows whose admitted label differs from the raw import, with the edit list and its tool/version provenance as census_05 records it.
- **`corrections_registry.json`:** each registered correction version, census-internal and external:
  - name, file, sha, keying, and how many release v3 rows it touches;
  - the external ones (ru1_v3_edits, n1_v1_w1, sf7) are **registered, not applied**, for add_corr.
- **`RELEASE_V3_RECEIPT.json`:** input shas (census CURRENT/summary/admitted_train/admission_records, SPLIT2, candidates, readout, CROPS4 receipts), counts per source/edition, the exclusion counts above, output shas and bytes.
- **Admission receipts:** reference the census_05 receipt chain by sha (CURRENT.json, summary.json, readout); do not copy the multi-GB files.

The rest of the package:
- `release_v3.sbatch`: normal partition, 1 node; time and memory sized from the measured local throughput on synthetic data plus the file sizes (state the arithmetic); `$W/venv_l1/bin/python`; absolute `--output`.
- `VERIFY.sh`: package mode, plus a light inputs mode (shas of small files, existence of the big ones and the CROPS4 receipts' status; no multi-GB hashing on the login node; the job hashes those).
- `submit_release_v3.sh`.
- Tests: a synthetic end-to-end run covering each exclusion, edits-only correctness (an unchanged row never appears in the edits), deterministic bytes, a missing crop dropped and counted, and a receipt sha mismatch failing.
- `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`.

Deploy to the new `$W/release_v3/pkg/<sha8>/` with every sha read back. Run VERIFY package mode there, and inputs mode against what exists now; report the CROPS4 W1/W2 receipts as pending if those jobs have not finished.

## Report
Write `release_v3/REL3.md`:
- the inventory findings: label formation, edit provenance, registered versions;
- the exclusion design;
- the exact coordinator command block;
- what is pending.

Write a guarded commit list. Do not run `git add` or `git commit`. Do not touch `seal02/` or `bench02/` (another run works there).

The last line must be exactly:
`REL3: done | package <root> VERIFY package ok | inputs <k>/<n> (pending <list>) | registry <m> versions (<names>) | tests <n> passed | no jobs submitted`
