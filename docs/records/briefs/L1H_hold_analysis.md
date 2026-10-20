# L1H — Why the complete gate holds 90% of training lines (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-l1` (branch `opus/spellcheck-l1`). No `.git` writes. Do NOT touch
`~/Projects/greek-ocr-toolkit-spellcheck` (an Astra verification pass is reading it) or `…-spellcheck-l1r` (another Sol run). Analysis only:
no gate or detector change, no job submission. Local Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
MacBook rule: no bulk transfer to the Mac — stream/aggregate on Clariden and bring back only aggregates and ≤ 200 sampled records + their
crops (≤ 200 images). On Clariden use the login node only for light streaming aggregation (a few minutes of one core); if an aggregation would
take longer, STOP and report (the coordinator would then submit a small job). SSH: transient errors retry ≤ 3; auth/cert errors STOP; never
refresh the cert.

## Data (read-only, on Clariden)
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`: L1E job 3679545 `l1e_20261017/output_3679545/recomposition/release/`
(`overlay_{presence,full,ensemble_ab}.jsonl.gz`, pre-SF4 complete gate: ENSEMBLE_AB keeps 12,064 / 124,669 = 9.7%), its receipts; L1-v0
`output_3679313/detector/shard-*-detector.jsonl.gz` (detector slot evidence incl. above/below blobs, `touches_border`, clipped flags, bbox) and
`combined/`. Wave/source per line: `docs/records/harvest/collection/v2/import_real_v2_train.jsonl` (symlinked locally; line `id`, `wave`).

## (1) HOLD reasons per wave, complete gate
For each mode (PRESENCE, FULL, ENSEMBLE_AB) and each wave (round1, round2, parliament, vouli, mixed, openarchives): slot counts per hold reason
and **lines held for that reason alone**, plus lines by reason-set (top 10). Same table shape as the L1-v0 analysis
(`docs/records/labelfix/DIRECTION_DECISION_20261017.md`). Reasons as recorded in the overlays (clipped_top, clipped_bottom, segmentation_uncertain,
localisation_unknown, unnamed, K1:*, edit_guard:*, A/B disagreement, kind disagreement, R1 UNKNOWN/uncertainty, …).

## (2) — dropped
The neighbour-ink hypothesis is tested directly by the masking experiment (sourcing lead's masked crops, run by the track lead), not here.

## Deliverables
`docs/records/labelfix/spellcheck/L1H_REPORT.md` with both tables, the sample ids, method and limits; aggregates under
`docs/records/labelfix/spellcheck/L1H_evidence/`. Last line:
`L1H RESULT: AB held 90.3%: top reasons <…>; per-wave sole-reason lines <…>; PRESENCE/FULL <…>`.
