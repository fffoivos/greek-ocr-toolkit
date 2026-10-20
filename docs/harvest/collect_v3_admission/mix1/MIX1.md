# MIX1D — A12 source custody, 20 October 2026

## MIX1D

Qualified package target: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_pkg/8d25940f`. MIX1C `e87b9e8d` and intermediate
`f1384fdb` are superseded and must not be submitted. All earlier deployed roots
and retained real round-trip evidence remain untouched. No jobs submitted,
spend, git add or git commit. Production draw manifests and derivatives are
future job outputs; package/deployment manifests are regenerated here.

A12 now binds `$P/e4/wave1b/v2-codec/old_v2/synthetic` everywhere in current
inputs, candidate/text-audit loading, M2 pools, export clone_build, manifest
source receipts and the real-sample receipt. Its build_info SHA is
94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc (codec v2).
`$P/e1_run4/synthetic` is only its provenance root, SHA
495453433c2efff88a8a0d7d39de32e856d878d815b923dbf3eb9354411bfbff.
Historical reference snapshots/receipts keep their original bindings and are
not current pool sources. E1 stays cloned directly from `$P/e1_run4/real`.

CHAIN_GT_SAMPLE.json records **1122 GT-equal rows across 51 shards**, spanning
train, val and reserved. The checked fields are line_id, gt_nfd, gt_nfc and
label_ids, in source order. Recipe hashes and all three split counts match.
This bounded witness is not a full-chain result: the export job hashes both
complete inventories and requires those fields equal for every row before
cloning A12. Failed equality stops export. Counts are 190486 / 9208 / 3999.

TEXT_AUDIT.json is recomputed from old_v2 labels: **287 dropped, 190199 kept**;
all per-source candidates, exact/substring30 hits, kept and dropped counts equal
MIX1C. Existing key/crop eligibility rules and all arm arithmetic are unchanged.
The full production candidate read/hashes remain in the manifests job.
MIX1D_REAL_SAMPLE.json records the fresh read-only sample check; the current
REAL_SAMPLE_RECEIPT.json retains 70/70 input coverage including the ref receipt.
The 52-test suite passes, including column-mismatch and corrupt-shard rejection.

The MIX1C real-crop round trip remains valid: 1000/1000 rows, three parents,
zero drops and zero NFD mismatches. module(), export_real(), read_export() and
load_real() are AST-identical to the hash-bound MIX1C snapshots; core.py,
roundtrip.py, factory, codec and reader are unchanged. VERIFY inputs rehashes
all nine retained evidence files at `mix1_scratch/roundtrip_e87b9e8d`.
No new real-pool transform or evidence directory was created.

Inventory03 is complete. A12_CROSSCHECK.json records the read-only pre-export
source build_info SHA and codec SHA equality against its control. The exact
final line for the training lead's S1 REVIEW_INPUTS is:

```text
CROSSCHECK_A12_CONTRACT_OK source 94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc codec eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6
```

Post-export derivative equality remains pending until the coordinator runs the
export job. The job writes the post-export comparison into EXPORT_RECEIPT.json:
both physical shard inventories are rehashed and their canonical inventory
hashes recorded; equal bytes are a bonus. Otherwise all columns across every
split must be equal in order, or export fails. The control is a comparison
receipt/pool only, never a MIX1 training component or source.

## Exact coordinator command block

For the coordinator to execute later; this task did not execute this block.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export MIX1_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_pkg/8d25940f
export MIX1_PYTHON="$W/venv/bin/python"
export MIX1_SUBSET_RECEIPT="$W/scaling_w3/subsets/scale1-c05-003/SUBSETS_RECEIPT.json"
export MIX1_SUBSET_SHA=467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2
export MIX1_OUTPUT="$W/scaling_w3/mix1_runs/MIX1D-8d25940f-manifests-001"
export MIX1_EXPORT_OUTPUT="$W/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001"
"$MIX1_ROOT/VERIFY.sh" package
"$MIX1_ROOT/VERIFY.sh" inputs --subset-receipt "$MIX1_SUBSET_RECEIPT" --subset-sha "$MIX1_SUBSET_SHA"
"$MIX1_ROOT/VERIFY.sh" crosscheck-a12 "$W/e4_wave2_rel3_20261020/preparation/inventory03/control_synthetic_7/build_info.json"
export MIX1_MANIFESTS_JOB="$("$MIX1_ROOT/submit_mix1.sh" manifests)"
"$MIX1_ROOT/submit_mix1.sh" export
```

The export submission uses exactly `--dependency="afterok:$MIX1_MANIFESTS_JOB"`.
Both jobs embed account a0140, normal partition and explicit CPU/time limits.
Manifests: 4 CPUs, 32 GiB, 2 hours. Export: 4 CPUs, 128 GiB, 4 hours, no GPUs.
These are limits, not measured runtime. Full hashing belongs in these jobs.
Nine plans × eight epochs × 428872 = 30878784 index rows; the manifests job
creates the first production draw. S1 consumes these indices without redraw.
The final deployed wave-2 loader remains 27a49e51fa735e8f.

## MIX1C historical qualification

The following section describes the predecessor, not an instruction to use it.

### MIX1C

The final loader is `$W/e4_wave2_rel3_20261020/code/27a49e51fa735e8f`;
WAVE2_BINDING.json binds c5841ba, receipt commit 27b9cd1…, and manifest SHA
27a49e51fa735e8f064fa68a2da2c5fda7dcefa0e54eecd0b3bc41664b1f1457.
Local and deployed codec, reader, clone_build, encode_admissions, wave1c and
factory import-source bytes are equal. The deployed factory binary SHA is
bdd52e588dd92a1ec15560062fae16bc3bcdc1cae2a9bd1da2d5525932441773;
a read-only SSH copy of that Linux binary was hashed locally and matched. It was
not executed locally. The local worktree remains read-only.

EXPORT implementation now creates one shared 364871-row real v2.1 set through
the unchanged factory + encode_admissions. It makes our own prep/E1 and prep/A12
v2.1 derivatives using unchanged clone_build; only codec_version changes. Sources
stay bound in place. encoding_derivation binds source build_info and codec SHA,
column equality and readback; label_ids are never re-encoded. The derivatives
are outputs of the future export job, not pre-existing outputs claimed here.

Each arm emits indices.jsonl.gz containing only
`[epoch, position, component, pool_index, line_id]`; draws.json and RECEIPT.json
are its header and pool/seed custody. D=428872, eight epochs, seed provenance
20261015. The exact upstream wave1c SHA byte check (lines 218–219) is extracted
unchanged without campaign import side effects. Byte format/gzip follow lines
182–183 and 207–208. Tests exercise both success and a corrupt-index rejection.
The verifier reserializes the same draw without sampling again. No draws of
record exist: job 3705237 was cancelled before starting. No production manifest
was generated here. The manifests job creates the first final draw.

Per-arm exported INDEX.json binds those same indices and a validated mix.json
pointing to shared real shards and our derivatives. Physical index identities
are checked against actual final pools; an order mismatch stops rather than
rewriting a draw. S1 owns the opt-in fixed-draw training reader, as recorded in
LOADER_CONTRACT.md. This package does not change the trainer.

Qualification requires ROUNDTRIP_RECEIPT.json: 1000 real rows, all three parents,
full validate() followed by load_rows(), exact membership, zero NFD label
mismatches, original crop hashes, and PNG dimensions. It must bind the final
27a49e51 root and current round-trip code. The original real sample receipt
remains mandatory. The check passed: **records=1000 written=1000 drops=0; full validate() +
load_rows() ok; NFD mismatches=0**. Parent coverage is W1=334, W2=334, v2=332.
The 760 literal differences are Unicode normalization only. Factory appearance
audit is report-only and returned audit_ok=false; no rows were filtered.

Evidence is retained at `$W/scaling_w3/mix1_scratch/roundtrip_e87b9e8d`
(21,707,253 bytes excluding the receipt). ROUNDTRIP_RECEIPT.json records every
output SHA, the loader/factory/codec, subset and executing code SHAs. Its content
map excludes the receipt itself. VERIFY inputs rehashes this bounded evidence.
EXPORT is qualified for the coordinator; the production export has not run.
No --full check is run on a login node. The superseded `mix1_pkg/f1384fdb`
and `mix1_scratch/roundtrip_f1384fdb` remain untouched. Its package check
passed, but inputs verification exposed the subset-SHA variable bug fixed
in this final package; that earlier package is not qualified.

