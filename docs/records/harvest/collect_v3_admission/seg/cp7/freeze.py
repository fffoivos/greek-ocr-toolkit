"""Create-once code/parameter/truth freeze and fresh native witness replay."""
import gzip,os,sys
from cp7_common import *
sys.path.insert(0,str(ROOT))
from greekocr.harvest import geometry_observations as g,admission as a
from greekocr.harvest.neighbour_words import WORD_PROXY
from greekocr.harvest import row_inclusion
ROW_PARAMETERS={k:getattr(row_inclusion,k) for k in dir(row_inclusion) if k.isupper() and isinstance(getattr(row_inclusion,k),(int,float,str))}
from greekocr.harvest.serbian import serbian_extension_sha256, serbian_documents_sha256
from greekocr.harvest.lookalikes import lookalike_table_sha256
from greekocr.harvest.seg_qualification import composed_requirements
from measure import observe,load_page,prepare_separators


def inputs():
    old=read(SEG/'CP5_verification.json');cp4=read(SEG/'CP5_cp4_verification.json')
    ledger=read(SEG/'calibration_ledger.json')
    wanted={c['row_id'] for c in ledger['cases']}|{c['row_id'] for c in ledger['gallery_witnesses'] if c['type']=='rotated_vertical_line'}
    targets={c['row_id']:c.get('observation',{}).get('target_row_id') for c in cp4['cases']}
    records=[]
    for c in old['cases']:
        if c['row_id'] in wanted:
            records.append(dict(id=c['row_id'],crop_bbox=c['crop_bbox'],crop_sha256=c['crop_sha256'],
                crop_source_image=c['source'],crop_source_sha256=c['source_sha256'],
                measured_row_id=targets.get(c['row_id']),source=c['dataset_source'],primary_class=c['primary_class']))
    assert {c['id'] for c in records}==wanted
    return records


def code_paths():
    return sorted(set([* (ROOT/'greekocr/harvest').glob('*.py'),
        *SEG.glob('*.py'),*HERE.glob('*.py'),* (HERE/'launchers').glob('*.sh'),
        HERE/'launch_cp7.sh',* (HERE/'prompts').glob('*.md'),
        *(HERE/'tools').glob('*.py')]))


def verify_freeze():
    f=read(SEG/'CP7_FREEZE.json')
    for path,digest in f['files'].items():assert sha(ROOT/path)==digest,'freeze drift: '+path
    assert f['geometry_implementation']==g.implementation_binding()
    assert sha(SEG/'calibration_ledger.json')==f['ledger_sha256']
    for path,digest in f['geometry_files'].items():assert sha(path)==digest,'geometry drift: '+path
    return f


def create():
    records=inputs();jsonl(HERE/'keys/witness_inputs.jsonl',records)
    for r in records:
        try:page=load_page(r)
        except (OSError,ValueError,KeyError):continue
        prepare_separators(page,r['id'].rsplit('-l',1)[0])
    geometry={}
    for r in records:
        from measure import cache_for
        try:cache=cache_for(r)
        except ValueError:continue
        for p in cache.iterdir():
            if p.is_file():geometry[str(p.resolve())]=sha(p)
    for p in (HERE/'separators').rglob('*.json'):geometry[str(p.resolve())]=sha(p)
    ledger_sha=sha(SEG/'calibration_ledger.json')
    assert ledger_sha=='76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f'
    extra=[SEG/'calibration_ledger.json',SEG/'CP5_verification.json',SEG/'CP5_cp4_verification.json',
        ROOT/'tests/test_seg_cp7.py',HERE/'keys/witness_inputs.jsonl',
        ROOT/'greekocr/labelfix/text.py',ROOT/'greekocr/_vendor/bench/e1_readout.py']
    files={str(p.relative_to(ROOT)):sha(p) for p in code_paths()+extra}
    f=dict(schema='SEG-CP7-freeze-1',files=files,ledger_sha256=ledger_sha,
        geometry_implementation=g.implementation_binding(),geometry_files=geometry,
        ownership_params_sha256=g.frozen(),ownership_parameters=g.foreign_ink.PARAMETERS,word_thresholds=WORD_PROXY,row_thresholds=ROW_PARAMETERS,
        text_thresholds=dict(confidence=.89,height_ratio=1.7,standard_letters=10,heading_letters=4,
            nonletter_fraction='1/3',numeric_min_digits=4,numeric_shape_percent=60),
        serbian_documents_sha256=serbian_documents_sha256(),
        codec_sha256=a.load_codec()['sha256'],serbian_extension_sha256=serbian_extension_sha256(),
        lookalike_table_sha256=lookalike_table_sha256(),expected_table_sha256=a.expected_table_sha256(),
        canonical_scanner_sha256=SCANNER,seed=SEED,
        geometry_policy='No new row detector; existing source/frame/options/payload-bound caches only. Missing/invalid geometry fails closed. Separator preparation reuses frozen pixels/structure with no row refit.',
        orientation_policy='CP5c unknown allowed for orientation only; never a verified KEEP',
        fresh_sampling='ADM4 included, candidate_usable true, W1 union W2; locked/eval and calibration IDs only excluded',
        reading='not launched; Part B pending')
    dump(SEG/'CP7_FREEZE.json',f,exclusive=True)
    return verify_freeze()


def gate():
    verify_freeze();ledger=read(SEG/'calibration_ledger.json');cases=[]
    for n,r in enumerate(inputs()):
        cases.append(observe(r));print(f'witness {n+1}/{len(inputs())}',file=sys.stderr,flush=True)
    by={c['row_id']:c for c in cases};truth={c['row_id']:c['truth'] for c in ledger['cases']}
    checks=composed_requirements(truth,{r:c['composed'] for r,c in by.items()},{r:c['crossing'] for r,c in by.items()})
    groups={'KEEP':{r for r,t in truth.items() if t=='keep'},'D':{r for r,t in truth.items() if t=='drop'},
        'C1':{c['row_id'] for c in ledger['c1_witnesses']},
        'gallery':{c['row_id'] for c in ledger['gallery_witnesses'] if c['type']=='merged_multi_line'},
        'rotated':{c['row_id'] for c in ledger['gallery_witnesses'] if c['type']=='rotated_vertical_line'}}
    counts={}
    for name,ids in groups.items():
        expected=name!='KEEP'
        counts[name]=dict(required=len(ids),met=sum(by[r]['composed']['drop'] is expected for r in ids),
            unresolved=[r for r in sorted(ids) if by[r]['composed']['drop'] is None],
            geometry_unavailable=[r for r in sorted(ids) if by[r]['geometry_unavailable']],
            orientation_unknown=[r for r in sorted(ids) if by[r]['orientation_unknown']],
            verified_keeps=sum(by[r]['composed']['verified_keep'] for r in ids))
    assert [counts[k]['required'] for k in ('KEEP','D','C1','gallery')]==[22,9,6,6]
    assert all(c['met']==c['required'] for c in counts.values()),counts
    assert all(checks.values()),checks
    data=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases).encode()
    (HERE/'keys/frozen_witness_measurements.jsonl.gz').write_bytes(gzip.compress(data,mtime=0))
    result=dict(schema='SEG-CP7-frozen-witness-1',passed=True,counts=counts,
        acceptance=dict(passed=all(checks.values()),requirements=checks,met=sum(checks.values()),required=len(checks)),
        freeze_sha256=sha(SEG/'CP7_FREEZE.json'),canonical_scanner_sha256=SCANNER,
        measurements_sha256=sha(HERE/'keys/frozen_witness_measurements.jsonl.gz'),
        note='D includes one explicit geometry-unavailable policy DROP; unknown orientation admits only that screen; text rules do not reduce witness denominators',
        readers_started=0,publish_actions=0)
    dump(SEG/'CP7_frozen_verification.json',result)
    verify_freeze();print(json.dumps(result,indent=2))

if __name__=='__main__':
    offline_guard()
    if sys.argv[1]=='create':create()
    elif sys.argv[1]=='gate':gate()
    elif sys.argv[1]=='verify':verify_freeze()
