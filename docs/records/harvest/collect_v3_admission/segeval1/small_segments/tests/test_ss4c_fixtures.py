"""Rescan the actual synthetic witnesses with the pinned scanner in place."""
import json, subprocess, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss4_common import *
from run_type import PILLOW
class Fixtures(unittest.TestCase):
    def test_canonical_fixtures(self):
        result=json.loads((SS/'q3/replay_fixture_ss4c/RESULT.json').read_text())
        check_scanner()
        for name,case in result['cases'].items():
            with self.subTest(case=name):
                p=subprocess.run(PILLOW+[str(SCANNER),case['rollout'],case['reader']],capture_output=True,text=True)
                scan=json.loads(p.stdout)
                self.assertEqual(scan['ok'],name in ('a','c'))
                self.assertEqual(p.returncode,0 if name in ('a','c') else 2)
                if name=='c': self.assertEqual(scan['image_match_counts'],{'bytes':2})
                if name=='a': self.assertEqual(scan['image_match_counts'],{'bytes':1})
                if name=='absolute_font': self.assertTrue(any(v['reason']=='absolute path outside reader_dir' for v in scan['violations']))
                if name=='b':
                    commands=[c for r in scan['reproductions'] for c in r['commands']]
                    self.assertTrue(any(c['status']=='replayed' and "open('items.jsonl')" in c['command'] for c in commands))
if __name__=='__main__': unittest.main()
