# DEL3: §6 "any time" small deletions in the toolkit worktrees (gpt-6.1-sol, medium, network OFF; no .git writes)

**Owner-approved** (CLEANUP_PLAN_20261017.md §6, last row, "any time"): toolkit `docs/*pytest-results.xml`, `.pytest_cache/`,
`__pycache__/`, `.cache/m2_*.log`.

**Scope:** the main worktree `~/Projects/greek-ocr-toolkit-spellcheck` ONLY. Other worktrees are not mine to clean. Only these exact
patterns:
- `__pycache__` directories, `.pytest_cache` directories;
- `docs/*pytest-results.xml` files;
- `.cache/m2_*.log` files.

**Rules:**
- **Never touch:** `.cache/labelfix/**`, `artifacts/**`, any tracked file, or anything else.
- **Check before deleting:** each path is untracked or ignored (`git ls-files` empty for it).
- **Write a receipt** `docs/records/reviews/harness/DEL3_receipt.json`: the before listing with sizes and sha256 for the files, then the after
  listing.
- **Verify afterwards:** run the full test suite after deletion. Failures must be only the pre-existing set (test_collection_outputs 3,
  test_provenance_cli_api 2, test_apply_clean 5 errors). A sandbox socket error is expected; report it separately.

Last line: `DEL3 READY: deleted <n> paths, <KB>; tracked touched 0; suite <passed>/<pre-existing only>`.
