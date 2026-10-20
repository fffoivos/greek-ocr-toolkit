# collect_v3 — W1d, plan rev 2.2

Offline build only. **Nothing collected; zero provider calls and actual spend.** The owner's collection go and fresh Linux worker provisioning remain pending; neither the Mac nor `home` is a collection target. The plan and review in `greek-page-ocr` are read-only; their current bindings are recorded in the plan/build receipts. W1c is `217ddf24`; the W1d brief HEAD is `76c3cc9a`. See [worker readiness](../../../../worker/README_WORKER.md) for exact Python/dependencies, offline bootstrap, preflight, environment-only credentials, detached W1 launch and checksum sync.

## CP-5r fixes

The local look-alike rule NFC-normalizes the whole label before tokenization and checks the complete token's NFD marks before stripping punctuation. Only diacritic-free tokens can map. NFC/NFD accented controls remain Greek; ambiguous υ-containing look-alike tokens exclude the line. The three printed abbreviation witnesses still map. The hash-bound 660-label population reproduces **618 unchanged / 3 mapped / 39 excluded**, in both NFC and NFD. See `lookalike_recount.json`, `lookalike_660_candidates.jsonl`, `label_rules_binding.json` and updated `code_provenance.json`. The upstream rule is unchanged; its source hash is distinguished from the adapted hash. Resume and regeneration bind the local implementation.

Gazette modern rows require the pipeline's primary class **`modern_scanned`**. The year never promotes polytonic text. Gazette-polytonic rows keep their primary class and `gazette_polytonic=true`, carry `gazette_polytonic_failed_v2`, and are excluded from candidates/admission. The failed stratum is never relabelled modern, and its 1982–1990 marks rate remains unmeasured rather than borrowing the modern rate. Other Gazette rows remain crop-held.

| Gazette allocation | 1982–1985 probe | 1986–1990 measured | Total |
|---|---:|---:|---:|
| W1 | 40 (10/year) | 200 (40/year) | 240 |
| W2 default | 0 | 960 (192/year) | 960 |
| W2 qualified alternative | uniform year-stratified over all nine years | same draw | 960 |

`W2_manifest.jsonl` is the measured-only fallback. `W2_gazette_probe_qualified.jsonl` is a separate, deterministic alternative disjoint from W1. It is selected only when the source's coordinator gate contains:

```json
{"passed":true,"classes":{"modern_scanned":true},"probe_1982_1985":{"passed":true,"pages":40,"letters":{"y":90,"n":100},"monotonic_share":0.75}}
```

This example is a schema, not an actual gate or qualification. Missing/failed probe evidence uses the fallback. An asserted pass with fewer than 40 judged cards, letters below 90%, fewer than 40 W1 pages or no finite share in [0,1] stops before W2. C1 cards and verdict denominators separate probe and measured strata. `audits/gazette_strata.json` reports primary-class counts and monotonic share with its denominator (all classified lines, including secondary classes). The audit command reports the measurement without writing a launch gate. Crop holds remain in force after a letters pass.

All Gazette rates use the **same 12 measured pages from 1986–1990**: modern 525/12, numerics 67/12, headings 57/12, dialogue 36/12. The 1982–1990 frame is **37,764 issues**, 37,757 after frozen exclusions. For the default branch, only 1,160 measured-stratum pages are projected; the 40 W1 probe pages have unknown yield. The plan's full-1,200 measured-equivalent ceilings (52,500 / 6,700 / 5,700 / 3,600) remain separately labelled, conditional quantities. A qualified alternative needs C1 yields to reproject its early-year contribution.

NLG has **23 remaining items, ≤920 capped pages**. Lekythos requires **≥13 issues, ≤24 pages/issue** (the seeded allocation uses a 23-page quota). Serbia's yield is **614 eligible rows / 30 pages**; 583 is the unseen blind-check pool, not the yield numerator. Spread reports use unique rows **after dedupe**, by class, for admitted and hold-inclusive populations. C2 uses the combined deduped W1+W2 release population and withholds any release class violating the 10% book/issue or 20% Gazette-year cap; `release_cap_blocks.json` records the block. It never reports a cap pass on pre-dedupe counts.

IA Greek+Latin also carries `crop_tight_page`, as required by rev 2.1: zero admitted contribution until the authorized recut qualifies. Its rule-survivor letters result does not remove the crop hold.

## Allocations and collection safeguards

| Source | Full pages | W1 | W2 |
|---|---:|---:|---:|
| BSB poly1850 | 1,000 | 200 | 800 |
| IA poly1850 | 1,600 | 320 | 1,280 |
| IA Greek+Latin | 1,000 | 200 | 800 |
| IA Russian | 400 | 80 | 320 |
| Serbia | 300 | 60 | 240 |
| NLG | 400 | 80 | 320 |
| ELSTAT | 60 | 12 | 48 |
| Kosmopolis | 600 | 120 | 480 |
| Lekythos | 290 | 58 | 232 |
| Gazette | 1,200 | 240 | 960 |
| **Total** | **6,850** | **1,370** | **5,480** |

The frozen IA poly1850 draw uses **41 books**, all at <=40 pages/book (short books keep their physical bounds); BSB uses 25 items. `ia_poly1850_books.md` records IDs, titles, years and planned/W1 pages. Page quotas are only a spread control; the existing C2 unique-row check enforces the actual 10% new-poly1850-row cap after dedupe. Both manifests and the remaining inventory were regenerated from the unchanged frozen seed/exclusions.

W1 projects USD 2.055 (cap 2.15), W2 USD 8.22 (cap 8.30). Frozen exclusions, cross-provider alias quarantine, T4b assembly/rollback, context-only Roman mapping, hyphen witnesses, default expanded Serbian codec, flag-only screen, marks rates, integer-micro-USD ledger, uncertain-read reconciliation and the shared POSIX host limiter remain active. MDZ's 500-image rolling-24h fallback is configurable and conservative; no documented live limit was looked up. Rights are recorded per item. Network is disabled and execution host unset in the shipped config. Nothing here authorizes launch.

## Storage diet

The default is `storage_diet=true`, `prune_images=false`. `prune_images=true` is refused: the only crop-source raster must survive. A completed read retains one crop-source raster and one Google JSON response with per-page SHA-256 binding and the route/analysis metadata needed to reproduce its rows. Production rasters are content-addressed; previews refer to the same file. Raw Google line/token/symbol geometry remains intact; embedded raster copies/auth material are omitted by the existing response sanitizer.

Stable-URL source PDFs and downloaded raster bodies are evicted only after the render binding is durable. Unknown PDF bounds are resolved/rendered one item at a time before advancing; prepared rasters are reused during reads. IIIF/IA metadata resolution does not prefetch W2 images or consume their image quota. A PDF without a stable re-download URL is retained and explicitly bound as an exception. Signed/expiring URLs are treated as unstable; a source can explicitly set `stable_redownload_url=false`.

Crops and detector caches are removed after each page; page rows and aggregate/separated exports are temporary through finalization. At rest, completed page receipts are compacted and bulk derivatives removed. Rebuilding uses retained inputs without provider requests or Google reads, verifies input hashes and the bound analysis recipe, and recreates only requested review crops with their original hashes.

```sh
.venv/bin/python collect_v3/run.py --output-root "$OUT" materialize --tranche W1
.venv/bin/python collect_v3/run.py --output-root "$OUT" cards --tranche W1
# After review, discard temporary exports/crops/review image copies:
.venv/bin/python collect_v3/run.py --output-root "$OUT" clean-work --tranche W1
```

`cards` materializes exports automatically when needed. Review images are working artifacts; `clean-work` preserves verdict files and keys that bind checker judgments. These commands take the output lock and do not launch collection.

`retention_projection.json` forecasts all 6,850 pages from three cached F2 witnesses/source, in decimal GB:

| Component | Projected GB |
|---|---:|
| Retained raster + Google JSON | 17.24 |
| Retained total including bindings, static files and 100 MB control allowance | **17.40** |
| Regenerable full-corpus products, if materialized | **30.52** |
| Peak disk working set, including retained inputs | **30.73** |

The retained projection meets the **≤20 GB** target. Peak accounts for temporary page rows plus aggregate/separated exports during finalization, atomic aggregate-replacement headroom on resume, maximum measured page work and one 160 MB download slot (the enforced HTTP cap). This is a disk estimate, not RAM or completed-collection size. Page mix may differ; unstable-URL PDF exceptions add their measured bytes and require re-projection. The 100 MB control reserve is an allowance. The forecast assumes one active PDF per item; an OJS fallback resolving multiple galley PDFs requires separate measured headroom. C1 review size is sampled, not a production-size guarantee. There is no duplicate-original-image or preview-raster allowance in retained storage.

## Offline validation and Git hand-off

Run the complete collector suite with a fresh evidence directory (the SIGKILL test requires a fresh directory):

```sh
PYTHONDONTWRITEBYTECODE=1 OMP_THREAD_LIMIT=1 \
COLLECT_V3_TEST_OUTPUT=/fresh/writable/test-evidence \
.venv/bin/python -m pytest -q collect_v3/tests
.venv/bin/python -m collect_v3.verify_offline \
  --test-evidence /fresh/writable/test-evidence \
  --replay-output docs/records/harvest/collect_v3/a_fresh_replay
```

The dry-run retains diagnostic derivatives explicitly to compare every legacy T4b field and measure temporary sizes; this differs from the production storage default. Network sockets and DNS are blocked, a fake token is scrub-tested, provider calls and actual spend remain zero. Parity covers **3,643 lines / 55 fields / 200,365 comparisons**, zero differences. The intentional Gazette admission/hold rules are tested separately from legacy compatibility parity.

The broader repository suite was also invoked. It stops at collection because the existing `tests/test_p1b_alignment.py` imports `docs/records/harvest/pilots_v2/p1b_align.py`, which is absent from both this checkout and W1b. `tests_full.log` records that pre-existing issue. Collector evidence is reported separately; the broad suite is not described as passing.

`build_manifest.json` binds the W1d code and portable artifacts. The guarded `commit_helper.py` checks branch, exact W1d brief HEAD, W1c ancestry, clean index and hashes. It excludes Git-ignored paths with `check-ignore --no-index`, including local pixels, proof workspaces, wheelhouse and venv. It attempts staging once; `W1d_commit_status.json` records the result. The unrelated `.venv` symlink remains outside scope. No push, live collection or paid read is performed.

The worker runtime fixes CPython at 3.11.3, accepts Linux x86_64 only, requires an explicit shared limiter directory, and has a fixed HTTPS host allowlist. No worker or live DNS was tested during this network-off build. The portable 30-page F2 fixture bundle is prepared under ignored `worker/fixtures/`, bound by tracked hashes and transferable with `worker/package_handoff.py`. A separately staged Linux wheelhouse is still required for actual box installation; `requirements.lock` pins the complete 24-package collector/test closure from local installed metadata. Target-wheel hashes are sealed on Linux; Mac installation hashes are not substituted.

W1d final validation: **116 collector tests passed, zero failed/skipped**, with a fresh portable replay. T4b parity remains **3,643 lines / 55 fields / 200,365 comparisons, zero differences**. The self-contained archive was extracted to a new temporary root and its checksums plus offline bootstrap passed with no sibling source/replay worktrees. `W1d_build_receipt.json` records the exact archive hash and validation limits; `w1d_repository_tests.log` preserves the unrelated full-suite collection error. No production root or C1 launch gate was created.
