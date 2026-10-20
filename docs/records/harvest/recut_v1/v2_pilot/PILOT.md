# T6c1 large-page masking pilot

Verdict: **stop**. Completed 1/20 selected pages.
Stop reason: line_curve_matching_failure: parliament--37e22f57-p000005 (48 lines).

Seed: `t6c1`; sorted test-page population, Python Random.sample: parliament then vouli; alternating execution order.
One fresh worker per page, nice >=15, one numerical thread. All data are external; original crops are read-only.
Timing includes native raster custody/decode, detector, matching, masking and output I/O; worker wall time additionally includes startup. The parliament stop gate checks both times.
Matching executes T6a2's exact functions. Multiple eligible curves are conservatively ambiguous; failure rows receive explicit identity proposals. Failure counts are distinct affected lines.

| Wave | Page | Status | MP | Detector s | Masking s | Page s | Worker wall s | Peak RSS MiB | Lines | Changed | Failures |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| parliament | 37e22f57-p000005 | completed | 40.109 | 16.657 | 5.845 | 22.729 | 23.156 | 4567.8 | 87 | 28 | 48 |
| vouli | 0d2e3015ff99-p000009 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 87d33c70-p000020 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 6d6305f7542e-p000002 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 100763df-p000027 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 808a6f56ea4d-p000027 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 7bd6c40b-p000031 | not run | — | — | — | — | — | — | — | — | — |
| vouli | ae65c155bdb2-p000001 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 76d25f50-p000041 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 9dd6d49acbbc-p000003 | not run | — | — | — | — | — | — | — | — | — |
| parliament | a65a813d-p000013 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 0d2e3015ff99-p000004 | not run | — | — | — | — | — | — | — | — | — |
| parliament | a92e918e-p000057 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 808a6f56ea4d-p000025 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 7bd6c40b-p000011 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 9dd6d49acbbc-p000009 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 51e4207d-p000009 | not run | — | — | — | — | — | — | — | — | — |
| vouli | b32fc7776b85-p000002 | not run | — | — | — | — | — | — | — | — | — |
| parliament | 20900789-p000014 | not run | — | — | — | — | — | — | — | — | — |
| vouli | 9dd6d49acbbc-p000014 | not run | — | — | — | — | — | — | — | — | — |

| Wave | Pages | Median/max s | Lines | Changed | Matching failures |
|---|---:|---|---:|---:|---:|
| parliament | 1 | 22.729/22.729 | 87 | 32.184% | 48 |
| vouli | 0 | n/a/n/a | 0 | n/a% | 0 |

Frozen params: `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`; library: `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5`.
Minimum free disk: 163.819 GB (26 checks).
The verdict concerns this pilot only. T6c2 remains pending; all-v2 processing requires the owner's explicit go.

T6c1: done | pages: 1 | parliament s/page median/max: 22.729/22.729 | vouli s/page median/max: n/a/n/a | match failures: 48 | changed: 32.184% | verdict: stop
