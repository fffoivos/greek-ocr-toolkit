import base64
import io
import itertools
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import scan_rollout
import lf1
import run
import build
import score_dryrun

def answer():
    return dict(card_id='k0000000000',letters='y',marks='y',crop_ok='y',errors=[],detail='',
                owner_crop={k:'no' for k,_ in lf1.CROP_TABLE},where=[])

class MappingTests(unittest.TestCase):
    def test_full_crop_truth_table(self):
        for bits in itertools.product(('yes','no'),repeat=5):
            a=answer();a['owner_crop']=dict(zip((x[0] for x in lf1.CROP_TABLE),bits))
            v=lf1.map_answer(a,'abc')
            self.assertEqual(v['verdict'],'CROP_VIOLATES' if 'yes' in bits else 'OK')
            self.assertEqual(v.get('reasons',[]),[r for (_,r),bit in zip(lf1.CROP_TABLE,bits) if bit=='yes'])
    def test_marks_ignored(self):
        a=answer();a.update(marks='n',errors=['wrong_mark','missing_mark','extra_mark'])
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'OK')
    def test_historical_crop_ignored(self):
        a=answer();a.update(crop_ok='n',errors=['crop_overrun'])
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'OK')
    def test_reading_evidence_only(self):
        a=answer();a['reading']='completely different'
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'OK')
    def test_letters_difference(self):
        a=answer();a.update(letters='n',where=[dict(label='b',printed='B')])
        v=lf1.map_answer(a,'abc');self.assertEqual(v['verdict'],'TEXT_DIFFERS');self.assertEqual(v['where'],a['where'])
    def test_punctuation_with_letters_y(self):
        a=answer();a.update(errors=['punctuation'],where=[dict(label='',printed='.')])
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'TEXT_DIFFERS')
    def test_crop_precedes_text(self):
        a=answer();a['owner_crop']['other_complete_line']='yes';a['letters']='n'
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'CROP_VIOLATES')
    def test_uncertain_never_invented_verdict(self):
        for field in ('letters',*[k for k,_ in lf1.CROP_TABLE]):
            a=answer()
            if field=='letters':a[field]='u'
            else:a['owner_crop'][field]='uncertain'
            with self.assertRaises(lf1.Unresolved):lf1.map_answer(a,'abc')
    def test_positive_crop_precedes_unknown(self):
        a=answer();a['letters']='u';a['owner_crop']['turned_or_clipped']='yes'
        self.assertEqual(lf1.map_answer(a,'abc')['verdict'],'CROP_VIOLATES')
    def test_missing_span_unresolved(self):
        a=answer();a['letters']='n'
        with self.assertRaises(lf1.Unresolved):lf1.map_answer(a,'abc')
    def test_nonliteral_span_unresolved(self):
        a=answer();a.update(letters='n',where=[dict(label='xxx',printed='X')])
        with self.assertRaises(lf1.Unresolved):lf1.map_answer(a,'abc')

class ReplacementTests(unittest.TestCase):
    def test_draw_order_and_same_class_source(self):
        selected=[dict(line_id='a',**{'class':'c'},source='s'),dict(line_id='b',**{'class':'c'},source='s')]
        over=[dict(line_id='x',**{'class':'c'},source='wrong'),dict(line_id='y',**{'class':'other'},source='s'),
              dict(line_id='z',**{'class':'c'},source='s'),dict(line_id='w',**{'class':'c'},source='s')]
        result=lf1.replace_flagged(['b','a'],selected,over)
        self.assertEqual([r['replacement_id'] for r in result],['z','w'])
        self.assertEqual([r['flagged_id'] for r in result],['b','a'])
    def test_used_and_unfilled(self):
        selected=[dict(line_id='a',**{'class':'c'},source='s')]
        self.assertEqual(lf1.replace_flagged(['a'],selected,selected)[0]['status'],'UNFILLED')
        over=[dict(line_id='z',**{'class':'c'},source='s')]
        self.assertEqual(lf1.replace_flagged(['a'],selected,over,['z'])[0]['status'],'UNFILLED')

class BudgetTests(unittest.TestCase):
    def test_post_probe_and_scan_on_failed_reader(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)),patch.object(run,'verify'):
            base=Path(tmp);(base/'prompts').mkdir();(base/'receipts').mkdir()
            (base/'prompts/lf1.md').write_text('synthetic prompt')
            lf1.dump(base/'receipts/prompt_receipt.json',dict(prompt_sha256=lf1.sha(base/'prompts/lf1.md')))
            calls=[]
            def probe(tag):calls.append(tag);return dict(weekly_used=20)
            read=lambda c,d:dict(rollout=str(base/'synthetic.jsonl'),rc=1,model='gpt-6.1-sol',effort='medium')
            scan=unittest.mock.Mock(return_value=dict(ok=False,violations=['synthetic']))
            result=run.attempt(dict(name='x',directory=tmp,cards=1,bed=1,controls=0),1,probe_fn=probe,read_fn=read,scan_fn=scan)
            self.assertEqual(result['status'],'VOID');self.assertEqual(len(calls),2)
            self.assertTrue(calls[0].endswith('_before'));self.assertTrue(calls[1].endswith('_after'))
            scan.assert_called_once();self.assertTrue((base/'runs/x.attempt1/scan.json').exists())
    def test_90_refused(self):
        for percent in (90,90.01,100):
            with self.assertRaises(RuntimeError):lf1.require_budget(percent)
    def test_below_90_allowed(self):
        lf1.require_budget(89.999)
    def test_attempt_never_reads_on_refusal(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)),patch.object(run,'verify'):
            read=unittest.mock.Mock()
            result=run.attempt(dict(name='x',directory=tmp,cards=1,bed=1,controls=0),1,
                               probe_fn=lambda _:dict(weekly_used=90),read_fn=read)
            self.assertEqual(result['status'],'REFUSED');read.assert_not_called()
    def test_void_gets_one_retry(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)),patch.object(run,'fresh',side_effect=lambda x:x),patch.object(run,'attempt',return_value=dict(status='VOID')) as attempt:
            self.assertEqual(len(run.worker(dict(name='x'))),2);self.assertEqual(attempt.call_count,2)
    def test_valid_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)),patch.object(run,'attempt',return_value=dict(status='VALID')) as attempt:
            self.assertEqual(len(run.worker(dict(name='x'))),1);self.assertEqual(attempt.call_count,1)

def call(cmd):
    return dict(payload=dict(type='function_call',name='exec_command',call_id='c',arguments=json.dumps(dict(cmd=cmd))))

def view(path,data):
    return [dict(payload=dict(type='function_call',name='view_image',call_id='v',arguments=json.dumps(dict(path=path)))),
            dict(payload=dict(type='function_call_output',call_id='v',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(data).decode())]))]

class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.rd=self.root/'r1';(self.rd/'img').mkdir(parents=True)
        self.im=Image.new('RGB',(40,20),'white');self.im.putpixel((10,10),(0,0,0));self.im.save(self.rd/'img/a.png')
        lf1.jsonl(self.rd/'items.jsonl',[dict(card_id='k0000000000',crop='img/a.png',google_text='abc')])
        lf1.dump(self.root/'MANIFEST.r1.json',dict(files={s:lf1.sha(self.rd/s) for s in ['items.jsonl','img/a.png']}))
    def tearDown(self):self.tmp.cleanup()
    def inspect(self,records):
        lf1.jsonl(self.root/'rollout.jsonl',records)
        return scan_rollout.inspect(self.root/'rollout.jsonl',self.rd)
    def test_scanner_hash(self):
        self.assertEqual(lf1.sha(lf1.BASE/'tools/scan_rollout.py'),lf1.SCANNER_SHA)
        self.assertEqual(scan_rollout.VERSION,'4.5.5')
    def test_original_pack_replay(self):
        result=self.inspect(view('img/a.png',(self.rd/'img/a.png').read_bytes()))
        self.assertTrue(result['ok'],result['violations'])
    def test_safe_literal_magick_zoom_replays(self):
        import subprocess
        (self.rd/'zoom').mkdir()
        subprocess.run(['magick','img/a.png','-filter','point','-resize','200%','zoom/z1.png'],cwd=self.rd,check=True)
        data=(self.rd/'zoom/z1.png').read_bytes()
        Image.new('RGB',(3,3),'blue').save(self.rd/'zoom/z1.png')
        command="python3 - <<'PY'\nimport subprocess\nsubprocess.run(['magick','img/a.png','-filter','point','-resize','200%','zoom/z1.png'],check=True)\nPY"
        records=[call('mkdir -p zoom'),call(command),*view('zoom/z1.png',data)]
        result=self.inspect(records)
        lf1.dump(lf1.BASE/'receipts/synthetic_positive_replay.json',result)
        self.assertTrue(result['ok'],result['violations']);self.assertTrue(result['reproductions'])
    def test_ss4c_heredoc_overwrite_caught(self):
        (self.rd/'zoom').mkdir();Image.new('RGB',(3,3),'blue').save(self.rd/'zoom/group01.png')
        # SS4c shape: items-driven montage in a heredoc, then a view; final tree
        # has an overwritten zoom, so the scanner must demand historical replay.
        command="""mkdir -p zoom
python3 - <<'PY'
import json,subprocess
cards=[json.loads(l) for l in open('items.jsonl')]
for start in range(0,1,1):
 args=['magick','montage','-font','Helvetica']
 for c in cards[start:start+1]:
  args+=['(',c['crop'],'-filter','point','-resize','400%',')']
 args+=['-tile','1x','-geometry','+12+16','-background','white',f'zoom/group{start//1+1:02}.png']
 subprocess.run(args,check=True)
PY"""
        b=io.BytesIO();self.im.resize((160,80),Image.Resampling.NEAREST).save(b,format='PNG')
        result=self.inspect([call(command),*view('zoom/group01.png',b.getvalue())])
        lf1.dump(lf1.BASE/'receipts/synthetic_ss4c_void.json',result)
        self.assertFalse(result['ok']);self.assertTrue(result['reproductions'])
        self.assertTrue(result['violations'])
        self.assertIn('error',result['reproductions'][0])
    def test_altered_original_caught(self):
        (self.rd/'items.jsonl').write_text('changed')
        self.assertFalse(self.inspect([])['ok'])
    def test_outside_key_caught(self):
        self.assertFalse(self.inspect([call('cat ../keys/truth.json')])['ok'])

class BuildTests(unittest.TestCase):
    def test_word_script_names_do_not_change_stored_text(self):
        self.assertEqual(build.word_scripts('יין'),[['יין','Hebrew']])
        self.assertEqual(build.word_scripts('ABC ΑΒΓ AΒ 123'),[['ABC','Latin'],['ΑΒΓ','Greek'],['AΒ','Mixed'],['123','none']])
    def test_score_confusion_and_cost(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(score_dryrun,'BASE',Path(tmp)):
            base=Path(tmp)
            key=base/'key.json';lf1.dump(key,dict(items={'a':dict(line_id='one',control=False),'b':dict(line_id='two',control=False),'c':dict(control=True)}))
            lf1.jsonl(base/'runs/x.attempt1/verdicts.jsonl',[dict(card_id='a',verdict='OK'),dict(card_id='b',verdict='TEXT_DIFFERS'),dict(card_id='c',verdict='OK')])
            contexts=[dict(name='x',key=str(key))]
            ledger=[dict(context='x',attempt=1,status='VALID',cards=3,run=dict(usage=dict(total_tokens=300)),before=dict(weekly_used=20),after=dict(weekly_used=21))]
            truth=[dict(line_id='one',expected='OK',quota_classes=['latin']),dict(line_id='two',expected='not OK',quota_classes=['latin'])]
            result=score_dryrun.score(contexts,ledger,truth)
            self.assertEqual(result['confusion'],{'OK':{'OK':1},'not OK':{'not OK':1}})
            self.assertEqual(result['agreement']['fraction'],1)
            self.assertEqual(result['per_class']['latin']['flag_rate'],.5)
            self.assertEqual(result['tokens_per_100_cards']['total_tokens'],10000)
            self.assertAlmostEqual(result['weekly_pp_per_100_cards'],100/3)
    def test_real_packs_synthetic_scanner_views(self):
        # No model/pixel judgement: synthesize recorded tool returns from bytes.
        for context in json.loads((lf1.BASE/'contexts.json').read_text()):
            rd=Path(context['directory']);records=[]
            for card in lf1.rows(rd/'items.jsonl'):
                records.extend(view(card['crop'],(rd/card['crop']).read_bytes()))
            with tempfile.TemporaryDirectory() as tmp:
                roll=Path(tmp)/'synthetic.jsonl';lf1.jsonl(roll,records)
                result=scan_rollout.inspect(roll,rd)
            lf1.dump(lf1.BASE/'receipts'/(context['name']+'.synthetic_scan.json'),result)
            self.assertTrue(result['ok'],result['violations'])
            self.assertEqual(result['returned_images'],context['cards'])
    def test_verbatim_protocol(self):
        source=(lf1.BASE/'prompts/source_bsb.md').read_text()
        body=source[source.index('You are a blind label checker'):source.index('# Done when')]
        self.assertIn(body,(lf1.BASE/'prompts/lf1.md').read_text())
    def test_layout_and_custody(self):
        for context in json.loads((lf1.BASE/'contexts.json').read_text()):
            rd=Path(context['directory'])
            # Sealed initial layout; live dry-run folders now also contain reader outputs.
            manifest=json.loads(Path(context['manifest']).read_text())['files']
            self.assertEqual({Path(p).parts[0] for p in manifest},{'items.jsonl','img'})
            self.assertLessEqual(context['cards'],100);self.assertLessEqual(context['bed'],90)
            self.assertEqual(context['cards'],len(lf1.rows(rd/'items.jsonl')))
            errors,skipped=scan_rollout.integrity(rd);self.assertEqual(errors,[]);self.assertFalse(skipped)
            for p in (rd/'img').iterdir():
                self.assertEqual(p.stem,lf1.sha(p));self.assertEqual(p.stat().st_nlink,1)
                with Image.open(p) as im:self.assertEqual(im.info,{})
    def test_opaque_public_fields(self):
        import re
        for context in json.loads((lf1.BASE/'contexts.json').read_text()):
            for item in lf1.rows(Path(context['directory'])/'items.jsonl'):
                self.assertRegex(item['card_id'],r'^k[0-9a-f]{10}$')
                self.assertEqual(set(item),{'card_id','crop','google_text','word_scripts'})
    def test_draw_rated_unique100(self):
        selected=lf1.rows(lf1.BASE/'keys/selected.jsonl')
        self.assertEqual(len(selected),100);self.assertEqual(len({x['line_id'] for x in selected}),100)
        self.assertTrue(all(x['owner_rating']['decision'] in ('KEEP','DROP') for x in selected))
    def test_control_coverage_frozen(self):
        pool=json.loads((lf1.BASE/'keys/control_pool.json').read_text())
        covered={r for c in pool for r in c['expected'].get('reasons',[])}
        self.assertEqual(covered,{r for _,r in lf1.CROP_TABLE})
        self.assertIn('OK',{c['expected']['verdict'] for c in pool})
        self.assertIn('TEXT_DIFFERS',{c['expected']['verdict'] for c in pool})
    def test_stratification_reproducible(self):
        rated=[dict(line_id=str(i),**{'class':str(i%5)}) for i in range(135)]
        self.assertEqual(build.stratified(rated),build.stratified(rated));self.assertEqual(len(build.stratified(rated)[0]),100)
    def test_not_run_score_explicit(self):
        result=score_dryrun.score([],[],[dict(line_id='x',expected='OK',quota_classes=['latin'])])
        self.assertEqual(result['unresolved'],1);self.assertIsNone(result['tokens_per_100_cards']);self.assertIsNone(result['weekly_pp_per_100_cards'])
    def test_native_pixels_preserved(self):
        contexts=json.loads((lf1.BASE/'contexts.json').read_text())
        for context in contexts:
            key=json.loads(Path(context['key']).read_text())['items']
            rd=Path(context['directory'])
            for card in lf1.rows(rd/'items.jsonl'):
                row=key[card['card_id']]
                if row['control']:continue
                with Image.open(row['source_crop']) as source,Image.open(rd/card['crop']) as target:
                    self.assertEqual(source.mode,target.mode);self.assertEqual(source.size,target.size)
                    self.assertEqual(source.tobytes(),target.tobytes())
    def test_mapping_receipt_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);item=dict(card_id='k0000000000',google_text='abc')
            lf1.jsonl(root/'items.jsonl',[item]);lf1.jsonl(root/'answers.jsonl',[answer()])
            lf1.dump(root/'key.json',dict(items={item['card_id']:dict(control=True,expected=dict(verdict='OK'))}))
            receipt=lf1.map_context(root,root/'key.json',root/'out')
            self.assertEqual(receipt['mapped'],1);self.assertEqual(receipt['control_errors'],0)
            self.assertEqual(lf1.rows(root/'out/verdicts.jsonl')[0]['verdict'],'OK')
            lf1.jsonl(root/'answers.jsonl',[])
            with self.assertRaises(ValueError):lf1.map_context(root,root/'key.json',root/'out2')


# LF2 production plumbing: fixtures use the census readout producer schema.
import csv
import prod_adapter
import prod_finalize
import build_candidates

class ProductionTests(unittest.TestCase):
    def candidate(self, rid='r1', parent='collect-v3-W1-20261018-0524', split='test'):
        return dict(parent_id=parent,row_id=rid,source='synthetic',split=split,
                    rank=1,edition_id='edition',quota_scope=split+':latin',
                    scope_rank=int.from_bytes((parent+rid).encode(),'big'),in_quota=True,overdraw_order=None,**{'class':'latin'})
    def readout(self, c, text='  α\nβ  ', digest='abc'):
        return dict(parent_id=c['parent_id'],row_id=c['row_id'],final_text=text,
                    crop_sha256=digest,crop_source_image='page.png',crop_bbox=[0,0,10,10],
                    raw_text_sha256='raw',edits=[])
    def test_adapter_order_verbatim_and_metadata(self):
        cc=[self.candidate('a'),self.candidate('b',split='dev')]
        rr=[self.readout(c) for c in reversed(cc)]
        out,mode=prod_adapter.adapt(cc,rr)
        self.assertEqual(mode,'row_id');self.assertEqual([r['line_id'] for r in out],['a','b'])
        self.assertEqual([r['class'] for r in out],['test|latin','dev|latin'])
        for r in out:
            self.assertEqual(r['label'],'  α\nβ  ');self.assertEqual(r['source_sha256'],'abc')
            for field in ('split','rank','parent_id','edition_id',*prod_adapter.DRAW_FIELDS):self.assertIn(field,r)
    def test_adapter_requires_explicit_fields(self):
        for field in prod_adapter.DRAW_FIELDS:
            c=self.candidate();del c[field]
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'missing explicit'):
                prod_adapter.adapt([c],[self.readout(c)])
    def test_adapter_cli_records_full_v3_draw_sha(self):
        with tempfile.TemporaryDirectory(dir=lf1.PACK_ROOT) as tmp:
            root=Path(tmp);cc=[self.candidate('a'),self.candidate('b')]
            lf1.jsonl(root/'v3.jsonl',cc);lf1.jsonl(root/'subset.jsonl',cc[:1])
            lf1.jsonl(root/'readout.jsonl',[self.readout(cc[0])])
            args=['prod_adapter.py','--candidates',str(root/'subset.jsonl'),
                '--draw-source',str(root/'v3.jsonl'),'--readout',str(root/'readout.jsonl'),
                '--output',str(root/'output.jsonl')]
            with patch('sys.argv',args):prod_adapter.main()
            receipt=json.loads((root/'output.jsonl.receipt.json').read_text())
            self.assertEqual(receipt['draw_sha256'],lf1.sha(root/'v3.jsonl'))
            cc[0]['in_quota']=False;cc[0]['overdraw_order']=1
            lf1.jsonl(root/'subset.jsonl',cc[:1])
            with patch('sys.argv',args),self.assertRaisesRegex(ValueError,'differs'):
                prod_adapter.main()
    def test_adapter_missing_extra_counts(self):
        with self.assertRaisesRegex(ValueError,"'missing_readout': 1, 'extra_readout': 1"):
            prod_adapter.adapt([self.candidate()],[self.readout(self.candidate('other'))])
    def test_adapter_duplicates(self):
        c=self.candidate();r=self.readout(c)
        for cc,rr in (([c,c],[r]),([c],[r,r])):
            with self.assertRaisesRegex(ValueError,'duplicate_'):prod_adapter.adapt(cc,rr)
    def test_adapter_parent_qualified_ids(self):
        cc=[self.candidate(),self.candidate(parent='collect-v3-W2-20261018-0524')]
        out,mode=prod_adapter.adapt(cc,[self.readout(c) for c in cc])
        self.assertEqual(mode,'parent_id/row_id');self.assertEqual(len({r['line_id'] for r in out}),2)
    def test_fetch_complete_unique_and_tranches(self):
        cc=lf1.rows(prod_adapter.DRAW)
        path=lf1.BASE/'prod/fetch_list.tsv'
        with path.open() as f: actual=list(csv.DictReader(f,delimiter='\t'))
        self.assertEqual(actual,prod_adapter.fetch_rows(cc));self.assertEqual(len(actual),3341)
        for field in ('remote_path','local_path'):
            self.assertEqual(len({r[field] for r in actual}),3341)
        self.assertEqual(sum(r['tranche']=='W1' for r in actual),2099)
        self.assertEqual(sum(r['tranche']=='W2' for r in actual),1242)
        for r in actual:
            part=f"collection_{r['tranche'].lower()}_originals/"
            self.assertIn(part,r['remote_path']);self.assertIn(part,r['local_path'])
    def test_fixture_adapter_build_scanner(self):
        # Temp BASE and PACK_ROOT live under the authorized external pack root.
        with tempfile.TemporaryDirectory(prefix='lf2-fixture-',dir=lf1.PACK_ROOT) as tmp:
            root=Path(tmp);base=root/'base';packs=root/'packs';crops=root/'crops'
            cc=[self.candidate(str(i)) for i in range(51)];rr=[]
            for c,f in zip(cc,prod_adapter.fetch_rows(cc,crops)):
                p=Path(f['local_path']);p.parent.mkdir(parents=True,exist_ok=True)
                Image.new('L',(20,5),int(c['row_id'])).save(p)
                rr.append(self.readout(c,'synthetic',lf1.sha(p)))
            out,_=prod_adapter.adapt(cc,rr,crops);draw=root/'adapted.jsonl';lf1.jsonl(draw,out)
            pool=[]
            for i in range(6):
                p=root/f'control{i}.png';Image.new('L',(4,4),100+i).save(p)
                pool.append(dict(pool_id=str(i),source_line_id='outside',crop=str(p),label='control',sha256=lf1.sha(p)))
            lf1.dump(base/'keys/control_pool.json',pool)
            with patch.object(build_candidates,'BASE',base),patch.object(build,'BASE',base),patch.object(build,'PACK_ROOT',packs),patch('sys.argv',['build_candidates.py',str(draw)]):
                build_candidates.main()
            contexts=json.loads((base/'candidate_contexts.json').read_text())
            self.assertEqual([(r['bed'],r['controls']) for r in contexts],[(50,6),(1,6)])
            for c in contexts:
                errors,skipped=scan_rollout.integrity(Path(c['directory']))
                self.assertEqual(errors,[]);self.assertFalse(skipped)
                self.assertEqual({p.name for p in Path(c['directory']).iterdir()},{'items.jsonl','img'})
    def test_builder_batch_names_and_rosters_do_not_collide(self):
        with tempfile.TemporaryDirectory(dir=lf1.PACK_ROOT) as tmp:
            root=Path(tmp);base=root/'base';packs=root/'packs'
            crop=root/'native.png';Image.new('L',(10,4),128).save(crop)
            cc=[self.candidate()];out,_=prod_adapter.adapt(cc,[self.readout(cc[0],digest=lf1.sha(crop))],root)
            out[0]['source_crop']=str(crop);draw=root/'draw.jsonl';lf1.jsonl(draw,out)
            lf1.dump(base/'keys/control_pool.json',[])
            with patch.object(build_candidates,'BASE',base),patch.object(build,'BASE',base),patch.object(build,'PACK_ROOT',packs):
                for batch in ('w1a','rest'):
                    roster=base/('candidate_contexts_'+batch+'.json')
                    with patch('sys.argv',['build_candidates.py',str(draw),'--output-roster',str(roster),'--context-prefix','candidate_'+batch+'_']):
                        build_candidates.main()
                    context=json.loads(roster.read_text())[0]
                    self.assertEqual(context['name'],'candidate_'+batch+'_00001')
                    self.assertTrue(Path(context['key']).exists())
                    self.assertTrue(Path(context['manifest']).exists())
            self.assertFalse((base/'candidate_contexts.json').exists())
            self.assertEqual(len(list(packs.glob('candidates/candidate_*'))),2)
    def test_same_class_hook_cannot_cross_split(self):
        cc=[self.candidate('old'),self.candidate('dev',split='dev'),self.candidate('test')]
        out,_=prod_adapter.adapt(cc,[self.readout(c) for c in cc])
        result=lf1.replace_flagged(['old'],out[:1],out[1:])
        self.assertEqual(result[0]['replacement_id'],'test')
        self.assertEqual(lf1.replace_flagged(['old'],out[:1],out[1:2])[0]['status'],'UNFILLED')
    def test_production_mapping_unresolved_and_void_twice(self):
        import prod_map
        with tempfile.TemporaryDirectory(dir=lf1.PACK_ROOT) as tmp:
            root=Path(tmp);key=root/'key.json'
            lf1.dump(key,dict(items={
                'a':dict(line_id='resolved',split='test',source='s',control=False,**{'class':'test|latin'}),
                'b':dict(line_id='missing',split='test',source='s',control=False,**{'class':'test|latin'}),
                'c':dict(control=True)}))
            contexts=[dict(name='c',key=str(key))]
            lf1.jsonl(root/'c.attempt1/verdicts.jsonl',[dict(card_id='a',verdict='OK')])
            result=prod_map.map_lines(contexts,[dict(context='c',attempt=1,status='VALID')],root)
            self.assertEqual([r['state'] for r in result],['RESOLVED','UNRESOLVED'])
            self.assertEqual(result[0]['verdict'],'OK');self.assertIsNone(result[1]['verdict'])
            result=prod_map.map_lines(contexts,[dict(context='c',attempt=i,status='VOID') for i in (1,2)],root)
            self.assertTrue(all(r['state']=='VOID_TWICE' and r['verdict'] is None for r in result))
    def test_finalize_explicit_partition(self):
        c=self.candidate();c['line_id']='r1'
        final,receipt=prod_finalize.finalize([c],[dict(line_id='r1',verdict='OK')])
        self.assertEqual([r['line_id'] for r in final],['r1'])
        self.assertEqual(receipt['summary'][0]['in_quota_OK'],1)

class FinalizeRulingTests(unittest.TestCase):
    def row(self,rid,order=1,source='s',split='test',cl='latin',sub=None,selected=None):
        if selected is None:selected=order==1
        return dict(parent_id='synthetic-parent',row_id=rid,line_id=rid,rank=999 if selected else 0,source=source,split=split,
                    **{'class':cl},quota_scope=':'.join([split,cl]+([sub] if sub else [])),
                    scope_rank=order,in_quota=selected,overdraw_order=None if selected else order)
    def run_final(self,cc,flags=()):
        vv=[dict(line_id=r['line_id'],verdict='CROP_VIOLATES' if r['line_id'] in flags else 'OK',reasons=['synthetic']) for r in cc]
        return prod_finalize.finalize(cc,vv)
    def test_finalizer_cli_receipt_v3_sha(self):
        with tempfile.TemporaryDirectory(dir=lf1.PACK_ROOT) as tmp:
            root=Path(tmp);cc=[self.row('a'),self.row('b',2)]
            lf1.jsonl(root/'v3.jsonl',cc)
            lf1.jsonl(root/'verdicts.jsonl',[dict(line_id='a',verdict='BAD',reasons=['synthetic']),dict(line_id='b',verdict='OK')])
            with patch('sys.argv',['prod_finalize.py','--candidates',str(root/'v3.jsonl'),
                    '--verdicts',str(root/'verdicts.jsonl'),'--output',str(root/'final.jsonl'),
                    '--receipt',str(root/'receipt.json')]):
                prod_finalize.main()
            receipt=json.loads((root/'receipt.json').read_text())
            self.assertEqual(receipt['candidates_sha256'],lf1.sha(root/'v3.jsonl'))
            details=json.loads((root/'receipt.json.details.json').read_text())
            self.assertEqual(details['replacements'][0]['flag_reason']['reasons'],['synthetic'])
            self.assertEqual(receipt['counts'],dict(flagged=1,REPLACED=1,UNFILLED=0))
            bindings=json.loads((root/'receipt.json.bindings.json').read_text())
            for item in bindings.values(): self.assertEqual(item['sha256'],lf1.sha(item['path']))
            self.assertEqual(lf1.rows(root/'final.jsonl')[0]['row_id'],'b')
    def test_explicit_boundary_ignores_rank_and_emission(self):
        f,r=self.run_final([self.row('reserve',2),self.row('selected',1)])
        self.assertEqual([x['line_id'] for x in f],['selected'])
    def test_explicit_order_ignores_scope_rank_and_rank(self):
        cc=[self.row('z',3),self.row('a',1),self.row('b',2)]
        cc[0]['scope_rank']=2;cc[2]['scope_rank']=3
        f,r=self.run_final(cc,['a'])
        self.assertEqual(f[0]['line_id'],'b');self.assertEqual(r['replacements'][0]['overdraw_order'],2)
    def test_same_source_despite_earlier_foreign_reserve(self):
        f,r=self.run_final([self.row('a'),self.row('other',2,'t'),self.row('same',3)],['a'])
        self.assertEqual(f[0]['line_id'],'same');self.assertEqual(r['replacements'][0]['status'],'REPLACED')
    def test_foreign_source_unfilled_and_flag_reason(self):
        f,r=self.run_final([self.row('a'),self.row('b',2,'t')],['a'])
        self.assertEqual(f,[]);self.assertEqual(r['replacements'][0]['status'],'UNFILLED')
        self.assertEqual(r['replacements'][0]['flag_reason']['reasons'],['synthetic'])
    def test_non_ok_reserve_used_never_promoted(self):
        f,r=self.run_final([self.row('a'),self.row('b',2),self.row('c',3)],['a','b'])
        self.assertEqual(f[0]['line_id'],'c');self.assertEqual(r['non_OK_reserve_used'][0]['line_id'],'b')
    def test_missing_reserve_verdict_used_never_promoted(self):
        f,r=prod_finalize.finalize([self.row('a'),self.row('missing',2),self.row('ok',3)],
            [dict(line_id='a',verdict='BAD'),dict(line_id='ok',verdict='OK')])
        self.assertEqual([x['line_id'] for x in f],['ok'])
        self.assertEqual(r['non_OK_reserve_used'],[dict(line_id='missing',verdict=None)])
    def test_split_isolation(self):
        f,r=self.run_final([self.row('a'),self.row('dev',2,split='dev')],['a'])
        self.assertEqual(f,[]);self.assertEqual(r['replacements'][0]['status'],'UNFILLED')
    def test_subgroup_isolation(self):
        f,r=self.run_final([self.row('a',cl='font_extremes',sub='small'),self.row('b',2,cl='font_extremes',sub='large')],['a'])
        self.assertEqual(f,[]);self.assertEqual(r['replacements'][0]['status'],'UNFILLED')
    def test_missing_fields_stop_with_row_no_rank_fallback(self):
        for field in prod_adapter.DRAW_FIELDS:
            c=self.row('missing');del c[field]
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'missing'):
                self.run_final([c])
    def test_unresolved_void_twice_separate_and_unique_use(self):
        cc=[self.row('a'),self.row('b',2,selected=True),self.row('c',3)]
        f,r=prod_finalize.finalize(cc,[dict(line_id='b',verdict=None,state='VOID_TWICE'),dict(line_id='c',verdict='OK')])
        self.assertEqual(len(f),1);self.assertEqual(f[0]['line_id'],'c')
        self.assertEqual(r['summary'][0]['unresolved'],1);self.assertEqual(r['summary'][0]['VOID_TWICE'],1)
        self.assertEqual(r['summary'][0]['UNFILLED'],1)
    def test_zero_reserve_every_flagged_line_unfilled(self):
        cc=[self.row('a'),self.row('b',2,selected=True),self.row('ok',3,selected=True)]
        f,r=self.run_final(cc,['a','b'])
        self.assertEqual([x['line_id'] for x in f],['ok'])
        self.assertEqual([x['status'] for x in r['replacements']],['UNFILLED','UNFILLED'])
    def test_only_literal_ok_passes_and_reserves_are_blocked(self):
        for verdict in ('BAD','ok','',None):
            with self.subTest(verdict=verdict):
                f,r=prod_finalize.finalize([self.row('a'),self.row('b',2)],
                    [dict(line_id=x,verdict=verdict) for x in ('a','b')])
                self.assertEqual(f,[]);self.assertEqual(r['replacements'][0]['status'],'UNFILLED')
                self.assertEqual(r['non_OK_reserve_used'][0]['line_id'],'b')
    def test_explicit_scope_validation(self):
        for updates in (dict(quota_scope='dev:latin'),dict(in_quota=1),dict(scope_rank=0),dict(overdraw_order=2)):
            with self.subTest(updates=updates),self.assertRaises(ValueError):
                self.run_final([dict(self.row('invalid'),**updates)])
    def test_unique_replacement_and_unfilled_after_same_source_exhaustion(self):
        cc=[self.row('a'),self.row('b',2,selected=True),self.row('same',3),self.row('other',4,'t')]
        f,r=self.run_final(cc,['a','b'])
        self.assertEqual([x['line_id'] for x in f],['same'])
        self.assertEqual([x['status'] for x in r['replacements']],['REPLACED','UNFILLED'])

if __name__=='__main__':unittest.main(verbosity=2)
