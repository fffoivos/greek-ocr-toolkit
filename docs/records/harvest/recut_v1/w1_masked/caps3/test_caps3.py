"""Offline CAPS3 qualification, including full screen replay and actual T6b re-mask."""
import sys
sys.dont_write_bytecode=True
import unittest
import json
import random
import subprocess
import io
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import build as b
import pipeline as p
import reference_adapter as adapter

class Caps3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool=b.rows(b.HERE/'keys/pool.jsonl')
        cls.screen=b.rows(b.HERE/'screen.jsonl')
        cls.records=b.rows(b.OUT/'records.jsonl')
        cls.key=json.loads((b.HERE/'keys/caps3.json').read_text())

    def test_01_screen_reproducibility_all_2211(self):
        self.assertEqual(len(self.pool),2211)
        self.assertEqual([r['id'] for r in self.pool],[r['id'] for r in b.rows(b.HERE.parent/'caps1/keys/pool.jsonl')])
        self.assertTrue(all(r['primary_class']=='headings_caps' and r['candidate_usable'] is True for r in self.pool))
        measured=[]
        for i,r in enumerate(self.pool):
            measured.append(dict(id=r['id'],source=r['source'],crop_sha256=r['crop_sha256'],**p.clip_measure(p.original(r))))
            if (i+1)%400==0:print('screen replay',i+1,flush=True)
        self.assertEqual(measured,self.screen)

    def test_02_existing_horizontal_tolerance(self):
        sys.path.insert(0,str(b.REPO))
        from greekocr.verify.calibration import RULES
        self.assertEqual(RULES['cut_left'],('left_fraction','gt',0.0))
        self.assertEqual(RULES['cut_right'],('right_fraction','gt',0.0))
        for r in self.screen:self.assertEqual(r['flagged'],any(r['sides'].values()))

    def test_03_caps2_report(self):
        receipt=json.loads((b.HERE/'screen_receipt.json').read_text())
        checks=receipt['caps2_validation']
        self.assertEqual(len(checks),100)
        self.assertEqual(sum(r['flagged'] for r in checks if 'crop_clipped' in r['verdict']['errors']),receipt['clipped_flagged'])
        self.assertEqual(sum(r['flagged'] for r in checks if r['verdict']['crop_ok']=='y'),receipt['fp'])
        self.assertEqual(sum(r['verdict']['crop_ok']=='y' for r in checks),89)

    def test_04_screen_to_mask_population(self):
        kept={r['id'] for r in self.screen if not r['flagged']}
        self.assertEqual({r['id'] for r in self.records},kept)
        self.assertEqual(len(self.records),len(kept))

    def test_05_three_t6b_rows_remask_byte_identical(self):
        with (b.HERE/'parity.log').open('w') as log:
            subprocess.run([sys.executable,'-B',str(b.HERE/'pipeline.py'),'parity'],check=True,stdout=log,stderr=subprocess.STDOUT)
        receipt=json.loads((b.OUT/'parity/receipt.json').read_text())
        b.dump(b.HERE/'remask_receipt.json',receipt)
        self.assertEqual(len(receipt),3)
        self.assertTrue(all(r['byte_identical'] and r['changed'] for r in receipt))

    def test_06_frozen_mask_guard_and_output_custody(self):
        t6b=p.load('caps3_test_t6b',b.HERE.parent/'run.py')
        binding=t6b.frozen()
        pilot=p.load('caps3_t6c2_matcher',b.HERE.parent.parent/'v2_pilot/run.py')
        self.assertEqual(t6b.PROBE.resolve(),pilot.PROBE.resolve())
        self.assertEqual(binding['params_sha256'],'801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8')
        artifact=json.loads((b.OUT/'artifact_receipt.json').read_text())
        self.assertEqual(artifact['records_sha256'],b.sha(b.OUT/'records.jsonl'))
        for f in artifact['files']:self.assertEqual(b.sha(b.OUT/f['path']),f['sha256'])
        for r in self.records:
            self.assertEqual(r['params_sha256'],binding['params_sha256'])
            self.assertEqual(r['library_sha256'],binding['library_sha256'])
            self.assertEqual(b.sha(b.OUT/r['masked_crop']),r['masked_crop_sha256'])
            self.assertEqual(r['wrong_line_risk'],r['own_ink_masked_fraction']>.30)
            self.assertEqual(r['matched'],r['runtime_index'] is not None)
            if r['wrong_line_risk'] or not r['matched']:
                self.assertEqual(r['masked_crop_sha256'],r['original_crop_sha256'])
                self.assertFalse(r['changed'])

    def test_07_seed_and_no_caps1_cards(self):
        eligible=b.rows(b.HERE/'keys/eligible.jsonl')
        old={r['id'] for r in b.rows(b.HERE.parent/'caps1/keys/draw.jsonl')}
        expected=[r for r in self.records if r['matched'] and r['id'] not in old]
        self.assertEqual(eligible,expected)
        selected=b.rows(b.HERE/'keys/draw.jsonl')
        self.assertEqual(selected,b.draw(eligible))
        self.assertFalse(old & {r['id'] for r in selected})
        self.assertEqual(len(selected),100)

    def test_08_control_truth_and_placement(self):
        prior=json.loads((b.HERE.parent/'caps1/keys/control_truth.json').read_text())
        self.assertEqual(json.loads((b.HERE/'keys/control_truth.json').read_text()),prior)
        old=json.loads((b.HERE.parent/'caps1/keys/caps1.json').read_text())
        controls=[m for m in self.key['items'].values() if m['control']]
        self.assertEqual({m['source_public_id'] for m in controls},{'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'})
        self.assertFalse(set(self.key['items']) & set(old['items']))
        for context in ('c1','c2'):
            ids=self.key['readers'][context]
            self.assertEqual(sum(self.key['items'][i]['control'] for i in ids),5)
            for c in (c for c in prior if c['context']==context):
                current=next(m for m in controls if m['line_id']==c['line_id'])
                self.assertEqual(current['reference_verdict'],c['reference_verdict'])
                self.assertEqual(current['expected'],{k:c['reference_verdict'][k] for k in ('letters','crop_ok')})

    def test_09_context_order(self):
        selected=b.rows(b.HERE/'keys/draw.jsonl')
        controls=json.loads((b.HERE/'keys/control_truth.json').read_text())
        for n,c in enumerate(('c1','c2')):
            ids=[r['id'] for r in selected[n*50:(n+1)*50]]+[r['line_id'] for r in controls if r['context']==c]
            random.Random(b.order_seed(c)).shuffle(ids)
            self.assertEqual([self.key['items'][i]['line_id'] for i in self.key['readers'][c]],ids)

    def test_10_closure(self):
        results=[adapter.closure(b.BED/c,compatible=True) for c in ('c1','c2')]
        b.dump(b.HERE/'scan/closure.json',results)
        for result in results:self.assertTrue(result['ok'],result['violations'])

    def test_11_prompt_launchers_and_settings(self):
        self.assertEqual((b.HERE/'prompts/caps3.md').read_bytes(),(b.REFERENCE/'prompts/bsb.md').read_bytes())
        read=(b.HERE/'launchers/run_read.sh').read_text()
        for flag in ('MODEL=gpt-6.1-sol','sandbox_workspace_write.network_access=false','web_search="disabled"','features.multi_agent=false','features.apps=false','features.remote_plugin=false','project_doc_max_bytes=0','approval_policy=never'):
            self.assertIn(flag,read)
        self.assertIn('"$P" medium',(b.HERE/'launchers/run_bed.sh').read_text())
        for name in ('run_read.sh','run_bed.sh','limit_probe.sh'):
            subprocess.run(['bash','-n',str(b.HERE/'launchers'/name)],check=True)
        self.assertIn('= caps3 ]; then exec bash '+str(b.HERE/'launchers/run_bed.sh'),(b.PACK_ROOT/'launchers/run_bed.sh').read_text())
        self.assertEqual(len((b.HERE/'launch_lines.txt').read_text().splitlines()),2)

    def test_12_inputs_public_copies_and_closure_policy(self):
        from PIL import Image
        inputs=json.loads((b.HERE/'build_receipt.json').read_text())['inputs']
        inputs.update(json.loads((b.HERE/'runtime_bindings.json').read_text())['reference_sources'])
        screen=json.loads((b.HERE/'screen_receipt.json').read_text())
        inputs.update(screen['inputs']);inputs.update(screen['helper_sources'])
        for path,digest in inputs.items():self.assertEqual(b.sha(path),digest,path)
        for context in ('c1','c2'):
            directory=b.BED/context
            cards=b.rows(directory/'cards.jsonl')
            self.assertEqual(len(cards),55)
            for c in cards:
                self.assertEqual(set(c),b.FIELDS)
                f=directory/c['crop']
                self.assertFalse(f.is_symlink());self.assertEqual(f.stat().st_nlink,1)
                self.assertEqual(f.stem,b.sha(f))
                with Image.open(f) as im:
                    self.assertEqual(im.mode,'L');self.assertFalse(im.info)
        start=json.loads((b.HERE/'keys/release_exclusions_at_start.json').read_text())
        observed=json.loads((b.HERE/'keys/release_exclusions_observed.json').read_text())
        self.assertEqual(b.sha(b.HERE/'keys/release_exclusions_at_start.json'),'aaa579dce6338d95ea5d50ccece45e9b364571ebaea3b0d58c878fabde02eae3')
        self.assertEqual(set(observed['classes'])-set(start['classes']),{'n1_locked_eval'})
        self.assertTrue(all(observed['classes'][k]==v for k,v in start['classes'].items()))
        registry=b.HERE/'keys/n1_locked_eval_observed_ids.txt'
        self.assertEqual(b.sha(registry),observed['classes']['n1_locked_eval']['sha256'])
        locked=set(registry.read_text().splitlines())
        drift=json.loads((b.HERE/'exclusion_drift.json').read_text())
        self.assertEqual(sorted(locked & {r['id'] for r in self.pool}),drift['pool_intersection'])
        self.assertEqual(sorted(locked & {r['id'] for r in b.rows(b.HERE/'keys/draw.jsonl')}),drift['draw_intersection'])
        original=(b.HERE.parent/'caps1/reference_adapter.py').read_text().replace('caps1','caps3').replace('CAPS1','CAPS3')
        self.assertEqual((b.HERE/'reference_adapter.py').read_text(),original)

if __name__=='__main__':
    p.network_off()
    start=time.monotonic();stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Caps3Tests))
    (b.HERE/'tests.log').write_text(stream.getvalue())
    ET.ElementTree(ET.Element('testsuite',tests=str(result.testsRun),failures=str(len(result.failures)),errors=str(len(result.errors)),skipped=str(len(result.skipped)),time=str(round(time.monotonic()-start,3)))).write(b.HERE/'tests.xml',encoding='unicode')
    print(stream.getvalue(),end='')
    raise SystemExit(0 if result.wasSuccessful() else 1)
