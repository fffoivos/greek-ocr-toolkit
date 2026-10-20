# T6hv: verify the T6h v2 masking run and write its completion receipt (gpt-6.1-sol, medium, network OFF, mechanical)

T6h (Mac v2 masking) completed at 15:27:
- PID 82255; pages_complete 5585/5585; failed 0;
- elapsed 9,915 s; 29.9 pages/min;
- host 192.168.1.13; tree 63c640a3; params 801d517e.

Outputs are under `docs/records/harvest/recut_v1/v2_full/out/` (git-ignored).

## Do
1. **Run the README's verify step:**
   `nice -n 5 "$PWD/.venv/bin/python" -B docs/records/harvest/recut_v1/v2_full/verify.py > docs/records/harvest/recut_v1/v2_full/out/verification.json`
   Your sandbox may not allow nice 15; use what it allows and record it. It re-hashes every output against the records and every original against the source crops. **Any mismatch: STOP and report.**
2. **Completion receipt** `docs/records/harvest/recut_v1/v2_full/receipts/COMPLETION_RECEIPT_20261017.json`:
   - population 258,465 crops / 5,585 pages;
   - per wave × split: total / masked / changed / guarded / unmatched / parliament_skipped / failed;
   - totals;
   - `records.jsonl` sha256 and line count, `summary.json` sha256, `verification.json` sha256;
   - host, tree sha, params, library;
   - start and end times, rate;
   - the mock-gate baseline sha (c9bf83b0…).
3. Write a short `COMPLETION.md` beside it with the per-wave table.
4. **Commit:** the receipt, COMPLETION.md and verification.json (small; records.jsonl stays ignored, bound by sha). Leave a guarded commit list.

The last line must be exactly:
`T6hv: done | verified: <n>/<n> outputs | records sha: <sha> | changed: <n> | guarded: <n> | unmatched: <n> | parliament: <n>`
