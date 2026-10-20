"""CQ4c eligibility, custody, selection, closure, and workflow regression tests."""
import collections as C,copy,hashlib,json,random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import build
from build import OUT,ROOT,PREP,SCANNER_SHA,PREREG_SHA,rows,load,sha,choose
from workflow import reread_trigger,overlay_rows,decode,controls_verified
from closure import scan

class CQ4cTests(unittest.TestCase):
 def test_hashes_and_scanner_regression(self):
  self.assertEqual(sha(OUT/'tools/scan_rollout.py'),SCANNER_SHA)
  self.assertEqual(sha(PREP/'docs/labelfix/spellcheck/R2/R2A2_PREREGISTRATION.md'),PREREG_SHA)
  for name in ('r1','r1b'):
   r=load(OUT/'regression'/f'cq1_{name}.scan_v44.json');self.assertEqual(r['scanner_sha256'],SCANNER_SHA);self.assertFalse(r['manifest_check_skipped']);self.assertEqual(r['ok'],name=='r1b')
   if name=='r1':self.assertTrue(any(x.get('record')==24 for x in r['violations']))
 def test_gate_and_caps_and_identity(self):
  for name,minimum,cap in [('wcap',210,30),('topup',844,120)]:
   data=rows(OUT/'keys'/f'{name}_selected.jsonl');self.assertGreaterEqual(len(data),minimum)
   self.assertEqual(len({tuple(x['slot_id']) for x in data}),len(data));self.assertLessEqual(max(C.Counter(x['doc'] for x in data).values()),cap);self.assertLessEqual(max(C.Counter(x['page'] for x in data).values()),5)
   for x in data:
    self.assertEqual(x['case_evidence']['case_class'],'capital');self.assertTrue(x['case_evidence']['recogniser_upper']);self.assertEqual(sha(Path(x['native_asset'])),x['slot_id'][0])
 def test_disjointness_and_correct_exclusions(self):
  w=rows(OUT/'keys/wcap_selected.jsonl');t=rows(OUT/'keys/topup_selected.jsonl');ex=load(OUT/'excluded_docs.json');old=load(OUT/'prior_cq4b/excluded_docs.json')['by_reason']
  wd={x['doc'] for x in w};td={x['doc'] for x in t}
  self.assertTrue(wd.isdisjoint(td));self.assertTrue(td.isdisjoint(ex['topup']['documents']));self.assertTrue(wd.isdisjoint(ex['wcap']['documents']))
  for reason in ('T4','validation','calibration','old_pool_heldout16','S8_DEV','print_truth','owner39','audit100','substitution60','CQ1'):self.assertTrue(td.isdisjoint(old[reason]))
  self.assertNotIn('T2',ex['by_reason']);self.assertNotIn('old_pool_316',ex['by_reason'])
  self.assertTrue(td & set(old['T2']),'training documents should be admitted')
 def test_wcap_roles_and_saved_teacher_location(self):
  roles=load(ROOT/'docs/labelfix/spellcheck/R2/doc_roles.json')['documents'];validation={build.alias(d) for d,r in roles.items() if r['role']=='validation'};unused=set(load(OUT/'prior_cq4/inventory.json')['wcap_candidate_documents'])
  data=rows(OUT/'keys/wcap_selected.jsonl');self.assertEqual({x['doc'] for x in data},validation|unused);self.assertEqual(len(validation),17)
  for x in data:
   if x['doc'] in validation:self.assertEqual(x['role'],'validation_reserve');self.assertTrue(x['teacher_export'].endswith('-validation_reserve.jsonl.gz'))
  self.assertEqual(load(OUT/'keys/intake.json')['unused_documents_dropped'],[])
 def test_manifest_and_t2_slot_exclusion(self):
  selected=rows(OUT/'keys/topup_selected.jsonl');ids={tuple(x['slot_id']) for x in selected};manifest={tuple(x['slot_id']) for x in rows(PREP/'artifacts/r2a_manifest/r2a_slots_v2.jsonl')};self.assertTrue(ids.isdisjoint(manifest))
  import unicodedata as U
  t2=set()
  for k in rows(ROOT/'docs/labelfix/spellcheck/R2/decks/T2/private/key.jsonl'):
   t2.update((k['crop_sha256'],k['crop_letter_offset']+i) for i in range(sum(U.category(c).startswith('L') for c in U.normalize('NFD',k['mining_key']))))
  self.assertTrue({(x['slot_id'][0],x['letter_index']) for x in selected}.isdisjoint(t2))
 def test_determinism_and_capping_fixture(self):
  pool=[dict(doc=str(d),page=f'{d}:{p}',line_id=f'{d}:{p}:{i}',slot_id=['a'*64,i],likely='marked' if i%2 else 'bare') for d in range(8) for p in range(3) for i in range(6)]
  with patch.object(build,'qualify',side_effect=lambda x:x):
   a,c=choose(pool,dict(marked=10,bare=10),4,2);b,cc=choose(list(reversed(pool)),dict(marked=10,bare=10),4,2)
  self.assertEqual(a,b);self.assertEqual(c,cc);self.assertEqual(len(a),20);self.assertLessEqual(max(C.Counter(x['page'] for x in a).values()),2)
 def test_reread_trigger(self):
  a=lambda b,c:dict(breathing=b,accent=c)
  for answer in [a('smooth','none'),a('rough','none'),a('unreadable','acute'),a('none','unreadable')]:self.assertTrue(reread_trigger(answer))
  for answer in [a('none','none'),a('smooth','acute'),a('rough','circumflex')]:self.assertFalse(reread_trigger(answer))
  self.assertFalse(reread_trigger(a('smooth','none'),True,False))
 def test_replace_not_append_and_ambiguous_stop(self):
  a=dict(slot_id=['a'*64,1],targets=[0,0,0,0]);b=dict(slot_id=['b'*64,2],targets=[1,0,0,0]);updated=a|dict(targets=[1,2,0,0])
  out=overlay_rows([a,b],[updated]);self.assertEqual(len(out),2);self.assertEqual(out[0]['targets'],[1,2,0,0]);self.assertEqual(out[1],b);self.assertEqual(out[0]['replaces'],a['slot_id'])
  self.assertEqual(overlay_rows([a,a,b],[]),[a,a,b])
  with self.assertRaisesRegex(ValueError,'ambiguous old identity'):overlay_rows([a,a,b],[updated])
  with self.assertRaises(ValueError):overlay_rows([a,b],[updated,updated])
 def test_every_context_closure_and_prompt(self):
  self.assertEqual((OUT/'prompts/cap1.md').read_bytes(),(ROOT/'artifacts/cq1/prompts/cap1.md').read_bytes())
  contexts=load(OUT/'contexts.json');seen=C.defaultdict(set)
  for c in contexts:
   key=load(c['key']);r=scan(Path(c['directory']),key['items'],write=False);self.assertTrue(r['ok'],r['violations']);self.assertLessEqual(r['items'],100)
   seen[c['set']].update(tuple(x['slot_id']) for x in key['items'].values() if not x['control'])
  for name in ('wcap','topup'):self.assertEqual(seen[name],{tuple(x['slot_id']) for x in rows(OUT/'keys'/f'{name}_selected.jsonl')})
 def test_closure_rejects_private_extra(self):
  import shutil
  c=load(OUT/'contexts.json')[0];key=load(c['key'])
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)/'r1';shutil.copytree(c['directory'],d);(d/'secret.json').write_text('{"truth":true}')
   r=scan(d,key['items'],write=False);self.assertFalse(r['ok']);self.assertTrue(any('unexpected file' in x for x in r['violations']))
 def test_controls_are_40_lowercase_reviewed(self):
  pool=load(OUT/'keys/control_pool.json');self.assertEqual(len(pool),40);self.assertEqual(len({x['source_id'] for x in pool}),40)
  resolved={x['card_id']:x for x in rows(ROOT/'artifacts/r2_resolve/T2/final/resolved.jsonl')}
  for x in pool:
   h=next(h for h in resolved[x['source_id']]['letter_heads'] if h['index']==0);self.assertIn(h['base'],'αεηιουω');self.assertNotEqual(x['expected'],dict(breathing='none',accent='none'))
  controls_verified()
  import workflow
  context=load(OUT/'contexts.json')[0];key=load(context['key']);bad=next(x for x in pool if not any(r['source_id']==x['source_id'] and r.get('verified') is True for r in load(OUT/'control_review/lead_review.json')['items']))
  modified=copy.deepcopy(key);ident=next(i for i,x in modified['items'].items() if x['control']);modified['items'][ident]=bad|dict(public=modified['items'][ident]['public'])
  original_load=workflow.load
  with patch.object(workflow,'load',side_effect=lambda p: modified if str(p)==context['key'] else original_load(p)):
   with self.assertRaisesRegex(AssertionError,'every placed control'):controls_verified([context])
  with patch.object(workflow,'load',side_effect=lambda p: load(p)|dict(status='pending') if str(p).endswith('lead_review.json') else load(p)):
   with self.assertRaisesRegex(AssertionError,'lead must'):controls_verified([])
 def test_decode_rejects_missing_or_bad_control(self):
  c=load(OUT/'contexts.json')[0];key=load(c['key']);answers=[]
  for i,x in key['items'].items():
   pub=x['public'];exp=x.get('expected',dict(breathing='none',accent='none'))
   answers.append(dict(item_id=i,breathing=next(k for k,v in pub['breathing_options'].items() if v==exp['breathing']),accent=next(k for k,v in pub['accent_options'].items() if v==exp['accent']),confidence='high',note=''))
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);build.jsonl(d/'answers.jsonl',answers);cc=c|dict(directory=str(d));decoded,errors=decode(cc);self.assertEqual(errors,0)
   build.jsonl(d/'answers.jsonl',answers[:-1])
   with self.assertRaises(AssertionError):decode(cc)
   bad=copy.deepcopy(answers)
   for a in bad:
    if key['items'][a['item_id']]['control']:a['breathing']='Z';break
   build.jsonl(d/'answers.jsonl',bad)
   with self.assertRaises(AssertionError):decode(cc)
 def test_aggregate_quarantines_disagreement_and_void(self):
  import workflow
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'artifacts/cq4';root=Path(tmp);out.mkdir(parents=True);report=root/'docs/labelfix/spellcheck/R2/CQ4_REPORT.md';report.parent.mkdir(parents=True);report.write_text('Build fixture\n')
   xs=[dict(slot_id=[str(i)*64,i],line_id=str(i),doc='d',source='s',role='train',control=False) for i in range(1,6)]
   build.jsonl(out/'keys/topup_selected.jsonl',xs);build.jsonl(out/'keys/wcap_selected.jsonl',[])
   answers=[dict(breathing='smooth',accent='none'),dict(breathing='rough',accent='none'),dict(breathing='unreadable',accent='none'),dict(breathing='none',accent='none')]
   contexts=[dict(tag='initial',set='topup',key=str(out/'keys/initial.json')),dict(tag='void',set='topup',key=str(out/'keys/void.json'))]
   build.dump(out/'keys/initial.json',dict(items={str(i):x for i,x in enumerate(xs[:4])}));build.dump(out/'keys/void.json',dict(items={'void':xs[4]}));build.dump(out/'contexts.json',contexts)
   build.dump(out/'initial_ledger.json',[dict(tag='initial',status='VALID',scanner_sha256=SCANNER_SHA,answers={str(i):a for i,a in enumerate(answers)},before={'weekly_used':1},after={'weekly_used':1}),dict(tag='void',status='VOID',scanner_sha256=SCANNER_SHA,before={'weekly_used':1},after={'weekly_used':1})])
   build.dump(out/'keys/second.json',dict(items={str(i):x for i,x in enumerate(xs[:3])}));build.dump(out/'reread_contexts.json',[dict(tag='second',set='topup',key=str(out/'keys/second.json'))])
   again=[answers[0],dict(breathing='none',accent='none'),answers[2]]
   build.dump(out/'reread_ledger.json',[dict(tag='second',status='VALID',scanner_sha256=SCANNER_SHA,answers={str(i):a for i,a in enumerate(again)},before={'weekly_used':1},after={'weekly_used':1})])
   with patch.object(workflow,'OUT',out),patch.object(workflow,'ROOT',root),patch.object(workflow,'frozen_verified'),patch.object(workflow,'contact_sheet'):
    workflow.aggregate()
   truth=rows(out/'truth/topup.jsonl');q=rows(out/'quarantine/topup.jsonl');queue=rows(out/'lead_queue.jsonl')
   self.assertEqual(len(truth),2);self.assertEqual(len(q),3);self.assertEqual(len(queue),3);self.assertTrue(all(x['truth_tier']=='C_sol_one_reader_reread' for x in truth));self.assertEqual({x['reason'] for x in queue},{'reread disagreement','agreed unreadable','VOID/missing initial context'})
 def test_void_context_continues_and_budget_refuses(self):
  import workflow,scan_rollout
  from types import SimpleNamespace
  contexts=load(OUT/'contexts.json')[:2]
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);build.dump(out/'contexts.json',contexts)
   with patch.object(workflow,'OUT',out),patch.object(workflow,'frozen_verified'),patch.object(workflow,'probe',return_value={'weekly_used':10}),patch.object(workflow.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{"rollout":"fixture"}\n',stderr='')),patch.object(scan_rollout,'inspect',side_effect=[dict(ok=False),dict(ok=True)]),patch.object(workflow,'decode',return_value=({},0)):
    workflow.run_all('initial')
   self.assertEqual([r['status'] for r in load(out/'initial_ledger.json')],['VOID','VALID'])
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);build.dump(out/'contexts.json',contexts)
   with patch.object(workflow,'OUT',out),patch.object(workflow,'frozen_verified'),patch.object(workflow,'probe',return_value={'weekly_used':78}),patch.object(workflow.subprocess,'run') as run:
    with self.assertRaisesRegex(RuntimeError,'>=78%'):workflow.run_all('initial')
    run.assert_not_called()
if __name__=='__main__':unittest.main()
