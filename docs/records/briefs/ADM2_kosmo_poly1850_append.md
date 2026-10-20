# ADM2: append kosmopolis poly1850 masked rows to the admission file as a release-v3 candidate (gpt-6.1-sol, network OFF, mechanical)

Write only under `docs/records/harvest/collect_v3/release_admissions/`. A live W2 collection imports `collect_v3/` from this checkout: never touch it.

## Ruling (coordinator)
- Append the kosmopolis **poly1850** masked rows to `w1_masked_1d.jsonl` as a separate class entry with `arm = "release-v3-candidate"` and `marks_status = "pending_opus"`.
- **Do not alter the 16,562 existing `arm = "wave-1d"` rows.** The 1d package is preregistered on them and reads only `arm = wave-1d`. Verify that their bytes are unchanged: compare the sha256 of the wave-1d subset before and after.

## Evidence for the class
- Cards: sol/recut-v1 72ae7114 (T6g; pool 462, 100 cards).
- Sol reading: 87db4392 (`docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/results.json`). Letters 96 and crop_ok 99 are final; marks 90 are pending Opus.

## Build
1. Reuse the existing builder `build_w1_masked_1d.py` logic (same validation) for **kosmopolis poly1850 only**:
   - rows from W1 `crop_tight_page.jsonl` plus the T6b records in `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmopolis/records.jsonl`;
   - exclude screen_merged, rotated_crop, release-exclusion ids and unmatched;
   - keep masked and guarded_original rows.
   - Expect 462 rows (the T6g pool); report any difference with reasons.
2. Each row has the same fields as the existing rows, plus `arm`, `marks_status` and `provenance.sol_reading = "sol/recut-v1 87db4392"`. Hash-validate each row exactly as the builder does.
3. Update `w1_masked_1d_summary.json`:
   - counts per arm × source × class;
   - the new file sha256;
   - a separate `wave1d_subset_sha256` (unchanged from before);
   - the bound input hashes, including the SRK2 results.json sha.
4. **Tests:** the wave-1d subset is byte-identical to before; the new rows validate; the arm filter yields 16,562 and 462.

## Hand-off
Leave a guarded commit list. The last line must be exactly:
`ADM2: done | wave-1d rows: 16562 (unchanged sha <ok>) | release-v3-candidate rows: <n> | file sha: <sha> | tests: <n> passed`
