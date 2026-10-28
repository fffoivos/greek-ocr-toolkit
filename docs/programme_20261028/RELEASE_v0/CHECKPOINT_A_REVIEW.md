# REL0 Checkpoint A — independent code review

28 October 2026, Europe/Athens. Reviewed commit: `f5300af9b9fe49a870c3e2b4c72fa0fc5ae599d2` (detached worktree).

**HOLD — numerical consolidation and local loader/export checks are sound, but the committed package is incomplete and the public inventory requires corrections before the GitHub push.**

## Scope and inputs

Read the verbatim `OWNER_BRIEF.md`, PLAN rev 2 (especially §§1, 2, 6 and 9), and the Astra plan review, including H07/H08/M01/M02. Checked `REL0_S2_REPORT.md`, `REL0_S2b_REPORT.md`, `CONSOLIDATION.md`, both command handoffs, publication scripts and inventory parts, `VERSIONS.md`, `MODELS.json`, README, relevant tests, provenance records, and sealed Stage C source.

Diffed **every one of the 13 sealed `vendor/train/` files**, all five supporting `vendor/bench/` files, and the codec against the maintained counterparts. Verified package/file and inventory-part hashes with local reads. Also read the original implementation worktree at `~/Projects/greek-ocr-toolkit-main-next/` and the `greek-page-ocr` records explicitly cited by VERSIONS. Those external working-tree records are distinguished below from files present in the reviewed commit.

No network, SSH, scheduler submissions, background watchers, production inference, staging, commits, or Git metadata writes. The only retained new file is this report. The pre-existing untracked review brief was preserved. The prescribed test unexpectedly rewrote one tracked receipt; its original HEAD bytes were restored, as detailed in M4. The pytest basetemp was deleted and its absence verified.

## Findings — severity order

### H1 [HIGH] The committed sealed package cannot pass its own integrity check

**Where:** `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/PAYLOAD.json:111`; `.gitignore:76`; `scripts/release_v0/analyze_models.py:105`; `tests/release_v0/test_analyze_models.py:28`.

**Evidence / failure scenario:** PAYLOAD binds `registry_v2.jsonl.gz`, 644,591 bytes, SHA256 `cbd43afa219970ab52ecd76b8ffa4ecf2a67c0f228f3ebdf3fcf823797f5ccc1`. It is absent and untracked in this detached checkout; the broad `/docs/**/*.gz` ignore applies. Here **92/93** payload members verify, with no mismatches among the present files. The exact requested suite therefore produces ten setup errors at `load_sealed()` before the scorer/selected-checkpoint integration cases execute. A fresh checkout cannot reproduce the reported complete seal. The implementation worktree contains the correct file and verifies **93/93**, so this is an omitted dependency, not evidence that the original seal was altered.

**Fix:** Retain the exact member through a narrow packaging/ignore exception, or provide a genuinely usable, hash-verified archive and explicit materialization step for the sealed package. Preserve PAYLOAD and all sealed bytes. Re-run the exact requested suite from a clean detached checkout; do not remove the integrity assertion or skip these tests to obtain green results.

### H2 [HIGH] The include list admits private audit keys and deblinding material

**Where:** `scripts/release_v0_publish/inventory.py:223`; `scripts/release_v0_publish/PUBLIC_INVENTORY.parts/part-0000.tsv:5736`; `scripts/release_v0_publish/PUBLIC_INVENTORY.parts/part-0002.tsv:6314`.

**Evidence / failure scenario:** The inventory includes `artifacts/sf7_rc1/audit/opus_keys/deck/private/{controls_proposed.json,key.jsonl}` and `docs/records/labelfix/spellcheck/R0_adjudication_private/{items_key.json,ia/items_key.json,...}`. The former key contains 36 records, including four controls, plus original identities and released labels. There are **78 included paths containing `private/`**; this count is a review queue, not a claim that every one is confidential. The R0 deck instructions explicitly keep the private keys and original identifiers away from readers (`docs/records/labelfix/spellcheck/R0_cards/README.md:4`). These are audit answer/deblinding keys, not authentication credentials. The namespace filter only recognizes a few dot-directories and credential filenames. Publishing the include rows without a separate disposition exposes operational audit material that the existing records designate private.

**Fix:** Explicitly exclude these private audit trees and review the remaining private/operational candidates before constructing the public tree. Preserve useful public method/results evidence separately; record any deliberate publication exception by exact path/hash. Rebuild the inventory after disposition. The current location-only credential scan does not resolve this semantic privacy issue.

### H3 [HIGH] Content heuristics remove required source code from the public snapshot

**Where:** `scripts/release_v0_publish/inventory.py:43`, `:209`; `scripts/release_v0_publish/PUBLIC_INVENTORY.parts/part-0002.tsv:9894`, `:9998`; `scripts/release_v0_publish/PUBLIC_INVENTORY.parts/part-0003.tsv:16741`; `scripts/release_v0_publish/PUBLIC_INVENTORY.parts/part-0004.tsv:1192`.

**Evidence / failure scenario:** `google_content()` treats a response field-name literal anywhere in a file as a raw response. Consequently it excludes **the inventory implementation itself**, `tests/train/test_public_inventory.py`, and `greekocr/harvest/montage.py`. Montage contains parsing code, not an embedded raw payload (`montage.py:298`). Included callers such as `tests/test_montage.py` still import that module. The credential-assignment heuristic also excludes `greekocr/readers/services/transkribus.py` for ordinary credential-handling source. A publication built from these decisions omits functioning toolkit components, loses the scanner required by its own handoff, and breaks retained callers. The README correctly calls the inventory a review aid, but there is no resolved public override list in this package.

**Fix:** Distinguish structured raw payloads from parser/scanner source. Review credential-pattern false positives without exposing their values, and bind any benign source/fixture exceptions to exact hashes. Retain actual raw-payload and secret exclusions. Validate imports and the relevant tests against the assembled public tree, not only the larger private checkout.

### M1 [MEDIUM] The documented step-6 parity invocation depends on an unstated import environment

**Where:** `scripts/release_v0_export/COMMANDS.md:47`, `:74`; `scripts/release_v0_export/verify_dev.py:17`.

**Evidence / failure scenario:** The handoff deploys a checkout and explicitly implies no installation, then invokes `python scripts/release_v0_export/verify_dev.py`. A direct script invocation adds its script directory, rather than the checkout root, to the import path. With `PYTHONPATH` unset, the supplied interpreter fails even at `--help`: `ModuleNotFoundError: No module named 'greekocr.train'`. The same interpreter succeeds with `python -B -m scripts.release_v0_export.verify_dev --help` from this root. Pytest masks this dependency by exporting the checkout root in `tests/conftest.py:25`. The sealed worker environment's PYTHONPATH contains only its package/vendor roots.

**Fix:** Specify the reviewed checkout as the working directory and use the module invocation, or explicitly bind installation/PYTHONPATH to that checkout. Verify the entry point in the intended credential-free worker environment before running real parity. The parity computation itself is fp32 CPU as documented.

### M2 [MEDIUM] One version-evidence hash is stale, and working-tree provenance is not portable

**Where:** `VERSIONS.md:33`, `:152`; `MODELS.json:13`, `:189`; `scripts/release_v0_publish/PUBLIC_INVENTORY.receipt.json:3`.

**Evidence / failure scenario:** VERSIONS pins the TRAIN_FULL execution ledger to SHA `2e8997c1...`, but the reviewed file hashes to `2ccf58c4bce6dffbde37fade42b4a7ae4dd5f5903b93ff884e180e8645f41059` and ends before the asserted 28 October completions. The later original-worktree ledger does record those completions and h14 deployment. All other **23** evidence hashes in the VERSIONS table match their cited local sources, including the PAGE sibling records. Thus the working ten-round interpretation is supported, but its named immutable evidence does not fully travel with this commit.

Eight distinct source-record paths referenced by MODELS are also absent here, including the h14 payload/config/PLAN and the attempt013 CLAIM/PLAN paths. **All 15 model record bindings (five per model) match exact bytes and hashes in the original implementation worktree**, as do producing commit/source-state fields and registered source-file identities; both original package seals verify completely (93 and 95 members). No invented value or h13 substitution was found. Inventory tuples also match these bindings, but an inventory row is not the missing file. More broadly, **23,249 inventory paths are absent here**, 23,223 marked include: the TSV describes the larger implementation working tree, not this commit's complete tree.

**Fix:** Retain immutable, accessible source/config/completion evidence and update references to those exact bytes; clearly identify the inventory's materialization root. Carry the h14 sealed package into the reviewed publication payload before claiming H08 complete. Settle the already-disclosed historical generation uncertainties before creating the immutable OCR tag. Do not infer extra generations or silently change a historical digest.

### M3 [MEDIUM] Consolidation includes an explicit behavior change beyond imports/packaging

**Where:** `greekocr/train/mix.py:27`, `:145`, `:259`, `:296`, `:327`; `greekocr/train/CONSOLIDATION.md:3`, `:692`.

**Evidence / failure scenario:** The maintained mix implementation removes historical recovery/replay/overlay/selection branches and rejects their keys before validation/row access. In particular, sealed metadata validation can accept `s1_selection` while the maintained path now immediately rejects it. This is a behavioral/scope change, even though the corresponding historical adapter closure is unavailable and ordinary Stage C numerical behavior is unchanged. REL0-S2b and the detailed mapping disclose the exclusion, but the opening blanket statement that all changes are packaging/import-only remains too broad.

**Fix:** Explicitly distinguish the documented historical-mode exclusion from the import-only consolidation in summary claims and release scope. If strict import-only scope is required, handle the exclusion as a separately identified compatibility change. Do not fabricate missing adapters. No change to released model mathematics, ordinary preprocessing, decoding, or codec bytes was found.

### M4 [MEDIUM] The wheel test overwrites historical evidence outside pytest scratch

**Where:** `tests/train/test_wheel_package.py:73`.

**Evidence / failure scenario:** The prescribed suite writes a newly built wheel receipt directly to tracked `tests/train/REL0_S2b_WHEEL.receipt.json`. This run changed its historical wheel SHA, despite building all temporary sources/venvs under basetemp. Repeated tests can therefore overwrite prior evidence and dirty a read-only review checkout. The test's resource/import checks passed; this finding concerns output isolation and evidence custody.

**Fix:** Write the test receipt under `tmp_path`; promote an implementation receipt through a separate explicit recording step. For this review, restored the original receipt byte-for-byte from HEAD (original receipt-file SHA256 `e1b825c442ef212360487e04089b4bcad75d85a5f6b63c73c5f2731230917a01`) and verified that no tracked changes remained.

## Test result

Executed the exact requested command:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/train tests/deploy tests/release_v0 tests/test_provenance_cli_api.py -q -p no:cacheprovider --basetemp=/private/tmp/rel0-cpa-pytest
```

**1,215 passed, 3 skipped, 10 errors, 0 failed; 15.67 seconds; exit 1.** All ten errors share H1's absent registry member. Three skips are the explicitly historical bench bindings in `tests/test_provenance_cli_api.py:13`. The broader S2b report used a different suite/populated worktree; its historical count is not a passing result for this detached checkout. No rerun with substituted dependencies or weakened checks was performed. `/private/tmp/rel0-cpa-pytest` was removed and verified absent.

Additional lightweight entry-point checks: direct parity-script `--help` fails without PYTHONPATH; module-form `--help` succeeds (M1). No real data was processed.

## GAPS

These are report-only entries for checkpoint triage; no source/docs fixes or issues were made here. Rows reference findings rather than creating additional counted findings.

| What | Where | Impact | Fix / disposition |
|---|---|---|---|
| Sealed dependency omitted from committed package | H1; PAYLOAD / ignored registry | Fresh-checkout seal verification and ten analysis integration tests fail | Restore exact dependency/usable archive and rerun before push. |
| Public inclusion/exclusion dispositions incomplete | H2/H3; inventory and private audit trees | Private audit material can escape while necessary source disappears | Review semantic privacy and benign matches, record hash-bound decisions, validate assembled public tree before push. |
| Historical generation/source evidence is working-tree dependent | M2; VERSIONS / MODELS / inventory | Hash pin and file pointers do not provide a self-contained reproduction record | Retain exact source/completion records, refresh evidence binding, resolve historical count gaps before immutable tags. |
| Historical-mode scope exception conflicts with blanket summary | M3; consolidation opening and mix adapter exclusions | Consumers can mistake a narrowed API for complete import-only equivalence | Qualify the claim; retain explicit unsupported-mode errors and exact diff. |
| Parity launch environment and stored precision need final disposition | M1; export COMMANDS; existing GAPS A6 | Direct CLI can import the wrong checkout/fail; stored GPU AMP hypotheses may differ from fp32 CPU | Fix entry-point handoff; retain original precision custody; run both dev panels/all three widths and investigate any mismatch at step 6. |
| Test evidence output escapes temporary scope | M4; wheel test | Routine validation overwrites a historical receipt | Isolate test output; record promoted evidence separately. |
| Final publication records remain pending | README, MODELS, existing GAPS A7/A8 | Final HF commits/weights/scores/collection links, static inventory, remote receipt custody and public-history checks are not yet certified | Complete at the planned steps; keep nulls/pending labels until readback. No extra owner gate or issue per placeholder is implied. |

## Cleared items and limits

- **Numerical implementation:** All 13 sealed trainer files were compared. Five are byte-identical; seven differ only in import/package routing or diagnostic import text; mix.py has the disclosed scope exception M3. Two supporting bench files are identical and three have import-only changes. The v2.1 codec is byte-identical. No numerical, ordinary preprocessing, decoding, or codec change was found for the released compact widths.
- **Independent equivalence:** `test_equivalence_stage_c.py:23` explicitly loads sealed files under flat module names, while the maintained side imports `greekocr.train`. The models are independently seeded/built at ×1/×1.5/×2 and compared with exact fp32 logits and greedy decoding. This is not the same-module-twice trap; the separate legacy-alias identity test intentionally is. These passing random fixtures do not establish real-weight/dev-population parity.
- **Export/Docling:** Export reads the specified trusted .pt, never a sibling; requires original fp32 floating tensors; clones without casting; and checks every exported tensor on readback. Release loading binds config/codec/weights and enforces exact state keys/dtypes plus strict shapes. Width multipliers, 266 classes, NFD head and NFC serving are enforced. Passing tests exercise actual lazy Docling engine loading at all three widths, tampering and codec reorder rejection. The prepared population gate uses exact PNGs/trainer collation, fp32 CPU without autocast, and NFD comparisons. Its two load_release calls check internal trainer/recognizer consistency; sealed-vs-maintained independence is established by the separate test/source comparison. Final real-weight parity remains unexecuted and correctly qualified, including the AMP caveat.
- **Selection/scoring:** Source inspection confirms trainer best.pt from eight epoch-end seal04_dev evaluations, strict-improvement/first minimum when exact records permit it, SHA-bound best.pt/safetensors/archive agreement, and fail-closed behavior when selected predictions are unavailable. No fallback to a convenient four-point archive or test-selected checkpoint was found. Complete sealed aggregate equality gates analysis. Cross-model bootstrap callers use only harvest_dev, seal04_dev and pooled_dev; test breakdowns are descriptive. The rounded-CSV/exact-diagnostic limitation is explicitly logged. Ten integration cases remain unexecuted because of H1, so this is not full runtime certification.
- **Versions and model identity:** Ten working OCR rounds follow the stated grouping rule; wave1b and corrected-control Task 2 are separately evidenced, O-series smoke/preparation and external-teacher bake-offs are excluded, widths/restarts do not increment n, and uncertain histories are explicitly marked. No additional count was invented to fill those holes. MODELS separates original training_source from null/pending release_code_commit and final artifact fields. Its three entries are 014/h14, 013/h14 and 013/h04; retired 013/×1/h13 is not a released entry. Original-worktree byte verification passes, subject to portability M2.
- **README:** Owner item 8's introduction/link style and pipeline order are present. Modern/monotonic and polytonic Greek, Latin, Cyrillic, mixed text and furniture are prominent. Publication, final pins, collection, scores, three-width completion and real-weight parity are labelled pending. No equal-accuracy, fully human-transcribed dataset, or completed end-to-end Docling claim is made. External link availability was not checked under the offline restriction.
- **Inventory mechanics:** The 5,000,000-byte threshold, receipts_*smoke* matching, named cache exclusions, symlink refusal and index/nonignored candidate union are implemented. All five receipt-listed review-part hashes verify; 74,256 rows comprise 73,382 include / 874 exclude decisions. The bulk manifest lists 679 files / 10,098,666 bytes; remote custody is not proven. Credential diagnostics contain exactly `path` and `line` columns, 122 rows, with a matching receipt hash; scanner stdout also emits locations only. These mechanics do not clear H2/H3 or prove arbitrary secret-format coverage.
- **H07 publication boundary:** The handoff correctly leaves fresh public-parent selection, newly reachable object checks, the final reviewed snapshot and readback to the coordinator. None was performed or certified in this review. No private ancestry should be pushed merely because local tests or an inventory receipt pass.

VERDICT: HOLD | BLOCKERS: 0 | HIGH: 3
