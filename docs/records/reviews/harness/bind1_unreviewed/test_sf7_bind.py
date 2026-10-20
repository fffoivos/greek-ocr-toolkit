"""Offline synthetic binding rehearsals; no live release binding or Git writes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT/'docs/reviews/harness/sf7_bind.sh'
REGISTRY = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c/labels/VERSIONS.json')
LQB = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/versions.json')
DOC = 'docs/labelfix/spellcheck/'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj))

class BindTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='.bind1-test-',dir=ROOT)
        self.root = Path(self.tmp.name)
        for name in ('docs/reviews/harness/sf7_bind.sh',DOC+'SF7_PREREGISTRATION.md',
                     DOC+'CORRECTION_STATUS_MARKS.md','artifacts/sf7_rc1/RELEASE_RECEIPT.json',
                     'artifacts/sf7_rc1/release_edits_only_A.jsonl'):
            p=self.root/name; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/name,p)
        self.verdict=self.root/'verdict.json'
        self.score()
        # Audit every Python file write, including temporary atomic files. The binder's only
        # subprocess is date. This catches attempted external writes even if later undone.
        hook=self.root/'hook'; hook.mkdir()
        (hook/'sitecustomize.py').write_text('''import sys, os
from pathlib import Path
root=Path(os.environ['BIND_TEST_ROOT']).resolve()
def guard(event,args):
    if event=='open':
        path,mode,flags=args
        write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write and isinstance(path,(str,bytes)) and not Path(os.fsdecode(path)).resolve().is_relative_to(root):
            raise RuntimeError('OUTSIDE WRITE: '+str(path))
    if event in ('os.rename','os.remove','os.mkdir','os.rmdir'):
        for path in args[:2] if event=='os.rename' else args[:1]:
            if isinstance(path,(str,bytes)) and not Path(os.fsdecode(path)).resolve().is_relative_to(root):
                raise RuntimeError('OUTSIDE MUTATION: '+str(path))
sys.addaudithook(guard)
''')
        self.env={**os.environ,'PYTHONPATH':str(hook),'PYTHONDONTWRITEBYTECODE':'1','BIND_TEST_ROOT':str(self.root)}
        self.external_before={p:sha(p) for p in (REGISTRY,LQB)}
    def tearDown(self):
        for p,before in self.external_before.items(): self.assertEqual(sha(p),before)
        self.tmp.cleanup()
    def score(self,correct=83,pending=0,**fields):
        lines=[dict(line_id=f'line-{i}',status='CORRECT' if i<correct else 'PENDING' if i<correct+pending else 'INCORRECT') for i in range(100)]
        s=dict(frame_lines=100,correct=correct,incorrect=100-correct-pending,pending=pending,
               scored=100-pending,final_line_precision=None if pending else correct/100,
               line_precision_bar_pass=None if pending else correct>=83,controls_gate_passed=True,
               full_preregistration_pass=True,cluster_bootstrap={'document_bootstrap95':[.75,.9]})
        s.update(fields);dump(self.verdict,dict(summary=s,lines=lines,heads=[]))
    def run_bind(self,*args,ok=True):
        r=subprocess.run(['bash',str(self.root/'docs/reviews/harness/sf7_bind.sh'),*args,str(self.verdict)],
                         cwd=self.root,env=self.env,capture_output=True,text=True)
        if ok:self.assertEqual(r.returncode,0,r.stderr)
        else:self.assertNotEqual(r.returncode,0,r.stdout)
        return r
    def snapshot(self):
        return {str(p.relative_to(self.root)):sha(p) for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}
    def counterpart(self):
        base=self.root/'artifacts/sf7_rc1_test'
        train=read(self.root/'artifacts/sf7_rc1/RELEASE_RECEIPT.json')
        row=json.loads((self.root/'artifacts/sf7_rc1/release_edits_only_A.jsonl').read_text().splitlines()[0])
        releases={}
        for split in ('test','dev'):
            rr=dict(row,line_id=f'{split}-id',split=split,release_id='sf7_rc1_test_edits_A')
            payload=base/split/f'release_edits_only_{split}_A.jsonl';dump(payload,rr)
            r={k:train[k] for k in ('schema','parent','variant','policy_digest','preregistration_sha256')}
            r.update(release_id='sf7_rc1_test_edits_A',split=split,status='candidate_pre_audit',bound=False,
                     source_job='1234567',path='/remote/output/'+payload.name,sha256=sha(payload),row_count=1,
                     edit_count=len(rr['edits']),parent_path='/raw/'+split,parent_sha256='a'*64)
            dump(base/split/f'RELEASE_RECEIPT_{split}.json',r);releases[split]=r
        dump(base/'receipt.json',dict(complete=True,dry_run=False,inference_executed=True,
             release_id='sf7_rc1_test_edits_A',releases=releases))
        return base
    def test_pass_without_counterpart(self):
        self.run_bind('--execute')
        r=read(self.root/'artifacts/sf7_rc1/RELEASE_RECEIPT.json')
        self.assertEqual(r['status'],'bound');self.assertTrue(r['bound'])
        self.assertEqual(r['test_counterpart']['status'],'pending')
        self.assertEqual(r['binding_audit']['verdict_sha256'],sha(self.verdict))
        self.assertRegex(r['binding_audit']['time_athens'],r'\+0[23]00$')
        patch=read(self.root/(DOC+'sf7_registry_entries.json'))
        self.assertEqual(set(patch['versions']),{'sf7_rc1_edits_A'})
        self.assertEqual(patch['target'],str(REGISTRY))
        self.assertEqual(patch['versions']['sf7_rc1_edits_A']['id_field'],'line_id')
        self.assertIn('Experiment-A switch-on handoff',(self.root/(DOC+'SF7_BINDING.md')).read_text())
    def test_pass_with_counterpart(self):
        base=self.counterpart();self.run_bind('--execute')
        for split in ('test','dev'):
            self.assertTrue(read(base/split/f'RELEASE_RECEIPT_{split}.json')['bound'])
        self.assertTrue(read(base/'receipt.json')['bound'])
        for name in ('sf7_registry_entries.json','sf7_lqb_registration.json'):
            patch=read(self.root/(DOC+name));e=patch['versions']['sf7_rc1_test_edits_A']
            self.assertEqual(e['sha256'],sha(Path(e['path'])))
            self.assertEqual(e['population']['rows'],2);self.assertEqual(patch['pending'],[])
        lqb=read(self.root/(DOC+'sf7_lqb_registration.json'))
        self.assertTrue(lqb['versions']['sf7_rc1_edits_A']['overlay'])
    def test_dry_run_default(self):
        before=self.snapshot();self.run_bind();after=self.snapshot()
        after.pop('docs/reviews/harness/sf7_bind.log')
        self.assertEqual(before,after)
    def test_fail_only_receipt_and_report(self):
        self.counterpart();self.score(correct=82)
        v=read(self.verdict);v.update(verdict='FAIL',reasons=['native audit rejected']);dump(self.verdict,v)
        before=self.snapshot();self.run_bind('--execute');after=self.snapshot()
        changed={p for p in after if before.get(p)!=after[p]}
        self.assertEqual(changed,{'artifacts/sf7_rc1/RELEASE_RECEIPT.json',DOC+'SF7_BINDING.md','docs/reviews/harness/sf7_bind.log'})
        self.assertIn('native audit rejected',read(self.root/'artifacts/sf7_rc1/RELEASE_RECEIPT.json')['rejection_reasons'])
    def test_pending_no_mutation(self):
        self.score(correct=70,pending=30);before=self.snapshot()
        self.assertIn('PENDING',self.run_bind('--execute',ok=False).stderr);self.assertEqual(before,self.snapshot())
    def test_unresolved_line_class_refused(self):
        self.score(full_preregistration_pass=None);self.run_bind('--execute',ok=False)
        self.assertFalse((self.root/(DOC+'SF7_BINDING.md')).exists())
    def test_contradictory_pass_refused(self):
        self.score(correct=82);v=read(self.verdict);v['verdict']='PASS';dump(self.verdict,v)
        self.run_bind('--execute',ok=False)
    def test_tampered_payload_refused(self):
        with (self.root/'artifacts/sf7_rc1/release_edits_only_A.jsonl').open('a') as f:f.write('\n')
        before=self.snapshot();self.run_bind('--execute',ok=False);self.assertEqual(before,self.snapshot())
    def test_partial_counterpart_refused(self):
        base=self.counterpart();(base/'dev/RELEASE_RECEIPT_dev.json').unlink()
        before=self.snapshot();self.run_bind('--execute',ok=False);self.assertEqual(before,self.snapshot())
    def test_mock_counterpart_refused(self):
        base=self.counterpart();v=read(base/'receipt.json');v['dry_run']=True;dump(base/'receipt.json',v)
        self.run_bind('--execute',ok=False)
    def test_external_symlink_refused_before_any_write(self):
        target=self.root/(DOC+'sf7_registry_entries.json');target.symlink_to(REGISTRY)
        before=self.snapshot();r=self.run_bind('--execute',ok=False)
        self.assertIn('symlink',r.stderr);self.assertEqual(before,self.snapshot())
    def test_log_symlink_refused_before_any_write(self):
        (self.root/'docs/reviews/harness/sf7_bind.log').symlink_to(LQB)
        before=self.snapshot();self.run_bind('--execute',ok=False)
        self.assertEqual(before,self.snapshot())
    def test_dry_run_with_counterpart(self):
        self.counterpart();before=self.snapshot();self.run_bind('--dry-run');after=self.snapshot()
        after.pop('docs/reviews/harness/sf7_bind.log');self.assertEqual(before,after)
    def test_duplicate_audit_lines_refused(self):
        v=read(self.verdict);v['lines'][1]['line_id']=v['lines'][0]['line_id'];dump(self.verdict,v)
        self.run_bind('--execute',ok=False)
    def test_line_class_failure_rejects(self):
        self.score(correct=90,full_preregistration_pass=False);self.run_bind('--execute')
        self.assertEqual(read(self.root/'artifacts/sf7_rc1/RELEASE_RECEIPT.json')['status'],'rejected')
    def test_no_push_or_git_invocation(self):
        traps=self.root/'bin';traps.mkdir()
        for name in ('git','ssh','curl','wget','rsync','scp'):
            p=traps/name;p.write_text('#!/bin/sh\necho FORBIDDEN >&2\nexit 99\n');p.chmod(0o755)
        self.env['PATH']=str(traps)+os.pathsep+os.environ['PATH']
        r=self.run_bind('--execute');self.assertNotIn('FORBIDDEN',r.stderr)
        text=SCRIPT.read_text()
        self.assertNotIn('git push',text);self.assertNotIn('tools.',text)

if __name__=='__main__':unittest.main()
