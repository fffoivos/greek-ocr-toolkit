# SEG-CP1 code review

18 October 2026. Reviewed uncommitted CP1 against ASTRA-SEG1 §Numbered PLAN, item 1, at HEAD `df76f4a52829e099da8ad79121272344dbdfa7a3` (`sol/recut-v1`). **PASS for CP1 accounting and fail-closed qualification. The segmentation policy remains GATE_FAIL and is not authorized for publication.**

## Findings by severity

- **Blocking: none.**
- **High: none.**
- **Medium/low: no actionable CP1 defect found.**

The pre-existing NW admission/staging drafts are explicitly outside the CP1 commit group (`docs/records/harvest/collect_v3_admission/seg/CP1_COMMIT_LIST.json:138`). This review does not qualify their detector, semantic word predicate, staging behavior, or future publication path. CP1 is required to expose the current failure, not repair CP2–CP7 defects.

## Sol criteria, applied verbatim

| Criterion | Result and inspected implementation |
|---|---|
| owner truth outranks old flags | PASS. KEEP is checked against the owner's exact brief list; D derives from named owner issues and pinned semantic gallery merges (`docs/records/harvest/collect_v3_admission/nw1b/calibrate.py:36`, `docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:36`). The flag-only half-line overrun is explicitly removed from semantic D, without inventing a KEEP verdict (`docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:107`). |
| no production id whitelist | PASS. Owner ids are confined to calibration/fixtures; inspected `greekocr/harvest/admission.py` and `greekocr/harvest/neighbour_words.py` contain no owner-id bypass. The saved rotated registry is an existing screen observation, as CP1 permits (`docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:64`). |
| no `gate = selected is not None` shortcut | PASS. The gate derives from combined confusion/unknowns and required challenge coverage; `selected` is a consequence (`docs/records/harvest/collect_v3_admission/nw1b/calibrate.py:128`). Both entrypoints call the same recomputing qualification function before side effects (`docs/records/harvest/collect_v3_admission/nw1b/prepare_w1.py:26`, `docs/records/harvest/collect_v3_admission/nw1b/reissue.py:17`). |
| no exclusion of historical false drops from the denominator | PASS. Scoring includes every KEEP regardless of content eligibility or old flags (`docs/records/harvest/collect_v3_admission/nw1b/calibrate.py:93`). All four exact ids have parameterized regression coverage (`tests/test_seg_cp1.py:53`). |
| inspect the pre-collector-screen population | PASS. Independently imported the collector's `included(r)` predicate and streamed the feature population before merged, rotated and class exclusions. This matches the freeze implementation (`docs/records/harvest/collect_v3_admission/seg/freeze_truth.py:68`) and the collector's actual order (`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/build_w1_originals_v3.py:71`). |

## Independently reproduced acceptance: 5/5

| CP1 acceptance | Measured result | Verdict |
|---|---|---|
| 22 unique KEEP | Exact equality to NW1b brief §2; 22 entries, 22 distinct ids, no KEEP/DROP overlap. | Met |
| Exact published D and provenance | Nine ids listed below. Reconstructed six pinned gallery merges plus seven named owner issues, four overlapping. Rechecked pinned Git blob, brief, and ledger entries. | Met |
| Current union failure detected 4/22 | Candidate neighbour alone TP=9, FP=0, FN=0, TN=22; actual three-screen union TP=9, FP=4, FN=0, TN=18. Top-level gate=false, selected=null; gate main returns 1. | Met |
| 0 publish actions while failing | Real prepare/reissue entrypoints both stop at GATE_FAIL; audit hook observes 0 filesystem write attempts, detector stub observes 0 calls. Protected data hashes remain unchanged. | Met |
| Every required positive represented | 9/9 D, 7/7 independently joined C1 witnesses, 6/6 pinned-gallery merges; union detects all, no unresolved union witnesses. C1/gallery overlap=5. c068 remains a separate challenge outside D/gallery. | Met |

Frozen ledger SHA-256 independently recomputed: `f4448ea50daeb0297a0d9b6eb65f889ca772e3fb8b83547ae2efc58082e9f4f4`.

Exact D, independently reconstructed:

| Row id | Provenance |
|---|---|
| `gazette_modern--0020420cfe156a73--s000-l0039` | Named owner issue + pinned gallery merge |
| `gazette_modern--0020420cfe156a73--s000-l0138` | Named owner issue + pinned gallery merge |
| `gazette_modern--0020420cfe156a73--s000-l0141` | Named owner issue |
| `gazette_modern--0020420cfe156a73--s000-l0146` | Pinned gallery merge |
| `gazette_modern--0020420cfe156a73--s000-l0162` | Named owner issue + pinned gallery merge |
| `gazette_modern--0020420cfe156a73--s000-l0228` | Named owner issue + pinned gallery merge |
| `gazette_modern--1f7db88d63c02afa--s000-l0287` | Named owner issue |
| `gazette_modern--5af16c5d518d2ebb--s000-l0128` | Pinned gallery merge |
| `nlg--6146c0455e0103d2--s001-l0006` | Named owner issue |

Gallery provenance was fetched read-only with `git show <ledger.gallery_binding.commit>:docs/records/harvest/collect_v3/segmentation_gallery/examples.jsonl` in the collector checkout, using the full commit recorded for `83aaab5d`. Its SHA-256 and all 24 gallery entries match the ledger. The owner list was read from `docs/records/briefs/NW1b_neighbour_words_recalibrated.md:22` and `:49`.

The reduction from ten to nine is explicit and supported by pinned `sg1-07`: `kosmopolis--62ca52b56ebe780a--s005-l0051` is `readable_half_line_overrun`, described as “lower halves of the line above and upper halves of the line below”. That saved description does not establish a whole neighbouring word under the owner rule. The case remains diagnostic, not a new KEEP label. No native reading or new owner verdict is claimed. The eighth owner issue remains unidentified, with null id (`docs/records/harvest/collect_v3_admission/seg/calibration_ledger.json:33`). The one borderline remains nongating and has false predictions for all three screens and the union.

C1 provenance was independently reconstructed from both bound verdict files' `merged_two_lines` records and the bound card-key join, including detail and line number, and exactly matches the seven ledger records. `gazette_modern--2e613d9290dd13d4--s000-l0209` (c068) is represented outside D/gallery. Its neighbour observation is unavailable, but the historical merged hit establishes a true saved OR result; it is not described as a verified neighbour keep.

The independent pre-screen census reproduces **101,098 feature rows**, **33,301 content-eligible rows**, and ordered eligible-id SHA-256 `88563264cf6f6a103d2cbe4ee86b98ac3cd15fcb5b024f7955defe82e82e7f92`. All 34 ledger cases' merged/rotated observations, crop hashes, eligibility and saved neighbour measurements match their underlying records.

The four false drops are retained despite three being outside the present content allowlist:

| KEEP id | Content eligible | Historical merged | Candidate neighbour |
|---|---:|---:|---:|
| `gazette_modern--54876940c2de96c3--s000-l0062` | no | true | false |
| `gazette_modern--836a4d5d06d0f16d--s000-l0045` | no | true | false |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0062` | no | true | false |
| `kosmopolis--109d033afd51aea6--s000-l0019` | yes | true | false |

## Executed verification

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python \
-m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp1-sol-review \
tests/test_seg_cp1.py tests/test_neighbour_words.py tests/test_harvest_admission.py \
tests/test_adm5b_schema.py tests/test_adm5c_variants.py
```

**205 passed in 5.70s.** This includes all four exact false-drop ids, planted standalone-pass/union-fail, missing observations, rotated composition, duplicate/invented truth, stale/forged reports, and stop-before-side-effect regressions. This scoped rerun does not claim full-suite or staging qualification.

Executed `calibrate.main()` in-process with its two `Path.write_text` calls intercepted in memory, asserting each generated string is byte-identical to the existing calibration report/GATE_FAIL file. This reruns the gate script's real main without changing either artifact. It returned 1 and printed:

```json
{"gate": false, "keep": 22, "drop": 9, "union": {"tp": 9, "fp": 4, "fn": 0, "tn": 18}}
```

Calling `require_qualification()` independently raises `GATE_FAIL: actual segmentation union rejects owner KEEP or misses required witnesses`. Executed `seg/verify_cp1.py` with bytecode disabled: 9/9 protected snapshots unchanged, 10/10 bound source hashes unchanged, 28,798/28,798 manifest PNGs matched, both guarded entrypoints stopped, zero write attempts, zero detector calls. No calibration regeneration, freezing, detection, reissue, staging or live-run locking was performed.

## Protected artifacts against HEAD

This command produced **empty output**:

```sh
git diff HEAD --stat -- ':(glob)**/*admission*.json*' ':(glob)**/*admitted*.jsonl' \
  ':(glob)**/*decisions*.jsonl' ':(glob)**/crops_manifest.jsonl' ':(glob)**/*.png'
```

Independently read each protected tracked blob with `git show HEAD:<path>` and compared its SHA-256 and bytes with the working file. All five match; paths below are relative to `docs/records/harvest/collect_v3_admission/`:

| File | SHA-256, identical in HEAD and worktree |
|---|---|
| `w1_originals_v3_admission.jsonl` | `155ed83b1274f6cd4e2f956471513b2c3fa98cc3c32ec9bf2fc0461bb33913db` |
| `w1_originals_v3_admission_receipt.json` | `5c68d2c77ad06436272c9503d67792b17852c80fbbd082bf50f025d368fb2d84` |
| `w1_originals_v3_admitted.jsonl` | `b6d13fa8bb4b07be632e299fd650cd75dd80348ecf0e0fd9e5cb34bdb6c72bfe` |
| `w1_originals_v3_decisions.jsonl` | `a95078fa8e5ecd8af7e94d822b94f5d7ae63458c317319a582fdb64b78c59081` |
| `crops_manifest.jsonl` | `dc3b1951687c951a1fe2b928810df8d62612ab2e582869da970a14d6690f2a9a` |

For staged crop PNGs, independently parsed the **HEAD** manifest, rather than trusting the working manifest: **28,798 SHA-256 checks, zero missing/mismatching crops**. Also compared all tracked PNG blobs against HEAD: 1,573 present PNGs match; eight unrelated historical PNG paths are absent with Git `S`/skip-worktree flags under the configured sparse exclusions (`docs/records/harvest/mixed/visual_samples/` and `docs/records/harvest/page_reads_v1/failure_images/`). These are not modified CP1 crops, and no hash equality is claimed for absent sparse files.

The two pre-existing untracked census admission/receipt artifacts have no HEAD blob. Their hashes independently match the manifest committed in `84b5df8d` (`08ab77820128fb80caf8d3f80a0f42f36b9a9e4a212f7f532c0202091072ec0f` and `4f32bd887312dd6ab404c698c413016efe4ae6008fa896dee1561fe95b9c8923`, respectively), and the CP1 protected-before snapshot. They remain separately classified ADM5c leftovers; an empty tracked diff alone would not establish their status.

All grouped and preserved-draft file hashes still match `CP1_COMMIT_LIST.json`; `git diff --check` passes. Review output is confined to this file; synthetic test output is under `/tmp`.

SEG-CP1 review: PASS | blocking: 0 | high: 0 | acceptance: 5/5 met | publish actions: 0
