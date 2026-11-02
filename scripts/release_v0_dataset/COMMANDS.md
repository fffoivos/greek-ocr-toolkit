# REL0-S4a probes and REL0-S4b builder — coordinator commands, 28 October 2026

## REL0-S4p — complete original crop hash census

From the deployed checkout root on Clariden, submit the existing CPU-only wrapper:

```sh
sbatch scripts/release_v0_dataset/resolve.sbatch /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/probes/original-crops-s4p-001 original_crops
```

This is the exact item command, provided for the coordinator; it was not run in
S4p. The output directory must be fresh. The wrapper requests 4 CPU cores,
48 GiB, no GPU, and 02:00:00; work has a 4800-second deadline and a separate
600-second reporting allowance. Every selected source receives a fair first-pass
scan share, with progress and partial/error status. The remaining item-query
budget covers exact S1/v4 mapping and per-population counts. There is no row
sample limit: `--samples` limits report examples only. Recorded crop files are
read and hashed in the disposable reader; image bytes are never emitted.

Review `original_crops.json` only when `complete` and `counts_complete` are true.
For every population inspect `rows`, `recorded_path`, `files_exist`,
`hashes_match`, `mapped_rows` and the three null-reason counts. Partial source or
mapping work cannot resolve the binding. Adopt the measured per-population
coverage in a new source spec, with the report's hash; then freeze and rebuild
into fresh output/work directories. The checked-in binding stays
`pending_resolve: original_crops` until those complete numbers exist. The
previous `original_assets` item remains metadata discovery evidence.

## REL0-S4d — coordinator decisions and Clariden resolver

`specs/source-spec-001.json` now assigns dataset **v0.5**, synthetic set
**v0.5** (lower bound), generator **v0.1** (lower bound), builder **v0.4**,
and OCR **v0.10** (lower bound), under the coordinator's owner-item-8 ruling.
The supplied public producing commit, final executed RUN_BINDING/CLAIM file
hashes, Unicode 15.0.0 and codec identities are bound in the spec. No remote/git
verification was performed in REL0-S4d.

The former 32 unresolved entries are now **13 filled decisions, 9 historical
unknowns and 10 pending resolver bindings**. Historical entries have
`value:null`, a reason/evidence locator, `historical_unknown:true`,
`blocks_freeze:false` and `blocks_smoke:false`. They survive in INPUT_LOCK,
`manifests/COVERAGE.json.historical_unknowns` and the card's **Known gaps**.
The census/old seven-key reconciliation is also probed, but remains a
non-blocking historical unknown until a valid tuple bridge settles it. The
directional one-S1/two-harvest removal key lists remain bound; audit witnesses
are not fabricated. All 10 pending joins retain null values and `resolve_probe`
item ids. Full relation and trained-row identity checks remain required.

The standalone validator uses **jsonschema** (Draft 2020-12); freeze invokes
the same validator before opening sources. Validation alone is structural,
not a claim of complete join coverage. Freeze verifies codec/Scripts SHA256s
against the supplied identities; read_lock checks the running Unicode database.
Use the existing Clariden Python 3.12.15 environment with Unicode **15.0.0**.

```sh
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --validate-spec scripts/release_v0_dataset/specs/source-spec-001.json
```

Run the following **inside a coordinator-authorized single debug-node CPU
allocation of 01:30:00**. This command does not allocate or submit anything.
Use an existing environment with `pyarrow` and `ijson` (`ijson` is required
for large/compressed JSON; small JSON has a bounded local fallback). A few GB
of private scratch for disk-backed key indexes is needed. No GPU, Hub client,
credentials or source-tree writes are used. The output directory must be fresh
and disjoint from every selected input; index files live only there.

```sh
rel0_resolve=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/probes/resolve-001
env -u HF_TOKEN -u HUGGING_FACE_HUB_TOKEN -u HUGGINGFACEHUB_API_TOKEN \
  -u HUGGINGFACE_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS \
  -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
  python3 -B scripts/release_v0_dataset/resolve_probe.py \
  --output-dir "$rel0_resolve" --budget-seconds 4800 --samples 3
```

Sources are shared across items and scanned once. Parquet reads project only
metadata columns, excluding nested binary fields before reading batches. JSON
strings (including raw box/provider metadata) are parsed for nested selectors;
image/content fields are removed. Source payloads, rasters and embedded
locators are never opened automatically. Root JSON maps stream top-level
entries; `json_selector` can explicitly select an array using ijson notation.
JSON coverage denominators are reported with their record unit; list selectors
use `[]`. Examples truncate long strings, arrays and objects. Full key counts
are separate from these samples. Per-wave bibliography coverage includes
explicit zero/missing counts for requested fields, together with their actual
observed selectors; exact nested schemas and examples preserve alternative
historical field names for review.

| JSON item | Evidence and counts to review |
|---|---|
| `v4_bridge` | census06 g2 binding tuples, v4 admissions, crops4 manifests, S1/old pools and staging pages/boxes/mac provenance; candidate tuple/ID/hash equality, directional census-versus-old tuple counts via S1, missing old aliases and ambiguous S1 ids |
| `logical_pages` | page_object_id, source_page_id, parsed page_object_ids_json and page/book relationships; candidate equality retains exact selectors |
| `page_frames` | Document AI dimension_json, transforms/detail/raw-page metadata, box frames and dimension fields; no transforms inferred from crop bounds |
| `segmenter_page_results` | source_object_id + raw_page_index, segmenter_run_id, page-image and observed logical-page key counts |
| `seal04` | seal04 suite/panel metadata schemas, nested panel paths, tuple/line ids and candidate coverage against census/S1 |
| `validation_bridge` | all selected prepared validation line_ids (expected population 13,088) versus census/S1/v4; inspect namespace collisions before adopting aliases |
| `row_instruments` | registry row_instrument_roles structures/examples, membership keys and suite/panel candidate joins |
| `harvest_provenance` | nested provenance selectors, catalogue/manifest/source URLs, edition/volume and page convention, coverage by wave |
| `original_assets` | crops4 manifest values, S1 original locators, original shared build/mix/records and node binding, mac manifests, data.json s1_asset_relocations contents |
| `raw_segmenter` | raw_segmenter_json nested language, emitted-index, reading-order and coordinate-frame selectors with coverage/examples |

Outputs: one `<item>.json` per row above, `SUMMARY.json`, `SUMMARY.md`, and
private `keys.sqlite`. Each JSON embeds source file identities (path/stat bytes;
not a full payload SHA), physical/observed schemas, sample rows, exact nested
field/nonnull coverage and key counts. Candidate comparisons include both
directions, matched occurrences and ambiguous right keys. Image SHA equality,
bare line-id equality and a complete scan alone are never promoted to identity.
`resolved:false` requires coordinator review even after a complete scan.

The **80-minute** scan/comparison budget reserves ten minutes for writing
reports before the allocation ends. The timer interrupts metadata reads;
missing/malformed sources or expired budgets produce partial reports and exit
**2**, not a success claim. Counts then apply only to scanned records. No live
Clariden timing has been measured here; if the budget is insufficient, retain
this evidence and rerun an explicitly narrowed plan. Reporting latency still
depends on the shared filesystem.

For a discovered manifest/relocation file or alternate suite representation,
copy the `SUMMARY.json.plan` object into a reviewed local plan and explicitly
add its path to the appropriate source's `patterns` (or add `json_selector`,
for example `panels.dev.item`). Run with `--plan /path/to/plan.json` and a new
`--output-dir`. Embedded locators are never authorization for traversal. Retain
the first report; do not rewrite null selectors without the resulting evidence.

After coordinator review, fill only demonstrated joins/selectors, validate,
then freeze using the existing command below. Historical-null entries do not
block freeze/smoke. Complete supporting relations and original/prepared tuple
coverage are still necessary for a full build and independent acceptance.

Local offline checks (then remove only this exact basetemp):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -B -m pytest tests/release_v0_dataset \
  --confcutdir=tests/release_v0_dataset -q -p no:cacheprovider \
  --basetemp=tests/release_v0_dataset/.basetemp-s4d
```

## REL0-S4j measured spec: freeze → plan → smoke

S4i-002 source observations are now bound as measured partial coverage (zero
book ambiguity). Exact field counts/null reasons and original-ID instrument
counts are in the spec, BOOK_BRIDGE.md and JOIN_DECISIONS.md. COVERAGE.json
keeps retained full-probe counts separate from this build's counts. Missing
harvest book origins, synthetic origins and other gaps remain explicit.

From the **deployed checkout root**, in an already authorized Clariden CPU
allocation, using the existing Python 3.12.15 / Unicode 15.0.0 release venv and
fresh output paths, after deployment verification:

```sh
rel0_python=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python
rel0_build=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/builds/s4j-001

"$rel0_python" -B scripts/release_v0_dataset/build_dataset.py \
  --freeze scripts/release_v0_dataset/specs/source-spec-001.json \
  --lock-out "$rel0_build/INPUT_LOCK.json"

"$rel0_python" -B scripts/release_v0_dataset/build_dataset.py \
  --input-lock "$rel0_build/INPUT_LOCK.json" --plan

"$rel0_python" -B scripts/release_v0_dataset/build_dataset.py \
  --input-lock "$rel0_build/INPUT_LOCK.json" \
  --out "$rel0_build/dataset-smoke" --work "$rel0_build/dataset-smoke.work" --smoke 3
```

Freeze hashes every selected input in full; --smoke bounds subsequent row
processing, not that hash I/O. These commands were prepared locally, not run
on Clariden. Structural validation and smoke do not certify full release or
independent acceptance; existing acceptance/geometry/asset gaps remain in GAPS.md.

## 0. Dataset build and independent readback (REL0-S4b)

Implementation: `build_dataset.py`, `common.py`, `features.py`,
`accept_dataset.py`, `build.sbatch`. Python >=3.10, `pyarrow`; `ijson` for
explicit JSON map/array selectors. `datasets` is optional: acceptance opens every
config with it when installed, otherwise every Parquet with Arrow. Pillow is
optional for ordinary non-interlaced PNG consumer checks (there is an independent
PNG decoder); other image formats/interlaced PNG require a working Pillow.
The **builder never decodes/re-encodes** any image. No installer, SSH, Hub,
network, git operation or scheduler submission is implemented here.

First prepare an **explicit local source spec** as described in
[SOURCE_SPEC.md](SOURCE_SPEC.md). It selects immutable files, original crop
assets/TARs, relation projections and typed joins. This is required input, not an
automatically inferred mapping. The saved probes establish row schemas and key
counts; they do not establish every page/box/frame join. Missing joins are
checkpoint findings, never names guessed from image hashes. Fill selectors from
inspected pinned sources before freezing. Do not select overlapping root/split
metadata as independent populations. `old_synth` is not an A12 alias.

On Clariden, using an existing CPU Python environment and the deployed checkout:

```sh
rel0_build=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/builds
rel0_spec=/path/to/reviewed-source-spec.json
rel0_lock="$rel0_build/inputs-001.json"
rel0_out="$rel0_build/dataset-001"
rel0_work="$rel0_build/dataset-001.work"

# CPU preparation: expands only the supplied patterns, hashes every selected file.
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --freeze "$rel0_spec" --lock-out "$rel0_lock"

# No output directory is created by --plan. JSON reports table bytes, file count,
# scratch envelope and CPU-hours, stating any assumed rather than measured rate.
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --input-lock "$rel0_lock" --plan

# Bounded first build: a few books per population, at most N*512 records per
# selected input file (override smoke_rows_per_source in spec), first A12 shard,
# first prepared shard per explicitly selected pool, first raster shard/source.
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --input-lock "$rel0_lock" --out "$rel0_out" --work "$rel0_work" --smoke 3
python3 -B scripts/release_v0_dataset/accept_dataset.py "$rel0_out" \
  --allow-smoke --report "$rel0_build/smoke-001.accept.json"
```

Smoke still hashes each **selected** immutable input file in full; a large census
file therefore has nontrivial hash I/O even though row parsing/payload output is
bounded. It cannot establish complete books, full coverage or release acceptance.
For a small first hash pass, freeze a separate spec with explicitly bounded source
files. Do not claim that a row cap bounds input hashing bytes.

The supplied sbatch is an **unsubmitted benchmark wrapper**, 8 CPUs/32 GiB,
zero GPUs, 30 minutes, partition `preemptable`, account `a0140`, `--export=NONE`.
It forwards the same CLI arguments. Always **submit from the checkout root**,
including `sbatch --test-only`: Slurm sets `SLURM_SUBMIT_DIR` to that directory,
and the wrapper expects `scripts/release_v0_dataset/build_dataset.py` beneath it.
Direct shell execution without `SLURM_SUBMIT_DIR` uses the wrapper's own directory.
A missing script fails before `srun` with its expected path and submission-root hint. Coordinator verifies local/deployed code and
lock SHAs, checks `sbatch --test-only`, and chooses the actual full allocation from
measured smoke rates and `--plan`; the wrapper's time is not a full-run estimate.
No credentials may enter the scheduler environment. Do not run a full build on
the Mac or hash the entire source tree on a login node.

For the full candidate, choose **fresh** out/work names and omit `--smoke`.
After interruption, repeat the **identical** command plus `--resume`. The lock,
all Python code hashes, cap/target and smoke extent bind the work ledger. Input
files are rehashed; a changed binding requires a new out/work. A file import is
one SQLite transaction; committed output batches carry logical input digests
and closed-file SHA receipts. Completed batches are verified and reused. Work
SQLite and checkpoint receipts live outside the public tree. A complete resumed
build preserves all public bytes, including timing/manifest receipts.

```sh
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --input-lock "$rel0_lock" --out "$rel0_build/full-001" \
  --work "$rel0_build/full-001.work"
python3 -B scripts/release_v0_dataset/accept_dataset.py "$rel0_build/full-001" \
  --input-lock "$rel0_lock" --report "$rel0_build/full-001.accept.json"

# After the coordinator separately uploads/downloads an exact pinned candidate:
python3 -B scripts/release_v0_dataset/accept_dataset.py /disjoint/downloaded-copy \
  --input-lock "$rel0_lock" --report "$rel0_build/download-001.accept.json"
```

Full acceptance reopens **all** output files, checks full path/byte/SHA coverage,
all embedded image hashes, typed keys/FKs/status/reasons, source labels/codec,
prepared shard ordinals/pool order, source-key directional differences, canonical
release counts, registry assignments, source-field coverage and a deterministic
1,000-row/all-label-variant independent feature replay (seed 20261022).
It independently streams the external locked sources again. The portable feature
bundle permits package-only checks without the original machine's paths.
Without `--input-lock`, the result is **SELF_CHECK_ONLY**, exit 2 for a full
candidate; it cannot certify source coverage. `--allow-smoke` explicitly permits
only this diagnostic result with exit 0; it never returns release PASS.
Reports must be fresh and outside the candidate, so readback does not change it.

`MANIFEST.json` excludes itself/SHA256SUMS; SHA256SUMS includes the manifest.
Table singletons use PLAN names; overflowing tables use `tables/<name>/part-*`
(registry similarly), and image configs always use parts. Every closed file is
checked against the cap (default 1,000,000,000 B, target 512,000,000 B). Parquet
and gzip streams recursively split oversized closed parts, preserving original
bytes and observation order. An individually oversized record is a packaging
finding and fails instead of truncating/re-encoding it. Metadata singletons must
also fit the cap; a missing complete MANIFEST means no completed candidate.
Public rows retain complete sanitized `record_json` alongside stable typed
columns. JSON-valued columns use canonical UTF-8 JSON strings, and ordered simple
lists (`label_ids`, operations, model ids, scripts) are Arrow lists. Decision
reasons can be structured objects and therefore use canonical JSON; a recorded
empty ADMIT failure list is preserved, while HOLD/DROP require their reasons.
The real view's primary `trainer_image` is accompanied by `trainer_variants[]`,
which embeds every pool/variant's original consumed bytes and exact codec label.
Thus raw/corrected/reference uses of one row do not overwrite its train variant.

Validation in this checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -B -m pytest tests/release_v0_dataset \
  --confcutdir=tests/release_v0_dataset -q -p no:cacheprovider \
  --basetemp=/private/tmp/rel0-s4b-pytest
bash -n scripts/release_v0_dataset/build.sbatch
```

The task's pytest scratch is removed after recording results. Tiny fixtures and
local Arrow loading are implementation evidence, **not** a Clariden production
build, installed-`datasets` readback, public visibility or main/tag validation.

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

## REL0-S4q — original crops only, 28–29 October 2026

The S4p report on code `rel0-s4p-20261028` completely verified S1
364,871/364,871, v4 167,946/167,946 and old 364,173/364,173 original images.
The spec now records those populations as resolved under the partial
`assets.original_crops` binding. Only census, harvest, seal04 and validation
retain `pending_resolve: original_crops`.

From the deployed checkout root, run exactly this one item into a fresh output:

```sh
sbatch scripts/release_v0_dataset/resolve.sbatch /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/probes/original-crops-s4q-001 original_crops
```

The unchanged wrapper allows 4,800 seconds of work plus at most 600 seconds of
reporting. S1/v4/old remain dependencies of this one item. Its dedicated scan
skips generic nested metadata/key indexing, hashes each distinct recorded file
once per fresh run in `crop-files.sqlite`, and reuses measured byte SHA256
identity for all 592,466 census rows, including non-admitted/non-train rows.
The census source count must equal that frozen denominator for complete counts.
Seal04 uses the exact panel `(parent_id,id)` → census binding tuple; validation
uses the intact `line_id` → unique census `binding.id`, then that same census
object's parent/ID/hash. All mapped recorded hashes must agree with the measured
anchor hash. No ID splitting or path reconstruction occurs.

Harvest alone overrides the metadata source with the pinned local
`hf_archive/harvest-20261025/data/*/*.parquet` shards (36 shards / 497,556 rows
in the retained inventory), revision `103c6dcd1e5dac6d72a1048462cd5b1864600cca`.
Only this source projects `image.bytes`; `image.path` and `file_name` are
locators and are never opened as files. Every byte payload is hashed. If its
recorded image hash is absent, `hashes_match` stays zero for that row and
`custody_basis=hf_pin_and_row_byte_sha256`, `recorded_hash_absent=true`, the HF pin
and measured row SHA256 explicitly record the weaker custody. The row retains
`no_recorded_hash`, rather than claiming recorded-hash equality. The retained complete HF parquet metadata inventory records non-null
`crop_sha256` in all 497,556 rows; embedded-byte equality still needs this
rerun. The missing-hash branch is qualified by a fixture, not claimed as an
observed production gap.

`original_crops.json` reports complete scanned/mapped/verified counts per
population, separate native source counters, pending population names,
`distinct_files_hashed`, and flagged pin/hash custody counts. `recorded_path`
counts usable recorded paths; a relative string with no evidenced root counts
only as `recorded_locator`. Embedded bytes count separately. Durable per-row
hashes, exact mapping keys and custody are in `keys.sqlite`; image bytes are never written.
Historical S4p report bytes are preserved; its contradictory harvest/seal04
locator counters are corrected only in the current spec coverage.

This command was prepared, not submitted locally. The complete production
census count remains unmeasured until its output says `counts_complete=true`;
the retained 448,005 source rows / 446,464 indexed census observations are partial.


## REL0-S4r: content-addressed original-crop index (29 October 2026)

From the deployed checkout root, using a fresh output directory:

```bash
sbatch scripts/release_v0_dataset/resolve.sbatch /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/probes/original-crops-s4r-001 original_crops
```

This prepares the four evidenced `crop_roots` once, reusing the same measured
file cache in all readers. It selects seal04's recorded hashes/paths relative
to each panel directory and hashes `validation_originals` before joining exact
`admitted_all_v2.id = prepared_validation.line_id`. No Mac-era locator is
rewritten. Inspect `content_index` (including every root's completion/errors),
per-population `custody_via_index`, census `previous_no_recorded_path` and
`previous_no_recorded_path_resolved_via_index`, and `validation_originals` join
field counts. Both `keys.sqlite` and `crop-files.sqlite` retain the audit trail.
`counts_complete=true` requires complete root/source scans and population
coverage. The coordinator must supply the full report, its SHA256 and input
hashes before replacing the pending spec measurements. The supplied S4q counts
are retained as coordinator-reported baseline evidence, separately from the
older SHA-bound S4p coverage. This command was prepared and was not submitted.

## REL0-S4t original export and acceptance

The release environment dependencies are declared in `requirements.txt` in this
directory (`pyarrow`, `jsonschema`, `ijson`, Pillow). Use the existing qualified
CPU environment; no installer or remote operation was run by S4t. Its read-only
preflight is:

```bash
python3 -B -c 'import pyarrow, jsonschema, ijson, PIL; from jsonschema import Draft202012Validator'
```

Use fresh freeze/out/work paths with S4t; old locks omit root-index/payload pins.
Freeze hashes the harvest override parquets as separate original payload inputs
and measures every declared crop root. Builder and acceptor independently
rebuild the root count/digest. Harvest native rows join payload rows by exact
tuple and recorded hash; a missing/duplicate tuple or mismatched hash fails.
`original_custody` names recorded_path, index or embedded_original on each public
row. Original bytes are hashed again when read for embedding.

Full acceptance requires published original image counts, in overlapping source
population units: harvest 497556, s1 364871, v4 167946, old 364173, seal04 2690,
validation 13088, census 483078 of 592466. Smoke replays the selected observations
and checks their actual public hashes/counts; it remains SELF_CHECK_ONLY.
The acceptor needs the external frozen lock and source roots/payload files to
perform this replay. Fixtures do not certify the unbuilt production release.

Local verification (no root test conftest or predictor build required):

```bash
python3 -B -m pytest -q tests/release_v0_dataset \
  --confcutdir=tests/release_v0_dataset -p no:cacheprovider \
  --basetemp=/private/tmp/rel0-s4t-basetemp \
  --junitxml=tests/release_v0_dataset/REL0_S4t_TESTS.xml
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --validate-spec scripts/release_v0_dataset/specs/source-spec-001.json
```

Remove that task basetemp after recording results. No SSH/network/git or
production transform is part of this local verification.

## REL0-S4u prepared payload custody and freeze-index reuse (29 October 2026)

`prepared()` always reads factory bytes as `trainer_image`. Its optional
`training_image_sha256` checks only those bytes; enriched `crop_sha256` and
`crop_path` belong to original custody. A missing factory payload cannot fall
back to the original path. All prepared pools share this route, including
validation, harvest_dev/test, seal04_dev/test, non_parliament, parliament and
synthetic. Original hash mismatch diagnostics include expected/actual SHA256,
custody kind and the complete path or parquet locator of the bytes.

S4t smoke **did** re-hash every declared crop file at Builder construction,
including on resume. New freezes also retain `<lock-name>.crop-index.sqlite`
next to the lock and pin its bytes/SHA256 in `crop_index_cache`. Preserve this
sidecar with the frozen lock. Builder checks that pin, the declared root
count/digest, and a full metadata snapshot (absolute paths, sizes, nanosecond
mtime/ctime, device/inode). Matching snapshots reuse the pinned index without
reading crop bytes; changed snapshots trigger a full byte rebuild and frozen
root digest comparison. Selected original payloads are always re-hashed on
read. `BUILD_RECEIPT.json.crop_index_reused` records the chosen path. Independent
acceptance still rebuilds the root index from bytes and does not trust this
cache. Root reports retain identical source counts/digests in either mode.

An existing S4t lock has no retained index: it remains usable with the payload
repair, but still re-hashes all roots. A fresh freeze is needed for reuse. No
Clariden timing or production rerun is claimed by the offline tests.

```bash
python3 -B -m pytest -q tests/release_v0_dataset \
  --confcutdir=tests/release_v0_dataset -p no:cacheprovider \
  --basetemp=/private/tmp/rel0-s4u-basetemp \
  --junitxml=tests/release_v0_dataset/REL0_S4u_TESTS.xml
python3 -B scripts/release_v0_dataset/build_dataset.py \
  --validate-spec scripts/release_v0_dataset/specs/source-spec-001.json
```

Remove this task's basetemp after recording results.

## HFD-P2a — layered builder (supersedes the historical export/resume paragraphs)

Coordinator commands and outstanding production gates:
`docs/programme_20261028/RELEASE_v0/HF_DATASETS/p2/HANDOFF.md`.
Use a **fresh** work directory, never `full-001.work`. The builder emits
`tables/lines`, `images/{crops,pages}`, versioned labels, current labels/features,
synthetic metadata and all inherited relations. It never emits real or synthetic
train byte views. Binding rev 2 H02 retains identified synthetic val/reserved views.
The A1 `--frozen-manifest` supplies exact existing paths/configs/bytes/SHAs and maps
each file to its prepared `pool` and `source_shard`; no shard name is guessed.

JSONL ingestion and original-payload imports commit every **50,000 records**, using
WAL, synchronous=NORMAL, 128 MiB SQLite cache and a 64 MiB WAL checkpoint target.
The durable cursor, rows, aliases, witnesses and payloads commit together. JSONL
resumes by byte seek; Parquet resumes at a row-group/ordinal boundary. Uncommitted
records roll back. Batch insertion was chosen to retain the established typed
SQLite joins without introducing a second census conversion/custody representation.
It removes repeated census parsing after a timeout; disk-speed qualification is
still a measured gate, not a claim from fixture tests. One SQLite writer, one Arrow
thread and OMP=1 are used within the existing 8-CPU/32-GiB starting allocation.

Progress goes to stderr at stage entry/exit and at most 60-second intervals,
including long SQL/hash work. Lines contain rows, bytes, rate and ETA (null when
no defensible total exists). Public receipts exclude elapsed timings so interrupted
and clean trees can be byte-identical; private `work/STAGES.json` retains timings.
CDC is enabled on every writer; the closed-file cap is enforced after writing.
Image shard first/last hashes and exact closed file identities are in MANIFEST.

`--measure --out FRESH_MEASURE_DIR` samples real approximately 2% prefixes of every
large input file, executes index/hash/ingest/derive/export/evidence/summary/manifest
and independent-readback phases, and writes MEASURE.json with per-stage projections,
peak RSS and scratch/index envelope. Full crop-index cost is measured once and not
multiplied by 50. A failed or unmeasured phase yields unknown full runtime and exit 2.
P1 recovery itself is outside P2a: supplying adapter locks to this rehearsal marks
that dependency-closure/feature cost unqualified rather than hiding it in an ETA.
Qualify raw integration separately before claiming the complete <=12 h target.

P1 plug-in lock: `label_variant_adapters:[{name,producer_version,files:[{path,bytes,
sha256}]}]`, `raw_text_responses:{wave:boolean}`. Each parquet row carries row_key,
label_variant,text,text_sha256,before_sha256,route_status,reason. For recovered raw
values also carry source_locator/source_sha256 (response/anchors) and
row_source_locator equal to the native row locator; the recorded raw hash must
match. P1 owns the proof of anchor/producer identity and recorded-edit composition.
No tool inference or sequential correction replay is implemented by this adapter.
Use the augmented candidate `manifests/INPUT_LOCK.json` for independent source
acceptance when CLI adapter/frozen overlays were supplied.

Foreground coordinator tools use only environment HF_TOKEN, disable implicit token
lookup and set HF_TOKEN_PATH=/dev/null. `upload_staging.py C --frozen-root A1_DOWNLOAD`
batches only to the designated private staging repository. `seal_candidate.py C`
seals/reverifies C. `drill_update.py C corrections.parquet --scratch FRESH_COPY_DIR
--parent-commit FULL_SHA --generation v0.n` uses ten real edits, commits only to
`drill`, verifies current joins and unchanged immutable oids, and repeats a table
rewrite. Attach both client/Xet transmitted-byte reports; local operation bytes are
not transport savings. `promote_candidate.py C --parent-commit FULL_PUBLIC_HEAD
--frozen-manifest A1_FROZEN.json` makes one CAS commit, verifies every resulting
remote path/size/LFS SHA256 (non-LFS files by byte SHA), and rejects unexpected paths.
Full-download byte/semantic acceptance runs separately in a credential-free CPU
allocation; remote object verification is not substituted for that gate.

### P2l validation modes and complete staging download

Build-time `--independent-readback` explicitly uses `external-cache`: C omits the
264 frozen trainer shards and five retained metadata files. A standalone build
check must say `--validation-mode external-cache`. CP-release acceptance defaults
to `complete-download`; use it explicitly in receipts. The reviewed retained and
replacement inventory is `p2/RELEASE_TREE_P2l.md`; no public path is deleted.
The existing `locks-final-p2k` locks need no regeneration. Changed code requires
fresh build/work/readback directories; see `p2/HANDOFF_P2l.md` for prepared deploy
and debug-chain commands. No deployment or launch is implied by these commands.

```sh
# Coordinator foreground upload, after sealing C and existing checkpoint gates.
# HF_TOKEN is injected into the environment, never argv or a saved credential.
python -B scripts/release_v0_dataset/upload_staging.py "$B/full-p2l" \
  --frozen-root "$R/hfd/p1-pre/a1-scratch/hub/datasets--fffoivos--greek-ocr-lines/snapshots/859fa9873d5ed23e49f01ae7628be6ef3d9c4e50"
```

The uploader resolves snapshot links only into this repository cache's blobs and
checks every frozen SHA. It downloads only the five retained metadata objects at
the public pin and verifies their reviewed SHAs before creating a staging commit.
Its output reports the final staging commit; record the full SHA in STAGING_SHA.
Materialise a fresh complete download on a CPU allocation, outside C and work:

```python
import os
from pathlib import Path
import shutil
from huggingface_hub import snapshot_download
snapshot = snapshot_download(repo_id='fffoivos/greek-ocr-lines-build', repo_type='dataset',
    revision=os.environ['STAGING_SHA'], token=os.environ['HF_TOKEN'],
    cache_dir=os.environ['DOWNLOAD_CACHE'])
# DOWNLOAD_ROOT must be fresh. Dereference the HF cache links; cache bookkeeping
# stays outside the dataset tree. No allow_patterns/ignore_patterns subset.
shutil.copytree(snapshot, Path(os.environ['DOWNLOAD_ROOT']), symlinks=False)
```

```sh
python -B scripts/release_v0_dataset/accept_dataset.py "$DOWNLOAD_ROOT" \
  --validation-mode complete-download \
  --input-lock "$B/full-p2l/manifests/INPUT_LOCK.json" \
  --scratch "$B/cp-release-p2l.readback" --deadline-seconds 4800 \
  --report "$B/CP_RELEASE_P2l.json"
# Subsequent CPU windows use the identical command plus --resume. A PAUSED exit
# is not acceptance: require the final report status PASS and mode complete-download.
```

Complete mode reads frozen files from DOWNLOAD_ROOT for SHA, ordered A1 mapping,
trainer membership, images and config loading, even if the lock retains an old
public_snapshot_root. Independent source replay still requires the pinned input
files and SHA-bound A1 receipt. Revision-pinned viewer checks, sealed-C drill and
client/Xet transmission receipts are separate CP-release evidence.
