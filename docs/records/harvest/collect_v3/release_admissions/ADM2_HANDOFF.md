# ADM2 admission handoff

Appended 462 kosmopolis/poly1850 rows with `arm = "release-v3-candidate"`,
`marks_status = "pending_opus"`, and
`provenance.sol_reading = "sol/recut-v1 87db4392"`. The admission file now has
17,024 rows. Network remained OFF. All task writes are under this directory;
the live imported `collect_v3/` package was not touched. Nothing was staged
or committed.

The original 16,562 rows are the exact original 16,094,551-byte prefix.
Their subset SHA-256 before and after is
`e16f824c3349f6fa20c4e693964d020096306ebab210c8799020f63b0bdf2b5d`.
The new complete file SHA-256 is
`5fedf0eedf97b3eb3b132d3581c4e4fc7e34dad3be71ef6cb9c2400ad3b2489f`.

## Existing arm contract mismatch

The original file and original builder serialize `arm = "wave-1d only"`,
not `"wave-1d"`. Preserving bytes precludes renaming that value. Verified
exact filters return:

| Literal arm | Rows |
| --- | ---: |
| `wave-1d` | 0 |
| `wave-1d only` | 16,562 |
| `release-v3-candidate` | 462 |

Thus the requested literal `arm == "wave-1d"` count of 16,562 cannot be
satisfied together with byte preservation against this baseline. Tests verify
16,562 using the actual legacy literal and explicitly verify the zero count
for `"wave-1d"`. No consumer or old row was changed. This naming mismatch
remains for coordinator review; it is not reported as a passing literal
`"wave-1d"` filter.

## Selection and evidence

The original builder's class-specific rules yield 473 eligible rows. T6g
excluded 11 previously drawn T6b cards, producing its recorded 462-row pool.
ADM2 uses exactly the T6g key's `_pool_line_ids`, including its exclusion of
those 11 cards. The summary records their IDs and the reason. Difference
from the requested T6g pool: zero. All 462 actual outputs are `masked`;
`guarded_original` remains supported and tested. No other class was appended.

The T6g key matches `sol/recut-v1 72ae7114`; SRK2 results match
`sol/recut-v1 87db4392`. All T6g bound source inputs remain hash-identical.
SRK2 results SHA-256 is
`152e0e8251fd8a13adbba3d1bb17710aa2ed1f7caf4615af40fe16393cdf55df`.
Letters 96/100 and crop_ok 99/100 are final; marks 90/100 remain pending
Opus. The summary binds the W1 inputs, T6b records, exclusion manifest and
ID files, T6g key/cards/receipt/pack/protocol, original builder, and SRK2
results. Its historical `counts` and `admitted_strata` retain the original
wave-1d build context; `counts_per_arm_source_class` gives current totals.

The append helper reuses the builder's crop hash validation and row fields
without importing its top-level writer. It rejects an unexpected baseline
or tail and permits an identical rerun without duplicating candidate rows.
The original builder itself is unchanged.

## Validation and guarded commit list

10 tests passed; evidence is in `adm2_tests.log`. They cover byte preservation,
literal arm counts, exact pool membership, fields/provenance, all candidate
crop hashes and collector metadata, guarded-original handling and hash
rejections, exclusion IDs, the 11-row pool difference, summary/input hashes,
and unchanged original builder.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/records/harvest/collect_v3/release_admissions/test_adm2_poly1850.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/records/harvest/collect_v3/release_admissions/append_adm2_poly1850.py --check-only
PYTHONDONTWRITEBYTECODE=1 python3 docs/records/harvest/collect_v3/release_admissions/guard_adm2_commit.py --check-only
```

`adm2_commit_inputs.json` is the exact guarded list: the two admission files,
append helper, tests, guard checker, test log, this handoff, and the manifest
itself (eight files). It binds source HEAD
`84ef9f428f82f8e5cba66a986bcdb59c798e0783`, branch `sol/collect-v3`, file
hashes, input hashes, the clean test receipt, and validation results. The
checker requires that HEAD and branch, an empty index, no ignored files in
scope, and unchanged evidence. It performs no staging or commit. Unrelated
working-tree changes are excluded. If any guard fails, stop and review;
do not regenerate the list merely to bypass a mismatch.

ADM2: done | wave-1d rows: 16562 (unchanged sha ok) | release-v3-candidate rows: 462 | file sha: 5fedf0eedf97b3eb3b132d3581c4e4fc7e34dad3be71ef6cb9c2400ad3b2489f | tests: 10 passed
