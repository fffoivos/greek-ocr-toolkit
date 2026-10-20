# W2C1b: finish the W2 stratum 100-card packs from the W2 features snapshot (gpt-6.1-sol, medium, network OFF, no reading)

Continue `docs/records/briefs/W2C1_packs.md`; every constraint there still applies. The earlier attempt prepared the tooling in `docs/records/harvest/recut_v1/w1_masked/w2c1/` (build.py, finalize.py, prepare.py, launch_all.sh, launchers, prompts…). Its offline replay (`rebuild.py`) died at 20/1,907 when the Sol session ended, so READY.json was never written.

**Now use the snapshot. Do not replay:**
- Input: `~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl`, sha256 `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4` (219,381 rows; the complete W2 materialize, 05:24). Verify the sha.
- Never read the live run root's features files: a BSB collector run is live. Crop regeneration uses only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (byte-exact), output outside the run root.

**Strata (100 cards each; W2 rows only; candidate_usable; uniform):** the 7 in W2C1, namely bsb_poly1850 poly1850, ia_poly1850 poly1850, nlg poly1850, nlg poly1900, nlg greek_poly, serbia cyrillic, elstat numerics_tables, **plus** an 8th, **gazette_modern modern_scanned**: the W2 Gazette read, on original crops, Gazette strata `measured_1986_1990` only (state the field used).
- **Pre-filter:** keep the W2C1 rule (screen_merged, rotated and registered classes excluded). Note the SEG screens are being qualified separately (CP7). These checks measure **letters and crop_ok** of the strata, and must not wait for SEG.
- **Scale:** 16 contexts (2 per stratum, 50 bed + 5 controls), the 10 lead-approved controls, canonical scanner by hash `dd2fc59d…`, `prompts/bsb.md` verbatim.
- **Pool sizes:** report them. BSB W2 is the partial set (298 pages at snapshot time); state it.

Make `finalize.py` / READY.json / `launch_all.sh` work from the snapshot. The launcher runs the 16 contexts sequentially with the `limit_probe.sh` stop at ≥ 78%. **Do not run it**; the lead does.

Tests: pool filters, seeds, crop sha equality, closure, scanner hash, the stop rule, and the snapshot sha check.

Update the README. The last line must be exactly:
`W2C1b: done | strata: 8 | pools: <short> | contexts: 16 | READY.json written | canonical scanner sha ok | launch_all ready | tests: <n> passed`
