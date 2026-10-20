# W1d: BSB/IA rebalance and worker-box readiness (gpt-6.1-sol, xhigh, network OFF, no spend, ≤ 60 min)

**Where to work.** This worktree, branch `sol/collect-v3`, starting from your W1c result.

**What to read.** The plan, rev 2.2 (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/SOURCING_T5_COLLECTION_PLAN_20261016.md`), is read-only.

**No collection.** Nothing is collected and nothing runs remotely.

## 1. Rebalance (coordinator ruling)

| Source | Before | After | Notes |
|---|---|---|---|
| BSB poly1850 | 1,600 pages | **1,000 pages** (25 items) | Keep the MDZ cap at 500 Image-API requests per rolling 24 h. Make it overridable by config when MDZ states a number. |
| IA poly1850 | 1,000 pages | **1,600 pages** (≥40 books) | Per-book cap: no IA book above 10% of new poly1850 rows; with ≤40 pages per book this is ≈1.5%. Write the book list (id, title, year, planned pages) to `docs/records/harvest/collect_v3/ia_poly1850_books.md`. |

Then:
- Regenerate the W1 and W2 manifests and the remaining inventory.
- W1 is still 20% of each source.
- Recheck that the totals are 6,850 pages and USD 10.28, with caps W1 USD 2.15 and W2 USD 8.30.

## 2. Worker-box readiness

The owner will create a fresh Linux worker box with ≥60 GB of disk. Neither the Mac nor `home` will be used. Make every runtime assumption explicit and scripted.

1. **`worker/README_WORKER.md`.**
   - Supported OS: Linux x86_64 (state the distro family you tested logic for).
   - Python version, pinned.
   - System packages: pdfium wheels, libjpeg, etc.
   - Disk: ≥60 GB total; peak working set and retained size from your W1c projection.
   - Network egress hosts, the allowlist the collector contacts:
     - archive.org
     - api.digitale-sammlungen.de
     - the NLG IIIF host
     - the Kosmopolis host
     - the Lekythos host
     - et.gr / the official Gazette host
     - the ELSTAT host
     - the Serbia NBS host
     - eu-documentai.googleapis.com
     - oauth2.googleapis.com
2. **`worker/requirements.lock`.** Exact versions of every Python dependency, with hashes if possible. Use the local venv as the source of truth.
3. **`worker/bootstrap.sh`.** Idempotent. It creates the venv from the lock, runs the offline test suite and the dry-run parity, and runs a **preflight** that checks:
   - free disk ≥60 GB;
   - Python version;
   - that the credential variables are set **without printing their values**;
   - DNS resolution only for the allowlist, with no HTTP requests;
   - that the shared limiter directory is writable.
4. **Credentials, environment only.** The Mac's Keychain is not available on the box. At launch the owner or coordinator sets **either**:
   - `GOOGLE_APPLICATION_CREDENTIALS` = the path of an ADC or service-account file they place on the box, **or**
   - `COLLECT_V3_ACCESS_TOKEN` = a short-lived token, with a documented refresh procedure that does not write it to disk.

   The collector never copies, prints or logs either. Keep the scrub test. Document both options with exact commands, using placeholders only.
5. **`worker/launch_w1.sh` and `worker/status.sh`.**
   - Detached (setsid/nohup), with a PID file and a resume-safe re-launch.
   - `--tranche W1` only; W2 refuses to start without `c1_gate.json`.
6. **`worker/sync_back.sh`.** Rsyncs the retained outputs (manifests, records, ledgers, rasters, responses, cards; not regenerable caches) to a destination given as an argument, with `--checksum`, a dry run by default and `--execute` to apply. **The destination is named later**, so do not hard-code one.
7. **`worker/teardown_checklist.md`.** What to verify before the box is deleted:
   - sync complete, with the checksum manifest;
   - the ledger total matches Google billing;
   - credentials removed from the box.

## Hand-off
Run all tests and the dry run. Commit with a guarded helper that excludes git-ignored paths.

The last line must be exactly:
`W1d: done | BSB 1000 / IA poly1850 1600: <ok> | W1 pages: <n> | worker bootstrap+preflight: <ok> | sync script: <ok> | tests: <n> passed`
