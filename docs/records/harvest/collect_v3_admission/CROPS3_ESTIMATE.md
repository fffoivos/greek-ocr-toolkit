# CROPS3 W2 byte estimate

Measured 2026-10-19T23:52:44+0300 through 2026-10-19T23:53:08+0300 (Athens, `date`). Decimal GB = 10⁹ bytes.
Snapshot: `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4`; verified against `SHA256_20261018_0524.txt` in the same read-only pass that counted **219,381 rows**.

| Source | W2 rows | Sample | Mean bytes | Median bytes | p95 bytes |
|---|---:|---:|---:|---:|---:|
| bsb_poly1850 | 20,316 | 185 | 22,030.96 | 22,450.0 | 40,662 |
| elstat | 14,835 | 135 | 2,815.21 | 1,447.0 | 10,484 |
| gazette_modern | 119,033 | 1,085 | 6,362.55 | 4,221.0 | 14,357 |
| ia_poly1850 | 48,454 | 442 | 32,780.62 | 33,990.0 | 67,246 |
| nlg | 9,889 | 90 | 32,729.00 | 37,795.5 | 51,339 |
| serbia | 6,854 | 63 | 11,477.70 | 12,725.0 | 19,887 |


Seed **20261019**; proportional source allocation with largest remainders, without replacement within each source; **2,000/2,000 byte-exact** using `collect_v3.storage.ensure_crop` and the collector interpreter. p95 uses the nearest-rank order statistic.

All-rows estimate: **3.237 GB**, 95% interval **3.129–3.346 GB**.
For source s with population Nₛ, sample nₛ, sample mean mₛ and sample variance vₛ:

- Estimated bytes = Σₛ Nₛ × mₛ.
- SE² = Σₛ Nₛ² × (1 − nₛ/Nₛ) × vₛ/nₛ; interval = estimate ± 1.96 × SE.
- This is a row-sampling normal interval with finite-population correction; it excludes encoder/environment changes and admission-selection effects.
- Admitted-only bytes = **Σₛ admitted_rowsₛ × mₛ**. Substitute the census_05 per-source admitted counts when available. Those counts are unknown tonight.
- **Proxy only:** apply 28,798/101,098 = 28.4852% per source: **0.922 GB**, about 62,491 admitted rows. Actual admission can change both source composition and crop size; this is not an admitted-cohort measurement.

Fresh sample staging: **18.662 s**, or **9.33 s per 1,000 crops**. Linear projection: **34.1 minutes** for all rows, **9.7 minutes** for the proxy cohort. The timed stage includes the snapshot join/hash, source verification, crop encoding, output hashing and receipt publication. The snapshot checksum/count pass and live-run inventory are outside the timer. Fixed read overhead is included in the linear projection; filesystem caching, larger runs and disk pressure can change runtime. No upload time is estimated.

Sample tree: `/private/tmp/crops3-estimate-20261019/crops_w2_estimate`. The requested `~/Projects/collect-v3-data/crops_w2_estimate/` could not be created: the sandbox returned `Operation not permitted`. No sample was written there. The temporary tree uses the requested source/row layout, with metadata beside the tree. No PNGs enter git.

The measurement performed a real idempotent second pass: 0 new files, unchanged crop inode/size/mtime/ctime inventory and identical manifest bytes. A full before/after live-run inventory covered **33,166 entries** and was unchanged. Snapshot files were read only. `CROPS3_ESTIMATE.json` is the machine-readable result.
