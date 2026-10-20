# MS4 tree checks and empty-directory reset — 17 October 2026

This section supersedes MS3's eight-path handoff count. Only the script, test, and NOTES are edited; the existing MS4 brief is for the lead to commit with these edits. No network calls, live Git writes, reset, or merge execution are performed. Test Git writes are confined to disposable synthetic repositories.

Both Option-A content gates now use `git ls-tree -r --name-only`: scratch checks `$FINAL`, and main checks `HEAD` after fast-forward. Empty leftover directories pass; tracked archive content aborts even when its file is absent on disk. A failed tree lookup aborts. The exact reference-delta check is retained.

The remaining filesystem existence checks were audited and retained: linked-worktree identity and in-progress operation metadata, collision/backup obstructions, Python executability, and scratchpad/log availability describe runtime filesystem state, not committed content. Handoff blob checks also intentionally compare actual working bytes and reject symlinks.

After guarded scratch checkout, reset uses `find "$SCRATCH" -mindepth 1 -type d -empty -delete -print`, through the execute/dry-run boundary. Find does not follow symlinks; only empty directories below scratch are deleted, and each successful deletion is printed into the normal timestamped log. The worktree root, non-empty directories, files, and paths outside scratch are preserved. Dry-run only prints the command. All existing reset guards remain.

`HANDOFF` now has nine paths including `docs/records/briefs/MS4_tree_check.md`; the exact reference allowlist adds that brief, bringing it to 18 rows. All nine blobs must match working bytes, and every intervening commit remains restricted to allowed additions/modifications.

Verification:

- `PYTHONDONTWRITEBYTECODE=1 python3 docs/records/reviews/harness/test_merge_20261017.py`: **69 passed, 1 skipped**, 70 total; Shellcheck is unavailable. Includes `bash -n`, exact nine-path/18-row checks, both tree gate refs, unreadable-tree refusal, reset deletion/logging/scope, and reset dry-run preservation. Output: `/private/tmp/ms4-tests.txt`.
- Normal `--dry-run` exit **1**; full output: `/private/tmp/ms4-dry-run.txt`. Remaining failures are **uncommitted edits** (MS4 addition pending, allowed-handoff net delta and tracked dirty), **final branch exists** (also scratch remains on `rehearsal/merge-final`; lead runs guarded reset first), and **Codex guard** (this session's worktree processes). Scratch is clean and has no `MERGE_HEAD`. No guard was bypassed in the live dry-run.
- `/private/tmp/ms4-snapshot.json` verifies refs, both HEADs, full statuses, stash, both index SHA256/mtime/size values, and scratchpad log inventory were identical before/after the live dry-run. Main remains at `77e4ab16083b00ba06a78bfa91f91cda337f99e1`. This results paragraph was written after that receipt; the tested script/test did not change.
- `git diff --check` passed. Only the requested three files are edited; the existing MS4 brief remains untracked for the lead's handoff commit.

MS4 READY: tree-based checks 2; reset removes empty dirs; handoff paths 9; tests 69 passed; dry-run remaining failures uncommitted edits, final branch exists (scratch on final), Codex guard.

---

# MS3 handoff-path update — 17 October 2026

This section supersedes the MS2 harness-only policy and live-history blocker below; the MS2 implementation and evidence are retained as historical notes. No live Git writes, network calls, scratch reset, or merge execution were performed. Git writes in tests remain confined to disposable synthetic repositories.

`HANDOFF` now contains exactly eight paths: the six existing harness files plus `docs/records/briefs/MS2_merge_script_fix.md` and `docs/records/briefs/MS3_handoff_paths.md`. Each commit since `16307355d9d247cf2abd5219b81735bcce110fb7` must remain linear and may only Add/Modify those paths. The net delta must be exactly the eight additions. All eight blobs, including the six harness files, are checked byte-for-byte against the working tree, with symlinks refused. Foreign edits remain rejected even if later reverted.

The exact post-merge delta allowlist versus `a241ed75e64e6ae3af2891aafe43eed3539174d4` already included the six harness additions. The two brief additions have been added, bringing that complete reference allowlist from 15 to 17 rows. Its other entries remain unchanged.

Verification:

- `PYTHONDONTWRITEBYTECODE=1 python3 docs/records/reviews/harness/test_merge_20261017.py`: **65 passed, 1 skipped**, 66 total. The skip is unavailable Shellcheck. `bash -n` and the no-push assertion passed within this suite. Output: `/private/tmp/ms3-tests.txt`.
- Six new tests cover the exact eight paths in both allowlists, sequential harness/MS2/MS3 commits with a harness modification, a foreign path in a later commit, a missing brief addition, brief deletion, and byte checks for each of the six harness files. The existing reverted-foreign-edit test remains intact.
- Normal `--dry-run` exit: **1**. Complete output: `/private/tmp/ms3-dry-run.txt`. The remaining failures are exactly these three categories:
  1. **Uncommitted edits:** the handoff net-delta assertion and `FAIL tip opus/spellcheck` occur because HEAD `6966d77a992f69ca927bebcab87bd40ecf05edf9` has seven allowed additions and the MS3 brief is still untracked. Every existing commit passed the allowed-path check. `FAIL main tracked dirty` names the script, test, and NOTES edits. The lead must commit these edits together with the MS3 brief.
  2. **Aborted scratch merge:** `FAIL scratch dirty`, `FAIL scratch branch rehearsal/merge-final`, `FAIL final branch exists`, and `FAIL scratch has MERGE_HEAD`. These are the known interrupted execute state; the lead runs guarded `--reset-scratch`.
  3. **Codex guard:** `FAIL process guard` reports this session's `codex` PID 82707 and `codex-code-mode-host` PID 82932 in the main worktree. No exemption was added.
- `PRECONDITIONS FAIL`, precondition exit 1, and the final ERR-trap pipeline report summarize those failures; they are not additional blockers. All five other pinned tips passed.
- Read-only receipt: `/private/tmp/ms3-snapshot.json` confirms refs, both HEADs, both full statuses, stash, both index SHA256/mtime/size values, and scratchpad log inventory were identical before and after the dry-run. This NOTES update was written after that receipt; the script/test are exactly the versions tested and previewed.

---

# MS2 merge script handoff — 17 October 2026

Only `merge_20261017.sh`, `test_merge_20261017.py`, and these notes were edited. No network calls, live Git writes, merge execution, scratch reset, launcher execution, or project-suite run were performed by Sol. Synthetic tests write only to disposable temporary repositories, as requested. The lead remains responsible for committing, resetting scratch, and executing the merge.

## Staged-state audit

The first execute log `merge_20261017_20261017T093753Z_78890.log` confirms the failure at `git rm -- L1_DEPLOY_FILES.txt`: the L1 merge had staged that path as an addition.

One removal command site was fixed: the `L1_OLD` loop now uses `git rm -f --`, covering all ten explicitly enumerated obsolete live L1 paths. This removes staged additions from both index and worktree during the in-progress merge. No other removal command exists in the script.

All source-tree path checkouts use `checkout "$BASE" -- <path>` or `checkout "$REFERENCE" -- <path>`. These replace index and worktree entries from the named commit, including staged entries and known conflicts; they require no force flag. The two branch checkouts are separately gated: final-branch creation follows clean-scratch preconditions, and scratch reset uses a non-forced checkout after merge abort. No broad forced branch checkout was added. The synthetic witness reproduces the original non-forced removal failure, exercises the actual fixed loop, and verifies source-tree checkout of a staged modification.

## Guarded scratch reset

Commands for the lead:

```bash
bash docs/records/reviews/harness/merge_20261017.sh --reset-scratch --dry-run
bash docs/records/reviews/harness/merge_20261017.sh --reset-scratch --execute
```

Bare `--reset-scratch` defaults to dry-run. Execute timestamps and writes a scratchpad log through the same logging path as normal execution; dry-run timestamps stdout and creates no log file. Normal `--dry-run` and `--execute` retain their existing behavior.

Reset validates the hard-coded scratch directory as a registered linked worktree in the main repository, distinct from main and its descendants. Main must remain on `opus/spellcheck`; scratch may be on only `rehearsal/merge-final` or `rehearsal/merge-20261017`. The reference branch must still point to `a241ed75e64e6ae3af2891aafe43eed3539174d4` and must not be checked out elsewhere. Other in-progress operations, untracked files, and unstaged edits cause refusal; unresolved merge entries are allowed only during a merge on the scratch final branch. Without a merge, scratch must be clean. The existing Codex process guard applies before any reset mutation.

If present, only the scratch merge is aborted. Scratch is checked out to the pinned reference branch, then the guards run again. Only `rehearsal/merge-final` may be deleted, and only after it is checked out nowhere and an ancestry check returns exactly 1 for final being an ancestor of `opus/spellcheck`. Missing final is harmless. An ancestor, another checkout, or an unreadable ancestry result causes refusal. The before guard allows final to be checked out in scratch solely so abort and checkout can precede the required unchecked deletion guard. Reset never updates main or any other branch. Failure stops in place; there is no automatic rollback or stash change.

## Harness-only handoff history

Main may now have a linear sequence of handoff commits after `16307355d9d247cf2abd5219b81735bcce110fb7`. Every individual commit must touch only the six literal `HANDOFF` files with additions or modifications. Reverted foreign edits also fail. The net delta must retain exactly the six harness additions, and all six tip blobs must match the working files byte-for-byte, with symlinks refused. The verified current tip becomes the rehearsal start. No SHA constant or reference allowlist was broadened.

**Live history blocker:** HEAD was already `6966d77a992f69ca927bebcab87bd40ecf05edf9`, the child of the original handoff `776b0a83d0c433d9900eb1d0ab2f57ba005e8e5e`. That child adds `docs/records/briefs/MS2_merge_script_fix.md`, outside `HANDOFF`. The requested strict check correctly rejects it. Merely committing this fix atop that tip will not resolve this blocker, and the same brief would also exceed the existing exact reference-delta allowlist. The lead must reconcile that history with the harness-only requirement before normal execution; Sol did not alter history or silently add a brief exception.

## Verification and live previews

- `PYTHONDONTWRITEBYTECODE=1 python3 docs/records/reviews/harness/test_merge_20261017.py`: **59 passed, 1 skipped**, 60 total. Shellcheck is unavailable. The suite includes the no-push assertion and `bash -n`; standalone `bash -n` also passed.
- Synthetic temporary repositories cover staged-addition removal, staged modification checkout, merge abort, pinned reference checkout, final-only deletion, dry-run index bytes/mtime and refs preservation, main/other-branch refusal, reference drift, final checked out elsewhere, ancestry refusal before abort, unstaged/untracked preservation, process-guard failure, and harness-only children with byte verification and reverted foreign edits rejected.
- Fresh normal `--dry-run` exit: **1**, with the complete output below. All five other pinned refs pass. Main fails the harness-only history check and is tracked-dirty from this preparation; scratch remains dirty on final with `MERGE_HEAD` and final still exists; the process guard detects this active session. The complete mutation plan prints, including ten forced L1 removals. These are expected refusals for the inspected state, not a successful merge rehearsal.
- `--reset-scratch --dry-run` exit: **1**. The actual scratch identity/branch/reference/ancestry guard passes; the active Codex process guard then refuses before abort or checkout. A successful reset and a successful reset dry-run are separately exercised in the synthetic repositories with the process inventory boundary isolated.
- Read-only receipt across both live previews: refs, both HEADs, full statuses, stash list, both index SHA256/mtime/size values, and scratchpad `merge_20261017_*.log` inventory are **identical before and after**. Capture receipts are `/private/tmp/ms2-dry-run.txt`, `/private/tmp/ms2-reset-dry-run.txt`, and `/private/tmp/ms2-snapshot.json`; test output is `/private/tmp/ms2-tests.txt`.
- The live dry-run was captured before the final test additions and this notes rewrite. The shell script itself is the exact version previewed. The captured dirty status therefore names the script and test; the notes file is also dirty after this handoff is written.

The frozen policy digest, exact reference tree delta, archive handling, full project-suite checks, collision backup, stash invariance, and final main fast-forward remain lead execution checks. This preparation does not claim those checks passed.

## Complete fresh normal dry-run output

Trailing spaces on timestamp-only blank lines are trimmed for repository whitespace checks; command and diagnostic content is otherwise unchanged.

```text
LOG: /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_20261017_20261017T094016Z_80753.log (execute only; dry-run logs to stdout and writes nothing)
2026-10-17T09:40:16+00:00 MODE --dry-run; MAIN /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck; SCRATCH /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal
2026-10-17T09:40:16+00:00 Handoff: commits since 16307355d9d247cf2abd5219b81735bcce110fb7 may touch only HANDOFF files; all tip blobs must match working bytes.
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/opus/spellcheck
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \<embedded\ helper\> handoff /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck 16307355d9d247cf2abd5219b81735bcce110fb7 6966d77a992f69ca927bebcab87bd40ecf05edf9 docs/records/reviews/harness/MERGE_SCRIPT_NOTES.md docs/records/reviews/harness/README.md docs/records/reviews/harness/merge_20261017.sh docs/records/reviews/harness/run_wt_medium_git.sh docs/records/reviews/harness/run_wt_medium_gitfull.sh docs/records/reviews/harness/test_merge_20261017.py
2026-10-17T09:40:16+00:00 READ git -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-list --parents 6966d77a992f69ca927bebcab87bd40ecf05edf9 ^16307355d9d247cf2abd5219b81735bcce110fb7
2026-10-17T09:40:16+00:00 READ git -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck diff --no-ext-diff --no-renames --name-status 776b0a83d0c433d9900eb1d0ab2f57ba005e8e5e 6966d77a992f69ca927bebcab87bd40ecf05edf9
2026-10-17T09:40:16+00:00 Traceback (most recent call last):
2026-10-17T09:40:16+00:00   File "<stdin>", line 175, in <module>
2026-10-17T09:40:16+00:00   File "<stdin>", line 18, in handoff
2026-10-17T09:40:16+00:00 AssertionError: non-harness commit path
2026-10-17T09:40:16+00:00 FAIL tip opus/spellcheck expected 16307355d9d247cf2abd5219b81735bcce110fb7 (main permits only verified harness-only history) actual 6966d77a992f69ca927bebcab87bd40ecf05edf9
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/opus/spellcheck-r0
2026-10-17T09:40:16+00:00 PASS tip opus/spellcheck-r0 7cef606f5a7c2d728625d192fc394d64d45f7301
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/opus/spellcheck-s8
2026-10-17T09:40:16+00:00 PASS tip opus/spellcheck-s8 2e1efb3be17494104653c4abad6666908442bba0
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/opus/spellcheck-l1f
2026-10-17T09:40:16+00:00 PASS tip opus/spellcheck-l1f ed5037aeeb108ed4cb58577f77071029eaa493f1
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/opus/spellcheck-l1
2026-10-17T09:40:16+00:00 PASS tip opus/spellcheck-l1 e3a694158996e5e29f1f67819853d79f8f44d724
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify refs/heads/rehearsal/merge-20261017
2026-10-17T09:40:16+00:00 PASS tip rehearsal/merge-20261017 a241ed75e64e6ae3af2891aafe43eed3539174d4
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck symbolic-ref --short HEAD
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck status --porcelain --untracked-files=no
2026-10-17T09:40:16+00:00 FAIL main tracked dirty:  M docs/records/reviews/harness/merge_20261017.sh
2026-10-17T09:40:16+00:00  M docs/records/reviews/harness/test_merge_20261017.py
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal status --porcelain --untracked-files=all
2026-10-17T09:40:16+00:00 FAIL scratch dirty: A  L1_DEPLOY_FILES.txt
2026-10-17T09:40:16+00:00 A  L1_DEPLOY_SHA256.txt
2026-10-17T09:40:16+00:00 A  L1_EXTERNAL_SHA256.txt
2026-10-17T09:40:16+00:00 A  docs/records/briefs/L1H_hold_analysis.md
2026-10-17T09:40:16+00:00 A  docs/records/briefs/L1M2_ownership_padding.md
2026-10-17T09:40:16+00:00 A  docs/records/briefs/L1M_masking_test.md
2026-10-17T09:40:16+00:00 A  docs/records/briefs/L1_scripts.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1C_census_3679781/AB_SF4_SUMMARY.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1C_census_3679781/CENSUS.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1C_census_3679781/CENSUS.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1C_census_3679781/receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_REPORT.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/aggregate.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/aggregate_login_attempt.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/aggregation.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/aggregation_ssh.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/build_report.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/build_stop_report.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/l1r_recompose_source_readback.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/pending_tables.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/probe.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/probe_ssh.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/release_gate_source_readback.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/release_manifests.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/sample_ids.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/samples.jsonl
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/schema_probe.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/status_by_wave.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1H_evidence/validation.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_REPORT.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/border_blobs.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/border_flags.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/details.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/lines.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/00c322b3ee04b419d1979f22-p000093-l0063.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/00c322b3ee04b419d1979f22-p000115-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/043b454a8c255b6690fd3777-p000008-l0056.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0550c3c52f2b388255690d5a-p000076-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0907df739607faca673d2169-p000018-l0042.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0a4bc4314e492706bcc0bf44-p000040-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0efd675a10c9a91816c7a41a-p000079-l0008.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0efd675a10c9a91816c7a41a-p000093-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/0efd675a10c9a91816c7a41a-p000186-l0025.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1092c25534f45a95669f3d2b-p000011-l0004.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1182f94b107a4cc4ada574da-p000037-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/12493332097bacc2a62b4d9a-p000024-l0009.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/137e9af6a0045d5746e26efa-p000006-l0009.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/137e9af6a0045d5746e26efa-p000008-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/143e78b5de2e6e784534ee0d-p000067-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1495fc2311427a558abbfd88-p000023-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1495fc2311427a558abbfd88-p000049-l0079.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1697d5cc21fa26717b97e073-p000019-l0066.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1c13bd49225f6fcf7dcca5a0-p000025-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1c13bd49225f6fcf7dcca5a0-p000091-l0017.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/1d9da09e2d3f82285de0cf2d-p000031-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/241c524ed5b20f2baadf4b8b-p000013-l0007.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/241c524ed5b20f2baadf4b8b-p000062-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000027-l0053.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000098-l0050.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000213-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000213-l0055.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000238-l0003.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/290a133b0e55593eb4ecdcfd-p000307-l0050.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/292f4a0b4f0dc8e6dddb103d-p000573-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/2b1d2b5340150ddc135a2b1a-p000153-l0027.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/2d29e5e76d90adc4cc1b093a-p000023-l0035.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/2f9e996ffbdaaa3b4a9dfdcf-p000049-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3249d506364999770e38aeef-p000022-l0052.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/32aae9fec147d3b483deb96e-p000011-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/32aae9fec147d3b483deb96e-p000019-l0072.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/32aae9fec147d3b483deb96e-p000052-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/32aae9fec147d3b483deb96e-p000060-l0057.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/32aae9fec147d3b483deb96e-p000076-l0055.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/341f77df7fe3f09264ceee79-p000017-l0008.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3598ebd512fe5593fddcc4ed-p000024-l0084.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3598ebd512fe5593fddcc4ed-p000030-l0044.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3598ebd512fe5593fddcc4ed-p000057-l0081.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/37a9179b-p000113-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/399d224c580127635c47cd8d-p000019-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/399d224c580127635c47cd8d-p000068-l0040.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/399d224c580127635c47cd8d-p000108-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/39fbbdfd2c8030f211a318b7-p000053-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3a469aeb16cd49371b9dfc3d-p000114-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3a469aeb16cd49371b9dfc3d-p000128-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3cb3c1caf7324ded3b11c1e5-p000010-l0061.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3cb3c1caf7324ded3b11c1e5-p000024-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3cb3c1caf7324ded3b11c1e5-p000024-l0044.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3cb3c1caf7324ded3b11c1e5-p000034-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/3cb3c1caf7324ded3b11c1e5-p000034-l0043.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/42c339ce492d83665f00774d-p000032-l0053.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/42c339ce492d83665f00774d-p000072-l0076.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/4c949ab8ae19e68be5a06c43-p000041-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/4c949ab8ae19e68be5a06c43-p000047-l0027.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/5165f9e7fe1f3d7053f5adcf-p000003-l0049.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/5a69150abb15eb1006f5a3ba-p000514-l0046.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/5a69150abb15eb1006f5a3ba-p000660-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/5e26b4de4e33e3295c6cf6c0-p000029-l0029.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/60b9798cc3e6f9f631070765-p000027-l0033.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/650670ab271096716888b108-p000019-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6a7f056059c027ecd8bffae2-p000043-l0060.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c0a582885e55adc7c535c48-p000016-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c0a582885e55adc7c535c48-p000029-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c0a582885e55adc7c535c48-p000055-l0034.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c0a582885e55adc7c535c48-p000149-l0053.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c0a582885e55adc7c535c48-p000149-l0061.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6c82556081bbe4aada41e496-p000030-l0038.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6d957fa757c72e1408f65dde-p000199-l0012.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6df192e72b10d13c5fc1374a-p000101-l0093.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6df192e72b10d13c5fc1374a-p000126-l0016.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/6f9ad9bf99fd956607f4f9b3-p000020-l0016.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7056dabdb0d8a5db4a0976f8-p000030-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7056dabdb0d8a5db4a0976f8-p000069-l0029.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7056dabdb0d8a5db4a0976f8-p000105-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7056dabdb0d8a5db4a0976f8-p000145-l0043.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/70e0a3447310acfc3f8dddf3-p000115-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/723c450ea9bb07fc4cdf47f9-p000124-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7cb612112b4f28a4f704a9cb-p000032-l0054.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7cb612112b4f28a4f704a9cb-p000052-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7cb612112b4f28a4f704a9cb-p000072-l0005.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7cb612112b4f28a4f704a9cb-p000075-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/7d1e098609bb25ba5bb9c0ed-p000050-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/80f0c63471e19f7383fa6f66-p000067-l0012.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/811cf35dbca2991bedc3ffac-p000117-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/827d2345ad77e5cdec320e80-p000022-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/827d2345ad77e5cdec320e80-p000028-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/827d2345ad77e5cdec320e80-p000036-l0029.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/827d2345ad77e5cdec320e80-p000059-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8298db8c50ae1b18df756118-p000012-l0033.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8298db8c50ae1b18df756118-p000024-l0009.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8298db8c50ae1b18df756118-p000028-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8298db8c50ae1b18df756118-p000046-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/82d33c43a02ea862069af4ad-p000166-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/82d33c43a02ea862069af4ad-p000258-l0035.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/83df10d25e7c4c1cefe2aed5-p000035-l0034.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8961f6bdd6daf004b4a84dfa-p000071-l0030.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8961f6bdd6daf004b4a84dfa-p000092-l0012.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8a482dd5cb341a70d157d5c4-p000364-l0021.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8b1c7bb49f3dc6c2519a8cc0-p000018-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8b1c7bb49f3dc6c2519a8cc0-p000018-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8b231047fdbd96ec30e1eded-p000032-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8b231047fdbd96ec30e1eded-p000033-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8b231047fdbd96ec30e1eded-p000038-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8c5bc46c09dbc633cc670d8b-p000032-l0005.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8c926ffa3b1b2be056e56b7e-p000250-l0040.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/8f477fb59c9bc6957aadc800-p000108-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/916a006055a9d43fdaa4c41b-p000008-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/92ab1a099d56dc9022fc4778-p000030-l0056.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/92ab1a099d56dc9022fc4778-p000032-l0011.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/92ab1a099d56dc9022fc4778-p000032-l0073.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/92ab1a099d56dc9022fc4778-p000035-l0068.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/96bb7196d840fe7513c2ed43-p000032-l0007.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/96bb7196d840fe7513c2ed43-p000038-l0012.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/99c8dbb018ec2c87af3fdce9-p000025-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/99c8dbb018ec2c87af3fdce9-p000054-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/9dd010d6eb008870ea7c536c-p000046-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a300f5e1c3f6a38d97201791-p000393-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a38045f531c81af524934fb8-p000009-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a38045f531c81af524934fb8-p000029-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a51f2efdcf758c1fa5ab52e6-p000024-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a51f2efdcf758c1fa5ab52e6-p000058-l0058.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a51f2efdcf758c1fa5ab52e6-p000078-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/a963b33d02c23d4127f5ec26-p000012-l0029.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/adc48c3e94eb469347d7cb4a-p000047-l0033.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/adc48c3e94eb469347d7cb4a-p000149-l0021.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/adc48c3e94eb469347d7cb4a-p000233-l0006.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b08a5423fb059fbb291900aa-p000056-l0038.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b08a5423fb059fbb291900aa-p000107-l0076.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b3c6afd03a5cab1b09b7d13e-p000036-l0056.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b3c6afd03a5cab1b09b7d13e-p000081-l0093.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p000447-l0043.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p001333-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p001333-l0060.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p001333-l0074.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p001776-l0088.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p002659-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b4266bf58120943ab8864b23-p002659-l0030.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b5076e8734ba287d549d79b5-p000041-l0007.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b5076e8734ba287d549d79b5-p000047-l0025.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b5076e8734ba287d549d79b5-p000073-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b518f9f9b73fe9a3257fe2f0-p000134-l0049.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b518f9f9b73fe9a3257fe2f0-p000171-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b5f8ce187b707837e5669281-p000038-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b5f8ce187b707837e5669281-p000063-l0060.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b8b6779da9a68fbed0ccdb5b-p000008-l0011.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b8b6779da9a68fbed0ccdb5b-p000011-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b8b6779da9a68fbed0ccdb5b-p000026-l0052.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b963a5d59be557e9eef8498b-p000042-l0020.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/b963a5d59be557e9eef8498b-p000057-l0065.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/bc780ca03714543a92331cd2-p000208-l0020.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/bf38261008b005a7898b7005-p000113-l0072.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c20219eff76f2fbc39f4c6fd-p000016-l0049.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c31a535c1436134ac8e91e5e-p000245-l0035.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c31a535c1436134ac8e91e5e-p000279-l0005.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c31a535c1436134ac8e91e5e-p000279-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c31a535c1436134ac8e91e5e-p000349-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c3468c02b6d929362f6e3fe7-p000082-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c569eefb453dc21fbe895554-p000094-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c8654864d161aa7fc41f65cb-p000226-l0020.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c8654864d161aa7fc41f65cb-p000226-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c8654864d161aa7fc41f65cb-p000226-l0030.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/c8654864d161aa7fc41f65cb-p001003-l0033.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/cc5059bc91ca2b178c20008c-p000025-l0034.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d0eda948e5b1f3632f8687fb-p000157-l0004.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d0eda948e5b1f3632f8687fb-p000620-l0025.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d0eda948e5b1f3632f8687fb-p000620-l0086.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d0eda948e5b1f3632f8687fb-p000773-l0032.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d0eda948e5b1f3632f8687fb-p000927-l0052.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d55d101cb2fa4c91b9e11083-p000046-l0006.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d9831a204aac7fccbd19bd58-p000013-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d9831a204aac7fccbd19bd58-p000017-l0006.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/d9831a204aac7fccbd19bd58-p000029-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/dc0f023a9668db71b2ffcb04-p000018-l0055.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/dc0f023a9668db71b2ffcb04-p000023-l0057.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/dc0f023a9668db71b2ffcb04-p000043-l0021.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/dc0f023a9668db71b2ffcb04-p000046-l0021.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/e1006e79dabe16c9460ae218-p000153-l0030.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/e28081a0d8ed58a169d0b77d-p000073-l0051.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/e32f8d6932bd505c2a0b1c8e-p000012-l0007.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/e85d2d01619fa0d87d878a35-p000031-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ecadd6f5c84ab0f85c671729-p000028-l0008.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ecadd6f5c84ab0f85c671729-p000193-l0036.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ee2ae82a5d56b54859d7385b-p000079-l0008.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ee2ae82a5d56b54859d7385b-p000117-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ef3cad078cfd452259f5b836-p000028-l0019.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/f3cfa262eedab9cd43a9e412-p000114-l0027.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/f77a8c0084022edb7981fb15-p000017-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/f77a8c0084022edb7981fb15-p000035-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/f77a8c0084022edb7981fb15-p000035-l0038.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/fa6c4ad060c9c9a1b0eb4843-p000114-l0025.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/fa6c4ad060c9c9a1b0eb4843-p000143-l0002.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/fdbb6015b076a41fcf67486b-p000031-l0024.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/fdbb6015b076a41fcf67486b-p000035-l0063.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/fdbb6015b076a41fcf67486b-p000052-l0061.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/pixels/ff1a79b283abb6e40e4b318b-p000024-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/slots.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/200/source_selected.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/SHA256SUMS.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/build_report.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/c1_membership.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/c1_selected_alignments.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/fetch_200_log.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/fetch_selected.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/fetch_vouli_log.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/01.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/02.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/03.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/04.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/05.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/06.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/07.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/08.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/09.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/10.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/11.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/12.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/sheet_1.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/sheet_2.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/sheet_3.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_panels/sheet_4.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/flip_visual_selection.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/line_guards.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/make_panels.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/SHA256SUMS.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/alignment.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/analyse.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/appendix.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/baseline.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/border_blobs.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/border_flags.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/exceptions.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/exceptions.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/flag_counts_independent.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/flag_transitions.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/input_hashes.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/lines.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/lines.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/masked_border_flags.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_01.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_02.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_03.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_04.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_05.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_06.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_07.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_08.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_09.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_10.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_11.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_12.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census/sheet_13.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/own_census_selection.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/padding_components.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/01.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/02.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/03.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/04.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/05.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/06.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/07.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/08.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/09.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/10.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/11.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/12.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/sheet_1.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/sheet_2.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/sheet_3.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/panels/sheet_4.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/run.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/summary.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/validate.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/validation.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/visual_review.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/visual_review.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/visual_selection.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/ownership/write_section.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/01.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/02.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/03.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/04.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/05.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/06.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/07.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/08.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/09.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/10.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/11.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/12.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/sheet_1.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/sheet_2.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/sheet_3.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/panels/sheet_4.png
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/per_line.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/projections.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/remote_200.json.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/remote_vouli.json.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/run_pair.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/slot_hold_reasons.csv
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/source_selected.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/staging_inventory.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/summary.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/validate_evidence.py
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/validation.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/visual_review.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/visual_review.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/visual_selection.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/border_blobs.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/border_flags.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/details.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/lines.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/0271e3cae771-p000005-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/07bc68f92367-p000004-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/17cbdf94881f-p000002-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/240e6345063d-p000001-l0082.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/2495f1aad484-p000001-l0111.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/2bcc4d069b39-p000004-l0034.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/4310963292e1-p000002-l0006.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/4310963292e1-p000017-l0018.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/4310963292e1-p000019-l0004.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/5090074e9fac-p000013-l0012.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/5090074e9fac-p000013-l0045.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000003-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000005-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000007-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000007-l0051.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000013-l0008.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/535ad352d7a7-p000015-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/63b665a3fb0f-p000008-l0036.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/65ad46153b1f-p000012-l0006.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/68ff7ed0985f-p000012-l0014.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/6cc7ddf6ed4e-p000015-l0056.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/6db81fc97db3-p000003-l0004.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/785410af1e5b-p000002-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/838d5080b03f-p000007-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/838d5080b03f-p000008-l0029.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/838d5080b03f-p000009-l0035.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/838d5080b03f-p000012-l0037.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/838d5080b03f-p000020-l0035.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/8c8a53ab3dd7-p000002-l0087.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/8c8a53ab3dd7-p000005-l0122.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/8c8a53ab3dd7-p000006-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/8cd0e8c1f0e5-p000001-l0066.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/8cd0e8c1f0e5-p000005-l0055.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/91252504a906-p000014-l0051.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/91252504a906-p000016-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/91252504a906-p000019-l0028.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/920a5a65051f-p000006-l0026.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/920a5a65051f-p000010-l0015.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/9e6fd8368590-p000003-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/a4fcf40ac18f-p000007-l0013.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/a4fcf40ac18f-p000014-l0039.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/aea7ecc2ca24-p000005-l0033.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/aee93d1337df-p000001-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/aee93d1337df-p000007-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/aee93d1337df-p000018-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/ba1c7cd4c91a-p000002-l0034.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/bec70ac3ff65-p000003-l0068.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/c8e289692021-p000003-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/ce43459c6fca-p000001-l0068.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d1dd97640ccb-p000007-l0005.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d7059ecf7417-p000006-l0022.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d7059ecf7417-p000013-l0002.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d9b7dfa900e3-p000002-l0021.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d9b7dfa900e3-p000002-l0023.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d9b7dfa900e3-p000014-l0007.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/d9b7dfa900e3-p000015-l0047.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/da9a31d7669d-p000003-l0017.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/da9a31d7669d-p000010-l0009.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/e046c3916322-p000002-l0010.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/pixels/f723eb9e115a-p000004-l0036.npz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/slots.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_evidence/vouli/source_selected.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_masking_sample_ids.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/L1M_masking_sample_ids_vouli.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_DEPLOY_FILES.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_DEPLOY_REMOTE_SHA256.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_DEPLOY_SHA256.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_EXTERNAL_SHA256.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_REPORT.md
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_binding.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_certificate.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_deploy.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_deploy_final.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_input_documents.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_input_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_inventory/L1_crop_inventory.jsonl.gz
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_inventory/inventory_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_local_revalidation.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_mock.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_mock_attempt1.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_mock_attempt2.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_mock_attempt3.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_mock_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_parity_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_prepare.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_pytest_l1.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_pytest_labelfix.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_readiness_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_remote_checks.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_remote_runtime.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_remote_sha256_final.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_E3_file_list_after.jsonl
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_E3_file_list_before.jsonl
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_pip_freeze.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_pip_install.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_runtime_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime/L1_scipy_SHA256.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime_build.log
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_runtime_receipt.json
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_sbatch_test_only.txt
2026-10-17T09:40:16+00:00 A  docs/records/labelfix/spellcheck/clariden/L1_timing_summary.json
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_inventory.py
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_job.sbatch
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_prepare.py
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_run.py
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_runtime.py
2026-10-17T09:40:16+00:00 A  scripts/labelfix/clariden/l1_verify.py
2026-10-17T09:40:16+00:00 A  tests/labelfix/test_l1.py
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal symbolic-ref --short HEAD
2026-10-17T09:40:16+00:00 FAIL scratch branch rehearsal/merge-final
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck show-ref --verify --quiet refs/heads/rehearsal/merge-final
2026-10-17T09:40:16+00:00 FAIL final branch exists
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck stash list --format=%gd\ %H\ %gs
2026-10-17T09:40:16+00:00 STASH (record only):
2026-10-17T09:40:16+00:00
2026-10-17T09:40:16+00:00 [2026-10-17T09:40:16Z] CMD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \<embedded\ helper\> processes /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal
2026-10-17T09:40:17+00:00 p4616
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Documents/Codex/2026-10-16/can-x20
2026-10-17T09:40:17+00:00 p22420
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/
2026-10-17T09:40:17+00:00 p22839
2026-10-17T09:40:17+00:00 ccodex-code-mode-host
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/
2026-10-17T09:40:17+00:00 p42470
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos
2026-10-17T09:40:17+00:00 p50399
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos
2026-10-17T09:40:17+00:00 p52782
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos
2026-10-17T09:40:17+00:00 p70023
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-plan
2026-10-17T09:40:17+00:00 p70200
2026-10-17T09:40:17+00:00 ccodex-code-mode-host
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-plan
2026-10-17T09:40:17+00:00 p76415
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/efficiency
2026-10-17T09:40:17+00:00 p76623
2026-10-17T09:40:17+00:00 ccodex-code-mode-host
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/efficiency
2026-10-17T09:40:17+00:00 p79434
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
2026-10-17T09:40:17+00:00 p79638
2026-10-17T09:40:17+00:00 ccodex-code-mode-host
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
2026-10-17T09:40:17+00:00 p91406
2026-10-17T09:40:17+00:00 ccodex-code-mode-host
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Users/foivoskarounos-zamparloukos
2026-10-17T09:40:17+00:00 p93395
2026-10-17T09:40:17+00:00 ccodex
2026-10-17T09:40:17+00:00 fcwd
2026-10-17T09:40:17+00:00 n/Applications/ChatGPT.app/Contents/Resources
2026-10-17T09:40:17+00:00 Traceback (most recent call last):
2026-10-17T09:40:17+00:00   File "<stdin>", line 177, in <module>
2026-10-17T09:40:17+00:00   File "<stdin>", line 76, in process_guard
2026-10-17T09:40:17+00:00 AssertionError: Codex worktree writer candidates (stop them before execution): [('79434', 'codex', '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck'), ('79638', 'codex-code-mode-host', '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')]
2026-10-17T09:40:17+00:00 FAIL process guard
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify --quiet MERGE_HEAD
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rev-parse --verify --quiet MERGE_HEAD
2026-10-17T09:40:17+00:00 e3a694158996e5e29f1f67819853d79f8f44d724
2026-10-17T09:40:17+00:00 FAIL scratch has MERGE_HEAD
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify --quiet CHERRY_PICK_HEAD
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rev-parse --verify --quiet CHERRY_PICK_HEAD
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse --verify --quiet REVERT_HEAD
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rev-parse --verify --quiet REVERT_HEAD
2026-10-17T09:40:17+00:00 PRECONDITIONS FAIL (see individual FAIL lines)
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout -b rehearsal/merge-final 16307355d9d247cf2abd5219b81735bcce110fb7
2026-10-17T09:40:17+00:00 MERGE opus/spellcheck-r0 at 7cef606f5a7c2d728625d192fc394d64d45f7301
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal merge --no-ff --no-commit 7cef606f5a7c2d728625d192fc394d64d45f7301
2026-10-17T09:40:17+00:00 CHECK: unmerged paths must be a subset of []; any other path aborts
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m merge\ r0:\ adjudicated\ docs
2026-10-17T09:40:17+00:00 MERGE opus/spellcheck-s8 at 2e1efb3be17494104653c4abad6666908442bba0
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal merge --no-ff --no-commit 2e1efb3be17494104653c4abad6666908442bba0
2026-10-17T09:40:17+00:00 CHECK: unmerged paths must be a subset of []; any other path aborts
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/case.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/ink.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/release_gate.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/text.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/segmentation.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1r_recompose.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_pages_build_combined.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/ctc_align.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/m2_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_extract.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_infer.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_measure.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_detect.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/archive/s8_l1r3_hashed_paths_20261017.patch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m merge\ s8:\ freeze\ SF6c\ and\ archive\ hashed\ candidate
2026-10-17T09:40:17+00:00 MERGE opus/spellcheck-l1f at ed5037aeeb108ed4cb58577f77071029eaa493f1
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal merge --no-ff --no-commit ed5037aeeb108ed4cb58577f77071029eaa493f1
2026-10-17T09:40:17+00:00 CHECK: unmerged paths must be a subset of [scripts/labelfix/clariden/l1r_recompose.py]; any other path aborts
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1r_recompose.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/release_gate.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/text.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/segmentation.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1r_recompose.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_pages_build_combined.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/ctc_align.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/m2_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_extract.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_infer.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_measure.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_detect.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/archive/l1f_hashed_paths_20261017.patch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m merge\ l1f:\ freeze\ SF6c\ and\ archive\ hashed\ candidate
2026-10-17T09:40:17+00:00 MERGE opus/spellcheck-l1 at e3a694158996e5e29f1f67819853d79f8f44d724
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal merge --no-ff --no-commit e3a694158996e5e29f1f67819853d79f8f44d724
2026-10-17T09:40:17+00:00 CHECK: unmerged paths must be a subset of [scripts/labelfix/clariden/l1_common.py scripts/labelfix/clariden/l1_detect.py scripts/labelfix/clariden/l1_infer.py]; any other path aborts
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_detect.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_infer.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/release_gate.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/text.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/segmentation.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1r_recompose.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_reading.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/owner_pages_build_combined.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- greekocr/labelfix/ctc_align.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/m2_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_extract.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_infer.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_measure.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1e_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/l1_detect.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout 16307355d9d247cf2abd5219b81735bcce110fb7 -- scripts/labelfix/clariden/r1_common.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- L1_DEPLOY_FILES.txt
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- L1_DEPLOY_SHA256.txt
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- L1_EXTERNAL_SHA256.txt
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_inventory.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_job.sbatch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_prepare.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_runtime.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- scripts/labelfix/clariden/l1_verify.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal rm -f -- tests/labelfix/test_l1.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/archive/l1_20261017
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m merge\ l1\ docs\ only:\ archive\ v0\ package\ verbatim
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- artifacts/labelfix_sf6/frozen_sf5_05f2dafb
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- artifacts/labelfix_l1e/fixture_v4
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m fixtures:\ exact\ reference\ bytes
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- config/l1f_job.json
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- config/l1f_mock.json
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_REPORT.md
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_evidence/l1r_after.log
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_evidence/l1r_before.log
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_evidence/suite_after.log
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_evidence/suite_before.log
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/cleanup_20261017/MR_C_evidence/verification.json
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- docs/records/briefs/MR_C_recompose_ext.md
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1f_job.sbatch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1f_mock_check.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1f_preflight.sh
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1f_run.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r3_preflight.sh
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r4_job.sbatch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r4_mock_check.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r4_preflight.sh
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r_job.sbatch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r_mock_check.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- scripts/labelfix/clariden/l1r_recompose_ext.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- tests/labelfix/test_l1f.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- tests/labelfix/test_l1r.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- tests/labelfix/test_l1r2.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- tests/labelfix/test_l1r3.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal checkout a241ed75e64e6ae3af2891aafe43eed3539174d4 -- tests/labelfix/test_policy_frozen_after_merge.py
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal commit -m Option\ C:\ non-hashed\ adapter\ and\ consumers\;\ no\ Option-A\ archive
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD check_tree
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD checks /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal scratch
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD helper processes /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD helper collisions /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rehearsal/merge-final /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_untracked_backup inspect
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD helper collisions /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rehearsal/merge-final /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_untracked_backup move
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck merge --ff-only rehearsal/merge-final
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD checks /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck main
2026-10-17T09:40:17+00:00 [2026-10-17T09:40:17Z] CMD g -C /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck rev-parse HEAD
2026-10-17T09:40:17+00:00 DRY-RUN COMPLETE; precondition exit=1; no files written
FAIL line 501: "$PYTHON" -u -c 'import datetime,sys
for line in sys.stdin:
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), line, end="", flush=True)' (exit 1)
```

MS2 READY: rm fixes 1; reset-scratch added; handoff check accepts harness-only children; tests 59 passed; dry-run preconditions FAIL (non-harness brief in live history, uncommitted edits, aborted scratch merge, active Codex guard).
