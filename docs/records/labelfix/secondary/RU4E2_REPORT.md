# RU4E2: complete Cyrillic census and offline reading preparation

**3,552 test rows, 411 dev rows, 13 books; 1,753 candidate positions in 1,359 lines.** All 13 books meet the requested mechanical pre_reform rule. Wave-1c scored a subset, so exact equality is **no**. No readers, usage probes, network, browser, computer-use, real .git writes or other-worktree writes were performed.

## Census

Every row in both imports was inspected. Selection is case-insensitive `script_class == cyrillic` OR at least three Unicode Cyrillic letters in the exact import `label`. These exact import labels supply the raw parent; no convention label stream, Unicode normalization or whitespace editing is used. `(source, doc)` is the book identity. There are 3,526 class-Cyrillic test rows plus 26 qualifying Latin-class rows, and 411 class-Cyrillic dev rows. Language is a metadata guess, not pixel evidence.

Orthography is `pre_reform` iff a book has >=5 final ъ or any ѣ/і/ѳ/ѵ (historical counts include uppercase via casefold). Final signs and candidates use the unchanged RU4E positional rule: lowercase sign, preceding Cyrillic letter, no following Cyrillic letter, `kind == final`; ASCII pre-hyphen positions are excluded. No Google ъ is a candidate. Offsets are zero-based Unicode code points in the untouched raw string.

| Book identity | Test | Dev | Language guess | Final ь | Final ъ | ѣ | і | ѳ | ѵ | Candidate lines |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| archive_b29337124:cyrillic:975289f3 | 0 | 219 | srp, ger, lat | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| archive_izvestiianatsars1112193839tsar:cyrillic:363040a9 | 200 | 0 | bul, ger | 46 | 374 | 149 | 9 | 0 | 0 | 41 |
| archive_izvestiianatsars910193637tsar:cyrillic:e2a71638 | 426 | 0 | bul, ger | 34 | 708 | 289 | 22 | 0 | 0 | 31 |
| wikisource_ru:wikisource:155dbad1 | 276 | 0 | ru | 167 | 419 | 162 | 44 | 0 | 0 | 128 |
| wikisource_ru:wikisource:18079f21 | 220 | 0 | ru | 142 | 338 | 154 | 33 | 0 | 0 | 103 |
| wikisource_ru:wikisource:34f692a4 | 238 | 0 | ru | 78 | 274 | 107 | 39 | 0 | 0 | 67 |
| wikisource_ru:wikisource:416065e0 | 261 | 0 | ru | 129 | 469 | 220 | 94 | 0 | 0 | 101 |
| wikisource_ru:wikisource:5a6a4fec | 254 | 0 | ru | 113 | 0 | 0 | 1 | 0 | 0 | 82 |
| wikisource_ru:wikisource:6e98c091 | 604 | 0 | ru | 274 | 933 | 442 | 136 | 0 | 0 | 230 |
| wikisource_ru:wikisource:8163523c | 327 | 0 | ru | 224 | 609 | 279 | 72 | 1 | 0 | 163 |
| wikisource_ru:wikisource:9b953170 | 0 | 192 | ru | 126 | 124 | 87 | 108 | 3 | 0 | 87 |
| wikisource_ru:wikisource:aa1eea4b | 398 | 0 | ru | 189 | 860 | 395 | 287 | 0 | 0 | 150 |
| wikisource_ru:wikisource:b51784e8 | 348 | 0 | ru | 231 | 680 | 301 | 171 | 0 | 0 | 176 |

All entries have mechanical orthography class `pre_reform`. The Serbian dev book qualifies through seven і and has zero final signs. Wikisource 5a6a4fec qualifies through a single і despite zero final ъ; its 113 candidate positions are retained as instructed. Neither case establishes historical Russian spelling. The two Bulgarian archive volumes are retained; do not interpret every candidate as a proposed Russian hard-sign edit.

Exact rows, per-book counts, candidate offsets and candidate lines are in [census_all_rows.jsonl](../../../../artifacts/ru1/ru4e2/census_all_rows.jsonl), [census_by_book.jsonl](../../../../artifacts/ru1/ru4e2/census_by_book.jsonl), [candidate_positions.full.jsonl](../../../../artifacts/ru1/ru4e2/candidate_positions.full.jsonl) and [candidate_lines.full.jsonl](../../../../artifacts/ru1/ru4e2/candidate_lines.full.jsonl). Per-split/book counts are also saved.

## Wave-1c comparison

Production readback root: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c/out/e4/wave1c_readback/remote/out/e4`. Its bound deployment manifest is `wave1c_prep/manifest_fix1.json`, SHA `3facf7e15cf0e3fe6ecb08a10ad13b0f0373f99f2cf579d2bf068bac3b3a6b2b`. Scored populations are established from `wave1c/job01/predictions/ctrl_s0_v2_test.jsonl` and its full-coverage counterpart, then independently compared for all six production arms and both instruments. Each of the 12 prediction files matches its saved `predictions_sha256` receipt. The deployed raw test and dev snapshots are SHA-identical to the census imports.

| Instrument | Cyrillic scored rows / unique IDs per arm | Census test rows | Missing census IDs | IDs outside census |
|---|---:|---:|---:|---:|
| v2_test | 1,742 / 1,742 | 3,552 | 1,810 | 0 |
| v2_test_full_coverage | 3,510 / 3,510 | 3,552 | 42 | 0 |

Both instruments have identical Cyrillic ID sets across all six arms. The full-coverage Cyrillic slice omits all 26 Latin-class census rows and 16 class-Cyrillic rows. No omission cause is inferred merely from the IDs. Neither instrument equals even the 3,526 script-class-only test rows. Dev is preparation scope, not part of these scored TEST instruments. Exact missing IDs, prediction paths/hashes and receipt paths/hashes are in [wave1c_comparison.json](../../../../artifacts/ru1/ru4e2/wave1c_comparison.json); receipt-hash verification is in [wave1c_receipt_validation.json](../../../../artifacts/ru1/ru4e2/wave1c_receipt_validation.json). This is an ID-population comparison, not a claim that encoded scoring strings are byte-identical to raw imports.

## Packs, driver and finaliser

Active pack root: `/private/tmp/ru4e2/sol_packs/ru4e`. This preserves the RU4E external-worktree closure guard while using the requested `sol_packs/ru4e/` suffix. Private keys and current evidence are under `artifacts/ru1/ru4e2/`; the original empty-scope RU4E artifacts are preserved. There are 16 contexts ×2, 1,359 candidate line items + 144 control line placements per round, 3,006 total reads, estimated **6.012 points** at 0.2 points / 100 reads. Probe and replacement-read costs are excluded. Controls come from the same 31 adjudicated lines / 65 positions. Each context contains 93 or 94 items, <=100; r2 reverses r1 exactly with fresh IDs. Closure passes on all 32 packs.

Public copies contain the same native decoded mode, dimensions and pixel bytes as the original crops. PNG metadata is removed because the existing closure scanner rejects it. Each private candidate item retains original path/SHA, native pixel SHA/mode/size and the sanitized PNG SHA. Original files are unchanged. The initial metadata-bearing build was rejected before any reading; its log/keys and `/private/tmp/ru4e2/failed_metadata_packs/` are retained separately and are not driver inputs.

The shared RU4E builder gained explicit selected-ID and crop-preparation hooks; its nine-book default and all read/adjudication gates remain in place. RU4E2 imports its own SHA-bound helper copies from `scripts/secondary/ru4e2_bound/`, with both launcher and probe output roots rebound to RU4E2. Model remains gpt-6.1-sol / medium, network and external reader tools disabled. The driver probes before contexts, stops at >=70%, claims attempts exclusively and never reruns them.

Later explicit launch: `scripts/secondary/run_ru4e2_all.sh`. The completed preparation used only `scripts/secondary/run_ru4e2_all.sh --dry-run`, reporting 32 planned contexts and zero probes/reads. Offline finalisation is `scripts/secondary/ru4e2_finalize.sh`, currently **PENDING_READS**, with all 1,753 positions held. It retains canonical v4.4 scans, independent rollout/model/effort/coverage/control gates, VOID-to-r3 routing, audit 20 edit_hard + 10 keep_soft plus disagreements, and mandatory lead checks on every edit. The current empty lead template is not an adjudication result.

After readings and completed pixel checks, `scripts/secondary/ru4e2_finalize.sh --apply-lead /absolute/completed-lead.jsonl` uses the unchanged sparse-output protocol: `artifacts/ru1/ru1_v3_test_edits.jsonl`, manifest + SHA and LQB `ru1_v3_test_edits`, parent `google_raw_v2_import`, recorded split, holds and omitted-ID inheritance. Every applied edit must have two admitted independent hard calls and the lead pixel check; raw bytes may change only at the listed ь→ъ offsets. **No production edit file, manifest or LQB registration was issued.**

## The 14 LQB failures

The original command reproduces **69 passed, 14 failed** under x86_64 Python 3.11 / NumPy 1.24.3. A read-only use of the existing compatible arm64 environment at `~/Projects/greek-ocr-toolkit/.venv/bin/python` gives **82 passed, 1 failed** for the same 83 tests. No packages or environments were changed. No genuine regression in this worktree's LQB code was found, so **0 fixed, 14 other**, and LQB code/tests/historical receipts were left untouched.

| Test | Cause | Compatible environment |
|---|---|---|
| `test_in_sample_separation` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_tier_c_never_in_headline` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_regression_only_separate` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_union_marks_known_and_inserted_unknown` | x86_64 Python/NumPy cannot load arm64 SciPy ndimage, reached through the existing union scorer and labelfix/ink.py. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_mark_heads_reported_separately` | x86_64 Python/NumPy cannot load arm64 SciPy ndimage, reached through the existing union scorer and labelfix/ink.py. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_selected_samples_never_population_rates[enriched]` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_selected_samples_never_population_rates[decision_audit]` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_mixed_samples_split_and_suppress_population` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_locked_selected_scope_not_population` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_population_types_allow_rates[uniform]` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_population_types_allow_rates[locked_stratum]` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_lqb2_real_training_split_and_label_parity` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_lqb2_run_autoloads_flags_and_inherits_training` | x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure. | passes |
| `test_v2_source_hashes_and_outputs` | Historical LQB3 receipt expects external release_exclusions.json SHA e9f975908d; current SHA is 573c8f3fec. The test calls relative_to(ROOT) on that changed external path and raises ValueError. Historical custody is unproven; no LQB runtime regression. | fails |

The last failure must not be made green by updating historical expected hashes or relaxing custody. The four changed local sources are already allowed as superseded by that historical test; the external release-exclusions hash is the additional drift. Exact expected/current hashes are retained in [historical_input_drift.json](../../../../artifacts/ru1/ru4e2/historical_input_drift.json). Full failure traces: [x86](../../../../artifacts/ru1/ru4e2/lqb_x86_initial.txt), [compatible arm64](../../../../artifacts/ru1/ru4e2/lqb_native_initial.txt). All 14 classified records: [lqb_failure_census.json](../../../../artifacts/ru1/ru4e2/lqb_failure_census.json).

## Verification

**29 RU4E/RU4E2 tests passed**, including all 24 original fixtures, selection by OR rule, threshold/isolated-letter behavior, exact raw offsets, no whole-book scope expansion, metadata stripping with pixel identity, sampled-wave inequality, non-nine scope packing and dry-run isolation. **11 canonical scanner tests passed**. Driver dry-run, offline pending finalisation and shell syntax checks passed. These focused passes do not make the historical LQB suite green.

Commands used x86_64 Python 3.11 with `-B`, `pytest -q -p no:cacheprovider tests/test_ru4e.py tests/test_ru4e2.py`, scanner unittest discovery, and the two documented LQB interpreters with `tests/test_lqb.py tests/test_lqb3.py`. Preparation tests use synthetic fixtures; no real glyph reading was performed.

RU4E2 READY: cyrillic rows test 3552/dev 411 in 13 books (pre_reform 13); candidates 1753 positions in 1359 lines; matches wave1c slice no; contexts 16 ×2; est 6.012 pts; LQB failures 14 (fixed 0, other 14)
