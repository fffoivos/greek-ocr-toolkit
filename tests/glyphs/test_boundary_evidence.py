"""Independent ink/layout adversaries for the Q1b boundary contract."""
from copy import deepcopy
import json

import numpy as np
from PIL import Image, ImageDraw
import pytest

from greekocr.glyphs.boundary_evidence import BoundaryEvidence
from greekocr.glyphs.line_structure import build_structure, join_pieces, _boundary
from test_line_structure import line, cell, geometry


def columns(scale=1, *, rows=6, gap=40, letter_gap=3):
    page = Image.new('L',(400,260),255)
    draw = ImageDraw.Draw(page)
    lines = []
    for y in range(40,40+rows*30,30):
        for a,b in ((20,160),(160+gap,340)):
            l = line(a,b,y)
            lines.append(l)
            for x in range(a,b-5,6+letter_gap):
                draw.rectangle((x,y-10,x+5,y-1),fill=0)
    if scale != 1:
        page = page.resize((page.width*scale,page.height*scale),Image.Resampling.NEAREST)
        for l in lines:
            for k in ('x0','x1','xheight'): l[k] *= scale
            for k in geometry(l):
                if isinstance(l[k],list): l[k] = np.repeat(np.asarray(l[k])*scale,scale).tolist()
    return page,lines,_boundary('gutter',(160+gap/2)*scale,0,(160+gap/2)*scale,260*scale,width=gap*scale)


@pytest.mark.parametrize('scale',[1,2,3])
def test_local_spacing_accepts_actual_sustained_columns_at_each_resolution(scale):
    page,lines,boundary = columns(scale)
    old = deepcopy(lines)
    s = build_structure(lines,[],page.size,boundaries=[boundary],fold=False,page=page)
    assert len(s['boundaries']) == 1
    assert s['boundaries'][0]['evidence']['side_row_counts'] == [6,6]
    assert len(s['columns']) == 2
    assert json.loads(json.dumps(s,allow_nan=False)) == s
    assert [geometry(l) for l in lines] == [geometry(l) for l in old]


@pytest.mark.parametrize('rows',[1,2])
def test_one_or_two_rows_are_not_column_blocks(rows):
    page,lines,boundary = columns(rows=rows)
    assert not BoundaryEvidence(page,lines).gutter(boundary)['accepted']


def test_letter_spaced_heading_uses_its_own_size_not_body_size():
    page,lines,boundary = columns(gap=40)
    heading = line(20,340,225)
    heading['xheight'] = 40
    for key in ('baseline','meanline','top','bottom'):
        heading[key] = [dict(baseline=225,meanline=185,top=180,bottom=230)[key]]*320
    draw = ImageDraw.Draw(page)
    for x in (20,100,200,280):draw.rectangle((x,185,x+35,224),fill=0)
    lines.append(heading)
    e = BoundaryEvidence(page,lines).gutter(boundary)
    assert e['width_xh'] == 1
    assert not e['checks']['wide_at_local_scale']
    s = build_structure(lines,[],page.size,boundaries=[boundary],fold=False,page=page)
    assert not s['boundaries']
    assert geometry(join_pieces([lines[-1]],structure=s)) == geometry(heading)


def test_repeated_large_word_spaces_are_not_gutters():
    page,lines,boundary = columns(gap=20,letter_gap=18)
    e = BoundaryEvidence(page,lines).gutter(boundary)
    assert e['required_width_px'] > 20
    assert not e['accepted']


def test_table_fragmentation_does_not_hide_ordinary_word_spacing():
    page = Image.new('L',(440,260),255)
    draw = ImageDraw.Draw(page)
    lines = []
    for y in range(40,220,30):
        for a,b in ((20,65),(90,135),(160,205),(235,280),(305,350),(375,420)):
            lines.append(line(a,b,y))
            for x in range(a,b-5,9):draw.rectangle((x,y-10,x+5,y-1),fill=0)
    e = BoundaryEvidence(page,lines).gutter(_boundary('gutter',220,0,220,260,width=30))
    assert min(e['interpiece_spacing_samples']) > 0
    assert e['required_width_px'] > 30
    assert not e['accepted']


def test_columns_with_staggered_baselines_still_form_separate_blocks():
    page,lines,boundary = columns()
    draw = ImageDraw.Draw(page)
    draw.rectangle((200,0,399,259),fill=255)
    for l in lines[1::2]:
        for k,v in geometry(l).items():
            if isinstance(v,list): l[k] = [y+15 for y in v]
        y = l['baseline'][0]
        for x in range(200,335,9):draw.rectangle((x,y-10,x+5,y-1),fill=0)
    assert BoundaryEvidence(page,lines).gutter(boundary)['accepted']


def test_gutter_rectangle_must_have_original_white_space():
    page,lines,boundary = columns()
    draw = ImageDraw.Draw(page)
    # These were falsely split detector pieces. Original print fills the lane.
    for l in lines[::2]:
        l['x1'] = 340
        for k,v in geometry(l).items():
            if isinstance(v,list):l[k] += [v[-1]]*(320-len(v))
        y = l['baseline'][0]
        draw.rectangle((160,y-10,200,y-1),fill=0)
    assert not BoundaryEvidence(page,lines).gutter(boundary)['checks']['original_whitespace']


@pytest.mark.parametrize('slope',[-.1,0,.1])
@pytest.mark.parametrize('dashed',[False,True])
def test_original_ink_accepts_thin_slanted_solid_and_dashed_rules(slope,dashed):
    page = Image.new('L',(200,300),255)
    draw = ImageDraw.Draw(page)
    for y in range(20,281):
        if not dashed or (y-20)%30 < 20:
            x = round(100+slope*(y-150))
            draw.line((x,y,x+1,y),fill=0)
    lines = [line(20,70,y) for y in range(40,260,30)]
    boundary = _boundary('rule',100+slope*(20-150),20,100+slope*(280-150),280)
    e = BoundaryEvidence(page,lines).rule(boundary)
    assert e['accepted'],e
    assert e['style'] == ('dashed' if dashed else 'continuous')


def test_printed_rule_junctions_are_ink_not_missing_stroke():
    page = Image.new('L',(200,300),255)
    draw = ImageDraw.Draw(page)
    draw.line((100,20,100,280),fill=0,width=2)
    for y in range(30,281,25):draw.rectangle((80,y,120,y+5),fill=0)
    e = BoundaryEvidence(page,[line(20,70,100)]).rule(_boundary('rule',100,20,100,280))
    assert e['accepted']
    assert e['support_fraction'] == 1
    assert .5 < e['thin_support_fraction'] < .85


def test_high_average_support_does_not_bridge_a_long_unprinted_rule_gap():
    page = Image.new('L',(200,500),255)
    draw = ImageDraw.Draw(page)
    draw.line((100,10,100,490),fill=0,width=2)
    draw.rectangle((98,220,102,260),fill=255)
    e = BoundaryEvidence(page,[line(20,70,100)]).rule(_boundary('rule',100,10,100,490))
    assert e['support_fraction'] > .85
    assert not e['checks']['no_long_unprinted_gap']
    assert not e['accepted']


@pytest.mark.parametrize('artifact',['gray','stamp','letters','curl'])
def test_dark_pixels_near_a_path_are_not_sufficient_rule_evidence(artifact):
    page = Image.new('L',(200,300),255)
    draw = ImageDraw.Draw(page)
    if artifact == 'gray': draw.rectangle((98,10,170,290),fill=140)
    if artifact == 'stamp': draw.ellipse((65,20,135,280),outline=0,width=3)
    if artifact == 'letters':
        for y in range(20,281,25):draw.rectangle((100,y,101,y+10),fill=0)
    if artifact == 'curl':
        points = [(int(100+12*np.sin(y/75)),y) for y in range(20,281)]
        draw.line(points,fill=0,width=2)
    boundary = _boundary('rule',101,10,101,290)
    assert not BoundaryEvidence(page,[line(20,70,100)]).rule(boundary)['accepted']


def test_rule_crossing_requires_own_ink_and_cannot_be_joined():
    page = Image.new('L',(200,200),255)
    draw = ImageDraw.Draw(page)
    draw.line((100,10,100,190),fill=0,width=2)
    draw.rectangle((80,90,93,99),fill=0)
    draw.rectangle((108,90,120,99),fill=0)
    lines = [line(70,130,100)]
    boundary = _boundary('rule',100,10,100,190)
    s = build_structure(lines,[cell(lines[0],0,'t')],page.size,boundaries=[boundary],fold=False,page=page)
    assert s['crossing_evidence'][0]['classification'] == 'real crossing'
    with pytest.raises(ValueError,match='crosses'):join_pieces(lines,structure=s)
    # The unchanged ribbon still intersects, but ink only on one side is not
    # evidence that this piece fuses text across the rule.
    draw.rectangle((108,90,120,99),fill=255)
    s = build_structure(lines,[],page.size,boundaries=[boundary],fold=False,page=page)
    assert s['crossing_evidence'][0]['classification'] == 'unresolved envelope overlap'
    assert len(s['boundaries']) == 1


def test_rejected_proposal_does_not_survive_as_legacy_column_address():
    page,lines,boundary = columns(rows=2)
    for i,l in enumerate(lines):l['column'] = i%2
    s = build_structure(lines,[],page.size,boundaries=[boundary],fold=False,page=page)
    assert not s['boundaries']
    assert len(s['columns']) == 1
    assert [l['column'] for l in lines] == [0,1,0,1]


def test_supplied_fold_is_preserved_and_defines_physical_leaves():
    page,lines,_ = columns()
    boundary = _boundary('fold',180,0,180,260,source='scan-metadata')
    s = build_structure(lines,[],page.size,boundaries=[boundary],page=page)
    assert len(s['boundaries']) == 1
    assert {l['page_side'] for l in lines} == {'left','right'}
    assert s['fold']['evidence']['method'] == 'spread-fold'


@pytest.mark.parametrize('second_width',[2,8])
def test_second_border_stroke_is_not_own_text_crossing(second_width):
    page = Image.new('L',(200,220),255)
    draw = ImageDraw.Draw(page)
    draw.line((100,10,100,210),fill=0,width=2)
    draw.line((114,10,114,210),fill=0,width=second_width)
    draw.rectangle((80,90,93,99),fill=0)
    lines = [line(70,130,100)]
    s = build_structure(lines,[],page.size,
        boundaries=[_boundary('rule',100,10,100,210)],fold=False,page=page)
    c = s['crossing_evidence'][0]
    assert c['own_ink_pixels_sides'][0] > 0
    assert c['own_ink_pixels_sides'][1] == 0
    assert c['classification'] == 'unresolved envelope overlap'
    assert c['excluded_rule_components']


def test_page_dimensions_must_match_frozen_geometry_frame():
    with pytest.raises(ValueError,match='match image_size'):
        build_structure([],[],(50,50),page=Image.new('L',(100,100),255))


def test_rule_subtraction_must_not_turn_slanted_edges_into_text_fragments():
    page = Image.new('L',(200,300),255)
    draw = ImageDraw.Draw(page)
    draw.line((100,10,110,290),fill=0,width=5)
    lines = [line(80,130,150)]
    # A tall curved detector envelope can include a long stroke. Its original
    # component must be identified before fitting/subtraction breaks it up.
    lines[0]['meanline'] = [20.]*50
    lines[0]['baseline'] = [270.]*50
    lines[0]['top'] = [10.]*50
    lines[0]['bottom'] = [280.]*50
    evidence = BoundaryEvidence(page,lines)
    b = _boundary('rule',100,10,110,290,id='b')
    c = evidence.crossing(0,b)
    assert c['own_ink_pixels_sides'] == [0,0]
    assert any(v['reason']=='original elongated rule component' for v in c['excluded_rule_components'])


def test_paper_texture_is_not_own_text_on_the_other_side_of_a_rule():
    page = Image.new('L',(200,220),240)
    draw = ImageDraw.Draw(page)
    draw.line((100,10,100,210),fill=0,width=2)
    draw.rectangle((80,90,93,99),fill=30)
    draw.rectangle((108,90,120,99),fill=195)
    lines = [line(70,130,100)]
    s = build_structure(lines,[],page.size,boundaries=[_boundary('rule',100,10,100,210)],fold=False,page=page)
    assert s['crossing_evidence'][0]['classification'] == 'unresolved envelope overlap'
    assert s['crossing_evidence'][0]['own_ink_pixels_sides'][1] == 0


def test_overlapping_observations_of_one_white_lane_do_not_invent_columns():
    page,lines,b = columns(gap=70)
    other = dict(b,path=[[b['path'][0][0]+10,60],[b['path'][-1][0]+10,240]],width=40)
    s = build_structure(lines,[],page.size,boundaries=[b,other],fold=False,page=page)
    assert len(s['boundaries']) == 2
    assert len(s['boundary_tracks']) == 1
    assert len(s['columns']) == 2
