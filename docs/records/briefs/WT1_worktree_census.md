# WT1: stale spell-check worktrees, a removal census and a lead-executed script (gpt-6.1-sol, medium, network OFF). Sol does NOT remove anything.

**Owner-approved clean-up** (after the 17 Oct merge, opus/spellcheck 960a70163+): remove the spell-check worktrees whose branches are fully
merged.
- **Candidates:** `-align`, `-l1`, `-l1f`, `-l1r`, `-l1r2`, `-l1r3`, `-r0`, `-s8` (all `~/Projects/greek-ocr-toolkit-spellcheck-*`).
- **KEEP:** `-r1` (its m2_run path is cited), `-r2cards`, `-r2prep`, the main worktree, `-cleanup`, and every non-spellcheck worktree.

## 1. Census (read-only), into `docs/records/reviews/harness/WT1_CENSUS.md` + `artifacts/wt1/census.json`

Per candidate:
- the branch and tip; whether the tip is an ancestor of opus/spellcheck (`merge-base --is-ancestor`);
- tracked modifications (must be 0);
- untracked files (count, size, top dirs) and ignored files (count, size);
- **citations:** grep the main worktree, `-r2prep`, `-r2cards`, `-cleanup` and `-r1` (docs, configs, scripts, deploy manifests, receipts)
  and `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/` for the worktree's absolute path prefix.
  - List every citing file and line.
  - Example known hit: the LQB inputs cite `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz`.
    State whether that exact file is TRACKED and byte-identical in the main worktree (then the citation can be repointed), or exists
    only in s8.
- whether any running process has its cwd there (lsof, as in merge_20261017.sh).

## 2. Disposition proposal per worktree (the lead rules)

- **REMOVE-CLEAN:** merged, 0 modifications, 0 untracked load-bearing files, 0 live citations.
- **CUSTODY-THEN-REMOVE:** untracked files exist.
  - Propose a custody copy to `~/Projects/greek-ocr-toolkit-spellcheck/artifacts/worktree_custody/<name>/`, preserving relative paths,
    with a sha manifest.
  - Exclude only regenerable caches (`__pycache__`, `.pytest_cache`); list them.
- **REPOINT-THEN-REMOVE:** live citations exist. List each citing file with the replacement path, which must be byte-identical.
- **KEEP:** not merged, or a running process.

## 3. Script `docs/records/reviews/harness/wt_remove_20261017.sh` (in the merge-script style)

- `set -euo pipefail`; `--dry-run` (default) / `--execute`; a timestamped log in the scratchpad.
- Per worktree, only for those listed in a ruling file `docs/records/reviews/harness/WT1_RULING.json`, which the lead writes:
  1. custody copy + sha verify, if ruled;
  2. assert the citations repointed, if ruled;
  3. `git worktree remove <path>` WITHOUT `--force`. A refusal means abort for that worktree.
- **Never:** `--force`, `rm -rf` on a worktree, branch deletion (branches stay), or push.
- Write tests (a synthetic repo) and run `--dry-run` against a placeholder ruling, then STOP.

Last line: `WT1 READY: candidates 8; REMOVE-CLEAN <n>; CUSTODY <n> (<MB>); REPOINT <n> (<files>); KEEP <n>; script tests <n> passed`.
