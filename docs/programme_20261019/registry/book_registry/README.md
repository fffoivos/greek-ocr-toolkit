# Canonical book registry — coordinator rulings, 23 October 2026

This standalone artifact consumes RUNNER5's registry read only; it never runs
that builder or edits `greek-ocr-toolkit-sol-collect`. The selected
`protected_registry_v3.json` SHA256 is pinned to
`a05814d9996b731cacd8fc4d986484a38fbc40d0cbb5359f130b81ab7e6a4c33`:
2,101 protection entries, zero unresolved producer identities. Producer source
files match commit `f4795e8b0`. This does not assert adoption of its Astra review.

`BUILD_RECEIPT.json` pins physical input paths, sizes and hashes. `SHA256SUMS`
binds artifacts, code, tests, documentation and investigation.
`book_registry.parquet` and deterministic `book_registry.jsonl.gz` contain
identical records, one per canonical connected book identity.
`row_instruments.parquet` is the portable exact-line membership relation;
downstream machines do not need the original list paths.

## Split and harvest protection are separate

The coordinator's 00:24 and 00:38 rulings is implemented as follows:

- Existing train assignments survive LQB and release-exclusion line lists.
  These are `scope=row` evidence, not competing book splits. All 147 former
  train/instrument conflicts now have `split=train`, retaining harvest protection.
- `harvest_protection=true` means RUNNER5 protects the entire book against NEW
  harvest pages. It does not remove existing training rows or assert model
  exposure. There are 734 protected canonical books.
- Rows join exact original line IDs to `row_instruments.parquet` for `lqb_row`,
  `release_excluded_row`, list name, declaration locator and list SHA. A flag on
  one line never flags other lines in its book. Both flags may coexist. Factory
  IDs must first resolve through their explicit original-row mapping; prefix
  matching is not line membership.
- A book with only instrument evidence has no invented dataset assignment:
  113 such books use `unassigned_line_instrument_only`. Their earlier
  `lqb/release_exclusion` values described instruments, not actual dataset splits.
- IA `b28038630` is train under the explicit 00:38 ruling in
  `SPLIT_RULING.json`, with harvest protection true. Historical hold-out
  assignments retain their provenance and `superseded_by` ruling ID.
  Other incompatible book assignments continue to fail closed.

`exportable` means the book assignment is resolved, not row admission. Training
selection additionally needs split=train, row decision/release membership and
that release's exact line-exclusion policy. LQB membership alone does not
rewrite historical membership; some lists explicitly record in-sample rows.

| Dataset split | Books |
| --- | ---: |
| train | 1,586 |
| dev | 28 |
| test | 92 |
| seal04_test | 148 |
| seal04_dev | 52 |
| hold_out | 153 |
| unassigned_w3_w4_pending | 148 |
| unassigned_superseded_wave | 8 |
| unassigned_harvested_not_admitted | 62 |
| unassigned_catalogue_only | 91 |
| unassigned_line_instrument_only | 113 |
| **Total** | **2,481** |

The original 309 no-assignment books are now 148 pending W3/W4, eight with
earlier collection rows absent from current v2, 62 observed harvested pages
without current assignments, and 91 catalogue-only identities with no observed
page. These labels describe observed coverage, not the reason an admission
decision was made. Each retains unassigned_reason, origin waves and hashed
identity provenance. No title guesses or default-to-train decisions occur.

Line instruments comprise 5,803 list memberships / 5,383 distinct line IDs:
1,536 LQB memberships and 4,267 release-exclusion memberships. Individual lists
retain their declared purpose and count/hash checks; lists can overlap.
`BUILD_RECEIPT.publishable=true`: zero unresolved book conflicts. This certifies
the registry assignment artifact; the production HF build remains on hold.

## Resolved hold-out investigation

[HOLDOUT_INVESTIGATION.json](HOLDOUT_INVESTIGATION.json) binds the evidence for
IA `b28038630`, local `4c207e1e`, canonical
`book-752c36effe44da3ba972fa6c`, *A Greek-English lexicon*.

The original mixed `holdout_C.json` / `holdout_books.json` mark it test;
the introducing commit is `f8805bcf81d51d4ba7dcb5f593bcd748d3ce3cfc`,
15 October 07:25:16 +03:00. The later explicit v2 policy is **whole book to
train**, committed as `7f50b69fbe5751fb9ff284cdbcb3bb954d173558` on
15 October 14:02:02 +03:00. `scripts/harvest/apply_clean.py` records the owner's
15 October “OK apply this” decision; `CLEAN_REPORT.md` and `split_moves_v2.json`
record the implementation. The 19 October cleanup commit only relocated files.

All 2,868 moved IDs are present and train in current v2; all 9,665 retained v2
lexicon rows are train. Thus the explicit later v2 policy is authoritative for
the recorded v2 release. RUNNER5 still consumes the older hold-out lists for
new-harvest protection. The coordinator's explicit 23 October 00:38 ruling
adopts TRAIN for the dataset registry. The ruling and both policy files are
hash-bound in the assignment; historical evidence is preserved.

## Identity, provenance and coverage

Aliases retain provider-scoped item IDs, NLG catalogue IDs, IA identifiers,
edition IDs, seal04 edition hashes, v2 book IDs, line-ID prefixes, source URLs
and recorded full-PDF hashes. Shared catalogue landing pages and page-PDF
hashes are descriptive references, not book-union keys. Titles never merge
books. Missing namespaces are not guessed. Book IDs are deterministic for the
pinned graph; identity amendments need a version and an old-to-new mapping.
Consumers bind both book ID and registry SHA.

Every assignment retains its source split/role, scope, reason, provenance file
and SHA. Source val maps to dev; reserved maps to test only after exact equality
with the 44,029 IDs in v2_test. seal04_dev/test is a book role, distinct from
actual membership in the 2,690-row panel. Earlier collection splits are identity
evidence; current v2 and split2 supply assignments. No release membership changes.

All eight legacy manifests are covered: round1 1,000; round2 781; mixed 1,396;
Cyrillic 663; OpenArchives 1,443; Parliament 1,153; Vouli 1,126; Wikisource 400.
All 8,574 retained legacy raster locators, including rescue/pilot identities,
join. W1/W2/W3/W4 observations number 1,370 / 5,234 / 2,446 / 2,159; these
include planned, failed and excluded pages, not successful/disjoint rasters.
The 293,439-row earlier collection and 271,987-row v2 supply aliases before text
is discarded. This extraction does not scan image/crop payloads.

## Reproduce and consume

Requires Python 3 with PyArrow (measured 25.0.1) and the pinned source files.
Downstream consumers need only the portable artifacts, not sibling worktrees.

```sh
python3 docs/programme_20261019/registry/book_registry/build_book_registry.py
# Expected exit 0: publishable registry, zero unresolved conflicts.
python3 -m unittest discover -s docs/programme_20261019/registry/book_registry -p test_book_registry.py -v
(cd docs/programme_20261019/registry/book_registry && shasum -a 256 -c SHA256SUMS)
```

HF ships metadata/book_registry.parquet, metadata/row_instruments.parquet,
build/source receipts and checksums. Pages and rows carry canonical book ID,
split, registry SHA, harvest protection, assignment provenance and aliases;
rows additionally carry exact line flags. Source IDs/splits remain visible.

The rebuilt offline probe at `/private/tmp/runner4-book-registry-dryrun-20261023/`
has 40 pages, 2,858 boxes, 1,429 rows and 2,858 feature variants; all 1,429
row→box→page→book joins and 1,066 used/v4 joins pass. Source book
`bsb_poly1850--027215cc6d2a7e8a` joins `book-1847f85939f1c427442b57b6`, train,
harvest protection false, zero exact line-instrument flags. It reuses the retained
hash-bound Clariden probe and existing Mac sources; no fresh remote access.

See [HF_BUILDER_PLAN.md](../HF_BUILDER_PLAN.md) for the CPU plan and its explicitly
non-publishable one-book execution mock.
