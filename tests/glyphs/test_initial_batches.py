"""Owner 8 Oct 20:15: the first two review batches are the regression set for every future version of the line tools.
Golden values: tests/fixtures/glyphs_golden/initial_batches.json (frozen from the crop-level tools)."""
import glob, json
from pathlib import Path

import numpy as np
import pytest

from greekocr.glyphs.report import document_priors, line_record

FIX = Path(__file__).parents[1] / 'fixtures'
GOLD = json.loads((FIX / 'glyphs_golden' / 'initial_batches.json').read_text())['lines']
POOL = sorted(glob.glob(str(FIX / 'o4d_sample400' / 'crops' / '*.png'))) + sorted(glob.glob(str(FIX / 'o4d_lines' / 'line*.png'))) \
    + sorted(glob.glob(str(FIX / 'o4d_lines' / 'regressions' / '*.png')))


@pytest.fixture(scope='module')
def priors():
    return document_priors(POOL)


@pytest.mark.parametrize('g', GOLD, ids=[g['id'] for g in GOLD])
def test_initial_batch_line_is_reproduced(g, priors):
    r = line_record(str(FIX / g['path']), priors=priors)
    assert r['n_columns'] == g['n_columns']
    assert r['n_full_lines'] == g['n_full_lines']
    assert abs(r['angle_deg'] - g['angle_deg']) <= .3
    base = np.array(r['segments'][r['main_segment']]['baseline'], float)
    gold = np.array(g['main_baseline'], float)
    n = min(len(base), len(gold))
    assert np.abs(base[:n] - gold[:n]).mean() <= 3.0
