# CQ6C coordinator hand-off

Assembly ready: 800/800 negatives, 500/500 positives. Training admission is
pending; see HEADS_AND_ADMISSION.md. No deployment or submission was performed.
The frozen CQ6 package remains stopped and byte-identical. The new attempt is
`artifacts/cq4/cq6c_package`.

Local verification and semantic smoke (no model, scheduler, or remote write):

```sh
cd artifacts/cq4/cq6c_package
python3 -B verify_deploy.py --require-ready
arch -x86_64 python3 -B test_instrument.py  # this Mac's installed NumPy is x86_64
arch -x86_64 python3 -B test_admission.py
python3 -B verify_deploy.py --require-training-ready
# Last command deliberately refuses: UNKNOWN heads; no admitted runtime.
```

After an independently authorized staging action, a coordinator may verify the
exact staged bytes read-only. Set CQ6C_STAGED_ROOT to that actual absolute path;
no staged location is claimed in this hand-off.

```sh
: "${CQ6C_STAGED_ROOT:?actual staged absolute package directory}"
ssh clariden "cd '$CQ6C_STAGED_ROOT' && python3 -B verify_deploy.py --require-ready"
```

Commands for the coordinator AFTER explicit scheduler authorization and actual
staging (documented only; not executed in CQ6C):

```sh
# On Clariden, inside the actual staged package:
export CQ6C_PACKAGE_ROOT="$PWD"
sbatch --export=ALL slurm/smoke.sbatch
sbatch --export=ALL slurm/prepare.sbatch
```

Smoke runs semantic instrument fixtures on **debug**, not a training smoke.
Prepare is an admission audit and deliberately refuses the current top-up.
Both use explicit `01:21:00`, one node, four GPUs, account a0140. Train and
evaluate resource specifications use **normal**, also `01:21:00`. These inherit
3683130's combined-job limit, not invented separate per-kind timings. Debug
partition's verified maximum is `01:30:00`. No command above was submitted.

Offline W-CAP evaluation, when complete three-arm/three-seed ledgers and blind
lead pixel review exist:

```sh
python3 -B evaluate.py --truth data/wcap_truth.jsonl \
  --predictions "$CQ6C_PREDICTIONS" --lead-review "$CQ6C_LEAD_REVIEW" \
  --lqb "$CQ6C_LQB_LEDGER" --guard data/lqb_guard.jsonl \
  --out "$CQ6C_EVALUATION_OUT"
```

Production training submission commands are **missing**: there is no admitted
four-head top-up or sealed production runtime/config. `slurm/train.sbatch`
refuses admission and never launches the historical runner with new unverified
inputs. Do not use `--require-ready` as permission for production: it is an
assembly check. `--require-training-ready` is the production gate.

Before a separately authorized production attempt: bind legitimate evidence
for the unread heads under the frozen policy; verify source assets and exact
extractor admission; preserve BASE duplicates and in-place correction semantics;
adapt/bind the runtime; qualify the real-input check and debug training smoke;
integrate the unchanged protection families; reseal every changed byte. Keep this
receipt and CQ6 frozen. No quota amendment, new labels, or remote execution is
authorized by these instructions.
