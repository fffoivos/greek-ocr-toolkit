"""Local fixtures only. Never import production census pipelines or score real data."""
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
import zlib
import build_suite02 as s
from make_mock import make

class SealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='seal02-tests-');cls.root=Path(cls.tmp.name)
        c=s.resolve(s.ROOT/'INPUT_BINDINGS.template.json');c['mock']=True
        for role in ('census_current','census_summary'):
            name='CURRENT.json' if role=='census_current' else 'summary.json'
            c['inputs'][role]['path']=str(s.ROOT/'inputs'/name)
        c['image_roots']={t:str(cls.root/('collection_'+t.lower()+'_originals')) for t in ('W1','W2')}
        readout=s.rows(c['inputs']['readout']['path']); cs=s.rows(c['inputs']['candidates']['path']);ci=s.index(cs)
        def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
        for i,label in enumerate(readout):
            # Valid tiny PNG with a representative 14 KB ancillary payload; unique bytes.
            png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,0,0,0,0))+chunk(b'tEXt',b'fixture\x00'+str(i).encode()+b'x'*14000)+chunk(b'IDAT',zlib.compress(b'\x00\xff'))+chunk(b'IEND',b'')
            label['crop_sha256']=hashlib.sha256(png).hexdigest();p=s.image_path(c,ci[s.key(label)]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(png)
        path=cls.root/'readout.jsonl';s.jsonl(path,readout);c['inputs']['readout']=dict(path=str(path),sha256=s.sha(path))
        make(c['inputs']['candidates']['path'],cls.root/'mock')
        for role,name in [('final_list','final_list.MOCK.jsonl'),('final_receipt','final_receipt.MOCK.json'),('verdicts','verdicts.MOCK.jsonl')]:
            path=cls.root/'mock'/name;c['inputs'][role]=dict(path=str(path),sha256=s.sha(path))
        for tranche,role in [('W1','w1_receipt'),('W2','w2_receipt')]:
            attempt=cls.root/role;attempt.mkdir();path=attempt/'upload_receipt.json'
            (attempt/'crops_sha256.txt').write_text('0'*64+'  collection_'+tranche.lower()+'_originals/source/row.png\n')
            s.dump(path,dict(status='ok',mode='full',mismatches=0,failures=0,sha256check_exit=0,selected=3341,byte_exact=3341,output_base=str(cls.root),context=dict(tranche=tranche,include_heldout=True,inputs={'summary.json':c['inputs']['census_summary']['sha256']})))
            c['inputs'][role]=dict(path=str(path),sha256=s.sha(path))
        cls.c=c;cls.cs=cs;cls.readout=readout
        cls.config=cls.root/'bindings.json';s.dump(cls.config,c)
        t=time.monotonic();cls.receipt=s.build(cls.config,cls.root/'full',mock=True);cls.build_seconds=time.monotonic()-t
        print('FULL_MOCK_TIMING '+json.dumps(dict(rows=cls.receipt['rows'],candidate_images=len(cs),image_bytes=sum(s.image_path(c,r).stat().st_size for r in cs),seconds=cls.build_seconds)),flush=True)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def final_args(self):
        return s.resolve(self.config),self.cs,True
    def test_full_mock_build(self):
        self.assertEqual(self.receipt['rows'],2793);self.assertEqual(self.receipt['status'],'MOCK')
        suite=s.load(self.root/'full/suite.json');self.assertEqual(suite['version'],'0.2')
        self.assertTrue(all(not p['scorable'] for p in suite['panels'].values()))
    def test_reference_final_text_byte_for_byte(self):
        expected=s.index(self.readout)
        for split in ('test','dev'):
            for r in s.rows(self.root/'full'/('benchmark_v02_'+split+'.jsonl')):
                self.assertEqual(r['text'].encode(),expected[s.key(r)]['final_text'].encode())
                self.assertEqual(r['reference'],r['text'])
    def test_missing_image(self):
        p=s.image_path(self.c,self.cs[0]);b=p.read_bytes();p.unlink()
        try:
            with self.assertRaisesRegex(ValueError,'missing candidate images'):s.build(self.config,self.root/'missing',mock=True)
        finally:p.write_bytes(b)
    def test_mismatched_image(self):
        p=s.image_path(self.c,self.cs[0]);b=p.read_bytes();p.write_bytes(b+b'bad')
        try:
            with self.assertRaisesRegex(ValueError,'image hash differs'):s.build(self.config,self.root/'badimage',mock=True)
        finally:p.write_bytes(b)
    def test_non_OK_verdict(self):
        c,cs,m=self.final_args();p=Path(c['inputs']['final_list']['path']);b=p.read_bytes();rs=s.rows(p);rs[0]['lf1_verdict']='TEXT_DIFFERS';s.jsonl(p,rs)
        try:
            with self.assertRaisesRegex(ValueError,'non-OK'):s.final_checked(c,cs,m)
        finally:p.write_bytes(b)
    def test_replacement_split_class_source_rank(self):
        c,cs,m=self.final_args();v=Path(c['inputs']['verdicts']['path']);f=Path(c['inputs']['final_list']['path']);rc=Path(c['inputs']['final_receipt']['path']);saved=[p.read_bytes() for p in (v,f,rc)]
        try:
            old=next(r for r in cs if r['in_quota'] and any(x['quota_scope']==r['quota_scope'] and x['source']==r['source'] and not x['in_quota'] for x in cs))
            reserve=sorted((r for r in cs if not r['in_quota'] and r['quota_scope']==old['quota_scope'] and r['source']==old['source']),key=lambda r:r['scope_rank'])
            vs=s.rows(v);next(r for r in vs if r['line_id']==old['row_id'])['verdict']='FLAGGED';s.jsonl(v,vs)
            c['inputs']['verdicts']['sha256']=s.sha(v);fs=[r for r in s.rows(f) if s.key(r)!=s.key(old)];new=reserve[0]
            replacement=dict(parent_id=new['parent_id'],row_id=new['row_id'],split=new['split'],quota_scope=new['quota_scope'],lf1_verdict='OK',replaces=dict(parent_id=old['parent_id'],row_id=old['row_id']),mock=True)
            fs.append(replacement)
            for r in fs:r['lf1_receipt_ref']=dict(verdicts_sha256=s.sha(v),line_id=r['row_id'])
            s.jsonl(f,fs);c['inputs']['final_list']['sha256']=s.sha(f)
            receipt=s.load(rc);receipt.update(verdicts_sha256=s.sha(v),final_list_sha256=s.sha(f),counts=dict(flagged=1,REPLACED=1,UNFILLED=0));s.dump(rc,receipt)
            s.final_checked(c,cs,m)
            for field,value in [('split','wrong'),('quota_scope','test:wrong'),('replaces',dict(parent_id=new['parent_id'],row_id=new['row_id']))]:
                bad=copy.deepcopy(fs);bad[-1][field]=value;s.jsonl(f,bad)
                with self.assertRaises(ValueError):s.final_checked(c,cs,m)
            # Select a foreign source/class reserve instead; expected-key check rejects it.
            bad=copy.deepcopy(fs);foreign=next(r for r in cs if not r['in_quota'] and r['source']!=old['source'] and r['class']!=old['class']);bad[-1].update(parent_id=foreign['parent_id'],row_id=foreign['row_id'])
            s.jsonl(f,bad)
            with self.assertRaisesRegex(ValueError,'selection/replacement'):s.final_checked(c,cs,m)
        finally:
            for p,b in zip((v,f,rc),saved):p.write_bytes(b)
    def test_unfilled_is_not_padded(self):
        c,cs,m=self.final_args();v=Path(c['inputs']['verdicts']['path']);f=Path(c['inputs']['final_list']['path']);rc=Path(c['inputs']['final_receipt']['path']);saved=[p.read_bytes() for p in (v,f,rc)]
        try:
            old=next(r for r in cs if r['in_quota'] and not any(not x['in_quota'] and x['source']==r['source'] and x['quota_scope']==r['quota_scope'] for x in cs))
            vs=s.rows(v);next(r for r in vs if r['line_id']==old['row_id'])['verdict']='FLAGGED';s.jsonl(v,vs);c['inputs']['verdicts']['sha256']=s.sha(v)
            fs=[r for r in s.rows(f) if s.key(r)!=s.key(old)]
            for r in fs:r['lf1_receipt_ref']['verdicts_sha256']=s.sha(v)
            s.jsonl(f,fs);c['inputs']['final_list']['sha256']=s.sha(f)
            receipt=s.load(rc);receipt.update(verdicts_sha256=s.sha(v),final_list_sha256=s.sha(f),counts=dict(flagged=1,REPLACED=0,UNFILLED=1));s.dump(rc,receipt)
            result,receipt,vd,unfilled=s.final_checked(c,cs,m)
            self.assertEqual(len(result),2792);self.assertEqual(len(unfilled),1)
        finally:
            for p,b in zip((v,f,rc),saved):p.write_bytes(b)
    def test_final_receipt_count_tamper(self):
        c,cs,m=self.final_args();p=Path(c['inputs']['final_receipt']['path']);saved=p.read_bytes();r=s.load(p);r['counts']['flagged']=1;s.dump(p,r)
        try:
            with self.assertRaisesRegex(ValueError,'counts differ'):s.final_checked(c,cs,m)
        finally:p.write_bytes(saved)
    def test_real_shaped_crops_receipt(self):
        for role in ('w1_receipt','w2_receipt'):
            rec=s.load(self.c['inputs'][role]['path'])
            self.assertEqual(rec['output_base'],str(self.root))
            s.receipt_checked(role,rec,self.c)
    def test_crops_receipt_wrong_root(self):
        for role in ('w1_receipt','w2_receipt'):
            rec=s.load(self.c['inputs'][role]['path']);rec['output_base']=str(self.root/'elsewhere')
            with self.assertRaisesRegex(ValueError,'output root/tranche/heldout'):
                s.receipt_checked(role,rec,self.c)
    def test_crops_manifest_wrong_prefix(self):
        p=Path(self.c['inputs']['w1_receipt']['path']).parent/'crops_sha256.txt';saved=p.read_bytes()
        try:
            p.write_text('0'*64+'  collection_w2_originals/source/row.png\n')
            with self.assertRaisesRegex(ValueError,'manifest prefix'):
                s.receipt_checked('w1_receipt',s.load(self.c['inputs']['w1_receipt']['path']),self.c)
        finally:p.write_bytes(saved)
    def test_failed_crops_receipt(self):
        c=copy.deepcopy(self.c);src=Path(c['inputs']['w1_receipt']['path']);p=self.root/'failed_crop_receipt.json';r=s.load(src);r['mismatches']=1;s.dump(p,r);c['inputs']['w1_receipt']=dict(path=str(p),sha256=s.sha(p));cfg=self.root/'failed_receipt_bindings.json';s.dump(cfg,c)
        with self.assertRaisesRegex(ValueError,'CROPS4 not complete'):s.verify_inputs(cfg)
    def test_incomplete_lf1_ledger(self):
        c,cs,m=self.final_args();p=Path(c['inputs']['verdicts']['path']);saved=p.read_bytes();s.jsonl(p,s.rows(p)[1:])
        try:
            with self.assertRaisesRegex(ValueError,'ledger incomplete'):s.final_checked(c,cs,m)
        finally:p.write_bytes(saved)
    def test_deterministic_suite_bytes(self):
        s.build(self.config,self.root/'repeat',mock=True)
        self.assertEqual((self.root/'full/suite.json').read_bytes(),(self.root/'repeat/suite.json').read_bytes())
    def test_01_scorer_accepts(self):
        # Synthetic local production-shaped fixture, no model predictions or metrics.
        c=copy.deepcopy(self.c);c['mock']=False
        for role in ('final_list','final_receipt','verdicts'):
            src=Path(c['inputs'][role]['path']);dst=self.root/('production_fixture_'+src.name);dst.write_bytes(src.read_bytes());c['inputs'][role]['path']=str(dst)
        v=Path(c['inputs']['verdicts']['path']);vs=s.rows(v)
        for r in vs:r['mock']=False
        s.jsonl(v,vs);c['inputs']['verdicts']['sha256']=s.sha(v)
        f=Path(c['inputs']['final_list']['path']);fs=s.rows(f)
        for r in fs:r['mock']=False;r['lf1_receipt_ref']['verdicts_sha256']=s.sha(v)
        s.jsonl(f,fs);c['inputs']['final_list']['sha256']=s.sha(f)
        rc=Path(c['inputs']['final_receipt']['path']);receipt=s.load(rc);receipt.update(mock=False,verdicts_sha256=s.sha(v),final_list_sha256=s.sha(f));s.dump(rc,receipt);c['inputs']['final_receipt']['sha256']=s.sha(rc)
        cfg=self.root/'synthetic_production.json';s.dump(cfg,c);s.build(cfg,self.root/'synthetic_production')
        sys.path.insert(0,str(s.ROOT/'v01'));from bench.benchmark_suite import read_panel,audit_model,prediction_map
        for split in ('dev','test'):
            suite,panel,records=read_panel(self.root/'synthetic_production/suite.json','benchmark_v02_'+split)
            self.assertEqual(audit_model(records,{})['status'],'diagnostic_only')
            self.assertTrue(prediction_map([dict(id=records[0]['id'],status='error')],{r['id'] for r in records})[records[0]['id']]==('','failed'))
    def test_mock_rejected_by_production(self):
        with self.assertRaisesRegex(ValueError,'MOCK'):s.build(self.config,self.root/'mock_forbidden')
    def test_changed_binding(self):
        c=copy.deepcopy(self.c);c['inputs']['readout']['sha256']='0'*64;p=self.root/'changed.json';s.dump(p,c)
        with self.assertRaisesRegex(ValueError,'input hash differs'):s.build(p,self.root/'changed',mock=True)
    def test_missing_binding(self):
        c=copy.deepcopy(self.c);c['inputs']['final_list']['sha256']=None;p=self.root/'unbound.json';s.dump(p,c)
        with self.assertRaisesRegex(ValueError,'missing or unbound'):s.build(p,self.root/'unbound',mock=True)
    def test_no_overwrite(self):
        with self.assertRaisesRegex(ValueError,'already exists'):s.build(self.config,self.root/'full',mock=True)
    def test_absolute_output_required(self):
        with self.assertRaisesRegex(ValueError,'absolute'):s.build(self.config,Path('relative'),mock=True)
    def build_pixel_fixture(self, name, split, cross=False, copies=1):
        # Rebind real fixture PNG bytes and readout hashes; all prior checks run.
        c=copy.deepcopy(self.c); labels=copy.deepcopy(self.readout)
        selected=[r for r in self.cs if r['in_quota']]
        kept=next(r for r in selected if r['split']==('test' if cross else split))
        changed=[r for r in selected if r['split']==split and s.key(r)!=s.key(kept)][:copies]
        png=s.image_path(c,kept).read_bytes(); saved=[]
        for r in changed:
            path=s.image_path(c,r);saved.append((path,path.read_bytes()));path.write_bytes(png)
            next(label for label in labels if s.key(label)==s.key(r))['crop_sha256']=hashlib.sha256(png).hexdigest()
        path=self.root/(name+'.readout.jsonl');s.jsonl(path,labels)
        c['inputs']['readout']=dict(path=str(path),sha256=s.sha(path))
        cfg=self.root/(name+'.bindings.json');s.dump(cfg,c)
        try:
            receipt=s.build(cfg,self.root/name,mock=True)
            return receipt,kept,changed
        finally:
            for path,data in saved:path.write_bytes(data)
    def check_cross_fixture(self, name, copies):
        receipt,kept,changed=self.build_pixel_fixture(name,'dev',cross=True,copies=copies)
        expected=[]
        for r in changed:
            expected.append(dict(image_sha256=hashlib.sha256(s.image_path(self.c,kept).read_bytes()).hexdigest(),
                dropped={k:r[k] for k in ('parent_id','row_id','split','quota_scope')},
                kept=[{k:kept[k] for k in ('parent_id','row_id','split','quota_scope')}]))
        expected.sort(key=lambda d:(d['dropped']['parent_id'],d['dropped']['row_id']))
        self.assertEqual(receipt['cross_panel_pixel_duplicates_dropped'],expected)
        self.assertEqual(receipt,s.load(self.root/name/'SEAL_RECEIPT.json'))
        self.assertEqual(receipt['rows'],2793-copies);self.assertEqual(receipt['images'],receipt['rows'])
        self.assertEqual((self.root/name/'benchmark_v02_test.jsonl').read_bytes(),
                         (self.root/'full/benchmark_v02_test.jsonl').read_bytes())
        remaining=s.rows(self.root/name/'benchmark_v02_dev.jsonl')
        self.assertTrue(all(s.key(r) not in {s.key(x) for x in changed} for r in remaining))
        scope_drops=s.Counter(r['quota_scope'] for r in changed)
        for scope,old in self.receipt['scope_counts'].items():
            want=dict(old)
            if scope in scope_drops:
                n=scope_drops[scope];want.update(sealed=old['sealed']-n,deficit=old['deficit']+n,pixel_duplicate_drops=n)
            self.assertEqual(receipt['scope_counts'][scope],want)
        suite=s.load(self.root/name/'suite.json')
        self.assertEqual(suite['scope_counts'],receipt['scope_counts'])
        for scope,n in s.Counter(r['split']+':'+r['class'] for r in changed).items():
            old=self.receipt['quota_counts'][scope];new=receipt['quota_counts'][scope]
            self.assertEqual(new['sealed'],old['sealed']-n);self.assertEqual(new['deficit'],old['deficit']+n)
    def test_cross_panel_pixel_duplicate(self):
        self.check_cross_fixture('cross_pixel',1)
    def test_two_dev_copies_of_test_image(self):
        self.check_cross_fixture('cross_pixel_twice',2)
    def test_duplicate_image_within_test(self):
        with self.assertRaisesRegex(ValueError,'duplicate image within panel test:.*parent_id.*row_id'):
            self.build_pixel_fixture('within_test','test')
        self.assertFalse((self.root/'within_test').exists())
    def test_duplicate_image_within_dev(self):
        with self.assertRaisesRegex(ValueError,'duplicate image within panel dev:.*parent_id.*row_id'):
            self.build_pixel_fixture('within_dev','dev')
        self.assertFalse((self.root/'within_dev').exists())
    def test_no_pixel_duplicates_unchanged(self):
        panels={split:s.rows(self.root/'full'/('benchmark_v02_'+split+'.jsonl')) for split in ('test','dev')}
        before=copy.deepcopy(panels);counts=copy.deepcopy(self.receipt['scope_counts'])
        retained,drops,adjusted=s.pixel_overlap_checked(panels,counts)
        self.assertEqual(retained,before);self.assertEqual(panels,before)
        self.assertEqual(adjusted,counts);self.assertEqual(drops,[])
        self.assertEqual(self.receipt['cross_panel_pixel_duplicates_dropped'],[])
    def test_package_imports(self):
        self.assertEqual(s.verify_package()['status'],'ok')
if __name__=='__main__':unittest.main(verbosity=2)
