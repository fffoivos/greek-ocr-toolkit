# BENCH02G: census_03 mechanics dry draw (gpt-6.1-sol, medium, network OFF, no reading, no spend)

The coordinator ran the bench02 `extract` on census_03 (Clariden job 3703009, package `bench02_pkg/9e779519`) and copied `tags.jsonl.gz` + `tags.jsonl.receipt.json` into `docs/harvest/collect_v3_admission/bench02/census03/`.
- This is the **mechanics dry run**: `draw --dry-run`. The pool is the W1/W2 rows whose only reason is the split-identity reason; no row is admitted in census_03.
- It is not a benchmark and seals nothing.
- Change no code unless the run fails. If it fails, fix the minimum, re-run the 34 tests, and report the fix.

## Do
1. Verify the receipt:
   - both join rates;
   - row counts: W1/W2 decision rows, against the census_03 W1/W2 count of 142,959 held as `split_or_edition_identity_unresolved`, and the 320,479 SPLIT rows;
   - the sha256 of tags.jsonl.gz against the receipt.
   Report any shortfall.
2. Run the `draw --dry-run` command from `bench02/run_dryrun_census03.md` exactly, with output to `bench02/census03/dryrun/`.
3. **Report**, in `bench02/census03/DRYRUN_CENSUS03.md`:
   - **Supply per class**, test and dev (pre-filter pool), against the quotas 2,460/615, and the filled and deficit counts;
   - **Tag availability** per field on the full census_03, present vs unavailable. This replaces the 4,000-row sample table;
   - **Sources and editions:** class × source counts, the edition-cap hits (4/edition), the editions per class (≥ 10 books / ≥ 3 sources where supply allows, per §3.2), and the excluded editions (v2/locked);
   - **Modern Cyrillic** subgroups (ru/sr/bg/uk) and the font subgroups;
   - **Degraded:** the confidence-only branch count (no ink-density field exists);
   - anything that would block the census_05 real run, e.g. a field missing in census_03 that census_05 is expected to add (gate 0.3 cell flag/A), clearly marked as expected-new vs absent.
4. Keep candidates.jsonl in git only if ≤ 5 MB; otherwise record its sha and bytes in the report and leave it untracked.

Write a guarded commit list (`bench02/census03/` minus large files, plus this brief). The last line must be exactly:
`BENCH02G: done | census_03 tags <rows> rows (join <a>%/<b>%) | dry pool test <t> dev <d> | classes filled test <k>/16 dev <j>/16 | deficits <list> | blockers for census_05 <none|list>`
