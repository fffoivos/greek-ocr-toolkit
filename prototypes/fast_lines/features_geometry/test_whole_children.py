"""Real native accepted-partition extent, on provenance-bound original pixels.

The fixture keeps native-3/5/7 support in small untranslated image crops;
polygons are translated by each crop origin. No detector or text truth seeds it.
Actual compose/208 receipts are separate because page-field ownership matters.
"""
from pathlib import Path
import cv2
import numpy as np
import pytest
from ..shared import geometry_rows as rows


def fixture(index):
    z=np.load(Path(__file__).with_name('whole_children_native.npz'))
    return z[f'gray{index}'],dict(polygon=z[f'polygon{index}'].tolist()),float(z[f'height{index}'])


def actual(index=3):
    gray,item,h=fixture(index);ctx={}
    record=rows.native(gray,item,h,route='slow',prepared=ctx)
    pieces,reason=rows.confirmed_partition(item,record,prepared=ctx)
    assert len(pieces)==2,reason
    return gray,item,record,pieces,ctx


def returned_page_audit(gray,polygons,threshold):
    """Independent audit of the returned rint/inclusive-fillPoly pixels."""
    ink=(cv2.GaussianBlur(gray,(3,3),.6)<threshold).astype(np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(ink,8)
    masks=[];partial=[]
    for polygon in polygons:
        mask=np.zeros(gray.shape,np.uint8)
        cv2.fillPoly(mask,[np.rint(polygon).astype(np.int32)],1)
        masks.append(mask)
        counts=np.bincount(labels[mask>0],minlength=n)
        partial.append(np.flatnonzero((counts[1:]>0)&(counts[1:]<stats[1:,4])).tolist())
    overlap=int((np.sum(masks,axis=0)>1).sum())
    return partial,overlap


def assert_whole_return(gray,polygons,ctx):
    partial,overlap=returned_page_audit(gray,polygons,ctx['threshold'])
    assert not any(partial),f'returned polygons clip page components: {partial}'
    assert overlap==0,f'returned polygons overlap at {overlap} original page pixels'


def test_vector_slice_mutation_cuts_native_components():
    gray,item,record,pieces,ctx=actual();polygons,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert len(polygons)==2 and r['page_membership']['members']
    assert not any(r['page_membership'][k] for k in ['losses','foreign','duplicates'])
    assert_whole_return(gray,polygons,ctx)
    partial_page,overlap=returned_page_audit(gray,pieces,ctx['threshold'])
    assert sum(map(len,partial_page))==56 and overlap==1269
    partial=set()
    for p in pieces:
        counts=np.bincount(ctx['labels'][rows._filled(ctx['labels'].shape,rows.from_page(p,ctx['transform']))>0],minlength=len(ctx['stats']))
        partial.update(k for k in range(1,len(counts)) if 0<counts[k]<ctx['stats'][k,4])
    assert len(partial)==56


def test_zero_parent_fragment_and_one_parent_pixel_are_distinct():
    gray,item,record,pieces,ctx=actual();polygons,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert polygons and 1 in r['outside_boundary_components']
    assert not any(1 in group for group in r['admitted_components'])
    y,x=np.argwhere(ctx['labels']==1)[0];ctx['mask'][y,x]=1
    p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert not p and 1 in r['retained_boundary_components']


@pytest.mark.parametrize('index,first_failure',[(5,'outside body'),(7,'admitted parent member')])
def test_selected_track_strip_truncation_keeps_legacy_partition(index,first_failure):
    gray,item,record,pieces,ctx=actual(index);p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert not p and first_failure in r['first_failure'] and len(pieces)==2


def test_forbidden_support_and_ambiguous_native_relation_abstain():
    gray,item,record,pieces,ctx=actual();p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert p
    completed,why=rows.whole_children(gray,item,record,pieces,ctx,forbidden_regions=[dict(polygon=p[1])])
    assert not completed and 'forbidden' in why['first_failure']
    label=ctx['body_labels'][record['tracks'][r['whole_word_tracks_per_child'][0][0]]['word_runs'][0][0]]
    ctx['body_tracks'][ctx['body_labels'].index(label)]=[0,1]
    completed,why=rows.whole_children(gray,item,record,pieces,ctx)
    assert not completed and 'identity' in why['first_failure']


@pytest.mark.parametrize('phase',range(13))
def test_real_remap_phases_reach_original_page_raster(monkeypatch,phase):
    original=rows.strip
    def shifted(gray,item,h,scale=1.):
        g,_,tr=original(gray,item,h,scale);x0=tr['x0']+phase;x1=tr['x0']+round(g.shape[1]/scale)
        pp=np.asarray(item['polygon'],float).copy();pp[:,1]-=tr['slope']*(pp[:,0]-x0)
        y0=int(np.floor(pp[:,1].min()-h));y1=int(np.ceil(pp[:,1].max()+h))
        w=round((x1-x0)*scale);hh=round((y1-y0)*scale)
        xs=x0+np.arange(w)/scale;ys=y0+np.arange(hh)/scale
        mx=np.broadcast_to(xs[None,:],(hh,w)).astype(np.float32)
        my=(ys[:,None]+tr['slope']*(xs[None,:]-x0)).astype(np.float32)
        return cv2.remap(gray,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255),rows._filled((hh,w),(pp-[x0,y0])*scale),dict(tr,x0=x0,y0=y0)
    monkeypatch.setattr(rows,'strip',shifted)
    gray,item,record,pieces,ctx=actual();p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert len(p)==2 and r['page_membership']['members']
    assert all(not r['page_membership'][k] for k in ['losses','foreign','duplicates'])
    assert_whole_return(gray,p,ctx)


def apostrophe_witness():
    gray,item,record,pieces,ctx=actual()
    polygons,receipt=rows.whole_children(gray,item,record,pieces,ctx)
    label=32;x,y,w,h,area=ctx['stats'][label]
    assert area==59 and not ctx['mask'][ctx['labels']==label].any()
    assert x>0 and y>0 and x+w<ctx['labels'].shape[1] and y+h<ctx['labels'].shape[0]
    assert not rows.mark_bodies(*ctx['centres'][label],ctx['body_boxes'],ctx['height'])
    assert label not in ctx['attachments']
    points=np.rint(rows.to_page(np.c_[np.nonzero(ctx['labels']==label)[1],
                                      np.nonzero(ctx['labels']==label)[0]],ctx['transform'])).astype(int)
    return gray,polygons,points,int(area)


@pytest.mark.xfail(strict=True,reason="CURL-03 prerequisite: rejected B upper child omits its own κατ’ apostrophe")
def test_proposed_upper_child_conserves_observed_apostrophe():
    gray,polygons,points,area=apostrophe_witness()
    mask=rows._filled(gray.shape,polygons[0])
    assert int(mask[points[:,1],points[:,0]].sum())==area


def test_real_final_reconcile_preserves_apostrophe_and_lower_child():
    import json
    from ..shared.stack_ownership import reconcile
    gray,polygons,points,area=apostrophe_witness()
    # Original field owner from the accepted real compose export, translated
    # with the same provenance-bound crop. No synthetic owner rectangle.
    pinned=json.loads(Path(__file__).with_name('whole_children_native.json').read_text())
    field=pinned['final_upper_field_owner'];offset=pinned['native_calls'][0]['crop_origin']
    field=dict(field,polygon=(np.asarray(field['polygon'])-offset).tolist())
    children=[dict(polygon=p,row_partition=True,source_ids=[2]) for p in polygons]
    final=reconcile(gray,children+[field])
    assert any(c['child']==0 and c['retired'] for c in final['changes'])
    assert any(q['polygon']==polygons[1] for q in final['items'])
    masks=[rows._filled(gray.shape,q['polygon']) for q in final['items']]
    assert int(np.maximum.reduce(masks)[points[:,1],points[:,0]].sum())==area


def test_exact_partition_census_is_passed_once_and_geometry_bound(monkeypatch):
    gray,item,h=fixture(3);ctx={};record=rows.native(gray,item,h,prepared=ctx)
    legacy,reason=rows.confirmed_partition(item,record)
    calls=[];original=cv2.pointPolygonTest
    def counted(*args):
        calls.append(1);return original(*args)
    monkeypatch.setattr(cv2,'pointPolygonTest',counted)
    pieces,new_reason=rows.confirmed_partition(item,record,prepared=ctx)
    assert pieces==legacy and reason==new_reason and calls
    calls.clear();p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert p and r['page_membership']['members'] and not calls
    # An exact old-piece census must not survive changed piece coordinates.
    stale=dict(ctx,partition_polygons=[np.asarray(q).copy() for q in pieces])
    stale['partition_polygons'][0][0,0]+=1
    p2,r2=rows.whole_children(gray,item,record,pieces,stale)
    assert calls and p2==p and r2['whole_word_tracks_per_child']==r['whole_word_tracks_per_child']


@pytest.mark.parametrize('index',[3,5,7])
def test_native_body_presence_is_exact_parent_support(index):
    _,_,record,_,ctx=actual(index)
    counts=np.bincount(ctx['labels'][ctx['mask']>0],minlength=len(ctx['stats']))
    assert all((record['bodies'][bi]['inside_height_h']>0)==(counts[label]>0)
               for bi,label in enumerate(ctx['body_labels']))


def test_unassigned_observed_body_needs_no_repeat_parent_scan(monkeypatch):
    gray,item,record,pieces,ctx=actual()
    bi=record['tracks'][0]['word_runs'][0][0];assert record['bodies'][bi]['inside_height_h']>0
    ctx['body_tracks'][bi]=[0,1]
    def repeated(*args,**kwargs):
        raise AssertionError('parent support was already observed by native')
    monkeypatch.setattr(rows.np,'bincount',repeated)
    p,r=rows.whole_children(gray,item,record,pieces,ctx)
    assert not p and 'identity' in r['first_failure']
