"""Tiny CPU evidence: sealed Stage C vs maintained package, all release widths."""
import importlib.util
import sys
from pathlib import Path

import pytest
import torch

from greekocr.train import cer, model

ROOT = Path(__file__).resolve().parents[2]
SEALED = ROOT/'docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor'


@pytest.fixture(scope='module')
def sealed():
    # Stage C uses flat imports. Load those under their original names temporarily;
    # never edit the sealed files or leak their names into other tests.
    saved = {name: sys.modules.get(name) for name in ('cer', 'model', 'heads')}
    loaded = {}
    try:
        for name in saved:
            spec = importlib.util.spec_from_file_location(name, SEALED/'train'/f'{name}.py')
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
        yield loaded
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


@pytest.mark.parametrize('width', [1.0, 1.5, 2.0])
def test_logits_and_decodes_identical(sealed, width):
    codec_path = SEALED/'codec/v2.1.json'
    old_codec = sealed['cer'].load_codec(str(codec_path))
    new_codec = cer.load_codec(str(ROOT/'greekocr/train/codec/v2.1.json'))
    torch.manual_seed(20261028)
    old = sealed['heads'].build_arm('nfd', 'compact', old_codec, width_mult=width, verbose=False).eval()
    torch.manual_seed(20261028)
    from greekocr.train.heads import build_arm
    new = build_arm('nfd', 'compact', new_codec, width_mult=width, verbose=False).eval()
    x = torch.rand(2, 1, 48, 40, dtype=torch.float32)*2-1
    lengths = torch.tensor([8, 10])
    with torch.no_grad():
        a = sealed['model'].masked_forward(old, x, lengths)
        b = model.masked_forward(new, x, lengths)
    assert a.dtype == b.dtype == torch.float32
    assert torch.equal(a, b)
    for i, n in enumerate(lengths):
        ids = a[i, :n].argmax(-1).tolist()
        assert sealed['cer'].greedy_decode_line(ids, old_codec) == cer.greedy_decode_line(ids, new_codec)


def test_codec_round_trip_identity(sealed):
    old = sealed['cer'].load_codec(str(SEALED/'codec/v2.1.json'))
    new = cer.load_codec(str(ROOT/'greekocr/train/codec/v2.1.json'))
    assert new.n_classes == old.n_classes == 266
    ids = list(range(1, 266))
    text = old.decode(ids)
    assert new.decode(ids) == text
    encode = {ch: i for i, ch in enumerate(new.atom_by_id) if i}
    assert [encode[ch] for ch in text] == ids
    assert (SEALED/'codec/v2.1.json').read_bytes() == (ROOT/'greekocr/train/codec/v2.1.json').read_bytes()


def test_legacy_module_identity():
    from greekocr._vendor.train import model as legacy
    assert legacy is model
