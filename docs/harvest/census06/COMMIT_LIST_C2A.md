# CENSUS06-C2a commit handoff

Local pre-binding package `fb0194d597f20655` (182 payload files), SF7 PENDING,
not deployed. C1 is carried unchanged; readout, flip report and binder add exact
kept_unverified evidence reason attribution. Pipeline and tool digests are unchanged.

The exact delta is **16 files** in `C2A_COMMIT_PATHS.txt`. The SHA256 seal covers
all listed files except itself. Existing unrelated dirty/untracked files and the
pre-existing brief are excluded. DEPLOY_PATHS.txt was rebuilt and remains byte
identical, so it needs no new commit. payload_diff.json compares with deployed
B's manifest (de597753a70a5d6d), including the previously committed C1 changes.

Review the files, then run the read-only guard before lead-controlled staging:

```bash
.venv/bin/python -B docs/harvest/census06/guard_c2a.py
```

Validation: 461 passed, 19 skipped, including all packaged regression suites,
census06, C1, readout streaming, exact known/unknown reason counts, both flip
directions and fresh mock smoke i/smoke ii/full ii invariant checks. Only
this run's pytest basetemp was deleted after success; tests.log/tests.xml remain.
No network, deploy, sbatch (including test-only), job, git add or git commit.

Next: lead commit; C2a-deploy installs and verifies this new pre-binding code dir;
coordinator follows the unchanged procedure in the C2a section of CENSUS06.md.
The binder must start from this deployed bundle and creates a further bound id.
