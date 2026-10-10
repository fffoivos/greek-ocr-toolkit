"""Geometry contracts, real frozen axis fixtures, abstention and crop policy."""
import json
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont, ImageOps

from greekocr.glyphs.orientation import (Orientation, QuarterTurn, canonical_word_crop,
                                       discover_directions, measure_orientation, recognizer_polarity)

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT/'.astra/orientation_research'
FONT = ROOT/'tests/fixtures/fonts/GFSDidot-Regular.ttf'


@pytest.mark.parametrize('angle',[0,90,180,270])
@pytest.mark.parametrize('offset',[(0,0),(11.25,13.5)])
def test_frame_round_trip_corners_guides_and_anisotropic_page_scale(angle,offset):
    frame = QuarterTurn(200,310,angle,offset)
    source = np.array([[0,0],[200,0],[200,310],[0,310]],float)+offset
    local = frame.points(source)
    assert np.max(abs(frame.points(local,inverse=True)-source)) < 1e-10
    corners = frame.rectangle((20,30,70,50))
    assert np.allclose(frame.points(corners),[[20,50],[70,50],[70,30],[20,30]])
    # Actual independent render ratios, crop offsets, all four ordered corners.
    scale = np.array([2.999,3.002])
    assert np.max(abs(corners/scale*scale-corners)) < 1e-10
    from docling_core.types.doc.page import BoundingRectangle
    from docling_core.types.doc import CoordOrigin
    r = BoundingRectangle(**{f'r_{axis}{i}':p[j] for i,p in enumerate(corners)
                              for j,axis in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)
    assert r.angle_360 == (-angle)%360


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_pixels_and_boundary_frame_agree(angle):
    im = Image.new('L',(101,151),255)
    ImageDraw.Draw(im).rectangle((20,30,39,49),fill=0)
    f = QuarterTurn(*im.size,angle)
    yy,xx = np.nonzero(np.asarray(f.image(im))==0)
    expected = f.rectangle((20,30,40,50),inverse=False)
    assert [xx.min(),yy.min(),xx.max()+1,yy.max()+1] == [*expected.min(0),*expected.max(0)]


def test_invalid_frames_rejected():
    for w,h,a in [(0,20,0),(20,float('nan'),0),(20,20,45)]:
        with pytest.raises(ValueError):QuarterTurn(w,h,a)


def test_unknown_does_not_become_zero_or_recognition_confidence():
    im = Image.new('L',(100,100),255)
    o = measure_orientation(im)
    assert o.orientation_cw is None and o.axis == 'unknown'
    assert o.to_record()['alternatives'] == [0,90,180,270]
    ambiguous = NS(recognize=lambda strips:[('123',.99),('321',.99)])
    o = recognizer_polarity(im,Orientation(axis='horizontal',alternatives=[0,180]),ambiguous)
    assert o.orientation_cw is None and len(o.evidence['readings']) == 2
    assert all(r['recognition_confidence']==.99 for r in o.evidence['readings'])


def test_margin_and_garbage_rejection():
    im = Image.new('L',(160,60),255)
    ImageDraw.Draw(im).text((10,5),'λόγος',font=ImageFont.truetype(str(FONT),36),fill=0)
    o = Orientation(axis='horizontal',alternatives=[0,180])
    for predictions in [[('',.999),('1234',.99)],[('λόγος',.95),('γολός',.94)]]:
        assert recognizer_polarity(im,o,NS(recognize=lambda s:predictions)).orientation_cw is None
    result = recognizer_polarity(im,o,NS(recognize=lambda s:[('λόγος',.99),('123',.5)]))
    assert result.orientation_cw == 0


def test_stable_word_padding_on_grey_paper():
    core = Image.new('L',(200,70),185)
    ImageDraw.Draw(core).text((15,4),'λόγος',font=ImageFont.truetype(str(FONT),42),fill=30)
    a = canonical_word_crop(ImageOps.expand(core,8,255))
    b = canonical_word_crop(ImageOps.expand(core,20,255))
    assert a.size == b.size and np.array_equal(a,b)


def _cases():
    path = RESEARCH/'testset/manifest.json'
    return json.loads(path.read_text())['cases'] if path.exists() else []


@pytest.mark.parametrize('case',[c for c in _cases() if c['kind'] in ('whole','skew') or c['unit']=='word'],ids=lambda c:c['id'])
def test_fixed_research_ink_axis(case):
    image = Image.open(RESEARCH/case['path'])
    decision = measure_orientation(image,unit=case['unit'])
    assert decision.axis == ('horizontal' if case['truth_cw']%180==0 else 'vertical')


def test_discovery_precedes_horizontal_fitting(monkeypatch):
    import greekocr.glyphs.oriented_page as mod
    events = []
    monkeypatch.setattr(mod,'discover_directions',lambda im:events.append('discover') or [])
    monkeypatch.setattr(mod,'measure_orientation',lambda *a,**kw:Orientation(axis='horizontal',orientation_cw=0))
    monkeypatch.setattr(mod,'segment_page',lambda im:events.append('fit') or NS())
    monkeypatch.setattr(mod,'prepare_delivery',lambda im,s,r,**kw:(s,[],[]))
    mod.oriented_page(Image.new('L',(100,100),255))
    assert events == ['discover','fit']


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_normalized_fitter_words_and_guides_reversible(angle):
    from greekocr.glyphs.oriented_page import oriented_page
    im = Image.new('L',(700,240),255);d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT),32)
    for y in (20,85,150):d.text((30,y),'λόγος καὶ ἀνθρώπων λόγος',font=font,fill=0)
    base = oriented_page(im,dominant=Orientation(axis='horizontal',orientation_cw=0),use_osd=False,discover=False)
    image = im.rotate(-angle,expand=True)
    result = oriented_page(image,dominant=Orientation(axis='vertical' if angle%180 else 'horizontal',orientation_cw=angle),use_osd=False,discover=False)
    assert len(result.words)==len(base.words)>6
    for a,b in zip(base.words,result.words):
        assert a.box == b.box and np.array_equal(a.crop,b.crop)
        record = b.to_record(image.size)
        assert record['orientation_cw']==angle
        assert np.allclose(b.frame.points(record['corners_pixels']),a.frame.rectangle(a.box))
        assert record['guides_local']==a.guides


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_rotated_artifact_reframing_preserves_pixel_and_page_units(angle):
    from greekocr.glyphs.oriented_page import OrientedWord
    from scripts.glyphs.archive.render_orientation_round4 import source_records
    image=Image.new('L',(500,600),255);outer=QuarterTurn(*image.size,angle)
    frame=QuarterTurn(100,60,180,(100,200))
    word=OrientedWord(0,'g',0,(10,10,80,40),frame,
        Orientation(axis='horizontal',orientation_cw=180,alternatives=[0,180]),
        dict(baseline=[[10,30],[80,30]]),Image.new('L',(70,30),255),text='λόγος',recognition_confidence=.9)
    record=source_records(NS(words=[word]),image,outer)[0]
    p=np.array([[10,40,1],[80,40,1],[80,10,1],[10,10,1]])
    assert np.allclose((p@np.array(record['local_to_pixels']).T)[:,:2],record['corners_pixels'])
    assert np.allclose((p@np.array(record['local_to_page']).T)[:,:2],record['corners_page'])
    assert np.allclose(np.array(record['guides_pixels']['baseline'])/3,record['guides_page']['baseline'])
    assert record['orientation_cw']==(180+angle)%360
