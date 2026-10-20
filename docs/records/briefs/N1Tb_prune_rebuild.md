# N1-Tb: fill dash control types, prune bed to mark-bearing gaps, rebuild packs (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-T (`docs/records/labelfix/secondary/N1T_REPORT.md`). Same worktree, constraints and interpreters.

**Lead rulings.**
1. **Dash control types:** take them from `docs/records/labelfix/secondary/N1_DASH_CONTROL_TYPES.md`. Fill
   `artifacts/n1/controls/dash_types_template.jsonl` into `dash_types.jsonl` and seal it with a sha. The 2 "unsure en/em" cells
   accept any dash type.
2. **Prune the bed, for cost.** Of the 2,129 phase-A slots, read only these:
   - (a) Google's gap is non-empty (any mark or a space); OR
   - (b) the geometry finds an ink component inside the gap, beyond what the digit boxes cover; OR
   - (c) geometry status is not ok.

   Slots with an empty Google gap and no ink component are decided as `nothing (geometry)` without reading. Keep them in the line
   record so the "Ours" line stays complete. They are NOT boxed on the owner sheet, which boxes marks only. A seeded 30-slot audit
   sample of these geometry-only slots goes into the bed anyway, so the rule gets checked.
3. **Rebuild** the r1/r2 bed packs on the pruned set: same structure, ≈9 controls per context, ≥1 raised-dot control each, at
   least 1 dash control of each type per context where possible. Also build the calibration pack v2 now that dash types exist.
   - The old N1-T packs stay on disk, superseded. Record them; do not delete.
   - Run closure on all packs and a dry-run of `run_n1.sh` for `n1cal2` and `n1t`.

   If the old `n1t` root is not empty, use a new root `n1t2`, and teach the launcher that root.
4. Write the receipt `artifacts/n1/N1Tb_RECEIPT.json` and a section "N1-Tb" in `N1T_REPORT.md`, with the pruned slot counts by
   reason, the context count and the Codex estimate. Run the tests.

**Last line:** `N1Tb READY: dash types sealed <sha8>; read slots <n> (google-mark <n>, ink-only <n>, geom-fail <n>, audit <n>); geometry-only nothing <n>; contexts <n> ×2 + cal2 (<n> items); closure <ok>; tests <n> passed`
