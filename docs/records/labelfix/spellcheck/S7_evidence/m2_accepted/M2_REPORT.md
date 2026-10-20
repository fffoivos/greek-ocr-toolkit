# M2 — S7 cached detector replay

513 inventory cards; 473 original Greek/mixed eligible cards; 40 monotonic lines excluded; 433 checked lines / 11 active source cohorts. The original 40 Cyrillic cards remain excluded. CTC and R1 forward passes: 0. Substitutions: [].

Scope comes only from independent pixel-review script classes. Unknown/mixed classes remain eligible. Inference receives pixels, cached recognizer letters/spans and cached R1 outputs; reference texts and blind verdicts enter scoring only. Print proposals are preserved; disagreement, unresolved localization and UNSEEN coverage remain HOLD.

All 77 original mark-only error pairs remain scored. Changed accepted slots on marks-correct cards are conditional upper bounds, not new visual adjudications.

| mode | corrected / HOLD / missed | new accepted changed slots | HOLD / checked | HOLD / original 473 |
|---|---|---|---|---|
| PRESENCE | 25 / 40 / 12 | 20 | 327/433 (75.5%) | 327/473 (69.1%) |
| FULL | 24 / 41 / 12 | 10 | 340/433 (78.5%) | 340/473 (71.9%) |

| source | checked | PRESENCE corrected / HOLD / missed | capital-breathing corrected | new accepted changed slots |
|---|---|---|---|---|
| anemi_poly1850 | 40 | 0 / 4 / 3 | 0 | 1 |
| bsb_mixed | 40 | 3 / 1 / 2 | 0 | 1 |
| bsb_poly1850 | 33 | 2 / 1 / 1 | 0 | 0 |
| gazette_modern | 0 | 0 / 0 / 0 | 0 | 0 |
| gazette_poly1900 | 40 | 0 / 4 / 1 | 0 | 4 |
| ia_greek_latin | 40 | 6 / 5 / 2 | 0 | 2 |
| ia_poly1850 | 40 | 1 / 2 / 0 | 0 | 4 |
| ia_russian | 0 | 0 / 0 / 0 | 0 | 0 |
| kosmopolis_poly | 40 | 2 / 2 / 1 | 0 | 1 |
| lekythos_poly1900 | 40 | 3 / 2 / 0 | 0 | 1 |
| nlg_poly | 40 | 0 / 6 / 0 | 0 | 1 |
| oa_poly1900 | 40 | 5 / 8 / 2 | 1 | 1 |
| pleias_poly1850 | 40 | 3 / 5 / 0 | 0 | 4 |
| POOLED | 433 | 25 / 40 / 12 | 1 | 20 |

Complete source/type/mode metrics: [M2_metrics.json](M2_metrics.json). Native runtime evidence and per-slot holds: [M2_lines.jsonl.gz](M2_lines.jsonl.gz). Exact error-pair ledger: [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl). Hash bindings: [M2_runtime_receipt.json](M2_runtime_receipt.json).

M2 RESULT: 433 lines/11 active sources; monotonic excluded 40; Google mark errors 77: PRESENCE corrected 25 HOLD 40 missed 12; FULL corrected 24 HOLD 41 missed 12; new changes PRESENCE 20 FULL 10; HOLD lines PRESENCE 75.5% checked / 69.1% original
