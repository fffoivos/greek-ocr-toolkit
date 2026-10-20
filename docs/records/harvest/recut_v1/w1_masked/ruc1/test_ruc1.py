"""Offline RUC1 qualification; synthetic answers never constitute reader results."""
import sys
sys.dont_write_bytecode=True
import unittest,json,random,shutil,tempfile,os,re
from pathlib import Path
import build as b
import reference_adapter as a
class RUC1Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pool,cls.rep,cls.classes,cls.c1,cls.bindings=b.inputs()
  cls.key=json.loads((b.HERE/'keys/ruc1.json').read_text())
  cls.cards={c:b.rows(b.BED/c/'cards.jsonl') for c in ('c1','c2')}
 def test_01_ru1_sha_and_all_parent_labels(self):
  self.assertEqual(b.sha(b.RU1),b.EXPECTED);self.assertEqual(len(self.rep),314)
  self.assertEqual(sum(r['status']=='hold' for r in self.rep.values()),3)
 def test_02_pool_and_exclusions(self):
  saved=b.rows(b.HERE/'keys/pool.jsonl');self.assertEqual([r['id'] for r in saved],[r['id'] for r in self.pool])
  ids={r['id'] for r in self.pool};self.assertFalse(ids&self.c1)
  for excluded in self.classes.values():self.assertFalse(ids&excluded)
  self.assertFalse(ids&{rid for rid,r in self.rep.items() if r['status']=='hold'})
  for r in self.pool:self.assertEqual((r['source'],r['primary_class'],r['candidate_usable']),('ia_russian','cyrillic',True))
 def test_03_exact_label_substitution(self):
  pool={r['id']:r for r in self.pool}
  for c,cards in self.cards.items():
   for card in cards:
    m=self.key['items'][card['card_id']]
    if m['control']:continue
    r=pool[m['line_id']];repair=self.rep.get(r['id'])
    expected=repair['label_ru1_v1'] if repair and repair['status']=='ok' else r['label']
    self.assertEqual(card['google_text'],expected);self.assertEqual(card['word_scripts'],b.word_scripts(expected));self.assertEqual(m['label_repaired'],expected!=r['label'])
  for r in b.rows(b.HERE/'keys/pool.jsonl'):
   repair=self.rep.get(r['id']);self.assertEqual(r['label_used'],repair['label_ru1_v1'] if repair and repair['status']=='ok' else r['label_parent'])
 def test_04_seed_and_order(self):
  self.assertEqual(b.SEED,'ruc1:ia_russian:cyrillic');draw=random.Random(b.SEED).sample(sorted(self.pool,key=lambda r:r['id']),100)
  self.assertEqual([r['id'] for r in draw],[r['id'] for r in b.rows(b.HERE/'keys/draw.jsonl')])
  controls=json.loads((b.HERE/'keys/control_truth.json').read_text())
  for n,c in enumerate(('c1','c2')):
   expected=[r['id'] for r in draw[n*50:(n+1)*50]]+[r['line_id'] for r in controls if r['context']==c];random.Random(b.order_seed(c)).shuffle(expected)
   self.assertEqual(expected,[self.key['items'][x['card_id']]['line_id'] for x in self.cards[c]])
 def test_05_crop_sha_and_native_custody(self):
  from PIL import Image
  custody=json.loads((b.HERE/'keys/crop_custody.json').read_text());self.assertEqual(len(custody),110)
  for r in custody:
   src=Path(r['source']);dst=Path(r['destination']);self.assertEqual(b.sha(src),r['sha256']);self.assertEqual(b.sha(dst),r['sha256']);self.assertEqual(dst.stem,r['sha256']);self.assertEqual(dst.stat().st_nlink,1);self.assertFalse(dst.is_symlink());self.assertFalse(os.path.samefile(src,dst))
   with Image.open(dst) as im:self.assertEqual(im.mode,'L');self.assertFalse(im.info)
  receipt=json.loads((b.HERE/'build_receipt.json').read_text());self.assertEqual(receipt['crops_regenerated'],100);self.assertEqual(receipt['invoked_interpreter'],str(b.PYTHON))
 def test_06_controls_and_contexts(self):
  self.assertEqual((b.HERE/'keys/control_truth.json').read_bytes(),(b.HERE.parent/'caps1/keys/control_truth.json').read_bytes())
  self.assertEqual(a.private_contract(b.BED/'c1'),[])
  old=json.loads((b.HERE.parent/'caps1/keys/caps1.json').read_text())
  for c,cards in self.cards.items():
   for card in cards:
    m=self.key['items'][card['card_id']]
    if m['control']:
     prior=next(x for x in old['items'].values() if x['line_id']==m['line_id']);self.assertEqual(m,prior)
 def test_07_closure(self):
  results=[a.closure(b.BED/c,compatible=True) for c in ('c1','c2')];b.dump(b.HERE/'scan/closure.json',results);self.assertTrue(all(r['ok'] for r in results),results)
 def test_08_closure_rejects_contamination(self):
  scanner=a.load_reference('scan_packs',a.CLOSURE_SUBSTITUTIONS)
  for mutation in ('truth','extra_file','escape','nonopaque','symlink','hardlink','tamper'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory(prefix='ruc1-test-') as temp:
    folder=Path(temp)/'c1';shutil.copytree(b.BED/'c1',folder);cards=b.rows(folder/'cards.jsonl');im=folder/cards[0]['crop']
    if mutation=='truth':cards[0]['truth']='y'
    elif mutation=='extra_file':(folder/'notes.txt').write_text('{}')
    elif mutation=='escape':cards[0]['crop']='../else.png'
    elif mutation=='nonopaque':cards[0]['card_id']='c001'
    elif mutation=='symlink':im.unlink();im.symlink_to(b.BED/'c1'/cards[0]['crop'])
    elif mutation=='hardlink':im.unlink();os.link(b.BED/'c1'/cards[0]['crop'],im)
    elif mutation=='tamper':im.write_bytes(b'broken')
    b.jsonl(folder/'cards.jsonl',cards);self.assertFalse(scanner.scan(folder,'ruc1',write_manifest=False)['ok'])
 def test_09_prompt_and_launcher_settings(self):
  self.assertEqual((b.HERE/'prompts/ruc1.md').read_bytes(),(b.REFERENCE/'prompts/bsb.md').read_bytes())
  run=(b.HERE/'launchers/run_read.sh').read_text()
  for s in ('gpt-6.1-sol','network_access=false','web_search','features.multi_agent=false','features.apps=false','features.remote_plugin=false','project_doc_max_bytes=0','approval_policy'):
   self.assertIn(s,run)
  self.assertIn('medium',(b.HERE/'launchers/run_bed.sh').read_text());self.assertIn('ruc1',(b.PACK_ROOT/'launchers/run_bed.sh').read_text())
 def test_10_fresh_ids_and_bindings(self):
  for iid in self.key['items']:self.assertRegex(iid,r'^k[0-9a-f]{10}$')
  others={r['card_id'] for p in b.PACK_ROOT.glob('*/*/cards.jsonl') if 'ruc1' not in p.parts for r in b.rows(p)};self.assertFalse(others&set(self.key['items']))
  receipt=json.loads((b.HERE/'build_receipt.json').read_text())
  for p,h in receipt['inputs'].items():self.assertEqual(b.sha(p),h)
 def test_11_mapper_controls_and_marks(self):
  mapper=a.load_reference('map_answers')
  for c,cards in self.cards.items():
   answers=[dict(card_id=x['card_id'],letters=self.key['items'][x['card_id']].get('expected',{}).get('letters','y'),crop_ok=self.key['items'][x['card_id']].get('expected',{}).get('crop_ok','y'),marks='n',errors=[],detail='') for x in cards]
   mapped,controls=mapper.map_records('bsb',c,answers,self.key,cards);self.assertEqual(len(mapped),50);self.assertEqual(controls['control_errors'],0)
if __name__=='__main__':unittest.main(verbosity=2)
