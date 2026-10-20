"""Offline synthetic-repository tests; never invoke the live shell entry point."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT=Path(__file__).with_name('wt_remove_20261017.sh')
NS={'__name__':'wt1_test'}
exec(compile(SCRIPT.read_text().split("<<'PY_HELPER'\n",1)[1].split('\nPY_HELPER',1)[0],str(SCRIPT),'exec'),NS)

class RemovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='wt1-test-')
        self.addCleanup(self.tmp.cleanup)
        self.main=Path(self.tmp.name).resolve()/'greek-ocr-toolkit-spellcheck'
        self.main.mkdir()
        self.g('init','-b','opus/spellcheck')
        self.g('config','user.email','test@example.invalid'); self.g('config','user.name','WT1 test')
        (self.main/'base').write_text('base')
        (self.main/'.gitignore').write_text('ignored/\n__pycache__/\n')
        self.g('add','.');self.g('commit','-m','base')
        self.root=Path(str(self.main)+'-align')
        self.g('worktree','add','-b','opus/spellcheck-align',str(self.root))
        self.tip=self.g('rev-parse','HEAD').strip()
        self.row=dict(name=self.root.name,path=str(self.root),tip=self.tip,branch='opus/spellcheck-align',proposal=['REMOVE-CLEAN'],untracked=[],ignored=[],citations=[],cache_exclusions=[])
        self.decision=dict(name=self.root.name,action='REMOVE',tip=self.tip,branch=self.row['branch'],custody=False,repoint=False)
        self.census=dict(main_tip=self.tip,candidates=[self.row],citation_roots=[str(self.main)])
        self.ruling=dict(main_tip=self.tip,worktrees=[self.decision])
        self.proc=mock.patch.dict(NS,processes=lambda r:None);self.proc.start();self.addCleanup(self.proc.stop)
    def g(self,*a,root=None):
        return subprocess.check_output(['git','-C',str(root or self.main),*a],stderr=subprocess.DEVNULL,text=True)
    def snapshot(self):
        items=NS['inventory'](self.root)
        self.row['untracked']=[x for x in items if not x['path'].startswith(('ignored/','__pycache__/'))]
        self.row['ignored']=[x for x in items if x not in self.row['untracked']]
        self.row['cache_exclusions']=[x['path'] for x in items if x['cache']]
    def prepare(self):
        p=self.main/'artifacts/wt1/census.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(self.census))
        self.ruling['census_sha256']=NS['sha'](p)
        p=self.main/'docs/reviews/harness/WT1_RULING.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(self.ruling))
    def run_script(self,execute=False):
        self.prepare()
        with contextlib.redirect_stdout(io.StringIO()): NS['run'](self.main,'--execute' if execute else '--dry-run')
    def guard(self):return NS['guard'](self.main,self.row,self.decision)
    def test_clean_dry_run_preserves_worktree_and_branch(self):
        self.run_script();self.assertTrue(self.root.exists());self.g('show-ref','--verify','refs/heads/opus/spellcheck-align')
    def test_clean_execute_removes_only_synthetic_worktree_keeps_branch(self):
        self.run_script(True);self.assertFalse(self.root.exists());self.g('show-ref','--verify','refs/heads/opus/spellcheck-align')
    def test_empty_placeholder_is_noop(self):
        self.ruling['worktrees']=[];self.run_script();self.assertTrue(self.root.exists())
    def test_keep_ruling_preserves(self):
        self.decision['action']='KEEP';self.run_script(True);self.assertTrue(self.root.exists())
    def test_unknown_candidate_rejected(self):
        self.decision['name']='greek-ocr-toolkit-spellcheck-r1'
        with self.assertRaisesRegex(RuntimeError,'unknown'):self.run_script()
    def test_protected_name_rejected_even_in_census(self):
        self.row['name']=self.main.name+'-r1'
        with self.assertRaisesRegex(RuntimeError,'allowlist'):self.guard()
    def test_tip_drift_rejected(self):
        self.row['tip']='0'*40
        with self.assertRaisesRegex(RuntimeError,'tip drift'):self.guard()
    def test_branch_drift_rejected(self):
        self.decision['branch']='other'
        with self.assertRaisesRegex(RuntimeError,'branch drift'):self.guard()
    def test_unmerged_rejected(self):
        (self.root/'new').write_text('new');self.g('add','new',root=self.root);self.g('commit','-m','unmerged',root=self.root)
        self.row['tip']=self.decision['tip']=self.g('rev-parse','HEAD',root=self.root).strip()
        with self.assertRaisesRegex(RuntimeError,'not merged'):self.guard()
    def test_tracked_modification_rejected(self):
        (self.root/'base').write_text('changed')
        with self.assertRaisesRegex(RuntimeError,'tracked modifications'):self.guard()
    def test_untracked_drift_rejected(self):
        (self.root/'new').write_text('new')
        with self.assertRaisesRegex(RuntimeError,'inventory drift'):self.guard()
    def test_main_tip_drift_rejected(self):
        self.ruling['main_tip']='0'*40
        with self.assertRaisesRegex(RuntimeError,'main tip drift'):self.run_script()
    def test_census_hash_mismatch_rejected(self):
        self.prepare();(self.main/'artifacts/wt1/census.json').write_text('{}')
        with self.assertRaisesRegex(RuntimeError,'census hash'):NS['run'](self.main,'--execute')
    def test_duplicate_ruling_rejected(self):
        self.ruling['worktrees']=[self.decision,self.decision]
        with self.assertRaisesRegex(RuntimeError,'duplicate'):self.run_script()
    def test_custody_required(self):
        (self.root/'new').write_text('preserve');self.snapshot()
        with self.assertRaisesRegex(RuntimeError,'custody ruling'):self.run_script()
    def test_custody_copies_ignored_and_symlinks_excludes_only_caches(self):
        (self.root/'new').write_text('preserve');(self.root/'link').symlink_to('/outside/does-not-exist')
        for name in ('ignored/evidence','__pycache__/cache'):
            p=self.root/name;p.parent.mkdir();p.write_text(name)
        self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()):NS['custody'](self.main,self.root,self.row,True)
        dest=self.main/'artifacts/worktree_custody'/self.root.name
        self.assertEqual((dest/'new').read_text(),'preserve');self.assertEqual((dest/'ignored/evidence').read_text(),'ignored/evidence')
        self.assertEqual(os.readlink(dest/'link'),'/outside/does-not-exist');self.assertFalse((dest/'__pycache__').exists())
        manifest=json.loads((dest.parent/(self.root.name+'.sha256.json')).read_text());self.assertEqual(len(manifest['files']),3)
        self.assertEqual(manifest['excluded_caches'],['__pycache__/cache'])
    def test_git_refusal_preserves_originals_and_custody(self):
        (self.root/'new').write_text('preserve');self.snapshot();self.decision['custody']=True
        with self.assertRaises(subprocess.CalledProcessError):self.run_script(True)
        self.assertEqual((self.root/'new').read_text(),'preserve')
        self.assertEqual((self.main/'artifacts/worktree_custody'/self.root.name/'new').read_text(),'preserve')
    def test_dry_run_custody_does_not_copy(self):
        (self.root/'new').write_text('preserve');self.snapshot();self.decision['custody']=True
        self.run_script();self.assertFalse((self.main/'artifacts/worktree_custody').exists())
    def test_existing_custody_rejected(self):
        dest=self.main/'artifacts/worktree_custody'/self.root.name;dest.mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError,'destination exists'):NS['custody'](self.main,self.root,self.row,True)
    def citation(self,repoint=True,identical=True):
        file=self.main/'citation';replacement=self.main/'base';old=str(self.root)+'/base'
        file.write_text(str(replacement) if repoint else old)
        self.row['citations']=[dict(file=str(file),targets=[dict(old=old,replacement=str(replacement),byte_identical=identical,sha256=NS['sha'](replacement))])]
    def test_verified_repoint_passes(self):
        self.citation();NS['repointed'](self.main,self.row,self.census)
    def test_stale_citation_rejected(self):
        self.citation(False)
        with self.assertRaisesRegex(RuntimeError,'not repointed'):NS['repointed'](self.main,self.row,self.census)
    def test_nonidentical_replacement_rejected(self):
        self.citation(identical=False)
        with self.assertRaisesRegex(RuntimeError,'no byte-identical'):NS['repointed'](self.main,self.row,self.census)
    def test_new_citation_rejected(self):
        self.citation();(self.main/'newcitation').write_text(str(self.root)+'/base')
        with self.assertRaisesRegex(RuntimeError,'remaining citations'):NS['repointed'](self.main,self.row,self.census)
    def test_process_and_scan_failure_guards(self):
        # Recover original function: setUp patched only the global dictionary.
        source=SCRIPT.read_text().split("<<'PY_HELPER'\n",1)[1].split('\nPY_HELPER',1)[0];fresh={'__name__':'test'};exec(source,fresh)
        for rc,out,err in [(0,'p1\ncworker\nn'+str(self.root)+'/child\n',''),(1,'','permission denied')]:
            with self.subTest(rc=rc),mock.patch.object(subprocess,'run',return_value=subprocess.CompletedProcess([],rc,out,err)):
                with self.assertRaises(RuntimeError):fresh['processes'](self.root)
    def test_no_force_branch_delete_or_push_command(self):
        source=SCRIPT.read_text()
        self.assertNotIn('--force',source);self.assertNotIn('rm -rf',source)
        self.assertNotIn("'push'",source);self.assertNotIn("'branch','-D'",source)

if __name__=='__main__':unittest.main(verbosity=2)
