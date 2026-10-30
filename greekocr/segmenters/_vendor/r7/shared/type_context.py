"""Composition adapters: separate type-grid geometry from actual ink ownership."""
import cv2
import numpy as np
from .contracts import bbox,rect


def grid_view(items):
    """Stable quadrilateral view for multi-vertex ribbons; unchanged quads exact.

    No curve is replaced in output. Min-area boxes are only grid nominations;
    original pixel contacts and current curved polygons confirm ownership.
    """
    return [q if len(q['polygon'])==4 else dict(q,polygon=cv2.boxPoints(
        cv2.minAreaRect(np.asarray(q['polygon'],np.float32))).tolist()) for q in items]


def excluded(regions):
    return [r if isinstance(r,dict) else dict(polygon=rect(r) if np.asarray(r).shape==(4,) else r) for r in regions]


def overlaps_exclusion(polygon,regions):
    """Conservative polygon intersection; never reintroduce a rejected footprint.

    Bounding boxes only prune pairs. A small local raster tests arbitrary concave
    ribbons rather than treating their convex hull as occupied ink.
    """
    q=dict(polygon=polygon);a=bbox(q)
    for r in regions:
        b=bbox(r);x0=max(a[0],b[0]);y0=max(a[1],b[1]);x1=min(a[2],b[2]);y1=min(a[3],b[3])
        if x1<=x0 or y1<=y0:continue
        origin=np.floor([x0,y0]);wh=np.ceil([x1,y1]).astype(int)-origin.astype(int)+1
        masks=[]
        for z in [q,r]:
            m=np.zeros((wh[1],wh[0]),np.uint8);cv2.fillPoly(m,[np.rint(np.asarray(z['polygon'])-origin).astype(np.int32)],1);masks.append(m)
        if np.any(masks[0]&masks[1]):return True
    return False


def recover(gray,items,detector,*,excluded_regions=(),grid_items=None,lattice_evidence=None,version=4):
    """Stack entry: no Q8 calls; caller runs final separator on additions if needed."""
    from .type_recovery import run
    return run(gray,items,detector,version=version,skip_initial_separator=True,final_separators=False,
               grid_items=grid_view(items) if grid_items is None else grid_items,
               lattice_evidence=lattice_evidence,excluded_regions=excluded_regions)
