# GATE2b: prepare the extended W2 gate inside the worktree (gpt-6.1-sol, medium, network OFF, mechanical)

GATE2 was blocked: your sandbox cannot write `~/Projects/collect-v3-data`. It confirmed that the current gate equals the starting snapshot `eb4a17ed…` and that no collector is running. **Prepare everything inside this worktree;** the lead installs the file as part of the coordinator-authorised Gazette launch one-off.

## Do
1. Under `docs/records/harvest/collect_v3/w2_gate/`, write `c1_gate.next.json`: the current `run/c1_gate.json` (read-only) plus `sources.gazette_modern`, exactly as specified in `docs/records/briefs/GATE2_gazette_entry.md` step 2. Every existing entry stays byte-identical in value; add `extended_at` and `extended_by`.
2. **Validate offline** with `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, using a temp mirror under this folder that contains only `c1_gate.json` (= next), `W2/state.json` (copied) and the snapshot (copied):
   - `gate_sources(…, six sources)` passes;
   - `probe_qualified` returns False;
   - `gate_extension_ok(mirror, state.identity, identity with gate_sha256 = sha(next))` returns True.
   - Write `validation.json`.
3. Write `INSTALL.md` with the exact two lines the lead runs:
   - first, a re-check that the live gate's sha still equals `eb4a17ed…` and that no collector is alive;
   - then an atomic install (`cp` to a temp file in the run root, then `mv` over `c1_gate.json`), with `shasum` before and after.
4. Leave a guarded commit list.

The last line must be exactly:
`GATE2b: done | next gate sha: <sha> | gate_sources ok | extension ok | probe_qualified False | install lines: 2`
