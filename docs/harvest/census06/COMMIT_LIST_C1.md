# Guarded CENSUS06-C1 commit list

C1 ran no git add or git commit. Only the literal repository-relative files in
`C1_COMMIT_PATHS.txt` belong to this change. Do not recursively stage this bundle
or the repository: unrelated dirty files and pre-existing untracked artifacts
are outside the allowlist, including the already present C1 brief.

Before any lead-controlled staging, review `timing_c1.patch`, every allowlisted
new file, and `CENSUS06.md`, then run the read-only guard:

```bash
.venv/bin/python -B docs/harvest/census06/guard_c1.py
```

`C1_COMMIT_SHA256SUMS` seals every allowlisted path except itself. The guard
checks the seal, scope, complete local deployment manifest, measured partition
maximum, passing XML and absent C1 basetemp. Any edit requires deliberate patch
and seal regeneration plus another guard run. No stage/commit command is supplied
or executed. The lead decides what to commit after review.

Local rebuild: `5de4fcd496663eae`, 182 payload files, SF7 PENDING, **not deployed**.
Pre-binding deployed id remains `de597753a70a5d6d`; C2 must rebuild after binding
and reverify a new deployed id. Manifests are local source artifacts only.

Validation: **438 passed, 19 skipped**. These are the packaged eight regression
suites, amendment/binding/flip suite, readout suite including its unchanged
600,000-row streaming test, and 27 C1 tests. Skips: nine missing packaged historical
evidence fixtures, nine missing historical readout fixtures, one real-SF7 test
pending supplied files. The final full run writes only `tests.log`/`tests.xml` as
test artifacts; its own `c1-test-tmp` is deleted after success. No historical
basetemp, mock corpus, baseline, correction input or other data was deleted.

The patch includes the substantive changes and all ordinary receipt files;
it excludes itself and the allowlist/seal that describe or seal it. Those three
are separately included in the guarded list. C1's only network operation was
read-only SSH to `scontrol show partition normal`: MaxTime **12:00:00**. No Slurm
submission, test-only scheduler request, deploy, allocation or spend occurred.
