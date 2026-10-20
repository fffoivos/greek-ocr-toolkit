# T6d: masked crops + own-ink audit for 200 held training lines (round1/round2/mixed), frozen T6a2 masking (gpt-6.1-sol, xhigh, network OFF, nice, ≤ 60 min)

This worktree (`sol/l1e-mask`) is branched from `sol/recut-v1`. It holds T6a2 masking, frozen params `801d517e…`, library `f203504a…`.

**Purpose.** The spell-check track's label-correction gate holds 90% of training lines. This sample decides whether that is foreign ink (masking fixes it) or detector failure (S8 retune).

**You build and test.** I execute the real run myself afterwards, because your sandbox cannot write `~/Projects/collect-v3-data/`.

## Build a runner
Create `docs/records/harvest/recut_v1/l1e_sample/run.py`, adapted from `docs/records/harvest/recut_v1/v2_pilot/run.py`. Keep the same safety: frozen-hash checks, nice ≥15, one fresh worker per page, one numerical thread, a disk watchdog at 10 GB, no W1 locks.

**Inputs**
- `--ids FILE`: one v2 line `id` per row, waves round1/round2/mixed only. Fail if any id is in another wave or is not a v2 line.
- Line metadata: `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`, plus `docs/harvest/<wave>/admitted.jsonl` (`crop_bbox`, `crop_sha256`). Group the lines by page.
- Rasters: `harvest_big/<wave>/images/`, plus `harvest_big/round1/rescue/images/` for round1 rescue pages. Resolve them with the feasibility scan `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/pages_scan.jsonl`.

All inputs are read-only.

**Processing**
- `--out DIR`: output root. The default must be `~/Projects/collect-v3-data/v2_masked/l1e_sample/`.
- Per page:
  - run the detector;
  - use T6a2's exact matcher, unchanged (single-column waves, so no x-overlap restriction);
  - run `mask_foreign_ink` on each **selected** line's original `crop_bbox`.
- **Do not stop on matching failures.** This sample is diagnostic: record them per line (ambiguous / unmatched) and leave the crop unmasked.

**Per-line record**
- id, wave, page;
- old box;
- original / stored / masked sha, and a re-cut pixel-equality check;
- **foreign pixels removed**;
- **own pixels lost**, measured with T6a2's dev method (`docs/records/harvest/recut_v1/masking/audit_dev.py` component ownership), reusing its functions;
- fill statistics;
- match status and failure kind;
- changed or not.

**Outputs.** Masked crops at `crops/<wave>/<doc>/<file>.png`, beside nothing else; the originals stay untouched. Plus `lines.jsonl` and `receipt.json` (counts per wave, totals, the share masked / changed / failed, the own-loss distribution).

## Test it
- Run it on **5 of the real ids**: the first 5 rows of `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_masking_sample_ids.txt`. That file holds 200 ids from the spell-check lead (round1 80, round2 60, mixed 60; greek_poly train lines held by L1E). Validate all 200 ids, but process only 5.
- Write to `--out` inside this worktree, e.g. `docs/records/harvest/recut_v1/l1e_sample/test_out/`, which must be git-ignored.
- Check that the records are complete and the originals unchanged.
- Add unit tests for: id validation, the page grouping, and that the default out-path is outside the checkout.

## Hand-off
Write `docs/records/harvest/recut_v1/l1e_sample/README.md` with the exact command I run:

`nice -n 15 .venv/bin/python -B docs/records/harvest/recut_v1/l1e_sample/run.py --ids <file>`

Commit with a guarded helper that excludes ignored paths. The last line must be exactly:

`T6d: done | runner ready | stand-in test: 5 lines <ok> | own-loss audit: reused audit_dev.py <yes|no> | tests: <n> passed`
