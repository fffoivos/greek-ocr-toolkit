"""T6 optional confidence contracts; the original vendored tests stay unchanged."""
import io
import json
import sys

import pytest

from greekocr._vendor.bench.e2_native import cllg_kraken
from test_vendor_r2_cllg import worker_fixture


def test_plain_worker_protocol_bytes_unchanged(monkeypatch):
    from greekocr._vendor.scripts.fetch import r2_cllg_worker as worker
    monkeypatch.setattr(worker, 'load', lambda *args: (None, None, {}))
    monkeypatch.setattr(worker, 'recognize', lambda model, config, paths: ['α\u0313'])
    monkeypatch.setattr(sys, 'argv', ['worker', '--checkpoint', 'fixture', '--checkpoint-sha256', 'hash'])
    monkeypatch.setattr(sys, 'stdin', io.StringIO('["crop.png"]\n'))
    output = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', output)
    worker.main()
    assert output.getvalue().encode('utf-8') == '["ἀ"]\n'.encode('utf-8')


def test_confidence_worker_protocol_and_plain_prediction_bytes(monkeypatch, tmp_path):
    import math
    import types
    from PIL import Image
    from greekocr._vendor.scripts.fetch import r2_cllg_worker as worker
    containers = types.ModuleType('kraken.containers')
    containers.BBoxLine = containers.Segmentation = lambda **kwargs: types.SimpleNamespace(**kwargs)
    monkeypatch.setitem(sys.modules, 'kraken', types.ModuleType('kraken'))
    monkeypatch.setitem(sys.modules, 'kraken.containers', containers)
    crop = tmp_path/'crop.png'
    Image.new('L', (200, 60), 255).save(crop)
    class Confidence:
        def __iter__(self):
            return iter([.9, .5])
    record = types.SimpleNamespace(prediction='α\u0313', confidences=Confidence())
    model = types.SimpleNamespace(predict=lambda *args: iter([record]))
    assert worker.recognize(model, None, [str(crop)]) == ['α\u0313']
    result, = worker.recognize(model, None, [str(crop)], confidence=True)
    assert result == dict(text='α\u0313', character_confidences=[.9, .5],
                          mean_confidence=.7, min_confidence=.5,
                          mean_log_probability=(math.log(.9)+math.log(.5))/2)
    record.prediction, record.confidences = '', []
    empty, = worker.recognize(model, None, [str(crop)], confidence=True)
    assert empty['mean_confidence'] is empty['min_confidence'] is empty['mean_log_probability'] is None
    record.confidences = [0]
    zero, = worker.recognize(model, None, [str(crop)], confidence=True)
    assert zero['mean_log_probability'] == math.log(1e-300)
    record.confidences = [float('nan')]
    with pytest.raises(ValueError, match='finite probabilities'):
        worker.recognize(model, None, [str(crop)], confidence=True)
    # Plain mode never touches confidence records, including older readers.
    del record.confidences
    assert worker.recognize(model, None, [str(crop)]) == ['']


@pytest.mark.parametrize('serve', [False, True])
def test_worker_confidence_flag_reaches_one_shot_and_serve(monkeypatch, serve):
    from greekocr._vendor.scripts.fetch import r2_cllg_worker as worker
    result = dict(text='α', character_confidences=[.8], mean_confidence=.8,
                  min_confidence=.8, mean_log_probability=-.223)
    def recognize(model, config, paths, *, confidence=False):
        assert confidence is True
        return [result for path in paths]
    monkeypatch.setattr(worker, 'load', lambda *args: (None, None, {}))
    monkeypatch.setattr(worker, 'recognize', recognize)
    monkeypatch.setattr(sys, 'argv', ['worker', '--checkpoint', 'fixture', '--checkpoint-sha256', 'hash',
                                     '--confidence'] + (['--serve'] if serve else []))
    monkeypatch.setattr(sys, 'stdin', io.StringIO('["crop.png"]\n'))
    output = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', output)
    worker.main()
    assert json.loads(output.getvalue()) == [result]


def test_native_confidence_protocol_is_optional_and_raw_text_is_preserved(worker_fixture):
    from greekocr.readers.cllg import load_cllg_worker
    checkpoint, state = worker_fixture
    record = dict(text='α\u0313', character_confidences=[.9, .8], mean_confidence=.85,
                  min_confidence=.8, mean_log_probability=-.164)
    state['predictions'] = [record]
    native = load_cllg_worker(checkpoint, confidence=True)
    assert native.read('crop.png') == record
    assert '--confidence' in state['starts'][0][0]
    assert '--confidence' not in state['calls'][0][0]  # Binding/describe stays unchanged.
    assert native.read_batch([]) == []
    native.close()
    state['predictions'] = ['α\u0313']
    plain = load_cllg_worker(checkpoint)
    assert plain.read('crop.png') == 'α\u0313'
    assert '--confidence' not in state['starts'][-1][0]
    plain.close()


@pytest.mark.parametrize('record', ['plain text', {'text': 'α'},
    dict(text='α', character_confidences=[2], mean_confidence=.8, min_confidence=.8, mean_log_probability=-.2),
    dict(text='α', character_confidences=[.8], mean_confidence=float('nan'), min_confidence=.8, mean_log_probability=-.2)])
def test_native_confidence_rejects_malformed_records(worker_fixture, record):
    checkpoint, state = worker_fixture
    state['predictions'] = [record]
    native = cllg_kraken(checkpoint, confidence=True)
    try:
        with pytest.raises(ValueError, match='text/confidence record'):
            native.read('crop.png')
    finally:
        native.close()
