"""Pass-1 VOID gating, overlap coverage, and reread closure using synthetic answers."""
import tempfile, shutil, unittest
from unittest.mock import patch
import common_full as common
import flag_full as flag
from common_full import *

class G4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='test-flag-v4-',dir=flag.scan_rollout.REPLAY_TMP)
        cls.fixture=Path(cls.temp.name);cls.root=cls.fixture/'private';cls.bed=cls.fixture/'packs';cls.aa=cls.fixture/'answers'
        (cls.root/'keys').mkdir(parents=True);cls.aa.mkdir();cls.bed.mkdir()
        for f in ('key.json','CONTROL_VERIFICATION.json'):shutil.copyfile(ROOT/'keys'/f,cls.root/'keys'/f)
        cls.key=load(ROOT/'keys/key.json');cls.names=list(dict.fromkeys(m['context'] for m in cls.key.values()))
        cls.flagged={}
        for name in cls.names:
            manifest=load(BED/f'MANIFEST.{name}.json');folder=cls.bed/name;folder.mkdir()
            for rel in manifest['files']:
                dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BED/name/rel,dest)
            shutil.copyfile(BED/f'MANIFEST.{name}.json',cls.bed/f'MANIFEST.{name}.json')
            answers=[];changed=False
            for iid,m in cls.key.items():
                if m['context']!=name:continue
                accent=m['truth_accent'] if m['role']=='control' else m['label_accent']
                if m['role']=='bed' and not changed:
                    accent='unreadable';changed=True;cls.flagged[name]=iid
                answers.append(dict(item_id=iid,accent=accent,confidence='high',note='SYNTHETIC SR-G4'))
            (cls.aa/(name+'.jsonl')).write_text(''.join(json.dumps(a)+'\n' for a in answers))
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        self.patches=[patch.object(mod,attr,value) for mod in (flag,common) for attr,value in (('ROOT',self.root),('BED',self.bed))]
        for p in self.patches:p.start()
        for name in self.names:(self.aa/(name+'.scan.json')).write_text(json.dumps(dict(scanner_version=4,ok=True,violations=[])))
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
    def void(self,name,version=4):
        (self.aa/(name+'.scan.json')).write_text(json.dumps(dict(scanner_version=version,ok=False if version==4 else True,violations=[dict(reason='SYNTHETIC violation')])))
    def test_void_excluded_and_overlap_accounted(self):
        self.void('p1c1');r=flag.run(answer_root=self.aa)
        self.assertEqual(r['void_contexts'],['p1c1'])
        self.assertEqual(r['items']+r['excluded_items'],sum(m['role']=='bed' for m in self.key.values()))
        self.assertEqual(r['flagged'],3);self.assertNotIn(self.flagged['p1c1'],{f['item_id'] for f in r['flags']})
        self.assertEqual(len(r['overlap'])+len(r['overlap_void']),17)
        self.assertNotIn('p1c1',r['controls']);self.assertIn('VOID', (self.root/'PASS1.md').read_text())
    def test_old_scanner_is_void(self):
        self.void('p1c2',3);r=flag.run(answer_root=self.aa);self.assertEqual(r['void_contexts'],['p1c2'])
    def test_reread_excludes_void_and_closes(self):
        self.void('p1c1');r=flag.run(True,self.aa)
        key=load(self.root/'keys/p2_key.json');beds=[m for m in key.values() if m['role']=='bed']
        self.assertEqual(len(beds),3);self.assertNotIn(self.flagged['p1c1'],{m['p1_id'] for m in beds})
        self.assertTrue(g1.scan(self.bed/'p2',key)['ok']);self.assertEqual(sum(m['role']=='control' for m in key.values()),2)
    def test_all_void_zero_denominators(self):
        for name in self.names:self.void(name)
        r=flag.run(answer_root=self.aa);self.assertEqual(r['items'],0);self.assertIsNone(r['sol_grave_share']['rate']);self.assertEqual(len(r['overlap_void']),17)

if __name__=='__main__':unittest.main(verbosity=2)
