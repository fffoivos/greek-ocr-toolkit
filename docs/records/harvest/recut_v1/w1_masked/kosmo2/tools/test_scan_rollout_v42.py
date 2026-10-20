import json, tempfile, unittest
from pathlib import Path
from scan_rollout_v42 import inspect, ruc1_scanner
from build import PACK_ROOT

RUC = Path(__file__).resolve().parents[2] / 'ruc1'
BED = PACK_ROOT / 'ruc1'
FONT = '/System/Library/Fonts/Helvetica.ttc'
ROLLOUT = Path('/Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T16-49-41-01a14a20-1ea7-73a3-b472-2ff79d7093dc.jsonl')

class FontTests(unittest.TestCase):
    def scan(self, cmd):
        raw = 'text(await tools.exec_command({cmd:'+json.dumps(cmd)+'}));'
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(json.dumps(dict(payload=dict(type='custom_tool_call', name='exec', input=raw)))+'\n')
            f.flush(); return inspect(f.name, BED/'c1')

    def test_real_witness(self):
        r = inspect(ROLLOUT, BED/'c1')
        self.assertTrue(r['ok'], r['violations'])
        self.assertEqual({a['record'] for a in r['os_resource_allowances']}, {194,215})
        self.assertEqual(r['returned_images'],81)
        self.assertEqual(sum(r['image_match_counts'].values()),81)
        self.assertFalse(r['manifest_check_skipped'])

    def test_nonfont_and_parent_escape_fail(self):
        for path in ('/private/tmp/outside.png','/System/Library/Fonts/../outside.png','/Library/FontsEvil/font.ttf'):
            with self.subTest(path=path): self.assertFalse(self.scan('cat '+path)['ok'])

    def test_font_write_fails(self):
        for cmd in (f'echo x > {FONT}',f'cat {FONT} > {FONT}',f'touch {FONT}',
            "python3 - <<'PY'\nopen('"+FONT+"','w').write('x')\nPY",
            "python3 - <<'PY'\nimport subprocess\nsubprocess.run(['magick','-font','"+FONT+"','zoom/a.png','"+FONT+"'])\nPY"):
            with self.subTest(cmd=cmd): self.assertFalse(self.scan(cmd)['ok'])

    def test_read_only_both_roots(self):
        for path in (FONT, '/Library/Fonts/example.ttf'):
            with self.subTest(path=path): self.assertTrue(self.scan('cat '+path)['ok'])

if __name__ == '__main__': unittest.main()
