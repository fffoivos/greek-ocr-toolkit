# ADM3: append screened, masked headings_caps rows to the admission file as a release-v3 candidate (gpt-6.1-sol, medium, network OFF, mechanical)

Write only under `docs/records/harvest/collect_v3/release_admissions/`. A live W2 imports `collect_v3/`: never touch it. Follow ADM2's method (`append_adm2_poly1850.py`, `test_adm2_poly1850.py`).

## Ruling (coordinator)
- Append the CAPS3 screened and masked headings_caps rows (masked + guarded_original; unmatched excluded; about 1,629) as `arm = "release-v3-candidate"`, `marks_status = "pending_opus"`.
- **The wave-1d rows stay byte-unchanged** (verify the subset sha), and so do the existing 462 release-v3-candidate kosmopolis rows.

## Inputs (read-only)
- CAPS3 records: `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps_masked/records.jsonl` (and the CAPS3 screen outputs under `caps3/`).
- W1 rows: `~/Projects/collect-v3-data/run/W1/features.jsonl` / `crop_tight_page.jsonl`.
- Evidence: sol/recut-v1 d8c31c97 (CAPS3 build), abaa200c (CAPS4: letters 100, crop_ok 99, marks 98 pending Opus).

## Build
- Same fields and hash validation as the existing rows, plus `arm`, `marks_status`, `provenance.sol_reading = "sol/recut-v1 abaa200c"` and `provenance.clip_screen`.
- Exclude rotated_crop, screen_merged, every release-exclusion class (including `n1_locked_eval`), and the edge-clip-screened rows.
- Report any count difference from 1,629, with reasons.
- **Summary:** add the counts per arm × source × class, and the edge-clip screen provenance:
  - helper name and tolerance;
  - 544 removed per source;
  - validation on CAPS2: 6/6 clipped flagged, 17/89 false positives.
  - Keep `wave1d_subset_sha256` unchanged, and update the file sha and the bound hashes.
- **Tests:** wave-1d and kosmopolis subsets unchanged; the new rows validate; the arm filter gives 16,562 / 462 / the new count.

The last line must be exactly:
`ADM3: done | wave-1d: 16562 (unchanged) | kosmo v3-cand: 462 (unchanged) | caps v3-cand: <n> | file sha: <sha> | tests: <n> passed`
