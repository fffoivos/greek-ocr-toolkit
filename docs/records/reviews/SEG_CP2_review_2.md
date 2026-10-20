# SEG-CP2 Sol code review 2 — including CP2b

2026-10-18. **PASS for CP2 infrastructure; H1 closed.** Reviewed against ASTRA-SEG1 §“Numbered PLAN”, item 2 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:191`), including both build/fix briefs and the complete earlier review. HEAD: `b921b8284d91f672fc2a2affff57529a664db3af`. The guarded commit list independently passes: 14 exact files, unchanged base HEAD, and matching file/dependency hashes. Reviewed the complete admission, geometry and neighbour modules, tests, measurement script and guard; unrelated pre-existing staging changes remain outside this checkpoint.

Only this report was written inside the repository. Test fixtures and independent reproduction artifacts are under `/tmp/seg-cp2-review2-*`. No publication, staging, commit, detector preparation, reader, recognizer, network or paid operation was performed. This checkpoint does not qualify the segmentation policy or authorize publication.

## Findings by severity

- **Blocking:** none.
- **High:** none open.
- **Medium:** none.
- **Low:** none.

### Earlier H1 — CLOSED

The earlier review's three exact mappings—missing qualification/status, explicitly stale with a wrong source hash, and explicitly unresolved—now each return **`passed=False`, `status='unresolved'`, `geometry_status='unavailable'`, `failed_rules=[]`**. I reran them directly as well as their regressions. Evidence: `greekocr/harvest/geometry_observations.py:213`, `greekocr/harvest/admission.py:558`, `tests/test_seg_cp2.py:203`, `tests/test_seg_cp2.py:217`.

The public admission boundary no longer imports or calls `runs()`: `greekocr/harvest/admission.py:560` sets the neighbour check to `n/a`, and `:570` prevents every unqualified CP2 result from becoming a verified keep. `rules_passed` preserves the separate text/rule result. Positive caller tags require full record/source/crop/target binding, reloading current cache/code/payload identities and reproducing the observation (`greekocr/harvest/geometry_observations.py:219`, `:225`, `:232`, `:235`). Even a valid observation with a forged qualification tag remains unresolved because CP2 has no qualified predicate (`:241`). This is appropriate fail-closed checkpoint behavior, not completed CP3/CP4 qualification.

The native-pixel **12 bodies at 6/10 visibility** regression still activates the historical diagnostic, while admission returns no neighbour DROP and no verified KEEP (`tests/test_neighbour_words.py:23`, `:34`, `:39`). The mechanical defect is retained visibly for later work, without an admission fallback. Regression spies also prohibit `runs()` at the boundary (`tests/test_seg_cp2.py:217`, `:280`). The five-row receipt integration reproduces **5 abstentions, 3 unavailable, 2 unresolved, 0 admitted**, with all five reasons counted (`tests/test_seg_cp2.py:292`; accounting at `greekocr/harvest/admission.py:699`). The earlier review listed no other independent blocking, medium or low findings.

## Sol code-review criteria — verbatim, one by one

Exact plan text (`ASTRA-SEG1_review_1.md:194`):

> no paint/fill call, no partial detector identity, no “missing neighbour = clean”, no basename-only identity, no silent matched/no-match tie-break. Preserve native component ids and neighbour-row x-heights.

| Criterion, verbatim | Verdict | File:line and independently checked evidence |
|---|---|---|
| no paint/fill call | PASS | `greekocr/harvest/geometry_observations.py:143`, `:152`, `:154` invoke only preparation, saved-curve conversion and the existing foreign-mask core. No paint/fill/ring path. Raster/labels remain identical and fills empty in `tests/test_seg_cp2.py:122`. |
| no partial detector identity | PASS | `greekocr/harvest/geometry_observations.py:30`, `:52`, `:85`: the complete existing collector pages/glyphs identity algorithm is reproduced, checked against the receipt, and supplemented with runtime geometry, adapter/admission/vendor identities and current dependency versions. Equality with vendor identity and changed-code rejection pass at `tests/test_seg_cp2.py:148`, `:156`. Historical producer dependency versions are absent from the existing cache format; current consumer versions are recorded without claiming historical provenance. |
| no “missing neighbour = clean” | PASS | `greekocr/harvest/geometry_observations.py:149` returns unavailable; `:185` propagates it. The boundary abstains at `greekocr/harvest/admission.py:558`, `:570`. Missing-neighbour and legacy/unavailable regression cases pass at `tests/test_seg_cp2.py:134`, `:177`, `:217`. H1 no longer bypasses this contract. |
| no basename-only identity | PASS | `greekocr/harvest/geometry_observations.py:82`, `:85` require resolved source path and exact source bytes/SHA. Boundary record/source/page/crop/target checks are at `:225`. Same-basename/different-path, changed bytes and cross-record binding cases pass at `tests/test_seg_cp2.py:82`, `:162`, `:256`. |
| no silent matched/no-match tie-break. | PASS | `greekocr/harvest/geometry_observations.py:169` collects all row-owned pixel hits before selection; `:175` requires exactly one supported row without an explicit structural target; `:179` rejects absent/duplicate explicit targets. Ambiguous and missing targets remain explicit at `tests/test_seg_cp2.py:108`. No nearest-centre matcher survives in the cache-consumption path. |
| Preserve native component ids and neighbour-row x-heights. | PASS | `greekocr/harvest/geometry_observations.py:123`, `:169`, `:191`, `:195` retain detector component ids, structural row ids, native foreign ids and each neighbour's own saved x-height. The fixture reproduces native foreign ids `[1, 3]` and neighbour heights `[10, 10]` (`tests/test_seg_cp2.py:108`). The implementation copies each neighbour's value directly rather than substituting the target height. |

## Independent acceptance reproduction

The denominator is the four explicit CP2 numerical requirements plus its conditional fallback limit: **5/5 met**. Values below come from this review's reruns, not the receipt or saved verification JSON.

| Plan requirement (`ASTRA-SEG1_review_1.md:195`) | Reproduced value and evidence | Verdict |
|---|---|---|
| 0 detector calls with recorded geometry | **0** in the native probe; cached measurement/admission also completes with `process_page` patched to raise (`tests/test_seg_cp2.py:58`). Admission correctly completes unresolved. | MET |
| 0 live-run/repository writes | Native measurement audit: **0 write attempts**, including write-open/mutation rejection (`docs/records/harvest/collect_v3_admission/seg/verify_cp2.py:37`). Cache fixture forbids writes and checks input hashes (`tests/test_seg_cp2.py:64`). Live-root inventory around the probe: **31,133 → 31,133 files; 0 added, 0 removed, 0 changed size/mtime/inode tuples**. Fixtures and review evidence use `/tmp`; this authorized report is separate. | MET for reviewed execution |
| 100% identical masks for equivalent frozen inputs | **11/11 = 100%**: **8/8 native** comparisons against the original core plus **3/3 planted** comparisons. Independent planted rerun yields **160, 40, 120** foreign pixels. Raster and label immutability checks pass (`tests/test_seg_cp2.py:122`; `seg/verify_cp2.py:87`). | MET |
| 0 unavailable checks reported as verified keeps | **0/7** native-probe boundary challenges, **0/3** exact earlier H1 inputs. Additional stale/unknown/legacy/forged/cross-crop/source/code/payload cases pass; five-row integration admits **0/5** (`tests/test_seg_cp2.py:217`, `:229`, `:238`, `:256`, `:280`, `:292`). | MET |
| Fallback preparation, if needed later, at most once per source-bound page and explicitly counted | **0 preparations, 0/page**. No fallback implementation is invoked. Missing-cache test abstains and creates no receipt (`tests/test_seg_cp2.py:169`; `greekocr/harvest/neighbour_words.py:91`). | MET; optional path unused |

The native control is `ia_poly1850--3773a91327e98bc0--s000`, metadata status **excluded**, with eight row comparisons. All eight native foreign masks contain **zero** foreign pixels. Nonempty equivalence is therefore established by planted controls, not native contaminated witnesses. Calibration/C1 cache coverage independently remains **0/24 pages**. These are infrastructure limits, not evidence of native whole-word truth, recovered witness coverage or later-checkpoint acceptance. No missing geometry was regenerated.

### Commands and results

Required collector interpreter, bytecode disabled, no pytest cache, temporary fixtures only:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp2-review2-tests tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
# 290 passed in 6.91s

PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/verify_cp2.py
# Exit 0; stdout independently captured at /tmp/seg-cp2-review2-verification.json

PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/guard_cp2_commit.py
# PASS; 14 exact files; HEAD b921b8284d91f672fc2a2affff57529a664db3af

git diff --check
# Exit 0
```

I additionally reconstructed the three planted masks directly and reran all three H1 inputs outside pytest. The CP1 tests rebuild the current historical union report and retain **4/22 KEEP losses**, GATE_FAIL and the stale saved-report guard (`tests/test_seg_cp1.py:59`, `:63`, `:79`; `tests/test_seg_cp2.py:194`). They do not rewrite calibration or publish. Passing CP2 therefore leaves publication blocked.

## Protected artifacts and live-root evidence

Independent SHA-256 comparisons against **HEAD bytes** found:

- All **8 HEAD-tracked** files in the nine-entry protection ledger match HEAD, including admission rows, admitted rows, decisions, receipts and `crops_manifest.jsonl`. All **9/9** match the committed CP1 protection ledger. The ninth, untracked `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.json`, has no HEAD object and is checked against that ledger only.
- All **28,798/28,798 PNGs** referenced by HEAD's crops manifest exist and match its SHA-256 values: **0 missing, 0 mismatches**. Manifest paths resolve relative to `docs/records/harvest/collect_v3_admission`. These staged PNGs are individually untracked; their HEAD baseline is the byte-identical tracked manifest.
- A broader scan compared **1,596 present tracked** PNG/admission-JSON/manifest paths with their HEAD blob hashes: **0 differences**. Another **24** selected paths are absent and all carry Git's sparse-checkout `S` flag.
- The native probe rehashes its source/cache inputs and checks source pixels/labels unchanged (`seg/verify_cp2.py:79`, `:93`). The live-root inventory delta is zero as reported above. The reviewed measurement code has no live-root write/lock path and the audit records no write attempt. This verifies this review's execution; it cannot retrospectively attribute filesystem operations by earlier or unrelated processes.

The compact protection results are retained in `/tmp/seg-cp2-review2-protected.json` and `/tmp/seg-cp2-review2-pngs.json`; live inventory/delta and planted-mask results are separate temporary JSON artifacts. No protected file was changed by this review.

## Existing-tool reuse and F2/F3 scope

The adapter consumes the existing `geometry.io.cache_page` payload/receipt format through its read-only loader (`greekocr/harvest/geometry_observations.py:75`), invokes the collector's actual `ownership.prepare_row()` and `box_hits()` (`:126`, `:171`), and retains saved curves and structural addresses (`:109`, `:115`, `:120`). It does not call the producer's cache-miss branch. `page_measurements()` reads metadata/cache only (`greekocr/harvest/neighbour_words.py:91`); the former unconditional re-detection and geometric nearest-centre matching are removed from that path.

The shared measurement entrypoint calls existing `foreign_ink.prepare_mask_page/_centre_fit/_foreign_mask` (`greekocr/harvest/geometry_observations.py:136`). `greekocr/glyphs/foreign_ink.py` is byte-identical to HEAD; the independently recalculated parameter digest remains **`801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`**. There is no new detector, ownership retuning, painting or new qualified heuristic.

F2's clipped-component graph remains explicitly historical (`greekocr/harvest/neighbour_words.py:35`, `:56`), used by frozen calibration diagnostics. It is unreachable as an admission decision after CP2b. Its semantic replacement belongs to CP4; row inclusion belongs to CP3. F3's recorded-geometry/provenance/ambiguity/unavailable issues are addressed within CP2, with the disclosed producer-provenance and native-coverage limits. No claim is made that the original combined segmentation gate, CP3–CP8, or the overall Astra program is now qualified.

SEG-CP2 review: PASS | blocking: 0 | high: 0 | acceptance: 5/5 met reproduced | publish actions: 0
