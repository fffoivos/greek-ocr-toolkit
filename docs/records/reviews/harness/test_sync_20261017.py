"""Offline SYNC3 tests; all Git mutations are confined to temporary repositories."""
import contextlib
import io
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name('sync_20261017.sh')
SOURCE = SCRIPT.read_text()
PREFIX = SOURCE.split("STAMP=$(date -u", 1)[0]
HELPER = SOURCE.split("<<'PY_HELPER'\n", 1)[1].split('\nPY_HELPER', 1)[0]
NS = {'__name__': 'sync_helper_test'}
exec(compile(HELPER, str(SCRIPT)+':embedded', 'exec'), NS)


class StaticTests(unittest.TestCase):
    def test_bash_syntax(self):
        subprocess.run(['bash', '-n', str(SCRIPT)], check=True)

    def test_no_push(self):
        # No dispatch site may push; the explicit deny rule is the only push token.
        self.assertNotIn('git push', SOURCE)
        self.assertNotRegex(SOURCE, r'\bg\s+(?:-C\s+\S+\s+)?push\b')
        self.assertEqual(SOURCE.count('push'), 1)
        p = subprocess.run(['bash', '-c', PREFIX + '\nrun() { echo UNEXPECTED_DISPATCH; }; g push origin HEAD'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 97)
        self.assertNotIn('UNEXPECTED_DISPATCH', p.stdout)

    def test_known_failures_exactly_match_merge_harness(self):
        original = SCRIPT.with_name('merge_20261017.sh').read_text()
        self.assertEqual(SOURCE.split('KNOWN =', 1)[1].split('def collisions', 1)[0],
                         original.split('KNOWN =', 1)[1].split('def collisions', 1)[0])

    def test_r2cards_not_a_target(self):
        self.assertEqual(SOURCE.split('BRANCHES=(', 1)[1].split(')', 1)[0], 'opus/cleanup-1 opus/r2-prep')

    def test_history_allowlists_are_exact(self):
        ranges = [shlex.split(line) for line in SOURCE.splitlines()
                  if line.strip().startswith('helper range ')]
        self.assertEqual(ranges, [
            ['helper', 'range', '$root', '$SOURCE_TIP', '$got',
             'docs/briefs/SYNC3_resume.md', 'docs/briefs/SYNC3b_allow_brief.md'],
            ['helper', 'range', '$root', '$CLEANUP_MERGE', 'HEAD',
             'docs/briefs/SYNC2_policy_test.md', 'docs/reviews/harness/SYNC2_NOTES.md',
             'tests/labelfix/test_policy_frozen_after_merge.py'],
        ])


class SyntheticRepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='sync_test_')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'repo'
        self.root.mkdir()
        self.git('init', '-b', 'target')
        self.git('config', 'user.name', 'SYNC Test')
        self.git('config', 'user.email', 'sync@example.invalid')
        (self.root/'conflict').write_text('base\n')
        self.commit('base')
        self.git('checkout', '-b', 'incoming')
        (self.root/'conflict').write_text('incoming\n')
        (self.root/'new').write_text('same\n')
        self.commit('incoming')
        self.git('checkout', 'target')
        (self.root/'conflict').write_text('target\n')
        self.commit('target')
        (self.root/'untracked').write_bytes(b'preserve\0bytes')

    def git(self, *args, check=True):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', '-C', str(self.root), *args], check=check, capture_output=True, text=True)

    def commit(self, message):
        self.git('add', '--all'); self.git('commit', '-m', message)

    def snapshot(self):
        return (self.git('show-ref').stdout, self.git('status', '--porcelain').stdout,
                {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts})

    def test_unlisted_actual_conflict_aborts_and_restores_worktree(self):
        before = self.snapshot()
        code = PREFIX + '\nSOURCE_TIP=incoming\nmerge_target ' + shlex.quote(str(self.root))
        p = subprocess.run(['bash', '-c', code], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('UNLISTED CONFLICTS', p.stderr)
        self.assertIn('merge aborted', p.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertNotEqual(self.git('rev-parse', '--verify', 'MERGE_HEAD', check=False).returncode, 0)
        self.assertEqual(self.git('ls-files', '-u').stdout, '')

    def test_prediction_rejects_conflict_without_writing_repo(self):
        before = self.snapshot()
        objects = {str(p.relative_to(self.root/'.git/objects')):p.read_bytes() for p in (self.root/'.git/objects').rglob('*') if p.is_file()}
        with self.assertRaisesRegex(AssertionError, 'unlisted predicted conflict'), contextlib.redirect_stdout(io.StringIO()):
            NS['predict'](str(self.root), 'target', 'incoming')
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(objects, {str(p.relative_to(self.root/'.git/objects')):p.read_bytes() for p in (self.root/'.git/objects').rglob('*') if p.is_file()})

    def test_clean_merge_keeps_old_ancestry(self):
        self.git('checkout', 'incoming')
        self.git('checkout', '-b', 'clean')
        (self.root/'another').write_text('branch addition')
        self.commit('branch addition')
        old = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('checkout', 'incoming')
        (self.root/'source-addition').write_text('source addition')
        self.commit('source addition')
        self.git('checkout', 'clean')
        p = subprocess.run(['bash', '-c', PREFIX + '\nSOURCE_TIP=incoming\nmerge_target '+shlex.quote(str(self.root))], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.git('merge-base', '--is-ancestor', old, 'HEAD')
        self.git('merge-base', '--is-ancestor', 'incoming', 'HEAD')
        self.assertEqual(len(self.git('rev-list', '--parents', '-n1', 'HEAD').stdout.split()), 3)

    def test_already_synced_runs_postchecks_only(self):
        self.git('checkout', 'incoming')
        source_tip = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root/'addition').write_text('already merged target addition')
        self.commit('synced target')
        before = self.snapshot()
        code = PREFIX + f'\nSOURCE_TIP={source_tip}\nMODE=--execute\n' + r"""
precondition() { echo PRECONDITION; }
helper() { echo UNEXPECTED_HELPER; return 99; }
merge_target() { echo UNEXPECTED_MERGE; return 99; }
postchecks() { echo POSTCHECKS; }
""" + '\nprepare_target ' + shlex.quote(str(self.root)) + ' HEAD /unused' + '\nsync_target ' + shlex.quote(str(self.root)) + ' target HEAD /unused'
        result = subprocess.run(['bash', '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('already synced; post-checks only', result.stdout)
        self.assertEqual(result.stdout.count('POSTCHECKS'), 1)
        self.assertNotIn('UNEXPECTED', result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_source_descendant_only_allows_briefs(self):
        (self.root/'untracked').unlink()
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        allowed = ('docs/briefs/SYNC3_resume.md', 'docs/briefs/SYNC3b_allow_brief.md')
        for brief in allowed:
            path = self.root/brief
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('allowed')
            self.commit(brief)
        with contextlib.redirect_stdout(io.StringIO()):
            NS['restricted_range'](str(self.root), base, 'HEAD', *allowed)
        (self.root/'other').write_text('unapproved')
        self.commit('unapproved')
        with self.assertRaisesRegex(AssertionError, 'unapproved paths'), contextlib.redirect_stdout(io.StringIO()):
            NS['restricted_range'](str(self.root), base, 'HEAD', *allowed)

    def test_restricted_range_rejects_reverted_unapproved_edit(self):
        (self.root/'untracked').unlink()
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root/'other').write_text('unapproved')
        self.commit('unapproved')
        (self.root/'other').unlink()
        self.commit('reverted')
        with self.assertRaisesRegex(AssertionError, 'unapproved paths'), contextlib.redirect_stdout(io.StringIO()):
            NS['restricted_range'](str(self.root), base, 'HEAD', 'brief')

    def collisions(self, move):
        backup = Path(self.tmp.name)/'backup'
        with contextlib.redirect_stdout(io.StringIO()):
            NS['collisions'](str(self.root), 'incoming', str(backup), move)
        return backup

    def test_identical_collision_is_backed_up(self):
        (self.root/'new').write_text('same\n')
        backup = self.collisions(True)
        self.assertEqual((backup/'new').read_text(), 'same\n')
        self.assertFalse((self.root/'new').exists())

    def test_dry_collision_inspection_preserves_bytes(self):
        (self.root/'new').write_text('same\n')
        before = self.snapshot()
        self.assertFalse(self.collisions(False).exists())
        self.assertEqual(before, self.snapshot())

    def test_nonidentical_collision_aborts_before_moves(self):
        (self.root/'new').write_text('different\n')
        before = self.snapshot()
        with self.assertRaisesRegex(AssertionError, 'non-identical collision'):
            self.collisions(True)
        self.assertEqual(before, self.snapshot())


class ProcessTests(unittest.TestCase):
    def test_codex_at_target_rejected(self):
        result = subprocess.CompletedProcess([], 0, 'p123\nccodex\nfcwd\nn/tmp/target\n', '')
        with mock.patch.object(NS['subprocess'], 'run', return_value=result), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'writer candidates'):
                NS['process_guard']('/tmp/target', '/tmp/target')

    def test_unverifiable_inventory_rejected(self):
        result = subprocess.CompletedProcess([], 1, '', 'permission denied')
        with mock.patch.object(NS['subprocess'], 'run', return_value=result), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'cannot inspect'):
                NS['process_guard']('/tmp/target', '/tmp/target')


if __name__ == '__main__':
    unittest.main(verbosity=2)
