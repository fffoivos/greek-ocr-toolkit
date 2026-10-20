# SEG-CP3 / CP3b Sol code review 2

2026-10-18. Reviewed the uncommitted candidate at HEAD `788c7ad8c681bd6b23a3bf26d88973b45b4dea72` against ASTRA-SEG1 Numbered PLAN item 3 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:197`), both build/fix briefs, and the earlier review. **CP3 algorithm acceptance: 4/4 reproduced. Overall review: FAIL because CP3b M1's required process attribution remains unverified.** B1 is closed; no blocking/high code defect was established. This does not qualify the admission union or authorize publication.

## Findings by severity

### Blocking

None open. Earlier **B1 is CLOSED**: the six previously unavailable Gazette merge witnesses now measure successfully without deleting them from either denominator. See the closure evidence below.

### High

None established in the reviewed CP3/CP3b scope.

### Medium — M1 remains partially open: the required writer identity is not verified

**Locations:** `docs/records/briefs/SEG_CP3b_fix.md:17`; `docs/records/harvest/collect_v3_admission/seg/CP3_RECEIPT.md:60`; `docs/records/harvest/collect_v3_admission/seg/CP3_RECEIPT.md:62`; `docs/records/harvest/collect_v3_admission/seg/verify_cp3.py:28`.

The fix brief explicitly requires the collector process's start time and command from `ps`, in addition to a no-SEG observation window. The receipt correctly narrows its assurance and explicitly leaves that process evidence unverified. I independently attempted `ps -axo pid,lstart,command`; the managed sandbox again returned `operation not permitted: ps`. Thus the current materialize PID, start time and command have not been independently reproduced. The archived supervisor/worker ids do not close this requirement. This is missing evidence, not an allegation that SEG wrote the live tree.

A fresh **25.010421-second** window, with no SEG scripts/tests running, independently reproduced both directory changes:

| Live-root directory | Before mtime_ns = ctime_ns | After mtime_ns = ctime_ns |
|---|---:|---:|
| `W2/crops` | 1792279833815062850 | 1792279859863218510 |
| `cache/g1b` | 1792279833815328603 | 1792279859863500513 |

The window spans Unix times `1792279838.212265`–`1792279863.222686`. Its observing process only performed stat/sleep. The independent record is `/tmp/seg-cp3-review2-no-seg-window.json`. A separate full-tree metadata comparison found **31,404 entries before/after**, with only these two directories changed; that earlier comparison overlapped the geometry audit and is not the no-SEG window.

Collector source supports the proposed mechanism: `collect_v3/storage.py:77` calls `finalize`; `collect_v3/runner.py:86` invokes `page_rows`; `collect_v3/storage.py:40` passes the tranche crops directory to existing analysis; `collect_v3/storage.py:43` then discards crops and the page's g1b cache via `collect_v3/storage.py:19` (all paths in the sibling `greek-ocr-toolkit-sol-collect` checkout). This establishes a compatible write path, not which running process used it.

**Required closure:** supply permitted, contemporaneous PID/start/command evidence for the identified materialize process and bind it to the independent directory-change window. Keep the receipt's limited assurance until then. I can confirm zero write attempts in the guarded SEG verifier and no inspected SEG path writing/locking the live root; I cannot confirm that nothing wrote to the live root. The observed directory changes contradict whole-root immutability.

### Low

None established.

## Sol code-review criteria — verbatim, one by one

The criterion column reproduces the four semicolon-separated criteria at `ASTRA-SEG1_review_1.md:200` verbatim. These verdicts concern CP3's supported-row mechanics and bounded fixtures.

| Criterion | Verdict | File:line and independently checked evidence |
|---|---|---|
| count physical structural rows, not delivery pieces | PASS | `greekocr/harvest/row_inclusion.py:53` validates structural addresses; `greekocr/harvest/row_inclusion.py:106` deduplicates row ids within page-side/column sets. `tests/test_seg_cp3.py:52` passes for two delivery pieces of one physical row. |
| use row-relative/local occupied overlap, not crop-height overlap | PASS | `greekocr/harvest/row_inclusion.py:65` uses existing `box_hits`; `greekocr/harvest/row_inclusion.py:85` selects local assigned body columns; `greekocr/harvest/row_inclusion.py:90` calls existing `band_cut` on each occupied run. Row x-height supplies body scale. Three rows each below the old crop-owner fraction and skew/local-envelope fixtures pass at `tests/test_seg_cp3.py:35` and `tests/test_seg_cp3.py:45`. |
| a large envelope or top/bottom fragment cannot alone cause DROP | PASS for the specified controls | `greekocr/harvest/row_inclusion.py:94` requires zero local body-guide cut and visible assigned body extent; `greekocr/harvest/row_inclusion.py:102` requires a supporting run. Envelope-only, exact-half, 60%-visible, full-row-plus-edge-halves and rule controls pass at `tests/test_seg_cp3.py:64`, `:71`, `:83`, `:99`. This is geometric support, not lexical whole-word proof. |
| no OR with the unqualified old model | PASS | `greekocr/harvest/row_inclusion.py:113` decides only from structural counts; `greekocr/harvest/row_inclusion.py:122` computes that decision before attaching legacy diagnostics. The legacy-positive/single-row control at `tests/test_seg_cp3.py:106` passes. No collector deployment is claimed. |

## Acceptance numbers independently reproduced

I reran the tests and native measurement script with the mandated collector interpreter. The complete newly generated verifier JSON is **exactly equal** to the saved `CP3_verification.json`, including bindings, per-case runs, invalid-row disclosures and unavailable reasons. This equality is a comparison after execution, not reliance on the saved result.

| PLAN item 3 acceptance requirement (`ASTRA-SEG1_review_1.md:201`) | Reproduced result | Verdict |
|---|---|---|
| 22/22 keeps preserved by merged screen | 22 required, 22 measured, 22 preserved; 0 false drops, 0 unresolved | MET |
| 7/7 C1 merge witnesses detected | 7 required, 7 measured, 7 detected; 0 misses, 0 unresolved | MET |
| 6/6 pinned-gallery merge witnesses detected (report overlap) | 6 required, 6 measured, 6 detected; 0 misses, 0 unresolved | MET |
| 0 false positives in planted single-row/half-letter/column controls | 0/12 negative controls | MET |

The **five overlapping ids** are Gazette page `0020420cfe156a73--s000` suffixes `l0039`, `l0138`, `l0162`, `l0228`, plus `gazette_modern--5af16c5d518d2ebb--s000-l0128`. There are **8 distinct merge witnesses**, all detected. All six formerly unavailable Gazette witnesses (`l0039`, `l0138`, `l0141`, `l0146`, `l0162`, `l0228`) are measured. The original ledger and denominators are unchanged; required unknowns cannot enter success counts (`verify_cp3.py:100`).

The twelve negative controls are one row, split pieces, short heading, three half/60%-visible cases, full row plus edge halves, adjacent columns, two rule cases, empty-body envelope and legacy-positive diagnostics (`tests/test_seg_cp3.py:35`, `:52`, `:58`, `:64`, `:71`, `:77`, `:83`, `:99`, `:106`). All ran successfully; synthetic bars establish mechanics rather than semantic word truth. The native witness-membership test at `tests/test_seg_cp3.py:120` alone does not prove native detection; the separate verifier does.

**321 tests passed in 6.09s**, including **31 CP3 cases**. The original native verifier reports **0 detector/network calls**, **0 runtime write attempts**, **24 pre-existing preparation attempts**, **24 preparation receipts**, **9 unchanged protected artifacts**, **28,798 matching manifest PNGs**, **23/24 loaded pages**, and **0 publish actions**. No new preparation was run. `publish_actions=0` is a literal field, so the publication conclusion also rests on inspected execution paths and independently unchanged protected artifacts.

## Earlier B1 closure and CP3b diagnosis

**B1 CLOSED by option (a), row-level unavailability**, implemented at `greekocr/harvest/geometry_observations.py:134`. Only a nonpositive saved envelope is quarantined. The adapter preserves the raw record, curves and component ids, supplies `status=invalid_geometry`, a reason/minimum and conservative unavailable box, and reports `invalid_geometry_count` (`geometry_observations.py:146`, `:159`). Valid rows still pass unchanged vendor `prepare_row` (`:153`). Source/payload/code/label identity, structural address, native component presence, finite curve shapes and positive body guides retain strict checks (`:94`, `:113`, `:129`, `:134`, `:139`).

Crop intersection, explicit invalid target, and relevant rows' recorded neighbour dependencies return unavailable (`geometry_observations.py:164`, `:234`); neighbours resolve by structural detector line indices, not positions in the filtered row list. The merged consumer checks quarantine before counting and returns `merged=None` (`greekocr/harvest/row_inclusion.py:40`). New regressions at `tests/test_seg_cp3.py:154`, `:167`, `:183` pass for inverted/degenerate envelopes, remote valid crops, invalid target/crop/neighbour dependencies, and malformed curves/body/native ids. No invalid row is silently treated as clean or detected.

I reran `audit_cp3b_geometry.py`, redirecting its single hard-coded JSON output to `/tmp` without editing the script or its repository evidence. The result equals the saved audit **except for `completed_utc`**: **99 cache records** (75 live + 24 isolated), **9,975 row records**, **181 inverted rows on 10 pages**, **4 also containing zero-height columns**, **0 additional degenerate-only rows**, **0 nonpositive body-guide rows**; recorded tranche counts are **38 W1 / 61 W2**. This is the enumerated concurrent cache snapshot, not historical coverage of discarded caches.

For `row-00077`, the independent audit reproduces **52 component ids**, **2,784 assigned pixels**, bbox **[255,1405,1609,1492]**, **516/1,354 inverted columns**, minimum **−8.886999999999944 px at x=327**, and minimum baseline-minus-meanline **13.22199999999998 px**. Saved structural data identify detector line 77, reading order 72, piece 0; neighbours resolve above to rows 73/74/76 and below to 75/78/79. This is not Google crop `l0077`; overlapping feature labels do not establish one native text label. The audit reproduces all twelve labelled crop overlaps. The source's max-above/min-below seam aggregation (`greekocr/pages/lines.py:920` in the collector checkout) can explain crossed envelopes; the intermediate seams were not saved, so the receipt correctly labels that cause as inference.

The six required witnesses are remote from the quarantine envelope and have no recorded invalid-row dependency; all now have supported valid-row evidence. Geometry was neither repaired nor re-detected. The separate NLG page still rejects its inconsistent label/ink plane: independently recomputed **41,068 disagreement pixels**. That required DROP is outside the CP3 merge denominators and remains later-checkpoint work, not a verified KEEP.

I also independently counted **24 distinct source/path-hash preparation bindings**, **24 exclusive attempt markers**, **24 receipts**, and an archival `detector_s` sum of **122.84278629138134s** (122.843s rounded). These are preserved preparation records, not a new detector timing measurement. Guard verification binds all **120 preparation files**. The mutating `prepare_cp3_geometry.py` was inspected, not rerun.

## Existing segmenter reuse — F2/F3

**PASS within CP3 scope.** `geometry_observations.py:94` consumes receipt/source/options/code/payload-bound existing geometry; `:132` preserves native component identity; `:153` calls existing `ownership.prepare_row`. `row_inclusion.py:65` uses existing `box_hits`; `:90` uses collector `magnitude.band_cut`. Existing boundary/structure constants support occupied-body and rule filtering (`row_inclusion.py:11`, `:78`, `:87`, `:94`). This is an admission-policy composition over saved segmenter evidence; it adds no peak/row detector, curve fit, x-height estimator, token clustering, anonymous pairwise bridge, crop-height ownership threshold, masking or ownership retuning.

`observe_crop` shares row evidence before owner selection or ambiguous-owner return (`geometry_observations.py:225`, `:233`, `:239`), reproduced by `tests/test_seg_cp3.py:111`. Unknown geometry remains unavailable. The public boundary still refuses unqualified evidence (`geometry_observations.py:277`). Preparation calls only the existing collector `cache_page` into isolated `CP3_geometry`, with exclusive once-per-page markers (`prepare_cp3_geometry.py:23`, `:52`, `:55`). Frozen ownership identity `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8` and vendor/dependency hashes validate unchanged.

This closes CP3's relevant F2/F3 mechanics. It does not close CP4's word semantics, later orientation/union qualification, or the fresh blind gate. Reusing constants and passing targeted fixtures does not establish universal physical completeness.

## Protected bytes and read-only boundary

I independently compared current bytes to **HEAD blobs**, rather than only trusting `protected_before.json`:

- All **8 tracked protected entries** match HEAD and their frozen SHA256 values, covering both W1 admission JSONLs, decisions/receipt, crops manifest and census admission/receipt/report. The ninth protected entry, untracked `ADMISSION_CENSUS_20261017.json`, matches its frozen SHA but has no HEAD blob.
- The HEAD crops-manifest SHA is `dc3b1951687c951a1fe2b928810df8d62612ab2e582869da970a14d6690f2a9a`; current bytes match. Parsing that **HEAD manifest** and hashing the referenced files gives **28,798/28,798 PNG matches**. These checks cover crop bytes whose individual files are untracked.
- A broader HEAD comparison found **21 present admission/manifest-named JSON/JSONL files** and **1,573 present tracked PNGs**, all unchanged. Another **43 matching tracked paths** are absent and all have Git's skip-worktree flag; their absent current bytes cannot be compared, and they are not candidate deletions.

No admission, crops manifest or existing crop PNG change was established. New isolated detector `ink.png` evidence is not a modified admitted crop. Results are in `/tmp/seg-cp3-review2-protected.json`.

The exact-scope guard passes: **13 files**, exact HEAD, read-only dependencies and **120 prepared-evidence hashes**. Unrelated `.gitignore`, staging-tool and NW drafts are outside this review's guarded CP3 scope. This review wrote only this report within the repository; test/output artifacts were confined to `/tmp`, bytecode and pytest cache output were disabled. No staging, commit, publication, OCR/reading, network, live-root lock or detector preparation was performed.

## Reproduction commands and limits

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp3-review2-pytest tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/verify_cp3.py > /tmp/seg-cp3-review2-verification.json
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/guard_cp3_commit.py
ps -axo pid,lstart,command
```

For the audit rerun, the same Python executed `runpy.run_path('docs/records/harvest/collect_v3_admission/seg/audit_cp3b_geometry.py', run_name='__main__')` with `Path.write_text` wrapped to assert the sole destination was `seg/CP3b_geometry_audit.json` and redirect it to `/tmp/seg-cp3-review2-geometry.json`. The source script's write is at `audit_cp3b_geometry.py:44`; its numerical computation was unchanged. The process command failed as reported above; no escalation was attempted. Tests are the specified regression set, not a full-suite, speed, semantic reading or deployment qualification.

SEG-CP3 review: FAIL | blocking: 0 | high: 0 | acceptance: 4/4 met reproduced | publish actions: 0
