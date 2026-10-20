# AU1B — fresh Sol contexts, build only

Built through the driver's own path:

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/sf7_rc1/audit/driver.py build --fresh au1b
```

`contexts.json` now selects `accent_initial_001_au1b` (79 targets + 10 controls) and `capital_initial_001_au1b` (3 targets + 10 controls). All 102 public item IDs are fresh and disjoint from the original IDs. Packs remain under the original isolated `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit/` root; exact pack/key/manifest paths and hashes are in `contexts.json`.

The original packs, private keys, and `runs/accent_initial_001` are preserved. The latter still records BLOCKED at `2026-10-19T04:16:04.772622`. Prior context/build/validation/hash metadata and the rebuild preservation receipt are in `build_history/au1b/`. Reusing the same fresh namespace refuses before mutation. Rebuilding creates new context and item IDs while retaining seed 20261017 and the original shuffle seed names; native images, public order, option mappings, target/control provenance, and verbatim prompts compare identically after excluding item IDs. The 100-line frame and `routing.json` hashes are unchanged.

Scanner bound: **v4.5.2**, SHA-256 `7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e`, from `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`. HANDOVER SHA-256: `ebcf7797e2cfc5d59ffb09ae3d4b838962656117f7151c1949d09db192fd812c`. `scanner_binding.json` pins both plus dependency hashes. The parser accepts HANDOVER's current `Canonical v4.5.2 file sha256` wording. RUN verifies the live binding against this receipt, copies exact canonical bytes and dependencies, and rechecks hashes before probes or readers; source drift fails closed.

Offline validation passed: `validate.py` (routing, closure, PNG/native hashes, prompt equality, controls gates and reread triggers), `check_au1b.py` (original/fresh equivalence, disjoint IDs, preserved blocked attempt, runtime scanner copy, binding-drift refusal and namespace reuse refusal), `check_scoring.py` (synthetic fixtures only), shell syntax, and `git diff --check`. Details are in `validation.json` and `AU1B_validation.json`. No reads, budget probes, nested Codex invocations, rollout scans, or network calls were made. No fresh attempt directories or answers exist.

Coordinator commands (scripts remain executable):

```bash
bash artifacts/sf7_rc1/audit/RUN.sh
bash artifacts/sf7_rc1/audit/REREAD.sh
bash artifacts/sf7_rc1/audit/SCORE.sh
```

RUN retains gpt-6.1-sol, medium, network OFF, web disabled, and the existing blinding/control/budget gates. REREAD follows valid initial readings; `REREAD.sh --build-only` prepares its packs without reading. Reader execution remains for the coordinator.

Delivery: `artifacts/sf7_rc1/audit/AU1B_bundle.tar.gz` with adjacent SHA-256 sidecar. This archive contains the audit tree, both generations of isolated packs/manifests, and the bound canonical scanner/HANDOVER snapshot. Archive roots are `repo/`, `reader_packs/`, and `canonical_scanner/`; the live absolute pack paths in `contexts.json` already exist on this Mac. No git commit was created; the bundle is the delivery artifact. `handoff_hashes.json` covers audit files excluding itself, the bundle, and its sidecar.

AU1B: done | contexts 2 fresh (ids accent_initial_001_au1b, capital_initial_001_au1b) | scanner bound v4.5.2 7b364716 | run: bash artifacts/sf7_rc1/audit/RUN.sh | commit bundle
