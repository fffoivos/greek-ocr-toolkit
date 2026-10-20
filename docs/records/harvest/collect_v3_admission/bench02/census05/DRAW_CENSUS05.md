# BENCH02J — census_05 real draw

Extract job: 3704816; deployed package: `bench02_pkg/0019ce4b`. Draw mode: `admitted W1/W2`; edition cap: 50 per class × edition; series cap: 150 per class; fair round-robin; forced pools: both; overdraw: 20%, rounded per subgroup. No code changes or additional flags.

Receipt: tags SHA-256 `8b5fc9d3acccd12572d744e35984b0e89c50df1901ac066ed0bc8c2d5840f553`; bytes 27,990,456. Both equal the receipt. Decisions 320,479 = SPLIT2 train 253,402 + dev 7,007 + test 60,070. Diagnostics = joined = dev + test = 67,077; diagnostic join rate 1.0; unmatched 0. All requested differences: 0.

| Split | Class | Pre-filter | Eligible supply | Quota | Target | Drawn | Credited | Deficit | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| test | caps_headings | 1111 | 1111 | 120 | 144 | 144 | 120 | 0 | 109 | 6 | 8.33% | True |
| dev | caps_headings | 439 | 439 | 30 | 36 | 36 | 30 | 0 | 15 | 3 | 36.11% | True |
| test | curved_skewed | 1924 | 1917 | 100 | 120 | 120 | 100 | 0 | 54 | 10 | 5.83% | True |
| dev | curved_skewed | 146 | 146 | 25 | 30 | 30 | 25 | 0 | 17 | 4 | 23.33% | True |
| test | degraded | 0 | 0 | 100 | 120 | 0 | 0 | 100 | 0 | 0 | 0.00% | False |
| dev | degraded | 0 | 0 | 25 | 30 | 0 | 0 | 25 | 0 | 0 | 0.00% | False |
| test | font_extremes | 6474 | 6438 | 100 | 120 | 120 | 100 | 0 | 54 | 10 | 6.67% | True |
| dev | font_extremes | 391 | 391 | 25 | 31 | 31 | 25 | 0 | 12 | 4 | 29.03% | True |
| test | greek_latin | 1447 | 1444 | 160 | 192 | 192 | 160 | 0 | 40 | 7 | 6.77% | True |
| dev | greek_latin | 16 | 16 | 40 | 48 | 16 | 16 | 24 | 6 | 3 | 31.25% | False |
| test | historical_russian | 344 | 344 | 120 | 144 | 144 | 120 | 0 | 6 | 1 | 19.44% | False |
| dev | historical_russian | 0 | 0 | 30 | 36 | 0 | 0 | 30 | 0 | 0 | 0.00% | False |
| test | latin | 2843 | 2843 | 160 | 192 | 192 | 160 | 0 | 28 | 6 | 6.77% | True |
| dev | latin | 4 | 4 | 40 | 48 | 4 | 4 | 36 | 2 | 2 | 50.00% | False |
| test | leaders_dashes | 5087 | 5021 | 100 | 120 | 120 | 100 | 0 | 48 | 10 | 6.67% | True |
| dev | leaders_dashes | 276 | 276 | 25 | 30 | 30 | 25 | 0 | 11 | 4 | 26.67% | True |
| test | long | 3201 | 3162 | 160 | 192 | 192 | 160 | 0 | 50 | 9 | 14.06% | True |
| dev | long | 110 | 110 | 40 | 48 | 48 | 40 | 0 | 10 | 4 | 33.33% | True |
| test | modern_cyrillic (Serbian-only) | 167 | 167 | 160 | 192 | 48 | 48 | 112 | 3 | 1 | 33.33% | False |
| dev | modern_cyrillic (Serbian-only) | 94 | 94 | 40 | 48 | 12 | 12 | 28 | 2 | 1 | 50.00% | False |
| test | monotonic | 2236 | 2224 | 240 | 288 | 288 | 240 | 0 | 76 | 1 | 1.39% | False |
| dev | monotonic | 535 | 535 | 60 | 72 | 72 | 60 | 0 | 26 | 1 | 4.17% | False |
| test | numeric_cells | 2407 | 2386 | 200 | 240 | 240 | 200 | 0 | 67 | 10 | 10.42% | True |
| dev | numeric_cells | 168 | 168 | 50 | 60 | 60 | 50 | 0 | 25 | 4 | 8.33% | True |
| test | poly_dictionary_journal | 4662 | 4533 | 160 | 192 | 192 | 160 | 0 | 12 | 2 | 10.42% | False |
| dev | poly_dictionary_journal | 0 | 0 | 40 | 48 | 0 | 0 | 40 | 0 | 0 | 0.00% | False |
| test | polytonic | 2675 | 2675 | 360 | 432 | 432 | 360 | 0 | 22 | 6 | 11.57% | True |
| dev | polytonic | 356 | 356 | 90 | 108 | 100 | 90 | 0 | 2 | 2 | 50.00% | False |
| test | short | 463 | 454 | 120 | 144 | 144 | 120 | 0 | 53 | 10 | 9.03% | True |
| dev | short | 55 | 55 | 30 | 36 | 36 | 30 | 0 | 19 | 3 | 16.67% | True |
| test | vertical_turned | 1124 | 1120 | 100 | 120 | 120 | 100 | 0 | 38 | 7 | 16.67% | True |
| dev | vertical_turned | 773 | 773 | 25 | 30 | 30 | 25 | 0 | 22 | 1 | 6.67% | False |

## Totals

| Split | Credited / quota | Drawn / target | Classes filled | Deficit |
|---|---:|---:|---:|---:|
| test | 2248/2460 | 2688/2952 | 14/16 | 212 |
| dev | 432/615 | 505/739 | 10/16 | 183 |

Credit = min(drawn, quota), as emitted by the tool. Books diagnostic counts edition IDs, including gazette issues; canonical-work independence is unverified.

## Deficits

| Split | Class | Deficit | Supply | Reason / tool label | census_03 all-rows upper-bound supply |
|---|---|---:|---:|---|---:|
| test | degraded | 100 | 0 | no supply | 2611 |
| test | modern_cyrillic | 112 | 167 | Serbian-only | 332 |
| dev | degraded | 25 | 0 | no supply | 373 |
| dev | greek_latin | 24 | 16 | supply 16 < quota 40 | 17 |
| dev | historical_russian | 30 | 0 | no supply | 0 |
| dev | latin | 36 | 4 | supply 4 < quota 40 | 14 |
| dev | modern_cyrillic | 28 | 94 | Serbian-only | 198 |
| dev | poly_dictionary_journal | 40 | 0 | no supply | 0 |

`Serbian-only` is the tool label. `no supply` denotes tool supply 0; other shortage reasons show the emitted supply and quota. The tool emits no separate textual deficit-reason field. census_03 upper-bound supply is from `../sweep/upper_bound_ruled/counts.json` and is not admitted supply.

| Split:class | Subgroup drawn | Subgroup quotas | Subgroup deficits |
|---|---|---|---|
| test:modern_cyrillic | `{"sr": 48}` | `{"bg": 40, "ru": 40, "sr": 40, "uk": 40}` | `{"bg": 40, "ru": 40, "sr": 0, "uk": 40}` |
| dev:modern_cyrillic | `{"sr": 12}` | `{"bg": 10, "ru": 10, "sr": 10, "uk": 10}` | `{"bg": 10, "ru": 10, "sr": 0, "uk": 10}` |

## Pool

| Split | Admitted before exclusions | Eligible after exclusions, including unclassified |
|---|---:|---:|
| train | 168637 | 168637 |
| test | 36266 | 35940 |
| dev | 3364 | 3364 |

Admitted total: 208,267. Forced non-locked additions before caps/class selection: test lqb 25,864 + n1 5,147 = 31,011; forced editions included 99. Train rows 168,637; dev/test unclassified rows 102.

Locked registry: 3,635 unique IDs. Locked rows present in tags: 916 (test); admitted locked rows excluded by the draw: 326 (test), equal to all 326 emitted excluded rows. Candidate locked intersections: 0. The other 590 locked tag rows were not admitted. Candidate keys: 3,193 unique.

## Artifacts and determinism

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `docs/harvest/collect_v3_admission/bench02/census05/candidates.jsonl` | 3403349 | 3193 | `f02ddb58e582adb909317ad0e6955b2bd0539de91a2c2add21e6e1c861ca8602` |
| `docs/harvest/collect_v3_admission/bench02/census05/draw_plan.json` | 7999 | 155 | `4fbb8f4c23e96c8f8809e0c9e64f938db077ee8aa549af5a0e1078be7db48181` |

First run: `bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh`. Second run: the same unchanged wrapper and Python file in a temporary mirror, with original tags/receipt and split inputs symlinked, no additional flags. Candidates byte-identical: yes; counts identical: yes. Temporary directory `/private/tmp/bench02j-eoi_ndks` deleted.

Series cap: 3 × 50 = 150 per class; unverifiable without series identity. Unknown series rows: 29,715.

## P6 staging and coordinator command

Remote directory `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census05_draw/` was absent and created with exclusive `mkdir`. Candidates transferred using `rsync --ignore-existing`; overwritten files: 0. Remote readback: SHA-256 `f02ddb58e582adb909317ad0e6955b2bd0539de91a2c2add21e6e1c861ca8602`, bytes 3,403,349, lines 3,193; local match: yes. Read-only check: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census05_readout` does not exist (including dangling symlink check).

Verified against deployed `submit_job.sh`, `readout.sbatch`, `job_common.sh`, and `bench02_draw.py readout`: argument order is mode, census attempt directory, output directory, candidates. Attempt symlinks `decisions.jsonl -> current/decisions.jsonl` and `evaluation_diagnostics.jsonl -> current/evaluation_diagnostics.jsonl` both resolve to readable files under `generations/g1-6283e1bcdf124516b599f8028ad910be/`, matching the extract input paths recorded in the receipt. Time limit: `01:00:00`. Expected outputs: `census05_readout/candidates_readout.jsonl` and `census05_readout/readout-%j.log`. Submit line changes: 0. Command prepared only; no jobs submitted.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
cd $W/filter_pipeline_20261018/bench02_pkg/0019ce4b && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh readout "$W/census_05_20261020/attempts/full-split-001" "$W/filter_pipeline_20261018/bench02/census05_readout" "$W/filter_pipeline_20261018/bench02/census05_draw/candidates.jsonl"
```
