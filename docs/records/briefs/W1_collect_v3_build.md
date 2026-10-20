# W1 build: the `collect_v3` collector, built and dry-run offline, launch-ready (gpt-6.1-sol, xhigh, network OFF, no spend, ≤ 90 min)

**Workspace.** Use this worktree (`~/Projects/greek-ocr-toolkit-sol-collect`, branch `sol/collect-v3`). Code goes in `collect_v3/` and outputs in `docs/records/harvest/collect_v3/`.

**Read-only inputs:**
- the F2 tracks `~/Projects/greek-ocr-toolkit-sol-funnel-{ia,intl,gr}`;
- the main checkout `~/Projects/greek-ocr-toolkit` (another agent works there);
- the plan `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/SOURCING_T5_COLLECTION_PLAN_20261016.md`, which is under review; do not edit it.

**This task does not collect anything.** There are no provider calls. W1 starts only after the owner decides the execution host (the MacBook or the `home` server), so the code must run on either.

## What to build
1. **Sources and routes**, exactly as in plan §3. Reuse the F2 route code (copy and adapt it into `collect_v3/routes/`; do not import from the other worktrees at runtime):

   | Source | Route |
   |---|---|
   | IA | per-page JPEG `/download/<id>/page/n<leaf>.jpg`, leaf bounds from scandata/imagecount |
   | BSB | MDZ IIIF |
   | NLG | IIIF |
   | Kosmopolis | OJS galleys |
   | Lekythos | PDFs |
   | Government Gazette | official download, catalogue-first |
   | ELSTAT | PDFs |
   | Serbia | PDFs |

   Pages per source: plan §3. W1 = the first 20% of every source. W2 = the rest, run only for sources listed as passed in `c1_gate.json`, which the coordinator writes.
2. **Draws.**
   - Items are drawn uniformly from each source's A0 frame on disk, seeded, with the seed recorded. Gazette draws are decade-stratified: 1910–1959 for the polytonic tranche and 1960–1990 for the modern one. BSB draws only from the poly1850 frame, and Fraktur lexica are excluded.
   - ≤40 pages per item; pages uniform within the bounds.
   - **Exclusions** are by provider id, PDF/image hash and normalised title+year:
     - collection v1/v2 books and all test/dev books (main checkout `docs/records/harvest/collection/` manifests, plus O2 `docs/records/harvest/oa_rebind_v1/o2/` in the `greek-ocr-toolkit-sol-inventory` worktree);
     - all F2-sampled items.

     Write `exclusions_receipt.json` with counts per key.
3. **Reading pipeline**, unchanged except where named:
   - Google Document AI with the same processor binding as F2, symbols on, no hints, long side ≤3500 px.
   - A **ledger reservation before every read**. Hard caps are per tranche, from config: W1 USD 2.10; W2 USD 8.00.
   - P1 admission + codec v1 (plus a Serbian codec option adding ј ћ њ љ ђ џ, off by default) + G1b + exact dedupe.
   - The **T4b assembly fix** (`sol/funnel-gr` `docs/records/harvest/screen_v1/assembly_fix.py`) as the default. Each row keeps `old_label` and `fixed_label`.
   - The convention rules from T4b (`screen.py`):
     - ſ count;
     - Roman look-alike fix or exclude;
     - dropped line-end hyphen + lowercase next line → exclude;
     - em-dash count.
   - The `screen_merged` flag column. It is a flag only and gates nothing.
   - The `marks_correction_required` tag on every polytonic source **except Gazette modern and IA poly1850**. Every row records its source's measured marks rate.
4. **Runner.**
   - Detached and resumable: a state file per tranche and atomic per-page records, so a re-run skips completed pages and never re-reads a page already paid in the ledger.
   - A per-host token bucket at ≤1 request/s (configurable lower, never higher), Retry-After honoured, the contact User-Agent from F2, robots preflight as in F2, no CAPTCHA or access-control workaround.
   - Images pruned after crops and hashes are written (config switch, default on), with the disk use reported.
   - **Credentials come only from the environment at launch:** ADC, or an access token in an env var you name. They are never written to disk, config, state or logs. Add a log scrubber test.
   - Paths are configurable (output root, cache) so the same code runs on `home` (Linux) or the Mac.
   - Provide `collect_v3/run.py` (CLI: `plan`, `run --tranche W1|W2 --sources …`, `status`, `cards`) and `launch_detached.sh`, which uses nohup/setsid, writes a PID file and survives the session closing.
5. **C1 cards.** `run.py cards --tranche W1` draws 100 cards per source/class **uniformly over post-fix usable rows, seeded, never sorted by length**. BSB gets ≥20 mixed lines as a separate stratum. Also 60 blind pages per source. Card files have the same shape as `blind_checks_v1/c0/` (cards.jsonl with card_id, crop, google_text; a separate key file).

## Prove it offline
- **Dry run end to end with no network.** Use a mock HTTP layer that serves 3 cached F2 pages per source from the F2 `bulk/` folders, and a mock Document AI that returns the saved F2 responses for those pages. Show that rows, labels, tags and flags equal the T4b `features.jsonl` values for the same lines, field by field.
- **Resume test:** kill mid-tranche and re-run; there are no duplicate reads and no duplicate ledger rows.
- **Rate-limit test:** time the mocked requests per host and show ≥1.0 s spacing.
- **Credential-scrub test:** feed a fake token through the env and grep all outputs and logs for it.
- **W1 manifest:** produce the W1 item/page draw for every source from the on-disk frames (no network). Sources whose page bounds need a network lookup are marked `resolve_at_run`. Show the projected pages, USD and rows per class against plan §3.

## Hand-off
- `docs/records/harvest/collect_v3/README.md`: how to launch W1 on the Mac or on `home`, the exact env vars, the expected time and USD.
- `W1_manifest.jsonl`.
- `dry_run_receipt.json`.
- the tests.

Commit if git allows; otherwise leave a guarded commit helper. The last line must be exactly:
`W1-build: done | sources: <n> | W1 pages planned: <n> usd cap: <x> | dry-run parity: <ok|diff> | resume: <ok> | rate: <ok> | cred-scrub: <ok>`
