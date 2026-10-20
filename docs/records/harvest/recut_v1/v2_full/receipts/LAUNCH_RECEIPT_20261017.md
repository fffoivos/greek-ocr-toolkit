# T6h launch receipt (one-off by the sourcing lead, coordinator-authorised option (a), 17 Oct 2026)

**Reason.** The Sol sandbox forbids setsid and nice ≥15 (receipts/launch-status.json). The coordinator authorised the lead to run exactly the two README commands, verbatim, from the sol-recut worktree.

1. **Mock gate**, 12:40:14 → 12:41:30 EEST:
   `nice -n 15 "$PWD/.venv/bin/python" -B docs/records/harvest/recut_v1/v2_full/run.py mock --workers 4`
   - Result: `{"ok": true, "identical": 50, "compared": 50, "differences": {}, "baseline_sha256": "c9bf83b077d3893e34d7eced2d2dd66826c9f98557a9d093f9f8e58b11cd0c4d"}`
   - Host 192.168.1.13; tree 63c640a3; params 801d517e; nice 15; 4 workers; 50/50 pages; 0 failed.
2. **Full run (detached)**, launched 12:41:35 EEST:
   `PATH="$PWD/docs/harvest/recut_v1/v2_full/bin:$PATH" setsid nohup nice -n 15 "$PWD/.venv/bin/python" -B "$PWD/docs/harvest/recut_v1/v2_full/run.py" run --workers 4 --detached > "$PWD/docs/harvest/recut_v1/v2_full/run.log" 2>&1 < /dev/null &`
   - Status at +90 s: PID 82255 alive (NI 20, own process group); 66/5,585 pages complete; 0 failed.
