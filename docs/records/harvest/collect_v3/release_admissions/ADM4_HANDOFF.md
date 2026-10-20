# ADM4 original-crop admission

Owner decision (17 October 2026 evening, coordinator): “forget the crop correction”. Crop admission drops only two-or-more-complete-line crops (`screen_merged`) and registered rotated crops. Overruns and other crop defects are acceptable. No CAPS3 edge screen, masking, output-kind restriction, previous-card pool restriction, codec rescreen or other crop screen is applied. The explicit stratum allowlist and registered line-level classes remain enforced.

`w1_originals_v3.jsonl`: **30,114 rows**, from 33,301 eligible W1 feature rows. Each row copies the post-convention W1 label, original crop_bbox and crop_sha256. `arm=release-v3`, `crop=original`. Kosmopolis poly1850 and all headings_caps marks are `pending_opus`; other admitted strata are `recorded`. Evidence commits are attached per row.

Disjoint first-hit removals: merged **2,740**, rotated **100**, registered classes **347**. Thus 33,301 − 2,740 − 100 − 347 = 30,114. Overlapping hits are merged 2,740, rotated 748, classes 348. Exactly 648 rotated hits were already merged; one class hit was already removed. The summary reports raw and disjoint counts, IDs and source × class breakdowns. All registered classes are read strictly; missing files fail. The 11 `lqb_truth_v1_wave1d_in_sample_ids` remain admitted.

| Source | Class | Gazette stratum | Rows |
|---|---|---|---:|
| bsb_poly1850 | poly1850 | — | 3,781 |
| ia_poly1850 | poly1850 | — | 1,944 |
| nlg | poly1850 | — | 767 |
| nlg | poly1900 | — | 428 |
| nlg | greek_poly | — | 196 |
| serbia | cyrillic | — | 1,226 |
| elstat | numerics_tables | — | 2,519 |
| gazette_modern | modern_scanned | measured_1986_1990 | 7,406 |
| kosmopolis | poly1900 | — | 2,148 |
| lekythos | poly1900 | — | 7,028 |
| kosmopolis | poly1850 | — | 473 |
| bsb_poly1850 | headings_caps | — | 46 |
| elstat | headings_caps | — | 1 |
| gazette_modern | headings_caps | measured_1986_1990 | 1,548 |
| gazette_modern | headings_caps | probe_1982_1985 | 234 |
| ia_greek_latin | headings_caps | — | 6 |
| ia_poly1850 | headings_caps | — | 61 |
| kosmopolis | headings_caps | — | 63 |
| lekythos | headings_caps | — | 206 |
| nlg | headings_caps | — | 33 |

The probe is excluded for modern_scanned; headings_caps qualifies across sources via CAPS4, including probe headings. No Latin primary class or pending/failed/unchecked class outside the explicit allowlist is admitted.

SHA256: `d12a7b5a895b43b515e21be1d8bc53d82ac836270f12f7a94b5762418accf5f8`.

The historical masked JSONL is byte-identical to HEAD and SHA256 `d9343b74c4eeb61b592257f25f63f9b624e7a83d3ddcb3971d8951998253d064`. Only its summary receives the owner rule and superseding file name.

Both ledgers now count W1 originals directly, keep masked rows as measurement history, and explain why original crop_ok rates of 53–82% are not admission blockers. Original collected-by-source/status values, unions, proxy gaps and costs remain under `adm4_history` in JSON; the Markdown history table retains old unions and gaps. Derived planning gaps and cost arithmetic use updated W1 counts and the existing historical W2 receipt/yields; live W2 is not read or credited. This does not certify final deduplication, codec, spread or release assurance.

Validation (metadata only; no image or label adjudication):

```sh
python3 -B docs/records/harvest/collect_v3/release_admissions/build_w1_originals_v3.py --check-only
python3 -B -m unittest discover -s docs/records/harvest/collect_v3/release_admissions -p test_adm4_originals_v3.py -v
python3 -B docs/records/harvest/collect_v3/release_admissions/guard_adm4_commit.py --check-only
```

The guarded list and manifest bind exact outputs, scripts, tests, HEAD/branch and W1/registry inputs. The pre-existing ledger JSON is ignored by Git and absent from HEAD; history is checked against the tracked pre-ADM4 Markdown table. Any future staging must explicitly include only the listed files (force-add only ignored exact paths when needed), then verify the staged path set. No staging or commit performed. Existing unrelated edits are outside the list. Never rerun the historical ledger builder to overwrite ADM4; use the ADM4 updater.

All writes are under docs/records/harvest/collect_v3/release_admissions or the two requested ledger paths. Collector code, live collect_v3/, run root, crops and registered exclusions are untouched. No network, OCR, spend or crop reading.
