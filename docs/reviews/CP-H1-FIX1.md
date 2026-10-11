# CP-H1 Fix 1 — scoped offline self re-review

12 October 2026. Scope: the two HIGH geometry findings plus the requested table
gate and portable fetch-test fixture. The full original CP-H1 and Plan §H1 were
read. This re-review was performed during implementation; it is **not independent
checkpoint certification**. No scale-up, network, Google calls or `.git` writes.

| Finding | Re-review evidence | Scoped outcome |
| --- | --- | --- |
| HIGH 1: cross-column labels | Both reviewer pages infer two physical bands from page pixels. Original p23 l38 and p24 l11/l12 reject with `crosses_column`. Fresh extraction gates split pieces, never the fused parent; exact source ink is retained. Single and montage list joins carry physical column context. Duplicate-row and minority-fusion controls pass. | Fixed in code and fixtures. |
| HIGH 2: neighbour slivers | p106 l41 rejects before reader construction. Upper retained ink is 5/32 rows and 572/796 x-span, including the original 19.4%-visible neighbour. Above/below strict threshold and clean own-accent controls pass. | Fixed in code and fixture. |
| MEDIUM: bordered prose classified as table | p20 has long rules but no lattice; its page gate passes. Positive rule-plus-lattice, rules-only, lattice-only and misaligned-box controls pass. | Fixed in code and fixture. |
| MEDIUM: absent fetcher path | Tests load two verbatim archived selection functions from a hash-bound repository fixture; no outside absolute import or temporary link. Bulk resolver is explicit and root-bounded. | Requested test path fixed; old gallery paths remain historical. |

The re-review also caught and fixed a median-gutter cut that would trim p24's
first German letter, a one-pixel rasterisation loss on a split sloping edge, and
legacy cache reuse that could bypass the new gates. Split crops now cut the
original polygon mask, and legacy samples fail closed before reader creation.
No label/tier/substitution/schema/body-font policy was changed; the corresponding
function ASTs match repository HEAD.

The exact requested harvest selection passes **119 tests**.
[Fixture custody](../../tests/fixtures/harvest_fix1/INVENTORY.md),
[test log](../harvest/fix1/tests.log), and
[artifact recount](../harvest/fix1/verification.json) bind the result.

The complete offline replay evaluates 14,200 originals, with
**2,012 additional rejects**, **106 released rejects**,
and **126 sampled crops now geometry-rejected**. Its total
reject count is **8,074**, versus 6,168 stored rejects.
The replay also evaluates straightener gates on every surviving candidate, so
its aggregate comparison includes newly checked unsampled lines. Full stage
definitions and overlapping flag counts are in the
[Fix 1 addendum](../harvest/PILOT_v1.md#fix-1-offline-re-gate).

Independent artifact recount matched the source record set, every before gate,
all transitions, flags, sampled annotations and code hashes. The input JSONL
retains SHA-256 `108c3635a5ffc3a424f5810b9491639fdee047fcd926c7423a731ed415b6cbe4`;
532 protected pilot files and 6,807 archived image/Google files are unchanged.
The existing fitter emitted 43 nonfatal RankWarnings;
exceptions, if present, remain fail-closed gate flags rather than admitted crops.

The MEDIUM rare-glyph exposure/CLLG qualification and LOW tilted-row height
conservatism are outside this requested fix and remain disclosed. The historical
gallery has not been republished or repaired. These heuristic regressions do not
certify rare-glyph coverage or the full future harvest population.

VERDICT: requested Fix 1 verified offline | independent CP-H1 recertification required before scale-up
