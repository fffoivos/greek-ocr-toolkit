#!/usr/bin/env python3
"""Fail-closed package/input verification and coordinator CPU entry point."""
from core import *
import argparse,sys,unittest
HERE=Path(__file__).resolve().parent

def sbatch_directives(root):
    import re
    files=list(Path(root).rglob('*.sbatch'));require(files,'no sbatch files')
    for file in files:
        text=file.read_text()
        for key in ('account','partition','time'):
            match=re.search(r'^#SBATCH\s+--'+key+r'(?:=|\s+)(\S+)',text,re.M)
            require(match is not None,'sbatch missing '+key+': '+str(file))
            if key=='account':require(match[1]=='a0140','sbatch account must be a0140')

def package():
    sbatch_directives(HERE)
    manifest=json.loads((HERE/'PACKAGE.json').read_text())
    for name,digest in manifest['files'].items():
        p=Path(name);require(not p.is_absolute() and '..' not in p.parts,'unsafe package path')
        require(sha(HERE/p)==digest,'package SHA '+name)
    sample=json.loads((HERE/'REAL_SAMPLE_RECEIPT.json').read_text())
    require(sample['schema']=='mix1-real-sample-v1','sample schema')
    require(sample['code_sha256']==sha(HERE/'core.py'),'sample used different core')
    for name,digest in sample['mix1b_code'].items():require(sha(HERE/'reference/mix1b'/name)==digest,'historical sample code changed '+name)
    # Current MIX1C code is independently bound by tests and final round trip.
    require(set(sample['inputs'])==set(json.loads((HERE/'INPUTS.json').read_text())),'bound input coverage set mismatch')
    require(sample['inputs'] and all(x['covered'] for x in sample['inputs'].values()),'real sample coverage missing')
    require(sample['covered']==len(sample['inputs']),'coverage ledger mismatch')
    for name,x in sample['inputs'].items():
        expected=json.loads((HERE/'INPUTS.json').read_text())[name]
        require(x['sha256']==expected['sha256'] and x['path']==expected['path'],'sample binding '+name)
    for parent in ('collect-v3-W1-20261018-0524','collect-v3-W2-20261018-0524','collection-v2-train'):
        p=sample['parents'][parent];require(p['rows']>=1000 and len(p['crops'])>=20,'real sample parent '+parent)
    for family in ('E1','synthetic_v5'):
        require(sample[family]['rows']>=1000 and sample[family]['images_rehashed']>=20,'real sample family '+family)
        for name,x in sample['inputs'].items():
            if name.startswith(family+'/shard-'):require(x['rows']>=20 and len(x['crops'])>=20,'real shard coverage '+name)
    require(sample['inputs']['tags_receipt']['sha256']=='e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39','tag receipt binding')
    tests=json.loads((HERE/'TEST_RECEIPT.json').read_text())
    require(tests['passed']>=24 and tests['failed']==0,'test receipt')
    for name,digest in tests['code'].items():require(sha(HERE/name)==digest,'tested code changed '+name)
    require(sample['covered']==sample['required']==70,'70/70 required')
    require(sample['ref_364871']['rows']>=1000,'ref sample missing')
    require(sample['export_sample']['attempted_rows']==1000 and sample['export_sample']['loader_reader_ok'] and sample['export_sample']['temporary_directory_removed'],'real export sample missing')
    roundtrip=json.loads((HERE/'ROUNDTRIP_RECEIPT.json').read_text())
    require(roundtrip['loader_root'].endswith('/27a49e51fa735e8f'),'final loader round trip required')
    require(roundtrip['rows']==roundtrip['attempted_rows']==1000 and roundtrip['round_trip'] and roundtrip['full_validate_ok'],'final real round trip failed')
    require(len(roundtrip['parents'])==3 and all(n>0 for n in roundtrip['parents'].values()),'three-parent round trip')
    require(roundtrip['binding']['loader_sha256']==sha(HERE/'wave2/train/mix.py'),'round trip loader changed')
    require(roundtrip['evidence_retained'] and roundtrip['contents_sha256'],'retained round trip evidence required')
    target=json.loads((HERE/'DEPLOY_TARGET.json').read_text())['root']
    require(roundtrip['evidence_directory']==str(Path(target).parents[1]/'mix1_scratch/roundtrip_e87b9e8d'),'retained MIX1C round trip evidence path')
    binding=json.loads((HERE/'WAVE2_BINDING.json').read_text())
    require(binding['local_deployed_equal'] and binding['manifest_sha256']=='27a49e51fa735e8f064fa68a2da2c5fda7dcefa0e54eecd0b3bc41664b1f1457','final loader binding')
    require(roundtrip['binding']['factory_sha256']==binding['factory_sha256'] and roundtrip['binding']['codec_sha256']==binding['files']['codec/v2.1.json'],'round trip factory/codec binding')
    for name,digest in roundtrip['mix1c_code'].items():
        historical=HERE/'reference/mix1c'/name if name in ('export.py','pipeline.py') else HERE/name
        require(sha(historical)==digest,'historical round trip code changed '+name)
    import ast
    for filename,functions in [('export.py',('module','export_real','read_export')),('pipeline.py',('load_real',))]:
        def bodies(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
        before=bodies(HERE/'reference/mix1c'/filename);after=bodies(HERE/filename)
        require(all(before[n]==after[n] for n in functions),'real pool code changed '+filename)
    chain=json.loads((HERE/'CHAIN_GT_SAMPLE.json').read_text())
    require(chain['status']=='ok' and chain['sample_rows']>=1000 and chain['sample_shards']>=20,'MIX1D chain sample')
    audit=json.loads((HERE/'TEXT_AUDIT.json').read_text())['families']['synthetic_v5']
    from custody import A12_SHA
    require(audit['dropped']==287 and audit['build_info']['sha256']==A12_SHA,'MIX1D text audit')
    for name,digest in sample['mix1d_sample_code'].items():require(sha(HERE/name)==digest,'MIX1D sample code changed '+name)
    print('VERIFY package ok',sample['covered'],'/',sample['required'],'inputs')

def inputs(receipt,digest,full=False):
    sample=json.loads((HERE/'REAL_SAMPLE_RECEIPT.json').read_text())
    for name,x in sample['inputs'].items():
        p=Path(x['path']);require(p.is_file(),'missing input '+name)
        if not x.get('hash_deferred_to_job') or full:require(sha(p)==x['sha256'],'input SHA '+name)
    rt=json.loads((HERE/'ROUNDTRIP_RECEIPT.json').read_text())
    for name,evidence_digest in rt['contents_sha256'].items():require(sha(Path(rt['evidence_directory'])/name)==evidence_digest,'round trip evidence SHA '+name)
    aux=json.loads((HERE/'AUX_INPUTS.json').read_text())
    for name,x in aux.items():require(sha(x['path'])==x['sha256'],'aux input SHA '+name)
    if not receipt or not digest:
        print('pending: required --subset-receipt PATH --subset-sha SHA256 (SCALE1 3705111 / scale1-c05-003)');return None
    require(digest=='467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2' and sha(receipt)==digest,'subset receipt SHA')
    obj=json.loads(Path(receipt).read_text());require(obj['status']=='ok','subset receipt status')
    require(obj['tags_receipt']['sha256']==sample['inputs']['tags_receipt']['sha256'],'subset tag receipt')
    entry=obj['subsets']['ref_364871'];require(entry['rows']==364871,'ref row count')
    require(sha(entry['output']['path'])==entry['output']['sha256'],'ref SHA')
    require(all(entry['audit'].get(k)==0 for k in ('dev_test_editions','benchmark_keys','benchmark_crop_hashes','v2_dev_test_docs')),'subset exposure audit')
    return obj

def build(a):
    require(a.subset_receipt and a.subset_sha,'pending: subset receipt path + SHA required')
    inputs(a.subset_receipt,a.subset_sha,full=True)
    sample=json.loads((HERE/'REAL_SAMPLE_RECEIPT.json').read_text())
    from pipeline import load_real,load_candidates
    from generate import all_arms
    real,record=load_real(a.subset_receipt,a.subset_sha,widths=True)
    candidates,blocked,audit_record=load_candidates()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    from custody import A12_SOURCE,E1_SOURCE
    sources={n:dict(path=str(r),build_info_sha256=sha(r/'build_info.json')) for n,r in [('A12',A12_SOURCE),('E1',E1_SOURCE)]}
    all_arms(out,[real,*candidates],blocked,record['M3_ok'],bound_sources=sources)
    dump(out/'QUALIFICATION.json',dict(record=record,text_audit=audit_record))


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['package','inputs','build','export','crosscheck-a12'])
    p.add_argument('crosscheck_path',nargs='?');p.add_argument('--own-build-info')
    p.add_argument('--subset-receipt');p.add_argument('--subset-sha');p.add_argument('--output');p.add_argument('--manifests');p.add_argument('--full',action='store_true');a=p.parse_args()
    if a.command=='crosscheck-a12':
        from crosscheck import crosscheck
        result=crosscheck(a.crosscheck_path,a.own_build_info);print(json.dumps(result,sort_keys=True))
        if result['status']=='ok':print(result['line'])
        return 0 if result['status']=='ok' else 1
    elif a.command=='package':package()
    elif a.command=='inputs':
        if inputs(a.subset_receipt,a.subset_sha,a.full) is None:return 3
        print('VERIFY inputs ok')
    elif a.command=='build':build(a)
    else:
        from export import production
        production(a)
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as e:print('MIX1 FAIL:',str(e),file=sys.stderr);sys.exit(1)
