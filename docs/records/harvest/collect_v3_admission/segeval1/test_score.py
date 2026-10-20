"""Synthetic scoring checks only. These are not reader answers or accuracy results."""
import copy,importlib.util,json,unittest
from pathlib import Path
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('score',D/'segeval1_score.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class ScoringTests(unittest.TestCase):
 def setUp(self):
  self.keys={b:s.load(D/'keys'/f'{b}.json') for b in ('segeval1_a','segeval1_b')}
  self.decisions={r['row_id']:r for r in s.rows(D/'keys/sealed_decisions.jsonl')}
  self.answers={}
  for bed,k in self.keys.items():
   aa=[]
   for iid in k['order']:
    m=k['items'][iid]
    a=dict(card_id=iid,letters='y',marks='y',crop_ok='y',errors=[],detail='',segmentation_detail='',**{f:'no' for f in s.RUBRIC})
    if m['control']:a.update({f:m['control_origin']['reference_verdict'][f] for f in ('letters','marks','crop_ok')})
    aa.append(a)
   self.answers[bed]=aa
 def study_answer(self,decision):
  return next(a for b,aa in self.answers.items() for a in aa if not self.keys[b]['items'][a['card_id']]['control'] and self.keys[b]['items'][a['card_id']]['decision']==decision)
 def run_score(self):return s.score(self.answers,self.keys,self.decisions)
 def test_all_fine(self):
  r,t=self.run_score();self.assertEqual((r['false_positives'],r['false_negatives'],len(t)),(50,0,150));self.assertTrue(r['controls_valid'])
 def test_overlapping_flags(self):
  a=self.study_answer('ACCEPT');a['rotated']='yes';a['multi_line']='yes'
  self.study_answer('REJECT')['neighbour_whole_word']='yes'
  r,_=self.run_score();self.assertEqual((r['false_positives'],r['false_negatives']),(49,1));self.assertEqual(r['false_negatives_by_rubric'],{'multi_line':1,'rotated':1})
 def test_uncertainty(self):
  self.study_answer('REJECT')['rotated']='uncertain'
  r,_=self.run_score();self.assertEqual(r['false_positives'],49);self.assertEqual(r['unresolved']['REJECT'],1)
 def test_transcription_not_segmentation(self):
  a=self.study_answer('ACCEPT');a.update(letters='n',crop_ok='n',errors=['wrong_letter'])
  r,_=self.run_score();self.assertEqual(r['false_negatives'],0)
 def test_order_rejected(self):
  self.answers['segeval1_a'].reverse()
  with self.assertRaises(ValueError):self.run_score()
 def test_missing_rubric_rejected(self):
  del self.study_answer('REJECT')['rotated']
  with self.assertRaises(KeyError):self.run_score()
 def test_control_gate(self):
  b='segeval1_a';aa=[a for a in self.answers[b] if self.keys[b]['items'][a['card_id']]['control']]
  for a in aa[:2]:a['letters']='n' if a['letters']=='y' else 'y'
  r,_=self.run_score();self.assertFalse(r['controls_valid'])
 def test_scan_gate_rejects_void_legacy_and_skipped(self):
  clean=dict(ok=True,violations=[],manifest_check_skipped=False,scanner_version=s.SCANNER_VERSION)
  for change in (dict(ok=False),dict(violations=[dict(reason='violation')]),dict(manifest_check_skipped=True),dict(scanner_version='v4.4-canonical')):
   with self.subTest(change=change),self.assertRaisesRegex(ValueError,'missing VALID'):
    s.validate_scan(dict(clean,**change),Path('/nonexistent/scan.json'),Path('/nonexistent/answers.jsonl'))
if __name__=='__main__':unittest.main()
