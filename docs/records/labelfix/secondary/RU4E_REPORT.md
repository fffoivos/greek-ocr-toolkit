# RU4E: test/dev preparation

The requested nine-book scope is empty in the supplied files: **0 test rows, 0 dev rows, 0 candidate positions, 0 candidate lines, 0 contexts ×2, estimated 0 points.** The preparation and fixture-tested workflow are ready, but there are no production readings to launch. This does not correct or qualify Wave 1c TEST references.

The nine identities are taken unchanged from `artifacts/ru1/ru2t/build.json`, the RU2T-0 manifest. All 44,029 test rows and 13,522 dev rows were inspected as text. Neither exact `(source, doc)` identity nor source-only identity matches any of the nine books. These files contain 3,526 and 411 rows respectively labelled `cyrillic`, from other identities; see [scope diagnostic](../../../../artifacts/ru1/ru4e/scope_diagnostic.json). No other book was substituted. The nine-book shorthand includes volumes whose RU2T metadata describe Bulgarian and Serbian; identities, not inferred language, determine membership.

## Bound inputs and census

| Input | SHA256 |
|---|---|
| `import_real_v2_test.jsonl` | `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` |
| `import_real_v2_dev.jsonl` | `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` |
| RU2T-0 `build.json` | `bbe7e74d165f38a3bec2c6cd4f81727dfbba9a6eddc0facd2b06ba564afd25ae` |

Both inputs are under `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/`. The `label` field in these exact import files is the RAW Google parent string. No convention label version is loaded. Parent version is `google_raw_v2_import`.

| RU2T-0 book identity | Test rows | Dev rows | Test candidate positions | Dev candidate positions |
|---|---:|---:|---:|---:|
| archive_AA9613308335D0B014B:cyrillic:9a32fb66 | 0 | 0 | 0 | 0 |
| archive_b24878935:cyrillic:94847f75 | 0 | 0 | 0 | 0 |
| archive_bub_gb_Cmg6AQAAIAAJ:cyrillic:7235f8d0 | 0 | 0 | 0 | 0 |
| archive_bub_gb_mG0mAQAAIAAJ:cyrillic:0b4bf868 | 0 | 0 | 0 | 0 |
| archive_izvestiianabul25192530bul:cyrillic:252fd568 | 0 | 0 | 0 | 0 |
| archive_izvestiianabulga610193138bulg:cyrillic:ae1a00a3 | 0 | 0 | 0 | 0 |
| archive_izvestiianatsars12192829tsar:cyrillic:b930919b | 0 | 0 | 0 | 0 |
| archive_izvestiianatsars1516194243tsar:cyrillic:4b2c4367 | 0 | 0 | 0 | 0 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930:cyrillic:be2e7fa5 | 0 | 0 | 0 | 0 |

Machine-readable census: [18 split/book records](../../../../artifacts/ru1/ru4e/census_by_split_book.jsonl), [candidate lines](../../../../artifacts/ru1/ru4e/candidate_lines.full.jsonl), [candidate positions](../../../../artifacts/ru1/ru4e/candidate_positions.full.jsonl). The last two files are intentionally empty.

Candidate scope is lowercase Google `ь`, with a preceding Cyrillic letter and no following Cyrillic letter, **`kind == final` only**. ASCII-hyphen `pre_hyphen` positions are excluded under this request's final-position restriction. Google `ъ` is never a candidate. Offsets are zero-based Unicode code points in the exact RAW string; whitespace, punctuation, combining marks, and all other bytes are preserved.

## Packs and budget

External root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru4e/`. Private keys: `artifacts/ru1/ru4e/keys/`. The lexical and resolved ancestor guard rejects every git worktree, including symlink aliases and `.git` worktree files. The root exists and is empty because there are no assignments. [Closure](../../../../artifacts/ru1/ru4e/closure.json) is explicitly `ok`, with zero packs and `empty_scope: true`; this is an empty-scope check, not evidence of glyph coverage.

For a nonempty corrected scope, the builder splits all candidate lines into contexts with at most 90 candidate items plus `ceil(0.1 × candidate items)` adjudicated controls, at most 100 total items. r2 is the exact reverse of r1 with globally fresh opaque IDs. Public folders contain only RU3T `items.jsonl` and SHA-named, byte-copied crops. All word-final soft/hard signs and pre-hyphen signs are masked in public text to avoid supplying Google hints; only final soft-sign slots enter the candidate decision ledger. A closure scan runs on every pack.

The frozen control inventory was verified locally: **31 slot-bearing adjudicated lines, 65 positions**. Zero control placements are needed for this empty scope. For nonempty packs, the seeded control pool uses these adjudicated positions and preserves the disputed-control exclusion and RU1 wrong-sign gate. Control count is rounded per context, so small contexts exceed 10%.

Estimate: `0.2 / 100 × 2 × (candidate line items + control items)`. Actual plan: **0 item reads, 0 points**. Probes and later replacement reads are not included in that glyph-read estimate. No usage probe ran.

## Driver and finaliser

[Driver](../../../../scripts/secondary/run_ru4e_all.sh): `scripts/secondary/run_ru4e_all.sh --dry-run`. Removing `--dry-run` is an explicit later reader launch; no such launch occurred. The driver uses its own SHA-bound helpers in `scripts/secondary/ru4e_bound/`, including its own fixed-output-root copies of `run_read.sh`, `limit_probe.sh`, ledger, prompt, mapper, coverage helper, and scanners. It does not mutate or rebind shared RU2T/RU3T helpers. Before each context it checks closure/bindings, probes the weekly bucket, and stops at **>=70%**. A permanent exclusive attempt claim is written before launch; failed or crashed attempts, existing run evidence, or existing answers are never rerun. It also probes after successful launcher parsing and stops at >=70%. Model is `gpt-6.1-sol`, effort `medium`, with network, web, apps, remote plugins, and multi-agent features disabled in reader configuration.

[Finaliser](../../../../scripts/secondary/ru4e_finalize.sh): `scripts/secondary/ru4e_finalize.sh`. It never launches readers or probes. It checks input/tool/pack hashes; distinct rollout digests; actual model/effort metadata; canonical v4.4 scans (SHA256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`); derived-view ancestry and viewed-item coverage; complete answer mappings; and controls. Unviewed items are dropped before control scoring. VOID contexts supply zero admitted votes. Missing or invalid evidence stays pending and cannot issue an overlay.

A VOID initial read automatically builds a fresh, isolated r3 assignment, preserving the original item population and controls in seeded order. Separate roots under external `ru4e_r3/<context>-<reader>/` allow both initial reads to be VOID without conflating independence. Private assignments live under `artifacts/ru1/ru4e/r3_replacements/`. The lead's launch list is `r3_to_run.jsonl`; the same driver picks it up on a later explicit invocation. Existing replacements are hash- and assignment-checked and never rebuilt or rerun. A VOID r3 remains unresolved for the lead.

After reads, `lead/sheets.html` shows native whole-line PNGs plus 4× nearest-neighbour views, with the exact raw-text offset marked. It invents no glyph boxes and is not opened automatically. The seeded audit selects **20 edit_hard + 10 keep_soft**, or all available with actual counts when fewer exist, plus all genuine binary disagreements. In addition, **every proposed edit** receives a required lead pixel-check entry. The current sheets and template are empty because there are no candidates. The 20/10 sampling path was tested with a synthetic 120-line census.

Later issuance: `scripts/secondary/ru4e_finalize.sh --apply-lead /absolute/path/completed-lead.jsonl`. The completed file must preserve the template's bound row, split, offset, crop path/hash, proposal, and audit/disagreement fields, and provide `call`, `pixel_checked: true`, and a named `reviewer` on every required entry. Each edit requires two admitted independent hard calls plus its explicit lead pixel check. The lead may reject or hold an edit; a disagreement cannot be promoted to an edit without two agreeing reads.

The issuance path writes `artifacts/ru1/ru1_v3_test_edits.jsonl`, rows with at least one edit plus hold rows, with recorded split, exact raw parent, per-edit reader/control/scan/coverage evidence and lead provenance. It verifies that every changed character is precisely a listed `ь→ъ` and restoring those characters recovers the raw UTF-8 bytes. Omitted IDs inherit their exact raw split text. It emits `ru1_v3_test_edits_manifest.json` and `.sha256`, then registers `ru1_v3_test_edits` under `google_raw_v2_import`. The LQB loader now supports explicit `parent_splits` so test/dev inheritance does not silently use the train population; existing train parent paths and overlays retain their original behavior. This path was exercised only on temporary fixtures.

**Current result: `EMPTY_SCOPE`. No real overlay, manifest, SHA, or LQB registration was issued.** Applying a lead file against this empty scope was checked to refuse before issuance, and the actual LQB registry hash stayed unchanged.

## Validation and receipt

**37 focused tests passed:** 24 RU4E synthetic fixtures, 11 canonical scanner regressions, 2 existing LQB loader regressions. Coverage includes all 16 call pairs, final-only census, exact reverse/fresh IDs, <=100-item packing, 20/10 audit sampling, complete sparse-overlay/LQB round trip, raw byte preservation, split recording and inheritance, explicit holds, omitted keep rows, per-edit lead checks, disagreement refusal, VOID/r3 routing for either or both initial readers, missing evidence, wrong model, reused rollout, forbidden reads, derived montage coverage, unviewed-item dropping, input/pack tampering, external-root guards, never-rerun attempts, dry-run isolation, and the exact 70% stop. Shell syntax checks pass. Production dry-run reports zero contexts, reads, and probes.

Logs: [RU4E fixtures](../../../../artifacts/ru1/ru4e/tests_ru4e.txt), [scanner](../../../../artifacts/ru1/ru4e/tests_scanner.txt), [LQB loader](../../../../artifacts/ru1/ru4e/tests_lqb_loader.txt), [dry-run](../../../../artifacts/ru1/ru4e/dry_run.json).

The broader existing LQB check was **not green: 69 passed, 14 failed**. Thirteen failures encountered the installed arm64 SciPy extension under x86_64 Python (and its NumPy version warning); one encountered an older frozen LQB3 receipt's external `release_exclusions.json` hash drift and an out-of-repository `relative_to` failure. Those dependencies and historical artifacts were left unchanged. See [broader check record](../../../../artifacts/ru1/ru4e/broader_lqb_check.json). The focused loader tests and new split-overlay fixture tests pass; the 37-test figure is not a claim that the entire repository suite passes.

Reproduce with the x86_64 Python 3.11 interpreter and `-B`: `-m unittest discover -s tests -p test_ru4e.py`; `-m unittest discover -s scripts/secondary/reading -p test_scan_rollout_v4.py`; and `-m pytest -q -p no:cacheprovider tests/test_lqb.py::test_overlay_and_admission_populations tests/test_lqb3.py::test_supplemental_google_hash_and_conflict_fail_closed`.

[Receipt](../../../../artifacts/ru1/ru4e/RU4E_RECEIPT.json), [build bindings](../../../../artifacts/ru1/ru4e/build.json), [owned helper hashes](../../../../artifacts/ru1/ru4e/helper_bindings.json). Network requests, production glyph reads, usage probes, browser/computer-use, source-file changes, and `.git` writes: **none**. Different files or identities are required to create a nonempty RU4E reading population.

RU4E READY: rows test 0/dev 0 in 9 books; candidates 0 positions in 0 lines; contexts 0 ×2; est 0 pts; closure ok; dry-run ok; tests 37 passed
