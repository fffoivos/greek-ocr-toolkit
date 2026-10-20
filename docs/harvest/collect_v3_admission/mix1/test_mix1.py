import unittest
from collections import Counter
from fractions import Fraction as F
from core import *
class DrawTests(unittest.TestCase):
 def test_largest_remainder(self):self.assertEqual(lr({'a':1,'b':1,'c':1},5),{'a':2,'b':2,'c':1})
 def test_fraction_totals(self):
  self.assertEqual([sum(epoch_counts([p]*8)) for p in (40,50,60)],[1372390,1715488,2058586])
 def test_epoch_error(self):
  for p in (40,50,60):self.assertTrue(all(abs(n-D*p/100)<1 for n in epoch_counts([p]*8)))
 def test_curriculum_total(self):self.assertEqual(sum(epoch_counts([70]*4+[30]*4)),1715488)
 def test_curriculum_images(self):
  for counts in ([50]*8,[70]*4+[30]*4):
   syn=epoch_counts(counts);real=[D-n for n in syn]
   for p,q in [('s',syn),('r',real)]:
    exposure=Counter(x for e in stream_epochs(list(range(137)),q,p) for x in e)
    if counts==[50]*8:setattr(self,p,exposure)
    else:self.assertEqual(getattr(self,p),exposure)
 def test_cap_first(self):
  p=script_quota({'parl':80,'cy':2,'greek':18},{'cy'},{'parl'},True)
  self.assertEqual(p,{'parl':F(1,4),'cy':F(6,100),'greek':F(69,100)})
 def test_uncapped_separate(self):self.assertEqual(script_quota({'p':30,'c':2,'g':68},{'c'},{'p'},False)['p'],F(3,10))
 def test_temperature_cap(self):
  p,l=temperature({'p':81,'g':16,'h':9},.5,{'p'})
  self.assertEqual(p['p'],F(1,4));self.assertEqual(p['g']/p['h'],F(4,3));self.assertEqual(sum(p.values()),1)
 def test_temperature_one(self):self.assertEqual(temperature({'a':3,'b':2},1,set())[0],{'a':F(3,5),'b':F(2,5)})
 def test_cap_no_support(self):
  with self.assertRaises(ValueError):cap({'p':3},{'p'})
 def test_m1_unsupported(self):
  r=[dict(script_class='a',width=129,line_id='a'),dict(script_class='b',width=128,line_id='b')];b=[r[0]]
  out,ledger=replay([(0,0,'a'),(0,1,'b'),(1,0,'s')],r,b,1,1)
  self.assertEqual(out,[(2,0,'a'),(0,1,'b'),(1,0,'s')]);self.assertTrue(ledger[1]['unsupported'])
 def test_m1_no_support(self):
  with self.assertRaises(ValueError):replay([(0,0,'a')],[dict(script_class='a',width=128)],[],1,1)
 def test_e1_val_id(self):
  with self.assertRaises(ValueError):exclude([dict(line_id='a',source_doc_id='a',split='train')],[dict(line_id='a',source_doc_id='b')])
 def test_e1_test_document(self):
  with self.assertRaises(ValueError):exclude([dict(line_id='a',source_doc_id='d',split='train')],[dict(line_id='b',source_doc_id='d')])
 def test_e1_split(self):
  with self.assertRaises(ValueError):exclude([dict(line_id='a',source_doc_id='a',split='val')],[])
 def test_exposure_edition(self):self.bad('edition_id','e',dict(editions={'e'},keys=set(),crops=set()))
 def test_exposure_key(self):self.bad('key',['p','i'],dict(editions=set(),keys={('p','i')},crops=set()))
 def test_exposure_crop(self):self.bad('crop_sha256','h',dict(editions=set(),keys=set(),crops={'h'}))
 def test_unknown_edition(self):self.bad('edition_id',None,dict(editions=set(),keys=set(),crops=set()))
 def test_nontrain(self):self.bad('split','test',dict(editions=set(),keys=set(),crops=set()))
 def bad(self,k,v,b):
  r=dict(edition_id='ok',key=['p','ok'],crop_sha256='ok',split='train');r[k]=v
  with self.assertRaises(ValueError):audit(r,b)
 def test_determinism(self):self.assertEqual(cycle(list(range(100)),250,SEED),cycle(list(range(100)),250,SEED))
 def test_bucket(self):self.assertEqual(stratum(dict(script_class='g',width=129)),('g',256))

class ManifestTests(unittest.TestCase):
 def test_real_emitter_and_trainer_consumer(self):
  import tempfile,importlib.util
  from generate import generate
  def pool(prefix,n):
   return [dict(line_id=f'{prefix}{i}',source_doc_id=f'{prefix}doc',key=[prefix,str(i)],edition_id=prefix,crop_sha256=f'{prefix}{i}',split='train',script_class='g',width=128) for i in range(n)]
  pools=[pool('r',31),pool('s',17),pool('b',9)]
  blocked=dict(editions=set(),keys=set(),crops=set())
  with tempfile.TemporaryDirectory() as tmp:
   plans=generate(tmp,pools,blocked,d=100)
   from index_contract import verify_index
   from generate import fraction_epochs,indexed_epoch
   for arm,entry in plans.items():
    plan=json.loads(Path(entry['path']).read_text());self.assertEqual(set(plan['epochs']),set(map(str,range(1,9))))
    index=Path(entry['path']).parent/plan['index']['path']
    data=list(rows(index));self.assertEqual(len(data),800)
    for e,pos,c,i,ident in data:self.assertEqual(pools[c][i]['line_id'],ident)
    epochs=[[(c,i,ident) for ee,pos,c,i,ident in data if ee==e] for e in range(1,9)]
    verify_index(index,epochs,pools)
    self.assertEqual(plan['seed_provenance'],20261015)
 def test_generator_rejects_unknown_edition(self):
  from generate import generate
  with self.assertRaisesRegex(ValueError,'unknown edition'):generate('/unused',[[dict(split='train')],[]],dict(editions=set(),keys=set(),crops=set()),active=('M2',),d=10)

if __name__=='__main__':unittest.main()

class RulingTests(unittest.TestCase):
 def test_text_exact_nfc_whitespace(self):self.assertEqual(TextExposure(['ά  β']).hit('α\u0301\tβ'),'exact')
 def test_text_shared_30(self):self.assertEqual(TextExposure(['x'+'a'*30+'y']).hit('z'+'a'*30+'q'),'substring30')
 def test_text_29_nonhit(self):self.assertIsNone(TextExposure(['x'+'a'*30+'y']).hit('z'+'a'*29+'q'))
 def test_text_short_exact(self):self.assertEqual(TextExposure(['abc']).hit('abc'),'exact')
 def test_text_source_ledger(self):
  r=dict(key=['p','a'],crop_sha256='h',split='train',label='exact',text_source='doc')
  kept,ledger=exposure_filter([r,dict(r,label='safe',text_source='other')],dict(keys=set(),crops=set()),TextExposure(['exact']))
  self.assertEqual(len(kept),1);self.assertEqual(ledger['doc']['dropped'],1)
 def test_dominant_argmax(self):self.assertEqual(dominant_script(dict(final_inventory=dict(greek_letters=2,latin_letters=1,cyrillic_letters=3))),'cyrillic')
 def test_dominant_tie(self):self.assertEqual(dominant_script(dict(final_inventory=dict(greek_letters=3,cyrillic_letters=3))),'none')
 def test_dominant_no_letters(self):self.assertEqual(dominant_script(dict(final_inventory=dict(greek_letters=0,latin_letters=0,cyrillic_letters=0))),'none')
 def test_dominant_absent(self):self.assertEqual(dominant_script({}),'none')
 def test_nine_wave_join(self):
  imports=[dict(id=k,wave=k) for k in IMPORT_COUNTS]
  ref=[dict(key=['collection-v2-train',k]) for k in IMPORT_COUNTS]+[dict(key=[p,'x']) for p in ('collect-v3-W1-20261018-0524','collect-v3-W2-20261018-0524')]
  _,n=wave_join(ref,imports);self.assertEqual(set(n),{'W1','W2',*IMPORT_COUNTS});self.assertEqual(sum(n.values()),9)
 def test_wave_missing_id_fails(self):
  with self.assertRaises(KeyError):wave_join([dict(key=['collection-v2-train','missing'])],[])
 def test_export_round_trip(self):
  import tempfile,io
  import pyarrow as pa,pyarrow.parquet as pq
  from PIL import Image
  from export import read_export
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'real/train').mkdir(parents=True);dump(out/'real/build_info.json',dict(kind='real'))
   codec=json.loads((Path(__file__).parent/'wave2/codec/v2.1.json').read_text());ident=next(a['id'] for a in codec['atoms'] if a['ch']=='α')
   png=io.BytesIO();Image.new('L',(64,48),255).save(png,format='PNG')
   pq.write_table(pa.Table.from_pylist([dict(line_id='real-id',label_ids=[ident],gt_nfd='α',image_png=png.getvalue(),width=64,codec_version='v2.1',split='train')]),out/'real/train/shard-00000.parquet')
   shard='train/shard-00000.parquet'
   dump(out/'real/build_info.json',dict(kind='real',partition_id='fixture',codec_version='v2.1',shard_sha256={shard:sha(out/'real'/shard)}))
   ref=[dict(line_id='real-id',key=['parent','real-id'],final_text='α')]
   r=read_export(out,ref,wave2=Path(__file__).parent/'wave2');self.assertTrue(r['round_trip']);self.assertEqual(r['rows'],1)
 def test_wave2_rejects_bound_v1(self):
  import tempfile,pyarrow as pa,pyarrow.parquet as pq
  from export import module
  reader=module(Path(__file__).parent/'wave2/train/mix.py','mix1_test_reader')
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'train').mkdir();dump(p/'build_info.json',dict(kind='real'));pq.write_table(pa.Table.from_pylist([dict(codec_version='v1',split='train')]),p/'train/shard-00000.parquet')
   with self.assertRaisesRegex(ValueError,'codec mismatch'):reader.load_rows(dict(codec_version='v2.1',components=[dict(kind='real',shard_dir=str(p),fraction=1)]),'train')

class AdditionalEvidenceTests(unittest.TestCase):
 def test_original_crop_exposure(self):
  r=dict(key=['p','id'],split='train',label='safe',text_source='doc',crop_sha256='encoded',original_crop_sha256='original')
  kept,ledger=exposure_filter([r],dict(keys=set(),crops={'original'}),TextExposure(['heldout']))
  self.assertEqual(kept,[]);self.assertEqual(ledger['doc']['crop'],1)
 def test_qualified_nine_plans(self):
  import tempfile
  from generate import all_arms
  def pool(prefix,n):
   return [dict(line_id=f'{prefix}{i}',source_doc_id=prefix,key=[prefix,str(i)],edition_id=prefix,crop_sha256=f'{prefix}{i}',split='train',script_class='g',width=128,dominant_script='cyrillic' if i%10==0 else 'greek',wave='round1' if i%10==0 else 'parliament' if i%3==0 else 'W1') for i in range(n)]
  with tempfile.TemporaryDirectory() as tmp:
   plans=all_arms(tmp,[pool('r',31),pool('s',17),pool('b',9)],dict(editions=set(),keys=set(),crops=set()),True,d=100)
   self.assertEqual(len(plans),9)
   for name in ('M3_capped','M3_uncapped','M4_alpha1','M4_alpha0.5'):self.assertIn(name,plans)

class Mix1CTests(unittest.TestCase):
 def test_sbatch_directives(self):
  from run import sbatch_directives
  import tempfile
  sbatch_directives(Path(__file__).parent)
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'x.sbatch'
   for missing in ('account','partition','time'):
    p.write_text('\n'.join('#SBATCH --'+k+'='+v for k,v in dict(account='a0140',partition='normal',time='01:00:00').items() if k!=missing))
    with self.assertRaisesRegex(ValueError,'missing '+missing):sbatch_directives(tmp)
 def test_index_byte_tamper(self):
  import tempfile
  from index_contract import write_index,wave1c_check
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);pool=[[dict(line_id='α',physical_index=7)]]
   write_index(p/'v_c_indices.jsonl.gz',[[(0,0,'α')]],pool)
   write_index(p/'bad.gz',[[(0,0,'α')],[(0,0,'α')]],pool)
   self.assertEqual(list(rows(p/'v_c_indices.jsonl.gz')),[[1,0,0,7,'α']])
   with self.assertRaisesRegex(ValueError,'indexed v_c draw bytes differ'):wave1c_check(tmp,p/'bad.gz')
 def test_clone_build_derivation(self):
  import tempfile,subprocess,sys,os
  import pyarrow as pa,pyarrow.parquet as pq
  binding=json.loads((Path(__file__).parent/'WAVE2_BINDING.json').read_text())
  upstream=Path(binding['worktree'])
  if not upstream.exists():upstream=Path(binding['deployed'])
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);source=p/'source';(source/'train').mkdir(parents=True)
   before=pa.Table.from_pylist([dict(line_id='original',codec_version='v1',label_ids=[1,2],image_png=b'pixels',split='train')])
   pq.write_table(before,source/'train/shard-00000.parquet');dump(source/'build_info.json',dict(codec_version='v1'))
   codec=upstream/'codec/v2.1.json'
   code="import sys;sys.path.insert(0,sys.argv[1]);from bench.e4_codec_release import clone_build;clone_build(sys.argv[2],sys.argv[3],codec_path=sys.argv[4])"
   subprocess.run([sys.executable,'-B','-c',code,str(upstream),str(source),str(p/'clone'),str(codec)],check=True)
   info=json.loads((p/'clone/build_info.json').read_text());d=info['encoding_derivation']
   self.assertEqual(d['source_receipt_sha256'],sha(source/'build_info.json'));self.assertEqual(d['codec_sha256'],sha(codec))
   self.assertTrue(d['source_columns_equal'] and d['readback_equal'])
   after=pq.read_table(p/'clone/train/shard-00000.parquet')
   self.assertTrue(before.drop(['codec_version']).equals(after.drop(['codec_version'])))
   self.assertEqual(after['codec_version'].to_pylist(),['v2.1'])
 def test_crosscheck_pending(self):
  from crosscheck import crosscheck
  self.assertEqual(crosscheck()['status'],'pending')
 def test_crosscheck_contract(self):
  from crosscheck import crosscheck
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   a=Path(tmp)/'a.json';b=Path(tmp)/'b.json'
   info=dict(encoding_derivation=dict(source_receipt_sha256='source',codec_sha256='codec'),shard_sha256={})
   dump(a,info);dump(b,info);self.assertEqual(crosscheck(b,a)['status'],'ok')
   info['encoding_derivation']['codec_sha256']='wrong';dump(b,info)
   self.assertEqual(crosscheck(b,a)['status'],'failed')


class CustodyTests(unittest.TestCase):
 def fixture(self,root,text='α',compression='snappy'):
  import pyarrow as pa,pyarrow.parquet as pq
  root=Path(root);(root/'train').mkdir(parents=True)
  path=root/'train/shard-00000.parquet'
  pq.write_table(pa.Table.from_pylist([dict(line_id='id',gt_nfd=text,gt_nfc=text,label_ids=[1],codec_version='v2.1',image_png=b'pixels')]),path,compression=compression)
  dump(root/'build_info.json',dict(encoding_derivation=dict(source_receipt_sha256='source',codec_sha256='codec'),shard_sha256={'train/'+path.name:sha(path)}))
  return root/'build_info.json'
 def test_pre_export_contract(self):
  import tempfile
  from unittest.mock import patch
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);source=p/'source.json';codec=p/'codec.json';other=p/'control.json'
   dump(source,{'codec_version':'v2'});dump(codec,{'version':'v2.1'})
   dump(other,dict(encoding_derivation=dict(source_receipt_sha256=sha(source),codec_sha256=sha(codec))))
   with patch('custody.A12_SHA',sha(source)),patch('custody.CODEC_SHA',sha(codec)):
    result=crosscheck(other,source=source,codec=codec)
    self.assertEqual(result['status'],'ok');self.assertEqual(result['phase'],'pre-export');self.assertIn('CROSSCHECK_A12_CONTRACT_OK',result['line'])
    dump(other,dict(encoding_derivation=dict(source_receipt_sha256='v1',codec_sha256=sha(codec))))
    self.assertEqual(crosscheck(other,source=source,codec=codec)['status'],'failed')
 def test_missing_derivative_fails(self):
  import tempfile
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   other=self.fixture(Path(tmp)/'control')
   with self.assertRaisesRegex(ValueError,'own derivative unavailable'):crosscheck(other,Path(tmp)/'missing')
 def test_post_export_equal_bytes(self):
  import tempfile
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=self.fixture(Path(tmp)/'b')
   result=crosscheck(b,a);self.assertEqual(result['status'],'ok');self.assertTrue(result['shard_inventory_equal'])
 def test_post_export_different_bytes_equal_columns(self):
  import tempfile
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=self.fixture(Path(tmp)/'b',compression='zstd')
   result=crosscheck(b,a);self.assertEqual(result['status'],'ok');self.assertFalse(result['shard_inventory_equal']);self.assertTrue(result['column_equality']['columns']['train']['label_ids'])
 def test_post_export_column_mismatch_fails(self):
  import tempfile
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=self.fixture(Path(tmp)/'b',text='β')
   with self.assertRaisesRegex(ValueError,'column equality failed'):crosscheck(b,a)
 def test_post_export_corrupt_shard_fails(self):
  import tempfile
  from crosscheck import crosscheck
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=self.fixture(Path(tmp)/'b')
   (b.parent/'train/shard-00000.parquet').write_bytes(b'corrupt')
   with self.assertRaisesRegex(ValueError,'inventory SHA'):crosscheck(b,a)
 def test_gt_comparison_ignores_codec_and_preserves_order(self):
  import tempfile
  from custody import compare_columns,GT_COLUMNS
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=self.fixture(Path(tmp)/'b',text='β')
   with self.assertRaisesRegex(ValueError,'column equality failed'):compare_columns(a.parent,b.parent,GT_COLUMNS)
 def test_gt_comparison_row_count_fails(self):
  import tempfile
  from custody import compare_columns,GT_COLUMNS
  with tempfile.TemporaryDirectory() as tmp:
   a=self.fixture(Path(tmp)/'a');b=Path(tmp)/'empty';b.mkdir()
   with self.assertRaisesRegex(ValueError,'row count differs'):compare_columns(a.parent,b,GT_COLUMNS)
