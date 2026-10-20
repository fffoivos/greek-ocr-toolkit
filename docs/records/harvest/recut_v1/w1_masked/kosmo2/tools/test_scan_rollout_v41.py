import base64, io, json, tempfile, unittest
from PIL import Image
from pathlib import Path
from scan_rollout_v41 import inspect, PWD
from build import HERE, BED
from reference_adapter import rollout_scanner

class TemplateTests(unittest.TestCase):
    def scan(self, extra=''):
        folder = BED / 'c2b'
        records = [dict(payload=dict(type='custom_tool_call', name='exec', input='image((await tools.view_image({path:`'+PWD+'/zoom/01.png`})).image_url);'+extra)),
                   dict(payload=dict(item=dict(type='CommandExecution', command=['/bin/zsh','-lc','pwd'], stdout=str(folder)+'\n', exit_code=0)))]
        with tempfile.NamedTemporaryFile(mode='w') as f:
            for r in records: f.write(json.dumps(r)+'\n')
            f.flush(); return inspect(f.name, folder)

    def test_pwd_template_witness_path_passes(self):
        report = json.loads((HERE/'scan/kosmo2/c2b.scan_v41_final.json').read_text())
        report = inspect(report['rollout'], BED/'c2b')
        self.assertTrue(report['ok'])
        self.assertEqual(report['violations'], [])
        self.assertEqual(report['returned_images'], 64)
        self.assertEqual(report['image_match_counts'], {'bytes': 53, 'downscale': 11})
        self.assertFalse(report['manifest_check_skipped'])
        self.assertTrue(report['v41_path_witness_ok'])
        self.assertEqual(report['pwd_evidence'][0]['record'], 27)
        self.assertTrue(self.scan()['ok'])

    def test_true_outside_path_still_fails(self):
        report = self.scan(';text(await tools.exec_command({cmd:"cat /private/tmp/outside.png"}));')
        self.assertFalse(report['ok'])
        self.assertTrue(any(v.get('path') == '/private/tmp/outside.png' for v in report['violations']))

    def test_parent_escape_still_fails(self):
        report = self.scan(';text(await tools.exec_command({cmd:"cat ../outside.png"}));')
        self.assertFalse(report['ok'])

    def test_v4_downscale_boundaries(self):
        scanner = rollout_scanner()
        source = Image.new('RGB', (4096, 200), 'white')
        original = io.BytesIO(); source.save(original, format='PNG')
        candidates = [('zoom/test.png', original.getvalue(), source)]
        def match(size, color):
            buf = io.BytesIO()
            Image.new('RGB', size, color).save(buf, format='PNG')
            return scanner.match_image(buf.getvalue(), candidates)
        self.assertEqual(match((2048, 100), (254,254,254))['match'], 'downscale')
        self.assertIsNone(match((2048, 100), (253,253,253)))  # MAD == 2 fails
        self.assertIsNone(match((2048, 103), 'white'))  # wrong aspect
        self.assertIsNone(match((1024, 50), 'white'))  # wrong long side

if __name__ == '__main__': unittest.main()
