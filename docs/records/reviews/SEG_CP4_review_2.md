# SEG-CP4 / SEG-CP4b Sol code review 2

2026-10-18. **FAIL: 1 blocking, 1 high; 3/5 CP4 acceptance requirements reproduced.** Reviewed the uncommitted checkpoint and fix round against ASTRA-SEG1 PLAN item 4, with CP2/CP3 dependencies and the earlier review. HEAD: `9937b6206c8ba80e681ae1aabca6428c9f020f58`. The updated receipt accurately discloses the failures. GATE_FAIL must remain; this work is not qualified for application/publication.

Only this report was written in the worktree. Verification stdout and pytest fixtures were confined to `/tmp`; no implementation, admission artifact, receipt or Git state was changed. No preparation was rerun: its once-per-source claim is already consumed.

## Findings by severity

### Blocking — B1 remains open: required DROP coverage and required resolution fail

**Locations:** `greekocr/harvest/geometry_observations.py:113`, `docs/records/harvest/collect_v3_admission/seg/verify_cp4.py:75`, `docs/records/harvest/collect_v3_admission/seg/CP4_RECEIPT.md:25`.

Independent native measurement still gives **8/9 required DROP** and **1/31 unresolved required calibration witnesses**. `nlg--6146c0455e0103d2--s001-l0006` remains unavailable with `invalid_source_frame_or_labels`; it is correctly retained in D and not counted as detected. Two CP4 acceptance requirements therefore remain unmet. Strict rejection of inconsistent planes is appropriate; relaxing validation would not close the finding.

The fallback mechanism is now present and isolated: `prepare_cp4_geometry.py:19` claims the source before processing, and line 73 calls the existing collector `geometry.io.cache_page()`. I verified **1 attempt marker, 1 serialized receipt, 0 usable fallback pages**, full source/detector/options binding, and identical inherited/fallback hashes for `ink.png`, `labels.npz` and `detector.json.gz`. The current script's richer preparation binding was added after the saved marker; the original marker binds source path/hash and complete detector digest, while options/payloads are checked through the receipt. This is disclosed, not a fabricated stronger historical marker.

The read-only census reproduces **100 entries, 5 inconsistent**: live g1b **3/75**, inherited CP3 **1/24**, isolated CP4 **1/1**; four distinct page IDs. NLG has **41,068 label-without-foreground pixels**, box `[1102,0,1192,1724]`. Live discrepancies are 3,517, 2,959 and 1,742 pixels on the three pages named in the receipt. Each entry's four file hashes stayed unchanged during the census. The collector's `greekocr/pages/pixels.py:625` computes labels before lines 643–648 clear scan-edge foreground without updating labels, explaining why unchanged-pipeline preparation repeats this inconsistency. This diagnosis and the honest failed fallback improve the evidence but do not repair the acceptance failure. An upstream consistency repair and an explicitly revised preparation policy remain necessary.

### High — H1 is only partly closed: fragment bypass fixed, required CP3 regression gate fails

**Locations:** `greekocr/harvest/row_inclusion.py:99`, `greekocr/harvest/row_inclusion.py:105`, `docs/records/briefs/SEG_CP4b_fix.md:14`, `docs/records/harvest/collect_v3_admission/seg/CP4_RECEIPT.md:33`.

The original union bypass is repaired: complete guide/native extents for a resolved local group are required before that row contributes to `merged`, before owner selection. The original partial-horizontal-group control now gives neighbour=False and union=False (`tests/test_seg_cp4.py:73`). All original nine controls give **0/9 drops** on both screens; the expanded set gives **0/12** on both, with **one unresolved** fragment control rather than a verified KEEP.

However, the fix brief explicitly requires retaining CP3 acceptance. Independent `verify_cp3.py` execution gives **KEEP 22/22, C1 6/7, gallery 6/6**, overlap **5**, unique merge witnesses **8**, and zero planted single-row/half-letter/column false positives. The failed C1 case is `gazette_modern--2e613d9290dd13d4--s000-l0209`, a measured negative, not unavailable. Thus H1 cannot be marked fully closed.

I independently matched its regenerated local groups to `CP4_C1_conflict.json`, checked source/response hashes and token 943's recorded text/box (`μένης`, `[216,1233,257,1254]`). In original crop `[217,1211,715,1249]`, row `row-00103` has a complete individual body run at x225:232 but its group spans `[217,1236,256,1251]` and is incomplete. Only `row-00102` qualifies as complete. This supports the receipt's explanation of the lost hit. Do not restore a partial-word positive or remove the challenge to force 7/7: the frozen challenge requirement and the repaired predicate still need resolution before qualification. The failure is reported honestly and is separate from the nine-case required DROP denominator.

### Medium

No additional findings.

### Low

No additional findings.

## Earlier review closure

| Earlier finding | Verdict | Current evidence / file:line |
|---|---|---|
| B1 — required coverage/resolution | OPEN, blocking | Failed fallback remains unavailable; D 8/9, unresolved 1/31. `geometry_observations.py:113`; `CP4_RECEIPT.md:27`. |
| H1 — union bypass / fragment accounting | PARTLY CLOSED, high | Bypass and accounting repaired; CP3 C1 acceptance regresses to 6/7. `row_inclusion.py:105`; `tests/test_seg_cp4.py:74`; `CP4_RECEIPT.md:33`. |
| H2 — middle-region extent mistaken for native completeness | CLOSED for reported defect and controls | Full native parent pixels are read outside row/middle bounds, partitioned across toolkit split children, and used for clipping. `neighbour_words.py:230`, `neighbour_words.py:283`; top-stroke and shared-parent conservation controls at `tests/test_seg_cp4.py:223` and `tests/test_seg_cp4.py:237`. Both top strokes reject neighbour and union; split overhang is retained and rejected. |
| H3 — native one-letter probes | CLOSED for specified row-local probes | Same tokens 549 Ο, 567 Ο, 652 ο now give 3/3 positives, 0 unresolved, with explicit source/response-bound recorded geometry. `neighbour_words.py:145`, `neighbour_words.py:286`; `tests/test_seg_cp4.py:145`. These are row-local corroborated probes, not an end-to-end claim that the neighbour API automatically supplies response geometry. |

Paths abbreviated in this table are under `greekocr/harvest/` or `docs/records/harvest/collect_v3_admission/seg/`, respectively.

## Sol code-review criteria — verbatim, individually applied

Authority: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:206`:

> one supported neighbour row/run per positive, visible complete bodies plus word-scale extent; no anonymous all-pairs bridge, marks-as-letters inflation or arbitrary length veto; half-letters alone never drop. Frozen ownership is a measurement, not independent truth.

| Verbatim criterion text | Verdict | File:line and evidence |
|---|---|---|
| one supported neighbour row/run per positive | PASS for provenance | `greekocr/harvest/neighbour_words.py:365`, `greekocr/harvest/neighbour_words.py:374`, `greekocr/harvest/neighbour_words.py:315`: one explicit same-column/page-side row and local group per neighbour positive; row IDs, native parents and neighbour x-height retained. Structural positives separately require two distinct supported rows. |
| visible complete bodies plus word-scale extent | PASS for repaired mechanics and supplied controls; semantic qualification remains FAIL | `greekocr/harvest/neighbour_words.py:274`, `greekocr/harvest/neighbour_words.py:306`, `greekocr/harvest/neighbour_words.py:317`: full native bounds plus guide/body support, all letters in the group, and width. `WORD_PROXY` at line 141 explicitly remains a development proxy; native recorded probes resolve 3/3. These controls do not establish general lexical truth or overcome B1/H1. |
| no anonymous all-pairs bridge | PASS on CP4 path | `greekocr/harvest/neighbour_words.py:256`, `greekocr/harvest/neighbour_words.py:258`: existing original-ink profile and ordered adjacent letters within one row. Historical pairwise `runs()` at line 54 remains diagnostic, is not called on this path, and does not qualify admission. |
| marks-as-letters inflation | PASS for supplied controls (prohibition satisfied) | `greekocr/harvest/neighbour_words.py:193`, `greekocr/harvest/neighbour_words.py:207`; `tests/test_seg_cp4.py:122`: native rule exclusions and existing middle-region letter machinery yield no DROP for marks/noise/rules. The constructed `role='letter'` at line 202 is a candidate descriptor, not saved semantic ground truth; no universal role-classification claim is warranted. |
| arbitrary length veto | PASS (prohibition satisfied) | `greekocr/harvest/neighbour_words.py:141`, `greekocr/harvest/neighbour_words.py:182`; `tests/test_seg_cp4.py:32`, `tests/test_seg_cp4.py:137`: minimum body count one, ten-body setting rejected, all 1–9-body positives caught. |
| half-letters alone never drop. | PASS for supplied controls | `greekocr/harvest/neighbour_words.py:281`, `greekocr/harvest/neighbour_words.py:283`; `tests/test_seg_cp4.py:43`: both edges at exact 50% and 60% visibility give neighbour=False and union=False, 0/4. Expanded fragment set is 0/12 drops, one unresolved. |
| Frozen ownership is a measurement, not independent truth. | PASS | `greekocr/harvest/neighbour_words.py:290`, `greekocr/harvest/geometry_observations.py:192`; `tests/test_seg_cp4.py:208`: unchanged `801d517e…` digest, direct-core mask parity, diagnostic foreign fraction, no ownership retuning or claim that foreign ink independently proves a word. |

## Acceptance independently reproduced

The five requirements are from PLAN item 4, `ASTRA-SEG1_review_1.md:207`. Counts below come from fresh execution, not the receipt.

| Requirement | Neighbour alone | Structural/neighbour union | Verdict |
|---|---|---|---|
| 0/22 KEEP false drops | 0/22; 22 resolved | 0/22; 22 resolved | MET |
| D/D required DROP | 8/9, one unavailable | 8/9, one unavailable; D unchanged at 9 | NOT MET |
| 0 planted fragment-only drops | Original 0/9, expanded 0/12 | Original 0/9, expanded 0/12; one unresolved in each set | MET for no-drop requirement |
| all planted complete short-word positives caught | 10/10 mechanical positives (1–9 bodies plus joined letters); 3/3 recorded row-local one-letter probes | 10/10 mechanical union positives; native probes are row-local, not union fixtures | MET for specified controls |
| 0 unresolved required calibration witnesses | 1/31 | 1/31 | NOT MET |

Result: **3/5**. Synthetic bars verify mechanics only. The nongating borderline remains neighbour=False, merged=False, union=False, without relabelling. For neighbour, merged and union separately, the required-ledger matrix is **TP=8, FP=0, FN=0, TN=22, unknown=1**. Measured precision and recall are 8/8 (Wilson 95% `[0.6755924351,1]`); KEEP false-drop and survivor-defect rates are 0/22 (`[0,0.1486548746]`). Required-positive coverage is **8/9**, not 100%. C1's measured miss is outside this matrix and remains separately reported. This selected development population does not establish generalization.

## Reproduction and F2/F3 reuse

Used exactly `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, with `PYTHONDONTWRITEBYTECODE=1` and `-B`. Tests:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp4-review2-tests tests/test_seg_cp4.py tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
```

**356 passed in 6.57s**, including 35 CP4 cases. Independently ran all read-only checkpoint scripts under `docs/records/harvest/collect_v3_admission/seg/`: `verify_cp4.py`, `verify_cp4_controls.py`, `audit_cp4_cache.py`, `verify_cp3.py`, `guard_cp4_commit.py`. The first four regenerated JSON outputs are JSON-equal to their saved CP4b counterparts. Stdout is preserved as `/tmp/seg-cp4-review2-{native,controls,cache,cp3}.json`. The controls script executes the fixtures and records both decisions; I checked its counts separately rather than relying on the native verifier's saved-controls input. Guard: **PASS, 18 exact files**, correct base HEAD, unchanged 120 inherited cache-file hashes and five separately bound fallback files. Preparation execution was deliberately excluded from this read-only review; its saved claim, receipt, source and payload identities were independently checked.

F2/F3 toolkit reuse is real, with new adapter/group-completeness glue rather than a new detector: `geometry_observations.py:84` reads source/options/full-detector/payload-bound cache hits; `row_inclusion.py:65` consumes existing `box_hits()`, and line 90 calls existing `band_cut()`. `neighbour_words.py:177` constructs existing `Band`/`LineGlyphs`, line 207 calls `letter_boxes()`, line 256 uses `BoundaryEvidence.profile()`, and line 323 uses `straighten_edges()`. The .35 x-height empty-gap scale already exists at `greekocr/glyphs/oriented_page.py:88`. Native extent/provenance reconstruction reuses the saved label plane and toolkit split cuts. No new row/page detector, curve refit, re-binarization or painting is used in measurement. Missing/ambiguous evidence remains explicit (`neighbour_words.py:349`, `neighbour_words.py:367`). No production calibration-ID whitelist was found; the preparation script's one NLG page is an explicit preparation scope, not an admission exception.

The legacy component graph and its thresholds remain archival diagnostics, not a CP4 completeness or word-boundary claim (`neighbour_words.py:33`, `neighbour_words.py:54`). The new .2/.8/.35 parameters are disclosed proxies, still unqualified; toolkit reuse does not turn them into semantic truth. Unrelated existing staging/.gitignore/NW drafts are outside the guarded CP4 scope and were not executed. No CP5+ work or recognizer/reading run was performed.

## Protected artifacts and live-run assurance

Independently SHA-256 compared working bytes with `git show HEAD:<path>` bytes. **8/8 tracked protected artifacts match HEAD**, including the crops manifest and admission outputs. All **9/9 frozen protected hashes** match; the ninth file, `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.json`, is untracked and has **no HEAD blob**, so only its frozen hash is verified.

Read the manifest from HEAD itself and hashed every referenced PNG, including ignored crops: **28,798/28,798 match the HEAD manifest**, which itself matches HEAD. Broader HEAD-blob comparison of paths ending `.png`, named `crops_manifest.jsonl`, or containing `admission` in the basename found **0 mismatches among 1,587 present files, including 1,573 PNGs**. Another 27 selected paths are absent sparse-checkout entries, all confirmed `S`/skip-worktree. The selection differs slightly from review 1's broader scan; these counts are from this review's explicit filter. No protected admission/manifest/PNG tracked diff exists.

Both native verifiers record **0 runtime filesystem write attempts and 0 detector/network calls** under their mutation guards (`verify_cp4.py:23`). The reviewed cache-hit path has no write/lock branch; the preparation code restricts writes/mutations to isolated `CP4_geometry` (`prepare_cp4_geometry.py:40`). Tests write only temporary fixtures under `/tmp`. Consequently **no write or lock to the live run root by this reviewed SEG execution was observed or attempted**; publication actions are **0**. Historical preparation is evidenced by isolated artifacts and inspected code, not retrospectively traced system calls. As `docs/records/briefs/SEG_CP4_build.md:18` explains, independent collector materialization may alter the live tree; this review cannot certify all-process live-root immutability or every historical process's I/O. No collector process was stopped or changed.

SEG-CP4 review: FAIL | blocking: 1 | high: 1 | acceptance: 3/5 met reproduced | publish actions: 0
