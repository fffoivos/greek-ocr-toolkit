# W2C1c: re-pack the 4 VOID contexts, then score the W2 strata once they are reread (gpt-6.1-sol, medium, network OFF, no reading)

W2C1b (16 contexts, `docs/records/harvest/recut_v1/w1_masked/w2c1/`) completed 12 contexts. **4 were VOIDed by the canonical scanner** (v4.4, dd2fc59d…):
- `w2c1_nlg_poly1900/c1`: unresolvable load expression ×10, plus 1 absolute path outside reader_dir;
- `w2c1_nlg_poly1900/c2`: absolute path outside reader_dir;
- `w2c1_nlg_greek_poly/c1`: unmatched image provenance;
- `w2c1_gazette_modern_modern_scanned/c2`: absolute path outside reader_dir.

The scans are under `w2c1/scan/`. Read the offending rollout records (paths in `w2c1/receipts/`).

## Do
1. **Diagnose** each VOID from its rollout: what did the reader do? State whether it is reader behaviour the HANDOVER prompt could prevent, e.g. "use only relative paths inside your reader dir; do not build file paths in loops". Do **not** change the scanner, and do not wrap it.
2. **Re-pack** the 4 contexts per HANDOVER:
   - the **same cards** (same row draw), with **fresh opaque ids** and fresh controls placement;
   - new bed names, e.g. `w2c1_nlg_poly1900_r2/c1`, so that run_bed's "refuse rerun" guard holds;
   - keys outside the packs.
   - If the HANDOVER allows a **prompt addendum** against the diagnosed behaviour, add it verbatim as a separate file appended after `prompts/bsb.md`, and say so. Otherwise use the prompt unchanged.
3. **Launcher:** write `w2c1/launch_repack.sh`, which runs the 4 sequentially with the limit probe. Do not run it.
4. **Scoring tool, ready for after the reread:** `w2c1/score.py` scores per stratum, for all 8 strata, from the 12 good contexts plus the 4 reread ones:
   - letters exact-match rate;
   - crop_ok rate;
   - marks: pending Opus for grave-heavy strata;
   - controls;
   - a pass/fail per stratum against the C1 bars (state the bars and their source, e.g. `c1/C1_REPORT.md`);
   - output `w2c1/W2C1_RESULTS.md` + json.

   Run it now on the 12 good contexts as a **partial** preview, labelled partial.

Tests: re-pack closure, fresh ids disjoint from the VOID packs, the scanner hash, and the score reproducibility.

The last line must be exactly:
`W2C1c: done | voids diagnosed: <short> | repacked 4 (addendum: yes/no) | launch_repack.sh ready | partial preview: <stratum: letters/crop_ok ...> | tests: <n> passed`
