# T6e L1E ownership export

Run these two commands from the `sol/l1e-mask` worktree root. Each output directory must be new or empty. The full jobs are for the operator to execute; this hand-off processes only the five-line test.

200 IDs → r4, comparing every crop against r3:

```sh
nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/run.py --ids ~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_masking_sample_ids.txt --export-ownership --out ~/Projects/collect-v3-data/v2_masked/l1e_sample_r4 --compare ~/Projects/collect-v3-data/v2_masked/l1e_sample_r3
```

Vouli 60 → vouli r2, comparing against the original vouli output:

```sh
nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/run.py --ids ~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_masking_sample_ids_vouli.txt --export-ownership --out ~/Projects/collect-v3-data/v2_masked/l1e_sample_vouli_r2 --compare ~/Projects/collect-v3-data/v2_masked/l1e_sample_vouli
```

`--export-ownership` is opt-in. Without it, the existing masking and audit flow produces crops and counts without ownership PNGs or component lists. `--compare <previous-output>` binds the requested IDs, crop rectangles, reference crop file hashes and mask hashes before detection. Every generated crop must have the same file SHA256 and applied-mask SHA256 as its reference; missing IDs, changed references or mismatches fail with a nonzero exit and a failure receipt. Matching/custody identity crops still use byte-exact copies of the stored crop.

## Ownership files and records

For each line, `ownership/<wave>/<doc>/<crop-stem>.png` is a single-channel, 8-bit greyscale PNG (`L`), exactly `(x1-x0, y1-y0)` pixels. Pixel `(0,0)` is native page pixel `(x0,y0)` of `crop_box`; there is no resize, padding, rotation or coordinate translation beyond that origin.

| Value | Meaning |
|---|---|
| 0 | Background, outside the masking library's ink set |
| 1 | Ink retained by the frozen Voronoi keep rule (identity exception below) |
| 2 | Masked ink assigned to a detector row above the selected line |
| 3 | Masked ink assigned to a detector row below the selected line |
| 4 | Masked ink without an assigned detector row |
| 5 | Foreign by Voronoi, retained because its component has an empty background ring |

`ownership_sets` calls the frozen `_centre_fit`, `_foreign_mask` and `_ring` functions on the same page, line, neighbours and rectangle passed to `mask_foreign_ink`. The runtime checks pixelwise equality of classes 2/3/4 with `MaskedCrop.mask`, the resulting `mask_sha256`, equality of class 5 with the reconstructed ring abstentions, and the complete background/keep partition. PNG dimensions, mode and every pixel are verified again on disk readback.

Each opted-in `lines.jsonl` record adds `ownership_path`, `ownership_sha256`, `ownership_export_status`, `ownership_checks` (mask-union and abstention hashes, counts of classes 0–5), and `components`. Each component entry has:

- `component_id`: the masking page's connected-component ID, matching the namespace used by `fills`.
- `detector_component_id`: the component ID at the same native pixels in the detector's distinct label plane, or null if those pixels are absent from that observation.
- `class_value` and `pixel_count`: the class and count for this component slice inside the crop.
- `owner_row_id`: its actual detector row index, or null if unassigned.
- `side`: `own`, `above`, `below`, or `unassigned` relative to the selected runtime line.
- `owner_geometry_valid`: whether that owner passed `prepare_audit_rows`, or null for unassigned ink.
- `ownership_conflict` and `side_basis`: explicit exceptions described below, or null/`detector_owner` for normal Voronoi exports.

The component list partitions all ink in the crop, including classes 1 and 5. A masking component may intersect multiple detector components or classes, so its ID may appear in several entries. Assignments come from the detector component rows prepared by `prepare_audit_rows`, with native detector labels providing the per-pixel crosswalk. An invalid ribbon cannot erase explicit component assignments: its raw detector `component_ids` remain available, marked `owner_geometry_valid=false`; the existing page-level own-loss audit remains unknown. No majority-overlap assignment is made. Above/below uses the median body-centre offset at the component's observed X coordinates; a nonadjacent owner's actual row ID is retained.

Detector attribution and Voronoi attribution are different observations. The six requested classes omit two cases already present in the reference samples. To retain the exact class-2/3/4 mask union and export every matching-status identity, the exporter uses these explicit exceptions:

- Masked ink assigned to the selected detector row uses class 2 above its body-centre curve and class 3 at or below that curve, per pixel. Its actual `owner_row_id` remains the selected row, `ownership_conflict="masked_detector_own"`, and `side_basis="pixel_position"`. Thus these flagged 2/3 entries describe the masked pixels' vertical side, rather than a different detector owner. The line has `ownership_export_status="voronoi_with_detector_conflicts"`; `ownership_checks.detector_own_masked_pixels` counts the exception. Existing reference audit counts show this issue in six r3 lines and three vouli lines.
- An unmatched or ambiguous crop is an untouched identity, with no applied mask or ring abstention. All native ink is class 1, with `ownership_export_status="identity_unmatched"` or `"identity_ambiguous"` and `ownership_checks.keep_basis="identity_unmasked"`. Assigned component sides are `unresolved`, with their actual detector owner IDs retained. This class 1 means kept by the identity operation; no Voronoi attribution is claimed. Normal lines use `keep_basis="_voronoi_keep"`.

These conventions are a documented resolution of the schema gap, not additional evidence that detector and Voronoi ownership agree. A custody-failed crop cannot safely be aligned to native ownership and makes an opted-in export fail loudly. None of the supplied r3/vouli reference records has a custody failure.

`crops/<wave>/<doc>/<file>.png`, source masking records, own-loss counts and matching logic retain T6d behavior. `comparison.json` binds the selected reference files; each line records its successful comparison. `receipt.json` states whether export was enabled and how many reference crops were verified. Partial artifacts and page logs remain after a failure; failed runs cannot resume into the same directory.

## Frozen processing and input custody

`foreign_ink.py` is unchanged. All existing frozen-source checks remain, including parameter SHA256 `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8` and library SHA256 `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5`. Matching still executes the original hash-checked T6a2 `match` and `runtime_fit`; no added column gate or ownership tolerance changes the crops.

All requested IDs are validated against the canonical v2 train/dev/test manifests and admitted metadata before `--limit` selects work. Accepted waves are round1, round2, mixed and vouli. Raster resolution uses the existing `pages_scan.jsonl`, including round1 rescue images and shortened round2 crop-directory document keys. `--validate-only` checks IDs and metadata and, when supplied, binds comparison crops, without creating output or running detection.

Each page uses one fresh subprocess, sequentially, at nice >=15. Numerical thread environment variables are forced to one; OpenCV parallel regions are disabled and verified. The audit hook blocks network connections and writes outside `--out`. Original rasters, crops, metadata, ID lists and comparison directories are read-only. The inherited T6d watchdog checks free space every second, stops below 10 GB and enforces its 55-minute runtime budget. No W1 locks are taken.

## Tests and five-line verification

```sh
nice -n 15 .venv/bin/python -B -m pytest -q -p no:cacheprovider docs/records/harvest/recut_v1/l1e_sample/tests docs/records/harvest/recut_v1/masking/tests/test_foreign_ink.py
```

The authorized five-line check writes only to the ignored local output:

```sh
nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/run.py --ids ~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_masking_sample_ids.txt --limit 5 --export-ownership --out docs/records/harvest/recut_v1/l1e_sample/test_out_t6e_final --compare ~/Projects/collect-v3-data/v2_masked/l1e_sample_r3
```

55 tests pass. All five lines passed the mask-union and native PNG alignment checks and matched the r3 crop bytes. Their maps contain 245 class-2 pixels, 134 class-3 pixels, 198 class-4 pixels and no class-5 pixels; the unit suite exercises real `_ring` abstention using a controlled native ink plane, own-row conflicts and identity maps. Total applied mask: 577 pixels; three crops changed; no measured own loss or schema exceptions in these five lines. These checks do not establish full 200-line or vouli export results. All 200 main-sample and 60 vouli IDs and reference crops also pass read-only validation. [t6e_validation.json](t6e_validation.json) records independent PNG/crop readback and source hashes; the earlier T6d evidence is retained in `test_validation.json`.

## Guarded commit

```sh
.venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/guarded_commit.py --prepare
.venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/guarded_commit.py --check-only
.venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/guarded_commit.py
```

The helper binds starting HEAD `55efb378afa4d8ef5831f77899b773296566f597` and branch `sol/l1e-mask`, requires an empty index, hashes changed source files only within this directory, excludes ignored paths, validates `handoff.patch`, and checks the exact staged set. It excludes unchanged files, test output, logs and caches. An index permission failure is terminal: no retry or alternate index. Ignored `COMMIT_STATUS.json` records the outcome. The helper is also tested in an isolated temporary repository.
