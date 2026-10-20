# S7 evidence

Final detector qualification is `metrics.json`, `receipt.json`, and `qualification_final.log`. The receipt checks that every bound source/input stayed unchanged throughout the run. `baseline` is a fresh SF1 control; `accepted` is the separately replayed empty substitution set. S1/S2/S3 remain experimental and off by default.

`original_launch_baseline.json` executes the original source from launch HEAD to distinguish saved-S6 drift from S7 changes. `accepted_config.json` is the current hash-bound configuration for the unchanged combined detector/reader policy.

Each `*_lines.jsonl.gz` retains the complete fixed character cohorts, native pixel runs, explicit physical ambiguity and guide provenance. `*_combined_lines.jsonl` and `owner_checks.jsonl` replay the unchanged CN1/SF1 instruments. `*_hold_slots.jsonl` retains held character identities. `kind_disagreements.jsonl` retains all original 80 slots for every variant, including unresolved truth.

`boxes_*.json` are outputs of the unchanged `scripts/labelfix/box_regression.py`, against saved S6 and the fresh launch control. Review and examples instruments are also run separately.

`m2_script_classes.jsonl` contains independent pixel-review script annotations, without reference text. Each `m2_*` directory contains a cached detector replay, runtime binding receipt, both M2 agreement-mode scores and complete pair/control ledgers. The original 473-card denominator is retained alongside the 433 in-scope lines; 40 monotonic cards are excluded before the polytonic checker.

`pytest_full.txt` records 241 passes and the sandbox-blocked HTTP socket fixture. `pytest_offline.txt` records 241 passes / 1 explicitly deselected HTTP fixture. No existing tests or assertions were changed. `R1_score_final` is the byte-identical source-bound scorer replay used to refresh the current-source receipt; its previous receipt is `historical_R1_score_receipt.json`.

Earlier `qualification.log` and `R1_score_replay` runs are development evidence. Only `qualification_final.log` and the verified final receipt/metrics support the report.
