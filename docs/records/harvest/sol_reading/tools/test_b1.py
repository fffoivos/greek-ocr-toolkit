"""SR-B1 regression tests. Synthetic answers are never reader results."""
import copy,io,json,os,random,tempfile,unittest
from pathlib import Path
from PIL import Image
from common import *
from build_packs import edited,word_scripts,mask,encode,owner_options,verify_owner_options,apply_yer_override,YER_OVERRIDES,check_pack_root
from map_answers import map_records,validate
from owner39_common import clusters,is_letter,tuple_heads
from scan_rollout import inspect,integrity
from scan_packs import scan
from ledger import weekly,record,append

PROBE=Path.home()/'.codex/sessions/2026/10/17/rollout-2026-10-17T12-27-30-01a14930-13a7-7f61-b21f-ed58bc8d20b0.jsonl'
BASELINE=(SCRATCH/'limit_probe.log').read_text().strip().splitlines()[0]

def fixture(bed,reader):
    key=json.loads((ROOT/f'keys/{bed}.json').read_text());items=rows(PACK_ROOT/bed/reader/itemfile(bed));answers=[]
    for item in items:
        iid=item[idfield(bed)];meta=key['items'][iid]
        if bed=='bsb':
            row=dict(card_id=iid,letters='y',marks='y',crop_ok='y',errors=[],detail='')
            if meta['control']:row.update(meta['expected'])
        elif bed=='yer':
            slots={str(i+1):'ъ' for i in range(item['slots'])}
            if meta['control']:slots=meta['expected']['slots']
            row=dict(item_id=iid,slots=slots,confidence={s:'high' for s in slots},unmarked_final_hard_signs=[],pre1918='unclear',note='synthetic')
        else:
            row=dict(card_id=iid,choice='unreadable',anchor_heads={h:'unknown' for h in ('breathing','accent','diaeresis','subscript')},letter_heads=[],readability='unreadable',ownership_ok=None,confidence='low',note='synthetic',usage=dict(input_tokens=0,output_tokens=0))
            if meta['control']:
                e=meta['expected'];row.update(choice=e['choice'],anchor_heads=e['heads'],readability='readable',confidence='high',ownership_ok=True if any(v!='none' for v in e['heads'].values()) else None)
                if e['choice']=='literal':row['transcription']=e['form']
        answers.append(row)
    return key,items,answers

class BuildTests(unittest.TestCase):
    def test_mask_matches_all_59(self):
        private=json.loads((C1/'yer_adjudication/key.json').read_text())
        for item in rows(EFF/'packs/yer/E1/r1/items.jsonl'):
            shown,calls=mask(private[item['item_id']]['google_text']);self.assertEqual((shown,len(calls)),(item['masked_text'],item['slots']))
    def test_letter_edit_only_unmarked_interior(self):
        original='παρακαλέσω νὰ μοῦ κάμετε χάριν τινὰ μεγίστην.'
        a,change=edited(original,'letters',random.Random('seed'))
        self.assertEqual(len(a),len(original));self.assertNotEqual(a,original)
        self.assertEqual(edited(original,'letters',random.Random('seed')),(a,change))
        self.assertIn('π',change['shown_word']);self.assertEqual(len([i for i,(x,y) in enumerate(zip(a,original)) if x!=y]),1)
    def test_mark_edit_preserves_base_breathing(self):
        a,_=edited('ἄνθρωπος','marks',random.Random(1));self.assertEqual(a,'ἀνθρωπος');self.assertEqual(word_scripts(a),[[a,'Greek']])
    def test_png_reencode_preserves_pixels_strips_info(self):
        im=Image.new('RGB',(10,10),(1,2,3));im.info['comment']='private truth';data=encode(im)
        with Image.open(io.BytesIO(data)) as result:self.assertEqual(result.tobytes(),im.tobytes());self.assertFalse(result.info)
    def test_packs_pass_and_reverse(self):
        for bed in FIELDS:
            for reader in ('r1','r2'):
                # Once a reader ran, audit its recorded manifest and permitted runtime additions.
                directory=PACK_ROOT/bed/reader
                if (directory/'answers.jsonl').exists():self.assertFalse(integrity(directory)[0])
                else:
                    result=scan(directory,bed,False);self.assertTrue(result['ok'],result['violations'])
            self.assertEqual(rows(PACK_ROOT/bed/'r1'/itemfile(bed)),list(reversed(rows(PACK_ROOT/bed/'r2'/itemfile(bed)))))
    def test_bed_copy_pixels_and_no_shared_inodes(self):
        for bed in FIELDS:
            key=json.loads((ROOT/f'keys/{bed}.json').read_text());source=EFF/'packs'/bed/('E0a' if bed=='owner39' else 'E1')/'r1';original={r[idfield(bed)]:r for r in rows(source/itemfile(bed))}
            for item in rows(PACK_ROOT/bed/'r1'/itemfile(bed)):
                meta=key['items'][item[idfield(bed)]]
                if meta['control']:continue
                old=original[meta['source_id']]
                for field in ('crop','word_image','line_image'):
                    if field not in item:continue
                    src=source/old[field]
                    if not src.exists():src=source/'img'/old[field]
                    dest=PACK_ROOT/bed/'r1'/item[field];other=PACK_ROOT/bed/'r2'/item[field]
                    with Image.open(src) as a,Image.open(dest) as b:self.assertEqual(a.convert('RGB').tobytes(),b.tobytes());self.assertEqual(a.size,b.size)
                    self.assertNotEqual(src.stat().st_ino,dest.stat().st_ino);self.assertNotEqual(dest.stat().st_ino,other.stat().st_ino)
    def test_control_counts_shortfall_explicit(self):
        expected={'bsb':10,'yer':5,'owner39':4}
        for bed,n in expected.items():
            key=json.loads((ROOT/f'keys/{bed}.json').read_text());self.assertEqual(sum(v['control'] for v in key['items'].values()),n)
    def test_controls_do_not_share_bed_lines(self):
        for bed in ('bsb','yer'):
            key=json.loads((ROOT/f'keys/{bed}.json').read_text());bedlines={m['line_id'] for m in key['items'].values() if not m['control']};controls=[m['line_id'] for m in key['items'].values() if m['control']]
            self.assertEqual(len(set(controls)),len(controls));self.assertFalse(set(controls)&bedlines)
    def test_owner_verified_marked_literal(self):
        key=json.loads((ROOT/'keys/owner39.json').read_text());controls=[v for v in key['items'].values() if v['control']]
        self.assertTrue(all(c['verification']['lead_verified'] is True for c in controls));self.assertTrue(any(c['expected']['choice']=='literal' for c in controls));self.assertTrue(any(any(v!='none' for v in c['expected']['heads'].values()) for c in controls))

class B1bTests(unittest.TestCase):
    def test_pack_root_private_closure(self):
        self.assertEqual({p.name for p in PACK_ROOT.iterdir()},set(FIELDS))
        for bed in FIELDS:
            entries={p.name for p in (PACK_ROOT/bed).iterdir()}
            self.assertTrue({'r1','r2','MANIFEST.r1.json','MANIFEST.r2.json'}<=entries)
            self.assertTrue(entries<={'r1','r2','r3','MANIFEST.r1.json','MANIFEST.r2.json','MANIFEST.r3.json'})
            self.assertTrue(all((PACK_ROOT/bed/r).is_dir() for r in ('r1','r2')))
            self.assertTrue(all((PACK_ROOT/bed/f'MANIFEST.{r}.json').is_file() for r in ('r1','r2')))
    def test_builder_rejects_private_root_entry(self):
        from unittest.mock import patch
        directory=Path(tempfile.mkdtemp(dir=ROOT/'validation',prefix='sr-b1b-root-'))
        (directory/'control_review').mkdir()
        with patch('build_packs.PACK_ROOT',directory):
            with self.assertRaises(AssertionError):check_pack_root()

    def test_yer_override_from_source(self):
        meta={'source_id':'s003','expected':{'slots':dict.fromkeys('12345','ь')}}
        apply_yer_override(meta)
        key=json.loads((ROOT/'keys/yer.json').read_text())['items']['k15896cc479']
        self.assertEqual(meta['expected'],key['expected'])
        self.assertEqual(key['expected']['slots'],{'1':'ь','2':'ь','3':'ъ','4':'ъ','5':'ъ'})
        self.assertEqual(key['provenance'],'lead pixel review 2026-10-17 12:41 (LEAD_REVIEW.md)')
        self.assertIn(key['provenance'],(ROOT/'keys/control_review/yer.md').read_text())
    def test_all_39_source_options_reproduced(self):
        data=rows(EFF/'packs/owner39/E0a/r1/cards.jsonl')
        self.assertEqual(verify_owner_options(data),39)
        data[0]['options']['A']='incorrect'
        with self.assertRaises(AssertionError):verify_owner_options(data)
    def test_owner_options_choices_and_seeded_permutation(self):
        import unicodedata as U
        before=json.loads((ROOT/'validation/BEFORE_B1b.json').read_text())['owner_key']
        key=json.loads((ROOT/'keys/owner39.json').read_text())
        source={r['card_id']:r for r in rows(EFF/'packs/owner39/E0a/r1/cards.jsonl')}
        rng=random.Random('sol-reading:owner39:r1');dummy=list(range(43));rng.shuffle(dummy)
        for card in rows(PACK_ROOT/'owner39/r1/cards.jsonl'):
            cid=card['card_id'];meta=key['items'][cid];letters=list('ABCD');permuted=letters.copy();rng.shuffle(permuted)
            self.assertEqual(meta['option_to_source'],dict(zip(letters,permuted)))
            base=next(iter(card['options'].values()))
            generated=owner_options(base,card['anchor_index'],meta['source_id'])
            self.assertEqual(card['options'],{a:generated[b] for a,b in meta['option_to_source'].items()})
            self.assertEqual(len(card['options']),4)
            if meta['control']:
                expected=meta['expected'];old=before['items'][cid]['expected']
                self.assertEqual((expected['form'],expected['heads']),(old['form'],old['heads']))
                choice=next((k for k,v in card['options'].items() if U.normalize('NFC',v)==U.normalize('NFC',expected['form'])),'literal')
                self.assertEqual(expected['choice'],choice)
                if expected['form']=='στάδιο':self.assertIn(choice,'ABCD')
    def test_scan_rejects_option_count_blinding(self):
        from unittest.mock import patch
        data=rows(PACK_ROOT/'owner39/r1/cards.jsonl');data[0]['options'].pop('D')
        with patch('scan_packs.rows',return_value=data):
            result=scan(PACK_ROOT/'owner39/r1','owner39',False)
        self.assertIn('inconsistent number of options within bed',result['violations'])
    def test_no_raster_or_other_bed_public_change(self):
        before=json.loads((ROOT/'validation/BEFORE_B1b.json').read_text())['files']
        after={str(p.relative_to(PACK_ROOT)):sha(p) for p in PACK_ROOT.rglob('*') if p.is_file()}
        # SR-B2: reader outputs/zoom are now allowed, original snapshot remains immutable.
        self.assertTrue(set(before)<=set(after))
        for name in set(after)-set(before):
            parts=Path(name).parts
            self.assertTrue((len(parts)>=3 and (parts[2]=='answers.jsonl' or parts[2]=='zoom' or parts[1]=='r3')) or (len(parts)==2 and parts[1]=='MANIFEST.r3.json'),name)
        for name,digest in before.items():
            if name.endswith('.png') or name.startswith(('bsb/','yer/')):
                self.assertEqual(after[name],digest,name)


class MapperTests(unittest.TestCase):
    def test_synthetic_all_beds_readers(self):
        outputs=[]
        for bed,n in [('bsb',100),('yer',59),('owner39',39)]:
            for reader in ('r1','r2'):
                key,items,answers=fixture(bed,reader);mapped,control=map_records(bed,reader,answers,key,items)
                self.assertEqual(len(mapped),n);self.assertEqual(control['control_errors'],0)
                self.assertEqual({r[idfield(bed)] for r in mapped},{m['source_id'] for m in key['items'].values() if not m['control']})
                dest=ROOT/'validation/synthetic'/bed;jsonl(dest/f'{reader}.answers.jsonl',answers);jsonl(dest/f'{reader}.mapped.jsonl',mapped);dump(dest/f'{reader}.controls.json',control)
                outputs.append(dict(bed=bed,reader=reader,mapped=len(mapped),control_errors=control['control_errors']))
        dump(ROOT/'validation/SYNTHETIC_MAPPING_B1.json',{'synthetic_only':True,'results':outputs})
    def test_order_and_count_rejected(self):
        key,items,a=fixture('bsb','r1');a[0],a[1]=a[1],a[0]
        with self.assertRaises(ValueError):map_records('bsb','r1',a,key,items)
        with self.assertRaises(ValueError):map_records('bsb','r1',a[:-1],key,items)
    def test_missing_bsb_fields(self):
        key,items,a=fixture('bsb','r1');del a[0]['detail']
        with self.assertRaises(ValueError):validate(a[0],items[0],'bsb')
    def test_yer_coverage(self):
        key,items,a=fixture('yer','r1');i=next(i for i,x in enumerate(items) if x['slots']);a[i]['slots']={}
        with self.assertRaises(ValueError):validate(a[i],items[i],'yer')
    def test_owner_head_agreement_and_letter_mapping(self):
        key,items,a=fixture('owner39','r1');i=next(i for i,x in enumerate(items) if not key['items'][x['card_id']]['control']);it=items[i]
        a[i].update(choice='A',anchor_heads={h:'unknown' for h in a[i]['anchor_heads']},readability='readable')
        mapped,_=map_records('owner39','r1',a,key,items);m=next(r for r in mapped if r['card_id']==key['items'][it['card_id']]['source_id']);self.assertEqual(m['choice'],key['items'][it['card_id']]['option_to_source']['A'])
        actual=tuple_heads([c for c in clusters(it['options']['A']) if is_letter(c[0])][it['anchor_index']]);a[i]['anchor_heads']['accent']='acute' if actual['accent']!='acute' else 'grave'
        with self.assertRaises(ValueError):validate(a[i],it,'owner39')
    def test_control_error_gate(self):
        key,items,a=fixture('bsb','r1')
        for row in a:
            if key['items'][row['card_id']]['control']:row.update(letters='u',marks='u')
        _,result=map_records('bsb','r1',a,key,items);self.assertEqual(result['control_errors'],10);self.assertTrue(result['flagged'])

class RolloutTests(unittest.TestCase):
    def make(self,inputs):
        root=Path(tempfile.mkdtemp(dir=ROOT/'validation',prefix='sr-b1-'));directory=root/'r1';directory.mkdir();(directory/'cards.jsonl').write_text('[]\n');dump(root/'MANIFEST.r1.json',{'files':{'cards.jsonl':sha(directory/'cards.jsonl')}})
        rollout=root/'rollout.jsonl';jsonl(rollout,[{'payload':{'type':'custom_tool_call','name':'exec','input':s}} for s in inputs]);return rollout,directory
    def test_synthetic_canary_and_safe(self):
        rollout,d=self.make(['await tools.view_image({path:"crops/abc.png"});','await tools.exec_command({cmd:"cat /private/tmp/planted_truth.txt"});'])
        result=inspect(rollout,d);self.assertFalse(result['ok']);self.assertEqual(result['view_image_calls'],1);self.assertEqual(result['exec_commands'],1);self.assertTrue(any(v.get('path')=='/private/tmp/planted_truth.txt' for v in result['violations']));dump(ROOT/'validation/SYNTHETIC_ROLLOUT_SCAN_B1.json',result)
        rollout,d=self.make(['await tools.view_image({path:"crops/abc.png"});','await tools.exec_command({cmd:"cat cards.jsonl"});']);self.assertTrue(inspect(rollout,d)['ok'])
    def test_probe_canary(self):
        result=inspect(PROBE,SCRATCH/'probe_img/A',True);self.assertFalse(result['ok']);self.assertTrue(result['manifest_check_skipped']);self.assertTrue(any(v.get('path','').endswith('/canary_outside.txt') for v in result['violations']));self.assertEqual(result['view_image_calls'],4);self.assertEqual(result['exec_commands'],2)
    def test_computed_arguments_allowed_v2(self):
        rollout,d=self.make(['await tools.view_image({path:variable});']);self.assertTrue(inspect(rollout,d)['ok'])
    def test_missing_manifest_is_failure(self):
        root=Path(tempfile.mkdtemp(dir=ROOT/'validation',prefix='sr-b1-'));r=root/'empty.jsonl';r.write_text('');self.assertFalse(inspect(r,root)['ok']);self.assertTrue(inspect(r,root,True)['ok'])
    def test_integrity_changed_and_added(self):
        r,d=self.make([]);(d/'answers.jsonl').write_text('');(d/'zoom').mkdir();(d/'zoom/a.txt').write_text('');self.assertFalse(integrity(d)[0]);(d/'cards.jsonl').write_text('changed');self.assertTrue(integrity(d)[0]);(d/'outside.txt').write_text('');self.assertTrue(any('unallowed' in e for e in integrity(d)[0]))
    def test_hardlink_rejected(self):
        r,d=self.make([]);os.link(d/'cards.jsonl',d/'answers.jsonl');self.assertTrue(any('hardlink' in e for e in integrity(d)[0]))
    def test_other_tool_formats(self):
        r,d=self.make([]);jsonl(r,[{'payload':{'type':'function_call','name':'view_image','arguments':json.dumps({'path':'crops/one.png'})}},{'payload':{'type':'local_shell_call','action':{'command':['cat','../truth.json']}}}]);out=inspect(r,d);self.assertFalse(out['ok']);self.assertEqual(out['view_image_calls'],1);self.assertEqual(out['exec_commands'],1)

class LedgerTests(unittest.TestCase):
    def run_data(self):
        report=json.loads((ROOT/'PROBE_SCAN_B1.json').read_text());return dict(label='SYNTHETIC-probe-fixture',rc=0,wall_s=18,rollout=str(PROBE),usage=report['total_token_usage'],tool_calls={'exec':3},rate_limits_in_rollout=report['rate_limits'])
    def test_probe_format_tokens_and_unknown_credit_before(self):
        r=record(self.run_data(),BASELINE,BASELINE,'probe','A',2);self.assertEqual(r['weekly_used_before'],32.0);self.assertEqual(r['weekly_delta'],0);self.assertEqual(r['tokens']['total'],78589);self.assertEqual(r['tokens_per_item']['total'],78589/2);self.assertIsNone(r['credits_balance_before']);self.assertAlmostEqual(r['credits_balance_after'],59974.713745);dump(ROOT/'validation/SYNTHETIC_LEDGER_B1.json',dict(synthetic_only=True,record=r))
    def test_delta_and_duplicates(self):
        r=record(self.run_data(),BASELINE,BASELINE.replace('32.0%','32.5%'),'probe','A',2);self.assertEqual(r['weekly_points_per_100_items'],25)
        p=Path(tempfile.mkdtemp(dir=ROOT/'validation',prefix='sr-b1-'))/'ledger.json';append(p,r)
        with self.assertRaises(ValueError):append(p,r)
    def test_unmeasured_rejected(self):
        run=self.run_data();run['usage']=None
        with self.assertRaises(ValueError):record(run,BASELINE,BASELINE,'probe','A',2)
        with self.assertRaises(ValueError):weekly('primary=- secondary=-')

if __name__=='__main__':unittest.main()
