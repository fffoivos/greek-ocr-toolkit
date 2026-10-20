#!/usr/bin/env bash
# SYNC3: offline, resumable pinned-source merge. Preparation agent writes/tests; lead executes.
set -euo pipefail
set -E
export GIT_OPTIONAL_LOCKS=0 GIT_NO_REPLACE_OBJECTS=1 PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
export PYTEST_ADDOPTS= PYTHONOPTIMIZE=
# Offline dependencies; the git boundary also rejects network subcommands.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PIP_NO_INDEX=1
MAIN=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
PAD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad
PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
SOURCE=opus/spellcheck
SOURCE_TIP=ac35c174b038eae08c977562a0a1a4e4ec76c306
DIGEST=6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406
BRANCHES=(opus/cleanup-1 opus/r2-prep)
ROOTS=(/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2prep)
CLEANUP_MERGE=b4234ee0e229a2729bfe37e539fc33bba9db24d8
TIPS=(6fe84030c8f65223b2c5065bc394d608b8f2616f d78b472b7d46dff3a005ef52b23c00ad2b25e404)
# opus/r2-cards is deliberately absent: active Sol runs, later separately pinned run.
MODE=${1:---dry-run}
[[ $# -le 1 && ( $MODE == --dry-run || $MODE == --execute ) ]] || { echo 'usage: sync_20261017.sh [--dry-run|--execute]' >&2; exit 2; }
ACTIVE=
now() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
command_line() { printf '[%s] CMD' "$(now)" >&2; printf ' %q' "$@" >&2; printf '\n' >&2; }
run() { command_line "$@"; "$@"; }
# Only local commands; no hooks, signing, external diff, editors or rerere.
g() {
 local arg
 for arg in "$@"; do
  case $arg in push|fetch|pull|clone|ls-remote|remote|submodule) echo "Forbidden git command: $arg" >&2; return 97;; esac
 done
 run git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c rerere.enabled=false -c rerere.autoupdate=false -c core.fsmonitor=false -c core.untrackedCache=false "$@"
}
fail() { printf 'ABORT: %s\n' "$*" >&2; return 1; }
on_error() {
 local rc=$1 line=$2 cmd=$3
 trap - ERR
 printf 'FAIL line %s: %s (exit %s)\n' "$line" "$cmd" "$rc" >&2
 if [[ -n $ACTIVE ]] && g -C "$ACTIVE" rev-parse --verify --quiet MERGE_HEAD >/dev/null; then
  g -C "$ACTIVE" merge --abort || echo 'ABORT FAILED: lead must inspect merge state' >&2
 fi
 # Completed merges are retained for inspection on a post-check failure; no reset.
 exit "$rc"
}
trap 'on_error "$?" "$LINENO" "$BASH_COMMAND"' ERR
helper() {
 command_line "$PYTHON" '<embedded helper>' "$@"
 "$PYTHON" - "$@" <<'PY_HELPER'
import collections, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

def git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false', '-C', root, *args])

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

def restricted_range(root, base, tip, *allowed):
    subprocess.check_call(['git', '-C', root, 'merge-base', '--is-ancestor', base, tip])
    # Inspect every commit, not just the net tree diff: reverted edits also count.
    commits = git(root, 'rev-list', base+'..'+tip).decode().splitlines()
    touched = set()
    for commit in commits:
        touched.update(os.fsdecode(p) for p in git(
            root, 'diff-tree', '--root', '-m', '--no-commit-id', '--name-only',
            '--no-renames', '-r', '-z', commit).split(b'\0') if p)
    unexpected = sorted(touched - set(allowed))
    assert not unexpected, f'unapproved paths since {base}: {unexpected}'
    print('PASS restricted history', base, tip, 'commits', len(commits), 'paths', sorted(touched))

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

def predict(root, old, source):
    # merge-tree writes objects, so isolate ALL new objects in a disposable ODB.
    # Existing repository objects are read via alternates; index/refs stay untouched.
    objects = git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip()
    with tempfile.TemporaryDirectory(prefix='sync_merge_tree_') as tmp:
        env = dict(os.environ, GIT_OBJECT_DIRECTORY=tmp,
                   GIT_ALTERNATE_OBJECT_DIRECTORIES=objects)
        p = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'rerere.enabled=false',
                            '-C', root, 'merge-tree', '--write-tree', '--name-only', '-z', old, source],
                           env=env, capture_output=True)
        assert p.returncode in (0, 1), p.stderr.decode(errors='replace')
        fields = p.stdout.split(b'\0')
        print('PREDICTED TREE', os.fsdecode(fields[0]))
        names = []
        if p.returncode == 1:
            for field in fields[1:]:
                if not field: break
                names.append(os.fsdecode(field))
        for path in names: print('PREDICTED CONFLICT', repr(path))
        print('PREDICTED CONFLICT COUNT', len(names))
        print('MERGE-TREE DETAILS', repr(p.stdout), p.stderr.decode(errors='replace'))
        # Resolution allowlist is EMPTY. No predicted conflict is justified by a rule.
        assert not names and p.returncode == 0, 'unlisted predicted conflict; no target mutation'

def policy(root, source, digest):
    os.chdir(root); sys.path.insert(0, root)
    from greekocr.labelfix.release_gate import policy_binding
    binding = policy_binding()
    print(json.dumps(binding, sort_keys=True, indent=2))
    assert binding['sha256'] == digest, 'policy digest mismatch'
    paths = sorted(binding['sources'])
    assert not git(root, 'diff', '--no-ext-diff', '--no-renames', source, 'HEAD', '--', *paths), 'hashed-set tree diff'
    assert not git(root, 'diff', '--no-ext-diff', '--no-renames', source, '--', *paths), 'hashed-set working diff'
    print('PASS policy digest and empty hashed-set diff')

if __name__ == '__main__':
    action, *args = sys.argv[1:]
    if action == 'processes': process_guard(*args)
    elif action == 'predict': predict(*args)
    elif action == 'range': restricted_range(*args)
    elif action == 'collisions': collisions(*args[:3], move=args[3]=='move')
    elif action == 'policy': policy(*args)
    elif action == 'suite':
        if suite(*args[:3], retry=len(args)>3): print('RETRY_FLAKY')
    else: raise SystemExit('unknown helper action')
PY_HELPER
}

precondition() {
 local root=$1 branch=$2 old=$3 got status op location
 [[ $(g -C "$root" rev-parse --path-format=absolute --git-common-dir) == $(g -C "$MAIN" rev-parse --path-format=absolute --git-common-dir) ]] || fail "different repository: $root"
 got=$(g -C "$root" symbolic-ref --short HEAD)
 [[ $got == "$branch" ]] || fail "branch expected $branch actual $got"
 got=$(g -C "$root" rev-parse HEAD)
 if [[ $got != "$old" ]]; then
  # A completed prior execution is acceptable; arbitrary target drift is not.
  g -C "$root" merge-base --is-ancestor "$old" "$got"
  already_synced "$root" || fail "tip $branch expected $old or a synced descendant actual $got"
 fi
 got=$(g -C "$root" rev-parse "refs/heads/$SOURCE")
 if already_synced "$root"; then echo "STATE $branch: already synced; post-checks only"; fi
 helper range "$root" "$SOURCE_TIP" "$got" docs/briefs/SYNC3_resume.md docs/briefs/SYNC3b_allow_brief.md
 if [[ $branch == opus/cleanup-1 ]]; then
  helper range "$root" "$CLEANUP_MERGE" HEAD docs/briefs/SYNC2_policy_test.md docs/reviews/harness/SYNC2_NOTES.md tests/labelfix/test_policy_frozen_after_merge.py
 fi
 status=$(g -C "$root" status --porcelain --untracked-files=no)
 [[ -z $status ]] || fail "tracked dirty $branch: $status"
 for op in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer; do
  location=$(g -C "$root" rev-parse --path-format=absolute --git-path "$op")
  [[ ! -e $location ]] || fail "operation in progress: $location"
 done
 echo "UNTRACKED $branch (allowed; ignored collisions are also checked):"
 g -C "$root" ls-files --others --exclude-standard
 helper processes "$root" "$root"
 echo "PASS preconditions $branch tip=$(g -C "$root" rev-parse HEAD) source=$SOURCE_TIP"
}
# Explicit per-path conflict rules: NONE (both predictions have zero conflicts).
# Every actual conflict, including one appearing after prediction, aborts the merge.
merge_target() {
 local root=$1 rc=0 conflicts
 ACTIVE=$root
 g -C "$root" merge --no-ff --no-edit "$SOURCE_TIP" || rc=$?
 if [[ $rc != 0 ]]; then
  conflicts=$(g -C "$root" diff --name-only --diff-filter=U)
  printf 'UNLISTED CONFLICTS (no resolution rules):\n%s\n' "$conflicts" >&2
  if g -C "$root" rev-parse --verify --quiet MERGE_HEAD >/dev/null; then
   g -C "$root" merge --abort
  fi
  ACTIVE=
  fail "merge aborted (rc=$rc); no unlisted conflict may be resolved"
 fi
 ACTIVE=
}
run_suite() {
 local root=$1 label=$2 rc=0 retry_rc=0 parsed
 local out=$PAD/sync_20261017_${STAMP}_${label}_pytest.log
 local xml=$PAD/sync_20261017_${STAMP}_${label}_pytest.xml
 (cd "$root"; run env PYTHONPATH="$root" "$PYTHON" -m pytest -q -ra -p no:cacheprovider --color=no --junitxml="$xml" tests/) 2>&1 | tee "$out" || rc=$?
 parsed=$(helper suite "$out" "$xml" "$rc")
 echo "$parsed"
 if [[ $parsed == *RETRY_FLAKY* ]]; then
  (cd "$root"; run env PYTHONPATH="$root" "$PYTHON" -m pytest -q -ra -p no:cacheprovider --color=no --junitxml="${xml%.xml}_retry.xml" tests/labelfix/test_s8_fetch_job.py::test_deadline_terminates_inflight_pool) 2>&1 | tee "${out%.log}_retry.log" || retry_rc=$?
  helper suite "${out%.log}_retry.log" "${xml%.xml}_retry.xml" "$retry_rc" retry
 fi
}
postchecks() {
 local root=$1 branch=$2 old=$3
 helper policy "$root" "$SOURCE_TIP" "$DIGEST"
 # Old-tip ancestry implies preservation of EVERY commit reachable from the old tip.
 g -C "$root" merge-base --is-ancestor "$old" HEAD
 g -C "$root" merge-base --is-ancestor "$SOURCE_TIP" HEAD
 [[ $(g -C "$root" rev-list --count "$old" --not HEAD) == 0 ]] || fail 'old commits lost'
 if [[ $branch == opus/cleanup-1 ]]; then
  # CU3/CU4's added pytest files all live in these two directories (commit readback).
  (cd "$root"; run env PYTHONPATH="$root" "$PYTHON" -m pytest -q -p no:cacheprovider tests/adjudicate tests/recogniser)
 else
  (cd "$root"; run env PYTHONPATH="$root" "$PYTHON" -m pytest -q -p no:cacheprovider tests/labelfix -k r2)
 fi
 run_suite "$root" "${branch#opus/}"
 [[ -z $(g -C "$root" status --porcelain --untracked-files=no) ]] || fail 'tests changed tracked files'
 helper policy "$root" "$SOURCE_TIP" "$DIGEST"
 echo "NEW TIP $branch $(g -C "$root" rev-parse HEAD)"
}
already_synced() { g -C "$1" merge-base --is-ancestor "$SOURCE_TIP" HEAD; }
prepare_target() {
 local root=$1 old=$2 backup=$3
 if already_synced "$root"; then return 0; fi
 helper predict "$root" "$old" "$SOURCE_TIP"
 helper collisions "$root" "$SOURCE_TIP" "$backup" inspect
}
sync_target() {
 local root=$1 branch=$2 old=$3 backup=$4
 # Revalidate after earlier target tests and before any move or merge.
 precondition "$root" "$branch" "$old"
 if already_synced "$root"; then
  echo "SKIP merge $branch: already synced; post-checks only"
 elif [[ $MODE == --dry-run ]]; then
  command_line helper collisions "$root" "$SOURCE_TIP" "$backup" move
  command_line g -C "$root" merge --no-ff --no-edit "$SOURCE_TIP"
 else
  helper predict "$root" "$old" "$SOURCE_TIP"
  helper collisions "$root" "$SOURCE_TIP" "$backup" move
  merge_target "$root"
 fi
 if [[ $MODE == --dry-run ]]; then
  command_line postchecks "$root" "$branch" "$old"
 else
  postchecks "$root" "$branch" "$old"
 fi
}
main() {
 local i bad=0 root branch old backup
 echo "MODE $MODE; pinned source $SOURCE $SOURCE_TIP; resolution rules 0"
 # Check BOTH targets before any mutation. Dry-run collects all failures.
 for i in "${!BRANCHES[@]}"; do
  root=${ROOTS[$i]}; branch=${BRANCHES[$i]}; old=${TIPS[$i]}
  # Run strict preconditions in a child shell; do not suppress errexit inside them.
  local rc=0
  ( trap - ERR; set -e; precondition "$root" "$branch" "$old" ) &
  wait $! || rc=$?
  if [[ $rc != 0 ]]; then echo "FAIL preconditions $branch"; bad=1; fi
  rc=0
  ( trap - ERR; set -e; prepare_target "$root" "$old" "$PAD/sync_untracked_backup/$branch" ) &
  wait $! || rc=$?
  if [[ $rc != 0 ]]; then echo "FAIL prediction/collisions $branch"; bad=1; fi
 done
 echo "DRY-RUN PREFLIGHT RESULT bad=$bad"
 [[ $bad == 0 ]] || return 1
 for i in "${!BRANCHES[@]}"; do
  root=${ROOTS[$i]}; branch=${BRANCHES[$i]}; old=${TIPS[$i]}
  backup=$PAD/sync_untracked_backup/$branch
  sync_target "$root" "$branch" "$old" "$backup"
 done
 echo "COMPLETE $MODE"
}
STAMP=$(date -u '+%Y%m%dT%H%M%SZ')_$$
LOG=$PAD/sync_20261017_${STAMP}.log
[[ -d $PAD && ! -e $LOG ]] || fail 'scratchpad missing or log exists'
echo "LOG: $LOG (dry-run writes only this log and disposable prediction objects)"
main 2>&1 | "$PYTHON" -u -c 'import datetime,sys
for line in sys.stdin:
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), line, end="", flush=True)' | tee "$LOG"
