# SEG-CP3 Sol code review

2026-10-18. Reviewed uncommitted CP3 at HEAD `89e0a59d7c9fc4c47a193b7e657def8ca3ad0dcc`, against ASTRA-SEG1 numbered PLAN item 3 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:197`). Verdict: **FAIL; retain GATE_FAIL and do not publish.** The candidate meets two of four acceptance requirements. The receipt accurately discloses that failure; passing unit tests does not close it.

## Findings by severity

### Blocking — B1: required native merge coverage is incomplete

**Locations:** `docs/records/harvest/collect_v3_admission/seg/verify_cp3.py:70`, `greekocr/harvest/geometry_observations.py:135`, `docs/records/harvest/collect_v3_admission/seg/CP3_verification.json:33`, `docs/records/harvest/collect_v3_admission/seg/CP3_verification.json:46`.

The independent measurement detects only **2/7 C1** and **1/6 gallery** witnesses. Each denominator has five unresolved cases. All six distinct unresolved merge witnesses belong to `gazette_modern--0020420cfe156a73--s000`: `l0039`, `l0138`, `l0141`, `l0146`, `l0162`, `l0228`. Thus all three exact former C1 misses and the specifically required gallery `l0146` remain unverified. The affected page cannot load because the saved `row-00077` has minimum `bottom-top = -8.886999999999944 px`; the unchanged vendor `prepare_row()` rejects it. This is an adapter/evidence coverage failure, not proof that those six crops are clean or that the predicate missed a measured case.

Resolve the geometry-contract failure in separately reviewable work and rerun the original denominators. Do not remove the invalid row silently, exclude the witnesses, weaken validation for this page, or count unavailable observations as KEEP/detected. The implementation already preserves unknowns and returns a failing gate (`verify_cp3.py:97`, `verify_cp3.py:125`), which is correct containment, but CP3 remains unaccepted.

### High

No additional high findings established in this CP3 diff.

### Medium — M1: the unconditional live-root no-write assurance is not established

**Locations:** `docs/records/harvest/collect_v3_admission/seg/CP3_RECEIPT.md:42`, `docs/records/harvest/collect_v3_admission/seg/verify_cp3.py:28`, `docs/records/harvest/collect_v3_admission/seg/verify_cp3.py:117`.

The verifier's zero write-attempt result describes its guarded Python execution; it is not a historical audit of every process or the entire live tree. Independent before/after metadata inventories of **31,403 live-root entries**, surrounding another verifier run, found changes to `W2/crops` and `cache/g1b`. A second run reproduced those two directory changes, with no lasting file-entry changes. On that second check their `(mtime_ns, ctime_ns)` changed respectively from `(1792279322522929645, 1792279322522929645)` to `(1792279340131814584, 1792279340131814584)`, and from `(1792279322523194289, 1792279322523194289)` to `(1792279340132117302, 1792279340132117302)`.

The verifier still reported **0 runtime write attempts**, and its inspected code does not write those directories. These observations do **not** attribute the changes to CP3; external activity or filesystem behavior remains unresolved. They do prevent this review from confirming the broader statement that nothing wrote to the live root. Narrow the receipt assurance to what was observed, or provide execution-wide evidence explaining the directory changes. No historical all-process no-write claim is made here.

### Low

No low findings established.

## Sol code-review criteria, verbatim and individually assessed

The four criteria below reproduce the wording of `ASTRA-SEG1_review_1.md:200` exactly. PASS here concerns the inspected mechanics and reproduced fixtures, not native acceptance or universal physical completeness.

| Criterion | Verdict | Evidence |
|---|---|---|
| count physical structural rows, not delivery pieces | PASS | `greekocr/harvest/row_inclusion.py:47` checks structural identities; `row_inclusion.py:101` inserts row ids into sets per page side/column. `tests/test_seg_cp3.py:52` reproduces two delivery pieces counting once. |
| use row-relative/local occupied overlap, not crop-height overlap | PASS | `greekocr/harvest/row_inclusion.py:60` uses existing `box_hits()`; `row_inclusion.py:80` restricts assigned body columns to the crop's horizontal interval; `row_inclusion.py:85` calls existing `band_cut()` on each occupied run. `tests/test_seg_cp3.py:35` and `tests/test_seg_cp3.py:45` pass the three-row/old-fraction and skew/local-envelope cases. |
| a large envelope or top/bottom fragment cannot alone cause DROP | PASS for the specified controls | `greekocr/harvest/row_inclusion.py:89` requires zero local body-band cut plus assigned visible body extent; `row_inclusion.py:97` requires at least one supporting run. Envelope-only, exact-half, 60%-visible and full-row-plus-edge-half cases pass at `tests/test_seg_cp3.py:64`, `tests/test_seg_cp3.py:71`, `tests/test_seg_cp3.py:99`. These synthetic checks establish the requested mechanics, not lexical whole-word truth. |
| no OR with the unqualified old model | PASS | The only candidate decision is the structural count at `greekocr/harvest/row_inclusion.py:107`. Old features are attached after that decision at `row_inclusion.py:117`. The old-positive/single-row test passes at `tests/test_seg_cp3.py:106`. No collector deployment or production-policy replacement is claimed. |

## Reproduced acceptance numbers

I executed the checkpoint's measurement script rather than reading its saved result. Its parsed output is **exactly equal** to the saved `CP3_verification.json`, including per-case measurements, bindings and unavailable reasons. Further audited reruns preserved the same acceptance counts.

| CP3 acceptance requirement (`ASTRA-SEG1_review_1.md:201`) | Independently reproduced | Verdict |
|---|---|---|
| 22/22 keeps preserved by merged screen | 22 required, 22 measured, 22 preserved; 0 false drops, 0 unresolved | MET |
| 7/7 C1 merge witnesses detected | 7 required, 2 measured/detected, 5 unresolved, 0 measured failures | NOT MET |
| 6/6 pinned-gallery merge witnesses detected (report overlap) | 6 required, 1 measured/detected, 5 unresolved, 0 measured failures | NOT MET |
| 0 false positives in planted single-row/half-letter/column controls | 0/12 negative controls | MET |

The **five overlapping ids** are Gazette page `0020420cfe156a73--s000` suffixes `l0039`, `l0138`, `l0162`, `l0228`, plus `gazette_modern--5af16c5d518d2ebb--s000-l0128`. There are **8 distinct merge witnesses**, **2 distinct detections**, and **6 distinct unresolved witnesses**. C1 detects `gazette_modern--5af16c5d518d2ebb--s000-l0128` and `gazette_modern--2e613d9290dd13d4--s000-l0209`; the gallery detects the former. Unknowns stay in the required denominators.

The twelve negative controls are the one-row case, split pieces, short heading, three half/60%-visible cases, full row plus edge halves, adjacent columns, two rule cases, empty-body envelope, and old-positive diagnostic case (`tests/test_seg_cp3.py:35`, `:52`, `:58`, `:64`, `:71`, `:77`, `:83`, `:99`, `:106`). All were executed. The other CP3 cases exercise two/three rows, skew, shared pre-owner evidence, witness identities and guard failures. In particular, `tests/test_seg_cp3.py:120` checks native witness membership; native detection results come from the separate measurement script, not that membership test.

## Commands and additional verification

Used the byte-exact collector interpreter, disabled bytecode/cache output, and confined test artifacts and independent measurement stdout to `/tmp`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp3-review-pytest tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/verify_cp3.py > /tmp/seg-cp3-review-verification.json
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/guard_cp3_commit.py
```

- **309 passed in 6.12s**, including **19 CP3 cases**. No full-suite or performance qualification is inferred.
- Guard **PASS**: exact HEAD, **10 scoped files**, dependency hashes and **120 prepared-evidence hashes** verified. The unrelated `.gitignore`, staging-tool and NW drafts remain outside CP3 scope.
- Native measurement: **0 detector/network calls**, **0 runtime write attempts**, **0 new preparations**, **0 publish actions**. The `publish_actions` output is a literal field, so the publication conclusion also rests on inspected execution paths and unchanged publication artifacts, not that field alone.
- Independently counted **0/24** live receipt-bound witness caches, **24** local exclusive attempt markers, **24** distinct source/path-hash bindings and **24** produced local receipts. **22/24** pages load through CP2. In addition to B1, the NLG page fails label/ink consistency: independently recomputed **41,068** disagreeing pixels. That required DROP is outside CP3's merge denominators (`geometry_observations.py:113`, `CP3_verification.json:1374`).
- Summing the stored preparation receipts' `detector_s` gives **122.84278629138134s**, rounded **122.843s**. This is an archival timing sum, not a new detector timing measurement. `prepare_cp3_geometry.py` is a mutating preparation stage, not a measurement script; I inspected it and its bound outputs but did not rerun detection or rewrite its evidence under this read-only review.

## Segmenter reuse and F2/F3

**PASS within CP3 scope.** `geometry_observations.load_cached_page()` consumes existing source/frame/options/code/payload-bound detector records (`geometry_observations.py:90`), preserves structural/native component identities (`:118`, `:125`), and calls the existing `prepare_row()` (`:135`). The candidate calls existing `box_hits()` and collector `magnitude.band_cut()` (`row_inclusion.py:60`, `:85`), using each row's own x-height. It introduces no peak detector, curve fitting, token clustering, all-pairs fragment bridge, crop-height owner fraction, ownership retuning or masking.

The occupied-run and rule/body-support composition at `row_inclusion.py:64` uses existing boundary/table constants; it is candidate admission policy, not an independently qualified word detector. Reusing those constants does not itself establish full words or resolve the missing native evidence. The code and receipt correctly avoid that claim. CP4's letter/word semantics remain deferred.

Shared row evidence is computed **before** ambiguous-owner return and attached to the neighbour observation (`geometry_observations.py:177`, `:185`, `:188`), reproduced by `tests/test_seg_cp3.py:111`. Unknown geometry is reported unavailable, and the existing admission boundary rejects unqualified observations (`geometry_observations.py:225`, `:229`). Optional preparation calls only the existing collector `cache_page()` with an isolated output path and exclusive attempt markers (`prepare_cp3_geometry.py:23`, `:52`, `:55`). The collector vendor hashes and frozen ownership identity `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8` validate unchanged.

## Protected artifacts and write boundary

**Admission files, crops manifest and crop PNGs: unchanged against HEAD.** I independently hashed the current bytes against `git show HEAD:<path>` for all eight tracked entries in `seg/protected_before.json`, including both W1 admission JSONLs, W1 decisions/receipt, the crops manifest, and census admission JSONL/receipt/report. All match. The ninth protected entry, `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.json`, is a pre-existing untracked census summary: its SHA matches the frozen baseline, but it has no HEAD blob and is not described as HEAD-verified.

The crops manifest SHA is `dc3b1951687c951a1fe2b928810df8d62612ab2e582869da970a14d6690f2a9a`, equal to HEAD. Independently parsing the **HEAD manifest** and hashing every referenced PNG gives **28,798/28,798 matches**. This covers materialized crop PNGs even where Git does not track their individual bytes. The preparation `ink.png` files are new isolated detector evidence, not changed crop PNGs.

An additional repository-wide HEAD-blob comparison found **9 present admission/manifest-named JSON/JSONL files** and **1,573 present tracked PNGs** unchanged. Another **26 admission/manifest files and 8 PNGs** are absent with Git's skip-worktree flag in this sparse checkout; these are not CP3 deletions, and no current-byte comparison is claimed for absent files.

**Live root:** the inspected verifier and preparation guards support process-local read-only measurement and isolated preparation. Full live-root historical immutability cannot be confirmed; see M1's independently observed directory metadata changes. No CP3-attributable live-root write was established. No code, admission, manifest, PNG, cache, lock or Git state was intentionally modified by this review; the only repository output is this review document.

SEG-CP3 review: FAIL | blocking: 1 | high: 0 | acceptance: 2/4 met reproduced | publish actions: 0
