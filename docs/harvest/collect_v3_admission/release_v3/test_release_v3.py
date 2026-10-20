import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
import build_release_v3 as b


class Fixture:
    def __init__(self,root,n=0):
        self.root=Path(root); self.root.mkdir(exist_ok=True)
        self.work=self.root/'work';self.work.mkdir()
        self.parent='collect-v3-W1-20261018-0524'
        self.reg=[dict(name='numerics_0.3',tool='numerics',version='0.3',tool_digest='d'*64,file='versions.json',sha256='',keying='binding',mode='census_internal',artifacts=[dict(parent_id=self.parent,sha256='a'*64)]),
                  dict(name='composer_0.3',tool='composer',version='0.3',tool_digest='c'*64,file='versions.json',sha256='',keying='binding',mode='census_internal',artifacts=[]),
                  dict(name='external',parent_id=self.parent,file='external.jsonl',sha256='',keying='id',id_field='id',text_field='text',parent_text_field='parent_text',mode='external_registered_not_applied')]
        self.rows=[self.row('same'),self.row('edit','12.34','12·34'),self.row('normal',' α  β ','α β'),self.row('missing'),self.row('pixels')]
        self.rows += [self.row('bulk'+str(i),padding='x'*20000) for i in range(n)]
        self.write('external.jsonl',[dict(id='edit',text='12·34',parent_text='12.34'),dict(id='same',text='abc',parent_text='abc')])
        self.write('versions.json',{})
        for r in self.reg:r['sha256']=b.sha(self.root/r['file'])
        self.config=self.root/'INPUTS.json'
        self.refresh()

    def write(self,name,x):
        p=self.root/name
        if isinstance(x,list):p.write_text(''.join(b.canonical(r)+'\n' for r in x))
        else:b.write_json(p,x)
        return p

    def row(self,i,raw='abc',final=None,padding=''):
        if final is None:final=raw
        binding=dict(parent_id=self.parent,id=i,split='train',crop_sha256=b.digest(i))
        edits=[];routes={};norm=None
        if i=='edit':
            e=dict(start=2,end=3,before='.',after='·')
            edits=[dict(e,tools=['numerics'])]
            routes['numerics']=dict(tool='numerics',tool_version='0.3',tool_digest='d'*64,binding=binding,raw_text_sha256=b.digest(raw),status='applied',edits=[e],evidence=dict(artifact_sha256='a'*64))
        if i=='normal':norm=dict(before=raw,after=final,policy='NFC-and-whitespace-only')
        d=dict(binding=binding,admitted=True,disposition='ADMIT',raw_text_sha256=b.digest(raw),final_text=final,final_text_sha256=b.digest(final),edits=edits,routes=routes,normalization=norm,toolchain_versions={},toolchain_digest='t',stages=[dict(evidence=padding)])
        return dict(binding,source='synthetic',book_id='book',edition_id='edition',raw_text=raw,raw_text_field='old_label',final_text=final,decision=d)

    def refresh(self):
        # Each crop is synthetic; hash is byte exact and rebound into the decision.
        manifest=[]
        for row in self.rows:
            i=row['id'];data=i.encode();h=b.digest(i)
            rel='collection_w1_originals/synthetic/'+i+'.png';p=self.work/rel;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data)
            row['crop_sha256']=h;row['decision']['binding']['crop_sha256']=h
            if i!='missing':manifest.append(dict(parent_id=self.parent,row_id=i,source='synthetic',split='train',relative_path=rel,sha256=h,bytes=len(data)))
        self.write('admitted_train',self.rows)
        self.write('admission_records',[dict(parent_id=r['parent_id'],row_id=r['id'],split='train',disposition='ADMIT',**{'pass':True},label=r['final_text'],decision=r['decision']) for r in self.rows])
        self.write('edition_map.jsonl',[dict(edition_id='edition',split='train',member_documents=['book'])])
        self.write('candidates_v3.jsonl',[dict(parent_id=self.parent,row_id='bench')])
        self.write('candidates_readout.jsonl',[dict(parent_id=self.parent,row_id='bench',crop_sha256=b.digest('pixels'))])
        summary=dict(complete=True,reconciled=True,outputs={n:dict(path=str(self.root/n),sha256=b.sha(self.root/n)) for n in ('admitted_train','admission_records')})
        self.write('summary.json',summary)
        self.write('CURRENT.json',dict(status='completed',summary_sha256=b.sha(self.root/'summary.json')))
        self.write('readout.json',dict(status='ok'))
        a=self.root/'crops';a.mkdir(exist_ok=True)
        self.write('crops/crops_manifest.jsonl',manifest)
        (a/'crops_sha256.txt').write_text(''.join(r['sha256']+'  '+r['relative_path']+'\n' for r in manifest))
        self.write('crops/upload_receipt.json',dict(status='ok',mode='full',sha256check_exit=0,failures=0,mismatches=0,byte_exact=len(manifest),selected=len(manifest),output_base=str(self.work),context=dict(tranche='W1',inputs={'CURRENT.json':b.sha(self.root/'CURRENT.json'),'summary.json':b.sha(self.root/'summary.json'),'admitted_train':b.sha(self.root/'admitted_train')})))
        names=['CURRENT.json','summary.json','readout.json','edition_map.jsonl','candidates_v3.jsonl','candidates_readout.jsonl','admitted_train','admission_records','external.jsonl','versions.json']
        inputs=[dict(name=n,path=n,sha256=b.sha(self.root/n),kind='large' if n in ('admitted_train','admission_records') else 'small',bytes=(self.root/n).stat().st_size) for n in names]
        self.cfg=dict(schema='synthetic',work_root=str(self.work),parents=[self.parent],inputs=inputs,registry=self.reg,sf7={'status':'pending'},crops=[dict(tranche='W1',attempt=str(a))])
        self.save()

    def save(self):b.write_json(self.config,self.cfg)
    def run(self,name='out'):return b.build(self.config,self.root/name)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.f=Fixture(self.temp.name)

    def test_end_to_end_edits_only_and_missing(self):
        r=self.f.run();self.assertEqual(r['counts']['released'],3)
        self.assertEqual(r['counts']['excluded_missing_exact_crop'],1)
        self.assertEqual(r['counts']['excluded_benchmark_pixels'],1)
        e=list(b.records(self.f.root/'out/release_v3_edits.jsonl'))
        self.assertEqual({r['row_id'] for r in e},{'edit','normal'})
        reg=json.loads((self.f.root/'out/corrections_registry.json').read_text())['versions']
        self.assertEqual(reg[-1]['release_rows_touched'],1)
        self.assertEqual(reg[-1]['release_rows_with_record'],2)
        self.assertEqual(reg[-1]['mode'],'external_registered_not_applied')

    def test_deterministic_bytes(self):
        self.f.run('one');self.f.run('two')
        for p in (self.f.root/'one').iterdir():self.assertEqual(p.read_bytes(),(self.f.root/'two'/p.name).read_bytes())

    def test_dev_edition_assertion(self):
        self.f.write('edition_map.jsonl',[dict(edition_id='edition',split='dev',member_documents=['book'])]);self.repin('edition_map.jsonl')
        with self.assertRaisesRegex(ValueError,'dev/test edition'):self.f.run()

    def test_benchmark_key_assertion(self):
        self.f.rows.append(self.f.row('bench'));self.f.refresh()
        with self.assertRaisesRegex(ValueError,'benchmark key'):self.f.run()

    def test_receipt_sha_mismatch(self):
        p=self.f.root/'summary.json';x=json.loads(p.read_text());x['outputs']['admitted_train']['sha256']='0'*64;b.write_json(p,x);self.repin('summary.json')
        c=json.loads((self.f.root/'CURRENT.json').read_text());c['summary_sha256']=b.sha(p);self.f.write('CURRENT.json',c);self.repin('CURRENT.json')
        with self.assertRaisesRegex(ValueError,'receipt sha mismatch'):self.f.run()

    def test_mutated_input_sha(self):
        with (self.f.root/'admitted_train').open('a') as f:f.write('{}\n')
        with self.assertRaisesRegex(ValueError,'input sha mismatch'):self.f.run()

    def test_crop_bytes_mismatch_dropped(self):
        (self.f.work/'collection_w1_originals/synthetic/same.png').write_bytes(b'bad')
        r=self.f.run();self.assertEqual(r['counts']['excluded_missing_exact_crop'],2)

    def test_unexplained_label_change_fails(self):
        self.f.rows[0]['final_text']='changed';d=self.f.rows[0]['decision'];d.update(final_text='changed',final_text_sha256=b.digest('changed'));self.f.refresh()
        with self.assertRaisesRegex(ValueError,'do not reconstruct'):self.f.run()

    def test_wrong_tool_version_fails(self):
        self.f.rows[1]['decision']['routes']['numerics']['tool_version']='invented';self.f.refresh()
        with self.assertRaisesRegex(ValueError,'tool/version mismatch'):self.f.run()

    def test_pending_crops_fail_closed(self):
        (self.f.root/'crops/upload_receipt.json').unlink()
        _,_,pending=b.input_check(self.f.root,self.f.cfg,light=True);self.assertEqual(pending,['W1_CROPS4_receipt'])
        with self.assertRaisesRegex(ValueError,'pending inputs'):self.f.run()

    def test_existing_output_refused(self):
        self.f.run()
        with self.assertRaisesRegex(ValueError,'output exists'):self.f.run()

    def test_admission_chain_mismatch(self):
        x=list(b.records(self.f.root/'admission_records'));x[0]['decision']['extra']='mismatch';self.f.write('admission_records',x);self.repin('admission_records')
        s=json.loads((self.f.root/'summary.json').read_text());s['outputs']['admission_records']['sha256']=b.sha(self.f.root/'admission_records');self.f.write('summary.json',s);self.repin('summary.json')
        self.f.write('CURRENT.json',dict(status='completed',summary_sha256=b.sha(self.f.root/'summary.json')));self.repin('CURRENT.json')
        p=self.f.root/'crops/upload_receipt.json';c=json.loads(p.read_text());c['context']['inputs'].update({'CURRENT.json':b.sha(self.f.root/'CURRENT.json'),'summary.json':b.sha(self.f.root/'summary.json')});b.write_json(p,c)
        with self.assertRaisesRegex(ValueError,'admission decision differs'):self.f.run()

    def repin(self,n):
        for x in self.f.cfg['inputs']:
            if x['name']==n:x.update(sha256=b.sha(self.f.root/n),bytes=(self.f.root/n).stat().st_size)
        self.f.save()


if __name__=='__main__':unittest.main()
