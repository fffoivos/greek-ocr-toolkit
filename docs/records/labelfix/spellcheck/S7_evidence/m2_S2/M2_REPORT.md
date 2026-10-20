# M2 — S7 cached detector replay

513 inventory cards; 473 original Greek/mixed eligible cards; 40 monotonic lines excluded; 433 checked lines / 11 active source cohorts. The original 40 Cyrillic cards remain excluded. CTC and R1 forward passes: 0. Substitutions: ['S2'].

Scope comes only from independent pixel-review script classes. Unknown/mixed classes remain eligible. Inference receives pixels, cached recognizer letters/spans and cached R1 outputs; reference texts and blind verdicts enter scoring only. Print proposals are preserved; disagreement, unresolved localization and UNSEEN coverage remain HOLD.

All 77 original mark-only error pairs remain scored. Changed accepted slots on marks-correct cards are conditional upper bounds, not new visual adjudications.

| mode | corrected / HOLD / missed | new accepted changed slots | HOLD / checked | HOLD / original 473 |
|---|---|---|---|---|
| PRESENCE | 27 / 38 / 12 | 20 | 329/433 (76.0%) | 329/473 (69.6%) |
| FULL | 26 / 39 / 12 | 10 | 340/433 (78.5%) | 340/473 (71.9%) |

| source | checked | PRESENCE corrected / HOLD / missed | capital-breathing corrected | new accepted changed slots |
|---|---|---|---|---|
| anemi_poly1850 | 40 | 0 / 4 / 3 | 0 | 1 |
| bsb_mixed | 40 | 3 / 1 / 2 | 0 | 1 |
| bsb_poly1850 | 33 | 3 / 0 / 1 | 1 | 0 |
| gazette_modern | 0 | 0 / 0 / 0 | 0 | 0 |
| gazette_poly1900 | 40 | 0 / 4 / 1 | 0 | 4 |
| ia_greek_latin | 40 | 6 / 5 / 2 | 0 | 2 |
| ia_poly1850 | 40 | 1 / 2 / 0 | 0 | 4 |
| ia_russian | 0 | 0 / 0 / 0 | 0 | 0 |
| kosmopolis_poly | 40 | 2 / 2 / 1 | 0 | 1 |
| lekythos_poly1900 | 40 | 3 / 2 / 0 | 0 | 1 |
| nlg_poly | 40 | 0 / 6 / 0 | 0 | 1 |
| oa_poly1900 | 40 | 6 / 7 / 2 | 1 | 1 |
| pleias_poly1850 | 40 | 3 / 5 / 0 | 0 | 4 |
| POOLED | 433 | 27 / 38 / 12 | 2 | 20 |

Complete source/type/mode metrics: [M2_metrics.json](M2_metrics.json). Native runtime evidence and per-slot holds: [M2_lines.jsonl.gz](M2_lines.jsonl.gz). Exact error-pair ledger: [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl). Hash bindings: [M2_runtime_receipt.json](M2_runtime_receipt.json).

M2 RESULT: 433 lines/11 active sources; monotonic excluded 40; Google mark errors 77: PRESENCE corrected 27 HOLD 38 missed 12; FULL corrected 26 HOLD 39 missed 12; new changes PRESENCE 20 FULL 10; HOLD lines PRESENCE 76.0% checked / 69.6% original
