"""Release-3 fail-closed binding, exposure and native v2.1 overlay consumer."""
import copy
import gzip
import hashlib
import json
from pathlib import Path

import pytest

from bench import e4_wave2_r3 as r3, e4_wave2 as w
from bench.e1_common import atomic_json, read_json, sha256
from bench.common import write_rows
from train import mix as tm


def pin(p): return dict(path=str(p), sha256=sha256(p))
def identity(ident='train', **kw):
    return dict(dict(parent_id='collection-v2-train', row_id=ident, edition_id='train-edition', crop_sha256='a'*64), **kw)


def receipt_for(suite):
    panels = read_json(suite)['panels']
    atomic_json(suite.parent/'SEAL_RECEIPT.json', dict(status='SEALED', version='0.2', mock=False,
        suite_sha256=sha256(suite), rows=sum(p['rows'] for p in panels.values()),
        quota_counts={name.removeprefix('benchmark_v02_')+':polytonic': dict(sealed=p['rows'])
                      for name, p in panels.items()}))


def fixture(tmp_path):
    suite = tmp_path/'suite.json'
    panels = {}
    for split in ('test', 'dev'):
        p = tmp_path/(split+'.jsonl')
        write_rows(p, [identity(split, edition_id=split+'-edition', crop_sha256=('b' if split=='test' else 'c')*64, split=split, doc=split+'-edition')])
        panels['benchmark_v02_'+split] = dict(path=p.name, sha256=sha256(p), rows=1, scorable=True)
    atomic_json(suite, dict(schema='ocr-benchmark-suite-v1', version='0.2', mock=False, panels=panels))
    receipt_for(suite)
    split = tmp_path/'split.jsonl.gz'
    with gzip.open(split, 'wt') as f: f.write(json.dumps(dict(edition_id='heldout', split='test'))+'\n')
    protected = tmp_path/'protected.jsonl'; write_rows(protected, [dict(crop_sha256='d'*64)])
    inv = {}
    for arm in r3.ARMS:
        p = tmp_path/(arm+'.jsonl'); write_rows(p, [identity()]); inv[arm] = pin(p)
    cfg = dict(input_files=[pin(split), pin(protected)], training_inventories=inv, split2=pin(split), protected_crops=pin(protected))
    p = tmp_path/'INPUTS.json'; atomic_json(p, cfg)
    return p, suite


def test_benchmark_unbound_and_bound_states(tmp_path):
    inputs, suite = fixture(tmp_path)
    result = r3.verify_inputs(read_json(inputs))
    assert result['state']=='VERIFY_INPUTS_FAIL' and 'BENCHMARK_0_2_UNBOUND' in result['errors']
    out = tmp_path/'BOUND.json'
    r3.bind_benchmark(inputs, suite, sha256(suite), out)
    assert r3.verify_inputs(read_json(out))['state']=='VERIFY_INPUTS_OK'
    assert set(read_json(out)['benchmark_0_2']['exposure'])==set(r3.ARMS)
    assert inputs.read_bytes()!=out.read_bytes()
    with pytest.raises(ValueError, match='OUTPUT_EXISTS'): r3.bind_benchmark(inputs,suite,sha256(suite),out)


@pytest.mark.parametrize('fault,code', [
    ('missing', 'MISSING'), ('status', 'NOT_SEALED'), ('mock', 'NOT_SEALED'),
    ('version', 'NOT_SEALED'), ('invalid_json', 'NOT_SEALED'),
    ('suite_sha256', 'SUITE_MISMATCH'), ('rows', 'SUITE_MISMATCH'),
    ('quota_counts', 'SUITE_MISMATCH'), ('split_counts', 'SUITE_MISMATCH')])
def test_seal_receipt_refusals(tmp_path, fault, code):
    inputs, suite = fixture(tmp_path)
    path = suite.parent/'SEAL_RECEIPT.json'
    receipt = read_json(path)
    if fault == 'missing': path.unlink()
    elif fault == 'invalid_json': path.write_text('{')
    else:
        if fault == 'status': receipt['status'] = 'PENDING'
        if fault == 'mock': receipt['mock'] = True
        if fault == 'version': receipt['version'] = '0.1'
        if fault == 'suite_sha256': receipt['suite_sha256'] = '0'*64
        if fault == 'rows': receipt['rows'] += 1
        if fault == 'quota_counts': receipt['quota_counts'] = {}
        if fault == 'split_counts':
            receipt['quota_counts']['test:polytonic']['sealed'] = 0
            receipt['quota_counts']['dev:polytonic']['sealed'] = 2
        atomic_json(path, receipt)
    out = tmp_path/'bound.json'
    with pytest.raises(ValueError, match='SEAL_RECEIPT_'+code):
        r3.bind_benchmark(inputs, suite, sha256(suite), out)
    assert not out.exists()


def test_rebind_new_seal_from_same_parent_and_verify_each(tmp_path, capsys):
    import os
    import shlex
    import subprocess
    import sys
    inputs, suite = fixture(tmp_path)
    before = inputs.read_bytes()
    # Seal03 has two dev rows; seal04 drops one, preserving the test panel.
    old = read_json(suite); old_dev = tmp_path/'dev.jsonl'
    row = json.loads(old_dev.read_text())
    write_rows(old_dev, [row, dict(row, row_id='dev-extra')])
    old['panels']['benchmark_v02_dev'].update(rows=2, sha256=sha256(old_dev))
    atomic_json(suite, old); receipt_for(suite)
    first = tmp_path/'INPUTS.bound.seal03.json'
    r3.bind_benchmark(inputs, suite, sha256(suite), first)
    import shutil
    new_dir = tmp_path/'seal04'; new_dir.mkdir()
    for name in ('suite.json', 'test.jsonl', 'dev.jsonl'):
        shutil.copyfile(tmp_path/name, new_dir/name)
    new_suite = new_dir/'suite.json'; s = read_json(new_suite)
    p = new_dir/'dev.jsonl'; write_rows(p, [row])
    s['panels']['benchmark_v02_dev'].update(rows=1, sha256=sha256(p))
    atomic_json(new_suite, s); receipt_for(new_suite)
    second = tmp_path/'INPUTS.bound.seal04.json'
    r3.bind_benchmark(inputs, new_suite, sha256(new_suite), second)
    a, b = read_json(first), read_json(second)
    for cfg, seal in ((a, suite.parent), (b, new_dir)):
        block = cfg['benchmark_0_2']
        assert block['seal_directory'] == str(seal)
        assert block['seal_receipt'] == pin(seal/'SEAL_RECEIPT.json')
    assert a.pop('benchmark_0_2') != b.pop('benchmark_0_2')
    assert a == b and inputs.read_bytes() == before
    root = Path(__file__).resolve().parents[1]
    (tmp_path/'runtime.sh').write_text('E3_PYTHON=('+shlex.quote(sys.executable)+')\n')
    for out in (first, second):
        assert r3.main(['verify-inputs', '--inputs', str(out)]) == 0
        assert json.loads(capsys.readouterr().out)['state'] == 'VERIFY_INPUTS_OK'
        result = subprocess.run(['bash', str(root/'VERIFY.sh'), 'inputs'],
            env=dict(os.environ, W=str(tmp_path), E4_ROOT=str(root), E4_INPUTS=str(out)),
            capture_output=True, text=True)
        assert result.returncode == 0, result.stderr + result.stdout
        assert json.loads(result.stdout)['state'] == 'VERIFY_INPUTS_OK'
    saved = second.read_bytes()
    with pytest.raises(ValueError, match='BIND_OUTPUT_EXISTS'):
        r3.bind_benchmark(inputs, new_suite, sha256(new_suite), second)
    assert second.read_bytes() == saved


def test_verify_rejects_changed_receipt(tmp_path):
    inputs, suite = fixture(tmp_path)
    cfg = r3.bind_benchmark(inputs, suite, sha256(suite), tmp_path/'bound.json')
    path = suite.parent/'SEAL_RECEIPT.json'; receipt = read_json(path)
    receipt['comparison_status'] = 'changed'; atomic_json(path, receipt)
    result = r3.verify_inputs(cfg)
    assert result['state'] == 'VERIFY_INPUTS_FAIL'
    assert any('SEAL_RECEIPT_SUITE_MISMATCH' in e for e in result['errors'])


@pytest.mark.parametrize('field,value,check', [
    ('edition_id','test-edition','benchmark_edition'),
    ('row_id','test','benchmark_row_key'),
    ('crop_sha256','b'*64,'benchmark_crop_sha256'),
    ('edition_id','heldout','split2_dev_test_edition'),
    ('crop_sha256','d'*64,'census05_protected_crop')])
def test_each_exposure_check_fatal_on_corrected_arm(tmp_path,field,value,check):
    inputs, suite = fixture(tmp_path); cfg=read_json(inputs)
    p=Path(cfg['training_inventories']['add_corr']['path']); write_rows(p,[identity(**{field:value})])
    cfg['training_inventories']['add_corr']=pin(p); atomic_json(inputs,cfg)
    rows,_=r3.sealed_rows(pin(suite)); audit=r3.audit_inventories(cfg,rows)
    assert audit['ctrl']['hits']==audit['add']['hits']==0
    assert audit['add_corr']['checks'][check]==1
    with pytest.raises(ValueError,match='EXPOSURE_FATAL'):r3.bind_benchmark(inputs,suite,sha256(suite),tmp_path/'bound.json')
    assert not (tmp_path/'bound.json').exists()


@pytest.mark.parametrize('fault',['suite_sha','panel_sha','mock','scorable','empty','missing_parent','missing_crop','missing_inventory'])
def test_seal_bind_rejects_incomplete_or_mutated_evidence(tmp_path,fault):
    inputs,suite=fixture(tmp_path);cfg=read_json(inputs);s=read_json(suite)
    if fault=='mock':s['mock']=True
    if fault=='scorable':s['panels']['benchmark_v02_test']['scorable']=False
    if fault=='empty':s['panels']['benchmark_v02_test']['rows']=0
    if fault in ('missing_parent','missing_crop'):
        p=tmp_path/'test.jsonl';row=identity('test');row.pop('parent_id' if fault=='missing_parent' else 'crop_sha256')
        write_rows(p,[row]);s['panels']['benchmark_v02_test']['sha256']=sha256(p)
    if fault=='missing_inventory':cfg['training_inventories'].pop('add_corr');atomic_json(inputs,cfg)
    atomic_json(suite,s)
    if fault=='panel_sha':(tmp_path/'test.jsonl').write_text('{}\n')
    digest='0'*64 if fault=='suite_sha' else sha256(suite)
    with pytest.raises((ValueError, KeyError)):r3.bind_benchmark(inputs,suite,digest,tmp_path/'bound.json')
    assert not (tmp_path/'bound.json').exists()


def test_release_v3_raw_labels_and_tranche_crop_roots(tmp_path):
    row=dict(parent_id='w1',row_id='r',source='s',split='train',label=' raw α ',
        raw_text_sha256=hashlib.sha256(' raw α '.encode()).hexdigest(),crop_relative_path='collection_w1_originals/s/r.png',
        crop_sha256='a'*64,edition_id='edition',admission_decision={'file':'census'})
    spec=dict(crop_roots={'w1':str(tmp_path/'collection_w1_originals')})
    r=r3.release_row(row,spec)
    assert r['label']==row['label'] and r['crops_layout']=='source/row_id'
    assert w.crop_path(r)==tmp_path/'collection_w1_originals/s/r.png'
    with pytest.raises(ValueError,match='NOT_RAW'):r3.release_row(dict(row,label='α'),spec)
    with pytest.raises(ValueError,match='CROP_PATH'):r3.release_row(dict(row,crop_relative_path='../r.png'),spec)


def test_v21_overlay_runs_through_actual_train_loader(tmp_path,monkeypatch):
    from tests.test_e4_wave1c import write_build,register,label,row
    from bench import e4_wave1c as labels
    monkeypatch.setattr(tm,'committed_recipes',lambda *a:{})
    rr=[dict(row('old'),codec_version='v2.1'),dict(row('new'),codec_version='v2.1'),dict(row('val'),split='val',codec_version='v2.1')]
    c=write_build(tmp_path/'build',rr)
    info=read_json(tmp_path/'build/build_info.json');info['codec_version']='v2.1';atomic_json(tmp_path/'build/build_info.json',info)
    registry=register(tmp_path/'labels',[label('old'),label('new')])
    overlay=labels.overlay_spec(registry,['real'],w.CODEC)
    p=tmp_path/'mix.json';atomic_json(p,dict(schema_version=1,components=[c],seed=20261015,codec_version='v2.1',created_by='test',notes='fixture',label_versions=overlay))
    resolved=tm.validate(p)
    assert [r['text'] for r in tm.load_rows(resolved,'train')[0]]==['β','β']
    assert tm.load_rows(resolved,'val')[0][0]['text']=='α'
    with pytest.raises(ValueError,match='train-only'):tm.validate(p,role='eval')
    with pytest.raises(ValueError,match='train-only'):tm.validate(p,role='val')


def census_fixture(tmp_path):
    records=[]
    for ident,split,disposition in [('old','train','ADMIT'),('hold','train','HOLD'),('test','test','ADMIT')]:
        binding=dict(parent_id='collection-v2-train',id=ident,split=split,crop_sha256='a'*64)
        d=dict(binding=binding,run_binding_sha256='binding',final_text='census correction',disposition=disposition,
            reasons=[] if disposition=='ADMIT' else [dict(reason='segmentation')])
        records.append(dict(row_id=ident,parent_id=binding['parent_id'],split=split,crop_sha256='a'*64,
            source='source',primary_class='class',decision=d,disposition=disposition,**{'pass':disposition=='ADMIT'}))
    p=tmp_path/'records.jsonl';write_rows(p,records)
    summary=tmp_path/'summary.json';atomic_json(summary,dict(complete=True,export_id='gen',input_rows=3,
        outputs=dict(admission_records=dict(sha256=sha256(p)))))
    current=tmp_path/'CURRENT.json';atomic_json(current,dict(status='completed',export_id='gen',
        run_binding_sha256='binding',summary_sha256=sha256(summary)))
    return dict(current=pin(current),summary=pin(summary),records=pin(p))


def test_census05_selects_admit_and_train_without_relabelling(tmp_path):
    cfg=census_fixture(tmp_path);gate=r3.Census05Admission(cfg)
    raw=[dict(line_id=i,text='factory label') for i in ('old','hold','test')]
    selected=gate.filter(raw)
    assert selected==[raw[0]] and selected[0]['text']=='factory label'
    assert gate.receipt(1)['control_rows']==1
    assert gate.receipt(1)['drops_per_rule']=={'segmentation':1}
    with pytest.raises(ValueError,match='absent'):gate.filter([dict(line_id='missing')])
    with pytest.raises(ValueError,match='failed'):gate.require_pass([raw[1]])


@pytest.mark.parametrize('fault',['count','binding','duplicate','generation','sha'])
def test_census05_refuses_unbound_or_ambiguous_selection(tmp_path,fault):
    cfg=census_fixture(tmp_path);records=list(__import__('bench.common',fromlist=['read_rows']).read_rows(cfg['records']['path']))
    if fault=='binding':records[0]['decision']['binding']['id']='wrong'
    if fault=='duplicate':records.append(records[0])
    if fault in ('binding','duplicate'):
        write_rows(cfg['records']['path'],records);cfg['records']=pin(Path(cfg['records']['path']))
        s=read_json(cfg['summary']['path']);s['outputs']['admission_records']['sha256']=cfg['records']['sha256'];atomic_json(cfg['summary']['path'],s)
    if fault=='count':
        s=read_json(cfg['summary']['path']);s['input_rows']=99;atomic_json(cfg['summary']['path'],s)
    if fault=='generation':
        s=read_json(cfg['summary']['path']);s['export_id']='wrong';atomic_json(cfg['summary']['path'],s)
    if fault!='sha':
        cfg['summary']=pin(Path(cfg['summary']['path']));c=read_json(cfg['current']['path']);c['summary_sha256']=cfg['summary']['sha256'];atomic_json(cfg['current']['path'],c);cfg['current']=pin(Path(cfg['current']['path']))
    else:cfg['records']['sha256']='0'*64
    with pytest.raises(ValueError):r3.Census05Admission(cfg)


def test_native_census_prepare_refuses_login_before_population_reads(tmp_path,monkeypatch):
    from types import SimpleNamespace
    p=tmp_path/'inputs.json';atomic_json(p,dict(census05={'records':'must not read'},schema='e4-wave2-inputs-v1',status='INVENTORY_ONLY'))
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    monkeypatch.setattr(w,'standard_admission',lambda *a:pytest.fail('read population on login/Mac'))
    with pytest.raises(ValueError,match='compute allocation'):
        w.prepare(SimpleNamespace(out=tmp_path/'out',inputs=p,stage='inventory'))


@pytest.mark.parametrize('value', [{}, {'ii': {}}, None])
def test_locked_key_refused_at_bind_and_prepare(tmp_path, value):
    from types import SimpleNamespace
    inputs,suite=fixture(tmp_path);cfg=read_json(inputs);cfg['locked']=value;atomic_json(inputs,cfg)
    with pytest.raises(ValueError,match='LOCKED_STRATA_REMOVED'):
        r3.bind_benchmark(inputs,suite,sha256(suite),tmp_path/'bound.json')
    with pytest.raises(ValueError,match='LOCKED_STRATA_REMOVED'):
        w.prepare(SimpleNamespace(inputs=inputs,out=tmp_path/'out'))
    assert any('LOCKED_STRATA_REMOVED' in e for e in r3.verify_inputs(cfg)['errors'])


@pytest.mark.parametrize('arm',r3.ARMS)
def test_factory_crop_candidate_match_for_every_arm(tmp_path,arm):
    inputs,suite=fixture(tmp_path);cfg=read_json(inputs)
    p=Path(cfg['training_inventories'][arm]['path'])
    write_rows(p,[identity(factory_crop_sha256='b'*64)])
    cfg['training_inventories'][arm]=pin(p)
    rows,_=r3.sealed_rows(pin(suite))
    audit=r3.audit_inventories(cfg,rows)
    assert audit[arm]['checks']['benchmark_crop_sha256']==1
    assert audit[arm]['checks']['benchmark_edition']==0


def test_inventory_summary_actual_draws_all_model_seeds_and_versions(tmp_path):
    from tests.test_e4_wave1c import row
    old=[[row('a')],[row('s',kind='synthetic')]]
    added=[[row('a'),row('b')],old[1]]
    comps=[dict(kind='real',fraction=.5),dict(kind='synthetic',fraction=.5)]
    overlay=dict(unmatched={'RU1':['missing'],'N1':[]},counts=[
        dict(version='RU1',outcome='substituted',rows=1),
        dict(version='RU1',outcome='codec_rejected',rows=1),
        dict(version='N1',outcome='unchanged',rows=1)])
    exposure={arm:dict(checks={'benchmark_crop_sha256':0}) for arm in r3.ARMS}
    atomic_json(tmp_path/'EXPOSURE_CANDIDATES.json',dict(arms=exposure))
    result=r3.inventory_summary(old,dict(components=comps,seed=20261015),added,comps,overlay,tmp_path,rows=20,epochs=2)
    for arm in r3.ARMS:
        assert set(result['arms'][arm])=={'0','1','2'}
        for seed in result['arms'][arm].values():
            assert seed['unique_real_rows']==(1 if arm=='ctrl' else 2)
            assert seed['total']==dict(real_draws=20,synthetic_draws=20)
            assert all(v['real_draws']==v['synthetic_draws']==10 for v in seed['epochs'].values())
    assert result['versions']['RU1']==dict(accepted=1,rejected=1,unmatched=1,substituted=1,unchanged=0)
    assert result['versions']['N1']['accepted']==1
    assert result['candidate_crop_exposure']==exposure
    assert 'factory + raw release-v3 import' in (tmp_path/'INVENTORY_SUMMARY.md').read_text()


def test_pending_inventory_states_exact(tmp_path):
    inputs,_=fixture(tmp_path);cfg=read_json(inputs)
    cfg.update(training_inventories={},protected_crops=None)
    assert r3.verify_inputs(cfg)['errors']==['INVENTORY_PENDING','BENCHMARK_0_2_UNBOUND']


def test_split2_bound_ledgers_and_forced_exclusion(tmp_path):
    inputs,_=fixture(tmp_path);cfg=read_json(inputs)
    editions=tmp_path/'editions.jsonl'
    write_rows(editions,[dict(edition_id='heldout',split='test',forced=True),dict(edition_id='train',split='train',forced=False)])
    cfg['editions']=pin(editions)
    held=tmp_path/'heldout.json';atomic_json(held,dict(edition_ids=['heldout']));cfg['heldout_editions']=pin(held)
    receipt=tmp_path/'receipt.json';atomic_json(receipt,dict(counts=dict(editions=2,forced_edition_details=[dict(edition_id='heldout')])))
    cfg['split2_receipt']=pin(receipt)
    # The fixture split carries an edition; add the canonical row identity.
    split=Path(cfg['split2']['path'])
    with gzip.open(split,'wt') as f:f.write(json.dumps(dict(row_id='r',edition_id='heldout',split='test'))+'\n')
    cfg['split2']=pin(split)
    assert r3.split2_ledgers(cfg)==({'r':'heldout'},{'heldout'})
    atomic_json(held,dict(edition_ids=[]));cfg['heldout_editions']=pin(held)
    with pytest.raises(ValueError,match='HELDOUT_LEDGER_MISMATCH'):r3.split2_ledgers(cfg)


@pytest.mark.parametrize('witness',['original','factory'])
def test_prepare_exposure_includes_vc_and_preserves_v2_book(tmp_path,witness):
    from types import SimpleNamespace
    inputs,_=fixture(tmp_path);cfg=read_json(inputs)
    pixels=b'canonical factory png'
    candidate_sha='a'*64 if witness=='original' else hashlib.sha256(pixels).hexdigest()
    candidates=tmp_path/'candidates.jsonl';readout=tmp_path/'readout.jsonl'
    write_rows(candidates,[identity('test',edition_id='test-edition',crop_sha256=candidate_sha)])
    write_rows(readout,[identity('test',edition_id='test-edition',crop_sha256=candidate_sha)])
    cfg.update(candidates=pin(candidates),candidates_readout=pin(readout))
    admitted=tmp_path/'admitted.jsonl'
    write_rows(admitted,[dict(id='old',parent_id='collection-v2-train',edition_id='census-alias',crop_sha256='a'*64)])
    policy=tmp_path/'policy.json';atomic_json(policy,dict(heldout_crop_sha256=['d'*64]))
    cfg['census05']=dict(admitted_train=pin(admitted),final_policy=pin(policy))
    gate=SimpleNamespace(rows={},decision=lambda r:dict(parent_id='collection-v2-train',crop_sha256='a'*64))
    real=[dict(line_id='old',edition_id='canonical-v2-book',image_png=pixels)]
    out=tmp_path/'inventory';out.mkdir()
    with pytest.raises(ValueError,match='CANDIDATE_EXPOSURE_FATAL'):
        r3.prepare_exposure(real,[],gate,cfg,out)
    audit=read_json(out/'EXPOSURE_CANDIDATES.json')
    assert all(audit['arms'][arm]['checks']['benchmark_crop_sha256']==1 for arm in r3.ARMS)
    stored=json.loads((out/'ctrl_train_inventory.jsonl').read_text())
    assert stored['edition_id']=='canonical-v2-book'
    assert stored['factory_crop_sha256']==hashlib.sha256(pixels).hexdigest()


def test_inventory_binding_promotes_final_only_after_audit(tmp_path):
    inputs,suite=fixture(tmp_path);cfg=read_json(inputs);cfg['status']='INVENTORY_ONLY';atomic_json(inputs,cfg)
    result=r3.bind_benchmark(inputs,suite,sha256(suite),tmp_path/'bound.json')
    assert result['status']=='FINAL'
    assert r3.verify_inputs(result)['state']=='VERIFY_INPUTS_OK'


# Real package heads: keep this in the package suite's existing collected module.
REAL_HEAD = Path(__file__).parent/'fixtures/e4w2_real_head'


def real_head(name):
    import base64
    from bench.common import read_rows
    path = REAL_HEAD/name
    if path.exists():
        rows = list(read_rows(path))
    else:
        with gzip.open(str(path)+'.gz', 'rt') as stream:
            rows = [json.loads(line) for line in stream]
    for row in rows:
        if isinstance(row.get('image_png'), dict):
            row['image_png'] = base64.b64decode(row['image_png']['base64'])
    return rows


def head_build(root, rows, *, kind='real', fraction=1., split='train', version='v2'):
    """Rebind sampled bytes to local paths; preserve every native row field."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    (root/split).mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([dict(r, split=split, codec_version=version) for r in rows]),
                   root/split/'shard-00000.parquet')
    info = dict(kind=kind, codec_version=version, partition_id='real-head',
                shard_sha256=tm.shard_inventory(root))
    if kind == 'synthetic':
        info.update(audit_ok=True, recipe_sha256=sha256(w.ROOT/'factory/recipe.v5.json'))
        component = dict(kind=kind, build_dir=str(root), recipe_sha256=info['recipe_sha256'], fraction=fraction)
    else:
        component = dict(kind=kind, shard_dir=str(root), shard_sha256=info['shard_sha256'],
                         partition_id=info['partition_id'], source='real-head', fraction=fraction)
    atomic_json(root/'build_info.json', info)
    return component


def head_mix(path, components, version='v2'):
    atomic_json(path, dict(schema_version=1, components=components, seed=20261015,
                           codec_version=version, created_by='real-head test', notes='Sample descriptors rebound locally'))
    return path


@pytest.fixture
def real_head_setup(tmp_path, monkeypatch):
    """Actual loaders, census, draws, exposure, imports and binding on sampled rows.

    Only external release custody and the Rust subprocess are test doubles.
    Descriptors (hashes/counts/paths) are rebound to the unchanged sample rows.
    """
    import shutil
    from types import SimpleNamespace
    from bench import e4_wave1c as labels, e1_prepare
    from bench.common import read_rows
    metadata = read_json(REAL_HEAD/'recovered_mix.json')
    components = []
    meta = []
    for i, c in enumerate(metadata['components']):
        rows = real_head(f'vc_{i}.jsonl')
        if i == 0:
            rows += real_head('vc_ru1_matched.jsonl')
        components.append(head_build(tmp_path/f'old/c{i}', rows, kind=c['kind'], fraction=c['fraction']))
        if c['kind'] == 'real':
            meta += [dict(line_id=r['line_id'], book_key=r['source_doc_id'],
                          wave=Path(c['shard_dir']).name) for r in rows]
    train = head_mix(tmp_path/'old/mix.json', components)
    prep = tmp_path/'prep'
    write_rows(prep/'records/head.meta.jsonl', meta)
    # Census heads plus exact matching native/edit IDs, all unchanged corpus rows.
    records = {}
    admitted = {}
    for name in ('census_records.jsonl', 'census_records_matched.jsonl'):
        records.update({r['row_id']:r for r in real_head(name)})
    for name in ('census_admitted_train.jsonl', 'census_admitted_train_matched.jsonl'):
        admitted.update({r['id']:r for r in real_head(name)})
    record_path = tmp_path/'census/records.jsonl'; write_rows(record_path, list(records.values()))
    admitted_path = tmp_path/'census/admitted.jsonl'; write_rows(admitted_path, list(admitted.values()))
    summary = json.loads(gzip.decompress((REAL_HEAD/'census_summary.json.gz').read_bytes()))
    summary['input_rows'] = len(records)
    summary['outputs']['admission_records'] = pin(record_path)
    summary_path = tmp_path/'census/summary.json'; atomic_json(summary_path, summary)
    current = read_json(REAL_HEAD/'census_current.json'); current['summary_sha256'] = sha256(summary_path)
    current_path = tmp_path/'census/CURRENT.json'; atomic_json(current_path, current)
    policy = tmp_path/'census/policy.json'; atomic_json(policy, json.loads(gzip.decompress((REAL_HEAD/'census_final_policy.json.gz').read_bytes())))
    census = dict(current=pin(current_path), summary=pin(summary_path), records=pin(record_path),
                  admitted_train=pin(admitted_path), final_policy=pin(policy))
    release_rows = real_head('release.jsonl')
    release_path = tmp_path/'release.jsonl'; write_rows(release_path, release_rows)
    shutil.copytree(REAL_HEAD/'crops', tmp_path/'crops')
    roots = {r['parent_id']:str(tmp_path/'crops'/r['crop_relative_path'].split('/')[0]) for r in release_rows}
    admissions = [dict(pin(release_path), rows=len(release_rows), final=True,
                       format='release-v3-20261020', crop_roots=roots)]
    # Actual RU1/N1 registry field mappings, statuses and provenance.
    registry = read_json(w.ROOT/'labels/VERSIONS.json')
    for version, filename in [('ru1_v3_edits','ru1_v3_edits.jsonl'), ('n1_v1_w1','n1_v1_w1.jsonl')]:
        target = tmp_path/'labels'/filename; write_rows(target, real_head(filename))
        v = registry['versions'][version]
        v.update(path=str(target), portable_path=filename, sha256=sha256(target))
        v['population']['rows'] = len(real_head(filename))
    registry_path = tmp_path/'labels/VERSIONS.json'; atomic_json(registry_path, registry)
    # Retain literal seal04 rows and original crop bytes. Rebind suite/receipt counts.
    seal = tmp_path/'seal04'; shutil.copytree(REAL_HEAD/'seal04', seal)
    suite = read_json(REAL_HEAD/'suite.json')
    for name, panel in suite['panels'].items():
        target = seal/panel['path']; write_rows(target, real_head(name+'.jsonl'))
        panel.update(rows=len(real_head(name+'.jsonl')), sha256=sha256(target))
    suite_path = seal/'suite.json'; atomic_json(suite_path, suite)
    receipt = read_json(REAL_HEAD/'SEAL_RECEIPT.json')
    receipt.update(suite_sha256=sha256(suite_path), rows=6,
                   quota_counts={name.removeprefix('benchmark_v02_')+':sample':dict(sealed=p['rows'])
                                 for name,p in suite['panels'].items()})
    atomic_json(seal/'SEAL_RECEIPT.json', receipt)
    benchmark, _ = r3.sealed_rows(pin(suite_path))
    candidates = tmp_path/'candidates.jsonl'; write_rows(candidates, benchmark)
    split = tmp_path/'split.jsonl.gz'
    held_editions = sorted({r['doc'] for r in benchmark})
    train_editions = sorted({r['edition_id'] for r in release_rows})
    with gzip.open(split, 'wt') as f:
        for r in release_rows:
            f.write(json.dumps(dict(row_id=r['row_id'], edition_id=r['edition_id'], split='train'))+'\n')
        for r in benchmark:
            f.write(json.dumps(dict(row_id=r['row_id'], edition_id=r['doc'], split=r['split']))+'\n')
    editions = tmp_path/'editions.jsonl'
    write_rows(editions, [dict(edition_id=e, split='train', forced=False) for e in train_editions] +
                        [dict(edition_id=e, split=next(r['split'] for r in benchmark if r['doc']==e),
                              forced=e==held_editions[0]) for e in held_editions])
    held = tmp_path/'held.json'; atomic_json(held, dict(edition_ids=held_editions))
    split_receipt = tmp_path/'split_receipt.json'
    atomic_json(split_receipt, dict(counts=dict(editions=len(train_editions)+len(held_editions),
        forced_edition_details=[dict(edition_id=held_editions[0])])))
    cfg = dict(schema='e4-wave2-inputs-v1', status='INVENTORY_ONLY', admissions=admissions,
        census05=census, versions=['ru1_v3_edits','n1_v1_w1'], editions=pin(editions), heldout_editions=pin(held),
        candidates=pin(candidates), candidates_readout=pin(candidates), split2=pin(split),
        split2_receipt=pin(split_receipt), input_files=[pin(record_path), pin(release_path), pin(split)])
    inputs = tmp_path/'INPUTS.json'; atomic_json(inputs, cfg)
    campaign = tmp_path/'campaign'
    release = campaign/'v2-codec/release.json'; atomic_json(release, dict(sample=True))
    index = campaign/'v2-codec/draw_rows_v_c.jsonl.gz'; index.write_bytes(b'head-sample draw custody')
    # Full remote release hashes/population are separately attested in SOURCES.
    monkeypatch.setattr(labels, 'RELEASE', sha256(release))
    monkeypatch.setattr(labels, 'DRAW_SHA', sha256(index))
    monkeypatch.setattr(w.base, 'ROWS', 40)
    valrow = real_head('vc_0.jsonl')[:1]
    val = head_mix(tmp_path/'val/mix.json', [head_build(tmp_path/'val/build', valrow, split='val')])
    ev = head_mix(tmp_path/'eval/mix.json', [head_build(tmp_path/'eval/build', valrow, split='reserved')])
    monkeypatch.setattr(w.base, 'load_release', lambda a:({}, dict(recovered_mix=train, val_v2=val), sha256(release)))
    monkeypatch.setattr(labels, 'instruments', lambda a:dict(v2_test=ev, v2_test_full_coverage=ev))
    # A native-schema factory subprocess double: no convenient 'text' field.
    def factory_build(executable, args, dest):
        feed = Path(args[args.index('--records')+1]); root = Path(args[args.index('--crops')+1])
        rows = []
        for r in read_rows(feed):
            text, ids, bad = labels.encode(r['text'], w.CODEC); assert not bad
            image = (root/r['crop_path']).read_bytes()
            native = dict(valrow[0], line_id=r['id'], gt_nfd=text, gt_nfc=__import__('unicodedata').normalize('NFC', text),
                label_ids=ids, image_png=image, width=int.from_bytes(image[16:20], 'big'),
                split=r['split'], script_class=r['script_class'], source_dataset=r['source_dataset'])
            assert 'text' not in native
            rows.append(native)
        head_build(dest, rows, split=rows[0]['split'], version='v2.1')
        info = read_json(dest/'build_info.json')
        info.update(partition_id=args[args.index('--partition')+1], records_sha256=sha256(feed), drop_ledger=[])
        atomic_json(dest/'build_info.json', info)
    monkeypatch.setattr(e1_prepare, 'factory_build', factory_build)
    monkeypatch.setenv('SLURM_JOB_ID', 'local-head-test')
    factory = tmp_path/'factory'; factory.write_bytes(b'local process double')
    a = SimpleNamespace(out=tmp_path/'inventory02', inputs=inputs, registry=registry_path, campaign=campaign,
                         prep=prep, factory=factory, stage='inventory', smoke=False, job='job02')
    return a, suite_path, train


def test_real_heads_native_labels_and_original_keyerror(real_head_setup):
    from train.cer import load_codec
    a, _, train = real_head_setup
    pools = tm.load_rows(tm.validate(train), 'train')
    codec = load_codec(str(w.ROOT/'codec/v2.json'))
    for pool in pools:
        for row in pool:
            assert 'text' not in row
            assert row['gt_nfd'] == codec.decode(row['label_ids'])
    real = w.standard_admission(a).filter(pools[0])
    gate = w.standard_admission(a)
    with pytest.raises(KeyError, match='text'):
        sum(gate.decision(r)['final_text'] != r['text'] for r in real)


def test_real_heads_full_inventory_done_and_seal04_bind(real_head_setup):
    from bench import e4_wave1c as labels
    a, suite, _ = real_head_setup
    w.prepare(a)
    done = read_json(a.out/'INVENTORY_DONE.json')
    assert done['mode'] == 'INVENTORY_ONLY'
    assert done['ctrl_rows'] == 21 and done['add_rows'] == 24
    assert done['release_rows'] == 3 and done['codec_rejections'] == []
    assert done['corrected_rows'] == 1
    assert set(done) == {'mode','ctrl_rows','add_rows','add_corr_rows','release_rows','codec_rejections',
                         'corrected_rows','ctrl_by_class','add_by_class','census_final_text_differs_factory',
                         'census_final_text_differs_factory_nfd','input_spec_sha256'}
    assert done['add_rows'] == done['add_corr_rows']
    assert done['input_spec_sha256'] == sha256(a.inputs)
    assert done['census_final_text_differs_factory'] == 21
    assert done['census_final_text_differs_factory_nfd'] == 3
    assert sum(done['ctrl_by_class'].values()) == done['ctrl_rows']
    assert sum(done['add_by_class'].values()) == done['add_rows']
    assert read_json(a.out/'substitution.json')['rows_substituted'] == done['corrected_rows']
    summary = read_json(a.out/'INVENTORY_SUMMARY.json')
    assert all(set(summary['arms'][arm]) == {'0','1','2'} for arm in r3.ARMS)
    bound = a.out/'BOUND.seal04.json'
    result = r3.bind_benchmark(a.out/'INPUTS.with_inventories.json', suite, sha256(suite), bound)
    assert r3.verify_inputs(result)['state'] == 'VERIFY_INPUTS_OK'
    assert all(v['hits'] == 0 for v in result['benchmark_0_2']['exposure'].values())
    assert all(len(real_head(name+'.jsonl')) == 3 for name in ('benchmark_v02_test','benchmark_v02_dev'))


def test_real_heads_production_prepare_and_actual_overlay(real_head_setup):
    from bench import e4_wave1c as labels
    a, suite, _ = real_head_setup
    # Inventory is also the authoritative source for the production binding.
    w.prepare(a)
    bound = a.out/'BOUND.seal04.json'
    r3.bind_benchmark(a.out/'INPUTS.with_inventories.json', suite, sha256(suite), bound)
    a.inputs = bound; a.out = a.out.parent/'production'; a.stage = 'prepare'
    node = w.prepare(a)
    assert node['mode'] == 'PRODUCTION' and w.verify(a) == node
    assert node['standard_admission']['census_final_text_differs_factory'] == 21
    assert node['standard_admission']['census_final_text_differs_factory_nfd'] == 3
    add = tm.load_rows(tm.validate(a.out/'add_mix.json'), 'train')
    corr = tm.load_rows(tm.validate(a.out/'add_corr_mix.json'), 'train')
    overlay = labels.check_overlay(node['versions'])
    ids = {r['line_id'] for pool in add for r in pool}
    assert ids & set(overlay['ru1_v3_edits']['rows'])
    assert not ids & set(overlay['n1_v1_w1']['rows'])
    stats = read_json(a.out/'substitution.json')
    assert stats['unmatched']['n1_v1_w1'] == sorted(overlay['n1_v1_w1']['rows'])
    for before, after in zip(add, corr):
        for raw, fixed in zip(before, after):
            assert raw['image_png'] == fixed['image_png'] and raw['line_id'] == fixed['line_id']
            assert 'text' not in raw and 'text' not in fixed
    assert node['draw_contract']['nonlabel_byte_identical']
    assert all(tm.load_rows(tm.validate(path, role='eval'), 'reserved') for name,path in node['instruments'].items())


def test_real_heads_source_receipts_and_size():
    """Keep native metadata portable, hash-bound and within the package budget."""
    sources = read_json(REAL_HEAD/'SOURCES.json')['sources']
    files = [p for p in REAL_HEAD.rglob('*') if p.is_file()]
    assert sum(p.stat().st_size for p in files) < 2_000_000
    for name, spec in sources.items():
        assert sha256(REAL_HEAD/name) == spec['sample_sha256']
        assert len(spec['source_sha256']) == 64 and spec['source_path'].startswith('/iopsstor/')
        assert spec['extraction_command']
        if spec['rows'] is not None:
            rows = real_head(name.removesuffix('.gz'))
            assert len(rows) == spec['rows'] <= 50
            assert sorted(set().union(*(r.keys() for r in rows))) == spec['keys']


# R3J remains in the unchanged package-suite command.
@pytest.fixture
def r3j_export(real_head_setup, tmp_path):
    import shutil
    from scripts.ops.e4_wave2_deploy import receipt_template
    a, suite, train = real_head_setup
    # Final-input metadata for proof dependency tests; scorer execution is outside
    # this projection. Use an explicitly bound import-only scorer fixture.
    scorer = tmp_path/'scorer'; (scorer/'bench').mkdir(parents=True)
    (scorer/'bench/__init__.py').write_text('')
    (scorer/'bench/benchmark_suite.py').write_text('# Import-only proof fixture; never scores.\n')
    (scorer/'bench/benchmark_suite.py').chmod(0o644)
    binding = tmp_path/'scorer_binding.json'
    atomic_json(binding, dict(files={str(p.relative_to(scorer)):sha256(p) for p in scorer.rglob('*.py')}))
    cfg = read_json(a.inputs)
    cfg.update(status='FINAL', benchmark_scorer_root=str(scorer), benchmark_scorer_binding=pin(binding),
               training_inventories={arm:pin(train) for arm in r3.ARMS},
               benchmark_0_2=dict(**pin(suite), seal_receipt=r3.seal_receipt(pin(suite)),
                                  exposure={arm:dict(hits=[]) for arm in r3.ARMS}))
    atomic_json(a.inputs, cfg)
    root = tmp_path/'export'
    for folder in ('bench','train','rec','factory','codec','pipeline','assets','composer','scripts','labels'):
        source = w.ROOT/folder
        if source.exists():
            shutil.copytree(source, root/folder, ignore=shutil.ignore_patterns('__pycache__','target','.DS_Store','tests','*.ttf','*.otf','*.pdf'))
    shutil.copyfile(w.ROOT/'VERIFY.sh', root/'VERIFY.sh')
    atomic_json(root/w.AMENDMENT_POLICY, dict(amendment_b=True))
    shutil.copytree(a.registry.parent, root/'labels', dirs_exist_ok=True)
    draw = dict(epochs={str(e):dict(class_source_counts={}) for e in range(1,9)})
    drawpath = a.campaign/'v2-codec/draw.json'; atomic_json(drawpath,draw)
    val = a.out.parent/'val/mix.json'; ev = a.out.parent/'eval/mix.json'
    assets = dict(recovered_mix=pin(train),val_v2=pin(val),codec_v1=pin(root/'codec/v1.json'),
                  codec_v2=pin(root/'codec/v2.json'),draw_v_a=pin(drawpath),draw_v_b=pin(drawpath),draw_v_c=pin(drawpath))
    release_path = a.campaign/'v2-codec/release.json'
    atomic_json(release_path,dict(schema='e4-campaign1-release-v1',tag='v2-codec',status='frozen',
        v2_asis=w.base.ASIS,F1='not-applicable: authorized as-is wave1b; no S1/label repair',assets=assets,input_inventory={}))
    # Fixture pins bind unchanged real head rows to fixture paths, as R3G does.
    labels = root/'bench/e4_wave1c.py'
    import re
    text = re.sub(r"(?m)^RELEASE = .*", 'RELEASE = '+repr(sha256(release_path)), labels.read_text())
    labels.write_text(text)
    from bench import e3_driver
    for name in e3_driver.INSTRUMENTS:
        target = a.prep/'mixes'/f'{name}_mix.json'; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ev,target)
    atomic_json(a.campaign/'v2-codec/common_intersection.json',dict(instruments={}))
    atomic_json(a.campaign/'v2-codec/full_coverage.json',dict(instruments={}))
    runtime = tmp_path/'runtime'; runtime.mkdir()
    import os,sys
    runtime_python=os.environ.get('E4_TEST_RUNTIME_PYTHON',sys.executable)
    # The local Torch 2.13 import creates a compiler TemporaryDirectory. Warm
    # external libraries before the proof's write guard; deployed modules are
    # still imported by the proof itself. Clariden's runtime needs no warmup.
    launcher=runtime/'preload.py'
    launcher.write_text('import sys,runpy\nimport torch,numpy,pyarrow,PIL.Image\nsys.argv=[x for x in sys.argv[1:] if x!="-B"]\nrunpy.run_path(sys.argv[0],run_name="__main__")\n')
    (runtime/'runtime.sh').write_text('E3_PYTHON=("'+runtime_python+'" -B "'+str(launcher)+'")\n')
    # Cluster launch commands are stat-only targets in local tests.
    commands = runtime/'bin'; commands.mkdir()
    for name in ('srun', 'scontrol', 'nvidia-smi'):
        command = commands/name; command.write_text('#!/bin/sh\nexit 99\n'); command.chmod(0o755)
    binary = root/'factory/target/release/linefactory'; binary.parent.mkdir(parents=True)
    binary.write_text('#!/bin/sh\nexit 99 # never launched by load proof\n'); binary.chmod(0o755)
    def seal():
        from scripts.ops.e4_wave2_package import payload_mode
        for path in root.rglob('*'):
            if path.is_file(): path.chmod(payload_mode(str(path.relative_to(root))))
        binary.chmod(0o755)
        (root/'LINEFACTORY_SHA256SUMS').write_text(''.join(sha256(root/name)+'  '+name+'\n'
            for name in ('factory/Cargo.lock', 'factory/target/release/linefactory')))
        files = sorted(p for p in root.rglob('*') if p.is_file() and p.name not in ('DEPLOY_SHA256SUMS','DEPLOY_RECEIPT.json','DEPLOY_SHA256.txt','LINEFACTORY_SHA256SUMS','linefactory'))
        raw = ''.join(sha256(p)+'  '+str(p.relative_to(root))+'\n' for p in files)
        (root/'DEPLOY_SHA256SUMS').write_text(raw)
        alias=root/'out/e4/wave2_prep/DEPLOY_SHA256.txt';alias.parent.mkdir(parents=True,exist_ok=True);alias.write_text(raw)
        atomic_json(root/'DEPLOY_RECEIPT.json',dict(receipt_template(root,'a'*40), linefactory_sha256=sha256(binary)))
    seal()
    import os
    env=dict(os.environ,E4_ROOT=str(root),PYTHONPATH=str(root),E4_INPUTS=str(a.inputs),W=str(runtime),
             PATH=str(commands)+os.pathsep+os.environ['PATH'], E4_TEST_LAUNCHER=str(launcher), E4_CAMPAIGN=str(a.campaign),E4_PREP=str(a.prep),PYTHONDONTWRITEBYTECODE='1')
    return root,a,env,seal


@pytest.mark.parametrize('kind',('inventory','smoke','preflight','job01','job02','job03','aggregate'))
def test_r3j_real_head_deployed_proof(r3j_export,kind):
    import subprocess,sys
    root,a,env,_=r3j_export
    p=subprocess.run([env.get('E4_TEST_RUNTIME_PYTHON',sys.executable),'-B',env['E4_TEST_LAUNCHER'],str(root/'scripts/ops/e4_wave2_load_proof.py'),
        '--root',str(root),'--inputs',str(a.inputs),'--kind',kind],env=env,capture_output=True,text=True)
    assert p.returncode==0,p.stdout+p.stderr
    receipt=json.loads(p.stdout.splitlines()[0])
    assert not receipt['failures'] and receipt['population_reads'] is False and receipt['remote_writes'] is False
    if kind in ('inventory', 'smoke', 'preflight'):
        assert receipt['result'] == 'ok:stops_before_population_read:' + read_json(a.inputs)['census05']['records']['path']
        assert receipt['needs'] == []
    elif kind in ('job01', 'job02', 'job03'):
        assert receipt['needs'] == ['out/e4/wave2/preflight/PREFLIGHT_DONE.json']
    else:
        assert set(receipt['needs']) == {f'out/e4/wave2/{job}/{name}' for job in ('job01','job02')
                                        for name in ('COMPLETE.json','node_binding.json')}
    assert any(step.startswith('mix:') for step in receipt['steps'])
    assert 'training_runtime_imports' in receipt['steps']


@pytest.mark.parametrize('fault',('good','missing_manifest_path','missing_mix','missing_state','missing_commit','missing_root','missing_manifest_sha256'))
def test_r3j_verify_package(r3j_export,fault):
    import subprocess
    root,a,env,_=r3j_export
    if fault.startswith('missing_') and fault!='missing_mix':
        path=root/'DEPLOY_RECEIPT.json';obj=read_json(path);obj.pop(fault.removeprefix('missing_'));atomic_json(path,obj)
    elif fault=='missing_mix':
        (a.out.parent/'old/mix.json').unlink()
    p=subprocess.run(['bash',str(root/'VERIFY.sh'),'package'],env=env,capture_output=True,text=True)
    assert (p.returncode==0)==(fault=='good'),p.stdout+p.stderr
    assert ('VERIFY_PACKAGE_OK' in p.stdout)==(fault=='good')
    if fault!='good': assert 'VERIFY_LOAD_FAIL:' in p.stdout,p.stdout+p.stderr


def test_r3j_deploy_template_and_empty_destination(tmp_path):
    import io,tarfile
    from scripts.ops.e4_wave2_deploy import receipt_template,extract_empty,MANIFEST_PATH
    root=tmp_path/'root';root.mkdir();(root/'existing').write_text('preserve')
    with tarfile.open(fileobj=io.BytesIO(),mode='w') as archive:
        with pytest.raises(ValueError,match='NONEMPTY_DESTINATION'):extract_empty(root,archive)
    assert (root/'existing').read_text()=='preserve'
    manifest=root/MANIFEST_PATH;manifest.parent.mkdir(parents=True);manifest.write_text('')
    (root/'DEPLOY_SHA256SUMS').write_text('')
    receipt=receipt_template(root,'a'*40)
    assert set(receipt)=={'state','root','commit','manifest_sha256','manifest_path'}
    assert receipt['manifest_path']==MANIFEST_PATH


@pytest.mark.parametrize('fault',('fields','schema','seed','codec','created_by','notes','components','component_object',
    'fraction','nan','fraction_sum','unknown_kind','real_fields','source','partition','real_kind','real_codec',
    'real_inventory','missing_info','missing_shard','extra_shard','empty_hashes',
    'synthetic_fields','recipe','build_recipe','audit','synthetic_kind','synthetic_codec',
    'recovery_spec','recovery_codec','recovery_hash','recovery_schema','recovery_seed',
    'replay_spec','replay_hash','replay_schema','replay_contract','replay_fractions',
    'overlay_role','overlay_codec','overlay_fields','overlay_registry_hash','overlay_codec_hash','overlay_version'))
def test_r3j_metadata_matches_full_before_rows(real_head_setup,monkeypatch,fault):
    a,_,path=real_head_setup
    mix=read_json(path);role='train';c=mix['components'][0]
    folder=Path(c.get('build_dir',c.get('shard_dir')));info=read_json(folder/'build_info.json')
    if fault=='fields':mix['unexpected']=True
    elif fault=='schema':mix['schema_version']=2
    elif fault=='seed':mix['seed']=-1
    elif fault=='codec':mix['codec_version']=''
    elif fault=='created_by':mix['created_by']=''
    elif fault=='notes':mix['notes']=None
    elif fault=='components':mix['components']=[]
    elif fault=='component_object':mix['components'][0]=None
    elif fault=='fraction':c['fraction']=-1
    elif fault=='nan':c['fraction']=float('nan')
    elif fault=='fraction_sum':c['fraction']/=2
    elif fault=='unknown_kind':c['kind']='unknown'
    elif fault=='missing_info':(folder/'build_info.json').unlink()
    elif fault=='missing_shard':next(folder.rglob('shard-*.parquet')).unlink()
    elif fault=='extra_shard':(folder/'train/shard-extra.parquet').touch()
    elif fault in ('real_fields','source','partition','real_kind','real_codec','real_inventory','empty_hashes'):
        c=next(c for c in mix['components'] if c['kind']=='real');folder=Path(c['shard_dir']);info=read_json(folder/'build_info.json')
        if fault=='real_fields':c['extra']=1
        elif fault=='source':c['source']=''
        elif fault=='partition':c['partition_id']=''
        elif fault=='real_kind':info['kind']='wrong'
        elif fault=='real_codec':info['codec_version']='wrong'
        elif fault=='real_inventory':info['shard_sha256']={}
        elif fault=='empty_hashes':c['shard_sha256']=info['shard_sha256']={}
        atomic_json(folder/'build_info.json',info)
    elif fault in ('synthetic_fields','recipe','build_recipe','audit','synthetic_kind','synthetic_codec'):
        c=next(c for c in mix['components'] if c['kind']=='synthetic');folder=Path(c['build_dir']);info=read_json(folder/'build_info.json')
        if fault=='synthetic_fields':c['extra']=1
        elif fault=='recipe':c['recipe_sha256']='0'*64
        elif fault=='build_recipe':info['recipe_sha256']='0'*64
        elif fault=='audit':info['audit_ok']=False
        elif fault=='synthetic_kind':info['kind']='real'
        elif fault=='synthetic_codec':info['codec_version']='wrong'
        atomic_json(folder/'build_info.json',info)
    elif fault.startswith('recovery_'):
        plan=path.parent/'recovery.json';atomic_json(plan,dict(schema='e4-codec-recovery-v1',seed=mix['seed'],old_counts=[1]*len(mix['components'])))
        mix['codec_recovery']=pin(plan)
        if fault=='recovery_spec':mix['codec_recovery']={}
        elif fault=='recovery_codec':mix['codec_version']='v1'
        elif fault=='recovery_hash':mix['codec_recovery']['sha256']='0'*64
        elif fault=='recovery_schema':atomic_json(plan,dict(schema='wrong'));mix['codec_recovery']=pin(plan)
        elif fault=='recovery_seed':obj=read_json(plan);obj['seed']+=1;atomic_json(plan,obj);mix['codec_recovery']=pin(plan)
    elif fault.startswith('replay_'):
        plan=path.parent/'replay.json.gz'
        obj=dict(schema='e4-matched-replay-v1',seed=mix['seed'],replay_component=len(mix['components'])-1,
            base_components=len(mix['components'])-1,base_fractions=[c['fraction'] for c in mix['components'][:-1]])
        if fault=='replay_schema':obj['schema']='bad'
        with gzip.open(plan,'wt') as stream:json.dump(obj,stream)
        mix['matched_replay']=pin(plan)
        if fault=='replay_spec':mix['matched_replay']={}
        elif fault=='replay_hash':mix['matched_replay']['sha256']='0'*64
        elif fault=='replay_fractions':
            # Reach the fraction check with a valid replay component contract.
            old=mix['components'][-1]['fraction'];mix['components'][-1]['fraction']=.1
            scale=.9/(1-old)
            for item in mix['components'][:-1]:item['fraction']*=scale
    elif fault.startswith('overlay_'):
        mix['label_versions']=w.labels.overlay_spec(a.registry,['ru1_v3_edits','n1_v1_w1'],w.CODEC)
        if fault=='overlay_role':role='eval'
        elif fault=='overlay_codec':mix['codec_version']='v1'
        elif fault=='overlay_fields':mix['label_versions']['extra']=1
        elif fault=='overlay_registry_hash':mix['label_versions']['registry_sha256']='0'*64
        elif fault=='overlay_codec_hash':mix['label_versions']['codec_sha256']='0'*64
        elif fault=='overlay_version':mix['label_versions']['versions']=['unregistered']
    if fault in ('overlay_codec','recovery_codec'):
        # Reach the overlay/recovery constraint, rather than an earlier build
        # codec mismatch (row bytes are deliberately never examined here).
        for component in mix['components']:
            directory=Path(component.get('build_dir',component.get('shard_dir')))
            receipt=read_json(directory/'build_info.json');receipt['codec_version']=mix['codec_version']
            atomic_json(directory/'build_info.json',receipt)
    path.write_text(json.dumps(mix))
    def no_population(*args,**kw):raise AssertionError('population read attempted')
    monkeypatch.setattr(tm,'shard_inventory',no_population)
    monkeypatch.setattr(tm,'load_rows',no_population)
    errors=[]
    for validator in (tm.validate_metadata,tm.validate):
        with pytest.raises((ValueError,KeyError,OSError,TypeError)) as raised:validator(path,role=role)
        errors.append((type(raised.value),str(raised.value)))
    assert errors[0]==errors[1]


def test_r3j_metadata_skips_bytes_full_still_hashes(real_head_setup,monkeypatch):
    _,_,path=real_head_setup
    meta=tm.validate_metadata(path)
    assert tm.validate(path)==meta
    folder=Path(meta['components'][0].get('build_dir',meta['components'][0].get('shard_dir')))
    next(folder.rglob('shard-*.parquet')).write_bytes(b'changed population bytes')
    assert tm.validate_metadata(path)==meta
    with pytest.raises(tm.MixError,match='hash mismatch'):tm.validate(path)


def test_r3j_nonpayload_map_and_handoff():
    from scripts.ops.e4_wave2_package import deploy_paths
    prefix='docs/ocr_program_2026-10-06/e4_wave2/'
    assert deploy_paths([prefix+'LOAD_PATH_MAP.md',prefix+'HANDOFF.md',prefix+'PREREGISTRATION.md']) == [prefix+'PREREGISTRATION.md']


def test_r3j_committed_remote_deployer_program(tmp_path):
    import io,tarfile,subprocess,sys,ast
    from scripts.ops.e4_wave2_deploy import remote_program,MANIFEST_PATH
    root=tmp_path/'deployment'
    blob=b'committed fixture bytes'
    lock=b'fixture lock'
    raw=hashlib.sha256(blob).hexdigest()+'  example.py\n'+hashlib.sha256(lock).hexdigest()+'  factory/Cargo.lock\n'
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        for name,content in [('example.py',blob),('factory/Cargo.lock',lock),('DEPLOY_SHA256SUMS',raw.encode()),(MANIFEST_PATH,raw.encode())]:
            info=tarfile.TarInfo(name);info.size=len(content);archive.addfile(info,io.BytesIO(content))
    work=tmp_path/'work'; work.mkdir()
    cargo=work/'cargo'
    cargo.write_text('#!/bin/bash\nset -eu\n[[ "$*" == "build --release --locked --manifest-path "* ]]\n'
        '[[ "$CARGO_HOME" == "'+str(root)+'/build-cache/cargo" ]]\n'
        '[[ "$TMPDIR" == "'+str(root)+'/build-cache/tmp" ]]\n'
        '[[ "$CARGO_TARGET_DIR" == "'+str(root)+'/factory/target" ]]\n'
        'mkdir -p "'+str(root)+'/factory/target/release"\n'
        'printf "#!/bin/sh\\nexit 0\\n" > "'+str(root)+'/factory/target/release/linefactory"\n'
        'chmod +x "'+str(root)+'/factory/target/release/linefactory"\n')
    cargo.chmod(0o755)
    (work/'runtime.sh').write_text('export PATH="'+str(work)+':$PATH"\n'
        'export CARGO_TARGET_DIR=/outside-package-target CARGO_HOME=/outside-cargo TMPDIR=/outside-tmp\n')
    code=remote_program(root,'b'*40,work)
    ast.parse(code,feature_version=(3,6)) # extraction/build wrapper runs under login Python
    p=subprocess.run([sys.executable,'-B','-c',code],input=buffer.getvalue(),capture_output=True)
    assert p.returncode==0,p.stderr
    result=json.loads(p.stdout)
    assert result['receipt']['manifest_path']==MANIFEST_PATH
    assert result['readback']==raw.splitlines()
    assert read_json(root/'DEPLOY_RECEIPT.json')==result['receipt']
    assert result['receipt']['linefactory_sha256']==sha256(root/'factory/target/release/linefactory')
    assert (root/'LINEFACTORY_SHA256SUMS').read_text()==''.join(sha256(root/name)+'  '+name+'\n'
        for name in ('factory/Cargo.lock','factory/target/release/linefactory'))
    # The same transport refuses an already populated root without edits.
    before=(root/'DEPLOY_RECEIPT.json').read_bytes()
    p=subprocess.run([sys.executable,'-B','-c',code],input=buffer.getvalue(),capture_output=True)
    assert p.returncode and b'NONEMPTY_DESTINATION' in p.stderr
    assert (root/'DEPLOY_RECEIPT.json').read_bytes()==before


def test_r3j_metadata_single_path_structure():
    import ast,inspect
    tree=ast.parse(inspect.getsource(tm.validate))
    names=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
    assert names.count('validate_metadata')==1 and names.count('shard_inventory')==1
    # The only full-only failure is digest/content mismatch; every metadata
    # failure necessarily comes from the identical shared implementation.
    raises=[n for n in ast.walk(tree) if isinstance(n,ast.Raise)]
    assert len(raises)==1 and 'shard hash mismatch' in inspect.getsource(tm.validate)


@pytest.mark.parametrize('fault,reason',[
    ('fields','legacy_eval fields'),('train','eval/transfer-only'),('role','eval/transfer-only'),
    ('provenance','provenance_status'),('disclosure','disclosure'),('recipe','must be a SHA-256'),
    ('build_recipe','recipe_sha256 mismatch'),('codec','codec_version mismatch'),
    ('role_name','unknown mix role'),('build_path','required nonempty path'),
    ('missing_field','mix fields'),('nonobject','expected an object'),('malformed','cannot read JSON')])
def test_r3j_remaining_metadata_error_paths(real_head_setup,monkeypatch,fault,reason):
    _,_,path=real_head_setup
    mix=read_json(path);original=next(c for c in mix['components'] if c['kind']=='synthetic')
    directory=Path(original['build_dir']);info=read_json(directory/'build_info.json')
    component=dict(kind='legacy_eval',shard_dir=str(directory),shard_sha256=info['shard_sha256'],
        recipe_sha256=info['recipe_sha256'],role='eval',provenance_status='unprovenanced_recipe',
        disclosure='literal historical provenance',fraction=1.)
    mix['components']=[component];role='eval'
    if fault=='fields':component['extra']=1
    elif fault=='train':role='train'
    elif fault=='role':component['role']='train'
    elif fault=='provenance':component['provenance_status']='made-up'
    elif fault=='disclosure':component['disclosure']=''
    elif fault=='recipe':component['recipe_sha256']='invalid'
    elif fault=='build_recipe':component['recipe_sha256']='0'*64
    elif fault=='codec':info['codec_version']='wrong';atomic_json(directory/'build_info.json',info)
    elif fault=='role_name':role='other'
    elif fault=='build_path':component['shard_dir']=''
    elif fault=='missing_field':mix.pop('notes')
    elif fault=='nonobject':mix=[]
    path.write_text('invalid JSON' if fault=='malformed' else json.dumps(mix))
    def forbidden(*args,**kw):raise AssertionError('population bytes read')
    monkeypatch.setattr(tm,'shard_inventory',forbidden)
    monkeypatch.setattr(tm,'load_rows',forbidden)
    errors=[]
    for validator in (tm.validate_metadata,tm.validate):
        with pytest.raises(ValueError,match=reason) as exc:validator(path,role=role)
        errors.append((type(exc.value),str(exc.value)))
    assert errors[0]==errors[1]


@pytest.mark.parametrize('fault', ('no_amendment', 'missing_asset', 'changed_policy', 'unbound_policy', 'missing_policy', 'missing_binding'))
def test_r3n_proof_dependencies_and_load_failures(r3j_export, fault):
    import subprocess, sys
    root, a, env, seal = r3j_export
    policy = root/w.AMENDMENT_POLICY
    if fault == 'no_amendment':
        policy.unlink(); seal()
    elif fault == 'missing_asset':
        Path(read_json(a.inputs)['census05']['records']['path']).unlink()
    elif fault == 'missing_policy':
        policy.unlink()
    elif fault == 'changed_policy':
        atomic_json(policy, dict(amendment_b=False))
    elif fault == 'unbound_policy':
        policy.unlink(); seal(); atomic_json(policy, dict(amendment_b=True))
    else:
        cfg = read_json(a.inputs); del cfg['benchmark_scorer_binding']; atomic_json(a.inputs, cfg)
    kind = 'aggregate' if fault == 'no_amendment' else 'smoke'
    p = subprocess.run([env.get('E4_TEST_RUNTIME_PYTHON', sys.executable), '-B', env['E4_TEST_LAUNCHER'],
        str(root/'scripts/ops/e4_wave2_load_proof.py'), '--root', str(root), '--inputs', str(a.inputs),
        '--kind', kind], env=env, capture_output=True, text=True)
    receipt = json.loads(p.stdout.splitlines()[0])
    if fault == 'no_amendment':
        assert p.returncode == 0, p.stdout+p.stderr
        assert set(receipt['needs']) == {f'out/e4/wave2/{job}/{name}' for job in ('job01','job02','job03')
                                        for name in ('COMPLETE.json','node_binding.json')}
    else:
        assert p.returncode == 2, p.stdout+p.stderr
        assert receipt['result'].startswith('FAIL:') and receipt['failures']
        assert not receipt['needs']
    assert receipt['population_reads'] is False and receipt['remote_writes'] is False


@pytest.mark.parametrize('kind', ('job01', 'job02', 'job03'))
def test_r3n_preflight_is_the_only_run_predecessor(r3j_export, kind):
    import subprocess, sys
    root, a, env, _ = r3j_export
    # A predecessor receipt with no produced load assets; the current
    # allocation's node is absent and must not be requested or fabricated.
    atomic_json(root/'out/e4/wave2/preflight/PREFLIGHT_DONE.json', dict(state='DONE', mode='PRODUCTION'))
    p = subprocess.run([env.get('E4_TEST_RUNTIME_PYTHON', sys.executable), '-B', env['E4_TEST_LAUNCHER'],
        str(root/'scripts/ops/e4_wave2_load_proof.py'), '--root', str(root), '--inputs', str(a.inputs),
        '--kind', kind], env=env, capture_output=True, text=True)
    receipt = json.loads(p.stdout.splitlines()[0])
    assert p.returncode == 0, p.stdout+p.stderr
    assert receipt['needs'] == [] and receipt['failures'] == []
    assert receipt['result'] == 'ok:stops_before_population_read:' + read_json(a.inputs)['census05']['records']['path']

# R3P's audit follows local imports (including lazy imports), then captures every
# subprocess/os.exec call and every generic run() dispatcher. Source hashes of
# argument expressions catch a changed target at an existing call as well.
def r3p_launch_sites(root):
    import ast
    pending = ['bench/e4_wave2.py', 'bench/e4_wave2_r3.py',
               'scripts/ops/e4_wave2_gate.py', 'scripts/ops/e4_wave2_load_proof.py',
               'scripts/ops/e4_wave2_executables.py']
    visited, sites = set(), {}
    while pending:
        name = pending.pop()
        if name in visited: continue
        visited.add(name)
        tree = ast.parse((root/name).read_text())
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import): modules = [a.name for a in node.names]
            if isinstance(node, ast.ImportFrom):
                base = node.module or ''
                modules = [base, *[base+'.'+a.name for a in node.names]]
            for module in modules:
                for candidate in (module.replace('.', '/')+'.py', 'train/'+module.replace('.', '/')+'.py'):
                    if (root/candidate).is_file() and candidate.startswith(('bench/','train/','scripts/')):
                        pending.append(candidate)
            if not isinstance(node, ast.Call): continue
            func = ast.unparse(node.func)
            if (func.startswith('subprocess.') and func.rsplit('.',1)[-1] in
                ('run','Popen','check_output','check_call','call','getoutput','getstatusoutput')
                or func.startswith('os.exec') or func in ('Popen','os.system','os.popen','run')):
                # Generic run() is the e1_common dispatcher (plus conservative
                # same-named functions). Keep the full expression in the audit.
                expression = ast.unparse(node)
                key = name+':'+expression
                sites[key] = node.lineno
    # Shell lines are reviewed in full, not just srun/bash: this catches added
    # command substitutions and command launches, even to an existing target.
    for path in sorted((root/'scripts/clariden').glob('e4_wave2*')):
        if path.suffix not in ('.sbatch','.sh'): continue
        for n, line in enumerate(path.read_text().splitlines(),1):
            line = line.strip()
            if line and not line.startswith('#'):
                sites[str(path.relative_to(root))+':'+line] = n
    return sites

@pytest.mark.parametrize('fault', ('missing', 'nonexec', 'sha', 'receipt', 'lock'))
def test_r3p_verify_executable_faults(r3j_export, fault):
    import subprocess
    root,a,env,_ = r3j_export
    binary = root/'factory/target/release/linefactory'
    if fault == 'missing': binary.unlink()
    elif fault == 'nonexec': binary.chmod(0o644)
    elif fault == 'sha': binary.write_text('changed binary')
    elif fault == 'lock': (root/'factory/Cargo.lock').write_text('changed lock')
    else:
        receipt = read_json(root/'DEPLOY_RECEIPT.json');receipt['linefactory_sha256']='0'*64
        atomic_json(root/'DEPLOY_RECEIPT.json',receipt)
    p = subprocess.run(['bash', str(root/'VERIFY.sh'), 'package'],env=env,capture_output=True,text=True)
    assert p.returncode == 2, p.stdout+p.stderr
    assert 'VERIFY_LOAD_FAIL:executable:linefactory' in p.stdout
    assert 'VERIFY_PACKAGE_OK' not in p.stdout


@pytest.mark.parametrize('kind', ('inventory','smoke','preflight','job01','job02','job03','aggregate'))
@pytest.mark.parametrize('target', ('linefactory', 'worker', 'trainer', 'scorer', 'checker'))
def test_r3p_proof_missing_subprocess_target(r3j_export,kind,target):
    import subprocess,sys
    root,a,env,_=r3j_export
    paths = dict(checker=root/'scripts/ops/e4_wave2_executables.py',linefactory=root/'factory/target/release/linefactory',worker=root/'bench/e4_wave2.py',
                 trainer=root/'train/train.py',scorer=Path(read_json(a.inputs)['benchmark_scorer_root'])/'bench/benchmark_suite.py')
    paths[target].unlink()
    p=subprocess.run([env.get('E4_TEST_RUNTIME_PYTHON',sys.executable),'-B',env['E4_TEST_LAUNCHER'],
        str(root/'scripts/ops/e4_wave2_load_proof.py'),'--root',str(root),'--inputs',str(a.inputs),'--kind',kind],
        env=env,capture_output=True,text=True)
    expected = dict(checker='scripts/ops/e4_wave2_executables.py',linefactory='linefactory',worker='bench/e4_wave2.py',trainer='train/train.py',scorer='scorer')[target]
    assert p.returncode == 2,p.stdout+p.stderr
    receipt=json.loads(p.stdout.splitlines()[0])
    assert receipt['result'].startswith('FAIL:executable:'),receipt['result']
    assert any(x['step']=='executable:'+expected for x in receipt['failures'])
    assert 'VERIFY_LOAD_FAIL:executable:'+expected in p.stdout


def test_r3p_git_free_custody_never_launches_git(r3j_export,monkeypatch):
    root,_,env,_=r3j_export
    monkeypatch.setenv('E4_ROOT',str(root))
    monkeypatch.setattr(tm,'git',lambda *a,**kw:pytest.fail('git invoked in exported deployment'))
    assert tm.exported_source(root) is not None
    assert tm.committed_recipes(root)
    assert tm.source_head(root)=='a'*40
    from scripts.ops.e4_wave2_gate import source_commit
    import subprocess
    monkeypatch.setattr(subprocess,'check_output',lambda *a,**kw:pytest.fail('subprocess invoked in git-free custody'))
    assert source_commit(root)=='a'*40


def test_r3p_package_modes_and_no_job_build():
    from scripts.ops.e4_wave2_package import payload_mode
    from scripts.ops.e4_wave2_executables import PAYLOAD_TARGETS
    for name in PAYLOAD_TARGETS: assert payload_mode(name)&0o111
    for path in (w.ROOT/'scripts/clariden').glob('e4_wave2*.sbatch'):
        assert 'cargo build' not in path.read_text()


def test_r3p_executable_map_equals_grep_derived_closure():
    import re
    from scripts.ops.e4_wave2_executables import TARGET_IDS, TARGET_KINDS
    text=(w.ROOT/'docs/ocr_program_2026-10-06/e4_wave2/LOAD_PATH_MAP.md').read_text()
    audit=json.loads(re.search(r'<!-- R3P_LAUNCH_AUDIT\n(.*?)\n-->',text,re.S)[1])
    sites=r3p_launch_sites(w.ROOT)
    assert set(audit['sites'])==set(sites), 'new/changed subprocess or shell call needs executable-map review'
    # Each grep-derived call has a reviewed expansion, or a reason proving it
    # outside the seven entry paths. The union must equal the executable table.
    derived={t for spec in audit['sites'].values() for t in spec['targets']}
    listed=set(re.findall(r'^\| `([^`]+)` \|',text.split('## R3P executable closure')[1].split('### Excluded')[0],re.M))
    assert derived==listed==set(TARGET_IDS)==set(TARGET_KINDS)
    observed = {}
    for site, spec in audit['sites'].items():
        assert set(spec['invocations']) == set(spec['targets'])
        for target, kind in spec['invocations'].items():
            assert TARGET_KINDS[target] == kind, site
            observed[target] = kind
            # Invocations are reviewed at these calls, including command builders.
            if kind == 'interpreter-run':
                assert any(token in site for token in ('source ', 'bash ', 'E3_PYTHON',
                    'sys.executable', 'child_command(', 'Popen(cmd', 'run(launch(', 'map(str, cmd)')), site
    assert observed == TARGET_KINDS


def test_r3p_audit_catches_new_call_and_new_import(tmp_path):
    # Minimal graph exercises recursive discovery, not a frozen filename list.
    (tmp_path/'bench').mkdir();(tmp_path/'scripts/ops').mkdir(parents=True)
    roots=['bench/e4_wave2.py','bench/e4_wave2_r3.py','scripts/ops/e4_wave2_gate.py',
           'scripts/ops/e4_wave2_load_proof.py','scripts/ops/e4_wave2_executables.py']
    for name in roots: (tmp_path/name).write_text('')
    assert r3p_launch_sites(tmp_path)=={}
    (tmp_path/'bench/e4_wave2.py').write_text('from bench import added\n')
    (tmp_path/'bench/added.py').write_text('import subprocess\nsubprocess.run(["new-target"])\n')
    sites=r3p_launch_sites(tmp_path)
    assert len(sites)==1 and 'new-target' in next(iter(sites))


@pytest.mark.parametrize('fault', ('good', 'direct_nonexec', 'interp_sha'))
def test_r3r_invocation_permissions_and_cache(r3j_export, fault):
    import subprocess
    from scripts.ops.e4_wave2_executables import PAYLOAD_TARGETS, TARGET_KINDS
    root, a, env, _ = r3j_export
    # Mode changes preserve content hashes. Scorer fixture is already 0644.
    for name in PAYLOAD_TARGETS: (root/name).chmod(0o644)
    cache = root/'build-cache/cargo'; cache.mkdir(parents=True)
    (cache/'unmanifested').write_text('post-extraction cache; outside source hash list')
    expected = None
    if fault == 'direct_nonexec':
        (root/'factory/target/release/linefactory').chmod(0o644)
        expected = 'linefactory'
    elif fault == 'interp_sha':
        scorer = Path(read_json(a.inputs)['benchmark_scorer_root'])/'bench/benchmark_suite.py'
        scorer.write_text('wrong sha; still readable\n')
        expected = 'scorer'
    p = subprocess.run(['bash', str(root/'VERIFY.sh'), 'package'], env=env,capture_output=True,text=True)
    if expected:
        assert p.returncode == 2, p.stdout+p.stderr
        assert 'VERIFY_LOAD_FAIL:executable:'+expected in p.stdout
        if fault == 'interp_sha': assert 'sha256 mismatch' in p.stdout
    else:
        assert p.returncode == 0, p.stdout+p.stderr
        receipt = json.loads(next(line for line in p.stdout.splitlines() if line.startswith('{')))
        assert {r['target']:r['invocation'] for r in receipt['executables']} == TARGET_KINDS
        assert all('exec' not in r['check'] and 'read' in r['check'] for r in receipt['executables']
                   if r['invocation'] == 'interpreter-run')


@pytest.mark.parametrize('mode', (0o644, 0o755))
def test_r3r_compute_cli_still_requires_exec(r3j_export, monkeypatch, mode):
    from scripts.ops.e4_wave2_executables import check
    root, a, env, _ = r3j_export
    for name in ('PATH', 'W'): monkeypatch.setenv(name, env[name])
    monkeypatch.setenv('SLURM_JOB_ID', 'fixture-only-no-scheduler-call')
    (Path(env['W'])/'bin/nvidia-smi').chmod(mode)
    failures = []
    def record(name, fn):
        try: fn()
        except Exception as exc: failures.append((name, str(exc)))
    results = check(root, read_json(a.inputs), record, 'smoke')
    assert bool(failures) == (mode == 0o644), failures
    if failures: assert failures[0][0] == 'executable:nvidia-smi'
    else: assert next(r for r in results if r['target']=='nvidia-smi')['check']=='exists/exec'
