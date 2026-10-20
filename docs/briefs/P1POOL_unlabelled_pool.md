# P1POOL: the P1 unlabelled train-only crop pool from census_06 (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**The coordinator's ruling** on DATA_NEEDS Q2 (`docs/harvest/collect_v3_admission/scaling_w3/DATA_NEEDS.md` §P1), under the end-to-end mandate, with the spec in TRAINING_DIRECTIONS (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/TRAINING_DIRECTIONS_20261016.md:50`):

**P1 pool** = every crop that passed **content gate 0.3 and segmentation 0.13** in **census_06** whose disposition is **ADMIT**, or **HOLD on correction grounds only** (every hold reason is `correction_unresolved` / `required_evidence_unresolved`; no gate, segmentation, eligibility or other reason). It:
- **excludes** DROP;
- **excludes** every SPLIT2 dev/test edition, every benchmark edition, key and crop sha (seal04 test/dev + REL3 candidates_v3/readout), and every held-out book/edition;
- is **train-only**: W1/W2 train split and collection-v2-train only;
- is **edition-deduplicated**;
- carries **no labels**;
- uses the same exposure audit as REL4.

The coordinator submits; you submit nothing. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Bases (read-only)
- **REL4/REL4b** (`docs/harvest/collect_v3_admission/release_v4/`, deployed `release_v4/pkg/60fa450c`): reuse its census_06 binding contract, its exclusions/exposure code (SPLIT2 edition join, the seal04 + candidates key/crop-sha union, pixel-duplicate drop) and its crop custody/union lookup, by import or a byte copy with sha.
- **census_06** (CENSUS06-A/B, `docs/harvest/census06/`): the decision schema (disposition, `reasons`, `routes`, gate/segmentation fields). The real attempt is `$W/census_06_20261020/attempts/full-split-002`, **pending**.
  - Develop and test on real census_05 rows: head samples of `$W/census_05_20261020/attempts/full-split-001` admission_records/decisions, read with `head` only, plus synthetic 0.3.3 kept_unverified/HOLD cases.
- **Crops:**
  - ADMIT rows are covered by CROPS4 c05/c06 (`collection_w{1,2}_originals`) and `$W/collection_v2/crops/` (v_c).
  - **HOLD rows were never materialised for W1/W2.** P1POOL needs a crop step for them: the same reconstruction as CROPS4 (`line_pipeline_native.reconstructed_crop`, sha `e7dbe6c4…`, imported from the bound census code with the CROPS4C `binding_checks.sh` checks).
  - It writes **only absent files**, exclusively, into a **new** tree `$W/p1pool_crops/<attempt>/`, never into the originals trees. Existing crops are referenced by path + sha, not copied.
  - Reuse CROPS4's materialiser via an explicit selection-manifest input if that is a small, tested change. Otherwise write a minimal one that imports the same functions; state which.

## Rules to define, as lead choices recorded in P1POOL.md (keep them simple; add nothing beyond these)
1. **Correction-grounds HOLD:** the exact reason set, from the census reason vocabulary (census06 readout `all_disposition_reasons`). List every HOLD reason with its census_05 count and say in or out.
2. **Edition deduplication:**
   - (a) exact crop pixel sha: keep one row per sha;
   - (b) for SPLIT2 editions with more than one member document, keep the rows of one member document per edition, chosen deterministically: most pool rows, then the lowest document id.
   Report both counts. If TRAINING_DIRECTIONS or the data plan (`DATA_PLAN_v2_20261016.md`) defines it differently, follow that and cite it.
3. **The 1,557 label-in-holdout flags** (TRAINING_DIRECTIONS:50, DATA_PLAN_v2):
   - locate the flag list;
   - if its keys join census_06 rows, exclude them and count;
   - if it applies only to the historical 84,799 initial rejects (a different population), state that, with evidence, and exclude nothing invented.
4. **No labels:** the manifest carries row identity, parent, source, edition, split=train, crop path + sha, disposition + reason class, and NO text, label, raw_text or final_text.
   - Assert that no label field appears.
   - Keep raw_text_sha256 only if it is needed for dedup audit; say if it is used.

## Package (`docs/harvest/collect_v3_admission/scaling_w3/p1pool/`)
- `build_p1pool.py` (selection + exclusions + dedup + audit) and the crop step for HOLD rows.
- Two sbatch files (select, then crops with afterok), `--account=a0140`, normal partition, sized time.
- `VERIFY.sh` (package; light inputs reporting census_06 PENDING), `submit_p1pool.sh`.
- `P1POOL_RECEIPT.json` contents:
  - input shas;
  - counts per parent/source/class/disposition-reason;
  - exclusion counts per rule;
  - dedup counts;
  - crops existing vs written;
  - output shas.
- **Real-head tests:** on real census_05 head rows (≥ 200 across all five parents), plus synthetic cases:
  - each exclusion;
  - correction-HOLD in and gate-HOLD out;
  - DROP out;
  - a dev/test edition out;
  - a benchmark key and a benchmark crop sha out;
  - a pixel dup;
  - multi-member edition dedup;
  - no label fields;
  - HOLD crop reconstruction byte-equal to a census_05 crop_sha256 on ≥ 20 real rows.
  - The last one needs Clariden pages: run it read-only on the login node (≤ 20 crops, written to a temp dir under your own new scratch dir, then removed), or say it needs a job.
- Delete your own pytest basetemp after a passing run, keeping only tests.log/tests.xml.
- Deploy to the **new** `$W/scaling_w3/p1pool_pkg/<sha8>/` and read every sha back.
- `P1POOL.md`: the rules as implemented, the census_05 projection of the yield (from the readout's counts, labelled as a projection), sizing, and **the exact coordinator block** (after census_06 full + readout).

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `p1pool/` and this brief; other runs work in `census06/`, `c2/` and `g_audit/`.

The last line must be exactly:
`P1POOL: done | package <root> VERIFY package ok | inputs <k>/<n> (pending census_06) | rules: hold-reasons <list>, dedup sha+edition-member, flags <applied n|n/a> | no labels asserted | real-head tests <n> + crop byte-equal <k>/<k> | tests <n> passed | basetemp deleted | no jobs submitted`
