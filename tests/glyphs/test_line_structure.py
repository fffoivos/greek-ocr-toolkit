"""Independent address, joining and immutable-geometry contracts."""
from copy import deepcopy

import numpy as np
import pytest
from PIL import Image

from greekocr.glyphs.line_structure import (
    build_structure, join_pieces, delivery_records, render_structure, ADDRESS,
)
from greekocr.glyphs.page_text_lines import CURVES, segment_page
from test_page_line_segments import page_fixture


def line(a,b,y,*,column=0,source=None):
    r=dict(x0=a,x1=b,xheight=10,column=column,discounted=None,
           neighbours={'above':[-1]*(b-a),'below':[-1]*(b-a)})
    for name,offset in zip(CURVES,[0,-15,-10,3,-12,-18,-20,5]):
        r[name]=[y+offset]*(b-a)
    if source is not None:r['row_source']=source
    return r


def cell(l,i,table=None):
    return dict(index=i,line_index=i,table_id=table,cell_id=f'piece-{i}',
                box_pixels=[l['x0'],min(l['top']),l['x1'],max(l['bottom'])])


def geometry(r):
    return {k:r[k] for k in ('x0','x1',*CURVES)}


def test_synthetic_two_columns_keep_whole_lines_and_column_order():
    page,_,_=page_fixture(columns=2)
    result=segment_page(page)
    lines=[l.to_record() for l in result.lines];old=deepcopy(lines)
    cells=[cell(l,i) for i,l in enumerate(lines)]
    s=build_structure(lines,cells,page.size,gutters=[(510,0,545,page.height)],fold=False)
    assert len(s['columns'])==2
    assert not s['violations']
    assert all(all(k in r for k in ADDRESS) for r in lines+cells)
    joined=delivery_records(lines,structure=s)
    assert len(joined)==len(old)==12
    assert sorted((geometry(r) for r in joined),key=lambda r:(r['x0'],r['baseline'][0]))==sorted(
        (geometry(r) for r in old),key=lambda r:(r['x0'],r['baseline'][0]))
    assert [r['column_id'] for r in joined]==[s['columns'][0]['id']]*6+[s['columns'][1]['id']]*6


def test_spread_physical_sides_and_no_cross_fold_even_with_same_source():
    lines=[line(a,a+100,y,source='same') for y in (50,90,130) for a in (50,650)]
    cells=[cell(l,i,'table') for i,l in enumerate(lines)]
    s=build_structure(lines,cells,(1000,700),gutters=[(470,0,530,700)])
    assert s['fold']['path']==[[500.,0.],[500.,700.]]
    assert {l['page_side'] for l in lines}=={'left','right'}
    assert lines[0]['row_id']!=lines[1]['row_id']
    with pytest.raises(ValueError,match='share page'):
        join_pieces(lines[:2],structure=s)


def test_table_row_pieces_share_row_and_reciprocal_neighbours():
    lines=[line(30,70,50,source='table:row0'),line(90,130,50,source='table:row0'),
           line(30,130,90,source='table:row1')]
    original=deepcopy(lines);cells=[cell(l,i,'table') for i,l in enumerate(lines)]
    s=build_structure(lines,cells,(200,150),fold=False)
    assert len(s['rows'])==2
    assert lines[0]['row_id']==lines[1]['row_id']!=lines[2]['row_id']
    assert [r['piece_index'] for r in lines]==[0,1,0]
    assert lines[0]['neighbours']['right']==1
    assert cells[1]['neighbours']['left']==0
    joined=join_pieces(lines[:2],structure=s)
    assert (joined['x0'],joined['x1'])==(30,130)
    assert len(joined['pieces'])==2
    for old,new in zip(original,lines):assert geometry(old)==geometry(new)
    assert len(delivery_records(lines,structure=s))==3
    assert len(delivery_records(lines,structure=s,granularity='rows'))==2
    assert len(delivery_records(lines,structure=s,granularity='pieces'))==3


def test_slanted_rule_geometry_and_join_guard():
    lines=[line(10,70,50,source='r'),line(130,190,50,source='r')]
    cells=[cell(l,i,'table') for i,l in enumerate(lines)]
    s=build_structure(lines,cells,(200,150),rules=[dict(kind='direct_rule',centre=100,
        slope=.1,radius=2,top=0,bottom=150)],fold=False)
    assert s['boundaries'][0]['path']==[[92.5,0.],[107.5,150.]]
    assert len({l['column_id'] for l in lines})==2
    assert len({l['row_id'] for l in lines})==2
    # Forged equal address still cannot bypass the geometric crossing guard.
    for k in ADDRESS:lines[1][k]=lines[0][k]
    lines[1]['piece_index']=1
    with pytest.raises(ValueError,match='crosses a boundary'):
        join_pieces(lines,structure=s)


def test_crossing_is_reported_without_changing_geometry():
    lines=[line(10,190,50)];old=geometry(deepcopy(lines[0]))
    s=build_structure(lines,[],(200,150),gutters=[(90,0,110,150)],fold=False)
    assert s['violations']==[dict(line_index=0,boundary_ids=['boundary-0000'],discounted=None)]
    assert geometry(lines[0])==old
    with pytest.raises(ValueError,match='crosses'):
        join_pieces(lines,structure=s)


def test_missing_row_or_duplicate_piece_cannot_be_joined():
    lines=[line(10,50,50)]
    s=build_structure(lines,[],(100,100),fold=False)
    with pytest.raises(ValueError,match='duplicate'):
        join_pieces(lines+lines,structure=s)
    lines[0]['row_id']='invented'
    with pytest.raises(ValueError,match='absent'):
        join_pieces(lines,structure=s)


def test_discounted_candidates_are_addressed_but_not_rendered_or_delivered():
    lines=[line(10,50,50)];lines[0]['discounted']='faint'
    s=build_structure(lines,[],(100,100),fold=False)
    assert all(k in lines[0] for k in ADDRESS)
    assert delivery_records(lines,structure=s)==[]
    page=Image.new('RGB',(100,100),'white')
    assert np.array_equal(np.asarray(render_structure(page,lines,s)),np.asarray(page))
    with pytest.raises(ValueError,match='discounted'):
        join_pieces(lines,structure=s)


def test_join_preserves_curved_samples_and_interpolates_only_gap():
    lines=[line(10,20,50,source='r'),line(25,35,52,source='r')]
    for l in lines:
        for k in CURVES:l[k]=[v+j*.1 for j,v in enumerate(l[k])]
    s=build_structure(lines,[cell(l,i,'t') for i,l in enumerate(lines)],(100,100),fold=False)
    joined=join_pieces(lines,structure=s)
    for k in CURVES:
        assert joined[k][:10]==lines[0][k]
        assert joined[k][-10:]==lines[1][k]


def test_finite_rule_does_not_cut_heading_above_it():
    lines=[line(10,190,30),line(10,70,100),line(130,190,100)]
    s=build_structure(lines,[],(200,200),rules=[dict(kind='direct_rule',centre=100,
        slope=.1,radius=2,top=70,bottom=180)],fold=False)
    assert not s['violations']
    assert join_pieces(lines[:1],structure=s)['x1']==190


def test_real_table_delivery_retains_provenance_and_addresses_every_record():
    from greekocr.glyphs.table_lines import prepare_delivery
    page,_,_=page_fixture(columns=2,rule=True,word_gap=True)
    original=segment_page(page)
    before=[geometry(l.to_record()) for l in original.lines]
    result,pieces,_=prepare_delivery(page,original,[('table',(20,20,1040,490))])
    lines=[l.to_record() for l in result.lines]
    cells=[p.to_record(i,page.size,page.size) for i,p in enumerate(pieces)]
    assert before==[geometry(l) for l in lines[:len(before)]]
    assert all(all(k in r for k in ADDRESS) for r in lines+cells)
    assert all(p.line.row_source is not None for p in pieces if p.table_id)
    # This repeated-glyph fixture has persistent gaps between individual glyphs;
    # the existing table detector regards those as gutters. Verify that the
    # pre-split provenance survives even where a hard stop vetoes reassembly.
    from collections import Counter
    assert max(Counter(p.line.row_source for p in pieces).values())>1
    for row in result.structure['rows']:
        if row['discounted']:continue
        records=[lines[i] for i in row['line_indices']]
        assert len({l['column_id'] for l in records})==1
        if len(records)>1:
            join_pieces(records,structure=result.structure)
    assert all(tuple(c[k] for k in ADDRESS)==tuple(lines[c['line_index']][k] for k in ADDRESS) for c in cells)


def test_review_renderer_writes_complete_addresses(tmp_path):
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    root=Path(__file__).resolve().parents[2]
    page,_,_=page_fixture()
    pages=tmp_path/'pages';pages.mkdir();page.save(pages/'synthetic.png')
    layout=tmp_path/'layout';layout.mkdir()
    (layout/'synthetic.json').write_text(json.dumps(dict(retained=[])))
    out=tmp_path/'out'
    subprocess.run([sys.executable,str(root/'scripts/glyphs/render_page_line_segments.py'),
        '--pages',str(pages),'--layout',str(layout),'--out',str(out)],check=True,cwd=root,
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True)
    lines=json.loads((out/'synthetic.lines.json').read_text())
    cells=json.loads((out/'synthetic.cells.json').read_text())['cells']
    structure=json.loads((out/'synthetic.structure.json').read_text())
    assert len(lines)==len(cells)==len(structure['rows'])==6
    assert all(all(k in r for k in ADDRESS) for r in lines+cells)
    with Image.open(out/'synthetic.structure.jpg') as im:
        assert im.size==page.size


def test_mismatched_piece_line_reference_is_rejected():
    with pytest.raises(ValueError,match='invalid line_index'):
        build_structure([line(10,50,30)],[dict(line_index=3)],(100,100))


def test_separate_table_seeds_regroup_on_one_baseline_without_joining_next_row():
    lines=[line(10,40,40,source='seed-a'),line(50,90,42,source='seed-b'),
           line(10,90,70,source='seed-c')]
    s=build_structure(lines,[cell(l,i,'t') for i,l in enumerate(lines)],(120,100),fold=False)
    assert lines[0]['row_id']==lines[1]['row_id']!=lines[2]['row_id']
    assert s['rows'][0]['row_sources']==['seed-a','seed-b']
    joined=join_pieces(lines[:2],structure=s)
    assert joined['x1']==90 and joined['support']==0
    assert len(joined['neighbours']['above'])==80


def test_table_row_grouping_is_scale_invariant():
    original=[line(10,40,40,source='a'),line(50,90,42,source='b'),line(10,90,70,source='c')]
    assignments=[]
    for scale in (1,3):
        lines=deepcopy(original)
        for l in lines:
            for k in ('x0','x1','xheight'):l[k]*=scale
            for k in CURVES:l[k]=np.repeat(np.asarray(l[k])*scale,scale).tolist()
            for k in ('above','below'):l['neighbours'][k]=[-1]*(l['x1']-l['x0'])
        build_structure(lines,[cell(l,i,'t') for i,l in enumerate(lines)],(120*scale,100*scale),fold=False)
        assignments.append([[l[k] for k in ADDRESS] for l in lines])
    assert assignments[0]==assignments[1]
