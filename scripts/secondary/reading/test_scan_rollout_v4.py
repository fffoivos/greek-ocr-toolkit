"""SR-G4: overwrite recovery and fail-closed reproduction regressions."""
import base64, io, json, struct, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, PngImagePlugin
import scan_rollout as scanner
from replay_literal import parse

class ReproductionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='test-v4-',dir=scanner.REPLAY_TMP)
        self.root=Path(self.tmp.name);self.reader=self.root/'reader';self.reader.mkdir()
        (self.reader/'img').mkdir();(self.reader/'zoom').mkdir()
        Image.new('RGB',(12,9),'red').save(self.reader/'img/source.png')
        (self.reader/'items.jsonl').write_text('{}\n')
        files={n:scanner.sha(self.reader/n) for n in ('items.jsonl','img/source.png')}
        (self.root/'MANIFEST.reader.json').write_text(json.dumps(dict(files=files)))
        self.make="mkdir -p zoom\npython3 - <<'PY'\nfrom PIL import Image\nImage.open('img/source.png').resize((60,45)).save('zoom/batch1.png')\nPY"
        self.old=io.BytesIO();Image.new('RGB',(60,45),'red').save(self.old,format='PNG')
        Image.new('RGB',(60,90),'blue').save(self.reader/'zoom/batch1.png')
    def tearDown(self):self.tmp.cleanup()
    def rollout(self,data,view='zoom/batch1.png',history=None):
        cmds=history if history is not None else [self.make]
        calls=[]
        for j,cmd in enumerate(cmds):
            calls.append(dict(payload=dict(type='function_call',name='exec_command',call_id=f'c{j}',arguments=json.dumps(dict(cmd=cmd)))))
        calls.append(dict(payload=dict(type='function_call',name='view_image',call_id='v',arguments=json.dumps(dict(path=view)))))
        calls.append(dict(payload=dict(type='function_call_output',call_id='v',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(data).decode())])))
        # A later overwrite must never enter the reproduction history.
        calls.append(dict(payload=dict(type='function_call',name='exec_command',call_id='later',arguments=json.dumps(dict(cmd="python3 - <<'PY'\nfrom PIL import Image\nImage.new('RGB',(60,90),'blue').save('zoom/batch1.png')\nPY")))))
        p=self.root/'rollout.jsonl';p.write_text(''.join(json.dumps(c)+'\n' for c in calls));return p
    def test_synthetic_overwrite(self):
        r=scanner.inspect(self.rollout(self.old.getvalue()),self.reader)
        self.assertTrue(r['ok'],r['violations']);self.assertEqual(r['image_matches'][0]['match'],'reproduced')
        self.assertEqual(r['reproductions'][0]['size'],[60,45]);self.assertEqual(len(r['reproductions'][0]['commands']),1)
        with Image.open(self.reader/'zoom/batch1.png') as im:self.assertEqual(im.size,(60,90))
    def test_exec_wrapper(self):
        p=self.rollout(self.old.getvalue());records=[json.loads(x) for x in p.read_text().splitlines()]
        records[0]['payload']=dict(type='custom_tool_call',name='exec',call_id='v',input='text(await tools.exec_command({cmd:'+json.dumps(self.make)+'})); const r=await tools.view_image({path:"zoom/batch1.png"});image(r.image_url);')
        del records[1];p.write_text(''.join(json.dumps(r)+'\n' for r in records))
        self.assertTrue(scanner.inspect(p,self.reader)['ok'])
    def test_time_chunk_difference_passes(self):
        def png_time(day):
            b=io.BytesIO();meta=PngImagePlugin.PngInfo()
            meta.add(b'tIME',struct.pack('>H5B',2026,10,day,12,0,0))
            Image.new('RGB',(60,45),'red').save(b,format='PNG',pnginfo=meta)
            return b.getvalue()
        observed=png_time(16);reproduced=png_time(17)
        self.assertNotEqual(observed,reproduced)
        # Both files have a real tIME chunk, with different timestamps.
        run=scanner.subprocess.run
        def replay_with_time(args,**kwargs):
            result=run(args,**kwargs)
            if result.returncode==0:
                (Path(args[-1])/'zoom/batch1.png').write_bytes(reproduced)
            return result
        with patch.object(scanner.subprocess,'run',side_effect=replay_with_time):
            r=scanner.inspect(self.rollout(observed),self.reader)
        self.assertTrue(r['ok'],r['violations'])
        self.assertEqual(r['image_matches'][0]['match'],'reproduced_pixels')
        self.assertEqual(r['image_matches'][0]['mad'],0)
        self.assertTrue(r['reproductions'][0]['pixels_exact'])
    def test_grayscale_pixels_pass(self):
        self.make=self.make.replace(".save('zoom/batch1.png')", ".convert('L').save('zoom/batch1.png')")
        b=io.BytesIO();meta=PngImagePlugin.PngInfo();meta.add_text('timestamp','different')
        Image.new('RGB',(60,45),'red').convert('L').save(b,format='PNG',pnginfo=meta)
        r=scanner.inspect(self.rollout(b.getvalue()),self.reader)
        self.assertTrue(r['ok'],r['violations'])
        self.assertEqual(r['image_matches'][0]['match'],'reproduced_pixels')
    def test_one_pixel_difference_fails(self):
        b=io.BytesIO();im=Image.new('RGB',(60,45),'red')
        im.putpixel((0,0),(254,0,0));im.save(b,format='PNG')
        r=scanner.inspect(self.rollout(b.getvalue()),self.reader)
        self.assertFalse(r['ok']);self.assertFalse(r['reproductions'][0]['pixels_exact'])
    def test_rgba_alpha_difference_fails(self):
        self.make=self.make.replace(".save('zoom/batch1.png')", ".convert('RGBA').save('zoom/batch1.png')")
        b=io.BytesIO();im=Image.new('RGBA',(60,45),(255,0,0,255))
        im.putpixel((0,0),(255,0,0,254));im.save(b,format='PNG')
        self.assertFalse(scanner.inspect(self.rollout(b.getvalue()),self.reader)['ok'])
    def test_mode_difference_fails(self):
        b=io.BytesIO();Image.new('RGBA',(60,45),(255,0,0,255)).save(b,format='PNG')
        self.assertFalse(scanner.inspect(self.rollout(b.getvalue()),self.reader)['ok'])
    def test_wrong_view_stays_violation(self):
        self.assertFalse(scanner.inspect(self.rollout(self.old.getvalue(),'zoom/missing.png'),self.reader)['ok'])
    def test_changed_manifest_stays_violation(self):
        (self.reader/'items.jsonl').write_text('changed')
        r=scanner.inspect(self.rollout(self.old.getvalue()),self.reader)
        self.assertFalse(r['ok']);self.assertIn('integrity failed',r['reproductions'][0]['error'])
    def test_unsafe_commands(self):
        for cmd in ('curl https://example.com','echo x > /tmp/escape','mkdir -p ../escape',"python3 - <<'PY'\nimport os\nos.system('id')\nPY",'cat $(whoami)',"python3 - <<'PY'\nopen('/tmp/out','w')\nPY",'echo x > answers.jsonl'):
            with self.subTest(cmd=cmd),self.assertRaises(ValueError):parse(cmd)
    def test_skip_unsafe_no_recovery(self):
        r=scanner.inspect(self.rollout(self.old.getvalue(),history=['echo x > answers.jsonl']),self.reader)
        self.assertFalse(r['ok']);self.assertEqual(r['reproductions'][0]['commands'][0]['status'],'skipped')

if __name__=='__main__':unittest.main(verbosity=2)
