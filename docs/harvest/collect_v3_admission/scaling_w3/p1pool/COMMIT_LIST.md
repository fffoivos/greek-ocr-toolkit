# Guarded commit list

No git add or git commit was run. Before staging, run `python3 docs/harvest/collect_v3_admission/scaling_w3/p1pool/guard_commit.py`. Stage only the exact paths in COMMIT_LIST.json plus COMMIT_LIST.json and COMMIT_LIST.md themselves. DEPLOY_READBACK.json and verify.log may be included only after their successful readback is reviewed. Do not stage concurrent census06, c2, g_audit or unrelated changes.
