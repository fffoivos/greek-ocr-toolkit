# SEG-CP1 receipt — truth frozen; actual union fails

18 October 2026. CP1 of ASTRA-SEG1 Numbered PLAN item 1 is complete. The segmentation policy remains **GATE_FAIL**. CP2–CP7 were not executed. No detector, reader, network, paid service, preparation job, reissue, staging or publication was run. The two guarded entrypoints were invoked only to verify that they stop before any write or detector call.

## Acceptance numbers

| CP1 requirement | Measured value | Evidence |
|---|---:|---|
| Unique owner KEEP | **22** | `calibration_ledger.json`, exact NW1b brief §2 list |
| Exact published required DROP D, with provenance | **9** | Nine ids below; explicit change from the prior ten-id draft explained below |
| Current union failure detected | **4/22** | `../nw1b/calibration.json`: candidate union TP=9, FP=4, FN=0, TN=18 |
| Publish actions while gate fails | **0** | `verification.json`; both entrypoints stop, zero write attempts |
| Required positive representation | **9/9 D**, **7/7 C1**, **6/6 gallery merges** | Separate lists in the ledger; C1/gallery overlap **5**, named-owner/gallery overlap **4** |
| KEEP/DROP overlap | **0** | Ledger validation and regression tests |
| Borderline silently relabelled | **0** | One borderline remains nongating |
| Eighth owner issue invented | **0** | Status remains `unidentified`, id `null` |
| Regression includes all four false-drop ids | **yes, 4/4** | `tests/test_seg_cp1.py`, parameterized by the four exact ids |
| Tests in the final scoped run | **205 passed** | `pytest.log` |

“DROP published” in the final status line means the required-DROP count published in this calibration ledger, not an admission publication. Admission publications are zero.

## Frozen ledger and D adjudication

Ledger: [`calibration_ledger.json`](calibration_ledger.json)

SHA-256: `f4448ea50daeb0297a0d9b6eb65f889ca772e3fb8b83547ae2efc58082e9f4f4`

The ledger binds the owner brief, full ASTRA review, pinned gallery blob at collector commit `83aaab5d`, C1 verdicts and card-key mapping, saved NW observations, live W1 feature snapshot, collector builder and rotated-id registry. It embeds all saved case observations; historical flags do not supply truth. It preserves all 24 gallery witnesses separately from the seven C1 merge witnesses. `freeze_truth.py` creates the ledger exclusively and refuses to overwrite an existing ledger.

Required D is the deduplicated union of six pinned-gallery merges and seven named owner issues, with four overlaps: **6 + 7 − 4 = 9**:

- `gazette_modern--0020420cfe156a73--s000-l0039`
- `gazette_modern--0020420cfe156a73--s000-l0138`
- `gazette_modern--0020420cfe156a73--s000-l0141`
- `gazette_modern--0020420cfe156a73--s000-l0146`
- `gazette_modern--0020420cfe156a73--s000-l0162`
- `gazette_modern--0020420cfe156a73--s000-l0228`
- `gazette_modern--1f7db88d63c02afa--s000-l0287`
- `gazette_modern--5af16c5d518d2ebb--s000-l0128`
- `nlg--6146c0455e0103d2--s001-l0006`

**Explicit D change, as required by review §5:** the ten-id NW1b draft added `kosmopolis--62ca52b56ebe780a--s005-l0051` solely through its historical `screen_merged` flag. The pinned `sg1-07` record calls it `readable_half_line_overrun` and describes “lower halves of the line above and upper halves of the line below”. Applying the owner's rule to that saved semantic evidence does not establish a complete neighbouring word or multiple complete rows. CP1 removes it from required semantic D and records `not_required_half_fragments`. It remains a diagnostic case with both historical merged and neighbour hits. It is **not** promoted to an invented owner KEEP verdict. This adjudication uses the pinned record; no new reading or whole-word annotation is claimed.

C1 `c068`, `gazette_modern--2e613d9290dd13d4--s000-l0209`, is separately represented as a challenge positive outside D and outside the gallery. It has a saved historical merged hit and unavailable neighbour measurement. Its union hit is supported by the merged observation; no missing neighbour observation is called a verified keep. Neither c068 nor any gallery id is asserted to be the unidentified eighth owner issue.

The borderline `ia_poly1850--36dcee7ce4c29f8b--s004-l0032` has saved neighbour=false, merged=false, rotated=false, union=false; it remains nongating.

## Actual gate and pre-screen population

`calibrate.py` now reads the frozen ledger and evaluates the three-screen OR: neighbour, historical merged, registered rotated. It makes no page-measurement or detection call. Existing `(10, 3.0, 0.6)` thresholds are evaluated as a diagnostic candidate; no threshold search or predicate repair was performed. `selected` is null because the combined gate fails. The prior report is preserved as `legacy_calibration.json` and is superseded by the CP1 report.

`prepare_w1.py` and `reissue.py` both call `require_qualification()`. It regenerates the same union decision, checks the entire report, binds the ledger and four code files by hash, verifies source hashes, and raises on GATE_FAIL. Standalone success, a forged top-level pass, stale hashes and the former selected-is-not-null shortcut cannot authorize these entrypoints. Owner ids appear only in calibration/test truth; production admission code was not changed by CP1.

| Saved candidate on 22 KEEP + 9 D | TP | FP | FN | TN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| Neighbour alone | 9 | 0 | 0 | 22 | 9/9 | 9/9 |
| Historical merged alone | 5 | 4 | 4 | 18 | 5/9 | 5/9 |
| Registered rotated alone | 0 | 0 | 9 | 22 | not estimable (0/0) | 0/9 |
| Actual union | 9 | 4 | 0 | 18 | 9/13 | 9/9 |

The report also contains the default-threshold results, per-screen KEEP-loss/survivor-defect rates, actual denominators, unknown counts and descriptive Wilson 95% intervals. These targeted, shared-page observations do not establish generalization or semantic validity of the existing screens. All seven C1 and six gallery merge witnesses have saved union hits; this is CP1 accounting, not CP3 physical qualification.

Read-only inspection reused the collector builder's `included(r)` predicate **before** merged/rotated/class removal: **101,098 feature rows; 33,301 eligible pre-screen rows**. Ordered eligible-id SHA-256 (feature-file order): `88563264cf6f6a103d2cbe4ee86b98ac3cd15fcb5b024f7955defe82e82e7f92`.

All four historical false-drop ids remain in the 22 KEEP denominator:

| Id | Current pre-screen content allowlist eligible | Merged hit | Neighbour hit |
|---|---|---|---|
| `gazette_modern--54876940c2de96c3--s000-l0062` | no | yes | no |
| `gazette_modern--836a4d5d06d0f16d--s000-l0045` | no | yes | no |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0062` | no | yes | no |
| `kosmopolis--109d033afd51aea6--s000-l0019` | yes | yes | no |

The first three are outside the builder's present content allowlist; they are not removed from calibration. The fourth is eligible and historically screened out upstream. No downstream survivor-only replay was used or prepared.

## Verification and worktree sorting

The byte-exact collector interpreter ran:

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp1-final tests/test_seg_cp1.py tests/test_neighbour_words.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py
```

**205 passed in 4.91s.** Tests include a planted standalone-pass/union-fail observation, zero-denominator handling, unavailable evidence, rotated-union composition, no invented truth/counts, the four exact KEEP ids, stale/forged qualification, and both stop-before-side-effect entrypoints. Synthetic fixtures use `/tmp` only.

An initial broader invocation also selected the pre-existing NW staging integration draft: its four tests failed in setup because the untouched historical manifest has no `admitted` field. Its staging/re-run test bodies did not execute. CP1 did not repair that later-stage draft or change the manifest. One import error in the new CP1 test was corrected before the final passing run. No full-suite or staging qualification is claimed.

`verify_cp1.py` confirms **9/9 protected artifacts unchanged by SHA-256, size and mtime**, **28,798/28,798 existing staged PNGs matching the unchanged original manifest**, **10/10 bound sources unchanged**, and both real guarded entrypoints stopped with **0 write attempts and 0 detector calls**. No live-run locks were taken.

Reviewable commit list: [`CP1_COMMIT_LIST.json`](CP1_COMMIT_LIST.json). No index or commit mutation was performed.

- **ADM5c-leftovers:** five exact manifest matches from `84b5df8d`: `codec/v2.json`, `test_adm5c_variants.py`, and the `.md`, `_admission.jsonl`, `_admission_receipt.json` census artifacts. They form their own group.
- **Mixed schema draft:** `test_adm5b_schema.py` is the ADM5b/c contract with later NW receipt/rule compatibility edits. Its current hash differs from the ADM5c manifest. The list records both hashes and excludes it from the exact leftover group until its hunks are split. CP1 did not edit it.
- **SEG-CP1:** the three gate scripts, regenerated report/GATE_FAIL, calibration test updates and frozen ledger/verification/receipt artifacts. File hashes and HEAD/branch are bound in the list; the receipt and list itself are explicit companion paths.
- **Preserved NW1/NW1b drafts:** `neighbour_words.py`, production `admission.py` edits, staging edits and remaining NW directories stay drafts. The `.gitignore` cache entries belong here, not ADM5c. The unchanged original measurement file remains bound evidence. The mixed `test_neighbour_words.py` contains both earlier planted draft tests and CP1 gate regressions; that distinction is recorded for review.
- **Excluded:** the older `ADMISSION_CENSUS_20261017.json` is explicitly superseded in the committed ADM5c manifest; `.venv`, recut leftovers and the review codexlog remain unrelated. No whole-worktree staging is proposed.

SEG-CP1: done | KEEP unique: 22 | DROP published: 9 (provenance ok) | union failure detected: 4/22 | publish actions: 0 | regression incl. 4 ids: yes | tests: 205 passed
