# ASTRA-CLEANUP certification review

Reviewed `cleanup/20261019`, base `ac1c38cf6` → HEAD `9dd7e80fdc`. Evidence includes exhaustive Git-tree accounting, all receipt hashes, source comparisons, raw score recounts and a full pytest run. Repository unchanged.

**Not certified for merge: four HIGH findings require resolution and re-review.**

[Full report and evidence links](ASTRA_CLEANUP_REVIEW.md)

## Findings

1. **[HIGH] Required files exist locally but are absent from Git and custody receipts.**  
   At [`.gitignore:78`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/.gitignore:78), broad ignore rules conceal **3,409 base files totaling 132,088,160 bytes**. None has a committed mapped destination or external receipt.

   Required new TSVs—including `LAYOUT_ALIASES_2.tsv`, `MOVE_MANIFEST.tsv` and receipt shards 02/03—are also untracked. [`scripts/layout_paths.py:16`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/scripts/layout_paths.py:16) opens the missing alias file unconditionally; an isolated import from committed source fails. SEG10’s **42,991,967-byte** raw replay is likewise untracked and unreceipted.

   **Fix:** commit required small metadata, deliberately retain or receipt every omitted file, and verify a checkout built solely from Git. [Complete missing-file list](unaccounted_base_files.tsv).

2. **[HIGH] Data relocation breaks readers.**  
   [`sf7_measure.py:33`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/scripts/labelfix/sf7_measure.py:33) hashes an unresolved local path after successfully reading its external counterpart. Data-enabled collection returns **7,007 tests collected, 1 error**.

   [`collection.py:251`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/greekocr/harvest/collection.py:251) rejects round1 and round2 despite available external inputs. [`r2_cards_prepare.py:317`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/scripts/labelfix/r2_cards_prepare.py:317) incorrectly rebases an unmoved sibling checkout: an actual row’s metadata changes from **1 admission / 1 record to 0 / 0**.

   **Fix:** consistently resolve reads, existence checks and hashes; preserve explicit sibling-checkout paths. [Reproduction results](reader_regressions.json).

3. **[HIGH] The mandatory full-suite gate fails.**  
   Raw result: **2 failed, 6,656 passed, 186 skipped, 19 errors; 63 subtests passed**, in **188.48 seconds**.

   [`test_r2_cards.py:30`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/tests/test_r2_cards.py:30) causes 19 errors by creating temporary directories inside the read-only repository. OS5 similarly writes a repository raster. The other failure exposes an existing global socket substitution leaking between tests.

   **Fix:** isolate temporary outputs and network substitutions, then rerun the entire suite under the requested conditions. These failures should not become historical skips. [Raw pytest log](astra-cleanup-head.log).

4. **[HIGH] Operational behavior changes beyond SEG10.**  
   [`stage_crops.py:79,122`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/stage_crops.py:79) changes the default disk floor **0 → 10 GB** and filters mixed legacy W1/W2 inputs to **W2 only**. These are intentional CROPS3 changes introduced after the specified base, not relocation changes.

   **Fix:** separate this operational work or explicitly expand its review scope and qualify it. This finding rejects “SEG10 is the only behavior change”; it does not establish that CROPS3 itself is incorrect.

5. **[MEDIUM] Current documentation contradicts current code.**  
   [`b_tools/README.md:9,68`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/B_training_data/b_tools/README.md:9), the segmentation guide and pipeline graph still describe **s4/.50–1.50** and obsolete integration limitations. Actual versions are **pipeline 0.3.1, segmentation 0.9-s5, numerics 0.3, census 0.6**, with band **.30–2.00**.  
   **Fix:** synchronize current guidance and clearly label historical material.

6. **[MEDIUM] Receipt metadata is incomplete.**  
   [`RECEIPTS/INDEX.md:9`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/cleanup_20261019/data_out/RECEIPTS/INDEX.md:9) understates totals. Nine later entries are absent from the manifest; CP5’s producing commit is literally `merge`.  
   **Fix:** update totals and manifest entries and supply a resolvable producing SHA.

7. **[LOW] One historical skip overstates its provenance.**  
   [`test_n1w1_r3.py:68`](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/tests/test_n1w1_r3.py:68) says “green at” a producing-phase anchor without an executed-green receipt.  
   **Fix:** qualify that wording or attach execution evidence.

## Cleared and verified

- **Taxonomy:** A.i/A.ii/A.iii map to real implementations and defensible historical generations. R7→R8 ancestry supports the distinction; these are not three independent current engines. B.a–d and AGENTS cover the requested process.
- **Base accounting:** 9,300 files remain at their paths; 31,936 have committed mapped destinations; 16,888 are externally receipted; **3,409 remain unaccounted**. Total **61,533**.
- **External custody:** all **16,897 entries / 10,494,028,696 bytes** checked; **zero size/hash mismatches**. All 16,888 base-derived external entries match original Git blobs. Symlink hashes cover link text.
- **Preservation:** the **147,025,055-byte SEGEVAL1.bundle** matches its receipt and exposes the documented bundled head. Original branch-tip SHAs remain reachable, although nine branch names advanced.
- **Size guard:** passed; **zero tracked files over 5 MB**.
- **Manifest:** **35 component occurrences, 23 unique files and 11 aggregate digests** all match.
- **Specific counts:** SF7 saved records recount **70 correct / 30 pending**; LQB contains **61,463 rows**. The report documents more than ten factual spot-checks.
- **Historical tests:** all **41 inspected function bodies remain unchanged**. The collection reduction is real: **7,329 − 530 + 24 = 6,823**, then 40 alias cases bring HEAD to **6,863**. Missing-input parameter collapse explains the reduction; it does not restore execution coverage.
- **SEG10:** independently recounted **1,705 replay rows**. Unfiltered FP/FN changes **16/15 → 4/19**; after the content gate, **11/15 → 2/18**. Owner-mark agreement improves **189/235 → 209/235**, but false negatives increase. Adoption is documented as a coordinator decision, not an owner ruling.

## Ordered asks

1. Repair committed custody and achieve zero unaccounted base files.
2. Fix the demonstrated reader regressions.
3. Obtain **0 failed / 0 errors** from the full read-only suite.
4. Resolve the additional operational-change scope.
5. Log or fix the lower-severity findings, then re-review the committed HEAD.

VERDICT: NOT CERTIFIED FOR MERGE — fix and re-review the four HIGH findings | BLOCKERS: 0 | HIGH: 4