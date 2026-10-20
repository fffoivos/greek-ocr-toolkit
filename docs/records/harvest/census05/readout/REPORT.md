# CENSUS05-R readout receipt

READY. The stdlib readout streams published exports without importing the pipeline. Five real mock outputs match their summaries exactly. The final suite passes 15 tests; no reader, census, network request, Git command or Slurm command ran.

## Files and usage

- `census_readout.py`: the requested CLI; writes only `readout.json` and `READOUT.md` in its output directory. Exit 0 means complete and all invariants PASS; exit 1 preserves the report with failed checks; malformed publication/binding/hash errors stop before report output.
- `test_census_readout.py`: five mock comparisons, synthetic faults, publication pinning, old syntax/Mac Python, spool wrapper, streaming, historical evidence and crop protection.
- `readout.sbatch`: normal, 1 node, 1 task, 16 CPUs, 00:30:00; requires absolute `CENSUS05_BUNDLE` pointing to this directory. `CENSUS05_RUN` and `CENSUS05_READOUT_OUT` select inputs/output. Optional `CENSUS05_PYTHON`, `CENSUS05_BASELINE`, `CENSUS05_EXPECT_ROWS` are supported.
- `example/READOUT.md`, `example/readout.json`, `example_cli.log`: mode-i-removed readout run with `/usr/bin/python3`.
- `tests.log`, `streaming_receipt.json`, `mac_python_receipt.json`, `spool_receipt.json`, `baseline_search.json`, `receipt.json`, `REPORT.md`, `SHA256SUMS`: validation, provenance and scope receipts.

```bash
python3 census_readout.py --run /absolute/attempt --out /absolute/readout --expect-rows 592466
# Add --baseline /absolute/census_03/summary.json only when an executed summary is available.
```

`CURRENT.json` pins the generation by export_id; root compatibility symlinks are ignored. Summary/output SHA256 and canonical run binding are verified. Every selected-generation file gets path, byte size and SHA256. The root CURRENT descriptor and `ledger.sqlite` supply control/binding/inventory provenance; they are also hashed. The tool manifest named by the binding is read only if present and its bound SHA256 matches; otherwise the report explicitly marks it unavailable and shows serialized toolchain versions. No other generation supplies counts.

The ledger is opened with `mode=ro&immutable=1`; a nonempty WAL is rejected. Run this on a finished, quiescent checkpointed attempt. Only registered observations and binding are read from SQLite, never its decision payloads. JSONL payloads are read one at a time. Compact SQLite identity indexes remain in memory; their size grows with unique row identities, not JSONL evidence size. Output within the run directory is refused.

All verdict and reason counts use the written records. `unexpected_script` is the code name for the foreign-script reason. Gate exclusions require the serialized content_gate.excluded marker. Role comes from the same observations.role field as summary.by_stratum, with script retained separately. Stage attribution uses written stages, then the corresponding finish() call site; unavailable producers are labeled. `all_reasons` counts each carried reason once per row across stages/routes/disposition; `all_disposition_reasons` isolates final reasons. Segmentation tables retain exact reason strings, including length bands, without inventing categories.

Training leak checks use the writer’s protected crop list (registered dev/test crops) and held-out editions (policy plus all registered non-train editions). They inspect both train ADMIT decisions and admitted_train exports, counting a leaked identity once. Evaluation ADMIT dev/test decisions remain evaluation passes. Export membership also checks crop identity.

## Verification

Command:

```bash
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 ~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=docs/records/harvest/census05/readout/test-work-final-validation docs/records/harvest/census05/readout/test_census_readout.py
```

Verbatim test output:

```text
...............                                                          [100%]
15 passed in 13.41s
```

`bash -n readout.sbatch` passed. `/usr/bin/python3` is **3.9.6**, not 3.6. It executed the CLI on a synthetic valid run and the real mode-i-removed example. `ast.parse(..., feature_version=(3, 6))` passed. Python 3.6 runtime execution was unavailable; no claim of a live 3.6 run is made.

The spool test copied only readout.sbatch to a separate spool directory, executed it from an unrelated cwd and doubled only srun. One srun invocation executed the real readout CLI. Its argv uses the absolute bundle script path. Like seg_census/jobs/common.sh, the wrapper inherits the allocation’s uenv and uses srun with account a0140, partition and cpu-bind=none; it does not start a separate uenv. No sbatch was invoked.

| Mock attempt | Rows | ADMIT | HOLD | DROP | admitted_train | Match summary | Readout seconds |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| mode-i | 200 | 73 | 87 | 40 | 63 | PASS | 0.0464 |
| mode-i-removed | 200 | 73 | 87 | 40 | 63 | PASS | 0.0416 |
| mode-ii | 200 | 133 | 14 | 53 | 116 | PASS | 0.0541 |
| smoke-mode-i | 144 | 65 | 56 | 23 | 55 | PASS | 0.0317 |
| smoke-mode-ii | 144 | 103 | 10 | 31 | 89 | PASS | 0.0399 |

Each comparison checks input rows, dispositions, exact by_stratum, overlapping reason occurrences, route status counts and segmentation availability, plus unchanged input hashes and the two-file output contract.

| Synthetic check | Count | Expected result |
| --- | ---: | --- |
| admitted_train_violations | 1 | FAIL |
| bound_inventory_counts | 0 | PASS |
| dispositions_sum | 0 | PASS |
| duplicates | 1 | FAIL |
| expect_rows | 1 | FAIL |
| gate_route_violations | 2 | FAIL |
| gate_segmentation_violations | 2 | FAIL |
| heldout_leaks | 1 | FAIL |
| missing_rows | 1 | FAIL |
| no_reason | 0 | PASS |
| pipeline_version_mismatch | 0 | PASS |
| summary_by_stratum | 1 | FAIL |
| summary_dispositions | 0 | PASS |
| unexpected_rows | 0 | PASS |

The duplicate is an extra written occurrence of the malformed gate row, so both its segmentation and route violation counts are 2. Missing and duplicate identities offset in the row total; identity checks still reject completeness. Every gate reason is covered. A dedup change, correction edit/status, pending HOLD reason, missing reason, pipeline version mismatch, unexpected disposition and a separate crop-only held-out leak are verified. The baseline arithmetic path is tested with a synthetic summary. Local historical validation and conditional counts are tested separately.

600,000-row subprocess readout: **7.681509 seconds**, **78.515625 MB peak RSS**, measured by `resource.getrusage(RUSAGE_SELF)` in the isolated readout process (Darwin bytes converted to MiB). All 14 checks including expect_rows pass; peak is below 1,024 MB. Fixture generation is outside this timing; fixture input/output files were removed after retaining receipts. This is a synthetic streaming measurement, not a full production run or a Slurm timing.

## Example: mode-i-removed

[Full Markdown](example/READOUT.md) and [machine report](example/readout.json) contain the same count tables and file hashes. Headline: **200 rows; ADMIT 73 / HOLD 87 / DROP 40; admitted_train 63; gate exclusions 0; held-out leaks 0; 14/14 invariants PASS**. Complete: yes; V3 train/dev/test/unassigned = 0/0/0/112; all four pending queues are empty.

Gate total zero describes this older mock’s written stages. Segmentation ran for all 200 rows; later reasons include mixed_script_word, short_line and numeric_shape. They are not relabeled as early gate exclusions.

```text
CENSUS READOUT: rows 200 (complete yes); ADMIT 73 HOLD 87 DROP 40; admitted_train 63; gate DROP 0 HOLD 0 (mixed 0 foreign 0 short 0 cell1 0 num1 0 unresolved 0); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/14 PASS
```

## census_03 baseline search

**Executed census_03 summary absent locally.** The offline path search inspected 103443 paths across the requested Clariden evidence, remote_evidence, sol-recut and main-next trees. The five census03-named paths are configuration/job/snapshot files; there is no executed census_03 summary or complete executed parent × disposition table. Full search roots and candidates are in baseline_search.json. No production baseline was fabricated.

`HANDOFF_SEGCENSUS1.md` records 65,900 admissions. The older `remote_evidence/HANDOFF.md` contains equivalent **conditional predictions**, not an executed baseline: collection-v2-train ADMIT 65,900 / HOLD 145,131 / DROP 3,405 (total 214,436), with diagnostic dev/test ADMIT 3,984 / 10,314. Its text explicitly says no executed census_03 and labels the assumptions. Those figures are retained as historical context only. `remote_evidence/validation.json` verifies the 592,466 registered input rows across five parents; that input binding is not an outcome summary.

## Scope guard and receipt

All created/changed files are confined to `docs/records/harvest/census05/readout/`. No Git operation ran. No source, fixture input, mock output or scheduler state was changed. The tests hash each real mock attempt before and after. Generated test-work directories were removed within the authorized output directory after receipts were captured.

`SHA256SUMS` lists every delivered file with its SHA256 and repository-relative path, including this REPORT and receipt.json. The checksum manifest itself is excluded from its own list to avoid a recursive self-hash. Receipt: [receipt.json](receipt.json).

| Source deliverable | SHA256 |
| --- | --- |
| census_readout.py | `01332f92c636ec823ed08103ef88da283d1b64f2279a0adf2f27893264790939` |
| test_census_readout.py | `de93bfaa96393a26548ab4b554a9ea58125b2f669051fcff681dcf6bb0217587` |
| readout.sbatch | `1f43383bd81d22184e98a5df04dde274667563e9d63dcd4aec985399f13d0100` |

CENSUS05-R READY: script 01332f92; sbatch 1f43383b; mock totals = summary 5/5; synthetic invariants ok; 600k rows 7.682 s peak 78.516 MB; census_03 baseline absent; tests 15 passed 0 failed
