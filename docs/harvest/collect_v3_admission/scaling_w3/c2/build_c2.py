"""C2 derivative builder. No scheduler, network, codec extension or image generation."""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, inspect, json, os, shutil, sys, time, unicodedata
from collections import Counter
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
HERE=Path(__file__).resolve().parent
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
SOURCE=W/'scaling_w3/mix1_runs/MIX1D-8d25940f-export-001'
LOADER=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f'
POOLS=('shared/real','prep/E1','prep/A12')
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj):Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
def codec_map(path):
 obj=read(path)
 if obj['version']!='v2.1':raise ValueError('requires codec v2.1')
 return {a['ch']:a['id'] for a in obj['atoms']}
def project(label, codec):
 """NFD -> remove Mn -> str.lower -> codec Unicode L* + ASCII space.

 Missing letters fail closed before filtering; nonletters other than space drop.
 str.lower is the lead choice: final sigma remains final sigma.
 """
 text=''.join(c for c in unicodedata.normalize('NFD',label) if unicodedata.category(c)!='Mn').lower()
 missing=sorted({c for c in text if unicodedata.category(c).startswith('L') and c not in codec})
 if missing:raise ValueError('projected letter outside codec v2.1: '+repr(missing))
 kept=''.join(c for c in text if c==' ' or (unicodedata.category(c).startswith('L') and c in codec))
 return ' '.join(filter(None,kept.split(' ')))
def projection_sha():return hashlib.sha256(inspect.getsource(project).encode()).hexdigest()
def augment(before,codec):
 if {'base_label','base_label_ids'} & set(before.column_names):raise ValueError('already has C2 columns')
 labels=[project(x,codec) for x in before['gt_nfd'].to_pylist()]
 after=before.append_column('base_label',pa.array(labels,type=pa.string())).append_column('base_label_ids',pa.array([[codec[c] for c in s] for s in labels],type=pa.list_(pa.field('element',pa.uint32()))))
 assert_original(before,after)
 return after
def assert_original(before,after):
 if after.column_names!=before.column_names+['base_label','base_label_ids'] or not before.equals(after.select(before.column_names),check_metadata=True):raise ValueError('original columns changed')
 # Same physical order proves line_id/pool_index invariance, including implicit indices.
 if not before['line_id'].equals(after['line_id']):raise ValueError('line_id order changed')
 if 'pool_index' in before.column_names and not before['pool_index'].equals(after['pool_index']):raise ValueError('pool_index changed')
def inventory(root):return {str(p.relative_to(root)):sha(p) for p in sorted(Path(root).rglob('shard-*.parquet'))}
def loader_module(root):
 spec=importlib.util.spec_from_file_location('c2_wave2_mix',Path(root)/'train/mix.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def clone_pool(source,target,codec_path):
 source,target=Path(source),Path(target)
 if target.exists():raise FileExistsError(target)
 info=read(source/'build_info.json');expected=info['shard_sha256']
 if inventory(source)!=expected:raise ValueError('source inventory changed: '+str(source))
 codec=codec_map(codec_path);target.mkdir(parents=True);counts=Counter();alphabet=set();empty=0
 for name in sorted(expected):
  before=pq.read_table(source/name);after=augment(before,codec);p=target/name;p.parent.mkdir(parents=True,exist_ok=True);pq.write_table(after,p,compression='zstd',use_compliant_nested_type=False)
  actual=pq.read_table(p);assert_original(before,actual)
  if not after.equals(actual,check_metadata=True):raise ValueError('derivative readback differs')
  counts[name.split('/')[0]]+=len(before)
  for s in actual['base_label'].to_pylist():alphabet.update(s.replace(' ',''));empty+=not s
 for name in ('word_tags.jsonl','audit_report.json','select_report.json'):
  if (source/name).is_file():shutil.copyfile(source/name,target/name)
 info['shard_sha256']=inventory(target)
 info['encoding_derivation']=dict(policy='C2 adds base_label and base_label_ids only; 0 new images',source=str(source),source_receipt_sha256=sha(source/'build_info.json'),source_shards=expected,source_shard_inventory_sha256=digest(expected),codec_sha256=sha(codec_path),projection_source_sha256=projection_sha(),builder_sha256=sha(__file__),source_columns_equal=True,readback_equal=True,line_id_order_equal=True,pool_index_equal=True,counts=dict(counts),alphabet=sorted(alphabet),empty=empty)
 dump(target/'build_info.json',info)
 return info['encoding_derivation']
def rewrite(obj,old,new):
 if isinstance(obj,str):return obj.replace(str(old),str(new))
 if isinstance(obj,list):return [rewrite(x,old,new) for x in obj]
 if isinstance(obj,dict):return {k:rewrite(v,old,new) for k,v in obj.items()}
 return obj
def build(output,loader=LOADER):
 verify_inputs(loader);output=Path(output)
 identity=read(HERE/'IDENTITY.json')['sha8']
 if output!=W/f'scaling_w3/mix1_runs/C2-{identity}-001':raise ValueError('output must be exact new C2 attempt')
 output.mkdir(parents=True,exist_ok=False);codec=Path(loader)/'codec/v2.1.json';m=loader_module(loader)
 deriv={p:clone_pool(SOURCE/p,output/p,codec) for p in POOLS}
 manifests={}
 for path in sorted(SOURCE.glob('*/mix.json')):
  obj=rewrite(read(path),SOURCE,output)
  for c in obj['components']:
   root=Path(c.get('build_dir',c.get('shard_dir')))
   if root not in [output/p for p in POOLS]:raise ValueError('unexpected arm pool')
   if c['kind']=='real':c['shard_sha256']=inventory(root)
  dest=output/path.relative_to(SOURCE);dest.parent.mkdir(parents=True,exist_ok=True);dump(dest,obj)
  resolved=m.validate(dest,repo=loader)
  # Full load_rows check of every referenced pool, once, instead of retaining all arms.
  manifests[str(path.relative_to(SOURCE))]=dict(source_sha256=sha(path),derivative_sha256=sha(dest),validate_ok=True)
  idx=path.with_name('INDEX.json')
  if idx.exists():
   shutil.copyfile(idx,dest.with_name('INDEX.source.json'))
   index=rewrite(read(idx),SOURCE,output)
   index['mix']=dict(path=str(dest),sha256=sha(dest))
   for pool in index['pools']:
    pool['build_info_sha256']=sha(Path(pool['path'])/'build_info.json')
   if index['index']!=read(idx)['index']:raise ValueError('draw index changed')
   dump(dest.with_name('INDEX.json'),index)
   dump(dest.with_name('C2_INDEX_BINDING.json'),dict(index_sha256=sha(idx),source=str(idx),derivative_index_sha256=sha(dest.with_name('INDEX.json')),line_id_order_equal=True,pool_index_equal=True))
 for pool in POOLS:
  info=read(output/pool/'build_info.json');kind='synthetic' if pool=='prep/A12' else 'real'
  c=dict(kind=kind,fraction=1.0)
  if kind=='synthetic':c.update(build_dir=str(output/pool),recipe_sha256=info['recipe_sha256'])
  else:c.update(shard_dir=str(output/pool),shard_sha256=info['shard_sha256'],partition_id=info['partition_id'],source=pool)
  for split in info.get('written',{'train':1}):
   rows=m.load_rows(dict(components=[c],codec_version='v2.1'),split)[0]
   if len(rows)!=info['written'][split]:raise ValueError('loader row count mismatch')
   del rows
 dump(output/'C2_RECEIPT.json',dict(status='ok',derivatives=deriv,manifests=manifests,export_receipt_sha256=sha(SOURCE/'EXPORT_RECEIPT.json'),codec_sha256=sha(codec),projection_source_sha256=projection_sha(),no_new_images=True))
def verify_inputs(loader=LOADER):
 b=read(HERE/'INPUTS.json')
 for name,spec in b.items():
  if sha(spec['path'])!=spec['sha256']:raise ValueError('changed input '+name)
 if sha(Path(loader)/'train/mix.py')!=b['loader']['sha256']:raise ValueError('loader changed')
def verify_package():
 expected=read(HERE/'PACKAGE.json')
 for name,d in expected.items():
  if sha(HERE/name)!=d:raise ValueError('changed package file '+name)
 actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='PACKAGE.json'}
 if actual!=set(expected):raise ValueError('package file set changed')
 print('VERIFY package ok',len(expected))
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','package','inputs']);p.add_argument('--output');a=p.parse_args()
 if a.action=='build':verify_package();build(a.output)
 elif a.action=='package':verify_package()
 else:verify_inputs();print('VERIFY inputs ok')
if __name__=='__main__':main()
