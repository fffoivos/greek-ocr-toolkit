"""Round-3 regression scenes with independent, drawn pixel ownership."""
import numpy as np
from PIL import Image, ImageDraw

from greekocr.glyphs.page_text_lines import segment_page, page_line_segments
from test_page_line_segments import page_fixture, assert_truth


def test_accent_row_is_owned_by_bodies():
    page, truth, _ = page_fixture()
    ink = np.asarray(page).copy()
    for x in range(35, 480, 16):
        ink[39:42, x+2:x+6] = 25
        truth[39:42, x+2:x+6] = 1
    result = segment_page(Image.fromarray(ink))
    assert_truth(result, truth, 6)
    assert result.lines[0].ink_classes['mark_above'] >= 20
    assert 'accent_top' not in result.lines[0].borrowed


def test_broken_rule_is_a_full_column_boundary():
    page, truth, _ = page_fixture(columns=2)
    draw = ImageDraw.Draw(page)
    for y in range(20, 485, 54):
        draw.rectangle((516,y,518,y+47), fill=20)
    result = segment_page(page)
    assert_truth(result, truth, 12)
    assert all(not (line.x0 < 517 < line.x1) for line in result.lines)


def test_spread_narrow_fold_level_baselines():
    page, truth, _ = page_fixture(columns=2)
    # Move the right page closer: a 2.5-x-height fold, level baselines.
    arr = np.asarray(page).copy()
    arr[:, 532:-33] = np.asarray(page)[:, 565:]
    arr[:, -33:] = 245
    truth[:, 532:-33] = truth[:, 565:]
    truth[:, -33:] = 0
    result = segment_page(Image.fromarray(arr))
    assert_truth(result, truth, 12)
    assert all(not (line.x0 < 510 < line.x1) for line in result.lines)


def _capital_page(spacing):
    page, truth, _ = page_fixture()
    arr = np.asarray(page).copy()
    # Insert an all-capital head above the paragraph, and move paragraph down.
    out = np.full((700,660),245,np.uint8); out[100:660] = arr
    for x in range(35,600,spacing):
        out[20:46,x:x+3] = 25; out[20:46,x+15:x+18] = 25
        out[20:23,x:x+18] = 25; out[43:46,x:x+18] = 25
    return Image.fromarray(out)


def test_letter_spaced_capital_heading_is_one_line():
    result = segment_page(_capital_page(54))
    heads = [l for l in result.lines if np.median(l.baseline)<90 and l.discounted is None]
    assert len(heads)==1
    assert heads[0].x0<=35 and heads[0].x1>=590
    assert 'meanline' in heads[0].borrowed


def test_all_capital_running_head_is_not_dropped():
    result = segment_page(_capital_page(25))
    heads = [l for l in result.lines if np.median(l.baseline)<90 and l.discounted is None]
    assert len(heads)==1
    assert heads[0].ink_classes['tall_body'] >= 15
    assert 'meanline' in heads[0].borrowed


def test_text_crossing_faint_stamp_keeps_extent():
    page, truth, _ = page_fixture()
    stamp = Image.new('L',page.size,245); d=ImageDraw.Draw(stamp)
    d.ellipse((330,205,620,455),outline=175,width=7)
    d.line((370,420,580,265),fill=175,width=5)
    arr=np.minimum(np.asarray(page),np.asarray(stamp))
    result=segment_page(Image.fromarray(arr))
    active=[l for l in result.lines if l.discounted is None]
    assert len(active)==6
    assert all(l.x1>=490 for l in active)
    assert result.pixels.barriers[205:455,330:620].mean()<.01


def test_ornament_band_is_not_ocr_text():
    page, _, _=page_fixture()
    out=Image.new('L',(660,710),245);out.paste(page,(0,150))
    d=ImageDraw.Draw(out)
    for x in range(35,590,36):
        d.ellipse((x,25,x+35,95),fill=25)
    lines=page_line_segments(out)
    assert len(lines)==6
    assert min(np.median(l.baseline) for l in lines)>150


def test_faint_showthrough_is_reported_and_uniform_fade_survives():
    page,_,_=page_fixture()
    arr=np.asarray(page).copy()
    out=np.full((560,1200),245,np.uint8);out[:,:660]=arr
    out[:,660:1200]=np.where(arr[:,:540]<128,190,245)
    r=segment_page(Image.fromarray(out))
    faint=[l for l in r.lines if l.x0>=660]
    assert len(faint)==6
    assert all(l.discounted and l.contrast<.62 for l in faint)
    faded=Image.fromarray(np.where(arr<128,190,245).astype('uint8'))
    assert len(page_line_segments(faded))==6


def test_curled_line_start_has_all_source_ink():
    page, truth, _ = page_fixture()
    arr=np.asarray(page).copy(); warped=np.full_like(arr,245); target=np.zeros_like(truth)
    for x in range(arr.shape[1]):
        shift=round(-24*np.exp(-max(0,x-35)/60))
        stop=shift or None
        warped[:stop,x]=arr[-shift:,x]
        target[:stop,x]=truth[-shift:,x]
    result=segment_page(Image.fromarray(warped))
    assert_truth(result,target,6)
    assert max(l.x0 for l in result.lines)<=36


def test_neighbour_regions_share_the_whole_seam_including_whitespace():
    page, _, _ = page_fixture(curve=24, short=True)
    result = segment_page(page)
    for i, line in enumerate(result.lines):
        for j in set(line.neighbours['below'])-{-1}:
            lower=result.lines[j]
            xs=np.flatnonzero(line.neighbours['below']==j)
            other=xs+line.x0-lower.x0
            np.testing.assert_allclose(line.bottom[xs],lower.top[other],atol=1e-8)
            assert np.all(lower.neighbours['above'][other]==i)


def test_indented_lines_keep_paragraph_reading_order():
    page, _, _=page_fixture()
    arr=np.asarray(page).copy()
    arr[140:210,:130]=245
    arr[210:280,:170]=245
    result=segment_page(Image.fromarray(arr))
    lines=[l for l in result.lines if l.discounted is None]
    assert len(lines)==6
    assert len({l.column for l in lines})==1
    assert np.all(np.diff([np.median(l.baseline) for l in lines])>0)


def test_connected_table_frame_does_not_erase_periodic_text():
    # A compact table occupies less than half a large page. Its vertical rule
    # touches the first glyph of every row, forming one large component.
    page,truth,_=page_fixture()
    canvas=Image.new('L',(1000,1200),245);canvas.paste(page,(100,300))
    d=ImageDraw.Draw(canvas)
    d.line((134,340,134,710),fill=25,width=2)
    result=segment_page(canvas)
    lines=[l for l in result.lines if l.discounted is None]
    assert len(lines)==6
    assert all(l.x0<155 and l.x1>585 for l in lines)
    assert all(not (a<300<b and t<500<bot) for a,t,b,bot in result.pixels.nontext_boxes)
