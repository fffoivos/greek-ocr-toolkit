# REL4b guarded commit handoff

No staging or commits were run. Run `python3 -B docs/harvest/collect_v3_admission/release_v4/guard_commit.py` immediately before staging. COMMIT_LIST.json contains the exact payload paths and hashes, deployment manifests, and the authorized REL4b brief hash. Do not stage unrelated worktree changes. The guard fails on any changed or missing listed bytes and prints the exact allowlist; it never executes Git.

Base commits: be85e348f, 0378caf7d, 90b55e49b. Census06 source: cf1db4dd4. CROPS4C source: ca949ca31. Existing package 22c3e0ba is preserved. New package root is identified by PACKAGE_ID and DEPLOY_READBACK.json. Production census06/sf7/CROPS4C bindings remain pending; do not present this pre-binding package as a release.

All 92 REL4/REL4b tests pass; only tests.log (the existing TESTS.log on this case-insensitive filesystem) and tests.xml retain pytest output. This run's rel4b_pytest_tmp has been deleted. No other data was deleted. No jobs, scheduler probes, spend, git add or git commit.
