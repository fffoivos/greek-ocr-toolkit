# HF step 2 — Clariden CPU builder plan, 23 October 2026

**Plan and offline one-book mock ready; production build remains on hold.**
No download, upload, repository creation, cluster job or submission ran. The
production source adapters are future work. Before a full build, the Mac handoff
must exist at an immutable HF commit, pass Clariden byte readback and the three
representative joins, then supply a measured bounded CPU batch. The lexicon book
is train with harvest_protection=true under the explicit 00:38 ruling; the
canonical book registry is publishable with zero unresolved conflicts.

## Immutable inputs

Use `/capstor/scratch/cscs/fffoivos/greek-ocr-data/line_registry/hf/v4/` with
separate `download/`, `inputs/<lock-sha>/`, `build/<binding>/`, `upload/` and
`receipts/`. A production INPUT_LOCK.json must contain exact paths, sizes,
SHA256s, selected row/key counts, code/runtime/schema/feature versions and the
HF commit. Historical absolute paths remain provenance, not download instructions.

| Input | Source and selection |
| --- | --- |
| Mac package | `/Users/foivoskarounos-zamparloukos/Projects/hf-staging/greek-ocr-lines/`; mac-artifacts.json SHA `8f2c43ff8d3d102850e7200529d0dab2c4408d490e4df21b0adc40bced0c5548`. Historical measured total 40,711,310,115 B / 110 files. Current manifest hash and presence of 108 listed artifacts checked; no new full payload rehash. The old temporary package was relocated outside this run. |
| Book policy | This worktree book_registry/{book_registry.parquet,row_instruments.parquet,BUILD_RECEIPT.json,SHA256SUMS,HOLDOUT_INVESTIGATION.json}. Consume the pinned RUNNER5 artifact; no runtime dependency on a changing sibling checkout. |
| Census | `W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d/`; immutable decisions/admission exports, generation/run binding and publication receipt. Exact export paths/hashes come from SOURCE_MANIFEST.json and must be read back in preflight. Never substitute the mutable live ledger. |
| Parents/splits | `W/collection_v2/import_real_v2_{train,dev,test}.jsonl`, frozen W1/W2 parent snapshots, raw labels/IDs and split2 editions, as pinned in the source and registry receipts. |
| v4/corrections | `W/release_v4/rel4_c06_full_01/`: 167,946 admission rows, stream SHA `dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75`. Preserve actual VERSIONS.v4.json, SF7/RU1/N1 inputs and codec/mix recipes; 904 SF7 records alone do not describe all corrected trainer labels. |
| Source crops | `W/collection_w{1,2}_originals/`, CROPS4C `W/crops4_attempts/crops4_c06_full_01/` manifest/checksums, plus v2 crop roots. Availability requires keyed inventory; missing bytes are never recreated under old hashes. |
| Trainer payloads | `J/union_{0,1}/train/shard-00000.parquet`: 364,173 real rows / 7.486898 GB. Preserve existing image_png, labels/codec and source-to-factory IDs. |
| Synthetic | `J/control_synthetic_7`: 51 Parquets / 203,693 rows / 6,225,008,494 B. Archive existing payloads and retained recipe/font/source/build manifests; unknown historical fields stay explicit. No rendering. |
| References | `W/benchmark_0.2/seal04`, `J/benchmark_0_2`; the selected v2-codec common_intersection/full_coverage JSONs and reserved shards; `J/validation_v21/mix.json` val shards. Preserve raw/corrected/full/common roles and diagnostic_only status. |

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.
`J=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code/out/e4/wave2/job02`.
SOURCE_MANIFEST.json SHA remains
`f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578`:
a pinned selection, not a current full-byte verification. Full inventory and
historical measured sizes remain in HF_REPO_SPEC.md / STAGING_PLAN.md. Pin
Python/PyArrow/Unicode Scripts.txt/codec, code hashes, label versions and crop
variant definitions too. The one-book live-ledger probe is diagnostic evidence,
not a substitute for immutable full-population exports.

## Foreground authentication, then credential-free CPU

1. After authorized Mac publication, select an exact 40-hex staging-v4 commit.
   A separate foreground SSH stdin launcher passes the token into the downloader's
   process memory. Only the Mac launch command uses
   `HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)"`.
   Token values never enter SSH argv, scheduler exports, scripts, files or logs.
   No persistent login. The downloader ends before any CPU job starts. The
   reviewed launcher is future work: the assignment and downloader command must
   share one invocation, never an exported login-shell variable.
2. Download the pinned manifest and selected objects into download/. Verify exact
   paths, bytes and SHA256. Fetch raw response/page objects needed for the W1,
   W2 and legacy witnesses; repeat the three complete joins on Clariden and save
   keyed outcomes. Existing Mac-only joins do not close this handoff requirement.
3. Write the credential-free INPUT_LOCK.json: HF repo/commit, manifest hash,
   local paths and readback extent. Atomically admit verified inputs. Exit the
   foreground staging process; never serialize its environment into a receipt.
4. Launch the later CPU worker separately. Reject HF_TOKEN,
   HUGGING_FACE_HUB_TOKEN, HUGGINGFACEHUB_API_TOKEN and HUGGINGFACE_API_KEY;
   import no Hub client, make no network calls and set Hub/dataset offline flags.
   No token goes to sbatch or --export. Upload is a third, later foreground
   authenticated process after complete output review.

No SSH/download command is run here. NEXT_SUBMIT.sh remains the separately
reviewed Phase 1 command handoff; this step does not authorize its execution.

## CPU dataflow

One CPU job streams immutable JSONL and Parquet batches using disk-backed
identity indexes. Do not load the entire 11 GB decision export or payload pool
into Python memory. The production source adapters and query CLI remain to
implement; the execution mock below tests the planned boundary only.

1. **Inventory every census key.** Preserve `(parent_id,row_id)` for ADMIT/HOLD/
   DROP, decision JSON, reasons/routes, raw/corrected labels, generation and run
   binding. Join immutable parents and Mac page aliases. Missing or ambiguous
   joins are keyed diagnostic records; SHAs never merge books or splits.
2. **Pages and boxes.** Resolve canonical book IDs/splits with registry SHA,
   source aliases/provenance and harvest_protection. Retain failed/excluded
   pages, every raw box, distinct harvest envelopes, contributor/anchor relations
   and segmenter zero/error/not_run outcomes. Keep native and Google frames
   distinct. The 194 known dimension mismatches remain unresolved; no guessed
   transform. Native position/comparison fields remain null until qualified;
   provider-frame positions require an explicit frame field. Retain effective
   detectedLanguages and line/page scope: the mock caught this fallback.
3. **Rows and labels.** Preserve original IDs and independent raw/corrected/
   overlay/trainer label versions. Exact line-list joins produce lqb_row and
   release_excluded_row with list name/hash; never flag a whole book from one
   line. Historical actual release membership survives later instrumentation.
   Newly selected training lists cannot include conflict_hold_out books.
4. **Crops and trainer images.** Resolve expected source-crop hashes, measure
   available bytes/dimensions, record missing custody explicitly. Archive exact
   source bytes in TAR with member offsets/hashes. Stream-copy trainer image_png
   and every original label/codec/operation/provenance field, retaining original
   shard and row ordinal. Source crop and transformed trainer hashes differ.
   Read back embedded payload hashes, labels and mappings, not just file hashes.
5. **Features.** Compute raw/census-corrected variants using the spec's pinned
   Unicode/codec/script rules and scoped confidence/geometry. Keep producer
   features separately. Independently recompute all fields on 1,000 pinned random
   rows, recording script/status/changed-label coverage. Same-helper replay in
   this mock does not satisfy independent production semantic verification.
6. **Synthetic/references.** Archive existing images/labels and all retained
   provenance. Missing font hashes/seed/text locators stay null with unknown
   reasons. Dataset reconstruction is supported; deterministic regeneration is
   not claimed. Synthetic factory identities have null physical page/box links.
   References retain full/common/raw/corrected membership and diagnostic status.
   Dedup identical image storage by hash while retaining each observation and
   original ordinal; do not erase membership or provenance during re-sharding.
7. **Seal and export.** Produce Parquet datasets, payload indexes, outcome/
   membership/label relations and derived SQLite. The later CLI exports existing
   row IDs with crop/label variant/hash/release, or page hashes/polygons/frame/run
   IDs for recropping; query/export does not create admissions or transfer Google
   labels to toolkit boxes solely through overlap.

## Resume, shards and acceptance

A page batch binds its sorted page keys, input-lock, code/schema, feature and
registry hashes. Write an incomplete directory, close outputs, read back their
hashes and keys, then atomically write DONE. Resume rehashes every completed
artifact before reuse; changed bindings use a new build root. Discard only the
builder-owned unfinished batch. Payload stream batches additionally bind source
shard and ordinal ranges. Publish COMPLETE/upload manifests last, after global
reconciliation. An interrupted build cannot appear complete.

Target shards about 512 MB; every closed file <=1,000,000,000 bytes. Split by
whole records after measuring actual size; never change embedded bytes/labels.
Report an individual oversized record. If SQLite exceeds the cap, transport
ordered byte chunks with individual hashes/sizes and full database SHA; consumers
reassemble and verify full SHA and integrity_check. Do not upload the oversized
singleton as well.

Production checks reconcile every census key/status/reason, 167,946 v4 keys,
all correction versions and the distinct actual 364,173-row trainer population.
Keep the reported seven-row census/trainer difference keyed and explained.
Every used row must join exactly one primary box/page/book; unused boxes and
missing crops stay visible. Verify PK/FK and feature coverage, exact payload/
label preservation, independent 1,000-row features, clean/resume equality,
row/box export round trips and full path/byte/hash manifests. One unresolved
book prevents a globally reconciled registry claim; never silently assign it.

## Costs and later allocation

No full allocation time is qualified. A later authorized bounded Clariden CPU
batch must measure per-stage wall time, rows/bytes, peak RSS and scratch,
including re-sharding and independent readback. Compute
`T = sum(remaining_work_i / measured_rate_i) + measured_fixed_costs`, report
variation, then select the allocation with the coordinator. Initial planning
resources are 8 CPUs / 32 GiB CPU-only, revised from that measurement. No job
configuration or scheduler submission occurs now; Mac mock rates are not
Clariden performance qualification.

The v4 envelope remains 75–95 GB, with 120 GB output staging plus 20 GB scratch,
excluding resident sources. Complete legacy crop totals and final dedup remain
unknown. Mac work in this step is only the small one-book metadata probe/mock.

## Offline one-book execution mock

Code: scripts/line_registry/{prepare_one_book_mock.py,mock_clariden_builder.py,
test_mock_clariden_builder.py}. Root:
`/private/tmp/runner4-hf-builder-mock-20261023/` (temporary, outside Git).
The real inputs contain 40 harvested page observations, 1,429 census rows,
2,858 raw/derived boxes, decisions/labels and canonical split fields. The mock
recomputes both text feature variants and checks 1,000 rows / 2,000 variants
using the same helper. Eight deterministic five-page batches model restart.

This book's source crops, trainer PNGs, synthetic and reference payloads are
not on the Mac. Those lanes use valid one-pixel PNG fixtures, all marked MOCK /
mock_fixture_not_training_data: one source crop, one trainer image, one synthetic
image and four raw/corrected seal04/v2-view fixtures. They exercise exact copy,
labels, unknown historical fields and shards; they do not certify actual remote
custody or provenance. Production mode is refused; publishable is always false.

```sh
python3 scripts/line_registry/prepare_one_book_mock.py --book-root /private/tmp/runner4-book-registry-dryrun-20261023 --output /private/tmp/runner4-hf-builder-mock-20261023/inputs
python3 scripts/line_registry/mock_clariden_builder.py --config /private/tmp/runner4-hf-builder-mock-20261023/inputs/INPUTS.json --output /private/tmp/runner4-hf-builder-mock-20261023/run2/resumed --stop-after-batches 2
python3 scripts/line_registry/mock_clariden_builder.py --config /private/tmp/runner4-hf-builder-mock-20261023/inputs/INPUTS.json --output /private/tmp/runner4-hf-builder-mock-20261023/run2/resumed
python3 scripts/line_registry/mock_clariden_builder.py --config /private/tmp/runner4-hf-builder-mock-20261023/inputs/INPUTS.json --output /private/tmp/runner4-hf-builder-mock-20261023/run2/clean
python3 -m unittest discover -s scripts/line_registry -p test_mock_clariden_builder.py -v
```

Tests force small caps to exercise multi-shard output and multi-part SQLite,
reject credentials, broken joins and source/output tampering, and compare clean/
resumed artifact manifests byte-for-byte. The receipt at
[evidence/HF_BUILDER_MOCK_RECEIPT.json](evidence/HF_BUILDER_MOCK_RECEIPT.json)
binds results, costs and code/input/output hashes. Production native-source
adapters, global joins, actual payload verification, independent features and
Clariden sizing remain future work. No repository or remote job was created.

Measured on this Mac: 2,008,789 B pinned inputs; 39 output artifacts /
14,267,318 B; clean run 1.34 s, resume 1.32 s with two batches reused and six
built. Both complete-manifest SHA256s are
`98915a599c52d7d62b40a28a784a2d3f190263c4ff08b8d26c2a88ec3b52e2a4`.
These figures include only the mock scope; no Clariden runtime estimate follows.
