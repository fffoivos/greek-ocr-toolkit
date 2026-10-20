"""Offline integration checks: split identity, all diagnostics, immutable inputs."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import pytest

from greekocr.harvest import line_pipeline_census as census
from greekocr.harvest import line_pipeline_census04 as c4
from greekocr.harvest.line_pipeline import canonical, digest, identity

D = Path(__file__).resolve().parents[1]
TOOLS = ('segmentation', 'polytonic', 'cyrillic', 'numerics', 'dashes', 'content_repair')
VERSIONS = {t: dict(version='0.8' if t == 'segmentation' else '0.1', digest=t) for t in TOOLS}


def write(path, value):
    path.write_text(json.dumps(value))
    return str(path)


def jsonl(path, rows):
    path.write_text(''.join(canonical(r)+'\n' for r in rows))
    return str(path)


def fixture(tmp_path):
    parent = dict(id='collect-v3-W1-fixture', format='collect-v3-features')
    rows = [dict(id=f'r{i}', page_id=f'elstat--book{i}--s001', source='elstat', label='1234',
                 crop_sha256=hex(i+10)[2:].zfill(64), primary_class='numerics_tables', script_class='nonletter') for i in range(4)]
    parent.update(path=jsonl(tmp_path/'rows.jsonl', rows), rows=len(rows))
    parent['sha256'] = census.file_sha(parent['path'])
    meta = dict(books={f'elstat--book{i}': dict(edition_id=f'e{i}', languages=['Greek'], scripts=['greek'],
                orthography='monotonic', provenance='offline fixture') for i in range(4)})
    config = dict(versions=write(tmp_path/'versions.json', dict(tools=VERSIONS)),
                  metadata=write(tmp_path/'metadata.json', meta), parents=[parent], corrections=[], final_policy={})
    return config, rows


def segment(row):
    return dict(tool_version='0.8', binding=identity(row), raw_text_sha256=digest(row['raw_text']),
                verdict='KEEP', reason='fixture', evidence=dict(characters=4,
                box_evidence=dict(row_frame=dict(length=30, height=10), prediction=dict(expected=4))),
                frame=dict(source_width=40, source_height=20))


def read_decisions(out):
    return [json.loads(s) for s in (out/'decisions.jsonl').read_text().splitlines()]


def pin_split(config, tmp_path):
    path = tmp_path/'split.jsonl'
    rows = [dict(parent_id=config['parents'][0]['id'], row_id=f'r{i}', edition_id=f'new-e{i}', split=s)
            for i, s in enumerate(('train', 'dev', 'test'))]
    jsonl(path, rows)
    config['split_input'] = dict(path=str(path), sha256=census.file_sha(path))
    return rows


def test_two_modes_absent_rows_and_input_preservation(tmp_path):
    config, _ = fixture(tmp_path)
    before = {p: Path(p).read_bytes() for p in (config['metadata'], config['parents'][0]['path'])}
    c4.run(config, tmp_path/'mode-i', execute=True, segmenter_factory=lambda: segment)
    first = read_decisions(tmp_path/'mode-i')
    assert all(d['disposition'] == 'HOLD' for d in first)
    pin_split(config, tmp_path)
    c4.run(config, tmp_path/'mode-ii', execute=True, segmenter_factory=lambda: segment)
    second = read_decisions(tmp_path/'mode-ii')
    assert [d['binding']['split'] for d in second] == ['train', 'dev', 'test', 'unassigned']
    assert second[0]['disposition'] == 'ADMIT' and second[3]['disposition'] == 'HOLD'
    assert len((tmp_path/'mode-ii/evaluation_diagnostics.jsonl').read_text().splitlines()) == 3
    assert len((tmp_path/'mode-ii/admitted_train.jsonl').read_text().splitlines()) == 1
    assert all(Path(p).read_bytes() == raw for p, raw in before.items())


def test_all_diagnostics_invariant_for_every_verdict(tmp_path):
    config, _ = fixture(tmp_path)
    pin_split(config, tmp_path)
    def varied(row):
        answer = segment(row)
        answer['verdict'] = {'r0': 'KEEP', 'r1': 'DROP', 'r2': 'UNCERTAIN', 'r3': 'KEEP'}[row['id']]
        return answer
    outputs = []
    for name, builder in [('normal', c4.diagnostics), ('removed', lambda *a: {}),
                          ('altered', lambda *a: dict(box_long_side=-1, box_height=100000, box_aspect_ratio=-1,
                           length_ratio=1e10, saved_characters=-7, is_cell=True, is_small_image=False,
                           is_numeric_output=False, reasons=['corrupt'], frozen_05=dict(verdict='DROP', reason='corrupt')))]:
        out = tmp_path/name
        c4.run(config, out, execute=True, segmenter_factory=lambda: varied, diagnostic_builder=builder)
        decisions = read_decisions(out)
        for d in decisions:
            d.pop('diagnostics')
            # Binding includes the source-code/config fingerprint, unchanged here.
        outputs.append(decisions)
    assert outputs[0] == outputs[1] == outputs[2]
    assert {d['disposition'] for d in outputs[0]} == {'ADMIT', 'DROP', 'HOLD'}


def test_cell_and_box_diagnostics_are_descriptive(tmp_path):
    config, rows = fixture(tmp_path)
    row = census.canonicalize(rows[0], config['parents'][0], json.loads(Path(config['metadata']).read_text()))
    d = dict(stages=[dict(stage='segmentation', result=segment(row))])
    result = c4.diagnostics(row, d, {})
    assert result['box_long_side'] == 30 and result['box_height'] == 10
    assert result['box_aspect_ratio'] == 3 and result['length_ratio'] == 1
    assert result['saved_characters'] == 4
    assert result['is_cell'] and result['is_small_image'] and result['is_numeric_output']
    assert result['frozen_05']['available'] is False


@pytest.mark.parametrize('problem', ['hash', 'duplicate', 'edition_conflict', 'proposal'])
def test_split_schema_rejects_bad_input(tmp_path, problem):
    config, _ = fixture(tmp_path)
    rows = pin_split(config, tmp_path)
    if problem == 'duplicate':
        rows.append(rows[0])
    elif problem == 'edition_conflict':
        rows[1]['edition_id'] = rows[0]['edition_id']
    elif problem == 'proposal':
        rows[0]['proposed_split'] = rows[0].pop('split')
    if problem != 'hash':
        jsonl(Path(config['split_input']['path']), rows)
        config['split_input']['sha256'] = census.file_sha(config['split_input']['path'])
    else:
        config['split_input']['sha256'] = '0'*64
    with pytest.raises((ValueError, KeyError)):
        c4.load_split(config['split_input'])


def test_correction_split_rebind_is_audited_and_original_is_checked(tmp_path):
    config, rows = fixture(tmp_path)
    metadata = json.loads(Path(config['metadata']).read_text())
    r = census.canonicalize(rows[0], config['parents'][0], metadata)
    record = dict(tool='numerics', tool_version='0.1', tool_digest='numerics', binding=identity(r),
                  raw_text_sha256=digest(r['raw_text']), status='verified_no_change', edits=[], evidence=dict(fixture=True))
    path = tmp_path/'correction.jsonl'
    jsonl(path, [record])
    release = dict(path=str(path), sha256=census.file_sha(path), format='line-tool-result-v1', tool='numerics',
                   parent_id=r['parent_id'], parent_manifest_sha256=config['parents'][0]['sha256'], status='released')
    config['corrections'] = [release]
    original = path.read_bytes()
    pin_split(config, tmp_path)
    c4.run(config, tmp_path/'bound', execute=True, segmenter_factory=lambda: segment)
    derived = next((tmp_path/'bound/split-bound-corrections').glob('*.jsonl'))
    rebound = json.loads(derived.read_text())
    assert rebound['binding']['split'] == 'train'
    assert rebound['evidence']['split_input_binding']['original_binding']['split'] == 'unassigned'
    assert rebound['status'] == record['status'] and rebound['edits'] == record['edits']
    assert path.read_bytes() == original
    record['binding']['crop_sha256'] = 'f'*64
    jsonl(path, [record]); release['sha256'] = census.file_sha(path)
    with pytest.raises(ValueError, match='different crop'):
        c4.run(config, tmp_path/'invalid', execute=True, segmenter_factory=lambda: segment)


def test_frozen_05_identity_and_verdict_reason(tmp_path):
    config, rows = fixture(tmp_path)
    r = census.canonicalize(rows[0], config['parents'][0], json.loads(Path(config['metadata']).read_text()))
    old = segment(r); old.update(tool_version='0.5', verdict='DROP', reason='frozen reason')
    path = tmp_path/'frozen.jsonl'
    jsonl(path, [dict(binding=identity(r), raw_text_sha256=digest(r['raw_text']), stages=[dict(stage='segmentation', result=old)])])
    config['frozen_05'] = dict(path=str(path), sha256=census.file_sha(path))
    frozen = c4.load_frozen(config['frozen_05'])
    d = c4.diagnostics(r, dict(stages=[dict(stage='segmentation', result=segment(r))]), frozen)
    assert d['frozen_05'] == dict(available=True, verdict='DROP', reason='frozen reason')
    with pytest.raises(ValueError, match='identity mismatch'):
        c4.diagnostics(dict(r, crop_sha256='f'*64), {}, frozen)


def test_full_config_rebases_only_code_and_preserves_inputs(tmp_path):
    spec = importlib.util.spec_from_file_location('census04_prepare', D/'prepare_config.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    source = json.loads((D/'census04_config.json').read_text())
    result = mod.prepare(source, D/'package/projects', tmp_path/'inputs')
    for key in ('parents', 'corrections', 'metadata', 'final_policy', 'predictor', 'runtime_manifest'):
        assert result[key] == source[key]
    assert result['versions'].startswith(str(D/'package'))
