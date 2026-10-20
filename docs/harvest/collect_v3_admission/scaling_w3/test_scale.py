import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import scale as s


def row(i,cl='a',source='src',edition='ed'):
    return dict(parent_id=s.VC,row_id=str(i),key=[s.VC,str(i)],source=source,edition_id=edition,doc='doc',primary_class=cl,crop_path='/tmp/unused',crop_sha256='0'*64)

class Selection(unittest.TestCase):
    def test_prefix_nesting(self):
        pool=[row(i) for i in range(30)];ref=s.reference(pool)
        self.assertLess({s.key(r) for r in ref[:20]},{s.key(r) for r in ref})
        self.assertEqual({s.key(r) for r in ref},{s.key(r) for r in pool})
    def test_determinism_independent_input_order(self):
        pool=[row(i,'a' if i%2 else 'b','s'+str(i%3),'e'+str(i%4)) for i in range(60)]
        self.assertEqual(s.reference(pool),s.reference(pool[::-1]))
        self.assertEqual(s.targeted(s.reference(pool),{'a':1,'b':1},40),s.targeted(s.reference(pool[::-1]),{'a':1,'b':1},40))
    def test_short_class_redistribution(self):
        pool=[row(0,'a')]+[row(i,'b') for i in range(1,30)]
        chosen,rep=s.targeted(s.reference(pool),{'a':3,'b':1},20)
        self.assertEqual(rep['allocations'],{'a':1,'b':19});self.assertEqual(len(chosen),20)
        self.assertEqual(rep['redistribution_trace'][0]['exhausted'],['a'])
    def test_iterative_redistribution(self):
        a,fill,trace=s.allocation({'a':1,'b':9,'c':30},{'a':4,'b':3,'c':1},20)
        self.assertEqual(a,{'a':1,'b':9,'c':10});self.assertEqual(fill,0);self.assertGreaterEqual(len(trace),3)
    def test_unclassified_reference_fill(self):
        ref=s.reference([row(0,'a')]+[row(i,None) for i in range(1,10)])
        chosen,rep=s.targeted(ref,{'a':1,'b':1},5)
        self.assertEqual(rep['unclassified_fill'],4)
        self.assertEqual(chosen[1:],[r for r in ref if r['primary_class'] is None][:4])
    def test_no_edition_or_series_caps(self):
        pool=[row(i) | {'series':'same'} for i in range(160)]
        self.assertEqual(len(s.rotation(pool,'a')),160)
    def test_source_round_robin_and_edition_cursor(self):
        pool=[row(f'{src}{ed}{i}',source=src,edition=ed) for src in ['a','b'] for ed in ['x','y'] for i in range(3)]
        rr=s.rotation(pool,'a')
        self.assertEqual(len({r['source'] for r in rr[:2]}),2)
        for src in ['a','b']:
            es=[r['edition_id'] for r in rr if r['source']==src]
            self.assertTrue(all(a!=b for a,b in zip(es,es[1:])))
    def test_fraction_rounding(self):
        a,left,_=s.allocation(dict(a=100,b=100,c=100),dict(a=1,b=1,c=1),5)
        self.assertEqual(a,dict(a=2,b=2,c=1));self.assertEqual(left,0)
    def test_relative_population_and_missing_confidence(self):
        pop={'src':[(None,('p','0'))]+[(.5,('p',str(i))) for i in range(1,21)]}
        flagged,rep=s.relative_flags(pop)
        self.assertEqual(len(flagged),2);self.assertNotIn(('p','0'),flagged)
        self.assertEqual(rep['src']['missing_confidence'],1)
    def test_classifier_null_evidence_unchanged(self):
        m=s.classifier();d=dict(binding=dict(parent_id=s.VC,id='1'),admitted=True,final_text='123',expectations={},raw_inventory={})
        slim=m.slim(d,{'crop_bbox':None});tags=m.tag(slim,relative_flag=False)
        self.assertEqual(tags['tags']['numeric_cells'],'unavailable');self.assertEqual(tags['tags']['font_extremes'],'unavailable')
    def test_quotas_loaded_from_counts(self):
        self.assertEqual(sum(s.quotas().values()),2460);self.assertEqual(len(s.quotas()),16)
    def test_vc_final_text_byte_for_byte(self):
        text='  α\u0313\t—\nΩ  ';r=row(1);r.update(final_text=text,label='wrong',decision={'final_text':text,'binding':{'crop_sha256':'0'*64}})
        out=s.vc_row(r,row(1));self.assertEqual(out['label'].encode(),text.encode())
        self.assertEqual(json.loads(json.dumps(out,ensure_ascii=False))['label'].encode(),text.encode())

class Exposure(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'crop';self.p.write_bytes(b'crop')
        self.r=row(1)|dict(crop_path=str(self.p),crop_sha256=hashlib.sha256(b'crop').hexdigest())
    def check(self,**kw):return s.exposure([self.r],kw.get('blocked',set()),kw.get('bkeys',set()),kw.get('bhashes',set()),kw.get('vdocs',set()))
    def test_clean(self):self.assertEqual(self.check()['crops_rehashed'],1)
    def test_dev_test_edition(self):
        with self.assertRaisesRegex(ValueError,'dev_test_editions'):self.check(blocked={'ed'})
    def test_benchmark_key(self):
        with self.assertRaisesRegex(ValueError,'benchmark_keys'):self.check(bkeys={s.key(self.r)})
    def test_benchmark_hash(self):
        with self.assertRaisesRegex(ValueError,'benchmark_crop_hashes'):self.check(bhashes={self.r['crop_sha256']})
    def test_v2_dev_test_doc(self):
        with self.assertRaisesRegex(ValueError,'v2_dev_test_docs'):self.check(vdocs={'doc'})
    def test_missing_crop(self):
        self.p.unlink()
        with self.assertRaisesRegex(ValueError,'missing crop'):self.check()
    def test_mismatched_crop(self):
        self.p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'crop SHA mismatch'):self.check()


class Pipeline(unittest.TestCase):
    def test_two_job_handoff_and_outputs(self):
        import shutil
        from unittest.mock import patch
        from benchmark import sample
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'vendor').mkdir()
            for name in ['bench02_draw.py','counts.json']:shutil.copy(s.HERE/'vendor'/name,root/'vendor'/name)
            crop=root/'crop';crop.write_bytes(b'pixels');digest=s.sha(crop)
            census=[]
            for i in range(8):
                r=sample(i);r['crop_path']=str(crop);r['crop_sha256']=digest;r['decision']['binding']['crop_sha256']=digest
                r['admitted']=False; r['rejection_reasons']=['short_line']
                if i<4:r['parent_id']=r['decision']['binding']['parent_id']='collect-v3-W1-fixture'
                r['final_text']=r['decision']['final_text']='  α\u0313\t—\nΩ  '+str(i)
                census.append(r)
            paths={}
            def write(name,rr):
                p=root/(name+'.jsonl');p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr));paths[name]=p
            write('admitted_train',census)
            write('release',[dict(crop_relative_path='collection_w1_originals/'+r['source']+'/'+r['id']+'.png',parent_id=r['parent_id'],row_id=r['id'],source=r['source'],edition_id=r['edition_id'],crop_sha256=digest,label='release-label-'+r['id'],split='train') for r in census[:4]])
            write('row_split.jsonl.gz',[dict(parent_id=r['parent_id'],row_id=r['id'],edition_id='doc',split='train') for r in census[:4]])
            # The fixture is plain JSONL despite this manifest name; reader detects actual .jsonl suffix.
            write('edition_map.jsonl',[dict(edition_id='doc',split='train')])
            for name in ['candidates_v3.jsonl','candidates_readout.jsonl','v2_dev','v2_test']:write(name,[])
            for name in ['live_CURRENT','live_summary']:write(name,[{}])
            p=root/'release_receipt.json';s.dump(p,dict(status='ok',outputs={'release_v3_admission.jsonl':s.info(paths['release'])}));paths['release_receipt']=p
            bindings={name:dict(name=name,kind='small',**s.info(p)) for name,p in paths.items()};s.dump(root/'inputs.json',list(bindings.values()))
            def fake_inputs(mode,full=False):return {k:v for k,v in bindings.items() if mode!='tags' or k in ['admitted_train','live_CURRENT','live_summary']}
            with patch.object(s,'HERE',root),patch.object(s,'inputs',side_effect=fake_inputs),patch.object(s,'W',root):
                for r in census[:4]:
                    original=root/'collection_w1_originals'/r['source']/(r['id']+'.png')
                    original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(b'pixels')
                s.tag_job(root/'tags',_vc_expected=4)
                receipt=root/'tags/TAGS_RECEIPT.json'
                tr=json.loads(receipt.read_text())
                for parent,fields in tr['availability'].items():
                    for field,counts in fields.items():self.assertEqual(sum(counts.values()),4,(parent,field))
                tr['wrapper_sha']=s.TAG_PRODUCER_SHA; s.dump(receipt,tr)
                with patch.object(s,'tag_path_sha',return_value='0'*64):
                    with self.assertRaisesRegex(ValueError,'status/code mismatch'):s.tags_binding(receipt,s.sha(receipt),True)
                s.build_job(root/'subsets',receipt,s.sha(receipt),_expected=(4,4,8),_size=6)
                out=list(s.rows(root/'subsets/ref_364871.jsonl'))
                self.assertEqual(len(out),8)
                for r in out:
                    i=int(r['row_id'])
                    self.assertEqual(r['crop_path'],str(root/'collection_w1_originals'/census[i]['source']/(str(i)+'.png')) if i<4 else str(crop))
                    self.assertEqual(r['label'],'release-label-'+str(i) if i<4 else census[i]['final_text'])
                rec=json.loads((root/'subsets/SUBSETS_RECEIPT.json').read_text());self.assertTrue(rec['nesting'])
                self.assertEqual(rec['subsets']['ref_364871']['audit']['crops_rehashed'],8)
                with self.assertRaisesRegex(ValueError,'receipt SHA mismatch'):s.tags_binding(receipt,'0'*64,True)

class CropResolver(unittest.TestCase):
    def fixtures(self):
        return list(s.rows(s.HERE/'fixtures/real_admitted_train.jsonl')), {s.key(r):r for r in s.rows(s.HERE/'fixtures/real_release.jsonl')}

    def test_real_fixture_resolver(self):
        rr,releases=self.fixtures()
        for r in rr:
            out=s.resolve_crop(r,releases.get(s.key(r)))
            self.assertEqual(out['crop_sha256'],r['decision']['binding']['crop_sha256'])
            if r['parent_id']==s.VC:self.assertEqual(out['crop_path'],r['crop_path'])
            else:
                self.assertEqual(out['crop_path'],str(s.W/releases[s.key(r)]['crop_relative_path']))
                self.assertNotEqual(out['crop_path'],r['crop_path'])

    def test_w12_cannot_resolve_to_census_path(self):
        rr,releases=self.fixtures()
        for original in rr:
            if original['parent_id']==s.VC:continue
            r=copy.deepcopy(original);release=releases[s.key(r)]
            r['crop_path']=str(s.W/release['crop_relative_path'])
            with self.assertRaisesRegex(ValueError,'resolved to census'):s.resolve_crop(r,release)

    def test_release_binding_failures(self):
        rr,releases=self.fixtures();r=next(x for x in rr if x['parent_id']!=s.VC)
        for change in ({'crop_sha256':'0'*64},{'row_id':'wrong'},{'crop_relative_path':'../bad'},{'crop_relative_path':r['crop_path']}):
            with self.subTest(change=change),self.assertRaises(ValueError):s.resolve_crop(r,releases[s.key(r)]|change)
        with self.assertRaises(ValueError):s.resolve_crop(r)

    def test_tag_producer_path_unchanged(self):
        self.assertEqual(s.tag_path_sha(),s.TAG_PATH_SHA)

class RealCensus(unittest.TestCase):
    def test_real_excerpt_full_tag_writer(self):
        from collections import Counter
        from unittest.mock import patch
        excerpt=s.HERE/'fixtures/real_admitted_train.jsonl'
        rr=list(s.rows(excerpt)); counts=Counter(r['parent_id'] for r in rr)
        self.assertEqual(sorted(counts.values()),[20,20,20])
        self.assertTrue(any(r.get('admitted') is False for r in rr))
        self.assertTrue(all(r['final_text']==r['decision']['final_text'] for r in rr))
        self.assertTrue(all(isinstance(r['final_text'],str) and r['final_text'] for r in rr))
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'tags'
            with patch.object(s,'inputs',return_value={'admitted_train':s.info(excerpt)}):
                s.tag_job(dest,_vc_expected=20)
            tags=list(s.rows(dest/'train_tags.jsonl.gz'))
            self.assertEqual(len(tags),60)
            m=s.classifier()
            populations={}
            for r in rr:
                slim=s.census_row(r,m)
                self.assertTrue(slim['admitted'])
                populations.setdefault(r['source'],[]).append((slim['evidence'].get('confidence'),s.key(slim)))
            flagged,_=s.relative_flags(populations)
            for r,out in zip(rr,tags):
                t=m.tag(s.census_row(r,m),relative_flag=s.key(r) in flagged)
                self.assertEqual(out['key'],list(s.key(r)))
                self.assertEqual(out['tags'],t['tags'])
                self.assertEqual(out['primary_class'],t['primary_class'])
                self.assertEqual(out['crop_sha256'],r['crop_sha256'])
                if r['parent_id']==s.VC:
                    self.assertIsNone(r.get('crop_bbox'))
                    self.assertEqual(out['tags']['cell_flag'],'unavailable')
                    self.assertEqual(s.vc_row(r,out)['label'].encode(),r['final_text'].encode())
            rec=json.loads((dest/'TAGS_RECEIPT.json').read_text())
            for parent,fields in rec['availability'].items():
                for field,available in fields.items():
                    self.assertEqual(sum(available.values()),20,(parent,field))
            self.assertEqual(rec['availability'][s.VC]['census.crop_bbox'],{'unavailable':20})

    def test_real_legacy_rejection_is_not_census_rejection(self):
        rr=list(s.rows(s.HERE/'fixtures/real_admitted_train.jsonl'))
        r=next(r for r in rr if r['id']=='bsb_poly1850--027215cc6d2a7e8a--s000-l0025')
        self.assertIs(r['admitted'],False)
        self.assertEqual(r['rejection_reasons'],['short_line'])
        self.assertTrue(s.census_row(r,s.classifier())['admitted'])

    def test_real_census_rejection_still_fails_closed(self):
        original=next(s.rows(s.HERE/'fixtures/real_admitted_train.jsonl'))
        for fields in ({'admitted':False},{'disposition':'REJECT'}):
            r=copy.deepcopy(original); r['admitted']=True; r['decision'].update(fields)
            with self.subTest(fields=fields),self.assertRaisesRegex(ValueError,'non-admitted train row'):
                s.census_row(r,s.classifier())

if __name__=='__main__':unittest.main()
