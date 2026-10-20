# SF2 — one release gate

17 October 2026. C2-B01/M01/M02/N01/N02 are repaired in this checkout. The shared policy is `sf2-release-v1`, bound to digest `6d47414ccaec24b199727771a301c93802f28115be72120f3cb461505cea9976`. This is a release-safety repair for experimental pseudo-labels, not independent print-truth qualification or approval to use a production L1 release.

The observed checkout was `opus/spellcheck` at `c8b4974b07d001199a93a71ed24654e8c56fa954`: relative to the requested `2ac34b23`, that existing commit adds only the SF2 brief. No Git metadata was written. Other worktrees were read only. Network, CTC/R1 forward passes, GPU work, training and detector-geometry changes: **zero**. Detector execution was limited to the requested 92-line owner page and its detector control; M2 and L1r reused saved detector/R1 records. Evidence and source hashes are in [execution_receipt.json](SF2_evidence/execution_receipt.json).

## C2-B01 — observation and uncertainty precede acceptance

[`release_gate.py`](../../../../greekocr/labelfix/release_gate.py) owns `decide`, `compose_reading`, `compose`, the serializer, the edit guard and the policy binding. M2's `combine` is its compatibility alias. Both the M2 measurement entry point and the current `agreement_mode.py` recompose saved runtime evidence through it. Combined owner pages call it directly; CN1 scores those hash-bound decisions. Both page builders use its serializer. Detector-only controls remain explicitly detector-only diagnostics.

Per slot, the gate emits ACCEPT, KEEP (outside the R1 heads, with no proposed mark edit), or HOLD, with reasons. R1-target slots require a prediction and a scored coverage record. UNKNOWN, any recorded uncertainty, missing observation fields, malformed predictions, unresolved detector localisation/segmentation, unnamed marks, relevant clipping/UNSEEN zones, K1 flags and disagreement abstain. Duplicate coverage/prediction starts are rejected. PRESENCE compares named families; FULL compares named mark sets. Accepted names come from R1. A resolved fused sample remains eligible.

With no validated observability masks, recorded top clipping is relevant to vowel/rho upper marks; bottom clipping is relevant to alpha/eta/omega subscripts, including a proposed absence. Existing left/right clipping or observation states are also consumed for preposed capital marks and word-final elisions. Irrelevant bottom clipping on rho does not itself veto a resolved slot. These are conservative release rules, not a claim that every coarse border flag identifies a truncated mark.

The review's UNKNOWN/no-pixels, UNKNOWN/out-of-image, uncertain segmentation and relevant clipping correction witnesses now HOLD in both modes. Their previous result was unheld `ά → α`. Every L1r overlay, including unchanged and held lines, exports slot decisions, R1 coverage, detector uncertainty/clipping evidence, K1 flags and punctuation evidence. Old saved `modes` are never trusted by the release writer.

## C2-M01 — supported edits and explicit punctuation policy

The shared per-character guard permits mark edits only on matching Greek bases, using psili, dasia, acute, grave, circumflex, subscript and dialytika. It permits at most one mark per family, rejects incompatible breathing/dialytika and invalid bearer combinations, and applies K1 separately. Base substitutions are held. Unsupported Greek marks and non-Greek clusters must remain unchanged; their original raw spelling cannot be silently converted to NFC while another character is edited. An unchanged label retains its original bytes.

The actual overlay witnesses `ᾱ → α`, `é → e`, and `ά̀ → α` change from **corrected → HOLD**, in both modes. Unsupported proposed marks are also rejected. M2's pair/control measurement applies this same guard to the original-label character before accepting an edit; recogniser inference remains reference-free.

Punctuation is a separate detector policy: remove the recogniser's leading quote aliases and leading ASCII spaces, then emit canonical `“` exactly when opening-quote detector evidence exists. Compose canonical word-final `’` from the detector's elision decision. The release guard allows those word-final elision differences after Greek letters; it holds changes to other punctuation, internal/trailing whitespace or unsupported spacing-mark forms that cannot satisfy this correspondence. It does not strip arbitrary combining marks to compare skeletons. Edit offsets remain original-label NFD offsets; evidence offsets remain recogniser NFD offsets.

## C2-M02 — identical composition, quotes and apostrophe custody

The combined builder no longer skips absent R1 predictions or independently renders text. The two lost opening quotes on `384c3f89-p000030-l0010` and `...-l0029` are restored. Across all 92 owner lines, quote-glyph differences from the detector control are **5 → 0**; the old six rendered-text differences, including spacing, are removed. All **92/92** rebuilt page readings and per-slot states/reasons exactly match M2 recomposition of their saved detector evidence. All **15/15** previously unheld missing-prediction/localisation/unnamed witnesses now HOLD. See [owner_parity.json](SF2_evidence/owner_parity.json).

`read_ink` now retains the already-computed apostrophe blobs in `MarkEvidence.apostrophes`, including source IDs and exact pixel runs. This changes serialization, not detection or geometry. Owner apostrophe boxes increase **0 → 23** on 21 lines. Four rendered native witnesses were inspected: both quote witnesses and two apostrophe lines, including the two elisions on `384c3f89-p000059-l0027`. The [witness image](SF2_evidence/punctuation_witnesses.png) shows the existing printed pixels with the recovered boxes; this is limited visual verification, not population accuracy.

The remeasured CN1-style instruments are:

| Instrument | Before | After |
|---|---:|---:|
| Held owner slots | 87 | 150 |
| Owner lines containing HOLD / 92 | 53 | 58 |
| Current review notes: fixed / HOLD / fail | 26 / 12 / 11 | 25 / 14 / 10 |
| Current example notes: fixed / HOLD / fail | 25 / 17 / 15 | 24 / 18 / 15 |
| Raw strict complete-note predicates, review / examples | 32 / 34 | 32 / 34 |

System-output coverage, actual R1 scored coverage and acceptance eligibility are separately exposed. HOLD is not counted as fixed. These remain owner-clause instruments with the review's physical-truth limitations. Full counts: [owner_summary.json](SF2_evidence/owner_summary.json). The historical CN1 artifacts were retained.

## C2-N01 — diagnostic policy divergence

`agreement_mode.py` now consumes detector/R1/coverage runtime records and calls the shared composer, including externally supplied K1 flags. The component/proxy diagnostic has been renamed `agreement_mode_historical.py` and explicitly disclaims L1 acceptance measurement; its external-flag overwrite and Google-equals-R1 disagreement exemption are also removed. Both reported synthetic outcomes change **keep → HOLD**. ZONE remains historical only.

## C2-N02 — matched-box state and reviewed-page binding

`box_regression.py` now compares explicit display owners, absolute source-pixel membership/source IDs, and status for matched boxes at every admitted IoU, including IoU 1. Identical-rectangle owner, pixel and status changes are reported independently of lost/added/moved geometry. Missing legacy fields are UNKNOWN, not a claim of unchanged state; mark-zone inference is not substituted for an absent display-owner field.

With `--notes`, the CLI requires `--review-binding`: JSON containing the actual `reviewed_page`, its `reviewed_page_sha256`, and a `notes_sha256` map keyed by the exact notes paths. It verifies the page bytes, the old sidecar's page binding and all note hashes before using approval language. Without notes it reports unreviewed changes. No new owner approval was inferred during this task.

| S6 baseline → rebuilt combined pages | Lost / added / moved | Owner / pixel / status changes | Unknown owner / pixel / status |
|---|---|---|---|
| Published S6 control page, 92 lines | 0 / 23 / 0 | 0 / 0 / 96 | 0 / 4 / 0 |
| Legacy saved-S6 box projection, 92 lines | 0 / 24 / 0 | 0 / 0 / 0 | 573 / 577 / 577 |

The published-page comparison's 23 additions are the recovered apostrophes; its 96 status changes are newly exposed HOLD states. Four old quote boxes lack pixel membership, so exact membership stability is unverified there. The legacy projection additionally lacked one quote box and most ownership/status/membership metadata. Its zero known-state deltas cannot certify stability. See [box_summary.json](SF2_evidence/box_summary.json); complete comparisons remain in scratch.

## L1r — saved evidence sufficiency and mock releases

Read-only inspection of L1's `l1_detect.py`, `l1_infer.py`, `l1_common.py` and saved mock shards found **sufficient evidence for every current release-gate input**: recogniser text/NFD offsets, detector slots and parts/unnamed state, localisation and segmentation flags, top/bottom clipping and available observation state, opening quotes, elision booleans, R1 predictions, and scored/UNKNOWN/uncertainty coverage. K1 is recomputed under the bound policy. No detector or R1 rerun is needed for release decisions.

The original records are **not sufficient to reconstruct apostrophe pixel boxes**: four mock detections retain the boolean but have empty apostrophe-blob lists. To recover only those boxes, the minimal follow-up is a CPU punctuation-evidence pass on the affected cached native crops, using the original cached alignment/owner slots and unchanged apostrophe-candidate routine, with crop/source/code hashes and an exact check that existing detector parts, coverage, R1 predictions and text decisions remain unchanged. Export each blob's source IDs and pixel runs. No CTC, window regeneration or R1 inference is required. This follow-up was not run on L1 data; that worktree remains unchanged. R1 observability-mask qualification remains deferred; the present gate abstains on relevant recorded clipping.

[`l1r_recompose.py`](../../../../scripts/labelfix/clariden/l1r_recompose.py) verifies the completed historical run, step receipts, original binding, shard hashes, exact selection/source hashes, historical overlays and controls before recomposition. It checks inputs unchanged afterward and writes separate overlays, kept IDs, ORIGINAL-label paired controls, manifests and an output-hash receipt. Both variants receive new release names: `v2-corrected-presence-r` and `v2-corrected-full-r`; controls have matching `-r` names. No historical L1 file is rewritten.

Mock input: L1's `artifacts/labelfix_l1/mock_checked_192/`, with its 160 actual runtime lines (the 32 parity lines are separate). Rebuilt releases: `/tmp/SF2-l1r-verified-20261017/release/`.

| Each variant, 160 lines | L1-v0 | L1r |
|---|---:|---:|
| Corrected | 5 | 3 |
| Unchanged | 29 | 10 |
| HOLD | 126 | 147 |
| Kept / exact matched ORIGINAL controls | 34 | 13 |

**21 unique lines change in each variant: 42 line-variant decisions total.** Two corrected and 19 unchanged lines become HOLD. Among the 21 changed lines, 16 have relevant top clipping, 14 relevant bottom clipping, and one segmentation uncertainty; these counts overlap. No change establishes that an old proposal was actually wrong. Original-label hashes, every kept line's domain/no-HOLD requirements, actual control labels and IDs, source/input/output hashes, and FULL-kept containment in PRESENCE were checked. Details: [L1r receipt](SF2_evidence/l1r_receipt.json), [PRESENCE changes](SF2_evidence/l1r_changes_presence.json), [FULL changes](SF2_evidence/l1r_changes_full.json).

This is the saved local mock. No remote job status, production completion, new node parity or actual production batch-shape qualification is claimed.

## M2 — saved-data replay under the same gate

The original 513-card inventory is retained: 473 Greek/mixed runtime lines and 40 excluded Russian cards. No recognition, detection or R1 forward pass was repeated. The same 77 literal mark-only target pairs and correct-reference control denominator are scored.

| Mode | Corrected pairs | HOLD pairs | Missed pairs | Accepted changed control slots | Lines with HOLD / 473 |
|---|---:|---:|---:|---:|---:|
| PRESENCE, before → after | 25 → 10 | 40 → 55 | 12 → 12 | 30 → 21 | 367 → 438 |
| FULL, before → after | 24 → 10 | 41 → 55 | 12 → 12 | 15 → 11 | 380 → 439 |

“New” means accepted changes on previously correct reference fragments, not independently adjudicated new errors. Pair-local corrections are not retained whole-line training benefit. The coverage reduction is the intended abstention on previously ignored evidence, not a detector accuracy improvement. See [M2 metrics](SF2_evidence/m2_metrics.json) and [pair ledger with decisions](SF2_evidence/m2_pairs.jsonl).

## Regression evidence and remaining scientific boundary

The review and all four probe scripts and their saved outputs were read before implementation. Their release witnesses are repository tests in `tests/labelfix/test_sf2.py`. The original cycle-1 clipping/mask, union, print-preservation, unsupported-truth, padding/blank-window, matching-order, note-target, model-asset and receipt witnesses remain covered by the existing unchanged tests. Saved disagreement accounting is tested without promoting its 62/3/2/13 proxy outcomes to geometry truth.

The two C2-M03 geometry probes remain physically reproducible: S2 still drops the locally legal 12-pixel candidate, and S1 still loses equal-best association state at its adapter boundary. SF2 changes no geometry. Their new release tests require HOLD for unqualified S2 or recorded ambiguous physical mapping; they do not assert that either adapter was repaired or qualified. Independent R0 truth, R2 window qualification and scientific calibration remain open.

Before implementation, the initial 35 release tests gave 29 failed / 6 passed. On a scratch copy of the actual HEAD source with all SF2 edits removed, the complete 61-test SF2 file gives **50 failed / 11 passed**; after the repair **61/61 pass**. The positive tests and already-fixed cycle-1 witnesses intentionally pass before as well. Logs: [before](SF2_evidence/tests_before.log), [after](SF2_evidence/tests_after.log).

Final labelfix run: **302 passed, 1 deselected**. The existing HTTP capture test needs a loopback socket bind, which this sandbox rejects with `PermissionError`; it was deselected for the offline final run. No existing test was edited, weakened or marked xfail. An initial full attempt also exposed the expected historical R1 source-hash drift. A saved-data rescore of all five arms and both policies reproduced every metrics/report/owner-check/reading payload exactly. Only the current source/policy receipt bindings were refreshed; `score_receipt_pre_SF2.json` preserves the old receipt. No R1 model was executed.

Reproduction, with the requested interpreter and `PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`, network disabled:

```sh
python scripts/labelfix/sf2_replay.py --out /tmp/NEW-SF2-replay
python scripts/labelfix/clariden/l1r_recompose.py \
  --input-run ../greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/mock_checked_192 \
  --selection ../greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/binding/mock_selection.jsonl \
  --binding-dir ../greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/binding \
  --source docs/records/harvest/collection/v2/import_real_v2_train.jsonl --out /tmp/NEW-L1r
python -m pytest tests/labelfix -p no:cacheprovider -q \
  -k 'not test_server_appends_each_decision_and_serves_static'
```

Complete scratch pages, sidecars, runtime records and comparisons: `/tmp/SF2-verified-20261017/`. Durable source bindings, summaries, decisions and receipts: `SF2_evidence/`. `git diff --check` passed.

SF2 RESULT: shared gate on M2/m2_score, agreement_mode, CN1/owner_pages, L1r/l1_common; C2-B01/M01/M02/N01/N02 fixed; L1r evidence sufficient yes; mock decisions changed 42; M2 PRESENCE corrected 10/77 HOLD lines 438/473; tests 302 passed
