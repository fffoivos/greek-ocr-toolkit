# MIX1C loader contract

Final loader: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel3_20261020/code/27a49e51fa735e8f`.
Code resolution is c5841ba on opus/e4-wave2-rel3; the deployment receipt's commit
is 27b9cd1de8c29d412d60b39979391ee061e7d64f. The manifest SHA is
27a49e51fa735e8f064fa68a2da2c5fda7dcefa0e54eecd0b3bc41664b1f1457.
WAVE2_BINDING.json records observed local HEAD separately and equal local/deployed
codec, reader, adapter, wave1c and factory import-source bytes. The deployed Linux
binary is independently SHA-bound and a read-only Linux binary copy was hashed
locally with equal bytes; it was not executed locally.

Gap 1 resolved: the final deployed encode_admissions adapter matches local bytes.
Gap 2 resolved in the export implementation: unchanged clone_build creates MIX1's
own prep/E1 and prep/A12 v2.1 derivatives. Only codec_version changes; label_ids
are append-compatible and never re-encoded. Each encoding_derivation binds the
original build_info SHA and codec SHA and asserts column equality/readback.
Original sources remain in place and untouched. Derivatives are created by the
export job; their existence is not claimed before that job runs.

Gap 3 is assigned to S1: an opt-in entry point consumes the gz JSONL index rows
`[epoch, position, component, pool_index, line_id]`. MIX1 supplies final indices,
shared real shards, derivatives and per-arm INDEX.json custody, without changing
train.mix.assemble or supplying a trainer. S1 must use these exact indices and
must not redraw from fractions. Component order is real ref_364871, A12, E1;
E1 is present only in M1. Physical indices address full derivative pools, even
where the existing MIX1B exposure audit excludes candidates from selection.

The upstream wave1c SHA check at bench/e4_wave1c.py:218-219 runs unchanged via
AST extraction, avoiding campaign imports that mutate sys.path. Serialization
and deterministic gzip match its lines 182-183 and 207-208. Re-serialization for
verification uses the same draw, never a second draw. Header/receipt is separate
from gzip rows. Every plan binds pool identities, D=428872, eight epochs and
seed provenance 20261015. No draws of record exist: 3705237 was cancelled before
starting. The manifests job is the first draw of record.

Full validate(), then load_rows(), is mandatory for the 1000-row real round trip
and shared export. validate_metadata() alone cannot qualify them. VERIFY package
requires the original real-sample receipt plus ROUNDTRIP_RECEIPT.json against
27a49e51, with retained evidence under mix1_scratch/roundtrip_e87b9e8d.
The bounded check passed: 1000/1000 rows, all three parents, zero drops and zero
NFD mismatches. VERIFY inputs rehashes this 21.7 MB evidence and otherwise remains
light unless --full is explicitly used in a job.

MIX1D A12 source: `$P/e4/wave1b/v2-codec/old_v2/synthetic`, build_info
94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc.
E1 remains directly sourced from `$P/e1_run4/real`. e1_run4/synthetic is only
the A12 provenance root. The export gates all train/val/reserved rows on ordered
line_id, gt_nfd, gt_nfc and label_ids equality across that chain and hashes both
inventories. CHAIN_GT_SAMPLE.json records the bounded login-node witness.

Pre-export, run:

```bash
"$MIX1_ROOT/VERIFY.sh" crosscheck-a12 \
 "$W/e4_wave2_rel3_20261020/preparation/inventory03/control_synthetic_7/build_info.json"
```

Post-export, add `--own-build-info "$MIX1_EXPORT_OUTPUT/prep/A12/build_info.json"`.
The export performs this second check automatically and records it in
EXPORT_RECEIPT.json. Both source_receipt_sha256 and codec_sha256 must match.
Both physical inventories are rehashed; equal verified bytes imply equal columns.
Otherwise every column in every split is compared in order, with unequal columns
or row counts stopping the export. inventory03 is a read-only comparison target,
never a component or pool source. Post-export equality remains pending until the
coordinator's export job runs.

The MIX1C round trip remains valid: AST comparisons require unchanged module(),
export_real(), read_export() and load_real() functions against hash-bound MIX1C
snapshots, alongside the original core/roundtrip hashes. Evidence remains at its
original e87b9e8d location and is rehashed by VERIFY inputs.
