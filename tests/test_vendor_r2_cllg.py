"""CLLG subprocess fixtures. They do not assert real-model recognition parity."""
import copy
import gc
import io
import json
from pathlib import Path
import subprocess
import sys
import unicodedata
import weakref

import pytest

from greekocr._vendor.bench.common import sha256
from greekocr._vendor.bench.e2_native import cllg_kraken


@pytest.fixture
def worker_fixture(tmp_path, monkeypatch):
    checkpoint = tmp_path / 'model.safetensors'
    checkpoint.write_bytes(b'protocol fixture, not CLLG weights')
    binding = dict(checkpoint_sha256=sha256(checkpoint),
        class_order=[dict(text='α', labels=[1]), dict(text='\u0313', labels=[2])],
        preprocess=dict(factory='kraken.lib.dataset:ImageInputTransforms',
            kraken_version='7.1.1', source_sha256='fixture-source',
            input_shape=[1, 3, 96, 0], parameters={'pad': [16, 0]}))
    state = dict(binding=binding, predictions=['α\u0313', 'Latin'], calls=[])
    def run(command, **kwargs):
        state['calls'].append((command, kwargs))
        result = state['binding'] if '--describe' in command else state['predictions']
        return subprocess.CompletedProcess(command, 0, json.dumps(result, ensure_ascii=False), '')
    monkeypatch.setattr(subprocess, 'run', run)
    interpreter = tmp_path / 'venv/bin/python'
    interpreter.parent.mkdir(parents=True)
    interpreter.symlink_to(sys.executable)
    monkeypatch.setenv('CLLG_PYTHON', str(interpreter))
    fake = tmp_path / 'fake_worker.py'
    fake.write_text('''import json, os, sys, time
from pathlib import Path
script = Path(__file__)
config = json.loads(script.with_suffix('.json').read_text())
def record(event, **fields):
    with script.with_suffix('.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps(dict(event=event, pid=os.getpid(), **fields)) + '\\n')
record('start')
for line in sys.stdin:
    paths = json.loads(line)
    record('request', paths=paths)
    if not paths:
        result = []
    elif config.get('crash_always'):
        print('fixture worker crash', file=sys.stderr, flush=True)
        os._exit(1)
    elif any(Path(path).name == 'error.png' for path in paths):
        result = {'error': 'fixture crop failed'}
    elif any(Path(path).name == 'nonjson.png' for path in paths):
        print('diagnostic noise', flush=True)
        continue
    elif any(Path(path).name == 'hang.png' for path in paths):
        time.sleep(5)
        result = ['late response']
    else:
        predictions = config['predictions']
        result = predictions[:len(paths)] if isinstance(predictions, list) else predictions
    print(json.dumps(result, ensure_ascii=False), flush=True)
''', encoding='utf-8')
    real_popen = subprocess.Popen
    state.update(starts=[], processes=[])
    def popen(command, **kwargs):
        state['starts'].append((command, kwargs))
        fake.with_suffix('.json').write_text(json.dumps(dict(
            predictions=state['predictions'], crash_always=state.get('crash_always', False))))
        process = real_popen(command[:2] + [str(fake)] + command[3:], **kwargs)
        state['processes'].append(process)
        return process
    monkeypatch.setattr(subprocess, 'Popen', popen)
    state['requests'] = lambda: [event['paths'] for event in
        map(json.loads, fake.with_suffix('.jsonl').read_text().splitlines())
        if event['event'] == 'request']
    yield checkpoint, state
    for process in state['processes']:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)


def test_batch_paths_order_unicode_and_venv_isolation(worker_fixture, tmp_path):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    assert native.last_batch_ms is None and not state['starts']
    assert native.read_batch([]) == [] and not state['starts']
    crops = [tmp_path / 'Greek crop α.png', tmp_path / 'Latin.png']
    output = native.read_batch(crops)
    assert output == ['α\u0313', 'Latin']
    assert output[0] != unicodedata.normalize('NFC', output[0])
    assert native.last_batch_ms >= 0
    command, kwargs = state['starts'][0]
    assert command[0] == str(tmp_path / 'venv/bin/python')
    assert command[0] != str(Path(command[0]).resolve())
    assert command[1] == '-I' and command[-1] == '--serve'
    assert command[2].endswith('scripts/fetch/r2_cllg_worker.py')
    assert command[command.index('--checkpoint-sha256') + 1] == sha256(checkpoint)
    assert kwargs['encoding'] == 'utf-8' and kwargs['text'] is True
    assert kwargs['stdin'] == kwargs['stdout'] == subprocess.PIPE
    assert native.binding == state['binding'] | {'worker_sha256': sha256(command[2])}
    pid = native._process.pid
    assert native.read(crops[0]) == 'α\u0313'
    assert native.read_batch(crops[:1]) == ['α\u0313']
    assert native.read_batch([]) == [] and native.last_batch_ms == 0
    assert native._process.pid == pid and len(state['starts']) == 1
    assert state['requests']() == [[], list(map(str, crops)), [str(crops[0])], [str(crops[0])]]
    assert len(state['calls']) == 1 and state['calls'][0][0][-1] == '--describe'
    native.close()


@pytest.mark.parametrize('predictions', [[], ['one'], ['one', 3], {'text': 'one'}])
def test_rejects_wrong_count_or_nonstring_output(worker_fixture, predictions):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    state['predictions'] = predictions
    with pytest.raises(ValueError, match='one string per crop'):
        native.read_batch(['a.png', 'b.png'])
    native.close()


def test_restarts_once_on_broken_pipe(worker_fixture):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    assert native.read('first.png') == 'α\u0313'
    first = native._process
    first.kill()
    first.wait(timeout=5)
    assert native.read('second.png') == 'α\u0313'
    assert native._process.pid != first.pid and len(state['starts']) == 2
    assert state['requests']() == [[], [str(Path('first.png').resolve())],
                                  [], [str(Path('second.png').resolve())]]
    native.close()


def test_worker_eof_retries_only_once_and_reports_stderr(worker_fixture):
    checkpoint, state = worker_fixture
    state['crash_always'] = True
    native = cllg_kraken(checkpoint)
    with pytest.raises(RuntimeError, match='pipe broke after restart: fixture worker crash'):
        native.read('crop.png')
    assert len(state['starts']) == 2 and native._process is None
    assert native.last_batch_ms is None
    assert all(process.returncode == 1 for process in state['processes'])


def test_error_response_is_for_one_batch_only(worker_fixture):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    with pytest.raises(ValueError, match='fixture crop failed'):
        native.read_batch(['good.png', 'error.png'])
    pid = native._process.pid
    assert native.last_batch_ms is None
    assert native.read('good.png') == 'α\u0313'
    assert native._process.pid == pid and len(state['starts']) == 1
    native.close()


def test_invalid_json_response_raises_without_desynchronizing(worker_fixture):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    with pytest.raises(ValueError, match='invalid JSON'):
        native.read('nonjson.png')
    assert native.read('good.png') == 'α\u0313'
    assert len(state['starts']) == 1
    native.close()


def test_last_batch_ms_starts_after_readiness(worker_fixture, monkeypatch):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    samples = []
    def clock():
        samples.append(state['requests']())
        return 10 + (len(samples) - 1) * .125
    with monkeypatch.context() as timing:
        timing.setattr('greekocr._vendor.bench.e2_native.time.perf_counter', clock)
        assert native.read('good.png') == 'α\u0313'
    assert samples[0] == [[]]
    assert samples[1] == [[], [str(Path('good.png').resolve())]]
    assert native.last_batch_ms == 125
    native.close()


def test_timeout_discards_worker_and_late_response(worker_fixture):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint, timeout=.5)
    with pytest.raises(RuntimeError, match='exceeded 0.5s'):
        native.read('hang.png')
    assert native._process is None and native.last_batch_ms is None
    assert native.read('good.png') == 'α\u0313'
    assert len(state['starts']) == 2
    native.close()


def test_close_sends_eof_and_is_idempotent(worker_fixture):
    checkpoint, state = worker_fixture
    native = cllg_kraken(checkpoint)
    native.close()
    assert not state['starts']
    native.read('good.png')
    process = native._process
    native.close()
    native.close()
    assert process.returncode == 0
    assert process.stdin.closed and process.stdout.closed
    assert state['starts'][0][1]['stderr'].closed


def test_destructor_closes_worker(worker_fixture):
    checkpoint, _ = worker_fixture
    native = cllg_kraken(checkpoint)
    native.read('good.png')
    process = native._process
    reference = weakref.ref(native)
    del native
    gc.collect()
    assert reference() is None
    assert process.wait(timeout=5) == 0


def test_rejects_contract_drift_and_wrong_runtime(worker_fixture):
    checkpoint, state = worker_fixture
    contract = copy.deepcopy(state['binding'])
    contract['class_order'][0]['text'] = 'changed'
    with pytest.raises(ValueError, match='contract changed: class_order'):
        cllg_kraken(checkpoint, contract)
    state['binding']['preprocess']['kraken_version'] = '7.0.3'
    with pytest.raises(ValueError, match='invalid model binding'):
        cllg_kraken(checkpoint)


def test_missing_venv_reports_setup_command(worker_fixture, monkeypatch):
    checkpoint, _ = worker_fixture
    def missing(*args, **kwargs): raise FileNotFoundError('fixture')
    monkeypatch.setattr(subprocess, 'run', missing)
    with pytest.raises(ModuleNotFoundError, match='r2_cllg_env.sh') as error:
        cllg_kraken(checkpoint)
    assert error.value.name == 'cllg_venv'


def test_missing_serve_interpreter_reports_setup_command(worker_fixture, monkeypatch):
    checkpoint, _ = worker_fixture
    native = cllg_kraken(checkpoint)
    def missing(*args, **kwargs): raise FileNotFoundError('fixture')
    monkeypatch.setattr(subprocess, 'Popen', missing)
    with pytest.raises(ModuleNotFoundError, match='r2_cllg_env.sh') as error:
        native.read('good.png')
    assert error.value.name == 'cllg_venv'
    assert native._process is None and native._stderr is None


@pytest.mark.parametrize('failure,kind,message', [
    (subprocess.CalledProcessError(1, ['worker'], stderr='strict load failed'), ValueError, 'strict load failed'),
    (subprocess.TimeoutExpired(['worker'], 300), RuntimeError, 'exceeded 300s'),
])
def test_worker_errors_are_visible(worker_fixture, monkeypatch, failure, kind, message):
    checkpoint, _ = worker_fixture
    def fail(*args, **kwargs): raise failure
    monkeypatch.setattr(subprocess, 'run', fail)
    with pytest.raises(kind, match=message): cllg_kraken(checkpoint)


def test_rejects_nonjson_stdout(worker_fixture, monkeypatch):
    checkpoint, _ = worker_fixture
    monkeypatch.setattr(subprocess, 'run', lambda command, **kwargs:
                        subprocess.CompletedProcess(command, 0, 'diagnostic noise\n[]', ''))
    with pytest.raises(ValueError, match='invalid JSON'): cllg_kraken(checkpoint)


def test_worker_serve_loads_once_flushes_and_recovers_request_errors(monkeypatch):
    from greekocr._vendor.scripts.fetch import r2_cllg_worker as worker
    loads = []
    model, config = object(), object()
    def load(*args):
        loads.append(args)
        print('load diagnostics')
        return model, config, {'fixture': 'binding'}
    def recognize(actual_model, actual_config, paths):
        assert (actual_model, actual_config) == (model, config)
        print('recognition diagnostics')
        if not isinstance(paths, list):
            raise ValueError('stdin must be a JSON list of crop paths')
        if paths == ['bad']:
            raise ValueError('fixture inference failure')
        return ['α\u0313' for path in paths]
    class Output(io.StringIO):
        flushes = 0
        def flush(self):
            self.flushes += 1
            super().flush()
    output, diagnostics = Output(), io.StringIO()
    payload = '\n'.join([json.dumps(['a', 'b']), '{broken', '{}',
                         json.dumps(['bad']), json.dumps(['again'])]) + '\n'
    monkeypatch.setattr(worker, 'load', load)
    monkeypatch.setattr(worker, 'recognize', recognize)
    monkeypatch.setattr(sys, 'argv', ['worker', '--checkpoint', 'fixture',
                                    '--checkpoint-sha256', 'fixture-hash', '--serve'])
    monkeypatch.setattr(sys, 'stdin', io.StringIO(payload))
    monkeypatch.setattr(sys, 'stdout', output)
    monkeypatch.setattr(sys, 'stderr', diagnostics)
    assert worker.main() is None
    responses = list(map(json.loads, output.getvalue().splitlines()))
    assert len(loads) == 1 and len(responses) == output.flushes == 5
    assert responses[0] == ['α\u0313', 'α\u0313'] and responses[-1] == ['α\u0313']
    assert set(responses[1]) == {'error'}
    assert responses[2] == {'error': 'stdin must be a JSON list of crop paths'}
    assert responses[3] == {'error': 'fixture inference failure'}
    assert 'load diagnostics' in diagnostics.getvalue()
    assert 'recognition diagnostics' in diagnostics.getvalue()


@pytest.mark.parametrize('describe', [False, True])
def test_worker_preserves_one_shot_and_describe(monkeypatch, describe):
    from greekocr._vendor.scripts.fetch import r2_cllg_worker as worker
    calls = []
    def load(*args):
        calls.append('load')
        return None, None, {'fixture': 'binding'}
    def recognize(model, config, paths):
        calls.append(paths)
        return ['α\u0313']
    output = io.StringIO()
    monkeypatch.setattr(worker, 'load', load)
    monkeypatch.setattr(worker, 'recognize', recognize)
    monkeypatch.setattr(sys, 'argv', ['worker', '--checkpoint', 'fixture',
        '--checkpoint-sha256', 'fixture-hash'] + (['--describe'] if describe else []))
    monkeypatch.setattr(sys, 'stdin', io.StringIO('[\n  "crop.png"\n]\n'))
    monkeypatch.setattr(sys, 'stdout', output)
    worker.main()
    assert json.loads(output.getvalue()) == ({'fixture': 'binding'} if describe else ['α\u0313'])
    assert calls == (['load'] if describe else ['load', ['crop.png']])
