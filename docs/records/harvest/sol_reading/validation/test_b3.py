"""SR-B3 regression tests, synthetic only."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import ROOT,dump,jsonl,PACK_ROOT
from scan_rollout import inspect
from score_all import paired_agreement,load_scorer,agreement_matrix
from b3_reports import matched,paired
class ScannerV3(unittest.TestCase):
 def fixture(self):
  root=Path(tempfile.mkdtemp(prefix='SYNTHETIC-B3-',dir=ROOT/'validation'));d=root/'sol_reading_packs/bsb/r1';d.mkdir(parents=True);dump(d.parent/'MANIFEST.r1.json',{'files':{}});return root,d
 def check(self,code):
  root,d=self.fixture();code=code.replace('READER',str(d)).replace('PACKROOT',str(d.parent.parent));r=root/'rollout.jsonl';jsonl(r,[{'payload':{'type':'custom_tool_call','name':'exec','input':code}}]);return inspect(r,d)
 def test_own_folder_absolute(self):
  for suffix in ('','/zoom/001.png','/cards.jsonl'):
   r=self.check('await tools.view_image({path:"READER'+suffix+'"})');self.assertTrue(r['ok'],r)
 def test_literal_template_interpolation(self):
  r=self.check("image((await tools.view_image({path:`${'READER'}/zoom/${String(i).padStart(3,'0')}.png`})).image_url)")
  self.assertTrue(r['ok'],r);self.assertNotIn('/zoom/$',r['paths'])
 def test_computed_template_suffix_relative(self):
  self.assertTrue(self.check('await tools.view_image({path:`${base}/zoom/${i}.png`})')['ok'])
 def test_sibling_and_pack_root_flag(self):
  for p in ('READER/../r2/zoom/001.png','PACKROOT/bsb/r2/zoom/001.png','PACKROOT','PACKROOT/yer/r1/zoom/001.png'):
   r=self.check('await tools.view_image({path:'+json.dumps(p)+'})');self.assertFalse(r['ok'],p)
 def test_sibling_template_flags(self):
  self.assertFalse(self.check("await tools.view_image({path:`${'PACKROOT/bsb/r2'}/zoom/${i}.png`})")['ok'])
class Agreements(unittest.TestCase):
 def fixture(self):
  heads=dict(breathing='none',accent='acute',diaeresis='none',subscript='none')
  a={i:dict(base='α',heads=copy.deepcopy(heads)) for i in ('a','b','c')};truth={i:dict(**copy.deepcopy(r),scored_heads=list(heads)) for i,r in a.items()};return a,truth
 def test_owner_self_and_known_count(self):
  a,t=self.fixture();scorer=load_scorer();self.assertEqual(paired_agreement(scorer,'owner39',a,a,t)['all_fields_per_card']['agree'],3)
  b=copy.deepcopy(a);b['b']['heads']['accent']='grave';r=paired_agreement(scorer,'owner39',a,b,t)
  self.assertEqual((r['all_fields_per_card']['agree'],r['all_fields_per_card']['compared']),(2,3))
 def test_disjoint_partial_cohorts_keep_self_agreement(self):
  a,t=self.fixture();n={'Sol r1':a,'Opus A':{'a':a['a']},'Opus B':{'b':a['b']}}
  self.assertEqual(set.intersection(*(set(x) for x in n.values())),set())
  m=agreement_matrix(load_scorer(),'owner39',n,list(n),t);r=m['Sol r1 | Sol r1'];self.assertEqual(r['fields']['base']['compared'],3);self.assertEqual(m['Sol r1 | Opus A']['all_fields_per_card']['compared'],1)
 def test_bsb_yer_self_denominators(self):
  scorer=load_scorer();b={'c':dict(letters='y',marks='n',crop_ok='y')};y={'a':dict(slots={'1':'ъ','2':'ь'})}
  self.assertEqual(paired_agreement(scorer,'bsb',b,b,b)['all_fields_per_card']['agree'],1)
  self.assertEqual(paired_agreement(scorer,'yer',y,y,y)['slots']['agree'],2)
 def test_paired_truth_counts(self):
  r=paired(dict(a='y',b='n',c='u',d='n'),dict(a='n',b='y',c='n',d='n'),dict.fromkeys('abcd','y'))
  self.assertEqual((r['better'],r['worse'],r['same'],r['n']),(1,1,2,4))
 def test_owner_pool_repeats_card_reads(self):
  a,t=self.fixture();b=copy.deepcopy(a);b['a']['heads']['accent']='grave'
  n={'Sol r1':a,'Opus E0a r1':{'a':a['a']},'Opus E0a r2':{'a':b['a'],'b':b['b']},'Opus E0b r1':{'b':b['b']},'Opus E0b r2':{'c':b['c']}}
  e=next(e for e in matched('owner39',n,t) if e['opus']=='Opus partial pooled' and e['metric']=='joint_anchor')
  self.assertEqual((e['n'],e['sol_correct'],e['opus_correct'],e['better'],e['worse'],e['same']),(5,5,4,1,0,4))
if __name__=='__main__':unittest.main()
