# BENCH02H guarded commit list

Review and stage only these exact repository-relative paths. No staging, commit or push was performed by this task. Do not use `git add .` or stage a directory: the checkout contains unrelated tracked and untracked work.

```text
docs/briefs/BENCH02H_cap_pool_sweep.md
docs/harvest/collect_v3_admission/bench02/bench02_draw.py
docs/harvest/collect_v3_admission/bench02/run_sweep.py
docs/harvest/collect_v3_admission/bench02/test_bench02h.py
docs/harvest/collect_v3_admission/bench02/sweep/GUARDED_COMMIT_LIST.md
docs/harvest/collect_v3_admission/bench02/sweep/SWEEP.md
docs/harvest/collect_v3_admission/bench02/sweep/sweep.json
docs/harvest/collect_v3_admission/bench02/sweep/run.log
docs/harvest/collect_v3_admission/bench02/sweep/tests.log
```

Before staging, require every listed path to be a regular file inside this checkout, not a symlink, and smaller than 5,000,000 bytes. Inspect the staged name list against this allowlist and run `git diff --cached --check`. Keep census archives, baseline artifacts, temporary sweep candidates, secrets and all unrelated changes out of this commit. The supplied brief is included unchanged.

Reproduce locally, without network or paid services, from the repository root:

```sh
python3 -B docs/harvest/collect_v3_admission/bench02/run_sweep.py > docs/harvest/collect_v3_admission/bench02/sweep/run.log 2>&1
python3 -B docs/harvest/collect_v3_admission/bench02/run_tests.py > docs/harvest/collect_v3_admission/bench02/sweep/tests.log 2>&1
```

The runner reuses frozen metadata within its process, runs all 48 combinations, asserts default candidate byte parity, checks every drawn key against all registered locked/eval IDs, and checks global edition/series counts before discarding temporary candidates. JSON records input/code hashes and candidate hashes for each combination. `null` cap means unlimited. Best and smallest-change ordering are defined in SWEEP.md. Production launchers are unchanged.
