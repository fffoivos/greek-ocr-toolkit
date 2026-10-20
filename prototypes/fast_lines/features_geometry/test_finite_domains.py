"""Finite printed boundaries through the real field producer and consumers."""
import pytest
import cv2
import numpy as np
from shapely.geometry import Polygon, box
from ..shared.geometry_page_field import blocks, render
from ..shared.geometry_field_detector import unbend, native_bands
from ..shared.geometry_field_selection import apply
from .test_page_field import item


def ruled_page():
    gray=np.full((940,1100),245,np.uint8);qs=[]
    # A spanning heading/footer population, with body columns between them.
    for y in range(60,910,50):
        spans=[(40,500),(600,1060)] if 260<y<660 else [(40,1060)]
        for a,c in spans:
            for x in range(a+8,c-15,25):cv2.rectangle(gray,(x,y),(x+10,y+19),30,-1)
            qs.append(item(a,y-3,c,y+24,len(qs)))
    rule=dict(path=[[548,260],[552,460],[558,660]],y0=260,y1=660)
    return gray,qs,dict(rules=[dict(accepted=True,rule=rule)])


def shape(field):
    return Polygon(field['domain']) if 'domain' in field else box(*field['region'])


@pytest.mark.xfail(strict=True,reason='R8-GEOM-02 i1: finite boundary consumer defect remains; repaired trial regresses native text elsewhere')
def test_real_render_and_unbend_preserve_spanning_text_outside_finite_rule():
    gray,qs,columns=ruled_page();e=render(gray,qs,column_evidence=columns)
    for y in (160,810):
        support=box(48,y,1034,y+20)
        fields=[f for f in e['fields'] if shape(f).covers(support)]
        assert len(fields)==1, 'spanning native text has no single field domain'
        # Outside-rule reconnection may be supported or unknown. The physical
        # obligation is whole spanning support, not a particular mesh layout.
    # Neither body domain can claim the other side's native glyphs.
    left=[f for f in e['fields'] if shape(f).covers(box(48,410,484,430))]
    right=[f for f in e['fields'] if shape(f).covers(box(608,410,1034,430))]
    assert len(left)==len(right)==1 and left[0] is not right[0]
    assert shape(left[0]).intersection(shape(right[0])).area==0
    for field,x in [(left[0],48),(right[0],608)]:
        crop,(a,b)=unbend(gray,field)
        assert np.any(crop[int(410-b):int(430-b),int(x-a):int(x+12-a)]<100)


@pytest.mark.xfail(strict=True,reason='R8-GEOM-02 i1: finite boundary consumer defect remains; repaired trial regresses native text elsewhere')
def test_multiple_rules_and_explicit_regions_keep_native_finite_paths():
    gray,qs,columns=ruled_page()
    columns['rules'].append(dict(accepted=True,rule=dict(path=[[820,460],[800,760]],y0=460,y1=760)))
    e=render(gray,qs,regions=[[0,0,1100,940]],column_evidence=columns)
    for y,intervals in [(160,[(48,1034)]),(410,[(48,484),(608,1034)]),(610,[(48,484),(608,790),(830,1034)]),(810,[(48,1034)])]:
        for a,c in intervals:
            assert sum(shape(f).covers(box(a,y,c,y+20)) for f in e['fields'])==1
    polygons=[shape(f) for f in e['fields']]
    assert all(p.intersection(q).area==0 for i,p in enumerate(polygons) for q in polygons[:i])
    # Exact path x=552 at y=460, not the path's median at every y.
    left=next(f for f in e['fields'] if shape(f).covers(box(48,410,484,430)))
    assert shape(left).covers(box(548,410,550,430))
    assert not shape(left).covers(box(554,410,556,430))


def test_rejected_and_missing_rules_leave_the_original_domain_contract():
    gray,qs,columns=ruled_page();columns['rules'][0]['accepted']=False
    assert blocks(qs,gray.shape[::-1],20,columns)==blocks(qs,gray.shape[::-1],20)


def test_native_endpoint_marks_reach_nonempty_selection_and_retention():
    gray=np.full((350,820),245,np.uint8)
    rows=[]
    for y in (75,110,170,230,290):
        for a,c in ((25,385),(435,795)):
            for x in range(a+8,c-15,25):
                cv2.rectangle(gray,(x,y),(x+10,y+19),30,-1)
            rows.append(item(a,y-16,c,y+25,len(rows)))
    for x in (358,768):cv2.rectangle(gray,(x,93),(x+4,100),30,-1)
    # These two accents belong to the first body row, above the printed rule's
    # endpoint. That endpoint is not an admissible horizontal clipping line.
    for x in (58,468):cv2.rectangle(gray,(x,102),(x+4,106),30,-1)
    cv2.line(gray,(410,108),(410,280),30,2)
    columns=dict(rules=[dict(accepted=True,rule=dict(
        path=[[410,108],[410,280]],y0=108,y1=280))])
    evidence=render(gray,rows,column_evidence=columns)
    # Native bands owns the attachment; separation sees the same pixel census.
    localized=[]
    for i,q in enumerate(rows):
        p=np.asarray(q['polygon']).copy()
        if i in (2,3):p[:,1]=np.maximum(p[:,1],108)
        localized.append(dict(q,polygon=p.tolist()))
    completed,audit=native_bands(gray,localized,evidence['height'])
    for i,x in ((2,58),(3,468)):
        poly=Polygon(completed[i]['polygon'])
        assert poly.covers(box(x,102,x+4,106))
        assert not audit[i]['foreign_components']
        assert audit[i]['gaps'], 'neighbour separation did not execute'
    accepted=apply(gray,rows,dict(items=completed,evidence=evidence),column_evidence=columns)
    assert accepted['decisions'] and accepted['replacements']
    assert all(q['accepted'] for q in accepted['decisions'])
    clipped=[dict(q) for q in completed]
    for i in (2,3):
        p=np.asarray(clipped[i]['polygon']).copy();p[:,1]=np.maximum(p[:,1],108)
        clipped[i]['polygon']=p.tolist()
    rejected=apply(gray,rows,dict(items=clipped,evidence=evidence),column_evidence=columns)
    lost=[r for r in rejected['decisions'] if r['reason']=='native ink would be lost']
    assert len(lost)==2 and all(r['lost_components'] for r in lost)
    for i in (2,3):assert rows[i] in rejected['items']
