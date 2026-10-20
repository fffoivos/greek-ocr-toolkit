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
import ru3t_r3 as r

class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.art=self.root/'art';self.art.mkdir();self.pack=self.root/'pack'
        self.info=dict(assignments=[dict(context='ctx18',reader=rd,replaces='ctx18/'+old,items=4) for rd,old in [('r3','r1'),('r4','r2')]])
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
        self.assertEqual([json.loads(x)['reader'] for x in out.getvalue().splitlines()],['r4'])
    def test_route_ctx18_to_two_physical_readers_and_preserve_combiner(self):
        collected=[]
        def collect(art,pack,ctx,reader,seen):collected.append((ctx,reader));return [],{}, {},{}
        def original_finalize():
            for reader in ['r1','r2']:r.m.collect_context(None,None,'ctx18',reader,set())
            p=dict(row_id='row',source_id='row',offset=0,google='ь',kind='pre_hyphen')
            votes=[dict(reader=reader,context='ctx18/'+reader,call='ъ',gate_status='VALID') for reader in ['r1','r2']]
            d=r.m.combine_position(p,votes);self.assertEqual(d['decision'],'edit_hard');self.assertEqual([d['reads'][x]['physical_reader'] for x in ['r1','r2']],['r3','r4'])
            return dict(output=dict(path=str(self.root/'labels.jsonl')),version='test',contexts={x['replaces']:dict(status='VALID') for x in self.info['assignments']},evidence={})
        import ru3t_delivery
        r.m.dump(self.art/'build.json',self.info)
        with patch.object(r,'original_info',return_value={}),patch.object(r.m,'collect_context',side_effect=collect),patch.object(r.m,'finalize',side_effect=original_finalize),patch.object(ru3t_delivery,'deliver',side_effect=lambda x:x):result=r.finalize()
        self.assertEqual(collected,[('ctx18','r3'),('ctx18','r4')]);self.assertEqual(result['contexts']['ctx18/r2']['replacement_reader'],'ctx18/r4')

if __name__=='__main__':unittest.main()
