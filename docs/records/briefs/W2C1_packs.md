# W2C1: 100-card checks of the W2 main-run strata: Sol-reader packs (gpt-6.1-sol, medium, network OFF, mechanical)

**Coordinator ruling.** The W2 strata need their own 100-card checks before admission:
- uniform draws over **W2 rows only**, on original crops after screen_merged and rotated_crop;
- Sol one-reader under the HANDOVER protocol with the **canonical scanner**;
- letters and crop_ok final, marks pending Opus for grave-heavy strata;
- Codex budget about 1.6 points; stop at 80%.

**The W2 run root is live** (the Gazette read is running): read only, never take locks. If a crop is regenerated, use **only** `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (byte-exact).

## Strata: 7, each 100 cards
bsb_poly1850 poly1850, ia_poly1850 poly1850, nlg poly1850, nlg poly1900, nlg greek_poly, serbia cyrillic, elstat numerics_tables.

- **Pool:** W2 rows with `candidate_usable == true` in the class, from `~/Projects/collect-v3-data/run/W2/features.jsonl` if present; else rebuild the W2 rows offline for these sources via the collector's storage path (read-only, outputs under this worktree). State which.
- Exclude `screen_merged`, rotated (h>w and ≥4 non-space characters; same rule as `w1_rotated_crop_ids`), and every registered line-level class in `release_exclusions.json`.
- Report each stratum's pool size. BSB W2 is partial (deferred at the MDZ cap): use the rows present and state the count.
- If a pool is below 100, take all of it and say so.

## Packs, as in CAPS3/KR1/RUC1
- 2 contexts per stratum (50 bed + 5 controls), 14 contexts in all.
- The 10 lead-approved controls are reused (CAPS1/CAPS1b list), 5 per context.
- Fresh opaque ids; seed `w2c1:<source>:<class>`.
- PACK_ROOT: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`, beds `w2c1_<stratum>`. Keys go outside, at `docs/records/harvest/recut_v1/w1_masked/w2c1/keys/`.
- The prompt is `prompts/bsb.md` verbatim.
- **Canonical scanner:** copy `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py` **by hash** (sha256 must equal `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`). Point `sol_packs/launchers/run_bed.sh` at that copy, **with no local wrappers**. Record the sha in every run receipt.
- Write `docs/records/harvest/recut_v1/w1_masked/w2c1/launch_all.sh`. It runs the 14 launch lines **sequentially**; before each one it probes the Codex limit (`launchers/limit_probe.sh`) and stops if weekly use is ≥ 78%; it logs to `w2c1/run.log`.

## Tests
Pool filters, seeds, crop sha equality, closure per context, the canonical scanner hash, and the stop rule in launch_all.sh.

README at `docs/records/harvest/recut_v1/w1_masked/w2c1/README.md`. The last line must be exactly:
`W2C1: done | strata: 7 | pools: <short> | contexts: 14 | canonical scanner sha ok | launch_all ready | tests: <n> passed`
