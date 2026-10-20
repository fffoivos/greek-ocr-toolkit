# SEG-CP5 review 2 — CP5b included

18 October 2026. **FAIL: 2/4 acceptance requirements independently reproduced as met.** Reviewed uncommitted CP5/CP5b against ASTRA-SEG1 numbered PLAN item 5, its F2/F3 findings and §4, both build/fix briefs, and the earlier `SEG_CP5_review.md`. Also reviewed the CP4c rule and truth changes committed in `81e7756c`. Current base HEAD is `7d76c93f2335862532ad30f45cf10061b0f3a185`; the earlier review's base is historical, not this review's binding. `CP5_COMMIT_LIST.json` and its guard pass for **85 exact files** and their dependencies. Only this document was written in the worktree; scratch evidence is under `/tmp/SEG_CP5_review2*`.

## Findings by severity

### Blocking — 0

No additional blocking implementation finding. The high findings below prevent CP5 qualification. `gate=False` remains explicit (`docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:198`), and public admission remains unqualified (`greekocr/harvest/admission.py:595`).

### High — 2

**H1 — OPEN from review 1: two adjudicated rotated positives remain uncaught.** `greekocr/harvest/orientation_screen.py:69`; `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:180`.

Fresh native execution catches **2/4**, with **2/4 unknown**. `gazette_modern--b9f59878fb904d91--s000-l0034` and `gazette_modern--ebdc4d07ff8c4122--s000-l0265` still do not produce a vertical exclusion. The former changed from wrong horizontal to unknown; the latter remains unknown. Both unchanged crops visibly contain sideways numeric cells. Their raw block/line axes are horizontal/vertical and unknown/vertical respectively; fresh existing page-region tools return an overlapping vertical region and a vertical block measurement for each. Thus the available toolkit evidence is richer than the crop-local result, but the current adapter never uses regional context to resolve these disagreements. It follows the fix brief's explicit disagreement veto, so this is an unmet acceptance condition rather than permission to override that direction.

The receipt honestly records the conflict (`docs/records/harvest/collect_v3_admission/seg/CP5_RECEIPT.md:49`). Resolve the regional-inheritance rule with the lead/coordinator and qualify an authorized local/regional consumer, or retain FAIL. Do not infer success from text-first composition: only one of the four positives reaches orientation under existing metadata, and its **1/1** catch does not replace standalone **2/4**. Unknown polarity is not the cause: both caught vertical positives have unknown polarity and are correctly excluded.

**H4 — Remaining qualification gap: five owner KEEP witnesses are unresolved by the full CP5 union.** `greekocr/harvest/orientation_screen.py:69`; `greekocr/harvest/orientation_screen.py:71`; `greekocr/harvest/orientation_screen.py:151`; `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:169`.

With native separators now available, the union verifies only **17/22 KEEP**, with **0 false drops and five unresolved axes**:

- `bsb_poly1850--e18cacecef3b4590--s005-l0076` — mixed regional axes;
- `gazette_modern--0d0b2233a81e355c--s000-l0019` — line/block disagreement;
- `gazette_modern--4b5e54c14bfb5810--s000-l0031` — line/block disagreement;
- `gazette_modern--54876940c2de96c3--s000-l0062` — mixed regional axes;
- `kosmopolis--109d033afd51aea6--s000-l0019` — mixed regional axes.

These five, plus H1's two positives, give **seven unresolved required native witnesses**. This finding concerns the five KEEP outcomes; H1 separately concerns the positive catch requirement. Conservative abstention closes the earlier false vertical decisions but does not establish accepted horizontal axes. Keep unknowns visible and resolve them with authorized existing evidence. Extending `geometry_unavailable` to unknown axes would create **5/22 known KEEP policy losses**, not solve orientation. Upright controls additionally have **8/11 standalone abstentions**, including **2/5** that pass text checks; these are also explicitly unqualified axis outcomes.

### Medium — 0

### Low — 0

## Earlier review findings: closure assessment

| Earlier finding | Verdict and current evidence |
|---|---|
| H1, two rotated misses | **OPEN.** Reproduced above; 2/4 caught, two unknown. `orientation_screen.py:69`, `verify_cp5.py:180`. |
| H2, owner KEEP and upright controls falsely vertical; line extent used as final axis | **CLOSED for false drops and the final-axis defect.** All final candidates come from block measurement; line extent can only veto. Fresh KEEP losses 0/22, upright losses 0/11 standalone and 0/5 after text rules. `greekocr/harvest/orientation_screen.py:56`, line 65, line 75; `tests/test_seg_cp5.py:138`. KEEP abstentions remain H4, not verified successes. |
| H3, absent native separator inventory | **CLOSED for the missing evidence.** Independently regenerated all 23 inventories in memory: exact equality with stored payloads, 32 gutters + one rule, 13 measured empty pages. Native crossing coverage 33/34, including all 22 KEEP; the remaining case is the already-known unavailable NLG geometry. `greekocr/harvest/separator_inventory.py:22`, line 41; `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:155`. Zero native positive crossings; positive crossing mechanics remain planted evidence. |
| L1, stale known-issues status | **CLOSED.** Receipt now records the collector handoff accurately at `docs/records/harvest/collect_v3_admission/seg/CP5_RECEIPT.md:87`. Read-only inspection confirms both entries, clean file status, and collector commit `7a026c3d7`. |

The l0019 diagnosis also reproduces: crop 718×41, raw block vertical, raw line horizontal; block neighbour votes H=22.3621/V=27.0878, 62 bodies, estimated x-height 7 px. Projection concentration favours horizontal (1.18945/0.93400). Recorded target row-00027 has x-height 12.1958 and 2,300 assigned pixels, versus 32 and 73 in adjacent rows. I inspected the native crop and surrounding page pixels: the printed line is horizontal. The adapter now abstains instead of falsely dropping it. Fragmented small print producing accidental vertical component alignments is a supported interpretation of the tool's failure, not independently proven component causation.

## CP5 Sol code-review criteria — verbatim, one by one

Wording below is copied from ASTRA-SEG1 item 5 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:212`). These implementation verdicts do not override acceptance failures.

| Verbatim criterion | Verdict and file:line |
|---|---|
| “no recognizer/OSD” | **PASS.** Both measurements explicitly set `use_osd=False` at `greekocr/harvest/orientation_screen.py:56` and line 58. Fresh census substitutes failures for recognizer polarity and OSD at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:31`; forbidden-attempt count is zero. |
| “no novel angle detector” | **PASS.** Existing `measure_orientation`, `discover_directions`, `axis_regions` and `resolve_regions` are reused at `greekocr/harvest/orientation_screen.py:13`, line 60 and line 95. No new detector implementation or detector retuning. |
| “no height/width-only final decision” | **PASS after CP5b.** Block measurement supplies the candidate at `greekocr/harvest/orientation_screen.py:56` and line 65. Tight-ink aspect is used only to abstain at line 64; line/block disagreement can only abstain at line 69. Neither extent result supplies a final horizontal/vertical axis. Regression at `tests/test_seg_cp5.py:138` reproduces a real line-extent result without letting it resolve block abstention. |
| “no silent unknown=horizontal” | **PASS.** Unknown axes return `rotated=None` at `greekocr/harvest/orientation_screen.py:83`; stale/corrupt saved observations are unavailable at line 43 and line 50. Tri-state union retains unknown at line 151. Abstentions and coverage are independently counted at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:114`. |
| “and no assumption that accepted axis proves valid horizontal segmentation.” | **PASS.** Independent structural/neighbour and crossing evidence is composed at `greekocr/harvest/orientation_screen.py:150`; a horizontal axis cannot cancel a positive. Two-/three-row and validated crossing regressions pass at `tests/test_seg_cp5.py:79` and line 97. |
| “Retain exact historical excluded-id audit alongside the new decision rather than blindly grandfathering every heuristic id.” | **PASS.** Exact 1,681 unique ids are loaded at `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:40`, retained per case at line 57 and measured at line 83. Membership supplies neither a semantic label nor an automatic DROP. |

## Independently reproduced acceptance

All values below come from new execution with the byte-exact collector interpreter, not receipt transcription. Fresh CP4 output exactly equals `CP5_cp4_verification.json`; fresh CP4 controls exactly equal `CP4_controls.json`. Fresh CP5 acceptance, coverage, screen matrices and their metric denominators/intervals equal the checkpoint output. Native diagnostics differ only in 18 timing fields.

| CP5 acceptance requirement | Fresh measurement | Verdict |
|---|---|---|
| all adjudicated rotated positives caught | 2/4 caught; 2 unknown, 0 horizontal | **FAIL** |
| 0 false drops on 22 keeps and planted upright controls | KEEP 0/22; upright 0/11 standalone, 0/5 text-eligible | **PASS** |
| 0 horizontal merge challenge misses | C1 6/6, gallery 6/6, overlap 5, seven distinct native witnesses; planted multi-row 2/2 and validated crossing 1/1 | **PASS** |
| 0 unresolved required witnesses | Seven required native witnesses: five KEEP + two rotated; upright abstentions separately reported above | **FAIL** |

C1's denominator is six under the explicit CP4c c068 ruling, not a silent reduction from the plan's original seven. No skips or xfails substitute for acceptance. Line/block observations of one rendered control are dependent examples.

Fresh census: **1,715 native crops**, including all **1,681 historical ids**. Historical axes: **1,043 vertical, 638 unknown**, coverage **1,043/1,681 = 62.05%**, abstention **638/1,681 = 37.95%**, unavailable **0**, polarity known **32/1,681**. KEEP axes: **17 horizontal, five unknown**, coverage **17/22 = 77.27%**, abstention **5/22 = 22.73%**, no vertical. Rotated witnesses: coverage **2/4**, abstention **2/4**, polarity known **0/4**. Both caught ids are `8213d286 l0144` and `83c3182a l0259`.

Text-first composition: **717/1,715** native rows, **19/22** KEEP and **1/4** rotated positives reach orientation. The three text-rejected KEEP fail the existing unexpected-language check. Three numeric-looking rotated crops fail their existing declared text rules; this review does not reclassify them. Six upright observations (`ΟΙ`/`12`, including tall-canvas controls) fail text requirements first. Of the five reaching orientation, three are horizontal and two abstain. Standalone denominators remain intact.

Fresh matrices, with DROP positive:

| Screen / population | TP | FP | FN | TN | Unknown |
|---|---:|---:|---:|---:|---:|
| Orientation, structural ledger | 0 | 0 | 9 | 17 | 5 |
| Orientation, KEEP + rotated positives | 2 | 0 | 0 | 17 | 7 |
| CP4 merged / neighbour / their union, each | 8 | 0 | 0 | 22 | 1 |
| CP5 measured union, structural ledger | 8 | 0 | 0 | 17 | 6 |
| CP5 union with CP4c policy | 9 | 0 | 0 | 17 | 5 |
| Text-eligible orientation, structural ledger | 0 | 0 | 9 | 14 | 5 |
| Text-eligible CP5 policy union, structural ledger | 9 | 0 | 0 | 14 | 5 |

The full fresh precision/recall/KEEP-loss/survivor-defect numerators, denominators and Wilson-95% intervals are preserved in `/tmp/SEG_CP5_review2_measurement.json:screens`. Unknowns are outside resolved denominators; zero denominators remain null/not estimable. For example, targeted resolved recall is 2/2 while the required end-to-end rotated catch is 2/4; calling the latter 100% would be wrong. No random-generalization or CP7 reading claim follows from these selected cases.

## CP4c additions and F2/F3 reuse

**CP4c PASS within this scope; no additional finding.** Bound evidence is revalidated before use (`greekocr/harvest/admission.py:583`, `greekocr/harvest/geometry_observations.py:272`). Unavailable geometry/unresolved target identity causes a distinct policy loss (`greekocr/harvest/admission.py:491`); unresolved letters remain unresolved. Composition preserves measured output separately at line 503. Version/rule declarations are updated at line 322 and line 335; the generic per-source/class rule-count hook includes this rule at line 735. Fresh inconsistent-plane, inverted-target, stale-evidence, valid-geometry and unresolved-target tests all pass (`tests/test_seg_cp4c.py:13`).

Rebuilding the ledger through its builder in temporary storage reproduces byte-exact SHA **76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f**; frozen bytes also match HEAD. The coordinator's c068 explanation is verbatim at `docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:25`; c068 remains a non-gating label-error witness, not an invented KEEP. The eighth owner issue remains unidentified.

Fresh CP4c evidence: KEEP **22/22**, C1 **6/6**, gallery **6/6**, D **9/9 policy-composed versus 8/9 measured**, one unavailable NLG, zero non-unavailable unresolved required cases. Controls: CP3 planted FP **0/11**, fragment union drops **0/12** with one unresolved, complete short-run mechanics **10/10**, native recorded one-letter words **3/3**. Synthetic mechanics do not supply native semantic word labels.

**F2/F3 toolkit reuse PASS as adapter design.** Orientation uses the existing tools listed above. New compact/disagreement/mixed-region vetoes are explicit conservative abstention policy from the fix brief; they are not new angle or word detectors. Horizontal positives reuse CP3/CP4 structural rows, native component provenance and neighbour geometry. Separator preparation calls existing `pages.pixels.prepare_pixels` and `pages.structure.build_structure` with copied recorded rows (`greekocr/harvest/separator_inventory.py:25`); crossing calls existing `BoundaryEvidence.validate/crossing` on original crop-local ink (`greekocr/harvest/orientation_screen.py:115`, line 137). No generic readability/clipping DROP, anonymous all-pairs graph, marks-as-letters count, ten-component word guarantee or `GAP_STOP` word boundary was added. No ownership retuning or painting; frozen ownership remains **801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8**.

I independently reran the separator measurement body once per each of **23 source-bound pages**, in memory under a write-blocking audit hook. Instrumentation counted **23 pixel preparations, 23 structure calls, 0 row-detector calls and 0 write attempts**. All 23 regenerated inventories exactly equal the saved inventories, including **32 validated gutters, one validated rule and 13 measured empty inventories**. Existing persistent attempt claims were not erased or rewritten. The original preparation orchestrator confines its output to the isolated cache (`docs/records/harvest/collect_v3_admission/seg/prepare_cp5_separators.py:18`) and uses the source-bound claim mechanism at line 37; alias-once behavior is tested at `tests/test_seg_cp5.py:199`. Measurement only loads inventories; it never prepares them. Coverage is **33 measured/one unavailable** across 34 CP4 cases, with all 22 KEEP covered and no native positive crossing in this set.

## Reproduction and preservation

Interpreter: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, always `PYTHONDONTWRITEBYTECODE=1` and `-B`. Independently ran:

```text
verify_cp4.py
review_cp4c.py
verify_cp4_controls.py
diagnose_cp5.py
verify_cp5.py
guard_cp5_commit.py
```

These scripts are under `docs/records/harvest/collect_v3_admission/seg/`; stdout/stderr went to `/tmp/SEG_CP5_review2_{cp4,cp4c,controls,diagnostics,measurement,guard}.*`. The separate in-memory preparation reproduction and preservation hash audit are `/tmp/SEG_CP5_review2_separators.py` and `/tmp/SEG_CP5_review2_preserve.py`, with JSON results beside them. Native inspection sheet: `/tmp/SEG_CP5_review2_native.png`.

Tests were rerun with `-m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp5-review2-tests` over `tests/test_seg_cp5.py`, `test_seg_cp4c.py`, `test_seg_cp4.py`, `test_seg_cp3.py`, `test_seg_cp2.py`, `test_harvest_admission.py`, `test_adm5b_schema.py`, `test_adm5c_variants.py`, `test_neighbour_words.py` and `test_seg_cp1.py`: **399 passed in 7.93s**, including **33 CP5 tests**, zero skips/xfails. Log: `/tmp/SEG_CP5_review2_pytest.log`. Polynomial-fit warnings remain in measurement logs; they were not hidden.

Independent SHA-256 comparisons against **HEAD blobs**, not just receipt hashes, establish:

- All **eight tracked protected artifacts**, including admission outputs and `crops_manifest.jsonl`, are byte-identical to HEAD.
- The ninth protected artifact, untracked `ADMISSION_CENSUS_20261017.json`, has no HEAD blob. It matches its prior SHA **d6f088c456605b7026af83361c2f468c5b31beef10073ebfc2b6dbe916fbfe3b**; this is snapshot evidence only.
- All **28,798 retained PNGs** match the **HEAD manifest's** SHA-256 values. All **1,573 present tracked PNGs** across the repository additionally match their HEAD blobs directly. Zero PNG/manifest tracked diffs.
- Eight unrelated historical tracked PNGs are absent with pre-existing `S`/skip-worktree flags. Their local bytes cannot be checked; they are not retained admission crops. Exact paths and flags are in `/tmp/SEG_CP5_review2_preservation.json`.

Fresh native CP4/CP5 paths prohibit writes/mutations and recorded **zero write attempts, detector/network/reader/OSD attempts and publish actions**. Diagnostics prohibit writes/network/processes. The extra separator rerun prohibited writes everywhere, and ledger reconstruction/test outputs were confined to `/tmp`. No review/checkpoint reproduction wrote or locked the live run root. Inspection of the original preparation path shows writes restricted to the separate repository cache; its bound claims and receipts pass the guard. The collector concurrently owns the live root: this evidence establishes no writes by the reviewed/reproduced paths, not that no other process wrote there or a forensic proof of every earlier execution. Missing historical crops are reconstructed only in memory and must reproduce the original PNG hash.

No implementation, admission, manifest, crop, attempt claim, Git index or commit was modified. Existing unrelated worktree drafts remain outside this review's changes.

SEG-CP5 review: FAIL | blocking: 0 | high: 2 | acceptance: 2/4 met reproduced | publish actions: 0
