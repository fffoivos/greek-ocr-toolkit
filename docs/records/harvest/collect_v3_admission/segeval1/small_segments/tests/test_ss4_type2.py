import collections,json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss4_common import *
from map_type import validate
from scan_type_packs import scan
from run_type import weekly
class SS4Type2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key=json.loads((SS/'q3/keys/type2.json').read_text()); cls.sample=rows(SS/'q3/sample.jsonl')
    def test_public_fields_hashes_and_closure(self):
        for ctx,c in self.key['contexts'].items():
            self.assertTrue(scan(ctx,False,layout="type2")['ok']); self.assertLessEqual(len(c['card_ids']),100)
            for r in rows(PACK_ROOT/'type2'/ctx/'r1/items.jsonl'):
                self.assertEqual(set(r),{'card_id','crop','google_text'})
                self.assertEqual(Path(r['crop']).stem,sha(PACK_ROOT/'type2'/ctx/'r1'/r['crop']))
                m=self.key['items'][r['card_id']]; src=next(x for x in self.sample if x['line_id']==m['line_id'])
                self.assertEqual(r['google_text'],src['raw_text']); self.assertEqual(sha(PACK_ROOT/'type2'/ctx/'r1'/r['crop']),src['crop_sha256'])
    def test_grep_entire_tree(self):
        forbidden={'line_id','source_id','key_opus','LEAD_CONTROLS','expected','stratum','verdict_05','primary_class'}
        for r in self.sample: forbidden.update([r['line_id'],r['book'],r['source']])
        # rg -a -w searches the whole tree, including binary bytes, for complete private tokens.
        # Whole tokens avoid accidental nlg inside compressed bytes 0nlg9i; byte copies are mandatory.
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write('\n'.join(sorted(forbidden))+'\n'); f.flush()
            p=subprocess.run(['rg','-a','-w','--hidden','--no-ignore','-l','-F','-f',f.name,str(PACK_ROOT/'type2')],capture_output=True,text=True)
        self.assertEqual(p.returncode,1,p.stdout+p.stderr)
    def test_controls_and_complete_bed(self):
        used=collections.Counter(); bed=[]
        for c in self.key['contexts'].values():
            ctl=[self.key['items'][i]['line_id'] for i in c['card_ids'] if self.key['items'][i]['control']]
            self.assertEqual(len(ctl),len(set(ctl))); self.assertTrue(8<=len(ctl)<=10); used.update(ctl)
            bed.extend(self.key['items'][i]['line_id'] for i in c['card_ids'] if not self.key['items'][i]['control'])
        controls=json.loads((SS/'q3/LEAD_CONTROLS.json').read_text())['controls']
        self.assertEqual(set(used),set(controls)); self.assertTrue(all(v>=1 for v in used.values()))
        self.assertEqual(len(bed),len(set(bed))); self.assertEqual(set(bed),{r['line_id'] for r in self.sample}-set(controls))
    def fixture(self):
        ctx='t01'; c=self.key['contexts'][ctx]; items=self.key['items']; answers=[]
        for cid in c['card_ids']:
            e=items[cid].get('expected',dict(type='word',text=['match'],crop=['ok'],rotated='no'))
            answers.append(dict(card_id=cid,type=e['type'],text=e['text'][0],crop=e['crop'][0],rotated=e['rotated'],detail=''))
        return answers,c['card_ids'],items,ctx
    def test_missing_card(self):
        a,o,k,c=self.fixture()
        with self.assertRaises(ValueError): validate(a[:-1],o,k,c)
    def test_wrong_order(self):
        a,o,k,c=self.fixture(); a[0],a[1]=a[1],a[0]
        with self.assertRaises(ValueError): validate(a,o,k,c)
    def test_out_of_list(self):
        a,o,k,c=self.fixture(); a[0]['type']='INVALID'
        with self.assertRaises(ValueError): validate(a,o,k,c)
    def test_control_error_and_flag(self):
        a,o,k,c=self.fixture(); self.assertEqual(validate(a,o,k,c)[1]['control_errors'],0)
        controls=[r for r in a if k[r['card_id']]['control']]
        controls[0]['rotated']='yes' if controls[0]['rotated']=='no' else 'no'; check=validate(a,o,k,c)[1]
        self.assertEqual(check['control_errors'],1); self.assertFalse(check['flagged'])
        controls[1]['rotated']='yes' if controls[1]['rotated']=='no' else 'no'; self.assertTrue(validate(a,o,k,c)[1]['flagged'])
    def test_scanner_hash_refusal(self):
        check_scanner()
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'different scanner'); f.flush()
            with self.assertRaises(ValueError): check_scanner(f.name)
    def test_weekly_bucket(self):
        self.assertEqual(weekly('limit_id=codex primary=2%/300m secondary=78%/10080m'),78)
        with self.assertRaises(ValueError): weekly('limit_id=codex primary=2%/300m')
if __name__=='__main__': unittest.main()
