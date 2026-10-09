"""Independent pixel scenes for the non-table owner feedback, round four."""
import numpy as np
import pytest
from PIL import Image, ImageDraw

from greekocr.glyphs.page_text_lines import segment_page, page_line_segments
from test_page_line_segments import page_fixture, assert_truth


def narrow_columns():
    page, truth, _ = page_fixture(columns=2)
    arr = np.asarray(page).copy()
    arr[:, 513:1008] = arr[:, 565:1060]
    arr[:, 1008:] = 245
    truth[:, 513:1008] = truth[:, 565:1060]
    truth[:, 1008:] = 0
    return arr, truth


@pytest.mark.parametrize('degrees', [-1., -.5, .5, 1.])
def test_oblique_column_rule_with_level_text(degrees):
    arr, truth = narrow_columns()
    slope = np.tan(np.deg2rad(degrees))
    page = Image.fromarray(arr)
    draw = ImageDraw.Draw(page)
    draw.line((502+slope*(20-260),20,502+slope*(490-260),490),fill=25,width=2)
    result = segment_page(page)
    assert_truth(result, truth, 12)
    for line in result.lines:
        crossing = 502+slope*(np.median(line.baseline)-260)
        assert not line.x0 < crossing < line.x1
    assert any(abs(b['slope']-slope)<.006 for b in result.pixels.column_boundaries)


def test_faint_half_cannot_borrow_dark_other_column_contrast():
    page, truth, _ = page_fixture(columns=2)
    arr = np.asarray(page).copy()
    # Exchange the foreground column halfway down the page. Each faint row
    # is level with a dark row, so whole-joined-line photometry would pass it.
    faint = np.isin(truth, [1,2,3,10,11,12])
    arr[faint] = 190
    result = segment_page(Image.fromarray(arr))
    assert len(result.lines) == 12
    active = [l for l in result.lines if l.discounted is None]
    rejected = [l for l in result.lines if l.discounted is not None]
    assert len(active) == len(rejected) == 6
    assert all(not l.x0 < 530 < l.x1 for l in result.lines)
    assert all('faint' in l.discounted and l.contrast < .62 for l in rejected)


def test_dark_prefix_does_not_validate_a_faint_tail_in_same_column():
    page,truth,_=page_fixture()
    arr=np.asarray(page).copy()
    arr[(truth==1)&(np.indices(truth.shape)[1]>220)]=190
    result=segment_page(Image.fromarray(arr))
    first=[l for l in result.lines if np.median(l.baseline)<100]
    dark=[l for l in first if l.discounted is None]
    faint=[l for l in first if l.discounted and 'faint' in l.discounted]
    assert len(dark)==len(faint)==1
    assert dark[0].x1<240 and faint[0].x0>210
    assert len([l for l in result.lines if l.discounted is None])==6


def test_curled_start_with_binding_shadow_keeps_first_letters():
    page, truth, baselines = page_fixture()
    arr = np.asarray(page)
    warped = np.full_like(arr,245); target = np.zeros_like(truth)
    shifts = np.rint(-30*np.exp(-np.maximum(0,np.arange(arr.shape[1])-35)/50)).astype(int)
    for x, shift in enumerate(shifts):
        stop = shift or None
        warped[:stop,x] = arr[-shift:,x]
        target[:stop,x] = truth[-shift:,x]
    # A broad shadow beside the curl is not a thin column rule.
    shadow = 245-55*np.exp(-np.arange(arr.shape[1])/22)
    warped = np.minimum(warped,shadow[None,:]).astype(np.uint8)
    result = segment_page(Image.fromarray(warped))
    assert_truth(result,target,6)
    for line,(_,_,xs,base) in zip(result.lines,baselines):
        assert line.x0 <= 35
        at = xs[:32]
        expected = base[:32]+shifts[at]
        assert np.max(abs(np.interp(at,np.arange(line.x0,line.x1),line.baseline)-expected)) < .45*line.xheight


def test_repeated_nonletter_band_is_discounted_but_letter_rows_survive():
    page, _, _ = page_fixture()
    draw = ImageDraw.Draw(page)
    for x in range(35,495,24):
        draw.rectangle((x,470,x+14,483),fill=25)
    result = segment_page(page)
    band = [l for l in result.lines if np.median(l.baseline)>450]
    assert band and all(l.discounted and 'non-text' in l.discounted for l in band)
    assert len(page_line_segments(page)) == 6


def test_continuation_does_not_invent_rule_through_letter_starts():
    from greekocr.glyphs.pixel_segments import _continue_rules
    xh=16.;mask=np.zeros((560,200),bool)
    # A false opened edge is present in the proposal mask, but only real
    # separated letter-sized stems support it in the source image.
    mask[:,98:101]=True
    source=np.zeros_like(mask)
    for y in range(30,540,48):
        source[y:y+16,98:101]=True
    assert _continue_rules(mask.copy(),xh,source)==[]
