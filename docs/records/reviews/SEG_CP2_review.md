# SEG-CP2 Sol code review

2026-10-18. **FAIL — one high finding.** Reviewed uncommitted CP2 against ASTRA-SEG1 numbered plan item 2 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:191`). HEAD: `aa49dbb4993e7018c52cdb54f39722712e876118`. Scope is the 14 files in `docs/records/harvest/collect_v3_admission/seg/CP2_COMMIT_LIST.json`, including the complete admission/neighbour drafts. The list's guard independently passed all file/dependency hashes and base HEAD. Unrelated staging drafts were inspected for scope, not modified. Only this report was written inside the repository; reproduction outputs and test fixtures are under `/tmp`.

## Findings by severity

### Blocking

None.

### High

**H1 — The admission boundary still trusts unqualified legacy measurements, admitting unavailable evidence and activating the F2 heuristic.** `greekocr/harvest/admission.py:560` checks a blacklist of two unavailable statuses and one CP2 decision tag. It requires neither a positive qualification state nor a valid source/code/geometry binding. Consequently each of these independently reproduced inputs returns `passed=True`, `status="pass"`, `geometry_status="available"`, and no failed rules for the otherwise eligible Greek record below:

```python
record = dict(label='ἑλληνικὸς πλήρης λόγος',
              source='bsb_poly1850', primary_class='poly1850')
measurements = [
    dict(matched=True, xheight=10., components=[]),
    dict(matched=True, xheight=10., components=[], status='stale',
         binding={'source_sha256': 'wrong'}),
    dict(matched=True, xheight=10., components=[],
         decision_status='unresolved'),
]
# evaluate(record, neighbour_measurement=m) passes all three.
```

The same branch calls `runs()` as an admission predicate (`greekocr/harvest/admission.py:567`). Its anonymous component graph, target-row normalization and half-height rule remain at `greekocr/harvest/neighbour_words.py:39`, `:48`, `:61`, and `:83`. A separate native-pixel planted reproduction with twelve neighbour bodies, each only **6/10 pixels visible**, returned `failed_rules=['neighbour_words']`, `status='fail'`. These rectangles demonstrate the F2 completeness defect, not semantic word truth. Thus the statement that the legacy proxy is only a historical diagnostic (`docs/records/harvest/collect_v3_admission/seg/CP2_RECEIPT.md:23`) is false for the public `evaluate()` API. Existing tests explicitly exercise this legacy admission branch (`tests/test_neighbour_words.py:38`).

The normal new `measure_rows()` path does carry `decision_status='unqualified_cp2'` and abstains, so this is a boundary bypass, not a claim that current cache observations automatically publish. Require affirmative, provenance-bound qualification before a measurement can affect admission; keep legacy `runs()` results diagnostic during CP2. Unknown, stale, missing-status and unresolved evidence must abstain. Add regression coverage for the three cases above. This fails CP2's zero-unavailable-verified-keeps acceptance requirement and leaves F2 reachable through admission.

### Medium

None independently of H1.

### Low

None.

## Sol code-review criteria, verbatim and individually assessed

The exact criteria at `ASTRA-SEG1_review_1.md:194` are:

> no paint/fill call, no partial detector identity, no “missing neighbour = clean”, no basename-only identity, no silent matched/no-match tie-break. Preserve native component ids and neighbour-row x-heights.

| Criterion (verbatim clause) | Verdict | File:line and evidence |
|---|---|---|
| no paint/fill call | PASS | `greekocr/harvest/geometry_observations.py:141`, `:152`: calls existing preparation and foreign-mask measurement only; no painting/ring/fill path. Input immutability and empty fills pass at `tests/test_seg_cp2.py:122`. |
| no partial detector identity | PASS | `greekocr/harvest/geometry_observations.py:29`, `:51`, `:86`: complete collector pages/glyphs identity matches the vendor algorithm; runtime geometry, adapter/admission/vendor hashes and consumer dependency versions are recorded. Identity-change rejection and vendor identity equality pass at `tests/test_seg_cp2.py:148`, `:156`. The producer format lacks historical dependency versions; the adapter does not claim to recover them. |
| no “missing neighbour = clean” | FAIL at admission boundary; PASS in CP2 adapter | `greekocr/harvest/geometry_observations.py:147` correctly returns unavailable for no neighbours; `tests/test_seg_cp2.py:177` passes. However absent neighbour/qualification provenance in the legacy mapping is sufficient for a verified keep at `greekocr/harvest/admission.py:560` (H1). |
| no basename-only identity | PASS | `greekocr/harvest/geometry_observations.py:81`, `:85`: resolved source path and source bytes must match the receipt and supplied SHA. Same-basename/different-path and changed-source rejection pass at `tests/test_seg_cp2.py:82`, `:162`. |
| no silent matched/no-match tie-break | PASS | `greekocr/harvest/geometry_observations.py:167`, `:173`, `:177`: collects row-owned pixel hits first, requires one supported row without an explicit target, and rejects absent/duplicate explicit targets. Ambiguity/stability tests pass at `tests/test_seg_cp2.py:108`. |
| Preserve native component ids | PASS for adapter | `greekocr/harvest/geometry_observations.py:122`, `:168`, `:189`, `:195`: retains detector component identities, row assignments and native foreign ids. Planted foreign ids are exactly `[1, 3]` at `tests/test_seg_cp2.py:115`. The legacy heuristic's clipped relabeling remains reachable only through the H1 bypass. |
| neighbour-row x-heights. | PASS for adapter | `greekocr/harvest/geometry_observations.py:193`: retains each neighbour's own saved x-height, rather than rewriting it as the target's height; tested at `tests/test_seg_cp2.py:116`. Legacy normalization at `greekocr/harvest/neighbour_words.py:48` is not a qualified replacement (H1). |

## Independent acceptance reproduction

Count: the four explicit numerical requirements plus the conditional fallback limit, matching the receipt's five-item denominator. **4/5 met.** All recorded results below were rerun, not copied from the receipt.

| CP2 requirement (`ASTRA-SEG1_review_1.md:195`) | Independently measured | Verdict |
|---|---|---|
| 0 detector calls with recorded geometry | **0** in native probe; raising-spy cached measurement/admission fixture also passes (`tests/test_seg_cp2.py:58`). The admission computation completes unresolved because CP2 is unqualified. | MET |
| 0 live-run/repository writes | Native probe reports **0 write attempts**, with mutation/open auditing (`seg/verify_cp2.py:37`); cached fixture forbids writes. Live-root inventory before/after: **31,133 → 31,133 files; 0 changed size/mtime/inode tuples, 0 added, 0 removed**. Fixtures and stdout artifacts were confined to `/tmp`; this authorized report is separate. | MET for reviewed execution |
| 100% identical masks for equivalent frozen inputs | **11/11 = 100%**: eight native comparisons plus three planted comparisons. Planted foreign pixel counts independently reproduced as **160, 40, 120**. | MET |
| 0 unavailable checks reported as verified keeps | Supplied native probe: **0/3**; six parameterized unavailable cases also pass. Independent boundary challenges: **3/3 incorrectly verified keeps**, including explicitly stale and unresolved measurements (H1). | NOT MET |
| Fallback preparation, if needed later, at most once per source-bound page and explicitly counted | **0 preparations, 0/page**. Missing-cache test abstains; no detector/cache-miss preparation implementation is invoked (`greekocr/harvest/neighbour_words.py:90`; `tests/test_seg_cp2.py:169`). | MET; conditional path unused |

Reproduction commands used the required byte-exact collector interpreter, bytecode disabled, no pytest cache:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp2-sol-review-tests tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
# 237 passed in 6.16s

PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/verify_cp2.py > /tmp/seg-cp2-sol-review-verification.json

PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/guard_cp2_commit.py
# PASS; 14 exact files; original HEAD; no staging/commit/publication
```

The native probe selected `ia_poly1850--3773a91327e98bc0--s000`, status `excluded`; all eight masks had **zero foreign pixels**. Nonempty mask equivalence is supported by the three planted cases, not by those native controls. Calibration/C1 geometry availability independently reproduced as **0/24 pages**. This is CP2 infrastructure evidence, not recovered native calibration coverage or CP3/CP4 qualification. The passing suite also independently rebuilds CP1's report and retains **4/22 KEEP losses**, a failing union and a stale saved-report guard (`tests/test_neighbour_words.py:82`; `tests/test_seg_cp1.py`).

## Protected artifacts, live-root writes and reuse

SHA-256 comparisons against **HEAD bytes**, rather than only Git status, found:

- All **eight HEAD-tracked** files in CP1's nine-entry protection ledger unchanged, including admitted rows, admission/decision outputs, admission receipts and `crops_manifest.jsonl`. The ninth file, `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.json`, is untracked and therefore has no HEAD baseline; its hash matches the committed CP1 protection ledger. All nine match that ledger.
- Every one of the **28,798 PNGs** referenced by HEAD's crops manifest exists and matches its recorded SHA-256: **0 missing, 0 mismatches**. These staged PNGs are not individually tracked; HEAD's byte-identical manifest supplies their baseline.
- A broader repository scan checked **1,579 present tracked** admission-JSON/manifest/PNG paths against HEAD: **0 byte differences**. Another **24** paths are absent with Git's sparse-checkout `S` flag; these are sparse exclusions, not crop/admission modifications.
- The review's live-root file inventory is unchanged as detailed above; the native probe additionally confirms source/cache payload SHA stability. No live-root write or lock was performed by this review. These observations verify this execution, not an unavailable historical filesystem audit of all prior processes.

The adapter genuinely reuses the collector's `ownership.prepare_row()` and `box_hits()` (`greekocr/harvest/geometry_observations.py:125`, `:169`), saved curves and structural ids (`:108`, `:119`, `:124`), and unchanged `foreign_ink.prepare_mask_page/_centre_fit/_foreign_mask` (`:141`, `:150`, `:152`). Complete code identities are compared or recorded; the frozen parameter digest remains `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. No new detector, ownership retuning or paint path was found. F3's unconditional page re-detection and nearest-centre matcher are removed from the new path. F2's heuristic remains reachable as an admission decision through H1, so tool reuse is substantial but insufficient to pass the checkpoint as submitted. CP3–CP8 are outside this review; publication remains blocked.

SEG-CP2 review: FAIL | blocking: 0 | high: 1 | acceptance: 4/5 met reproduced | publish actions: 0
