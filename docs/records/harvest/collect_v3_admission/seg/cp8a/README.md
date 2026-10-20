CP8a is restricted to evidence custody, evaluator qualification and the authorized
ADMW2 rerun. No new readers, geometry preparation, population replay or publication.

Use the collector interpreter, PYTHONDONTWRITEBYTECODE=1, PYTHONPATH including the
repository and collector roots. Run restore_cp5.py, qualify.py, build_manifest.py.
For a package-only reproduction without external snapshots or temporary pack directories, run qualify.py --evidence-only. Full text-parity qualification additionally verifies the original snapshots.
The restore validates the archived SHA, uncompressed SHA and 119720892-byte length
before atomically materializing CP5_verification.json, and checks existing bytes.
Both original freeze files and frozen evaluator sources remain untouched.

qualify.py verifies the historical scorer/runtime amendment, raw remapping,
controls, original pack hashes and canonical rollout scans. The B public pack is
copied here under sol_packs/segcp7r2_b; original absolute custody is retained in
historical scans. No original FAIL matrix is overwritten.

r1/r2_matrices.json retain raw matrices, adjudicated standalone matrices and
text-eligible composition matrices separately. Geometry-unavailable rows are
policy losses and excluded from measured matrices. The Elstat orientation FP
remains in standalone diagnostics; text ineligibility removes its admission
effect, not its false-positive label. The two Gazette FP remain false positives.
The coordinator's class-wide end-clip ruling applies to r1; it does not create
new individual pixel adjudications. Entries without an individual lead override retain their original reader labels explicitly; no new pixel findings are asserted. All four r1 apparent FN follow the review section 2 class-wide end-clip ruling.

application_manifest.json is a canonical file-hash closure over a conservative
superset of transitive Python source, codec/tables, parameters, truth/adjudication,
reader custody and qualification, plus installed distribution versions. Its own
SHA is the application identity. The manifest excludes downstream receipts to
avoid a hash cycle. Changing a bound input requires rebuilding qualification and
the manifest. Frozen evidence retains its original identities; generated outputs
reference the application manifest. Historical CP2 evaluate() remains an
unqualified compatibility interface; the qualified entry point is
qualified_admission.evaluate_evidence(), called by the ADMW2 measurement wrapper
and frozen-observation qualification. End-clips never enter DROP_ORDER.

The native ADMW2 rerun writes only /tmp/segcp8a-admw2. compare_admw2.py checks all
rows against the preserved ADMW2 output, allowing only the manifest identity
addition. Counts and all original decision fields must match exactly.
