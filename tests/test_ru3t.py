"""Offline RU3T fixtures: synthetic pixels and answers, no model/probe/network."""
import base64, copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru3t as m
import ru3t_driver as driver
from PIL import Image, ImageOps

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ru3t-fixture-');self.root=Path(self.tmp.name)
        self.art=self.root/'art';self.pack=self.root/'packs';self.old=self.root/'old';self.source=self.root/'source.jsonl';self.prior=self.root/'prior.jsonl';self.registry=self.root/'registry.json';self.output=self.root/'v3.jsonl'
        image=self.root/'glyph.png';Image.new('RGB',(13,8),'white').save(image)
        data=[dict(id=i,label='ѣ конь домъ конь-',source='fixture',doc='book',script_class='cyrillic',crop=str(image)) for i in ['old-line-0001','new-line-0002','new-line-0003']]
        for j,r in enumerate(data):
            path=self.root/f'bed{j}.png';Image.new('RGB',(15+j,8),'white').save(path);r['crop']=str(path)
        m.jsonl(self.source,data)
        oldp=dict(id=data[0]['id'],label='ѣ конъ домъ конь-',status='hold',holds=[dict(offset=15,reason='frozen_lead')])
        m.jsonl(self.prior,[oldp]+[dict(id=r['id'],label=r['label'],status='ok',holds=[]) for r in data[1:]])
        candidates=m.census(data)[3];olddec=[dict(p,source_id=p['row_id'],decision='hold',reason='frozen_lead') for p in candidates if p['row_id']==data[0]['id']]
        m.jsonl(self.old/'decisions.jsonl',olddec);m.jsonl(self.old/'selected_lines.jsonl',[dict(row_id=data[0]['id'])]);m.dump(self.old/'build.json',dict(parent_sha256=m.sha(self.source)))
        masked,slots=m.mask('конь домъ конь домъ')
        for s in slots:s.update(prior='unknown',control_truth=s['google'])
        pool=[dict(control=True,row_id='control-line-000001',source_id='control-line-000001',book='fixture:book',slots=slots,masked_text=masked,source_crop_sha256=m.sha(image),image=str(image))]
        with patch.object(m,'controls',return_value=pool):m.build(self.source,self.art,self.pack,self.prior,self.old,m.sha(self.prior))
        m.dump(self.registry,dict(versions={}))
        for ctx,r in driver.plan(json.loads((self.art/'build.json').read_text())):self.reader(ctx,r)
    def tearDown(self):self.tmp.cleanup()
    def reader(self,ctx,r):
        rd=self.pack/ctx/r;stem=m.reader_stem(ctx,r);key=json.loads((self.art/f'keys/{stem}.json').read_text());items=list(m.rows(rd/'items.jsonl'));records=[dict(type='turn_context',payload=dict(model='gpt-6.1-sol',effort='medium',reader=r))];answers=[]
        for j,i in enumerate(items):
            meta=key['items'][i['item_id']]
            answers.append(dict(item_id=i['item_id'],slots={str(n):s['control_truth'] if meta['control'] else 'ъ' for n,s in enumerate(meta['slots'],1)},confidence={str(n):'high' for n in range(1,i['slots']+1)},unmarked_final_hard_signs=[],pre1918='yes',note='synthetic'))
            records.extend([dict(payload=dict(type='function_call',name='view_image',call_id=f'v{j}',arguments=json.dumps(dict(path=i['crop'])))),dict(payload=dict(type='function_call_output',call_id=f'v{j}',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode((rd/i['crop']).read_bytes()).decode())]))])
        m.jsonl(rd/'answers.jsonl',answers);roll=self.root/(stem+'.rollout.jsonl');m.jsonl(roll,records);m.dump(self.art/f'answers/{stem}.run.json',dict(rc=0,model='gpt-6.1-sol',rollout=str(roll)))
    def finish(self):return m.finalize(self.art,self.pack,self.source,self.registry,self.output)
    def mutate_answers(self,fn):
        p=self.pack/'ctx01/r2/answers.jsonl';aa=list(m.rows(p));key=json.loads((self.art/'keys/ctx01.r2.json').read_text())
        for a in aa:fn(a,key['items'][a['item_id']])
        m.jsonl(p,aa)
    def test_complete_merge_frozen_old_and_parent(self):
        x=self.finish();self.assertEqual(x['counts'],{'edit_hard':4});out=list(m.rows(self.output));self.assertEqual(out[0],list(m.rows(self.prior))[0]);self.assertEqual(out[1]['label'],'ѣ конъ домъ конъ-');self.assertTrue(self.output.with_suffix('.sha256').exists());v=json.loads(self.registry.read_text())['versions'];self.assertEqual(v['ru1_v3_train']['parent'],'collection_v2_train');self.assertEqual(x['output']['sha256'],m.sha(self.output))
    def test_selection_excludes_ru2t_and_reverse(self):
        self.assertEqual({r['row_id'] for r in m.rows(self.art/'selected_lines.jsonl')},{'new-line-0002','new-line-0003'})
        a=list(m.rows(self.pack/'ctx01/r1/items.jsonl'));b=list(m.rows(self.pack/'ctx01/r2/items.jsonl'));strip=lambda i:{k:v for k,v in i.items() if k!='item_id'}
        self.assertEqual(list(map(strip,a)),list(map(strip,reversed(b))));self.assertFalse({i['item_id'] for i in a}&{i['item_id'] for i in b});self.assertLessEqual(len(a),100)
    def test_void_drops_all_votes(self):
        def mutate(a,meta):
            if meta['control']:a['slots']={k:'other' for k in a['slots']}
        self.mutate_answers(mutate);x=self.finish();self.assertEqual(x['counts'],{'lead_review':4});self.assertEqual(x['contexts']['ctx01/r2']['status'],'VOID');self.assertEqual(x['fresh_r3_positions'],4)
        self.assertTrue(all(d['reads']['r2'] is None for d in m.rows(self.art/'decisions.jsonl')))
    def test_soft_void_cannot_keep(self):
        def mutate(a,meta):a['slots']={k:'other' if meta['control'] else 'ь' for k in a['slots']}
        self.mutate_answers(mutate);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_missing_run_to_review(self):
        (self.art/'answers/ctx01.r2.run.json').unlink();x=self.finish();self.assertEqual(x['counts'],{'lead_review':4});self.assertEqual(x['contexts']['ctx01/r2']['status'],'FAILED')
    def test_failed_rc_to_review(self):
        p=self.art/'answers/ctx01.r2.run.json';r=json.loads(p.read_text());r['rc']=2;m.dump(p,r);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_wrong_model_to_review(self):
        p=self.root/'ctx01.r2.rollout.jsonl';r=list(m.rows(p));r[0]['payload']['model']='other';m.jsonl(p,r);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_forbidden_rollout_to_review(self):
        p=self.root/'ctx01.r2.rollout.jsonl';r=list(m.rows(p));r.append(dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd='cat ../keys/private.json')))));m.jsonl(p,r);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_reused_rollout_to_review(self):
        (self.art/'answers/ctx01.r2.run.json').write_bytes((self.art/'answers/ctx01.run.json').read_bytes());self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_missing_answer_to_review(self):
        p=self.pack/'ctx01/r2/answers.jsonl';m.jsonl(p,list(m.rows(p))[:-1]);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_disagreement_review(self):
        self.mutate_answers(lambda a,p:a.update(slots={k:'ь' for k in a['slots']}) if not p['control'] else None);self.assertEqual(self.finish()['counts'],{'lead_review':4})
    def test_parent_tamper_fails(self):
        self.source.write_text(self.source.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'bound input changed'):self.finish()
    def test_pack_tamper_fails(self):
        p=self.pack/'ctx01/r1/items.jsonl';p.write_text('{}\n')
        with self.assertRaisesRegex(ValueError,'bound input changed'):self.finish()
    def test_partial_filename_and_covered(self):
        m.dump(self.art/'STOPPED_AT_70.json',dict(contexts_done=['ctx01/r1']))
        # Remove r2: only the frozen RU2T line is fully covered.
        (self.art/'answers/ctx01.r2.run.json').unlink();x=self.finish();self.assertEqual(x['version'],'ru1_v3_train_partial');self.assertEqual((self.art/'covered_lines.txt').read_text(),'old-line-0001\n');self.assertIn('ru1_v3_train_partial',json.loads(self.registry.read_text())['versions'])
    def test_direct_coverage(self):
        for cov in self.finish()['coverage'].values():self.assertEqual((cov['derived'],cov['unviewed']),(0,0))
    def remove_view(self,derived=False):
        rd=self.pack/'ctx01/r2';items=list(m.rows(rd/'items.jsonl'));key=json.loads((self.art/'keys/ctx01.r2.json').read_text());j=next(n for n,i in enumerate(items) if not key['items'][i['item_id']]['control']);item=items[j]
        p=self.root/'ctx01.r2.rollout.jsonl';rr=list(m.rows(p));start=1+2*j;del rr[start:start+2]
        if derived:
            dest=rd/'zoom/montage.png';dest.parent.mkdir();
            with Image.open(rd/item['crop']) as im:
                tile=ImageOps.expand(im,border=3,fill='black');montage=Image.new('RGB',(tile.width*2,tile.height),'gray');montage.paste(tile,(0,0));montage.paste(tile,(tile.width,0));montage.save(dest)
            cmd='magick '+item['crop']+' -bordercolor black -border 3x3 '+item['crop']+' -bordercolor black -border 3x3 +append zoom/montage.png'
            rr.extend([dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd=cmd)))),dict(payload=dict(type='function_call',name='view_image',call_id='montage',arguments=json.dumps(dict(path='zoom/montage.png')))),dict(payload=dict(type='function_call_output',call_id='montage',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(dest.read_bytes()).decode())]))])
        m.jsonl(p,rr)
    def test_derived_montage_coverage(self):
        self.remove_view(True);x=self.finish();self.assertEqual(x['coverage']['ctx01/r2']['derived'],1);self.assertEqual(x['counts'],{'edit_hard':4})
    def test_unviewed_dropped(self):
        self.remove_view();x=self.finish();self.assertGreater(x['coverage']['ctx01/r2']['unviewed'],0);self.assertEqual(x['counts'],{'edit_hard':2,'lead_review':2});self.assertEqual(x['contexts']['ctx01/r2']['status'],'VALID')

class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.art=Path(self.tmp.name)/'art';self.pack=Path(self.tmp.name)/'pack';self.art.mkdir();self.info=dict(contexts=[dict(context='ctx01'),dict(context='ctx02')]);self.validate=patch.object(m,'validate',return_value=self.info);self.validate.start()
    def tearDown(self):self.validate.stop();self.tmp.cleanup()
    def run_driver(self,used,runner=None,dry=False):
        return driver.drive(self.art,self.pack,dry,runner or (lambda *a,**k:subprocess.CompletedProcess(a,0,'{"rc":0}\n','')),lambda *a,**k:f'limit_id=codex primary={used}%/10080m reset ?')
    def test_dry_run_no_probe_or_launch(self):
        def fail(*a,**k):raise AssertionError('live call')
        self.assertEqual(driver.drive(self.art,self.pack,True,fail,fail),0);self.assertFalse((self.art/'answers').exists())
    def test_resume_dry_run_omits_done_and_preserves_claims(self):
        import io
        from contextlib import redirect_stdout
        m.dump(self.art/'answers/ctx01.run.json',dict(rc=0))
        m.dump(self.art/'answers/ctx02.attempt.json',dict(status='CLAIMED'))
        def fail(*a,**k):raise AssertionError('live call')
        output=io.StringIO()
        with redirect_stdout(output):driver.drive(self.art,self.pack,True,fail,fail)
        self.assertEqual([(x['context'],x['reader']) for x in map(json.loads,output.getvalue().splitlines())],[('ctx01','r2'),('ctx02','r2')])
    def test_order_and_no_repeats(self):
        calls=[]
        def run(cmd,**kw):calls.append(cmd[-2:]);return subprocess.CompletedProcess(cmd,0,'result\n','')
        self.run_driver(69,run);self.run_driver(69,run);self.assertEqual(calls,[['ctx01','r1'],['ctx02','r1'],['ctx01','r2'],['ctx02','r2']]);self.assertEqual(len(list(m.rows(self.art/'context_results.jsonl'))),4)
    def test_stop_at_exact70_and_above(self):
        self.run_driver(70);stop=json.loads((self.art/'STOPPED_AT_70.json').read_text());self.assertEqual(stop['contexts_done'],[]);self.assertEqual(stop['next_context'],'ctx01/r1');self.assertFalse((self.art/'answers/ctx01.attempt.json').exists())
    def test_stop_after_first_records_done(self):
        probes=iter([69,70])
        driver.drive(self.art,self.pack,False,lambda *a,**kw:subprocess.CompletedProcess(a,0,'done',''),lambda *a,**kw:f'primary={next(probes)}%/10080m')
        self.assertEqual(json.loads((self.art/'STOPPED_AT_70.json').read_text())['contexts_done'],['ctx01/r1'])
    def test_failed_context_not_retried(self):
        calls=[]
        def run(cmd,**kw):calls.append(cmd);return subprocess.CompletedProcess(cmd,3,'','failure')
        self.run_driver(69,run);self.run_driver(69,run);self.assertEqual(len(calls),4)
    def test_claimed_after_crash_not_retried(self):
        m.dump(self.art/'answers/ctx01.attempt.json',dict(status='CLAIMED'));calls=[]
        def run(cmd,**kw):calls.append(cmd[-2:]);return subprocess.CompletedProcess(cmd,0,'ok','')
        self.run_driver(69,run);self.assertEqual(len(calls),3);self.assertNotIn(['ctx01','r1'],calls)
    def test_missing_weekly_bucket_fails_closed(self):
        with self.assertRaises(ValueError):driver.drive(self.art,self.pack,False,lambda *a,**k:None,lambda *a,**k:'NONE')
    def test_in_repo_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)/'repo';repo.mkdir();(repo/'.git').mkdir()
            with self.assertRaisesRegex(ValueError,'outside every git worktree'):m.require_external_pack_root(repo/'tmp_packs')


class DeliveryTests(unittest.TestCase):
    def test_review_and_seeded_40_20_audit_with_same_book_references(self):
        import ru3t_delivery as delivery
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);art=root/'art';out=root/'review';keys={};decisions=[]
            for n in range(63):
                rid=f'fixture-row-{n:04}';iid=f'k{n:010x}';decision='edit_hard' if n<41 else 'keep_soft' if n<62 else 'lead_review';call='ъ' if n<41 else 'ь'
                keys[iid]=dict(control=False,row_id=rid,book='fixture:book',slots=[dict(offset=3,google='ь')])
                decisions.append(dict(row_id=rid,offset=3,decision=decision,reads={r:dict(reader=r,context='ctx01/'+r,call=call) for r in ['r1','r2']} if n<62 else dict(r1=None,r2=None)))
            m.dump(art/'build.json',dict(contexts=[dict(context='ctx01')]))
            m.dump(art/'keys/ctx01.json',dict(items=keys));m.jsonl(art/'decisions.jsonl',decisions)
            class Crops:
                parent={}
                def get(self,*args):return dict(line=Image.new('RGB',(40,8),'white'),word=Image.new('RGB',(20,8),'white'),final=Image.new('RGB',(3,8),'white'),geometry={'fixture':True},crop_sha256='a'*64)
            with patch.object(m,'ART',art),patch.object(delivery,'OUT',out),patch.object(delivery,'Crops',Crops):
                result=delivery.build_sheets();first=json.loads((out/'sheets_index.json').read_text());again=delivery.build_sheets();second=json.loads((out/'sheets_index.json').read_text())
            self.assertEqual((result['review_cells'],result['audit_cells']),(1,60));self.assertEqual(result['audit_shortfall'],dict(edit_hard=0,keep_soft=0));self.assertEqual(first,second)
            self.assertEqual(len(list(out.glob('audit_*.png'))),6);self.assertEqual(len(list(out.glob('review_*.png'))),1)
            refs=json.loads((out/'references.json').read_text());self.assertTrue(all(r['book']=='fixture:book' and r['basis']=='agreement' for r in refs['fixture:book'].values()))
    def test_lqb_offline_command_version_and_truth(self):
        import ru3t_delivery as delivery
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);truth=work/'docs/records/labelfix/lqb/truth_v1_1.jsonl';m.jsonl(truth,[])
            target=truth.parent/'score_ru1_v3_train_partial.json';m.dump(target,dict(paired={'collection_v2_train→ru1_v3_train_partial':{'fixture':True}}))
            with patch.object(m,'WORK',work),patch.object(m,'ART',work/'art'),patch.object(delivery.subprocess,'run') as run:
                result=delivery.score_lqb(dict(version='ru1_v3_train_partial'))
            self.assertTrue(result['registered']);cmd=run.call_args.args[0];self.assertIn('trend',cmd);self.assertIn(str(truth),cmd);self.assertTrue(run.call_args.kwargs['check'])

if __name__=='__main__':unittest.main()
