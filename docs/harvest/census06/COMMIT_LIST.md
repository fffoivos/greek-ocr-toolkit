# Guarded CENSUS06-A commit list

The lead commits. This run never invokes git add or git commit. The exact allowlist is `commit_paths.txt`; `commit_receipt.json` seals its bytes. Every path is inside `docs/harvest/census06/`. Do not stage the directory recursively or use a broad repository pathspec.

Before the lead stages anything:

```bash
export GIT_OPTIONAL_LOCKS=0
.venv/bin/python -B docs/harvest/census06/guard_commit.py
.venv/bin/python -B docs/harvest/census06/final_checks.py
# Recheck the guard after any reviewed edit and regenerate its receipt deliberately.
```

Review `CENSUS06.md`, `CHANGES.md`, `config_diff.json`, `payload_diff.json`, `pipeline_033.patch`, `readout_033.patch`, `fingerprints.json`, `corrections/report.json`, `INPUTS.json`, qualification logs/results, the two deploy manifests and all new binding/flip/guard scripts. Only then stage the exact listed paths using Git's literal pathspec-file support, under the lead's authority. No staging command is executed or inferred by this handoff.

Excluded: ignored raw regenerated ledgers and their gzip archives; disposable SQLite/test/mock/native runtime directories; the copied baseline tree; historical stopped-draft intermediates not named by the list. Preserve `corrections/archives/` separately: INPUTS.json records their absolute paths, byte sizes and hashes; restore_inputs.py rehydrates exact raw files for B without overwriting. These large archives are not Git or deploy payload.

Pre-existing unrelated tracked and untracked changes are not ours; the guard reports current tracked dirty paths but never changes them. The external verifier's dirty-path check covers the **whole tree**, not payload paths alone. A real lead commit and a clean tracked tree must precede B's unchanged verifier. No temporary Git repository, synthetic commit, dirty-path exemption or verifier bypass exists.

CENSUS06-B is separate: deploy committed manifest bytes to the new empty code directory; copy the five new numerics inputs and unchanged split to new destinations; hash every payload/input back; rehash standing cyrillic in place; run the unchanged verifier for regression/parity/census/readout with receipts outside the repo; run scheduler test-only checks. sf7-binding remains PENDING until actual coordinator-supplied per-parent files pass the binder. No production submission is authorized for A or B.
