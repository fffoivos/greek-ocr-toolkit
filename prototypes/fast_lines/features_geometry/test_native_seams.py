"""Finite native seams through the real solver and clipping consumer."""
import pytest
import cv2
import numpy as np
from ..shared.contracts import rect
from ..shared.geometry_field_detector import separate_bands


def covered(shape, item):
    mask = np.zeros(shape, np.uint8)
    cv2.fillPoly(mask, [np.rint(item['polygon']).astype(np.int32)], 1)
    return mask


def separate(gray, boxes, height):
    ink = (gray < 100).astype(np.uint8)
    _, labels, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    rows = [dict(polygon=rect(b)) for b in boxes]
    result, audit = separate_bands(gray, rows, height, ink, stats, labels, {})
    return rows, result, audit, labels


@pytest.mark.xfail(strict=True, reason="Inherited seam extrapolation cuts unsupported terminal ink; finite clipping alone changes residual requests and worsens accepted lower strokes on 4959 p5")
def test_short_neighbour_cannot_cut_ink_outside_its_observed_span():
    gray = np.full((130, 220), 255, np.uint8)
    # A complete descender belongs to the long upper row, beyond the short
    # lower row's observed x support. Its absence there is not a flat seam.
    cv2.rectangle(gray, (160, 40), (168, 90), 0, -1)
    cv2.rectangle(gray, (90, 82), (115, 105), 0, -1)
    before, after, audit, labels = separate(
        gray, [[10, 20, 200, 95], [80, 65, 130, 115]], 20)
    assert len(audit) == 1 and audit[0]['accepted']
    assert audit[0]['path'][0][0] == 80 and audit[0]['path'][-1][0] == 130
    original = covered(gray.shape, before[0])
    upper, lower = [covered(gray.shape, q) for q in after]
    descender = labels == labels[50, 164]
    assert original[descender].all()
    assert upper[descender].all(), 'finite neighbour erased terminal body ink'
    assert not lower[descender].any()
    # Separation actually occurred in the observed shared span, rather than
    # an early-return fixture that merely preserves both input polygons.
    assert original[83, 100] and not upper[83, 100] and lower[83, 100]
    assert np.array_equal(original[:, 131:], upper[:, 131:])


@pytest.mark.xfail(strict=True, reason="Inherited seam crossing tolerance accepts a native pixel contact; strict rejection regresses accepted M18/final rows on 4959 p4")
def test_native_pixel_on_seam_remains_unresolved_not_a_tolerated_cut():
    gray = np.full((130, 220), 255, np.uint8)
    # The solver's real interpolated path reaches y65 here. The last row of
    # this detached mark is on it, although its sampled cost misses the mark.
    cv2.rectangle(gray, (13, 63), (15, 65), 0, -1)
    before, after, audit, labels = separate(
        gray, [[10, 15, 200, 75], [10, 55, 200, 115]], 50)
    mark = int(labels[64, 14])
    assert len(audit) == 1 and audit[0]['path']
    path = np.asarray(audit[0]['path'])
    assert np.all(np.interp([13, 14, 15], path[:, 0], path[:, 1]) == 65)
    assert not audit[0]['accepted'] and mark in audit[0]['crossing']
    # Rejecting a separator does not give the mark a semantic owner. Preserve
    # both old envelopes and their uncertainty instead of clipping the mark.
    for old, new in zip(before, after):
        assert np.array_equal(covered(gray.shape, old), covered(gray.shape, new))
