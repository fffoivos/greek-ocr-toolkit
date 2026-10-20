# CQ6 — stopped at the frozen capital quota

19 October 2026, Europe/Athens. Prepared locally; Clariden access was read-only
SSH `clariden`. No deployment, Slurm submission, reader, OCR, training, inference,
remote write or real-input dry run occurred. This is a stopped evidence package,
not a trainable or deployable candidate. Source checkout remains at the recorded
HEAD; unrelated untracked files were preserved. Custody is a local tar bundle.

## Assembly

| Capital slice | Negative | Positive |
|---|---:|---:|
| Frozen R2a v2 | 214 | 127 |
| Resolved top-up labels available | 720 | 289 |
| Selected additional labels | 586 | 289 |
| Assembled total | 800 / 800 | 416 / 500 |
| Shortfall | 0 | 84 |

The 875 selected top-up identities follow the already frozen selection order;
134 excess resolved negatives are retained separately. The v2 1,572-slot file
is copied byte-for-byte (20b24e0f…). The partial combined overlay has 2,447 rows.
CQ4 top-up and v2 identities are disjoint; W-CAP/top-up documents are disjoint.
The old pool is referenced exactly as BASE used it: 1,935,016 rows, five excess
duplicate rows retained. Actual parent bindings and the saved zero-old-crop
overlap receipt are included. No old pool was rewritten or deduplicated.

W-CAP stays witness only: 281/300 resolved, 133 marked / 148 bare, 19 quarantined.
The explicit preregistered 210-slot W-CAP minimum passes. CQ4's build inventory
minimum 844 also passes (1,009 resolved, 875 selected). The frozen preregistration
does not specify a separate reduced final-training quota. Because it explicitly
requires 800/500, this task does not certify 800/416 as exactly preregistered.
This stop is a final-quota shortfall, not a failure of the W-CAP minimum or a
claim of demonstrated statistical power.

The partial top-up rows are truth proposals, not admitted four-head training
rows: CQ4 asserts breathing/accent only; other heads remain UNKNOWN. No physical
extraction admission, real-input dry run, adapted production runner, or training
smoke is claimed. These are pending a complete training candidate.

## Amendment 1a and custody

Current preregistration SHA256: `7cb5a6fb53a4b5c35a55e85cce9a14961570b4a880cc79a6e4f227b9149f6964`.
Original amendment-1 SHA256:
`dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc`.

The amendment quotes the consequence: “The validation documents are now exposed
to capitals witness selection, so they cannot serve as a fresh final capitals
readout. The locked (ii)/(i-b) strata are the only untouched final cohorts. The
LQB in-sample guard lists the W-CAP items against R2a-2.”

It is explicitly dated after the existing reads, not backdated. CQ4 build,
re-read-build, aggregate and rescan-evidence receipts have a separate
`cq6_amendment1a_binding`; their historical freeze hashes remain intact.
Original receipt bytes are archived inside the package. All 300 selected W-CAP
items, including quarantine, are in the R2a-2 exposure guard; `trained_on=false`.
The combined LQB guard also covers proposed training overlay identities.

## Recipe, instruments and limits

Read the actual parent config, run bindings for all three seeds, trainer,
extractor, model, sbatch, and sacct on Clariden. The four critical source hashes
match all actual bindings. `19` actual recipe fields, 0 intended changes;
additional effective settings and every config leaf are tabled in
`cq6_package/PARAMETERS_VS_R2A.md`. This states intended equality, not a new-run
measurement. Full seeds remain 20261016, 20261017, 20261018.

Parent job 3683130 COMPLETED: partition `normal`, limit `01:21:00`, one node,
four GPUs, account a0140. Parent sacct supplies only a combined-job limit.
The prepare/train/evaluate resource stubs explicitly preserve it; debug semantic
smoke explicitly overrides partition to `debug` and keeps 81 minutes (live debug
max 90 minutes). No independently observed per-kind limits are fabricated.
Production stubs refuse admission. Real training smoke remains pending.

`evaluate.py` implements exact-tuple W-CAP recall, >=10 pp gain, 50,000 paired
document-cluster bootstrap replicates (seed 20261017), CI lower >0, gains in
>=2/3 seeds with positive mean, <=+2 pooled invented marks, explicit false
additions, secondary R2a comparison, and LQB tier-A/B named-mark precision.
Complete predictions and blind lead pixel-review receipts are required. Four
small semantic fixtures passed. No real model predictions or full endpoint
results are claimed. Parent protection scorer/digest are preserved by reference;
protection integration and overall adoption remain unestablished.

## Coordinator files and verification

- Package: `artifacts/cq4/cq6_package/`.
- Read `SUBMIT.md`, `EVALUATION.md`, `assembly_receipt.json` and parameter table.
- `DATA_MANIFEST.json` binds data; `DEPLOY_FILES.txt` and `DEPLOY_SHA256.txt` bind
  the whole stopped package, despite their conventional deployment filenames.
- Run `python3 -B artifacts/cq4/cq6_package/verify_deploy.py` for byte closure.
- Add `--require-ready` for expected refusal. No deployment command was run.
- Bundle: `artifacts/cq4/CQ6_STOPPED_BUNDLE.tar`; SHA256 sidecar accompanies it.

No reduced quota was silently adopted, no quarantine promoted to truth, and no
W-CAP label trained on. Remaining admission work is listed in `SUBMIT.md`.

CQ6: stopped | top-up assembled 800/800 416/500 | W-CAP witness 281/300 | seeds 20261016/17/18 | recipe = 3683130 (19 params, 0 changed) | package artifacts/cq4/cq6_package | commit bundle
