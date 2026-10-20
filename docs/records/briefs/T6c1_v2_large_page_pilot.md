# T6c1: large-page pilot for masking collection v2 (gpt-6.1-sol, xhigh, network OFF, ≤ 60 min)

This runs in this worktree (`sol/recut-v1`), on top of T6a2 (eacb5c39). It uses the frozen masking: `greekocr/glyphs/foreign_ink.py`, params `801d517e…`.

**Ruling.** Pilot first. The full v2_test run (T6c2) waits for these numbers. All of v2 waits for the owner's explicit go.

**Bounds on this Mac:**
- run every compute process under `nice -n 15`;
- **at most 6 worker processes**, because a live collection (W1) and other sessions share the CPU;
- start a watchdog that stops your run if free disk on `$HOME` drops below 10 GB.

**Outputs.** Write only under `~/Projects/collect-v3-data/v2_masked/pilot/`. This is outside every checkout.
- Never write into `~/Projects/greek-ocr-toolkit` (the main checkout, another agent's) or into the W1 run root `~/Projects/collect-v3-data/run`.
- The original crops stay untouched.

## Inputs (read-only)
All are under `~/Projects/greek-ocr-toolkit/docs/harvest/`:
- collection v2 lines: `collection/v2/import_real_v2_test.jsonl`;
- crop boxes: `<wave>/admitted.jsonl`, field `crop_bbox`;
- page rasters: `harvest_big/<wave>/images/`; round1 rescue pages are in `harvest_big/round1/rescue/images/`.

The scratch feasibility scan lists page paths and sizes: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/pages_scan.jsonl` and `v2_masking_feasibility.md` in the same folder.

## Do
1. **Sample.** Draw **10 parliament and 10 vouli pages**, seeded `t6c1`, from the v2 **test** split pages. Parliament pages average 33.6 megapixels, about 4× the largest page in T6a2.
2. **Process each page:**
   - run the detector line-curve fit;
   - match every v2 line on the page to a fitted line curve, exactly as T6a2 did;
   - mask each line's original `crop_bbox` region;
   - write the masked crop and a per-line record: line id, original crop sha (re-cut and checked against the stored crop), masked sha, fill statistics, masked px/components, match status.
3. **Measure:**
   - seconds per page (detector, then masking), and megapixels;
   - peak RSS per worker;
   - **line-curve matching failures**: any v2 line with no matched curve, an ambiguous match, or a re-cut sha mismatch;
   - the share of crops changed.
4. **Stop rules** from the coordinator:
   - any parliament page taking **over 60 s**, **or**
   - **any** line-curve matching failure.

   If either occurs, record it, finish the current page, and stop.

## Hand-off
Write `~/Projects/collect-v3-data/v2_masked/pilot/PILOT.md` with a per-page table, the per-wave summary and the stop-rule verdict. Write `pilot_receipt.json` beside it. Commit only the code changes, if any, plus a copy of PILOT.md under `docs/records/harvest/recut_v1/v2_pilot/`, with the guarded helper.

The last line must be exactly:
`T6c1: done | pages: 20 | parliament s/page median/max: <a>/<b> | vouli s/page median/max: <c>/<d> | match failures: <n> | changed: <x>% | verdict: <go|stop>`
