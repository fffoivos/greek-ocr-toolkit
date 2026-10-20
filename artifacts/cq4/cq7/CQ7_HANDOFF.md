# CQ7 hand-off — build only

Built offline on 19 October 2026. No reader, usage probe, OCR, inference, training,
network request, or image adjudication ran. The frozen quota remains 800 negative /
500 positive; CQ6 remains at 800/416 until new reads are imported and the candidate
is rebuilt separately. No production readiness or quota completion is claimed.

## Scope and prior-read yield

All 196 unresolved identities from the frozen 1,205-slot top-up are covered exactly
once by each of two new independent readers. The existing 1,009 resolved top-up
labels and the W-CAP witness stay intact. Reasons before CQ7: 180 missing/VOID
re-reads, 11 disagreements, 5 agreed unreadables.

Prior initial single reads indicate **171 potential positives**: 111 smooth/none
and 60 rough/none. The other 25 initial tuples contain unreadable (21
unreadable/none, 3 unreadable/unreadable, 1 rough/unreadable) and receive no numeric
yield estimate. This is a prior-vote count, not a calibrated forecast or accepted
truth. Agreement on 84 additional positive slots would reach 500; confirmation of
all 171 would offer 587 total positives, 87 above quota. Select the eventual 500
using the already frozen order; never change the quota or promote quarantine to
reach it. `prior_reads.jsonl` records the evidence per slot without showing it to
readers.

## Prepared contexts

| Batch | r1 targets | r2 targets | Controls in each | Total cards in each |
|---|---:|---:|---:|---:|
| 00 | 90 | 90 | 10 | 100 |
| 01 | 90 | 90 | 10 | 100 |
| 02 | 16 | 16 | 10 | 26 |

Six contexts, 392 target reads and 60 control reads (452 cards). Each reader has a
fresh context tag and fresh opaque item IDs, independently shuffled option maps,
and copied metadata-free RGB PNGs named by content hash. Reader 2 gets the exact
reverse **identity order**, including controls. Each context has ten distinct
controls from the previously lead-verified pool, outside the capital stratum.
There is no new control adjudication in this task. More than one control error
voids that context. Keys and prior reads live only here, outside reader folders.

The HANDOVER §4 requires packs outside repositories. Thus the blind image packs
are in the external temporary pack root recorded below; all coordinator code,
keys, manifests' hashes, closure receipts and evidence are under `artifacts/cq4/cq7/`.
Do not delete that temporary root before execution/import. `contexts.json` gives
absolute reader locations and the hashes of their adjacent manifests.

`/private/tmp/cq7_ddd097b22ed84f5e94d1050ff5ab5e64/packs`

`HANDOVER.md` is the source handover snapshot. `prompts/cap1.verbatim.md` is the
byte-identical frozen CQ4/CQ1 capital prompt; `prompts/cap1.md` appends only the
requested precedence addendum, verbatim:

> view each image with one explicit call, never iterate over paths in code

The protocol body remains unchanged. The addendum overrides its old image-batching
guidance. Each reader sees only its own items, images, README and answer schema.

## Coordinator execution

From the project root:

```bash
bash artifacts/cq4/cq7/VERIFY.sh
bash artifacts/cq4/cq7/RUN.sh
bash artifacts/cq4/cq7/IMPORT.sh
```

`RUN.sh` uses the exact `artifacts/cq4/launchers/run_read.sh` launcher used by
`RUN_ALL.sh`: gpt-6.1-sol, medium, reader network OFF, web OFF, no apps, plugins or
nested agents, project docs disabled, isolated cwd. It probes before and after
**each** run and refuses the next run at >=78% weekly usage. No live meter was
probed during build. Recorded contexts, including VOID, are skipped on resume;
unexplained existing answers stop execution. No automatic retry can overwrite a
reader. All six terminal records are required for import; a VOID remains eligible
only for explicit later adjudication, never for truth.

`IMPORT.sh` is offline. It rechecks immutable custody, audits each VALID rollout
with the unmodified canonical scanner v4.5.5 (manifest checks enabled), decodes
options and checks controls. It saves `imported_ledger.json` and `import_receipt.json`
then invokes the existing `AGGREGATE.sh`. The aggregate automatically consumes the
bound CQ7 import. Matching readable tuples from **both new readers** resolve a
slot; a prior single read never breaks a tie. Other slots remain quarantined with
their CQ7 votes and reason. New truth is labelled `C_sol_two_independent_CQ7_agreed`.
Existing resolved labels and W-CAP are preserved in frozen selection order.
Re-running `AGGREGATE.sh` keeps CQ7 results and verifies their answer/rollout/scan
hashes. This does not rebuild or unstop the frozen CQ6 package, extract training
inputs, deploy, or launch compute. Inspect the new counts before any later work.

## Custody and checks

Canonical scanner v4.5.5 SHA256:
`e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`.
Scanner and replay helper are unchanged and bound in `freeze.json`. Every pack has
an adjacent manifest and a successful build closure receipt. `VERIFY.sh` checks
hashes, controls and manifest integrity; `test_cq7.py` additionally checks complete
coverage, reverse ordering, fresh IDs, answer gating and incomplete-import refusal,
with process launches and probes forbidden. `validation.json` records the result.

`baseline/` preserves the prior aggregate, truth, quarantine, workflow and freeze.
CQ6 had already amended the preregistration and two receipts without refreshing
the live CQ4 freeze. `custody_amendments.json` explains the exact four live-freeze
changes: those three prior CQ6 changes, verified against their archived originals,
and the CQ7 aggregate integration in `workflow.py`. Historical receipt hashes and
preregistration bindings remain evidence, with the current amendment-1a file
checked explicitly. No scanner fork, data-selection change or historical-ledger
rewrite was made. `freeze.json` binds the coordinator scripts, prompts, keys,
context metadata, baseline evidence and dependencies. `BUILD.sh` refuses to
replace an existing build; the current prepared contexts are the handoff artifact.

CQ7: built | unresolved slots 196 | contexts 6 | expected positives 171 | run: bash artifacts/cq4/cq7/RUN.sh
