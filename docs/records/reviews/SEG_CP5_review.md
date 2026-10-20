# SEG-CP5 independent code review

Reviewed 18 October 2026 against ASTRA-SEG1 numbered PLAN item 5, including F2/F3 and the CP4c rulings. Base HEAD: `132b363648469ff4b6f13b9078f820189a6c4706`. Scope: the 11 files in `seg/CP5_COMMIT_LIST.json`, that manifest, and the CP4c rule/ledger additions committed in `81e7756c`. **FAIL: 1/4 acceptance requirements reproduced as met.** The receipt accurately reports the qualification failure. Passing contract tests does not close it.

## Findings by severity

### Blocking — 0

No additional blocking implementation finding. The qualification failures below still prevent progressing past CP5 or publishing the candidate. Public admission remains unqualified (`greekocr/harvest/admission.py:595`); the verifier retains `gate=False` (`docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:164`).

### High — 3

**H1 — Two of four adjudicated rotated witnesses are not caught.** `greekocr/harvest/orientation_screen.py:55`, `greekocr/harvest/orientation_screen.py:63`; acceptance counter at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:148`.

Fresh native measurements classify `gazette_modern--b9f59878fb904d91--s000-l0034` as horizontal and `gazette_modern--ebdc4d07ff8c4122--s000-l0265` as unknown. Only `gazette_modern--8213d28643843855--s000-l0144` and `gazette_modern--83c3182a4175392a--s000-l0259` are caught. Axis coverage is 3/4, but end-to-end catches are **2/4**, not 3/3 or 100%. Unknown polarity is correctly allowed for the two vertical results; it does not explain away the misses. Retain failure until the required native positives are resolved through the authorized toolkit path or separately adjudicated with authority; do not grandfather historical ids.

**H2 — The orientation exclusion loses an owner KEEP and upright controls.** `greekocr/harvest/orientation_screen.py:63`, `tests/test_seg_cp5.py:132`; inherited extent override at `greekocr/glyphs/orientation.py:195`.

The fresh block-context result excludes owner KEEP `gazette_modern--0d0b2233a81e355c--s000-l0019`: **1/22 KEEP false drops**. Compact upright `ΟΙ` and `12` are each falsely vertical in both line and block contexts: **4/11 upright decisions false drops**, plus one upright abstention. The sideways short controls also expose inverse mistakes. The tests intentionally assert the known wrong result at `tests/test_seg_cp5.py:136`; their success is evidence that the limitation remains reproducible, not that these controls satisfy acceptance. In line context the existing tight-ink aspect override can directly determine the final axis; toolkit reuse alone does not qualify that heuristic. Keep this path unqualified until zero-loss controls and the owner KEEP denominator pass.

**H3 — Native horizontal column coverage is unavailable, leaving 22 required cases unresolved.** `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:140`, `greekocr/harvest/orientation_screen.py:84`, `greekocr/harvest/orientation_screen.py:129`.

The native verifier supplies unavailable column evidence for every CP4 case because the consumed cache has no serialized separator inventory. Consequently **21 KEEP cases remain unresolved** in the complete union; the unknown rotated witness adds one, for **22 unresolved required witnesses**. There are zero fully verified CP5 KEEP outcomes. The planted validated-rule crossing passes, but no native column-crossing qualification is established. The adapter correctly preserves unknown rather than inventing an empty inventory; the missing evidence is nevertheless an unmet deliverable/acceptance condition. Supply source-bound existing separator/crossing evidence through the authorized tools before claiming CP5 qualification.

### Medium — 0

### Low — 1

**L1 — CP4c known-issues handoff status is stale.** `docs/records/harvest/collect_v3_admission/seg/CP5_RECEIPT.md:67`.

The receipt calls the collector `KNOWN_ISSUES.md` handoff a remaining blocked limitation. Live read-only verification found the document at `../greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/KNOWN_ISSUES.md:1`, with both requested later-fix entries, committed as `7a026c3d7`; `git status --short -- <path>` is empty. Its bytes match the local CP4c handoff document. Update the receipt's status when revising the checkpoint artifacts. This review did not edit that checkout.

## CP5 Sol code-review criteria, verbatim and individually assessed

The following preserves the wording of each criterion in ASTRA-SEG1 item 5 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:212`). Implementation compliance and acceptance qualification are assessed separately.

| Verbatim criterion | Verdict and evidence |
|---|---|
| “no recognizer/OSD” | **PASS.** `greekocr/harvest/orientation_screen.py:55` explicitly supplies `use_osd=False`; `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:29` replaces recognizer polarity and OSD with failures. The fresh run recorded zero forbidden attempts. |
| “no novel angle detector” | **PASS.** Existing `measure_orientation`, `axis_regions`, `resolve_regions`, and `BoundaryEvidence` are imported at `greekocr/harvest/orientation_screen.py:13`; ambiguity context is diagnostic at line 59. No detector implementation was added or changed. |
| “no height/width-only final decision” | **FAIL for the optional line-context path; native block path avoids this override.** `greekocr/harvest/orientation_screen.py:55` forwards explicit line context to the existing tight-ink height/width override at `greekocr/glyphs/orientation.py:195`, then maps its axis directly to exclusion at adapter line 63. ASTRA §4 explicitly permits testing that existing override, so this is not a novel-detector finding. However, the receipt's narrower assertion that no canvas-ratio predicate was added does not establish this literal final-decision criterion. The reproduced counterexamples remain H2. |
| “no silent unknown=horizontal” | **PASS.** Unknown/stale observations produce `rotated=None` at `greekocr/harvest/orientation_screen.py:43` and line 63; the union retains unknown at line 129. Coverage and abstention are counted separately at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:110`. |
| “and no assumption that accepted axis proves valid horizontal segmentation.” | **PASS in composition; coverage incomplete (H3).** `greekocr/harvest/orientation_screen.py:128` independently composes orientation, structural union and crossing. Horizontal/unknown axis cannot erase a measured structural positive; planted two-/three-row tests exercise this at `tests/test_seg_cp5.py:79`. |
| “Retain exact historical excluded-id audit alongside the new decision rather than blindly grandfathering every heuristic id.” | **PASS.** Exact unique historical membership is loaded at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:38`, retained per case at line 55 and independently measured at line 81. All 1,681 historical ids are present beside new decisions; membership is not treated as semantic truth or an automatic DROP. |

## Independently reproduced acceptance numbers

Every row below comes from new execution, not the receipt. Fresh CP4 output is structurally identical to `CP5_cp4_verification.json`, so the CP5 verifier's saved structural input was independently validated before accepting the composed numbers. Fresh CP4 control output is also exactly equal to `CP4_controls.json`.

| CP5 requirement, unchanged | Reproduced measurement | Verdict |
|---|---|---|
| all adjudicated rotated positives caught | 2/4; one horizontal, one unknown | FAIL |
| 0 false drops on 22 keeps and planted upright controls | KEEP 1/22; upright 4/11, with 1/11 abstention | FAIL |
| 0 horizontal merge challenge misses | C1 6/6, gallery 6/6, overlap 5, hence 7 distinct native witnesses; planted two-/three-row positives 2/2; validated crossing positive 1/1 | PASS |
| 0 unresolved required witnesses | 22: 21 KEEP cases plus one rotated witness | FAIL |

C1's six-case denominator follows the explicit CP4c c068 ruling, not an unapproved change to the original seven-case plan. Line/block decisions on the same rendered raster are dependent observations, not independent native examples.

Orientation census: **1,715 distinct native crops**; all **1,681 historical ids** measured with block context. Historical results: **1,052 vertical, 458 horizontal, 171 unknown**; axis coverage **1,510/1,681 = 89.83%**, abstention **171/1,681 = 10.17%**, unavailable measurements **0**, known polarity **34/1,681**. KEEP axis coverage **21/22** (20 horizontal, one vertical, one unknown); rotated-positive axis coverage **3/4**, known polarity **0/4**. These historical suspect decisions are not newly adjudicated semantic labels.

The fresh screen matrices match the checkpoint output, including their denominators and Wilson intervals: orientation on the structural ledger TP/FP/FN/TN/unknown = **0/1/9/20/1**; targeted orientation **2/1/1/20/2**; CP4 structural/neighbour union **8/0/0/22/1**; full measured CP5 union **8/1/0/0/22**; policy-composed union **9/1/0/0/21**. Unknowns remain outside measured precision/recall denominators; zero denominators remain not estimable. No random/held-out generalization claim follows from this selected population.

## CP4c additions and F2/F3 reuse review

**CP4c rule/ledger: PASS within the requested scope; no new code/ledger finding.** The public evaluation path checks bound geometry before using its status (`greekocr/harvest/admission.py:583`, `greekocr/harvest/geometry_observations.py:272`). `geometry_unavailable` covers unavailable geometry and unresolved target identity (`greekocr/harvest/admission.py:491`); unresolved letter/word evidence stays unresolved. Composition preserves policy loss separately from measured detection at line 503. Source × class rule counts include the new rule via the existing generic hook at `greekocr/harvest/admission.py:735`. Semantic versions are bumped at line 322. The inconsistent-plane, inverted-target, stale evidence, valid-geometry and unresolved-target regressions all passed in the fresh test run (`tests/test_seg_cp4c.py:13`).

The ledger builder was rerun with its output redirected to `/tmp`. Rebuilt and frozen bytes both hash to **`76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f`**. Original ledger bytes also match HEAD. The coordinator's c068 reasoning is preserved verbatim in `docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:25`; provenance remains in `calibration_ledger.json:105`. It is explicitly a non-gating label-error witness, not an invented KEEP. The eighth owner issue remains unidentified.

Fresh CP4c/structural numbers: **KEEP 22/22**, **C1 6/6**, **gallery 6/6**, **D composed 9/9 versus measured 8/9**, with one unavailable NLG witness; **0 non-unavailable unresolved required cases**. Fresh controls: CP3 planted false positives **0/11**, fragment union drops **0/12** (one unresolved), complete short-run mechanics **10/10**, native recorded one-letter words **3/3**. These preserve the distinction between synthetic mechanics and native semantic evidence.

**F2/F3 toolkit reuse: PASS as an adapter design, not qualification.** CP5 adds orchestration and evidence binding, not a new angle/row/word detector. It calls existing orientation and regional tools; horizontal positives reuse CP3/CP4, and supplied separator proposals go through existing `BoundaryEvidence.validate()` and crop-local `crossing()` (`greekocr/harvest/orientation_screen.py:94`, line 115). No legacy anonymous all-pairs bridge, ten-component completeness assertion, `GAP_STOP` word boundary, generic readability/clipping DROP, ownership retuning, paint/fill, or admission-time page re-detection was added. Frozen ownership remains `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. The native missing-column evidence is honestly unavailable, not synthesized from structural column ids.

## Reproduction and preservation evidence

Used the exact interpreter `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, with `PYTHONDONTWRITEBYTECODE=1` and `-B`. Independently ran:

```sh
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp4.py
python -B docs/records/harvest/collect_v3_admission/seg/review_cp4c.py
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp4_controls.py
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp5.py
python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp5-review-tests tests/test_seg_cp5.py tests/test_seg_cp4c.py tests/test_seg_cp4.py tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
python -B docs/records/harvest/collect_v3_admission/seg/guard_cp5_commit.py
```

Here `python` denotes that full path. Result: **391 passed in 8.31s**, including **25 CP5 tests**; no skipped/xfail acceptance workaround. The guard passed for all **11 exact files**, dependency hashes and unchanged HEAD. Polynomial-fit warnings were retained in the new measurement log. Temporary evidence: `/tmp/SEG_CP5_review_{measurement,cp4,cp4c,controls,preservation}.json`, `/tmp/SEG_CP5_review_measurement.log`, `/tmp/SEG_CP5_review_pytest.log`, and `/tmp/SEG_CP5_review_tracked_pngs.json`.

Independent SHA-256 checks against `git show HEAD:<path>` confirmed that all **8 tracked protected artifacts**, including admission outputs and the crops manifest, match HEAD. The ninth protected artifact, untracked `ADMISSION_CENSUS_20261017.json`, has no HEAD bytes; it matches its prior snapshot SHA-256 `d6f088c456605b7026af83361c2f468c5b31beef10073ebfc2b6dbe916fbfe3b`. This is explicitly snapshot evidence, not a HEAD comparison.

All **28,798 retained PNGs** match the hashes from the **HEAD version** of `crops_manifest.jsonl`; the manifest bytes are identical to HEAD. Additionally, all **1,573 present tracked PNGs** across the repository were compared directly by SHA-256 with their HEAD blobs: zero mismatches. Eight other tracked PNGs are absent with Git's pre-existing `S`/skip-worktree flag; their bytes cannot be checked locally. There are zero tracked PNG/manifest diffs. The absent files are unrelated historical mixed/page-read visual samples, not retained admission crops.

Fresh CP4 and CP5 measurement audit hooks recorded **zero write/mutation attempts**, **zero detector/network/reader/OSD calls**, and **zero publish actions**. CP4c reconstruction writes only inside a temporary directory; tests use `/tmp`, bytecode and pytest cache writes are disabled. Source-bound crop reconstruction occurs in memory and must reproduce the historical PNG hash. No live-run lock, preparation, crop save, or publication was executed by this review. The live root is concurrently collector-owned; these observations establish no writes by the reproduced review/checkpoint paths, not a global absence of concurrent collector writes or a forensic proof of every earlier process action. Before/after file hashes alone cannot establish that stronger historical claim.

Only this review document was written in the worktree. Existing unrelated `.gitignore`, `stage_crops.py`, test drafts and untracked artifacts were left as found. No staging or commit was performed.

SEG-CP5 review: FAIL | blocking: 0 | high: 3 | acceptance: 1/4 met reproduced | publish actions: 0
