[Full scoped report](ASTRA-CENSUS05b_full_report.md).

- **H1 fixed:** deployed reader reports **1 leak, exit 1**. Recount: **9,119 configured / 6,904 config-only** hashes.
- **L1 fixed:** empty export reports **3 missing rows, exit 1**.
- **154/154** CODE_SHA files identical; **178/178** remote hashes match—167 package files plus 11 inputs.
- **4 VERIFY_OK receipts revalidated**; fresh scheduler checks **8/8 pass**. Full census retains normal/**04:00:00**, with no debug leftovers.
- **28 distinct readout tests pass:** 19 directly, nine with historical fixtures supplied in scratch.

No release-v3 or benchmark regression found in C/D. MEDIUM/LOW limitations are logged. No jobs submitted.

VERDICT: CERTIFIED for submission; prior smoke-before-full gates retained | BLOCKERS: 0 | HIGH: 0