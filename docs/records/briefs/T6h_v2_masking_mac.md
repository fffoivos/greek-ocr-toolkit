# T6h: v2 masking on the Mac, the wave-1d prerequisite (gpt-6.1-sol, network OFF)

This runs in this worktree (`sol/recut-v1`). T6f's Clariden route was dropped: 19/50 byte-identical. **The coordinator approved this Mac run.** A live W2 collection keeps CPU priority.

## Fixed semantics, unchanged from T6f phase 0
- Frozen source tree 63c640a3: `greekocr/glyphs/foreign_ink.py`, `recut.py`, params `801d517e…`, library `f203504a…`.
- The T6c2 worker and nearest-curve matcher (unmatched lines left unmasked and flagged).
- The T6b guard via `guard_measure`: original-crop grayscale pixels <128; strictly >0.30 restores the original bytes and sets `wrong_line_risk`.
- **Reuse `docs/records/harvest/recut_v1/v2_clariden/phase0_mask.py` and its bindings.** Write no new masking or matching code.
- Population: the v2 train + test imports (214,436 + 44,029). Parliament (76,463 lines on 645 pages) stays unmasked: byte-exact originals, `skipped_wave=parliament`. Dev is out of scope.
- **Host provenance:** every record carries `host` (`hostname`) and the source tree sha.

## Resources
- `nice -n 15`, **at most 4 worker processes**, one fresh process per page. Use the per-page memory cap from T6c2 (≤3 concurrent when the page is above 20 MP).
- A disk watchdog stops the run below 10 GB free.
- Do not touch `~/Projects/collect-v3-data/run` or its locks.
- Read-only inputs: the main checkout `~/Projects/greek-ocr-toolkit` (imports, admitted files, `harvest_big` rasters).

## Output (git-ignored, inside this worktree)
- `docs/records/harvest/recut_v1/v2_full/out/crops/<wave>/<doc>/<file>.png`: every v2 train/test crop, masked or byte-exact original.
- `out/records.jsonl`, per crop: id, wave, split, original sha256, output sha256, guard status (`masked` / `guarded_original` / `unmatched_original` / `parliament_skipped` / `failed_page`), match status, masked pixel and component counts, params hash, host, tree sha.
- `out/summary.json`: changed / guarded / unmatched / failed counts per wave × split.
- `verify.py`: re-hashes every output against the records, and every original against the source crops.
- Resumable: a page whose records are complete is skipped on restart. A page failure is recorded and the run continues; it is never silent.

## Steps
1. **Build** the runner as a thin wrapper around phase0_mask.py for the full population. Add unit tests for population counts, the parliament skip, resume and the guard.
2. **Test:** rerun the T6f 50-crop mock locally. The outputs must be **byte-identical to `v2_clariden/receipts/mock_mac_records.jsonl`** (output sha256 for all 50).
3. **Launch the full run detached,** so it survives the end of your session: `setsid nohup`, logging to `v2_full/run.log`, PID in `v2_full/run.pid`. Confirm it is alive and has completed at least 3 pages before you exit. Report the measured pages/min and an ETA.
   - **If your sandbox cannot leave a detached process running,** stop. Report `launch blocked` with the exact one-line launch command, and the lead will escalate.
4. Write `docs/records/harvest/recut_v1/v2_full/README.md` with: the launch command, how to check status, how to verify at the end, and the resume command.

## Hand-off
Leave a guarded commit list (code, tests, README; out/ ignored). The last line must be exactly:
`T6h: <launched|launch blocked> | mock 50 identical to Mac: <ok> | rate: <pages/min> | ETA: <hh:mm Athens> | tests: <n> passed`
