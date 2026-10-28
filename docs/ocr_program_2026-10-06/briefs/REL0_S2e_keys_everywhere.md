# REL0-S2e — Sol: widen the review-key exclusion (coordinator decision on KEYS_REVIEW.md), 28 Oct 2026

Decision on scripts/release_v0_publish/KEYS_REVIEW.md: deblinding keys of past blind reviews stay out of the public snapshot (kept locally, retrievable later). Change `private_rule` in scripts/release_v0_publish/inventory.py so that, anywhere in the tree (not only artifacts/):
- any path with a directory component named `keys` is excluded ("review deck key tree");
- files named `*_key.json`, `*_key.jsonl`, `key_SEALED.json`, `blind_key.json`, `blind_pages_key.json`, `wl_key.json` (and their .gz) are excluded ("review deck key file");
- `*.mapped.jsonl` under an `answers/` directory is excluded ("review answer join").
Content-only leads stay included. Add fixture tests for each pattern; ensure no source code under greekocr/, scripts/ (outside this rule's intent) or tests/ is excluded by it — list any such hit in KEYS_REVIEW.md and exempt code files (`*.py`) from the `keys` directory rule. Rerun the inventory, refresh receipts and PRIVATE_REVIEW.tsv. Tests for scripts/release_v0_publish only; delete basetemp after.
If you find a documentation or provenance gap, add it to docs/programme_20261028/RELEASE_v0/GAPS.md (what / where / impact / fix); don't fix it here.
Write scope: scripts/release_v0_publish/, its tests, GAPS.md. No git. Do not touch scripts/release_v0_dataset/. One-line report.
