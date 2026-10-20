# Guarded CENSUS06-B commit list

The lead commits; B ran no git add or git commit. Review the new B section in CENSUS06.md and the complete b_evidence receipts, scripts and unexecuted coordinator block.

Use only the exact repository-relative paths in B_COMMIT_PATHS.txt (one literal path per line), never recursive directory staging. B_COMMIT_SHA256SUMS seals every listed file except itself. The read-only guard checks the exact allowlist/seal, unchanged committed payload bytes, the untouched clean worktree at cf1db4dd4, four VERIFY_OK receipts with zero exemptions, and deleted basetemps:

```bash
.venv/bin/python -B docs/harvest/census06/b_evidence/guard_b.py
```

The allowlist includes the modified CENSUS06.md and new B files only. No A payload, input ledger/archive, baseline/mock data, unrelated dirty file, .git path or clean verifier worktree is authorized. Preserve ignored inputs/archives separately. Before staging, review each diff; any edited B file requires deliberate seal regeneration and another guard run. No stage/commit command is executed or inferred here. Coordinator job commands remain unexecuted review material, and SF7 is PENDING.
