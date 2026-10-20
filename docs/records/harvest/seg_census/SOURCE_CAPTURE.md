# SEGCENSUS-1 source capture

Status: **three conflicts resolved per SEGCENSUS-1c lead ruling.** All 150 requested sol-recut files are archived byte-for-byte under `source_capture/`; the three conflicts were copied from sol-recut and verified. No source worktree was modified. The table retains the before/after hashes.

- capture = sol-recut working tree on 19 Oct (includes 0.8); no Clariden code snapshot equals it
- census_03 ran snapshot 87407ec7430a375f (all 325 manifest files match)
- the census_04 package derives from 87407ec7 with only the 0.8 segmentation files + tool-versions changed

The last statement describes changes **among the 325 baseline files**. Two additive files implement the requested diagnostic and split plumbing: `numeric_cells.py` and `line_pipeline_census04.py`. No other baseline source changed. The census fingerprint truthfully includes these adapters and the 0.8 native source. [Composition](package_composition.json).

The full-suite comparison found no regressions: 4,051 passed; all 36 failures and 5 setup errors also fail on pristine sol/seg-cells. Only `tests/test_seg_cp7c.py` is deselected, after the same missing CP5 evidence was proven on pristine. [Comparison](suite_comparison.json). No historical evidence was copied in this run.

## Existing-file conflicts

Full unified diffs: [source_conflicts.patch](source_conflicts.patch).

| File | Branch SHA256 | Sol-recut SHA256 | Difference |
|---|---|---|---|
| greekocr/harvest/geometry_observations.py | `b987509ea007401c2317829ee7abcd032f40cb52c2b8eefc51877bc8a6ad0d78` | `524972373acb094384f48055dfb1189f799c648df81370c5a9d5952c7798c695` | Extract existing geometry validation/quarantine to prepare_geometry_row; loader delegates to it. |
| greekocr/harvest/row_inclusion.py | `ceeb8ca065d54289739c02620167b7169b584e1be6c0d43e2a75524868b057fb` | `f688347ff2d2461a81be879ba4cfe6540621e91d7f39f3638a3e59117b5ba98b` | Optional magnitude_loader injection. |
| pyproject.toml | `c49e727731c53979db540197d3f0eb60327aacef6696174e60b23684f8f9add3` | `e963e52128ce50ff4320b501b679d51c6ed13c6929f4c93b7414dd7f58f4aee1` | Register filter CLI and filtering package data. |

## Clariden snapshot comparisons

SSH succeeded. Each requested path was SHA256 checked in every listed snapshot. **No exact match exists.** Missing documentation is counted as missing, not silently excluded. The current sol-recut source includes 0.8; the deployed census snapshots used 0.5.

| Snapshot | Same | Different present | Missing |
|---|---:|---:|---:|
| 05a3eb60c921b6e4 | 8 | 9 | 133 |
| 2527901af7ec870e | 10 | 8 | 132 |
| 413f8dc311e772e0 | 8 | 9 | 133 |
| 44012fe4dbb59aa4 | 8 | 9 | 133 |
| 6261c3f58cc80e1b | 12 | 6 | 132 |
| 786f64d7712f0717 | 10 | 8 | 132 |
| 96e82c64fd7f5335 | 9 | 9 | 132 |
| aea118049ff77422 | 8 | 9 | 133 |
| be263f1ff3c93cce | 8 | 10 | 132 |
| d67c76bc6e93e8ae | 9 | 9 | 132 |
| d74ad2830c479f7b | 14 | 4 | 132 |
| e393b4c787db7b75 | 10 | 8 | 132 |
| f9e06adc1e43b24b | 10 | 8 | 132 |
| fd4d5e20283b4f1b | 10 | 8 | 132 |
| census03_87407ec7430a375f | 12 | 6 | 132 |

Per-file hashes and missing paths: [source_capture.json](source_capture.json); complete unified diffs for present differences: [snapshot_diffs/](snapshot_diffs/). All captured file hashes are in `capture_inventory.json`.

## Actual census_03 baseline

Job 3695426 used **87407ec7430a375f**, nested under `prepared/`, rather than a directory in `code/`. Its exact path, config binding and SHA check are in [remote_evidence/census03.sbatch](remote_evidence/census03.sbatch) and [remote_evidence/code_receipt.json](remote_evidence/code_receipt.json).

Downloaded baseline: `census03_baseline/projects/`. All **325** manifest entries independently match; manifest SHA256 **7c885291db4b661b026ffdad9f3c6d9e5f7a6dcdb426ddda7b2bdc8f037ea05c**.

Compared with that baseline, six present capture files differ: the segmentation policy, crop tools, native adapter, versions JSON, core pipeline and census. The final two are the census_03 numeric-adjacency and external-heldout-crop fixes, which the local sol-recut capture lacks. The candidate package therefore starts from census_03, not from the capture.

