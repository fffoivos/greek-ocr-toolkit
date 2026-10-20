# Sourcing: morning note, 18 Oct 2026 (sourcing lead)

## Owner decisions needed
1. **Free disk space.** Free space is about 5.8 GB. The work below needs about 15 GB.
   - **Proposal:** delete the data in the parked worktrees, about **9.8 GB**. These are sparse copies of main-checkout data, listed under "separate owner decision" in `greek-ocr-toolkit-spellcheck/docs/CLEANUP_PLAN_20261017_sourcing.md`:
     - sol-inventory `pilots_v2` (5.6 GB);
     - sol-funnel-gr `sample_v1` (1.9 GB);
     - sol-inventory `round1` (849 MB);
     - sol-inventory `collection` (738 MB);
     - sol-inventory `oa_rebind_v1` (727 MB).
2. **(b) The full-population geometry run** (MacBook processing, 3,057 pages, about 5.3 GB, about 1.2 h with 4 workers at nice 10; resumable; stops below 10 GB free):
   ```sh
   bash ~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seg/cp7/launch_population_geometry.sh 4
   # monitor: cat ~/Projects/collect-v3-data/geometry_prep/progress.json
   # stop:    kill -TERM "$(cat ~/Projects/collect-v3-data/geometry_prep/population.pid)"
   ```

## Relaunch commands (held; bulk writes)
Run from `~/Projects/greek-ocr-toolkit-sol-collect`.

1. **BSB resume 2.** The remaining W2 BSB pages are 300 of the 800 under the owner's go (500 done: 497 read, 3 excluded).
   - **MDZ window:** the cap is 500 images per rolling 24 h. The 17 Oct W2 BSB reads (about 10:22–11:15) age out **about 10:25–11:15 today**; today's pass-1 reads (05:24–05:47) age out about 05:25–05:47 on 19 Oct. **From about 11:15 today there is room for all 300 remaining pages.** The window does not close: it is rolling, so any later time also works.
   - Command (authorised one-off, logged as O):
   ```sh
   export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json COLLECT_V3_PYTHON=$PWD/.venv/bin/python
   nice -n 10 sh collect_v3/launch_detached.sh ~/Projects/collect-v3-data/run --config ~/Projects/collect-v3-data/config_w1_mac.json --output-root ~/Projects/collect-v3-data/run run --tranche W2 --sources bsb_poly1850 --execution-host owner_mac --enable-network --serbian-codec
   ```
   - **Stop:** `kill -TERM <supervisor>` from `run/collector_pids.json`. Never signal the worker.
   - Its finalize rebuilds W1 + W2 features. That needs about 2.2 GB of headroom at the end, and takes about 4.5 h with materialize included.
2. **One materialize,** only if the BSB run's finalize is not completed:
   ```sh
   nice -n 10 .venv/bin/python -B collect_v3/run.py --config ~/Projects/collect-v3-data/config_w1_mac.json --output-root ~/Projects/collect-v3-data/run materialize --tranche W2
   ```
   - Afterwards, snapshot `run/W1` and `run/W2` `features.jsonl` into `~/Projects/collect-v3-data/snapshots/`, with SHA256, **before** any other collector run.
3. **Crop staging for the deferred admitted rows** (8,317, about 100 MB) through `stage_crops.py`, after the final admission re-run.

## State (all committed on sol/recut-v1; history not rewritten since aa3d9067)
- **Screens:** SEG CP1–CP6 PASS. The screens were accepted under ruling (ii): 0 adjudicated misses in two fresh draws, false drops about 2%, all on the safe side.
- **Reviews:** ASTRA-SEG2 done. CP8 items 1–2 done (ab29281d): evaluator `greekocr.harvest.qualified_admission`, manifest 29af474e.
- **Admission on the current geometry (ADMW2):**
  - W2 75,244 → 8,139 admitted (86.7% `geometry_unavailable`);
  - Gazette W2 40,804 → 5,411;
  - W1 screened 32,205 → 3,280.
  - **These are placeholders until (b).** The builder `build_release_admission.py` re-runs them.
- **W2 stratum checks:** letters pass in all 8 strata; crop_ok is handled by the screens; marks are deferred to after the Claude reset.
- **v2 census:** CENSUS3 (ef694589…) is the standard.
- **Known classes:**
  - end-clips, admitted and counted (about 4–8% of the fresh draws);
  - `geometry_unavailable`, fail closed;
  - `orientation_unknown`, admitted and counted;
  - the Gazette structural-split false fires (ASTRA-SEG2 diagnosis; a fix belongs in the toolkit's row-identity contract).

## After (b): the order of work
1. BSB resume 2.
2. One materialize, then a snapshot.
3. CP8 items 3–7: page inventory reconciliation, pinned replay denominator and row ledger, full accounting, old-screen delta explanations, hash/byte reconciliation.
4. The final release-v3 admission file (W1 + W2 + Gazette + BSB), with counts per class against the data-plan quotas.
5. Crop staging.
6. The W2 completion report.
