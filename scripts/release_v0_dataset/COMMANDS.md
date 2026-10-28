# REL0-S4a source probes — coordinator commands, 28 October 2026

These scripts only read local inputs and write a **fresh, disjoint** `--output-dir`.
They use no SSH, network, git, credentials, model, GPU, image decoder or generator.
The coordinator downloads pinned HF snapshots separately. Do not pass a token to
these commands, a scheduler environment, or a receipt. Existing output directories
are refused; choose a new attempt. Directory symlinks and file symlinks are not
followed. Mounted `/iopsstor`/`/capstor` aliases may point to the same data: do not
add their file counts together as independent observations.

Use an existing CPU Python environment with Python >=3.10, `pyarrow` and `ijson`.
No installer is run by either probe. `ijson` is needed for compressed/large JSON;
without it small JSON/JSONL/Parquet still work, and unsupported inputs report an
error and exit 2. Large JSON objects require an explicit selection to avoid
loading a giant mapping. Parquet reads project metadata columns in 512-row batches
with one Arrow thread; images are neither projected nor decoded. JSON may contain
embedded image strings; none are emitted. Metadata JSON/JSONL and opaque archives
are different: TARs and images receive file/byte inventory only, not member scans.

## 1. Locate bindings and sample on the login node

Run from the toolkit checkout containing these scripts. All shell variables below
are task-specific. Set the HF directories to the coordinator's **completed pinned
snapshot** directories, not a mutable Hub cache ref. Record the full harvest commit
in the separate download/input lock: only the prefix `103c6dcd1e…` is supplied in
this brief; the probe cannot certify a directory's originating HF commit.

```sh
rel0_base=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
rel0_prepared="$rel0_base/train_full/attempts/full-v1-005-genn/data/prepared"
rel0_hf="$rel0_base/release_v0/sources/hf_archive"
rel0_probe="$rel0_base/release_v0/probes"

# Coordinator must substitute the actual snapshot paths if downloader layout differs.
rel0_staging="$rel0_hf/staging-v4"
rel0_harvest="$rel0_hf/harvest-20261025"

python3 -B scripts/release_v0_dataset/probe_sources.py \
  --source "staging=$rel0_staging" --source "hfharvest=$rel0_harvest" \
  --source "runtime=$rel0_prepared/runtime.json" \
  --source "config=$rel0_base/train_full/attempts/full-v1-005-genn/data.json" \
  --source "s1mix=$rel0_base/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/shared/real_mix.json" \
  --source "s1node=$rel0_base/scaling_w3/s1_run01/w2_ref_364871/node_binding.json" \
  --output-dir "$rel0_probe/discovery-001" --max-rows 20
```

`*.inventory.json` includes discovered absolute paths from runtime, config and mix
receipts. These locators are **not automatically opened**. Inspect the actual
config to confirm the Gennadius harvest-root switch, S1 node identity, source
relocations and referenced mixes; `data.template.json` is only a path guide. Sample
mode bounds rows **per file**, not total files: a huge tree still costs a full stat
walk. For the lightest first run pass just receipt files, then directory roots in
a CPU job. Sampling never establishes global JSONL counts or a completed join.

`staging-v4` expected pin: `8ee9cb2e4c880f450c69b9c45cd683765d4da755`.
The probe inventories pages/rasters, MAC Google boxes/outcomes, source descriptors,
raw-object containers and manifests; no assumption that staging contains v4 line
images. The harvested snapshot is expected to contain root/split metadata, PNGs,
decisions, registry and receipts. Duplicate root/split views remain separate.

## 2. Full metadata/key scan in a short CPU job

No scheduler submission is included. Census decisions alone are ~11 GB of JSONL;
use a CPU job rather than streaming that on the login node. Start with 1 CPU and
4–8 GiB RAM; measure elapsed and scratch before choosing a full allocation. File
statistics do not verify content SHA. `--full` streams JSONL once and projects
Parquet metadata, leaving all original inputs unchanged.

```sh
rel0_s1="$rel0_base/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/shared"
rel0_old=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code/out/e4/wave2/job02
rel0_census="$rel0_base/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d"

python3 -B scripts/release_v0_dataset/probe_sources.py \
  --source "prepared=$rel0_prepared" \
  --source "hfharvest=$rel0_harvest" \
  --source "harvest=$rel0_base/releases/harvest_20261025_v1" \
  --source "gennadius=$rel0_base/releases/release_with_gennadius_cached_v4" \
  --source "s1subset=$rel0_base/scaling_w3/subsets/scale1-c05-003/ref_364871.jsonl" \
  --source "s1records=$rel0_s1/records.jsonl" \
  --source "s1info=$rel0_s1/real/build_info.json" \
  --source "old0=$rel0_old/union_0/train" --source "old1=$rel0_old/union_1/train" \
  --source "census=$rel0_census/decisions.jsonl" \
  --source "releasev4=$rel0_base/release_v4/rel4_c06_full_01" \
  --source "v4package=$rel0_base/release_v4/pkg/fde561ca/inputs" \
  --source "crops4=$rel0_base/crops4_attempts/crops4_c06_full_01" \
  --json-map 'prepared|factory/build_info.json|crop_sha256' \
  --json-map 's1info|build_info.json|crop_sha256' \
  --compare 's1_old0=s1subset|*|row_id|old0|*.parquet|line_id' \
  --compare 's1_old1=s1subset|*|row_id|old1|*.parquet|line_id' \
  --compare 's1_retained=s1subset|*|row_id|prepared|[np]*/*.parquet|nonharvest_id_candidate' \
  --compare 'harvest_prepared=harvest|metadata.jsonl|harvest_wave_id|prepared|[hnp]*/*.parquet|harvest_wave_id' \
  --compare 'harvest_hf=harvest|metadata.jsonl|harvest_wave_id|hfharvest|metadata.jsonl|harvest_wave_id' \
  --output-dir "$rel0_probe/full-001" --full
```

Confirm S1 shard directories in the discovered shared real mix; add each as a
named source to inventory the **physical payloads behind the 364,871 subset**.
Add the audit's manifest directory (including `rows.jsonl`, eval-wins removal and
repeat witnesses) from actual runtime/audit paths, plus the frozen reference mix
paths from the S1 node. The audit can reference attempt **004** witness files even
when runtime is **005**; retain those explicit bindings. Do not guess replacements.
If a source JSON is a root array, use `--json-array 'NAME|GLOB|item'`; for a nested
array use `rows.item`; for keyed metadata use `--json-map 'NAME|GLOB|PREFIX'`.
Large JSON with no selector fails explicitly rather than hiding a memory spike.

Comparisons use `NAME=SOURCE|FILE_GLOB|KEY_FAMILY|SOURCE|FILE_GLOB|KEY_FAMILY`.
Families include literal key columns, `parent_row` (typed `[parent_id,row_id]`),
`harvest_wave_id` (`[wave,id]`, also parsed from `harvest:<wave>:<id>`),
`harvest_original_id`, `trainer_id_candidate`, `nonharvest_id_candidate`, and
`_map_key`. Candidate families expose possible mappings; they do not qualify them.
Never strip a harvest namespace for a final join unless uniqueness is proven.
For census compare `parent_row` against the release table's same key; if that
source lacks it, the missing relation is a finding, not an invitation to guess.

`keys.sqlite` preserves counts by source/file/family/value; comparisons emit all
left/right-only **keys**, duplicate-key counts and intersection, without image or
text payloads. The two old unions must be reconciled as a **union of distinct
keys**, not by adding two intersections; use their index rows in SQLite. A
complete comparison also needs observed keys and selected tables on both sides.
Each inventory records errors and coverage extent. Exit 0 means the requested
probe completed without input errors; it does **not** mean publication acceptance.
A sampled probe can exit 0 with incomplete scans. Exit 2 means missing/unreadable/
unsupported input. Keep those findings and choose a new attempt for a rerun.

The population comparison produces the expected 698 **net** difference only if
old keys form the expected subset. Retain both directional key lists: 698 is not
proof of 698 additions and zero removals. Similarly, the one S1 removal and two
harvest removals need the audit's keyed crop witnesses. Probes test joinability;
phase (b) verifies every image/label variant and per-model membership.

## 3. Synthetic builds, kept separate

```sh
rel0_a12=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12
python3 -B scripts/release_v0_dataset/probe_synthetic.py \
  --build "a12=$rel0_a12" --build "old_synth=$rel0_old/control_synthetic_7" \
  --build "prepared_train=$rel0_prepared/synthetic" \
  --evidence "prepared_train=$rel0_prepared/runtime.json" \
  --factory-src greekocr/_vendor/factory/src \
  --output-dir "$rel0_probe/synthetic-001"
```

Add **explicit** build/codec/source/font/job/recipe receipt files with
`--evidence BUILD_NAME=/path/file.json` after locating them. The probe hashes
receipts, reports configured versus realised distributions, row-column coverage,
full-font-SHA versus sha16 evidence, distinct source/effective recipe hashes,
generator identities, seeds, text locators, and every observed operation name
with occurrence count and local file:function mapping. Ordered operations stay in
the original rows; counts do not replace sequences. Unknown operation names stay
UNMAPPED. Local source SHA proves only the inspected map, not historical binary
identity. No global absence claim follows from absence in the searched roots.
Use `--sample-rows 20` for a preliminary diagnostic; incomplete split totals are
null. A12 and old_synth val/reserved never get combined on recipe name alone.

## 4. Offline tiny fixtures

```sh
PYTHONPATH=. python3 -B -m pytest tests/release_v0_dataset \
  --confcutdir=tests/release_v0_dataset -q -p no:cacheprovider \
  --basetemp=/private/tmp/rel0-s4a-probe-pytest
```

The dedicated conftest blocks network and avoids unrelated predictor/torch
fixtures. `--confcutdir` also avoids this checkout's top-level `tests._paths`
import failure under the supplied interpreter. Remove only that pytest basetemp
after collecting the result (this run does so); never remove any source tree.
