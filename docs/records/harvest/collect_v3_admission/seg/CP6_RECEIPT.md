# SEG-CP6 receipt

Authority: ASTRA-SEG1 review 1, Numbered PLAN item 6, plus the explicit CP6 coordinator rulings in `docs/records/briefs/SEG_CP6_build.md`. Base HEAD: `f6dcb1898f3753716169e4d203c07db0b8f6b0f2`. Scope is text consolidation and review of CP5c. No reader run, new detector, geometry preparation, ownership change, masking, admission publication or later-checkpoint execution.

## Acceptance numbers

| Plan acceptance requirement | Measured value | Verdict |
|---|---|---|
| 0 unintended text-rule/label changes | **0** differences against ruled text results on **120/120** frozen local fixtures; **0** CENSUS3 public text-field differences on **271,987/271,987** rows; **0** label changes against the independent pre-cleanup normalization expression over the entire census | MET |
| Exact codec/extension hashes retained | **2/2** exact: base codec and ordered Serbian extension; document and lookalike bindings also match CENSUS3, **2/2** | MET |
| All existing admission regressions pass | **633 passed**, including standard/legacy admission, schema, variants, original-crop neighbour, CP1–CP5, CP6 and offline labelfix regressions | MET |

**3/3 CP6 acceptance requirements met.** This does not qualify segmentation publication; existing GATE_FAIL and unresolved admission status remain. The orientation finding below concerns diagnostic accounting, with zero affected rows in the saved eligible cases, and is not hidden as a passing admission claim.

## Implementation and declared boundaries

`greekocr/harvest/text_primitives.py` wraps the existing validating `greekocr._vendor.train.cer.load_codec`, checks NFD policy and byte stability, and exposes the artifact's kind/script/policy metadata and raw-byte hash. Standard script votes use NFD base metadata once per NFC letter; combining marks have no votes. One Unicode-name fallback serves out-of-codec and legacy diagnostics; bench `common.script` delegates to it. No v2 artifact bytes changed.

Both `normalize_label` and standard `evaluate` use the same named `admission-dot-nfc-v1` implementation, retaining the ordered dot-above/NFC/whitespace trace. Lunate sigma, homoglyphs and zero-width characters are not corrected. `labelfix.text` supplies NFC/NFD, mark groups and explicit delimiter modes. Its whitespace tokenization is preserved, while admission retains internal Unicode punctuation and `=/-` boundaries. The broader Unicode-M inventory predicate is explicit so spacing/enclosing marks with ccc=0 do not accidentally change legacy classes.

The source/class expectation table, confidence 0.89, standard 10-letter minimum, heading 4-letter minimum, one-third nonletter limit, numeric 4-digit/60% shape rule and 1.7 height heuristic stay explicit in admission. Wave-0 retains its historical Roman exemption; standard R6 retains no Roman exemption. `serbian.py` shares exact extension data and document IDs; source/document activation stays in the admission table. No collector, `glyphs/` or `pages/` source file is changed, and frozen ownership parameters remain `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`.

## Intentional semantic changes and rulings

The coordinator explicitly required consolidating committed CENSUS2/CENSUS3 rules into this branch. This is the sole intentional semantic change, separately recorded here rather than attributed to cleanup:

- **CENSUS2, `3f93d204`:** activate the exact Serbian extension on declared Cyrillic-wave documents `cyrillic:7235f8d0` and `cyrillic:975289f3`, in addition to the established `serbia` source. Language comes from catalogue/document metadata, not label guessing.
- **CENSUS3, `c8a83470`, coordinator confirmation `504bdb1e`:** the declared `cyrillic` class permits whole Latin secondary words; the declared `latin` class permits whole Greek secondary words and reclassifies to `mixed_greek_latin` when a distinguishing Greek word is present. `lookalike_only_word` rejects secondary words whose every NFC letter has a primary-script counterpart. Mixed-script words still fail R6, with no lookalike exemption and no character folding. Reclassification is recorded even if another rule rejects the row, exactly as CENSUS3.
- The exact shared `harvest/lookalikes.py` is copied from that read-only worktree. Bench readout imports its table; no duplicate table remains. Public result diagnostics add CENSUS3's `class_original` and `lookalike_only_words`; receipts bind the document and lookalike tables. Existing on-disk admissions retain their prior schemas and bytes.

The fixture file contains both pre-CP6 ADM5c results and independently evaluated CENSUS3 results. **40/120** fixtures change prior public fields under these rulings (including expected-script metadata); **0/120** labels or normalization traces change. Corpus parity is against CENSUS3, not obsolete ADM5c decisions: **269,498** text passes, **2,489** text failures, **6,799** reclassifications, **0** public text-field differences. Segmentation rules and the unqualified segmentation pass status alone are excluded from the comparison. No census admission JSONL was generated or overwritten: ordered comparison is in memory and stdout contains measurement totals only.

## Exact hashes

| Binding | SHA-256 |
|---|---|
| Vendored codec v2 bytes, unchanged versus HEAD | `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9` |
| Ordered UTF-8 Serbian extension `јћњљђџЈЋЊЉЂЏ` | `202a906c5f4b96d4e06d01783e9cffad20f4626db8eea4dc80a9ca3ed1105850` |
| Sorted Serbian document IDs, compact JSON | `f101a0893a020e0851c7467c6d14f599c3aed5ec97185bffcf9485eb22a72c73` |
| Ordered shared lookalike groups, compact UTF-8 JSON | `f5dddff62b61fca9af6b1fb115ac23ef3ece4bd50e14e9031c25ec4f51ed7acd` |
| Read-only CENSUS3 reference `ADMISSION_CENSUS_20261018b_admission.jsonl` | `ef694589fa0e8e6875ac712159222d19177e0d02213d48031fa92ff1efbc6451` |

## Sol code-review criteria, applied individually

1. **“no lunate/lookalike correction imported accidentally” — PASS.** `text_primitives.py:61` performs only the current normalization; `admission.py:545` checks scripts/lookalikes without replacing text. `lookalikes.py` is the sole table source. The newly ruled rejection is explicit above.
2. **“no script/language inferred from label instead of declared source/class” — PASS with declared CENSUS3 exception.** `admission.py:428` resolves source/wave/class/document first and raises for unknown identities; `admission.py:554` applies only the explicitly authorized secondary-word reclassification. No new language guessing is introduced.
3. **“no double-counting NFD marks” — PASS.** `text_primitives.py:40` decomposes NFC letters to their base vote and ignores inherited marks. Canonically equivalent Greek/Cyrillic cases, spacing atoms and mark-only inputs are covered in `test_seg_cp6.py`.
4. **“no global extension of codec v2” — PASS.** `admission.py:560` creates a per-evaluation atom union only under the table's Serbian codec scope. The exact artifact hash is unchanged; non-Serbian documents retain coverage failures.
5. **“no changed thresholds hidden as cleanup” — PASS.** The threshold/class-variant regressions pass and the frozen results change only under the separately ruled CENSUS2/3 policies. Geometry decisions are not rewritten by this consolidation.

## CP5c review and finding

**Regional inheritance — reviewed, no defect found in the shipped caller path.** `orientation_screen.py:106` only changes an unknown axis, requires a centre-containing region and agreement of every overlapping region, preserves measured horizontal decisions and leaves mixed/unresolved regions unknown. `verify_cp5.py:85` binds page source bytes/frame before measuring regional context. Saved inherited observations require page revalidation. Existing CP5 regressions cover unknown/vertical, mixed-region abstention, measured-horizontal preservation and saved-regional rejection.

**Unknown → orientation-only admit — reviewed, no defect found.** `orientation_screen.py:191` keeps measured state distinct from policy composition: unknown axis contributes no orientation drop, does not become a verified keep, cannot cancel a structural positive, and cannot bypass fail-closed geometry. CP5c regressions exercise those distinctions.

**Hook accounting — reproduced within its recorded scope.** The saved **1,715** historical/calibration/challenge cases contain **110** unknowns in **8** source × class groups. Recomputing unknown IDs and the union of historical-membership/tall-text exclusions gives **0** counting differences. This is a selected historical/challenge population, not a full pre-screen population count; no CP7 sampling or population extension was performed.

**CP6-F1 — medium: CP5's text-eligibility diagnostic uses an incomplete hard-coded rule list.** `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:97` omits `low_confidence` and the now-consolidated `lookalike_only_word` (and handles neither the separate tall-box heuristic nor a complete general rule composition). Consequently `text_rule_composition` at line 241 is not a general content-eligibility predicate. Reproduction: an otherwise valid Greek row at confidence **0.88**, and a declared Cyrillic row ending in **coco**, both pass that filter despite failing the respective text rule. The CP6 verifier records both counterexamples. Rechecking all saved rows marked eligible finds **0** affected native rows in this snapshot. No published file is affected, and CP5's geometric/axis tests still pass. Reported for correction before this diagnostic is used to build a later content-eligible population; the CP5 verifier is left read-only in CP6.

Coordinator's deferred design line (not implemented in this cycle): *candidate label check: label tokens vs owned-ink extent, from the existing ownership measure, for Google labels that append words whose ink is not in the crop (failure mode of C1 card c068)*.

## Reproduction and safeguards

Use the required interpreter with `PYTHONPATH=.` and `PYTHONDONTWRITEBYTECODE=1`:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/seg/verify_cp6.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp6-qualified tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_round1_admission_outputs.py tests/test_seg_cp1.py tests/test_seg_cp2.py tests/test_seg_cp3.py tests/test_seg_cp4.py tests/test_seg_cp4c.py tests/test_seg_cp5.py tests/test_seg_cp6.py tests/labelfix --ignore=tests/labelfix/test_capture.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/seg/guard_cp6_commit.py
```

Evidence: `CP6_verification.json`, `CP6_text_fixtures.json`, `CP6_pytest.log`, and `CP6_COMMIT_LIST.json`. The extra labelfix HTTP capture test was tried in a broader run; its localhost bind was blocked by network-OFF. It is excluded from the offline qualification command; no admission regression is excluded. Synthetic test files/crops are created only under pytest's `/tmp` fixtures; existing admission artifacts/crops are never regenerated.

The verifier denies runtime file writes, socket activity, subprocesses and filesystem mutations; its observed forbidden-attempt list is empty. Input/census hashes are checked before and after, all **9** protected artifact hashes are unchanged, and the guard independently compares tracked protected bytes with HEAD and all **28,798** retained PNG hashes with the unchanged manifest. The guard validates exact changed-file scope and all file/dependency hashes against the base HEAD, including read-only census and interpreter dependencies. The manifest itself is excluded from its own hashed list to avoid self-reference. It stages, commits and publishes nothing. Existing unrelated `.gitignore`, stage-crops drafts and NW scratch files are excluded from the CP6 commit scope. No live-run path was opened for writing or locking; the only live-run input read by the CP6 measurement is `W1/features.jsonl`.

SEG-CP6: done | acceptance: 3/3 met | unintended text/label changes 0; exact codec/extension hashes 2/2; regressions 633/633 | publish actions: 0 | tests: 633 passed
