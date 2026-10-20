# SEG-CP7a3: prepare geometry for the drawn 100, recompute the sealed decisions, and prepare (do NOT run) the full-population geometry run (gpt-6.1-sol, medium, network OFF, no reading)

**Context:** CP7a2 (12603fea) drew the fresh uniform 100, but all 100 were sealed `geometry_unavailable`, because the collector's storage diet discards g1b geometry per page. The coordinator ruled:
- **(a) go:** prepare geometry for the ≤ 100 pages of the drawn rows;
- **(b) hold:** the full population needs the owner's explicit permission, because it is a 3-hour Mac run. Prepare it fully; do not run it.

All CP7a constraints still apply. Freeze `seg/CP7_FREEZE.json` (9212fe49…): confirm that the code still hashes to it, and stop if anything drifted.

## (a) The gate pages: run this now
1. **The draw is unchanged** (seed `seg-cp7:fresh100`). Do not redraw. List the distinct source pages of the 100 rows.
2. Prepare their geometry with the **CP2 fallback mechanism, exactly as CP3/CP4 did** (`prepare_cp3_geometry.py`/`prepare_cp4_geometry.py` pattern; existing pipeline; once per source-bound page; explicitly counted; full identity binding).
   - Write it into a separate cache: `docs/records/harvest/collect_v3_admission/seg/CP7_geometry/` (git-ignored if large).
   - Write nothing to the live run root, where a BSB collector run is live. Read the source rasters only.
3. **Recompute the sealed composed decisions** for the 100 rows on the frozen code. Keep them sealed; readers never see them.
4. Confirm the packs are byte-unchanged, since they contain no decisions. Report:
   - pages prepared, failures, s/page, MB/page;
   - how many of the 100 are still `geometry_unavailable` after preparation, and why (inconsistent planes, inverted rows, …);
   - the sealed screen-drop count, by rule.

## (b) The full population: prepare, do NOT run
Write `docs/records/harvest/collect_v3_admission/seg/cp7/prepare_population_geometry.py` plus a detached launcher `launch_population_geometry.sh`:
- **Scope:** every distinct page of the W1 + W2 pre-screen population (from the snapshots).
- **Behaviour:**
  - resumable: skip pages already prepared and hash-valid;
  - per-page counted, with a progress file;
  - N workers (default 4);
  - `nice 10`;
  - disk watchdog: stop at < 10 GB free.
- **Output** goes **outside any repo checkout**: `~/Projects/collect-v3-data/geometry_prep/` (a cache plus a receipt per page).
- **Detachment:** detached via `nohup … &` with a pid file.
- **Report:** the exact command, page count, disk estimate, wall-time estimate at 1/2/4 workers (from your measured s/page in (a)), and how to monitor and stop it.
- Tests: resumability on 2 pages (dry-run mode), the watchdog, and skip-valid.

Update `seg/CP7a_RECEIPT.md` and `seg/CP7_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP7a3: done | gate pages prepared <n> (fail <f>, <s> s/page, <mb> MB/page) | still unavailable <u>/100 | sealed drops <k> (<by rule>) | packs unchanged | population run: <pages> pages, ~<GB> GB, ~<h> h @4 workers, command ready (not run) | tests: <n> passed`
