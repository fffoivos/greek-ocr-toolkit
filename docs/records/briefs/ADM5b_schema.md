# ADM5b: conform the admission tool to the coordinator's fixed output schema (gpt-6.1-sol, medium, network OFF)

ADM5 (the commit before this brief) built `greekocr.harvest.admission`. **The coordinator has fixed the output schema so the training builds can consume it now.** Change the tool and rerun both outputs.

- **Per-row file `<name>_admission.jsonl`:** {"row_id": str, "source": str, "class": str, "pass": bool, "rules_failed": [rule_id…], "expected_language": str, "expected_scripts": [str…], "letters": int, "nonletter_frac": float, "scripts_seen": {script: count}, "mixed_script_words": [str…], "foreign_chars": [str…]}
- **Receipt `<name>_admission_receipt.json`:** {"tool_version": str, "tool_sha256": str, "input_path": str, "input_sha256": str, "rows_total": int, "rows_pass": int, "drops_per_rule": {rule_id: n}, "drops_per_source_class": {"source|class": {rule_id: n}}, "expected_table_sha256": str, "created": ISO time}
- **Rule ids, exactly:** short_line, low_confidence, tall_box, nonletter_frac, unexpected_language, unexpected_script, mixed_script_word, foreign_char. Map the current R1–R8 to these, and document the map.
- **The same schema for the v2 census** (row_id = the collection v2 line id). Keep the census MD summary, with its counts by wave × rule.
- Keep the passing rows' admitted file (`w1_originals_v3_admitted.jsonl`) beside the per-row file.

**Also check the codec rule** (24,499 v2 failures). Report which codec file and version is used, and the top 20 failing characters with their counts. If most of them are characters that the current training codec (v2) contains but an older codec (v1) lacks, use the **current training codec** (state its path and sha) and report the before/after counts.

Tests: a schema validation test on both outputs, plus the existing planted cases.

The last line must be exactly:
`ADM5b: done | schema ok | codec: <path sha> | w1_originals_v3: <in> -> <pass> | v2 census: <fail>/<n> | top foreign chars: <short> | tests: <n> passed`
