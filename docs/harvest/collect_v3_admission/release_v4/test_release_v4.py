import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
import build_release_v4 as b


class Fixture:
    def __init__(self,root,n=0):
        self.root=Path(root); self.root.mkdir(exist_ok=True)
        self.work=self.root/'work';self.work.mkdir()
        self.parent='collect-v3-W1-20261018-0524'
        self.reg=[dict(name='numerics_0.3',tool='numerics',version='0.3',tool_digest='d'*64,file='versions.json',sha256='',keying='binding',mode='census_internal',artifacts=[dict(parent_id=self.parent,sha256='a'*64)]),
                  dict(name='composer_0.3',tool='composer',version='0.3',tool_digest='c'*64,file='versions.json',sha256='',keying='binding',mode='census_internal',artifacts=[]),
                  dict(name='external',parent_id=self.parent,file='external.jsonl',sha256='',keying='id',id_field='id',text_field='text',parent_text_field='parent_text',mode='external_registered_not_applied')]
        self.reg.insert(0,dict(name='sf7',tool='polytonic',version='0.7',tool_digest='p'*64,artifacts=[],file='release_v4_sf7_edits.jsonl',sha256=None,keying='row_id',id_field='row_id',text_field='text',parent_text_field='parent_text',mode='external_registered_not_applied',status='released'))
        self.extra_records=[]; self.old_rows=[dict(parent_id=self.parent,row_id='missing',source='synthetic')];self.sf7_records=[]
        self.rows=[self.row('same'),self.row('edit','12.34','12·34'),self.row('normal',' α  β ','α β'),self.row('missing'),self.row('pixels')]
        self.rows += [self.row('bulk'+str(i),padding='x'*20000) for i in range(n)]
        self.write('external.jsonl',[dict(id='edit',text='12·34',parent_text='12.34'),dict(id='same',text='abc',parent_text='abc')])
        self.write('versions.json',{})
        for r in self.reg:
            if r['name']!='sf7':r['sha256']=b.sha(self.root/r['file'])
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
        d=dict(pipeline_version='0.3.3',binding=binding,admitted=True,disposition='ADMIT',raw_text_sha256=b.digest(raw),final_text=final,final_text_sha256=b.digest(final),edits=edits,routes=routes,normalization=norm,toolchain_versions={},toolchain_digest='t',stages=[dict(evidence=padding)])
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
        self.write('admission_records',[dict(parent_id=r['parent_id'],row_id=r['id'],split='train',disposition='ADMIT',**{'pass':True},source=r['source'],label=r['final_text'],decision=r['decision']) for r in self.rows]+self.extra_records+[dict(parent_id=self.parent,row_id='missing',source='synthetic',decision=dict(pipeline_version='0.3.3',routes={})) for _ in [0] if not any(r['id']=='missing' for r in self.rows) and any(r['row_id']=='missing' for r in self.old_rows)])
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
        self.write('seal04_test',[]);self.write('seal04_dev',[])
        self.write('release_v3_admission',self.old_rows)
        self.write('RELEASE_V3_RECEIPT.json',dict(status='ok',outputs={'release_v3_admission.jsonl':dict(sha256=b.sha(self.root/'release_v3_admission'))}))
        self.write('sf7.jsonl',self.sf7_records)
        led=dict(path='sf7.jsonl',sha256=b.sha(self.root/'sf7.jsonl'),bytes=(self.root/'sf7.jsonl').stat().st_size,parent_id=self.parent,tool='polytonic',status='released',format='line-tool-result-v1')
        self.reg[0]['artifacts']=[led]
        names=['seal04_test','seal04_dev','release_v3_admission','RELEASE_V3_RECEIPT.json','CURRENT.json','summary.json','readout.json','edition_map.jsonl','candidates_v3.jsonl','candidates_readout.jsonl','admitted_train','admission_records','external.jsonl','versions.json']
        inputs=[dict(name=n,path=n,sha256=b.sha(self.root/n),kind='large' if n in ('admitted_train','admission_records') else 'small',bytes=(self.root/n).stat().st_size) for n in names]
        self.cfg=dict(schema='synthetic',work_root=str(self.work),parents=[self.parent],inputs=inputs,registry=self.reg,sf7=dict(status='released',version='0.7',tool_digest='p'*64,binding_status='bound',ledgers=[led]),crops=[dict(tranche='W1',attempt=str(a))])
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
        e=list(b.records(self.f.root/'out/release_v4_edits.jsonl'))
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
        with self.assertRaisesRegex(ValueError,'missing_crop_new_admits must be zero'):self.f.run()

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



class Rel4Tests(unittest.TestCase):
    setUp=ReleaseTests.setUp
    repin=ReleaseTests.repin
    def add_poly(self):
        f=self.f; row=f.row('poly','α. β','ἁ· β'); d=row['decision']
        pe=dict(start=0,end=1,before='α',after='ἁ')
        ne=dict(start=1,end=2,before='.',after='·')
        ledger=dict(tool='polytonic',tool_version='0.7',tool_digest='p'*64,binding=copy.deepcopy(d['binding']),raw_text_sha256=b.digest(row['raw_text']),status='applied',edits=[copy.deepcopy(pe)])
        f.sf7_records=[ledger]
        h=b.digest(b.canonical(ledger)+'\n')
        d['routes']['polytonic']=dict(copy.deepcopy(ledger),evidence=dict(artifact_sha256=h,original_record_sha256=b.digest(b.canonical(ledger))))
        d['routes']['numerics']=dict(tool='numerics',tool_version='0.3',tool_digest='d'*64,binding=d['binding'],raw_text_sha256=b.digest(row['raw_text']),status='applied',edits=[ne],evidence=dict(artifact_sha256='a'*64))
        d['edits']=[dict(pe,tools=['polytonic']),dict(ne,tools=['numerics'])]
        f.rows.append(row);f.refresh();return row

    def test_raw_labels_when_final_differs(self):
        self.add_poly();self.f.run()
        rows={r['row_id']:r for r in b.records(self.f.root/'out/release_v4_admission.jsonl')}
        for row in self.f.rows:
            if row['id'] in rows:
                out=rows[row['id']];self.assertEqual(out['label'],row['raw_text']);self.assertEqual(b.digest(out['label']),out['raw_text_sha256'])
        self.assertEqual(rows['poly']['label'],'α. β')

    def test_sf7_only_and_overlay_roundtrip(self):
        self.add_poly();receipt=self.f.run()
        self.assertEqual(receipt['polytonic_released_per_parent'][self.f.parent]['applied'],1)
        from rel4_contract import parse_overlay_record
        rows=list(b.records(self.f.root/'out/release_v4_sf7_edits.jsonl'))
        self.assertEqual(len(rows),1);r=rows[0]
        self.assertEqual(r['parent_text'],'α. β');self.assertEqual(r['text'],'ἁ. β')
        self.assertEqual(parse_overlay_record(json.loads(b.canonical(r)),dict(id_field='row_id',text_field='text')),r)
        self.assertEqual(r['provenance']['ledger_record']['record_sha256'],b.digest(b.canonical(self.f.sf7_records[0])))
        edits={r['row_id']:r for r in b.records(self.f.root/'out/release_v4_edits.jsonl')}
        self.assertEqual(edits['poly']['label'],'α· β')
        self.assertNotIn('polytonic',edits['poly']['routes'])
        self.assertTrue(all('polytonic' not in e['tools'] for e in edits['poly']['edits']))

    def test_actual_reader_parsing_ast_unchanged(self):
        # Heavy driver imports train modules; extract its side-effect-free registry
        # function unchanged by AST, supplying exactly its IO dependencies.
        import ast
        root=Path(__file__).parent
        tree=ast.parse((root/'evidence/e4_wave1c.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='registry')
        module=ast.Module(body=[node],type_ignores=[])
        scope=dict(Path=Path,read_json=lambda p:json.loads(Path(p).read_text()),sha256=b.sha,read_rows=b.records)
        exec(compile(module,'bench/e4_wave1c.py','exec'),scope)
        self.add_poly();self.f.run();p=self.f.root/'out/release_v4_sf7_edits.jsonl'
        reg=self.f.write('overlay_registry.json',dict(schema='lqb-versions-v1',versions=dict(sf7=dict(path=str(p),sha256=b.sha(p),population=dict(rows=1),parent=None,id_field='row_id',text_field='text',status='released',read='exact text'))))
        loaded=scope['registry'](reg,['sf7'],production=True)
        self.assertEqual(loaded['sf7']['rows']['poly']['text'],'ἁ. β')

    def test_sf7_ledger_reference_mismatch(self):
        row=self.add_poly();row['decision']['routes']['polytonic']['evidence']['original_record_sha256']='0'*64;self.f.refresh()
        with self.assertRaisesRegex(ValueError,'ledger record reference mismatch'):self.f.run()

    def test_sf7_ledger_span_mismatch(self):
        row=self.add_poly();ledger=self.f.sf7_records[0];ledger['edits'][0]['after']='ἂ'
        route=row['decision']['routes']['polytonic'];route['evidence'].update(artifact_sha256=b.digest(b.canonical(ledger)+'\n'),original_record_sha256=b.digest(b.canonical(ledger)))
        self.f.refresh()
        with self.assertRaisesRegex(ValueError,'ledger spans mismatch'):self.f.run()

    def test_sf7_registry_touch_counts(self):
        self.add_poly();self.f.run()
        versions=json.loads((self.f.root/'out/corrections_registry.json').read_text())['versions'];r=next(r for r in versions if r['name']=='sf7')
        self.assertEqual((r['release_rows_touched'],r['release_rows_with_record']),(1,1))
        self.assertEqual(r['sha256'],b.sha(self.f.root/'out/release_v4_sf7_edits.jsonl'))
        self.assertEqual(r['mode'],'external_registered_not_applied');self.assertEqual(r['status'],'released')

    def test_flip_counts_polytonic_hold_and_edit(self):
        self.add_poly();f=self.f
        f.rows=[r for r in f.rows if r['id']!='missing']
        f.old_rows=[dict(parent_id=f.parent,row_id='old_hold',source='synthetic'),dict(parent_id=f.parent,row_id='same',source='synthetic')]
        held=f.row('old_hold');held['decision'].update(admitted=False,disposition='HOLD',routes=dict(polytonic=dict(status='required_evidence_unresolved',edits=[])))
        f.extra_records=[dict(parent_id=f.parent,row_id='old_hold',source='synthetic',decision=held['decision'],split='train',disposition='HOLD',**{'pass':False},label='abc')]
        f.refresh();receipt=f.run()
        counts={(x['direction'],x['reason']):x['rows'] for x in receipt['flips']}
        self.assertEqual(counts,{('added','other'):2,('added','polytonic edit'):1,('removed','polytonic hold'):1})
        self.assertEqual(len(list(b.records(f.root/'out/release_v4_flips.jsonl'))),4)

    def test_missing_crop_new_admits(self):
        f=self.f;f.old_rows=[dict(parent_id=f.parent,row_id='same',source='synthetic')];f.refresh()
        with self.assertRaisesRegex(ValueError,'missing_crop_new_admits must be zero'):f.run()
        failed=json.loads((f.root/'out/FAILED.json').read_text())
        self.assertEqual(failed['counts']['missing_crop_new_admits'],1)
        self.assertFalse((f.root/'out/RELEASE_V4_RECEIPT.json').exists())

    def test_missing_crop_existing_row_not_new(self):
        f=self.f;f.old_rows=[dict(parent_id=f.parent,row_id='missing',source='synthetic')];f.refresh();r=f.run()
        self.assertEqual(r['counts']['missing_crop_new_admits'],0)
        self.assertFalse(r['requires_crops4_top_up'])

    def test_seal04_key_assertion(self):
        self.f.write('seal04_test',[dict(parent_id=self.f.parent,row_id='same',crop_sha256='1'*64,split='test')]);self.repin('seal04_test')
        with self.assertRaisesRegex(ValueError,'benchmark key'):self.f.run()

    def test_seal04_pixel_drop(self):
        self.f.write('seal04_dev',[dict(parent_id='another',row_id='sealed',crop_sha256=b.digest('same'),split='dev')]);self.repin('seal04_dev')
        r=self.f.run();self.assertEqual(r['counts']['excluded_benchmark_pixels'],2)

    def test_pending_sf7_refuses_before_output(self):
        self.f.cfg['sf7']['binding_status']='pending';self.f.save()
        with self.assertRaisesRegex(ValueError,'pending inputs: sf7'):self.f.run()
        self.assertFalse((self.f.root/'out').exists())

    def test_pending_census06_refuses_before_output(self):
        self.f.cfg['inputs'][0].update(sha256=None,group='census_06');self.f.save()
        with self.assertRaisesRegex(ValueError,'pending inputs: census_06'):self.f.run()
        self.assertFalse((self.f.root/'out').exists())

    def test_receipt_binds_generation_outputs(self):
        r=self.f.run()
        self.assertTrue((self.f.root/'out/RELEASE_V4_RECEIPT.json').is_file())
        for name in ('CURRENT.json','summary.json','admission_records','admitted_train'):
            self.assertEqual(r['admission_receipt_chain'][name]['sha256'],b.sha(self.f.root/name))
        for name,meta in r['outputs'].items():self.assertEqual(meta['sha256'],b.sha(self.f.root/'out'/name))

    def test_overlay_rejects_missing_provenance(self):
        from rel4_contract import parse_overlay_record
        with self.assertRaisesRegex(ValueError,'provenance'):parse_overlay_record(dict(row_id='r',text='x'),dict(id_field='row_id',text_field='text'))

    def test_non_sf7_file_empty_without_internal_edits(self):
        self.f.rows=[self.f.row('same')];self.f.refresh();self.f.run()
        self.assertEqual((self.f.root/'out/release_v4_edits.jsonl').read_bytes(),b'')
        self.assertEqual((self.f.root/'out/release_v4_sf7_edits.jsonl').read_bytes(),b'')

    def test_sf7_split_rebound_original_record(self):
        row=self.add_poly();ledger=self.f.sf7_records[0];ledger['binding']['split']='dev'
        h=b.digest(b.canonical(ledger)+'\n');route=row['decision']['routes']['polytonic']
        route['evidence'].update(artifact_sha256='rebound-file',original_record_sha256='rebound-record',split_input_binding=dict(source_artifact_sha256=h,source_record_sha256=b.digest(b.canonical(ledger)),original_binding=copy.deepcopy(ledger['binding'])))
        self.f.refresh();self.f.run()
        r=next(b.records(self.f.root/'out/release_v4_sf7_edits.jsonl'))
        self.assertEqual(r['provenance']['ledger_sha256'],h)

    def test_non_sf7_normalization_reconstructs(self):
        self.f.run();rows=list(b.records(self.f.root/'out/release_v4_edits.jsonl'))
        from rel4_contract import apply_spans
        for row in rows:
            text=apply_spans(row['raw_text'],row['edits'])
            if row['normalization']:
                self.assertEqual(row['normalization']['before'],text);text=row['normalization']['after']
            self.assertEqual(text,row['label'])

    def test_census05_schema_witness(self):
        samples=list(b.records(Path(__file__).parent/'evidence/census05_sample_rows.jsonl'))
        sample=next(x for x in samples if 'raw_text' in x)
        sample=copy.deepcopy(sample);sample['decision']['pipeline_version']='0.3.3' # replay baseline edits under the expected export contract
        b.validate_edits(sample,self.f.cfg)
        self.assertEqual(sample['raw_text'],sample['final_text'])

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.f=Fixture(self.temp.name)

    def production_fixture(self):
        f=self.f
        cfg=copy.deepcopy(f.cfg);cfg['schema']='release-v4-package-v1'
        attempt=f.work/'census_06_20261020/attempts/full-split-002'
        gen=attempt/'generations/g1-fixture';gen.mkdir(parents=True)
        readout=Path(str(attempt)+'.readout')/'readout.json';readout.parent.mkdir()
        ledgers=copy.deepcopy(cfg['sf7']['ledgers'])
        for x in ledgers:x['path']=str((f.root/x['path']).resolve())
        versions=dict(tools=dict(polytonic=dict(version='0.7',digest='p'*64,scope='released'),numerics=dict(version='0.3',digest='d'*64),composer=dict(version='0.3',digest='c'*64)))
        tv=f.write('c06_versions.json',versions)
        (f.root/'inputs').mkdir();b.write_json(f.root/'inputs/census06_expected_tool_versions.json',versions)
        cc=dict(versions=str(tv),corrections=ledgers,routes_out_of_scope=[])
        cp=f.write('c06_config.json',cc)
        binding=dict(config=cc,versions_sha256=b.sha(tv));cfg['census_run_binding']=binding
        summary=json.loads((f.root/'summary.json').read_text());summary['run_binding_sha256']=b.digest(b.canonical(binding))
        for n in ('admitted_train','admission_records'):
            (gen/(n+'.jsonl')).write_bytes((f.root/n).read_bytes());summary['outputs'][n]['path']=str(gen/(n+'.jsonl'))
        b.write_json(gen/'summary.json',summary)
        b.write_json(attempt/'CURRENT.json',dict(status='completed',summary_path=str(gen/'summary.json'),summary_sha256=b.sha(gen/'summary.json'),run_binding_sha256=summary['run_binding_sha256']))
        import sqlite3
        with sqlite3.connect(attempt/'ledger.sqlite') as con:
            con.execute('CREATE TABLE run(key TEXT,value TEXT)');con.execute('INSERT INTO run VALUES (?,?)',('binding',b.canonical(binding)))
        files=[dict(path=str(p),sha256=b.sha(p)) for p in [attempt/'CURRENT.json',gen/'summary.json',gen/'admitted_train.jsonl',gen/'admission_records.jsonl']]
        b.write_json(readout,dict(complete=True,problems=dict(example=dict(count=0)),invariants=dict(example=dict(status='PASS')),generation=str(gen),files=files))
        for i in cfg['inputs']:i['path']=str(f.root/i['path'])
        cfg['census_attempt']=str(attempt)
        cfg['crop_census']={n:b.sha(f.root/n) for n in ('CURRENT.json','summary.json','admitted_train')}
        for n in ('census06_config.json','census06_tool_versions.json','seal04_suite.json','seal04_receipt.json'):
            p=cp if n=='census06_config.json' else tv if n=='census06_tool_versions.json' else f.write(n,{})
            cfg['inputs'].append(dict(name=n,path=str(p),sha256=b.sha(p),kind='small'))
        for i in cfg['inputs']:
            if i['name'] in ('CURRENT.json','summary.json','admitted_train','admission_records','readout.json','census06_config.json','census06_tool_versions.json'):
                i.update(group='census_06',sha256=None)
        return cfg,cp,tv,readout

    def test_completed_census_binding_roundtrip(self):
        from bind_release_v4 import bind_config
        cfg,cp,tv,readout=self.production_fixture()
        bound=bind_config(self.f.root,cfg,cp,tv,readout)
        self.assertEqual(bound['sf7']['binding_status'],'bound')
        _,_,pending=b.input_check(self.f.root,bound,light=True);self.assertEqual(pending,[])
        self.assertEqual(bound['sf7']['ledgers'],json.loads(cp.read_text())['corrections'])

    def test_readout_mixed_generation_rejected(self):
        from bind_release_v4 import bind_config
        cfg,cp,tv,readout=self.production_fixture();r=json.loads(readout.read_text());r['generation']=str(self.f.root);b.write_json(readout,r)
        with self.assertRaisesRegex(ValueError,'generation mismatch'):bind_config(self.f.root,cfg,cp,tv,readout)

    def test_binding_rejects_unrelated_census_config(self):
        from bind_release_v4 import bind_config
        cfg,cp,tv,readout=self.production_fixture();r=json.loads(cp.read_text());r['unrelated']=True;b.write_json(cp,r)
        with self.assertRaisesRegex(ValueError,'differs from completed run'):bind_config(self.f.root,cfg,cp,tv,readout)

    def test_submit_pending_never_reaches_sbatch(self):
        import subprocess,sys,os
        source=Path(__file__).resolve().parent;f=self.f
        wrapper=f.root/'submit_release_v4.sh';wrapper.write_bytes((source/'submit_release_v4.sh').read_bytes())
        verify=f.root/'VERIFY.sh'
        import shlex
        verify.write_text('#!/bin/bash\nif [[ "$1" == package ]]; then exit 0; fi\nexec '+shlex.quote(sys.executable)+' -B '+shlex.quote(str(source/'verify_release_v4.py'))+' inputs --config '+shlex.quote(str(f.config))+'\n')
        sbatch=f.root/'sbatch';sentinel=f.root/'SUBMITTED'
        sbatch.write_text('#!/bin/bash\ntouch '+shlex.quote(str(sentinel))+'\n');sbatch.chmod(0o755)
        for pending in ('sf7','census_06'):
            cfg=copy.deepcopy(f.cfg)
            if pending=='sf7':cfg['sf7']['binding_status']='pending'
            else:cfg['inputs'][0].update(group='census_06',sha256=None)
            b.write_json(f.config,cfg)
            r=subprocess.run(['bash',str(wrapper),'rel4_pending_fixture'],capture_output=True,text=True,env=dict(os.environ,PATH=str(f.root)+os.pathsep+os.environ['PATH']))
            self.assertEqual(r.returncode,2,r.stderr);self.assertIn(pending+' PENDING',r.stdout);self.assertFalse(sentinel.exists())

if __name__=='__main__':unittest.main()

# REL4b: explicit status and CROPS4C refusal witnesses.
import pytest
from crops4c_contract import validate as validate_crops4c


def valid_crops4c():
    context=dict(tranche='all',include_heldout=True,inputs={'CURRENT.json':'a'*64})
    per={t:dict(selected=1,written=0,skipped_valid=1,mismatches=0,failures=0,bytes=3) for t in ('W1','W2')}
    r=dict(status='ok',mode='full',context=context,output_base='/work',sha256check_exit=0,mismatches=0,failures=0,byte_exact=2,selected=2,written=0,skipped_valid=2,bytes=6,train_selected=1,heldout_selected=1,selection_sha256='s'*64,per_tranche=per)
    smoke=dict(status='ok',mode='smoke',context=dict(context,tranche='W2'),selected=500,byte_exact=500,sha256check_exit=0,failures=0,mismatches=0,output_base='/smoke/smoke')
    cfg=dict(work_root='/work',crops4c=dict(context=copy.deepcopy(context),smoke_attempt='/smoke'))
    return r,smoke,cfg,context['inputs']


@pytest.mark.parametrize('field,value',[
    ('status','failed'),('mode','smoke'),('context.tranche','W2'),('context.include_heldout',False),
    ('output_base','/wrong'),('sha256check_exit',1),('mismatches',1),('failures',1),
    ('byte_exact',1),('selected',3),('written',1),('skipped_valid',1),('train_selected',0),('heldout_selected',0),
    ('selection_sha256','bad'),('per_tranche.W1.selected',2),('per_tranche.W1.written',1),
    ('per_tranche.W1.skipped_valid',0),('per_tranche.W1.mismatches',1),('per_tranche.W1.failures',1),('per_tranche.W1.bytes',4),
    ('context.inputs',{}),('context.census_code','/wrong')])
def test_crops4c_each_check(field,value):
    r,smoke,cfg,inputs=valid_crops4c();target=r
    parts=field.split('.')
    for part in parts[:-1]:target=target[part]
    target[parts[-1]]=value
    with pytest.raises(ValueError,match='CROPS4C'):validate_crops4c(r,smoke,cfg,inputs,b.require)


@pytest.mark.parametrize('field,value',[('status','failed'),('mode','full'),('selected',499),('byte_exact',499),('context',{}),('sha256check_exit',1),('failures',1),('mismatches',1),('output_base','/wrong')])
def test_crops4c_smoke_rejected(field,value):
    r,smoke,cfg,inputs=valid_crops4c();smoke[field]=value
    with pytest.raises(ValueError,match='CROPS4C'):validate_crops4c(r,smoke,cfg,inputs,b.require)


def test_crops4c_valid():
    r,s,c,i=valid_crops4c();validate_crops4c(r,s,c,i,b.require)


@pytest.mark.parametrize('status',['kept_unverified','verified_no_change','required_evidence_unresolved','proposal_only','failed','applied'])
def test_overlay_status_gate(tmp_path,status):
    from rel4_contract import sf7_record
    row=dict(parent_id='p',id='r',decision=dict(routes=dict(polytonic=dict(status=status,edits=[]))))
    assert sf7_record(row,{},b.require,b.digest,b.canonical) is None
    if status!='applied':
        row['decision']['routes']['polytonic']['edits']=[dict(start=0,end=1,before='a',after='b')]
        assert sf7_record(row,{},b.require,b.digest,b.canonical) is None


@pytest.mark.parametrize('status',['kept_unverified','verified_no_change'])
@pytest.mark.parametrize('index',[0,1])
def test_released_status_counts_and_raw(tmp_path,status,index):
    f=Fixture(tmp_path);row=f.rows[index];row['primary_class']='prose'
    row['decision']['routes']['polytonic']=dict(status=status,edits=[],evidence=dict(kept_unverified=True,reason='insufficient evidence'))
    f.refresh();r=f.run()
    assert r['polytonic_released_per_parent'][f.parent][status]==1
    assert r['polytonic_released_per_class']['prose'][status]==1
    assert dict(parent_id=f.parent,line_class='prose',status=status,rows=1) in r['polytonic_released_per_parent_class']
    out=next(x for x in b.records(f.root/'out/release_v4_admission.jsonl') if x['row_id']==row['id'])
    assert out['label']==row['raw_text']
    assert not list(b.records(f.root/'out/release_v4_sf7_edits.jsonl'))


def test_pipeline_032_rejected(tmp_path):
    f=Fixture(tmp_path);f.rows[0]['decision']['pipeline_version']='0.3.2';f.refresh()
    with pytest.raises(ValueError,match='pipeline_version'):f.run()


def test_union_and_new_admit_c06(tmp_path):
    f=Fixture(tmp_path);a=f.root/'c06';a.mkdir()
    old=list(b.records(f.root/'crops/crops_manifest.jsonl'))
    missing=f.rows[3];rel='collection_w1_originals/synthetic/missing.png'
    new=dict(parent_id=f.parent,row_id='missing',source='synthetic',split='train',relative_path=rel,sha256=missing['crop_sha256'],bytes=7)
    manifest=old+[new]
    f.write('c06/crops_manifest.jsonl',manifest)
    (a/'crops_sha256.txt').write_text(''.join(x['sha256']+'  '+x['relative_path']+'\n' for x in manifest))
    f.write('c06/upload_receipt.json',dict(byte_exact=5,selected=5,train_selected=5,heldout_selected=0,bytes=sum(x['bytes'] for x in manifest),per_tranche=dict(W1=dict(selected=5,bytes=sum(x['bytes'] for x in manifest)),W2=dict(selected=0,bytes=0))))
    cfg=copy.deepcopy(f.cfg);cfg['crops4c']=dict(binding_status='bound',attempt=str(a))
    crops,_=b.crop_index(cfg)
    assert len(crops)==5 and crops[(f.parent,'missing')][0]==missing['crop_sha256']
    # Exercise the real builder with the validated union; receipt validator tested separately.
    original=b.crop_index
    try:
        b.crop_index=lambda ignored:original(cfg)
        f.old_rows=[];f.refresh();r=f.run()
        assert r['counts']['missing_crop_new_admits']==0 and r['counts']['released']==4
    finally:b.crop_index=original

@pytest.mark.parametrize('tamper',[None,'native','versions','materialiser','interpreter','codec','package_manifest','code_id','full_manifest','smoke_receipt','census_input'])
def test_crops4c_binding_custody(tmp_path,tamper):
    from crops4c_contract import bind,check,FILES
    r,smoke,cfg,inputs=valid_crops4c()
    cfg['work_root']=str(tmp_path);r['output_base']=str(tmp_path)
    full=tmp_path/'crops4_attempts/crops4_c06_full_01';sm=tmp_path/'crops4_attempts/crops4_c06_smoke_01'
    full.mkdir(parents=True);sm.mkdir()
    cfg['crops4c'].update(attempt=str(full),smoke_attempt=str(sm))
    native=Path(__file__).parents[2]/'census06/package/projects/greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py'
    contents={'package/projects/pipe/greekocr/harvest/line_pipeline_native.py':native.read_bytes(),'package/projects/pipe/docs/tool_versions.json':b'{}'}
    manifest_data=''.join(b.digest(v.decode())+'  '+k+'\n' for k,v in contents.items())
    base=tmp_path/'code'/b.digest(manifest_data)[:16];base.mkdir(parents=True)
    manifest=base/'DEPLOY_SHA256SUMS';manifest.write_text(manifest_data)
    for n,data in contents.items():
        p=base/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    versions=base/'package/projects/pipe/docs/tool_versions.json';nf=base/'package/projects/pipe/greekocr/harvest/line_pipeline_native.py'
    package=tmp_path/'crops4_package/9a3b80c1';package.mkdir(parents=True)
    module=package/'materialise_crops.py';module.write_text('materialiser')
    deploy=package/'DEPLOY_SHA256SUMS';deploy.write_text(b.sha(module)+'  materialise_crops.py\n')
    cfg['crops4c_package_manifest_sha256']=b.sha(deploy)
    interpreter=tmp_path/'python';interpreter.write_text('python');codec=tmp_path/'codec';codec.write_text('codec')
    byname={}
    for n in ('CURRENT.json','summary.json'):
        byname[n]=tmp_path/n;b.write_json(byname[n],{})
    b.write_json(byname['summary.json'],dict(outputs={n:dict(sha256=n*4) for n in ('admitted_train','decisions','evaluation_diagnostics')}))
    inputs={n:b.sha(byname[n]) for n in byname}
    inputs.update({n:n*4 for n in ('admitted_train','decisions','evaluation_diagnostics')})
    context=dict(inputs=inputs,tranche='all',include_heldout=True,census_code=str(nf.parents[2]),code_sha256=b.sha(module),reconstruction_module='greekocr.harvest.line_pipeline_native',reconstruction_function='reconstructed_crop',reconstruction_file=str(nf),reconstruction_sha256=b.sha(nf),interpreter=str(interpreter),interpreter_sha256=b.sha(interpreter),codec_preload=str(codec),codec_preload_sha256=b.sha(codec))
    r['context']=context;smoke['context']=dict(context,tranche='W2');smoke['output_base']=str(sm/'smoke')
    for a,receipt in ((full,r),(sm,smoke)):
        for n in FILES:(a/n).write_text('evidence')
        b.write_json(a/'upload_receipt.json',receipt)
    if tamper in ('native','versions','materialiser','interpreter','codec','package_manifest'):
        {'native':nf,'versions':versions,'materialiser':module,'interpreter':interpreter,'codec':codec,'package_manifest':deploy}[tamper].write_text('changed')
    if tamper=='code_id':manifest.write_text(manifest_data+'\n')
    if tamper in ('native','versions','materialiser','interpreter','codec','package_manifest','code_id'):
        with pytest.raises(ValueError,match='CROPS4C'):bind(cfg,manifest,versions,b.sha,b.require)
        return
    bind(cfg,manifest,versions,b.sha,b.require)
    if tamper=='full_manifest':(full/'crops_manifest.jsonl').write_text('changed')
    if tamper=='smoke_receipt':(sm/'upload_receipt.json').write_text('changed')
    if tamper=='census_input':byname['CURRENT.json'].write_text('changed')
    if tamper:
        with pytest.raises(ValueError,match='CROPS4C'):check(tmp_path,cfg,byname,b.sha,b.require)
    else:assert check(tmp_path,cfg,byname,b.sha,b.require)['check']=='full_smoke_and_custody'


def test_wave2_handoff_hashes_and_mutation(tmp_path):
    from handoff_release_v4 import handoff
    f=Fixture(tmp_path);f.run();receipt=f.root/'out/RELEASE_V4_RECEIPT.json'
    args=handoff(receipt)
    assert len(args)==8 and args['RELEASE_V4_RECEIPT.json']['sha256']==b.sha(receipt)
    (f.root/'out/release_v4_sf7_edits.jsonl').write_text('mutated')
    with pytest.raises(ValueError,match='handoff SHA mismatch'):handoff(receipt)
