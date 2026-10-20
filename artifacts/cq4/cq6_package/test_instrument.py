"""Small semantic fixtures; no production bootstrap or inference."""
import copy
import unittest
import evaluate as e

class Instrument(unittest.TestCase):
    def fixture(self):
        truth=[dict(slot_id=['a',0],doc='d1',breathing='smooth',accent='acute'),
               dict(slot_id=['b',0],doc='d2',breathing='none',accent='none')]
        predictions=[]
        for s in e.SEEDS:
            for a in e.ARMS:
                for t in truth:
                    predictions.append(dict(t,seed=s,arm=a,breathing=t['breathing'] if a=='R2a-2' else 'none',accent=t['accent'] if a=='R2a-2' else 'none'))
        review=dict(truth_sha256='t',predictions_sha256='p',items=[dict(seed=s,slot_id=['a',0],pixel_checked=True,blind_to_arm=True,evidence='fixture') for s in e.SEEDS])
        return truth,predictions,review

    def test_exact_tuple_and_seed_pairing(self):
        t,p,r=self.fixture()
        result=e.primary(t,p,r,'t','p',reps=100)
        self.assertEqual(result['primary']['pooled_gain_pp'],100)
        self.assertTrue(result['primary']['primary_pass'])
        # Correct breathing with wrong accent is an exact-tuple miss.
        for x in p:
            if x['slot_id']==['a',0] and x['arm']=='R2a-2':x['accent']='none'
        self.assertEqual(e.primary(t,p,r,'t','p',reps=100)['primary']['pooled_gain_pp'],0)

    def test_no_review_no_score_and_missing_stops(self):
        t,p,r=self.fixture()
        with self.assertRaises(ValueError):e.primary(t,p,{},'t','p',reps=100)
        with self.assertRaises(ValueError):e.primary(t,p[:-1],r,'t','p',reps=100)

    def test_false_additions_guard(self):
        t,p,r=self.fixture()
        for x in p:
            if x['slot_id']==['b',0] and x['arm']=='R2a-2':x['breathing']='smooth'
        r['items'] += [dict(seed=s,slot_id=['b',0],pixel_checked=True,blind_to_arm=True,evidence='fixture') for s in e.SEEDS]
        result=e.primary(t,p,r,'t','p',reps=100)['primary']
        self.assertEqual(result['pooled_false_additions_delta'],3)
        self.assertFalse(result['primary_pass'])

    def test_lqb_exposure_and_unknown(self):
        rr=[dict(slot_id=['a',0],arm='R2a-2',truth_tier='A',truth=[1,0,None,0],prediction=[1,1,1,0]),
            dict(slot_id=['b',0],arm='R2a-2',truth_tier='B',truth=[1,0,0,0],prediction=[1,0,0,0])]
        result=e.lqb(rr,[dict(slot_id=['a',0])])
        self.assertEqual(result[0]['marks_precision'],.5)
        self.assertEqual(result[0]['unknown_truth'],1)
        self.assertEqual(result[0]['false_additions'],1)
        self.assertEqual(result[1]['marks_precision'],1)

if __name__=='__main__':unittest.main()
