# MR-C: move l1f's recomposition adapter into a NON-hashed module (rehearsal branch only) (gpt-6.1-sol, medium, network OFF)

Workspace: THIS scratch worktree (branch `rehearsal/merge-20261017`, a merge rehearsal of opus/spellcheck + r0/s8/l1f/l1).
- **This is a rehearsal branch. Never touch any real branch or any other worktree.** No `.git` writes (the lead commits).
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.

Context: `docs/records/cleanup_20261017/CLEANUP_MERGE_REHEARSAL.md` (owner decision sheet, risk 1, options A–D). The coordinator ruled **C**.

## Problem

The frozen release gate's `policy_binding()` hashes 16 repo-relative paths, including
`scripts/labelfix/clariden/l1r_recompose.py` and `l1_common.py`. It must stay at
`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`.

The rehearsal kept the SF6c versions of the hashed files. l1f's versions are archived in
`docs/records/archive/l1f_hashed_paths_20261017.patch` (and `s8_l1r3_hashed_paths_20261017.patch`). Against the SF6c `l1r_recompose`, the
L1R…L1R4 drivers break: 4 scripts don't import, and 6 drivers call a `--config` option that SF6c's version lacks. 15 tests fail:
`tests/labelfix/test_l1r.py` (7), `test_l1r2.py` (3), `test_l1r3.py` (5).

Option A is rehearsed as commit 698cdfa7 (drivers + 2 l1f configs + test_l1f.py archived to `docs/records/archive/l1r_line_20261017/`). Start
from the branch tip; if A's archive moves get in the way of C, revert them in your working tree and say so.

## Do (ruling C)

1. Create a NEW, non-hashed module holding the l1f recomposition functionality the L1R drivers need: the `--config` handling, the
   adapter functions and anything else the patch added. Take it from the archived l1f patch, e.g.
   `scripts/labelfix/clariden/l1r_recompose_ext.py`. It may import from the frozen `l1r_recompose.py` and `l1_common.py`; it must not
   modify them.
2. Point the L1R drivers (and their tests) at the new module. Restore any driver/config/test that Option A archived, if C makes it
   work again.
3. **Every one of the 16 policy-hashed paths stays byte-for-byte identical** to opus/spellcheck (SF6c): `git diff <opus/spellcheck>
   -- <the 16 paths>` must be EMPTY. Nothing in `greekocr/` changes.
4. New test `tests/labelfix/test_policy_frozen_after_merge.py`:
   - `release_gate.policy_binding()` digest == 6f62925a…c406;
   - no hashed path imports the new module (AST scan of the 16 paths);
   - `greekocr/` tree sha256 list == opus/spellcheck's.
5. Run the full `tests/` suite. **Target: the 15 L1R failures gone, 0 new failures.** The pre-existing environmental failures
   (test_collection_outputs 3, test_provenance_cli_api 2, test_apply_clean 5 errors, and the flaky
   test_deadline_terminates_inflight_pool) are not yours; list them separately.
6. **If C cannot reach 0 L1R failures without touching a hashed path, STOP.** Fall back to A: archive + `pytest.mark.xfail(reason=...)`
   on each remaining test, with the precise reason. Report why C failed.

## Report

`docs/records/cleanup_20261017/MR_C_REPORT.md`: the new module (functions, provenance from the l1f patch); the drivers changed; `git diff --stat` vs the branch
tip; the hashed-set diff (must be empty); digest; greekocr identical; test counts before/after.

Last line:
`MR-C READY: hashed diff empty <yes>; digest 6f62925a <yes>; L1R failures <15 -> n>; new failures <0>; suite <passed>/<failed>`.
