"""Synthetic OC2 integration tests. No audit truth is read or invented."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/labelfix'))
import sf7_final_score as F
import copy,json,tempfile,unittest,unicodedata as U
R=F.R2;K=F.K

class FinalScoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pack=F.verify();cls.cards=R.read(K/'deck/blind/cards.jsonl');cls.keys={k['card_id']:k for k in R.read(K/'deck/private/key.jsonl')};cls.controls={c['card_id']:c for c in F.load(K/'deck/private/controls_proposed.json')['controls']};cls.target=next(c for c in cls.cards if not cls.keys[c['card_id']]['control'])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='oc2_test_',dir=K);self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def answer(self,c,wrong=False,unknown=False):
  k=self.keys[c['card_id']]
  if k['control']:form=self.controls[c['card_id']]['expected_form']
  else:
   marks={'smooth':'\u0313','rough':'\u0314','acute':'\u0301','grave':'\u0300','circumflex':'\u0342','subscript':'\u0345','none':''};base=c['base_letters'];chars=list(base);idx=[i for i,v in enumerate(chars) if v.isalpha()][c['anchor_index']]
   mark=marks[k['released_label']]
   if wrong:mark='' if mark else '\u0301'
   chars[idx]+=mark;form=U.normalize('NFC',''.join(chars))
  heads=R.form_heads(form)[c['anchor_index']]
  if unknown:heads={h:'unknown' for h in R.HEADS}
  return dict(card_id=c['card_id'],choice='literal',transcription=form,anchor_heads=heads,letter_heads=[],readability='readable',ownership_ok=None if R.unmarked(heads) else True,confidence='high',note='synthetic fixture only',usage=dict(input_tokens=0,output_tokens=0))
 def answers(self):return [self.answer(c) for c in self.cards]
 def run_pair(self,a,b,third=None):
  R.write(self.d/'r1.jsonl',a);R.write(self.d/'r2.jsonl',list(reversed(b)))
  if third is not None:R.write(self.d/'r3.jsonl',third)
  return F.resolve(self.d/'r1.jsonl',self.d/'r2.jsonl',self.d/'resolution',self.d/'r3.jsonl' if third is not None else None)
 def test_all_agree_and_bar(self):
  a=self.answers();truth,gates,passed=self.run_pair(a,a);s=F.merge(truth,passed)['summary']
  self.assertTrue(passed);self.assertEqual((s['correct'],s['pending'],s['final_line_precision']),(100,0,1));self.assertTrue(s['line_precision_bar_pass']);self.assertEqual(sum(x['total'] for x in s['per_head'].values()),107);self.assertEqual(s['cluster_bootstrap']['replicates'],10000)
 def test_disagreement_generates_fresh_tiebreak_then_two_of_three(self):
  a=self.answers();b=copy.deepcopy(a);i=next(i for i,c in enumerate(self.cards) if c==self.target);b[i]=self.answer(self.target,wrong=True)
  truth,gates,passed=self.run_pair(a,b);s=F.merge(truth,passed,bootstrap=False)['summary'];self.assertEqual(s['pending'],1)
  tb=R.read(self.d/'resolution/tiebreak/blind/cards.jsonl');self.assertEqual({c['card_id'] for c in tb},set(self.controls)|{self.target['card_id']})
  self.assertNotEqual(next(c for c in tb if c['card_id']==self.target['card_id'])['options'],self.target['options'])
  third=[self.answer(c) for c in tb];truth,gates,passed=self.run_pair(a,b,third);self.assertEqual(F.merge(truth,passed,bootstrap=False)['summary']['correct'],100)
 def test_tiebreak_folder_is_blind_and_write_once(self):
  a=self.answers();b=copy.deepcopy(a);i=next(i for i,c in enumerate(self.cards) if c==self.target);b[i]=self.answer(self.target,wrong=True);self.run_pair(a,b)
  folder=self.d/'reader3';F.stage_tiebreak(self.d/'resolution',folder);self.assertTrue(F.leak_scan(folder)['passed']);self.assertEqual((folder/'answers.jsonl').read_text(),'')
  (folder/'answers.jsonl').write_text('synthetic answer preservation');F.stage_tiebreak(self.d/'resolution',folder);self.assertEqual((folder/'answers.jsonl').read_text(),'synthetic answer preservation')
 def test_control_gate_fails_after_two_errors(self):
  a=self.answers();b=copy.deepcopy(a)
  for x in [x for x in b if x['card_id'] in self.controls][:2]:x['transcription']='?';x['anchor_heads']={h:'unknown' for h in R.HEADS}
  truth,gates,passed=self.run_pair(a,b);self.assertFalse(passed);self.assertFalse(gates['reader2']['accepted']);s=F.merge(truth,passed,bootstrap=False)['summary'];self.assertEqual((s['correct'],s['pending']),(70,30));self.assertIsNone(s['line_precision_bar_pass'])
 def test_one_control_error_is_allowed_by_r2(self):
  a=self.answers();b=copy.deepcopy(a);x=next(x for x in b if x['card_id'] in self.controls);x['choice']='unreadable';x['readability']='unreadable';x['anchor_heads']={h:'unknown' for h in R.HEADS}
  _,gates,passed=self.run_pair(a,b);self.assertTrue(passed);self.assertEqual(gates['reader2']['control_errors'],1)
 def test_unknown_keeps_line_pending(self):
  a=self.answers();i=next(i for i,c in enumerate(self.cards) if c==self.target);a[i]=self.answer(self.target,unknown=True)
  truth,gates,passed=self.run_pair(a,a);report=F.merge(truth,passed,bootstrap=False);self.assertEqual(report['summary']['pending'],1);self.assertIsNone(report['summary']['final_line_precision']);self.assertIsNone(report['summary']['line_precision_bar_pass']);self.assertEqual(next(x for x in report['heads'] if x['head_id']==self.keys[self.target['card_id']]['head_id'])['status'],'PENDING')
 def test_invalid_vote_is_per_card_and_gets_tiebreak(self):
  a=self.answers();b=copy.deepcopy(a);i=next(i for i,c in enumerate(self.cards) if c==self.target);b[i]['confidence']='invalid'
  truth,gates,passed=self.run_pair(a,b);self.assertTrue(passed);self.assertEqual(gates['reader2']['invalid_answer_count'],1);self.assertEqual(F.merge(truth,passed,bootstrap=False)['summary']['pending'],1)
  tb=R.read(self.d/'resolution/tiebreak/blind/cards.jsonl');self.assertEqual(len(tb),5);truth,gates,passed=self.run_pair(a,b,[self.answer(c) for c in tb]);self.assertEqual(F.merge(truth,passed,bootstrap=False)['summary']['correct'],100)
 def test_unmarked_anchor_ownership_null(self):
  c=next(c for c in self.cards if c['card_id'] in self.controls and R.unmarked(next(h for h in self.controls[c['card_id']]['expected_letter_heads'] if h['index']==c['anchor_index'])))
  a=self.answer(c);self.assertIsNone(R.normalise(a,c)['ownership_ok'])
 def test_reverse_order_and_folder_integrity(self):
  r1=R.read(self.pack/'r1/cards.jsonl');r2=R.read(self.pack/'r2/cards.jsonl');self.assertEqual(r1,list(reversed(r2)));self.assertEqual(len(r1),36)
  for reader in ('r1','r2'):self.assertEqual((self.pack/reader/'answers.jsonl').read_text(),'');self.assertTrue(F.leak_scan(self.pack/reader,['RB7-','released_label','stratum','source_id'])['passed'])
 def test_wrong_head_makes_line_incorrect(self):
  a=self.answers();i=next(i for i,c in enumerate(self.cards) if c==self.target);a[i]=self.answer(self.target,wrong=True);truth,_,passed=self.run_pair(a,a);s=F.merge(truth,passed,bootstrap=False)['summary'];self.assertEqual((s['correct'],s['incorrect'],s['pending']),(99,1,0))
 def test_missing_card_is_assignment_error(self):
  a=self.answers()
  with self.assertRaisesRegex(ValueError,'IDs/order'):self.run_pair(a,a[:-1])
 def test_tiebreak_failure_never_changes_truth(self):
  a=self.answers();b=copy.deepcopy(a);i=next(i for i,c in enumerate(self.cards) if c==self.target);b[i]=self.answer(self.target,wrong=True);self.run_pair(a,b);tb=R.read(self.d/'resolution/tiebreak/blind/cards.jsonl');third=[self.answer(c) for c in tb]
  for x in [x for x in third if x['card_id'] in self.controls][:2]:x['choice']='unreadable';x['readability']='unreadable';x['anchor_heads']={h:'unknown' for h in R.HEADS}
  truth,gates,passed=self.run_pair(a,b,third);self.assertFalse(passed);self.assertEqual(F.merge(truth,passed,bootstrap=False)['summary']['pending'],30)
 def test_pending_even_when_another_head_is_wrong(self):
  a=self.answers();multi=next(l for l in F.load(F.A/'routing.json')['lines'] if len([h for h in self.keys.values() if not h['control'] and h['line_id']==l['line_id']])==2);kk=[h for h in self.keys.values() if not h['control'] and h['line_id']==multi['line_id']]
  for k,unknown in zip(kk,[False,True]):
   i=next(i for i,c in enumerate(self.cards) if c['card_id']==k['card_id']);a[i]=self.answer(self.cards[i],wrong=not unknown,unknown=unknown)
  truth,_,passed=self.run_pair(a,a);r=F.merge(truth,passed,bootstrap=False);self.assertEqual(next(l for l in r['lines'] if l['line_id']==multi['line_id'])['status'],'PENDING')

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(FinalScoreTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 F.R2.dump(K/'test_receipt.json',dict(tests_run=result.testsRun,passed=result.testsRun-len(result.failures)-len(result.errors),failures=len(result.failures),errors=len(result.errors),synthetic_only=True,reads_launched=0,hashes={str(p):F.sha(p) for p in (Path(__file__),ROOT/'scripts/labelfix/sf7_final_score.py',ROOT/'scripts/labelfix/r2_cards_resolve.py')}))
 sys.exit(not result.wasSuccessful())
