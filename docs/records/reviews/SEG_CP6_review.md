# SEG-CP6 review

18 October 2026. **PASS for CP6**, with two medium diagnostic findings. This does not qualify the combined segmentation gate or authorize publication.

Reviewed HEAD `f6dcb1898f3753716169e4d203c07db0b8f6b0f2`, the uncommitted 15-file CP6 scope in `docs/records/harvest/collect_v3_admission/seg/CP6_COMMIT_LIST.json`, and the CP5c additions committed in `dc47b8bb`. Authority: ASTRA-SEG1 Numbered PLAN item 6 and the explicit CENSUS2/3 and CP5c rulings in `docs/records/briefs/SEG_CP6_build.md:16` and `docs/records/briefs/SEG_CP5c_rulings.md:5`. The short `seg/` manifest reference resolves to `docs/records/harvest/collect_v3_admission/seg/`, not a repository-root directory. Unrelated stage-crops/NW drafts were excluded. Only this review was written in the worktree; pytest temporary files were confined to `/tmp`.

## Findings by severity

### Blocking — 0

None found in the reviewed scope.

### High — 0

None found in the reviewed scope.

### Medium — 2

**M1: CP5's content-eligibility diagnostic omits active rejection rules.** `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:97`, duplicated at line 189 and consumed by `text_rule_composition` at line 241. The hard-coded whitelist omits `low_confidence` and CP6's `lookalike_only_word`; it also omits `tall_box`. Consequently an otherwise valid `bsb_poly1850` row labelled `ἑλληνικὸς λόγος` at confidence `0.88` is called text-eligible despite failing confidence. A declared Cyrillic `archive_b24878935`/`wave=cyrillic` row labelled `Это чистая русская строка coco` is called eligible despite failing `lookalike_only_word`. A Greek row with bbox `[0,0,100,18]` and page median height `10` likewise passes the whitelist despite `tall_box`. I executed all three counterexamples independently. The height rule may intentionally remain outside a narrowly defined text predicate, but confidence/lookalike omissions make the current composition misleading even under that interpretation.

Rechecking the saved eligible native cases against the complete current non-segmentation failure set found **0 affected rows** in this snapshot. This is a diagnostic defect, not an observed published admission error or failed CP6 text-parity acceptance. Before using this field to select a later content-eligible population, share a named eligibility composition with admission, explicitly state the height-rule boundary, and regress these counterexamples. The CP6 receipt already discloses this finding at `docs/records/harvest/collect_v3_admission/seg/CP6_RECEIPT.md:59`; disclosure does not fix it.

**M2: CP5's acceptance summary does not require a resolved, passing composed union.** `docs/records/harvest/collect_v3_admission/seg/verify_cp5.py:213`. The four `requirements` only inspect standalone orientation catches/false drops, stored horizontal-witness counts, and explicit unknown statuses. They do not constrain `unresolved_required` (computed at line 183), union KEEP losses, or unavailable separator coverage. In the controlled native diagnostic replay described below, the normal separator loader rejected the stale inventories, leaving **22 unresolved required union outcomes and zero verified KEEP**, yet `acceptance.met` still reported **4/4**. The unmodified verifier's earlier CP4-binding assertion correctly stopped the ordinary CP6 replay; that does not cover independently missing/corrupt separator inventories when the CP4 binding is otherwise current. No public admission was produced and `gate=False` remains, so this is a medium qualification-reporting defect rather than a demonstrated unsafe publication. Require the union checks and required evidence availability in the reported acceptance predicate, while retaining the coordinator's explicit orientation-only unknown allowance; add a missing/corrupt-separator regression.

### Low — 0

None found in the reviewed scope.

## CP6 Sol code-review criteria, verbatim and individually

| Criterion | Verdict and evidence |
|---|---|
| “no lunate/lookalike correction imported accidentally” | **PASS.** `greekocr/harvest/text_primitives.py:61` retains only dot-above replacement, NFC and whitespace normalization. `greekocr/harvest/admission.py:545` detects/rejects ruled secondary-script lookalike words without replacing characters. The shared table is `greekocr/harvest/lookalikes.py:9`; bench imports it at `greekocr/_vendor/bench/e1_readout.py:19`. Lunate/homoglyph/zero-width preservation passed at `tests/test_seg_cp6.py:85`. |
| “no script/language inferred from label instead of declared source/class” | **PASS under the explicit CENSUS3 ruling.** `greekocr/harvest/admission.py:428` resolves declared source, wave, class and document; unknown identities raise. The label-dependent Latin → `mixed_greek_latin` reclassification at line 554 is the specifically authorized exception in `docs/records/briefs/SEG_CP6_build.md:17`, separately recorded in `CP6_RECEIPT.md:28`; it is not an unruled cleanup change. No language guessing activates Serbian. |
| “no double-counting NFD marks” | **PASS.** `greekocr/harvest/text_primitives.py:40` returns one base-script vote per NFC letter and none for inherited marks; `greekocr/harvest/admission.py:531` normalizes before counting. Canonically equivalent Greek/Cyrillic inputs and U+0345/U+0301 passed at `tests/test_seg_cp6.py:61`. Codec punctuation overrides passed at line 74. |
| “no global extension of codec v2” | **PASS.** `greekocr/harvest/serbian.py:9` holds the exact ordered extension. `greekocr/harvest/admission.py:446` activates only declared Serbian documents in the Cyrillic wave, supplementing the existing Serbia source; line 560 creates a local atom union. The base codec remains immutable. Non-Serbian rejection and document scope passed at `tests/test_adm5c_variants.py:30` and `tests/test_seg_cp6.py:53`. |
| “no changed thresholds hidden as cleanup” | **PASS.** `greekocr/harvest/admission.py:571` retains height 1.7, standard/heading letter limits 10/4, confidence .89, one-third nonletters and numeric 4-digit/60% rules. Source/class variants remain explicit at line 345. Wave-0's Roman exemption remains at line 87; standard mixed-word rejection has none at line 548. Independent fixture regeneration and corpus parity below found no unruled changes. |

The deliverable uses the existing validating loader (`greekocr/harvest/text_primitives.py:8`, line 25), exposes codec kind/script metadata at line 30, and shares NFC/NFD/mark primitives from `labelfix.text`. Admission and labelfix use explicit delimiter modes at `greekocr/labelfix/text.py:131`; labelfix remains whitespace-tokenized while admission also splits punctuation and `=/-`. Normalization has one implementation. The numeric `4.547.331`/`p. 12`, heading, mixed-word, unknown-source/wave and byte-preservation tests all ran.

## Acceptance independently reproduced — 3/3

| CP6 acceptance | Fresh measurement | Verdict |
|---|---|---|
| **0 unintended text-rule/label changes** | **120/120** current fixture projections match ruled results; **0** label/normalization-trace changes. I separately regenerated **120/120** stored `before` results from HEAD admission code and **120/120** `ruled` results from the hash-bound census implementation, in memory. **40/120** fixture public-field changes are the explicitly ruled CENSUS2/3 changes. Census: **271,987/271,987** ordered rows match, **0** public text-field differences and **0** normalized-label differences against the independent old normalization expression. | **MET** |
| Exact codec/extension hashes retained | **2/2** exact: codec SHA `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`, equal to HEAD; ordered Serbian extension SHA `202a906c5f4b96d4e06d01783e9cffad20f4626db8eea4dc80a9ca3ed1105850`, equal to the collector inventory. Additional document/table hashes match CENSUS3, **2/2**. | **MET** |
| **All existing admission regressions pass** | **633 passed in 8.76s**, no failures/skips/xfails, with the exact offline qualification selection below. This includes every admission/ADM5/neighbour/CP1–CP6 test file and offline labelfix tests. | **MET** |

I reran `verify_cp6.py` rather than reading its saved JSON as proof. It hashes the reference itself and compares complete public rows in ordered lockstep at `docs/records/harvest/collect_v3_admission/seg/verify_cp6.py:142`, after excluding only segmentation failures/status. Reference SHA is **`ef694589fa0e8e6875ac712159222d19177e0d02213d48031fa92ff1efbc6451`**. Reproduced totals: **269,498 text passes; 2,489 failures; 6,799 reclassifications**. The three input hashes and reference hash were checked before/after. No admission JSONL was generated.

Additional reproduced hashes: Serbian documents `f101a0893a020e0851c7467c6d14f599c3aed5ec97185bffcf9485eb22a72c73`; shared ordered lookalike table `f5dddff62b61fca9af6b1fb115ac23ef3ece4bd50e14e9031c25ec4f51ed7acd`. The shared lookalikes file is byte-identical to the census worktree. The deferred candidate-label/owned-ink design line is present, without implementation, at `CP6_RECEIPT.md:61`.

## CP5c and existing segmenter reuse

**Regional inheritance: PASS for the implemented caller contract.** `greekocr/harvest/orientation_screen.py:106` only changes unknown local axes. Crop-centre membership and agreement of every overlapping discovered/measured region are required at lines 119–124; horizontal axes remain unchanged. Mixed/unresolved regions abstain. `verify_cp5.py:85` validates the page source hash and single-frame identity before using `measure_page_regions`; `orientation_screen.py:96` delegates to existing `discover_directions`, `axis_regions`, `measure_orientation(use_osd=False)` and `resolve_regions`. Saved regional decisions demand revalidation at line 54. The new regional/mixed/horizontal/non-membership regressions passed at `tests/test_seg_cp5.py:217`.

**Unknown → orientation-only admission: PASS.** `greekocr/harvest/orientation_screen.py:198` makes only the orientation policy fail open. The measured value remains unknown; line 210 prevents verified-KEEP credit. Structural/crossing positives remain positive, and geometry unavailability still fails closed. These distinctions passed the CP5 tests, including structural-positive preservation at `tests/test_seg_cp5.py:256`.

**CP7 hooks:** the CP6 verifier independently recomputed the saved unknown IDs and membership/tall-text exclusion unions: **1,715 cases, 110 unknowns, eight source × class groups, zero accounting differences** (`verify_cp6.py:45`). The hooks at `verify_cp5.py:225` describe the selected historical/calibration/challenge population, not full pre-screen population coverage. They are suitable diagnostic hooks; CP7 still needs its own full-population accounting and fresh selection. M1 applies to their adjacent eligibility diagnostic.

**Binding limitation of the native CP5 replay.** The unmodified `verify_cp5.py` was executed and stopped at line 133: its stored CP4 binding contains pre-CP6 admission SHA `9b5566e4…`, whereas the current SHA is `d0500c33…`. Independently comparing every binding field found exactly this one difference. This is correct stale-evidence rejection, not a passing current CP5 qualification. For diagnostic isolation, a second execution compiled the verifier in memory, replacing only that assertion with assertions that the sole delta is precisely these two admission hashes and that the ledger still matches. No file or saved receipt was changed. Its fresh orientation/hook results are recorded below; separator inventories remain subject to their normal binding checks. Historical CP3/4 and full-union qualification must be regenerated/rebound under the final candidate before CP7; the CP6 3/3 claim does not imply that has occurred.

That diagnostic execution completed in **75.17s**. Fresh standalone measurements: **4/4 rotated** (**2 measured + 2 regional**), **0/22 KEEP false drops**, **0/11 upright false drops** (**0/5** text-eligible controls), KEEP axes **17 horizontal + 5 unknown**, historical axes **1,576 vertical + 105 unknown** out of **1,681**. All four rotated witnesses have unknown polarity, correctly without suppressing vertical exclusion. Hook IDs/counts exactly match the saved hooks: **110 unknown, 105 old-policy exclusions, eight groups**. The five KEEP unknown IDs are `bsb_poly1850--e18cacecef3b4590--s005-l0076`, `gazette_modern--0d0b2233a81e355c--s000-l0019`, `gazette_modern--4b5e54c14bfb5810--s000-l0031`, `gazette_modern--54876940c2de96c3--s000-l0062`, and `kosmopolis--109d033afd51aea6--s000-l0019`. Native text-eligibility diagnostics report **717/1,715**, **19/22 KEEP**, **1/4 rotated**, subject to M1. Full observation-dictionary equality is not expected because orientation evidence includes fresh elapsed timings.

The historical CP4 fields read **C1 6/6 and gallery 6/6**; those structural measurements were reused, not freshly reproduced by the CP5 diagnostic. Its current full union has **22 unresolved required outcomes, zero verified KEEP**, because separator bindings reject the changed admission hash. Thus I do **not** reproduce the older receipt's complete resolved-union claim under current CP6 bytes. The diagnostic nevertheless prints acceptance **4/4**, establishing M2. It reports zero runtime forbidden attempts and verifies all **28,798** retained PNGs. The CP5c orientation behavior itself is reproduced; final union qualification remains a later candidate-binding obligation.

**F2/F3 reuse: PASS within CP6/CP5c scope.** No `glyphs/`, `pages/` or collector source changed. Cache consumption at `greekocr/harvest/neighbour_words.py:92` calls the read-only, source/frame/options/code/payload-bound loader (`geometry_observations.py:84`); missing geometry does not invoke page detection. Native ownership and component identities survive `ownership.prepare_row/box_hits`, and frozen foreign-mask measurement calls the original core at `geometry_observations.py:192`. The existing neighbour candidate calls `letter_boxes`, `straighten_edges` and `BoundaryEvidence` at `neighbour_words.py:177`, using each neighbour's x-height at line 185. The old graph still exists as legacy code at line 54, but standard admission explicitly does not invoke it at `admission.py:592`. CP6 adds no detector, word/angle heuristic, masking or ownership retuning. Frozen ownership SHA reproduced as `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. These checks do not promote the earlier geometric word proxy to semantic word truth.

## Preservation and execution evidence

The CP6 guard was rerun successfully: **15 exact files**, unchanged base HEAD, all declared file/dependency hashes correct, no staging/commit/publication. I additionally hashed all present tracked PNG/admission-JSON/manifest candidates directly against their HEAD blobs: **1,579 files, including 1,573 PNGs; zero differences**. Another **24** candidates are absent sparse-checkout entries (`git ls-files -v` reports `S`), not deleted/modified files.

The HEAD crops manifest itself has SHA **`dc3b1951687c951a1fe2b928810df8d62612ab2e582869da970a14d6690f2a9a`**, identical to the working copy. I parsed the **HEAD blob**, then hashed all **28,798** retained PNGs against its entries: **zero differences**. Thus ignored/untracked retained PNGs are checked transitively against HEAD's manifest, not falsely claimed to have individual HEAD blobs. All **nine** protected snapshot artifacts match; **eight** have HEAD blobs and match them. `ADMISSION_CENSUS_20261017.json` is untracked and only snapshot-bound, SHA `d6f088c456605b7026af83361c2f468c5b31beef10073ebfc2b6dbe916fbfe3b`; no HEAD comparison is possible for it.

No live-run write/lock was performed in this review. The sandbox makes that root read-only; measurement audit hooks rejected file-write opens and mutation attempts and reported **zero forbidden attempts**. CP6 read only `W1/features.jsonl` in that root, with unchanged SHA `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c`; the native CP5 diagnostic also read source crops/pages. Hashes demonstrate present byte preservation, not the absence of any transient write by an earlier process before this review. No historical syscall trace was supplied, so that stronger retrospective claim cannot be independently established. Review publish actions: **0**.

Reproduction commands (required collector interpreter, no bytecode/cache writes):

```sh
export PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1
../greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/seg/verify_cp6.py
../greek-ocr-toolkit-sol-collect/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp6-review-pytest tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_round1_admission_outputs.py tests/test_seg_cp1.py tests/test_seg_cp2.py tests/test_seg_cp3.py tests/test_seg_cp4.py tests/test_seg_cp4c.py tests/test_seg_cp5.py tests/test_seg_cp6.py tests/labelfix --ignore=tests/labelfix/test_capture.py
../greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/seg/guard_cp6_commit.py
```

The excluded capture test is an HTTP/localhost labelfix integration test outside offline admission qualification; no admission test was excluded. Original receipt/fixture/log/measurement/manifest files were left unchanged. No reader, OCR, training, sampling, replay, preparation or publish job was launched.

SEG-CP6 review: PASS | blocking: 0 | high: 0 | acceptance: 3/3 met reproduced | publish actions: 0
