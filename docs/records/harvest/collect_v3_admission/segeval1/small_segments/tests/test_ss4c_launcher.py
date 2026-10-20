"""Driver plumbing without invoking probes, Codex, or a reader."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import run_type
from ss4_common import SS, PACK_ROOT
class Launcher(unittest.TestCase):
    def exercise(self, scan_rc=0, budget=20):
        with tempfile.TemporaryDirectory(dir=SS/'q3') as td:
            root=Path(td)
            for name in ('q3/prompts_rendered','q3/answers','prompts'): (root/name).mkdir(parents=True,exist_ok=True)
            prompt=(SS/'prompts/type.md').read_bytes(); (root/'prompts/type.md').write_bytes(prompt)
            rollout=root/'rollout.jsonl'; rollout.write_text('')
            calls=[]
            def command(argv,**kw):
                calls.append(argv)
                if 'run_read.sh' in str(argv):
                    self.assertEqual(argv[3],str(PACK_ROOT/'type2/t01/r1'))
                    self.assertEqual(Path(argv[4]).read_bytes(),prompt)
                    return subprocess.CompletedProcess(argv,0,json.dumps(dict(rc=0,model='gpt-6.1-sol',rollout=str(rollout),usage={'total_tokens':1})), '')
                if str(run_type.SCANNER) in argv:
                    kw['stdout'].write(json.dumps(dict(ok=scan_rc==0)))
                    return subprocess.CompletedProcess(argv,scan_rc,'','')
                self.assertEqual(argv[-3:],['t01','--layout','type2'])
                return subprocess.CompletedProcess(argv,0,'','')
            with patch.object(run_type,'SS',root), patch.object(run_type,'probe',return_value=f'limit_id=codex secondary={budget}%/10080m') as probes, patch.object(run_type.subprocess,'run',side_effect=command), patch('scan_type_packs.scan',return_value={'ok':True}):
                rc=run_type.main('t01')
            if budget>=78:
                self.assertEqual(rc,8); self.assertFalse(calls); self.assertEqual(probes.call_count,1)
            else:
                self.assertEqual(rc,2 if scan_rc else 0); self.assertEqual(len(calls),2 if scan_rc else 3); self.assertEqual(probes.call_count,2)
                ledger=json.loads((root/'q3/usage_ledger.jsonl').read_text()); self.assertEqual(ledger['layout'],'type2'); self.assertEqual(ledger['void'],scan_rc!=0)
    def test_success(self): self.exercise()
    def test_void(self): self.exercise(scan_rc=2)
    def test_budget_gate(self): self.exercise(budget=78)
if __name__=='__main__': unittest.main()
