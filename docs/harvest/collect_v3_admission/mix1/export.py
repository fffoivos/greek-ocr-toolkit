"""Canonical factory import and unchanged wave-2 shard reader.
One shared real pool plus append-compatible derivatives; no redraws or filters.
"""
from core import *
import subprocess,sys,importlib.util,unicodedata,os
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
WAVE2=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f'
FACTORY=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f/factory/target/release/linefactory'
FACTORY_SHA='bdd52e588dd92a1ec15560062fae16bc3bcdc1cae2a9bd1da2d5525932441773'

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def export_real(ref,out,*,wave2=WAVE2,factory=FACTORY,diagnostic=False):
    """One canonical re-encoding, shared by all arms. Never filters a failed row."""
    import pyarrow.parquet as pq
    require(sha(factory)==FACTORY_SHA,'factory binary binding')
    codec=Path(wave2)/'codec/v2.1.json';out=Path(out);out.mkdir(parents=True,exist_ok=False)
    # Reuse wave-2's exact label/codec/class adapter, including nonletter -> furniture.
    sys.path.insert(0,str(wave2))
    from bench.e4_wave2 import encode_admissions
    adapted,rejected=encode_admissions([dict(r,label=r['final_text'],row_id=r['line_id']) for r in ref])
    require(not rejected,'EXPORT stopped: wave-2 rejected census labels; no extra filters authorized')
    adapted={r['line_id']:r for r in adapted}
    ids=set();feed=out/'records.jsonl';raw_bytes=0
    with open(feed,'wb') as f:
        for r in ref:
            require(r['line_id'] not in ids,'nonunique line_id across parents');ids.add(r['line_id'])
            require(sha(r['crop_path'])==r['crop_sha256'],'export original crop SHA')
            raw_bytes+=Path(r['crop_path']).stat().st_size
            f.write(encode(dict(id=r['line_id'],text=adapted[r['line_id']]['text'],crop_path=str(Path(r['crop_path']).relative_to(W)),doc=r['edition_id'],split='train',source_dataset=r['source'],script_class=adapted[r['line_id']]['script_class'],admitted=True)))
    pool=out/'real'
    subprocess.run([str(factory),'import-real','--records',str(feed),'--crops',str(W),'--partition','mix1b-ref364871-v1','--codec-json',str(codec),'--out',str(pool)],check=True,stdout=sys.stderr,stderr=sys.stderr)
    info=json.loads((pool/'build_info.json').read_text())
    require(diagnostic or not info.get('drop_ledger'),'EXPORT stopped: factory dropped rows; no extra filters authorized')
    return read_export(out,ref,wave2=wave2,raw_bytes=raw_bytes,factory=factory,drops=info.get('drop_ledger',[]))

def read_export(out,ref,*,wave2,raw_bytes=0,factory=None,drops=None):
    out=Path(out);pool=out/'real';codec=Path(wave2)/'codec/v2.1.json'
    ids={r['line_id'] for r in ref}
    if (Path(wave2)/'DEPLOY_RECEIPT.json').is_file():os.environ['E4_ROOT']=str(Path(wave2).resolve())
    mix_reader=module(Path(wave2)/'train/mix.py','mix1_wave2_reader')
    spec=dict(components=[dict(kind='real',shard_dir=str(pool),fraction=1)],codec_version='v2.1')
    info=json.loads((pool/'build_info.json').read_text())
    spec.update(seed=SEED,created_by='MIX1C',notes='Canonical factory real round trip')
    spec['components'][0].update(shard_sha256=mix_reader.shard_inventory(pool),partition_id=info['partition_id'],source='ref_364871')
    manifest=out/'real_mix.json';dump(manifest,spec)
    validated=mix_reader.validate(manifest,repo=wave2)
    loaded=mix_reader.load_rows(validated,'train')[0]
    missing={r['line_id'] for r in drops or []}
    require(len(loaded)+len(missing)==len(ref) and {r['line_id'] for r in loaded}==ids-missing,'export membership mismatch')
    cer=module(Path(wave2)/'train/cer.py','mix1_wave2_cer');decoder=cer.load_codec(str(codec))
    by_id={r['line_id']:r for r in ref};literal=0;nfd=0
    for r in loaded:
        expected=by_id[r['line_id']]['final_text'];decoded=decoder.decode(r['label_ids'])
        require(decoded==r['gt_nfd'],'decoded factory label mismatch')
        literal+=decoded!=expected;nfd+=unicodedata.normalize('NFD',decoded)!=unicodedata.normalize('NFD',expected)
        from PIL import Image
        import io
        with Image.open(io.BytesIO(r['image_png'])) as im:require(im.height==48 and im.width==r['width'],'PNG contract')
    require(nfd==0,'factory decoded label differs from census NFD')
    binding=dict(codec_version='v2.1',codec_sha256=sha(codec),factory_sha256=sha(factory) if factory else None,loader_sha256=sha(Path(wave2)/'train/mix.py'),shard_sha256=mix_reader.shard_inventory(pool))
    dump(out/'CODEC_BINDING.json',binding)
    # Canonical factory order may differ from ref order: always bind the explicit map.
    physical={r['line_id']:i for i,r in enumerate(loaded)}
    dump(out/'REF_PHYSICAL_INDEX.json',[[r['key'],physical[r['line_id']],r['line_id']] for r in ref if r['line_id'] in physical])
    return dict(rows=len(loaded),attempted_rows=len(ref),loader_reader_ok=True,drop_ledger=drops or [],full_membership_preserved=not bool(drops),parents=dict(Counter(r['key'][0] for r in ref)),round_trip=not bool(drops),binding=binding,source_bytes=raw_bytes,census_final_text_differs_factory=literal,census_final_text_differs_factory_nfd=nfd,physical_map_sha256=sha(out/'REF_PHYSICAL_INDEX.json'),full_validate_ok=True,loader_root=str(wave2),status='ok')

def prepare_derivatives(prep,*,wave2=WAVE2):
    """Call the bound, unchanged append-only adapter once per original source."""
    sys.path.insert(0,str(wave2))
    from bench.e4_codec_release import clone_build
    result={}
    for name,kind in [('E1','real'),('A12','synthetic')]:
        from custody import A12_SOURCE, E1_SOURCE, chain_equal
        source=A12_SOURCE if name=='A12' else E1_SOURCE;target=Path(prep)/name
        chain=chain_equal(full=True) if name=='A12' else None
        before=sha(source/'build_info.json')
        clone_build(source,target,codec_path=Path(wave2)/'codec/v2.1.json')
        info=json.loads((target/'build_info.json').read_text());derivation=info['encoding_derivation']
        require(sha(source/'build_info.json')==before==derivation['source_receipt_sha256'],'source changed')
        require(derivation['codec_sha256']==sha(Path(wave2)/'codec/v2.1.json'),'codec derivation')
        require(derivation['source_columns_equal'] and derivation['readback_equal'],'clone column custody')
        result[name]=dict(path=str(target),build_info_sha256=sha(target/'build_info.json'),encoding_derivation=derivation,provenance_chain=chain)
    dump(Path(prep)/'DERIVATIVES_RECEIPT.json',result)
    return result


def production(a):
    from run import inputs,package
    from pipeline import load_real
    package();inputs(a.subset_receipt,a.subset_sha,full=True)
    manifests=Path(a.manifests);mr=json.loads((manifests/'MANIFESTS_RECEIPT.json').read_text())
    require(sha(mr['pools']['path'])==mr['pools']['sha256'],'pool receipt')
    for entry in mr['plans'].values():require(sha(entry['path'])==entry['sha256'],'plan receipt')
    from custody import A12_SOURCE,E1_SOURCE
    for name,source in [('A12',A12_SOURCE),('E1',E1_SOURCE)]:
        require(mr['bound_sources'][name]==dict(path=str(source),build_info_sha256=sha(source/'build_info.json')),'manifest source binding '+name)
    ref,_=load_real(a.subset_receipt,a.subset_sha)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    result=export_real(ref,out/'shared')
    require(result['rows']==364871 and result['round_trip'] and result['full_validate_ok'],'shared real membership')
    physical=json.loads((out/'shared/REF_PHYSICAL_INDEX.json').read_text())
    require(all(i==r[1] and ref[i]['line_id']==r[2] for i,r in enumerate(physical)),'factory pool order differs: refusing to rewrite final draw')
    derivatives=prepare_derivatives(out/'prep')
    roots=[out/'shared/real',Path(derivatives['A12']['path']),Path(derivatives['E1']['path'])]
    reader=module(WAVE2/'train/mix.py','mix1_export_full_reader')
    # Check each final index against the shared physical pool identities, streaming.
    import pyarrow.parquet as pq
    ids=[]
    for root in roots:
        ids.append([x for shard in sorted((root/'train').glob('shard-*.parquet')) for x in pq.read_table(shard,columns=['line_id']).column('line_id').to_pylist()])
    for name,entry in mr['plans'].items():
        plan=json.loads(Path(entry['path']).read_text());index=Path(entry['path']).parent/plan['index']['path']
        require(sha(index)==plan['index']['sha256'],'index SHA')
        counts=Counter()
        for epoch,position,c,i,ident in rows(index):
            require(ids[c][i]==ident and position==counts[epoch],'physical index identity/order');counts[epoch]+=1
        require(dict(counts)=={e:D for e in range(1,9)},'index epoch budget')
        folder=out/name;folder.mkdir()
        components=[]
        for c,fraction in enumerate(plan['fractions']):
            root=roots[c];info=json.loads((root/'build_info.json').read_text())
            if c==1:component=dict(kind='synthetic',build_dir=str(root),recipe_sha256=info['recipe_sha256'],fraction=fraction)
            else:component=dict(kind='real',shard_dir=str(root),shard_sha256=info['shard_sha256'],partition_id=info['partition_id'],source='ref_364871' if c==0 else 'E1',fraction=fraction)
            components.append(component)
        mix=folder/'mix.json';dump(mix,dict(components=components,seed=SEED,codec_version='v2.1',created_by='MIX1C',notes='S1 opt-in fixed index; do not assemble/redraw'))
        reader.validate(mix,repo=WAVE2)
        dump(folder/'INDEX.json',dict(schema='mix1-wave1c-index-v1',index=dict(path=str(index),sha256=sha(index)),mix=dict(path=str(mix),sha256=sha(mix)),epoch_rows=D,epochs=8,seed_provenance=SEED,pools=[dict(path=str(r),build_info_sha256=sha(r/'build_info.json')) for r in roots[:len(components)]]))
    from crosscheck import crosscheck
    from custody import CONTROL
    comparison=crosscheck(CONTROL,out/'prep/A12/build_info.json')
    require(comparison['status']=='ok','post-export A12 crosscheck failed')
    dump(out/'EXPORT_RECEIPT.json',dict(status='ok',shared_real=result,derivatives=derivatives,manifests_sha256=sha(manifests/'MANIFESTS_RECEIPT.json'),A12_crosscheck=comparison))
