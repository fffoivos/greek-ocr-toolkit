"""Offline replacement routing and launch-policy fixtures; no reader execution."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru3t_r5 as r

class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.art=self.root/'art';self.art.mkdir();self.pack=self.root/'pack'
        self.info=dict(assignments=[dict(context=ctx,reader='r5',replaces=ctx+'/r1',items=4) for ctx in ['ctx08','ctx18']])
        self.stack=contextlib.ExitStack();self.stack.enter_context(patch.object(r,'ART',self.art));self.stack.enter_context(patch.object(r,'PACK',self.pack));self.stack.enter_context(patch.object(r,'validate',return_value=self.info))
    def tearDown(self):self.stack.close();self.tmp.cleanup()
    def probe(self,used):return lambda *a,**k:f'limit_id=codex primary={used}%/10080m reset ?'
    def test_dry_run_has_no_probe_or_launch(self):
        def fail(*a,**k):raise AssertionError('live invocation')
        out=io.StringIO()
        with contextlib.redirect_stdout(out):r.drive(True,fail,fail)
        self.assertEqual(len(out.getvalue().splitlines()),2);self.assertFalse((self.art/'driver.lock').exists())
    def test_exact70_and_persistent_stop(self):
        def fail(*a,**k):raise AssertionError('launch')
        r.drive(False,fail,self.probe(70));self.assertTrue((self.art/'STOPPED_AT_70.json').exists());r.drive(False,fail,fail)
    def test_bad_probe_fails_closed(self):
        with self.assertRaises(ValueError):r.drive(False,lambda *a,**k:self.fail(),lambda *a,**k:'NONE')
    def test_launch_claim_is_permanent_even_after_failure(self):
        calls=[]
        def fail(*a,**k):calls.append(a);raise OSError('fixture')
        with self.assertRaises(OSError):r.drive(False,fail,self.probe(69))
        self.assertTrue(r.attempted(self.info['assignments'][0]))
        with self.assertRaises(OSError):r.drive(False,fail,self.probe(69))
        self.assertTrue(r.attempted(self.info['assignments'][1]));r.drive(False,fail,self.probe(69));self.assertEqual(len(calls),2)
    def test_existing_answer_never_reruns(self):
        a=self.info['assignments'][0];_,rd=r.paths(a);rd.mkdir(parents=True);(rd/'answers.jsonl').write_text('')
        out=io.StringIO()
        with contextlib.redirect_stdout(out):r.drive(True)
        self.assertEqual([json.loads(x)['context'] for x in out.getvalue().splitlines()],['ctx18'])
    def test_r5_routes_replace_five_and_keep_r4(self):
        previous=[dict(context='ctx18',reader=rd,replaces='ctx18/'+old) for rd,old in [('r3','r1'),('r4','r2')]]
        r.m.dump(self.art/'build.json',dict(assignments=previous))
        info=dict(assignments=[dict(context='ctx18',reader='r5',replaces='ctx18/r1')])
        with patch.object(r.prior,'ART',self.art):routes=r.routes(info)
        self.assertEqual(routes['ctx18/r1']['reader'],'r5')
        self.assertEqual(routes['ctx18/r2']['reader'],'r4')

    def test_finalizer_dry_run_never_collects_or_writes_labels(self):
        routes={a['replaces']:dict(a,round='r5') for a in self.info['assignments']}
        with patch.object(r,'original_info',return_value={}),patch.object(r,'routes',return_value=routes),patch.object(r.m,'collect_context',side_effect=AssertionError('reading')),patch.object(r.m,'finalize',side_effect=AssertionError('label write')):
            result=r.finalize(True)
        self.assertEqual(result['r5_contexts'],2)
        self.assertFalse(result['labels_written'])
        self.assertFalse(result['registry_written'])

if __name__=='__main__':unittest.main()
