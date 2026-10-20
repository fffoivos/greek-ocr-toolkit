# MS: write the owner-approved merge as ONE executable script (gpt-6.1-sol, medium, network OFF; Sol does NOT run git writes)

**Owner decision (17 Oct):** the merge into `opus/spellcheck` is approved. The owner chose: Sol writes the script, the lead executes it
verbatim. Coordinator form: `docs/records/reviews/harness/merge_20261017.sh`, committed by the lead, executed verbatim, with its full log as the
receipt.

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`).
- **You may NOT write git metadata** (the sandbox forbids it anyway). Read-only git commands are fine.
- Write only:
  - `docs/records/reviews/harness/merge_20261017.sh` and its tests;
  - copies of the two launcher variants (below) with a README;
  - `docs/records/reviews/harness/MERGE_SCRIPT_NOTES.md`.

**The spec** is the decision sheet (`docs/records/cleanup_20261017/CLEANUP_MERGE_REHEARSAL.md`, top block) and the previous brief `docs/records/briefs/MERGE_final.md`
(§1 sequence, §2 checks, §3 fast-forward + untracked-collision handling). Reference result: branch `rehearsal/merge-20261017` at
`a241ed75e`, in the scratch worktree
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal`.

## Script requirements

- **Shell:** bash, `set -euo pipefail`, `trap` printing the failing line.
- **Modes:** `--dry-run` (default) and `--execute`.
  - Dry-run ONLY prints the commands and verifies preconditions, writing nothing.
  - Execute runs them.
- **Everything is logged:** each command and its output, with timestamps, to `merge_20261017_<timestamp>.log` in the scratchpad (path
  printed).

**Preconditions, all checked in both modes:**
- exact branch tips as observed now, as constants in the script: `opus/spellcheck`, `opus/spellcheck-r0`, `-s8`, `-l1f`, `-l1`,
  `rehearsal/merge-20261017` = a241ed75e;
- `opus/spellcheck` worktree tracked files clean;
- scratch worktree clean;
- no branch `rehearsal/merge-final` yet;
- `git stash list` untouched (just record it);
- no codex processes writing in this worktree.

**Steps** (in the scratch worktree, on a new branch `rehearsal/merge-final` from the CURRENT opus/spellcheck):
1. r0;
2. s8 (keep case.py/ink.py = opus/spellcheck; add the s8_l1r3 archive patch from the reference);
3. l1f (policy-hashed paths = opus/spellcheck SF6c; add the l1f archive patch from the reference);
4. l1 docs only (+ `docs/records/archive/l1_20261017/` exactly as on the reference);
5. fixtures commit (byte-identical to the reference);
6. Option C content taken from the reference (`l1r_recompose_ext.py`, driver/config/test changes, `test_policy_frozen_after_merge.py`),
   with NO Option-A archive (`docs/records/archive/l1r_line_20261017/` must not exist).

Resolve every conflict deterministically, with explicit `git checkout --ours/--theirs -- <path>` or `git checkout <ref> -- <path>` per
path, named in the script. An unexpected conflict path aborts.

**Post-checks that ABORT on mismatch:**
- (a) `git diff --name-status a241ed75e rehearsal/merge-final` equals an allowlist written in the script: the docs paths added on
  opus/spellcheck after 291f581a, plus the deletion of `docs/records/archive/l1r_line_20261017/**`;
- (b) the hashed-set diff vs opus/spellcheck is empty (paths from `release_gate.policy_binding()`);
- (c) the digest = 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406;
- (d) the `greekocr/` sha list is identical;
- (e) the full suite: failures only in the known pre-existing set (test_collection_outputs 3, test_provenance_cli_api 2,
  test_apply_clean 5 errors; flaky test_deadline_terminates_inflight_pool retried once), parsed from the pytest output.

**Fast-forward:**
- `git -C <main worktree> merge --ff-only rehearsal/merge-final`, with the untracked-collision handling: byte-identical untracked files
  are moved to `scratchpad/merge_untracked_backup/`; a non-identical one aborts.
- Then re-run checks (b)–(e) in the main worktree.
- Print the final sha.
- **NO push command anywhere in the script.** A test asserts that `git push` does not occur in the file.

## Tests and dry run

- Static tests: `bash -n`; shellcheck if available; the no-push assertion; the allowlist is non-empty and sorted.
- Run `--dry-run` yourself (read-only) and include its log in NOTES.

## Also

Copy the two launcher variants from the scratchpad into `docs/records/reviews/harness/`, with a README giving each one's diff vs the shared
`run_wt.sh` copy:
- `run_wt_medium_git.sh` (writable root; failed: codex keeps .git read-only);
- `run_wt_medium_gitfull.sh` (danger-full-access; NOT used, blocked by the session's permission policy; keep it as a record only).

Last line:
`MS READY: merge_20261017.sh <lines>; dry-run preconditions <ok|fail list>; tests <n> passed; no push yes`.
