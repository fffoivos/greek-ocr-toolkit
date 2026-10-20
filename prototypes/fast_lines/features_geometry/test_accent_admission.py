"""Historical nearest-box veto and original-page coarse-clip witness.

FONT i1's experiment had wrong attribution as well as failed reconciliation;
default admission remains the independently accepted base.
"""
from pathlib import Path
import cv2
import numpy as np
from ..shared import geometry_rows as rows


def actual(index=13):
    z=np.load(Path(__file__).with_name('accent_native.npz'))
    gray=z[f'gray{index}'];item=dict(polygon=z[f'polygon{index}'].tolist())
    ctx={};record=rows.native(gray,item,float(z[f'height{index}']),prepared=ctx)
    pieces,_=rows.confirmed_partition(item,record,prepared=ctx)
    return gray,item,ctx,record,pieces


def test_legacy_nearest_descender_causes_original_mark_only_veto():
    _,_,ctx,record,pieces=actual()
    v=next(v for v in record['valleys'] if v['tracks']==[0,3])
    assert len(pieces)==2 and ctx['partition_tracks']==[[1,2],[0,3]]
    assert v['mark_crossing']==[28] and not v['accepted']
    assert not (v['crossing'] or v['row_crossing'] or v['outside_corridor'])
    assert record['bridges'][28]['component']==147 and record['bridges'][28]['body']==56
    assert ctx['attachments'][147]==[56] and ctx['body_tracks'][56]==[0]
    assert ctx['stats'][147].tolist()==[720,167,8,15,74]


def test_clearing_veto_without_a_new_export_clips_lower_rows_accent():
    gray,item,ctx,record,_=actual()
    v=next(v for v in record['valleys'] if v['tracks']==[0,3]);v['accepted']=True
    pieces,_=rows.confirmed_partition(item,record,prepared=ctx)
    assert len(pieces)==3 and ctx['partition_tracks']==[[1,2],[0],[3]]
    source=(cv2.GaussianBlur(gray,(3,3),.6)<ctx['threshold']).astype(np.uint8)
    _,labels,stats,_=cv2.connectedComponentsWithStats(source,8)
    yy,xx=np.nonzero(ctx['labels']==147)
    points=np.rint(rows.to_page(np.c_[xx,yy],ctx['transform'])).astype(int)
    marks=set(labels[points[:,1],points[:,0]])-{0};assert marks
    masks=[rows._filled(gray.shape,p) for p in pieces]
    bx,by=np.rint(record['bodies'][77]['centre']).astype(int);assert masks[2][by,bx]
    for k in marks:
        hits=[int(m[labels==k].sum()) for m in masks]
        assert hits!=[0,0,int(stats[k,4])] and hits[1]>0  # lower row owns it; coarse export clips


def test_ambiguous_mark_and_real_body_crossings_remain_protective():
    _,_,ctx,record,_=actual()
    v=next(v for v in record['valleys'] if v['tracks']==[1,2])
    assert not v['accepted'] and 81 in [record['bridges'][k]['component'] for k in v['mark_crossing']]
    candidates=ctx['attachments'][81]
    assert {t for b in candidates for t in ctx['body_tracks'][b]}=={1,2}
    _,_,_,record,pieces=actual(14)
    v=next(v for v in record['valleys'] if v['tracks']==[2,3])
    assert not v['accepted'] and v['crossing']==[96,122] and len(pieces)==2
