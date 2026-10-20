"""E4 wave 2 / H7: hash-bound original admissions at fixed optimizer draws.

Offline bind/mock/prepare; GPU stages require Slurm. Never deploys or submits.
The metadata mock binds all admission rows but uses fixture old/synthetic pools.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from bench.e1_common import ROOT, atomic_json, check_files, files_binding, read_json, sha256
from bench.common import read_rows, write_rows
from bench import e3_driver as e3, e4_wave1b as base, e4_wave1c as labels
from bench.e4_admission import Admission
from bench.line_categories import categories
from bench.o4b_common import tag
from train.mix import validate, load_rows, assemble, shard_inventory

CODEC = ROOT/'codec/v2.1.json'
JOBS = {f'job0{i+1}': [f'{arm}_s{s}' for s in range(3)] for i, arm in enumerate(('ctrl','add','add_corr'))}
WEAK = ('all_caps','numerics','punctuation_heavy','mixed_script','cyrillic')
VERSION_IDS = ('ru1_v2_train','n1_v1_train','sf7-rc1','ru1_v3_edits','n1_v1_w1')
W1 = Path.home()/'Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/w1_originals_v3.jsonl'
W1_SHA = 'd12a7b5a895b43b515e21be1d8bc53d82ac836270f12f7a94b5762418accf5f8'
CROPS = Path.home()/'Projects/collect-v3-data/run/W1/crops'
ADMISSION_TOOL = Path.home()/'Projects/greek-ocr-toolkit-sol-collect/greekocr/harvest/admission.py'


def bound_file(spec):
    path = Path(spec['path']).expanduser().resolve()
    if not re.fullmatch('[0-9a-f]{64}',spec.get('sha256','')) or sha256(path) != spec['sha256']:
        raise ValueError('input sha mismatch: '+str(path))
    return path


def admission_union(specs):
    """Exact identity union; repeated final-file memberships add no training mass."""
    if not specs: raise ValueError('admission file list is empty')
    by_id, custody, memberships = {}, [], defaultdict(list)
    fields = ('row_id','label','crop_sha256','source','primary_class','page_id','crop_bbox')
    for spec in specs:
        path = bound_file(spec); raw = list(read_rows(path))
        if spec.get('rows') is not None and len(raw) != spec['rows']: raise ValueError('admission count mismatch')
        seen = set()
        for row in raw:
            if spec.get('format') == 'release-v3-20261020':
                from bench.e4_wave2_r3 import release_row
                row = release_row(row, spec)
            ident = row.get('row_id')
            if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9_.:-]+',ident):
                raise ValueError('unsafe/missing admission row_id')
            if ident in seen: raise ValueError('duplicate admission row_id within file: '+ident)
            seen.add(ident)
            if (row.get('crop') != 'original' or row.get('arm') != 'release-v3'
                or not isinstance(row.get('label'),str) or not row.get('provenance')
                or not re.fullmatch('[0-9a-f]{64}',row.get('crop_sha256',''))
                or any(k not in row for k in fields)):
                raise ValueError('requires original release-v3 admission with label, provenance and crop sha')
            if ident in by_id and any(by_id[ident][k] != row[k] for k in fields):
                raise ValueError('conflicting admission identity: '+ident)
            if ident not in by_id:
                by_id[ident] = dict(row, crops_root=str(Path(row['crops_root'] if spec.get('format') == 'release-v3-20261020' else spec['crops_root']).expanduser().resolve()),
                                   crops_layout=row['crops_layout'] if spec.get('format') == 'release-v3-20261020' else spec.get('crops_layout','flat'))
            memberships[ident].append(str(path))
        custody.append(dict(path=str(path),sha256=spec['sha256'],rows=len(raw)))
    return [by_id[k] for k in sorted(by_id)], dict(files=custody,unique_rows=len(by_id),
        file_rows=sum(x['rows'] for x in custody),duplicate_memberships=sum(len(v)-1 for v in memberships.values()),
        memberships=dict(memberships))


def encode_admissions(rows):
    context = labels.encoding_context(CODEC); accepted, rejected = [], []
    for row in rows:
        text, ids, bad = labels.encode(row['label'],CODEC,context)
        if bad:
            rejected.append(dict(row_id=row['row_id'],original=row['label'],normalized=text,unmapped=bad,
                                 source=row['source'],primary_class=row['primary_class']))
            continue
        cls = tag(text)
        if cls in ('cyrillic_latin_cs','greek_cyrillic_cs'): cls = 'cyrillic'
        accepted.append(dict(row,line_id=row['row_id'],text=text,gt_nfd=text,label_ids=ids,
            script_class=cls or 'furniture',source_script_class=cls or 'furniture',
            source_dataset=row['source'],wave='new:'+row['source'],split='train',codec_version='v2.1'))
    return accepted,rejected


def crop_path(row):
    root = Path(row['crops_root']).resolve()
    # Only this literal original root; never resolve a masked-copy fallback.
    if 'masked' in str(root).lower(): raise ValueError('masked crop roots forbidden')
    layout = row.get('crops_layout','flat')
    if layout not in ('flat','source/row_id'): raise ValueError('unknown original crop layout')
    relative = Path(row['row_id']+'.png')
    if layout == 'source/row_id':
        source = row['source']
        if not re.fullmatch(r'[A-Za-z0-9_.:-]+',source) or source in ('.','..'):
            raise ValueError('unsafe crop source')
        relative = Path(source)/relative
    path = (root/relative).resolve()
    if not path.is_relative_to(root): raise ValueError('crop escaped original root')
    return path


def upload_plan(rows, out, *, require_present=False):
    """One entry per admitted original crop, even when its label fails codec v2.1."""
    out = Path(out); out.mkdir(parents=True,exist_ok=True)
    entries = []; total = 0; missing = []
    for row in rows:
        path = crop_path(row); size = None
        if path.is_file():
            if sha256(path) != row['crop_sha256']: raise ValueError('original crop hash mismatch: '+row['row_id'])
            size = path.stat().st_size; total += size
        else: missing.append(row['row_id'])
        entries.append(dict(row_id=row['row_id'],local_path=str(path),sha256=row['crop_sha256'],bytes=size,
                            destination='originals/'+str(path.relative_to(Path(row['crops_root']).resolve()))))
    write_rows(out/'UPLOAD_FILES.jsonl',entries)
    receipt = dict(schema='e4-wave2-upload-v1',state='READY' if not missing else 'PENDING_SOURCE_BYTES',
        files=len(entries),verified_files=len(entries)-len(missing),missing_files=len(missing),
        verified_bytes=total,total_bytes=total if not missing else None,GB=total/1e9 if not missing else None,
        inventory_sha256=sha256(out/'UPLOAD_FILES.jsonl'),executed=False)
    atomic_json(out/'UPLOAD_PLAN.json',receipt)
    if require_present and missing: raise ValueError('original crops unavailable; upload plan incomplete')
    return receipt


def merge_real(old, new):
    by_id = {}
    for row in [*old,*new]:
        ident = row['line_id']
        if ident in by_id:
            prev = by_id[ident]
            if prev['label_ids'] != row['label_ids'] or prev['image_png'] != row['image_png']:
                raise ValueError('conflicting old/new real row_id: '+ident)
        else: by_id[ident] = row
    return [by_id[k] for k in sorted(by_id)]


def natural_pools(real, synthetic, synthetic_components):
    """Keep every unique real row; parliament is capped in draw mass, not removed.

    Within the two real source strata each row has equal frequency. No class
    multiplier: primary collection quotas remain provenance, not upsampling.
    """
    groups = [[r for r in real if r['wave'] != 'parliament'],[r for r in real if r['wave'] == 'parliament']]
    non, parl = map(len,groups)
    if not non: raise ValueError('cannot satisfy parliament cap without non-parliament rows')
    share = min(parl/(non+parl),.25)
    fractions = [.5*(1-share),.5*share]
    comps = [dict(kind='real',fraction=f,source=s) for f,s in zip(fractions,('non_parliament','parliament'))]
    mass = sum(c['fraction'] for c in synthetic_components)
    if mass <= 0 or not synthetic: raise ValueError('synthetic v5 support required')
    groups += synthetic
    comps += [dict(c,fraction=.5*c['fraction']/mass) for c in synthetic_components]
    # Empty parliament component would otherwise need a fake shard inventory.
    if not parl: groups.pop(1); comps.pop(1)
    return groups,comps,dict(real_unique=non+parl,parliament_unique=parl,parliament_real_draw_share=share,
        synthetic_fraction=.5,synthetic_equivalent_pool_mass=non+parl,
        policy='all accepted real IDs retained; natural per-row mass except parliament cap 25% of real')


def draw_stats(groups, components, seed, rows, epochs, *, recovery=None):
    stats = Counter(); support = set(); manifest = hashlib.sha256(); epoch_counts = {}
    for epoch in range(1,epochs+1):
        drawn, counts = assemble(groups,[c['fraction'] for c in components],seed,epoch,rows,exact_rows=True,recovery=recovery)
        syn = sum(n for n,c in zip(counts,components) if c['kind']=='synthetic')
        real = rows-syn
        parl = sum(components[r['_component']]['kind']=='real' and r.get('wave')=='parliament' for r in drawn)
        if syn != rows//2: raise ValueError('synthetic draw fraction differs from 50%')
        # At most one rounding draw per source stratum. Hard cap checked below.
        epoch_counts[str(epoch)] = dict(draws=len(drawn),synthetic=syn,real=real,parliament=parl,
            parliament_real_share=parl/real)
        for r in drawn:
            kind = components[r['_component']]['kind']; cls = r.get('source_script_class',r['script_class'])
            stats[(kind,cls)] += 1
            support.add((kind,r['_component'],r['_pool_index']))
            manifest.update(labels._line([epoch,r['_component'],r['_pool_index'],r['line_id'],
                hashlib.sha256(r['image_png']).hexdigest(),r['label_ids']]))
    return dict(draws=rows*epochs,unique_drawn=len(support),repeats=rows*epochs-len(support),epochs=epoch_counts,
        ordered_image_label_sha256=manifest.hexdigest(),by_class={kind:{c:n for (k,c),n in sorted(stats.items()) if k==kind}
            for kind in ('real','synthetic')})


def mix_table(old, added, old_components, add_components, seed, out, *, rows=base.ROWS, epochs=8, recovery=None):
    previous = draw_stats(old,old_components,seed,rows,epochs,recovery=recovery)
    current = draw_stats(added,add_components,seed,rows,epochs)
    if any(v['parliament']*4 > v['real'] for v in current['epochs'].values()):
        raise ValueError('parliament draw cap exceeded after integer apportionment')
    def unique(groups,components):
        return Counter(r.get('source_script_class',r['script_class']) for g,c in zip(groups,components)
                       if c['kind']=='real' for r in g)
    p,n = unique(old,old_components),unique(added,add_components)
    table = [dict(script_class=c,previous_unique_rows=p[c],new_unique_rows=n[c],
        previous_draws=previous['by_class']['real'].get(c,0),new_draws=current['by_class']['real'].get(c,0),
        previous_draw_share=previous['by_class']['real'].get(c,0)/previous['draws'],
        new_draw_share=current['by_class']['real'].get(c,0)/current['draws']) for c in sorted(p.keys()|n.keys())]
    result = dict(codec='codec v2.1 in all arms',codec_sha256=sha256(CODEC),schema='e4-wave2-mix-v1',denominator='all draws, including synthetic; classes disjoint',
        previous=previous,new=current,table=table)
    atomic_json(Path(out)/'MIX_TABLE.json',result)
    text = 'codec v2.1 in all arms (ctrl/add/add_corr).\n\n| Class | Previous unique | Union unique | Previous draw share | New draw share |\n|---|---:|---:|---:|---:|\n'
    text += ''.join(f"| {r['script_class']} | {r['previous_unique_rows']} | {r['new_unique_rows']} | {r['previous_draw_share']:.8%} | {r['new_draw_share']:.8%} |\n" for r in table)
    (Path(out)/'MIX_TABLE.md').write_text(text)
    return result


def verdict(control, add, corrected, corrected_classes, *, mode='PRODUCTION'):
    """Strict rational comparisons; equality at the range boundary is refuted."""
    from fractions import Fraction
    if mode != 'PRODUCTION': return dict(add=mode+'_ONLY',add_corr=mode+'_ONLY')
    required = {'overall',*WEAK}
    if not required <= control.keys() or not required <= add.keys():
        return dict(add='H7_PENDING_MISSING_SLICE',add_corr='H7_PENDING_MISSING_SLICE')
    def values(data,key):
        v = data[key]
        if set(v) != {'0','1','2'}: raise ValueError('missing seeds')
        result=[]
        for m in v.values():
            if not m or m['ref_len'] <= 0 or m.get('lines',0) <= 0: raise ValueError('empty support')
            result.append(Fraction(m['edits'],m['ref_len']))
        return result
    def improves(a,b,key):
        left,right=values(a,key),values(b,key)
        return sum(left)/3-sum(right)/3 > max(left)-min(left)
    try:
        passed = all([improves(control,add,k) for k in sorted(required)])
        # Validate every gate even when an earlier one fails.
        for k in required: values(control,k); values(add,k)
        vadd = 'H7_ADD_CONFIRMED' if passed else 'H7_ADD_REFUTED'
    except (ValueError,KeyError):
        return dict(add='H7_PENDING_MISSING_SEEDS_OR_SUPPORT',add_corr='H7_PENDING_MISSING_SEEDS_OR_SUPPORT')
    if not corrected_classes: return dict(add=vadd,add_corr='H7_PENDING_NO_CORRECTED_CLASSES')
    try:
        further = all([sum(values(corrected,'class:'+k)) < sum(values(add,'class:'+k)) for k in corrected_classes])
        corr = 'H7_ADD_CORR_CONFIRMED' if further else 'H7_ADD_CORR_REFUTED'
    except (ValueError,KeyError): corr = 'H7_PENDING_MISSING_SEEDS_OR_SUPPORT'
    return dict(add=vadd,add_corr=corr)


def selected_overlay(registry, names=None, *, production=True):
    obj = read_json(registry)
    selected = names if names is not None else [n for n,v in obj['versions'].items()
        if (n in VERSION_IDS or n.startswith('sf7-rc1')) and (v.get('status')=='released' or (v.get('status')=='local'
            and v.get('e4_adoption')=='coordinator-registered' and v.get('provenance')))]
    if not selected: raise ValueError('no registered released corrections; add_corr cannot bind')
    return labels.overlay_spec(registry,selected,CODEC,production=production)


def materialize(directory, rows, *, source, inputs):
    """Lossless union of factory rows. Parent custody is retained, no recropping."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    directory=Path(directory); (directory/'train').mkdir(parents=True,exist_ok=True)
    path=directory/'train/shard-00000.parquet'
    pq.write_table(pa.Table.from_pylist([dict(r,codec_version='v2.1') for r in rows]),path)
    info=dict(kind='real',codec_version='v2.1',partition_id='e4-wave2-union-v1',
        shard_sha256=shard_inventory(directory),parent_inputs=inputs,source=source,
        operation='lossless exact-row-id union of already imported factory rows')
    atomic_json(directory/'build_info.json',info)
    return dict(kind='real',shard_dir=str(directory),shard_sha256=info['shard_sha256'],
        partition_id=info['partition_id'],source=source)


def import_admissions(rows, directory, *, factory, split='train'):
    """Import only sha-verified ORIGINAL crops through canonical Rust codec v2.1."""
    from bench.e1_prepare import factory_build
    groups=defaultdict(list)
    for row in rows: groups[row['crops_root']].append(row)
    result=[]; inputs=[]
    for i,(root,group) in enumerate(sorted(groups.items())):
        records=[]
        for row in group:
            path=crop_path(row)
            if sha256(path)!=row['crop_sha256']: raise ValueError('original crop hash changed')
            inputs.append(path)
            records.append(dict(id=row['line_id'],text=row['text'],crop_path=str(path.relative_to(Path(root).resolve())),doc=row['edition_id'],
                split=split,source_dataset=row['source'],script_class=row['script_class'],admitted=True))
        feed=directory/f'import_{i}.jsonl';write_rows(feed,records)
        build=directory/f'factory_{i}'
        if not build.exists():
            factory_build(factory,['import-real','--records',feed,'--crops',root,
                '--partition','e4-wave2-source-editions-v1','--codec-json',CODEC],build)
        info=read_json(build/'build_info.json')
        if info['records_sha256']!=sha256(feed) or info['shard_sha256']!=shard_inventory(build):
            raise ValueError('factory import custody changed')
        if info.get('drop_ledger'): raise ValueError('factory dropped codec-accepted admissions; inspect drop_ledger')
        pool=[]
        import pyarrow.parquet as pq
        for p in sorted((build/split).glob('shard-*.parquet')): pool+=pq.read_table(p).to_pylist()
        source={r['line_id']:r for r in group}
        if {r['line_id'] for r in pool}!=set(source): raise ValueError('factory lost admission IDs')
        for row in pool:
            original=source[row['line_id']]
            if row['label_ids']!=original['label_ids']: raise ValueError('Rust/Python codec policy drift')
            row.update(wave='new:'+original['source'],source_script_class=row['script_class'])
        result+=pool;inputs += [feed,*[p for p in build.rglob('*') if p.is_file()]]
    return result,inputs


def edition_guard(real, cfg, prep):
    """Require sourcing's cross-source edition map; hashed page IDs are insufficient."""
    mapping={}
    if cfg.get('split2'):
        from bench.e4_wave2_r3 import split2_ledgers
        mapping, _ = split2_ledgers(cfg)
    else:
        for row in read_rows(bound_file(cfg['editions'])):
            if row['row_id'] in mapping or not row.get('edition_id'): raise ValueError('invalid edition map')
            mapping[row['row_id']]=row['edition_id']
    oldmeta={}
    for p in sorted((prep/'records').glob('*.meta.jsonl')):
        for r in read_rows(p):
            if r['line_id'] in oldmeta and oldmeta[r['line_id']]!=r: raise ValueError('conflicting old metadata')
            oldmeta[r['line_id']]=r
    oldtrain=set()
    for r in real:
        if r['line_id'] not in oldmeta: raise ValueError('missing old row metadata')
        m=oldmeta[r['line_id']]
        if not m.get('book_key') or not m.get('wave'): raise ValueError('missing old edition/wave')
        r.update(wave=m['wave'],edition_id=m['book_key'])
        oldtrain.add(r['edition_id'])
    heldout=set(read_json(bound_file(cfg['heldout_editions']))['edition_ids'])
    if not heldout: raise ValueError('empty heldout editions')
    # Bind all old reserved/val metadata, in addition to sourcing's exclusions.
    for p in (prep/'records').glob('*.jsonl'):
        if p.name.endswith('.meta.jsonl'): continue
        for r in read_rows(p):
            if r.get('split') in ('reserved','val') and r.get('line_id') in oldmeta:
                heldout.add(oldmeta[r['line_id']]['book_key'])
    return mapping,oldtrain,heldout


def standard_admission(a):
    decisions = getattr(a, 'admission', None)
    receipts = getattr(a, 'admission_receipt', None) or []
    tool = getattr(a, 'admission_tool', ADMISSION_TOOL)
    # Allocation wrappers can consume the same hash-bound INPUTS configuration.
    # Explicit CLI pairs take precedence; an incomplete pair never falls back.
    if not decisions and not receipts and getattr(a, 'inputs', None):
        config = read_json(a.inputs).get('standard_admission', {})
        decisions = [p['admission'] for p in config.get('pairs', [])]
        receipts = [p['receipt'] for p in config.get('pairs', [])]
        tool = config.get('tool', tool)
    if not decisions and not receipts and getattr(a, 'inputs', None):
        census = read_json(a.inputs).get('census05')
        if census:
            from bench.e4_wave2_r3 import Census05Admission
            return Census05Admission(census)
    return Admission(decisions, receipts, tool)


def filtered_control(old, oldmix, gate, out, parent, *, smoke=False):
    """Materialize passing real rows; retain the pinned synthetic pools/fractions.

    Original recovery/index plans address pre-filter pool positions and cannot
    be reused after selection. This control has a fresh bound draw contract.
    """
    groups, components = [], []
    for i, (pool, component) in enumerate(zip(old, oldmix['components'])):
        c = {k: v for k, v in component.items() if k not in ('build_info_sha256', 'shard_sha256')}
        if c['kind'] == 'real':
            pool = gate.filter(pool)
            if not pool and c['fraction'] > 0:
                raise ValueError('admission filters emptied an active control component')
            if smoke: pool = pool[:10]
            gate.require_pass(pool)
            c = dict(materialize(out/f'control_{i}', pool, source=c['source'], inputs=parent), fraction=c['fraction'])
        else:
            from bench.e4_codec_release import clone_build
            target = out/f'control_synthetic_{i}'
            clone_build(c['build_dir'], target, codec_path=CODEC)
            c['build_dir'] = str(target)
            pool = [dict(r, codec_version='v2.1') for r in pool]
        groups.append(pool); components.append(c)
    mix = {k: v for k, v in oldmix.items() if k not in ('components', 'codec_recovery', 'matched_replay', 'label_versions')}
    mix.update(components=components, codec_version='v2.1', notes='Standard-admission-filtered control; fresh deterministic draws')
    path = out/'ctrl_mix.json'
    e3.immutable(path, mix)
    if smoke:
        path = labels.slice_mix(path, out/'smoke_data/ctrl.json', 'train', 20)
        mix = validate(path); groups = load_rows(mix, 'train')
    return path, mix, groups


def validation_v21(source, out):
    """Append-compatible validation tag derivative; IDs/labels/pixels/order unchanged."""
    from bench.e4_codec_release import clone_build
    original=validate(source,role='eval'); components=[]
    for i,c in enumerate(original['components']):
        if c['kind']!='real': raise ValueError('shared validation requires real rows')
        target=out/f'component_{i}'
        clone_build(c['shard_dir'],target,codec_path=CODEC)
        cc={k:v for k,v in c.items() if k not in ('build_info_sha256','shard_sha256')}
        cc.update(shard_dir=str(target),shard_sha256=shard_inventory(target));components.append(cc)
    path=out/'mix.json'
    e3.immutable(path,dict(original,components=components,codec_version='v2.1',
        notes='Same validation IDs/labels/pixels/order; append-compatible v2.1 tag'))
    validate(path,role='eval')
    return path


def prepare(a):
    cfg=read_json(a.inputs)
    from bench.e4_wave2_r3 import refuse_locked
    refuse_locked(cfg)
    if (a.out/'node_binding.json').exists(): return verify(a)
    inventory_only = getattr(a, 'stage', None) == 'inventory'
    if cfg.get('census05') and not os.environ.get('SLURM_JOB_ID'):
        raise ValueError('census05 preparation requires a Slurm compute allocation')
    allowed_status = ('INVENTORY_ONLY', 'FINAL') if inventory_only else ('FINAL',)
    if cfg.get('schema')!='e4-wave2-inputs-v1' or cfg.get('status') not in allowed_status:
        raise ValueError('final admission binding required; W1 mock is not production')
    if not any(s.get('final') for s in cfg['admissions']): raise ValueError('final release admission file missing')
    gate=standard_admission(a)
    gate.require_coverage([s['path'] for s in cfg['admissions']])
    rows,admission=admission_union(cfg['admissions'])
    rows=gate.filter(rows)
    if cfg.get('census05'):
        for row in rows:
            row['primary_class'] = gate.decision(row)['primary_class']
    accepted,rejected=encode_admissions(rows)
    spec=selected_overlay(a.registry,cfg.get('versions'))
    release,assets,digest=base.load_release(a)
    if digest!=labels.RELEASE or sha256(a.campaign/'v2-codec/draw_rows_v_c.jsonl.gz')!=labels.DRAW_SHA:
        raise ValueError('unpinned v_c release/draws')
    oldmix=validate(assets['recovered_mix']);old=load_rows(oldmix,'train')
    old_inputs=[Path(assets['recovered_mix'])]
    for component in oldmix['components']:
        folder=Path(component.get('build_dir',component.get('shard_dir')))
        old_inputs += [p for p in folder.rglob('*') if p.is_file()]
    for key in ('codec_recovery','matched_replay'):
        if key in oldmix:old_inputs.append(Path(oldmix[key]['path']))
    real=merge_real([r for g,c in zip(old,oldmix['components']) if c['kind']=='real' for r in g],[])
    gate.require_census(real,[s['path'] for s in cfg['admissions']])
    real=gate.filter(real)
    mapping,oldtrain,heldout=edition_guard(real,cfg,a.prep)
    for r in accepted:
        if r['row_id'] not in mapping: raise ValueError('missing new-source edition identity')
        r['edition_id']=mapping[r['row_id']]
    if oldtrain & heldout or {r['edition_id'] for r in accepted} & heldout:
        raise ValueError('training/heldout edition overlap')
    if inventory_only:
        if not os.environ.get('SLURM_JOB_ID') or a.smoke or not cfg.get('census05'):
            raise ValueError('inventory requires a non-smoke census05 compute allocation')
        from bench.e4_wave2_r3 import prepare_exposure
        a.out.mkdir(parents=True,exist_ok=True)
        inventory = prepare_exposure(real, accepted, gate, cfg, a.out)
        if {r['line_id'] for r in real} & {r['line_id'] for r in accepted}:
            raise ValueError('inventory requires review of overlapping old/new IDs')
        _, overlay = labels.substitute([real,accepted],[dict(kind='real'),dict(kind='real')],spec)
        atomic_json(a.out/'substitution.json',overlay)
        from bench.e4_wave2_r3 import inventory_summary
        synth=[g for g,c in zip(old,oldmix['components']) if c['kind']=='synthetic']
        sc=[c for c in oldmix['components'] if c['kind']=='synthetic']
        ctrlpath,cm,cg=filtered_control(old,oldmix,gate,a.out,files_binding([*gate.inputs,*old_inputs]))
        groups,comps,_=natural_pools([*real,*accepted],synth,sc)
        inventory_summary(cg,cm,groups,comps,overlay,a.out)
        atomic_json(a.out/'INVENTORY_DONE.json',dict(mode='INVENTORY_ONLY',ctrl_rows=len(real),
            add_rows=len(real)+len(accepted),add_corr_rows=len(real)+len(accepted),
            release_rows=len(rows),codec_rejections=rejected,corrected_rows=overlay['rows_substituted'],
            ctrl_by_class=dict(Counter(r.get('source_script_class',r['script_class']) for r in real)),
            add_by_class=dict(Counter(r.get('source_script_class',r['script_class']) for r in [*real,*accepted])),
            census_final_text_differs_factory=sum(gate.decision(r)['final_text']!=r['text'] for r in real),
            input_spec_sha256=sha256(a.inputs)))
        return inventory
    a.out.mkdir(parents=True,exist_ok=True);(a.out/'logs').mkdir(exist_ok=True)
    (a.out/'workers.log').touch(exist_ok=True)
    from bench.codec_v21 import recount
    atomic_json(a.out/'CODEC_V21_RECOUNT.json', recount(rows))
    upload_plan(rows,a.out/'upload',require_present=True)
    atomic_json(a.out/'admission_receipt.json',dict(**admission,accepted=len(accepted),codec_rejections=rejected))
    if a.smoke:
        accepted=accepted[:10]
    waves={r['line_id']:r['wave'] for r in real}
    for g,c in zip(old,oldmix['components']):
        if c['kind']=='real':
            for r in g:
                if r['line_id'] in waves:r['wave']=waves[r['line_id']]
    ctrlpath,oldmix,old=filtered_control(old,oldmix,gate,a.out,files_binding([*gate.inputs,*old_inputs]),smoke=a.smoke)
    if a.smoke:
        ctrlpath = labels.slice_mix(ctrlpath, a.out/'smoke_data/control.json', 'train', 20)
        oldmix = validate(ctrlpath); old = load_rows(oldmix, 'train')
    real=merge_real([r for g,c in zip(old,oldmix['components']) if c['kind']=='real' for r in g],[])
    standard=gate.receipt(len(real))
    if cfg.get('census05'):
        import unicodedata
        standard['census_final_text_differs_factory'] = sum(gate.decision(r)['final_text'] != r['text'] for r in real)
        standard['census_final_text_differs_factory_nfd'] = sum(unicodedata.normalize('NFD', gate.decision(r)['final_text']) != unicodedata.normalize('NFD', r['text']) for r in real)
    atomic_json(a.out/'STANDARD_ADMISSION.json',standard)
    (a.out/'PREREGISTRATION.md').write_text(
        'codec v2.1 in all arms (ctrl/add/add_corr).\n'
        'Control and candidates are filtered identically with the standard admission rules; '
        f"the resulting control row count is {len(real)}.\n")
    if cfg.get('census05'):
        from bench.e4_wave2_r3 import prepare_exposure
        prepare_exposure(real, accepted, gate, cfg, a.out)
    new,import_inputs=import_admissions(accepted,a.out/'imports',factory=a.factory)
    gate.require_pass(new)
    union=merge_real(real,new)
    gate.require_pass(union)
    synth=[g for g,c in zip(old,oldmix['components']) if c['kind']=='synthetic']
    sc=[c for c in oldmix['components'] if c['kind']=='synthetic']
    if any(c['recipe_sha256']!=sha256(ROOT/'factory/recipe.v5.json') for c in sc): raise ValueError('synthetic recipe is not v5')
    groups,comps,policy=natural_pools(union,synth,sc)
    input_paths=[*gate.inputs,*old_inputs,ROOT/'bench/e4_admission.py',ROOT/'bench/codec_v21.py',ROOT/'bench/e4_codec_release.py',a.inputs,a.registry,CODEC,a.factory,a.campaign/'v2-codec/release.json',
        *[Path(v['path']) for v in labels.check_overlay(spec).values()],
        *[Path(s['path']).expanduser() for s in cfg['admissions']],
        bound_file(cfg['editions']),bound_file(cfg['heldout_editions']),*import_inputs]
    if cfg.get('census05'):
        input_paths += [bound_file(v) for v in cfg['input_files']]
        input_paths += [bound_file(cfg['census05'][k]) for k in ('admitted_train','final_policy')]
        from bench.e4_wave2_r3 import sealed_rows
        _, benchmark_files = sealed_rows(cfg['benchmark_0_2'])
        input_paths += [Path(f['path']) for f in benchmark_files]
    parent=files_binding(input_paths)
    runtime=[]
    for i,(g,c) in enumerate(zip(groups,comps)):
        if c['kind']=='real': runtime.append(dict(materialize(a.out/f'union_{i}',g,source=c['source'],inputs=parent),fraction=c['fraction']))
        else: runtime.append({k:v for k,v in c.items() if k not in ('build_info_sha256','shard_sha256')})
    mix=dict(schema_version=1,components=runtime,seed=oldmix['seed'],codec_version='v2.1',created_by='E4 wave2',notes='Natural union, 25% real parliament cap; 50% synthetic v5')
    e3.immutable(a.out/'add_mix.json',mix)
    e3.immutable(a.out/'add_corr_mix.json',dict(mix,label_versions=spec))
    fixed,stats=labels.substitute(groups,comps,spec)
    corrected_classes = sorted({r['script_class'] for r in stats['changes']})
    evaluation_primary_class = {}
    if cfg.get('census05'):
        corrected_classes = sorted({'numerics_tables' if gate.rows[r['row_id']]['primary_class'] == 'numerics_tables'
            else r['script_class'] for r in stats['changes']})
        evaluation_primary_class = {ident:r['primary_class'] for ident,r in gate.rows.items() if r['split'] != 'train'}
    atomic_json(a.out/'substitution.json',stats)
    epochs=1 if a.smoke else 8;draws=20 if a.smoke else base.ROWS
    pair=labels.draw_contract(groups,fixed,mix,a.out/'draws/paired',rows=draws,epochs=epochs)
    ctrl_contract=labels.draw_contract(old,old,oldmix,a.out/'draws/ctrl',rows=draws,epochs=epochs,
        reference=None,indexed=None)
    table=mix_table(old,groups,oldmix['components'],comps,mix['seed'],a.out,rows=draws,epochs=epochs,recovery=oldmix.get('codec_recovery'))
    table['standard_admission']=standard
    atomic_json(a.out/'MIX_TABLE.json',table)
    with (a.out/'MIX_TABLE.md').open('a') as stream:
        stream.write('\nStandard admission drops (source × class × rule):\n\n```json\n'+json.dumps(standard['drops_per_source_class'],indent=2)+'\n```\n')
    evals=labels.instruments(a)
    for path in [assets['val_v2'],*evals.values()]:
        role='val' if path==assets['val_v2'] else 'eval'
        instrument=validate(path,role=role)
        pools=load_rows(instrument,'val' if role=='val' else 'reserved')
        for pool,component in zip(pools,instrument['components']):
            if not cfg.get('census05') and component['kind'] in ('real','legacy_eval'):gate.require_pass(pool)
    if cfg.get('census05'):
        from bench.e4_wave2_r3 import prepare_benchmark
        evals.update(prepare_benchmark(cfg, a.out/'benchmark_0_2', a.factory, CODEC))
    val=validation_v21(assets['val_v2'],a.out/'validation_v21')
    if a.smoke:
        val=labels.slice_mix(val,a.out/'smoke_data/val.json','val',8)
        evals={k:labels.slice_mix(v,a.out/f'smoke_data/{k}.json','reserved',4) for k,v in evals.items()}
    names=['ctrl_s0','add_s0','add_corr_s0'] if a.smoke or a.job=='preflight' else JOBS[a.job]
    arms=[]
    for run in names:
        config,seed=run.rsplit('_s',1);p=base.parameters(a.out,50,int(seed),draws)
        p.update(mix=str(ctrlpath if config=='ctrl' else a.out/f'{config}_mix.json'),codec=str(CODEC),
            val_mix=str(val),transfer_mix=None,repeat_to_epoch_rows=True,width_mult=2.,epochs=epochs)
        if a.smoke:p['workers']=0
        arms.append(dict(arm=config,run=run,seed=int(seed),parameters=p,initialization='from-scratch'))
    input_paths += [*base.code_files(),*[ROOT/p for p in ('bench/e1_prepare.py','bench/o5_prepare.py','bench/codec_coverage.py','bench/o4b_common.py','bench/line_categories.py','factory/Cargo.toml','factory/Cargo.lock')],*ROOT.glob('scripts/ops/*wave2*'),*ROOT.glob('scripts/clariden/*wave2*'),
        *ROOT.glob('codec/*.json'),*a.out.glob('*.json'),*evals.values(),val,ctrlpath]
    for path in [ctrlpath,a.out/'add_mix.json',val,*evals.values()]:
        obj=validate(path,role='train' if path in (ctrlpath,a.out/'add_mix.json') else 'val' if path==val else 'eval')
        for c in obj['components']:
            folder=Path(c.get('build_dir',c.get('shard_dir')))
            input_paths += [p for p in folder.rglob('*') if p.is_file()]
        for key in ('codec_recovery','matched_replay'):
            if key in obj:input_paths.append(Path(obj[key]['path']))
    input_paths += [a.out/'PREREGISTRATION.md']
    input_paths += sorted((a.prep/'records').glob('*.meta.jsonl'))
    e3.immutable(a.out/'arms.json',arms)
    node=dict(schema='e4-wave2-node-v1',mode='SMOKE' if a.smoke else 'PRODUCTION',job=a.job,root=str(ROOT),out=str(a.out),
        prep=str(a.prep),campaign=str(a.campaign),input_spec=str(a.inputs),input_spec_sha256=sha256(a.inputs),
        versions=spec,release_sha256=labels.RELEASE,arms=arms,instruments={k:str(v) for k,v in evals.items()},
        corrected_classes=corrected_classes, evaluation_primary_class=evaluation_primary_class,
        inputs=files_binding(input_paths),draw_contract=pair,ctrl_contract=ctrl_contract,policy=policy,
        admission=admission,standard_admission=standard,control='retrain',mix_table_sha256=sha256(a.out/'MIX_TABLE.json'))
    e3.immutable(a.out/'node_binding.json',node)
    return verify(a)


def verify(a):
    node=read_json(a.out/'node_binding.json')
    if any(node[k]!=str(v) for k,v in dict(root=ROOT,out=a.out,prep=a.prep,campaign=a.campaign,input_spec=a.inputs).items()):
        raise ValueError('wave2 binding destination mismatch')
    if node['schema']!='e4-wave2-node-v1' or node['mode']!=('SMOKE' if a.smoke else 'PRODUCTION') or node['job']!=a.job:
        raise ValueError('wave2 mode/job mismatch')
    if not node.get('standard_admission',{}).get('refuses_unfiltered_rows'):
        raise ValueError('legacy binding lacks standard admission receipts; rebind required')
    check_files(node['inputs']);labels.check_overlay(node['versions'])
    for contract,folder in ((node['draw_contract'],'paired'),(node['ctrl_contract'],'ctrl')):
        for ep in contract['epochs'].values():check_files(ep['files'])
        if sha256(a.out/f'draws/{folder}/v_c_indices.jsonl.gz')!=contract['indexed_sha256']:raise ValueError('changed draw indices')
    if read_json(a.out/'arms.json')!=node['arms']:raise ValueError('changed arms')
    return node


def evaluate_arm(a, arm):
    from bench.e1_eval import evaluate_run
    from bench import e1_common
    node = verify(a); original = e1_common.runtime_binding
    e1_common.runtime_binding = lambda device:e3.allocation_runtime(original(device))
    try:
        for name, path in node['instruments'].items():
            codec = ROOT/'codec'/f"{read_json(path)['codec_version']}.json"
            evaluate_run(a.out, arm['run'], name, Path(path), codec_path=arm['parameters']['codec'], reference_codec_path=codec)
        cfg = read_json(a.inputs)
        if cfg.get('benchmark_0_2'):
            from bench.e4_wave2_r3 import score_benchmark
            score_benchmark(cfg, a.out, arm['run'], a.smoke)
    finally:
        e1_common.runtime_binding = original


def report(a, roots):
    from bench.e1_readout import summarize, metric, clean_row
    results, class_values, sources, populations = {}, defaultdict(lambda:defaultdict(dict)), {}, {}
    overall_values = defaultdict(lambda:defaultdict(dict))
    common = None
    slices = defaultdict(lambda:defaultdict(lambda:defaultdict(dict)))
    for run, root in roots.items():
        local = copy.copy(a); local.out = root; local.job = read_json(root/'node_binding.json')['job']
        node = verify(local)
        identity = {k:node[k] for k in ('mode','versions','release_sha256','corrected_classes','input_spec_sha256','mix_table_sha256')}
        if common is not None and identity != common: raise ValueError('mixed aggregate identity')
        common = identity
        done = base.verify_done(root/'runs'/run)
        arm = next(r for r in node['arms'] if r['run'] == run)
        if (done['binding']['node_binding_sha256'] != sha256(root/'node_binding.json')
            or done['binding']['parameters'] != arm['parameters']
            or done['binding'] != read_json(root/'runs'/run/'run_binding.json')):
            raise ValueError('completed run differs from arm/node binding')
        expected_epochs=1 if a.smoke else 8
        if (done['epoch']!=expected_epochs or done['budget_epochs']!=expected_epochs
            or done['global_step']!=((arm['parameters']['epoch_rows']+63)//64)*expected_epochs):
            raise ValueError('completed run differs from fixed epoch/update budget')
        config, seed = run.rsplit('_s',1)
        for name in node['instruments']:
            pred = root/'predictions'/f'{run}_{name}.jsonl'; rec = read_json(pred.with_suffix('.receipt.json'))
            if sha256(pred) != rec['predictions_sha256']: raise ValueError('prediction hash mismatch')
            if rec['binding']['checkpoint_sha256'] != done['checkpoint_hashes']['best.pt']:
                raise ValueError('prediction checkpoint mismatch')
            if (rec['binding']['mix_sha256'] != sha256(node['instruments'][name])
                or rec['binding']['codec_sha256'] != sha256(arm['parameters']['codec'])
                or rec['binding']['provenance_sha256'] != done['provenance_sha256']):
                raise ValueError('prediction data/codec/provenance mismatch')
            reference_codec=ROOT/'codec'/f"{read_json(node['instruments'][name])['codec_version']}.json"
            if rec['binding']['reference_codec_sha256']!=sha256(reference_codec):
                raise ValueError('prediction reference codec mismatch')
            check_files(rec['crop_hashes'])
            raw = list(read_rows(pred))
            if len(raw) != rec['result']['n_lines'] or any(r['arm'] != config or r['seed'] != int(seed) or r['instrument'] != name for r in raw):
                raise ValueError('prediction population identity mismatch')
            reference_population = sorted((r['line_id'], r['gt'], sha256(r['crop_path'])) for r in raw)
            if name in populations and populations[name] != reference_population: raise ValueError('different evaluation populations')
            populations[name] = reference_population
            rows = e3.joined_rows(raw, a.prep, name.removesuffix('_full_coverage')) if name.removesuffix('_full_coverage') in e3.INSTRUMENTS[:2] else [clean_row(r) for r in raw]
            result = summarize(rows)
            result['by_source_script_class'] = {c:metric([r for r in rows if r.get('source_script_class',r['script_class']) == c])
                for c in sorted({r.get('source_script_class',r['script_class']) for r in rows})}
            if node.get('evaluation_primary_class'):
                numeric = [r for r in rows if node['evaluation_primary_class'].get(r['line_id']) == 'numerics_tables']
                result['by_source_script_class']['numerics_tables'] = metric(numeric)
                result['by_category']['numerics'] = metric(numeric)
            result['by_wave'] = {w:metric([r for r in rows if r.get('wave','unknown') == w]) for w in sorted({r.get('wave','unknown') for r in rows})}
            result['changed_label'] = labels.changed_slice(rows, node['versions']) if name in ('v2_test', 'v2_test_full_coverage') else None
            results[run+'/'+name] = result
            if name in ('v2_test','v2_test_full_coverage'):
                selected={'overall':result['overall']}
                selected.update({k:result['by_category'].get(k) for k in WEAK if k!='cyrillic'})
                selected['cyrillic']=result['by_source_script_class'].get('cyrillic')
                selected.update({'class:'+k:v for k,v in result['by_source_script_class'].items()})
                for key,m in selected.items():slices[name][config][key][seed]=m
            overall_values[name][config][seed] = result['overall']['cer']
            if name in ('v2_test', 'v2_test_full_coverage'):
                for cls, m in result['by_source_script_class'].items():
                    if m['lines']: class_values[name][config].setdefault(cls,{})[seed] = m['cer']
            sources[str(pred)] = sha256(pred); sources[str(pred.with_suffix('.receipt.json'))] = sha256(pred.with_suffix('.receipt.json'))
    a.out.mkdir(parents=True, exist_ok=True)
    expected = {'ctrl_s0','add_s0','add_corr_s0'} if a.smoke else set(sum(JOBS.values(), []))
    def seed_summary(values):
        finite = [v for v in values.values() if v is not None]
        return dict(seeds=values, n_seeds=len(values), complete=set(values) == {'0','1','2'},
            mean=sum(finite)/len(finite) if finite else None, min=min(finite) if finite else None,
            max=max(finite) if finite else None, range=max(finite)-min(finite) if finite else None)
    obj = dict(schema='e4-wave2-report-v1', mode=common['mode'], control='retrain', identity=common,
        complete=set(roots) == expected, missing=sorted(expected-set(roots)), results=results,
        aggregate={i:{c:seed_summary(v) for c,v in groups.items()} for i,groups in overall_values.items()},
        class_aggregate={i:{c:{cls:seed_summary(v) for cls,v in classes.items()} for c,classes in groups.items()}
                         for i,groups in class_values.items()},
        verdicts={view:verdict(slices[view].get('ctrl',{}), slices[view].get('add',{}), slices[view].get('add_corr',{}), common['corrected_classes'], mode=common['mode']) for view in ('v2_test','v2_test_full_coverage')},
        sources=sources, metric='strict literal NFD codepoint CER',
        primary='v2_test_full_coverage; original references, paired changed-label slice also reported')
    if read_json(a.inputs).get('benchmark_0_2'):
        obj['benchmark_0_2'] = {}
        for run, root in roots.items():
            obj['benchmark_0_2'][run] = {name: read_json(root/'predictions'/(run+'_'+name+'.score.json'))
                for name in ('benchmark_v02_test','benchmark_v02_dev')}
    atomic_json(a.out/'report.json', obj)
    (a.out/'REPORT.md').write_text('# E4 wave 2 / H7\n\n'+obj['mode']+'\n\n'+json.dumps(obj['verdicts'],ensure_ascii=False)+'\n\nCustody: completed checkpoints, prediction/checkpoint identity, prediction files, crops, immutable code/data/label bindings and equal evaluation populations are hash checked. Original references remain visible; the changed-label slice scores the identical predictions twice.\n')
    return obj


def worker(a, gpu):
    node = verify(a)
    for arm in node['arms']:
        if arm['run'] not in a.runs.split(','): continue
        e3.run_arm(a, arm, gpu); evaluate_arm(a, arm)


def run_stage(a):
    if not os.environ.get('SLURM_JOB_ID'): raise ValueError('compute stage requires Slurm')
    node = prepare(a)
    if a.stage == 'inventory': return node
    if a.stage == 'preflight':
        # Exercise the unchanged widest-batch forward/backward/checkpoint path at width x2.
        for arm in node['arms']:
            preflight_worker(a, arm)
        atomic_json(a.out/'PREFLIGHT_DONE.json', dict(state='DONE', mode=node['mode'], inputs=node['inputs']))
    elif a.stage == 'runs':
        gate = a.run_root/'preflight/PREFLIGHT_DONE.json'
        pre = read_json(gate)
        if pre['state'] != 'DONE' or pre['mode'] != node['mode']: raise ValueError('fresh matching preflight required')
        check_files(pre['inputs'])
        groups = [node['arms']] if a.smoke else [[arm] for arm in node['arms']]
        procs = []
        for gpu, arms in enumerate(groups):
            cmd = [sys.executable,'-u','-m','bench.e4_wave2', *a.child_args,
                   '--worker',str(gpu),'--runs',','.join(r['run'] for r in arms)]
            log = (a.out/'logs'/f'worker_{gpu}.log').open('a')
            procs.append((subprocess.Popen(cmd,cwd=ROOT,env=e3.pinned_env(str(gpu)),stdout=log,stderr=log),log))
        failed = []
        for proc, log in procs:
            if proc.wait(): failed.append(proc.returncode)
            log.close()
        if failed: raise ValueError('training/readout worker failed')
        report(a, {r['run']:a.out for r in node['arms']})
    else: raise ValueError('unknown compute stage')
    outputs = files_binding([p for p in a.out.rglob('*') if p.is_file() and p.name not in ('SMOKE_DONE.json','COMPLETE.json') and 'logs' not in p.parts])
    atomic_json(a.out/('SMOKE_DONE.json' if a.smoke else 'COMPLETE.json'),dict(state='DONE', mode=node['mode'],
        job_id=os.environ['SLURM_JOB_ID'], job=a.job, node_binding_sha256=sha256(a.out/'node_binding.json'), outputs=outputs))


def aggregate(a):
    roots, failures = {}, {}
    for job in (['job01'] if a.smoke else JOBS):
        root = a.run_root/job; marker = root/('SMOKE_DONE.json' if a.smoke else 'COMPLETE.json')
        if not marker.exists(): failures[job] = 'missing completion receipt'; continue
        done = read_json(marker)
        if done['state'] != 'DONE' or done['mode'] != ('SMOKE' if a.smoke else 'PRODUCTION') or done['node_binding_sha256'] != sha256(root/'node_binding.json'):
            raise ValueError('aggregate completion mismatch')
        check_files(done['outputs'])
        for arm in read_json(root/'arms.json'):
            if arm['run'] in roots: raise ValueError('duplicate aggregate run')
            roots[arm['run']] = root
    a.out.mkdir(parents=True,exist_ok=True)
    if roots:
        result=report(a, roots)
    else:
        result=dict(complete=False,mode='SMOKE' if a.smoke else 'PRODUCTION',verdicts={'campaign':dict(add='H7_PENDING_NO_RUNS',add_corr='H7_PENDING_NO_RUNS')})
        atomic_json(a.out/'report.json',result)
        (a.out/'REPORT.md').write_text('E4 wave 2: no complete runs; H7 pending.\n')
    atomic_json(a.out/'aggregate_status.json',dict(state='DONE' if result['complete'] and not failures else 'PARTIAL', failures=failures))
    if a.smoke and (failures or not result['complete']): raise ValueError('incomplete smoke aggregate')
    atomic_json(a.out/('SMOKE_DONE.json' if a.smoke else 'E4_AGGREGATE_COMPLETE.json'),dict(state='DONE' if result['complete'] and not failures else 'PARTIAL',
        mode='SMOKE' if a.smoke else 'PRODUCTION', job_id=os.environ.get('SLURM_JOB_ID'),job='aggregate',
        outputs=files_binding([a.out/'report.json',a.out/'REPORT.md',a.out/'aggregate_status.json'])))



def preflight_worker(a, arm):
    """Native widest-batch update, CTC feasibility and inference roundtrip."""
    import torch
    from bench.e4_width_probe import training_runtime
    from train.data import ManifestDataset,make_loader,collate_strips
    from train.model import build_model,masked_forward,amp_dtype_for,autocast_ctx,count_params
    from bench.e1_eval import inference_checkpoint
    from train.eval_cer import load_checkpoint
    trainer=training_runtime(); trainer.set_seeds(0); torch.set_num_threads(8)
    p=arm['parameters'];mix=validate(p['mix']);pools=load_rows(mix,'train')
    drawn,counts=assemble(pools,[c['fraction'] for c in mix['components']],mix['seed'],1,p['epoch_rows'],
        exact_rows=True,recovery=mix.get('codec_recovery'))
    infeasible=[r['line_id'] for r in drawn if (r['width']+3)//4 < len(r['label_ids'])+sum(x==y for x,y in zip(r['label_ids'],r['label_ids'][1:]))]
    if infeasible:raise ValueError('CTC-infeasible admitted rows: '+str(infeasible[:20]))
    model,codec=build_model(codec_path=CODEC,width_mult=2.,verbose=False);model.cuda().train()
    ds=ManifestDataset(drawn,codec.version,codec.n_classes-1,'train')
    _,sampler=make_loader(ds,64,seed=mix['seed'],shuffle=True,num_workers=0,pin_memory=True,pack_bucket_tails=True)
    sampler.set_epoch(1);widest=max(iter(sampler),key=lambda b:len(b)*max(drawn[i]['width'] for i in b))
    batch=collate_strips([ds[i] for i in widest]);lens=batch['input_lengths'].cuda()
    opt=torch.optim.AdamW(trainer.no_decay_param_groups(model,.05),lr=1e-4,weight_decay=.05)
    torch.cuda.reset_peak_memory_stats()
    with autocast_ctx(torch.device('cuda'),amp_dtype_for(torch.device('cuda'))):output=masked_forward(model,batch['images'].cuda(),lens)
    loss=torch.nn.CTCLoss(blank=0,zero_infinity=False)(output.float().transpose(0,1),batch['targets'].cuda(),lens,batch['target_lengths'].cuda())
    if not torch.isfinite(loss):raise ValueError('nonfinite CTC preflight')
    loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),trainer.GRAD_CLIP);opt.step()
    folder=a.out/'preflight';folder.mkdir(exist_ok=True);temp=folder/f"{arm['run']}.pt"
    torch.save(inference_checkpoint(dict(model=model.state_dict(),arch='compact',head='nfd',codec_version=codec.version,
        n_classes=codec.n_classes,width_mult=2.)),temp)
    restored,_=load_checkpoint(str(temp),codec,torch.device('cpu'))
    if count_params(restored)!=count_params(model):raise ValueError('inference roundtrip mismatch')
    temp.unlink()
    atomic_json(folder/f"{arm['run']}.json",dict(state='DONE',steps=1,loss=loss.item(),parameters=count_params(model),
        component_draws=counts,batch_shape=list(batch['images'].shape),max_memory_allocated=torch.cuda.max_memory_allocated(),
        ctc_feasible=True,inference_roundtrip='DONE',job_id=os.environ['SLURM_JOB_ID']))


def mock(a):
    """All real W1 metadata, fixture control and synthetic pixels, no model run."""
    gate=standard_admission(a)
    gate.require_coverage([a.release_rows])
    rows,receipt=admission_union([dict(path=str(a.release_rows),sha256=a.sha,rows=30114 if a.sha==W1_SHA else None,crops_root=str(a.crops))])
    rows=gate.filter(rows)
    accepted,rejected=encode_admissions(rows)
    out=a.out;out.mkdir(parents=True,exist_ok=True)
    plan=upload_plan(rows,out/'upload')
    ids=labels.encode('α',CODEC)[1]
    def fixture(ident, wave):
        return dict(line_id=ident,text='α',gt_nfd='α',label_ids=ids,image_png=b'MOCK_ONLY',width=64,
            script_class='greek_poly',source_dataset='fixture',wave=wave,codec_version='v2.1',split='train')
    old=[[fixture(f'mock-old-{i}','parliament' if i<2 else 'mock-old') for i in range(10)],
         [fixture(f'mock-synthetic-{i}','synthetic') for i in range(10)]]
    old[0]=gate.filter(old[0])
    oldcomp=[dict(kind='real',fraction=.5),dict(kind='synthetic',fraction=.5)]
    new=[dict(r,image_png=b'MOCK_ONLY',width=64) for r in accepted]
    groups,comps,policy=natural_pools(merge_real(old[0],new),[old[1]],[oldcomp[1]])
    # A fixture overlay exercises exact IDs on BOTH old and new rows. Never registered for production.
    selected=[old[0][0]['line_id'],*[r['line_id'] for r in new[:49]]]
    reg=out/'labels/VERSIONS.json';version=reg.parent/'synthetic50.jsonl'
    write_rows(version,[dict(row_id=i,text='β',provenance=dict(source='MOCK_ONLY')) for i in selected])
    atomic_json(reg,dict(schema='lqb-versions-v1',versions=dict(synthetic50=dict(path=version.name,sha256=sha256(version),
        population=dict(rows=len(selected)),parent=None,text_field='text',id_field='row_id',status='mock',read='test fixture only'))))
    spec=labels.overlay_spec(reg,['synthetic50'],CODEC,production=False)
    fixed,sub=labels.substitute(groups,comps,spec)
    contract=labels.draw_contract(groups,fixed,dict(components=comps,seed=20261015),out/'draws',rows=100,epochs=8)
    table=mix_table(old,groups,oldcomp,comps,20261015,out,rows=100,epochs=8)
    table['standard_admission']=gate.receipt(len(old[0]))
    atomic_json(out/'MIX_TABLE.json',table)
    atomic_json(out/'admission_receipt.json',dict(**receipt,standard_admission=table['standard_admission'],accepted=len(accepted),codec_rejections=rejected))
    atomic_json(out/'mock.json',dict(mode='MOCK_ONLY',admitted_rows_bound=len(rows),codec_accepted=len(accepted),
        codec_rejected=len(rejected),policy=policy,upload=plan,substitution=sub,contract=contract,
        control='fixture ten old rows, not v_c',new_crop_pixels='unavailable; expected crop SHA only',
        verdicts=verdict({}, {}, {}, [],mode='MOCK')))
    print('E4_WAVE2_MOCK',len(rows),'admitted;',len(accepted),'codec accepted;',len(rejected),'codec rejected')


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mock',action='store_true');ap.add_argument('--smoke',action='store_true');ap.add_argument('--upload-plan',action='store_true')
    ap.add_argument('--stage',choices=('inventory','prepare','preflight','runs','aggregate'),default='prepare')
    ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--out',type=Path)
    ap.add_argument('--run-root',type=Path);ap.add_argument('--prep',type=Path);ap.add_argument('--campaign',type=Path)
    ap.add_argument('--inputs',type=Path,default=ROOT/'out/e4/wave2_prep/INPUTS.json')
    ap.add_argument('--factory',type=Path,default=ROOT/'factory/target/release/linefactory')
    ap.add_argument('--registry',type=Path,default=ROOT/'labels/VERSIONS.json')
    ap.add_argument('--job',choices=('preflight',*JOBS,'aggregate'),default='preflight')
    ap.add_argument('--worker');ap.add_argument('--runs')
    ap.add_argument('--admission',type=Path,action='append',help='standard per-row decisions; repeat with matching receipts')
    ap.add_argument('--admission-receipt',type=Path,action='append')
    ap.add_argument('--admission-tool',type=Path,default=ADMISSION_TOOL,help='local greekocr.harvest.admission source for tool_sha256 validation')
    ap.add_argument('--admission-mock-bind',type=Path,help='offline JSONL of proposed real rows; strict gate only, no factory/model')
    ap.add_argument('--release-rows',type=Path,default=W1);ap.add_argument('--sha',default=W1_SHA);ap.add_argument('--crops',type=Path,default=CROPS)
    a=ap.parse_args(argv)
    if len(a.admission or []) != len(a.admission_receipt or []):
        raise ValueError('one --admission-receipt required per --admission')
    for key in ('root','inputs','factory','registry'):setattr(a,key,getattr(a,key).resolve())
    a.run_root=(a.run_root or ROOT/('out/e4/wave2_smoke' if a.smoke else 'out/e4/wave2')).resolve()
    a.out=(a.out or a.run_root/a.job).resolve();a.prep=(a.prep or ROOT/'out/e3').resolve();a.campaign=(a.campaign or ROOT/'out/e4/wave1b').resolve()
    if a.admission_mock_bind:
        gate=standard_admission(a)
        proposed=list(read_rows(a.admission_mock_bind))
        gate.require_pass(proposed)
        a.out.mkdir(parents=True,exist_ok=True)
        atomic_json(a.out/'MOCK_BIND.json',dict(mode='MOCK_ONLY',bound_rows=len(proposed),standard_admission=gate.receipt(len(proposed))))
        return
    if a.upload_plan:
        rows,_=admission_union([dict(path=str(a.release_rows),sha256=a.sha,crops_root=str(a.crops))])
        return upload_plan(rows,a.out,require_present=True)
    if a.mock:return mock(a)
    if a.root!=ROOT:raise ValueError('E4_ROOT differs from executable source root')
    a.child_args=['--root',str(ROOT),'--inputs',str(a.inputs),'--factory',str(a.factory),'--registry',str(a.registry),
        '--run-root',str(a.run_root),'--out',str(a.out),'--prep',str(a.prep),'--campaign',str(a.campaign),'--job',a.job,'--stage',a.stage]
    for decision,receipt in zip(a.admission or [],a.admission_receipt or []):
        a.child_args+=['--admission',str(decision.resolve()),'--admission-receipt',str(receipt.resolve())]
    if a.admission_tool:a.child_args+=['--admission-tool',str(a.admission_tool.resolve())]
    if a.smoke:a.child_args+=['--smoke']
    if a.worker is not None:return worker(a,a.worker)
    if a.stage=='aggregate':return aggregate(a)
    if a.stage=='prepare':return prepare(a)
    return run_stage(a)

if __name__=='__main__':main()
