"""Differential checks for the deliberately opt-in array experiments."""
from types import SimpleNamespace

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from greekocr.pages.font import _smooth_samples
from greekocr.pages.lines import _extract
from greekocr.pages.pixels import _rect_morphology
from greekocr.pages.torch_prototypes import TorchArrays


@pytest.fixture(scope="module")
def arrays():
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    yield TorchArrays("cpu", batch_size=3)
    torch.set_num_threads(previous_threads)


@pytest.mark.parametrize("shape", [(1, 1), (2, 4), (3, 7), (8, 1), (1, 20)])
@pytest.mark.parametrize("closing", [False, True])
def test_morphology_exact_borders_origins_and_batches(arrays, shape, closing):
    rng = np.random.default_rng(12)
    masks = [rng.random((11, 17)) > .4, np.ones((11, 17), bool), np.zeros((11, 17), bool), rng.random((7, 9)) > .5]
    calls = [(m, shape, closing) for m in masks]
    for actual, (mask, kernel, close) in zip(arrays.morphology_batch(calls), calls):
        np.testing.assert_array_equal(actual, _rect_morphology(mask, kernel, closing=close))


@pytest.mark.parametrize("kind", ["sparse", "curved", "outliers", "constant", "translated"])
def test_wls_ragged_inputs_and_irls(arrays, kind):
    calls = []
    for n in (2, 11, 85, 23):
        xs = np.linspace(20, 240, n)
        ys = .2*np.sin(xs/50)
        if kind == "sparse":
            xs = xs*.01+100
        if kind == "outliers":
            ys[::3] += 10
        if kind == "constant":
            ys[:] = 3
        shift = 10000 if kind == "translated" else 0
        calls.append((xs+shift, ys, np.arange(15, 250)+shift, 12.))
    for value, call in zip(arrays.smooth_batch(calls), calls):
        np.testing.assert_allclose(value, _smooth_samples(*call), atol=1e-3, rtol=0)


def test_straightening_keeps_envelope_and_constant_outside(arrays):
    gray = np.random.default_rng(31).integers(0, 256, (120, 90)).astype(float)
    lines = []
    for x0, x1, base in ((0, 90, 10), (21, 75, 100), (1, 2, 1), (0, 90, 50)):
        baseline = base+3*np.sin(np.arange(x1-x0)/15)
        lines.append(SimpleNamespace(x0=x0, x1=x1, xheight=13., baseline=baseline,
            meanline=baseline-13, top=baseline-17, bottom=baseline+9))
    # Very small budget crosses strip boundaries and exercises tile ordering.
    actual = arrays.straighten_batch(gray, lines, pixel_budget=317)
    for value, line in zip(actual, lines):
        expected = np.asarray(_extract(gray, line, 32))
        assert value.shape == expected.shape
        assert np.max(np.abs(value.astype(int)-expected.astype(int))) <= 1
        assert np.array_equal(value == 255, expected == 255)


def test_empty_batches_and_invalid_device(arrays):
    assert arrays.smooth_batch([]) == arrays.morphology_batch([]) == []
    assert arrays.straighten_batch(np.zeros((1, 1)), []) == []
    with pytest.raises(ValueError):
        TorchArrays("automatic")
    with pytest.raises(ValueError):
        TorchArrays("cpu", 0)
    with pytest.raises(ValueError):
        arrays.straighten_batch(np.zeros((1, 1)), [], xheight=0)
