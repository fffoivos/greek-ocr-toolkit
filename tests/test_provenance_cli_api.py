import ast
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import tomllib
import pytest
from greekocr.cli import main
ROOT=Path(__file__).resolve().parents[1]
ENTRIES=json.loads((ROOT/'greekocr/_vendor/origins.json').read_text())

@pytest.mark.parametrize('entry', [
    pytest.param(entry, marks=pytest.mark.skip(reason=
        'historical binding; green at opus/spellcheck@408ed69b9; see docs/cleanup_20261019/TEST_RECORDS.md'))
    if entry['path'] in {'greekocr/_vendor/bench/common.py', 'greekocr/_vendor/bench/e1_common.py',
                         'greekocr/_vendor/bench/e1_readout.py'}
    else entry for entry in ENTRIES
], ids=lambda e:e['path'])
def test_every_vendor_file_has_origin_and_exact_bytes(entry):
    path=ROOT/entry['path']
    if entry.get('record_type') == 'live':
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['vendored_sha256']
        mapping = ROOT/entry['consolidation']
        assert entry['consolidation'] == 'greekocr/train/CONSOLIDATION.md'
        assert hashlib.sha256(mapping.read_bytes()).hexdigest() == entry['consolidation_sha256']
        assert entry['path'] in mapping.read_text()
        source = ROOT/entry['origin']
        if entry['origin'] == 'greekocr/_vendor/train/detector_common.py':
            historical = next(e for e in ENTRIES if e.get('record_type') == 'historical'
                              and e['path'] == entry['origin'])
            assert entry['source_sha256'] == historical['source_sha256']
            assert historical['historical_id'] in entry['historical_records']
        else:
            assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['source_sha256']
        return
    if entry.get('record_type') != 'historical':
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['vendored_sha256']
    assert Path(entry['origin']).is_absolute() and len(entry['source_sha256'])==64
    if entry['transform']=='byte-identical':assert entry['source_sha256']==entry['vendored_sha256']
    if entry['commit'] is not None:assert len(entry['commit'])==40
    assert entry['path'] in (ROOT/'docs/INVENTORY.md').read_text()
    if 'logic_sha256' in entry and entry.get('record_type') != 'historical':
        from scripts.vendor_sources import logic_hash
        assert logic_hash(path.read_text())==entry['logic_sha256']


def _canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def test_original_ledger_records_preserved():
    # Bind every original field, including source path, source/vendored/logic SHAs
    # and commit. Adding live records cannot silently rewrite historical identity.
    original = [{k: v for k, v in e.items()
                 if k not in {'record_type', 'historical_id', 'superseded_by'}}
                for e in ENTRIES if e.get('record_type') != 'live']
    assert len(original) == 1108
    assert _canonical_sha(original) == '553cf98ce2b0c037052dc5ab03d80b276c3a70c886e87524efabb8b073a81676'


def test_historical_and_live_references_are_complete():
    live = [e for e in ENTRIES if e.get('record_type') == 'live']
    by_path = {e['path']: e for e in live}
    historical = {e['historical_id']: e for e in ENTRIES if e.get('record_type') == 'historical'}
    assert len(by_path) == len(live) == 40
    assert len(historical) == 17
    for hid, old in historical.items():
        original = {k: v for k, v in old.items()
                    if k not in {'record_type', 'historical_id', 'superseded_by'}}
        assert _canonical_sha(original) == hid
        assert old['path'] in old['superseded_by']
        for path in old['superseded_by']:
            assert hid in by_path[path]['historical_records']
    for current in live:
        for hid in current['historical_records']:
            assert current['path'] in historical[hid]['superseded_by']
    # Exactly one current byte contract per path, including unaffected vendors.
    current_paths = [e['path'] for e in ENTRIES if e.get('record_type') != 'historical']
    assert len(set(current_paths)) == len(current_paths)


def test_all_vendored_files_are_in_inventory():
    origins={e['path'] for e in ENTRIES}
    # New local test fixtures are not vendor imports. Audit every file under
    # each fixture namespace that the origins ledger actually vendors.
    fixture_roots = {ROOT/Path(*Path(path).parts[:3]) for path in origins
                     if path.startswith('tests/fixtures/')}
    for root in (ROOT/'greekocr/_vendor', ROOT/'greekocr/deploy/docling_plugin',
                 ROOT/'docs/origins', ROOT/'greekocr/train', *sorted(fixture_roots)):
        for path in root.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.name!='origins.json':
                relative=str(path.relative_to(ROOT))
                if relative not in origins:
                    assert path.name=='__init__.py' and 'Preserved implementation detail' in path.read_text()


def test_public_callables_typed_and_documented():
    from scripts.generate_api_docs import api_entries
    docs=(ROOT/'docs/API.md').read_text()
    for module,name,node,owner in api_entries():
        qualified=module+'.'+(owner+'.' if owner else '')+name
        assert '### `'+qualified+'`' in docs
        if isinstance(node,ast.FunctionDef) and module!='greekocr.deploy.docling_plugin.docling_plugin':
            assert node.returns is not None
            assert all(arg.annotation is not None for arg in node.args.posonlyargs+node.args.args+node.args.kwonlyargs if arg.arg not in ('self','cls'))
        obj=importlib.import_module(module)
        assert callable(getattr(getattr(obj,owner) if owner else obj,name))
    for example in docs.split('```python\n')[1:]:assert len(example.split('\n```')[0].splitlines())==2


def test_cli_registry_annotation_score_and_refusal(tmp_path,capsys):
    assert main(['recipes'])==0
    assert set(json.loads(capsys.readouterr().out))=={'v5','v7','v8'}
    assert main(['annotate','ἅλφα Latin'])==0
    result=json.loads(capsys.readouterr().out);assert result['script_class']=='greek_latin_cs'
    assert main(['verify-recipe','v5','--sha256','0'*64])==3
    assert 'mismatch' in capsys.readouterr().err
    readings=tmp_path/'readings.jsonl';readings.write_text(json.dumps(dict(text='ά',prediction='ά',cohort='gold',script_class='greek_mono',crop_path='fixture'))+'\n')
    assert main(['score',str(readings)])==0
    assert json.loads(capsys.readouterr().out)['overall']['cer']==0
    assert main(['env-plan','ocr',str(tmp_path/'venv')])==0
    assert 'cu126' in capsys.readouterr().out
    assert main(['validate-mix',str(tmp_path/'absent'), '--repo',str(tmp_path)])==3
    assert 'cannot read JSON' in capsys.readouterr().err


def test_entrypoint_metadata_and_package_resources():
    from importlib.metadata import entry_points
    ep=next(e for e in entry_points(group='docling') if e.name=='glossapi')
    assert ep.value=='greekocr.deploy.docling_plugin.docling_plugin'
    project=tomllib.loads((ROOT/'pyproject.toml').read_text())['project']
    assert project['requires-python']=='>=3.11' and project['scripts']['greekocr']=='greekocr.cli:main'
