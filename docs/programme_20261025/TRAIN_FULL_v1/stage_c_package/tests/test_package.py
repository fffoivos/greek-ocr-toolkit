import copy
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, cadence, digest, read, schedule, sha, spec, write_rows
from manifest import Registry, combine, relocate


def book(bid='book-a', split='train', edition='ed-a', **kwargs):
    return dict(book_id=bid, split=split, conflict=False, harvest_protection=False,
                aliases=[dict(namespace='edition_id', value=edition)], **kwargs)


def row(ident='a', crop='a' * 64, split='train', bid='book-a', ed='ed-a', **kwargs):
    return dict(id=ident, text='αβ', source='source', split=split, book_id=bid,
                edition_id=ed, crop_sha256=crop, release='v4', **kwargs)


def test_horizon_and_cadence():
    assert 8 * ((428872 + 63) // 64) == 53616
    assert schedule() == [50000, 53616]
    assert schedule(80424) == [50000, 80424]
    assert schedule(100000) == [50000, 100000]
    assert schedule(4, 2) == [2, 4]
    assert not cadence(0, 4, 2)


def test_cross_release_dedupe_and_heldout_retention():
    registry = Registry([book(), book('book-b', 'dev', 'ed-b')])
    r = row()
    h = dict(r, release='harvest', id='harvest-alias')
    ev = row('ev', 'e' * 64, 'dev', 'book-b', 'ed-b')
    kept, report = combine([r, h, ev, dict(ev, id='ev2')], registry)
    assert len(kept) == 3
    assert report['duplicate_train_rows'] == 1
    assert report['unique_crops'] == 2
    assert report['split_counts'] == {'train': 1, 'dev': 2}


@pytest.mark.parametrize('kind', ['line', 'book', 'edition', 'provider'])
def test_leakage_refuses(kind):
    reg = Registry([book(), book('book-b', 'dev', 'ed-b')])
    a = row(item='item' if kind == 'provider' else 'one')
    b = row('b', 'b' * 64, 'dev', 'book-b', 'ed-b', item='item' if kind == 'provider' else 'two')
    if kind == 'crop':
        b['crop_sha256'] = a['crop_sha256']
    elif kind == 'line':
        b['id'] = a['id']
    elif kind == 'book':
        b['book_id'] = a['book_id']
    elif kind == 'edition':
        b['edition_id'] = a['edition_id']
    with pytest.raises(ValueError):
        combine([a, b], reg)


def test_conflicting_labels_and_ambiguous_aliases():
    with pytest.raises(ValueError, match='conflicting duplicate'):
        combine([row(), dict(row(), release='harvest', text='different')], Registry([book()]))
    with pytest.raises(ValueError, match='ambiguous registry'):
        Registry([book(), book('book-b')])
    with pytest.raises(ValueError, match='registry v2 assignment changed'):
        Registry([book()], [book(split='dev')])


def test_sha_relocation_and_mac_refusal(tmp_path):
    p = tmp_path / 'crop.png'
    p.write_bytes(b'pixels')
    assert relocate('/Users/old/crop.png', {'/Users/old': str(tmp_path)}, sha(p), fixture=True) == str(p)
    with pytest.raises(ValueError, match='SHA'):
        relocate(p, {}, '0' * 64, fixture=True)
    with pytest.raises(ValueError, match='non-Clariden'):
        relocate(p, {}, sha(p))


def mock_runtime(tmp_path):
    import numpy as np
    from PIL import Image
    from prepare import write_pool
    rng = np.random.default_rng(123)
    def data(split, prefix, n=8):
        result = []
        for i in range(n):
            image = Image.fromarray(rng.integers(0, 256, (48, 64), dtype=np.uint8))
            f = io.BytesIO()
            image.save(f, format='PNG')
            result.append(dict(line_id=prefix + str(i), image_png=f.getvalue(), width=64,
                label_ids=[2, 3, 4], codec_version='v2.1', script_class='latin', split=split,
                severity=0, bg_type='flat', polarity='dark', font='fixture',
                source_dataset=prefix, source_doc_id='edition-' + prefix))
        return result
    collections = {'real': data('train', 'real'), 'synthetic': data('train', 'syn'),
                   'validation': data('val', 'val')}
    for name in ('seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test'):
        collections[name] = data('reserved', name)
    pools = {name: write_pool(tmp_path / name, rr) for name, rr in collections.items()}
    runtime = dict(mock=True, seed=20261015, codec_version='v2.1', pools=pools,
        references={name: {r['line_id']: 'ABC' for r in rr} for name, rr in collections.items()
                    if name not in ('real', 'synthetic', 'validation')},
        components=[dict(name='real', kind='real', fraction=.5),
                    dict(name='synthetic', kind='synthetic', fraction=.5, recipe_sha256='mock')])
    atomic(tmp_path / 'runtime.json', runtime)
    return tmp_path / 'runtime.json'


def spawn(runtime, output, env=None):
    output.mkdir(exist_ok=True)
    log = (output / 'process.log').open('a')
    child = subprocess.Popen([sys.executable, '-B', str(PKG / 'tests/mock_worker.py'),
                              '--runtime', str(runtime), '--out', str(output)],
        stdout=log, stderr=log, env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
            'MKL_NUM_THREADS': '1', 'VECLIB_MAXIMUM_THREADS': '1', 'S1_TRACE': '1',
            'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    log.close()
    return child


@pytest.mark.parametrize('kill_step', [2, 4])
def test_hard_kill_restart_identity_real_s1_trainer(tmp_path, kill_step):
    import torch
    runtime = mock_runtime(tmp_path)
    full, split = tmp_path / 'full', tmp_path / 'split'
    c = spawn(runtime, full)
    assert c.wait(timeout=40) == 0, (full / 'process.log').read_text()
    c = spawn(runtime, split, {'TRAIN_FULL_TEST_PAUSE_STEP': str(kill_step)})
    deadline = time.monotonic() + 30
    while not (split / 'TEST_PAUSED.json').exists() and c.poll() is None and time.monotonic() < deadline:
        time.sleep(.05)
    if not (split / 'TEST_PAUSED.json').exists():
        c.kill()
        c.wait(timeout=5)
        pytest.fail((split / 'process.log').read_text())
    os.kill(c.pid, signal.SIGKILL)
    assert c.wait(timeout=5) == -signal.SIGKILL
    c = spawn(runtime, split)
    assert c.wait(timeout=40) == 0, (split / 'process.log').read_text()
    a = torch.load(full / 'segment.pt', weights_only=False, map_location='cpu')
    b = torch.load(split / 'segment.pt', weights_only=False, map_location='cpu')
    # Whole checkpoints contain intentionally different output paths and wall times.
    # Compare every scientific continuation field, including draw/loss traces.
    fields = ('model', 'opt', 'sched', 'rng', 'epoch', 'batch_position', 'iterator_created',
              'global_step', 'best', 'bad_epochs', 'health', 'trace', 'draw_chain', 'draw_position')
    def equal(x, y):
        import numpy as np
        if torch.is_tensor(x):
            assert torch.equal(x, y)
        elif isinstance(x, np.ndarray):
            assert np.array_equal(x, y)
        elif isinstance(x, dict):
            assert x.keys() == y.keys()
            for k in x:
                equal(x[k], y[k])
        elif isinstance(x, (list, tuple)):
            assert len(x) == len(y)
            for xx, yy in zip(x, y):
                equal(xx, yy)
        else:
            assert x == y
    for key in fields:
        equal(a[key], b[key])
    for step in [2, 4, 6, 8]:
        left = read(full / 'eval' / ('step-%09d.json' % step))
        right = read(split / 'eval' / ('step-%09d.json' % step))
        assert left['instruments'] == right['instruments']
        assert set(left['instruments']) == {'seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test'}
    assert (split / 'COMPLETE.json').exists()
    atomic(tmp_path / 'IDENTITY.json', dict(status='BIT_IDENTICAL', mock_model=True,
        real_s1_training_body=True, killed_with='SIGKILL', killed_step=kill_step,
        compared_fields=list(fields), final_step=b['global_step']))


def test_test_numbers_cannot_select_stop_or_adjust_training(tmp_path):
    import torch
    runtime = mock_runtime(tmp_path)
    aout, bout = tmp_path / 'test-a', tmp_path / 'test-b'
    a = spawn(runtime, aout)
    assert a.wait(timeout=40) == 0, (aout / 'process.log').read_text()
    # Change test references dramatically while preserving train + validation.
    changed = read(runtime)
    for name in ('seal04_test', 'harvest_test'):
        changed['references'][name] = {k: 'ZZZZZZ' for k in changed['references'][name]}
    atomic(tmp_path / 'changed.json', changed)
    b = spawn(tmp_path / 'changed.json', bout)
    assert b.wait(timeout=40) == 0, (bout / 'process.log').read_text()
    left = torch.load(aout / 'segment.pt', weights_only=False, map_location='cpu')
    right = torch.load(bout / 'segment.pt', weights_only=False, map_location='cpu')
    sys.path.insert(0, str(PKG / 'vendor'))
    from train import train as trainer
    trainer._runtime()
    from compare import FIELDS
    assert trainer.checkpoint_state_sha256({k: left[k] for k in FIELDS}) == trainer.checkpoint_state_sha256({k: right[k] for k in FIELDS})
    la = read(aout / 'eval/step-000000008.json')['instruments']['seal04_test']
    lb = read(bout / 'eval/step-000000008.json')['instruments']['seal04_test']
    assert la['score'] != lb['score']


def test_frozen_scorer_literal_order():
    sys.path.insert(0, str(PKG / 'vendor'))
    from bench.score import aggregate
    result = aggregate([(dict(text='α\u0313\u0301'), 'α\u0301\u0313')])
    assert result['cer']['nfd_atom']['edits'] > 0
    pins = read(PKG / 'vendor/SCORER_BINDING.json')
    assert all(sha(PKG / 'vendor' / name) == value for name, value in pins.items())
