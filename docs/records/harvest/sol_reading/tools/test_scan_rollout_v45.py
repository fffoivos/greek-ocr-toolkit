"""SC45 closed grammar and seeded provenance acceptance/rejection fixtures.
No CQ4 rollout is inspected here. Only synthetic temporary reader packs run.
"""
import ast,base64,hashlib,io,json,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
import scan_rollout as s

RECORDER=Path(__file__).with_name('fixtures_v45').joinpath('record_confined.txt').read_text()
DEFINE="cat > zoom/record.py <<'PY'\n"+RECORDER+"\nPY"
def call(cmd):return dict(payload=dict(type='function_call',name='exec_command',call_id='c',arguments=json.dumps(dict(cmd=cmd))))
def exe(code):return dict(payload=dict(type='custom_tool_call',name='exec',call_id='v',input=code))
def png(im):
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def returned(*ims):
    return dict(payload=dict(type='function_call_output',call_id='v',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(png(im)).decode()) for im in ims]))
def view(path):return 'image((await tools.view_image({path:'+json.dumps(path)+'})).image_url);'

def pattern():
    im=Image.new('RGB',(180,120));im.putdata([((x*7+y*3)%256,(x*2+y*11)%256,(x*13+y*5)%256) for y in range(120) for x in range(180)]);return im

class Pack(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='sc45-');self.root=Path(self.tmp.name);self.reader=self.root/'r1';self.reader.mkdir();(self.reader/'img').mkdir();(self.reader/'zoom').mkdir()
        self.source=pattern();self.source.save(self.reader/'img/source.png');Image.new('RGB',(180,120),'blue').save(self.reader/'img/blue.png')
        (self.reader/'items.jsonl').write_text('{}\n');self.manifest()
    def tearDown(self):self.tmp.cleanup()
    def manifest(self):
        files={str(p.relative_to(self.reader)):s.sha(p) for p in [self.reader/'items.jsonl',*sorted((self.reader/'img').glob('*.png'))]}
        (self.root/'MANIFEST.r1.json').write_text(json.dumps(dict(files=files)))
    def scan(self,*records):
        rollout=self.root/'rollout.jsonl';rollout.write_text(''.join(json.dumps(r)+'\n' for r in records));return s.inspect(rollout,self.reader)
    def assertOK(self,*records):
        r=self.scan(*records);self.assertTrue(r['ok'],r['violations']);return r
    def assertBad(self,*records):
        r=self.scan(*records);self.assertFalse(r['ok']);return r
    def make(self,name='batch.png',source='source.png'):
        return "python3 - <<'PY'\nfrom PIL import Image\nImage.open('img/"+source+"').save('zoom/"+name+"')\nPY"

class P1Positive(Pack):
    def test_four_cq4e_commands(self):
        for atoms in ('r?/n n/n n/n r/n n/a','s/n s/a s/n s/n r?/a','n/n r?/n s/a n/n n/n','n/a n/n n/n s?/c s/a'):
            with self.subTest(atoms=atoms):self.assertOK(call(DEFINE),call("python3 zoom/record.py '"+atoms+"'"))
    def test_complete_closed_grammar(self):
        atoms=' '.join(b+q+'/'+a+t for b in 'nsru' for a in 'nagcu' for q in ('','?') for t in ('','?'))
        self.assertOK(call(DEFINE),exe('text(await tools.exec_command({cmd:'+json.dumps("python3 zoom/record.py '"+atoms+"'")+'}));'))
    def test_confined_helper_pin(self):
        self.assertEqual(hashlib.sha256(ast.dump(ast.parse(RECORDER)).encode()).hexdigest(),s.RECORD_AST_SHA)
        self.assertEqual(s.answer_data("python3 zoom/record.py 'r?/n'",[(0,DEFINE)]),'python3 zoom/record.py ANSWER_DATA')

class P1Negative(Pack):
    def test_real_absolute_operands_once(self):
        for path in ('/n','/a','/c','/tmp/outside'):
            with self.subTest(path=path):
                r=self.assertBad(exe('text(await tools.exec_command({cmd:'+json.dumps('cat '+path)+'}));'))
                self.assertEqual(len(r['violations']),1);self.assertEqual(r['violations'][0]['path'],path)
    def test_traversal_and_keys(self):
        for path in ('../truth.json','keys/','../outside'):
            with self.subTest(path=path):self.assertBad(call(DEFINE),call("python3 zoom/record.py 'r?/n' "+path))
    def test_invalid_atom_and_mixed_argv(self):
        for arg in ('x?/n','r??/n','r?/n /n','r?/n /tmp/outside','r?/n ../truth.json','r?/n keys/'):
            with self.subTest(arg=arg):self.assertBad(call(DEFINE),call("python3 zoom/record.py '"+arg+"'"))
    def test_filename_is_not_authority(self):
        self.assertBad(call("python3 zoom/record.py 'r?/n'"))
        self.assertBad(call(DEFINE.replace("open('items.jsonl')","open('/tmp/outside')")),call("python3 zoom/record.py 'r?/n'"))
    def test_shell_and_helper_overwrite(self):
        self.assertBad(call(DEFINE),call("python3 zoom/record.py 'r?/n'; cat /n"))
        self.assertBad(call(DEFINE),call('echo unsafe > zoom/record.py'),call("python3 zoom/record.py 'r?/n'"))

class P2Positive(Pack):
    def test_general_shrink_rgb(self):
        for size in ((164,109),(90,60),(17,12)):
            with self.subTest(size=size):
                r=self.assertOK(exe(view('img/source.png')),returned(self.source.resize(size,Image.Resampling.BILINEAR)))
                self.assertIn(r['image_matches'][0]['resampling'],('LANCZOS','BICUBIC','BILINEAR','NEAREST','BOX','HAMMING'))
    def test_opaque_rgba(self):
        im=self.source.resize((164,109),Image.Resampling.BILINEAR).convert('RGBA')
        self.assertOK(exe(view('img/source.png')),returned(im))
    def test_one_pixel_axis_rounding(self):
        im=self.source.resize((91,59),Image.Resampling.BILINEAR)
        self.assertOK(exe(view('img/source.png')),returned(im))
    def test_historical_shrink(self):
        Image.new('RGB',(180,120),'blue').save(self.reader/'zoom/batch.png')
        r=self.assertOK(call('mkdir -p zoom'),call(self.make()),exe(view('zoom/batch.png')),returned(self.source.resize((164,109),Image.Resampling.BILINEAR).convert('RGBA')))
        self.assertEqual(r['image_matches'][0]['match'],'reproduced_downscale');self.assertTrue(r['reproductions'][0]['manifest_verified'])

class P2Negative(Pack):
    def test_upscale(self):self.assertBad(exe(view('img/source.png')),returned(self.source.resize((181,121))))
    def test_crop(self):
        for box in ((10,10,170,110),(15,10,165,110)):
            with self.subTest(box=box):self.assertBad(exe(view('img/source.png')),returned(self.source.crop(box)))
    def test_distortion(self):self.assertBad(exe(view('img/source.png')),returned(self.source.resize((100,100))))
    def test_transparency(self):
        im=self.source.resize((90,60)).convert('RGBA');im.putpixel((0,0),(0,0,0,254));self.assertBad(exe(view('img/source.png')),returned(im))
    def test_unrelated(self):self.assertBad(exe(view('img/source.png')),returned(Image.new('RGB',(90,60),'blue')))
    def test_mad_strict_boundary(self):
        white=Image.new('RGB',(180,120),'white');white.save(self.reader/'img/white.png');self.manifest()
        self.assertOK(exe(view('img/white.png')),returned(Image.new('RGB',(90,60),(254,254,254))))
        self.assertBad(exe(view('img/white.png')),returned(Image.new('RGB',(90,60),(253,253,253))))
    def test_changed_original_and_unseeded_zoom(self):
        (self.reader/'items.jsonl').write_text('changed');self.assertBad(exe(view('img/source.png')),returned(self.source.resize((90,60))))
        self.manifest();self.source.save(self.reader/'zoom/unproven.png')
        self.assertBad(exe(view('zoom/unproven.png')),returned(self.source.resize((90,60))))

class P3Positive(Pack):
    def test_literal_array_order(self):
        r=self.assertOK(exe('for(const n of ["source","blue"])'+ 'image((await tools.view_image({path:`img/${n}.png`})).image_url);'),returned(self.source,Image.new('RGB',(180,120),'blue')))
        self.assertEqual([m['path'] for m in r['image_matches']],['img/source.png','img/blue.png'])
    def test_constant_ranges(self):
        self.source.save(self.reader/'img/b10.png');self.source.save(self.reader/'img/b11.png');self.source.save(self.reader/'img/b12.png');self.manifest()
        for bound in ('i<=12','i<13'):
            r=self.assertOK(exe('for(let i=10;'+bound+';i++){image((await tools.view_image({path:`img/b${i}.png`})).image_url)}'),returned(self.source,self.source,self.source))
            self.assertEqual(r['loop_expansions'][0]['views'],3)
    def test_historical_literal_helper(self):
        helper="import sys\nfrom PIL import Image\ni=int(sys.argv[1])\nImage.open('img/source.png' if i==0 else 'img/blue.png').save('zoom/batch.png')"
        define="cat > zoom/batch.py <<'PY'\n"+helper+"\nPY"
        r=self.assertOK(call('mkdir -p zoom'),call(define),call('python3 zoom/batch.py 0'),exe(view('zoom/batch.png')),returned(self.source),call('python3 zoom/batch.py 1'),exe(view('zoom/batch.png')),returned(Image.new('RGB',(180,120),'blue')))
        self.assertEqual([m['match'] for m in r['image_matches']],['reproduced','reproduced'])
        self.assertFalse((self.reader/'zoom/batch.png').exists())
        # A helper rewrite later in the same command cannot affect an earlier invocation.
        future="python3 zoom/batch.py 0\ncat > zoom/batch.py <<'PY'\nfrom PIL import Image\nImage.open('img/blue.png').save('zoom/batch.png')\nPY"
        self.assertOK(call('mkdir -p zoom'),call(define),call(future),exe(view('zoom/batch.png')),returned(self.source))
    def test_recorded_batch_helper_19_snapshots(self):
        # The CQ4E helper bytes, over fresh synthetic manifest-seeded items.
        helper=Path(__file__).with_name('fixtures_v45').joinpath('batch_confined.txt').read_text()
        items=[dict(item_id='k'+format(i,'010x'),word_image='img/source.png',line_image='img/blue.png') for i in range(95)]
        (self.reader/'items.jsonl').write_text(''.join(json.dumps(it)+'\n' for it in items));self.manifest()
        records=[call("mkdir -p zoom\ncat > zoom/batch.py <<'PY'\n"+helper+"\nPY")]
        for start in range(0,95,5):
            sheet=Image.new('RGB',(1400,1400),'white')
            for j in range(5):
                row=Image.new('RGB',(1400,280),'white')
                ImageDraw.Draw(row).text((4,3),str(start+j+1)+' '+items[start+j]['item_id'],fill='black')
                row.paste(self.source,(0,25));row.paste(Image.new('RGB',(180,120),'blue'),(0,150));sheet.paste(row,(0,j*280))
            records.extend([call('python zoom/batch.py '+str(start)),exe(view('zoom/batch.png')),returned(sheet)])
        r=self.assertOK(*records)
        self.assertEqual(len(r['reproductions']),19)
        self.assertEqual(r['image_match_counts'],{'reproduced':19})
        self.assertTrue(all(e['manifest_verified'] for e in r['reproductions']))

    def test_mkdir_survives_rejected_code(self):
        (self.reader/'zoom').rmdir()
        rejected="mkdir -p zoom\npython3 - <<'PY'\nfrom PIL import ImageOps\nPY"
        self.assertOK(call(rejected),call(self.make()),exe(view('zoom/batch.png')),returned(self.source))
    def test_mixed_answer_and_image_heredocs(self):
        command="mkdir -p zoom\npython3 - <<'PY'\nopen('answers.jsonl').read()\nPY\n"+self.make()+"\npython3 - <<'PY'\nopen('answers.jsonl','w').write('do not execute')\nPY"
        r=self.assertOK(call(command),exe(view('zoom/batch.png')),returned(self.source))
        self.assertFalse((self.reader/'answers.jsonl').exists());self.assertNotIn('answers.jsonl',str(r['reproductions'][0]['commands']))
    def test_loop_snapshot_and_padding(self):
        cmd='mkdir -p zoom\n'+self.make('b08.png')+'\n'+self.make('b09.png','blue.png')
        r=self.assertOK(call(cmd),exe('for (const n of [8,9]) image((await tools.view_image({path:`zoom/b${String(n).padStart(2,"0")}.png`})).image_url);'),returned(self.source,Image.new('RGB',(180,120),'blue')),call(self.make('b08.png','blue.png')))
        self.assertEqual([m['path'] for m in r['image_matches']],['zoom/b08.png','zoom/b09.png'])

class P3Negative(Pack):
    def test_dynamic_bounds(self):
        for loop in ('for(let i=0;i<count;i++)','for(const i of values)'):
            self.assertBad(exe(loop+'image((await tools.view_image({path:`img/b${i}.png`})).image_url);'),returned(self.source))
    def test_output_order_swapped(self):
        self.assertBad(exe('for(const n of ["source","blue"])image((await tools.view_image({path:`img/${n}.png`})).image_url);'),returned(Image.new('RGB',(180,120),'blue'),self.source))
    def test_extra_image(self):self.assertBad(exe(view('img/source.png')),returned(self.source,self.source))
    def test_path_escape(self):
        self.assertBad(exe('for(const n of ["../truth.json","/tmp/outside"])image((await tools.view_image({path:`${n}`})).image_url);'),returned(self.source,self.source))
    def test_unsafe_helper(self):
        cmd="cat > zoom/batch.py <<'PY'\nimport os\nos.system('id')\nPY\npython3 zoom/batch.py 0"
        self.assertBad(call(cmd),exe(view('zoom/batch.png')),returned(self.source))
    def test_nonliteral_helper_argv(self):
        helper="cat > zoom/batch.py <<'PY'\nfrom PIL import Image\nImage.open('img/source.png').save('zoom/batch.png')\nPY"
        self.assertBad(call(helper),call('python3 zoom/batch.py $N'),exe(view('zoom/batch.png')),returned(self.source))
    def test_answers_in_image_heredoc(self):
        cmd=self.make().replace("from PIL import Image","from PIL import Image\nopen('answers.jsonl').read()")
        self.assertBad(call(cmd),exe(view('zoom/batch.png')),returned(self.source))
    def test_helper_from_final_tree_is_not_history(self):
        (self.reader/'zoom/batch.py').write_text("from PIL import Image\nImage.open('img/source.png').save('zoom/batch.png')")
        self.assertBad(call('python3 zoom/batch.py 0'),exe(view('zoom/batch.png')),returned(self.source))
    def test_unproven_output_and_unsafe_loop_body(self):
        self.assertBad(exe('text("no image requested")'),returned(self.source.resize((90,60))))
        self.assertBad(exe('for(let i=0;i<1;i++){danger();image((await tools.view_image({path:`img/source.png`})).image_url)}'),returned(self.source))

if __name__=='__main__':unittest.main(verbosity=2)
