# ASTRA-CP3B — wave-2 v4 prelaunch review

**BLOCK launch: one HIGH finding makes both production H7 verdicts permanently pending. Data identity, exposure, smoke execution and the nine-run budget otherwise pass.**

Reviewed firsthand, read-only. No files changed or jobs submitted.

## Findings

1. **HIGH — the report erases the preregistered numeric evaluation slice.**  
   [bench/e4_wave2.py:749](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/bench/e4_wave2.py:749) replaces the existing `numerics` category with census `primary_class == numerics_tables`.

   Independent full-reference recount:

   | Instrument | Reference rows | Preregistered numeric rows | Replacement numeric rows |
   |---|---:|---:|---:|
   | v2_test | 42,038 | 221 | **0** |
   | v2_test_full_coverage | 43,883 | 221 | **0** |

   Every reference row in these views has census primary class `prose`. The original category is the overlapping E3 numeric rule, explicitly retained by [PREREGISTRATION.md:22](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/PREREGISTRATION.md:22).

   **Failure scenario:** even nine successful runs produce `H7_PENDING_MISSING_SEEDS_OR_SUPPORT` for **both contrasts**, because [the verdict rejects zero support](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/bench/e4_wave2.py:289). I reproduced this using the committed verdict function: an otherwise confirming three-seed example becomes pending when numeric support is zero. Smoke cannot catch this: [line 280](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/bench/e4_wave2.py:280) returns `SMOKE_ONLY` before validating support.

   **Fix:** preserve `summarize()`’s `by_category['numerics']`; keep census `numerics_tables` separately. Verify **221 numeric rows in each complete view** and exercise production verdict evaluation. Commit and deploy the corrected bytes, then obtain a scoped re-review.

2. **MEDIUM — duplicated breathing in one sf7 target, independently corroborated.**  
   `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01/release_v4_sf7_edits.jsonl:205`, row `lekythos--3bfc4a385d61b883--s001-l0106`: `στὴν᾿ Αθήνα.` → `στὴν᾿ Ἀθήνα.` The hash-verified crop contains one breathing; the target retains the detached mark while adding another to Α.  
   **Effect:** one erroneous corrected target. **Fix:** repair mark ownership in a future versioned overlay; retain this qualification in CP4. This corroborates Sol’s sample finding, not a population error rate.

3. **MEDIUM — residual raw OCR error, independently corroborated.**  
   The same release’s `release_v4_admission.jsonl:124956`, row `gazette_modern--dacf995fd419bebd--s000-l0113`, contains `Χρξώστες Διάφοροι`; the hash-verified crop reads `Χρεώστες Διάφοροι`.  
   **Effect:** an imperfect raw training target, consistent with the registered raw-label recipe. **Fix:** catalogue it for subsequent label repair. It does not invalidate this recipe comparison.

4. **LOW — handoff documentation mixes current and obsolete instructions.**  
   [Documented REVIEW_INPUTS.md:3](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/REVIEW_INPUTS.md:3) still says v4 is unavailable. The current packet is [out/runner2/REVIEW_INPUTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/out/runner2/REVIEW_INPUTS.md). Its line 80 also calls aggregate exclusive, although [the aggregate script](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/scripts/clariden/e4_wave2_aggregate.sbatch:2) has no explicit `--exclusive`.  
   **Failure scenario:** an operator follows superseded gates or misstates requested resources. **Fix:** redirect the old handoff and correct the aggregate description.

## Cleared items

**Committed/deployed identity.** All **572/572** packaged files match commit `ceb4a0044a81ca4855be3054ab847737251e8b6c` and live deployment; **0 mismatches**, **0 missing/extra payload entries**.

- Manifest: `bdec8234d627571ba824c1fe3b0f04e82a531356dc4d1e2989003d9463ff63eb`
- Archive: `d95bef43200eaa236db1646afdbf53c606445ad1e8e3b49dff914e895cc9b7db`
- Live release receipt, bound inputs and native linefactory match their supplied pins.

**Census and arm identities.** I scanned and hashed all **592,466 census records**, reproducing the pinned `a3daa187…` digest. Every training inventory row has a matching ADMIT/train decision and crop identity: **0 missing / 0 invalid**.

| Arm | Unique real rows | Independently verified identity |
|---|---:|---|
| ctrl | 196,227 | v_c factory pool ∩ census_06 ADMIT/train |
| add | 364,173 | ctrl + 167,946 raw release rows |
| add_corr | 364,173 | Identical membership; registered label overlays |

Census old-pool availability is **196,234**; the other **7 IDs are absent from native v_c**, explaining the intersection exactly. All **196,227 control label-ID sequences** match their factory originals. Release comprises **50,622 W1 + 117,324 W2**, with **0 raw-text hash failures / 0 codec rejections**. Nested-set differences and unexpected shared metadata changes are **0**.

| Overlay | File rows / unique IDs | Changed training rows | Unmatched | Rejected |
|---|---:|---:|---:|---:|
| sf7 | 904 / 904 | 904 | 0 | 0 |
| ru1_v3_edits | 680 / 680 | 167 | 513 | 0 |
| n1_v1_w1 | 629 / 629 | 0 | 629 | 0 |
| **Total changed** | | **1,071** | | **0** |

Changes were independently compared after codec encoding. Their classes are **897 Greek polytonic / 7 Greek–Latin / 167 Cyrillic**; none becomes `numerics_tables`. N1 has no treatment exposure in this retest.

**Exposure.** Rehashed and recounted seal04: **2,253 test + 437 dev**, **2,690 unique keys/hashes**, **199 editions**; all edition mappings agree. Each arm has **0 key / row-ID / original-crop SHA / factory-crop SHA / seal04-edition overlaps**. Overlaps with all **200 SPLIT2 held-out editions** and protected crop hashes are also **0**. The **190,486 synthetic records** are unchanged as a multiset and have **0 seal04 crop-hash or row-ID matches**.

**Recipe parity.** Production parameter construction differs only by arm mix and model seed, after normalizing output paths. Common settings: codec v2.1, compact ×2, height 48, **8 × 428,872 draws**, batch 64, accumulation 1, AdamW `1e-4/.05`, unchanged OneCycle and validation selection. This specifies **53,616 updates/run**. Add/add_corr share pools, fractions and ordering; their smoke nonlabel manifests are hash-identical. Ctrl versus add intentionally changes sampling proportions, as preregistered.

**Smoke.** Live log hash matches `eabd11cd…`; its embedded review packet equals the saved packet. Saved Slurm history records **3713629 COMPLETED 0:0, 1,235 seconds**. Verified:

- Wheel-venv runtime, GH200, CUDA matmul, no `LD_LIBRARY_PATH`/`LD_PRELOAD`.
- Native imports **10/10 release, 437/437 dev, 2,253/2,253 test**, zero drops.
- All three arms: **4 updates**, actual run paths in their logs, **6/6 best/last checkpoint hashes** matching.
- **30 prediction files × 4 rows**, all prediction/checkpoint bindings matching.
- Aggregate `DONE`, no missing arm; seal04 remains **diagnostic_only**.

This clears sampled execution, not H1’s production verdict path.

## Reviewed launch and budget

Three allocations: **a0140 / normal / 1 node / 1 task / 3 GPUs / exclusive / 12:00:00**, respectively ctrl, add and add_corr, each with seeds **0/1/2**. Aggregate: **normal / 00:26:00 / no GPU request**, `afterok` on all three. No separate production preflight.

The exact literal commands are at [REVIEW_INPUTS.md:83](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/out/runner2/REVIEW_INPUTS.md:83). Equivalently, with the reviewed root exported:

```sh
export E4_ROOT=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_ceb4a00_20261021_prep02/code
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export E4_INPUTS="$E4_ROOT/out/e4/wave2_prep/INPUTS.bound.v4.seal04.json"
export E4_PREP="$W/greek-page-ocr/out/e3"
export E4_CAMPAIGN="$W/greek-page-ocr/out/e4/wave1b"
export E4_COORDINATOR=1
unset LD_LIBRARY_PATH LD_PRELOAD

sbatch --parsable --account=a0140 --uenv-passthrough=ignore --job-name=e4_wave2_job01 --export=ALL,E4_ROOT="$E4_ROOT",E4_JOB=job01,E4_SMOKE=0 --output="$E4_ROOT/out/e4/wave2/job01/slurm_%j.log" --time=12:00:00 "$E4_ROOT/scripts/clariden/e4_wave2_job01.sbatch"
sbatch --parsable --account=a0140 --uenv-passthrough=ignore --job-name=e4_wave2_job02 --export=ALL,E4_ROOT="$E4_ROOT",E4_JOB=job02,E4_SMOKE=0 --output="$E4_ROOT/out/e4/wave2/job02/slurm_%j.log" --time=12:00:00 "$E4_ROOT/scripts/clariden/e4_wave2_job02.sbatch"
sbatch --parsable --account=a0140 --uenv-passthrough=ignore --job-name=e4_wave2_job03 --export=ALL,E4_ROOT="$E4_ROOT",E4_JOB=job03,E4_SMOKE=0 --output="$E4_ROOT/out/e4/wave2/job03/slurm_%j.log" --time=12:00:00 "$E4_ROOT/scripts/clariden/e4_wave2_job03.sbatch"
```

**These commands remain blocked by H1.**

| Requested-hour accounting | GPU-h |
|---|---:|
| Production limits: 3 allocations × 3 GPUs × 12 h | 108.000000 |
| Accumulated wave-2 spend | 0.840556 |
| **Maximum reviewed total** | **108.840556** |
| Headroom below 150 | **41.159444** |
| Headroom below 120 | **11.159444** |

**The nine runs fit both requested-hour comparisons.** The 0.840556 includes earlier attempts; October 21 alone contributes 0.343056. Whole-node accounting gives a separate conservative maximum of **151.302222 allocated GPU-h**, including aggregate; that is not the specified requested-hour basis. This review does not certify future S1-series spending.

VERDICT: BLOCK launch until H1 is fixed and re-reviewed | BLOCKERS: 0 | HIGH: 1