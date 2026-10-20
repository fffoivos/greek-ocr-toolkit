# Updating the weak-category ledger

Run `python3 docs/records/harvest/collect_v3/weak_ledger/build_ledger.py` from the repository root. This performs local text/JSON accounting only. Do not start a collector, read page images, acquire locks, or edit the run root. The builder writes only this ledger and its accompanying data/guard files.

When BSB closes, replace its pending forecast with observed usable rows, retain the original check status, and recompute the remaining-page forecast from the successful/excluded page states. The coordinator supplied the resume date; no timestamp receipt was found in the inspected files.

When Gazette closes, first obtain a completed receipt with separate source/class/stratum counts and its masked-arm qualification. Keep original-crop failures separate from masked candidates. Credit only the named qualified arm. Do not merge Gazette progress into the old main-run receipt. If W2 features appear, the builder deliberately stops: extend its grouping to source/class/stratum and check status, retain the old receipt for reconciliation, and remove the fallback only after totals reconcile.

When a check closes, update the authoritative stratum/check receipt through its owning task; this task only rereads it. Pending becomes passed or failed according to that receipt. Preserve sample error tags, review queues and pending marks, and recompute the qualified original-ID union so masked rows are never counted twice. A check pass is not final release assurance. Apply final line exclusions, dedupe, codec and spread receipts before publishing a certified release gap.

Before an exact period deficit is used, resolve collector date mismatches and undated greek_poly rows. Before ordering dedicated front/back bands, measure their own true category yield; general Gazette headings yield is only an arithmetic scenario. Leaders have no qualified read-yield estimate and the later sourcing plan specifies synthetic production.

Every numeric fact object has source paths and derived facts have formulas. Null/not-found fields list searched paths. Rebuild the Markdown and JSON together, inspect changes, then verify the guarded commit list, empty index, HEAD/branch and hashes. The guard intentionally detects live-source drift. No commit is made by the builder.
