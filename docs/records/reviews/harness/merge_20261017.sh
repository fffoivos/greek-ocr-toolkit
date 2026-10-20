#!/usr/bin/env bash
# Owner-approved offline merge. Lead executes; preparation agent never executes writes.
set -euo pipefail
set -E
trap 'rc=$?; printf "FAIL line %s: %s (exit %s)\n" "$LINENO" "$BASH_COMMAND" "$rc" >&2; exit "$rc"' ERR
export GIT_OPTIONAL_LOCKS=0 GIT_NO_REPLACE_OBJECTS=1 PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
# Inherited pytest selection flags must not silently narrow the required full suite.
export PYTEST_ADDOPTS=
# Embedded safety checks use assertions; inherited optimization must not disable them.
export PYTHONOPTIMIZE=
MAIN=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
PAD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad
SCRATCH=$PAD/merge_rehearsal
PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
BASE=16307355d9d247cf2abd5219b81735bcce110fb7
REFERENCE=a241ed75e64e6ae3af2891aafe43eed3539174d4
START=$BASE
FINAL=rehearsal/merge-final
DIGEST=6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406
RESET_SCRATCH=0
if [[ ${1:-} == --reset-scratch ]]; then RESET_SCRATCH=1; shift; fi
MODE=${1:---dry-run}
[[ $# -le 1 && ( $MODE == --dry-run || $MODE == --execute ) ]] || { echo 'usage: merge_20261017.sh [--reset-scratch] [--dry-run|--execute]' >&2; exit 2; }

# Sorted, exact name-status delta from the reference; no wildcards.
ALLOWLIST=$(cat <<'ALLOWLIST_END'
A	docs/CLEANUP_MERGE_REHEARSAL_optionC.md
A	docs/SOL_ROUTING_spellcheck_20261017.md
A	docs/briefs/MERGE_final.md
A	docs/briefs/MS2_merge_script_fix.md
A	docs/briefs/MS3_handoff_paths.md
A	docs/briefs/MS4_tree_check.md
A	docs/briefs/MS_merge_script.md
A	docs/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md
A	docs/labelfix/spellcheck/R2_evidence/reader_errors_39_card_inputs.json
A	docs/labelfix/spellcheck/R2_evidence/reader_errors_39_owner_final.json
A	docs/reviews/harness/MERGE_SCRIPT_NOTES.md
A	docs/reviews/harness/README.md
A	docs/reviews/harness/merge_20261017.sh
A	docs/reviews/harness/run_wt_medium_git.sh
A	docs/reviews/harness/run_wt_medium_gitfull.sh
A	docs/reviews/harness/test_merge_20261017.py
D	docs/archive/l1r_line_20261017/README.md
M	docs/CLEANUP_MERGE_REHEARSAL.md
ALLOWLIST_END
)
TIPS=(
'opus/spellcheck 16307355d9d247cf2abd5219b81735bcce110fb7'
'opus/spellcheck-r0 7cef606f5a7c2d728625d192fc394d64d45f7301'
'opus/spellcheck-s8 2e1efb3be17494104653c4abad6666908442bba0'
'opus/spellcheck-l1f ed5037aeeb108ed4cb58577f77071029eaa493f1'
'opus/spellcheck-l1 e3a694158996e5e29f1f67819853d79f8f44d724'
'rehearsal/merge-20261017 a241ed75e64e6ae3af2891aafe43eed3539174d4'
)
# Only these nine handoff paths may change in commits since BASE.
# Every current handoff blob must equal its working-tree bytes.
HANDOFF=(
 docs/briefs/MS2_merge_script_fix.md docs/briefs/MS3_handoff_paths.md docs/briefs/MS4_tree_check.md
 docs/reviews/harness/MERGE_SCRIPT_NOTES.md docs/reviews/harness/README.md
 docs/reviews/harness/merge_20261017.sh docs/reviews/harness/run_wt_medium_git.sh
 docs/reviews/harness/run_wt_medium_gitfull.sh docs/reviews/harness/test_merge_20261017.py
)
HASHED=(
 greekocr/labelfix/release_gate.py greekocr/labelfix/reading.py
 greekocr/labelfix/text.py greekocr/labelfix/segmentation.py
 scripts/labelfix/clariden/l1_common.py scripts/labelfix/clariden/l1r_recompose.py
 scripts/labelfix/owner_reading.py scripts/labelfix/owner_pages_build_combined.py
 greekocr/labelfix/ctc_align.py scripts/labelfix/m2_run.py
 scripts/labelfix/clariden/r1_extract.py scripts/labelfix/clariden/l1_infer.py
 scripts/labelfix/clariden/l1e_measure.py scripts/labelfix/clariden/l1e_run.py
 scripts/labelfix/clariden/l1_detect.py scripts/labelfix/clariden/r1_common.py
)
# Every non-doc L1-v0 addition, explicitly removed from the live package.
L1_OLD=(
 L1_DEPLOY_FILES.txt L1_DEPLOY_SHA256.txt L1_EXTERNAL_SHA256.txt
 scripts/labelfix/clariden/l1_inventory.py scripts/labelfix/clariden/l1_job.sbatch
 scripts/labelfix/clariden/l1_prepare.py scripts/labelfix/clariden/l1_run.py
 scripts/labelfix/clariden/l1_runtime.py scripts/labelfix/clariden/l1_verify.py
 tests/labelfix/test_l1.py
)
OPTION_C=(
 config/l1f_job.json config/l1f_mock.json
 docs/MR_C_REPORT.md docs/MR_C_evidence/l1r_after.log docs/MR_C_evidence/l1r_before.log
 docs/MR_C_evidence/suite_after.log docs/MR_C_evidence/suite_before.log
 docs/MR_C_evidence/verification.json docs/briefs/MR_C_recompose_ext.md
 scripts/labelfix/clariden/l1f_job.sbatch scripts/labelfix/clariden/l1f_mock_check.py
 scripts/labelfix/clariden/l1f_preflight.sh scripts/labelfix/clariden/l1f_run.py
 scripts/labelfix/clariden/l1r3_preflight.sh scripts/labelfix/clariden/l1r4_job.sbatch
 scripts/labelfix/clariden/l1r4_mock_check.py scripts/labelfix/clariden/l1r4_preflight.sh
 scripts/labelfix/clariden/l1r_job.sbatch scripts/labelfix/clariden/l1r_mock_check.py
 scripts/labelfix/clariden/l1r_recompose_ext.py tests/labelfix/test_l1f.py
 tests/labelfix/test_l1r.py tests/labelfix/test_l1r2.py tests/labelfix/test_l1r3.py
 tests/labelfix/test_policy_frozen_after_merge.py
)
now() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
command_line() { printf '[%s] CMD' "$(now)" >&2; printf ' %q' "$@" >&2; printf '\n' >&2; }
run() { command_line "$@"; "$@"; }
# No hooks, signing prompts, editor, network or implicit rerere resolutions.
g() { run git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false "$@"; }
mutate() { if [[ $MODE == --execute ]]; then "$@"; else command_line "$@"; fi; }
fail() { printf 'ABORT: %s\n' "$*" >&2; return 1; }

# All Python operations are embedded: the delivered shell file is self-contained.
helper() {
 command_line "$PYTHON" '<embedded helper>' "$@"
 "$PYTHON" - "$@" <<'PY_HELPER'
import collections, hashlib, io, json, os, pathlib, re, shutil, subprocess, sys, tarfile
import xml.etree.ElementTree as ET

def git(root, *args):
    print('READ git -C', root, *args, flush=True)
    return subprocess.check_output(['git', '-C', root, *args])

def handoff(main, base, tip, paths):
    # Inspect every commit, not just the net diff: reverted foreign edits fail.
    rows = git(main, 'rev-list', '--parents', tip, '^'+base).decode().splitlines()
    assert rows, 'handoff must descend from base'
    current = tip
    for row in rows:
        fields = row.split()
        assert len(fields) == 2 and fields[0] == current, 'handoff must be a linear descendant of base'
        commit, parent = fields
        changed = git(main, 'diff', '--no-ext-diff', '--no-renames', '--name-status', parent, commit).decode().splitlines()
        assert all(r.split('\t', 1)[0] in ('A', 'M') and r.split('\t', 1)[1] in paths for r in changed), 'non-allowed handoff commit path'
        current = parent
    assert current == base, 'handoff must descend from base'
    delta = git(main, 'diff', '--no-ext-diff', '--no-renames', '--name-status', base, tip).decode().splitlines()
    assert delta == ['A\t'+p for p in sorted(paths)], 'handoff must retain exactly the allowed additions (commit pending handoff files first)'
    for p in paths:
        path = pathlib.Path(main)/p
        assert not path.is_symlink() and path.read_bytes() == git(main, 'show', tip+':'+p), 'handoff bytes differ: '+p
    print('PASS allowed-path handoff history and exact working bytes', tip)

def reset_guard(main, scratch, reference, final, phase):
    main, scratch = pathlib.Path(main).resolve(), pathlib.Path(scratch).resolve()
    assert scratch != main and main not in scratch.parents, 'refuse main worktree or its descendants'
    records = [dict(line.split(' ', 1) for line in block.splitlines() if ' ' in line)
               for block in git(str(main), 'worktree', 'list', '--porcelain').decode().strip().split('\n\n')]
    registered = {pathlib.Path(r['worktree']).resolve(): r for r in records}
    assert main in registered and scratch in registered, 'scratch must be a registered worktree'
    assert (scratch/'.git').is_file(), 'scratch must be a linked worktree'
    assert git(str(main), 'rev-parse', '--path-format=absolute', '--git-common-dir') == git(str(scratch), 'rev-parse', '--path-format=absolute', '--git-common-dir'), 'different repository'
    assert registered[main].get('branch') == 'refs/heads/opus/spellcheck', 'main branch changed'
    assert all(p == scratch or r.get('branch') != 'refs/heads/rehearsal/merge-20261017' for p,r in registered.items()), 'reference branch checked out elsewhere'
    branch = registered[scratch].get('branch')
    allowed = {'refs/heads/rehearsal/merge-20261017'}
    if phase == 'before': allowed.add('refs/heads/'+final)
    assert branch in allowed, 'refuse any other scratch branch'
    assert git(str(scratch), 'rev-parse', 'refs/heads/rehearsal/merge-20261017').decode().strip() == reference, 'reference branch moved'
    for op in ('CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer'):
        location = git(str(scratch), 'rev-parse', '--git-path', op).decode().strip()
        assert not (scratch/location).exists(), 'scratch has another operation: '+op
    merge_path = git(str(scratch), 'rev-parse', '--git-path', 'MERGE_HEAD').decode().strip()
    merging = (scratch/merge_path).exists()
    status = git(str(scratch), 'status', '--porcelain', '--untracked-files=all').decode().splitlines()
    if merging:
        assert phase == 'before' and branch == 'refs/heads/'+final, 'merge allowed only on final scratch branch'
        assert all(len(row) > 2 and (row[1] == ' ' or row[:2] in {'DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU'}) for row in status), 'scratch has unstaged/untracked changes'
    else:
        assert not status, 'scratch must be clean without a merge'
    refs = git(str(main), 'for-each-ref', '--format=%(refname)', 'refs/heads/'+final).decode().splitlines()
    if 'refs/heads/'+final in refs:
        owners = [p for p,r in registered.items() if r.get('branch') == 'refs/heads/'+final]
        assert not owners or (phase == 'before' and owners == [scratch]), 'final branch checked out elsewhere'
        rc = subprocess.run(['git', '-C', str(main), 'merge-base', '--is-ancestor', 'refs/heads/'+final, 'refs/heads/opus/spellcheck']).returncode
        assert rc == 1, 'final branch is an ancestor of main or ancestry check failed'
    print('PASS reset scratch guard', phase)

def process_guard(main, scratch):
    # Reject all Codex cwd candidates, even idle ones: no unverifiable writer exemption.
    p = subprocess.run(['lsof', '-a', '-c', 'codex', '-d', 'cwd', '-Fpcn'], capture_output=True, text=True)
    print(p.stdout, end=''); print(p.stderr, end='', file=sys.stderr)
    assert p.returncode in (0, 1) and not p.stderr, 'cannot inspect Codex processes'
    pid = command = ''; candidates = []
    for line in p.stdout.splitlines():
        if line.startswith('p'): pid = line[1:]
        if line.startswith('c'): command = line[1:]
        if line.startswith('n'):
            cwd = pathlib.Path(line[1:]).resolve()
            if any(cwd == pathlib.Path(r).resolve() or pathlib.Path(r).resolve() in cwd.parents for r in (main, scratch)):
                candidates.append((pid, command, str(cwd)))
    assert not candidates, f'Codex worktree writer candidates (stop them before execution): {candidates}'

def policy(root, base, digest, paths):
    sys.path.insert(0, root); os.chdir(root)
    from greekocr.labelfix.release_gate import policy_binding
    binding = policy_binding()
    print(json.dumps(binding, sort_keys=True, indent=2))
    assert sorted(binding['sources']) == sorted(paths), 'policy source set changed'
    assert binding['sha256'] == digest, 'digest mismatch'
    assert not git(root, 'diff', '--no-ext-diff', base, 'HEAD', '--', *binding['sources']), 'hashed tree differs'
    assert not git(root, 'diff', '--no-ext-diff', base, '--', *binding['sources']), 'hashed bytes differ'
    expected = {}
    with tarfile.open(fileobj=io.BytesIO(git(root, 'archive', base, '--', 'greekocr/'))) as archive:
        for entry in archive:
            if entry.isfile(): expected[entry.name] = hashlib.sha256(archive.extractfile(entry).read()).hexdigest()
    names = git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', 'greekocr/').split(b'\0')
    actual = {os.fsdecode(n): hashlib.sha256((pathlib.Path(root)/os.fsdecode(n)).read_bytes()).hexdigest() for n in names if n}
    assert actual == expected, 'greekocr sha list differs'
    for name in sorted(actual): print(actual[name], name)
    print('PASS hashed diff, policy digest, greekocr sha list')

KNOWN = {
 'FAILED': {
  'tests/test_collection_outputs.py::test_provenance_sums_all_wave_budgets',
  'tests/test_collection_outputs.py::test_frozen_wave_inputs_remain_unchanged',
  'tests/test_collection_outputs.py::test_sheet_index_lists_every_existing_admission_image',
  'tests/test_provenance_cli_api.py::test_all_vendored_files_are_in_inventory',
  'tests/test_provenance_cli_api.py::test_public_callables_typed_and_documented'},
 'ERROR': {'tests/test_apply_clean.py::'+n for n in (
  'test_counts_add_up', 'test_relabels_applied', 'test_books_are_split_disjoint_and_lexicon_in_train',
  'test_no_train_label_in_holdout', 'test_manifests_match_rows')},
}
FLAKY = 'tests/labelfix/test_s8_fetch_job.py::test_deadline_terminates_inflight_pool'

def suite(log, xml, rc, retry=False):
    text = pathlib.Path(log).read_text()
    rc = int(rc); assert rc in (0, 1), f'pytest abnormal exit {rc}'
    rows = re.findall(r'^(FAILED|ERROR) (\S+)', text, re.M)
    failures = collections.Counter(rows)
    assert all(n == 1 for n in failures.values()), 'duplicate failure summary'
    allowed = {'FAILED': {FLAKY}, 'ERROR': set()} if retry else {k: set(v) for k, v in KNOWN.items()}
    if not retry: allowed['FAILED'].add(FLAKY)
    for status, node in rows: assert node in allowed[status], f'new {status}: {node}'
    tree = ET.parse(xml); cases = tree.findall('.//testcase')
    counts = collections.Counter()
    passed = collections.Counter()
    for case in cases:
        counts['failed'] += case.find('failure') is not None
        counts['error'] += case.find('error') is not None
        if not any(case.find(k) is not None for k in ('failure','error','skipped')):
            counts['passed'] += 1; passed[case.get('classname', '').split('.')[-1]] += 1
    assert counts['failed'] == sum(s == 'FAILED' for s,n in rows), 'XML/output failures differ'
    assert counts['error'] == sum(s == 'ERROR' for s,n in rows), 'XML/output errors differ'
    assert counts['passed'] > 0, 'no passing tests'
    assert (rc == 0) == (not rows), 'exit/summary mismatch'
    if retry:
        assert len(cases) == 1 and not rows and counts['passed'] == 1, 'flaky retry did not pass'
    else:
        for module in ('test_l1r','test_l1r2','test_l1r3','test_l1f','test_policy_frozen_after_merge'):
            matching = [c for c in cases if c.get('classname','').split('.')[-1] == module]
            assert matching and passed[module] == len(matching), f'{module} absent, skipped or failed'
    print('SUITE ACCEPTED', dict(counts), 'known summaries', rows)
    return any(n == FLAKY for s,n in rows)

def collisions(main, incoming, backup, move):
    root = pathlib.Path(main); dest = pathlib.Path(backup)
    tracked = set(git(main, 'ls-files', '-z').split(b'\0'))
    entries = git(main, 'ls-tree', '-rz', incoming).split(b'\0'); pending = []
    for entry in entries:
        if not entry: continue
        meta, name = entry.split(b'\t',1); mode, kind, oid = meta.split()
        path = root/os.fsdecode(name)
        for parent in path.parents:
            if parent == root: break
            assert not parent.is_symlink() and (not parent.exists() or parent.is_dir()), f'ancestor obstruction {parent}'
        if name in tracked or not os.path.lexists(path): continue
        assert kind == b'blob' and not path.is_dir(), f'untracked obstruction {path}'
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
        expected = git(main, 'cat-file', 'blob', oid.decode())
        assert (mode == b'120000') == path.is_symlink() and data == expected, f'non-identical collision: {path}'
        target = dest/os.fsdecode(name)
        assert not os.path.lexists(target), f'backup already exists: {target}'
        for parent in target.parents:
            assert not parent.is_symlink(), f'backup symlink: {parent}'
            if parent == dest.parent: break
        pending.append((path, target, hashlib.sha256(data).hexdigest()))
    # Validate the complete set before moving anything.
    for path, target, sha in pending:
        print('IDENTICAL COLLISION', sha, path, '->', target, flush=True)
    if move:
        for path, target, sha in pending:
            data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == sha and not os.path.lexists(target), 'collision changed'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target)); print('MOVED', path, '->', target, flush=True)
    print('collision count', len(pending))

if __name__ == '__main__':
    action, *args = sys.argv[1:]
    if action == 'handoff': handoff(*args[:3], args[3:])
    elif action == 'reset-guard': reset_guard(*args)
    elif action == 'processes': process_guard(*args)
    elif action == 'policy': policy(*args[:3], args[3:])
    elif action == 'suite':
        flaky = suite(*args[:3], retry=len(args)>3)
        if flaky: print('RETRY_FLAKY')
    elif action == 'collisions': collisions(*args[:3], move=args[3]=='move')
    else: raise SystemExit('unknown helper action')
PY_HELPER
}

preconditions() {
 local bad=0 item branch tip got status
 for item in "${TIPS[@]}"; do
  branch=${item% *}; tip=${item#* }
  got=$(g -C "$MAIN" rev-parse --verify "refs/heads/$branch") || { bad=1; got=UNREADABLE; }
  if [[ $got == "$tip" ]]; then
   echo "PASS tip $branch $got"
  elif [[ $branch == opus/spellcheck ]] && helper handoff "$MAIN" "$BASE" "$got" "${HANDOFF[@]}"; then
   START=$got
  else
   echo "FAIL tip $branch expected $tip (main permits only verified allowed-path handoff history) actual $got"; bad=1
  fi
 done
 got=$(g -C "$MAIN" symbolic-ref --short HEAD)
 if [[ $got != opus/spellcheck ]]; then echo "FAIL main branch $got"; bad=1; fi
 status=$(g -C "$MAIN" status --porcelain --untracked-files=no) || { bad=1; status=UNREADABLE; }
 if [[ -n $status ]]; then echo "FAIL main tracked dirty: $status"; bad=1; else echo 'PASS main tracked clean'; fi
 status=$(g -C "$SCRATCH" status --porcelain --untracked-files=all) || { bad=1; status=UNREADABLE; }
 if [[ -n $status ]]; then echo "FAIL scratch dirty: $status"; bad=1; else echo 'PASS scratch clean'; fi
 got=$(g -C "$SCRATCH" symbolic-ref --short HEAD)
 if [[ $got != rehearsal/merge-20261017 ]]; then echo "FAIL scratch branch $got"; bad=1; fi
 local ref_rc=0
 g -C "$MAIN" show-ref --verify --quiet "refs/heads/$FINAL" || ref_rc=$?
 case $ref_rc in
  0) echo 'FAIL final branch exists'; bad=1 ;;
  1) echo 'PASS final branch absent' ;;
  *) echo "FAIL cannot inspect final branch (rc=$ref_rc)"; bad=1 ;;
 esac
 STASH_BEFORE=$(g -C "$MAIN" stash list --format='%gd %H %gs') || { bad=1; STASH_BEFORE=UNREADABLE; }
 printf 'STASH (record only):\n%s\n' "$STASH_BEFORE"
 if helper processes "$MAIN" "$SCRATCH"; then echo 'PASS no Codex worktree writer candidates'; else echo 'FAIL process guard'; bad=1; fi
 for branch in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
  if g -C "$MAIN" rev-parse --verify --quiet "$branch"; then echo "FAIL main has $branch"; bad=1; fi
  if g -C "$SCRATCH" rev-parse --verify --quiet "$branch"; then echo "FAIL scratch has $branch"; bad=1; fi
 done
 if [[ $MODE == --execute && $START == "$BASE" ]]; then echo 'FAIL lead must first commit the nine handoff paths'; bad=1; fi
 if [[ ! -x $PYTHON ]]; then echo 'FAIL Python missing'; bad=1; fi
 if [[ $bad == 0 ]]; then echo 'PRECONDITIONS OK'; else echo 'PRECONDITIONS FAIL (see individual FAIL lines)'; fi
 return "$bad"
}
stash_unchanged() {
 local after
 after=$(g -C "$MAIN" stash list --format='%gd %H %gs')
 [[ $after == "$STASH_BEFORE" ]] || fail 'stash list changed'
}
freeze_policy() {
 local p
 # Source-tree path checkout replaces index and worktree, including staged entries.
 for p in "${HASHED[@]}"; do mutate g -C "$SCRATCH" checkout "$BASE" -- "$p"; done
}
merge_stage() {
 local branch=$1 allowed=$2 rc=0 conflicts path found=0 item pin=''
 # Merge immutable commits, so a concurrent ref advance cannot change the plan.
 for item in "${TIPS[@]}"; do
  if [[ ${item% *} == "$branch" ]]; then pin=${item#* }; break; fi
 done
 [[ -n $pin ]] || { fail "merge branch has no pinned tip: $branch"; return 1; }
 echo "MERGE $branch at $pin"
 mutate g -C "$SCRATCH" merge --no-ff --no-commit "$pin" || rc=$?
 if [[ $MODE == --dry-run ]]; then
  echo "CHECK: unmerged paths must be a subset of [$allowed]; any other path aborts"
  return
 fi
 conflicts=$(g -C "$SCRATCH" diff --name-only --diff-filter=U)
 while IFS= read -r path; do
  [[ -z $path ]] && continue
  case " $allowed " in *" $path "*) found=1 ;; *) fail "unexpected conflict: $path"; return 1 ;; esac
 done <<< "$conflicts"
 [[ $rc == 0 || ( $rc == 1 && $found == 1 ) ]] || fail "merge failed without expected conflicts: $branch rc=$rc"
 g -C "$SCRATCH" rev-parse --verify MERGE_HEAD
}
commit_stage() {
 local label=$1
 if [[ $MODE == --execute ]]; then
  [[ -z $(g -C "$SCRATCH" diff --name-only --diff-filter=U) ]] || fail 'unresolved conflicts'
 fi
 mutate g -C "$SCRATCH" commit -m "$label"
}
restore_reference() {
 local p
 for p in "$@"; do mutate g -C "$SCRATCH" checkout "$REFERENCE" -- "$p"; done
}
check_no_option_a() {
 local tree=$1 ref=$2 entries
 # Check committed content; Git does not track empty leftover directories.
 entries=$(g -C "$tree" ls-tree -r --name-only "$ref" -- docs/archive/l1r_line_20261017)
 [[ -z $entries ]] || fail "Option-A archive exists in tree $ref: $entries"
}
check_tree() {
 local actual
 actual=$(g -C "$SCRATCH" diff --no-ext-diff --no-renames --name-status "$REFERENCE" "$FINAL" | sort)
 printf 'REFERENCE DELTA:\n%s\n' "$actual"
 [[ $actual == "$ALLOWLIST" ]] || fail 'reference delta not equal to literal allowlist'
 check_no_option_a "$SCRATCH" "$FINAL"
}
run_suite() {
 local tree=$1 label=$2 rc=0 parsed retry_rc=0
 local out=$PAD/merge_20261017_${STAMP}_${label}_pytest.log
 local xml=$PAD/merge_20261017_${STAMP}_${label}_pytest.xml
 (
  cd "$tree"
  run env PYTHONPATH="$tree" "$PYTHON" -m pytest -q -ra -p no:cacheprovider --color=no --junitxml="$xml" tests/
 ) 2>&1 | tee "$out" || rc=$?
 parsed=$(helper suite "$out" "$xml" "$rc")
 printf '%s\n' "$parsed"
 if [[ $parsed == *RETRY_FLAKY* ]]; then
  (
   cd "$tree"
   run env PYTHONPATH="$tree" "$PYTHON" -m pytest -q -ra -p no:cacheprovider --color=no --junitxml="${xml%.xml}_retry.xml" tests/labelfix/test_s8_fetch_job.py::test_deadline_terminates_inflight_pool
  ) 2>&1 | tee "${out%.log}_retry.log" || retry_rc=$?
  helper suite "${out%.log}_retry.log" "${xml%.xml}_retry.xml" "$retry_rc" retry
 fi
}
checks() {
 local tree=$1 label=$2
 helper policy "$tree" "$BASE" "$DIGEST" "${HASHED[@]}"
 run_suite "$tree" "$label"
 # Tests may generate artifacts, but must not change tracked bytes.
 [[ -z $(g -C "$tree" status --porcelain --untracked-files=no) ]] || fail 'suite changed tracked files'
 stash_unchanged
}
sequence() {
 local p
 mutate g -C "$SCRATCH" checkout -b "$FINAL" "$START"
 merge_stage opus/spellcheck-r0 ''
 commit_stage 'merge r0: adjudicated docs'
 merge_stage opus/spellcheck-s8 ''
 # Explicit per-path SF6c rulings, even when the textual merge is clean.
 mutate g -C "$SCRATCH" checkout "$BASE" -- greekocr/labelfix/case.py
 mutate g -C "$SCRATCH" checkout "$BASE" -- greekocr/labelfix/ink.py
 freeze_policy
 restore_reference docs/archive/s8_l1r3_hashed_paths_20261017.patch
 commit_stage 'merge s8: freeze SF6c and archive hashed candidate'
 merge_stage opus/spellcheck-l1f 'scripts/labelfix/clariden/l1r_recompose.py'
 mutate g -C "$SCRATCH" checkout "$BASE" -- scripts/labelfix/clariden/l1r_recompose.py
 freeze_policy
 restore_reference docs/archive/l1f_hashed_paths_20261017.patch
 commit_stage 'merge l1f: freeze SF6c and archive hashed candidate'
 merge_stage opus/spellcheck-l1 'scripts/labelfix/clariden/l1_common.py scripts/labelfix/clariden/l1_detect.py scripts/labelfix/clariden/l1_infer.py'
 mutate g -C "$SCRATCH" checkout "$BASE" -- scripts/labelfix/clariden/l1_common.py
 mutate g -C "$SCRATCH" checkout "$BASE" -- scripts/labelfix/clariden/l1_detect.py
 mutate g -C "$SCRATCH" checkout "$BASE" -- scripts/labelfix/clariden/l1_infer.py
 freeze_policy
 for p in "${L1_OLD[@]}"; do mutate g -C "$SCRATCH" rm -f -- "$p"; done
 restore_reference docs/archive/l1_20261017
 if [[ $MODE == --execute ]]; then
  while IFS= read -r p; do [[ $p == docs/* ]] || fail "l1 is not docs only: $p"; done < <(g -C "$SCRATCH" diff --cached --name-only HEAD)
 fi
 commit_stage 'merge l1 docs only: archive v0 package verbatim'
 restore_reference artifacts/labelfix_sf6/frozen_sf5_05f2dafb artifacts/labelfix_l1e/fixture_v4
 commit_stage 'fixtures: exact reference bytes'
 restore_reference "${OPTION_C[@]}"
 commit_stage 'Option C: non-hashed adapter and consumers; no Option-A archive'
 if [[ $MODE == --dry-run ]]; then
  command_line check_tree
  command_line checks "$SCRATCH" scratch
  command_line helper processes "$MAIN" "$SCRATCH"
  command_line helper collisions "$MAIN" "$FINAL" "$PAD/merge_untracked_backup" inspect
  command_line helper collisions "$MAIN" "$FINAL" "$PAD/merge_untracked_backup" move
  command_line g -C "$MAIN" merge --ff-only "$FINAL"
  command_line checks "$MAIN" main
  command_line g -C "$MAIN" rev-parse HEAD
  return
 fi
 check_tree
 checks "$SCRATCH" scratch
 # Revalidate before touching the main worktree. Never use an advanced main as baseline.
 [[ $(g -C "$MAIN" rev-parse HEAD) == "$START" ]] || fail 'main moved during rehearsal'
 [[ $(g -C "$MAIN" symbolic-ref --short HEAD) == opus/spellcheck ]] || fail 'main branch changed'
 [[ -z $(g -C "$MAIN" status --porcelain --untracked-files=no) ]] || fail 'main became dirty'
 helper processes "$MAIN" "$SCRATCH"
 stash_unchanged
 helper collisions "$MAIN" "$FINAL" "$PAD/merge_untracked_backup" inspect
 helper collisions "$MAIN" "$FINAL" "$PAD/merge_untracked_backup" move
 g -C "$MAIN" merge --ff-only "$FINAL"
 checks "$MAIN" main
 check_no_option_a "$MAIN" HEAD
 echo "FINAL SHA: $(g -C "$MAIN" rev-parse HEAD)"
}
reset_scratch() {
 helper reset-guard "$MAIN" "$SCRATCH" "$REFERENCE" "$FINAL" before
 helper processes "$MAIN" "$SCRATCH"
 if g -C "$SCRATCH" rev-parse --verify --quiet MERGE_HEAD; then
  mutate g -C "$SCRATCH" merge --abort
 fi
 mutate g -C "$SCRATCH" checkout rehearsal/merge-20261017
 # Depth-first find deletes only empty directories, retaining the worktree root.
 # Print after successful deletion so every removed directory is logged.
 mutate run find "$SCRATCH" -mindepth 1 -type d -empty -delete -print
 if [[ $MODE == --execute ]]; then
  helper reset-guard "$MAIN" "$SCRATCH" "$REFERENCE" "$FINAL" after
 else
  command_line helper reset-guard "$MAIN" "$SCRATCH" "$REFERENCE" "$FINAL" after
 fi
 if g -C "$SCRATCH" show-ref --verify --quiet "refs/heads/$FINAL"; then
  mutate g -C "$SCRATCH" branch -D -- "$FINAL"
 fi
 echo "RESET-SCRATCH COMPLETE; mode=$MODE"
}
main() {
 local rc=0
 echo "MODE $MODE; MAIN $MAIN; SCRATCH $SCRATCH"
 if [[ $RESET_SCRATCH == 1 ]]; then reset_scratch; return; fi
 echo "Handoff: commits since $BASE may touch only HANDOFF files; all tip blobs must match working bytes."
 preconditions || rc=$?
 if [[ $MODE == --execute && $rc != 0 ]]; then return "$rc"; fi
 sequence
 if [[ $MODE == --dry-run ]]; then echo "DRY-RUN COMPLETE; precondition exit=$rc; no files written"; fi
 return "$rc"
}
STAMP=$(date -u '+%Y%m%dT%H%M%SZ')_$$
if [[ $MODE == --execute ]]; then
 LOG=$PAD/merge_20261017_${STAMP}.log
 [[ -d $PAD && ! -e $LOG ]] || fail 'scratchpad missing or log already exists'
 printf 'LOG: %s\n' "$LOG"
 # Entire command/output stream timestamped, synchronous tee; pipeline errors propagate.
 main 2>&1 | "$PYTHON" -u -c 'import datetime,sys
for line in sys.stdin:
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), line, end="", flush=True)' | tee "$LOG"
else
 echo "LOG: $PAD/merge_20261017_${STAMP}.log (execute only; dry-run logs to stdout and writes nothing)"
 main 2>&1 | "$PYTHON" -u -c 'import datetime,sys
for line in sys.stdin:
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), line, end="", flush=True)'
fi
