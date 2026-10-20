"""SEG-GATE-2: exactly three rules; cut diagnostics never affect decisions."""
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import ADMISSION, SEG_STEPS, require_file

import numpy as np
from PIL import Image
import pytest

from greekocr.glyphs.baseline import text_lines
from greekocr.glyphs.components import Band, Component, LineGlyphs
from greekocr.harvest.line_pipeline_native import NativeSegmenter

ROOT = Path(__file__).resolve().parents[1]
D = ADMISSION / 'segeval1'


def load(path, key):
    return {r[key]: r for r in map(json.loads, _data_input(path).read_text().splitlines())}


@pytest.fixture(scope='module')
def native():
    worker = NativeSegmenter({'segmentation': {'version': '0.9-s2'}},
        ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
    yield worker
    worker.close()


def real_row(rid):
    require_file(D/'crops'/f'{rid}.png')
    seal = load(D/'keys/sealed_decisions.jsonl', 'row_id')[rid]
    feature = load(D/'keys/selected_features.jsonl', 'row_id')[rid]
    # Explicitly omit page context, even if the feature has it.
    return dict(seal['segmentation']['binding'], raw_text=seal['google_text'],
        script_class=feature['script_class'], primary_class=feature['primary_class'],
        crop_path=str(require_file(D/'crops'/f'{rid}.png')))


def test_cut_witness_decides_by_frozen_length(native):
    require_file('docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_segeval1.jsonl')
    rid = '847e1ec1-p000015-l0035'
    before = load(D/'deskew/replay_segeval1.jsonl','line_id')[rid]['after']
    answer = native(real_row(rid))
    gate = answer['evidence']['gate']
    assert gate['verdict'] == 'PASS' and answer['reason'].startswith('length:')
    assert gate['main_cut']['baseline_exit']
    assert gate['main_cut']['crossings'][0]['x'] == pytest.approx(1817.4010238826568)
    assert gate['main_cut']['cut_spans'] == [dict(x0=1990,x1=2044,edge='bottom',min_visible=.869)]
    assert len(gate['main_cut']['cut_letters']) == 10
    assert 'row_frame_taller' not in gate['main_cut']
    box = answer['evidence']['box_evidence']
    assert box == before['evidence']['box_evidence']
    ratio = (answer['evidence']['characters']+1)/(box['predictions'][2]+1)
    assert answer['evidence']['padding_evidence']['total_padding_line_heights'] <= 1.5
    assert answer['verdict'] == ('DROP' if ratio < .30 or ratio > 2.00 else 'KEEP')
    print(f'{rid}: length ratio={ratio!r}; verdict={answer["verdict"]}')


def test_partial_body_witness_keeps_without_context(native):
    answer = native(real_row('b8b6779da9a68fbed0ccdb5b-p000011-l0018'))
    e = answer['evidence']
    assert answer['verdict'] == 'KEEP' and answer['reason'].startswith('length:')
    assert e['gate']['verdict'] == 'PASS' and e['gate']['reason'] == 'gate: pass'
    assert e['gate']['whole_words'] == 0 and e['gate']['cutoff_words'] > 0
    assert e['gate']['complete_rows'] == [] and not e['gate']['main_cut']['cut']
    assert e['neighbour_evidence']['status'] == 'unavailable'


def synthetic(neighbour_xs, *, neighbour_height=20):
    """Native component/role witness on a physical raster; existing text_lines."""
    w, h, xh = 400, 85, 20
    labels = np.zeros((h,w), dtype=np.int32)
    components = []
    for role, xs, y0, y1 in [('letter', range(10,390,14), 45,65),
                              ('neighbour', neighbour_xs, 25-neighbour_height,25)]:
        for x in xs:
            cid = len(components)+1
            labels[y0:y1,x:x+8] = cid
            touches = tuple(k for k,v in [('left',x==0),('right',x+8==w),('top',y0==0),('bottom',y1==h)] if v)
            components.append(Component(cid,x,y0,x+8,y1,8*(y1-y0),0,0,2.,0.,1.,touches,role=role))
    main = [c for c in components if c.role == 'letter']
    support = tuple((c.cx,65.,'bottom') for c in main)
    band = Band(np.full(w,45.),np.full(w,65.),xh,len(support),support)
    ink = labels > 0
    g = LineGlyphs(np.where(ink,0.,255.),ink,labels,components,band,255.,0.,2.,8.,np.zeros_like(labels))
    packed = [dict(index=c.index,bbox=[c.x0,c.y0,c.x1,c.y1],role=c.role,area=c.area,touches=list(c.touches)) for c in components]
    return g, packed


def gate_for(native, xs, **kwargs):
    glyphs, comps = synthetic(xs, **kwargs)
    lines, cut = native.crop_tools.line_inventory(glyphs,text_lines(glyphs),comps,0)
    e = dict(lines=lines,gate=dict(main_cut=cut),orientation_resolved=True,gate_only=True)
    return native.service.call(dict(operation='decide',policy_sha256=native.policy_sha,evidence=e)), e


def test_complete_second_line(native):
    gate, e = gate_for(native, range(10,390,14))
    assert (gate['verdict'],gate['reason']) == ('DROP','gate: second complete line')
    assert len(gate['complete_rows']) == 1
    row = e['lines'][gate['complete_rows'][0]]
    assert row['bodies'] >= 6 and row['coverage'] >= .6 and row['visible'] >= .9


@pytest.mark.parametrize('words,verdict,reason', [(3,'DROP','gate: too many whole neighbour words'),(2,'PASS','gate: pass')])
def test_word_allowance(native, words, verdict, reason):
    xs = [x for start in [30,90,150][:words] for x in [start,start+12]]
    gate, _ = gate_for(native, xs)
    assert (gate['verdict'],gate['reason']) == (verdict,reason)
    assert gate['whole_words'] == words and gate['cutoff_words'] == 0
    assert gate['complete_rows'] == []


def test_edge_contact_and_one_body_do_not_veto_whole_word(native):
    gate, e = gate_for(native, [0,12,90,102,150])
    assert gate['verdict'] == 'DROP' and gate['whole_words'] == 3 and gate['cutoff_words'] == 0
    neighbour = next(l for l in e['lines'] if l['side'] != 'main')
    assert neighbour['word_groups'][0]['touches_horizontal_edge']


@pytest.mark.parametrize('visible,whole', [(.949,0),(.950,2)])
def test_ninety_five_percent_body_boundary(native,visible,whole):
    from dataclasses import replace
    glyphs, comps = synthetic([30,42,90,102],neighbour_height=25)
    lines = text_lines(synthetic([30,42,90,102])[0])
    lines = [replace(l,base=np.full(400,20*visible),mean=np.full(400,20*(visible-1)))
             if l.side != 'main' else l for l in lines]
    inventory,_ = native.crop_tools.line_inventory(glyphs,lines,comps,0)
    assert sum(l['whole_words'] for l in inventory) == whole


def test_one_cut_body_makes_entire_word_cutoff(native):
    from dataclasses import replace
    glyphs, comps = synthetic([30,42],neighbour_height=25)
    lines = text_lines(synthetic([30,42,90,102])[0])
    for i,l in enumerate(lines):
        if l.side != 'main':
            base=np.full(400,20.);base[46]=18.98
            lines[i]=replace(l,base=base,mean=base-20)
    inventory,_=native.crop_tools.line_inventory(glyphs,lines,comps,0)
    word=next(l for l in inventory if l['side']!='main')['word_groups'][0]
    assert word['bodies']==2 and not word['whole']
    assert [b['visible'] for b in word['body_visibility']]==pytest.approx([1.,.949])


def test_stage_b_zero_angle_equals_06_to_digit(native):
    require_file('docs/records/harvest/collect_v3_admission/segeval1/deskew/replay_segeval1.jsonl')
    rid = '51db636c-p000048-l0024'
    before = load(D/'deskew/replay_segeval1.jsonl','line_id')[rid]['after']['evidence']
    after = native(real_row(rid))['evidence']
    assert after['gate']['verdict'] == 'PASS'
    assert after['box_evidence']['row_frame']['angle_deg'] == 0
    assert after['box_evidence'] == before['box_evidence']
    assert after['padding_evidence'] == before['padding_evidence']


@pytest.mark.parametrize('change,reason', [
    ('no_main','gate: no main row found'),('orientation','gate: reading direction unresolved'),
])
def test_gate_precedence_and_only_two_uncertainties(native,change,reason):
    gate,e = gate_for(native,[30,42,90,102,150,162])
    if change == 'no_main': e['lines'] = [l for l in e['lines'] if l['side'] != 'main']
    if change == 'orientation': e['orientation_resolved'] = False
    result = native.service.call(dict(operation='decide',policy_sha256=native.policy_sha,evidence=e))
    assert result['reason'] == reason
    assert result['verdict'] == 'UNCERTAIN'


@pytest.mark.parametrize('diagnostic', [
    dict(cut=True), dict(baseline_exit=True), dict(low_visibility_span=True),
    dict(crossings=[dict(line='baseline',meaning='leaves the crop')]),
    dict(cut_spans=[dict(min_visible=0)]), dict(cut_letters=[dict(body_cut=1)]),
    dict(row_frame_height=1000,upright_box_height=1),
])
def test_cut_diagnostics_cannot_change_gate_or_final_decision(native,diagnostic):
    gate,e = gate_for(native,[30,42,90,102])
    e.update(gate_only=False,characters=20,box_evidence=dict(available=True,predictions=[None,None,20]),
        padding_evidence=dict(available=True,total_padding_line_heights=0))
    request = dict(operation='decide',policy_sha256=native.policy_sha)
    before = native.service.call(dict(request,evidence=e))
    e['gate']['main_cut'].update(diagnostic)
    assert native.service.call(dict(request,evidence=e)) == before
    e['gate_only'] = True
    after = native.service.call(dict(request,evidence=e))
    assert (after['verdict'],after['reason']) == (gate['verdict'],gate['reason']) == ('PASS','gate: pass')


def test_context_cannot_change_gate(native):
    gate,e = gate_for(native,[30,42,90,102])
    e['neighbour_evidence'] = dict(status='measured',whole_neighbour_words=99,additional_full_line_count=2)
    result = native.service.call(dict(operation='decide',policy_sha256=native.policy_sha,evidence=e))
    assert result == gate


@pytest.mark.parametrize('error',[FileNotFoundError('missing page'),ValueError('context page hash mismatch')])
def test_optional_context_failure_cannot_prevent_crop_decision(native,monkeypatch,error):
    def unavailable(*args): raise error
    monkeypatch.setattr(native,'context',unavailable)
    answer = native(real_row('b8b6779da9a68fbed0ccdb5b-p000011-l0018'))
    assert answer['verdict'] == 'KEEP'
    assert answer['evidence']['gate']['verdict'] == 'PASS'
    assert answer['evidence']['context_unavailable']['error']['type'] == type(error).__name__


@pytest.mark.parametrize('width,height,turned', [(22,23,True),(22,22,False),(24,22,False)])
def test_s2_exact_height_boundary(native,width,height,turned):
    from greekocr.glyphs.orientation import QuarterTurn
    def forbidden(*args,**kwargs):
        raise AssertionError('S2 must not consult an orientation detector')
    image=Image.fromarray(np.arange(width*height,dtype=np.uint16).reshape(height,width))
    out,frame=native.crop_tools.orient_crop(image,'numerics_tables',forbidden,QuarterTurn)
    expected=image.transpose(Image.Transpose.ROTATE_270) if turned else image
    assert np.array_equal(out,expected)
    assert frame['orientation_resolved']
    assert frame['normalization_cw']==(270 if turned else 0)


def test_s2_asymmetric_clockwise_pixel_and_boundary_mapping(native):
    from greekocr.glyphs.orientation import QuarterTurn
    image=Image.fromarray(np.arange(35,dtype=np.uint8).reshape(7,5))
    out,frame=native.crop_tools.orient_crop(image,None,None,QuarterTurn)
    matrix=np.asarray(frame['source_to_measurement'])
    for y in range(7):
        for x in range(5):
            assert out.getpixel((7-1-y,x))==image.getpixel((x,y))
            assert np.array_equal(matrix@np.array([x+.5,y+.5,1]),[7-y-.5,x+.5,1])


@pytest.mark.parametrize('size',[(1,1),(24,22),(41,41),(80,10)])
def test_s2_horizontal_orientation_byte_identical_to_s1(native,size):
    import importlib.util
    from greekocr.glyphs.orientation import QuarterTurn
    path=SEG_STEPS / 's2/baseline/greekocr/harvest/filtering_assets/crop-tools.py'
    spec=importlib.util.spec_from_file_location('s1_crop_tools',path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    image=Image.fromarray(np.arange(size[0]*size[1],dtype=np.uint16).reshape(size[1],size[0]))
    a,af=old.orient_crop(image,None,None,QuarterTurn)
    b,bf=native.crop_tools.orient_crop(image,None,None,QuarterTurn)
    assert a.tobytes()==b.tobytes() and af==bf


@pytest.mark.parametrize('chars,verdict', [(2999, 'KEEP'), (19999, 'KEEP'), (2998, 'DROP'), (20000, 'DROP')])
def test_s5_mode2_length_boundaries(native, chars, verdict):
    # (chars+1)/(9999+1) = .30, 2.00, .2999, 2.0001.
    # Both orchestration branches exercise the two default-band entry points.
    for small in (False, True):
        evidence = dict(characters=chars, small_segment=small,
            box_evidence=dict(available=True, predictions=[None, None, 9999]),
            padding_evidence=dict(available=True, total_padding_line_heights=0),
            lines=[dict(side='main', votes=1)])
        result = native.service.call(dict(operation='decide', policy_sha256=native.policy_sha, evidence=evidence))
        assert result['verdict'] == verdict
        assert result['reason'].startswith('length:')
