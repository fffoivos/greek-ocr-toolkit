# E2 implementation and node handoff — 8 October 2026

Offline code and fixtures only. No training, networking, GPU execution or Git
mutation is part of this handoff. O4c files are outside this change. Current
`train/train.py` is unchanged. Seven stages are implemented:
`retrain → bakeoff → vouli → warmstart-parity → mixes → runs → readout`.
`E2_fix2_HANDOFF.json` contains the normalization/reader/backend fix inventory, verification counts and limitations.

## Parameter table versus E1

| Parameter | Certified E1 run4 | E2 |
|---|---|---|
| Teacher re-executions | f50_s0 / f75_s0, checkpoints lost when pod terminated | Same original run manifests and E1 runner; separate `out/e2/retrain/runs`; seed 0; `data_provenance.json` and explicit re-execution receipts |
| Training recipe | v5, target 200,000; realized 203,693; disclosed allow-deficit | Reuse unchanged bound E1 v5 shards; retain the deficit disclosure |
| Sweep fraction of real supervision | 0, .25, .5, .75, 1 | .25 and .5; real = E1 + admitted Vouli, weighted within real by TRAIN pool size |
| Initialization | compact/NFD scratch | compact scratch, R01 donor, R03 donor; distinct architecture IDs `e2_r01`, `e2_r03` |
| Strip height | 48 | 48; all 12 proposed 64px arms explicitly deferred |
| Seeds | 0, 1, 2 | 0, 1; 12 enabled arms, 24 preset arms including deferred height 64 |
| Exposure / updates | 19,657 rows/epoch, 8 epochs, bs64, accum1, 308 updates/epoch | Same cap and packed bucket tails: 2,464 planned updates/arm |
| Optimizer | AdamW lr1e-4, wd.05; exclude norm/bias decay; no cycle momentum | Same, fresh optimizer/scheduler for donors |
| Selection | mixture DEV CER, patience6 | Same; TEST and transfer never select checkpoints |
| Runtime | CUDA A100, BF16, workers6, pinned memory | Same runner flags; actual node runtime bound in receipts |
| Instruments | real TEST, v7 rendered held-out, legacy transfer | Same real TEST; new document-disjoint Vouli polytonic TEST; rebuilt v8 rendered held-out; unchanged, disclosed legacy transfer |

E1's receipt binds trainer SHA `9508594a1747504759dff819542df2d2e72a7adb09597feb81ceb356f828deda`
at retained revision `2e3cf6f`. The current frozen trainer is SHA
`7c20b9a316d70a247e1aea6166486e03403a3fa7ab66c1a427f2a1e1d4756fe1`.
The difference is checkpoint hash-v2/storage-independence certification work.
`e2_retrain.code_parity` compares the scratch loop AST (excluding only its nested
checkpoint writer), parser, seed setup, runtime imports and optimizer grouping,
and demands byte equality for data/model/heads/mix/CER/evaluator dependencies.
It records both hashes. Historical code input receipts are checked against that
retained Git revision; data, recipes, fonts, factory executable and all factory
artifacts remain subject to their original byte gates. This is the same scientific
re-execution with the current certified checkpoint writer, **not** a claim of
byte-identical historical source or GPU checkpoints. No old weight hash is
represented as a recoverable weight artifact.

## Node preparation and exact commands

These commands are instructions for the node operator; none were executed here.
Stage the bound E1 dataset artifacts at their original absolute paths first.
E1 run manifests are preserved byte-for-byte and still refer to
`/home/ubuntu/work/greek-page-ocr/out/e1_run4/...`. Missing or mismatched shards,
source inputs, factory executable or recipes stop the job. Do not regenerate
manifests to hide missing custody. The E1 checkpoints themselves are not required.

Also stage the native dataset releases, reviewed licences/GT/book identities,
Kalchas checkout at `7a0f9fddcfb14276bc48850abcc6706170583eb9`, CLLG assets,
and the official paired donor configs/weights/native inference checkouts.
Dependencies must already be installed offline: E1 Torch/NumPy/Pillow/PyArrow,
PDFium/OpenCV, safetensors, Transformers with PP-OCRv5-mobile/v6-small support,
PyYAML, Kraken 7.1, the complete Kalchas runtime dependencies listed below,
native OpenOCR dependencies, and CPU Paddle for R01 parity.
No tool in E2 downloads or installs assets. The prototype R01 **default**
Transformers config is not a substitute for the official recognition config.

The prior CP-E2code fix set v8's mixed-script/polytonic marginal to .10/.35
and recorded it in `docs/data_contracts.md`. Those recipe bytes and the 137-text
exclusion are committed on main. **E2fix2 changes no recipe**; the unchanged
provenance gate still requires committed recipe bytes. This job leaves code edits
and never writes `.git`.

```bash
cd /home/ubuntu/work/greek-page-ocr
export PYTHON=/opt/e2-venv/bin/python
export GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
# After staging/reviewing actual payloads, adapt the example's absolute paths.
cp bench/e2_config.example.json /opt/e2-assets/e2_config.json
# Edit the copied config: actual immutable revisions and reviewed native preprocessing.
# Preserve factory/target/release/linefactory at its E1-receipted bytes.
# Cargo puts the new release in release-e2/release/; publish it to the separate
# importer path configured by vouli.factory. Never rebuild the E1 target.
export CARGO_TARGET_DIR="$PWD/factory/target/release-e2"
cargo build --offline --release --manifest-path factory/Cargo.toml
install -m 755 "$CARGO_TARGET_DIR/release/linefactory" "$CARGO_TARGET_DIR/linefactory"
"$PYTHON" - <<'PY'
from pathlib import Path
from bench.e1_common import read_json, sha256
old = Path('factory/target/release/linefactory').resolve()
assert sha256(old) == read_json('out/e1_run4/build_info.json')['inputs'][str(old)]
new = Path('factory/target/release-e2/linefactory').resolve()
assert old != new
print({'E1_factory_sha256': sha256(old), 'vouli_factory_sha256': sha256(new)})
PY
# The example config explicitly sets vouli.factory to this new importer;
# the global E2 binding hashes BOTH executables and rejects a shared path.

# Build the reviewed GOLD-source exclusion partition via existing O4b machinery.
"$PYTHON" -m bench.o4b_partition \
  --o5-info out/o5/build_info.json \
  --c1 data/sources/e2_c1_documents.json \
  --document-map data/sources/e2_canonical_works.json \
  --reviewed --out out/o4b/e2_gold_partition.json

# Full foreground job, stages have per-stage logs and bound done/failed markers.
PYTHON="$PYTHON" bash bench/e2_node.sh \
  --e1 out/e1_run4 --out out/e2 --config /opt/e2-assets/e2_config.json
# Optional persistent node launch; same config/output identity and advisory lock.
PYTHON="$PYTHON" bash bench/e2_node.sh --launch \
  --e1 out/e1_run4 --out out/e2 --config /opt/e2-assets/e2_config.json
# Poll logs/markers; rerun the same foreground command for verified completed-stage reuse.
```

To run a single stage, supply the same arguments and `--stage retrain` (or any of
the other six names). Every earlier marker and all of its outputs/external inputs
are revalidated. A failed training attempt is retained and can resume only through
E1's existing full-state gate. O4b's extraction/import tools require fresh outputs:
a failed preparation/adjudication/parity stage may require a new E2 output root;
retain the failed attempt, and update the bake-off checkpoint paths in the config
when changing roots. No stage silently cleans, relabels or promotes partial data.

Standalone teacher retrain and Vouli entry points:

```bash
PYTHON="$PYTHON" bash bench/e2_retrain.sh --e1 out/e1_run4 --out out/e2/retrain
# Standalone inputs use the corresponding subsections of the node config.
"$PYTHON" -c 'import json; p=json.load(open("/opt/e2-assets/e2_config.json")); json.dump(p["bakeoff"],open("/opt/e2-assets/bakeoff.json","w")); json.dump(p["vouli"],open("/opt/e2-assets/vouli.json","w"))'
"$PYTHON" -m bench.e2_bakeoff --e1 out/e1_run4 \
  --config /opt/e2-assets/bakeoff.json --out out/e2/bakeoff
PYTHON="$PYTHON" bash bench/e2_vouli.sh --e1 out/e1_run4 \
  --config /opt/e2-assets/vouli.json --bakeoff out/e2/bakeoff --out out/e2
# Conversion alone never confers parity qualification.
"$PYTHON" -m bench.e2_warmstart --donor R01 \
  --checkpoint /opt/e2-assets/R01/model.safetensors --config /opt/e2-assets/R01/config.json \
  --revision ACTUAL_IMMUTABLE_HF_REVISION --out out/e2/warmstart/R01
"$PYTHON" -m bench.e2_warmstart --donor R03 \
  --checkpoint /opt/e2-assets/R03/model.pth --config /opt/e2-assets/R03/config.yml \
  --revision ACTUAL_RELEASE_SHA256 --out out/e2/warmstart/R03
```

Local verification commands (no training):

```bash
C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory .venv/bin/python -m pytest -q \
  bench/tests/test_e2.py bench/tests/test_o4b.py bench/tests/test_e1.py
PYTHON=.venv/bin/python bash bench/e2_node.sh --dry-run --out /private/tmp/e2-dry
```

A dry-run writes seven explicit `executed:false` records and
`training_executed:false`; it does not manufacture teachers, data, parity or scores.

## Bake-off and teacher contracts

Polyton-DB enters through `bench.o4b_import_datasets.convert`. The manifest must
identify actual release files, manually transcribed gold evidence, scan/transcription
rights and canonical works. A release with no line-image/container supply triggers
the explicit GRPOLY-DB **MachinePrinted-B** fallback. Invalid rights, missing
identity, malformed annotations or a gold quota shortfall fail; they do not trigger
fallback or duplication. Exactly 300 unique admitted polytonic gold lines are
selected deterministically by line ID. All E1 synthetic-pool/real TRAIN/DEV text and the
137 shared texts are excluded from gold selection. The 300 unique v7 polytonic
control lines exclude that inventory (reserved corpus membership is not exposure) and gold texts; control text is also excluded
from the v8 sweep instrument.

Each candidate reports strict NFD CER, per-mark TP/FP/FN/precision/recall/F1,
Greek→Latin homoglyph substitution counts, missing lines, and warmed CPU wall
ms/line including preprocessing/decode. Remote services have CPU latency NA.
Saved readings retain their decoder codepoints. The E2 bake-off canonically
normalizes **both** gold and hypotheses to NFD before CER and mark alignment;
whitespace is unchanged. Equal-ccc mark swaps remain errors. This E2 boundary
adaptation leaves `train/cer.py`, `train/eval_cer.py` and `bench/e1_readout.py`
unchanged: those evaluate raw codec atoms, not serving NFC strings. Layer twins must be
explicitly present as `layer_text` on gold records; absence is NA, never fabricated
by aligning unpaired texts. The layer never enters the top-two selection.
O4b carries supplied twins through TSV (`columns.layer_text`, default `layer_text`),
PAGE's explicitly selected `text_equiv_index`/`layer_text_equiv_index`, XML
`layer_text` attribute or `LayerText` child, or an explicit page manifest's
line-ID → `layer_text` map. Arrow uses `layer_text_column` (default `layer_text`),
LMDB `layer_text_prefix` (default `layer_text-`), and pairs an opt-in
`layer_text_suffix`. Admission preserves the twin separately from gold truth.

**Preset selection:** pooled micro mark F1 on all 300 real-gold crops, descending;
ties by strict CER, warmed wall latency, then ID. Require complete real-gold predictions.
Require at least two fully scored, overlap-qualified **non-E1** candidates before
selecting exactly two enabled image readers; the layer and control never select.
An E1-only top-ranked pair also refuses selection instead of silently substituting
a different ranking. No teacher fallback is permitted.
Services can win only with `--service`, credentials and a supplied adapter; the same
flag is required when reloading a service teacher for Vouli adjudication. Local CPU
and remote wall latency have distinct reporting fields. Exact provider weights and
future API deployment behavior are not established by these hook receipts.
`teachers.json` records actual loaded byte bindings and rule; fewer than two
fully scored non-E1 candidates leaves `ready:false`, an explicit reason and an
empty teacher list, and fails the stage. Vouli checks readiness, external candidate
coverage, bake-off digest and the reader-parity receipt **before** creating outputs
or opening any PDF. Historical E1-only teacher files are refused.
Kalchas uses its released native `.ocr([PIL grayscale])`, a pinned clean checkout,
and verifies loaded tensors against the selected released checkpoint. E1 readers
also verify checkpoint state SHA and compare the actually loaded model tensors,
including any safetensors sibling, to the re-execution's full-state checkpoint;
the actual weight-file hash is in `teachers.json`. Native
network acquisition is refused. No custom architecture substitutes for Kalchas.

CLLG Zenodo 22232579 is **a teacher only**, not 794,564 locally available corpus
pairs. Its publisher README front-matter establishes `software_name: kraken`,
`software_hints: kraken 7.1`, recognition, scripts Grek+Latn, CER 4.54,
CC-BY-4.0 and base model Zenodo 10592716. A cached publisher README was read
locally for this fix; the recognition weights and Kraken are absent in this venv.
The filename `ppocr_v6_tau090.safetensors` does not establish a Transformers model.
The loader retains publisher MD5 checks `2b59c47ba44a58ca7200d6f0e51676dd`
(weights) and `046be7d582b1435bf027227b78651198` (README).

`bench/e2_cllg_contract.py` reads YAML front-matter and builds
`readme_contract.json`: README SHA-256, established software/script/metric/licence/
base-model facts with literal excerpts, `backend: kraken-native` and
`factory: bench.e2_native:cllg_kraken`. **Class order is taken from the loaded
Kraken codec**, preserving multi-label/multi-codepoint mappings. **Preprocessing
is taken from the installed Kraken `ImageInputTransforms`**, its actual defaults,
model input shape and stored padding; source hash, Kraken version and transform
representations are recorded. Codec/resize details are not invented as README
quotes. The adapter uses `kraken.lib.models.load_any`, PIL grayscale line images,
Kraken's line transforms and `predict_string` on CPU. Contract reload independently
loads the weights and checks checkpoint, codec and transform identity. A guessed
Transformers backend is refused. Tiny fake-model tests cover the adapter protocol
only because Kraken cannot be imported here; actual release inference is node-only.

Before the bake-off, after staging actual CLLG weights and Kraken 7.1:

```bash
"$PYTHON" -m bench.e2_cllg_contract \
  --readme /opt/e2-assets/cllg/README.md \
  --checkpoint /opt/e2-assets/cllg/ppocr_v6_tau090.safetensors \
  --out /opt/e2-assets/cllg/readme_contract.json
```

Both Kalchas candidates use the clean pinned commit
`7a0f9fddcfb14276bc48850abcc6706170583eb9`:

| Candidate | Registry name | Released checkpoint |
|---|---|---|
| `kalchas` | `Kalchas` | `kalchas/checkpoints/Kalchas/model9_best_loss_1.35.pt` |
| `kalchas_polytondb` | `Polyton-DB` | `kalchas/checkpoints/Polyton-DB/99_model_best_loss_1.184.pt` |

Each also requires its adjacent `_artifacts.pt` (native codec, width/height).
The pinned native loader uses paths relative to cwd; the wrapper loads inside the
checkout and restores cwd/socket state afterward. Actual loaded tensors, codec
artifacts and loader source are hash-bound. `kalchas_polytondb` carries
`gold_overlap_risk: true`: it is scored diagnostically but excluded from selection
on any Polyton-DB gold, including when the config omits the risk flag. Only a
reviewed `gold_overlap_disproof` JSON with `overlap_disproven:true`,
`gold_dataset:polyton_db`, a reason and nonempty hash-checked evidence `files` can
clear that exclusion. A GRPOLY fallback does not by itself prove other data disjointness.

**All Kalchas line-reader runtime dependencies**, checked against the cached pinned
`ocr.py`, `dataset.py`, `image_utils.py`, `ctc_decoder.py` and `model.py`:
`numpy` (upstream declares >=1.14.5), `torch` (>=2.2.0), a compatible `torchvision`,
`Pillow` (imports as `PIL`), and **`scipy`** (`scipy.ndimage` for native binarization
and `scipy.special.logsumexp` for decoding). The upstream setup file lists only
NumPy/Torch; that list is incomplete for inference. Optional package helpers need
`kraken` (`utils.py` segmentation/binarization) and `tqdm` (`factory.py`); the E2
line reader does not import those helpers. The demo's `wand`/ImageMagick and
plotting/notebook `matplotlib`/`jupyter` are optional demo tools. Missing import
errors name the absent module and the full line-runtime list; incompatible native
libraries remain visible load failures. This fix performs no installation.

`--service` activates optional `module:factory(service_name)` hooks returning a
blind crop reader. No hook is invoked without all required environment variables:

| Hook name | Environment variables (values never receipted) |
|---|---|
| google / Document AI | `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`, `DOCUMENTAI_PROCESSOR_ID`, `DOCUMENTAI_LOCATION` |
| azure / Azure DI | `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY` |
| mistral / Mistral OCR | `MISTRAL_API_KEY` |

No credentials = no-op/NA. With credentials, the operator must supply the explicit
service adapter; its source hash is recorded. These hooks may perform external
OCR only when invoked on the node with `--service`; none ran here.

## E2fix2 reader parity and copied-node normalization evidence

Every bake-off with E1 candidates must first pass `bench/e2_reader_parity.py`.
It validates E1's byte-bound v7 synthetic held-out mix, chooses 200 distinct rows
by line ID, and evaluates their factory `label_ids` through the unchanged
`train/eval_cer.py` path (`ManifestDataset`, parquet strip bytes, width-bucket bs64,
FP32 CPU). It independently loads the same checkpoint with E1's tensor-only safe
wrapper, exports the **same PNG bytes**, then reads each crop with E2's reader.
Require >=99% **exact raw decoded strings** for each E1 candidate. Unicode/space
folding is prohibited in this comparison. The complete matches/mismatches,
checkpoint/data/mix/source bindings and crop hashes go in
`bakeoff/reader_parity.json`. Failure or missing inputs produces `passed:false`
and `teachers.json ready:false` before any candidate scoring. The gate reruns;
a stale pass boolean never skips model execution.

E2's reader preserves valid 48px grayscale factory strips without resampling.
For raw crops it retains import-real resize/letterbox; tensor construction uses
`train.data.collate_strips` exactly: uint8 pixels, rounded own-background median,
right `DET_PAD_MARGIN` halo, pre-pad `ceil(width/4)` lengths, FP32 px/255 and
(x-.5)/.5. Greedy decoding returns raw E1 codec atoms, bypassing the serving
Recognizer's NFC conversion. No polarity inversion is added. The historical
O4b/serving reader and trainer are unchanged.

Copied evidence from the A6000 run at 8 October 03:14 remains untouched under
`out/e2c_bakeoff_evidence/`. Offline re-scoring of its **existing** predictions,
without model re-execution, gives:

| Candidate | Cohort | Corrected NFD CER | Acute recall | Micro mark F1 |
|---|---|---|---|---|
| f50_s0 | real gold | 6.0230% | 98.4234% | 0.826718 |
| f50_s0 | v7 control | 6.2954% | 94.1850% | 0.871899 |
| f75_s0 | real gold | 8.3013% | 98.5360% | 0.737215 |
| f75_s0 | v7 control | 8.3277% | 91.7125% | 0.835800 |

Machine-readable counts, per-mark metrics and prediction SHA-256s are in
`out/e2_fix2/normalization_recheck.json`. These control rows are not the complete
E1 instrument, so 8.3277% is not a remeasurement of E1's reported 8.9%.
The copied `ready:true` E1-only selection is invalid under this fix.

Local tests exercise NFC/NFD identity at 0 CER and full mark recall, unchanged
whitespace, all marks, actual parquet/PNG/loader/evaluator paths on **200 fixture
rows** (200/200 exact decodes and identical FP32 tensors), and rejection at
197/200; the exact 198/200 boundary passes. That verifies plumbing, not production checkpoint parity. Production
v7 shard paths and retrained f50/f75 weights are absent locally; the node gate
must still measure and pass them. Actual Kalchas/CLLG loads remain unmeasured.

### Agreement modes

E2 fix 5 supersedes the two-teacher selection requirement above: select the top
fully real-gold-scored **non-E1, non-overlap** readers by pooled mark F1 (same tie
breaks). Two select `layer+2`; one selects `layer+1`; zero leaves `ready:false`
and refuses. Both Kalchas specs receive `gold_overlap:true` in the loaded config;
this flag always excludes selection, even with an overlap-disproof receipt. They
and E1 remain scored diagnostics. `teachers.json` records the mode, loaded reader
bindings, excluded candidates and reasons.

The two-reader descriptions elsewhere in these notes refer to `layer+2`.
In `layer+2`, the layer and both readers must agree exactly. In `layer+1`, the
PDF text layer (InVision OCR) and the sole independent reader must agree under
the same NFC + whitespace-collapse comparison. Receipts disclose: "silver = exact
agreement of two independent systems (PDF text layer + reader); biased toward
lines both get right". Errors never count as agreement; geometry, exposure,
partition, 1,126-page, holdout minimum and text-disjointness gates are unchanged.
`vouli.json` records the mode and selected teacher IDs/bindings. The reported
8 October node evidence motivates this mode; these code tests do not establish
a successful Vouli rerun or human-gold accuracy.

### CP-E2b fix 6 receipt and reporting gates

Adoption now validates receipt content before copying: current external-input inventories,
configured candidate checkpoint hashes and checkout revisions, linked bake-off/parity hashes,
Vouli holdout counts recomputed from records, and adjudication totals and bindings. Warm-start
adoption requires 100 crops and all 300 scale-normalised endpoint results, the converted-checkpoint
hash, donor/config/revision bindings and the independent preprocessing receipt. Retraining
requires completion/run receipts with best/last checkpoint hashes and current E1 data bindings.
Empty markers and markers for another stage are refused. Older incomplete receipts must be
regenerated; hashing current inputs cannot supply their missing provenance.

Reader exclusion and independence use loaded checkpoint SHA-256 plus checkout revision
or service name plus recorded model/version (adapter hash if no model revision is supplied).
A declared overlap on any alias applies to every matching identity.
Loaded Kalchas registry models stay precautionarily excluded, E1 checkpoints stay diagnostic,
and duplicate reader bindings cannot create `layer+2`. The Vouli wrapper re-derives these
gates from the bound bake-off results before processing PDFs.

Every Vouli result and numeric row carries the agreement mode, teacher IDs, `silver_agreed`
label tier, machine-agreement status, `human_gold:false`, and acceptance rates: final admitted
lines / all adjudicated lines, by split and script (`reserved` is TEST), including lines removed
by later exposure/duplicate gates in the denominator. Each Markdown table row repeats these
qualifications and this fixed bias sentence:

"exact agreement of the PDF text layer and one independent reader; shared errors can survive; hard disagreement lines are excluded, so the instrument is agreement-conditioned"

The sentence also appears in `vouli.json` and the adjudication receipt. For `layer+2`, the
recorded mode and teacher IDs disclose the additional reader; agreement still conditions coverage.
Fixture checks establish these refusal/reporting behaviours, not a new production result.

### CP-E2b fix 7 adoption contract

Adoption's contract is **copy + hash-bind + re-verify the stage's own semantics from
stored content**. The driver validates source content and current input bindings
before copying, verifies copied hashes, and repeats semantic validation at the
destination before recording a done marker. Marker reuse repeats those checks.
This verifies stored evidence and custody; it does not attest that computation ran
under the current code or rerun OCR, tensor parity, or training.

For bake-off, `gold.jsonl` and `control.jsonl` must each contain the expected cohort
count (300 by default, or the explicit `bakeoff.required` fixture count), distinct
line IDs/texts, and nonempty `crop_path` and `text` on every row. Each selected
candidate must have `scored == rows` and zero missing readings in both cohorts.
The complete reader-parity receipt must retain its evaluator/adapter, v7 mix,
code/codec and candidate bindings, 200 stored comparisons per E1 reader, and
consistent row counts, exact-string match counts/fractions and the 99% threshold.
With no E1 candidates, the full receipt must explicitly state that parity is not
required and carry an empty candidate inventory. A bare `passed:true` is refused.

For every admitted Vouli row, `silver_agreed` requires no stored reader errors,
`exact_agreement:true`, and stored readings equal to the text under the recorded
NFC + whitespace-collapse comparison: the sole reading in `layer+1`, both in
`layer+2`. Original extraction admission and geometry must also permit admission.
The driver recomputes these decisions from stored content and refuses a
contradiction with its line ID, even when all aggregate hashes/counts agree.
O4b may retain a silver agreement tier on a geometric reject; it remains excluded.

Identity exclusions inventory every identity supported by `reader_identity()`,
including service name plus model/version, so a flagged service's unflagged alias
cannot qualify through a different adapter or candidate name.

**`readout` adoption is refused**, including reuse of old adopted readout markers.
Reports must be regenerated with the driver's `readout` stage after verification
of the Vouli dependency receipt. This supplies agreement mode, teacher IDs,
machine/silver status, acceptance rates and the bias sentence from verified
evidence; copying an old completed report could bypass those qualification gates.
`runs` adoption remains supported: every completion/run binding must match the
destination's corresponding adopted/generated training mix, build information,
transfer mix/binding, trainer and donor bytes. Changes to those inputs invalidate
adoption or marker reuse.

Local fix-7 verification: `bench/tests/test_e2.py` **259 passed** and
`bench/tests/test_o4b.py` **66 passed** (**325 total**, including **77 new fix-7
cases**), with no failures or skips. These are offline fixtures. The handoff is
`E2_FIX7_HANDOFF.json`; only the permitted source/tests/notes were changed and
the repository's `.git` inventory and modification metadata remained unchanged.

## Vouli partition and admission

All 107 `data/raw/pdf_cache` PDFs bind to S17 refetch rights/source receipts and
PDF SHA-256s. PDFium verifies 1,126 total pages. Text-layer lines reuse O4b/O1's
character boxes, baseline/column assembly and ink ownership at 200dpi. The July
S17 boxes provide prior silver layout evidence; they do not become line GT.

The canonical work map must contain `reviewed:true` and group mirror scans,
volumes/editions and all pages of each work. O4b builds the O5 TEST/C1 exclusions;
E2 adds **every** E1 real/synthetic/held-out/transfer exposed document and every
bake-off gold/control document. Every exclusion must resolve to a map key or a
known canonical value, including O5/C1 aliases and all E1/bake-off IDs. The build,
reservation and partition reader refuse with the full unresolved list. Remaining
works are ordered by SHA-256(`E2/20261008/work`); first max(10,ceil(.20*N)) TEST,
next ceil(.05*N) DEV, rest TRAIN. This override is fixed before text extraction or
teacher outcomes. All pages of a work retain its split.

Both selected readers blindly reread each crop through `o4b_adjudicate`; exact
NFC/space agreement with the layer yields `silver_agreed`, otherwise `flagged`.
The historical adjudicator's `e1`/`kalchas` reading keys denote two slots; receipts
explicitly record the selected IDs. Geometry rejects never become admitted on
agreement alone. Previously exposed text is removed, then TEST-text duplicates
are removed from TRAIN/DEV and DEV-text duplicates from TRAIN, with a ledger.

Only factory `import-real` writes shards. `out/e2/real_vouli/test` is an alias to
the same frozen `reserved` bytes; no second writer or split rewrite. Require at
least 400 **polytonic** imported TEST lines across at least 10 canonical works;
source tags alone cannot satisfy the floor. A shortfall fails without choosing new
works based on teacher quality. This is the **FIRST real Vouli polytonic test
instrument**, with **silver-agreed labels, not human gold**. It is disjoint from
all inventoried project exposures; document overlap with undisclosed external
donor/teacher pretraining corpora remains unverified.

## Warm-start, parity and deferred work

R01 retains official HF `model.backbone.*` and `head.encoder.*`; only
`head.head`, Linear(120,248), is new. R03 retains the full upstream tiny encoder
([64,128,256], depths [3,6,3]) and RCTC `char_token`, `fc_kv`, `w_atten_block`;
only `decoder.ctc_decoder.fc`, Linear(256,248), is new. Auxiliary NRTR/SMTR is
absent/dropped explicitly; unknown retained keys and shape mismatches reject.
R03 uses the existing byte-pinned vendored implementation, with strict mapping
from the staged native config. A newer source incompatibility fails, rather than
substituting our derived `svtrv2_small` encoder.

`donor_init.pt` is a safe weights-only wrapper with codec/architecture identity,
full checkpoint-state SHA-256 v2 and a bound `donor_provenance.json` (URL, immutable
revision, licence, source/config/codec hashes, exact mapping, dropped layers).
Fixture tests demonstrate strict loading through the existing trainer initializer.
E2 registers architecture factories in `bench/e2_train.py` and calls the frozen
trainer's **existing** `--init-from`; no `--init-from-donor` is added. Optimizer,
scheduler and training RNG are fresh. RGB kernels are retained and grayscale is
replicated. R01's **training adapter** retains the normalized right-background
extension to a width multiple of four. The E3d installed-donor probe establishes
`T_native = floor(ceil(W/4)/2)` after that extension (130 -> 132 pixels -> 16
frames); native parity independently records 320 pixels -> 40 frames. E3e
repeats each encoder frame twice by parameter-free nearest-neighbour upsampling,
then crops or right-pads with the last frame to exactly `ceil(W/4)` before the
classifier. This preserves the frozen contract and CTC label-length feasibility;
warm-start weights and head initialization are untouched. Duplicate frames change
CTC alignment granularity, which the new head learns. Native parity bypasses
this training adaptation and compares the original classifier.

The new head is initialized once with converter seed 0 (recorded); sweep seeds
0/1 govern training RNG, sampling and dropout. This is a fixed donor-head control.
Whole-network training starts at update 1 using E1's optimizer policy. The survey's
5% head-only phase, frozen BN and 0.1× encoder LR are **deferred**: they need a
separately reviewed trainer-policy change and are not silently emulated here.
Donor adapters inherit the current non-mask-aware native attention/padding path;
parity does not prove batch invariance, GPU throughput or deployment behavior.

Before logits, parity runs the donor's own preprocessing on **20 distinct crops**,
including short, very_long, blank and padded cases, and compares its FP32 tensors
to ours (same shape, max abs ≤1e-6). R01 calls the pinned Paddle
`TextRecognizer.resize_norm_img` on OpenCV-decoded BGR; reviewed
`native_preprocess.rec_image_shape` is required (the example's `reviewed:false`
deliberately refuses). R03 calls the pinned OpenOCR evaluation
`RatioDataSetTVResize.resize_norm_img` with its native config and rounded ratio
buckets. Random native padding is refused. Both source hashes and the 20 tensor
comparisons/NPZ artifacts enter the receipt; the launcher refuses old receipts
that lack this gate. Reconcile the example's local resize/padding options with
the actual predictor before marking R01 reviewed. A mismatch stops before any
logit comparison; no native preprocessing equivalence was measured here.

Parity then uses 100 distinct crops (JSONL `crop_path`, `parity_kind` including short,
very_long, blank, padded), one explicit original preprocessing transform, actual
FP32 arrays, original class ordering, backbone/neck/pre-softmax logits and saved
endpoint NPZ files. Require max abs ≤1e-4, relative ≤1e-3 for |native|>1e-3, and
identical greedy CTC sequences. `bench.e2_native:r01_paddle` and
`bench.e2_native:r03_openocr` use the clean native checkouts at pinned revisions;
R03 explicitly selects its CTC decoder, irrespective of `infer_gtc:true`.
The configured native preprocessing must be reconciled with those actual pinned
predictors before launch (the example is survey-derived, not measured proof).
The Paddle layer-map converter requires exhaustive explicit source→target keys,
Linear transposes and BN counter treatment; no regex/shape guessing. Official
paired Paddle weights/config or their complete mapping are not staged locally,
so actual Paddle→Torch parity remains **node-only**, as does R03 native parity.
Converted-state success alone never marks parity passed. Both donors must also
pass the 48px/log-softmax/ceil(W/4) shape gate before sweep runs.

R02 is optional and not scheduled; generic v6-small head-swap support exists, but
no R02 acquisition, parity or arm is claimed. Height 64, codec v2, Core ML/ANE,
FP16 parity, BN/freeze/LR variants, human correction of Vouli TEST labels and any
teacher-quality conclusion are deferred. The reason for 64 is the frozen factory
and dataset loader geometry, not a presumed accuracy outcome.

## Readout

E2 calls E1's runner, evaluator, readout and galleries with explicit arm/instrument
coverage. Four instruments × 12 enabled arms = 48 evaluations. Per-epoch planned
and realized data provenance and actual stopping budgets remain available.
Real factory word-tag sidecars are SHA-bound and joined by line ID; rendered lines
receive the matching frozen rule tags. Gallery rows display word tags (M01 fix).
The frozen E1 real receipt lacks `word_tags_sha256`; evaluation preserves it and
reports **`word_tags: absent`** in JSON and Markdown. Displayed fallback tags
are explicitly `rule-derived`, bound to `line_categories.py`; an adjacent
unbound sidecar is ignored. A sidecar promised by a receipt remains mandatory
and hash-checked.
A3b `line_categories.py` adds overlapping leader/numeric/caps/footnote/italic/bold/
hyphenation/punctuation/mixed-script/long-line strata, with explicit unknown font
buckets; source PDF font sizes are points, never inferred from resized ink height.
Metrics use the unchanged E1 strict scorer and its mark alignment ties. Every
legacy transfer number inherits the existing `unprovenanced_recipe` disclosure.
Page omission/detector coverage and a model release are not established by this
line-only experiment.

## CP-E2code fixes and custody

v8 now requests 240 mixed-script and 840 polytonic lines. `v8_exclusions.json`
records the actual hash-bound before/after census and exact factory quotas.
Additional exclusions can still cause a shortfall; the build refuses rather
than altering the recipe or admitting excluded texts. The real pool census,
loaded CLLG model/transform contract, production reader parity, native donor preprocessing/logits, importer node build
and production run remain node-only and unverified locally.

Stage input snapshots recursively read manifests and traverse `root` sources
relative to each manifest's directory, including annotations, images and
containers. Reuse checks those source hashes directly; changed source bytes
invalidate the marker. The global binding also includes reused O1
`bench/extract_lines.py` and `bench/admission.py`, and both factory executables.
The fix response with file/line references and local evidence is
`reviews/CP-E2code_reply_1.md`.

Local fix verification: **180/180 tests passed in 183.77 seconds** with the
prescribed `C0_FACTORY` command above; **7/7 final dry-run stages** passed with
`executed:false` and `training_executed:false`. Shell syntax and scoped
`git diff --check` passed. The frozen trainer remains SHA-256
`7c20b9a316d70a247e1aea6166486e03403a3fa7ab66c1a427f2a1e1d4756fe1`.
The retained E1 receipt and 137-text exclusion bytes are unchanged. No network,
GPU, production training, factory compilation or Git mutation ran here.

## E2fix2 local verification and remaining node gate

The prescribed two-suite command passes **123/123 tests**. `git diff --check`
passes. The unchanged trainer SHA-256 is
`7c20b9a316d70a247e1aea6166486e03403a3fa7ab66c1a427f2a1e1d4756fe1`.
No network, GPU, training, dependency installation, factory compilation or `.git`
write was performed. Original copied node evidence was not edited.

`out/e2_fix2/bakeoff/reader_parity.json` is explicitly **passed:false** because the
node's v7 factory receipt/shards are not staged on this Mac. Its sibling
`teachers.json` is **ready:false**: the copied run has zero non-E1 scored readers,
and production parity remains pending. These are refusal receipts, not completed
production results. `E2_fix2_HANDOFF.json` records local evidence and exact node
steps. Retain `out/e2c` and its retrained checkpoints; point the updated standalone
bake-off config at those existing checkpoints and use a fresh bake-off output
directory. Generate the CLLG contract with actual weights/Kraken first, stage both
Kalchas models and artifacts, then run the standalone bake-off. It automatically
executes the 200-row gate before scoring. Only a resulting `ready:true` file may
proceed to Vouli. Older supervisor markers bind old code and cannot be reused
under the new source identity.

## Results (8 Oct 2026)

### Teacher bake-off v3 (`out/e2d/bakeoff_v3`, copy `out/e2d_bakeoff_v3/`; scorer NFD both sides; reader-parity gate vs E1 evaluation passed)

300 real polytonic gold lines (Polyton-DB: Gazette 1850s + Appian 1880s; the Parliament subset excluded as Vouli-shared) and 300 v7 rendered polytonic control lines. Strict NFD CER; pooled micro mark F1.

| candidate | real gold CER | real gold mark F1 | v7 control CER | v7 control mark F1 | CPU ms/line |
| --- | --- | --- | --- | --- | --- |
| f50_s0 (ours, E1 recipe, 50% real) | 6.00% | 0.827 | 6.32% | 0.871 | 64 |
| f75_s0 (ours, 75% real) | 8.14% | 0.740 | 8.36% | 0.834 | 68 |
| kalchas (model9) | 0.02% | 0.999 | 35.0% | 0.636 | 196 |
| kalchas_polytondb | 0.02% | 1.000 | 46.9% | 0.603 | 191 |
| cllg (Inria, Kraken PP-OCRv6) | **1.30%** | **0.992** | **5.13%** | **0.920** | 6,333 (†) |
| azure / google / mistral / vouli_layer | NA (not enabled / no layer) | | | | |

(†) CLLG's ms/line in this run is process start-up: the adapter spawned one worker per line (7.96 s measured). E2 fix 3 (commit 3d07f3d) makes the worker persistent; inference-only timing to be re-measured in the Vouli stage.

Reading. Polyton-DB is Kalchas's training data (0.02% CER = memorised; 35–47% on our renders), so it is not an independent gold set for Kalchas. CLLG has not seen Polyton-DB and reads it at 1.3% CER with mark F1 0.99; on our renders it reads 5.1% with a systematic grave-accent over-prediction (precision 0.42 on v7 control) and a weaker iota subscript. Our E1 half-real arm reads real polytonic at 6.0% before any polytonic-targeted training; marks are the gap (rough breathing, iota subscript). Teacher selection: `ready:true`, teachers = kalchas + cllg (two fully scored non-E1 readers). Note for the Vouli test split: Kalchas may have seen Parliament scans of the same era (Polyton-DB Parliament subset); that affects only Kalchas-vs-ours comparisons on that split, not its use as one of two independent silver readers.

### Warm-start R01 parity (8 Oct, `out/e2d/warmstart/R01/parity`, copy `out/e2d_warmstart_R01/parity.json`)

Native reference = PaddleOCR @dab3fe35 dygraph `el_PP-OCRv5_mobile_rec.yaml` + official PaddleX pretrained parameters
(sha256 fde26517…; the staged inference export carries no Architecture block). HF donor weights equal those parameters exactly
(136/136 convolution tensors, max abs 0). Reviewed preprocessing (`R01_native_preprocess_review.md`; `paddle_dynamic` pad rule) matches
the predictor on 20/20 crops in FP32. Endpoints on 100 crops (30 short, 30 very long, 30 padded real, 10 blank):

| endpoint | suite max abs diff | reference scale at suite maximum | worst normalised |
| --- | --- | --- | --- |
| backbone | 1.09e-3 | 107.0 | 1.0e-5 |
| neck | 5.3e-4 | 6.80 | 7.8e-5 |
| logits | 2.4e-3 | 25.17 | 9.6e-5 |

These are the suite maxima from the copied receipt, not the first crop. All **300 endpoint ratios** are ≤ 1e-4.
The scale-normalised rule has a known blind spot: a localised error below 1e-4 of the tensor maximum passes
if greedy decoding stays unchanged; exact agreement of greedy CTC sequences remains required. This is a rule
limitation, not evidence of an observed production port error.

Greedy CTC decodes identical. Verdict `passed:true` under the scale-normalised rule (max abs / max(1, max|native|) ≤ 1e-4), which
replaced the element-wise rule after it failed on this framework-level FP32 noise (disclosed, commit a63e5bd). R03 (SVTRv2-T) has no
obtainable checkpoint (Google-Drive only; R2 found no mirror) and is recorded absent; the sweep is 8 arms (scratch/R01 × .25/.5 × 2 seeds).

## E2 fix 8 — optional Vouli instrument and CP-E2b cycle-3 gaps

User-reported node evidence, `out/e2d/vouli_v6`, 8 October 2026 at 12:30:
layer+1 produced 5,003 `silver_agreed` lines, including 1,015 reserved
`greek_poly` lines. Every silver line remained `admitted:false` at the
text-layer geometry gate (`born_digital_candidate` provenance): all had
`unexplained_ink:true` and positive `ink_bbox_error`; 4,146 had `missing_ink`.
This is agreement evidence, not usable real supply. The geometry gate is
unchanged; agreement never overrides it. These node counts were supplied with
the fix request, not independently rerun locally.

If the admitted holdout fails validation, `e2_vouli` now writes a completed
`vouli.json` with `instrument:"unavailable"`, the exact validation reason,
zero admitted/imported/test lines, tier counts by split/script and a geometry
flag histogram over all silver rows. Extraction and adjudication evidence is
retained; final `records.jsonl` is empty and no import is called. Adoption and
marker reuse recompute admission, the shortfall reason and the histogram;
unavailable receipts cannot claim imported or test lines.

`e2_mixes` uses E1 alone for real supply in that case, retains the fixed update
budget, omits `vouli_test_mix.json` and records `vouli:"unavailable"` plus
`reason` in `mix_plan.json`. Driver evaluation uses the three available
instruments. JSON and Markdown readouts carry `unavailable: <reason>` for each
arm's Vouli metrics, with no blank or zero score. `E2_COMPLETE.json` records
`vouli_instrument:"unavailable"`; readout adoption remains refused.

CP-E2b HIGH 1: parity receipt verification reloads the hash-bound v7 reserved
shards and repeats the sorted first-200 selection. Every comparison must match
that row's ID, codec-decoded label IDs and `gt_nfd`, the SHA-256 of its PNG bytes,
and the stored numbered parity crop. Consistent aggregate hashes and match
counts cannot authorize different rows, labels or crops.

CP-E2b HIGH 2: adoption, marker reuse and the Vouli wrapper reload the complete
gold/control cohorts before `validate_teachers` recomputes identity exclusions.
Fresh bake-offs also bind the stored cohort hashes. A `gold_overlap_risk`
service candidate propagates its exclusion to an alias of the same service/model
when the verified gold cohort contains Polyton-DB, as in fresh selection.
The cycle-3 probes use complete 300+300 scored cohorts and remain refused.

Local validation: **303 E2 + 66 O4b = 369 passed** in 42.03 seconds with
`C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory`,
`PYTHONDONTWRITEBYTECODE=1`, `GIT_OPTIONAL_LOCKS=0` and pytest's cache disabled.
There are 42 explicitly named fix-8 cases, plus two added geometry-rejection
cases in the existing Vouli mode matrix. Fixtures cover unavailable receipt
adoption/reuse, E1-only mixes, readout wording, completion receipts and both
cycle-3 gaps. No node OCR, GPU run or production training was launched.
The repository's 4,334 `.git` files have identical inventories and SHA-256
hashes before and after local validation. `git diff --check` passes.

CP-E2b HIGH 3 stays fixed: reports must be regenerated through verified stage
dependencies. MEDIUM 5 remains logged and unchanged (serving identity
acknowledgement, worker inventory/placement and native latency labels).
Use a fresh driver root under the changed code identity; this patch does not
upgrade or certify older supervisor markers. See `E2_FIX8_HANDOFF.json` at the
repository root for exact file hashes and test evidence.

## E2 fix 9 — CP-E2b cycle-4 optional-Vouli validation

A1: adoption and marker reuse require `lines/report.json` and both extraction
inventories before accepting an unavailable receipt. Report admission/rejection
counts, unique candidate IDs, page candidate counts, extraction/adjudication
coverage and crop hashes must agree. An empty inventory cannot satisfy a
retained 402-candidate report, even with consistent aggregate file hashes.

`e2_vouli.exposure()` now supplies the same exposure rule to fresh extraction
and receipt verification: all E1 TRAIN/DEV/TEST/transfer texts and bake-off
gold/control texts; image documents and reviewed synthetic document aliases.
Unavailable adoption/reuse recomputes the entire `exposure.json`, checks the
partition's effective exclusions against its base plus those exposures, and
repeats text/duplicate exclusions. Unsupported exclusions cannot turn a
qualified holdout into an unavailable instrument.

A2: a shared mix verifier runs at adoption, marker reuse and `run_plan()`.
It opens every run manifest, every TEST manifest and transfer, validates and
resolves component custody, and permits real supply only from the bound E1
real directory and, with an explicitly available positive-admission receipt,
the root's Vouli import. Retained external imports are refused even with zero
fraction. It recounts shard rows from Parquet metadata and reproduces each
epoch's largest-remainder component quotas, checking both the declared real
pool counts and every `planned` component count. Manifest inventories and
real fractions must also agree with the plan and receipt.

Regressions exercise both unavailable-evidence boundaries and all three mix
boundaries with genuine Parquet/manifest custody. The cycle-4 training probe
loads 19,657 E1 rows plus one retained Vouli row under ordinary `train.mix`
validation, then fails the E2 supply gate. Positive controls cover E1-only
unavailable mixes and available Vouli supply with positive admission.
The previous unavailable fixture pipeline now uses actual manifests and
assembly while keeping factory rendering and model evaluation stubbed.

This changes verification only; geometry/admission rules, production training
and the previously logged MEDIUM serving/execution-receipt work are unchanged.
Use a fresh driver root for the new code identity. Local fixture evidence and
final scoped file hashes are recorded in root `E2_FIX9_HANDOFF.json`.

Final local validation: **362 E2 + 66 O4b = 428 passed** in 140.69 seconds,
including **59 fix-9 cases**, with zero failures, errors or skips. Command:
`C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 .venv/bin/python -m pytest -q -p no:cacheprovider bench/tests/test_e2.py bench/tests/test_o4b.py`.
JUnit and log evidence are under `/private/tmp/e2-fix9-evidence/tests-final.*`.
Fixture custody checks cache the actual HEAD recipe inventory per fixture;
production recipe validation is unchanged. No node OCR or training was run.

All Git commands used here were read-only. An intermediate comparison matched
all 4,361 original `.git` file hashes. During handoff preparation, concurrent
Plan-copy commits `30511ea` and `d28b924` changed `.git`; their committed diff
touches only `PLAN_GLOSSAPI_v3_20261007_copy.md`. The handoff records the
observed inventory delta instead of claiming final `.git` equality. The scoped
working diff contains only the five allowed edited files; `git diff --check`
passes, and the requested handoff is the only new task artifact in the repo.

## E2 fix 10 — bounded Vouli adjudication and verification

`adjudication.readers` contains only `{id, binding_sha256}`: SHA-256 of the full
reader envelope serialized with `json.dumps(binding, sort_keys=True,
ensure_ascii=False)` in UTF-8. New adjudication report key `readers_full` keeps
full bindings once; `vouli.json.teachers` remains full. Reader/config changes
still reject admission, adoption and reuse. Duplicated teacher aliases and
constant agreement disclosures leave the rows.

Summaries and driver verification stream `all.jsonl`; missing split/script
values use `unknown`. Raw inventory equality
uses row digests and small ID/page/crop summaries. New extraction report keys
`pages[].geometry` and `pages[].geometry_sha256` hold both page gutter arrays
once, after the geometry gate; rows use `page_geometry_sha256`. Character-index
arrays and constant script/codec/partition/policy metadata remain in raw rows;
new adjudicated field `extraction_row_sha256` binds their complete content.
Fix 11 requires and verifies `lines/report.json` for available and unavailable Vouli at adoption, stage completion and reuse.
Page geometry hashes are recomputed with the same canonical JSON serialization; mismatches fail closed with the first offending `line_id`.
Fonts and diagnostics stay on adjudicated rows. Character-index arrays dominated
the local fixture; the node's 56 KB raw rows were not staged for measurement.

Use a **fresh E2 driver root** for the changed code identity; existing markers
and receipts are untouched. No node stage ran. Full-suite collection also needed
`o5_eval` to load the unchanged trainer by file path instead of the colliding
`train` namespace, and the page-slice adapter to accept both Docling postprocess
return shapes. Missing test dependencies use existing local packages, offline.

Validation: `python -m pytest bench/tests -q -x -p no:cacheprovider` completed
with **1,055 passed, 1 skipped** (absent optional O1 audit replay), in 737.79s.
The largest native fixture row with two 200 KB bindings is **3,832 UTF-8 bytes**.
Local execution used `.venv`, `C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory`,
`PYTHONPATH=/private/tmp/e2fix10-arm-deps`, disabled bytecode/Git locks, and
`OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`. No packages were installed.

E3f production R01 uses micro-batch 32 with accumulation 2 (effective batch 64; BatchNorm statistics on 32 rows), selected by the 44.6 GiB widest-bucket probe; see E3_NOTES.md and out/e3f/probe/probe.json.
