"""Offline timing and fake-sbatch tests. Never contact a scheduler."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from timing_c1 import guard, hms, projection, seconds, timing_line


def measurements(load=12.0):
    return dict(sf7_load=dict(bytes=123456, records=1000, seconds=load, whole_files=True),
                decisions=dict(rows=200, seconds=20.0), sf7_lookup=dict(calls=50, seconds=0.02))


def test_projection_line():
    p = projection(measurements())
    assert p['projected_full_seconds'] == 9228
    assert p['suggested_limit'] == '03:50:42'
    line = timing_line(p)
    assert re.search(r'CENSUS TIMING: sf7 load 1000 rec in 12\.000000 s .*decisions 200 in 20\.000000 s .*projected full 02:33:48', line)
    assert 'full sf7 files loaded' in line and 'not representative' in line
    assert 'partition max 12:00:00' in line


def test_capped_limit():
    assert projection(measurements(40000))['suggested_limit'] == '12:00:00'


@pytest.mark.parametrize('value', ['1:00', '00:60:00', '00:00:00', 'bad', '01:00:99'])
def test_bad_times(value):
    with pytest.raises(ValueError): seconds(value)


def test_guard(tmp_path):
    p = tmp_path/'readout.json'
    p.write_text(json.dumps(dict(census_timing=projection(measurements(6000)))))
    with pytest.raises(ValueError, match='explicit full limit'): guard(p, '')
    guard(p, '07:00:00')
    with pytest.raises(ValueError, match='partition max'): guard(p, '13:00:00')


def chain(tmp_path, *, smoke=False, override=None, args=(), projected=None):
    bundle = tmp_path/'bundle'; bundle.mkdir()
    (bundle/'binding_state.py').write_text('')  # Isolate timing from real PENDING bindings.
    (bundle/'timing_c1.py').write_bytes((D/'timing_c1.py').read_bytes())
    (bundle/'submit_chain.sh').write_bytes((D/'submit_chain.sh').read_bytes())
    binpath = tmp_path/'bin'; binpath.mkdir()
    fake = binpath/'sbatch'
    fake.write_text('#!/usr/bin/env python3\nimport json,os,sys\nwith open(os.environ["CALLS"],"a") as f:f.write(json.dumps([sys.argv[1:],os.environ.get("SBATCH_TIMELIMIT")])+"\\n")\nprint("123")\n')
    fake.chmod(0o755)
    env = dict(os.environ, PATH=str(binpath)+os.pathsep+os.environ['PATH'], W=str(tmp_path/'W'),
               CENSUS06_BUNDLE=str(bundle), CENSUS06_PYTHON=sys.executable,
               CENSUS06_ATTEMPT='smoke-test' if smoke else 'full-test', E4_SMOKE=str(int(smoke)), CALLS=str(tmp_path/'calls'))
    env.pop('SBATCH_TIMELIMIT', None); env.pop('CENSUS06_SMOKE_READOUT', None)
    if override: env['SBATCH_TIMELIMIT'] = override
    if projected is not None:
        p = tmp_path/'W/census_06_20261020/attempts/smoke-test.readout/readout.json'
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(dict(census_timing=dict(projected_full_seconds=projected))))
    r = subprocess.run(['bash', str(bundle/'submit_chain.sh'), *args], env=env, capture_output=True, text=True)
    calls = [json.loads(l) for l in (tmp_path/'calls').read_text().splitlines()] if (tmp_path/'calls').exists() else []
    return r, calls


@pytest.mark.parametrize('override,args', [('06:00:00', ()), (None, ('--full-time','06:00:00')), ('05:00:00', ('--full-time=06:00:00',))])
def test_full_only(tmp_path, override, args):
    r, calls = chain(tmp_path, override=override, args=args)
    assert r.returncode == 0, r.stderr
    assert len(calls) == 4
    for i, (argv, envlimit) in enumerate(calls):
        assert envlimit is None
        assert ('--time=06:00:00' in argv) == (i == 2)
    assert re.findall(r'effective --time=(\S+)', r.stderr) == ['00:05:00','00:05:00','06:00:00','00:30:00']


@pytest.mark.parametrize('smoke', [True, False])
def test_defaults(tmp_path, smoke):
    r, calls = chain(tmp_path, smoke=smoke)
    assert r.returncode == 0, r.stderr
    assert len(calls) == 4
    expected = ['00:30:00']*4 if smoke else ['00:05:00','00:05:00','04:00:00','00:30:00']
    assert re.findall(r'effective --time=(\S+)', r.stderr) == expected
    if smoke: assert all('--partition=debug' in a and '--time=00:30:00' in a for a,e in calls)


def test_smoke_ignores_full_override(tmp_path):
    r, calls = chain(tmp_path, smoke=True, override='06:00:00', args=('--full-time','07:00:00'))
    assert r.returncode == 0, r.stderr
    assert all('--time=00:30:00' in a and e is None for a,e in calls)


@pytest.mark.parametrize('limit', [None, '07:00:00'])
def test_refusal_before_any_sbatch(tmp_path, limit):
    r, calls = chain(tmp_path, override=limit, projected=18000)
    if limit:
        assert r.returncode == 0 and len(calls) == 4
    else:
        assert r.returncode != 0 and not calls
        assert 'explicit full limit required' in r.stderr


def test_packaged_limits_unaffected():
    for name, value in [('regression','00:05:00'),('parity','00:05:00'),('readout','00:30:00')]:
        assert f'#SBATCH --time={value}' in (D/'jobs'/f'{name}.sbatch').read_text()
    for name in ['bind_sf7', 'flip_report']:
        assert '#SBATCH --time=00:30:00' in (D/f'{name}.sbatch').read_text()


def test_explicit_common_time(tmp_path):
    r, calls = chain(tmp_path, args=('--time','01:20:00'))
    assert r.returncode == 0
    assert re.findall(r'effective --time=(\S+)', r.stderr) == ['01:20:00']*4


@pytest.mark.parametrize('split', [False, True])
@pytest.mark.parametrize('smoke', [False, True])
@pytest.mark.parametrize('corrupt', [False, True])
def test_whole_sf7_smoke_load_and_timing(tmp_path, split, smoke, corrupt):
    from test_pipeline_033 import row, answer
    from test_line_pipeline import census_config, segment, expected
    from greekocr.harvest.line_pipeline import canonical
    from greekocr.harvest.line_pipeline_census import file_sha
    from greekocr.harvest.line_pipeline_census04 import run
    from prepare_config import prepare
    rows = [dict(row(), id=str(i)) for i in range(45)]
    source = census_config(tmp_path, rows)
    source['codec'] = str(D/'package/projects/greek-ocr-toolkit-pipe032/greekocr/_vendor/codec/v2.json')
    Path(source['metadata']).write_text(canonical(dict(books={'book':expected()})))
    sf7 = tmp_path/'sf7.jsonl'
    records = [answer(r, 'polytonic') for r in rows]
    if corrupt: records[-1]['tool_digest'] = 'bad-digest'  # Outside the 40-row smoke slice.
    sf7.write_text(''.join(canonical(r)+'\n' for r in records))
    source['corrections'] = [dict(tool='polytonic',parent_id='parent',path=str(sf7),sha256=file_sha(sf7),
        format='line-tool-result-v1',status='released',parent_manifest_sha256=source['parents'][0]['sha256'])]
    assignments = tmp_path/'split.jsonl'
    assignments.write_text(''.join(canonical(dict(parent_id='parent',row_id=r['id'],edition_id='book',split='train'))+'\n' for r in rows))
    config = prepare(source, D/'package/projects', tmp_path/'inputs', smoke=smoke,
        split_input=dict(path=str(assignments),sha256=file_sha(assignments)) if split else None)
    n = 40 if smoke else 45
    assert config['parents'][0]['rows'] == n
    assert config['corrections'][0]['path'] == str(sf7)
    if corrupt:
        with pytest.raises(ValueError):
            run(config, tmp_path/'run', execute=True, segmenter_factory=lambda:segment)
        return
    result = run(config, tmp_path/'run', execute=True, segmenter_factory=lambda:segment)
    timing = result['census_timing']
    assert result['input_rows'] == n and result['complete']
    assert timing['sf7_load']['records'] == 45
    assert timing['sf7_load']['bytes'] == sf7.stat().st_size
    assert timing['sf7_load']['seconds'] > 0
    assert timing['decisions']['rows'] == n and timing['decisions']['rows_per_second'] > 0
    assert timing['sf7_lookup']['calls'] == n
    assert timing['sf7_lookup']['seconds'] > 0


def test_readout_parses_mock_summary_timing(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('timing_readout_tests', D/'readout/test_census_readout.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    run = m.make_run(tmp_path/'run', corrupt=False)
    generation = run/'generations/g1-test'
    summary = generation/'summary.json'
    value = json.loads(summary.read_text()); value['census_timing'] = measurements()
    m.dump(summary, value)
    current = run/'CURRENT.json'; value = json.loads(current.read_text())
    value['summary_sha256'] = m.reader.sha(summary); m.dump(current, value)
    r = m.reader.readout(run, tmp_path/'out')
    assert r['census_timing']['projected_full_seconds'] == 9228
    assert r['census_timing_line'].startswith('CENSUS TIMING: sf7 load 1000')
    assert r['census_timing_line'] in (tmp_path/'out/READOUT.md').read_text()

    proc = subprocess.run([sys.executable, '-B', str(D/'readout/census_readout.py'),
        '--run', str(run), '--out', str(tmp_path/'cli-out')], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.count('CENSUS TIMING:') == 1
