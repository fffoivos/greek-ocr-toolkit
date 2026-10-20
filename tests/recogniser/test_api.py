import hashlib
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
from PIL import Image
import pytest
from greekocr.labelfix import ctc_align as old
from greekocr.recogniser import (Alignment, AlignmentCache, Reading, align, confidence_matches,
    crop_key, forbid_forward, run_shard, transfer)
from greekocr.recogniser.api import Recogniser, binding_errors
from greekocr.recogniser.evidence import (EVIDENCE_SCHEMA, LINE_PROVENANCE, REGION_PROVENANCE,
    RECORD_KEYS, OPTIONAL_RECORD_KEYS, alignment_sha256)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_ROOT = ROOT.parent/'greek-ocr-toolkit-spellcheck/.cache/labelfix'


def canonical(obj):
    return json.dumps(obj, sort_keys=True).encode()


def example():
    return Alignment('α\u0301β', [old.CharSpan(c, i, i, i+1, i*4+.123, i*4+4.567)
                               for i, c in enumerate('α\u0301β')], 4, 1., 16, .8, [.7,.8,.9,.8])


def test_frozen_caches():
    root = Path(os.environ.get('CU3_CACHE_ROOT', DEFAULT_CACHE_ROOT))
    paths = [root/'align_s0.jsonl', *sorted(root.rglob('align_locked_*.jsonl'))]
    locked_root = ROOT.parent/'greek-ocr-toolkit-spellcheck-r0/.cache/labelfix'
    paths += sorted(locked_root.rglob('align_locked_*.jsonl'))
    assert paths[0].is_file(), f'frozen golden cache required: {paths[0]}'
    counts = {}
    with forbid_forward():
        for path in paths:
            count = 0
            for line in path.open():
                record = json.loads(line)['alignment']
                a, b = old.Alignment.from_record(record), Alignment.from_record(record)
                assert canonical(a.to_record()) == canonical(b.to_record())
                width = max(1, a.strip_width*a.scale)
                slots = [dict(start=0, base='α', evidence=dict(window=[0, width])),
                         dict(start=1, base='β', evidence=dict(window=[-1, width]))]
                assert canonical(a.recognition_evidence(slots, width)) == canonical(b.evidence(slots, width))
                assert alignment_sha256(b) == hashlib.sha256(canonical(a.to_record())).hexdigest()
                count += 1
            assert count
            counts[str(path)] = count
    # pytest output can be archived with -s; the test never writes frozen inputs.
    print('golden records:', counts)


def test_frozen_contract():
    assert EVIDENCE_SCHEMA == 'ctc-window-score-v1'
    assert LINE_PROVENANCE == 'saved_alignment_confidence'
    assert REGION_PROVENANCE == 'minimum_max_frame_posterior_including_blank'
    assert RECORD_KEYS == {'prediction','n_frames','scale','strip_width','confidence','spans'}
    assert OPTIONAL_RECORD_KEYS == {'frame_confidences','frame_prediction_sha256','transferred'}
    a = example()
    assert set(a.to_record()) == RECORD_KEYS | {'frame_confidences','frame_prediction_sha256'}
    assert set(Alignment('').to_record()) == RECORD_KEYS
    assert set(transfer(a, 'α').to_record()) == RECORD_KEYS | {'transferred'}
    ev = a.evidence(a.slots(), 16)
    assert ev['schema'] == EVIDENCE_SCHEMA
    assert ev['provenance'] == LINE_PROVENANCE
    assert ev['regions'] and all(r['provenance'] == REGION_PROVENANCE for r in ev['regions'])
    assert alignment_sha256(a) == 'efb5d44171dc7034de6dbc6d49ed291e4d84629822d0777685f8e066b19068b7'


@pytest.mark.parametrize('text', ['άβ', 'α\u0301β', '', 'ζα\u0301βγ'])
@pytest.mark.parametrize('record', [False, True])
def test_transfer(text, record):
    import unicodedata
    a = example()
    out = transfer(a.to_record() if record else a, text)
    assert out.prediction == unicodedata.normalize('NFD', text)
    assert out.transferred and out.frame_confidences is None
    assert 'frame_prediction_sha256' not in out.to_record()
    assert a.frame_confidences is not None and not getattr(a, 'transferred', False)
    assert out.evidence(out.slots(), 16)['regions'] == []
    source = old.Alignment.from_record(a.to_record()) if record else a
    expected = old.transfer_alignment(out.prediction, source)
    assert out.to_record()['spans'] == expected.to_record()['spans']


def test_empty_transfer():
    assert len(transfer(Alignment(''), 'ά').spans) == 2


def test_tolerance_witnesses():
    data = json.loads((Path(__file__).parent/'fixtures/l1f_17_tolerance_witnesses.json').read_text())
    rows = data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))
    assert len(rows) == 17
    for r in rows:
        frames, confidence = r['frame_confidences'], r['recognition_confidence']
        assert confidence_matches(frames, confidence)
        assert not math.isclose(sum(frames)/len(frames), confidence, rel_tol=0, abs_tol=2e-7)
        assert not confidence_matches(frames, confidence-.001)


@pytest.mark.parametrize('frames,confidence', [([], .5), ([float('nan')], .5), ([1.1], 1.1),
                                            (None, .5), ([.5], None), ([[.5]], .5)])
def test_invalid_confidence(frames, confidence):
    assert not confidence_matches(frames, confidence)


def test_cache(tmp_path):
    a = example()
    reader = SimpleNamespace(read=Mock(return_value=[Reading(a.prediction, 'labelfix', {'test':1}, a)]))
    path = tmp_path/'cache.jsonl'
    crops = ['/machine/docs/harvest/book/crop.png']
    first = run_shard(crops, reader, path)
    with forbid_forward():
        replay = AlignmentCache(path, reader).get(crops)
    key = crop_key(crops[0])
    assert first[key].spans[0].x0 == .1
    assert canonical(first[key].to_record()) == canonical(replay[key].to_record())
    assert reader.read.call_count == 1
    assert json.loads(path.read_text())['provenance'] == {'test':1}
    with pytest.raises(ValueError):
        crop_key('/outside/crop.png')
    path.write_text(path.read_text()*2)
    with pytest.raises(ValueError, match='duplicate'):
        AlignmentCache(path, reader)


def test_checks(tmp_path):
    codec = tmp_path/'codec'; codec.write_text('test')
    c = SimpleNamespace(version='v1', n_classes=3)
    meta = dict(codec_version='v1', n_classes='3', head='nfd', codec_sha256=hashlib.sha256(b'test').hexdigest())
    assert binding_errors(meta, c, codec) == []
    for key, value in [('codec_version','bad'),('n_classes',4),('head','other'),('codec_sha256','bad')]:
        assert any(key in e for e in binding_errors(dict(meta, **{key:value}), c, codec))


def fake_api(backend):
    api = Recogniser.__new__(Recogniser)
    api.provenance = {'test':1}
    api._backend = lambda profile: backend
    return api


def test_profiles_delegate(tmp_path):
    im = Image.new('L', (64,48), 255)
    path = tmp_path/'crop.png'; im.save(path)
    a = example(); backend = SimpleNamespace(align_batch=Mock(return_value=[a]))
    api = fake_api(backend)
    r = api.read([im])[0]
    assert align(r).to_record() == a.to_record() and r.frames == a.frame_confidences
    backend = SimpleNamespace(read=Mock(return_value='α\u0301'), logits=Mock(return_value=np.ones((2,3))))
    api = fake_api(backend)
    assert api.read([im], profile='eval')[0].text == 'α\u0301'
    assert api.as_reader().read(path) == 'α\u0301'
    assert api.logits([im])[0].dtype == np.float32
    assert api.logits([path], dtype=np.float64)[0].dtype == np.float64
    backend = SimpleNamespace(recognize=Mock(return_value=[('ά', .8)]))
    api = fake_api(backend)
    strip = np.ones((48,64), dtype=np.float32)
    assert api.read([strip], profile='serve')[0].text == 'ά'
    assert backend.recognize.call_args.args[0][0] is strip
    with pytest.raises(ValueError, match='index 0'):
        api.read([tmp_path/'missing'], profile='eval')
    with pytest.raises(ValueError, match='strip'):
        api.read([np.ones((5,5))], profile='serve')
    with pytest.raises(ValueError):
        align(Reading('x', 'eval', {}))


def test_guard_restores():
    method = old.Recognizer.align_batch
    with forbid_forward():
        with forbid_forward():
            with pytest.raises(RuntimeError):
                old.Recognizer.align_batch(None, [])
        with pytest.raises(RuntimeError):
            Recogniser.read(None, [])
    assert old.Recognizer.align_batch is method


def test_strict_load_and_legacy_escape(tmp_path, monkeypatch):
    from greekocr.recogniser import load
    from greekocr._vendor.train import cer, ckpt_io
    checkpoint = tmp_path/'weights.pt'; checkpoint.write_bytes(b'weights')
    codec = tmp_path/'codec.json'; codec.write_bytes(b'codec')
    meta = dict(codec_version='v1', n_classes=3, head='nfd', codec_sha256='wrong')
    monkeypatch.setattr(ckpt_io, 'load_model_weights', lambda path: ({}, meta))
    monkeypatch.setattr(cer, 'load_codec', lambda path: SimpleNamespace(version='v1', n_classes=3))
    with pytest.raises(ValueError, match='codec_sha256'):
        load(checkpoint, codec, threads=2)
    legacy = load(checkpoint, codec, threads=2, strict=False)
    assert legacy.binding_errors == ['codec_sha256 mismatch or missing']
    assert legacy._backends == {}
    assert legacy.provenance['checkpoint_sha256'] == hashlib.sha256(b'weights').hexdigest()
    assert legacy.provenance['strict'] is False
    meta['codec_sha256'] = hashlib.sha256(b'codec').hexdigest()
    strict = load(checkpoint, codec)
    assert strict.binding_errors == []
    with pytest.raises(ValueError, match='positive'):
        load(checkpoint, codec, threads=0)
    with pytest.raises(ValueError, match='unknown profile'):
        strict._backend('unknown')


def test_identity_transfer_is_detached():
    a = example()
    b = transfer(a, a.prediction)
    assert b is not a and b.transferred and b.frame_confidences is None
    b.spans[0].x0 = 99
    assert a.spans[0].x0 != 99


def test_missing_results_never_write_cache(tmp_path):
    reader = SimpleNamespace(read=lambda *a, **kw: [])
    path = tmp_path/'cache.jsonl'
    with pytest.raises(ValueError, match='count mismatch'):
        AlignmentCache(path, reader).get(['docs/harvest/crop.png'])
    assert not path.exists()
