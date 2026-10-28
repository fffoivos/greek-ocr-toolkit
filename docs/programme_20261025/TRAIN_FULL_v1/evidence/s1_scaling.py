"""S1 SCALE1 custody and preparation. No deployment or submission side effects."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import unicodedata

from bench.e1_common import ROOT, atomic_json, read_json, sha256
from bench.common import read_rows
from bench.e4_wave2_r3 import bound, Census05Admission, exposure, sealed_rows, seal_receipt

DOC = ROOT/'docs/ocr_program_2026-10-06/s1_scaling'
W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
EXPORT = W/'scaling_w3/mix1_runs/MIX1D-8d25940f-export-001'
SIZES = {'ref_208k':208000, 'ref_364871':364871, 'tgt_208k':208000}
WIDTHS = (1.,1.5,2.)
D = 428872
SUBSETS_SHA = '467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2'
EXPORT_SHA = '965fae30022b38fd285b624676f3b64819d6173c5a03c1fb3cb1595afcb242ed'
SEVEN_ROWS_SHA256 = '1cfedda4882bc1776b06b066b04c76c8931c9030640ead84ab731926ef128a3a'
SEAL_SHA = '9447f09c6073028c1085996e1663232a18ac70ef8b81eda4be5c232a4025b924'


def digest_json(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def load_subset(spec, *, stream=False):
    """Hash-bound SCALE1 rows; exhaust stream=True to prove count and uniqueness.

    Identity is the opaque (parent_id, row_id) pair, not a line-ID spelling.
    SCALE1 reference prefixes retain unclassified rows with primary_class=null;
    the targeted allocation excludes them (SUBSETS_RECEIPT / subsets_plan).
    """
    path = bound(spec)
    def checked_rows():
        seen = set()
        for number, r in enumerate(read_rows(path), 1):
            context = f'{path}:{number}'
            if (not isinstance(r, dict) or
                any(not isinstance(r.get(k), str) or not r[k]
                    for k in ('parent_id', 'row_id', 'source')) or
                r.get('key') != [r.get('parent_id'), r.get('row_id')]):
                raise ValueError('SUBSET_ROW_IDENTITY: '+context)
            if r['row_id'] in seen:
                raise ValueError('SUBSET_ROW_IDENTITY: duplicate row_id: '+context)
            if (not isinstance(r.get('label'), str) or 'primary_class' not in r or
                (r['primary_class'] is not None and
                 (not isinstance(r['primary_class'], str) or not r['primary_class'])) or
                not isinstance(r.get('crop_path'), str) or not Path(r['crop_path']).is_absolute() or
                not isinstance(r.get('crop_sha256'), str) or len(r['crop_sha256']) != 64 or
                any(c not in '0123456789abcdefABCDEF' for c in r['crop_sha256'])):
                raise ValueError('SUBSET_ROW_SCHEMA: '+context)
            seen.add(r['row_id'])
            yield r
        if len(seen) != spec['rows']:
            raise ValueError('SUBSET_COUNT: '+str(path))
    return checked_rows() if stream else list(checked_rows())


def select_rows(groups, components, selection):
    """Select by exact subset IDs in shared shards; preserve all stored labels/pixels."""
    from train.cer import load_codec
    subset = load_subset(selection['subset'])
    provenance=read_json(bound(selection['provenance']))
    by_id = {r['row_id']:r for r in subset}
    decode = load_codec(str(ROOT/'codec/v2.1.json')).decode
    seen, result = set(), []
    label_diffs = 0
    for pool,c in zip(groups,components):
        if c['kind'] != 'real': result.append(pool); continue
        chosen=[]
        for r in pool:
            ident=r['line_id']
            if ident not in by_id: continue
            s=by_id[ident]
            parliament=s['source']=='parliament_proceedings_1975_2000'
            if c['source'] != ('parliament' if parliament else 'non_parliament'): continue
            if ident in seen: raise ValueError('SHARED_DUPLICATE_ID')
            seen.add(ident)
            if r['source_doc_id'] != provenance[ident]['edition_id'] or r['source_dataset'] != s['source']:
                raise ValueError('SHARED_SOURCE_MISMATCH')
            if provenance[ident]['crop_sha256'] != s['crop_sha256']: raise ValueError('SHARED_CROP_MISMATCH')
            label_diffs += unicodedata.normalize('NFD',decode(r['label_ids'])) != unicodedata.normalize('NFD',s['label'])
            chosen.append(dict(r,parent_id=s['parent_id'],row_id=ident,source=s['source'],
                edition_id=r['source_doc_id'],crop_sha256=s['crop_sha256'],primary_class=s['primary_class'],wave='parliament' if parliament else r.get('wave','unknown')))
        result.append(chosen)
    if seen != set(by_id): raise ValueError('SHARED_MEMBERSHIP_MISMATCH')
    if label_diffs: raise ValueError('SHARED_LABEL_DIFFS:'+str(label_diffs))
    return result


def normalise_row_id(row, form):
    """Exact opaque IDs: SCALE1=(parent_id,row_id,key=[parent,row]);
    inventory03=(parent_id,row_id), no key/line_id; shared records=id and
    Parquet=line_id (no parent). Never strip prefixes, split dashes, or derive
    a parent from an ID. Parent identity is checked against SCALE1 at the join.
    If aliases coexist they must agree, rather than silently choosing one.
    """
    fields = {'subset': 'row_id', 'inventory': 'row_id', 'shared': 'line_id' if 'line_id' in row else 'id'}
    if form not in fields:
        raise ValueError('S1_ID_FORM')
    ident = row.get(fields[form])
    if not isinstance(ident, str) or not ident:
        raise ValueError('S1_ID_MISSING:'+form)
    if any(row[k] != ident for k in ('row_id', 'line_id', 'id') if k in row):
        raise ValueError('S1_ID_ALIAS_CONFLICT:'+form)
    if form in ('subset', 'inventory'):
        if not isinstance(row.get('parent_id'), str) or not row['parent_id']:
            raise ValueError('S1_ID_PARENT:'+form)
    if 'key' in row and row['key'] != [row.get('parent_id'), ident]:
        raise ValueError('S1_ID_KEY:'+form)
    if form == 'subset' and 'key' not in row:
        raise ValueError('S1_ID_KEY:subset')
    return ident


def reconcile_seven_rows(rows, oldids, *, expected_old=364864):
    """Streaming join; inventory records or legacy caller's opaque ID strings.

    Only compact identity/source/class metadata is retained, never images or
    full population rows. Production counts are fixed; fixtures opt into their
    smaller predecessor size. Duplicate IDs and wrong parents are fatal.
    """
    byid = {}
    for r in rows:
        ident = normalise_row_id(r, 'subset')
        if ident in byid: raise ValueError('S1_SEVEN_ROW_RECONCILIATION: duplicate subset')
        byid[ident] = (r['parent_id'], r['source'], r['primary_class'])
    old = set()
    for r in oldids:
        ident = r if isinstance(r, str) else normalise_row_id(r, 'inventory')
        if ident in old: raise ValueError('S1_SEVEN_ROW_RECONCILIATION: duplicate predecessor')
        if ident not in byid or (not isinstance(r, str) and r['parent_id'] != byid[ident][0]):
            raise ValueError('S1_SEVEN_ROW_RECONCILIATION: predecessor outside/parent')
        old.add(ident)
    extra = set(byid) - old
    if len(old) != expected_old or len(byid) != expected_old+7 or len(extra) != 7:
        raise ValueError('S1_SEVEN_ROW_RECONCILIATION: counts')
    return [dict(row_id=k, source=byid[k][1], primary_class=byid[k][2],
                 cause='census_05 ADMIT intersection train absent from v_c pools') for k in sorted(extra)]


def seven_rows_bytes(additions):
    """Canonical receipt bytes, identical on login and compute nodes."""
    return (json.dumps(additions, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')


def reconcile_population(cfg, *, expected_old=364864):
    """Read-only login-safe production join, all bound JSONL and Parquet IDs.

    No train.mix.load_rows (which materializes images). Parquet scans only the
    line_id/source_dataset columns. Full shard byte hashes remain the compute
    population validator's responsibility; this proves actual ID membership.
    """
    import pyarrow.parquet as pq
    predecessor = read_json(DOC/'record/WAVE2_INPUTS.json')['training_inventories']['add']
    subset = cfg['subsets']['ref_364871']
    # Keep parent/source/class only, then feed the exact same reconciler.
    universe = {}
    for r in load_subset(subset, stream=True):
        ident = normalise_row_id(r, 'subset')
        universe[ident] = dict(parent_id=r['parent_id'], row_id=ident, key=r['key'],
                              source=r['source'], primary_class=r['primary_class'])
    old = list()  # IDs and parents only; no crops, text or image bytes.
    for r in read_rows(bound(predecessor)):
        old.append(dict(row_id=normalise_row_id(r, 'inventory'), parent_id=r['parent_id']))
    additions = reconcile_seven_rows(iter(universe.values()), iter(old), expected_old=expected_old)
    def shared_ids(rows):
        seen = set()
        for r in rows:
            ident = normalise_row_id(r, 'shared')
            if ident in seen: raise ValueError('S1_SHARED_ID_DUPLICATE')
            if ident not in universe or r['source_dataset'] != universe[ident]['source']:
                raise ValueError('S1_SHARED_ID_SOURCE_MISMATCH')
            seen.add(ident)
        if seen != set(universe): raise ValueError('S1_SHARED_ID_MEMBERSHIP')
        return seen
    records = shared_ids(read_rows(bound(cfg['shared_records'])))
    mix = read_json(bound(cfg['shared_mix']))
    def shard_rows():
        for component in mix['components']:
            if component['kind'] != 'real': raise ValueError('S1_SHARED_COMPONENT')
            if component['shard_sha256'] != cfg['shared_binding']['shard_sha256']:
                raise ValueError('S1_SHARED_SHARD_BINDING')
            for name in sorted(component['shard_sha256']):
                if not name.startswith('train/'): raise ValueError('S1_SHARED_SPLIT')
                path = Path(component['shard_dir'])/name
                for batch in pq.ParquetFile(path).iter_batches(batch_size=8192, columns=['line_id','source_dataset']):
                    yield from batch.to_pylist()
    shards = shared_ids(shard_rows())
    digest = lambda ids: hashlib.sha256(('\n'.join(sorted(ids))+'\n').encode()).hexdigest()
    return dict(predecessor=predecessor, predecessor_rows=len(old), predecessor_ids=len(old),
                predecessor_idset_sha256=digest(r['row_id'] for r in old),
                current_ids=len(universe), shared_record_ids=len(records), shared_shard_ids=len(shards),
                current_idset_sha256=digest(universe), additions=additions,
                additions_sha256=hashlib.sha256(seven_rows_bytes(additions)).hexdigest(),
                subset=subset, shared_records=cfg['shared_records'], shared_mix=cfg['shared_mix'])


def verify_seven_rows(cfg):
    """Every deploy and job must reproduce the login-pinned bytes exactly."""
    result = reconcile_population(cfg)
    path = DOC/'record/SEVEN_ROWS.json'
    expected = bound(dict(path=str(path), sha256=SEVEN_ROWS_SHA256)).read_bytes()
    if seven_rows_bytes(result['additions']) != expected:
        raise ValueError('S1_SEVEN_ROWS_PIN_MISMATCH')
    result['pinned'] = spec(path)
    return result


def build_cache(census, target):
    """Only preflight builds the cache, using the unchanged Census05Admission."""
    for source in census.values(): bound(source)
    gate=Census05Admission(census)
    entries={k:[v['parent_id'],v['crop_sha256']] for k,v in gate.rows.items() if v['pass']}
    obj=dict(schema='s1-census-cache-v1',sources=census,admitted=entries)
    if Path(target).exists(): raise ValueError('CACHE_ALREADY_EXISTS')
    atomic_json(target,obj)
    return dict(path=str(Path(target).resolve()),sha256=sha256(target),sources=census)


def require_cache(spec, census, rows):
    """Bind the once-verified large sources by their immutable hashes, not re-scans.

    Jobs verify cache bytes and compare the full source-spec identities. Small
    current/summary files are rehashed to detect a changed live generation.
    """
    obj=read_json(bound(spec))
    if obj['schema']!='s1-census-cache-v1' or obj['sources']!=census or spec['sources']!=census:
        raise ValueError('CACHE_SOURCE_MISMATCH')
    for name in ('current','summary'): bound(census[name])
    for r in rows:
        if obj['admitted'].get(r['row_id']) != [r['parent_id'],r['crop_sha256']]:
            raise ValueError('CACHE_ADMISSION_MISMATCH')
    return obj


def index_header(groups, components, pool_shas, *, seed, rows=D, epochs=8):
    if len(groups)!=len(components) or len(pool_shas)!=len(groups): raise ValueError('INDEX_POOL_COUNT')
    return dict(schema='s1-index-v1',pool_shas=pool_shas,component_map=components,D=rows,epochs=epochs,
        seed_provenance=dict(data_seed=seed,model_seed_independent=True))


def read_index(path, groups, expected, *, legacy_header=None):
    """Separate opt-in reader; never called by S1 arms. Legacy header is hash-bound.

    draw_contract writes bare tuples; a sidecar binds those exact gzip bytes and
    supplies their header without modifying the original index file.
    """
    if legacy_header is not None:
        side=read_json(bound(legacy_header))
        if side['index_sha256']!=sha256(path): raise ValueError('INDEX_BYTES_CHANGED')
        header=side['header']
    with gzip.open(path,'rt',encoding='utf-8') as stream:
        if legacy_header is None:
            first=next(stream,None)
            if first is None:raise ValueError('INDEX_MISSING_HEADER')
            header=json.loads(first)
        if header!=expected: raise ValueError('INDEX_HEADER_MISMATCH')
        if (header.get('schema')!='s1-index-v1' or any(type(header.get(k)) is not int or header[k]<=0 for k in ('D','epochs'))
            or len(header['pool_shas'])!=len(groups)
            or any(not isinstance(v,str) or len(v)!=64 or any(ch not in '0123456789abcdef' for ch in v) for v in header['pool_shas'])):
            raise ValueError('INDEX_HEADER_SCHEMA')
        if len(groups)!=len(header['component_map']): raise ValueError('INDEX_COMPONENT_MAP')
        count=0
        for line in stream:
            row=json.loads(line)
            if not isinstance(row,list) or len(row)!=5: raise ValueError('INDEX_TUPLE')
            epoch,pos,component,index,ident=row
            if any(type(x) is not int for x in (epoch,pos,component,index)):
                raise ValueError('INDEX_INTEGER')
            if (epoch,pos)!= (count//header['D']+1,count%header['D']): raise ValueError('INDEX_POSITION')
            if not 0<=component<len(groups) or not 0<=index<len(groups[component]): raise ValueError('INDEX_POOL_INDEX')
            r=groups[component][index]
            if r['line_id']!=ident: raise ValueError('INDEX_LINE_ID')
            count+=1
            if epoch>header['epochs']: raise ValueError('INDEX_EPOCH_COUNT')
            yield dict(r,_component=component,_pool_index=index)
        if count!=header['D']*header['epochs']: raise ValueError('INDEX_DRAW_COUNT')


def compare(control, candidate):
    """H7-style strict rational mean gain beyond the control's three-seed range."""
    def vals(data):
        if set(data)!={'0','1','2'}: raise ValueError('S1_MISSING_SEEDS')
        out=[]
        for v in data.values():
            if type(v['edits']) is not int or v['edits']<0 or type(v['ref_len']) is not int or v['ref_len']<=0:
                raise ValueError('S1_EMPTY_OR_INVALID_SUPPORT')
            out.append(Fraction(v['edits'],v['ref_len']))
        return out
    a,b=vals(control),vals(candidate)
    gain=(sum(a)-sum(b))/3; span=max(a)-min(a)
    rational=lambda x:dict(numerator=x.numerator,denominator=x.denominator)
    return dict(confirmed=gain>span,gain=rational(gain),control_range=rational(span),
        floor='NOT_IDENTIFIABLE: one sub-doubling; two consecutive doublings and qualified bootstrap required')


DROPPED_CELL = 'w2_tgt_208k'


def active_cells():
    return [(w,u) for w in WIDTHS for u in SIZES if f'w{w:g}_{u}' != DROPPED_CELL]


def budget():
    from bench.s1_limits import segment_plans
    from scripts.ops.s1_production_adapter import policy_adoption
    policy=policy_adoption(ROOT)
    plans=segment_plans();cells=[]
    for width,subset in active_cells():
        name=f'w{width:g}_{subset}';plan=plans[name];seconds=plan['estimate_seconds']
        reservation=sum(x['limit_seconds'] for x in plans[name]['segments'])
        cells.append(dict(cell=name,series='A' if width<2 else 'B',width=width,subset=subset,seeds=3,seconds=seconds,
            requested_gpu_h=3*seconds/3600,node_charged_gpu_h=4*seconds/3600,
            reserved_requested_gpu_h=3*reservation/3600,reserved_node_gpu_h=4*reservation/3600,
            training_limit_seconds=plan['segments'][0]['limit_seconds'],limit_capped=len(plan['segments'])>1))
    series={k:{field:sum(c[field] for c in cells if c['series']==k) for field in
        ('requested_gpu_h','node_charged_gpu_h','reserved_requested_gpu_h','reserved_node_gpu_h')} for k in ('A','B')}
    return dict(cells=cells,series=series,requested_gpu_h=sum(c['requested_gpu_h'] for c in cells),
        node_charged_gpu_h=sum(c['node_charged_gpu_h'] for c in cells),
        wave_cap=policy['wave_cap_gpu_h'],series_cap=policy['series_cap_gpu_h'],
        accounting_basis='requested GPU elapsed time; recovered 3714223 measurements; owner 350 wave, no series caps',
        status='MEASURED_HEAVIEST_PROFILE_BOUND_NOT_CP4B',amendment='S1-O',dropped_cell=DROPPED_CELL,
        excludes='preflight/smoke/aggregate and prior consumption; CP4B accounting still required')


def spec(path):
    return dict(path=str(Path(path).resolve()),sha256=sha256(path))


def metadata_bind(out):
    """Light metadata only. Full input verification is an explicit compute stage."""
    sr=read_json(DOC/'record/SUBSETS_RECEIPT.json');er=read_json(DOC/'record/EXPORT_RECEIPT.json')
    if sha256(DOC/'record/SUBSETS_RECEIPT.json')!=SUBSETS_SHA or sha256(DOC/'record/EXPORT_RECEIPT.json')!=EXPORT_SHA:
        raise ValueError('RECEIPT_BYTES_CHANGED')
    old=read_json(DOC/'record/WAVE2_INPUTS.json')
    cfg=dict(policy=dict(path='docs/ocr_program_2026-10-06/s1_scaling/POLICY.json',sha256=sha256(DOC/'POLICY.json')),runtime=read_json(DOC/'record/RUNTIME.json'),schema='s1-inputs-v1',status='METADATA_BOUND_COMPUTE_VALIDATION_REQUIRED',
        subsets_receipt=dict(path=str(W/'scaling_w3/subsets/scale1-c05-003/SUBSETS_RECEIPT.json'),sha256=SUBSETS_SHA),
        export_receipt=dict(path=str(EXPORT/'EXPORT_RECEIPT.json'),sha256=EXPORT_SHA),
        subsets={k:dict(v['output'],rows=v['rows']) for k,v in sr['subsets'].items()},
        shared_mix=dict(path=str(EXPORT/'shared/real_mix.json'),sha256=sha256(DOC/'record/SHARED_MIX.json')),
        shared_build_info=dict(path=str(EXPORT/'shared/real/build_info.json'),sha256=read_json(DOC/'record/SHARED_BUILD_INFO.json')['source_sha256']),
        shared_records=dict(path=str(EXPORT/'shared/records.jsonl'),sha256=read_json(DOC/'record/SHARED_BUILD_INFO.json')['records_sha256']),
        shared_binding=er['shared_real']['binding'],physical_index=dict(path=str(EXPORT/'shared/REF_PHYSICAL_INDEX.json'),
            sha256=er['shared_real']['physical_map_sha256']),
        benchmark_0_2=dict(path=str(W/'benchmark_0.2/seal04/suite.json'),sha256=SEAL_SHA,
            seal_receipt=dict(path=str(W/'benchmark_0.2/seal04/SEAL_RECEIPT.json'),sha256=sha256(DOC/'record/SEAL04_RECEIPT.json')),
            panels=read_json(DOC/'record/SEAL04_SUITE.json')['panels']),
        synthetic=dict(path=str(EXPORT/'prep/A12'),build_info_sha256=er['derivatives']['A12']['build_info_sha256'],
            shard_inventory_sha256=er['A12_crosscheck']['shard_inventory_sha256']['own']),
        **{k:old[k] for k in ('census05','split2','editions','heldout_editions','protected_crops',
            'benchmark_scorer_binding','benchmark_scorer_root')})
    atomic_json(out,cfg)
    return cfg


def validate_inputs(cfg, cache, *, full=True):
    """All a-e must be proved here through this branch before preparing any arm."""
    if not full: raise ValueError('FULL_COMPUTE_PROOF_REQUIRED')
    from bench.s1_jobs import compute_only
    compute_only(cpu_prepare=True)
    from train.mix import validate, load_rows, shard_inventory
    bound(cfg['policy'])
    from train.cer import load_codec
    bound(cfg['subsets_receipt']);er=read_json(bound(cfg['export_receipt']))
    if cfg['subsets_receipt']['sha256']!=SUBSETS_SHA or cfg['export_receipt']['sha256']!=EXPORT_SHA:
        raise ValueError('S1_PIN_CHANGED')
    shared_mix=validate(bound(cfg['shared_mix']))
    if shared_mix['components'][0]['shard_sha256']!=cfg['shared_binding']['shard_sha256'] or cfg['shared_binding']!=er['shared_real']['binding']:
        raise ValueError('SHARED_SHARD_BINDING')
    pools=load_rows(shared_mix,'train')
    physical=read_json(bound(cfg['physical_index']))
    flattened=[r for pool in pools for r in pool]
    if len(physical)!=len(flattened) or any(flattened[v[1]]['line_id']!=v[2] or v[0][1]!=v[2] for v in physical):
        raise ValueError('SHARED_PHYSICAL_INDEX')
    shared={}
    for pool in pools:
        for r in pool:
            if r['line_id'] in shared: raise ValueError('SHARED_DUPLICATE_ID')
            shared[r['line_id']]=r
    subsets={k:load_subset(v) for k,v in cfg['subsets'].items()}
    if set(shared)!={r['row_id'] for r in subsets['ref_364871']}: raise ValueError('SHARED_UNIVERSE_MISMATCH')
    decode=load_codec(str(ROOT/'codec/v2.1.json')).decode
    info=read_json(bound(cfg['shared_build_info']))
    if info['shard_sha256']!=cfg['shared_binding']['shard_sha256'] or info['records_sha256']!=cfg['shared_records']['sha256']:
        raise ValueError('SHARED_BUILD_INFO_BINDING')
    provenance={}
    universe={r['row_id']:r for r in subsets['ref_364871']}
    for ident,r in universe.items():
        if info['crop_sha256'].get(ident)!=r['crop_sha256']:
            raise ValueError('SHARED_ORIGINAL_CROP_MISMATCH')
        provenance[ident]=dict(crop_sha256=info['crop_sha256'][ident],edition_id=shared[ident]['source_doc_id'])
    if set(info['crop_sha256'])!=set(shared): raise ValueError('SHARED_CROP_MEMBERSHIP')
    diffs=0
    for rows in subsets.values():
        require_cache(cache,cfg['census05'],rows)
        for r in rows:
            if r['row_id'] not in shared: raise ValueError('SUBSET_OUTSIDE_SHARED')
            x=shared[r['row_id']]
            if provenance[r['row_id']]['crop_sha256']!=r['crop_sha256']: raise ValueError('SHARED_CROP_MISMATCH')
            diffs+=unicodedata.normalize('NFD',decode(x['label_ids']))!=unicodedata.normalize('NFD',r['label'])
    if diffs: raise ValueError('SHARED_LABEL_DIFFS:'+str(diffs))
    if not {r['row_id'] for r in subsets['ref_208k']}<set(shared): raise ValueError('SUBSET_NOT_NESTED')
    syn=Path(cfg['synthetic']['path']);info=read_json(syn/'build_info.json')
    cross=er['A12_crosscheck']
    inv=shard_inventory(syn)
    # Match sourcing's insertion-order compact JSON plus newline.
    invsha=hashlib.sha256((json.dumps(inv,ensure_ascii=True,separators=(',',':'))+'\n').encode()).hexdigest()
    if (sha256(syn/'build_info.json')!=cfg['synthetic']['build_info_sha256']
        or inv!=info['shard_sha256'] or invsha!=cfg['synthetic']['shard_inventory_sha256'] or not cross['shard_inventory_equal']
        or cross['own']['sha256']!=cross['other']['sha256']): raise ValueError('SYNTHETIC_PARITY')
    benchmark=cfg['benchmark_0_2']
    if benchmark['sha256']!=SEAL_SHA: raise ValueError('SEAL04_PIN_CHANGED')
    if seal_receipt(benchmark)!=benchmark['seal_receipt']:raise ValueError('SEAL_RECEIPT_BINDING_CHANGED')
    bench,_=sealed_rows(benchmark)
    with gzip.open(bound(cfg['split2']),'rt') as stream:
        holdout={r['edition_id'] for r in map(json.loads,stream) if r['split'] in ('dev','test')}
    protected={r['crop_sha256'] for r in read_rows(bound(cfg['protected_crops']))}
    if not holdout or not protected: raise ValueError('EMPTY_PROTECTED_POPULATION')
    audits={}
    for name,rows in subsets.items():
        real=[dict(r,edition_id=shared[r['row_id']]['source_doc_id']) for r in rows]
        audits[name]=exposure(real,bench,holdout,protected)
        if audits[name]['hits']: raise ValueError('S1_EXPOSURE_FATAL:'+name)
    return dict(checks={k:True for k in 'abcde'},label_diffs=diffs,exposure=audits,
        shared_rows=len(shared),synthetic_inventory_digest_computed=invsha,input_sha256=digest_json(cfg),
        cache_sha256=cache['sha256'],provenance=provenance)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    b=sub.add_parser('bind');b.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('budget')
    r=sub.add_parser('reconcile');r.add_argument('--inputs',type=Path,required=True)
    a=p.parse_args(argv)
    if a.action=='bind': metadata_bind(a.out)
    elif a.action=='reconcile': print(json.dumps(verify_seven_rows(read_json(a.inputs)),sort_keys=True))
    else: print(json.dumps(budget(),indent=2))

if __name__=='__main__': main()
