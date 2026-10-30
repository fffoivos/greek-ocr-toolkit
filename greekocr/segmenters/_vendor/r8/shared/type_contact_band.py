"""Smooth candidate-local bands from native contacts, with competing-row veto.

These paths model lower body contacts. They are not semantic baselines. Regional
Paddle supplies localization; the physical contacts separate neighbouring rows.
"""
import cv2
import numpy as np
from .geometry import robust_fit
from .type_lattice import point_ownership
from .contracts import bbox


def narrow(item, row, body_field, items):
    p=np.asarray(item['polygon'],float);bodies=body_field['bodies'];h=row['height']
    centres=np.array([b['centre'] for b in bodies])
    inside=np.array(point_ownership(centres,[item]))
    ids=[i for i in row['free'] if inside[i]]
    if len(ids)<5:return None,dict(reason='short contact chain')
    boxes=np.array([b['bbox'] for b in bodies]);xs=centres[ids,0];ys=boxes[ids,3]
    origin=float(xs.mean());coef=robust_fit((xs-origin)/h,ys,2 if np.ptp(xs)>12*h else 1)
    def curve(x):return np.polynomial.polynomial.polyval((np.asarray(x)-origin)/h,coef)
    if np.max(np.abs(ys-curve(xs)))>.5*h:
        return None,dict(reason='contact chain changes row',residual_h=(np.abs(ys-curve(xs))/h).tolist())
    # Extend only through measured bodies on this contact curve and inside the
    # regional localization. Another row's tall letters are competing evidence.
    sizes=boxes[:,3]-boxes[:,1]
    same=inside & (abs(boxes[:,3]-curve(centres[:,0]))<.45*h) & (sizes>.45*h)&(sizes<1.8*h)
    use=np.flatnonzero(same)
    if len(use)<5:return None,dict(reason='too few common contacts')
    left=max(float(p[:,0].min()),float(boxes[use,0].min())-.25*h)
    right=min(float(p[:,0].max()),float(boxes[use,2].max())+.25*h)
    xx=np.linspace(left,right,max(3,round((right-left)/(2*h))+1))
    roof=float(np.min(boxes[use,1]-curve(centres[use,0])))-.25*h
    floor=.25*h
    poly=np.vstack([np.c_[xx,curve(xx)+roof],np.c_[xx[::-1],curve(xx[::-1])+floor]])
    # A newly proposed line must have its own centre, even where existing broad
    # boxes own a few of its glyph pixels. Never accept over an existing axis.
    for old in items:
        bb=bbox(old);cx=(bb[0]+bb[2])/2;cy=(bb[1]+bb[3])/2
        if left<cx<right and curve(cx)+roof<cy<curve(cx)+floor:
            return None,dict(reason='existing line centre competes',source_bbox=bb)
    return dict(item,polygon=poly.tolist(),contact_band=True),dict(reason='native contact band',
        height=h,contacts=use.tolist(),path=np.c_[xx,curve(xx)].tolist(),roof=roof,floor=floor)
