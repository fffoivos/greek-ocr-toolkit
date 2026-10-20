"""Offline script tests. Git writes are confined to synthetic temporary repositories."""
import ast
import contextlib
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'merge_20261017.sh'
SOURCE = SCRIPT.read_text()
HELPER = SOURCE.split("<<'PY_HELPER'\n", 1)[1].split('\nPY_HELPER', 1)[0]
HANDOFF = SOURCE.split('HANDOFF=(\n', 1)[1].split('\n)', 1)[0].split()
NS = {'__name__': 'merge_helper_test'}
exec(compile(HELPER, str(SCRIPT) + ':embedded', 'exec'), NS)


class StaticTests(unittest.TestCase):
    def test_bash_syntax(self):
        subprocess.run(['bash', '-n', str(SCRIPT)], check=True)

    @unittest.skipUnless(shutil.which('shellcheck'), 'shellcheck unavailable')
    def test_shellcheck(self):
        subprocess.run(['shellcheck', str(SCRIPT)], check=True)

    def test_no_push(self):
        self.assertNotIn('git push', SOURCE)
        self.assertNotRegex(SOURCE, r'\bpush\b')

    def test_allowlist_nonempty_sorted_exact(self):
        rows = SOURCE.split("<<'ALLOWLIST_END'\n", 1)[1].split('\nALLOWLIST_END', 1)[0].splitlines()
        self.assertTrue(rows)
        self.assertEqual(rows, sorted(set(rows)))
        self.assertEqual(len(rows), 18)
        self.assertTrue(all(re.fullmatch(r'[AMD]\tdocs/[^\s]+', r) for r in rows))
        self.assertIn('D\tdocs/archive/l1r_line_20261017/README.md', rows)

    def test_exact_nine_handoff_paths_also_in_reference_allowlist(self):
        expected = {
            'docs/reviews/harness/' + name for name in (
                'MERGE_SCRIPT_NOTES.md', 'README.md', 'merge_20261017.sh',
                'run_wt_medium_git.sh', 'run_wt_medium_gitfull.sh', 'test_merge_20261017.py')
        } | {'docs/briefs/MS2_merge_script_fix.md', 'docs/briefs/MS3_handoff_paths.md', 'docs/briefs/MS4_tree_check.md'}
        self.assertEqual(len(HANDOFF), 9)
        self.assertEqual(set(HANDOFF), expected)
        rows = SOURCE.split("<<'ALLOWLIST_END'\n", 1)[1].split('\nALLOWLIST_END', 1)[0].splitlines()
        self.assertTrue({'A\t' + p for p in expected}.issubset(rows))

    def test_helper_compiles(self):
        ast.parse(HELPER)

    def test_required_modes_and_pins(self):
        self.assertIn('set -euo pipefail', SOURCE)
        self.assertIn("trap '", SOURCE)
        self.assertIn('MODE=${1:---dry-run}', SOURCE)
        for ref in ('opus/spellcheck', 'opus/spellcheck-r0', 'opus/spellcheck-s8', 'opus/spellcheck-l1f', 'opus/spellcheck-l1', 'rehearsal/merge-20261017'):
            self.assertRegex(SOURCE, re.escape("'" + ref) + r' [0-9a-f]{40}\'')

    def test_no_external_network_commands(self):
        self.assertNotRegex(SOURCE, r'\b(fetch|pull|curl|wget|ssh)\b')

    def test_inherited_pytest_selection_disabled(self):
        self.assertIn('export PYTEST_ADDOPTS=\n', SOURCE)

    def test_pinned_objects_ignore_replace_refs(self):
        self.assertIn('GIT_NO_REPLACE_OBJECTS=1', SOURCE)

    def test_option_c_paths_exactly_reference_commit(self):
        result = subprocess.check_output([
            'git', '--no-replace-objects', '-C', str(HERE.parents[2]),
            'diff-tree', '--no-commit-id', '--name-only', '-r',
            'a241ed75e64e6ae3af2891aafe43eed3539174d4'], text=True)
        expected = {p for p in result.splitlines() if not p.startswith('docs/archive/l1r_line_20261017/')}
        actual = set(SOURCE.split('OPTION_C=(\n', 1)[1].split('\n)', 1)[0].split())
        self.assertEqual(actual, expected)

    def test_option_c_no_option_a_checkout(self):
        self.assertIn('l1r_recompose_ext.py', SOURCE)
        self.assertNotRegex(SOURCE, r'checkout[^\n]*docs/archive/l1r_line_20261017')

    def test_hashed_conflicts_explicit(self):
        for name in ('l1_common.py', 'l1_detect.py', 'l1_infer.py', 'l1r_recompose.py'):
            self.assertIn('checkout "$BASE" -- scripts/labelfix/clariden/' + name, SOURCE)
        self.assertNotIn('git add -A', SOURCE)

    def test_invalid_argument_rejected(self):
        p = subprocess.run(['bash', str(SCRIPT), '--invalid'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('usage:', p.stderr)

    def test_execute_is_gated(self):
        self.assertIn('if [[ $MODE == --execute && $rc != 0 ]]; then return "$rc"; fi', SOURCE)
        self.assertLess(SOURCE.index('check_tree\n checks'), SOURCE.index('g -C "$MAIN" merge --ff-only "$FINAL"\n checks'))


class ModeBoundaryTests(unittest.TestCase):
    def shell(self, stub):
        prefix = SOURCE.split("STAMP=$(date -u", 1)[0]
        return subprocess.run(['bash', '-c', prefix + stub], capture_output=True, text=True)

    def test_dry_run_never_invokes_mutation(self):
        result = self.shell("""
MODE=--dry-run
forbidden() { echo MUTATION_EXECUTED; return 97; }
mutate forbidden checkout example
""")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('MUTATION_EXECUTED', result.stdout)
        self.assertIn('CMD forbidden checkout example', result.stderr)

    def test_execute_failed_preconditions_never_calls_sequence(self):
        result = self.shell("""
MODE=--execute
preconditions() { echo EXPECTED_PRECONDITION_FAILURE; return 1; }
sequence() { echo MUTATION_EXECUTED; }
main
""")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('MUTATION_EXECUTED', result.stdout)

    def test_dry_run_reports_failure_and_prints_plan(self):
        result = self.shell("""
MODE=--dry-run
preconditions() { return 1; }
sequence() { echo PLAN_PRINTED; }
main
""")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PLAN_PRINTED', result.stdout)
        self.assertIn('precondition exit=1; no files written', result.stdout)

    def test_inherited_optimization_cannot_disable_guards(self):
        prefix = SOURCE.split("STAMP=$(date -u", 1)[0]
        env = dict(os.environ, PYTHONOPTIMIZE='2')
        # Check the child interpreter itself: its assert must still execute.
        result = subprocess.run(['bash', '-c', prefix + "\n\"$PYTHON\" -c \"assert False, 'ASSERTIONS_ENABLED'\""], env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('AssertionError: ASSERTIONS_ENABLED', result.stderr)

    def test_execute_success_invokes_mutation(self):
        result = self.shell("""
MODE=--execute
marker() { echo EXPECTED_MUTATION_BOUNDARY; }
mutate marker
""")
        self.assertEqual(result.returncode, 0)
        self.assertIn('EXPECTED_MUTATION_BOUNDARY', result.stdout)


class SuiteTests(unittest.TestCase):
    def fixture(self, folder, rows=(), modules=True, extra_case='', rc=None):
        from xml.sax.saxutils import escape
        log, xml = Path(folder)/'pytest.log', Path(folder)/'pytest.xml'
        log.write_text('\n'.join(f'{status} {node} - message' for status,node in rows) + '\n')
        cases = []
        if modules:
            cases += [f'<testcase classname="tests.labelfix.{m}" name="test_ok" />' for m in ('test_l1r','test_l1r2','test_l1r3','test_l1f','test_policy_frozen_after_merge')]
        for status,node in rows:
            cases.append(f'<testcase classname="fixture" name="{escape(node)}"><{"failure" if status == "FAILED" else "error"}/></testcase>')
        xml.write_text('<testsuites><testsuite>' + ''.join(cases) + extra_case + '</testsuite></testsuites>')
        return str(log), str(xml), str(int(bool(rows)) if rc is None else rc)

    def check(self, rows=(), **kwargs):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            return NS['suite'](*self.fixture(td, rows, **kwargs))

    def test_accept_clean(self):
        self.assertFalse(self.check())

    def test_accept_exact_known_set(self):
        rows = [(s,n) for s,nodes in NS['KNOWN'].items() for n in nodes]
        self.assertEqual(len(rows), 10)
        self.assertFalse(self.check(rows))

    def test_reject_new_failure_in_known_module(self):
        with self.assertRaisesRegex(AssertionError, 'new FAILED'):
            self.check([('FAILED', 'tests/test_collection_outputs.py::test_new_bug')])

    def test_reject_new_error(self):
        with self.assertRaisesRegex(AssertionError, 'new ERROR'):
            self.check([('ERROR', 'tests/labelfix/test_capture.py::test_socket')])

    def test_error_vs_failure_is_not_interchangeable(self):
        node = next(iter(NS['KNOWN']['FAILED']))
        with self.assertRaisesRegex(AssertionError, 'new ERROR'):
            self.check([('ERROR', node)])

    def test_duplicate_failure_rejected(self):
        node = next(iter(NS['KNOWN']['FAILED']))
        with self.assertRaisesRegex(AssertionError, 'duplicate'):
            self.check([('FAILED',node)] * 2)

    def test_abnormal_exit_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'abnormal exit'):
            self.check(rc=2)

    def test_missing_critical_modules_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'absent, skipped or failed'):
            self.check(modules=False, extra_case='<testcase classname="other" name="test_ok"/>')

    def test_skipped_policy_test_rejected(self):
        extra = '<testcase classname="tests.labelfix.test_policy_frozen_after_merge" name="test_skip"><skipped/></testcase>'
        with self.assertRaisesRegex(AssertionError, 'absent, skipped or failed'):
            self.check(extra_case=extra)

    def test_xml_output_mismatch_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'XML/output'):
            self.check(extra_case='<testcase name="hidden"><failure/></testcase>')

    def test_flaky_requests_retry(self):
        self.assertTrue(self.check([('FAILED', NS['FLAKY'])]))

    def test_retry_must_pass_single_test(self):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            args = self.fixture(td, modules=False, extra_case='<testcase name="flaky"/>')
            self.assertFalse(NS['suite'](*args, retry=True))

    def test_retry_failure_rejected(self):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            args = self.fixture(td, [('FAILED',NS['FLAKY'])])
            with self.assertRaisesRegex(AssertionError, 'retry did not pass'):
                NS['suite'](*args, retry=True)


class CollisionTests(unittest.TestCase):
    def check(self, td, contents, incoming, move):
        main, backup = Path(td)/'main', Path(td)/'backup'
        main.mkdir(exist_ok=True)
        for name,data in contents.items():
            (main/name).parent.mkdir(parents=True, exist_ok=True); (main/name).write_bytes(data)
        blobs = {str(i): data for i,(name,data) in enumerate(incoming.items())}
        entries = b'\0'.join(b'100644 blob '+str(i).encode()+b'\t'+name.encode() for i,name in enumerate(incoming)) + b'\0'
        def fake_git(root, *args):
            if args[0] == 'ls-files': return b''
            if args[0] == 'ls-tree': return entries
            if args[0] == 'cat-file': return blobs[args[-1]]
            raise AssertionError(args)
        with mock.patch.dict(NS, git=fake_git), contextlib.redirect_stdout(io.StringIO()):
            NS['collisions'](str(main), 'incoming', str(backup), move)
        return main, backup

    def test_inspect_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            main,backup = self.check(td, {'a': b'same'}, {'a': b'same'}, False)
            self.assertEqual((main/'a').read_bytes(), b'same'); self.assertFalse(backup.exists())

    def test_identical_preserved_in_backup(self):
        with tempfile.TemporaryDirectory() as td:
            main,backup = self.check(td, {'dir/a': b'same'}, {'dir/a': b'same'}, True)
            self.assertFalse((main/'dir/a').exists()); self.assertEqual((backup/'dir/a').read_bytes(), b'same')

    def test_mismatch_prevents_all_moves(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(AssertionError, 'non-identical'):
                self.check(td, {'a':b'same', 'b':b'other'}, {'a':b'same', 'b':b'incoming'}, True)
            self.assertTrue((Path(td)/'main/a').exists()); self.assertFalse((Path(td)/'backup').exists())

    def test_existing_backup_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'backup').mkdir(); (Path(td)/'backup/a').write_bytes(b'keep')
            with self.assertRaisesRegex(AssertionError, 'backup already exists'):
                self.check(td, {'a':b'same'}, {'a':b'same'}, True)
            self.assertEqual((Path(td)/'backup/a').read_bytes(), b'keep')

    def test_ancestor_obstruction_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(AssertionError, 'ancestor obstruction'):
                self.check(td, {'dir':b'file'}, {'dir/a':b'incoming'}, True)


class MergeConflictTests(unittest.TestCase):
    def run_stage(self, conflict, allowed):
        # Source only definitions, replace the git boundary; no real repository access.
        prefix = SOURCE.split("STAMP=$(date -u", 1)[0]
        stub = r"""
MODE=--execute
TIPS=('test-branch 1111111111111111111111111111111111111111')
mutate() { return 1; }
g() {
 case " $* " in
  *' diff '*) printf '%s\n' "$TEST_CONFLICT" ;;
  *' rev-parse '*) printf '%s\n' test-merge-head ;;
  *) return 90 ;;
 esac
}
merge_stage test-branch "$TEST_ALLOWED"
"""
        env = dict(os.environ, TEST_CONFLICT=conflict, TEST_ALLOWED=allowed)
        return subprocess.run(['bash', '-c', prefix + stub], env=env, capture_output=True, text=True)

    def test_expected_conflict_accepted(self):
        self.assertEqual(self.run_stage('scripts/expected.py', 'scripts/expected.py').returncode, 0)

    def test_unexpected_conflict_aborts(self):
        p = self.run_stage('scripts/unexpected.py', 'scripts/expected.py')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('unexpected conflict', p.stderr)

    def test_failed_merge_without_conflict_aborts(self):
        p = self.run_stage('', 'scripts/expected.py')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('failed without expected conflicts', p.stderr)


class SyntheticRepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'main'
        self.root.mkdir()
        self.git('init', '-b', 'opus/spellcheck')
        self.git('config', 'user.name', 'Synthetic Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        (self.root/'base').write_text('base')
        self.commit('base')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.scratch = Path(self.tmp.name)/'scratch'

    def git(self, *args, root=None, check=True):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root or self.root), *args],
                              check=check, capture_output=True, text=True)

    def commit(self, message, root=None):
        self.git('add', '--all', root=root)
        self.git('commit', '-m', message, root=root)

    def shell(self, body, mode='--execute'):
        import shlex
        prefix = SOURCE.split("STAMP=$(date -u", 1)[0]
        config = '\n'.join(f'{k}={shlex.quote(str(v))}' for k,v in {
            'MAIN': self.root, 'SCRATCH': self.scratch, 'REFERENCE': self.base,
            'PYTHON': os.sys.executable, 'MODE': mode}.items())
        return subprocess.run(['bash', '-c', prefix + '\n' + config + '\n' + body], capture_output=True, text=True)

    def start_merge(self):
        self.git('branch', 'rehearsal/merge-20261017')
        self.git('checkout', '-b', 'incoming')
        (self.root/'L1_DEPLOY_FILES.txt').write_text('staged addition')
        self.commit('incoming addition')
        self.git('checkout', 'opus/spellcheck')
        self.git('worktree', 'add', '-b', 'rehearsal/merge-final', str(self.scratch), self.base)
        (self.scratch/'prefix').write_text('prior completed merge stage')
        self.commit('completed stage', root=self.scratch)
        self.git('merge', '--no-ff', '--no-commit', 'incoming', root=self.scratch)
        self.assertIn('A  L1_DEPLOY_FILES.txt', self.git('status', '--porcelain', root=self.scratch).stdout)

    def guard(self, phase='before', scratch=None):
        with contextlib.redirect_stdout(io.StringIO()):
            NS['reset_guard'](str(self.root), str(scratch or self.scratch), self.base, 'rehearsal/merge-final', phase)

    def archive_worktree(self):
        self.git('worktree', 'add', '-b', 'rehearsal/merge-final', str(self.scratch), self.base)
        archive = self.scratch/'docs/archive/l1r_line_20261017'
        for name in ('config', 'tests/labelfix', 'scripts/labelfix/clariden'):
            (archive/name).mkdir(parents=True)
        return archive

    def test_tree_check_accepts_empty_leftover_directories(self):
        archive = self.archive_worktree()
        result = self.shell('ALLOWLIST=\'\'\ncheck_tree\ncheck_no_option_a "$SCRATCH" HEAD')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((archive/'config').is_dir())

    def test_tree_check_rejects_tracked_archive_even_if_missing_on_disk(self):
        archive = self.archive_worktree()
        witness = archive/'config/tracked'
        witness.write_text('must abort')
        self.commit('tracked Option-A', root=self.scratch)
        witness.unlink()
        # Match the reference delta so the archive gate itself must reject it.
        result = self.shell('ALLOWLIST=$(g -C "$SCRATCH" diff --no-ext-diff --no-renames --name-status "$REFERENCE" "$FINAL" | sort)\ncheck_tree')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Option-A archive exists in tree', result.stderr)
        result = self.shell('check_no_option_a "$SCRATCH" HEAD')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Option-A archive exists in tree', result.stderr)

    def test_tree_check_rejects_unreadable_ref(self):
        self.archive_worktree()
        result = self.shell('check_no_option_a "$SCRATCH" missing-ref')
        self.assertNotEqual(result.returncode, 0)

    def test_reset_removes_and_logs_empty_dirs_preserves_nonempty_and_outside(self):
        self.start_merge()
        empty = self.scratch/'leftover/nested'
        empty.mkdir(parents=True)
        outside = Path(self.tmp.name)/'outside/empty'
        outside.mkdir(parents=True)
        result = self.shell('helper_original=$(declare -f helper)\neval "${helper_original/helper ()/real_helper ()}"\nhelper() { if [[ $1 == processes ]]; then return; fi; real_helper "$@"; }\nreset_scratch')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.scratch/'leftover').exists())
        self.assertIn(str(empty), result.stdout.splitlines())
        self.assertIn(str(empty.parent), result.stdout.splitlines())
        self.assertTrue(outside.is_dir())
        self.assertTrue(self.scratch.is_dir())
        self.assertEqual((self.scratch/'base').read_text(), 'base')
        self.assertTrue((self.scratch/'.git').is_file())

    def test_staged_addition_rm_regression_and_source_checkout(self):
        self.start_merge()
        self.assertNotEqual(self.git('rm', '--', 'L1_DEPLOY_FILES.txt', root=self.scratch, check=False).returncode, 0)
        # Exercise the actual deletion loop, narrowed to the synthetic witness.
        loop = SOURCE.split(' for p in "${L1_OLD[@]}";', 1)[1].split('\n restore_reference', 1)[0]
        result = self.shell('L1_OLD=(L1_DEPLOY_FILES.txt)\nfor p in "${L1_OLD[@]}";' + loop)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.scratch/'L1_DEPLOY_FILES.txt').exists())
        self.assertEqual(self.git('ls-files', '--', 'L1_DEPLOY_FILES.txt', root=self.scratch).stdout, '')
        # Explicit source-tree checkouts overwrite staged modifications safely.
        (self.scratch/'base').write_text('changed')
        self.git('add', 'base', root=self.scratch)
        result = self.shell('BASE=$REFERENCE; HASHED=(base); freeze_policy')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.scratch/'base').read_text(), 'base')

    def test_reset_aborts_checks_out_and_deletes_only_final(self):
        self.start_merge()
        main_before = self.git('rev-parse', 'HEAD').stdout
        result = self.shell('helper_original=$(declare -f helper)\neval "${helper_original/helper ()/real_helper ()}"\nhelper() { if [[ $1 == processes ]]; then return; fi; real_helper "$@"; }\nreset_scratch')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git('symbolic-ref', '--short', 'HEAD', root=self.scratch).stdout.strip(), 'rehearsal/merge-20261017')
        self.assertEqual(self.git('status', '--porcelain', root=self.scratch).stdout, '')
        self.assertNotEqual(self.git('show-ref', '--verify', 'refs/heads/rehearsal/merge-final', check=False).returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, main_before)
        self.assertEqual(self.git('rev-parse', 'incoming').returncode, 0)

    def test_reset_dry_run_preserves_merge_index_and_refs(self):
        self.start_merge()
        empty = self.scratch/'leftover/nested'
        empty.mkdir(parents=True)
        index = Path(self.git('rev-parse', '--git-path', 'index', root=self.scratch).stdout.strip())
        before = (index.read_bytes(), index.stat().st_mtime_ns, self.git('show-ref').stdout)
        result = self.shell('helper_original=$(declare -f helper)\neval "${helper_original/helper ()/real_helper ()}"\nhelper() { if [[ $1 == processes ]]; then return; fi; real_helper "$@"; }\nreset_scratch', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, (index.read_bytes(), index.stat().st_mtime_ns, self.git('show-ref').stdout))
        self.assertTrue(empty.is_dir())
        self.assertIn('-type d -empty -delete -print', result.stderr)
        self.assertEqual(self.git('rev-parse', '--verify', 'MERGE_HEAD', root=self.scratch).returncode, 0)

    def test_reset_refuses_main(self):
        with self.assertRaisesRegex(AssertionError, 'refuse main'):
            self.guard(scratch=self.root)

    def test_reset_refuses_other_branch(self):
        self.start_merge()
        self.git('merge', '--abort', root=self.scratch)
        self.git('checkout', '-b', 'other', root=self.scratch)
        with self.assertRaisesRegex(AssertionError, 'other scratch branch'):
            self.guard()

    def test_reset_refuses_final_checked_out_elsewhere(self):
        self.start_merge()
        self.git('merge', '--abort', root=self.scratch)
        self.git('checkout', 'rehearsal/merge-20261017', root=self.scratch)
        self.git('worktree', 'add', str(Path(self.tmp.name)/'elsewhere'), 'rehearsal/merge-final')
        with self.assertRaisesRegex(AssertionError, 'checked out elsewhere'):
            self.guard()

    def test_reset_refuses_ancestor_of_main_before_abort(self):
        self.start_merge()
        self.git('merge', '--ff-only', 'rehearsal/merge-final')
        with self.assertRaisesRegex(AssertionError, 'ancestor of main'):
            self.guard()
        self.assertEqual(self.git('rev-parse', '--verify', 'MERGE_HEAD', root=self.scratch).returncode, 0)

    def test_reset_refuses_unstaged_edits(self):
        self.start_merge()
        (self.scratch/'base').write_text('unrelated local edit')
        with self.assertRaisesRegex(AssertionError, 'unstaged/untracked'):
            self.guard()

    def test_reset_refuses_moved_reference(self):
        self.start_merge()
        self.git('branch', '-f', 'rehearsal/merge-20261017', 'incoming')
        with self.assertRaisesRegex(AssertionError, 'reference branch moved'):
            self.guard()

    def test_reset_after_phase_requires_final_unchecked(self):
        self.start_merge()
        self.git('merge', '--abort', root=self.scratch)
        with self.assertRaisesRegex(AssertionError, 'other scratch branch'):
            self.guard(phase='after')

    def test_reset_refuses_untracked_files(self):
        self.start_merge()
        (self.scratch/'untracked').write_text('preserve')
        with self.assertRaisesRegex(AssertionError, 'unstaged/untracked'):
            self.guard()

    def test_reset_process_failure_prevents_abort(self):
        self.start_merge()
        result = self.shell('helper_original=$(declare -f helper)\neval "${helper_original/helper ()/real_helper ()}"\nhelper() { if [[ $1 == processes ]]; then return 93; fi; real_helper "$@"; }\nreset_scratch')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git('rev-parse', '--verify', 'MERGE_HEAD', root=self.scratch).returncode, 0)
        self.assertNotIn('CMD git', result.stderr)

    def handoff(self, paths=None):
        tip = self.git('rev-parse', 'HEAD').stdout.strip()
        with contextlib.redirect_stdout(io.StringIO()):
            NS['handoff'](str(self.root), self.base, tip, ['docs/a'] if paths is None else paths)

    def add_handoff(self):
        (self.root/'docs').mkdir()
        (self.root/'docs/a').write_text('approved')
        self.commit('handoff')

    def test_handoff_single_commit(self):
        self.add_handoff(); self.handoff()

    def test_handoff_harness_only_child(self):
        self.add_handoff()
        (self.root/'docs/a').write_text('fixed')
        self.commit('fix handoff'); self.handoff()

    def test_handoff_rejects_foreign_change_even_if_reverted(self):
        self.add_handoff()
        (self.root/'base').write_text('foreign')
        self.commit('foreign edit')
        (self.root/'base').write_text('base')
        self.commit('revert foreign edit')
        with self.assertRaisesRegex(AssertionError, 'non-allowed handoff'):
            self.handoff()

    def test_handoff_rejects_uncommitted_bytes(self):
        self.add_handoff()
        (self.root/'docs/a').write_text('uncommitted')
        with self.assertRaisesRegex(AssertionError, 'bytes differ'):
            self.handoff()

    def add_nine_path_handoff(self):
        # Mirror live history: harness commit, lead's MS2 brief, then MS3 edits/brief.
        for name in HANDOFF:
            if name.startswith('docs/reviews/harness/'):
                path = self.root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('harness')
        self.commit('six harness files')
        brief = self.root/'docs/briefs/MS2_merge_script_fix.md'
        brief.parent.mkdir(parents=True)
        brief.write_text('MS2 brief')
        self.commit('lead MS2 brief')
        (self.root/'docs/briefs/MS3_handoff_paths.md').write_text('MS3 brief')
        (self.root/'docs/reviews/harness/merge_20261017.sh').write_text('MS3 fix')
        self.commit('MS3 handoff')
        (self.root/'docs/briefs/MS4_tree_check.md').write_text('MS4 brief')
        self.commit('MS4 handoff')

    def test_handoff_accepts_brief_commits_and_harness_modification(self):
        self.add_nine_path_handoff()
        self.handoff(HANDOFF)

    def test_handoff_rejects_non_allowed_path_in_later_commit(self):
        self.add_nine_path_handoff()
        (self.root/'docs/briefs/foreign.md').write_text('not allowed')
        self.commit('later foreign path')
        with self.assertRaisesRegex(AssertionError, 'non-allowed handoff'):
            self.handoff(HANDOFF)

    def test_handoff_rejects_missing_brief_addition(self):
        self.add_nine_path_handoff()
        tip = self.git('rev-parse', 'HEAD~1').stdout.strip()
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'exactly the allowed additions'):
                NS['handoff'](str(self.root), self.base, tip, HANDOFF)

    def test_handoff_rejects_brief_deletion(self):
        self.add_nine_path_handoff()
        (self.root/'docs/briefs/MS2_merge_script_fix.md').unlink()
        self.commit('delete allowed brief')
        with self.assertRaisesRegex(AssertionError, 'non-allowed handoff'):
            self.handoff(HANDOFF)

    def test_handoff_byte_checks_all_six_harness_files(self):
        self.add_nine_path_handoff()
        for name in HANDOFF:
            if name.startswith('docs/reviews/harness/'):
                with self.subTest(path=name):
                    path = self.root/name
                    original = path.read_bytes()
                    path.write_bytes(b'uncommitted')
                    with self.assertRaisesRegex(AssertionError, 'bytes differ'):
                        self.handoff(HANDOFF)
                    path.write_bytes(original)

    def test_handoff_rejects_unrelated_history(self):
        self.git('checkout', '--orphan', 'unrelated')
        self.commit('unrelated root')
        with self.assertRaisesRegex(AssertionError, 'linear descendant'):
            self.handoff()


class ProcessGuardTests(unittest.TestCase):
    def test_reject_worktree_codex(self):
        p = subprocess.CompletedProcess([], 0, 'p123\nccodex\nfcwd\nn/tmp/main\n', '')
        with mock.patch.object(NS['subprocess'], 'run', return_value=p), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'writer candidates'):
                NS['process_guard']('/tmp/main', '/tmp/scratch')

    def test_other_worktree_allowed(self):
        p = subprocess.CompletedProcess([], 0, 'p123\nccodex\nfcwd\nn/tmp/main-r2\n', '')
        with mock.patch.object(NS['subprocess'], 'run', return_value=p), contextlib.redirect_stdout(io.StringIO()):
            NS['process_guard']('/tmp/main', '/tmp/scratch')

    def test_failed_inventory_rejected(self):
        p = subprocess.CompletedProcess([], 1, '', 'permission denied')
        with mock.patch.object(NS['subprocess'], 'run', return_value=p), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'cannot inspect'):
                NS['process_guard']('/tmp/main', '/tmp/scratch')


if __name__ == '__main__':
    unittest.main(verbosity=2)
