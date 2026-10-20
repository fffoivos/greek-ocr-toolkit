# Large tracked files to move out of git: receipt (19 Oct 2026)

These five tracked files are data, not source. The repo clean-up may move them out of git by this receipt.
- Keep each file outside the repo with its exact bytes, and verify the bytes and sha256 below before removing it from git.
- The files are not removed by this commit.

**Do not lose them.** The readers below expect them at these paths. After the move, those readers need a documented location
for the file (an env var or a data-root path) or a retrieval step that checks the sha256.

## The files

| # | Branch | Path | Bytes | sha256 |
|---|---|---|---:|---|
| 1 | opus/secondary-corrections | `artifacts/n1/n1_v1_train.jsonl` | 215,263,750 | `0b32e8d9b04383cc8fe5542b0b40ccfa47978c5cd09b36c1a535083f0b41bf92` |
| 2 | opus/secondary-corrections | `docs/records/labelfix/lqb/truth_v1_1.jsonl` | 86,937,484 | `b54e238ccfd89df91cabf5255ad8c9b8b26701304fb0bf552f12e4baf435fa5b` |
| 3 | opus/seg-census, sol/recut-v1 | `docs/records/harvest/collect_v3_admission/segeval1/keys/candidate_order_KEEP.jsonl` | 476,509,196 | `08b1b5a054bd5161534ac637c81b4155be6d4d6c843ab41421f584b0c285dd07` |
| 4 | opus/seg-census, sol/recut-v1 | `docs/records/harvest/collect_v3_admission/segeval1/SEGEVAL1.bundle` | 147,025,055 | `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a` |
| 5 | opus/seg-census | `docs/records/harvest/collect_v3_admission/segeval1/cells/population_cells.jsonl.gz` | 88,576,911 | `65dd922629c9e81d05c3cf419f5a623837d55a1820e89811bbd8b74511956dfc` |

Files 1 and 2 already have `.sha256` sidecars in git (`artifacts/n1/n1_v1_train.sha256`, `docs/records/labelfix/lqb/truth_v1_1.sha256`).
Keep those sidecars in git.

## What each file is, and who reads it

### 1. `n1_v1_train.jsonl`

**What it is:** the full-train N1 label file. It is superseded by the edits-only rule: a label version holds only the corrected
rows.

**Code that reads it:**
- `scripts/numerics/n1_apply_train.py`
- `scripts/numerics/n1g.py`
- `scripts/numerics/n1r_receipt.py`
- `artifacts/n1/n1g/predecessor/n1_apply_train.py`

**Docs that cite it:**
- `docs/records/briefs/N1G_gate.md`, `N1R_rule_fit.md`, `N1T2_train_read.md` and `N1TRF2.md`
- `docs/records/labelfix/secondary/HANDOFF_20261018.md`, `N1R_REPORT.md` and `N1TR_REPORT.md`

**Retrieval:** needed only to re-run the N1 train application.

### 2. `truth_v1_1.jsonl`

**What it is:** the frozen Label Quality Benchmark truth v1.1. Every label fix is scored against it.

**Code that reads it:**
- `scripts/lqb/build_v2_1.py` and `build_v2_2.py`
- `scripts/numerics/n1g.py`, `n1tr.py`, `n1tr_f2.py`, `n1w1_f2.py` and `n1w1_f3.py`
- `scripts/secondary/ru2t_apply_lead.py` and `ru2t_delivery.py`

**Docs that cite it:** `docs/records/briefs/LQB4_sx1v2_truth11.md` and `artifacts/ru1/ru2t/finalize_RU2TF3.log`.

**Retrieval: must stay retrievable.** It is the benchmark of record.

### 3. `candidate_order_KEEP.jsonl`

**What it is:** the segeval1 sampling key (candidate order).

**Who reads it:** no code reads it by name. It is listed in `segeval1/package_receipt.json`, and as an untouched protected file
in the scope guards: `seg_steps/s1–s4/initial_hashes.json`, `gate_rereport/initial_scope.json` and
`line_pipeline/gate03/part3-initial-hashes.json`.

**Retrieval:** moving it out makes those historical guard rechecks report the file as missing. That is expected; record it with
the move.

### 4. `SEGEVAL1.bundle`

**What it is:** a git transport bundle. Its head `b3b5aaa19835ac626af6576da37e008386b26879` (`refs/heads/segeval1-artifacts`) is
NOT in this repo's history.

**Retrieval: keep the file itself.** It is the only copy of that ref here.

**Who reads it:**
- `segeval1/tools/package.py`, `segeval2_package.py` and `write_handoff.py`
- `segeval1/HANDOFF.md`, `package_receipt.json` and `segeval2_package_receipt.json`
- the same scope guards as file 3

### 5. `population_cells.jsonl.gz`

**What it is:** all 592,466 census_02 rows, as Sol's SEG-CELLS-1 export: raw Google text, crop sha and size, verdicts and
dispositions.

**Code that reads it:** in `segeval1/cells/`:
- `classify_population.py`, `distributions.py`, `fetch_samples.py`
- `materialise_1b.py`, `prepare_reconstruction.py`, `reduce_population.py`
- `validate.py`, `validate_1b.py`, `write_handoff.py`

**Other readers:**
- `docs/records/briefs/SEG_GATE_rereport.md`, for the gate re-report's "unexpected scripts by book" table;
- the Small segment analysis keys v2/v3 (outside this repo).

**Retrieval:** needed to reproduce the cells analysis and the gate re-report.

## Not part of this receipt

- `docs/records/harvest/seg09/` is untracked: stray output of the abandoned SEG09_CP1 run. Leave it out of git.
- `segeval1/keys/census02_segmentation_evidence.jsonl` (1.7 MB) is committed (3889741f3) and stays in git.
