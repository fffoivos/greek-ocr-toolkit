"""Independent synthetic pixel truth for the complete page path, not OCR boxes."""
import numpy as np
from PIL import Image
import pytest

from greekocr.glyphs.page_text_lines import page_line_segments, segment_page


def page_fixture(*, columns=1, rule=False, curve=0., skew=0., drift=0., word_gap=False, short=False, cells=False):
    h, w, xh = 560, 1060 if columns == 2 else 660, 16
    truth = np.zeros((h, w), np.int32)
    baseline = []
    for col in range(columns):
        for row in range(6):
            left = 35 + col * 530
            right = left + (16 * int(cells) + 2 if cells and col == 0 else 470)
            if short and row == 5:
                right = left + 75
            xs = np.arange(left, right)
            shift = curve * ((xs - left) / 470 - .5) ** 2 * 4 + (skew + drift * row) * (xs - left)
            base = 65 + 68 * row + np.rint(shift).astype(int)
            baseline.append((col, row, xs, base))
            for k, x in enumerate(range(left, right - 8, 16)):
                if word_gap and row == 2 and 175 < x - left < 240:
                    continue
                up = xh + (6 if k % 7 == 2 else 0)
                down = 5 if k % 9 == 3 else 0
                for dx in range(9):
                    y = base[x + dx - left]
                    # Hollow letter bodies plus top/bottom strokes; some tall
                    # letters and descenders, all with independently known ink.
                    if dx in (0, 1, 7, 8):
                        truth[y - up:y + down, x + dx] = 1 + col * 6 + row
                    else:
                        truth[y - up:y - up + 2, x + dx] = 1 + col * 6 + row
                        truth[y - 2:y, x + dx] = 1 + col * 6 + row
            if row % 2 == 0 and len(base) > 50:
                # A detached accent is truth belonging to this line.
                x = left + 50
                y = base[50] - xh - 5
                truth[y:y + 2, x:x + 4] = 1 + col * 6 + row
    gray = np.where(truth, 25, 245).astype(np.uint8)
    if rule:
        gray[20:490, 516:519] = 20
    return Image.fromarray(gray), truth, baseline


def assert_truth(result, truth, expected):
    assert len(result.lines) == expected
    explained = set()
    for line in result.lines:
        x = np.arange(line.x0, line.x1)
        ys = np.arange(truth.shape[0])[:, None]
        region = (ys >= line.top) & (ys < line.bottom)
        ink = truth[:, x]
        counts = np.bincount(ink[region], minlength=expected + 1); counts[0] = 0
        owner = int(np.argmax(counts)); assert owner > 0
        assert owner not in explained
        explained.add(owner)
        assert counts[owner] / max(1, counts.sum()) > .995
        assert counts[owner] / (truth == owner).sum() > .99
    assert result.diagnostics['rule_gutter_crossings'] == 0
    assert result.diagnostics['boundary_overlaps'] == 0
    assert result.diagnostics['broken_line_pairs'] == 0


@pytest.mark.parametrize('kwargs,expected', [
    ({'columns': 2, 'rule': True}, 12),
    ({'columns': 2}, 12),
    ({'curve': 34}, 6),
    ({'skew': -.06, 'drift': .022}, 6),
    ({'word_gap': True}, 6),
    ({'columns': 2, 'rule': True, 'cells': True}, 12),
    ({'columns': 2, 'rule': True, 'cells': 2, 'skew': .04}, 12),
    ({'short': True}, 6),
])
def test_page_pixels_preserve_whole_lines(kwargs, expected):
    page, truth, _ = page_fixture(**kwargs)
    result = segment_page(page)
    assert_truth(result, truth, expected)
    for line in result.lines:
        strip = np.asarray(line.unroll(page))
        assert strip.shape[0] == 128
        assert not (strip[[0, -1]] < 128).any()
        assert np.allclose(line.baseline - line.meanline, line.xheight)


def test_one_seed_holds_three_lines(monkeypatch):
    import greekocr.glyphs.page_text_lines as mod
    from greekocr.glyphs.pixel_segments import prepare_pixels
    page, truth, _ = page_fixture(curve=30)
    p = prepare_pixels(page)
    p.boxes = [(30, 20, 515, 245), (30, 245, 515, 490)]
    monkeypatch.setattr(mod, 'prepare_pixels', lambda _: p)
    result = mod.segment_page(page)
    assert_truth(result, truth, 6)
    assert result.diagnostics['multi_line_segments'] == 2
    assert len([l for l in result.lines if 0 in l.segment_indices]) == 3


def test_hints_cannot_change_lines():
    page, _, _ = page_fixture(short=True)
    a = page_line_segments(page)
    b = page_line_segments(page, hints=[(0, 0, page.width, page.height)])
    assert len(a) == len(b)
    for x, y in zip(a, b):
        assert (x.x0, x.x1, x.column) == (y.x0, y.x1, y.column)
        np.testing.assert_array_equal(x.baseline, y.baseline)
        assert y.hint_indices == (0,)


def test_blank_and_validation():
    assert page_line_segments(Image.new('L', (200, 300), 255)) == []
    for bad in (np.empty((0, 0)), np.full((8, 8), np.nan), np.full((8, 8), 256)):
        with pytest.raises(ValueError):
            page_line_segments(bad)
    with pytest.raises(ValueError):
        page_line_segments(Image.new('L', (40, 40)), hints=[(1, 2, 0, 3)])


@pytest.mark.parametrize('kwargs', [{'curve': 34}, {'skew': -.06, 'drift': .022}])
def test_baseline_contacts_straighten_at_the_fixed_position(kwargs):
    page, truth, baselines = page_fixture(**kwargs)
    result = segment_page(page)
    for line, (_, _, x, true_base) in zip(result.lines, baselines):
        reference = np.interp(np.arange(line.x0, line.x1), x, true_base)
        # Independent drawing coordinates, not the detector's own supports.
        assert np.max(abs(line.baseline - reference)) < .15 * line.xheight
        strip = np.asarray(line.unroll(page))
        assert np.flatnonzero((strip < 128).any(axis=1)).max() < 100


def test_json_contract_and_full_pixel_partition():
    import json
    page, truth, _ = page_fixture(curve=24, short=True)
    result = segment_page(page)
    cover = np.zeros(truth.shape, int)
    for line in result.lines:
        row = json.loads(json.dumps(line.to_record()))
        for key in ('baseline', 'font_top', 'meanline', 'font_bottom', 'top', 'bottom'):
            assert len(row[key]) == row['x1'] - row['x0']
        yy = np.arange(truth.shape[0])[:, None]
        cover[:, line.x0:line.x1] += (yy >= line.top) & (yy < line.bottom)
        assert row['segment_indices']
    assert cover.max() == 1
    assert np.mean(cover[truth > 0] == 1) > .995
    # Neighbour addresses are reciprocal, including where a short last line
    # changes which printed line occupies the adjacent vertical interval.
    for i, line in enumerate(result.lines):
        for x, neighbour in enumerate(line.neighbours['below']):
            if neighbour >= 0:
                lower = result.lines[neighbour]
                assert lower.neighbours['above'][x + line.x0 - lower.x0] == i


def test_sparse_cell_geometry_is_borrowed():
    page, truth, _ = page_fixture(columns=2, rule=True, cells=2, skew=.04)
    result = segment_page(page)
    short = [line for line in result.lines if line.x1 < 100]
    assert len(short) == 6
    assert all(line.geometry_source == 'borrowed' for line in short)
    assert all(abs(np.median(np.diff(line.baseline)) - .04) < .02 for line in short)


def test_frame_and_solid_illustration_do_not_make_text():
    from PIL import ImageDraw
    page, truth, _ = page_fixture(short=True)
    page = page.copy(); d = ImageDraw.Draw(page)
    d.rectangle((3, 3, page.width - 4, page.height - 4), outline=15, width=4)
    d.rectangle((525, 75, 640, 230), fill=30)
    result = segment_page(page)
    assert_truth(result, truth, 6)
    assert all(line.x1 < 525 for line in result.lines)
