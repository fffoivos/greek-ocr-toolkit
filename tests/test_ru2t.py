"""Offline fixtures only: synthetic glyph PNGs/answers, never real readings."""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru2t as m
from PIL import Image


def row(i,label,**kw):
    return dict(id=i,label=label,source='fixture',doc='book',script_class='cyrillic',crop='',attribution='',**kw)


class PackRootTests(unittest.TestCase):
    def test_builder_refuses_git_worktree_before_reading_inputs(self):
        with tempfile.TemporaryDirectory(prefix='ru2t-root-') as tmp:
            root=Path(tmp)
            for marker_kind in ('directory','file'):
                with self.subTest(marker_kind=marker_kind):
                    repo=root/marker_kind;repo.mkdir()
                    marker=repo/'.git'
                    if marker_kind=='directory':marker.mkdir()
                    else:marker.write_text('gitdir: /unread/git/worktrees/fixture\n')
                    pack=repo/'not-created'/'packs'
                    with patch.object(m,'check_scanner') as scanner, patch.object(m,'sha') as digest:
                        with self.assertRaisesRegex(ValueError,'outside every git worktree'):
                            m.build(root/'missing-source',root/'art',pack)
                        scanner.assert_not_called();digest.assert_not_called()
                    self.assertFalse(pack.exists())

    def test_symlink_into_worktree_refused(self):
        with tempfile.TemporaryDirectory(prefix='ru2t-root-') as tmp:
            root=Path(tmp);repo=root/'repo';repo.mkdir();(repo/'.git').mkdir()
            alias=root/'alias';alias.symlink_to(repo,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'outside every git worktree'):
                m.require_external_pack_root(alias/'packs')

    def test_external_nonexistent_root_allowed(self):
        with tempfile.TemporaryDirectory(prefix='ru2t-root-') as tmp:
            pack=Path(tmp)/'new'/'packs'
            m.require_external_pack_root(pack)
            self.assertFalse(pack.exists())


class TextTests(unittest.TestCase):
    def test_cyrillic_selection(self):
        data=[row('a','abc'),row('b','абв'),row('c','аб')]
        for r in data:r['script_class']='latin'
        self.assertEqual([r['id'] for r in m.census(data)[0]],['b'])
    def test_class_threshold(self):
        for label,want in [('аъ '*4,'modern'),('аъ '*5,'pre_reform'),('ѣ','pre_reform'),('І','pre_reform'),('Ѳ','pre_reform'),('Ѵ','pre_reform')]:
            with self.subTest(label=label):self.assertEqual(next(iter(m.census([row('a',label)])[1].values()))['orthography'],want)
    def test_modern_excluded(self):
        self.assertEqual(m.census([row('a','конь')])[3],[])
    def test_hyphen_and_hard(self):
        c=m.census([row('a','ѣ конь конь- домъ')])[3]
        self.assertEqual([p['kind'] for p in c],['final','pre_hyphen']);self.assertEqual(len(c),2)
    def test_stratification(self):
        pp=[dict(book=f'b{b}',row_id=f'{b}-{i}') for b in range(9) for i in range(30+b*10)]
        a,q=m.stratified(pp,200);self.assertEqual(len(set(a)),200);self.assertEqual(sum(q.values()),200);self.assertTrue(all(q.values()));self.assertEqual(a,m.stratified(pp,200)[0])
    def decision(self,calls,gates=('VALID','VALID'),kind='final'):
        p=dict(row_id='a',source_id='a',google='ь',offset=3,kind=kind,control=False,prior='unknown')
        votes=[dict(reader=r,context='ctx04/'+r,call=c,gate_status=g,confidence='high',item_id=r) for r,c,g in zip(['r1','r2'],calls,gates)]
        return m.combine_position(p,votes)
    def test_vote_matrix(self):
        for a in ['ъ','ь','u','other']:
            for b in ['ъ','ь','u','other']:
                with self.subTest(a=a,b=b):self.assertEqual(self.decision([a,b])['decision'],'edit_hard' if a==b=='ъ' else 'keep_soft' if a==b=='ь' else 'hold')
    def test_void_gate(self):
        self.assertEqual(self.decision(['ъ','ъ'],['VOID','VOID'])['decision'],'hold')
        self.assertEqual(self.decision(['ъ','ъ'],['VALID','VOID'])['decision'],'edit_hard')
    def test_hyphen_owner_scope(self):
        self.assertEqual(self.decision(['ъ','ъ'],kind='pre_hyphen')['kind'],'pre_hyphen')
    def test_missing_read_hold(self):
        d=m.combine_position(dict(row_id='a',source_id='a',google='ь',offset=0,kind='final',control=False),[])
        self.assertEqual(d['decision'],'hold')
    def test_full_output_and_counts(self):
        ds=[self.decision(['ъ','ъ'])];data=[row('a','конь домъ'),row('b','конь')]
        out,cc=m.apply_version(data,ds);self.assertEqual(out,[dict(id='a',label='конъ домъ',status='ok',holds=[]),dict(id='b',label='конь',status='ok',holds=[])]);self.assertEqual(cc[0]['decisions'],{'edit_hard':1});self.assertFalse(cc[1]['changed'])
    def test_parent_mismatch_refused(self):
        with self.assertRaises(ValueError):m.apply_version([row('a','конъ')],[self.decision(['ъ','ъ'])])
    def test_scanner_pin(self):m.check_scanner()


class FinalizeFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ru2t-fixture-');self.root=Path(self.tmp.name);self.art=self.root/'art';self.pack=self.root/'pack'
        image=self.root/'glyph.png';Image.new('RGB',(13,8),'white').save(image)
        self.source=self.root/'parent.jsonl';m.jsonl(self.source,[row('fixture-parent-line-0001','ѣ конь домъ конь-',crop_unused=None)])
        data=list(m.rows(self.source));data[0]['crop']=str(image);m.jsonl(self.source,data)
        with patch.object(m,'controls',return_value=m.controls()):m.build(self.source,self.art,self.pack)
        self.registry=self.root/'versions.json';m.dump(self.registry,dict(schema='lqb-versions-v1',versions={'existing':dict(status='local')}))
        self.output=self.root/'ru1_v2_train.jsonl'
        for rd in self.pack.glob('ctx*/r[12]'):
            stem=rd.parent.name+('' if rd.name=='r1' else '.r2');key=json.loads((self.art/f'keys/{stem}.json').read_text());items=list(m.rows(rd/'items.jsonl'));answers=[];records=[dict(type='turn_context',payload=dict(model='gpt-6.1-sol',effort='medium',reader=rd.name))]
            for j,i in enumerate(items):
                meta=key['items'][i['item_id']]
                answers.append(dict(item_id=i['item_id'],slots={str(n):s['control_truth'] if meta['control'] else 'ъ' for n,s in enumerate(meta['slots'],1)},confidence={str(n):'high' for n in range(1,i['slots']+1)},unmarked_final_hard_signs=[],pre1918='yes',note='synthetic fixture'))
                records.extend([dict(payload=dict(type='function_call',name='view_image',call_id=f'v{j}',arguments=json.dumps(dict(path=i['crop'])))),dict(payload=dict(type='function_call_output',call_id=f'v{j}',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode((rd/i['crop']).read_bytes()).decode())]))])
            m.jsonl(rd/'answers.jsonl',answers);rollout=self.root/(stem+'.rollout.jsonl');m.jsonl(rollout,records)
            m.dump(self.art/f'answers/{stem}.run.json',dict(rc=0,model='gpt-6.1-sol',rollout=str(rollout)))
    def tearDown(self):self.tmp.cleanup()
    def finish(self):return m.finalize(self.art,self.pack,self.source,self.registry,self.output)
    def test_end_to_end_scanner_mapping_combiner_registration(self):
        x=self.finish();self.assertEqual(x['counts'],{'edit_hard':2});self.assertEqual(list(m.rows(self.output))[0]['label'],'ѣ конъ домъ конъ-')
        from greekocr.labelfix.lqb import load_version
        registry=json.loads(self.registry.read_text());self.assertEqual(load_version('ru1_v2_train',registry)['fixture-parent-line-0001'],'ѣ конъ домъ конъ-')
        v=registry['versions'];self.assertIn('existing',v);self.assertEqual(v['ru1_v2_train']['parent'],'collection_v2_train');self.assertEqual(v['ru1_v2_train']['sha256'],m.sha(self.output))
    def test_direct_view_coverage(self):
        result=self.finish()
        for cov in result['coverage'].values():
            self.assertEqual(cov['direct'],cov['assigned_crops'])
            self.assertEqual((cov['derived'],cov['unviewed']),(0,0))

    def replace_bed_view(self, derived=False, late=False, mention=False):
        rd=self.pack/'ctx01/r2';items=list(m.rows(rd/'items.jsonl'))
        key=json.loads((self.art/'keys/ctx01.r2.json').read_text())
        j=next(n for n,i in enumerate(items) if not key['items'][i['item_id']]['control'])
        item=items[j];path=self.root/'ctx01.r2.rollout.jsonl';rr=list(m.rows(path))
        start=1+2*j;del rr[start:start+2]
        if derived:
            from PIL import ImageOps
            dest=rd/'zoom/montage.png';dest.parent.mkdir(exist_ok=True)
            with Image.open(rd/item['crop']) as im:
                tile=ImageOps.expand(im,border=3,fill='black')
                montage=Image.new('RGB',(tile.width*2,tile.height),'gray')
                montage.paste(tile,(0,0));montage.paste(tile,(tile.width,0));montage.save(dest)
            # Two literal image operands: a montage, not a path-name heuristic.
            cmd='magick '+item['crop']+' -bordercolor black -border 3x3 '+item['crop']+' -bordercolor black -border 3x3 +append zoom/montage.png'
            command=dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd=cmd))))
            view=[dict(payload=dict(type='function_call',name='view_image',call_id='montage',arguments=json.dumps(dict(path='zoom/montage.png')))),dict(payload=dict(type='function_call_output',call_id='montage',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(dest.read_bytes()).decode())]))]
            rr[start:start]=view+[command] if late else [command]+view
        if mention:
            rr.append(dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd='echo '+item['crop'])))))
        m.jsonl(path,rr)
        return item

    def test_derived_montage_coverage(self):
        self.replace_bed_view(derived=True)
        result=self.finish();cov=result['coverage']['ctx01/r2']
        self.assertEqual((cov['derived'],cov['unviewed']),(1,0))
        self.assertEqual(result['counts'],{'edit_hard':2})
        self.assertTrue(any(e.get('images') for e in cov['replay_log']))

    def test_unviewed_item_only_dropped(self):
        item=self.replace_bed_view(mention=True)
        result=self.finish();cov=result['coverage']['ctx01/r2']
        self.assertEqual((cov['derived'],cov['unviewed']),(0,1))
        self.assertEqual(cov['dropped_items'],[item['item_id']])
        self.assertEqual(result['counts'],{'hold':2})
        kept=list(m.rows(self.art/'answers/ctx01.r2.mapped.jsonl'))
        self.assertTrue(kept);self.assertTrue(all(p['control'] for p in kept))
        for d in m.rows(self.art/'decisions.jsonl'):
            self.assertIsNotNone(d['reads']['r1']);self.assertIsNone(d['reads']['r2'])
            self.assertEqual(d['reason'],'missing_independent_reads')
        saved=list(m.rows(self.output))[0]
        self.assertEqual(saved['label'],'ѣ конь домъ конь-')
        self.assertEqual(saved['status'],'hold');self.assertEqual(len(saved['holds']),2)

    def test_post_view_command_not_coverage(self):
        self.replace_bed_view(derived=True,late=True)
        self.assertEqual(self.finish()['coverage']['ctx01/r2']['unviewed'],1)

    def test_ctx02_r3_routing_never_consumes_void_r2(self):
        self.check_r3_routing('ctx02')

    def test_ctx03_r3_routing_never_consumes_void_r2(self):
        self.check_r3_routing('ctx03')

    def check_r3_routing(self, context):
        # Turn the synthetic one-context fixture into {context}, preserving all bindings.
        old=self.pack/'ctx01';new=self.pack/context;old.rename(new)
        for reader in ('r1','r2'):
            a=m.reader_stem('ctx01',reader);b=m.reader_stem(context,reader)
            kp=self.art/f'keys/{a}.json';key=json.loads(kp.read_text());key['context']=context
            kp.unlink();m.dump(self.art/f'keys/{b}.json',key)
            (self.art/f'answers/{a}.run.json').rename(self.art/f'answers/{b}.run.json')
        info=json.loads((self.art/'build.json').read_text());info['contexts'][0]['context']=context
        info['pack_inputs']={str(p).replace(str(old),str(new)).replace('/keys/ctx01',f'/keys/{context}'):h for p,h in info['pack_inputs'].items()}
        info['pack_inputs']={p:m.sha(p) for p in info['pack_inputs']}
        m.dump(self.art/'build.json',info)
        receipt=m.build_r3(context,self.art,self.pack)
        self.assertTrue(receipt['closure_ok'])
        self.assertEqual(m.accepted_readers(context),('r1','r3'))
        self.assertEqual(m.accepted_readers('ctx01'),('r1','r2'))
        rd=new/'r3';items=list(m.rows(rd/'items.jsonl'))
        orig=list(m.rows(new/'r1/items.jsonl'));expected=list(orig)
        m.random.Random(m.R3_SEEDS[context]).shuffle(expected)
        self.assertEqual([{k:v for k,v in i.items() if k!='item_id'} for i in items],
                         [{k:v for k,v in i.items() if k!='item_id'} for i in expected])
        key=json.loads((self.art/f'keys/{context}.r3.json').read_text())
        oldkey=json.loads((self.art/f'keys/{context}.json').read_text())
        self.assertEqual(sorted(map(str,key['items'].values())),sorted(map(str,oldkey['items'].values())))
        self.assertFalse(set(key['items']) & set(oldkey['items']))
        answers={a['item_id']:a for a in m.rows(new/'r1/answers.jsonl')}
        bycrop={i['crop']:answers[i['item_id']] for i in orig}
        m.jsonl(rd/'answers.jsonl',[dict(bycrop[i['crop']],item_id=i['item_id']) for i in items])
        rollout=self.root/'r3.rollout.jsonl'
        rr=list(m.rows(self.root/'ctx01.rollout.jsonl'));rr[0]['payload']['reader']='r3'
        m.jsonl(rollout,rr)
        m.dump(self.art/f'answers/{context}.r3.run.json',dict(rc=0,model='gpt-6.1-sol',rollout=str(rollout)))
        # Poison VOID run evidence: any attempt to use it would fail immediately.
        (self.art/f'answers/{context}.r2.run.json').write_text('VOID: must never parse')
        real_scan=m.scan_rollout.inspect
        with patch.object(m.scan_rollout,'inspect',wraps=real_scan) as scanner:
            result=self.finish()
        self.assertEqual(result['counts'],{'edit_hard':2})
        for decision in m.rows(self.art/'decisions.jsonl'):
            self.assertEqual(set(decision['reads']),{'r1','r3'})
            self.assertEqual(decision['reads']['r3']['context'],f'{context}/r3')
        self.assertEqual([call.args[1].name for call in scanner.call_args_list],['r1','r3'])
        self.assertFalse(any(f'{context}.r2' in p for p in result['evidence']))
        self.assertFalse(any('/r2/' in p for p in result['evidence']))
        # r2 must never be a fallback when r3 is missing.
        (self.art/f'answers/{context}.r3.run.json').unlink()
        with self.assertRaises(FileNotFoundError):self.finish()

    def test_missing_run_refused_before_output(self):
        next((self.art/'answers').glob('*.run.json')).unlink()
        with self.assertRaises(FileNotFoundError):self.finish()
        self.assertFalse(self.output.exists());self.assertNotIn('ru1_v2_train',json.loads(self.registry.read_text())['versions'])
    def test_parent_mutation_refused(self):
        self.source.write_text(self.source.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'parent changed'):self.finish()
    def test_pack_mutation_refused(self):
        next(self.pack.glob('ctx*/r1/items.jsonl')).write_text('{}\n')
        with self.assertRaisesRegex(ValueError,'bound pack changed'):self.finish()
    def test_unreadable_holds(self):
        p=next(self.pack.glob('ctx*/r2/answers.jsonl'));aa=list(m.rows(p))
        key=json.loads((self.art/'keys/ctx01.r2.json').read_text())
        for a in aa:
            if not key['items'][a['item_id']]['control']:a['slots']={k:'u' for k in a['slots']}
        m.jsonl(p,aa);self.assertEqual(self.finish()['counts'],{'hold':2});self.assertEqual(list(m.rows(self.output))[0]['label'],'ѣ конь домъ конь-')
    def test_forbidden_rollout_refused(self):
        p=next(self.root.glob('*.rollout.jsonl'));rr=list(m.rows(p));rr.append(dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd='cat ../keys/private.json')))));m.jsonl(p,rr)
        with self.assertRaisesRegex(ValueError,'unclean canonical scan'):self.finish()
    def test_wrong_model_refused(self):
        p=next(self.root.glob('*.rollout.jsonl'));rr=list(m.rows(p));rr[0]['payload']['model']='other';m.jsonl(p,rr)
        with self.assertRaisesRegex(ValueError,'model/effort mismatch'):self.finish()
    def test_independence_refused(self):
        a=self.art/'answers/ctx01.run.json';b=self.art/'answers/ctx01.r2.run.json';b.write_bytes(a.read_bytes())
        with self.assertRaisesRegex(ValueError,'reuse rollout'):self.finish()
    def test_omitted_answer_refused(self):
        p=next(self.pack.glob('ctx*/r2/answers.jsonl'));m.jsonl(p,list(m.rows(p))[:-1])
        with self.assertRaisesRegex(ValueError,'answer count'):self.finish()

if __name__=='__main__':unittest.main()
