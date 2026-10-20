# Sourcing track hand-off, 18 Oct 2026 ~10:45 EEST (Claude usage stop)

The full state, the decisions and the commands are in `MORNING_NOTE_20261018.md` (7fbaf302) in this directory. This file adds what changed since then and the in-flight runs.

## In flight (no Claude needed)
- **BSB resume 2 (W2):** launched at 10:40. Supervisor **52080**, worker 52083; log `~/Projects/collect-v3-data/run/collector.log`.
  - 300 BSB pages remain under the owner's go (500/800 done). The MDZ window frees until about 11:15, so the run may defer part of the pages at the cap, then finalize (W1 + W2 rebuild, ~4.5 h).
  - **Stop only via** `kill -TERM 52080` (the supervisor). Never signal the worker.
  - A session guard (it may die with the session) sends that TERM if free disk drops below 10 GB.
- No Sol jobs are running.

## When BSB resume 2 ends (collector.exit written)
1. **Snapshot** the features **before any other collector run**:
   ```sh
   D=~/Projects/collect-v3-data; T=$(date +%Y%m%d_%H%M); cp -p $D/run/W1/features.jsonl $D/snapshots/W1_features_$T.jsonl; cp -p $D/run/W2/features.jsonl $D/snapshots/W2_features_$T.jsonl; (cd $D/snapshots && shasum -a 256 W1_features_$T.jsonl W2_features_$T.jsonl > SHA256_$T.txt)
   ```
2. **If BSB pages are still pending** (cap deferral), relaunch the same command once the window allows, and snapshot again afterwards:
   ```sh
   cd ~/Projects/greek-ocr-toolkit-sol-collect; export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json COLLECT_V3_PYTHON=$PWD/.venv/bin/python; D=~/Projects/collect-v3-data
   nice -n 10 sh collect_v3/launch_detached.sh $D/run --config $D/config_w1_mac.json --output-root $D/run run --tranche W2 --sources bsb_poly1850 --execution-host owner_mac --enable-network --serbian-codec
   ```

## Waiting on the owner
**(b) The full-population geometry run.** Disk now allows it: 26 GB free at 10:35.
```sh
bash ~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seg/cp7/launch_population_geometry.sh 4
```
- 3,057 pages, about 5.3 GB, about 1.2 h with 4 workers.
- **Rebind its population to the newest snapshot first,** if BSB resume 2 added pages. That is a small Sol task: the page list currently comes from the 05:24 snapshots.

## After (b): Sol briefs plus lead rulings, Claude needed
1. CP8 items 3–7 of `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG2_review_1.md`.
2. Re-run `build_release_admission.py --tranche all` through `greekocr.harvest.qualified_admission` (manifest 29af474e) on full geometry. This produces the final release-v3 admission file, with counts per class against the data-plan quotas.
3. `stage_crops.py` for the admitted rows (8,317 deferred plus the new ones).
4. The W2 completion report. Marks for the grave-heavy W2 strata are deferred to after the Claude reset (the owner's no-Opus rule); the Sol targeted letter pass is an allowed earlier option.

## Since the morning note
- Deletions approved by the coordinator:
  - sol-collect replays and validation (75,995 files);
  - `v2_masked/pilot` and `w1_masked_records`;
  - recut_v1 items 1–8 (344,239 untracked files: v2_full/out, w1_masked masked crops, tmp, masking outputs, mock-out).
  - 0 tracked files removed. The lists are in the session scratchpad (`deleted_20261018.txt`, `deleted_recut_v1_20261018.txt`).
- `seg/CP5_verification.json` is **bound by the CP7 freeze**. It is restored from its .gz (sha cc513146…); never delete it.
- Collector worker 77125 was SIGKILLed at 08:5x after ignoring a TERM sent to the worker (the correct stop is via the supervisor). Exit −9; nothing durable was lost.

## Update 16:03: BSB resume 2 finished
- **Result:** exit 0. W2 BSB is **736/800** (729 read, 7 excluded). **64 pages are deferred** at the MDZ cap; they need one more resume with the same command from about 11:15 on 19 Oct.
- **Finalize:** completed, but the storage diet **removed W2/features.jsonl again**, so there was nothing to snapshot.
- **Next, after the last resume:** one `materialize --tranche W2` (command in MORNING_NOTE), then the snapshot. Rebind (b) to that snapshot.
- **Free disk:** 84 GB.

## 19 Oct: superseded
`greekocr.harvest.qualified_admission`, the SEG CP ledger, `build_release_admission.py` and the ADMW2 admission files (`w2_originals_v3_*`, `gazette_w2_originals_v3_*`, `w1_originals_v3_screened_*`) are **SUPERSEDED, and parked**. The owner's Clariden filter pipeline (segmentation 0.8 = the owner's three rules) is the admission tool; the segmentation lead owns it. Sourcing now supplies the inputs: the W1/W2 rows (snapshots), the edition-level split (SPLIT1) and the original crops on Clariden (CROPS2).
