# CLEAN1B — read-only inventory, part docs

You are gpt-6.1-sol working in `$R` = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next (branch `cleanup/20261019`, created from `sol/recut-v1`). This run is an INVENTORY ONLY, one of three parallel runs (A code, B docs, C branches) writing different files into the same directory; never touch the other runs' files. Write only under `$R/docs/cleanup_20261019/inventory/`. Everything else is read-only.

## Hard rules
- Never run `git checkout`, `merge`, `rebase`, `stash`, `reset`, `clean`, `prune`, `branch -d`, `worktree remove/prune`, `fetch`, `push`, or edit any file outside `$R/docs/cleanup_20261019/inventory/`. Read-only git commands only (`branch`, `log`, `diff --stat`, `merge-base`, `status --porcelain`, `worktree list`, `rev-list`, `ls-files`, `cat-file`, `show`).
- Do not run the test suite or any script; do not open network connections.
- Do not delete, move or touch files in any worktree. Other worktrees are read-only inputs.
- Report what you measured; where a fact is unknown say so instead of guessing.

## Context: the owner's taxonomy (apply it as the classification column everywhere)
The owner wants the repo organised to distinguish:
- **(A) development of OCR and our segmenter**: (i) the slow line detector, (ii) the next-generation one, (iii) the one built on top of the small detector.
- **(B) creation of training data for OCR**: (a) running Google OCR (Document AI) on pages; (b) the tools built on top of (A)'s segmenter for correcting and filtering those lines (polytonic marks sf7, Cyrillic RU1, numerics N1, dashes, the segmentation filter 0.5→0.9-s4, the content gate 0.3); (c) the exact pipeline organising all of (B) (greekocr/harvest/line_pipeline*.py, docs/records/harvest/line_pipeline_legacy/pipeline.mmd and README); (d) the revision pipeline for (b): the review sheets/artifacts and how they are published for human review (greekocr/adjudicate on branch coord/review-sheets, greekocr/labelfix sheet generators, docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md).
Also: shared infrastructure (deploy, ops, verify, types, cli, _vendor), obsolete, unsure.
The owner's brief is at `$R/docs/cleanup_20261019/OWNER_BRIEF.md`. Read it first.

## Repository facts
Main checkout `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit` (currently on branch fable/label-correction; `main` = 7f50b69fb, 15 Oct). ~43 local branches, ~45 worktrees at `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-*` (`git worktree list`). docs/ in the main checkout is ~60 GB on disk; .git 3.6 GB. Latest work: opus/seg-census (segmentation filter + gate + census pipeline; worktree -segcensus), coord/review-sheets (-review), sol/recut-v1 (-sol-recut), opus/spellcheck (-spellcheck), opus/secondary-corrections (-secondary), astra/ff-ink (-ff-ink, fast lines round 8), astra/page-lines-4 (-astra-lines4), fable/label-correction (main checkout), sol/collect-v3, sol/census-v2-serbian, sol/source-inventory, sol/funnel-*, sol/wikisource-r0, sol/l1e-mask, opus/sol-reading, opus/r2-*, rehearsal/*, readme-public.

## Deliverables (all under `$R/docs/cleanup_20261019/inventory/`)

1. `INVENTORY_DOCS.md` + `docs.json`: size map (`du -sh`, two levels under docs/) for the main checkout and each worktree above, TRACKED vs UNTRACKED separated (`git ls-files` vs `git status --porcelain --ignored`); the directories holding bulk artifacts (crops, PNG, JSONL.gz, HTML sheets, montages, pytest xml) and whether tracked; the 30 largest tracked blobs across all branches (`git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)'`), with the introducing branch where cheap. Documentation map: every .md under docs/ (main checkout + branch-only additions of the worktrees): path, first heading, date if present, one-line purpose, taxonomy slot, status CURRENT / RECORD / SUPERSEDED (by which) / SCRATCH. Top-level files: README.md, docs/STANDARD.md, docs/INVENTORY.md, docs/API.md, AGENTS.md (main checkout and the -review worktree), docs/records/review/HUMAN_REVIEW_SHEETS.md: 3-line summary each and whether it matches the present code. Top-level clutter: build/, dist/, greek_ocr_toolkit.egg-info, fixes/, prototypes/, seed/, docs/*.xml, docs/*.json: tracked?, size, last commit touching them.

Finish by printing the paths of the files written and the byte counts. Do not commit.
