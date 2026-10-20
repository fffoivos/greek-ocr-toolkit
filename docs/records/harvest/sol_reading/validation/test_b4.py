"""B4 artifact invariants: accounting, cohort identity, and scoring reconciliation."""
import json,re,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import ROOT,PACK_ROOT,FIELDS,rows,itemfile
from summary_b4 import changes
from map_answers import map_records

class FinalArtifacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((ROOT/'results/SUMMARY.json').read_text())
  cls.r=json.loads((ROOT/'results/results.json').read_text())
  cls.ledger=json.loads((ROOT/'usage_ledger.json').read_text())
 def test_r3_provenance_and_mapping_complete(self):
  for a in self.s['r3_scans']:
   b=a['bed'];scan=json.loads((ROOT/f'answers/{b}/r3.scan.json').read_text())
   self.assertEqual((scan['scanner_version'],scan['ok'],scan['violations']),(3,True,[]))
   self.assertGreater(scan['returned_images'],0)
   mapped,controls=map_records(b,'r3',rows(ROOT/f'answers/{b}/r3.jsonl'),json.loads((ROOT/f'keys/{b}_r3.json').read_text()),rows(PACK_ROOT/b/'r3'/itemfile(b)))
   self.assertEqual(mapped,rows(ROOT/f'answers/{b}/r3.mapped.jsonl'))
   self.assertEqual(controls,json.loads((ROOT/f'answers/{b}/r3.controls.json').read_text()))
 def test_resolution_and_accuracy_reconcile(self):
  for e in self.s['S1_to_S2']:
   d=self.r['beds'][e['bed']]['readers'];m=e['metric']
   a=d[e['S1']]['accuracy'][m];b=d['Sol S2']['accuracy'][m]
   self.assertEqual((a['n'],b['n']),(e['n'],e['n']))
   self.assertEqual(b['correct']-a['correct'],e['net_correct'])
   self.assertEqual(e['changed'],sum(e[f] for f in ('changed_to_correct','changed_to_wrong','changed_between_wrong')))
   receipt=json.loads((ROOT/f"answers/{e['bed']}/S2.unresolved.json").read_text())
   self.assertEqual(receipt['used_readers'],['r1','r2','r3'])
   if m in ('joint','item','joint_anchor'):self.assertEqual(e['unresolved'],receipt['unresolved_units'])
 def test_owner_pool_preserves_card_read_multiplicity(self):
  group=[r for r in self.s['accuracy'] if r['bed']=='owner39' and r['scope']=='partial pooled card-reads']
  refs=[r for n,r in self.r['beds']['owner39']['readers'].items() if n.startswith('Opus ')]
  self.assertEqual(sum(r['answered_items'] for r in refs),33)
  self.assertLess(len(set().union(*(set(r['raw']) for r in refs))),33)
  self.assertEqual(len(group),4)
  for r in group:self.assertEqual(r['metrics']['joint_anchor']['n'],33)
  p=next(r for r in group if r['reader']=='Opus partial pooled')
  for metric,m in p['metrics'].items():
   self.assertEqual(m['correct'],sum(r['accuracy'][metric]['correct'] for r in refs))
   self.assertEqual(m['n'],sum(r['accuracy'][metric]['n'] for r in refs))
 def test_variance_accuracy_uses_common_denominator(self):
  for r in self.s['variance']:
   self.assertLessEqual(r['agree'],r['n'])
   self.assertAlmostEqual(r['absolute_accuracy_difference'],abs(r['left_correct']-r['right_correct'])/r['n'])
  v=[r for r in self.s['variance'] if r['bed']=='owner39' and r['left'].startswith('Opus')]
  self.assertTrue(v);self.assertEqual({r['n'] for r in v},{8})
 def test_costs_against_ledger_and_zero_denominators(self):
  for r in self.s['Sol_cost_per_run']+self.s['Sol_cost_per_arm']:
   source=[e for e in self.ledger if e['bed']==r['bed'] and e['reader'] in r['runs']]
   self.assertEqual(r['wall_seconds'],sum(e['wall_seconds'] for e in source))
   self.assertEqual(r['tool_calls'],sum(e['total_tool_calls'] for e in source))
   for f in ('input','cached_input','output','reasoning','total'):
    self.assertEqual(r['tokens'][f],sum(e['tokens'][f] for e in source))
    self.assertAlmostEqual(r['tokens_per_item'][f]*r['denominator_items'],r['tokens'][f])
   self.assertEqual(r['tokens']['input']-r['tokens']['cached_input'],r['tokens']['uncached_input'])
   self.assertEqual(r['tokens']['input']+r['tokens']['output'],r['tokens']['total'])
   self.assertIsNone(r['credits_spent'])
  for ratio in self.s['cost_ratios']:
   arms={r['arm']:r for r in self.s['Sol_cost_per_arm'] if r['bed']==ratio['bed']}
   self.assertAlmostEqual(ratio['tokens']['total'],arms['S2']['tokens']['total']/arms[ratio['baseline']]['tokens']['total'])
   self.assertIsNone(ratio['weekly_delta']);self.assertIsNone(ratio['credits_spent'])
 def test_experiment_and_build_receipts(self):
  w=self.s['whole_experiment'];r=w['Sol_reading']
  self.assertEqual(r['runs'],9)
  self.assertEqual(r['tokens']['total'],sum(e['tokens']['total'] for e in self.ledger))
  self.assertEqual(r['weekly_percent_first'],min(self.ledger,key=lambda e:e['limit_probe_before'])['weekly_used_before'])
  self.assertEqual(r['weekly_percent_last'],max(self.ledger,key=lambda e:e['limit_probe_after'])['weekly_used_after'])
  for b in w['build_brief_runs']:
   self.assertIn('session id: '+b['session_id'],Path(b['launcher_log']).read_text())
   self.assertIn(b['session_id'],b['rollout'])
   events=rows(Path(b['rollout']))
   e=next(e for e in events if e.get('timestamp')==b['usage_timestamp_utc'] and e.get('payload',{}).get('type')=='token_count')
   self.assertEqual(b['tokens']['total'],e['payload']['info']['total_token_usage']['total_tokens'])
   self.assertTrue(b['status']=='completed' or 'lower-bound snapshot' in b['status'])
  self.assertEqual(w['completed_build_tokens']['total'],sum(b['tokens']['total'] for b in w['build_brief_runs'] if b['status']=='completed'))
 def test_summary_tables_only_and_separate_meters(self):
  text=(ROOT/'results/SUMMARY.md').read_text()
  self.assertTrue(all(not line or line.startswith('|') for line in text.splitlines()))
  self.assertIn('Sol bed',text);self.assertIn('Opus bed',text)
  self.assertEqual(len(self.s['Opus_cost_per_run']),14)
  self.assertEqual(sum(r['items'] for r in self.s['Opus_cost_per_run'] if r['partial']),33)

if __name__=='__main__':unittest.main()
