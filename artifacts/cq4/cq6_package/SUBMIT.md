# Coordinator hand-off — STOPPED

Do not deploy or submit this package. The frozen 800/500 capital slice can only
be assembled to 800/416 from the resolved labels. The missing 84 positives are
not supplied by duplicating rows, using W-CAP, or treating quarantine as truth.
The written W-CAP minimum of 210 passes (281); CQ4's inventory minimum 844 also
passes. Neither rule authorizes a smaller final training quota. No separate
lower final-training minimum exists in the supplied preregistration.

Local receipt/byte checks (safe; no deployment or scheduler action):

```sh
cd artifacts/cq4/cq6_package
python3 -B verify_deploy.py
python3 -B verify_deploy.py --require-ready  # expected STOP / nonzero
```

If a separately reviewed package is later staged, its coordinator verifies it
read-only with (this command is documented, not executed here):

```sh
ssh clariden 'cd /REVIEWED/PACKAGE/PATH && python3 -B verify_deploy.py --require-ready'
```

No valid sbatch submission command is authorized for this stopped package.
`slurm/{prepare,train,evaluate}.sbatch` are guarded resource specifications; all
refuse to execute work. They preserve parent normal/01:21:00/one node/four GPUs.
Parent sacct has one combined job, not three independent per-kind limits; no
per-kind timing measurement is claimed. `slurm/smoke.sbatch` explicitly uses
debug/01:21:00 for semantic fixtures, not a qualified real-input training smoke.
Nothing was submitted, including smoke.

Continuation needs 84 additional admissible positive capital labels from the
authorized lead process (or an explicit scientific quota amendment), then a new
manifest seal. Keep the 134 unused resolved negatives available, not appended.
The provisional top-up records contain CQ4 breathing/accent truth only: unasserted
diaeresis/subscript heads remain UNKNOWN rather than invented zero labels. Their
four-head admission and physical frozen-extractor coverage must be resolved and
verified before they can become executable training rows.

Only after complete admission: adapt the parent runtime to the top-up native
sources without weakening R2J4, run the real-input A/B check and debug training
smoke, finish protection-family scoring integration, bind every native asset
and checkpoint, reseal DEPLOY closure, then prepare concrete coordinator sbatch
commands. This package stops before those operations and must not be called ready.
