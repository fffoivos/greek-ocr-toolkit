"""Experimental normal-run growth evidence for the next geometry task.

NOT wired into default Stack: the tested adapter lost retained text and added
cost. An affirmative photometric witness does not establish front ownership.

All positions are native page pixels. Arrays are float64 polygons [V,2]; unit
bounds are half open. NormalInk is the existing typed photometric reference.
Unknown calibration forbids growth; it never authorizes deletion of found text.
"""
from typing import NamedTuple
import numpy as np

class NormalInk(NamedTuple):
    core: float
    spread: float
    boundary: float
    support: int

    def values(self):
        return np.array([self.core,self.spread,self.boundary]) if self.support>=12 else np.array([1.,0.,2.])


class PageInk(NamedTuple):
    normal: NormalInk
    height: float
    body_height: float
    stroke: float
    image_size: tuple

class LetterGrowth(NamedTuple):
    admitted: np.ndarray       # bool[N], found units are always retained
    runs: np.ndarray           # int[N], -1 not an admitted normal run
    gap_limit: float           # page pixels


def follow_letters(bounds,material_y,normal,found,body_height,row,*,gap_limit):
    """Continuity in unbent coordinates, letter by letter, never a box vote.

    bounds[N,4] are ordered internally by x; material_y[N] are observed body
    centres after unbending. normal[N] means each component passed the SAME
    NormalInk reference; found[N] means ink already lies inside a kept crop.
    A normal run needs three bodies and can include retained terminal bodies.
    A faint new body ends a run even when strong letters occur farther out.
    A gap ends a run; a later independent three-body run can be a new segment.
    No operation uses these decisions to delete or narrow a retained crop.
    """
    bounds=np.asarray(bounds,float).reshape(-1,4);found=np.asarray(found,bool);normal=np.asarray(normal,bool)
    admitted=found.copy();runs=np.full(len(bounds),-1,int)
    if not len(bounds):return LetterGrowth(admitted,runs,float(gap_limit))
    valid=(abs(np.asarray(material_y)-row)<=body_height/2)&(bounds[:,3]-bounds[:,1]>=2*body_height/3)
    order=np.argsort(bounds[:,0],kind='stable');groups=[];group=[]
    for i in order:
        if not valid[i]:continue
        if not normal[i]:
            if group:groups.append(group);group=[]
            continue
        if group and bounds[i,0]-bounds[group[-1],2]>gap_limit:
            groups.append(group);group=[]
        group.append(int(i))
    if group:groups.append(group)
    for j,g in enumerate(groups):
        if len(g)>=3:admitted[g]=True;runs[g]=j
    return LetterGrowth(admitted,runs,float(gap_limit))



def calibrate(gray,items,*,height=None):
    """Compute the existing reference before geometry, once per page generation.

    Returns (PageInk, evidence). Height/stroke/coordinates are native pixels;
    core/spread/boundary are dimensionless contrast; support counts sampled
    bodies. Bind the context to the same image pixels and never recalibrate it
    from later geometry. This opt-in computation costs ~25ms median in the
    rejected all-page integration, so callers must measure and scout its need.
    """
    from .ink_faintness import analyze
    evidence=analyze(gray,items,height=height,require_reference=True)
    r=evidence['reference'];normal=NormalInk(**{k:r[k] for k in ('core','spread','boundary','support')})
    return PageInk(normal,evidence['height'],r.get('body_height',0),r.get('stroke',0),tuple(gray.shape[::-1])),evidence
