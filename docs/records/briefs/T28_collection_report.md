# T28 — Collection plan v1 close-out: merge every wave's admitted lines, check the pool against the targets, build the trainer manifest and the owner's report (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network OFF. No Google calls. No `.git` writes.
Inputs: docs/records/harvest/{round1,vouli,round2,parliament,openarchives,mixed,cyrillic,wikisource}/{admitted.jsonl, rejected.jsonl, admission_summary.json, holdout_books.json,
READS.md|ADMISSION.md} — any wave folder that is missing or whose summary is absent is reported as "not delivered" (do not fail). docs/records/harvest/COLLECTION_PLAN_v1.md §1
targets. Crops under docs/records/harvest/harvest_big/<wave>/crops/ (round 1: docs/records/harvest/harvest_big/round1/crops/).
Required:
1. docs/records/harvest/collection/admitted_all.jsonl: union of all waves' admitted rows with a uniform schema (id, wave, source, licence, source_url, book/doc key, year,
   decade, script_class, split, label, human_label (wikisource only), confidence, bbox, crop path (relative to repo), crop sha256, width, height). Global checks:
   (a) no crop path or id twice; (b) every crop file exists and its sha matches (sample 2,000 per wave, all for waves < 2,000); (c) global label_in_holdout: any
   train label equal to any dev/test label across ALL waves → move that train row to `rejected_global.jsonl` with reason; (d) per-source cap: no single source
   (Vouli, one Anemi round, one repository …) above 40 % of a class's train rows — report, do not fix; (e) class/split tallies per wave.
2. docs/records/harvest/collection/COLLECTION_REPORT.md: the plan's target table with "have now" per class (train / dev / test), the gap, cost per wave and total (sum of
   the waves' ledgers), pages per wave, rejection reasons per wave, Google-vs-human CER from wave 7 if delivered, per-source shares, what was not delivered and why
   (from the wave reports' last lines). Also the realised mix marginals (script class, decade, length buckets, digit-bearing share, all-caps share) against the
   proposed total mix in the plan (modern 40 / polytonic 25 / cs 15 / latin 10 / cyrillic 5 / furniture 5).
3. docs/records/harvest/collection/manifest_train.json / manifest_dev.json / manifest_test.json: rows {crop, label, script_class, source, licence, wave, year} ready for
   greek-page-ocr `linefactory import-real` (same field names as docs/records/harvest/round1/admitted.jsonl where they exist; state the schema in the report), plus
   data_provenance.json (per wave: brief, read_batch, DocAI processor id, ledger usd, pages, lines, admission module sha).
4. Contact-sheet index docs/records/harvest/harvest_big/collection/SHEETS.md listing every wave's admission_sheet images and compiled-image folders (for the owner's
   after-the-fact look, Finder-ready paths).
5. Split repair for wave 5 part C: the Internet Archive lexicon (source archive_b28038630) is a single source and the per-source hold-out put ALL its 9,788 lines in
   `test`. Re-split it by PAGE (seed 20261015: 70 % train / 10 % dev / 20 % test by page), then apply the global label_in_holdout rule; report the before/after
   class × split counts. Do the same for any other wave whose class has train = 0 while test > 0 because a single source was held out.
6. Tests (no network) for the merge schema, duplicate detection, global hold-out rule, cap computation. INVENTORY. `## Close-out` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T28: done | waves: <delivered>/<8> | train: <n> | dev: <n> | test: <n> | poly: <n> | mono: <n> | cs: <n> | latin: <n> | cyr: <n> | usd_total: <x.xx> | tests: <n> passed`.
