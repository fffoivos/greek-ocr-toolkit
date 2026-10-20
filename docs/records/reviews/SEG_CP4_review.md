# SEG-CP4 Sol code review

2026-10-18. **FAIL.** Reviewed uncommitted CP4 against ASTRA-SEG1 numbered PLAN item 4 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:203`). Base HEAD: `072c9db39d41b54a9350dfbc9320a6cb6b749edc`. Only this review was written in the repository; temporary verification output is under `/tmp`. No implementation, receipt, admission artifact or Git state was changed.

The 351 tests pass, but acceptance is **1/5 for the structural/neighbour union**, not the receipt's 2/5. Its fragment count is reproducible for neighbour alone; the union drops one of those same nine controls. The saved native verification JSON reproduces exactly. GATE_FAIL must remain; no application/publication is qualified.

## Findings by severity

### Blocking — B1: required DROP coverage and required-witness resolution still fail

**Locations:** `docs/records/harvest/collect_v3_admission/seg/verify_cp4.py:75`, `greekocr/harvest/geometry_observations.py:113`, `docs/records/harvest/collect_v3_admission/seg/CP4_verification.json:35`.

Independent execution detects **8/9 required DROP**, with `nlg--6146c0455e0103d2--s001-l0006` unavailable because the cached foreground and label planes disagree (`invalid_source_frame_or_labels`). There is **1/31 unresolved required calibration witnesses**. Rejecting inconsistent geometry is correct, but it leaves two CP4 acceptance requirements unmet. An unavailable positive cannot be removed from D or counted as a successful detection. Repair requires separately authorized, source-bound preparation and remeasurement, not relaxing cache validation. The receipt discloses this limitation correctly.

### High — H1: the union bypasses the partial-word rejection; the fragment acceptance count is overstated

**Locations:** `greekocr/harvest/neighbour_words.py:299`, `tests/test_seg_cp4.py:73`, `docs/records/harvest/collect_v3_admission/seg/CP4_RECEIPT.md:9` (underlying structural support: `greekocr/harvest/row_inclusion.py:94`).

Rerunning the receipt's nine fragment controls while recording both decisions gives **neighbour: 0/9 drops; union: 1/9 drops**. The existing `test_separated_partial_word_cannot_become_complete_substring` uses crop `[12,10,160,70]`, cutting the first body of the sole four-body neighbour group. Its neighbour result correctly rejects completeness, but `merged=True` forces `union_drop=True`. The test checks only `neighbour_drop`, so all 351 tests pass despite this combined failure. The separated-fragment control also remains unresolved rather than a verified KEEP.

The receipt explicitly includes this partial horizontal group in its nine fragment-only controls. Its “0/9 ... Met” does not hold for the composed decision. Reconcile supported-row inclusion with incomplete local groups and assert the union on these controls; do not report a standalone number as combined acceptance. This does not require bringing forward CP5 orientation work.

### High — H2: native letter completeness is checked against a middle-region horizontal extent

**Locations:** `greekocr/harvest/neighbour_words.py:211`, `greekocr/harvest/neighbour_words.py:236`; existing tool contract: `greekocr/glyphs/letters.py:117`, `greekocr/glyphs/letters.py:144`.

`letter_boxes()` derives horizontal bounds from middle-region pieces and measures vertical extent only inside those horizontal bounds. CP4 treats this box as the complete native letter extent. Ink from the same assigned component can extend sideways above/below the middle region and outside the crop without invalidating `extent_complete`.

An independent in-memory mechanical probe, using the existing planted fixture, adds a connected top stroke to the single neighbour body: native extent `[10,16,21,30]`, middle body `[10,20,16,30]`, crop `[10,10,16,70]`. CP4 reports letter extent `[10,16,16,30]`, `extent_complete=True`, `complete=True`, `positive=True`, `unresolved=False` and `neighbour_drop=True`, although five columns of the same native component are outside the crop. `profile_runs` itself preserves `[10,21]`. Thus the lost extent is available but not used in completeness. This proves a completeness-mechanics defect; it is not a synthetic lexical-word label.

Preserve full assigned letter ink/parent provenance when checking clipping, resolving shared-parent split letters explicitly; do not blindly require every joined parent to fit as one letter. Add this control before treating a positive as complete.

### High — H3: recorded native short-word acceptance remains 1/3

**Locations:** `greekocr/harvest/neighbour_words.py:225`, `tests/test_seg_cp4.py:164`, `docs/records/harvest/collect_v3_admission/seg/CP4_one_letter_words.json:72`.

Independent response/word-box checks and native remeasurement reproduce token 549 `Ο`: unresolved; token 567 `Ο`: unresolved; token 652 `ο`: positive. Both missed positives have visible saved extents but insufficient proxy body support; the first is split into two letter boxes sharing native parent 100. The test deliberately asserts `[False,False,True]`. This preserves honest negative evidence, but **10/10 synthetic mechanical positives cannot satisfy “all planted complete short-word positives caught”** when the recorded native probes yield **1/3 caught, 2 unresolved**. Resolve the evidence using the existing tools, or continue to fail qualification. The receipt correctly marks this requirement unmet.

### Medium

No additional findings.

### Low

No additional findings.

## Sol code-review criteria, verbatim and individually applied

Authority, `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md:206`:

> one supported neighbour row/run per positive, visible complete bodies plus word-scale extent; no anonymous all-pairs bridge, marks-as-letters inflation or arbitrary length veto; half-letters alone never drop. Frozen ownership is a measurement, not independent truth.

The table separates the compound clause without substituting the receipt's rewritten criteria.

| Verbatim criterion text | Verdict | File:line and evidence |
|---|---|---|
| one supported neighbour row/run per positive | PASS for provenance | `greekocr/harvest/neighbour_words.py:280`, `greekocr/harvest/neighbour_words.py:290`, `greekocr/harvest/neighbour_words.py:242`: positives belong to one assigned same-column/page-side row and local group, retaining native parent IDs and the neighbour's own x-height. Completeness is assessed separately below. |
| visible complete bodies plus word-scale extent | FAIL | `greekocr/harvest/neighbour_words.py:211`, `greekocr/harvest/neighbour_words.py:236`: extent can omit connected out-of-middle-region ink (H2); `.2/.8/.35` remains an explicitly unqualified proxy and native short-word qualification fails (H3). Union bypass also remains (H1). |
| no anonymous all-pairs bridge | PASS on CP4 path | `greekocr/harvest/neighbour_words.py:187`, `greekocr/harvest/neighbour_words.py:190`: original assigned-ink profile and ordered adjacent letters within one row. Historical pairwise `runs()` remains at line 54, but CP4 does not call it or use `GAP_STOP`. |
| marks-as-letters inflation | PASS for supplied controls (prohibition satisfied) | `greekocr/harvest/neighbour_words.py:170`, `greekocr/harvest/neighbour_words.py:184`, `tests/test_seg_cp4.py:121`: CP3 rule exclusions and existing middle-region letter extraction; marks/noise/rule controls each produce no neighbour or union DROP. Cache roles are absent; `role='letter'` at line 179 is a candidate descriptor, not saved semantic truth or a general guarantee. |
| arbitrary length veto | PASS (prohibition satisfied) | `greekocr/harvest/neighbour_words.py:159`, `tests/test_seg_cp4.py:32`, `tests/test_seg_cp4.py:136`: minimum body count is one, ten-body settings are rejected, and all 1–9-body mechanical positives are caught. |
| half-letters alone never drop. | PASS for exact supplied edge controls | `greekocr/harvest/neighbour_words.py:209`, `tests/test_seg_cp4.py:41`: both edges at 50% and 60% visibility give neighbour=False and union=False, 0/4 drops. This bounded result does not establish H2's full native extent requirement. |
| Frozen ownership is a measurement, not independent truth. | PASS | `greekocr/harvest/neighbour_words.py:213`, `greekocr/harvest/geometry_observations.py:198`, `tests/test_seg_cp4.py:206`: parameter digest remains `801d517e…`; frozen mask is diagnostic, native limitations stay explicit, and direct-core mask parity passes. |

## Acceptance numbers independently reproduced

All five requirements below are copied from PLAN item 4 (`ASTRA-SEG1_review_1.md:207`). Fragment acceptance is assessed on the composed decision as well as neighbour alone, consistent with the owner standard and the plan's combined-gate requirement.

| Requirement | Reproduced measurement | Verdict |
|---|---|---|
| 0/22 KEEP false drops | Neighbour 0/22; structural 0/22; union 0/22; 22/22 resolved. | MET |
| D/D required DROP by the structural/neighbour union | D=9; neighbour, structural and union each detect 8/9, with one unavailable and no measured negative. | NOT MET |
| 0 planted fragment-only drops | Neighbour 0/9; **union 1/9**; one additional control unresolved. Four edge halves/60%, partial horizontal group, three mark/noise/rule cases, separated fragments. | NOT MET for union (H1) |
| all planted complete short-word positives caught | Mechanical 1–9 bodies plus resolved joined letters: 10/10 neighbour and union positives. Recorded native one-letter words: 1/3 positive, 2 unresolved. Bars establish mechanics only. | NOT MET |
| 0 unresolved required calibration witnesses | 1/31 required witnesses unresolved; 0/22 KEEP unresolved. | NOT MET |

**Acceptance: 1/5 met.** If “fragment-only drops” is restricted to neighbour alone, the receipt's standalone 0/9 and 2/5 reproduce, but that narrower accounting leaves H1's composed false drop untested and cannot qualify the union. No new negative probe was added to the receipt's denominator to obtain 1/9.

Native matrices, DROP positive, excluding the nongating borderline:

| Screen | TP | FP | FN | TN | Unknown |
|---|---:|---:|---:|---:|---:|
| Neighbour | 8 | 0 | 0 | 22 | 1 |
| Structural | 8 | 0 | 0 | 22 | 1 |
| Union | 8 | 0 | 0 | 22 | 1 |

Each screen's measured-only precision and recall are 8/8 (Wilson 95% `[0.6755924351,1]`); KEEP false-drop and survivor-defect rates are 0/22 (`[0,0.1486548746]`). Required-positive detection remains 8/9. Unknowns are not successes; this selected, page-dependent development ledger is not independent generalization evidence.

C1: **7/7**; pinned-gallery merges: **6/6**; overlap **5**, unique witnesses **8**. Nongating borderline `ia_poly1850--36dcee7ce4c29f8b--s004-l0032`: measured; neighbour=False, structural=False, union=False. Truth unchanged.

## Reproduction and reuse checks

Used the required collector interpreter, `PYTHONDONTWRITEBYTECODE=1`, `-B`, and pytest `-p no:cacheprovider --basetemp=/tmp/seg-cp4-review-tests`:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp4-review-tests tests/test_seg_cp4.py tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/verify_cp4.py
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/collect_v3_admission/seg/guard_cp4_commit.py
```

**351 passed in 6.30s**, including 30 CP4 cases. The verifier output, saved only to `/tmp/seg-cp4-review-verification.json`, is JSON-equal to `CP4_verification.json`; its gate is false. Guard: PASS, exact nine files, base HEAD unchanged; 120 inherited prepared-cache files retain their bound hashes. There are 24 inherited preparations/24 receipts and **0 new preparations**. All per-case native measurements, matrices, intervals and recorded-word outcomes were recomputed, not copied from the receipt.

For fragment/mechanical counts, imported `tests/test_seg_cp4.py` with `tests` on `sys.path`, wrapped its `observe()` to retain the returned records while preserving every original assertion, then called the four parametrized edge cases, partial-horizontal-group case, three CC-inflation cases and separated-fragment case. Repeated for the nine body-count cases and resolved-joined-letter case. This exposes the union values omitted by the partial-word assertion.

H2 is reproducible without writing a fixture:

```python
import sys
sys.path.insert(0, 'tests')
from test_seg_cp4 import short_page, observe
p = short_page(1)
r = p['rows'][1]
cid = r['component_ids'][0]
p['labels'][16:20, 10:21] = cid
p['ink'][:] = p['labels'] > 0
p['rows'][1] = p['ownership'].prepare_row(
    {k: v for k, v in r.items() if not k.startswith('_')},
    p['ink'], p['labels'])
m = observe(p, [10, 10, 16, 70])
assert m['neighbour_drop'] is True
assert m['rows'][0]['groups'][0]['letters'][0]['extent_complete'] is True
# Native component x1 is 21; crop and reported letter x1 are 16.
```

F2/F3 reuse is real: CP4 consumes the CP2 cache-hit adapter and CP3 structural evidence, constructs `LineGlyphs`/`Band`, calls existing `letter_boxes()`, `BoundaryEvidence.profile()` and `straighten_edges()`, and shares the unchanged foreign-mask core (`neighbour_words.py:154`, `geometry_observations.py:84`, `geometry_observations.py:215`). The `.35*xh` gap scale exists in `greekocr/glyphs/oriented_page.py:88`. No new page/row detector, refit, re-binarization, ownership retuning or paint/fill call occurs on this path. The new grouping/completeness glue is still a development proxy: toolkit reuse does not validate its semantics (H1–H3). Missing/ambiguous targets and missing neighbours remain unresolved (`neighbour_words.py:265`, `neighbour_words.py:283`); no production calibration-ID whitelist was found. Existing unrelated staging/.gitignore/NW drafts are outside the guarded CP4 file list and were not executed.

## Protected artifacts and live-run assurance

Independently hashed protected working files and `git show HEAD:<path>` bytes, rather than trusting Git status alone. **8/8 tracked protected artifacts match HEAD** by SHA-256. The ninth, `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017.json`, is already untracked and has no HEAD blob; it matches its frozen `protected_before.json` SHA-256. Do not describe that file as HEAD-verified.

Read `crops_manifest.jsonl` directly from HEAD and hashed every referenced crop: **28,798/28,798 PNG SHA-256 values match the HEAD manifest**; the manifest itself matches HEAD. This checks ignored crops too. Broader HEAD-blob comparison of available tracked PNG/admission/manifest artifacts found **0 mismatches among 1,589 files, including 1,573 PNGs**. Another 24 selected HEAD paths are absent sparse-checkout entries (skip-worktree), not changed CP4 crop artifacts. `git diff HEAD` reports no protected admission/manifest/PNG changes. All nine protected frozen hashes match.

Verifier runtime assurance (`verify_cp4.py:23`): **0 filesystem write attempts, 0 detector/network calls, 0 new preparations** with its mutation audit active. The reviewed cache-hit and measure paths contain no live-root write or lock, and test writes use pytest temporary fixtures under `/tmp`. Consequently **no write or lock by the reviewed SEG execution to `~/Projects/collect-v3-data/run` was observed or attempted**. This is not a claim that the whole live tree was immutable across all processes, nor a retrospective proof of every earlier builder process; the brief explicitly identifies concurrent collector materialization (`docs/records/briefs/SEG_CP4_build.md:18`). No collector was stopped or modified. Publish actions in this review: **0**.

SEG-CP4 review: FAIL | blocking: 1 | high: 3 | acceptance: 1/5 met reproduced | publish actions: 0
