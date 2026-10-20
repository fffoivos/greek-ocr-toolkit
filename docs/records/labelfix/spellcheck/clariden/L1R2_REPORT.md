# L1R2 — SF5 recomposition and HOLD / deletion census

17 October 2026. **READY: both jobs prepared, mocked, deployed, SHA-checked and scheduler-tested. No job submitted.** Policy `sf5-release-v1`; 8,784/8,784 input files and 974/974 shards verified; 256/256 mode/line and 7,620/7,620 slot/mode decisions match; 908 labelfix tests pass; 324/324 deployed files match locally and remotely.

Worktree `greek-ocr-toolkit-spellcheck-l1r2`, branch `opus/spellcheck-l1r2`, actual HEAD `c1d5f7fd423ebf88823007d957220fcee5cedf0c`. The sole commit above the brief's `39f7dedd` adds `docs/records/briefs/L1R2_sf5_recompose_job.md`. The gate, text, reading, segmentation and **entire merged `l1_common.py`** retain their starting bytes. Five frozen source files plus eight Git metadata files were hash-checked unchanged ([protected receipt](L1R2_evidence/protected_unchanged.json), [starting hashes](L1R2_evidence/protected_before.json)). No Git writes or other-worktree writes were made.

The requested [CSCS skill](/Users/foivoskarounos-zamparloukos/.claude/skills/optimize-apertus-cscs/SKILL.md), [L1R report](L1R_REPORT.md), [L1C report](L1C_REPORT.md), and [L1A audit](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/L1A_AUDIT_REPORT.md) were read. This is experiment-owned CPU packaging/analysis; canonical lifecycle tooling was not changed. The explicit Clariden-only network and no-other-worktree constraints exclude a canonical-repository fetch. External network access was limited to Clariden SSH/SCP. No SSH transient or authentication/certificate failure occurred; no certificate refresh occurred. The inspected certificate expires at 19:18:52 local Mac time.

## Frozen policy and packaging

| File | SHA-256 |
|---|---|
| `greekocr/labelfix/release_gate.py` | `b1137154ca1dce903967cd86974a83abae6e690dd818d21dc5ecf8eaf058a9c9` |
| `greekocr/labelfix/text.py` | `b2fbe9cf6d8c97d1f8e06e149bfe4e11cc58b9b4f2bb323bddc8afce2ca52c92` |
| `greekocr/labelfix/reading.py` | `6b2838a31e17960a03b2080bc7b23a68d8b58995490ca22e7761406ab8941518` |
| merged `scripts/labelfix/clariden/l1_common.py` | `1b5596908eda61915b36cad2f821dc654353cbb5009b534231767c482c08d6d4` |

The merged common consumer already adds `composed_text`, slot `parts` and verified-source hash reuse to the SF5 version; those supplied bytes remain frozen. The source-bound policy digest for this package is `9d427223b5e7c8dfa6333805757f92a7abfddbb747a23d5c72c6ef943d137ced`. Its change from the original SF5 measurement digest binds the supplied merged adapter and the revised `l1r_recompose.py` packaging. It does not change gate rules. [Remote policy](L1R2_evidence/remote_readback/preflight/policy.json).

Job 1 uses the same [`l1r_recompose.py`](../../../../../scripts/labelfix/clariden/l1r_recompose.py) entry point, input verifier, 32-worker shard composition and durable exact-binding receipts as L1R. Packaging now names all corrected/control releases with `-sf5`, sums `alias_only` across **all shards**, preserves its wave/source coverage counts, and sums the frozen overlay elision census. Every corrected/control manifest has `elision_census` for all in-scope proposals and `elision_census_released` for accepted labels, with explicit aligned/unaligned line totals. Held proposals are therefore distinguishable from released deletions. The optional mock audit now retains the complete full-composer decisions, including every slot field.

Release names are `v2-corrected-presence-sf5`, `v2-corrected-full-sf5`, `v2-corrected-ensemble-ab-sf5`, paired with `v2-ctrl-subset-{presence,full,ensemble-ab}-sf5`. Original-label SHA, exact control/kept-ID pairing, input verification, source/checkpoint/exclusion/R0 provenance and HOLD exclusion remain enforced. Every corrected/control manifest carries this caveat verbatim:

> A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment.

Outputs are siblings of the historical SF4 outputs:

```text
.../labelfix_l1_20261017/l1e_20261017/l1r_sf5_<JOB1>/
  input_verification.json
  shards/shard-NNNNN/{selection.jsonl,release/*,receipt.json}
  release/{overlay_*.jsonl.gz,ctrl_subset_*.jsonl.gz,kept_*_line_ids.txt,release_*.json}
  receipt.json
```

The coordinator's SF4 **NOT USABLE** ruling remains in force; this package does not edit or reuse SF4 release payloads.

## Inputs verified in place

Deployment root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf5/`.

The production config is byte-identical to L1R's audited config: [config](L1R2_evidence/remote_readback/config/l1r_job.json). Inputs remain L1-v0 `output_3679313/`, L1E `l1e_20261017/output_3679545/inference/`, the bound original selection and `collection_v2/import_real_v2_train.jsonl`.

The deployed entry point ran `--verify-only --workers 4` on Clariden: **124,669 lines, 974 shards, 2,901,998 samples; 8,784 input hashes; 13.338 s**. Its complete hash map is **identical to L1R's verified input map**. This checks the complete historical run, all detector payloads, A and B/E inference shards, completion/population/selection/checkpoint identities and per-shard receipt bindings. The job repeats it before composing, then rehashes inputs before its final seal. No training-population data was processed locally or transferred to the Mac.

[Full input audit](L1R2_evidence/remote_readback/preflight/input_verification.json), [audit log](L1R2_evidence/remote_readback/preflight/input_verification.log), [input/deploy comparison](L1R2_evidence/deploy_verification.json).

Six separately pinned external inputs passed SHA checks: L1-v0/L1E top receipts, the SciPy manifest, and A/B/E checkpoint files ([external manifest](L1R2_evidence/L1R2_EXTERNAL_SHA256.txt), [remote check](L1R2_evidence/remote_readback/preflight/external_verify.log)). The existing `venv_l1` SciPy manifest passed in place; SciPy **1.17.1** imports from that venv under Python 3.12 ([runtime/import log](L1R2_evidence/remote_readback/preflight.log)). No installation or environment mutation occurred.

## Job 2 — analysis only

[`l1r2_census.py`](../../../../../scripts/labelfix/clariden/l1r2_census.py) sequentially runs:

1. [`l1c_census.py`](../../../../../scripts/labelfix/clariden/l1c_census.py): only policy acceptance/hash correspondence changes; the counting, exact-detail deduplication, families, ALONE logic, global top ten, six explicit waves and source coverage checks are unchanged. SF4 verification remains supported, with its original pinned gate. Job 2 passes the exact SF5 directory explicitly, bypassing the historical SF4 job-ID resolver.
2. [`l1r2_changes.py`](../../../../../scripts/labelfix/clariden/l1r2_changes.py): original v2 `selection.jsonl` labels versus actual corrected overlay `label`, using NFD `difflib.SequenceMatcher(..., autojunk=False)` for every corrected-status line in each mode/wave.

The reported correction count is **`real_mark_correction_lines`**: at least one combining-mark insertion/deletion. `corrected_status_lines` is retained solely as a release-status accounting denominator. Both real-mark and raw-status shares of lines with any single-source deletion are available; the Markdown table leads with the real-mark denominator.

Word-final **and lowercase consonant-initial** elision aliases are comparison-folded, including `᾿στὸν → 'στὸν`; aliases never become real mark corrections. Spacing breathings before capitals/vowels are kept distinct. Each deleted/inserted NFD codepoint is classified as combining mark, numeral keraia, elision apostrophe, quote, other mark, base letter, whitespace or other. Keraia includes U+0374/U+0384/U+02B9 and apostrophes after uppercase Greek numeral tokens (including `Ι'`), decimal tokens or Unicode numeral letters. Opening quotes are included, including unpaired ASCII quotes before capitals/vowels. Bare lowercase ASCII apostrophes can be numeral/elision ambiguous; the deterministic rule retains them as elisions rather than treating ordinary `μ'`/`κ'` as numerals. These are orthographic classes, without new print adjudication.

Source support compares the original atom with the recogniser at the same letter boundary and occurrence, requiring equal letter skeletons. Deletions are partitioned into single-source and shared; all combining-mark deletions are also explicitly visible. Insertions have the same character classes. Alias substitutions count one edit; a combining-mark replacement counts one deletion plus one insertion. Line counts deduplicate within each class. Global lexically sorted example IDs retain up to 20 per class/mode/wave. Aggregate class marginals overlap the separate real-mark totals and should not be added together.

Consensus-elision deletion is independently counted at shared original/recogniser letter boundaries. **Any nonzero count writes diagnostic counts with an incomplete receipt and fails Job 2**. It never changes a label or the frozen policy.

Each analysis verifies the complete Job 1 aggregate/shard output DAG before and after counting, including original-label hashes, manifests, selections, controls and kept IDs. Exact code/input-bound shard partials support restart; corruption fails closed. The combined receipt is sealed only after both analyses complete. A replacement allocation can reuse partials only with the same input, code and explicit earlier `--out` directory. No gate/reader/detector module is imported by the census.

```text
.../labelfix_l1_20261017/l1r_sf5/census/output_<JOB1>_<JOB2>/
  hold/{CENSUS.json,CENSUS.md,binding.json,input_verification.json,partials/*,receipt.json}
  changes/{CHANGES.json,CHANGES.md,binding.json,input_verification.json,partials/*,receipt.json}
  receipt.json
```

## Exact-entry-point mocks and tests

Only the existing complete 64-line saved A/B/E verification runtime was copied from L1R, with **all 15 fixture hashes checked first** ([copy receipt](L1R2_evidence/mock_input_copy.json)). Its two SF4-pinned runtime hashes are unchanged. No inference or detector ran.

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1r_mock_check.py \
  --config artifacts/labelfix_l1r2/mock.json \
  --out artifacts/labelfix_l1r2/mock_ready \
  --evidence docs/records/labelfix/spellcheck/clariden/L1R2_evidence

PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1r2_census.py \
  --input-dir artifacts/labelfix_l1r2/mock_ready \
  --out artifacts/labelfix_l1r2/mock_ready_census --workers 2
```

The exact Job 1 entry point finished in **3.426 s**, including the optional complete four-mode decision audit. **256/256 mode/line and 7,620/7,620 slot/mode decisions** match SF5's full composer, with full decision-object equality. The three emitted releases additionally match **192/192 mode/line and 5,715/5,715 slot decisions**, plus effective label/status/accepted alias and elision-census parity with `scripts/labelfix/sf5_measure.py`. Unchanged releases retain the original label bytes, as the frozen consumer requires. [Parity receipt](L1R2_evidence/mock_parity.json), [successful mock log](L1R2_evidence/mock_ready.log).

The exact combined Job 2 entry point finished in **0.253 s**; both component receipts and the combined receipt are complete. [Combined receipt](L1R2_evidence/mock_census_receipt.json), [HOLD JSON](L1R2_evidence/mock_hold_CENSUS.json), [HOLD Markdown](L1R2_evidence/mock_hold_CENSUS.md), [change JSON](L1R2_evidence/mock_changes_CHANGES.json), [change Markdown](L1R2_evidence/mock_changes_CHANGES.md), [independent sums/line-count checks](L1R2_evidence/mock_independent_checks.json).

| Mode | Mock real mark-correction lines | HOLD lines | Accepted alias-only | Real mark lines with single-source deletion | Share | Consensus elisions deleted |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | 14 | 49 | 0 | 8 | 57.14% | 0 |
| FULL | 11 | 53 | 0 | 7 | 63.64% | 0 |
| ENSEMBLE_AB | 17 | 43 | 1 | 12 | 70.59% | 0 |

All mock single-source deletions are combining marks (9/8/15 edits); no mock keraia, elision or quote deletion occurred. These are verification-runtime counts, not production-population estimates. Ten [synthetic cases](L1R2_evidence/deletion_synthetic.json) cover keraia (including `Ι'`), opening quote, both alias positions, a retained consensus elision, a deliberately deleted consensus elision, single-source elision and insertion classes. The deliberate consensus deletion is detected; an integration test also confirms that it fails the zero gate and leaves an incomplete diagnostic receipt. Two-shard tests expose first-shard-only alias/census aggregation, plus exact restart and corruption refusal.

**908 passed in 9.69 s**, no skips, deselections or errors ([final all-labelfix log](L1R2_evidence/tests_labelfix_final.log)):

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  -m pytest -q tests/labelfix -p no:cacheprovider
```

Both sbatch scripts pass `bash -n`; remote Python parses the exact entry points; `git diff --check` passes.

## Deployment and scheduler checks

**324/324 files** passed remote SHA checks before and after the scheduler probes. The remote `L1R2_DEPLOY_SHA256.txt` is byte-identical to the local file; its SHA-256 is **`7392878d8752abd67246f17b3a6cd6e1c9ab42ae9a400615c3e5cb4a09fa6f77`**. All **321 source-map entries** match the local mock source tree exactly. [Deploy manifest](L1R2_evidence/L1R2_DEPLOY_SHA256.txt), [verification receipt](L1R2_evidence/deploy_verification.json), [final remote SHA check](L1R2_evidence/remote_readback/preflight/test_only_deploy_after.log), [source map](L1R2_evidence/remote_readback/preflight/code_sources.json).

The first Mac tar transfer included AppleDouble metadata sidecars. The 362 generated sidecars were moved, without deletion, into `preflight/macos_metadata/` outside the deployed source directories. Final source-map and manifest checks then passed exactly; the sidecars are neither imported nor part of the job code map. [Relocation receipt](L1R2_evidence/remote_readback/preflight/metadata_relocation.json).

Job 1 [`l1r_job.sbatch`](../../../../../scripts/labelfix/clariden/l1r_job.sbatch): account `a0140`, `debug`, one exclusive node, one task, 64 CPUs, 32 workers, one-hour limit. Job 2 [`l1r2_census_job.sbatch`](../../../../../scripts/labelfix/clariden/l1r2_census_job.sbatch): same account/partition, one node/task, 16 CPUs/workers, 30-minute limit. Neither runs GPU inference. Live `debug` is UP with a 01:30:00 cap; debug QoS permits one running and two submitted jobs per user ([live probe](L1R2_evidence/remote_readback/initial_probe.log)).

Successful probes at cluster time `2026-10-17T04:26:50+02:00`:

```bash
sbatch --test-only scripts/labelfix/clariden/l1r_job.sbatch
sbatch --test-only scripts/labelfix/clariden/l1r2_census_job.sbatch 3679725
```

```text
sbatch: Job 3680623 to start at 04:26:50 a using 288 processors on nodes nid007648 in partition debug
sbatch: Job 3680624 to start at 04:26:51 a using 288 processors on nodes nid007648 in partition debug
```

These IDs are **scheduler test predictions, not submitted jobs**. The attempted Job 2 test using `--dependency=afterok:3679725` returned `Job dependency problem`: the completed historical job is no longer an available scheduler dependency. The exact second payload then passed without that stale dependency. A future Job 1 ID cannot be validated before Job 1 is submitted; the coordinator command below supplies that real ID. [Full test-only transcript](L1R2_evidence/remote_readback/test_only_final.log), [scheduler receipt](L1R2_evidence/scheduler_verification.json). Deployment/config/script hashes remained unchanged across testing; the final `squeue` contains only its header ([readback](L1R2_evidence/remote_readback/preflight/squeue_after.txt)).

Planning estimate: **15 minutes total after allocations start**, allowing about 10 minutes for recomposition and 5 for both census passes, hashing and filesystem overhead. The provided successful L1R/L1C times were 7 minutes and 33 seconds; the new census adds a second verified traversal and NFD analysis. This is a conservative planning estimate, not a measured full-population SF5 runtime. Durable partials preserve completed work after a timeout. Queue delay is additional.

## Coordinator submit commands — prepared, NOT executed

Run on Clariden only when the coordinator authorizes submission. These capture the **actual** Job 1 ID and bind Job 2 with `afterok`; do not use either test-only prediction above.

```bash
set -euo pipefail
L1R2_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf5
cd "$L1R2_ROOT"
sha256sum --check L1R2_DEPLOY_SHA256.txt
JOB1=$(sbatch --parsable scripts/labelfix/clariden/l1r_job.sbatch)
JOB1=${JOB1%%;*}
JOB2=$(sbatch --parsable --dependency=afterok:"$JOB1" \
  scripts/labelfix/clariden/l1r2_census_job.sbatch "$JOB1")
JOB2=${JOB2%%;*}
printf 'L1R2_JOB1=%s\nL1R2_JOB2=%s\n' "$JOB1" "$JOB2"
```

## Pull manifests and census — after completion

Run on the Mac in this worktree, replacing the two values with the real submitted IDs. This pulls small manifests/census/receipts, without overlays, corpora, inference shards or detector arrays.

```bash
JOB1=REPLACE_WITH_REAL_JOB1
JOB2=REPLACE_WITH_REAL_JOB2
L1R2_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R2_RELEASE="$L1R2_BASE/l1e_20261017/l1r_sf5_$JOB1"
L1R2_CENSUS="$L1R2_BASE/l1r_sf5/census/output_${JOB1}_${JOB2}"
L1R2_LOCAL="docs/records/labelfix/spellcheck/clariden/L1R2_evidence/production_${JOB1}_${JOB2}"
mkdir -p "$L1R2_LOCAL/release" "$L1R2_LOCAL/census/hold" "$L1R2_LOCAL/census/changes"
scp "clariden:$L1R2_RELEASE/release/release_*.json" "$L1R2_LOCAL/release/"
scp "clariden:$L1R2_RELEASE/receipt.json" "clariden:$L1R2_RELEASE/input_verification.json" "$L1R2_LOCAL/"
scp "clariden:$L1R2_CENSUS/receipt.json" "$L1R2_LOCAL/census/"
for L1R2_FILE in CENSUS.json CENSUS.md receipt.json; do
  scp "clariden:$L1R2_CENSUS/hold/$L1R2_FILE" "$L1R2_LOCAL/census/hold/"
done
for L1R2_FILE in CHANGES.json CHANGES.md receipt.json; do
  scp "clariden:$L1R2_CENSUS/changes/$L1R2_FILE" "$L1R2_LOCAL/census/changes/"
done
```

L1R2 READY: policy sf5-release-v1; inputs verified ok (8784/8784 files, 974/974 shards); mock parity 256/256; deploy sha256 324/324; test-only 3680623/3680624; est 15 min
