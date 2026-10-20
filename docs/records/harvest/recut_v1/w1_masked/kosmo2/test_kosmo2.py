"""Offline mechanical qualification; no readers, probes, or scoring."""
import sys
sys.dont_write_bytecode=True
import unittest,json,random,re,subprocess,shutil,tempfile,os,io
from pathlib import Path
import xml.etree.ElementTree as ET
import build as b
import reference_adapter as a

class KR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key=json.loads((b.HERE/'keys/kosmo2.json').read_text())
        cls.original=b.rows(b.SOURCE/'cards.jsonl')
        cls.controls=json.loads((b.HERE/'keys/control_truth.json').read_text())

    def test_01_exact_t6g_card_set(self):
        sourcekey=json.loads((b.HERE.parent/'cards_kosmo_poly1850_key.json').read_text())
        bed=[m for m in self.key['items'].values() if not m['control']]
        self.assertEqual(len(bed),100)
        self.assertEqual({m['line_id'] for m in bed},{sourcekey[c['card_id']]['line_id'] for c in self.original})
        self.assertEqual({m['source_public_id'] for m in bed},{c['card_id'] for c in self.original})

    def test_02_t6g_bytes_labels_scripts(self):
        original={c['card_id']:c for c in self.original}
        for context,ids in self.key['readers'].items():
            for card in b.rows(b.BED/context/'cards.jsonl'):
                m=self.key['items'][card['card_id']]
                if m['control']:continue
                src=original[m['source_public_id']]
                self.assertEqual((b.SOURCE/src['crop']).read_bytes(),(b.BED/context/card['crop']).read_bytes())
                for field in ('google_text','word_scripts'):self.assertEqual(src[field],card[field])

    def test_03_control_truth_identity(self):
        self.assertEqual((b.HERE/'keys/control_truth.json').read_bytes(),(b.HERE.parent/'caps1/keys/control_truth.json').read_bytes())
        self.assertEqual({c['source_card']['card_id'] for c in self.controls},{'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'})
        for c in self.controls:
            m=next(m for m in self.key['items'].values() if m['line_id']==c['line_id'])
            self.assertTrue(m['control']);self.assertEqual(m['reference_verdict'],c['reference_verdict'])
            self.assertEqual(m['expected'],{k:c['reference_verdict'][k] for k in ('letters','crop_ok')})

    def test_04_controls_and_disjoint_contexts(self):
        self.assertFalse(set(self.key['readers']['c1'])&set(self.key['readers']['c2']))
        for context,ids in self.key['readers'].items():
            meta=[self.key['items'][i] for i in ids]
            self.assertEqual(len(meta),55);self.assertEqual(sum(m['control'] for m in meta),5)
            self.assertEqual({m['line_id'] for m in meta if m['control']},{c['line_id'] for c in self.controls if c['context']==context})
            self.assertTrue(all(m['source']==('bsb_poly1850' if m['control'] else 'kosmopolis') for m in meta))
        self.assertEqual(a.private_contract(b.BED/'c1'),[])

    def test_05_seed_reproducible(self):
        selected=b.draw(self.original)
        self.assertEqual([c['card_id'] for c in selected],[r['source_public_id'] for r in b.rows(b.HERE/'keys/draw.jsonl')])
        self.assertEqual(b.SEED,'kr1:kosmo:poly1850')
        for n,context in enumerate(('c1','c2')):
            expected=[c['card_id'] for c in selected[n*50:(n+1)*50]]+[c['source_card']['card_id'] for c in self.controls if c['context']==context]
            random.Random(b.order_seed(context)).shuffle(expected)
            self.assertEqual(expected,[self.key['items'][i]['source_public_id'] for i in self.key['readers'][context]])

    def test_06_new_order_and_fresh_ids(self):
        prior=json.loads((b.HERE.parent/'cards_kosmo_poly1850_sol_key.json').read_text())
        self.assertNotEqual([c['card_id'] for c in b.draw(self.original)],prior['reordered_source_ids'])
        used=set(prior['items'])
        for bed in ('caps1','caps3'):used.update(json.loads((b.HERE.parent/bed/'keys'/f'{bed}.json').read_text())['items'])
        self.assertFalse(used&set(self.key['items']))
        self.assertTrue(all(re.fullmatch('k[0-9a-f]{10}',i) for i in self.key['items']))

    def test_07_closure(self):
        results=[a.closure(b.BED/c,compatible=True) for c in ('c1','c2')]
        b.dump(b.HERE/'scan/closure.json',results)
        self.assertTrue(all(r['ok'] for r in results),results)
        self.assertFalse(b.PACK_ROOT.resolve() in b.HERE.resolve().parents)

    def test_08_closure_rejects_contamination(self):
        scanner=a.load_reference('scan_packs',a.CLOSURE_SUBSTITUTIONS)
        mutations=('private_field','source_id','nonopaque','truth_file','key_file','extra_file','path_escape','symlink','hardlink','tamper')
        for mutation in mutations:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory(prefix='kr1-') as temp:
                folder=Path(temp)/'c1';shutil.copytree(b.BED/'c1',folder)
                cards=b.rows(folder/'cards.jsonl');image=folder/cards[0]['crop']
                if mutation=='private_field':cards[0]['truth']='y'
                elif mutation=='source_id':cards[0]['google_text']=next(iter(self.key['items'].values()))['line_id']
                elif mutation=='nonopaque':cards[0]['card_id']='c001'
                elif mutation in ('truth_file','key_file','extra_file'):(folder/({'truth_file':'truth.json','key_file':'key.json','extra_file':'notes.txt'}[mutation])).write_text('{}')
                elif mutation=='path_escape':cards[0]['crop']='../elsewhere.png'
                elif mutation=='symlink':image.unlink();image.symlink_to(b.BED/'c1'/cards[0]['crop'])
                elif mutation=='hardlink':image.unlink();os.link(b.BED/'c1'/cards[0]['crop'],image)
                elif mutation=='tamper':image.write_bytes(b'broken')
                b.jsonl(folder/'cards.jsonl',cards)
                self.assertFalse(scanner.scan(folder,'kosmo2',write_manifest=False)['ok'])

    def test_09_custody_hash_names_no_metadata(self):
        from PIL import Image
        for row in json.loads((b.HERE/'keys/crop_custody.json').read_text()):
            source=Path(row['source']);dest=Path(row['destination'])
            self.assertEqual(b.sha(source),row['sha256']);self.assertEqual(b.sha(dest),row['sha256'])
            self.assertEqual(dest.stem,row['sha256']);self.assertFalse(dest.is_symlink());self.assertEqual(dest.stat().st_nlink,1)
            self.assertFalse(os.path.samefile(source,dest))
            with Image.open(dest) as im:self.assertEqual(im.mode,'L');self.assertFalse(im.info)

    def test_10_verbatim_prompt_and_launchers(self):
        prompt=(b.HERE/'prompts/kosmo2.md').read_bytes()
        self.assertEqual(prompt,(b.REFERENCE/'prompts/bsb.md').read_bytes())
        self.assertNotIn(b'{{READER2_CLAUSE}}',prompt)
        read=(b.HERE/'launchers/run_read.sh').read_text()
        for flag in ('MODEL=gpt-6.1-sol','sandbox_workspace_write.network_access=false','web_search="disabled"','features.multi_agent=false','features.apps=false','features.remote_plugin=false','project_doc_max_bytes=0','approval_policy=never'):
            self.assertIn(flag,read)
        self.assertIn('"$P" medium',(b.HERE/'launchers/run_bed.sh').read_text())
        for name in ('run_read.sh','run_bed.sh','limit_probe.sh'):
            subprocess.run(['bash','-n',str(b.HERE/'launchers'/name)],check=True)
        subprocess.run(['bash','-n',str(b.PACK_ROOT/'launchers/run_bed.sh')],check=True)
        self.assertIn('= kosmo2 ]; then exec bash '+str(b.HERE/'launchers/run_bed.sh'),(b.PACK_ROOT/'launchers/run_bed.sh').read_text())
        self.assertEqual(len((b.HERE/'launch_lines.txt').read_text().splitlines()),2)

    def test_11_source_bindings_and_v4_routing(self):
        receipt=json.loads((b.HERE/'build_receipt.json').read_text())
        inputs=receipt['inputs']|json.loads((b.HERE/'runtime_bindings.json').read_text())['reference_sources']
        for path,digest in inputs.items():self.assertEqual(b.sha(path),digest,path)
        scanner=a.rollout_scanner()
        self.assertIn('audit v4',scanner.__doc__)
        self.assertTrue(callable(scanner.main))
        self.assertEqual(receipt['readers_started'],0);self.assertEqual(receipt['crops_regenerated'],0)
        self.assertEqual(receipt['prior_run']['label'],'pre-handover, no controls')

    def test_12_adapter_policy_diff(self):
        original=(b.HERE.parent/'caps1/reference_adapter.py').read_text().replace('caps1','kosmo2').replace('CAPS1','KOSMO2')
        original=original.replace("if any(m['primary_class'] == 'headings_caps' for m in c):", "if any(m['source'] != 'bsb_poly1850' or m['primary_class'] != 'poly1850' for m in c):")
        original=original.replace("if any(m['primary_class'] != 'headings_caps' for m in b):", "if any(m['source'] != 'kosmopolis' or m['primary_class'] != 'poly1850' for m in b):")
        self.assertEqual(original,(b.HERE/'reference_adapter.py').read_text())
        self.assertEqual(len(a.CLOSURE_SUBSTITUTIONS),2)

if __name__=='__main__':
    b.io_guard();stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(KR1Tests))
    (b.HERE/'tests.log').write_text(stream.getvalue())
    ET.ElementTree(ET.Element('testsuite',tests=str(result.testsRun),failures=str(len(result.failures)),errors=str(len(result.errors)),skipped=str(len(result.skipped)))).write(b.HERE/'tests.xml',encoding='unicode')
    print(stream.getvalue(),end='');raise SystemExit(0 if result.wasSuccessful() else 1)
