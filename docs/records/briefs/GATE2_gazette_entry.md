# GATE2: add gazette_modern to the W2 c1_gate.json (gpt-6.1-sol, medium, network OFF, mechanical)

The W2 main run has ended (deferred_daily_limit; no collector is running). The coordinator issued the Gazette W2 go, measured stratum only, after the T6b masked cards passed (97/96).

## Do
1. Read `~/Projects/collect-v3-data/run/c1_gate.json` and the starting snapshot `run/W2/gate_snapshots/<sha>.json`.
   - Confirm that the current gate file is byte-identical to the snapshot named in `run/W2/state.json` identity `gate_sha256`.
   - Confirm that no collector is running: `collector_pids.json` PIDs are not alive and `run.lock` is not held.
2. Write the new gate: add `sources.gazette_modern = {passed: true, classes: {modern_scanned: true}, note: "T6b masked cards 97/96 (sol/recut-v1 7f70de90); admission = masked rows for the wave-1d arm only; W2 reads measured_1986_1990 only (all 960 W2 manifest pages)", probe_1982_1985: {passed: false, letters: {n: 40, y: 35}}}`.
   - Every existing source entry stays byte-identical in value.
   - Keep `issued_at` and the other provenance fields, and add `extended_at` (from `date`) plus `extended_by`.
   - Write atomically (temp file, then rename).
3. **Validate** with the collector's own functions, read-only, using `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`:
   - `runner.gate_sources(gate, ['bsb_poly1850','ia_poly1850','nlg','serbia','elstat','gazette_modern'])` passes;
   - `runner.probe_qualified(...)` returns False;
   - `runner.gate_extension_ok(out, old_identity, new_identity)` returns True, where new_identity's gate_sha256 is the new file's sha.
4. **Receipt:** `run/W2/gate_snapshots/GATE2_receipt.json` with the old and new sha and the validation results.

You may write only `run/c1_gate.json` and the receipt. Do not touch anything else in the run root, and do not take locks.

The last line must be exactly:
`GATE2: done | gate sha: <old> -> <new> | gate_sources ok | extension ok | probe_qualified: False`
