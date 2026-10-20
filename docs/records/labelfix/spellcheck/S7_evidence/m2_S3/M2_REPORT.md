# M2 — S7 cached detector replay

513 inventory cards; 473 original Greek/mixed eligible cards; 40 monotonic lines excluded; 433 checked lines / 11 active source cohorts. The original 40 Cyrillic cards remain excluded. CTC and R1 forward passes: 0. Substitutions: ['S3'].

Scope comes only from independent pixel-review script classes. Unknown/mixed classes remain eligible. Inference receives pixels, cached recognizer letters/spans and cached R1 outputs; reference texts and blind verdicts enter scoring only. Print proposals are preserved; disagreement, unresolved localization and UNSEEN coverage remain HOLD.

All 77 original mark-only error pairs remain scored. Changed accepted slots on marks-correct cards are conditional upper bounds, not new visual adjudications.

| mode | corrected / HOLD / missed | new accepted changed slots | HOLD / checked | HOLD / original 473 |
|---|---|---|---|---|
| PRESENCE | 3 / 62 / 12 | 8 | 430/433 (99.3%) | 430/473 (90.9%) |
| FULL | 3 / 62 / 12 | 3 | 430/433 (99.3%) | 430/473 (90.9%) |

| source | checked | PRESENCE corrected / HOLD / missed | capital-breathing corrected | new accepted changed slots |
|---|---|---|---|---|
| anemi_poly1850 | 40 | 0 / 4 / 3 | 0 | 1 |
| bsb_mixed | 40 | 0 / 4 / 2 | 0 | 0 |
| bsb_poly1850 | 33 | 0 / 3 / 1 | 0 | 0 |
| gazette_modern | 0 | 0 / 0 / 0 | 0 | 0 |
| gazette_poly1900 | 40 | 0 / 4 / 1 | 0 | 0 |
| ia_greek_latin | 40 | 1 / 10 / 2 | 0 | 1 |
| ia_poly1850 | 40 | 0 / 3 / 0 | 0 | 1 |
| ia_russian | 0 | 0 / 0 / 0 | 0 | 0 |
| kosmopolis_poly | 40 | 0 / 4 / 1 | 0 | 1 |
| lekythos_poly1900 | 40 | 1 / 4 / 0 | 0 | 0 |
| nlg_poly | 40 | 0 / 6 / 0 | 0 | 1 |
| oa_poly1900 | 40 | 1 / 12 / 2 | 0 | 0 |
| pleias_poly1850 | 40 | 0 / 8 / 0 | 0 | 3 |
| POOLED | 433 | 3 / 62 / 12 | 0 | 8 |

Complete source/type/mode metrics: [M2_metrics.json](M2_metrics.json). Native runtime evidence and per-slot holds: [M2_lines.jsonl.gz](M2_lines.jsonl.gz). Exact error-pair ledger: [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl). Hash bindings: [M2_runtime_receipt.json](M2_runtime_receipt.json).

M2 RESULT: 433 lines/11 active sources; monotonic excluded 40; Google mark errors 77: PRESENCE corrected 3 HOLD 62 missed 12; FULL corrected 3 HOLD 62 missed 12; new changes PRESENCE 8 FULL 3; HOLD lines PRESENCE 99.3% checked / 90.9% original
