import copy
import json
from pathlib import Path
import subprocess
import pytest
from greekocr.synth import recipe_registry, verify_recipe_sha, build_mix, validate_mix, assemble_mix, build_shards
from greekocr._vendor.train import mix

@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    directory = tmp_path/'synth'; (directory/'train').mkdir(parents=True)
    (directory/'train/shard-000.parquet').write_bytes(b'recorded shard custody fixture; not parquet')
    recipe = recipe_registry()['v5']
    def git(repo, *args):
        assert Path(repo) == tmp_path
        if args[0] == 'ls-files': return b'factory/recipe.v5.json\0'
        if args[0] == 'cat-file': return recipe.path.read_bytes()
        raise AssertionError(args)
    monkeypatch.setattr(mix,'git',git)
    info = dict(recipe_sha256=recipe.sha256,audit_ok=True,kind='synthetic',codec_version='v1',
                shard_sha256=mix.shard_inventory(directory))
    (directory/'build_info.json').write_text(json.dumps(info))
    manifest=tmp_path/'mix.json'
    component=dict(kind='synthetic',build_dir='synth',fraction=1.0)
    build_mix([component],manifest,repo=tmp_path)
    return directory,manifest,info


def test_registry_exact_source_identity():
    registry = recipe_registry()
    assert set(registry) == {'v5','v7','v8'}
    assert len({r.sha256 for r in registry.values()}) == 3
    for r in registry.values(): assert verify_recipe_sha(r) == r.sha256


def test_unregistered_recipe_needs_expected_hash(tmp_path):
    recipe=tmp_path/'custom.json';recipe.write_text('{}')
    with pytest.raises(mix.MixError,match='unregistered'): verify_recipe_sha(recipe)
    assert verify_recipe_sha(recipe,mix.sha256(recipe)) == mix.sha256(recipe)
    with pytest.raises(mix.MixError,match='mismatch'): verify_recipe_sha(recipe,'0'*64)


def test_committed_recipes_use_head_not_working_file(tmp_path,monkeypatch):
    (tmp_path/'factory').mkdir();(tmp_path/'factory/recipe.v5.json').write_text('dirty worktree')
    calls=[]
    def git(repo,*args):
        calls.append(args)
        return b'factory/recipe.v5.json\0factory/staged.json\0' if args[0]=='ls-files' else (
            b'{"target_total":1,"content_marginals":{}}' if args[-1]=='HEAD:factory/recipe.v5.json' else b'{}')
    monkeypatch.setattr(mix,'git',git)
    got=mix.committed_recipes(tmp_path)
    assert list(got.values())==['factory/recipe.v5.json']
    assert all(c[0]=='ls-files' or c[:2]==('cat-file','blob') for c in calls)


def test_mix_validated_copy_binds_receipt_and_shards(synthetic,tmp_path):
    root,path,_=synthetic
    got=validate_mix(path,repo=tmp_path)
    assert got['components'][0]['build_dir']==str(root)
    assert got['components'][0]['build_info_sha256']==mix.sha256(root/'build_info.json')
    assert 'build_info_sha256' not in json.loads(path.read_text())['components'][0]

@pytest.mark.parametrize('mutation,match',[
    ('recipe','recipe_sha256'),('audit','audit_ok'),('codec','codec_version'),('kind','non-synthetic'),
    ('receipt_inventory','nonempty shard_sha256'),('changed_shard','shard hash'),('new_shard','shard hash'),
    ('removed_shard','shard hash'),('unknown_field','synthetic fields'),('fraction','fractions sum'),
    ('nan','fraction must'),('missing_seed','mix fields'),('seed_bool','seed must'),('legacy','legacy_eval')])
def test_mix_failures_closed(synthetic,tmp_path,mutation,match):
    root,path,info=synthetic;obj=json.loads(path.read_text())
    if mutation=='recipe': obj['components'][0]['recipe_sha256']='0'*64
    if mutation=='audit': info['audit_ok']=False
    if mutation=='codec': info['codec_version']='v2'
    if mutation=='kind': info['kind']='real'
    if mutation=='receipt_inventory': info['shard_sha256']={}
    if mutation=='changed_shard': (root/'train/shard-000.parquet').write_bytes(b'changed')
    if mutation=='new_shard': (root/'train/shard-new.parquet').write_bytes(b'new')
    if mutation=='removed_shard': (root/'train/shard-000.parquet').unlink()
    if mutation=='unknown_field': obj['components'][0]['extra']=True
    if mutation=='fraction': obj['components'][0]['fraction']=.5
    if mutation=='nan': obj['components'][0]['fraction']=float('nan')
    if mutation=='missing_seed': obj.pop('seed')
    if mutation=='seed_bool': obj['seed']=True
    if mutation=='legacy': obj['components'][0]=dict(kind='legacy_eval',shard_dir='synth',shard_sha256=info['shard_sha256'],
        recipe_sha256=info['recipe_sha256'],role='eval',provenance_status='unprovenanced_recipe',disclosure='historical fixture',fraction=1)
    path.write_text(json.dumps(obj));(root/'build_info.json').write_text(json.dumps(info))
    with pytest.raises(mix.MixError,match=match):validate_mix(path,repo=tmp_path)


def test_failed_build_never_publishes_candidate(synthetic,tmp_path):
    root,_,info=synthetic;info['audit_ok']=False;(root/'build_info.json').write_text(json.dumps(info))
    path=tmp_path/'invalid.json'
    with pytest.raises(mix.MixError):build_mix([dict(kind='synthetic',build_dir='synth',fraction=1)],path,repo=tmp_path)
    assert not path.exists() and not path.with_name('invalid.json.candidate').exists()


def test_real_mix_requires_import_receipt(tmp_path,monkeypatch):
    monkeypatch.setattr(mix,'git',lambda *args:b'')
    root=tmp_path/'real';root.mkdir();(root/'shard-0.parquet').write_bytes(b'bound')
    info=dict(kind='real',partition_id='works-v1',codec_version='v1',shard_sha256=mix.shard_inventory(root))
    (root/'build_info.json').write_text(json.dumps(info))
    path=tmp_path/'real.json'
    build_mix([dict(kind='real',shard_dir='real',fraction=1,source='polyton_db')],path,repo=tmp_path)
    assert validate_mix(path,repo=tmp_path)['components'][0]['partition_id']=='works-v1'
    info['partition_id']='changed';(root/'build_info.json').write_text(json.dumps(info))
    with pytest.raises(mix.MixError,match='partition_id'):validate_mix(path,repo=tmp_path)


def test_sampling_largest_remainder_and_epochs():
    groups=[[dict(line_id=f'a{i}') for i in range(20)],[dict(line_id=f'b{i}') for i in range(20)]]
    first,counts=assemble_mix(groups,[.25,.75],0,max_rows=9)
    assert counts==[2,7] and len(first)==9
    assert first==assemble_mix(groups,[.25,.75],0,max_rows=9)[0]
    assert first!=assemble_mix(groups,[.25,.75],0,epoch=1,max_rows=9)[0]
    cycled,counts=assemble_mix([groups[0],groups[1][:1]],[.1,.9],0)
    assert counts==[2,19] and sum(r['_component']==1 for r in cycled)==19
    with pytest.raises(mix.MixError,match='empty'):assemble_mix([[]],[1],0)


def test_build_shards_command_and_receipt(tmp_path,monkeypatch):
    recipe=recipe_registry()['v7'];out=tmp_path/'out';seen=[]
    def run(command,**kwargs):
        seen.append((command,kwargs));(out/'reserved').mkdir(parents=True)
        (out/'reserved/shard-0.parquet').write_bytes(b'bound')
        (out/'build_info.json').write_text(json.dumps(dict(recipe_sha256=recipe.sha256,audit_ok=True,
          shard_sha256=mix.shard_inventory(out))))
    monkeypatch.setattr(subprocess,'run',run)
    receipt=build_shards('v7','/worker/linefactory',out,pool=tmp_path/'pool.jsonl',timeout=8)
    assert receipt['audit_ok'] and seen[0][0][1:3]==['build','--recipe'] and seen[0][1]['timeout']==8
    with pytest.raises(ValueError,match='fresh'):build_shards('v7','/worker/linefactory',out,pool='pool')


def test_trainer_refuses_custody_before_runtime(tmp_path,monkeypatch):
    from greekocr._vendor.train import train as trainer
    monkeypatch.setattr(trainer,'_runtime',lambda:pytest.fail('runtime reached invalid data'))
    assert trainer.main(['--mix',str(tmp_path/'absent.json')])==3
    assert not (tmp_path/'out').exists()
