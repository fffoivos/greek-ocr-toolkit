"""Canonical factory import and unchanged wave-2 shard reader.
Production stops on the recorded loader gaps; diagnostic slice is still runnable.
"""
from core import *
import subprocess,sys,importlib.util,unicodedata
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
WAVE2=W/'e4_wave2_rel3_20261020/code/4537ef9d20a5dc3a'
FACTORY=W/'e4_wave2_rel3_20261020/code/efe9f501e9bf42bb/factory/target/release/linefactory'
FACTORY_SHA='46bf391300853948714662dace1c7ebc3f703e653d1495bd900fd0e0767bca73'

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
    mix_reader=module(Path(wave2)/'train/mix.py','mix1_wave2_reader')
    spec=dict(components=[dict(kind='real',shard_dir=str(pool),fraction=1)],codec_version='v2.1')
    loaded=mix_reader.load_rows(spec,'train')[0]
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
    binding=dict(codec_version='v2.1',codec_sha256=sha(codec),factory_sha256=sha(factory) if factory else None,loader_sha256=sha(Path(wave2)/'train/mix.py'),shard_sha256=mix_reader.shard_inventory(pool))
    dump(out/'CODEC_BINDING.json',binding)
    # Canonical factory order may differ from ref order: always bind the explicit map.
    physical={r['line_id']:i for i,r in enumerate(loaded)}
    dump(out/'REF_PHYSICAL_INDEX.json',[[r['key'],physical[r['line_id']],r['line_id']] for r in ref if r['line_id'] in physical])
    return dict(rows=len(loaded),attempted_rows=len(ref),loader_reader_ok=True,drop_ledger=drops or [],full_membership_preserved=not bool(drops),parents=dict(Counter(r['key'][0] for r in ref)),round_trip=not bool(drops),binding=binding,source_bytes=raw_bytes,census_final_text_differs_factory=literal,census_final_text_differs_factory_nfd=nfd,physical_map_sha256=sha(out/'REF_PHYSICAL_INDEX.json'),status='diagnostic-only; production loader gaps remain')

def production(a):
    here=Path(__file__).resolve().parent
    gaps=json.loads((here/'EXPORT_STATUS.json').read_text())
    require(gaps['status']=='ok','EXPORT stopped: '+ '; '.join(gaps['gaps']))
    raise ValueError('EXPORT stopped: this revision is diagnostic only; trainer owner must resolve the bound gaps')
