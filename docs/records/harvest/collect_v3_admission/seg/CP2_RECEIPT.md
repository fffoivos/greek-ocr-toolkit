# SEG-CP2b — admission-boundary fix receipt

2026-10-18. Authority: `docs/records/briefs/SEG_CP2b_fix.md`, the complete SEG-CP2 review, CP2 build brief and ASTRA-SEG1 review 1 (numbered plan item 2). Base HEAD: `b921b8284d91f672fc2a2affff57529a664db3af`, branch `sol/recut-v1`. The earlier CP2 receipt's 5/5 claim was invalidated by H1; this receipt replaces it with rerun evidence.

**H1 fixed; CP2 infrastructure acceptance: 5/5 met.** No blocking or medium findings were listed. Publication remains blocked, CP1 GATE_FAIL remains in force, and no CP3+ predicate or qualification has been implemented. No publication, Git staging/commit, recognizer, reader, OSD, network, paid job, ownership tuning, masking, recropping or detector preparation was performed.

| CP2 acceptance | Measured value | Evidence and limits |
|---|---:|---|
| 0 detector calls with recorded geometry | **0** | Native probe and cache/admission test install a raising `process_page` spy. Geometry measurement succeeds; admission remains unresolved. |
| 0 live-run/repository writes during measurement | **0 write attempts** | Native probe rejects write-open and mutation audit events. Cached fixture forbids writes. Source/cache hashes and raster/labels remain unchanged. Authorized code/test/receipt updates and synthetic fixtures under `/tmp` are separate. No live-root lock was taken. |
| 100% identical masks on equivalent frozen inputs | **11/11 = 100%** | 8 native comparisons plus 3 planted comparisons against the unchanged `_foreign_mask` core. Native controls have empty foreign masks; planted counts are 160, 40 and 120 pixels. Equivalence is not semantic word qualification. |
| 0 unavailable checks reported as verified keeps | **0/7** native-probe boundary challenges; **0/3** exact H1 inputs | The regression suite also covers missing/unknown states, forged qualification, stale source/code/geometry/receipt/payload and cross-crop/target/source/page bindings. The twelve-body 6/10-visible reproduction still triggers the historical diagnostic but cannot trigger admission DROP or KEEP. |
| Optional fallback at most once per source-bound page, explicitly counted | **0 preparations; 0/page** | No fallback is invoked. Missing cache/metadata/fields remain unavailable. |

## H1 boundary and accounting

`evaluate()` no longer imports or calls `runs()`. The old component graph is retained only for historical calibration diagnostics; its completeness defect is not repaired or qualified in CP2. The review's three exact otherwise-eligible Greek inputs now yield `passed=False`, `status=unresolved`, `geometry_status=unavailable`, no failed rules and `checks.neighbour_words=n/a`.

`admission_evidence_status()` requires affirmative `status=measured`, `matched=True` and `decision_status=qualified` before considering a caller's binding. For such a claim it revalidates source bytes/path, current full detector/runtime/adapter/vendor/dependency identities, receipt/options/frame and geometry/ink/label payload hashes via the existing read-only loader. It checks the record's source path/SHA, page, crop rectangle and structural target, then reproduces the observation and compares its complete contents. A digest-shaped string or a claimed state is insufficient.

Even a current, fully bound observation carrying a caller-supplied qualification tag remains `unresolved` with `qualification_not_supported_cp2`: CP2 has no authorized qualified decision consumer. Thus every public CP2 evaluation remains ineligible for a verified keep. Later checkpoints must explicitly introduce and review a qualified predicate; no legacy branch is available as a fallback. Text/rule results remain separately reported through `rules_passed` and `failed_rules`.

Receipts retain the total `neighbour_words_unavailable` count for every abstention and add `neighbour_words_status_counts` and `neighbour_words_reason_counts`. Unmatched counts now cover unavailable evidence rather than conflating it with measured but unresolved qualification. A five-row integration fixture containing all three review bypasses, an unqualified CP2 observation and a forged qualified observation records **5 abstentions, 3 unavailable, 2 unresolved, 0 admitted**, with all five reasons accounted for. Public decision-row schema is unchanged. Tool version is `NW1b-20261018.CP2b`.

## Reuse, provenance and scope

The adapter still uses the collector's read-only `ownership.prepare_row/box_hits`, saved curves, structural identities, native component ids and each neighbour's own x-height. Complete code identity, source path/bytes, options and payloads remain bound; `cache_directory` now identifies the exact receipt location for boundary revalidation. The frozen ownership digest is `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. The producer's historical dependency versions remain unavailable; current consumer versions are recorded without inventing producer provenance.

Calibration/C1 cache coverage remains **0/24 pages**. The native probe uses the review's retained W1 excluded-page control `ia_poly1850--3773a91327e98bc0--s000` (8 rows). No W2 witness was used or missing geometry regenerated. An initial probe scanning other live caches failed because a selected payload disappeared before readback. The probe now uses that explicit retained W1 control and passed. This failure was not treated as clean evidence.

The live root is externally active: the read-only inventory observed **31,137 → 31,137 files, 4 added, 4 removed, 0 changed size/mtime/inode tuples among common paths**. This is not a claim of a globally frozen tree. This execution's native audit records zero write attempts, and the selected source/cache hashes stayed unchanged.

All **9/9 CP1 protected-file SHA checks** match `protected_before.json`, including admission outputs, receipts, the census and crops manifest. All **28,798/28,798 manifest-referenced PNG hashes** match, with no missing or mismatched PNGs. No protected admission file, manifest or crop PNG was modified. CP1's regenerated temporary report still reproduces **4/22 owner KEEP losses** and GATE_FAIL; its stale saved-report guard remains effective.

## Validation and review list

**290 tests passed**, including 53 additional cases relative to the review's 237. Final command, using the byte-exact collector interpreter, disabled bytecode/cache and temporary fixture outputs only:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp2b-final-version-tests tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
```

`CP2_pytest.log` preserves the passing output. `CP2_verification.json` is the native probe's stdout, including implementation binding and input hashes. `git diff --check` passed. `CP2_COMMIT_LIST.json` binds the same 14-file CP2 review scope to current bytes and the CP2b brief commit; read-only dependencies include the review and both briefs. `guard_cp2_commit.py` verifies exact scope, base HEAD and all hashes without staging, committing or publishing. Unrelated existing staging drafts and artifacts remain outside the review list.

SEG-CP2b: done | findings fixed: H1 | acceptance: 5/5 met | publish actions: 0 | tests: 290 passed
