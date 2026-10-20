# RU1-0 census and pack preparation

**BLOCKED: no reader packs are ready.** All 1,146 W1 crop regenerations failed the required crop SHA256 check; the retained source-raster hashes passed. No replacement crops were used. No reader or limit probe ran, no image was viewed, no network was used, and no collector or .git writes were made.

The 1,146 usable-row rule is reproduced exactly: cyrillic 949, numerics_tables 156, latin 40, nonletter 1. source == ia_russian; candidate_usable is true (fixed_usable, no text_exclusions, deduplicated by collector); crop and crop_sha256 and complete regeneration recipe present; id absent from union of release_exclusions.json classes[*].file. Crop existence is regenerability, not presence of the disposable original crop. Do not apply stratum_gate: ia_russian is withheld pending this correction. All selected rows also have usable_final=true.

All 10 W1 Russian books are pre1918 by the requested rule (at least 5 final hard signs or any ѣ/і/ѳ/ѵ); there are zero modern books. The requested 20-position modern spot check is unavailable in this input.

## Census per book

Final means immediately not followed by a Cyrillic letter, except `-` gets its own pre_hyphen class. A preceding Cyrillic letter is required. Offsets index Python Unicode code points in the unnormalized current `label`. Pre-hyphen positions are recorded and masked but never edit candidates. Uppercase signs are outside the specified lowercase ъ/ь census.

| Book (source ia_russian) | Rows / usable | Final ъ all / usable | Final ь all / usable | Pre-hyphen ъ all / usable | Pre-hyphen ь all / usable |
|---|---:|---:|---:|---:|---:|
| 487-beliaev-1800-kabinet-petra-velikago-izdano-po-vysochaishemu-poveleniiu | 306 / 110 | 206 / 92 | 205 / 97 | 0 / 0 | 1 / 1 |
| kniazhnamenshiko00bant | 206 / 90 | 209 / 97 | 75 / 35 | 1 / 0 | 3 / 1 |
| trudygeol3638190719088800 | 284 / 112 | 463 / 186 | 55 / 15 | 6 / 2 | 0 / 0 |
| opisanezapysnykh01vikt | 372 / 116 | 778 / 225 | 74 / 18 | 9 / 4 | 4 / 2 |
| razskayvolumes00goog | 305 / 122 | 459 / 212 | 160 / 76 | 7 / 5 | 7 / 3 |
| PolnoesobranieuchenyhputeshestvijpoRossi56 | 247 / 124 | 374 / 204 | 81 / 43 | 1 / 0 | 5 / 4 |
| bub_gb_yrhbAAAAcAAJ | 243 / 97 | 321 / 152 | 129 / 61 | 2 / 0 | 2 / 2 |
| 9.2-1848 | 413 / 177 | 505 / 193 | 58 / 17 | 8 / 5 | 4 / 0 |
| 1865.-ebook-2012 | 277 / 98 | 436 / 157 | 92 / 35 | 4 / 3 | 1 / 0 |
| IstorijaGosudarstvaRossijskagoT980 | 310 / 100 | 405 / 135 | 124 / 38 | 3 / 0 | 4 / 2 |

Counts by book and primary_class are in `artifacts/ru1/census.json`; every position and prior is in `artifacts/ru1/positions.jsonl`. Across all rows: final ъ 4,156, final ь 1,053, pre-hyphen ъ 41, pre-hyphen ь 31. Usable: final ъ 1,653, final ь 435, pre-hyphen ъ 19, pre-hyphen ь 15.

## Orthographic prior

Casefold Cyrillic token stem before the yer, without spelling normalization. Leave the target occurrence out of W1 label stem counts, including pre_hyphen. If other occurrences show both signs => both; only one => that sign_only. Otherwise unknown. No dictionary guesses or ink truth. Corpus evidence may itself contain Google errors; this is only a cross-check, never an edit decision.

| Prior on Google ь (final and pre_hyphen) | All | Usable |
|---|---:|---:|
| ъ_only | 77 | 34 |
| ь_only | 363 | 141 |
| both | 94 | 38 |
| unknown | 550 | 237 |

Final-only Google-ь prior distributions: all {'unknown': 532, 'ь_only': 352, 'ъ_only': 75, 'both': 94}; usable {'unknown': 228, 'ь_only': 136, 'ъ_only': 33, 'both': 38}.

## Bed, controls and contexts

The planned pre1918 bed has **314 lines / 869 masked slots**, including 405 candidate final ь positions after excluding all C1 control lines. All final yer signs are masked, including Google hard signs and pre-hyphen signs. Actual packed bed: **0 lines / 0 slots**.

The control inventory has **59 lines / 65 slots**: 31 slot-bearing lines plus 28 zero-slot lines. 19 C1 lines map exactly to W1; the 40 v2 lines have older source IDs and no W1 match. Their saved adjudication crops match the recorded SHA256 values from the original efficiency builder. The 19 C1 crops failed regeneration; no controls were packed. `keys/control_inventory.json` preserves table ink truth, offsets and the missing-W1 status explicitly. No invented W1 IDs.

Context list: **empty (0 built; 4 planned at ≤90 bed items plus about 10% controls)**. The builder uses seeded ordering and round-robin controls without within-context repetition; opaque IDs are fresh random hex. The closure scanner was run against the empty root; the overall readiness gate is FAIL because required contexts are absent. There are no manifests to issue for a nonexistent context.

Codex estimate: approximately 349 item reads × 0.2/100 = 0.698 weekly points for the available planned bed and controls. The modern supplement is excluded from this estimate because no eligible positions exist. Live meter: not probed (network OFF and no reading run). Usage ledger remains empty.

## Tooling and validation

The yer prompt and scanner-v4 test are copied verbatim. Scanner-v4 differs only in its replay temporary-directory path. Pack scanner adaptations select context-specific private keys, permit one reader, and check the pack-root shape. The original builder and mapper are retained under `scripts/secondary/reading/reference/`. The prepared launchers use gpt-6.1-sol / medium, network and web disabled, before/after probes, and the 78% refusal. They were syntax-checked, never executed. The mapper voids every edit proposal after more than one control-slot error, keeps u/other for review, and never edits Google ъ or pre-hyphen slots. Its output is a review proposal, not a label version.

Tests: 24 passed (13 text tests; 11 copied scanner-v4 tests). See `artifacts/ru1/text_tests.txt`, `scanner_tests.txt`, and `tests.json`.

Rebuild with the required x86_64 Python: `python3 -B scripts/secondary/ru1_census.py`; `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B scripts/secondary/ru1_build_packs.py`. The builder fails closed and records a blocked build if any required crop fails. The sourcing lead must resolve the regeneration/hash recipe and identify a modern-book input before this can become READY.

## RU1-0b

**READY: four blind reader packs built and closure verified.** This section supersedes the earlier blocked readiness and rebuild instructions; the RU1-0 receipt is preserved.

Regenerated **1146/1146 W1 crops**, unavailable **0**, using `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (arm64, Python 3.11.3, Pillow 12.3.0). Each `ensure_crop` call received a shallow row copy with its crop redirected into `ru1_cache/crops/`. Source-raster and crop SHA256 checks passed. `crop_unavailable.jsonl` is empty. No collector or .git writes, network, image viewing, reader run, or limit probe occurred.

The packs contain byte-exact copies of verified PNGs. The copied closure checker permits grayscale L as well as RGB PNGs so W1 bytes remain unchanged; it still checks content-hash names, metadata absence, links, public fields and closure. No image was visually read.

**Modern spot check: dropped**, as instructed: all 10 W1 books are pre-1918; no modern sample or replacement population was added.

Bed: **314 lines / 869 masked slots**, with **405 Google-final-ь edit candidates**. Every bed line appears in exactly one context. Both signs and pre-hyphen slots remain masked; only final Google-ь positions can later yield edit proposals.

All **59 control lines / 65 slots** are available: 19 C1 lines use regenerated W1 crops; 40 v2 lines use the saved `items_*.jsonl` adjudication crop paths, matched against the original recorded SHA256 before copying. Private keys retain their original source IDs and explicit `w1_id: null` for v2. The inventory includes 31 slot-bearing lines and 28 zero-slot lines. Zero-slot lines can test only the unmarked-final-hard-sign field and do not count toward the control gate; none were needed in these contexts.

Each context has nine slot-bearing controls. Round-robin allocation uses all 31 slot-bearing lines once before repeating five in another context; no line repeats within a context.

| Context | Bed lines | Bed slots | Control lines | Control slots | Total items |
|---|---:|---:|---:|---:|---:|
| ctx01 | 78 | 209 | 9 | 18 | 87 |
| ctx02 | 79 | 210 | 9 | 21 | 88 |
| ctx03 | 78 | 234 | 9 | 16 | 87 |
| ctx04 | 79 | 216 | 9 | 20 | 88 |

Pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru1`. Each `ctxNN/r1/` contains only `items.jsonl` and `crops/`; each `ctxNN/MANIFEST.r1.json` binds its files per HANDOVER §4. The copied `scan_packs.py` reports **ok** for all four contexts. Private keys and control truth stay in `artifacts/ru1/keys/`.

Estimated reading cost: 350 items × 0.2 weekly points / 100 = **0.700 weekly points**. No live meter was probed; the ledger remains unused.

Tests re-run: **24 passed** (13 text and 11 copied scanner-v4 tests); launcher shell syntax passed. Automatic artifact checks additionally verified complete bed coverage, source-byte equality, source-ID uniqueness, control rotation, availability of all controls, and all four manifests.

Rebuild (requires a fresh empty pack root): `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/secondary/ru1_build_packs.py`. Receipt: `artifacts/ru1/RU10b_RECEIPT.json`; previous `RU10_RECEIPT.json` kept unchanged.

## RU1-1b

**READY for r2 preparation; anchor-source exception documented below.** No reader, limit probe, network request, collector write, or .git write was made. R2 has not run.

Four `ctxNN/r2/` packs contain the same 350 items, controls, masks and PNG bytes as r1, in exact reverse order, with fresh opaque IDs. Private assignments are `artifacts/ru1/keys/ctxNN.r2.json`; each context has `MANIFEST.r2.json`. Closure passes **8/8 reader folders**, including content reversal, disjoint sibling IDs, content-hash PNGs, metadata absence and input-only file closure. Existing r1 `answers.jsonl` and `zoom/` runtime evidence was moved byte-for-byte to scratchpad `ru1_review/r1_runtime/ctxNN/`, outside the blind inputs. Every archived file and its original path is recorded in `artifacts/ru1/runtime_archive_RU11b.json`; canonical r1 answer artifacts are preserved unchanged. R1 manifests retain their original input bindings.

`run_bed.sh ctxNN [r1|r2]` defaults to r1. R1 answer/scan/mapped/control paths remain unchanged; r2 uses `ctxNN.r2.*`, its own pack and key, and distinct reader ledger entries. The before/after probes and weekly usage refusal at 78% remain. `RU1_DRY_RUN=1` reports paths and exits before probes, mkdir or launch. The mapper now accepts `--reader r2` while retaining the r1 default.

`python3 -B scripts/secondary/ru1_decide.py` joins non-control slots by `(row_id, offset)`. Reader context identities are `ctxNN/r1` and `ctxNN/r2`: separate reader invocations, sharing the prescribed item/control membership. Two independent hard reads, at least one VALID gate, and no soft read are required for `edit_hard`. Two soft reads yield `keep_soft`; disagreement, u/other, missing reads and exclusively VOID hard votes yield `lead_review`. Google hard signs and pre-hyphen positions have no decision rows and can never be edited. A prior disagreement records the vote decision, sets the final decision to `lead_review`, and is counted/listed in `decisions.summary.json`. Duplicate votes, inconsistent position metadata, gate mismatches and unclean scans fail closed. This tool writes proposals only.

The current `decisions.jsonl` has **405 Google-final-ь rows, all lead_review**, with r1 evidence and explicit null r2 reads. Summary status is `pending_r2`, with zero prior disagreements so far. These are incomplete evidence records, not completed two-reader decisions. Re-run the combiner after r2 mapping and scans exist.

The contact sheet is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/ru1_review/ru1_failed_controls.png`, with `sheets_index.json` beside it. It contains the **five failed slots and six correctly read anchors** (three hard, three soft). Each cell shows a line crop, exact 4× word and 8× final-letter crops using nearest-neighbor scaling, truth, r1 call and source ID. Crops are pinned by SHA256; magnification bounds come from exact retained Google symbol text anchors, not character-width estimates. V2 geometry uses the saved crop frame. The index records crop hashes, offsets, boxes, scale factors and source books. No image was visually read or control truth re-adjudicated by this preparation task.

**Anchor-source exception:** the failure books have only one correctly read r1 soft-sign control; the other two true-soft slots in those books are themselves failures. Thus three correctly read same-book soft anchors do not exist in these inputs. The sheet uses that one same-book soft anchor plus two correct soft controls from other pre-1918 books, visibly marked **OTHER BOOK** and flagged in the index. All three hard anchors are from failure books. This preserves six correct anchors without relabeling failures as correct. The lead still must verify the control truth visually.

`ru1_review.py --decisions artifacts/ru1/decisions.jsonl --output <scratch-output>` builds post-r2 lead-review sheets with r1/r2 calls, gate statuses and prior; at most 12 cells per sheet and a `sheets_index.json`. It refuses missing r2 evidence. This path was exercised **only with synthetic fixtures** now; no real bed review sheets were generated. Retained Google text must match exactly; missing/ambiguous or changed-label geometry fails explicitly for manual handling.

Validation: **39 targeted tests passed**, including **16 combiner cases**, launcher r1/r2 dry-runs, r2 mapping, reverse closure/tamper detection and review-builder fixtures; **11 scanner-v4 tests passed** (50 total). Shell syntax passed. Raw r1 answers were re-mapped and exactly matched all saved mapped/control outputs: 70/75 controls, ctx01/ctx02 VOID, ctx03/ctx04 VALID. Logs are `artifacts/ru1/text_tests_RU11b.txt`, `scanner_tests_RU11b.txt`, `scan_packs_RU11b.json`, and `r1_verified_RU11b.json`.

Image/closure commands use `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`; no crop regeneration was needed. Receipt: `artifacts/ru1/RU11b_RECEIPT.json`. Rerunning the r2 pack builder refuses existing packs; do not overwrite a prepared or used reader folder.

## RU1-S

**BLOCKED on ctx04/r2 image provenance; final owner HTML not emitted.** Control rescoring and the owner-sheet builder are implemented. No reader, network request, limit probe, collector write, cleanup-worktree write, or .git write occurred. The cleanup renderer is verified at `994456de085e8c5427eac490edb1f018cd680841` on `opus/cleanup-1`, satisfying the requested minimum. The owner builder uses the collect venv and cleanup PYTHONPATH and refuses incomplete two-reader decisions.

The disputed `ia_russian--d558bd3e803e7865--s003-l0032` slot 2 is excluded in both readers. Control `u` is an abstention, separate from wrong signs. More than one wrong sign makes a context VOID. The combiner independently recomputes gates from mapped controls and rejects stale gate statuses. `wrong_signs` is the gate count; the old `control_errors` field is retained only as explicitly labelled legacy raw mismatches, including abstentions and the excluded slot, for existing consumers/tests.

| Reader-context | Wrong signs | Abstentions | Excluded | Gate | Scan cleared |
|---|---:|---:|---:|---|---|
| ctx01/r1 | 1 | 0 | 1 | VALID | yes |
| ctx02/r1 | 1 | 1 | 0 | VALID | yes |
| ctx03/r1 | 1 | 0 | 0 | VALID | yes |
| ctx04/r1 | 0 | 0 | 0 | VALID | yes |
| ctx01/r2 | 0 | 0 | 1 | VALID | yes |
| ctx02/r2 | 1 | 0 | 0 | VALID | yes |
| ctx03/r2 | 1 | 0 | 0 | VALID | yes |
| ctx04/r2 | 0 | 0 | 0 | VALID | NO |

R1 totals: **70 correct / 74 scored, 1 abstention, 3 wrong signs**; 4/4 control gates VALID. R2 totals from saved answers: **72 correct / 74 scored, 0 abstentions, 2 wrong signs**; 4/4 control gates VALID. Gate validity does not clear the separate provenance scan.

At entry, ctx01/r2 and ctx04/r2 had failed scans and no canonical answers; ctx02/r2 had neither a scan nor canonical answers. Their completed raw answers existed in their reader folders. Offline scanning clears ctx02. Two narrow scanner corrections (literal `pwd` template base, Python `//4` mistaken for an absolute path) clear ctx01 and the path findings in ctx04. Same-mode, same-size, exact pixel matching now also permits PNG re-encoding as already described by the scanner policy. Nine new scanner regression cases preserve outside-path, mode-change, one-pixel and alpha-change rejection. Original failed ctx01/ctx04 scans are preserved in `artifacts/ru1/RU1S_original_scans/`. No image was visually read.

**Remaining blocker:** ctx04/r2 retains **15 unmatched image-provenance findings**. Its recorded panel command was reconstructed from manifest-bound original crops in a fresh temporary directory, without reading generated zooms as source. Exact matching failed. Automatic diagnostics indicate additional tool downscaling below the scanner's 2048-long-side envelope; the scanner's accepted downscale envelope/MAD policy was not widened. `scripts/secondary/ru1_rescan.py` preserves an exact-only reproducer and refuses unresolved images. A lead-cleared scan (or an independently justified, tested tool-downscale policy) is required. No scan waiver or invented read was supplied.

The mapper was rerun for r1 and clean r2 contexts; ctx04/r2 was mapped separately into `artifacts/ru1/RU1S_uncleared/`, without promotion to canonical accepted answers. The combiner was rerun and remains **pending_r2**: **edit_hard 102, keep_soft 184, lead_review 119** (missing independent reads 102; prior disagreement 14; reader disagreement 2; uncertain read 1). Accepted partial prior disagreements: **14**. All 405 positions are retained.

For transparent diagnosis only, `RU1S_uncleared/provisional_decisions.jsonl` combines all saved reads, including the uncleared ctx04/r2: **edit_hard 138, keep_soft 239, lead_review 28** (prior disagreement 21; reader disagreement 5; uncertain read 2), **21 prior disagreements**. These are explicitly **UNCLEARED_NOT_FINAL**, not accepted decisions.

`ru1_owner_sheet.py` implements one card per candidate bed line, severity grouping, all review/edit lines, up to 40 kept lines sampled with `20261017:RU1S`, W1 `text` for Google, label-only proposed edits, per-position reads/prior, book/decision tags, blank Printed, 4×/8× exact symbol-anchor zooms, source hashes and a strict 15,000,000-byte cap. It deliberately refuses the present incomplete decision summary. `owner_sheet/summary.json` records BLOCKED and no HTML/hash; no HTML size or card count is claimed. Actual HTML generation, size/layout checks and input-hash closure remain outstanding.

Validation: **76 tests passed, 7 subtests passed**, using the collect venv with `-B -m pytest --noconftest -q -p no:cacheprovider` over all RU1 tests and the copied scanner-v4 tests. Log: `artifacts/ru1/tests_RU1S.txt`. Receipt: `artifacts/ru1/RU1S_RECEIPT.json`. No live usage probe was made; the most recent existing r2 scan reports 37.0% weekly and is historical evidence only.

## RU1-R3

**READY for the lead's ctx04/r3 reading; no reading run or final owner HTML build was performed.** The 17 October ruling supersedes the RU1-S ctx04/r2 clearance proposal: **ctx04/r2 is VOID**, its **15 unmatched image-provenance findings remain unresolved**, and it is permanently excluded from accepted decisions. Its raw answers are now also preserved at `artifacts/ru1/RU1S_uncleared/ctx04.r2.jsonl`, alongside the existing mapped answers and historical UNCLEARED_NOT_FINAL provisional outputs. Control-score VALID in the historical RU1-S table does not override this provenance ruling. No downscale-policy change, network request, usage probe, collector/cleanup write, or .git write occurred.

`ru1_third_reader.py` built `PACK_ROOT/ctx04/r3/` once from ctx04/r1: **88 items, including the same 9 control items (20 control slots)**, identical crop bytes and private item/slot metadata, seeded shuffle **`20261017:RU1:ctx04:r3`**, and fresh opaque IDs disjoint from earlier assignments. The builder refuses overwrite. `artifacts/ru1/keys/ctx04.r3.json` and `PACK_ROOT/ctx04/MANIFEST.r3.json` are written. Closure is **ok**; `artifacts/ru1/closure_RU1R3.json` records every public-file hash. The closure scanner verifies the seeded r3 order and ID separation while retaining r1/r2's reverse-order contract.

Launcher and mapper accept r3 and resolve **`ctx04.r3.*`** paths. The launcher refuses the VOID ctx04/r2 assignment. Both dry-run checks passed; logs are `artifacts/ru1/launcher_dry_run_RU1R3.txt` and `artifacts/ru1/mapper_dry_run_RU1R3.json`. The mapper dry-run checks the actual pack/key assignment without requiring or inventing reader answers.

`ru1_decide.py` now defines the eight accepted assignments explicitly: ctx01–04/r1, ctx01–03/r2, and **ctx04/r3**. Both the combiner and owner-sheet input hashing use this list. ctx04 decisions expose the actual `r3` read/context rather than relabelling it r2; owner cards display that identity. ctx04/r2 is never opened by the combiner, even if malformed, scan-failed, or apparently clean with conflicting calls. Missing r3 remains missing; it cannot fall back to r2. **7 dedicated combiner/r3 routing tests passed.** Existing partial decision files were not regenerated during this preparation.

After the lead runs and clears the r3 reading, run one command from this worktree:

```sh
scripts/secondary/ru1_finalize.sh
```

It uses the **collect venv** with **cleanup PYTHONPATH**, and performs **all accepted scan checks → all mappings → combiner → `ru1_owner_sheet.py` HTML build → `artifacts/ru1/finalization.summary.json`**. Scan checks require boolean `ok: true`, no unresolved violations, and no skipped manifest check. All eight scans must clear before any mapping/output write; all mappings are validated in memory before emission. Control-gate VOID retains the RU1-S decision rules and is distinct from scan clearance. Owner rendering retains the RU1-S line-card, zoom, sample, input-hash and size rules. Final summary records decisions, owner-sheet results and accepted scan hashes. Fixture tests verify refusal for each missing accepted scan, false/non-boolean clearance, unresolved violations and skipped manifests; successful stage order; and no success summary after an owner-build failure.

`ru1_finalize.sh --dry-run` passed with **no writes**, printing the complete plan and accepted assignments. It explicitly reports `scans_cleared: false` because ctx04/r3 has not yet been read/scanned. A normal invocation was separately checked and **refused before writes** with `scan has not cleared: ctx04.r3 (missing)`. Thus dry-run success is preparation readiness, not completed finalisation or owner-sheet validation.

**Scanner-v4 delta.** The complete diff against the live sol-reading v4 source (`docs/records/harvest/sol_reading/tools/scan_rollout.py`) is recorded in [`artifacts/ru1/scanner_v4_RU1R3.diff`](../../../../artifacts/ru1/scanner_v4_RU1R3.diff). No scanner code was changed in RU1-R3. The two lead-accepted RU1-S path corrections are visible in that diff: (1) resolve only the exact literal `pwd` template expression to the reader directory, without executing it; (2) the absolute-path regex lookbehind changes from `(?<![\w:/])` to `(?<![\w:/)])`, avoiding the false `/4` path in `(j+1)//4`. The full diff also records the pre-existing local replay-temp relocation and RU1-S same-mode/same-size/exact-pixel PNG re-encoding match. These are disclosed separately from the two path corrections. The downscale envelope remains **2048 long side, one-pixel aspect tolerance, RGB MAD strictly below 2.0**, with the same resampling filters. ctx04/r2's 15 unmatched images are not cleared by any of these changes.

Validation: **104 tests passed, 7 subtests passed**, with the collect venv using `-B -m pytest --noconftest -q -p no:cacheprovider` across the RU1 tests and copied scanner-v4 tests. Dedicated routing subset: **7 passed**. Both shell scripts pass `bash -n`. Logs: `artifacts/ru1/tests_RU1R3.txt`, `artifacts/ru1/routing_tests_RU1R3.txt`, `artifacts/ru1/finalize_dry_run_RU1R3.json`. Receipt: `artifacts/ru1/RU1R3_RECEIPT.json`. Remaining lead action: run ctx04/r3 reading; then invoke the finalisation command. Actual final decisions and owner HTML remain pending that read and scan.

## RU1-F

**Finalisation complete; rendered layout QA blocked by computer-use approval.** The lead-completed ctx04/r3 scan is **ok** (`ok: true`, no violations, manifest check not skipped). `scripts/secondary/ru1_finalize.sh` completed all eight accepted scan checks → mappings → combiner → owner HTML → finalisation summary. ctx04/r3 replaces ctx04/r2; ctx04/r2 remains VOID and excluded. No reading run, network request, classification, collector/cleanup write, or .git write occurred.

Final decisions over **405 positions**: **edit_hard 139, keep_soft 239, lead_review 27**. Review reasons: **prior_disagreement 21, reader_disagreement 4, uncertain_read 2**. There are **21 prior disagreements**, listed individually in `decisions.summary.json` and the RU1-F receipt; these remain lead_review rather than edits.

| Reader-context | Wrong signs | Abstentions | Excluded | Correct / scored | Gate | Scan |
|---|---:|---:|---:|---:|---|---|
| ctx01/r1 | 1 | 0 | 1 | 16 / 17 | VALID | ok |
| ctx02/r1 | 1 | 1 | 0 | 19 / 21 | VALID | ok |
| ctx03/r1 | 1 | 0 | 0 | 15 / 16 | VALID | ok |
| ctx04/r1 | 0 | 0 | 0 | 20 / 20 | VALID | ok |
| ctx01/r2 | 0 | 0 | 1 | 17 / 17 | VALID | ok |
| ctx02/r2 | 1 | 0 | 0 | 20 / 21 | VALID | ok |
| ctx03/r2 | 1 | 0 | 0 | 15 / 16 | VALID | ok |
| ctx04/r3 | 0 | 0 | 0 | 20 / 20 | VALID | ok |

The mapper now uses deterministic unit-cost character alignment, considering **every optimal alignment** rather than trusting a tie-break. A yer and its entire alphabetic word must map unchanged, contiguously, with the same word boundaries and one unique exact mapping in every alignment. Deletion, substitution inside the word, or ambiguous repeated-word placement yields no zoom. Any such position suppresses all zooms on the card and adds `zoom: unaligned`; its line crop and label-based proposal remain. `collect_v3/vendor/conventions.py` has `roman_fixes` old/new token records without offsets; `pipeline.py` also has assembly, em-dash and later rule changes, so those records are not a complete offset map. No convention is reversed or guessed.

**Displayed zoom positions: aligned 245, unaligned 0.** Across the entire candidate population, label↔Google-text alignment is **aligned 405, unaligned 0**; the 160 undisplayed positions were checked textually without claiming rendered zooms for them. Geometry receipts retain both label and Google offsets. The intro's last sentence explicitly says: “Proposed is built on the W1 label (the current label version).” Google rows retain W1 `text`.

The single self-contained HTML is `artifacts/ru1/owner_sheet/ru1_sheet.html`: **14,988,436 bytes / 14.988436 MB; 174 cards**. All groups below are sections of this same file, so the size applies to the shared file, not separate group exports.

| Group | HTML path | Shared file size (MB) | Cards shown | All candidate lines | Positions shown / all in group |
|---|---|---:|---:|---:|---:|
| Needs a look | `artifacts/ru1/owner_sheet/ru1_sheet.html` | 14.988436 | 26 | 26 | 44 / 44 |
| Proposed ъ | `artifacts/ru1/owner_sheet/ru1_sheet.html` | 14.988436 | 108 | 108 | 156 / 156 |
| Kept ь | `artifacts/ru1/owner_sheet/ru1_sheet.html` | 14.988436 | 40 | 180 | 45 / 205 |

The initial 4× word / 8× letter build was 15,574,528 bytes and refused the 15 MB cap. As permitted by RU1-S, final zoom PNGs use **3× words / 6× letters**, both above native resolution, with nearest-neighbor scaling. No line crops were reduced. All review/edit lines are shown; kept lines retain the prescribed seeded 40-line sample. Group positions include every candidate on each line, including less-severe decisions.

Validation: **113 tests passed, 7 subtests passed**, including **9 new mapping/proposal cases** for changes elsewhere, changes within a word, ambiguous repeated words, repeated-word identity, and proposals based on the current label. The collect venv, cleanup PYTHONPATH, `-B`, `--noconftest`, and disabled pytest cache were used. Builder input hashes and accepted scan hashes were rechecked after finalisation. Structural HTML checks confirm 174 cards, 664 embedded images (490 zooms), blank Printed and Note fields, and no external resource elements. Logs: `artifacts/ru1/tests_RU1F.txt`, `finalize_RU1F.log`, `layout_checks_RU1F.json`; receipt: `artifacts/ru1/RU1F_RECEIPT.json`.

**Visual limitation:** zero rendered cards were opened (within the maximum of three), and none were classified. Computer Use returned “Computer Use was not approved to use Google Chrome”; Chrome and in-app browser surfaces were unavailable, and the available browser inventory was empty. Layout appearance remains unverified; structural validation is not visual QA.

## RU1-L

**Ready for lead shape adjudication; no classifications made.** The sheets are in the existing scratchpad at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/ru1_review/lead/`. `review_001.png`–`review_003.png` contain all **27 lead_review positions** (10, 10, 7 cells); `audit_001.png`–`audit_004.png` contain **40 audit positions** (10 per sheet). Cell numbers are globally unique, 1–67. Each cell shows the same-book reference **ъ on the left**, the target in the centre, and reference **ь on the right**, all at **8× native pixels**, followed by a **4× word crop**, a small line crop, and the accepted r1/r2 or r1/r3 calls. No prior or Google transcription is displayed. Nearest-neighbour scaling and the existing RU1-F unambiguous whole-word alignment plus saved symbol-box crop geometry are reused; no source crop is regenerated.

**References cover all 10 books (20 glyphs): 3 books use two ink-truth controls, 3 use one ink-truth control plus one agreement reference, and 4 are agreement-only.** Thus 7 books have at least one agreement reference (11 agreement glyphs in total). Every agreement reference is explicitly labelled **“agreement reference, not adjudicated”** on the sheets. Control truths were cross-checked between `keys/control_inventory.json` and the saved adjudication `table.json`; the disputed d558bd3e803e7865-s003-l0032 slot 2 was excluded. Same-book controls correct for every accepted reader are preferred. The only available soft-sign control for `PolnoesobranieuchenyhputeshestvijpoRossi56` is retained as ink-truth despite a reader error; its complete calls and `all_readers_correct: false` are recorded. Where a control sign is absent, references come from non-control final positions with unanimous accepted reads; hard-sign agreement references also require Google ъ. ctx04/r2 is excluded throughout. `references.json` records each reference source position, basis, calls, exact geometry, and source hash; `references/` contains all 20 separate 8× PNG crops.

The audit uses **`20261017:RU1L:audit`**. The 30 edit_hard positions are sampled by proportional book quotas using Hamilton largest remainders (lexical book tie-break), then seeded sampling within each sorted book population. The same seeded RNG subsequently samples 10 keep_soft positions from the sorted population. The receipt records book populations and quotas; books with quotas rounded to zero are not forced into this proportional sample. Review and audit decisions are existing proposals, not lead rulings.

`sheets_index.json` maps every numbered cell to row ID, label offset, set, existing decision, accepted reads, sheet rectangle and crop geometry. `artifacts/ru1/lead_review_template.jsonl` contains **67 unanswered rows**, each exactly `{cell, row_id, offset, set, lead: null, note: ""}`. The index ↔ rendered-cell ↔ answer-row count check passed: **27 review + 30 edit_hard + 10 keep_soft = 67**, with no sheet exceeding 10 cells. No test suite or reader was run. No network, .git, collector, cleanup, or label writes occurred. Built with the collect venv, cleanup PYTHONPATH, and `-B` using `scripts/secondary/ru1_lead_sheets.py`. Receipt: `artifacts/ru1/RU1L_RECEIPT.json`, including input/output SHA-256 hashes.

## RU1-2

**READY.** Applied the recorded lead rulings from `RU1_LEAD_REVIEW.md` through the RU1-L cell index: cells 1–8, 10–16, 18–22 and 24–26 → edit_hard (23); cell 23 → keep_soft; cells 17 and 27 → hold_yat; cell 9 → hold_uncertain. Each position records `lead_ruling`, the cell and review-document reference. Audit cells 28–67 retain every original decision and record `lead_audit_confirmed` (30 edits and 10 keeps). Final position counts: **162 edit_hard, 240 keep_soft, 2 hold_yat, 1 hold_uncertain**. The original decisions and summary are preserved as `decisions.pre_ru1_v1.jsonl` and `decisions.summary.pre_ru1_v1.json`; the current decision summary records the resolved stage. The prior disagreement trigger is withdrawn as the lead directed.

`artifacts/ru1/ru1_v1.jsonl` contains **314 ia_russian W1 rows: 311 ok, 3 hold**, covering exactly the non-control bed lines with at least one Google-final-ь position. Parent labels are copied exactly from W1 `label`. There are **162 single-character ь → ъ edits: 139 two_reads, 23 lead_ruling**. Holds keep the parent character; any row containing a hold is marked hold, even if another position on that row is edited. Offsets are Unicode code-point indices into `label_parent`. Every other character is byte-identical. SHA-256: `1fb0a9f5bde4a166fd480ffb414d5e376596b600fd728b6e099b6b1803af2db0`. The manifest gives all input hashes, counts and all **36 excluded bed control lines**; controls keep their label, and v2 controls without a W1 mapping remain outside this version.

The owner page remains `artifacts/ru1/owner_sheet/ru1_sheet.html`, titled **RU1 Hard Sign Decisions**, using the same cleanup owner-sheet renderer. It has only **What a change looks like** (12 seeded edit-position cards, sampled from all 162 edits with seed `20261017:RU12:owner`) and **Held back** (all three hold rows). Each comparison puts the saved same-book hard reference on the left, the target in the middle at **8× native pixels**, and the soft reference on the right; a 3× word crop follows. Google uses W1 `text`, Proposed uses `label_ru1_v1`, with only the target word highlighted in each. No Reads row or Printed input is supplied. The four-sentence intro gives the counts, audit result and plain shape-comparison instruction. File size: **792,856 bytes / 0.792856 MB**, below 5 MB; SHA-256 `6f27c69d8c26ef6f80dfc10ded7d7ec33683900a09428e3bf60b859bf7a2cb45`. The original owner geometry manifest is retained in `owner_sheet/summary_RU1F.json`. RU1-L reference provenance, including agreement references that were not adjudicated, is retained per card in the new summary.

**Validation: 110 tests passed**, including eight new artifact checks for exact population and W1 parent binding, unchanged non-edited bytes, protected Google-ъ/pre_hyphen slots, hold status and edit basis, exact lead rulings and unchanged audit decisions, manifest hashes/control exclusion, HTML structure/highlights/size, and seeded selection/geometry. The existing mapping, decision, review, scanner, census and finalisation suites also passed. Test log: `artifacts/ru1/tests_RU12.txt`. One generated comparison bitmap was visually inspected for caption placement and clipping; browser layout was not verified. No new glyph classifications, reader run, network request, .git write, or collector/cleanup write occurred. The only external run data read was the explicitly named W1 features file; all other pixels and geometry came from existing saved RU1 artifacts. Interpreter: collect venv; cleanup PYTHONPATH; `-B`; pytest cache disabled. Receipt: `artifacts/ru1/RU12_RECEIPT.json`.
