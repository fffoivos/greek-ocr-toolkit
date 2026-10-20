"""Offline regression tests for the provisional literal-binding wrapper."""
import sys
sys.dont_write_bytecode = True
import json, tempfile, unittest
from pathlib import Path
from scan_rollout_v43 import inspect

class LiteralBindings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.reader = self.root/'r1'; self.reader.mkdir()
        (self.root/'MANIFEST.r1.json').write_text(json.dumps({'files':{}}))
    def tearDown(self): self.tmp.cleanup()
    def scan(self, *code):
        rollout = self.root/'rollout.jsonl'
        rollout.write_text(''.join(json.dumps({'payload':{'type':'custom_tool_call',
            'name':'exec','input':s}})+'\n' for s in code))
        return inspect(rollout, self.reader)
    def test_both_quotes_and_cross_record_binding(self):
        r = self.scan(f'store("base",{json.dumps(str(self.reader))});',
            'image(load("base")+"/zoom/a.png"); image(load(\'base\')+\'/zoom/b.png\');')
        self.assertTrue(r['ok'], r['violations'])
        self.assertEqual(len(r['template_resolutions']), 2)
        self.assertEqual(r['template_resolutions'][0]['binding']['record'], 0)
    def test_external_keys_still_fail(self):
        r = self.scan('store("base","/Users/x"); image(load("base")+"/keys/k.json");')
        self.assertFalse(r['ok'])
        self.assertEqual(r['template_resolutions'][0]['resolved'], '/Users/x/keys/k.json')
        self.assertTrue(any(v['reason']=='forbidden literal path/name' for v in r['violations']))
        self.assertTrue(any(v.get('path')=='/Users/x/keys/k.json' for v in r['violations']))
    def test_missing_store_fails_even_relative_suffix(self):
        self.assertFalse(self.scan('image(load("base")+"zoom/a.png");')['ok'])
    def test_dynamic_rebinding_invalidates(self):
        r = self.scan(f'store("base",{json.dumps(str(self.reader))});',
            'store("base",getPath()); image(load("base")+"/zoom/a.png");')
        self.assertFalse(r['ok']); self.assertEqual(r['template_resolutions'], [])
    def test_string_and_comment_are_not_bindings(self):
        r = self.scan('// store("base","/tmp");\ntext(\'store("base","/tmp")\'); image(load("base")+"/zoom/a.png");')
        self.assertFalse(r['ok']); self.assertEqual(r['template_resolutions'], [])
    def test_unbound_cwd_is_not_waived(self):
        r = self.scan('image(cwd+"/zoom/a.png");')
        self.assertFalse(r['ok']); self.assertEqual(r['template_resolutions'], [])
    def test_parent_escape_and_forbidden_names_retained(self):
        for suffix in ('/../x.png','/keys/k.json','/truth.json'):
            r = self.scan(f'store("base",{json.dumps(str(self.reader))});image(load("base")+{json.dumps(suffix)});')
            self.assertFalse(r['ok'])
    def test_font_allowance_retained(self):
        self.assertTrue(self.scan('text(await tools.exec_command({cmd:"stat /System/Library/Fonts/Helvetica.ttc"}));')['ok'])
        self.assertFalse(self.scan('text(await tools.exec_command({cmd:"touch /System/Library/Fonts/Helvetica.ttc"}));')['ok'])
    def test_manifest_still_checked(self):
        (self.reader/'unexpected.txt').write_text('x')
        self.assertFalse(self.scan('text("ok");')['ok'])

if __name__ == '__main__': unittest.main()
