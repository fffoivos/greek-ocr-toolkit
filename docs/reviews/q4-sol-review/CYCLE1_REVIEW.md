# Q4 independent certification

**HOLD — the fresh RAM sample matches exactly and the receipts show a speedup, but mandatory filesystem and timing verification remain blocked.**

- **[BLOCKER] Required execution gates remain incomplete.** The sandbox rejected writes to both `/tmp` and `$TMPDIR` with `Operation not permitted`. The timing script stopped at `scripts/pages/benchmark_q4.py:254`: **0/10 requested timing pages completed**. Creating the required parent worktree was also blocked. The full-suite retry reached all 2,352 cases: **2,102 passed, 16 skipped, 233 errors, 1 failure**. All 234 unsuccessful reports contained permission errors. Consequently, neither a full-suite pass nor the fresh per-page/per-stage ±20% timing check is certified.

- **[MEDIUM] The 3× target remains unmet.** Recomputed receipt medians are **11.452959833026398 s → 5.136717208020855 s**, giving **2.22962630980403×**. The report acknowledges this accurately (`docs/reviews/PAGE_LINES_Q4_SPEED.md:38`).

- **[LOW] The comparator can accept missing coverage.** At `scripts/pages/benchmark_q4.py:272–284`, matching mode sets are accepted without requiring the expected 16 modes. Removing every mode from both receipts produced **`equal=true`, `pages=95`, `api_calls_per_revision=1520`, `comparisons=0`, exit code 0**. The committed receipts contain complete coverage; I verified that independently.

- **[LOW] The baseline used a different runner version.** Its recorded hash is `56ab7b…`; the retained runner and Q4 receipts use `4f1cf9…`. No matching older runner was found under `scripts/` or `.astra/`. The claim of identical stage instrumentation (`docs/reviews/PAGE_LINES_Q4_SPEED.md:55`) therefore remains incompletely auditable.

**Verified as good:**

- **15/15 supplemental fresh comparisons matched exactly:** all eight table pages, both required spreads, and five additional pages, including two book pages. Parent code came directly from Git’s Q3b archive. JSON values, ordered Parquet rows/schema, delivered pieces, crop dimensions/pixels, ownership, and unrounded line fields matched. These runs used RAM serialization sinks and therefore do not replace the required worktree and disk-output checks.
- Independently audited the committed evidence against the actual **54 + 41 inputs**, parent/current source manifests, all **16 modes**, and expected output families: **13,680 matching fingerprint comparisons**, zero differences.
- Recomputed the timing distributions, stage totals, and throughput arithmetic. Every stored stage sum reconciles exactly to its page’s API time. Timing reproducibility remains unverified.
- Read the production diff and independently checked existing literal constants: no threshold changes or page-specific production branches found.
- All **19 added Q4 differential cases passed** in the suite retry. The repository remained clean.

VERDICT: HOLD Mandatory filesystem and timing verification remain blocked | BLOCKERS: 1 | HIGH: 0