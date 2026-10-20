# CAPS2: aggregate the capitals/headings Sol reading (gpt-6.1-sol, medium, network OFF, mechanical)

Both contexts of CAPS1 finished through `run_bed.sh`: c1 and c2, 55 items each, mapped 50 + 50, 0 control errors, Codex 34 → 35%. Outputs are under `docs/records/harvest/recut_v1/w1_masked/caps1/` (answers, scan, ledger) and the launcher logs.

## Do
1. **Confirm** that each context's rollout scan (scanner v4) is clean, with coverage 55/55 images viewed. Quote the scan files. **If either is not clean, the run is VOID:** report and stop.
2. **Aggregate the 100 bed cards** through the keys: letters y/n/u, crop_ok y/n, marks y/n/na, error types and per-source splits.
   - **Ruling:** letters and crop_ok from Sol are final; marks are recorded as `pending_opus`.
   - Gate: letters ≥ 90 and crop_ok ≥ 90 on n=100.
   - Report each control's outcome as well.
3. **Route every `u` (unreadable) and every flagged failure** to `review_queue.jsonl`, with card id, line id, source, detail and the crop path, for a later lead or Opus eye (HANDOVER §8). Do not auto-accept or auto-reject them.
4. **Usage:** from the ledger; no estimates.

## Output
`docs/records/harvest/recut_v1/w1_masked/caps1/RESULTS.md` + `results.json` + `review_queue.jsonl`. Leave a guarded commit list. The last line must be exactly:
`CAPS2: <done|VOID> | letters y: <n> | crop_ok y: <n> | marks y: <n> (pending opus) | gate: <pass|fail> | controls: <k>/10 | review queue: <n> | tokens: <n>`
