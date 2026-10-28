# E1 implementation and node handoff — 7 October 2026

E1 prepares factory-owned data, creates five real-fraction manifests and fifteen
scratch-initialized runs, evaluates final best checkpoints, and writes the
pain-point report and five portable sprite galleries. No model steps, network
access, GPU access, background jobs or writes under `out/` were performed on this
Mac. Source edits remain on main's working tree; original `.git` is untouched.
`E1_fix_HANDOFF.json` lists the current fix edits and their hashes. Test indexes
and generated fixture artifacts are confined to temporary storage.

## Resolve the binding constraints explicitly

* V5's committed target is **200,000**, not 19,657. It remains byte-identical.
  Production builds use `linefactory build --recipe factory/recipe.v5.json` with
  no `--smoke` or `--allow-deficit`. TRAIN exposure is then capped at **19,657**
  rows per epoch through C0 assembly. Quotas use largest-remainder rounding, so
  realized f differs from requested f by at most one row. Width-bucket tails are
  combined, giving **308 batches/epoch, 2,464 planned updates/run** at bs64 and
  accum1, regardless of widths. Early stopping remains terminal and its actual
  epochs/updates are reported. A CTC-skipped update prevents completion rather
  than producing an equal-updates claim.
* O5's fixed real TEST has 3,600 lines / 36 documents, **zero polytonic and zero
  Cyrillic**. Real DEV has one polytonic and no Cyrillic line. These cannot become
  polytonic/Cyrillic-complete without changing the binding O5 selection. E1
  preserves the selection, records the shortfalls, emits NA metrics and uses a
  separate synthetic held-out instrument with >=300 lines in each required
  stratum. Every production TRAIN arm/seed/epoch is checked for polytonic. The
  pure-real arm retains its native class counts; its distribution cannot equal
  v5 synthetic marginals. All mixtures disclose actual counts. The frozen real
  importer maps Cyrillic code-switch classes to `cyrillic`; readout distinguishes
  Cyrillic/Latin references diagnostically without changing shard labels.
* The old `transfer-dev` command changes recipe fonts in memory and is refused by
  C0. **V6 is a separate committed evaluation-only recipe**: 2,400 reserved-band
  rows, exact class quotas, three v5 held-out fonts, minimum polytonic300 and
  Cyrillic300. It disables train-only crop/ink augmentation, declares an explicit
  0.85 font-share cap for the three-font instrument, and keeps the other v5
  appearance settings/exclusions. Factory audits emitted strata; shortages or
  failed appearance audits stop preparation. A mix loader cannot use this build
  for train/val. V5's training recipe is unchanged; the P4 change paragraph is in
  `docs/data_contracts.md`.
* `--transfer-mix` normally selects on transfer CER. E1 explicitly passes
  `--selection-metric val_cer --transfer-final-only`: custody is bound before
  training, reserved rows never feed training, and only the final best checkpoint
  is evaluated on held-out instruments. Patience stays six on DEV `val_cer`.
* Historical `out/transfer_dev_v4/reserved` is an **optional eval-only legacy
  instrument**, preserving O5 continuity. Its receipt reports an uncommitted
  recipe (60d65de2…) and `audit_ok:false` after in-memory font substitution. It
  cannot pass synthetic training custody. The new `legacy_eval` component binds
  recomputed shard hashes plus the original recipe SHA and resolved receipt SHA,
  requires `role:eval|transfer`, `provenance_status:unprovenanced_recipe`, and a
  nonempty disclosure. `validate(..., role='train'|'val')` and training's initial
  CLI gate reject it, even at fraction zero. `load_rows` independently refuses
  train/val. The default validator/manifest-builder role is **train**; evaluating
  a legacy manifest requires explicit `--role transfer` or `--role eval`.
* Without `--transfer-mix`, E1 never reads or binds the historical instrument,
  creates no transfer manifest/binding, passes no transfer input to training,
  evaluates **30** arm/seed/instrument combinations, and explicitly reports that
  transfer columns/metrics were omitted. With the option, it evaluates **45**.
  Stale transfer artifacts in a transfer-disabled output are refused; use a new
  E1_OUT to change configuration. A supplied instrument must match the exact
  unchanged O5 reserved shard inventory, including a byte-identical relocated
  copy. Its original receipt/shards are bound in node inputs and
  `transfer_binding.json`, rechecked during training/retries/final evaluation.
* `bench/e1_make_legacy_transfer_mix.py` reads the existing reserved receipt,
  requires `audit_ok:false`, copies its recipe SHA and codec version, and
  recomputes shard hashes. It writes only the manifest; it never repairs or
  restamps historical receipts/shards. Disclosure includes recipe SHA, failed
  audit, in-memory fonts and July 2026 dating. If the receipt has `built_utc` or
  `created_at`, that value is used; otherwise July dating is explicitly labelled
  historical O5 dating. The helper refuses missing/unreadable/empty inputs and any manifest output
  inside the immutable reserved instrument.
  `data_provenance.json` includes component disclosures alongside transfer epoch
  summaries and every object with numerical readout values. Every legacy
  prediction carries the disclosure; REPORT.md repeats it beside every numerical
  table row, report.json attaches it to numeric metric objects, galleries print it
  beside line CER, and the evaluator prints it beside aggregate CER.

## Preparation and custody

`bench/e1_prepare.sh` calls the Python selector/orchestrator, not a shard writer.
Production selection imports `bench.o5_prepare.select_manifests`, compares the
complete document assignment to `out/o5/build_info.json`, checks authoritative
O5 record hashes, reconstructs identical test-text exclusions, and imports all
selected rows via `linefactory import-real --partition o5-docs-v1`. An importer
drop or a mismatch with TRAIN19657 / TEST3600 / TEST docs36 stops preparation.
The real build's factory receipt covers train, val and reserved; `real/test` is
an alias to those immutable reserved files. TRAIN/DEV readers never load them.

The paired corpus is limited to the selected O5 TRAIN documents/texts. Additional
generator sources must be local JSONL files supplied with repeated `--corpus`
arguments, each row carrying text, source_dataset, source_doc_id and license.
E1 rejects missing provenance fields, excludes every TEST text and O5 DEV/TEST
source document before factory ingest, and retains v5's own exclusions. It does
not download corpora, generate replacements, or silently lower class/atom floors.
`supply.json`, ingest reports, select reports, audit reports, failed attempts and
`prepare_failure.json` expose shortages. The held-out synthetic pool uses only
the factory reserved text band and excludes every real TRAIN/DEV/TEST text.

`out/e1/build_info.json` binds all certified record files, every selected crop,
O5 selection/corpus/exclusions, corpus source files, raw recipes, codec artifact
and source, factory binary, train/factory/E1 base code, assets, repository HEAD,
factory receipts and exact shard inventories. Stages verify hashes again before
reuse. Changed code/config/data requires a new E1_OUT. Preparation stages publish
only complete factory directories; partial/quarantined attempts are retained.
No O5 ad-hoc writer is called.

Canonical manifests are created by `python -m train.mix build` and validated by
its CLI. Single-component f0/f100 omit zero-weight components. Each seed gets a
separate seed-bound run manifest; `mix_plan.json` records all eight planned
epochs' row marginals and quotas. The trainer writes actual epoch marginals in
`data_provenance.json` before stepping, and full-state resume preserves earlier
committed epoch records.

## Disclose-recipe-changes: every training parameter vs O5 real

| Parameter / mechanism | O5 real arm | E1 |
|---|---|---|
| Initial weights | incumbent best.pt via `--init-from` | **from scratch**, no donor |
| Architecture / head / codec | compact / NFD / v1 | same |
| Seeds | 0,1,2 | same; also manifest seeds 0,1,2 |
| Epoch budget | 8 | same |
| Batch size / accumulation | 64 / 1 | same |
| Optimizer | AdamW, default betas (.9,.999), eps1e-8 | same |
| Max LR / weight decay | 1e-4 / .05 | same |
| Norm/bias decay | excluded | same, `--no-decay-norm-bias` |
| OneCycle / pct_start | OneCycleLR / .075 | same; horizon is308×8 |
| Cycle momentum | disabled | same, `--no-cycle-momentum` |
| Gradient norm clip | 5 | same |
| Loss | CTC blank0, zero_infinity=True | same |
| Device / AMP | CUDA / incumbent device-selected AMP | same, runtime/dtype identity bound |
| Workers / pin memory | 6 / enabled | same |
| Model selection / patience | corresponding paired DEV val_cer / 6 | mixture DEV val_cer / 6 |
| Transfer evaluation | final best only | optional `--transfer-mix`, final-only; legacy disclosure when supplied |
| Data gate | historical O5 loose directories, now refused | required C0 manifests |
| Real rows / partition | O5 selected TRAIN/DEV, disjoint TEST | same IDs/texts/docs/exclusions |
| Crop normalization | historical Python resize, symmetric paired right-pad | Rust import-real 48px, aspect preserved, own-background padding, no paired-width padding |
| Strip size / readability | height48, width64..2560, floor14 | same contract |
| Batch widths / update horizon | width buckets; paired widths equal across two arms | packed bucket tails; ceil19657/64 independent of widths |
| Exposure / real f | real-only paired arm | 19657 rows/epoch; f0/.25/.50/.75/1 |
| Synthetic recipe | O5 v1 scheduling override, grandfathered only | **unchanged committed v5**, fully audited |
| Synthetic total / effective TRAIN | O5 paired selected texts | v5 pool200000; TRAIN assembly19657 |
| Synthetic texts | paired O5 TRAIN/DEV | paired TRAIN + provenanced generator sources |
| Validation membership | fixed paired DEV | fixed C0 mixture epoch0; native component pool sizes |
| Reserved text / fonts | real TEST + unchanged transfer_dev_v4 | same + committed v6 synthetic font-OOD |
| Augmentation | existing real crops | real unchanged; synthetic v5 crop+ink settings; v6 clean eval |
| Greek-only / smoke / selftest | false in full run | same |
| Determinism | seed recorded; full determinism not forced | same; runtime flags bound |
| Resume | full state; corrupt attempt restarts from donor | full C0-gated state; rejection fails the arm by default; preset opt-in may archive and restart the same seed **from scratch** |
| Arm P (C4b) | absent | not among the requested15; waits for100-crop conversion check |

No factory training knob is overridden: v5 content, severity/background/polarity,
fonts, lengths, pool caps, reuse, atom floor, spacing, ink fit, contrast, survival,
appearance band, watermarks, exclusions, crop and ink transfer all remain its
committed values. Factory-recipe parameters apply to the synthetic component;
the final assembled mixture is measured, never described as having v5 marginals.

## Coordinator commands on the A100 pod

Review/adopt the source edits bound by `E1_fix3_HANDOFF.json` on the node checkout.
V6 and the C0 fix are now on main; the gate still requires every ordinary
synthetic recipe at HEAD. Copying or staging an uncommitted recipe is insufficient.
Supply the repaired O1 records/crops, authoritative O5 selection/corpus/exclusions,
factory font/watermark assets, local generator corpora, and the unchanged transfer
instrument with a disclosed eval-only manifest if transfer continuity is needed. Use the already-provisioned environment; no online
install/fetch is part of the runner. The coordinator owns the C1/review launch gates.

```bash
cd /path/to/greek-page-ocr
export PYTHON="${VIRTUAL_ENV:?activate the pod environment}/bin/python"
export E1_OUT="$PWD/out/e1"
# Optional: bind the unchanged historical instrument without modifying it:
"$PYTHON" bench/e1_make_legacy_transfer_mix.py \
  --reserved "$PWD/out/transfer_dev_v4/reserved" --out /data/unchanged_transfer_v4_mix.json
"$PYTHON" -m train.mix validate /data/unchanged_transfer_v4_mix.json --role transfer
# Foreground preparation/stages, if the terminal is stable:
bash bench/e1_node.sh --corpus /data/generator_sources.jsonl \
  --transfer-mix /data/unchanged_transfer_v4_mix.json

# Or omit --transfer-mix: training plus real TEST and synthetic held-out only.
bash bench/e1_node.sh --corpus /data/generator_sources.jsonl

# Or start the same stages resilient to a dropped SSH connection:
bash bench/e1_node.sh --launch --corpus /data/generator_sources.jsonl \
  --transfer-mix /data/unchanged_transfer_v4_mix.json
# Poll individual success/failure markers; do not infer success from a silent SSH call:
ls "$E1_OUT"/markers/
tail -20 "$E1_OUT"/logs/supervisor.log
cat "$E1_OUT"/E1_COMPLETE.json
```

Default stages: offline cached factory build + CUDA/provision check; preparation;
mixes/validation; runs; final readout+galleries; completion. Every stage logs under
`out/e1/logs/`, has started/done/failed markers, and binds inputs and output hashes.
An advisory lock prevents two supervisors sharing an output. Rerun the identical
command to reuse verified finished stages/runs/evaluations. `--jobs 1` may be used
on retry after OOM; completed arms remain reusable. Two concurrent foreground
trainer subprocesses are selected only with >=32GiB free GPU memory (16GiB/run
planning allowance, **not a measured memory qualification**). `concurrency.json`
records the actual choice, GPU and free/total memory. The supplied ~40min/run is
an estimate; no A100 timing or memory was measured here. Optimistic two-way
training duration is ~5h20m, excluding rendering, readout, contention and retries.
Immutable concurrency observations for each attempt are retained in logs and
included in report.json, so an OOM retry with jobs1 does not erase the prior choice.

The runner checks both last/best checkpoint archives, configuration, selection
metadata/hash, CSV commit position and prior-epoch marginal counts. Before any
CSV/receipt repair, last.pt must pass C0's unchanged `validate_resume` gate against
the actual existing receipt and a freshly reconstructed CPU E1 plan (trainer
parser/defaults, datasets/samplers, optimizer groups and OneCycle constants; no
forward or optimizer step). Interrupted uncommitted CSV/provenance rows are then
trimmed; committed epochs, exact `checkpoint_updates`, metadata and session history
are retained. Only the trainer appends a continuation session.

The preset recovery rule is **`fail` by default**. A gate rejection writes
`runs/<arm>/recovery.json` and `E1_RUN_FAILED.json` with
`status: blocked_by_resume_gate` and the gate's exact message in `reason`. Rejected
checkpoint/receipt/CSV bytes and mtimes are retained; the arm launches no scratch
trainer. Other custody/completion-check refusals also fail closed, with distinct
statuses. All other arms continue, for either jobs1 or jobs2. `runs_summary.json`
records failed arms; the runs stage fails after all arms finish, so an incomplete
experiment cannot advance to readout or publish E1_COMPLETE.json.

Only a preselected **`--recovery-rule restart-from-scratch`** permits a rejected
attempt to be archived under the arm's recovery directory and initialized again
with the same seed, without `--resume` or `--init-from`. The rule is bound in both
node/run identity and must be selected before the run; changing it requires a
fresh E1_OUT. A CUDA trainer gate refusal after CPU preflight retains the exact
trainer diagnostic and follows the same rule; opt-in permits one fresh launch,
without retrying a fresh trainer failure. No missing legacy bindings or historical
progress values are invented. Completed runs additionally bind both checkpoints,
CSV, metadata and data_provenance bytes. Early-stopped runs are completed and skipped.

## Readout and limitations

`bench/e1_eval.py` validates each instrument manifest before loading Torch. It
uses `train/eval_cer.evaluate` with an optional line observer, the same greedy
decoder and strict `train/cer.levenshtein`, and reference strings decoded from
label_ids. Final evaluation receipts bind best.pt, data provenance, complete
instrument custody, runtime/device/AMP/deterministic flags, scorer, codec,
prediction bytes and materialized crop bytes. Predictions are **not normalized**;
mark ordering errors stay errors. Trusted local runner checkpoints use a temporary
tensor-only wrapper for the unchanged safe inference loader; no checkpoint is
edited and no safetensors installation is required.

Readout writes REPORT.md/report.json for 30 combinations without transfer,
or 45 arm×seed×instrument combinations with transfer:
overall and six script-class CERs; mark precision/recall/error rate, including
per-class marks; seen/held-out/unknown fonts and named fonts; severity, background,
polarity, 128px width buckets, NFD length buckets and crop-augmentation state;
class-specific 3×3 homoglyph matrices;50 worst lines/class/instrument. Galleries
combine the50 worst/class across seeds/instruments into one self-contained HTML
per f, with embedded PNG sprites and escaped GT/prediction/path text.

Mark error rate is `(FP+FN)/reference mark occurrences` on a deterministic strict
edit alignment; common identical prefix/suffix are stripped, then ties prefer
diagonal, deletion, insertion. Circumflex groups U+0342/U+0302 but exact atom
substitutions still count. NA means absent reference support. The pain-point
threshold is strictly `>2×greek_mono CER` on the same arm/seed/instrument: mark
loss/polytonic -> C4 Experiment3 (48 vs64px + training-only guidance); cross-script
classes -> C5 rescoring; unseen fonts -> C4 Experiment2 mixture/f choice. An
absent modern-Greek reference prevents assessment, never yields an invented zero.
This is a diagnostic rule across different denominators, not significance testing.

Page-level CER and detector coverage require the C1 plugin/cohort, which is not
implemented in this checkout. E1 line readout explicitly reports `not_measured`
and maps detector coverage to C1/C2 attribution -> C4 Experiment1. Line errors
cannot establish that page-level result. Full results remain PROVISIONAL until
the requested review and owner-sealed label gates. CPU fixtures certify code/data
contracts; they do not certify production v5 promotion, A100 behavior or OCR quality.

## Offline verification

```bash
CARGO_HOME=/private/tmp/c0-cargo CARGO_TARGET_DIR=/private/tmp/c0fix-target \
  cargo build --offline --locked --release --manifest-path factory/Cargo.toml
C0_FACTORY=/private/tmp/c0fix-target/release/linefactory \
  .venv/bin/python -m pytest -q bench/tests/test_e1.py bench/tests/test_mix.py \
  bench/tests/test_o5.py bench/tests/test_o5_recovery.py bench/tests/test_o5_init.py \
  bench/tests/test_o2.py
.venv/bin/python -m pytest -q bench/tests/test_o5_runtime.py
CARGO_HOME=/private/tmp/c0-cargo CARGO_TARGET_DIR=/private/tmp/c0fix-target \
  CARGO_PROFILE_TEST_OPT_LEVEL=2 \
  cargo test --offline --manifest-path factory/Cargo.toml
bash -n bench/e1_node.sh bench/e1_prepare.sh
.venv/bin/python -m py_compile bench/e1*.py train/train.py train/data.py \
  train/mix.py train/eval_cer.py
```

Current fix totals are recorded in E1_fix_HANDOFF.json. O5 runtime tests run separately
because their legacy flat `train` import collides with the namespace package
already loaded by mix tests in a shared pytest process. Both invocations exercise
the real checks; no tests are skipped to bypass that import layout.

The original E1 implementation suite (before this fix) totalled **125/125 passing checks**:67 Python E1/gate/O5
regression checks,19 separate O5 runtime checks and39 Rust checks. One existing
opt-in Rust gallery test is ignored and excluded from the125 denominator. Bash
syntax, Python compilation and `git diff --check` also pass. The new evaluator
observer is checked with fake CPU logits against the exact scorer inputs and a
breathing/accent swap; no recognizer model or optimization step runs in that test.

E1 tests cover actual Rust preparation on all20 fixture crops and the committed
smoke recipe; actual C0 CLI validation of all five manifests; equal exposure and
packed sampler membership; actual Rust held-out rendering with polytonic/Cyrillic
strata and a supply-shortfall refusal; synthetic-eval training refusal; all mark
metrics and strict ordering; complete fake45-instrument readout and all five sprite
galleries; six-stage dry-run, retries, ordering and altered-output refusal; scratch
commands, corrupt restart, valid CSV/provenance rollback and early-stop receipts;
changed preparation bytes. Current fixtures use read-only HEAD and temporary indexes; the tiny
eval rendering recipe uses the test-only stub described below. No fixture is used as OCR training supervision.

## E1 fix and C0 resume compatibility — 7 October 2026 (historical first fix)

C0 now embeds complete receipt snapshots and manifest hashes in full checkpoints,
checks them before output writes, and preserves prior receipt metadata/HEAD/session
history. E1 recovery invokes C0's receipt reconciliation for last.pt before any
CSV/receipt repair, checks best.pt's snapshot/manifest identities and committed
prefix, verifies fixed validation assembly and even the interrupted next epoch
against the gated mix plan, then
trims only uncommitted epoch/CSV rows. Recovery does not append a session; the
trainer owns that. Missing legacy bindings and mismatched identities/epochs are
archived for a same-seed scratch restart under that historical policy, superseded
by fix 3's default fail rule above. The four trainer validation call sites
now specify train versus transfer role; the C0 resume implementation is preserved.

C0's enriched resolved components include synthetic shard and build-receipt hashes;
these are annotations, not manifest fields. E1 republishes the original supplied
manifest with resolved absolute directory paths, preserving valid manifest fields,
then revalidates it. Both ordinary synthetic and legacy transfer fixtures cover
this compatibility issue. Recovery fixtures exercise no transfer, legacy transfer
and ordinary synthetic transfer, including CSV rollback and corrupt attempted
TRAIN/VAL records.

Tests use existing read-only HEAD, copied temporary indexes and fixture artifacts
in temporary storage; no .git files are written. The tiny eight-row eval rendering
recipe gets a narrowly scoped test-only eligibility stub; it is not asserted to be
committed. Ordinary smoke manifests still pass the actual CLI HEAD gate. No
fixture/model optimization or GPU steps run. A fake final-evaluation observer
checks disclosure propagation and cache reuse without constructing a recognizer.
The root release binary was stale relative to C0; tests use the current source's
offline locked build under `/private/tmp/c0fix-target`, selected by `C0_FACTORY`.

The historical reserved receipt/shards are absent from this Mac checkout. Only
fixtures were bound here; run the helper against the original instrument on the
node. Production preparation/training/quality remain unmeasured in this fix.
Final E1-fix verification totals and file hashes are recorded in
`E1_fix_HANDOFF.json`. Edits remain on main; no network, GPU, background jobs,
production out/ writes or .git writes were performed by this implementation.

Final fix checks: **200/200 executed tests pass**: 140 Python E1/C0/O2/O5
regressions, 2 additional helper immutability cases, 19 separate O5 runtime tests,
and 39 Rust tests. One existing opt-in Rust gallery test is ignored and excluded.
Bash syntax, Python compilation, offline locked release build and diff whitespace
checks pass. Raw logs are under `reviews/E1_fix_evidence/`.

E1 fix 2 (7 October 2026): preparation now projects selected O1 rows to the ten fields read by `import-real` (`crop`, `text`, `source_doc_id`, `line_id`, `script_class`, `split`, `source_dataset`, `license`, `admitted`, `word_tags`), emitting each optional field only when supplied and preserving the existing dataset/license defaults; overlapping serde aliases and unrelated O1 keys never reach the importer. The full selected source rows, including occurrence IDs, page/line numbers and O5 enrichment, are retained in `real_records_source.jsonl` with the selected split, and both JSONL artifacts are SHA-256-bound by the preparation receipt. The importer stores occurrence IDs but no page/line numbers, so those remain in source custody. An offline locked release build under `/private/tmp/e1fix2-target`, selected with `C0_FACTORY`, accepted all 20 fixture crops enriched with `text` plus `gt_nfc` and every other importer alias; the two new regressions verify projection, label/ID/tag preservation and custody-tamper refusal. Only `bench/tests/test_e1.py` ran: the final shared-tree result is 56/59 passing, with three existing recovery cases failing because E1 calls C0's changed `continue_provenance` without its now-required prior receipt; the first run also detected two concurrent trainer-code edits, which disappeared on rerun. No C0-owned files were edited, and no network, GPU or `.git` writes were performed. Use a fresh `E1_OUT` for the changed code binding; file hashes, commands, exact failures and logs are recorded in root `E1_fix2_HANDOFF.json` and `reviews/E1_fix2_evidence/`.

E1 fix 3 (7 October 2026): recovery now calls C0's single `validate_resume` gate
instead of treating `continue_provenance` as a validator. Success fixtures use the
current trainer's real checkpoint writer with directly assigned nonzero progress;
model forwards and optimizer steps are forbidden. They cover absent transfer,
legacy transfer and ordinary synthetic transfer, preserve committed epochs and
sessions, trim epoch3 after checkpoint2, and then pass the actual trainer resume
path. Refusal fixtures check legacy/missing horizon bindings, wrong scheduler
horizon, prior identity, best binding and attempted TRAIN/VAL records, retaining
all existing bytes/mtimes by default and testing archival only under explicit
opt-in. Mocked orchestration tests verify arm continuation and CUDA gate refusal
handling without GPU use. The requested combined E1/mix verification and trainer
immutability hashes are recorded in `E1_fix3_HANDOFF.json`; raw logs are under
`reviews/E1_fix3_evidence/`. No network, GPU computation, production training or
`.git` writes are performed for this fix. Production GPU continuation remains
unmeasured; the C0 trainer/gate source is untouched.

Final fix-3 verification: **149/149 tests passed** (70 E1, 79 C0 mix) in 176.39s
with `C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory .venv/bin/python
-m pytest -q bench/tests/test_e1.py bench/tests/test_mix.py`. The trainer's SHA-256
is unchanged from committed HEAD. Whitespace checks pass. The retained initial
run was interrupted at an incorrect test probe boundary; the intermediate run
passed 148/149 because one orchestration fixture lacked the receipt needed to
reach its intended checkpoint diagnostic. Neither result is added to the final
test count.


## E1 fix 4 — C0 fix-3 hash-bound recovery (7 October 2026)

Recovery uses C0's unchanged `validate_resume` for both `last.pt` and `best.pt`
before repairing the receipt or CSV. Last is checked against the actual receipt,
including the interrupted next epoch. Best is checked against the actual receipt's
committed epoch/update prefix, preserving every recorded `state_sha256`; hashes
are never manufactured for legacy checkpoints. This checks both checkpoint/receipt
hash binding and complete optimizer state through the trainer's own gate.

Recovery fixtures use the trainer's real writer and the existing full-parameter
optimizer-progress helper, with no model forwards or optimizer steps. Epoch 2
retains the writer's epoch-1 digest. Deliberately resealed schedule/provenance and
best-optimizer mutations still exercise semantic refusal; an unresealed best-state
mutation exercises integrity refusal. Success retains hashes, committed epochs,
update counts, metadata and sessions, trims only the attempted epoch/CSV tail, and
passes the actual trainer resume setup. Default refusal retains bytes/mtimes,
marks the arm failed, continues other arms, and launches no silent scratch restart.
The explicitly preset archive/restart option remains covered.

The node run `e1_run4` executes commit `2e3cf6f` (pre-fix-4). Recovery there would
mark the arm failed per the preset `fail` rule if C0's resume gate rejects the
donor; other arms continue and no silent restart occurs. These local edits do not
change the code executing in that run.

`train/train.py` and `bench/e1_driver.py` were not edited by this implementation.
The initial checkout was main at `a228b650237b453f4b9ccefdcdf5317996cfd6fe`.
During verification HEAD advanced externally and the trainer received Astra
recertification edits. Final C0 fix-3 compatibility verification therefore uses
`/private/tmp/e1fix4-snapshot`, containing the starting committed dependencies and
these E1 edits. Its trainer SHA-256 is
`9508594a1747504759dff819542df2d2e72a7adb09597feb81ceb356f828deda`.
The snapshot has detached temporary Git metadata named `git-meta`, with read-only
original object alternates and copied temporary indexes. No original `.git`
writes, network access, GPU work or production training were performed by this
implementation; external trainer/Git changes are preserved and recorded separately.
This verification is for the C0 fix-3 contract, not Astra's subsequent trainer edits.

Raw logs, JUnit results and source identities are under `reviews/E1_fix4_evidence/`;
final counts and reproduction commands are recorded in root `E1_fix4_HANDOFF.json`.
The initial shared-tree result reproduced **25 failed, 162 passed** (187 total) in
271.60s. A shared-tree attempt was interrupted after 28 passes when concurrent
trainer changes were detected. The first frozen run lacked font assets and reported
**20 passed, 173 setup errors** in 9.10s; the tracked assets were added without
changing implementation. Interrupted/setup results are excluded from final counts.

Final fix-4 verification: **193/193 tests passed** (76 E1, 117 C0 mix) in
324.82s, with zero failures/errors/skips. The final frozen-source invocation uses
`C0_FACTORY=/private/tmp/e1fix2-target/release/linefactory .venv/bin/python -m
pytest -q bench/tests/test_e1.py bench/tests/test_mix.py`, with the documented
snapshot Git environment and an additional JUnit output flag. Six best-checkpoint
regressions are new; the original 187 tests all pass. Scoped whitespace and AST
checks pass. Initial, interrupted and setup attempts are not added to the final
193 denominator. The original raw failure log is preserved byte-for-byte as gzip.

## E1 run4 results (7 Oct 2026 23:15)
See `E1_REPORT_run4.md` (headline tables, per-class, pain-point map). Review: CP-E1 (Sol) pending.


## Corrections (CP-E1 cycle 1, 7 Oct 23:30)
- Run4 executed with a DISCLOSED `--allow-deficit` synthetic build (5 Latin mark atoms below floor; furniture −141) and the eval-only `recipe.v7.json` held-out (not v6); earlier paragraphs in this file describing 'no allow-deficit' and v6 are historical design text, superseded for run4.
- Word tags are absent from the galleries and prediction sidecars (M01): to add in the readout before the next round.
