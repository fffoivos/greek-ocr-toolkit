# T6i2: finish the locked-strata masking inline (gpt-6.1-sol, medium, network OFF)

This continues T6i (preparation is done: 600/600 sources resolved; `docs/records/harvest/recut_v1/v2_full/locked/`).

**Lead ruling on priority.** The nice ≥15 floor was a resource rule from the T6h brief: it protected a live W2 during a 2.5 h, 4-worker run. It is **not** masking semantics. For this 600-line job:
- run inline at the priority your sandbox gives you (nice 5), with **at most 2 workers**;
- do not edit the T6h runner or its frozen checks;
- the locked orchestration wrapper sets its own documented floor (`min_nice=5` for this job only) and records the actual nice in every record.

## Do (as README §"Remaining work" says)
1. Implement **only** the locked-population orchestration around the unchanged T6h `page_worker` / phase0 adapter: separate worker bindings per source root, and HARVEST containment and source-crop checks intact. Use the frozen snapshot export. No masking, matching or guard change.
2. **Mock:** rerun 5 T6h mock ids in fresh processes. They must be byte-identical to the T6h mock outputs. Otherwise STOP.
3. **Process** the resolved locked pages: outputs at `crops/<stratum>/<id>.png`, unresolved reasons recorded, every original and output rehashed. Then write `records.jsonl` (T6h schema plus stratum and actual nice) and a per-stratum `summary.json`.
4. **Tests:** the orchestration, the mock identity, and that the population equals the two exclusion files.

## Hand-off
Leave a guarded commit list (records and summary committed; PNGs ignored). The last line must be exactly:
`T6i2: done | (ii) <masked>/<guarded>/<unmatched>/<unresolved> of 200 | (i-b) <...> of 400 | records sha: <sha> | mock-5 identical: <ok> | nice: <n>`
