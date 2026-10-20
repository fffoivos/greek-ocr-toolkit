# T6h: Mac v2 masking

**Launch blocked in this sandbox.** `nice -n 15` reports `nice: setpriority: Operation not permitted` and leaves the process at nice 5. `os.setsid()` reports `PermissionError: [Errno 1] Operation not permitted`. Both were probed without loading the detector. The bundled Mac `bin/setsid /usr/bin/true` also exits with `launch blocked: setsid: [Errno 1] Operation not permitted`.

No new 50-crop processing mock or production run was started. There is no live production PID, three-page confirmation, measured production rate or ETA. The old T6f Mac mock is the comparison baseline, not evidence of a new rerun. Escalation needs an execution context that permits session detachment and nice >=15. The runner fails before processing when its actual priority is below 15.

The population tests bind the live, read-only main checkout imports: **214,436 train + 44,029 test = 258,465 crops on 5,585 pages**. Parliament is **76,463 crops on 645 pages**, copied as byte-exact originals with `skipped_wave=parliament`. There are 4,940 masking pages. Dev imports and codec exclusions are not used. Import splits take precedence over older admitted split fields; both are retained in the selection.

The only masking entry point is the existing `../v2_clariden/phase0_mask.py`. It uses the unchanged T6c2 worker, nearest-curve matcher and T6b `guard_measure`: original grayscale <128, strictly >0.30 restores source bytes and marks `wrong_line_risk`. Unmatched originals are copied and flagged. The runtime code is exported from tree `63c640a3aa4abe08d200258cf24d235dfa4a1625` into the ignored output; params remain `801d517e…`, library `f203504a…`. No masking, matching, encoder or dependency changes were made.

Run all commands below from this worktree, `~/Projects/greek-ocr-toolkit-sol-recut`, on branch `sol/recut-v1`. Networking stays off. No command accesses the W2 run directory or its locks.

## First run the required local mock

In the escalated context:

```sh
nice -n 15 "$PWD/.venv/bin/python" -B docs/records/harvest/recut_v1/v2_full/run.py mock --workers 4
```

This selects the exact original 50 IDs from the full imports, processes all 50 pages afresh on first use, rehashes their source/output crops and compares every output SHA256 with `v2_clariden/receipts/mock_mac_records.jsonl`. It also checks guard, match, risk and mask counts. Evidence is `mock-out/mock-comparison.json`; all 50 must match. An interrupted mock resumes complete pages. The production runner rechecks the actual mock files and the frozen bindings before launching page workers. A rejected or absent mock cannot authorize the full run.

## Exact detached launch command

```sh
PATH="$PWD/docs/harvest/recut_v1/v2_full/bin:$PATH" setsid nohup nice -n 15 "$PWD/.venv/bin/python" -B "$PWD/docs/harvest/recut_v1/v2_full/run.py" run --workers 4 --detached > "$PWD/docs/harvest/recut_v1/v2_full/run.log" 2>&1 < /dev/null &
```

`bin/setsid` is a minimal Mac shim for `os.setsid(); execvp(...)`; it does not bypass sandbox restrictions. The runner writes its own PID to `v2_full/run.pid` after checking nice, session leadership and the output-local lock. `nohup` and explicit standard-stream redirection allow the detached process to survive the launching shell. Successful detachment and survival remain unverified here because the sandbox rejects `setsid`.

There are at most four page workers, each a fresh interpreter inheriting nice >=15 and one numerical thread. Whenever an active or proposed page exceeds 20 MP, the cap is three. A separate watchdog samples free space every 0.5 seconds, stops launching work and kills active workers below 10,000,000,000 bytes free. There is no 90-minute limit on this full run.

## Check status and confirm the launch

```sh
cat docs/records/harvest/recut_v1/v2_full/run.pid
ps -p "$(cat docs/records/harvest/recut_v1/v2_full/run.pid)" -o pid,ppid,pgid,sess,ni,etime,command
tail -n 10 docs/records/harvest/recut_v1/v2_full/run.log
python3 -m json.tool docs/records/harvest/recut_v1/v2_full/out/summary.json
```

Before calling this launched, check the actual PID is alive after the launcher exits and `pages_complete >= 3`, with no failed crops in the per-wave/split totals. Summary fields include `masking_pages_this_session`, `pages_per_minute` and `eta_athens`. Rate is newly successful non-parliament pages divided by session elapsed time, including worker startup. The ETA extrapolates that rate to remaining masking pages; early pages and parliament copying can make it provisional. Do not use the old one-crop-per-page mock timing as full-population throughput.

## Outputs, failures and resume

`out/crops/<wave>/<doc>/<file>.png` contains every produced crop. `out/records.jsonl` records original/output SHA256, split, match/guard status, mask counts, actual host and frozen tree SHA. `out/summary.json` counts changed, guarded, unmatched, failed and skipped crops by wave and split. Adapter diagnostics and page logs remain under `out/work/` and `out/logs/`.

Completed page records under `out/pages/*.records.jsonl` are the resume authority. Each restart checks exact page IDs, record completeness, provenance, and both original/output hashes. Complete pages are skipped. The aggregate is rebuilt from those pages before appending new results, so an interrupted append is harmless. A page exception or worker crash records `failed_page` for every crop and copies verified originals, then continues. Failures remain visible and give a nonzero final exit status; a failed page with all fallback crops present is a complete recorded page and is skipped on restart. Missing/corrupt outputs or originals invalidate the page and are retried. Watchdog/signal interruptions leave unfinished pages for the next run.

After confirming the previous PID is no longer running, use the same launch command to resume, appending to the log:

```sh
PATH="$PWD/docs/harvest/recut_v1/v2_full/bin:$PATH" setsid nohup nice -n 15 "$PWD/.venv/bin/python" -B "$PWD/docs/harvest/recut_v1/v2_full/run.py" run --workers 4 --detached >> "$PWD/docs/harvest/recut_v1/v2_full/run.log" 2>&1 < /dev/null &
```

The output-local advisory lock prevents duplicate coordinators. Source/import/params/code/selection changes block resume instead of mixing runs. All output, mock scratch, logs and PID files are ignored by Git.

## Verify when finished

```sh
nice -n 15 "$PWD/.venv/bin/python" -B docs/records/harvest/recut_v1/v2_full/verify.py > docs/records/harvest/recut_v1/v2_full/out/verification.json
```

The verifier reconstructs the fixed population from read-only imports/admitted files, checks the frozen snapshot and all page/aggregate records, rehashes **every original and every output**, detects missing/extra crop files, and recomputes summary counts. It returns nonzero on any mismatch, missing output or recorded page failure. `ok: true` requires all 258,465 originals and outputs and zero failed crops.

## Tests and guarded commit list

```sh
"$PWD/.venv/bin/python" -B -m unittest discover -s docs/records/harvest/recut_v1/v2_full -p test_run.py -v
python3 -B docs/records/harvest/recut_v1/v2_full/guarded_commit.py
```

**27 unit tests passed in 26.171 seconds.** The suite uses small synthetic crops and read-only population inventories. It does not run a detector or certify the required 50-crop output gate. `receipts/unit-tests.log` is the test receipt. `receipts/launch-status.json` preserves the blocked probe and exact launch command.

`commit-inputs.json` lists code, tests, README, ignore rules and receipts, bound to the starting HEAD/branch, file SHA256 values, modes and unchanged phase-0 dependencies. Git metadata is read-only here; no worker commit or staging attempt was made. After review, the coordinator can run the guarded helper with `--commit` in a writable context. It checks the exact staged set and never uses an alternate index or retries a rejected write.
