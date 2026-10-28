# TRAIN_FULL_v1 — owner-run commands, PREPARE ONLY handoff

No command here has been submitted or executed remotely by Sol. Preparation is ready. The fetched harvest receipt exists; remote cross-release audit, real requeue smoke, Astra review and owner's launch go remain pending. See [PLAN.md](../../docs/programme_20261025/TRAIN_FULL_v1/PLAN.md).

## Audit fix 2 — redeploy, rebind, fresh full-v1-003

Coordinator reports audit **3747871 completed its scan but BLOCKED** under payload `becab5e065f057c9`, attempt `full-v1-002`: 204,417 registry-resolution failures and 9 crop diagnostics; counts were UNQUALIFIED. Preserve **both 001 and 002**, all receipts/logs/collisions. Sol performed no remote action. The replacement payload is **e3a023657d27bae8ec219afe25289ba7a14fdaee2af35b510131a028efa5079b** (ID `e3a023657d27bae8`).

The fix restores typed `v2_book_id` and full `pdf_sha256` identity lookup, the registry's exact legacy line-prefix parser, and `seal04_dev/test` split roles. All identity namespaces must remain unique. `harvest_protection` constrains new harvest; SHA-bound S1 train membership retains the adopted registry TRAIN assignment. Catalogue/search URLs and page-PDF hashes remain metadata. Eval wins: crop-identical train rows are excluded with witnesses; all eval rows survive, including repeats across eval panels. Independent book/edition/provider/line conflicts still block.

Run on the Mac from this repo:

```bash
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_SHA=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -d ' ' -f1)
test "$TF_SHA" = e3a023657d27bae8ec219afe25289ba7a14fdaee2af35b510131a028efa5079b
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/e3a023657d27bae8
ssh clariden "mkdir -p '$TF_REMOTE'"
rsync -rt --partial "$TF_LOCAL/" "clariden:$TF_REMOTE/"
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

After BOTH full hashes match, run in the Clariden shell. Same successful binding as 002: `--horizon full`, no extra relocations. This creates a new attempt, preserving prior evidence:

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/e3a023657d27bae8
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"
export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-003
test ! -e "$TF_WORK"
mkdir -p "$TF_WORK/controls"
sacct -X -n -P -j 3747846,3747871 --format=JobIDRaw,State,ExitCode,ElapsedRaw > "$TF_WORK/controls/prior-audits-sacct.txt"
TF_HARVEST=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/releases/harvest_20261025_v1
"$TF_PYTHON" -B "$TF_PACKAGE/bind_config.py" \
  --harvest-root "$TF_HARVEST" --horizon full --out "$TF_WORK/data.json"
export TF_DATA_CONFIG="$TF_WORK/data.json"
export TF_PREP_ROOT="$TF_WORK/data"
sbatch --test-only --output="$TF_WORK/controls/audit-%j.log" "$TF_PACKAGE/audit.sbatch"
AUDIT_JOB=$(sbatch --parsable --output="$TF_WORK/controls/audit-%j.log" "$TF_PACKAGE/audit.sbatch")
AUDIT_JOB=${AUDIT_JOB%%;*}
printf '%s\n' "$AUDIT_JOB" | tee "$TF_WORK/controls/audit-job-id.txt"
sacct -X -n -P -j "$AUDIT_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Wait for COMPLETED/0:0, then run the section 2 PASS/readback block and inspect `s1_resolution` (364,871 resolved with matching S1 split, zero unresolved/mismatches), `train_eval_removals.jsonl` and `eval_crop_repeats.jsonl`. The fresh audit, not attempt 002's UNQUALIFIED numbers, determines training counts/horizon. Continue sections 3–5 only after PASS: factory preparation → real forced-requeue smoke → Astra review → owner launch go. No GPU submission is part of this retry.

## 1. Local review and exact package transfer

The coordinator commits if desired; Sol has not staged or committed anything. Preserve the package bytes through smoke and review. Any source/config change requires a new payload seal and fresh review; changing the data requires a new manifest/preparation/smoke binding.

```bash
# Owner shell on this Mac; verify before transferring.
TF_LOCAL=docs/programme_20261025/TRAIN_FULL_v1/package
python3 -B "$TF_LOCAL/verify.py"
TF_ID=$(shasum -a 256 "$TF_LOCAL/PAYLOAD.json" | cut -c1-16)
TF_REMOTE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/$TF_ID
ssh clariden "mkdir -p '$TF_REMOTE'"
rsync -rt --partial "$TF_LOCAL/" "clariden:$TF_REMOTE/"
# Read back the payload SHA and verify EVERY deployed source/registry/config file.
ssh clariden "python3 -B '$TF_REMOTE/verify.py'; sha256sum '$TF_REMOTE/PAYLOAD.json'"
shasum -a 256 "$TF_LOCAL/PAYLOAD.json"
```

The two payload hashes must match. No new Mac dataset/crop transfer is required by this package. Existing crop bytes stay in SHA-verified Clariden custody. Copy only small control/receipt files back later; do not fetch images/shards.

## 2. Bind inputs, then submit the CPU union audit first

Run in the owner's Clariden shell. Set `TF_PACKAGE` to the exact content-addressed path printed above. Confirm the **release-producing** job is COMPLETED/0:0 with its exact job ID before proceeding; the final release must include all eight required waves. Unknown/pending/missing release counts do not clear this gate. The builder refuses a release missing any W5 tranche.

```bash
export TF_PACKAGE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/REPLACE_WITH_TF_ID
source "$TF_PACKAGE/runtime_env.sh"
"$TF_PYTHON" -B "$TF_PACKAGE/verify.py"

# Owner supplies the actual release job ID; retain the exact parent record.
HARVEST_JOB=REPLACE_WITH_RELEASE_JOB_ID
sacct -X -n -P -j "$HARVEST_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw

export TF_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-003
mkdir -p "$TF_WORK/controls"

# Single source switch. For the optional variant, replace ONLY this release root
# with /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_with_gennadius_cached_v4
# after its completion (same release schema), and use a new TF_WORK.
TF_HARVEST=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/releases/harvest_20261025_v1

# Supply a JSON object of exact original crop-prefix -> staged remote prefix.
# Example shape only: {"/Users/.../originals": "/capstor/.../verified-originals"}
# Use the actual S1/crop staging inventory, never a guessed basename/root.
# An empty object is valid only if every old crop path is already valid on Clariden.
TF_RELOCATIONS=/absolute/path/to/owner-verified-crop-relocations.json
"$TF_PYTHON" -B "$TF_PACKAGE/bind_config.py" \
  --harvest-root "$TF_HARVEST" --relocations "$TF_RELOCATIONS" \
  --horizon full --out "$TF_WORK/data.json"
# Explicit alternatives: --horizon s1-literal (53,616 updates), or longer (12 full-pass epochs).
# Each requires its own TF_WORK and new audit/preparation/smoke/review. Default is full.

export TF_DATA_CONFIG="$TF_WORK/data.json"
export TF_PREP_ROOT="$TF_WORK/data"
# Exact scheduler dry check, then the same options on actual submit.
sbatch --test-only --output="$TF_WORK/controls/audit-%j.log" "$TF_PACKAGE/audit.sbatch"
AUDIT_JOB=$(sbatch --parsable --output="$TF_WORK/controls/audit-%j.log" "$TF_PACKAGE/audit.sbatch")
AUDIT_JOB=${AUDIT_JOB%%;*}
printf '%s\n' "$AUDIT_JOB"
sacct -X -n -P -j "$AUDIT_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

The audit requests **zero GPUs**, a0140/preemptable/8CPUs/80m, `--requeue`. It hashes releases in place, including every crop, both metadata layouts, exact labels and the book/edition/provider registry joins. On preemption incomplete output is preserved and the scan restarts; a finished stage is reused only under the same config/package/output identities. An80m cap is a bounded operational choice, not a measured audit runtime; inspect retained logs if it cannot finish. No native factory, training, upload or release edit occurs in this job.

Wait for the exact audit parent to be **COMPLETED/0:0**; retain its fresh `sacct` output in controls. Inspect `data/AUDIT_COMPLETE.json` and `data/manifest/AUDIT.json`. The audit includes true `train_unique`, `dataset_unique_crops`, distinct-crop counts by split/source/class, input/retained tables, S1 source/class deltas and exact horizon alternatives. `collisions.jsonl` retains all detected row conflicts and `duplicates.jsonl` retains deterministic duplicate witnesses. Any blocking collisions mark counts UNQUALIFIED and prevent training-manifest publication. Path/SHA/schema failures retain `AUDIT_FAILED_*.json`. Only the authorized crop-based train exclusion is applied; no eval row is filtered or reassigned. Crop repeats in eval are recorded separately as diagnostics.

```bash
# Only after COMPLETED/0:0 and AUDIT_COMPLETE PASS for this config/package.
sacct -X -n -P -j "$AUDIT_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw > "$TF_WORK/controls/audit-sacct.txt"
"$TF_PYTHON" -B - "$TF_PREP_ROOT" <<'PYCHECK'
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
c=json.loads((root/'AUDIT_COMPLETE.json').read_text())
a=json.loads((root/'manifest/AUDIT.json').read_text())
assert c['status']=='PASS' and not c['fixture']
assert a['status']=='PASS' and a['collisions']==0
assert a['s1_resolution']==dict(input_rows=364871, resolved_split_matches_s1=364871, unresolved_or_split_mismatch=0)
print(json.dumps({k:a[k] for k in ('train_unique','dataset_unique_crops','dataset_unique_by_split','horizons','s1_resolution','train_eval_removed_rows','eval_crop_repeat_rows')},indent=2))
PYCHECK
```

Record the true count and exact default update/evaluation steps in PLAN/the Astra review. **782,151 train /195,544 updates is only the no-overlap projection.** At this stage the CPU audit, not the raw sum, supplies the final numbers. Copy back small audit summary receipts only; retain full witness/prediction/row files remotely.

## 3. CPU factory preparation, using the audited manifest

Submit after the authenticated completed audit. There is **no afterok on its possibly purged job ID**; retained sacct proof and the bound completion receipt establish completion. `prepare_job.py` verifies the audit's package/config/manifest and refuses missing or fixture clearance.

```bash
sbatch --test-only --output="$TF_WORK/controls/prepare-%j.log" "$TF_PACKAGE/prepare.sbatch"
PREPARE_JOB=$(sbatch --parsable --output="$TF_WORK/controls/prepare-%j.log" "$TF_PACKAGE/prepare.sbatch")
PREPARE_JOB=${PREPARE_JOB%%;*}
printf '%s\n' "$PREPARE_JOB"
sacct -X -n -P -j "$PREPARE_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Prepare requests zero GPUs, a0140/preemptable/24CPUs/4h and requeue. It reuses S1 tensors, imports only harvest through the frozen factory, and requires exact row coverage. Any codec/shape/appearance drop stops for inspection. It verifies one real draw per unique row under unchanged S1 quotas and binds the resolved epoch/update/scheduler horizon into `prepared/runtime.json`. Partial output is preserved; complete SHA-bound stages are reused.

Wait for **COMPLETED/0:0**, retain its sacct proof, then inspect `PREPARE_COMPLETE.json`, full `MANIFEST.json` counts and `runtime.json.horizon`/`full_pass_check`. No GPU submission follows from a failed job or a missing receipt.

```bash
export TF_RUNTIME="$TF_PREP_ROOT/prepared/runtime.json"
"$TF_PYTHON" -B "$TF_PACKAGE/readout.py" \
  --manifest "$TF_PREP_ROOT/manifest/MANIFEST.json" --runtime "$TF_RUNTIME" \
  --out "$TF_WORK/OWNER_READOUT_BEFORE_SMOKE.json"
```

## 4. Real width ×2 smoke and forced scheduler requeue

These commands request bounded real GPU work; the owner runs them after checking the actual data and allocation budget. They use preemptable, so there is no normal/debug fallback. Each requests one GPU/exclusive node/24 CPUs/80m. They run the actual model and six-worker S1 profile on the **final full population**, with 2 epochs ×128 mixed draws, batch64, four updates total. The four complete instruments are evaluated at steps2 and4. Only the tiny horizon/cadence is diagnostic. Keep the final runtime immutable.

```bash
CONTROL_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/smoke-control" \
  --controls "$TF_WORK/controls/smoke-control" --mode smoke-control)
REQUEUE_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/smoke-requeue" \
  --controls "$TF_WORK/controls/smoke-requeue" --mode smoke-requeue)
printf '%s\n' "$CONTROL_JOB" "$REQUEUE_JOB"
sacct -X -n -P -j "$CONTROL_JOB,$REQUEUE_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

`chain.py` verifies package bytes and performs exact `sbatch --test-only` before each submit. The requeue smoke publishes step2's full checkpoint/eval, returns planned yield75, and its wrapper executes `scontrol requeue` once. The next allocation must have the same job ID and `SLURM_RESTART_COUNT >=1`; forced split is then disabled. Appended Slurm logs and per-restart allocation receipts preserve both legs. No manually created PASS can replace these records.

Wait for both actual parents to reach COMPLETED/0:0. If the smoke cannot finish all instruments within80m, retain evidence, measure the bottleneck and ask the coordinator to revise the bounded request; do not silently reduce the instruments. Then:

```bash
"$TF_PYTHON" -B "$TF_PACKAGE/compare.py" \
  --control "$TF_WORK/smoke-control" --resumed "$TF_WORK/smoke-requeue" \
  --out "$TF_WORK/SMOKE_IDENTITY.json"
"$TF_PYTHON" -B "$TF_PACKAGE/readout.py" \
  --manifest "$TF_PREP_ROOT/manifest/MANIFEST.json" --runtime "$TF_RUNTIME" \
  --smoke-control "$TF_WORK/smoke-control" --out "$TF_WORK/OWNER_READOUT.json"
```

`compare.py` requires real CUDA/width2/six-worker state, ≥2 evals, actual restart records, identical data, and BIT_IDENTICAL model/optimizer/scheduler/RNG/cursor/health/draw/loss traces plus equal instrument metrics. It refuses mock results. Refresh all scoped parent-only S1/wave accounting before launch; include failed/retried/active allocations and avoid counting Slurm steps twice. Historical118.995/350 GPU-h is not a live balance. `OWNER_READOUT.json` adds the measured full-evaluation cost to the S1 throughput projection; queue/preemption tails remain separate.

Fetch small receipts/logs only: OWNER_READOUT, AUDIT_COMPLETE, manifest/AUDIT.json, PREPARE_COMPLETE, MANIFEST (summary, without large train/rows files), SMOKE_IDENTITY, COMPLETE/eval JSON, ALLOCATION/SEGMENT_TRACE JSON and scoped sacct proofs. Keep prediction files on Clariden unless specifically needed for review.

## 5. Astra review, then owner launch go

Provide Astra the verbatim brief, PLAN/recipe table, payload SHA/readback, actual union counts/leakage/dedupe receipts, tests and offline mock disclosure, both real smoke logs/receipts, BIT_IDENTICAL result and fresh GPU accounting. No Astra review was performed by Sol in this handoff. The reviewer/coordinator issues a review JSON only after its review, with this structure:

```json
{
  "verdict": "PASS",
  "package_sha256": "ACTUAL_SHA256_OF_PAYLOAD_JSON",
  "runtime_sha256": "ACTUAL_SHA256_OF_FINAL_RUNTIME_JSON",
  "smoke_identity": {
    "path": "/absolute/Clariden/path/SMOKE_IDENTITY.json",
    "sha256": "ACTUAL_SHA256_OF_SMOKE_IDENTITY_JSON"
  },
  "reviewer": "Astra",
  "review_record": "exact retained review record"
}
```

The example is a schema, not an issued PASS. Test-only full job request checking may be reviewed now without owner launch go; `chain.py` itself requires the actual Astra PASS/data/smoke binding and explicit `--owner-go` for submission. Run the next block **only after the owner's separate launch go**:

```bash
TRAIN_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/train" \
  --controls "$TF_WORK/controls/train" --mode train \
  --review "$TF_WORK/ASTRA_REVIEW.json" --owner-go)
printf '%s\n' "$TRAIN_JOB"
sacct -X -n -P -j "$TRAIN_JOB" --format=JobIDRaw,State,ExitCode,ElapsedRaw,ReqTRES
```

Default: **epoch_rows=2 × audited unique real TRAIN**, eight epochs, total **8 ×ceil(2U/64)** updates; archived four-instrument loss+CER every50,000 updates and final. At nominal U=782,151 this is **195,544 updates**, evals50k/100k/150k/195,544 and ≈**24.42h +4E/3600** from historical S1 timing. Only AUDIT/OWNER_READOUT can supply the actual final U/horizon/forecast. OneCycle is initialized over that horizon; no extension in place. The fixed53,616-update S1 recipe is the alternative, not default.

Nominal default requires **at least three12h segments**, before measured evaluation/restart tails. Three segments +two80m smokes request38.667 GPU-h against the historical231.005 remaining; live accounting must clear the actual chain. The12-epoch full-pass alternative projects293,316 updates and≈36.60h +6E/3600, at least four12h requests. CPU audit/factory time and queue delay are separate.
Prepare enough chained12h requests for OWNER_READOUT's measured-cost projection within the refreshed budget; the nominal default already exceeds24h. Chain in advance while a predecessor is active, or submit the next segment after its authenticated yield. The same owner-go covers the explicitly authorized chain only. Example next segment (for a running predecessor or authenticated COMPLETED/0:0 yield):

```bash
NEXT_JOB=$("$TF_PYTHON" -B "$TF_PACKAGE/chain.py" \
  --runtime "$TF_RUNTIME" --out "$TF_WORK/train" \
  --controls "$TF_WORK/controls/train" --segment 2 --prior "$TRAIN_JOB" --mode train \
  --review "$TF_WORK/ASTRA_REVIEW.json" --owner-go)
```

An active predecessor keeps `afterok`; an already COMPLETED/0:0 predecessor gets **no dependency**, backed by retained sacct proof and bound yield checkpoint. FAILED/CANCELLED/unknown parents refuse. Do not delete or overwrite submission intents after an ambiguous response; inspect the actual scheduler record. Hard preemption requeues the same job and loads the latest atomic checkpoint. A complete run requires `train/COMPLETE.json`, every specified checkpoint eval and actual final parent accounting, not scheduler success alone.

TRAIN_FULL READY (pending remote union audit, smoke/Astra/owner go). No remote command above has been run by Sol.
