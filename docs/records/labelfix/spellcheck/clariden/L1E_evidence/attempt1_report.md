# L1E — preparation stopped on SSH failure

**NOT READY.** At 01:51 Athens on 17 October 2026, SSH failed during banner exchange. The coordinator's instruction was “if ssh fails, STOP; never refresh.” Clariden operations were stopped, including an in-flight transfer. No certificate refresh was attempted. No Slurm job was submitted. Final deployment verification and `sbatch --test-only` have not run.

The checkout head was `e48e06e8`: the L1E brief commit immediately after SF2 `0472a908`. No Git mutation commands were run; no other worktree was modified.

## Code and tests

`greekocr/labelfix/release_gate.py` implements PRESENCE, FULL, ENSEMBLE_AB and diagnostic ENSEMBLE_AE. A supplies names; B/E must supply an identical mark set. Ensemble modes drop the detector mark-kind veto and retain reader uncertainty, missing predictions/coverage, detector localisation/segmentation/unnamed/clipping states, K1 flags, punctuation evidence and the edit guard. Release, measurement and page adapters call this shared implementation.

`scripts/labelfix/clariden/l1_infer.py` is a byte-identical copy of L1-v0's inference module. L1E imports its unchanged `predictions()` function. B loads with `embedding=False`; E with `embedding=True`. Checkpoint loading checks SHA-256, arm identity and strict model compatibility. Inference uses fp32, TF32 disabled and no autocast.

`l1e_windows.py` audits historical receipts, every stored window hash/shape, exact line identities and every scored extraction start. Its repair path writes into a new directory and requires unchanged L1 extraction to reproduce historical samples, coverage and the original wide-array hash.

`l1e_run.py` prepares window-audit and per-shard inference receipts, then calls the extended SF2 `l1r_recompose.py`. Recomposition is configured for PRESENCE, FULL and ENSEMBLE_AB, with new overlays, kept IDs, paired original-label controls, wave/source coverage, exclusions, checkpoint/code/policy hashes and the mandatory caveat. This integrated path remains **unverified** until the CPU mock completes.

The complete local suite passed: **380 passed in 7.08 seconds**. See [tests.log](L1E_evidence/tests.log). Tests include agreement/disagreement, all requested uncertainty classes, detector-kind disagreement, edit guard, detector punctuation, page/runtime parity, control pairing, checkpoint identity failures, immutable historical outputs and corrupted/missing/unaccounted windows. The parallel release branch is covered with two workers.

## Held-out instrument

The 666-line audit runs on Clariden using saved A/B/E predictions, S6 detector evidence and the **frozen S4 ownership/truth instrument used by R1 RESULT**. Using S6 ownership instead would change the known-error denominator to 81; frozen S4 ownership reproduces 80.

The older R1 extraction lacks `evidence_state` and `uncertainty`. An initial conservative audit therefore held all 80 errors; that intermediate result is **not the final L1E table**. Its receipt remains in [heldout_receipt.json](L1E_evidence/heldout_receipt.json) for provenance.

The final measurement adapter recovers the exact unchanged `extract_line` observation predicates from recorded `pixel_measurements`, original spans and hash-bound PNG header widths, without decoding or extracting pixels. Missing font measurements cause failure, never a default clean state. A revised 666-line audit completed remotely, but its table and 64-line fixture were **not retrieved and read back before the SSH stop**.

| Mode | Corrected / 80 | Wrong | Missed | HOLD errors | New | Lines held / 666 |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | pending retrieval | pending | pending | pending | pending | pending |
| FULL | pending retrieval | pending | pending | pending | pending | pending |
| ENSEMBLE_AB | pending retrieval | pending | pending | pending | pending | pending |
| ENSEMBLE_AE | pending retrieval | pending | pending | pending | pending | pending |

The brief's historical PRESENCE reference is `48/2/5/50`; it is not asserted as a verified result of this revised SF2 measurement.

Remote measurement directory: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/heldout_v4/`. Its `measurement_receipt.json`, `observation_recovery.json`, `events.jsonl`, `decisions.jsonl.gz` and `mock/` require retrieval/readback after the coordinator permits further access.

## Stored windows — verified

The completed read-only audit verified **all 124,669 lines, 2,901,998 windows and 974 shards**, with **zero missing or repaired shards**, in **295.889 seconds**. Receipt: [windows_receipt.json](L1E_evidence/windows_receipt.json).

| Binding | SHA-256 |
|---|---|
| Historical run receipt | `2042fd48b6250636e7847d3b6a1cd6f8a3111dd31575af30c198e63e4d6062bc` |
| Historical detector receipt | `5fcd1baa9eb05a621399a04f9dfdaad68130f5772c945836cdbe9813248ebf04` |
| Selection | `ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec` |
| A checkpoint | `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` |
| B checkpoint | `f25f16e633966ec16037099e27ee75624b9a3600d96682dca654aeded9396d69` |
| E checkpoint | `330b43a04dc47425d3da977f06f28aaa54bee681700d81feef0bcb8ea1ed42c5` |
| Unchanged L1 inference | `0710ca4c41c13b6804dcd8beacf16d0b7732cc76403c02a93abf1e40de2875ba` |
| Unchanged L1 extraction | `e16f0b69a853c9172bf40329af473480ddb7852bfef5930903f8e9f5314986ca` |
| Unchanged pixel helpers | `ee516375fb7447720d8efbb67a1cabf05e0861f48ee1b20a192000445137d3d6` |

The job additionally checks historical A prediction starts and detector evidence against the audited samples before B/E inference. That production check has not run.

## Mock, deployment and scheduler status

| Item | Verified status |
|---|---|
| Mac bound | No local model inference run; planned verification fixture is 64 lines, within the 200-line limit |
| Exact mock entry point | `L1E_MOCK=1 ... bash scripts/labelfix/clariden/l1e_job.sbatch`, dispatching to `l1e_run.py --mock` |
| Mock outcome / parity | **Pending** |
| Deployment location | Isolated new subtree `labelfix_l1_20261017/l1e_20261017/`; historical L1-v0 outputs unchanged |
| Deployment SHA list | **Pending**; partial code copies are not a verified final bundle |
| Live partition | `debug`, UP, MaxTime `01:30:00`, confirmed over SSH |
| Prepared job request | `a0140`, `debug`, one exclusive node, one task, `01:00:00` |
| Runtime | `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python` for all steps |
| `sbatch --test-only` | **NOT RUN** |
| Production runtime estimate | **Unqualified** until the mock is timed; historical L1-v0 total was 1,785.544 seconds, of which inference/composition was 1,314.995 seconds and GPU inference 58.438 seconds |

The pending deployment must generate `config/l1e_job.json`, `L1E_DEPLOY_SHA256.txt` and `L1E_EXTERNAL_SHA256.txt`, verify local/remote equality, then run the scheduler test. A base configuration is prepared locally at `artifacts/labelfix_l1e/config/l1e_job.base.json`; it is not the final executable configuration.

After those checks pass, the intended **coordinator-only** submit command is:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017
sbatch scripts/labelfix/clariden/l1e_job.sbatch
```

It is recorded for handoff and **must not be used with the current partial deployment**.

Required release-manifest text, included verbatim in the shared release writer:

> A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment.

SSH failure that triggered the mandatory stop:

```text
Connection timed out during banner exchange
Connection to UNKNOWN port 65535 timed out
```

L1E NOT READY: gate tests ok (380 passed); held-out final table pending retrieval; mock/parity pending; windows stored all; final deploy sha256 pending; test-only NOT RUN; estimate unqualified; stopped on SSH failure as instructed.
