# SX1 / SX1b — sf6 release labels for LQB truth IDs

**101 of 2,196 unique truth line IDs are in the 124,669-line release selection. ENSEMBLE_AB releases 99 corrected labels and HOLDs 2 lines; audit100 has 99/99 corrected releases and zero HOLDs. PRESENCE and FULL each release 28 corrected labels and HOLD 73 lines. No mode has a released-unchanged label in this extract. The remaining 2,095 truth line IDs are outside the selection.**

The frozen input contains 39,484 truth items. Its SHA-256 is `d2cdc75c5b0e529c4b7ddd20ea85f778e9da105c3f1cad4afb318d3c438ca34f`, matching the required `d2cdc75c` prefix. [Input copy](../../../../artifacts/sx1/truth_v1_input.jsonl) has mode `0444`. All counts below are unique line IDs, not truth items or cards. Set membership uses every `provenance_all[].set`, falling back to `provenance.set`; memberships can overlap, so set rows must not be summed. CQ1 is shown as a subset of T2.

| Truth set | Truth line IDs | In selection | Released PRESENCE | HOLD PRESENCE | Released FULL | HOLD FULL | Released ENSEMBLE_AB | HOLD ENSEMBLE_AB | Not covered |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N1_controls | 80 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 80 |
| N1_lead | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 |
| RU1_audit | 38 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 38 |
| RU1_review | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 |
| RU1_two_sol | 276 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 276 |
| T2 | 720 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 719 |
| T4 | 747 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 746 |
| audit100 | 99 | 99 | 28 | 71 | 28 | 71 | 99 | 0 | 0 |
| owner39 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 36 |
| print189 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 168 |
| yer_adjudication | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 |
| CQ1 (T2 capitals subset) | 60 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 60 |
| S8_DEV (omitted from frozen truth) | — | — | — | — | — | — | — | — | — |
| substitution60 (omitted from frozen truth) | — | — | — | — | — | — | — | — | — |
| **Unique total** | 2196 | 101 | 28 | 73 | 28 | 73 | 99 | 2 | 2095 |

“In selection” is release-population coverage, including HOLD. “Released” means an actual emitted label. “Not covered” means absent from the selection, not HOLD. The same 73 lines are held in PRESENCE and FULL; only two are held in all three modes. All released counts in the table are corrected labels. A zero among present sets is measured; a dash means the set is absent from the frozen truth input.

**Expectation check: PASS.** Audit100 is fully in the selection: 99/99 truth line IDs (the benchmark excludes its unreadable card). All 99 are `released-corrected` in ENSEMBLE_AB, matching the owner-audited release mode. The 71 HOLDs in PRESENCE/FULL are mode-specific and do not describe the audited ENSEMBLE_AB release. The substitution sample and DEV expectations cannot be tested with this truth snapshot: [SCORE_v1.md](../../../../../greek-ocr-toolkit-secondary/docs/labelfix/lqb/SCORE_v1.md) explicitly omits substitution60 because complete printed heads are not bound, and S8_DEV because reader models/blinding and tier remain unresolved. They are not silently substituted with another set.

T2 and T4 are mostly outside the selection, but the expectation of no overlap is refuted by one selected line in each, both HOLD in all three modes (PRESENCE/FULL reasons below; complete reasons for every mode are in v2):

- T2: `a85515c7-p000130-l0025`, source `openarchives_mixed_ktisis`, wave `mixed`; unnamed detector mark and insufficient positive absences for mark deletion.
- T4: `f1cf6e4b-p000022-l0003`, source `parliament_proceedings_1975_2000`, wave `parliament`; detector clipping at five slots.

CQ1 is confirmed outside the selection: its 60 capitals are represented under T2, as documented in [INPUTS.md](../../../../../greek-ocr-toolkit-secondary/docs/labelfix/lqb/INPUTS.md). Owner39 is also outside it: 36/36 unique line IDs in this truth snapshot, rather than 39 distinct line IDs. These observations establish selection overlap; they do not independently establish why a source was included or excluded.

**Extraction and verification.** [extract_v2.py](../../../../artifacts/sx1/extract_v2.py) repeats SX1's SSH-stdin procedure on `clariden-ln002` in 60.61 seconds. It scans each overlay's full unique selection population (124,669 lines), validates each compressed overlay's actual SHA-256 against the frozen run receipt's `outputs`, checks original-label hashes for extracted rows, and preserves complete raw HOLD-slot reasons. It performs no inference, recomposition, remote filesystem writes, job submissions, certificate refreshes or Git operations. Only the 101-line v2 extract (84,327 bytes) and small hash/validation metadata crossed back; overlays and selection were not downloaded.

The original secondary-checkout truth file has changed since SX1. SX1b therefore reads the preserved mode-0444 SX1 input copy, whose SHA matches the required frozen truth exactly. The v1 extract, receipt, script, stderr, frozen input and [not-in-selection file](../../../../artifacts/sx1/not_in_selection.jsonl) remain byte-identical; before/after hashes are in the v2 receipt. PRESENCE/FULL row contents are exactly equal to v1 after removing the added ENSEMBLE_AB field. [validate_v2.py](../../../../artifacts/sx1/validate_v2.py) independently checks local readback, hashes, per-set mode counts, HOLD semantics, v1 preservation and audit100's 99 corrected releases.

Exact remote inputs:

- Run: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729`.
- Selection: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl`; SHA-256 `ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec`.
- Receipt: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729/receipt.json`; SHA-256 `c7cfcc852281c9ba6ebbe4c6d121455e8b094f48da84472989b0ac795fd991a3`.
- Overlays under the run (actual compressed-file SHA-256, each matched to the frozen receipt):
  - `overlay_ensemble_ab.jsonl.gz`: `68c331b7a17d6f42b8a7de04ee0585be5b292fae6cf4e93f18e112e8c021abb0` (ENSEMBLE_AB).
  - `overlay_full.jsonl.gz`: `410a73b29acd1f3a30ac682df777f3e7724605f9bfbee044c79f3f4961b360e7` (FULL).
  - `overlay_presence.jsonl.gz`: `aeeeeb78a6d44d56f4b434e4e290063d241a5a2f2af5a008b8de0dbdc26f0d5c` (PRESENCE).
- ENSEMBLE_AB data file: `release/overlay_ensemble_ab.jsonl.gz`; its status, label and `hold_slots` supply the added mode. The shared selection and `receipt.json` above bind its population and output hash. No model or inference input files are needed for this extraction.
- Verified local 16-path policy digest: `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`. Production merged L1R3 packaging digest: `82f8d5423f88fdc05546ea834a878ce07c51399f60b7cb1150597db70be59363`; verified against SQ1’s exact policy map. The two packaging paths differ in `l1_common.py` and `l1r_recompose.py`; these bindings are recorded separately.
- Executed script SHA-256: `db8d68691f8c12f44359328b8f64dffda6ec975b15b7edf40c34b29e6e1ac663` (v2).
- [Extract v2](../../../../artifacts/sx1/sf6_release_extract_lqb_v2.jsonl) SHA-256: `30b827478264403e61e9bbe09e9472cab748598b08743da1d7137457734ba6da`; computed remotely on emitted bytes, matched after transfer and after local readback.

Each extract row has `line_id`, original `google_text`, `source`, `wave`, `truth_sets`, and `modes.PRESENCE`/`modes.FULL`/`modes.ENSEMBLE_AB`. Each mode has `status` (`released-corrected`, `released-unchanged`, or `HOLD`), `label` (null on HOLD), and `hold_reasons` (the complete saved `hold_slots`). HOLD proposals are deliberately not labels. [RECEIPT_v2.json](../../../../artifacts/sx1/RECEIPT_v2.json) records hashes, paths, per-set counts, the CQ1 subset, policy maps and validation.

V1 remains available as [sf6_release_extract_lqb.jsonl](../../../../artifacts/sx1/sf6_release_extract_lqb.jsonl) with [RECEIPT.json](../../../../artifacts/sx1/RECEIPT.json).

SX1b READY: ENSEMBLE_AB released 99 / held 2; audit100 released 99/99 yes; extract v2 sha 30b827478264
