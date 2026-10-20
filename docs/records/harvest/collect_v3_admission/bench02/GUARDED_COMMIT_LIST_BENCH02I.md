# BENCH02I guarded commit list

Exact review-only allowlist. No staging, commit, push, network access or paid operation performed. Preserve unrelated tracked/untracked work, BENCH02G dryrun/, the legacy tags receipt, and the historical BENCH02H sweep. Do not stage a directory or use git add . / git add -A.

Every listed artifact was checked as a regular file inside this checkout, not a symlink, below 5,000,000 bytes. Recheck sizes and hashes immediately before staging. Compare staged names against this list and run git diff --cached --check. Include this guarded list itself; its self-hash is intentionally omitted.

| Repository-relative path | Bytes | SHA-256 |
|---|---:|---|
| docs/briefs/BENCH02I_ruled_cap_and_pool.md | 4011 | d887e91cef1b5e13a49a8ad07772cf6df904fdc8eba8a541be97635b87f0f66d |
| docs/harvest/collect_v3_admission/bench02/bench02_draw.py | 39070 | 7cb76e3a16e2a00a588b71c872fd59f00739e65fa56fca1b132a241910b50582 |
| docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh | 1034 | a61205ca16a2ae15bc73c8367ea8a12a6e69e94b2986da5971d99a076a17775a |
| docs/harvest/collect_v3_admission/bench02/run_ruled_draw.py | 8822 | 5cb9d4bff28c50c8a360e071cfa915d837899be6a5aad12ad20c94c4e0a55de9 |
| docs/harvest/collect_v3_admission/bench02/test_bench02_draw.py | 10911 | 4546cb0ec248975d8f2a85872a4562e5ec01c8a576a22fe61c59c938304e947e |
| docs/harvest/collect_v3_admission/bench02/test_bench02h.py | 6619 | 9acb2faf489fb42eaf23ac222a2b0fd70eb783f011d187f1420836a79671db27 |
| docs/harvest/collect_v3_admission/bench02/test_bench02i.py | 6165 | 74e49e1150c4825b6c879eda2344349f00ff2e51ad912349f35087ace7257a96 |
| docs/harvest/collect_v3_admission/bench02/census03/DRYRUN_V2.md | 6158 | 864e411a587160dc005a09b2217fcfebd056f830866e3ae853524e7b157de58e |
| docs/harvest/collect_v3_admission/bench02/sweep/CAP_CHOICE.md | 9421 | 67921e5ccfed1cd1f8d4dee1baff6589a35bdb040d2d04dbfede0b342767a2a7 |
| docs/harvest/collect_v3_admission/bench02/sweep/cap_choice.json | 108445 | 0318e0bdb64bf3a27d915efaa841e959ed7de95e2ea2008cbdcbda7acee4b0e2 |
| docs/harvest/collect_v3_admission/bench02/sweep/ruled_run.log | 3180 | cf75c03664a90aa40d6e1d511ad9f003a3bafb32e6cf1b1f593690128ec4372e |
| docs/harvest/collect_v3_admission/bench02/sweep/ruled_tests.log | 5603 | 110d5c67051c4fdeaf76e0afe9506ce8cfc710c9a916962c6b7287159469beee |
| docs/harvest/collect_v3_admission/bench02/census03/dryrun_v2/candidates.jsonl | 2474958 | 1faa0fa5cfc6ad88a6cb86ce24912ae401310347e39080ce0296380b449c0f39 |
| docs/harvest/collect_v3_admission/bench02/census03/dryrun_v2/counts.json | 1178992 | 10f88ad1a7f47a19b53c8aaca863aa225e16c0eff296dbb788785a1866c7ca89 |
| docs/harvest/collect_v3_admission/bench02/census03/dryrun_v2/COUNTS.md | 3388 | 16c412086de2ab02f953622c8e1bdebf640c789235dbe8d670ca8df4aecdd57b |
| docs/harvest/collect_v3_admission/bench02/census03/dryrun_v2/draw_plan.json | 8077 | 92fa710cc376e0d0b3d08b5f6530a16585581b129cdfb7a1b401a791301ad4d9 |
| docs/harvest/collect_v3_admission/bench02/sweep/upper_bound_ruled/candidates.jsonl | 3569105 | 438508e486494fe0114ac8b545981bee553ad67709a79a4e96eaeadfe10e2934 |
| docs/harvest/collect_v3_admission/bench02/sweep/upper_bound_ruled/counts.json | 1471530 | 504fdfaacaeced4b0007cbf0465dadf840e9059766fd52d450c74044c05bac57 |
| docs/harvest/collect_v3_admission/bench02/sweep/upper_bound_ruled/COUNTS.md | 3413 | f93d2978cca1fc40072d2a47671eaea21f4fd5ae4877768198a62543edd6eaea |
| docs/harvest/collect_v3_admission/bench02/sweep/upper_bound_ruled/draw_plan.json | 8069 | 5b7d60374666b2b161e1cc51ed2ad418255038b094c384ded15e10288ebce14c |

Also include `docs/harvest/collect_v3_admission/bench02/GUARDED_COMMIT_LIST_BENCH02I.md`.

Out of git: census03/tags.jsonl.gz (32,741,890 bytes), SHA-256 9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b. Existing unrelated working-tree paths stay out of scope.

## Verification

47 tests passed under run_tests.py; filesystem audit reports zero writes outside bench02. The CLI subprocess, fresh-cache dry replay, locked-row exclusion tests, end-to-end three-class fairness/cap test, match/mismatch/legacy receipt checks, wrapper requirement and 12/25/50 cap-choice checks pass. git diff --check passes. Classifier, text facets, density logic, subgroup quotas, exclusions and diagnostic_locks ASTs match BENCH02H. Original dryrun/ and tags receipt have no diff.

## Existing tests updated (four)

- DrawTests.test_caps_global_across_classes renamed test_caps_per_class_across_classes: global counters are replaced by class-scoped counters; expected maximum now follows the ruled default.
- DrawTests.test_caps_with_single_edition: expected count changes from 4 to min(40, default cap), because the production default is 50.
- Bench02HTests.test_default_cli_reproduces_bench02g_bytes renamed test_default_cli_reproduces_ruled_v2_bytes: no cap/pool flags must reproduce v2 with cap 50 and pool both; the pinned legacy tags checksum is supplied.
- Bench02HTests.test_global_caps_every_sweep_value renamed test_per_class_caps_every_sweep_value: two classes independently receive up to six cap units from the two series, hence 12×cap total instead of the old shared 6×cap. Unlimited remains unchanged.

All other existing tests retain their expectations. The BENCH02H sweep and its regression test remain historical evidence of that base commit; reproduce its old 48-run sweep at a0b62ef75, rather than overwriting it with the ruled semantics.

## Reproduce offline

From the repository root:

```sh
python3 -B docs/harvest/collect_v3_admission/bench02/run_ruled_draw.py > docs/harvest/collect_v3_admission/bench02/sweep/ruled_run.log 2>&1
python3 -B docs/harvest/collect_v3_admission/bench02/run_tests.py > docs/harvest/collect_v3_admission/bench02/sweep/ruled_tests.log 2>&1
```

Cap choice is fallback 50: no tested cap satisfies all supplied classes. Source→edition round-robin chooses independently within each class; class-scoped caps make these selections independent, so fair edition-local interleaving changes no selected row. Class rank preserves the source→edition selection sequence; candidates are emitted one row per class/edition/pass in precedence order, as specified exactly in draw_plan.json.

Dry forced-pool addition: 19,514 non-locked rows across 99 editions (LQB 14,293, N1 5,221); all-rows upper-bound addition: 51,552 (LQB 42,632, N1 8,920). Credit is quota-clipped, classes filled use aggregate credit, and subgroup deficits remain separate. Historical Russian test supply is restored by the ruled pool (345 dry rows), so it now credits 120/120; no compensating filter or quota transfer was introduced. Series-cap compliance remains unverifiable without identity.
