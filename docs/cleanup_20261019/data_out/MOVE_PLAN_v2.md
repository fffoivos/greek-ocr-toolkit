# CLEAN3B MOVE plan v2

Authoritative input: CLEAN3A MOVE_PLAN.tsv, HEAD `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. Decimal thresholds: 5,000,000 / 1,000,000 / 50,000 bytes. Rules are evaluated a, d, b (with exception), c. The rule column records the first applicable MOVE rule; KEEP has an empty rule. All original columns are retained verbatim except decision/reason.

| Decision | Count | Bytes |
|---|---:|---:|
| MOVE | 16,888 | 9,984,555,912 |
| KEEP | 44,645 | 2,871,824,589 |

Small literal inputs retained by b exception: 31 (SMALL_INPUTS_v2.tsv). Rule d moves only the 19 symlink entries with their mirrored parent paths; sibling files follow a/b/c. External or dangling targets are never traversed. Exact link text: SYMLINKS_v2.tsv.

## Kind

| Group | MOVE count | MOVE bytes | KEEP count | KEEP bytes |
|---|---:|---:|---:|---:|
| bundle | 11 | 169,310,442 | 0 | 0 |
| census-export | 11 | 403,858,598 | 79 | 9,914,865 |
| crop-set | 12,787 | 643,415,214 | 968 | 47,554,581 |
| key | 25 | 1,294,606,752 | 576 | 73,830,143 |
| log | 24 | 12,907,640 | 3,232 | 114,975,603 |
| model-output | 294 | 516,751,279 | 265 | 10,669,679 |
| montage | 3 | 1,065,866 | 0 | 0 |
| other | 3,281 | 1,016,748,722 | 37,887 | 2,474,765,174 |
| pool | 423 | 5,660,055,892 | 1,564 | 133,051,190 |
| sheet | 29 | 265,835,507 | 74 | 7,063,354 |
## Top-level directory

| Group | MOVE count | MOVE bytes | KEEP count | KEEP bytes |
|---|---:|---:|---:|---:|
| .gitignore | 0 | 0 | 1 | 2,449 |
| AGENTS.md | 0 | 0 | 1 | 1,213 |
| R2A_DEPLOY_FILES.txt | 0 | 0 | 1 | 202,567 |
| R2A_DEPLOY_SHA256.txt | 0 | 0 | 1 | 364,597 |
| R2_DEPLOY_SHA256.txt | 0 | 0 | 1 | 39,243 |
| README.md | 0 | 0 | 1 | 5,409 |
| SF7_DEPLOY_FILES.txt | 0 | 0 | 1 | 13,005 |
| SF7_DEPLOY_SHA256.txt | 0 | 0 | 1 | 37,248 |
| TR2_DEPLOY_FILES.txt | 0 | 0 | 1 | 29,232 |
| TR2_DEPLOY_SHA256.txt | 0 | 0 | 1 | 74,574 |
| artifacts | 1,808 | 1,010,768,962 | 4,400 | 268,135,390 |
| collect_v3 | 0 | 0 | 53 | 352,480 |
| config | 0 | 0 | 10 | 2,226,340 |
| docs | 15,074 | 8,966,374,818 | 37,229 | 2,501,355,474 |
| fixes | 0 | 0 | 1 | 3,461,513 |
| greekocr | 0 | 0 | 350 | 5,092,461 |
| legacy_l1 | 0 | 0 | 260 | 2,508,044 |
| out | 5 | 505,012 | 150 | 7,606,226 |
| prototypes | 1 | 6,907,120 | 395 | 20,328,769 |
| pyproject.toml | 0 | 0 | 1 | 1,848 |
| scripts | 0 | 0 | 513 | 5,105,282 |
| seed | 0 | 0 | 4 | 8,320 |
| tests | 0 | 0 | 1,246 | 54,800,652 |
| worker | 0 | 0 | 23 | 72,253 |
## MOVE rule

| Group | MOVE count | MOVE bytes | KEEP count | KEEP bytes |
|---|---:|---:|---:|---:|
| KEEP | 0 | 0 | 44,645 | 2,871,824,589 |
| a | 232 | 8,559,279,830 | 0 | 0 |
| b | 16,376 | 860,644,666 | 0 | 0 |
| c | 261 | 564,628,746 | 0 | 0 |
| d | 19 | 2,670 | 0 | 0 |

## Delta versus v1

37,858 v1 MOVE files (2,657,936,043 bytes) now KEEP. All 19 v1 ASK links now MOVE.

| Kind | v1 MOVE -> v2 KEEP count | Bytes |
|---|---:|---:|
| census-export | 71 | 9,716,802 |
| crop-set | 947 | 45,690,871 |
| key | 550 | 73,312,208 |
| log | 3,232 | 114,975,603 |
| model-output | 262 | 10,504,817 |
| other | 31,165 | 2,266,397,559 |
| pool | 1,557 | 130,274,829 |
| sheet | 74 | 7,063,354 |

## Directories becoming empty

91 directories lose all HEAD entries; 91 are also empty in the current working tree after the planned removals. EMPTY_DIRECTORIES_v2.tsv records both. Actual deletion uses rmdir only and never removes untracked content.

- `artifacts/cq4/packs/solcap_topup/topup_reread_000/r1/img`
- `artifacts/cq4/packs/solcap_topup/topup_reread_001/r1/img`
- `artifacts/cq4/packs/solcap_topup/topup_reread_002/r1/img`
- `artifacts/cq4/packs/solcap_topup/topup_reread_003/r1/img`
- `artifacts/cq4/packs/solcap_topup/topup_reread_004/r1/img`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_000/r1/img`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_001/r1/img`
- `artifacts/cq4/packs/solcap_wcap/wcap_reread_001/r1/zoom`
- `artifacts/ru1/ru4e2/lead/crops`
- `artifacts/sf7_rc1/audit/opus_keys/deck/blind/img`
- `docs/records/harvest/analysis/clean_preview`
- `docs/records/harvest/blind_checks_v1/c0/ia_greek_latin/crops`
- `docs/records/harvest/blind_checks_v1/c0/ia_poly1850/crops`
- `docs/records/harvest/blind_checks_v1/c0/ia_russian/crops`
- `docs/records/harvest/blind_checks_v1/c0/kosmopolis_poly/crops`
- `docs/records/harvest/blind_checks_v1/c0/nlg_poly/crops`
- `docs/records/harvest/blind_checks_v1/t4c/anemi_poly1850/crops`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_mixed/crops`
- `docs/records/harvest/blind_checks_v1/t4c/bsb_poly1850/crops`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_modern/crops`
- `docs/records/harvest/blind_checks_v1/t4c/gazette_poly1900/crops`
- `docs/records/harvest/blind_checks_v1/t4c/lekythos_poly1900/crops`
- `docs/records/harvest/blind_checks_v1/t4c/oa_poly1900/crops`
- `docs/records/harvest/blind_checks_v1/t4c/pleias_poly1850/crops`
- `docs/records/harvest/collect_v3_admission/seg/cp7/crops`
- `docs/records/harvest/collect_v3_admission/seg/cp7/r2/crops`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/rollouts`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_a/r1/crops`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_a/r1/zoom`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_b/r1/crops`
- `docs/records/harvest/collect_v3_admission/seg/cp8a/sol_packs/segcp7r2_b/r1/zoom`
- `docs/records/harvest/collect_v3_admission/segeval1/cells/samples`
- `docs/records/harvest/collect_v3_admission/segeval1/cells_opus/crops`
- `docs/records/harvest/collect_v3_admission/segeval1/crops`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/crops`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/control_sheets`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/q3/eye_sheets`
- `docs/records/harvest/collect_v3_admission/split1/crops`
- `docs/records/harvest/montage_v1/determinism/norule/images`
- `docs/records/harvest/page_reads_v1/failure_images`
- `docs/records/harvest/parliament/assignments`
- `docs/records/harvest/r2a`
- `docs/records/harvest/r2a/crops`
- `docs/records/harvest/recut_v1/f2/lekythos_poly1900`
- `docs/records/harvest/recut_v1/masking/f2/gazette_modern`
- `docs/records/harvest/recut_v1/masking/f2/ia_greek_latin`
- `docs/records/harvest/recut_v1/masking/f2/kosmopolis_poly1900`
- `docs/records/harvest/recut_v1/masking/f2/lekythos_poly1900`
- `docs/records/harvest/recut_v1/v2_pilot/diag/sheets`
- `docs/records/harvest/recut_v1/v2_pilot/diag/witnesses`
- `docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/review-data/font-normalized`
- `docs/records/harvest/seg_steps/s1/overlays`
- `docs/records/harvest/seg_steps/s2/census_crops`
- `docs/records/harvest/seg_steps/s2/near_square`
- `docs/records/harvest/seg_steps/s2/overlays`
- `docs/records/harvest/seg_steps/s3/overlays`
- `docs/records/labelfix/review_deck/cards`
- `docs/records/labelfix/review_deck/cards/accent`
- `docs/records/labelfix/review_deck/cards/accent_2`
- `docs/records/labelfix/review_deck/cards/base_sub`
- `docs/records/labelfix/review_deck/cards/base_sub_2`
- `docs/records/labelfix/review_deck/cards/breathing`
- `docs/records/labelfix/review_deck/cards/constraint`
- `docs/records/labelfix/review_deck/cards/final_grave`
- `docs/records/labelfix/review_deck/cards/final_grave_2`
- `docs/records/labelfix/review_deck/cards/final_sigma`
- `docs/records/labelfix/review_deck/cards/ink_decisive`
- `docs/records/labelfix/review_deck/cards/marks_multi`
- `docs/records/labelfix/review_deck/cards/subscript`
- `docs/records/labelfix/spellcheck/L1M_evidence/200/pixels`
- `docs/records/labelfix/spellcheck/L1M_evidence/flip_panels`
- `docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census`
- `docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels`
- `docs/records/labelfix/spellcheck/L1M_evidence/panels`
- `docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels`
- `docs/records/labelfix/spellcheck/R0_cards/img`
- `docs/records/labelfix/spellcheck/R0_cards_ia/img`
- `docs/records/labelfix/spellcheck/R0_cards_ib/img`
- `docs/records/labelfix/spellcheck/S8_DEV/audit/img`
- `docs/records/labelfix/spellcheck/S8_DEV/audit100/img`
- `docs/records/labelfix/spellcheck/S8_DEV/cards/img`
- `docs/records/labelfix/spellcheck/S8_DEV/evidence/baseline`
- `docs/records/labelfix/spellcheck/S8_DEV/evidence/baseline/original`
- `docs/records/labelfix/spellcheck/S8_DEV/masked/baseline`
- `docs/records/labelfix/spellcheck/S8_DEV/masked/baseline/masked`
- `docs/records/labelfix/spellcheck/S8_DEV/s8b/dev_detector`
- `docs/records/labelfix/spellcheck/S8_DEV/s8b/regression_detector`
- `docs/records/labelfix/spellcheck/clariden/L1E_evidence/remote_readback/heldout_final`
- `docs/records/labelfix/spellcheck/clariden/L1E_evidence/remote_readback/heldout_final/mock`
- `docs/records/labelfix/spellcheck/crops_S2`
- `docs/records/reviews/q1b-evidence`

## Special custody cases

SEGEVAL1.bundle is preserved as a file (147,025,055 bytes; sha256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`). Its header names bundled head `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`. Custody is the bundle bytes, not assumed availability in local history.

`candidate_order_KEEP.jsonl` and `SEGEVAL1.bundle` are referenced by historical scope guards s1–s4 / gate_rereport / gate03. Those records and scripts under docs/ remain unchanged. Historical replay needs a new receipt-backed adapter or a deliberate restored mirror; current scope-guard execution is not qualified by this plan.
