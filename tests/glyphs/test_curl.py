"""Owner's 8 October curled starts. Pixel references were selected from the original crops, independently of the fit.

Coordinates are baseline contacts, not fitted support: omit descenders, accents, punctuation and neighbouring lines.
The starts of 17 and 18 contain capitals only; 21 includes digits and 32 is mostly capitals. Keep those explicit
instead of calling their bottoms x-height measurements. The same fixed points drive the before/after report.
"""
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from greekocr.glyphs.columns import column_segments

PAGE = Path(__file__).parents[1] / 'fixtures' / 'page_s2-49598b2e848ab1f0ee1e-p00001' / 'crops'
# (x, bottom row, body | capital | digit); clipped body letters still have a visible baseline contact.
CONTACTS = {
    17: [(96.5, 14, 'capital'), (117.5, 17, 'capital'), (148.5, 23, 'capital'), (185, 27, 'capital'),
         (216, 30, 'capital'), (242, 31, 'capital'), (281, 35, 'capital'), (318, 37, 'capital'), (388.5, 40, 'capital')],
    18: [(96, 91, 'capital'), (133.5, 99, 'capital'), (169.5, 105, 'capital'), (205.5, 109, 'capital'),
         (229, 112, 'capital'), (249.5, 114, 'capital'), (286.5, 116, 'capital'), (321.5, 119, 'capital')],
    21: [(55, 6, 'body'), (71, 9, 'body'), (87.5, 15, 'body'), (108.5, 17, 'body'),
         (157.5, 25, 'digit'), (188.5, 31, 'digit'), (269, 39, 'digit'), (304, 41, 'digit'),
         (353.5, 44, 'digit'), (387.5, 44, 'digit')],
    23: [(62.5, 9, 'body'), (109, 10, 'body'), (131, 21, 'body'), (170.5, 20, 'body'), (198, 25, 'body'),
         (261, 32, 'body'), (291.5, 34, 'body'), (317, 36, 'body'), (366, 40, 'body'), (387, 40, 'body')],
    25: [(93.5, 16, 'body'), (119.5, 20, 'body'), (143, 24, 'body'), (183.5, 30, 'body'), (204.5, 33, 'body'),
         (229, 36, 'body'), (264, 36, 'body'), (342, 44, 'body'), (365, 45, 'body'), (390, 44, 'body')],
    29: [(76, 7, 'body'), (100, 14, 'body'), (123, 18, 'body'), (144.5, 21, 'body'), (195.5, 31, 'body'),
         (240, 35, 'body'), (259.5, 38, 'body'), (284, 38, 'body'), (329, 42, 'body'), (355.5, 42, 'body'),
         (380.5, 42, 'body')],
    30: [(105.5, 12, 'body'), (134, 18, 'body'), (155.5, 22, 'body'), (178, 24, 'body'),
         (259, 33, 'body'), (322, 37, 'body'), (348.5, 38, 'body'), (375, 39, 'body')],
    32: [(94.5, 96, 'capital'), (128.5, 102, 'capital'), (163, 108, 'capital'), (198.5, 114, 'capital'),
         (232, 117, 'capital'), (260.5, 119, 'capital'), (323.5, 123, 'capital'), (367, 125, 'body')],
    35: [(102, 11, 'body'), (124, 15, 'body'), (147, 21, 'body'), (171, 24, 'body'),
         (215, 31, 'body'), (240, 33, 'body'), (319, 39, 'body'), (375.5, 40, 'body'), (397, 43, 'body')],
}


@pytest.mark.parametrize('number', CONTACTS, ids=lambda n: f'l{n:05d}')
def test_curled_start_stays_with_its_own_line(number):
    image = Image.open(PAGE / f's2-49598b2e848ab1f0ee1e-p00001-l{number:05d}.png')
    segments = column_segments(image)
    # The left column remains a single line over its curled word; no artificial split in the first 400 pixels.
    segment = segments[0]
    assert segment.x0 == 0 and segment.x1 > 400
    residual = [abs(segment.glyphs.band.bottom[int(x)] - y) for x, y, _ in CONTACTS[number]]
    assert np.median(residual) < 3
    assert max(residual) < 6
