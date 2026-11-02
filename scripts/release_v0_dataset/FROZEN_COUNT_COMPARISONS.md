# REL0-S4v frozen-count inventory — 29 October 2026

The numeric comparison rule lives in **`BindingPolicy.coverage`** in
`accept_bindings.py`. Builder writes and independent acceptance use it. Full
mode is exact even if a caller supplies `exact=False` or `comparable=False`.
For smoke, an incomplete comparable selection is bounded above by the frozen
count; complete loaded denominators are exact. A dependent count with `u`
witnessed unloaded observations may be short by at most `u` when its source
denominator is complete. Its observed real count must still never exceed the
frozen count. An unknown real reason has frozen allowance zero.

`CropIndex.load_smoke_targets` reads pinned S1/v4 metadata, and census metadata
when a seal04/validation dependency needs it. It retains only relevant exact
keys/hashes outside the selected observations. It does not open omitted crop
files or verify their images; parquet scans project identity/hash columns.
Unique tuple mapping and recorded-hash agreement still apply. Census may reuse
an anchor's recorded hash for byte custody without inventing a row identity.
Broken loaded partners alone, ambiguous IDs, absent metadata partners and
recorded-hash disagreements cannot authorize an unloaded-target skip. The declared-root
index is complete in smoke, so index custody resolves normally rather than
being treated as an omitted index entry.

Each skipped selected crop observation contributes once to
`populations.<population>.smoke_unloaded_target`, outside `reasons`, and to the
S4l witness/count stream under `<source>.original_crops`. The witness identifies
both source observations by pinned file SHA256 and ordinal. Independent source
replay reconstructs the same omitted metadata and requires exactly the same
crop witnesses. Public rows whose original depends on an omitted partner carry
the explicit smoke reason and null original image/dimensions. A keyset or
prepared observation whose public tuple is omitted remains `unselected`.

Every frozen-count comparison made by the builder/acceptor is listed below.
Other exact checks compare the current selected package with its own rows,
hashes or witnesses; they are identified separately to avoid confusing them
with a sampled measurement.

1. **Original coverage:** `assets.original_crops.coverage.<population>.rows`,
   `custody_established`, and every `reasons.<reason>`, in builder summaries,
   acceptance binding checks and independent original replay. Rows use the
   ordinary subset/complete rule. Custody and real reasons use the same helper
   with the witnessed unloaded count. Real reasons never absorb sample misses.
   This applies to old→S1, census→S1/v4/hash/index, seal04 and validation→census
   (including a loaded census whose anchor is omitted), and every other source
   using the same mapped-custody resolver. Existing admitted validation metadata
   is loaded completely; its tuple/hash checks remain exact.

2. **Published original images:** population `published_images.images` versus
   frozen `custody_established`, in builder summaries and independent acceptance.
   Same helper, with `unselected` observations and witnessed null originals as
   the unavailable portion. A resolved population also requires exactly one
   image for each available selected observation. Source/public hash agreement
   and `images + null + unselected == rows` are exact in both modes. A missing
   public row is permitted only for smoke keyset/prepared source observations.

3. **Population totals:** `population_counts.s1`, `old_union`, `prepared_s1`,
   `harvest`, `prepared_harvest`, `prepared_harvest_train`, `a12`, `census_g2`,
   plus per-model `prepared_harvest_dev`, `prepared_harvest_test`, `seal04_dev`,
   `seal04_test`, `prepared_validation`; and every filtered
   `expected_counts[*].count`. Acceptance uses the common subset rule in smoke,
   exact in full. These scalar declarations have no separate completeness
   denominator; a smaller smoke total cannot establish full completeness.

4. **Resolved joins/panels:** `seal04.original_rows_and_references.coverage.panel_rows`
   by split and `validation.original_tuple_bridge.coverage.chosen_candidate.left_distinct`.
   Acceptance counts loaded references/memberships using the same subset rule.
   Missing sampled relation partners retain the existing counted S4l skips.
   Candidate/rejected probe counts are evidence, not required FK denominators.

5. **Source fields/selectors:** `staging.boxes.parsed_provider_fields.coverage`
   and `bibliography.exact_source_locators.coverage`, including
   `nonnull_rows`/`missing_rows`, provider language fields and nested selectors.
   Builder source observations, acceptance public-provider checks and independent
   source replay use the helper with their selected field denominator and the
   frozen `nonnull_rows + missing_rows` total. Complete denominators are exact;
   incomplete smoke fields cannot exceed either frozen bucket. Native source
   locators are counted before book enrichment, not again from enriched rows.

6. **Instruments:** `tables.row_instruments.coverage.memberships` and
   `distinct_original_line_ids` describe the completely loaded pinned instrument
   lists, so independent replay uses `exact=True` in smoke and full.
   `population_matches.<population>` includes rows, instrument rows/memberships,
   lqb/release-exclusion flags and unknown original IDs; acceptance recursively
   uses the common subset/complete rule on each population's observation extent.

7. **Book bridge:** every numeric leaf of `book_bridge.coverage.<population>`
   (also bound as `bibliography.book_bridge.coverage`): rows; match/no_key/
   unmatched/ambiguous; source-field nonnull/null/null-reason buckets; instrument
   rows/memberships; lqb/release-exclusion and unknown-ID counts; match paths.
   Acceptance recursively uses the same helper and population denominator.
   Book registry, source metadata and instrument declarations are fully loaded;
   selected observation coverage remains a subset. Independent replay versus
   the selected build coverage, candidate sets, source hashes, status/field/null
   denominator identities and instrument membership/flags remain exact.

8. **Directional reconciliation:** `reconciliations[*].left_only/right_only`,
   including resolved census/old seven-key declarations. Builder and acceptor
   use the helper's `comparable=False`: independently sampled keyset differences
   are diagnostic in smoke, since an omitted right key can increase a left-only
   count. The raw selected difference counts and complete directional witnesses
   are still checked exactly. Full differences are exact frozen requirements;
   the builder retains a failed report before refusing completion. Keyset bridge
   misses retain counted S4l skips in smoke and fail in full. The copied resolved
   reconciliation declaration must equal the lock in both modes.

9. **Original payload override:** `original_crops_source.expected_rows` is
   compared by the same helper. Smoke may stop after its wanted tuples, so the
   raw scanned prefix is not a comparable full count (`comparable=False`). Exact
   selected tuple existence/uniqueness, native/override recorded hashes and byte
   hashes remain mandatory. Full scanned row count is exact.

10. **Frozen root index:** `crop_roots[*].index.files`, at freeze when supplied,
    cache import and rebuilt-index checks. The same helper uses `exact=True`:
    the whole declared-root index is measured or validated even in smoke. Root
    digest, root set, sidecar pin, metadata snapshots and selected payload hashes
    remain exact. No sampled-index exception exists.

11. **Frozen evidence identity and selected-package readback:** copied original
    probe coverage/report pins, book probe/partial-binding coverage and resolved
    reconciliation requirements must equal the frozen lock without sampling.
    Manifest relation counts/logical digests, source-field/feature summaries,
    native source book coverage, synthetic collision/group/member counts and
    smoke skip counts must equal the actual selected package and replayed
    witnesses in both modes. These compare identical extents, not selected rows
    against a full frozen population. Complete synthetic native/train multisets
    are checked only in full; smoke retains loaded-group and S4l partner checks.

Original diagnostic counters (`mapped_rows`, `reused_verification`, path/index/
embedded counts, previous recovery counts, file-check/cache reuse) remain
reported and independently replayed for the selection. They were not separate
frozen acceptance thresholds and are not made new thresholds here; verification
reuse can differ by execution path. An unloaded result contributes no successful
mapping/index/hash verification and no real failure reason.

Smoke acceptance remains **SELF_CHECK_ONLY**. Full fixture acceptance is not a
production build or production source measurement. The metadata scan's cost on
production inputs remains unmeasured; see programme `GAPS.md`.
