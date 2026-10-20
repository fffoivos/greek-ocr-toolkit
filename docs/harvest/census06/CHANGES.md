# CENSUS06 authorized changes

All 167 inherited payload files remain: 155 identical, 12 changed. Additive payload paths are listed below. The current manifest is authoritative. The final lead ruling explicitly authorizes the shared fingerprints and converter-regenerated numerics, superseding the earlier unchanged-digest requirement.

| Inherited changed path | Reason |
| --- | --- |
| `census06_config.json` | Polytonic in scope, pending released SF7 per-parent files, converter-regenerated numerics hashes, new relocation marker. |
| `jobs/census.sbatch` | CENSUS06 names/config/root only; original resource/time settings retained. |
| `jobs/common.sh` | CENSUS06 environment and output root only; native settings unchanged. |
| `jobs/parity.sbatch` | CENSUS06 environment/job names only. |
| `jobs/readout.sbatch` | CENSUS06 names/root and sibling readout; version derives from 0.3.3 code. |
| `jobs/regression.sbatch` | CENSUS06 names and added amendment/head tests; existing regression fixture set unchanged. |
| `package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json` | Owner-released polytonic 0.7 plus eight amended-source digests, same tool generations. |
| `package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py` | Only authorized 0.3.3 kept_unverified validation/routing amendment. |
| `package/projects/greek-ocr-toolkit-pipe032/tests/test_content_gate.py` | Only expected pipeline version 0.3.2 -> 0.3.3. |
| `prepare_config.py` | CENSUS06 relocation/config names plus pending-binding refusal. |
| `readout/census_readout.py` | Required per-parent/class SF7 statuses/admissions and no-polytonic-edit invariant. |
| `readout/readout.sbatch` | CENSUS06 environment names only. |

All remaining additions support those authorized changes: binding, guards, tests, provenance, manifests, runtime sizing, handoff and flip reporting. No other native/policy/threshold/source change is present. `config_diff.json`, `payload_diff.json`, `pipeline_033.patch`, `readout_033.patch`, and `fingerprints.json` provide exact review evidence.

The source-copy manifest contains no native build target, raw regenerated ledger, archive, test work database or alternate repository. The same split/parent/metadata/frozen/held-out data remain bound. Five old cyrillic shas are untouched; five numerics shas change only because the converter emits the new active digest. Archives are ignored and listed in INPUTS.

Additive deploy paths (the refreshed payload_diff.json lists the complete final set):

- `INPUTS.json`
- `PAYLOAD_PATHS.txt`
- `VERIFY.sh`
- `bind_sf7.py`
- `bind_sf7.sbatch`
- `binding_state.py`
- `build_package.py`
- `flip_report.py`
- `flip_report.sbatch`
- `pipeline_033.patch`
- `polytonic_parent_candidates.json`
- `submit_chain.sh`
- `test_pipeline_033.py`
