"""Known residual-envelope failures, through the real recovery consumer.

The model boundary supplies localizations; scout, native field, piece support,
column splitting, layer checks and final acceptance all execute normally.
"""
import cv2
import numpy as np
import pytest
from ..shared import type_residual_recovery as residual
from ..shared.contracts import rect


def item(bounds):
    return dict(polygon=rect(bounds), baseline=None, score=.9)


def recovered_fixture(monkeypatch, separated, roof, floor):
    width = 1200 if separated else 650
    gray = np.full((220, width), 255, np.uint8)
    starts = [35, 685] if separated else [35]
    for baseline in (69, 139):
        for x in starts:
            cv2.putText(gray, 'abcdefghi jklmnopq rstuvwxyz', (x, baseline),
                        cv2.FONT_HERSHEY_SIMPLEX, .9, 20, 2, cv2.LINE_8)
            cv2.rectangle(gray, (x+29, baseline-27), (x+32, baseline-23), 20, -1)
    target = gray < 100
    target[:100] = False
    competing = gray < 100
    competing[90:] = False
    columns = None
    if separated:
        cv2.line(gray, (600, 100), (600, 170), 20, 2)
        columns = dict(height=23.5, rules=[dict(accepted=True, rule=dict(
            path=[[600, 100], [600, 170]], y0=100, y1=170))])
    current = [item([x-10, 37, x+390, 84]) for x in starts]
    localization = item([24, roof, width-26, floor])
    # Only the detector and request intervention are supplied. In particular,
    # do not stub field(), piece_support(), attachment or ownership.
    calls = []
    class Detector:
        def infer(self, crop, side=960):
            calls.append((crop.shape, side))
            return None, dict(tensor=[1, 3, *crop.shape])
    monkeypatch.setattr(residual, 'postprocess', lambda *a, **k: [localization])
    monkeypatch.setattr(residual, 'requests', lambda *a: [dict(
        bbox=[0, 0, width, 220], id='fixture', derivation=[], dependencies=[])])
    result = residual.recover(gray, current, Detector(), version=11,
                              column_evidence=columns)
    assert len(calls) == 1 and result['fields'][0]['rows']
    assert len(result['added']) == len(starts), result['decisions']
    if separated:
        assert any(d.get('stage') == 'shared column certificate'
                   for d in result['decisions'])
        # A coincident separator can differ by a few binary ulps. Test
        # native ink on both sides, not strict ordering of float vertices.
        for q in result['added']:
            covered = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(covered, [np.rint(q['polygon']).astype(np.int32)], 1)
            assert not (np.any(covered[:, :599] & target[:, :599]) and
                        np.any(covered[:, 602:] & target[:, 602:]))
    mask = np.zeros(gray.shape, np.uint8)
    for q in result['added']:
        cv2.fillPoly(mask, [np.rint(q['polygon']).astype(np.int32)], 1)
    assert not np.any(competing & (mask > 0)), 'neighbour body/mark stolen'
    return result, target, mask


@pytest.mark.parametrize('separated', [False, True])
@pytest.mark.xfail(strict=True, reason='v11 DB roof/floor clips synthetic descenders or detached marks; this fixture is not the native apostrophe')
def test_recover_finishes_glyphs_independently_of_localization(monkeypatch, separated):
    first, target, mask = recovered_fixture(monkeypatch, separated, 115, 138)
    second, other_target, other_mask = recovered_fixture(monkeypatch, separated, 118, 139)
    assert np.array_equal(target, other_target)
    assert not np.any(target & (mask == 0)), 'descender or detached mark clipped'
    assert not np.any(target & (other_mask == 0)), 'second localization clips ink'
    assert [q['polygon'] for q in first['added']] == [q['polygon'] for q in second['added']]


def ambiguous_corridor_fixture():
    """A mark nearer the upper descender, with an actual whitespace seam.

    This is a synthetic native M17 consumer fixture, not the 4959 photograph.
    The two columns and all three rows have independent complete ink support.
    """
    gray = np.full((250, 640), 255, np.uint8)
    rows = []
    for start in (0, 320):
        for y in (50, 115, 180):
            for x in range(30+start, 291+start, 20):
                cv2.rectangle(gray, (x, y), (x+8, y+17), 20, -1)
        cv2.rectangle(gray, (100+start, 50), (104+start, 93), 20, -1)
        cv2.rectangle(gray, (108+start, 101), (112+start, 104), 20, -1)
        cv2.rectangle(gray, (200+start, 98), (208+start, 132), 20, -1)
        cv2.rectangle(gray, (240+start, 115), (248+start, 145), 20, -1)
        for y in (58, 123, 188):
            rows.append(item([20+start, y-12, 309+start, y+12]))
    cv2.line(gray, (320, 80), (320, 220), 20, 2)
    return gray, rows


def polygon_pixels(gray, q):
    mask = np.zeros(gray.shape, np.uint8)
    cv2.fillPoly(mask, [np.rint(q['polygon']).astype(np.int32)], 1)
    return mask


def canonical_polygon(q):
    points = [tuple(p) for p in q['polygon']]
    return min(tuple(points[k:]+points[:k]) for k in range(len(points)))


def test_native_band_audits_ambiguous_mark_without_owned_only_hull():
    from ..shared.geometry_field_detector import native_bands
    gray, rows = ambiguous_corridor_fixture()
    mapped, audit = native_bands(gray, rows, 40)
    # Same physical observations, permuted row inputs. Match by identity rather
    # than comparing positional row IDs in an ownership census.
    order = [4, 0, 5, 2, 1, 3]
    permuted, other = native_bands(gray, [rows[i] for i in order], 40)
    assert all(canonical_polygon(mapped[i]) == canonical_polygon(permuted[order.index(i)])
               for i in range(len(rows)))
    paper = cv2.boxFilter(gray, cv2.CV_32F, (161, 161))
    _, labels, stats, _ = cv2.connectedComponentsWithStats(
        (paper-gray > 255*.08).astype(np.uint8), 8)
    for target, x in ((1, 108), (4, 428)):
        mark = int(labels[102, x+1])
        assert mark and stats[mark, 4] == 20
        # Verify the hard case: the upper descender is nearer by bbox distance.
        centre = np.array([x+2., 102.5])
        def distance(component):
            left, top, width, height = stats[component, :4]
            delta = np.maximum(0, np.maximum([left, top]-centre,
                                             centre-[left+width, top+height]))
            return np.linalg.norm(delta)
        assert distance(labels[60, x-7]) < distance(labels[120, x+3])
        m = polygon_pixels(gray, mapped[target])
        assert np.all(m[labels == mark]), 'unassigned mark must remain contained'
        assert not np.any(m[75:94, x-8:x-3]), 'preceding descender enters target'
        assert audit[target]['gaps'] and any(g['accepted'] for g in audit[target]['gaps'])
        # Reproduce the rejected i2 omission using its owned-label population.
        owned_only = np.isin(labels, audit[target]['components'])
        assert not owned_only[labels == mark].any()
        record = next(r for r in audit[target]['support_accounting']['present']
                      if r['component'] == mark)
        assert record['state'] == 'contained_unassigned'
        assert record['assigned_row'] is None and record['other_rows'] == []
        assert audit[target]['support_accounting']['complete_support'] is None
        match = other[order.index(target)]['support_accounting']
        assert next(r for r in match['present'] if r['component'] == mark)['state'] == record['state']
    for q in mapped:
        m = polygon_pixels(gray, q)
        assert not np.any(m[80:221, 319:322] & (gray[80:221, 319:322] < 100))
        assert not (np.any(m[:, :319] & (gray[:, :319] < 100)) and
                    np.any(m[:, 322:] & (gray[:, 322:] < 100)))


def test_native_band_audit_keeps_shared_and_partial_unassigned_ink_unknown():
    from ..shared.geometry_field_detector import native_bands
    gray = np.full((120, 200), 255, np.uint8)
    cv2.rectangle(gray, (85, 15), (100, 105), 20, -1)
    # This joined object is too tall to be an assigned body. Two localizations
    # cover it partially: absence from owner must not erase it from the audit.
    rows = [item([50, 25, 130, 65]), item([50, 55, 130, 95])]
    mapped, audit = native_bands(gray, rows, 20)
    assert len(mapped) == 2
    records = []
    for i, ev in enumerate(audit):
        a = ev['support_accounting']
        assert len(a['present'])+a['outside_polygon'] == a['population']
        record = a['present'][0]
        assert record['state'] == 'shared' and record['other_rows'] == [1-i]
        assert 0 < record['pixels'] < record['total_pixels']
        assert record['assigned_row'] is None and a['complete_support'] is None
        records.append(record)
    records[0]['other_rows'].append(99)
    assert records[1]['other_rows'] == [0], 'component records must be unaliased'
