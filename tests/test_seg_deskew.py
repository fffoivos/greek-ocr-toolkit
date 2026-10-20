"""SEG-DESKEW-1 measurement regressions under the current crop gate, offline."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
from tests._paths import ADMISSION, SEG_STEPS
from types import SimpleNamespace

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytest
from scipy import ndimage as ndi

from greekocr.harvest.line_pipeline_native import ASSETS, NativeSegmenter

ROOT = Path(__file__).resolve().parents[1]
DRAW = ADMISSION / 'segeval1'


def rows(path, key):
    return {r[key]: r for r in map(json.loads, _data_input(path).read_text().splitlines())}


@pytest.fixture(scope='module')
def native(predictor_path):
    worker = NativeSegmenter({'segmentation': {'version': '0.7'}}, predictor_path)
    yield worker
    worker.close()


@pytest.mark.parametrize('line_id', [
    '51db636c-p000048-l0024',
    'gazette_modern--6d6a6fe53e769b59--s000-l0009',
    'gazette_modern--59ebc3dbeb1516d3--s000-l0066',
])
def test_real_zero_angle_is_digit_exact(native, line_id, monkeypatch):
    # This historical 0.6 arithmetic fixture includes a vertical crop. Retain
    # its S1 orientation for this historical comparison; S2 physical rotation
    # and full replay invariance are checked in test_seg_gate and S2 readback.
    require_file('docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl')
    import importlib.util
    path=SEG_STEPS / 's2/baseline/greekocr/harvest/filtering_assets/crop-tools.py'
    spec=importlib.util.spec_from_file_location('historical_s1_crop_tools',path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    monkeypatch.setattr(native.crop_tools,'orient_crop',old.orient_crop)
    # Isolate the historical row-frame arithmetic; S4 small path is tested separately.
    monkeypatch.setattr(native.crop_tools,'is_small_segment',lambda *args: False)
    before = rows(DRAW/'keys/census02_segmentation_evidence.jsonl', 'row_id')[line_id]
    sealed = rows(DRAW/'keys/sealed_decisions.jsonl', 'row_id')[line_id]
    row = rows(DRAW/'keys/selected_features.jsonl', 'row_id')[line_id]
    row = dict(row, **sealed['segmentation']['binding'], raw_text=sealed['google_text'],
               crop_path=str(require_file(DRAW/'crops'/f'{line_id}.png')))
    # Measure theta=0 independently: 0.7 may reject a clipped crop before
    # Stage B. This regression still checks the unchanged 0.6 arithmetic.
    from greekocr.glyphs.components import line_glyphs
    from greekocr.glyphs.baseline import text_lines
    from greekocr.glyphs.orientation import QuarterTurn, measure_orientation
    image,_ = native.crop_tools.orient_crop(Image.open(_data_input(row['crop_path'])),row.get('primary_class'),measure_orientation,QuarterTurn)
    glyphs = line_glyphs(image)
    lines = text_lines(glyphs)
    complete = [l for l in lines if l.visible >= .9 and l.votes >= 6 and l.x1-l.x0 >= 3*glyphs.band.xh]
    if len(complete) == 1 and complete[0].side != 'main' and lines[0].visible < .9:
        mid = float(np.median(complete[0].base[complete[0].x0:complete[0].x1+1]));xh = glyphs.band.xh
        glyphs = line_glyphs(image,focus=(mid-.4*xh,mid+.4*xh))
    components = [dict(index=c.index,bbox=[c.x0,c.y0,c.x1,c.y1],role=c.role,area=c.area) for c in glyphs.components]
    yy,xx = np.nonzero(glyphs.ink)
    f = native.crop_tools.features_from_observation(width=glyphs.width,height=glyphs.height,
        components=components,ink_box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],
        ink_pixels=int(glyphs.ink.sum()),xheight=glyphs.band.xh,xheight_source=glyphs.band.xh_source,
        support_count=glyphs.band.n_support,chars=before['evidence']['characters'],labels=glyphs.labels,angle_deg=0)
    b = before['evidence']; box = f['candidate_text_box'];rf = f['row_frame_text_box']
    prediction = native.predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=row['script_class']))
    assert box['bbox'] == b['box_evidence']['bbox']
    assert prediction['expected'] == b['box_evidence']['prediction']['expected']
    assert (glyphs.height-box['height'])/rf['height'] == b['padding_evidence']['total_padding_line_heights']
    x0,y0,x1,y1 = box['bbox']
    assert rf == dict(angle_deg=0,length=x1-x0,height=y1-y0,corners=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
    after = native(row)['evidence']
    if after['gate']['verdict'] == 'PASS':
        assert after['box_evidence']['prediction'] == prediction
        assert after['box_evidence']['row_frame'] == rf
    else:
        expected_reason = 'gate: reading direction unresolved' if after['orientation_resolved'] is False else 'gate: target line cut'
        assert after['gate']['reason'] == expected_reason
        assert not after['box_evidence']['available']


def observation(crop_tools, image, angle):
    ink = np.asarray(image) < 128
    labels, _ = ndi.label(ink)
    components = []
    for index, slices in enumerate(ndi.find_objects(labels), 1):
        if slices is None:
            continue
        ys, xs = slices
        components.append(dict(index=index, bbox=[xs.start,ys.start,xs.stop,ys.stop],
                               role='letter', area=int((labels[slices] == index).sum())))
    yy, xx = np.nonzero(ink)
    return crop_tools.features_from_observation(width=image.width, height=image.height,
        components=components, ink_box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],
        ink_pixels=int(ink.sum()), xheight=24, xheight_source='test', support_count=20, chars=40,
        labels=labels, angle_deg=angle)


@pytest.mark.parametrize('angle', [2, -2])
def test_rendered_line_row_frame_restores_dimensions(native, angle):
    font = ImageFont.truetype(str(ROOT/'tests/fixtures/fonts/GFSDidot-Regular.ttf'), 32)
    image = Image.new('L', (1200, 160), 255)
    ImageDraw.Draw(image).text((40, 60), 'ἀνδρώας κύστεως μεταξὺ τῶν τῆς ἥβης καλουμένων ὀστῶν', font=font, fill=0)
    upright = observation(native.crop_tools, image, 0)['row_frame_text_box']
    # PIL is counterclockwise positive; the measurement convention is clockwise.
    skewed = image.rotate(-angle, resample=Image.Resampling.NEAREST, fillcolor=255)
    features = observation(native.crop_tools, skewed, angle)
    box = features['row_frame_text_box']
    assert abs(box['height'] - upright['height']) <= 1
    assert abs(box['length']/upright['length'] - 1) <= .01
    corners = np.asarray(box['corners'])
    assert np.linalg.norm(corners[1]-corners[0]) == pytest.approx(box['length'])
    assert np.linalg.norm(corners[2]-corners[1]) == pytest.approx(box['height'])
    assert np.degrees(np.arctan2(*(corners[1]-corners[0])[::-1])) == pytest.approx(angle)


def test_tall_crop_padding_uses_upright_envelope_and_row_height(native, monkeypatch, tmp_path):
    import greekocr.glyphs.baseline as baseline
    import greekocr.glyphs.components as components
    w, h = 300, 160
    slope = np.tan(np.radians(2))
    yy, xx = np.indices((h,w))
    ink = (xx >= 20) & (xx < 280) & (yy >= 65+slope*(xx-150)) & (yy < 85+slope*(xx-150))
    labels = ink.astype(np.int32)
    ys, xs = np.nonzero(ink)
    bbox = [int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    glyphs = SimpleNamespace(width=w, height=h, ink=ink, labels=labels,
        components=[SimpleNamespace(index=1,x0=bbox[0],y0=bbox[1],x1=bbox[2],y1=bbox[3],role='letter',area=int(ink.sum()),touches=[])],
        band=SimpleNamespace(xh=20,xh_source='test',n_support=20))
    base = 85+slope*(np.arange(w)-150)
    from greekocr.glyphs.components import Band
    glyphs.band = Band(base-20,base,20.,20,tuple((float(x),float(base[x]),'bottom') for x in range(20,280,13)),xh_source='test')
    glyphs.letter_w = 8.
    c = glyphs.components[0]
    c.h = bbox[3]-bbox[1];c.w = bbox[2]-bbox[0];c.cx = (bbox[0]+bbox[2])/2
    line = SimpleNamespace(side='main',visible=1.,votes=20.,x0=20,x1=279,
        ascender=base-30,mean=base-20,base=base,descender=base+5)
    monkeypatch.setattr(components, 'line_glyphs', lambda image: glyphs)
    monkeypatch.setattr(baseline, 'text_lines', lambda glyphs: [line])
    path = tmp_path/'tall.png'
    Image.fromarray(np.where(ink,0,255).astype(np.uint8)).save(path)
    row = dict(parent_id='test',id='tall',split='unassigned',crop_path=str(path),
        crop_sha256=hashlib.sha256(_data_input(path).read_bytes()).hexdigest(),raw_text='abcdefghi',script_class='pooled')
    answer = native(row)
    p = answer['evidence']['padding_evidence']
    rf = answer['evidence']['box_evidence']['row_frame']
    assert rf['angle_deg'] == pytest.approx(2)
    assert p['upright_box_height'] == bbox[3]-bbox[1]
    assert p['row_frame_height'] == rf['height']
    assert p['total_padding_line_heights'] == (h-p['upright_box_height'])/p['row_frame_height']
    assert h > p['upright_box_height'] + 1.5*p['row_frame_height']
    # Drive the unchanged padding rule independently of length-rule precedence.
    evidence = deepcopy(answer['evidence'])
    evidence['characters'] = evidence['box_evidence']['prediction']['expected']
    result = native.service.call(dict(operation='decide',policy_sha256=native.policy_sha,evidence=evidence))
    assert result['reason'] == 'length: Top and bottom padding together exceed 1.5 target-line heights.'
