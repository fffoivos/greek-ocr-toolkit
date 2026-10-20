# REL4 package handoff

Pre-binding package: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/pkg/22c3e0ba/`. Package identity is SHA256 of the ordered eleven-file core (defined in package_release_v4.py); DEPLOY_SHA256SUMS binds every payload.

Release v4 changes admission membership to census_06 with polytonic in scope. Every exported admission label is the exact immutable import raw_text. The builder asserts both literal equality and SHA256 equality with decision.raw_text_sha256 for each released row; census final_text is validated as selection evidence and never exported as a training label. See INVENTORY.md for the verified REL3 baseline and input pins.

No release has been produced by this preparation. census_06 and sf7 ledger bindings are pending. The package-root corrections_registry.json is a seven-version registration template: four internal census versions plus sf7, ru1_v3_edits and n1_v1_w1. sf7 status is released by the owner ruling; its binding/file SHA and all production touch counts remain null until the coordinator binds and runs the export. All three external versions are registered, not applied to release labels, and reserved for add_corr.

| Overlay | Changed v4 rows | V4 rows with any record | Binding |
| --- | --- | --- | --- |
| sf7 | pending | pending | released, ledger SHAs pending |
| ru1_v3_edits | pending | pending | original sparse artifact pinned; exact collection-v2-train parent |
| n1_v1_w1 | pending | pending | original sparse artifact pinned; exact W1 parent |

The job fills both counters independently. Hold-only records count toward coverage, not changed rows. ru1 cannot touch a W1/W2 row merely because the row ID resembles a collection-v2 ID.

## Exact overlay contract

The actual reader is `~/Projects/greek-page-ocr-e4w2/bench/e4_wave1c.py:37-80`, especially **66-74**. `bench/e4_wave2.py:25` imports it as labels; lines 277 and 556 construct and apply the overlay. `bench/e4_wave2_r3.py:388-400` adapts raw release rows. `tests/test_e4_wave2_r3.py:193-209` exercises the actual v2.1 training loader. The saved source files and SOURCE_CITATIONS.json pin these citations.

The reader accepts field pair row_id/text (also legacy id/label or id/text), requires nonempty provenance on the row or version spec, preserves extra row fields, and requires globally unique row IDs per artifact. Parent is provenance only, not part of its lookup (lines 40-41 and 129-135). REL4 therefore rejects a row ID collision even across different released parents.

`release_v4_sf7_edits.jsonl` uses precisely `row_id`, `text`, `provenance`. Extra audit fields retained by that reader are `parent_id`, `parent_text` (exact raw label), `raw_text_sha256`, `tool_version`, `tool_digest` (the census tool-version SHA). `provenance` contains the complete polytonic route, source ledger SHA, and ledger record path/line/canonical-record SHA. There is no consumer-defined old_text/new_text/tool_version_sha schema; introducing those names instead of text/provenance would not satisfy this reader.

Text is raw_text with only the applied polytonic route's raw Unicode-codepoint edits. No numeric, Cyrillic, composer or other route edit enters this file. Each output is cross-checked against the source ledger's parent, raw binding, version/digest, raw spans or legacy target, successful status and canonical record hash. Split-rebound records retain and verify original_binding/source_record_sha256/source_artifact_sha256 as defined in inputs/line_pipeline_census04.py:124-139. Sparse omissions are never treated as verified no-change.

The driver has heavyweight training imports. The round-trip test extracts its **unchanged registry function** by AST into a namespace providing its original IO helper semantics, runs it with production=True, and reads the generated sf7 file. rel4_contract.py also reproduces its exact per-record parsing statements at reader lines 66-74. No consumer code was modified.

`release_v4_edits.jsonl` retains REL3's edits-only fields for other census edits, independently replayed on raw text. Polytonic tools/routes are removed from this file. Recorded composer normalization is projected onto that non-sf7 stream using its existing NFC/whitespace policy; census_normalization retains the unmodified original normalization record for provenance when the full census stream also contained polytonic changes. Both files are evidence/overlay artifacts, never raw admission labels. The receipt reports edited_rows for other internal edits and sf7_edited_rows separately; REL3's verified baseline was zero. Actual REL4 counts are pending.

## Exclusions, flips and receipt chain

Join census book_id through the pinned SPLIT2 edition map and assert matching edition_id. Dev/test-edition and benchmark-key counts must both be zero or the attempt fails. Benchmark keys and crop SHAs are the union of official seal04 test/dev and REL3's candidates_v3/readout; the candidate/readout sets must still agree exactly. Exact benchmark-pixel duplicates are dropped and counted. Missing manifest matches, wrong hashes/sizes, missing images and nonmatching crop bytes are dropped and counted. At least one backed row must survive.

Historical REL4 rule (superseded by REL4b below): CROPS4 remains bound to its original census_05 generation. Newly admitted rows absent from the actual REL3 release and lacking an exact CROPS4 crop are additionally counted in missing_crop_new_admits, with explicit per-parent zeros. **Any nonzero count requires a CROPS4 top-up before this release is used.** The receipt sets requires_crops4_top_up=true; do not treat a successful export receipt alone as permission to train. Top-up receipts require a separately reviewed package revision; the pinned old receipt SHAs cannot be silently replaced.

release_v4_flips.jsonl lists every actual added/removed release row with parent, source, census_06 decision and reason: polytonic hold, polytonic edit or other. Receipt flips aggregate each direction by parent/source/reason. Removed rows still admitted by census but excluded for crops/pixels are included, with their real census reason, not relabelled as holds. Every removed key must have exactly one census_06 admission record, or the build fails. Missing newly admitted crops are counted before dropping, so cannot disappear from the report.

RELEASE_V4_RECEIPT.json is written last. It binds all release outputs plus CURRENT/summary/admission_records/admitted_train, sibling readout, actual config/tool manifest, REL3 output and REL3 success receipt, by SHA. The generation/config hashes are tied to the completed census run binding; mixed generations and unrelated configs fail closed. Every release decision is reconciled against admission_records. Big inputs and sf7 ledgers are fully hashed before and after streaming in the release job; CROPS4 metadata is rehashed after use. Failed attempts retain FAILED.json and have no success receipt. Existing attempt paths are refused.

The wave-2 admission gate must consume these bound census_06 generation files and the new RELEASE_V4_RECEIPT.json. Its older census_05-only configuration is not automatically rebound by this package. Gate integration is the coordinator's dependent handoff, not a claim that a census_06 release already exists.

## Resources, verification and pending work

REL3's measured synthetic model included both full-file hash passes at 265,026,561 bytes/sec. Census_05's 18,282,843,972 bytes plus the 173,707,408-byte REL3 release imply 18,456,551,380 / 265,026,561 × 20 + 1,200 seconds = about 43.2 minutes. The 1,200-second reserve covers crop reads (300s) and new ledger/flip/receipt work (900s). size_release_v4.py recomputes from the actual bound census_06 sizes, rounds up to 15 minutes with a 60-minute minimum, and refuses an estimate above normal's 12h limit. Memory starts at 8 GiB and grows with 4× selected-parent sf7 JSON expansion plus allocator headroom. The sbatch defaults are 60 minutes/8 GiB; submit supplies the byte-sized values. This is a conservative sizing model, not a production performance measurement.

VERIFY package checks payload hashes, package identity, Python syntax and shell syntax. VERIFY inputs hashes small files below 64 MiB, sizes big files without parsing/hashing them, and validates receipt chains. sf7 light checks ledger sizes only; the binder verifies their hashes below its 64 MiB per-file limit and the batch hashes them again. Exit 2 means pending, other errors are hard failures. The submit wrapper and batch both verify package and inputs before proceeding. No jobs, scheduler probes or allocations are required for package verification.

REL4b pre-binding inputs verification: 31/42 ready; census_06, sf7 and crops4c PENDING.

Pending: nine census_06 generation/config/version pins, sf7 ledger binding and CROPS4C full/smoke custody; all production row, flip, exclusion, edit and touch counts; full output SHAs; zero missing new-admit crops; coordinator export and wave-2 consumption. Tests cover all twelve REL3 cases, real census_05 schema witnesses and synthetic polytonic edit/hold cases, actual consumer parsing, ledger mismatches, raw labels, edit separation, flips, crop gaps, seal04, completed binding and pending submission refusal. See TESTS.log for the final count. DEPLOY_READBACK.json is local post-deployment evidence outside the immutable deployed payload manifest.

Guarded commit list: COMMIT_LIST.json and guard_commit.py. The guard only validates hashes and prints release_v4 paths; it never runs Git. No git add/commit was run. Only release_v4 files were written; existing REL3 and unrelated dirty worktree files were left untouched.

## REL4b — CROPS4C and pipeline 0.3.3

Supersedes the pre-binding REL4 crop/top-up and non-polytonic-drift rules above. The old package `22c3e0ba` is preserved. The new package ID is in sibling PACKAGE_ID; its remote root is `$W/release_v4/pkg/$(cut -c1-8 PACKAGE_ID)`. The package expects final census_06 decisions at pipeline **0.3.3**, including every non-released/held-out decision. Version 0.3.2 is rejected. CENSUS06-A commit cf1db4dd4/package de597753a70a5d6d is pre-binding only; it is never substituted for the final code ID.

`inputs/census06_expected_tool_versions.json` is the byte-exact CENSUS06-A manifest, checked against fingerprints.json and pipeline_033.patch. The eight regenerated digests are expected; polytonic remains de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5. Binding authenticates the actual final code manifest and actual configured tool_versions, requires equality with these expected tool entries, and replaces every internal registry digest, manifest SHA and correction artifact with the census_06 binding. Census_05 manifests remain solely historical baseline/c05 crop-custody evidence.

CROPS4C full and smoke are required pending inputs. The binder pins full SHA256s for the final census manifest/code ID, CROPS4C package manifest, materialiser, reconstruction module, interpreter, codec, both receipts, both manifests/checksum lists, sha256check.log and prepared-check.log. The full receipt must satisfy the complete CROPS4C handoff: ok/full/all/include-heldout, exact W output base, no mismatch/failure/checksum error, byte_exact=selected=written+skipped_valid, train+heldout=selected, all W1/W2 aggregates reconciled, and exact CURRENT/summary/admitted_train/decisions/evaluation_diagnostics hash context. Smoke must be ok/smoke, 500/500 and have the same context except tranche W2. Its output base is its own attempt/smoke. Runtime paths/hashes and final-manifest membership are authenticated at bind time, then retained and rehashed in verification and the job. selection_sha256 and split totals are retained in the v4 input receipt; producer selection authentication remains CROPS4C's own smoke/full gate.

Crop lookup is the union of both historical c05 manifests and the new c06 full manifest. Identical overlaps are accepted; conflicting overlaps, duplicate identities within a manifest, unsafe/wrong identity paths, checksum disagreement or aggregate disagreement fail. Every released crop is still independently hashed from W by REL4. `missing_crop_new_admits` and per-parent counts remain; any nonzero count aborts with FAILED.json and no ok receipt. No successful release may require a crop top-up.

Released polytonic applied, verified_no_change and kept_unverified counts are recorded per parent, per class and jointly per parent/class in RELEASE_V4_RECEIPT.json. Class uses the exported observation's primary_class/content_role. Every exported label equals exact raw_text, with a dedicated kept_unverified assertion and tests including a simultaneous numeric edit. kept_unverified requires its evidence flag and nonempty reason and cannot contain edits. The sf7 overlay contains only applied routes with nonempty edits; verified_no_change, kept_unverified and unresolved routes are excluded. Admission labels remain raw independently of overlay text.

Full local qualification: **92 passed** in tests.log/tests.xml. Every previous REL4 test remains, with former successful new-admit-gap expectations changed to require failure. Added individual receipt-check failures, runtime/manifest custody failures, full/smoke mutation, union/new-admit coverage, status/raw-label/overlay tests and pipeline 0.3.2 rejection. This run's `rel4b_pytest_tmp` was deleted after the passing suite; nothing else was deleted. No jobs or scheduler probes were run.

### Exact coordinator block — documentation only

Run only after final sf7 binding, verified census_06 full + sibling readout, and reviewed successful CROPS4C smoke + full. Set CENSUS06_BOUND_ID to the **final** verified code ID. All commands below are coordinator actions, not executed by REL4b.

```bash
set -euo pipefail
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
: "${CENSUS06_BOUND_ID:?final sf7-bound census06 code ID required}"
# PRE is this REL4b deployment, derived from its PACKAGE_ID (not 22c3e0ba).
: "${REL4B_PACKAGE_ID:?full REL4b PACKAGE_ID required}"
PRE="$W/release_v4/pkg/${REL4B_PACKAGE_ID:0:8}"
CONFIG="$W/census_06_20261020/attempts/full-split-002/inputs/config.json"
VERSIONS=$("$W/venv_l1/bin/python" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["versions"])' "$CONFIG")
ROOT=$("$W/venv_l1/bin/python" -B "$PRE/bind_release_v4.py" \
  --census-config "$CONFIG" --tool-versions "$VERSIONS" \
  --census-manifest "$W/census_06_20261020/code/$CENSUS06_BOUND_ID/DEPLOY_SHA256SUMS" \
  --readout "$W/census_06_20261020/attempts/full-split-002.readout/readout.json")
bash "$ROOT/VERIFY.sh" package
bash "$ROOT/VERIFY.sh" inputs
"$W/venv_l1/bin/python" -B "$ROOT/size_release_v4.py" --config "$ROOT/INPUTS.json"
bash "$ROOT/submit_release_v4.sh" rel4_c06_full_01
```

The binder uses the configured CROPS4C attempts `crops4_c06_full_01` and `crops4_c06_smoke_01`, refuses incomplete inputs, and writes a new content-addressed bound package. The final command submits the REL4 job only after both verification modes pass. No existing package or attempt is overwritten.

### Wave-2 / S1 lead argument handoff

Production SHAs are **PENDING**, not the package/template SHAs. After the REL4 job succeeds, supply these exact path/SHA pairs to the downstream admission gate and correction loader:

| Argument | Exact path | SHA source |
| --- | --- | --- |
| release v4 admission | `$W/release_v4/rel4_c06_full_01/release_v4_admission.jsonl` | v4 receipt outputs.release_v4_admission.jsonl.sha256 |
| corrections registry | `$W/release_v4/rel4_c06_full_01/corrections_registry.json` | v4 receipt outputs.corrections_registry.json.sha256 |
| sf7 applied overlay | `$W/release_v4/rel4_c06_full_01/release_v4_sf7_edits.jsonl` | v4 receipt outputs.release_v4_sf7_edits.jsonl.sha256 |
| census_06 CURRENT | `$W/census_06_20261020/attempts/full-split-002/CURRENT.json` | v4 receipt admission_receipt_chain.CURRENT.json.sha256 |
| census_06 summary | immutable generation path from v4 receipt admission_receipt_chain.summary.json.path | same entry sha256 |
| census_06 admission_records | immutable generation path from v4 receipt admission_receipt_chain.admission_records.path | same entry sha256 |
| census_06 admitted_train | immutable generation path from v4 receipt admission_receipt_chain.admitted_train.path | same entry sha256 |
| v4 receipt | `$W/release_v4/rel4_c06_full_01/RELEASE_V4_RECEIPT.json` | independently compute full SHA256 after success |

Use `handoff_release_v4.py --receipt PATH` after success to print machine-readable path/SHA pairs, checking every named file before returning them. It does not change downstream configuration or submit work. The lead must use these new census_06 inputs, rather than census_05 gate arguments. No production paths/SHAs are claimed ready by this pre-binding package.
