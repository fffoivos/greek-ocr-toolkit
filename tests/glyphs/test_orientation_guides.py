"""Structural fixtures: paired fits, region inheritance and sparse abstention."""
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from greekocr.glyphs.orientation import Orientation, measure_orientation
from greekocr.glyphs.orientation_regions import axis_regions, page_regions, resolve_regions

FONT = Path(__file__).parents[1]/'fixtures/fonts/GFSDidot-Regular.ttf'


def text_page(text='λόγος καὶ ἀνθρώπων ἀγαθὸς κόσμος', rows=6):
    im=Image.new('L',(760,rows*65+40),255)
    draw=ImageDraw.Draw(im); font=ImageFont.truetype(str(FONT),36)
    for y in range(20,rows*65,65):draw.text((30,y),text,font=font,fill=0)
    return im


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_both_readings_fit_measured_font_and_accent_guides(angle):
    decision=measure_orientation(text_page().rotate(-angle,expand=True))
    assert decision.orientation_cw == angle
    evidence=decision.evidence['guide_test']
    assert {r['orientation_cw'] for r in evidence['readings']} == set(decision.alternatives)
    right=next(r for r in evidence['readings'] if r['orientation_cw']==angle)
    wrong=next(r for r in evidence['readings'] if r['orientation_cw']!=angle)
    assert right['accent_above'] > wrong['accent_above']
    assert wrong['mark_below'] > right['mark_below']
    assert right['contacts']['baseline'] >= 12
    assert all('accent_top' in line['contacts'] and 'font_bottom' in line['contacts'] for line in right['lines'])


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_numbers_alone_abstain_then_inherit_header(angle):
    numbers=text_page('1234567890 9876543210 36969',rows=4).rotate(-angle,expand=True)
    # Test pixel-only abstention as well as the explicit numeric contract.
    assert measure_orientation(numbers).orientation_cw is None
    numeric=measure_orientation(numbers,content_kind='numbers')
    header=measure_orientation(text_page(rows=2).rotate(-angle,expand=True))
    assert header.orientation_cw == angle
    rows=resolve_regions([dict(id='header',orientation_group='table',decision=header),
                          dict(id='figures',orientation_group='table',content_kind='numbers',decision=numeric)],main_id='header')
    assert rows[1]['decision'].orientation_cw == angle
    assert rows[1]['decision'].evidence['inherited_from']=='header'
    assert numeric.orientation_cw is None  # no mutation or circular numeric vote


def test_conflicting_headers_do_not_decide_numeric_rows():
    rows=resolve_regions([
        dict(id='a',orientation_group='g',decision=Orientation(axis='horizontal',orientation_cw=0)),
        dict(id='b',orientation_group='g',decision=Orientation(axis='horizontal',orientation_cw=180)),
        dict(id='n',orientation_group='g',content_kind='numbers',decision=Orientation(axis='horizontal'))])
    assert rows[-1]['decision'].orientation_cw is None


def test_third_orientation_is_unknown_with_hypotheses():
    rows=resolve_regions([dict(id=str(a),components=100-i*30,
                              decision=Orientation(axis='vertical' if a%180 else 'horizontal',
                                                   orientation_cw=a,alternatives=[a%180,a%180+180]))
                          for i,a in enumerate([0,90,180])],main_id='0')
    assert [r['decision'].orientation_cw for r in rows]==[0,90,None]
    assert rows[2]['decision'].alternatives == [0,180]
    assert rows[2]['decision'].evidence['rejected_orientation_cw'] == 180


@pytest.mark.parametrize('angle',[90,270])
def test_blind_two_orientation_composite(angle):
    main=text_page(rows=8); minority=text_page(rows=3).crop((0,0,650,220)).rotate(-angle,expand=True)
    composite=Image.new('L',(main.width+minority.width+100,max(main.height,minority.height)+40),255)
    composite.paste(main,(0,0));composite.paste(minority,(main.width+80,20))
    dominant,regions,_=page_regions(composite)
    assert dominant.orientation_cw==0
    local=[r for r in regions[1:] if r['axis']=='vertical']
    assert local and any(r['decision'].orientation_cw==angle for r in local)
    assert all(r['decision'].orientation_cw in (angle,None) for r in local)
    from greekocr.glyphs.oriented_page import oriented_page
    delivered=oriented_page(composite,use_osd=False)
    minority_words=[w for w in delivered.words if w.frame.rectangle(w.box).mean(0)[0]>main.width+80]
    assert minority_words and any(w.orientation.orientation_cw==angle for w in minority_words)
    assert all(w.orientation.orientation_cw in (angle,None) for w in minority_words)
    assert all(w.frame.orientation_cw==angle for w in minority_words if w.orientation.orientation_cw is not None)


def test_words_inherit_one_region_and_never_vote(monkeypatch):
    import greekocr.glyphs.oriented_page as mod
    # A caller-supplied region decision is propagated, even to short words.
    o=Orientation(axis='horizontal',orientation_cw=180,alternatives=[0,180])
    result=mod.oriented_page(text_page(rows=2).rotate(180),dominant=o,use_osd=False,discover=False)
    assert len(result.words)>4
    assert all(w.orientation.orientation_cw==180 and w.orientation.evidence['inherited_from']=='page' for w in result.words)
    assert measure_orientation(text_page(rows=1),unit='word').orientation_cw is None


def test_uniform_page_not_vetoed_by_cross_line_neighbours(monkeypatch):
    import greekocr.deploy.docling_plugin.orientation as mod
    from docling_core.types.doc import Size
    image=text_page().rotate(-90,expand=True);size=Size(width=image.width,height=image.height)
    backend=NS(is_valid=lambda:True,get_size=lambda:size,get_page_image=lambda scale:image)
    page=NS(page_no=1,_backend=backend,size=size,_image_cache={1:image},parsed_page='stale')
    # The old 2% heuristic vetoed this: an accidental perpendicular short
    # chain lies entirely in a coherent vertical line region.
    proposals=[dict(axis='vertical',components=90,box=[20,20,70,600],xheight=20,axis_confidence=.9),
               dict(axis='horizontal',components=3,box=[25,50,65,65],xheight=20,axis_confidence=.7)]
    monkeypatch.setattr(mod,'discover_directions',lambda im:proposals)
    seen=[]
    adapter=mod.PageOrientationAdapter(lambda c,p:seen.extend(p) or iter(p))
    list(adapter(NS(),[page]))
    assert adapter.records[0]['applied'] and not adapter.records[0]['mixed']
    assert np.array_equal(page._backend.get_page_image(),image.rotate(90,expand=True))
    assert seen[0].parsed_page is None


def test_word_partition_retains_faint_ink_in_boundary_safe_piece():
    from greekocr.glyphs.oriented_page import _word_boxes
    image=Image.new('L',(200,65),255);draw=ImageDraw.Draw(image)
    draw.rectangle((10,25,65,48),fill=0);draw.rectangle((115,25,180,48),fill=0)
    # An accent already included by the detector is too faint for the word-gap
    # Otsu mask. Tightening to that mask used to throw this ink away.
    draw.rectangle((25,5,28,8),fill=210)
    piece=NS(box=(0,0,200,65),line=NS(xheight=20))
    boxes=_word_boxes(image,piece)
    assert len(boxes)==2
    assert any(a<=25<b and t<=5<bot for a,t,b,bot in boxes)
    covered=np.zeros((65,200),bool)
    for a,t,b,bot in boxes:covered[t:bot,a:b]=True
    assert covered[np.asarray(image)<255].all()


def test_pixel_detected_table_survives_unknown_perpendicular_proposal(monkeypatch):
    import greekocr.glyphs.oriented_page as mod
    import greekocr.glyphs.orientation_regions as regions
    from greekocr.glyphs.page_text_lines import segment_page
    from greekocr.glyphs.table_lines import prepare_delivery
    image=text_page(rows=3)
    segmentation=segment_page(image)
    segmentation,pieces,_=prepare_delivery(image,segmentation,[])
    for piece in pieces:
        piece.table_id='pixel-table-fixture'
    main=Orientation(axis='horizontal',orientation_cw=0)
    unknown=Orientation(axis='vertical',alternatives=[90,270])
    row=dict(id='cross-line',box=[20,20,80,image.height-20],xheight=20,decision=unknown)
    second={**row,'id':'another-cross-line','box':[100,20,160,image.height-20]}
    monkeypatch.setattr(regions,'page_regions',lambda *a,**kw:(main,[dict(id='page'),row,second],[]))
    table_fits=[]
    def table_orientation(*args,**kwargs):
        table_fits.append(args[0].size)
        return Orientation(axis='horizontal')
    monkeypatch.setattr(mod,'measure_orientation',table_orientation)
    result=mod.oriented_page(image,dominant=main,segmentation=segmentation,pieces=pieces,discover=False)
    assert len(result.words)==len(pieces)>0
    assert all(w.table_id=='pixel-table-fixture' for w in result.words)
    assert [w.box for w in result.words]==[p.box for p in pieces]
    assert all(w.frame.orientation_cw==0 for w in result.words)
    assert result.groups[-1]['delivery']=='table-region-preserved'
    assert len(table_fits)==1  # both proposals inspect the same unchanged table
