"""Canonical scanner regressions, including every original v4 test and local witnesses."""
import base64, io, json, struct, tempfile, unittest, shutil
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


inspect = scanner.inspect
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


class CanonicalRules(unittest.TestCase):
    setUp = LiteralBindings.setUp
    tearDown = LiteralBindings.tearDown
    scan = LiteralBindings.scan
    def test_stores_do_not_cross_rollouts(self):
        self.assertTrue(self.scan('store("base",'+json.dumps(str(self.reader))+');')['ok'])
        self.assertFalse(self.scan('image(load("base")+"/zoom/a.png");')['ok'])

    def test_store_must_precede_load(self):
        self.assertFalse(self.scan('image(load("base")+"zoom/a.png");store("base",'+json.dumps(str(self.reader))+');')['ok'])

    def test_dynamic_suffix_fails(self):
        self.assertFalse(self.scan('store("base",'+json.dumps(str(self.reader))+');image(load("base")+suffix);')['ok'])

    def test_data_load_retains_v4_behavior(self):
        self.assertTrue(self.scan('store("rows",JSON.parse(output));',
            'const rows=load("rows");text(rows);')['ok'])
        self.assertFalse(self.scan('const rows=load("rows");text(rows);')['ok'])

    def test_version(self):
        self.assertEqual(self.scan('text("ok");')['scanner_version'], '4.5.5')

    def test_pwd_positive(self):
        p = self.root/'rollout.jsonl'
        records = [dict(payload=dict(type='custom_tool_call', name='exec', input='image({path:`'+scanner.PWD+'/zoom/a.png`});')),
            dict(payload=dict(item=dict(type='CommandExecution', command=['/bin/zsh','-lc','pwd'], stdout=str(self.reader)+'\n', exit_code=0)))]
        p.write_text(''.join(json.dumps(r)+'\n' for r in records))
        r = inspect(p, self.reader)
        self.assertTrue(r['ok'], r['violations']); self.assertEqual(len(r['pwd_evidence']), 1)
        for output, code in ((str(self.root), 0), (str(self.reader), 1)):
            records[1]['payload']['item'].update(stdout=output, exit_code=code)
            p.write_text(''.join(json.dumps(r)+'\n' for r in records))
            self.assertFalse(inspect(p, self.reader)['ok'])

    def test_pwd_missing_output_fails(self):
        self.assertFalse(self.scan('image({path:`'+scanner.PWD+'/zoom/a.png`});')['ok'])

    def test_literal_base_templates(self):
        code='const base='+json.dumps(str(self.reader))+'; image({path:`${base}/zoom/a.png`});'
        self.assertTrue(self.scan(code)['ok'])
        self.assertFalse(self.scan('const base="/private/tmp/outside"; image({path:`${base}/zoom/a.png`});')['ok'])

    def test_store_template_positive_and_negative(self):
        self.assertTrue(self.scan('store("base",'+json.dumps(str(self.reader))+');',
            'image({path:`${load("base")}/zoom/a.png`});')['ok'])
        self.assertFalse(self.scan('image({path:`${load("base")}/zoom/a.png`});')['ok'])
        self.assertTrue(self.scan('const base='+json.dumps(str(self.reader))+';store("base",base);',
            'image({path:`${load("base")}/zoom/a.png`});')['ok'])
        # Const-based v4.1 templates do not authorize v4.3 concatenations.
        self.assertFalse(self.scan('const base='+json.dumps(str(self.reader))+';',
            'image(load("base")+"/zoom/a.png");')['ok'])

    def test_floor_division_positive(self):
        cmd="python3 - <<'PY'\nprint((j+1)//4)\nPY"
        r=self.scan('text(await tools.exec_command({cmd:'+json.dumps(cmd)+'}));')
        self.assertTrue(r['ok'],r['violations'])
        self.assertEqual(r['commands'],[cmd])

    def test_slash_outside_path_negative(self):
        self.assertFalse(self.scan('text(await tools.exec_command({cmd:"cat /4"}));')['ok'])

    def test_font_read_both_roots(self):
        for path in ('/System/Library/Fonts/Helvetica.ttc', '/Library/Fonts/example.ttf'):
            self.assertTrue(self.scan('text(await tools.exec_command({cmd:'+json.dumps('stat '+path)+'}));')['ok'])

    def test_font_magick_proof(self):
        cmd="python3 - <<'PY'\nimport subprocess\nsubprocess.run(['magick','-font','/System/Library/Fonts/Helvetica.ttc','zoom/a.png','zoom/b.png'])\nPY"
        self.assertTrue(self.scan('text(await tools.exec_command({cmd:'+json.dumps(cmd)+'}));')['ok'])

    def test_font_write_or_ambiguous_fails(self):
        font='/System/Library/Fonts/Helvetica.ttc'
        for cmd in ('touch '+font, 'cat '+font+' > '+font, 'echo x > '+font,
            'cat /System/Library/Fonts/../outside.ttf', 'cat /Library/FontsEvil/a.ttf',
            "python3 - <<'PY'\nimport subprocess\nsubprocess.run(['magick','-font','"+font+"','zoom/a.png','"+font+"'])\nPY"):
            with self.subTest(cmd=cmd):
                self.assertFalse(self.scan('text(await tools.exec_command({cmd:'+json.dumps(cmd)+'}));')['ok'])

    def test_reencoding_positive_and_negative(self):
        source=Image.new('RGBA',(12,9),(255,0,0,255)); original=io.BytesIO(); source.save(original,format='PNG')
        meta=PngImagePlugin.PngInfo(); meta.add_text('timestamp','different')
        def match(im):
            b=io.BytesIO();im.save(b,format='PNG',pnginfo=meta)
            return scanner.match_image(b.getvalue(), [('img/a.png',original.getvalue(),source.convert('RGB'))])
        self.assertEqual(match(source)['match'],'pixels')
        self.assertIsNone(match(source.convert('RGB')))
        source.putpixel((0,0),(255,0,0,254));self.assertIsNone(match(source))
        source.putpixel((0,0),(254,0,0,255));self.assertIsNone(match(source))

    def test_downscale_boundaries(self):
        source=Image.new('RGB',(4096,200),'white'); original=io.BytesIO();source.save(original,format='PNG')
        def match(size,color):
            b=io.BytesIO();Image.new('RGB',size,color).save(b,format='PNG')
            return scanner.match_image(b.getvalue(), [('zoom/a.png',original.getvalue(),source)])
        self.assertEqual(match((2048,100),(254,254,254))['match'],'downscale')
        self.assertEqual(match((1024,50),'white')['match'],'downscale')
        for size,color in (((2048,100),(253,253,253)),((2048,103),'white')):
            self.assertIsNone(match(size,color))


SESSIONS=Path.home()/'.codex/sessions/2026/10/17'
WITNESSES = {
    'cq1_r1': ('rollout-2026-10-17T18-40-41-01a14a85-bfd9-75e3-b20f-a79f924d6dbf.jsonl', False, 15),
    'cq1_r1b': ('rollout-2026-10-17T18-57-48-01a14a95-6a88-7932-b4be-e126741b7e28.jsonl', True, 19),
    'ru1_ctx01_r2': ('rollout-2026-10-17T15-54-40-01a149ed-c0e3-7143-9bc9-11ac09eebd4d.jsonl', True, 90),
    'ru1_ctx04_r2': ('rollout-2026-10-17T16-03-16-01a149f5-9e87-7a20-a543-62a90d71e078.jsonl', False, 195),
    'v41_kosmo2': ('rollout-2026-10-17T16-05-06-01a149f7-4d1e-7f80-ad8d-aff3b314a204.jsonl', True, 64),
    'v42_ruc1': ('rollout-2026-10-17T16-49-41-01a14a20-1ea7-73a3-b472-2ff79d7093dc.jsonl', True, 81),
}

def replay_witness(rollout, directory):
    """Rehydrate missing content-addressed RU1 crops in a temporary snapshot.

    The historical rollout and pack are never changed. Roots are relocated in
    string fields only; the literal /zoom CQ1 violation is never rewritten.
    Every recovered byte must match the existing manifest, and the complete
    snapshot must pass integrity before the witness is inspected.
    """
    manifest=directory.parent/f'MANIFEST.{directory.name}.json'
    files=json.loads(manifest.read_text())['files']
    missing=[name for name in files if not (directory/name).is_file()]
    if not missing:return inspect(rollout,directory)
    if not all(name.startswith('crops/') for name in missing):
        raise AssertionError('Missing non-crop witness originals: '+str(missing))
    scratch=next((p for p in directory.parents if p.name=='scratchpad'),None)
    if scratch is None:raise AssertionError('No local witness cache root')
    with tempfile.TemporaryDirectory(prefix='sc45-witness-') as tmp:
        root=Path(tmp).resolve();snapshot=root/directory.name
        shutil.copytree(directory,snapshot)
        shutil.copyfile(manifest,root/manifest.name)
        for name in missing:
            source=scratch/'ru1_cache'/name
            if not source.is_file() or scanner.sha(source)!=files[name]:
                raise AssertionError('Unavailable or changed cached witness crop: '+name)
            (snapshot/name).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,snapshot/name)
        errors,skipped=scanner.integrity(snapshot)
        if errors or skipped:raise AssertionError('Snapshot integrity: '+str(errors))
        def relocate(obj):
            if isinstance(obj,str):return obj.replace(str(directory),str(snapshot))
            if isinstance(obj,list):return [relocate(v) for v in obj]
            if isinstance(obj,dict):return {k:relocate(v) for k,v in obj.items()}
            return obj
        replay=root/'rollout.jsonl'
        replay.write_text(''.join(json.dumps(relocate(json.loads(line)))+'\n' for line in rollout.read_text().splitlines()))
        print('WITNESS SNAPSHOT '+rollout.name+' source_sha256='+scanner.sha(rollout)+
            ' manifest_sha256='+scanner.sha(manifest)+' recovered='+str(len(missing))+
            ' all_manifest_hashes=PASS original_pack_unchanged=true',flush=True)
        return inspect(replay,snapshot)


class WitnessReplays(unittest.TestCase):
    def replay(self, name):
        filename, ok, images = WITNESSES[name]; rollout=SESSIONS/filename
        if not rollout.is_file(): self.skipTest('MISSING witness rollout: '+str(rollout))
        with rollout.open() as f: directory=Path(json.loads(next(f))['payload']['cwd'])
        # Missing packs are a failure: do not silently skip a present rollout.
        self.assertTrue(directory.is_dir(), 'Missing witness reader pack: '+str(directory))
        result=replay_witness(rollout,directory)
        self.assertEqual(result['ok'],ok,result['violations'])
        self.assertEqual(result['returned_images'],images)
        self.assertFalse(result['manifest_check_skipped'])
        if ok: self.assertEqual(result['violations'],[])
        return result

    def test_witness_cq1_r1(self):
        r=self.replay('cq1_r1')
        self.assertEqual(r['violations'],[dict(record=24,reason='absolute path outside reader_dir',path='/zoom/batch1.png')])

    def test_witness_cq1_r1b(self): self.replay('cq1_r1b')
    def test_witness_ru1_ctx01_r2(self): self.replay('ru1_ctx01_r2')
    def test_witness_ru1_ctx04_r2(self):
        r=self.replay('ru1_ctx04_r2')
        self.assertEqual(len(r['violations']),15)
        self.assertTrue(all(v['reason']=='image provenance: unmatched image provenance' for v in r['violations']))
        self.assertEqual([v['record'] for v in r['violations']],[69,80,80,80,108,135,135,219,246,246,246,300,300,331,358])
    def test_witness_v41_kosmo2(self):
        r=self.replay('v41_kosmo2')
        self.assertEqual(r['image_match_counts'],{'bytes':53,'downscale':11})
        self.assertEqual(r['pwd_evidence'][0]['record'],27)
    def test_witness_v42_ruc1(self):
        r=self.replay('v42_ruc1')
        self.assertEqual(r['image_match_counts'],{'bytes':27,'downscale':54})
        self.assertEqual({v['record'] for v in r['os_resource_allowances']},{194,215})

if __name__=='__main__': unittest.main(verbosity=2)
