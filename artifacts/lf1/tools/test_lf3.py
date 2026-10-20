"""Offline synthetic LF3 authorization, custody, prompt and finalization tests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import build
import build_vertical
import lf1
import prod_map
import prod_finalize
import run

BLOCK='This class is printed vertically. Judge after mentally reading along the text direction. Flag only clipping, more than one line, more than 2 whole neighbour words, or text that differs from the ink.'


def candidate(rid, selected=True, source='s', cl='vertical_turned'):
    return dict(parent_id='SYNTHETIC',row_id=rid,line_id=rid,source=source,split='test',
        **{'class':cl},quota_scope='test:'+cl,scope_rank=1 if selected else 2,
        in_quota=selected,overdraw_order=None if selected else 1)


class ExtraAttemptTests(unittest.TestCase):
    def test_named_extra_only_and_history(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)):
            c=dict(name='candidate_w2_00004')
            for i in (1,2):lf1.dump(Path(tmp)/f'runs/{c["name"]}.attempt{i}/receipt.json',dict(context=c['name'],attempt=i,status='VOID'))
            with patch.object(run,'fresh',return_value=c) as fresh,patch.object(run,'attempt',return_value=dict(status='VOID')) as attempt:
                self.assertEqual(len(run.worker(c)),2);attempt.assert_not_called()
                result=run.worker(c,extra_attempt=True)
                self.assertEqual(len(result),3);attempt.assert_called_once_with(c,3);fresh.assert_called_once_with(c,3)
                self.assertEqual([r['attempt'] for r in result[:2]],[1,2])
    def test_extra_cli_rejects_unnamed_authorization(self):
        with patch('sys.argv',['run.py','--extra-attempt','other']),patch.object(run,'control_review') as review:
            with self.assertRaises(SystemExit):run.main()
            review.assert_not_called()
    def test_existing_third_is_preserved_without_new_authorization(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)):
            c=dict(name='candidate_w2_00013')
            for i in (1,2,3):lf1.dump(Path(tmp)/f'runs/{c["name"]}.attempt{i}/receipt.json',dict(context=c['name'],attempt=i,status='VOID'))
            with patch.object(run,'attempt') as attempt:
                self.assertEqual(len(run.worker(c)),3);attempt.assert_not_called()
    def test_third_fresh_has_originals_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)/'original';(d/'img').mkdir(parents=True)
            (d/'img/x.png').write_bytes(b'synthetic');(d/'items.jsonl').write_text('items')
            (d/'answers.jsonl').write_text('old answer');(d/'zoom').mkdir()
            manifest=Path(tmp)/'manifest.json';lf1.dump(manifest,dict(files={'items.jsonl':lf1.sha(d/'items.jsonl'),'img/x.png':lf1.sha(d/'img/x.png')}))
            c=dict(directory=str(d),manifest=str(manifest))
            second=run.fresh(c);third=run.fresh(c,3)
            self.assertNotEqual(second['directory'],third['directory'])
            self.assertEqual({p.name for p in Path(third['directory']).iterdir()},{'items.jsonl','img'})
            self.assertEqual((Path(third['directory'])/'img/x.png').read_bytes(),b'synthetic')
    def test_third_receipt_authorization_and_void(self):
        expected = {
            'candidate_w2_00004': 'coordinator 20 Oct ~06:20 (VOID is a reader-process failure)',
            'candidate_w2_00013': 'coordinator 20 Oct ~06:20 (VOID is a reader-process failure)',
            'candidate_w1b_00008': 'coordinator 20 Oct ~06:27 GO (then the VOID re-reads)',
        }
        self.assertEqual(set(run.EXTRA_CONTEXTS),set(expected))
        for name,source in expected.items():
            with self.subTest(context=name),tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)),patch.object(run,'verify'),patch.object(run,'prompt_for',return_value=Path(tmp)/'p'):
                (Path(tmp)/'p').write_text('synthetic')
                c=dict(name=name,directory=tmp,cards=1,bed=1,controls=0)
                r=run.attempt(c,3,probe_fn=lambda t:dict(weekly_used=20),
                    read_fn=lambda c,d:dict(rollout=tmp,rc=1,model='gpt-6.1-sol',effort='medium'),scan_fn=lambda *a:dict(ok=False))
                self.assertEqual(r['status'],'VOID');self.assertEqual(r['authorised_by'],source)
                self.assertEqual(json.loads((Path(tmp)/'runs'/f'{name}.attempt3/receipt.json').read_text())['authorised_by'],source)
                self.assertEqual(r['no_verdict'],'no verdict (reader VOID x3)')


class VerticalTests(unittest.TestCase):
    def test_prompt_exact_append(self):
        original=(lf1.BASE/'prompts/lf1.md').read_text()
        self.assertEqual((lf1.BASE/'prompts/lf1_vertical.md').read_text(),original+'\n'+BLOCK+'\n')
    def test_per_roster_prompt_and_default(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)):
            root=Path(tmp);(root/'prompts').mkdir()
            normal=root/'prompts/lf1.md';normal.write_text('normal')
            vertical=root/'prompts/lf1_vertical.md';vertical.write_text('vertical')
            lf1.dump(root/'receipts/prompt_receipt.json',dict(prompt_sha256=lf1.sha(normal)))
            self.assertEqual(run.prompt_for({}),normal)
            self.assertEqual(run.prompt_for(dict(prompt=str(vertical),prompt_sha256=lf1.sha(vertical))),vertical)
            vertical.write_text('changed')
            with self.assertRaisesRegex(ValueError,'custody'):run.prompt_for(dict(prompt=str(vertical),prompt_sha256='old'))
    def test_builder_class_control_bytes_labels_and_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'base';packs=root/'packs';crop=root/'crop.png'
            Image.new('L',(4,20),128).save(crop)
            bed=[dict(candidate(str(i)),draw_class='vertical_turned',label='  α\nβ  ',source_crop=str(crop),source_sha256=lf1.sha(crop)) for i in range(51)]
            bed.append(dict(bed[0],line_id='other',draw_class='latin'))
            pool=[dict(pool_id='lf1-control-'+n,crop=str(crop),sha256=lf1.sha(crop),label=n,expected=dict(verdict='OK')) for n in ('ok','multiline','omitted_span','turned','clipped','textdiff')]
            with patch.object(build,'BASE',base),patch.object(build,'PACK_ROOT',packs),patch.object(build_vertical,'BASE',base):
                old=build.pack('candidate_old_00001',bed,pool)
                roster=root/'roster.json';lf1.dump(roster,[old]);lf1.dump(base/'keys/control_pool.json',pool)
                (base/'prompts').mkdir();(base/'prompts/lf1_vertical.md').write_text('vertical')
                receipt=build_vertical.build_vertical([roster],'test')
                self.assertEqual(receipt['omitted_control'],'lf1-control-turned')
                contexts=json.loads((base/'candidate_contexts_vert_test.json').read_text())
                self.assertEqual([(c['bed'],c['controls']) for c in contexts],[(50,5),(1,5)])
                oldids=set(json.loads(Path(old['key']).read_text())['items'])
                selected=[]
                for c in contexts:
                    self.assertEqual(c['prompt'],str(base/'prompts/lf1_vertical.md'))
                    key=json.loads(Path(c['key']).read_text())['items']
                    self.assertFalse(oldids & set(key))
                    self.assertEqual({r['pool_id'] for r in key.values() if r['control']},{r['pool_id'] for r in pool if r['pool_id']!='lf1-control-turned'})
                    for card in lf1.rows(Path(c['directory'])/'items.jsonl'):
                        row=key[card['card_id']]
                        if row['control']:continue
                        selected.append(row['line_id']);self.assertEqual(row['draw_class'],'vertical_turned')
                        self.assertEqual(card['google_text'],'  α\nβ  ')
                        self.assertEqual((Path(c['directory'])/card['crop']).read_bytes(),Path(row['source_crop']).read_bytes())
                self.assertEqual(set(selected),{str(i) for i in range(51)})
    def test_void_counts_and_receipt_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);key=root/'key';lf1.dump(key,dict(items={'a':dict(candidate('a'),control=False)}))
            for count,state in ((2,'VOID_TWICE'),(3,'VOID_THREE')):
                mapped=prod_map.map_lines([dict(name='c',key=str(key))],
                    [dict(context='c',attempt=i,status='VOID') for i in range(1,count+1)],root)
                self.assertEqual(mapped[0]['state'],state)
                self.assertEqual(mapped[0]['no_verdict'],f'no verdict (reader VOID x{count})')
                combined=prod_map.vertical_override(dict(line_id='a',verdict='OK'),mapped[0])
                final,details=prod_finalize.finalize([candidate('a')],[combined])
                self.assertEqual(final,[])
                rec=details['replacements'][0]
                self.assertEqual(rec['status'],'UNFILLED')
                self.assertEqual(rec['flag_reason']['no_verdict'],f'no verdict (reader VOID x{count})')
                self.assertIsNone(rec['flag_reason']['verdict'])
    def test_nonvertical_void_three_replaces_only_from_same_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);key=root/'key'
            lf1.dump(key,dict(items={'a':dict(candidate('a',cl='latin'),control=False)}))
            mapped=prod_map.map_lines([dict(name='c',key=str(key))],
                [dict(context='c',attempt=i,status='VOID') for i in (1,2,3)],root)
            for source,expected in (('s','REPLACED'),('other','UNFILLED')):
                final,details=prod_finalize.finalize([candidate('a',cl='latin'),candidate('b',False,source,cl='latin')],
                    mapped+[dict(line_id='b',verdict='OK')])
                self.assertEqual(details['replacements'][0]['status'],expected)
                self.assertEqual(details['replacements'][0]['flag_reason']['no_verdict'],'no verdict (reader VOID x3)')
                self.assertEqual(details['summary'][0]['VOID_THREE'],1)
                self.assertEqual(details['summary'][0]['no_verdict'],1)
                self.assertEqual(details['summary'][0]['verdict_flags'],0)
    def test_override_both_directions_and_first_retained(self):
        for first_v,new_v in (('CROP_VIOLATES','OK'),('OK','TEXT_DIFFERS')):
            first=dict(line_id='a',draw_class='vertical_turned',verdict=first_v,state='RESOLVED')
            reread=dict(line_id='a',verdict=new_v,state='RESOLVED')
            merged,separate=prod_map.merge_vertical([first],[reread])
            self.assertEqual(separate[0]['first_verdict'],first);self.assertEqual(separate[0]['reread_verdict'],reread)
            final,details=prod_finalize.finalize([candidate('a')],merged)
            self.assertEqual(bool(final),new_v=='OK')
            self.assertEqual(details['vertical_verdicts'][0]['first_verdict'],first)
    def test_no_reread_cannot_promote_first_ok(self):
        final,details=prod_finalize.finalize([candidate('a')],[dict(line_id='a',verdict='OK')])
        self.assertEqual(final,[]);self.assertEqual(details['replacements'][0]['status'],'UNFILLED')
    def test_separate_file_overrides_first_and_uses_same_source_reserve(self):
        a=candidate('a');b=candidate('b',False)
        first=[dict(line_id='a',verdict='OK'),dict(line_id='b',verdict='CROP_VIOLATES')]
        vertical=[dict(line_id=v['line_id'],first_verdict=v,reread_verdict=dict(verdict='TEXT_DIFFERS' if v['line_id']=='a' else 'OK',state='RESOLVED')) for v in first]
        final,details=prod_finalize.finalize([a,b],first,vertical)
        self.assertEqual([r['line_id'] for r in final],['b'])
        self.assertEqual(details['replacements'][0]['replacement_source'],'s')
    def test_runner_writes_separate_vertical_pairs_and_preserves_first_file(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(run,'BASE',Path(tmp)):
            root=Path(tmp);first_key=root/'first_key';vert_key=root/'vert_key'
            row=dict(candidate('a'),draw_class='vertical_turned',control=False)
            lf1.dump(first_key,dict(items={'old':row}));lf1.dump(vert_key,dict(items={'new':row}))
            old=dict(name='first',key=str(first_key))
            first_roster=root/'first_roster';lf1.dump(first_roster,[old])
            c=dict(name='vertical',key=str(vert_key),reread='vertical_turned',first_rosters=[str(first_roster)])
            roster=root/'vertical_roster';lf1.dump(roster,[c])
            ledger=[dict(context='first',attempt=1,status='VALID')]
            lf1.dump(root/'ledger.json',ledger)
            lf1.jsonl(root/'runs/first.attempt1/verdicts.jsonl',[dict(card_id='old',verdict='CROP_VIOLATES')])
            lf1.jsonl(root/'runs/vertical.attempt1/verdicts.jsonl',[dict(card_id='new',verdict='OK')])
            lf1.jsonl(root/'verdicts.jsonl',[dict(unchanged='first file')])
            lf1.jsonl(root/'prod/vertical_reread_verdicts.jsonl',[dict(line_id='previous_batch')])
            with patch.object(run,'control_review'),patch.object(run,'verify'),patch.object(run,'worker',return_value=[dict(context='vertical',attempt=1,status='VALID')]),patch('sys.argv',['run.py','--contexts',str(roster)]):
                run.main()
            self.assertEqual(lf1.rows(root/'verdicts.jsonl'),[dict(unchanged='first file')])
            result=lf1.rows(root/'prod/vertical_reread_verdicts.jsonl')
            self.assertEqual(result[0]['line_id'],'previous_batch')
            self.assertEqual(result[1]['first_verdict']['verdict'],'CROP_VIOLATES')
            self.assertEqual(result[1]['reread_verdict']['verdict'],'OK')
            self.assertEqual(len(json.loads((root/'ledger.json').read_text())),2)
    def test_mapping_cli_emits_separate_paired_file(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(prod_map,'BASE',Path(tmp)):
            root=Path(tmp);key=root/'key'
            lf1.dump(key,dict(items={'card':dict(candidate('a'),draw_class='vertical_turned',control=False)}))
            for name in ('first','vert'):
                lf1.dump(root/name,[dict(name=name,key=str(key))])
            lf1.dump(root/'ledger',[dict(context='first',attempt=1,status='VALID')]+[dict(context='vert',attempt=i,status='VOID') for i in (1,2)])
            lf1.jsonl(root/'runs/first.attempt1/verdicts.jsonl',[dict(card_id='card',verdict='OK')])
            with patch('sys.argv',['prod_map.py','--contexts',str(root/'first'),'--ledger',str(root/'ledger'),'--vertical-contexts',str(root/'vert'),'--vertical-output',str(root/'pairs'),'--output',str(root/'merged')]):
                prod_map.main()
            merged=lf1.rows(root/'merged');self.assertEqual(merged,lf1.rows(root/'pairs'))
            self.assertEqual(merged[0]['first_verdict']['verdict'],'OK')
            self.assertIsNone(merged[0]['verdict']);self.assertEqual(merged[0]['no_verdict'],'no verdict (reader VOID x2)')
    def test_nonvertical_unaffected(self):
        first=dict(line_id='a',draw_class='latin',verdict='OK')
        self.assertEqual(prod_map.merge_vertical([first],[dict(line_id='a',verdict='BAD')]),([first],[]))
        final,_=prod_finalize.finalize([candidate('a',cl='latin')],[first])
        self.assertEqual(len(final),1)

if __name__=='__main__':unittest.main(verbosity=2)
