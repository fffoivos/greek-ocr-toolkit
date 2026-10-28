"""Exercise the actual Docling recognizer and lazy engine loader after export."""
import json
import unicodedata
from pathlib import Path

import numpy as np
import pytest
import torch

from greekocr.train import model, cer
from greekocr.train.export import export_checkpoint, load_release, CODEC_SHA256
from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer

CODEC = Path(__file__).resolve().parents[2]/'greekocr/train/codec/v2.1.json'


@pytest.fixture(params=[1.0, 1.5, 2.0])
def release(tmp_path, request):
    torch.manual_seed(42)
    net, _ = model.build_model(n_classes=266, width_mult=request.param, verbose=False)
    ck = dict(model=net.state_dict(), arch='compact', width_mult=request.param, head='nfd',
              n_classes=266, codec_version='v2.1', codec_sha256=CODEC_SHA256)
    checkpoint = tmp_path/'best.pt'
    torch.save(ck, checkpoint)
    config = tmp_path/'run.json'
    config.write_text(json.dumps(dict(parameters=dict(width_mult=request.param))))
    out = tmp_path/'release'
    export_checkpoint(checkpoint, config, CODEC, out, trusted_checkpoint=True)
    return out, net.eval(), config, checkpoint


def test_export_load_and_actual_docling_path(release):
    out, original, _, _ = release
    loaded, codec, config = load_release(out)
    assert all(torch.equal(v, loaded.state_dict()[k]) for k, v in original.state_dict().items())
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    options = GlossapiOcrOptions(checkpoint=out, replace_policy='all')
    plugin = GlossapiOcrModel(enabled=True, artifacts_path=None, options=options,
                             accelerator_options=AcceleratorOptions(device='cpu'))
    recognizer = plugin._get_recognizer()
    assert isinstance(recognizer, Recognizer)
    strips = [np.random.default_rng(4).random((48, 29), dtype=np.float32),
              np.random.default_rng(5).random((48, 36), dtype=np.float32)]
    # Trainer collate implements its own preprocessing. Compare pixels, fp32 logits,
    # and truncated greedy decodes (serving is NFC; compare in NFD).
    from greekocr.train.data import collate_strips
    samples = [dict(image=np.round(s*255).astype(np.uint8), width=s.shape[1],
                    label=np.array([1], dtype=np.int64), script_class='fixture') for s in strips]
    batch = collate_strips(samples)
    serving_strips = [s['image'].astype(np.float32)/255 for s in samples]
    with torch.no_grad():
        logits = model.masked_forward(original, batch['images'], batch['input_lengths'])
        actual = model.masked_forward(recognizer.model, batch['images'], batch['input_lengths'])
    assert torch.equal(logits, actual)
    expected = [cer.greedy_decode_line(logits[i, :n].argmax(-1).tolist(), codec)
                for i, n in enumerate(batch['input_lengths'])]
    got = recognizer.recognize(serving_strips)
    assert [unicodedata.normalize('NFD', x[0]) for x in got] == [unicodedata.normalize('NFD', x) for x in expected]
    assert all(unicodedata.is_normalized('NFC', text) for text, _ in got)


@pytest.mark.parametrize('name', ['config.json', 'codec.json', 'model.safetensors'])
def test_rejects_tampered_release(release, name):
    out, *_ = release
    with (out/name).open('ab') as f:
        f.write(b' ')
    with pytest.raises(ValueError, match='SHA mismatch'):
        Recognizer(str(out))


def test_export_rejects_wrong_config(release, tmp_path):
    _, _, config, checkpoint = release
    config.write_text(json.dumps({'width_mult': 1.25}))
    with pytest.raises(ValueError, match='width_mult'):
        export_checkpoint(checkpoint, config, CODEC, tmp_path/'bad', trusted_checkpoint=True)
    with pytest.raises(ValueError, match='trusted_checkpoint'):
        export_checkpoint(checkpoint, config, CODEC, tmp_path/'bad')


def rehash(out, name):
    from greekocr.train.ckpt_io import sha256_file
    manifest = json.loads((out/'MANIFEST.json').read_text())
    manifest['files'][name] = dict(bytes=(out/name).stat().st_size, sha256=sha256_file(str(out/name)))
    (out/'MANIFEST.json').write_text(json.dumps(manifest))


def test_strict_state_rejects_missing_key_even_if_manifest_rehashed(release):
    from safetensors.torch import load_file, save_file
    from safetensors import safe_open
    out, *_ = release
    path = str(out/'model.safetensors')
    with safe_open(path, framework='pt') as f:
        metadata = f.metadata()
    state = load_file(path)
    state.pop(next(iter(state)))
    save_file(state, path, metadata=metadata)
    rehash(out, 'model.safetensors')
    with pytest.raises(RuntimeError, match='Missing key'):
        Recognizer(str(out))


def test_config_sha_binding_rejects_supported_width_tamper(release):
    out, *_ = release
    config = json.loads((out/'config.json').read_text())
    config['width_mult'] = 2.0 if config['width_mult'] != 2.0 else 1.0
    (out/'config.json').write_text(json.dumps(config))
    rehash(out, 'config.json')
    with pytest.raises(ValueError, match='metadata mismatch|config SHA binding'):
        Recognizer(str(out))


def test_codec_identity_rejects_reordered_equal_size_codec(release):
    out, *_ = release
    obj = json.loads((out/'codec.json').read_text())
    obj['atoms'][0], obj['atoms'][1] = obj['atoms'][1], obj['atoms'][0]
    (out/'codec.json').write_text(json.dumps(obj))
    rehash(out, 'codec.json')
    with pytest.raises(ValueError, match='codec SHA'):
        Recognizer(str(out))


def test_nfc_serving_and_nfd_head(monkeypatch):
    import greekocr.deploy.docling_plugin.recognizer.inference as serving
    codec = cer.load_codec(str(CODEC))
    lookup = {ch: i for i, ch in enumerate(codec.atom_by_id)}
    nfd = unicodedata.normalize('NFD', 'ά')
    ids = [lookup[nfd[0]], lookup[nfd[1]], 0, 0]
    recognizer = Recognizer.__new__(Recognizer)
    recognizer.codec = codec
    recognizer.model = None
    recognizer.device = 'cpu'
    def fake_forward(*args):
        logits = torch.full((1, 4, 266), -100.)
        for t, identity in enumerate(ids): logits[0, t, identity] = 0
        return logits
    monkeypatch.setattr(serving, 'masked_forward', fake_forward)
    assert recognizer.recognize([np.ones((48, 16), dtype=np.float32)])[0][0] == 'ά'


def test_dev_gate_on_tiny_byte_bound_pool(release, tmp_path):
    import io
    from PIL import Image
    import pyarrow as pa
    import pyarrow.parquet as pq
    from scripts.release_v0_export.verify_dev import verify
    from greekocr.train.ckpt_io import sha256_file
    out, *_ = release
    pixels = np.full((48, 64), 255, dtype=np.uint8)
    pixels[12:30, 20:28] = 0
    encoded = io.BytesIO(); Image.fromarray(pixels).save(encoded, format='PNG')
    rows = [dict(line_id='fixture:0', image_png=encoded.getvalue(), width=64,
                 label_ids=[1], script_class='fixture', split='reserved', codec_version='v2.1')]
    shard = tmp_path/'pool.parquet'; pq.write_table(pa.Table.from_pylist(rows), shard)
    runtime = tmp_path/'runtime.json'
    runtime.write_text(json.dumps({'pools': {'seal04_dev': {'rows': 1, 'files': [dict(
        path=str(shard), bytes=shard.stat().st_size, sha256=sha256_file(str(shard)))]}}}))
    predicted = Recognizer(str(out)).recognize([pixels.astype(np.float32)/255])[0][0]
    predictions = tmp_path/'predictions.jsonl'
    predictions.write_text(json.dumps(dict(id='fixture:0', hyp=unicodedata.normalize('NFD', predicted)))+'\n')
    result = verify(out, runtime, sha256_file(str(runtime)), 'seal04_dev', predictions,
                    sha256_file(str(predictions)), tmp_path/'receipt.json')
    assert result['status'] == 'PASS' and result['rows'] == 1
    predictions.write_text(json.dumps(dict(id='fixture:0', hyp='deliberately mismatched'))+'\n')
    assert verify(out, runtime, sha256_file(str(runtime)), 'seal04_dev', predictions,
                  sha256_file(str(predictions)), tmp_path/'fail.json')['status'] == 'FAIL'
    with pytest.raises(ValueError, match='dev only'):
        verify(out, runtime, sha256_file(str(runtime)), 'seal04_test', predictions,
               sha256_file(str(predictions)), tmp_path/'test.json')
