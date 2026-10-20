"""Build the explicitly authorized as-is codec release; never claims F1/S1 repair."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import gc
import json
from pathlib import Path
import shutil
import subprocess
import unicodedata

from bench.common import read_rows,write_rows
from bench.e1_common import ROOT,atomic_json,files_binding,read_json,sha256
from bench.e3_prepare import real_component
from train.mix import validate,shard_inventory,build,load_rows,assemble


def normalize(text,codec):
    from bench.codec_coverage import load_v1
    _,folds=load_v1();added={a['ch'] for a in codec['atoms'][247:]}
    return ' '.join(''.join(c if c in added else folds.get(c,c) for c in unicodedata.normalize('NFD',text)).split())


def doc_id(value):
    return value.removesuffix(':human').split(':')[-1]


def clone_build(source,target,*,extra=None,codec_path=None):
    """Copy factory rows, changing only codec_version; append native recovered rows.

    Images, IDs, labels, pool order and all other columns are compared with the
    source Arrow table before the new inventory/derivation receipt is published.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    codec_path = Path(codec_path or ROOT/"codec/v2.json")
    version = read_json(codec_path)["version"]
    source,target=Path(source),Path(target)
    if target.exists():
        info=read_json(target/'build_info.json')
        if (info['shard_sha256']!=shard_inventory(target) or
            info['encoding_derivation']['source_receipt_sha256']!=sha256(source/'build_info.json') or
            info['encoding_derivation']['codec_sha256']!=sha256(codec_path)):
            raise ValueError('changed encoding derivative')
        return
    target.mkdir(parents=True);info=copy.deepcopy(read_json(source/'build_info.json'))
    old_counts=Counter();new_counts=Counter()
    for split in ('train','val','reserved'):
        shards=sorted((source/split).glob('shard-*.parquet'))
        if not shards:continue
        tables=[]
        for path in shards:
            before=pq.read_table(path);after=before.set_column(before.schema.get_field_index('codec_version'),before.schema.field('codec_version'),pa.array([version]*len(before)))
            if not before.drop(['codec_version']).equals(after.drop(['codec_version'])):raise ValueError('recode changed source content')
            tables.append(after);old_counts[split]+=len(before)
        if extra:
            for path in sorted((Path(extra)/split).glob('shard-*.parquet')):
                tables.append(pq.read_table(path));new_counts[split]+=len(tables[-1])
        table=pa.concat_tables(tables);folder=target/split;folder.mkdir()
        for i,offset in enumerate(range(0,len(table),4096)):
            pq.write_table(table.slice(offset,4096),folder/f'shard-{i:05d}.parquet',compression='zstd')
        # Independent post-write check, including pixels and label IDs, in order.
        actual=pa.concat_tables([pq.read_table(p) for p in sorted(folder.glob('shard-*.parquet'))])
        if not table.equals(actual):raise ValueError('recode readback differs')
    for name in ('word_tags.jsonl','audit_report.json','select_report.json'):
        if (source/name).is_file():shutil.copyfile(source/name,target/name)
    if extra and (Path(extra)/'word_tags.jsonl').exists():
        with (target/'word_tags.jsonl').open('ab') as f:f.write((Path(extra)/'word_tags.jsonl').read_bytes())
    if (target/'word_tags.jsonl').exists():info['word_tags_sha256']=sha256(target/'word_tags.jsonl')
    if extra:
        einfo=read_json(Path(extra)/'build_info.json')
        recovered_ids=set(einfo.get('record_sha256',{}))
        info['source_drop_ledger']=info.get('drop_ledger',[])
        info['drop_ledger']=[r for r in info.get('drop_ledger',[]) if r['line_id'] not in recovered_ids]
        for key in ('record_sha256','crop_sha256','doc_splits'):
            info.setdefault(key,{}).update(einfo.get(key,{}))
        for key,count in einfo.get('counts_per_script_class',{}).items():
            info.setdefault('counts_per_script_class',{})[key]=info.get('counts_per_script_class',{}).get(key,0)+count
    info['written']={k:old_counts[k]+new_counts[k] for k in set(old_counts)|set(new_counts)}
    info['n_written']=sum(info['written'].values())
    info.update(codec_version=version,shard_sha256=shard_inventory(target))
    info['encoding_derivation']=dict(policy=f'append-compatible {version} tag only; original factory labels/pixels/order unchanged',
        source=str(source),source_receipt_sha256=sha256(source/'build_info.json'),source_shards=shard_inventory(source),
        codec_sha256=sha256(codec_path),old_counts=dict(old_counts),appended_counts=dict(new_counts),
        source_columns_equal=True,readback_equal=True,adapter_sha256=sha256(__file__))
    if extra:info['encoding_derivation']['recovered_inputs']=files_binding([Path(extra)/'build_info.json',*Path(extra).rglob('shard-*.parquet')])
    atomic_json(target/'build_info.json',info)


def make_mix(path,components,version,role='train',notes=''):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():return validate(path,role=role)
    build(components,path,seed=20261015,codec_version=version,created_by='e4-wave1b',role=role,notes=notes)
    return validate(path,role=role)


def train_candidates(prep,codec):
    chars={a['ch'] for a in codec['atoms']};recovered={}
    for c in validate(prep/'mixes/full.json')['components']:
        if c['kind']!='real':continue
        src=Path(c['shard_dir']);wave=src.name;info=read_json(src/'build_info.json')
        bad={r['line_id'] for r in info['drop_ledger'] if r['reason']=='unmapped_codepoint'}
        rows=[r for r in read_rows(prep/'records'/f'{wave}.jsonl') if r['line_id'] in bad and r['split']=='train'
              and set(normalize(r['text'],codec))<=chars]
        recovered[wave]=rows
    return recovered


def exclusions(prep,recovered,books,out):
    docs={doc_id(r['source_doc_id']) for rows in recovered.values() for r in rows}
    checks={};inputs=[books]
    for name in ('v2_test','wikisource_human','e1_real_test'):
        path=prep/'records'/f'{name}.jsonl'
        if path.exists():
            other={doc_id(r['source_doc_id']) for r in read_rows(path)};inputs.append(path)
        else:
            manifest=prep/'mixes'/f'{name}_mix.json';inputs.append(manifest)
            other={doc_id(r['source_doc_id']) for g in load_rows(validate(manifest,role='eval'),'reserved') for r in g}
        checks[name]=dict(heldout_docs=sorted(other),intersection=sorted(docs&other))
    booklist=read_json(books)
    for key,values in [('labelfix_all_books',booklist['books']),('labelfix_DEV_books',booklist['dev_books'])]:
        other={doc_id(d) for d in values};checks[key]=dict(heldout_docs=sorted(other),intersection=sorted(docs&other))
    receipt=dict(state='DONE' if all(not c['intersection'] for c in checks.values()) else 'FAILED',
        recovered_docs=sorted(docs),rows=sum(map(len,recovered.values())),checks=checks,inputs=files_binding(inputs))
    atomic_json(out,receipt)
    if receipt['state']!='DONE':raise ValueError('recovered train intersects heldout documents')


def build_release(a):
    from bench.e4_draw_contract import draw_contract
    from bench.e4_wave1a import release_identity
    root=a.out.resolve();root.mkdir(parents=True,exist_ok=True);prep=a.prep.resolve()
    codec=read_json(ROOT/'codec/v2.json');v1=read_json(ROOT/'codec/v1.json')
    if codec['version']!='v2' or codec['atoms'][:len(v1['atoms'])]!=v1['atoms']:raise ValueError('codec prefix')
    recovered=train_candidates(prep,codec)
    exclusions(prep,recovered,a.labelfix_books.resolve(),root/'zero_intersection.json')
    atomic_json(root/'recovered_inventory.json',dict(rows=sum(map(len,recovered.values())),
        by_wave={k:len(v) for k,v in recovered.items()},by_class_source=dict(Counter(json.dumps([r['script_class'],r['source_dataset']],separators=(',',':')) for rows in recovered.values() for r in rows))))
    # Native import checks every recovered crop through the unchanged image/gate path.
    def native(name,rows):
        dest=root/'native_recovered'/name;feed=root/'records'/f'{name}.jsonl';feed.parent.mkdir(exist_ok=True)
        write_rows(feed,rows)
        if rows and not dest.exists():
            subprocess.run([str(a.factory.resolve()),'import-real','--records',str(feed),'--crops',str(a.crops.resolve()),
                '--out',str(dest),'--partition','e4-v2-recovered-'+name,'--codec-json',str(ROOT/'codec/v2.json')],check=True)
        if rows:
            info=read_json(dest/'build_info.json')
            if info['n_written']!=len(rows) or info['drop_ledger']:raise ValueError('recovered rows failed native admission '+name)
        return dest if rows else None
    native_train={k:native(k,v) for k,v in recovered.items()}
    full=validate(prep/'mixes/full.json');val=validate(prep/'mixes/val_mix.json',role='eval')
    # Clone each old component once, including shared validation-only Wikisource.
    clones={};expanded={};old_counts=[]
    for c in full['components']+val['components']:
        source=Path(c.get('build_dir',c.get('shard_dir')))
        if str(source) in clones:continue
        name=('synthetic' if c['kind']=='synthetic' else source.name)
        target=root/'old_v2'/name;clone_build(source,target);clones[str(source)]=target
        extra=native_train.get(source.name)
        if extra:
            expanded_target=root/'expanded_v2'/name;clone_build(source,expanded_target,extra=extra);expanded[str(source)]=expanded_target
        else:expanded[str(source)]=target
    def components(mix,lookup):
        result=[]
        for c in mix['components']:
            c=copy.deepcopy(c);key='build_dir' if c['kind']=='synthetic' else 'shard_dir';c[key]=str(lookup[c[key]])
            c.pop('build_info_sha256',None)
            if c['kind']=='synthetic':c.pop('shard_sha256',None)
            result.append(c)
        return result
    full_path=prep/'mixes/full.json';val1_path=prep/'mixes/val_mix.json'
    oldpath=root/'mixes/old_v2.json';cpath=root/'mixes/recovered.json';valpath=root/'mixes/val_v2.json'
    make_mix(oldpath,components(full,clones),'v2',notes='Original images, labels, order, draws; codec tag v2 only')
    make_mix(valpath,components(val,clones),'v2',role='eval',notes='Same validation population and labels; prefix-compatible tag only')
    for c in full['components']:
        src=Path(c.get('build_dir',c.get('shard_dir')))
        old_counts.append(read_json(clones[str(src)]/'build_info.json')['encoding_derivation']['old_counts'].get('train',0))
    plan=root/'recovery_plan_v2.json'
    atomic_json(plan,dict(schema='e4-codec-recovery-v1',seed=full['seed'],epoch_rows=428872,old_counts=old_counts,
        policy='Seeded uniform shuffled pool cycles from old plus recovered rows within each original component/class/source quota; unaffected strata retain original draws; no quota or total-draw change'))
    make_mix(cpath,components(full,expanded),'v2',notes='5074 recovered rows in expanded pools; uniform per-stratum pool sampling at exactly preserved old-draw class/source quotas')
    cobj=read_json(cpath);cobj['codec_recovery']=dict(path=str(plan),sha256=sha256(plan));atomic_json(cpath,cobj);validate(cpath)
    # Original four instruments are the common intersection with unchanged references.
    common=dict(data_release='v2-codec',policy='Original factory labels and complete old population; same denominator for A/B/C',instruments={})
    coverage=dict(data_release='v2-codec',policy='Original common rows plus native v2-only admitted held-out rows; original labels are never rewritten',instruments={})
    for instrument in ('v2_test','wikisource_human','e1_real_test','synthetic_heldout'):
        oldmix=prep/'mixes'/f'{instrument}_mix.json';mix=validate(oldmix,role='eval')
        common['instruments'][instrument]=dict(path=str(oldmix),sha256=sha256(oldmix))
        if instrument in ('v2_test','wikisource_human'):
            source=Path(mix['components'][0]['shard_dir']);info=read_json(source/'build_info.json')
            bad={r['line_id'] for r in info['drop_ledger'] if r['reason']=='unmapped_codepoint'}
            rows=[r for r in read_rows(prep/'records'/f'{instrument}.jsonl') if r['line_id'] in bad and set(normalize(r['text'],codec))<={x['ch'] for x in codec['atoms']}]
            extra=native(instrument,rows);target=root/'full_coverage'/instrument;clone_build(source,target,extra=extra)
            cm=copy.deepcopy(mix['components'][0]);cm['shard_dir']=str(target);cm.pop('build_info_sha256',None)
            manifest=root/'mixes'/f'{instrument}_full.json';make_mix(manifest,[cm],'v2',role='eval')
            coverage['instruments'][instrument]=dict(path=str(manifest),sha256=sha256(manifest),added_rows=len(rows))
        else:coverage['instruments'][instrument]=common['instruments'][instrument]
    atomic_json(root/'common_intersection.json',common);atomic_json(root/'full_coverage.json',coverage)
    assets=dict(full_mix=full_path,old_v2_mix=oldpath,recovered_mix=cpath,val_v1=val1_path,val_v2=valpath,
        codec_v1=ROOT/'codec/v1.json',codec_v2=ROOT/'codec/v2.json',common_intersection=root/'common_intersection.json',
        full_coverage=root/'full_coverage.json',reference_stratum=ROOT/'out/e4prep/reference_stratum.json',
        m1_mix=ROOT/'out/e4prep/mixes/m1_replay10.json')
    contracts={}
    for key,path in [('v_a',full_path),('v_b',oldpath),('v_c',cpath)]:
        target=root/f'draw_{key}.json'
        if not target.exists():atomic_json(target,draw_contract(path,root/f'draw_rows_{key}.jsonl.gz'))
        contracts[key]=read_json(target);assets['draw_'+key]=target
        gc.collect()
    if contracts['v_a']!=contracts['v_b']:raise ValueError('A/B draws changed')
    for epoch in map(str,range(1,9)):
        if contracts['v_a']['epochs'][epoch]['class_source_counts']!=contracts['v_c']['epochs'][epoch]['class_source_counts']:
            raise ValueError('C class/source quotas changed')
    # Unused template control/M1 assets remain honestly identified as unsubmitted.
    assets['draw_control']=assets['draw_v_a']
    target=root/'draw_m1.json'
    if not target.exists():atomic_json(target,draw_contract(assets['m1_mix'],root/'draw_rows_m1.jsonl.gz'))
    assets['draw_m1']=target
    from bench.e4_driver import ASSETS,verify_draw_contracts
    if set(assets)!=ASSETS:raise ValueError('campaign-1 template asset set differs')
    verify_draw_contracts({k:read_json(v) for k,v in assets.items() if k.startswith('draw_')})

    template=read_json(ROOT/'out/e4prep/campaign1.release.template.json')
    template.update(tag='v2-codec',status='frozen',F1='not-applicable: authorized as-is wave1b; no S1/label repair',
        authorization='E4 wave 1b coordinator 17 Oct: codec A/B/C on original E3 rows plus codec recovery',
        unsubmitted_template_assets=['m1_mix','draw_m1','draw_control'],
        assets={k:dict(path=str(v),sha256=sha256(v)) for k,v in sorted(assets.items())},
        input_inventory=files_binding([a.factory.resolve(),ROOT/'codec/v2.proposed.json',a.labelfix_books.resolve(),
            root/'zero_intersection.json',root/'recovery_plan_v2.json',root/'recovered_inventory.json',
            *sorted((prep/'records').glob('*.jsonl')),*sorted(root.glob('**/build_info.json')),
            *sorted(root.glob('**/shard-*.parquet')),*sorted(root.glob('draw_rows_*.jsonl.gz'))]),
        v2_asis=release_identity(prep)['binding_sha256'],model_seeds=[0,1,2],data_seed=20261015)
    if template['v2_asis']!='af1ff90200e8ad897e246192da9a420a15fec2793fbc987649dbf2ff77d81621':raise ValueError('original release changed')
    atomic_json(root/'release.json',template)
    print('E4_CODEC_RELEASE_DONE',sha256(root/'release.json'),flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prep',type=Path,default=Path('out/e3'))
    ap.add_argument('--out',type=Path)
    ap.add_argument('--factory',type=Path,default=Path('factory/target/release-e4codec/linefactory'))
    ap.add_argument('--crops',type=Path,default=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/crops'))
    ap.add_argument('--labelfix-books',type=Path,default=Path('out/e4/wave1b/labelfix_books.json'))
    ap.add_argument('--codec', choices=['v2','v2.1'], default='v2')
    ap.add_argument('--font-receipt', type=Path, help='Previously verified per-font raster receipt')
    ap.add_argument('--admissions', type=Path, nargs='+', help='Offline row files to recount for v2.1')
    args=ap.parse_args()
    args.out = args.out or Path('out/e4/wave2_prep/codec_v21' if args.codec=='v2.1' else 'out/e4/wave1b/v2-codec')
    if args.codec == 'v2.1':
        if not args.admissions: ap.error('--codec v2.1 requires --admissions for recovered-row recount')
        from bench.codec_v21 import release
        release(args.admissions, args.out, args.font_receipt)
    else: build_release(args)
if __name__=='__main__':main()
