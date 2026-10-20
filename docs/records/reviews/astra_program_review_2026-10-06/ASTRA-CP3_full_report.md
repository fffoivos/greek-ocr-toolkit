# ASTRA-CP3 — checkpoint 3 / P9 certification of release v3 and benchmark 0.2

**NOT CERTIFIED for wave 2: release v3 integrity passes; benchmark seal03 contains one byte-identical crop in both DEV and TEST.**

Reviewed 2026-10-20T07:23:56+03:00. Repository HEAD `fd43e1c74df51f18e37924c188d7de44f6532af5`. Independent certifier review, with no implementation changes or delegation. Repository and Clariden were read-only. Remote work used foreground SSH reads and Python counting/hashing; no submission, remote output, or background job. All new evidence is in this scratch directory.

Repository paths below are relative to `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3`. `$W` means `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Findings, most severe first

### H1 — HIGH: DEV and TEST contain the same crop bytes

**Evidence:** `$W/benchmark_0.2/seal03/benchmark_v02_test.jsonl:2209` and `benchmark_v02_dev.jsonl:422` both reference `images/4b22b2ff40ca5b79195fd9e735a7d15c25f56bb3dac2d8eb904a16d02ff0dafb.png`, with literal reference `НБС`:

| Split | Row | Edition | Quota scope |
|---|---|---|---|
| TEST | `serbia--d6030713c8d88c96--s005-l0006` | `122c52e696f5f8931b1b06c37362373dc2bdb2739f9a17b80a30b1917c100e99` | `test:font_extremes:small` |
| DEV | `serbia--27b182bf4116728f--s009-l0006` | `b864d188c49355b3268530b7e8008b01539b52ee2b18cb5fe2780db40396d0ed` | `dev:font_extremes:small` |

Local witnesses: [readout:923](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/harvest/collect_v3_admission/seal02/inputs/candidates_readout.jsonl:923) and [readout:1223](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/harvest/collect_v3_admission/seal02/inputs/candidates_readout.jsonl:1223); retained at [final_list:2039](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/artifacts/lf1/prod/final_list.jsonl:2039) and [final_list:2216](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/artifacts/lf1/prod/final_list.jsonl:2216). I hashed every sealed image and visually inspected [the native duplicate](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/physical_samples/00.png). It is a repeated library mark, not merely equal text in distinct images. There are **2,691 rows, 2,690 unique image hashes, exactly one cross-split hash collision, and zero cross-split edition-ID overlaps**.

**Failure scenario:** DEV-based inspection, tuning or selection exposes an identical TEST observation. Edition separation alone misses the collision. Its extent is bounded to one three-character crop; this is not evidence of broad training leakage. It nevertheless defeats an independent DEV/TEST freeze before wave 2. The builder copies images by hash at [build_suite02.py:234](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/harvest/collect_v3_admission/seal02/build_suite02.py:234), but never rejects a hash used by both panels.

**Fix:** preserve seal03 as evidence; remove the DEV duplicate through an explicit evaluation-overlap exclusion, and use an eligible unused reserve in the **same split + quota_scope + source**, or report UNFILLED. `serbia--9caa9fc02f50cad6--s000-l0015` is an unused LF1-OK reserve in `dev:font_extremes:small`, source `serbia`, overdraw_order 3; revalidate its crop against both panels before selecting it. Preserve the original LF1 verdict rather than fabricating a text/crop fault. Make selection and sealing enforce cross-panel crop disjointness, regenerate the final-list/receipt bindings, seal a new immutable attempt, and repeat the membership/hash/exposure checks. Do not move split2 editions or take rows from training.

### M1 — MEDIUM: LF1 “OK” does not certify diacritics; programme wording overstates reference accuracy

**Evidence:** [programme:67](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md:67) says the text is what the image shows. In contrast, [LF1 brief:22](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/briefs/LF1_last_filter_check_tool.md:22), [prompt:72](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/artifacts/lf1/prompts/lf1.md:72), and [mapper:54](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/artifacts/lf1/tools/lf1.py:54) explicitly exclude mark-only errors from the verdict. This is deliberate and consistent with the existing reader qualification limit in [reader handover:10](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/records/harvest/sol_reading/HANDOVER.md:10); I do not treat it as an unauthorized implementation change or require unqualified Sol mark decisions to become truth.

I joined all **2,691 retained rows** to the effective original reader answers, including vertical overrides, and checked answer/key hashes against their run receipts: **0 missing answers and 0 custody mismatches**. The recorded marks are **1,756 y / 97 n / 838 na**; the 97 diagnostic flags are **83 TEST + 14 DEV**, including 23 polytonic, 11 dictionary/journal, 11 monotonic, and 2 vertical rows. These are **reader flags, not 97 independently confirmed label errors**. One firsthand counterexample is `$W/benchmark_0.2/seal03/benchmark_v02_test.jsonl:21`, `bsb_poly1850--2032df1e3e983f1d--s000-l0011`: the image shows initial **Ἀθηναίων**, while the unchanged reference starts **Αθηναίων**. Native [image](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/physical_samples/11.png) and nearest-neighbour [zoom](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/physical_samples/11_zoom.png); full answer provenance in [local_answer_audit.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/local_answer_audit.json).

**Failure scenario:** interpreting LF1-OK as accent-qualified ground truth can penalize a correct mark prediction or misstate evidence for a correction arm. **Fix:** explicitly describe the suite as pipeline-reference, letters/crop-filtered, with diacritics unqualified; retain the diagnostic flags in the evidence and scope mark-related claims accordingly. Any stronger qualification requires an authorized qualified audit, without silently substituting reader text for references. The suite's existing `diagnostic_only` status is appropriate.

### M2 — MEDIUM: programme size and coverage prose is stale relative to the sealed instrument

**Evidence:** [programme:37](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md:37) and [programme:59](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md:59) say 2,400/600 and “15 classes”; the actual 16-class table sums to **2,460/615**. Its authorized-revision paragraph at line 62 describes **candidate-stage** 15/16 TEST and 11/16 DEV quota completion; these must not be carried forward as sealed coverage.

seal03 has **16/16 nonempty TEST classes but only 2/16 full quotas**, and **14/16 nonempty DEV classes, 6/16 full quotas**. DEV historical Russian and dictionary/journal remain empty. Modern Cyrillic contains only Serbian: **40 TEST / 8 DEV**, not a modern-Russian/Bulgarian/Ukrainian evaluation. Counts and deficits in the machine-readable seal are correct.

**Failure scenario:** sizing power or interpreting “all classes filled” from the old prose misrepresents the actual experiment. **Fix:** publish the sealed table below, distinguish nonempty from quota-complete coverage, and state initial supply deficits separately from LF1 losses. No easier-source substitution or extra training subtraction is justified.

### L1 — LOW: LF1 summary still names pre-LF4 hashes at current paths

[LF1_FINAL.md:12](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/labelfix/spellcheck/LF1_FINAL.md:12) and [NIGHT_STATE.json:52](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/programme_20261019/NIGHT_STATE.json:52) retain final-list SHA `75fe0dbc…`; current list/receipt hashes are `0fa4a1fe…` / `00016527…`, as correctly recorded in [LF4_REPORT.md:40](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/labelfix/spellcheck/LF4_REPORT.md:40) and bound by seal03. Local and remote comparisons both find **identical 2,691-key membership, 64 changed `replaces` values, and zero other per-row field changes**; order also changed. **Failure scenario:** a consumer following the older summary binds the superseded pairing. **Fix:** label the older hashes as v1 historical and link the LF4 identities. This is not a seal03 hash failure.

## Cleared items and independently measured results

### Release v3 and training exposure — PASS

The complete admitted-train scan, including streaming SHA-256, yields:

| Parent | Admitted train | Released |
|---|---:|---:|
| `collect-v3-W1-20261018-0524` | 50,736 | 50,736 |
| `collect-v3-W2-20261018-0524` | 117,901 | 117,901 |
| `collection-v2-train` (v_c admitted rows) | 196,234 | outside release v3 scope |
| **Total** | **364,871** | **168,637** |

- Release membership equals the complete W1/W2 admitted-train subset: **0 missing, 0 extra, 0 duplicate keys, 0 duplicate crop hashes**. All decision digests, final labels and crop fields match their admitted rows.
- I compared **168,637/168,637 labels directly as UTF-8 bytes with `old_label` in the two bound raw imports**; **0 mismatches**, and both complete import hashes match their bindings. The independently seeded sample is 2,500 rows: W1 **733**, W2 **1,767**, seed **202610200731**. All **2,500/2,500 actual release-crop file hashes** match the bound crop SHA. Sampling verifies these crop files, not a fresh rehash of all 168,637 files.
- **0 applied-edit rows and 0 normalization rows** in released W1/W2; `release_v3_edits.jsonl` is **0 bytes**. Empty edits are supported by the raw comparison, not inferred from the exporter receipt.
- Across all **364,871** training admissions, versus both all **3,341 candidates** and the **2,691 sealed rows**: **0 edition-ID overlaps, 0 parent/row-key overlaps, 0 crop-SHA overlaps**. Because both training tranches are included, this clears release v3 and all **196,234 v_c admitted rows** separately. No claim is made here about every row previously seen by a reused checkpoint, synthetic text, corrector training, or unresolved canonical-work aliases.
- split2 remains pinned to **253,402 train / 7,007 dev / 60,070 test rows**, **1,159 / 52 / 148 editions**. Every release row agrees with its train assignment and bound book→edition map; **0 DEV/TEST-edition training rows**. Thus **zero subtraction from the admitted W1/W2 training set** holds exactly. It does not mean the original unsplit or unfiltered collection suffered no losses.
- Registry files and external-overlay hashes match. `ru1_v3_edits`: **680 records, 426 changed-text records, 0 release-row matches**; `n1_v1_w1`: **629 records, 63 changed-text records, 0 release-row matches**. Both are registered-not-applied. Internal Cyrillic/numeric/composer release touches are zero. SF7 is not registered because its bound receipt remains **`candidate_pre_audit`, `bound:false`**, with polytonic correction explicitly out of scope.
- Live CROPS4 receipts report W1 **68,779/68,779**, W2 **139,488/139,488** byte-exact, with **0 failures / 0 mismatches / SHA check exit 0**. These receipt populations also include evaluation crops; they are not release-train counts.

Evidence: [release_recount.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/release_recount.json), [sample_2500.jsonl](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/sample_2500.jsonl), [remote_tags_audit.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/remote_tags_audit.json), [final_remote_readback.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/final_remote_readback.json).

### Benchmark construction, quotas and LF1 lineage — PASS except H1

- Receipt is **SEALED**, version **0.2**, `mock:false`. All 12 bound inputs and all copied seal evidence match their SHA bindings; panel hashes match. Final-list and suite key sets are exactly equal: **0 symmetric difference**.
- Every one of **2,691** `text` and `reference` values equals readout `final_text` verbatim; all image/crop SHA fields agree, and all **2,690 unique physical image files** hash correctly. All row metadata, effective LF1 evidence and replacement references agree.
- Independently reconstructed replacements yield **350 flagged in-quota slots = 248 replacements + 102 UNFILLED**. TEST: **298 = 211 + 87**; DEV: **52 = 37 + 15**. **0 pairing/order mismatches, 0 source/scope substitutions, 0 promoted non-OK reserves**. The 422 non-OK candidates overall comprise 350 in-quota and 72 reserve rows; these denominators must not be conflated.
- Seven hash-bound exclusion ID files contain, respectively, **60, 1,465, 258, 273, 133, 1,246 and 200 IDs**; each has **0 candidate-row intersections**, hence 0 sealed-row intersections. All 3,341 candidates are admitted, agree with split2 split/edition, and match tag crop hashes. Maximum drawn class×edition count is **50**, including reserves.
- Pre-LF1 quota deficits are **120 TEST + 162 DEV = 282**; LF1 adds **87 + 15 = 102**; sealed total deficits are **207 TEST + 177 DEV = 384** against the actual quota table.

| Class | TEST quota | TEST sealed | DEV quota | DEV sealed | LF1 UNFILLED T/D |
|---|---:|---:|---:|---:|---:|
| caps_headings | 120 | 119 | 30 | 30 | 1/0 |
| curved_skewed | 100 | 99 | 25 | 24 | 1/1 |
| degraded | 100 | 80 | 25 | 20 | 20/5 |
| font_extremes | 100 | 97 | 25 | 24 | 3/1 |
| greek_latin | 160 | 152 | 40 | 12 | 8/3 |
| historical_russian | 120 | 120 | 30 | 0 | 0/0 |
| latin | 160 | 157 | 40 | 3 | 3/0 |
| leaders_dashes | 100 | 94 | 25 | 25 | 6/0 |
| long | 160 | 146 | 40 | 38 | 14/2 |
| modern_cyrillic | 160 | 40 | 40 | 8 | 0/2 |
| monotonic | 240 | 240 | 60 | 60 | 0/0 |
| numeric_cells | 200 | 199 | 50 | 50 | 1/0 |
| poly_dictionary_journal | 160 | 155 | 40 | 0 | 5/0 |
| polytonic | 360 | 340 | 90 | 90 | 20/0 |
| short | 120 | 119 | 30 | 30 | 1/0 |
| vertical_turned | 100 | 96 | 25 | 24 | 4/1 |
| **Total** | **2,460** | **2,253** | **615** | **438** | **87/15** |

The seal's per-class deficits agree with every row above. Final edition counts are **147 TEST / 52 DEV**; exact source/edition diversity per class is in [final_diversity.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/final_diversity.json). “≥10 books / ≥3 sources” is not universally achieved: e.g. historical Russian TEST is **6 editions / 1 source**, modern Cyrillic TEST **3 / 1**, DEV polytonic **2 / 2**. These are supply-limited diagnostics, not proof of canonical-work diversity.

### Prior findings, coordinator rulings, controls and VOID — cleared within recorded scope

**CENSUS05R H1:** the original cap-4/excluded-forced-editions rule was revised explicitly; the measured cap-50, forced-edition/nonlocked-row draw and honest deficits resolve the original capacity objection. This does not promise full post-LF1 quotas.

**CENSUS05R H2:** I recomputed rotation-free aspect from raw-import crop boxes for **all 3,341 candidates**: **0 cell-tag mismatches**, **300/300 numeric-cell candidates are A≤6**, **180/180 short candidates are non-cell**, and **150/150 vertical candidates have h>w**. The corrected extraction at [bench02_draw.py:101](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-cp3/docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py:101) resolves the missing-cell-evidence finding.

**Relative degraded:** I reread the hash-bound 27,990,456-byte compressed tag population on Clariden and independently ranked admitted W1/W2 evaluation rows by `(confidence,parent,row)` within **split×source**, selecting `ceil(5%×population)`. All **14 population counts and 3,341 candidate flags match**, with no missing confidence in these populations. This is a defensible relative-confidence instrument after the 0.89 admission floor; it does not establish physical faintness/show-through. The exact split×source denominator is more precise than the programme's “within source” shorthand.

**Vertical ruling:** orientation alone is not a fault under the recorded revision. All **150** original/re-read pairs are preserved; all **150** effective verdicts match the reread. Transitions: **110 CROP→OK, 19 OK→OK, 14 CROP→CROP, 3 CROP→TEXT_DIFFERS, 3 OK→CROP, 1 TEXT_DIFFERS→CROP**. Final vertical count is **96 TEST / 24 DEV**. Eight fresh sampled sealed vertical crops were inspected at native resolution; the class includes physically rotated text and short horizontal text in taller-than-wide boxes, consistent with its h>w definition. Do not describe every member as intrinsically vertical printing.

**Controls/VOID:** independently counted **86 production attempts: 72 VALID + 14 VOID**; terminal state **72/72 contexts VALID** (68 main + 4 vertical). The three named twice-VOID contexts each have preserved attempts VOID, VOID, VALID. **2 unresolved cards** remain non-OK and are absent from the seal. Controls reproduce **405/408 main, 16/20 vertical**. The recorded three-error vertical context is diagnostic/control-flagged, not VOID; **one** of its two bed rows survives. I found no policy requiring a control flag to void that context. The known over-flagging and contradictory inherited orientation question deserve a clearer prompt in future qualification, but the recorded override and exclusions were applied as specified.

Evidence: [benchmark_recount.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/benchmark_recount.json), [local_lf1_audit.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/local_lf1_audit.json), [local_answer_audit.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/local_answer_audit.json), [remote_tags_audit.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/remote_tags_audit.json), [physical_samples/index.json](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/physical_samples/index.json).

## Identities, tests and certification boundary

| Artifact | Independently verified SHA-256 |
|---|---|
| Release admission | `92770112efe63669eb079384da0b2e4754901fff0b14fdcc97208207533e37b9` |
| Census admitted_train | `fe955d00af930b90b1d963a0454a4f4cba26de8fd24332ecc6873fd99f42c4f3` |
| seal03 suite | `33e7fe9f0392518bcea030772a6ff18934d94513bcce6e28c7a9c81c53f09539` |
| seal03 bindings | `9da9acac4eab1b9742098eebf99413802dd17ad4ad62c9321cdf4ca2eea04e30` |
| candidates_v3 | `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2` |
| candidates_readout | `929e231ce84ace1faa25ffed6b82010c75bc6b105828c3f311e3e5b75c150973` |
| LF1 final list v2 | `0fa4a1fe747e06dfeb9bdb4e6c1a8f3027140b4b160330c4ce07621a9315a08b` |
| Effective LF1 verdicts | `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9` |

The release and suite hashes were checked again at the end and remained unchanged. Deployed REL3 **39/39** and SEAL02B **31/31** manifest entries match; the local manifests and their listed files match the same identities. The requested draw code now lives under `docs/records/harvest/collect_v3_admission/bench02/`, rather than the old live-doc path in the brief.

Focused tests: **78 passed, 3 subtests passed** across release_v3, seal02, bench02 draw/candidates, LF3 and LF4. See [pytest_final.log](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/pytest_final.log). They were run from the repository root with `PYTHONDONTWRITEBYTECODE=1`, `-B` and `-p no:cacheprovider`. Four initial draw tests attempted fixture writes beneath the read-only module directory; those writes were denied. The review-only [scratch fixture adapter](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/pytest_scratch_plugin.py) redirects the draw module's output root/defaults to writable scratch and copies its read-only sbatch fixture; it does not alter selection code or assertions. LF3 uses the installed x86_64 Python/Pillow pairing after the native interpreter exposed a Pillow architecture mismatch. Earlier failure logs are preserved.

This review certifies artifact identities and the measured exposure boundaries, not every historical checkpoint's training exposure, canonical-work identity, synthetic/corrector provenance, model scoring or the wave-2 deployment. The suite itself correctly remains **`diagnostic_only`**. Checkpoint **3b** still must review the actual deployment, smoke, preregistration and complete checkpoint exposure before any launch. No baseline score or launch is claimed here.

**Disposition:** fix H1 and re-review the new sealed membership before wave 2; log M1, M2 and L1. Release v3 needs no demonstrated repair from this review. Independent audit source: [audit_remote.py](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/audit_remote.py), [audit_tags_remote.py](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/audit_tags_remote.py), [audit_local_details.py](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/audit_local_details.py); raw output: [remote_audit.jsonl](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CP3/remote_audit.jsonl). The initial tag-audit text comparison queried a field that slim tags intentionally omit; that probe was corrected to record field absence, not a data mismatch. Literal-label certification comes from the readout/panel comparison and full release/raw comparison described above.

VERDICT: NOT CERTIFIED for wave 2; release v3 passes, benchmark DEV/TEST crop collision must be fixed and resealed | BLOCKERS: 0 | HIGH: 1
