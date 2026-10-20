"""Offline preparation and synthetic answer-gating checks; never invokes a reader."""
import collections as C
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import cq7 as q

class CQ7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contexts=q.load(q.HERE/'contexts.json')

    def fixtures(self,answer=None):
        answer=answer or dict(breathing='smooth',accent='none')
        return [dict(tag=c['tag'],status='VALID',answers={i:answer.copy() for i in q.load(c['key'])['items']}) for c in self.contexts]

    def test_custody_and_packs(self):
        self.assertEqual(len(q.verify()),6)
        prior=q.rows(q.HERE/'prior_reads.jsonl')
        slots={q.sid(x) for x in prior}
        self.assertEqual(len(slots),196)
        self.assertEqual(slots,{q.sid(x) for x in q.rows(q.HERE/'baseline/quarantine/topup.jsonl')})
        counts=C.Counter();ids=[]
        for batch in range(3):
            a,z=[c for c in self.contexts if c['batch']==batch]
            ka=q.load(a['key'])['items'];kz=q.load(z['key'])['items']
            self.assertEqual([(x['slot_id'],x['control']) for x in ka.values()],[(x['slot_id'],x['control']) for x in list(kz.values())[::-1]])
            for c,key in ((a,ka),(z,kz)):
                self.assertLessEqual(c['items'],100)
                self.assertEqual(sum(x['control'] for x in key.values()),10)
                ids.extend(key)
                for x in key.values():
                    if not x['control']:counts[q.sid(x)]+=1
                rd=Path(c['directory'])
                self.assertFalse((rd/'answers.jsonl').exists())
                result=q.closure.scan(rd,key,write=False)
                self.assertTrue(result['ok'],result)
                self.assertNotIn(str(q.b.ROOT),str(rd))
        self.assertEqual(set(counts),slots)
        self.assertEqual(set(counts.values()),{2})
        self.assertEqual(len(set(ids)),len(ids))
        historical=set()
        for c in q.load(q.CQ/'contexts.json')+q.load(q.CQ/'reread_contexts.json'):
            historical.update(q.load(c['key'])['items'])
        self.assertFalse(historical.intersection(ids))
        prompt=(q.HERE/'prompts/cap1.md').read_text()
        self.assertEqual(prompt,(q.CQ/'prompts/cap1.md').read_text()+q.ADDENDUM)
        self.assertEqual(q.sha(q.HERE/'prompts/cap1.verbatim.md'),q.sha(q.CQ/'prompts/cap1.md'))
        self.assertEqual(sum(q.readable(x['initial']) and x['initial']!={'breathing':'none','accent':'none'} for x in prior),171)

    def test_two_readers_required_and_readable(self):
        ledger=self.fixtures()
        accepted,rejected=q.resolve(self.contexts,ledger)
        self.assertEqual((len(accepted),len(rejected)),(196,0))
        ledger[1]['status']='VOID'
        accepted,rejected=q.resolve(self.contexts,ledger)
        self.assertEqual((len(accepted),len(rejected)),(106,90))
        ledger=self.fixtures()
        target=next(i for i,x in q.load(self.contexts[1]['key'])['items'].items() if not x['control'])
        ledger[1]['answers'][target]=dict(breathing='rough',accent='none')
        self.assertEqual(len(q.resolve(self.contexts,ledger)[1]),1)
        ledger=self.fixtures(dict(breathing='unreadable',accent='none'))
        self.assertEqual(len(q.resolve(self.contexts,ledger)[0]),0)
        with self.assertRaises(AssertionError):q.resolve(self.contexts,ledger[:-1])
        with self.assertRaises(AssertionError):q.resolve(self.contexts,ledger+[ledger[0]])

    def test_incomplete_import_and_usage_stop_never_launch(self):
        with patch.object(q.subprocess,'run',side_effect=AssertionError('process launch forbidden')), patch.object(q.w,'probe',side_effect=AssertionError('probe forbidden')):
            with self.assertRaisesRegex(AssertionError,'incomplete'):q.import_reads()
        self.assertFalse((q.HERE/'import_receipt.json').exists())
        with patch.object(q.subprocess,'run',side_effect=AssertionError('reader forbidden')), patch.object(q.w,'probe',return_value=dict(weekly_used=78)):
            with self.assertRaisesRegex(AssertionError,'weekly usage'):q.run()
        self.assertEqual(q.load(q.HERE/'ledger.json'),[])

    def capture_aggregate(self, accepted=None, rejected=None):
        output={};real_exists=Path.exists;real_load=q.w.load
        import_path=q.CQ/'cq7/import_receipt.json'
        def exists(p):return p==import_path or real_exists(p)
        def load(p):return dict(accepted=len(accepted or {}),quarantined=len(rejected or [])) if p==import_path else real_load(p)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report=root/'docs/labelfix/spellcheck/R2/CQ4_REPORT.md'
            report.parent.mkdir(parents=True);report.write_text('Synthetic report\n')
            with patch.object(q.w,'ROOT',root), patch.object(q.w,'jsonl',side_effect=lambda p,v:output.update({str(p.relative_to(q.CQ)):v})), patch.object(q.w,'dump',side_effect=lambda p,v:output.update({str(p.relative_to(q.CQ)):v})), patch.object(q.w,'contact_sheet'), patch.object(q,'imported_answers',return_value=(accepted or {},rejected or [])), patch.object(Path,'exists',exists), patch.object(q.w,'load',side_effect=load), patch.object(q.subprocess,'run',side_effect=AssertionError('launch forbidden')), patch.object(q.w,'probe',side_effect=AssertionError('probe forbidden')):
                q.w.aggregate()
        return output

    def test_aggregate_integration_preserves_existing_truth_and_wcap(self):
        prior=q.rows(q.HERE/'prior_reads.jsonl');slot=q.sid(prior[0])
        allgood=dict(breathing='rough',accent='none')
        output=self.capture_aggregate({slot:allgood})
        top=output['truth/topup.jsonl']
        self.assertEqual(len(top),1010)
        self.assertEqual([x for x in top if q.sid(x)!=slot],q.rows(q.HERE/'baseline/truth/topup.jsonl'))
        new=next(x for x in top if q.sid(x)==slot)
        self.assertEqual(new['truth_tier'],'C_sol_two_independent_CQ7_agreed')
        self.assertEqual(output['truth/wcap.jsonl'],q.rows(q.HERE/'baseline/truth/wcap.jsonl'))
        self.assertEqual(len(output['quarantine/topup.jsonl']),195)
        reject=dict(slot_id=list(slot),reason='CQ7 disagreement',votes=dict(r1=allgood,r2=dict(breathing='none',accent='none')))
        output=self.capture_aggregate(rejected=[reject])
        self.assertEqual(output['truth/topup.jsonl'],q.rows(q.HERE/'baseline/truth/topup.jsonl'))
        self.assertIn(reject,output['quarantine/topup.jsonl'])

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CQ7))
    q.dump(q.HERE/'validation.json',dict(ok=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),reader_runs=0,usage_probes=0,network_used=False,scanner_sha256=q.SCANNER))
    raise SystemExit(0 if result.wasSuccessful() else 1)
