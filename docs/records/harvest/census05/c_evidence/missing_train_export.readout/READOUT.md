3 rows; ADMIT 3 / HOLD 0 / DROP 0; admitted_train 0; gate exclusions 0; invariants FAIL (14/15).

Published generation: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test`. Counts use exported dispositions and reasons only. Foreign-script gate reason is `unexpected_script` (the code name). Class is the ledger role, exactly summary.by_stratum.role; script is retained in by_stratum. all_reasons includes distinct reason names/strings from decisions, stages and routes, once per row; all_disposition_reasons contains only final disposition reasons. Held-out protection checks training admissions; dev/test ADMIT rows are evaluation passes. The protected crop list is the writer’s registered dev/test crops; protected editions are policy entries plus registered non-train editions. Root ledger is immutable input provenance, never a verdict source. Only compact identity indexes are retained in memory; JSONL payloads are streamed. Stage attribution uses serialized stages first, then known finish() call sites; missing producers are explicitly labeled. Failure counts in invariants are zero on PASS.

### Totals

Counted from: `decisions.jsonl`.

| disposition | rows |
| --- | --- |
| ADMIT | 3 |

### Disposition reason occurrences

Counted from: `decisions.jsonl`.

(zero rows)

### Route statuses

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| content_repair:not_run_due_to_prior_exclusion | 3 |
| cyrillic:not_run_due_to_prior_exclusion | 3 |
| dashes:not_run_due_to_prior_exclusion | 3 |
| numerics:not_run_due_to_prior_exclusion | 3 |
| polytonic:not_run_due_to_prior_exclusion | 3 |

### Segmentation availability

Counted from: `decisions.jsonl`.

(zero rows)

### Gate totals

Counted from: `decisions.jsonl`.

(zero rows)

### V3 splits

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| dev | 0 |
| test | 0 |
| train | 0 |
| unassigned | 0 |

### Pending totals

Counted from: `pending_<tool>.jsonl`.

| value | rows |
| --- | --- |
| content_repair | 0 |
| cyrillic | 0 |
| numerics | 0 |
| polytonic | 0 |

### Pipeline versions

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| 0.3 | 3 |

### Admission export

Counted from: `admitted_train.jsonl`.

| rows |
| --- |
| 0 |

### Completeness

Counted from: `decisions.jsonl`, ledger binding.

| rows | input_rows | complete |
| --- | --- | --- |
| 3 | 3 | True |

### Invariants

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, `summary.json`, ledger inventory.

| invariant | status | count |
| --- | --- | --- |
| admitted_train_equals_eligible | FAIL | 3 |
| admitted_train_violations | PASS | 0 |
| bound_inventory_counts | PASS | 0 |
| dispositions_sum | PASS | 0 |
| duplicates | PASS | 0 |
| expect_rows | PASS | 0 |
| gate_route_violations | PASS | 0 |
| gate_segmentation_violations | PASS | 0 |
| heldout_leaks | PASS | 0 |
| missing_rows | PASS | 0 |
| no_reason | PASS | 0 |
| pipeline_version_mismatch | PASS | 0 |
| summary_by_stratum | PASS | 0 |
| summary_dispositions | PASS | 0 |
| unexpected_rows | PASS | 0 |

### all_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### by_stratum

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | source | role | script | disposition | rows |
| --- | --- | --- | --- | --- | --- | --- |
| p | train | s | prose | greek | ADMIT | 3 |

### class

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| prose | p | train | ADMIT | 3 |

### class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| prose | p | train | 3 | 3 | 1.0 |

### class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | disposition | rows |
| --- | --- | --- | --- |
| prose | train | ADMIT | 3 |

### class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| prose | train | 3 | 3 | 1.0 |

### deciding_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### decisions_by_parent_split

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | disposition | rows |
| --- | --- | --- | --- |
| p | train | ADMIT | 3 |

### gate_by_class

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_parent

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_source

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### input_rows

Counted from: `ledger.sqlite` binding/observations.

| parent | rows | registered |
| --- | --- | --- |
| p | 3 | 3 |

### input_splits

Counted from: `ledger.sqlite` binding/observations.

| parent | split | rows |
| --- | --- | --- |
| p | train | 3 |

### issue_counts

Counted from: `decisions.jsonl` + ledger inventory.

| issue | parent | rows |
| --- | --- | --- |
| admitted_train_equals_eligible | p | 3 |

### segmentation_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### source

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| s | p | train | ADMIT | 3 |

### source_class

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| s | prose | p | train | ADMIT | 3 |

### source_class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| s | prose | p | train | 3 | 3 | 1.0 |

### source_class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | disposition | rows |
| --- | --- | --- | --- | --- |
| s | prose | train | ADMIT | 3 |

### source_class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| s | prose | train | 3 | 3 | 1.0 |

### source_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| s | p | train | 3 | 3 | 1.0 |

### source_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | disposition | rows |
| --- | --- | --- | --- |
| s | train | ADMIT | 3 |

### source_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| s | train | 3 | 3 | 1.0 |

### toolchain_versions

Counted from: `decisions.jsonl` + ledger inventory.

| tool | version | rows |
| --- | --- | --- |
| segmentation | 0.8 | 3 |

### Timing

Counted from: readout process wall clock.

| elapsed_seconds |
| --- |
| 0.0020020008087158203 |

### Tool version binding

Counted from: `ledger.sqlite` run binding.

| path | sha256 | availability |
| --- | --- | --- |
| None | None | bound manifest unavailable; values seen in decisions below |

### Diagnostics (first 20 in file order)

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, ledger inventory.

| issue | count | first20 |
| --- | --- | --- |
| admitted_train_equals_eligible | 3 | [{"id":"0","kind":"missing","parent":"p"},{"id":"1","kind":"missing","parent":"p"},{"id":"2","kind":"missing","parent":"p"}] |
| admitted_train_violations | 0 | [] |
| duplicates | 0 | [] |
| gate_route_violations | 0 | [] |
| gate_segmentation_violations | 0 | [] |
| heldout_leaks | 0 | [] |
| missing_rows | 0 | [] |
| no_reason | 0 | [] |
| pipeline_version_mismatch | 0 | [] |
| unexpected_rows | 0 | [] |

### File provenance

Counted from: files named below (streamed SHA256).

| path | bytes | sha256 |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/CURRENT.json | 232 | 6a3236ff79a5db7ee60225c29188243e4c7208d2bc5a179a51e32dc362a967d0 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/admission_records.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/admitted_train.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/decisions.jsonl | 1515 | 60f0d597f64211a5be0b89e7e0a58c0d33491448da9015f0f02a75751387f5ee |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/evaluation_diagnostics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/pending_content_repair.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/pending_cyrillic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/pending_numerics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/pending_polytonic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/generations/g1-test/summary.json | 1063 | 6bbf49634c6c0e153e743965704f09d42c57bb3b5c9788c0e91d9a2273fa9451 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/c_evidence/missing_train_export/ledger.sqlite | 20480 | ef7c446532516ba413750b2f9f0b51c92bd6615e790f7e62928b8ede13054b88 |

No baseline supplied; no historical delta inferred. The handoff records 65,900 admissions.

CENSUS READOUT: rows 3 (complete yes); ADMIT 3 HOLD 0 DROP 0; admitted_train 0; gate DROP 0 HOLD 0 (mixed 0 foreign 0 short 0 cell1 0 num1 0 unresolved 0); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/15 PASS
