"""Original-pixel body contacts outside existing localizations.

The rendering is a physical row hypothesis, never foreground certification.
Small footnote bodies keep their own scale; no pitch is inferred from boxes.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .geometry import height_proxy, mask
from . import observations as obs
from .local_scale import component_extent


def render(gray, items, *, route='slow', version=1, excluded_regions=(), height=None):
    start = perf_counter()
    height = height_proxy(items, (gray.shape[1], gray.shape[0])) if height is None else float(height)
    step = 1. if route == 'slow' else max(1., height / (20 if version>=3 else 12))
    small = obs.resize(gray, (round(gray.shape[1]/step), round(gray.shape[0]/step)))
    sx, sy = gray.shape[1]/small.shape[1], gray.shape[0]/small.shape[0]
    h = height / step
    k = max(1, round(3*h)) | 1
    ink = obs.ink(small, k, method="closing", threshold=.18, arithmetic="relative")
    _, labels, stats, centres = obs.components(ink)
    stats, centres = stats[1:], centres[1:]
    good = ((stats[:,3] > .25*h) & (stats[:,3] < 2.5*h) &
            (stats[:,2] > .12*stats[:,3]) & (stats[:,2] < 3*stats[:,3]) &
            (stats[:,4] > .08*stats[:,3]**2))
    ids = np.flatnonzero(good)
    st, c = stats[ids], centres[ids]
    owned_mask = mask(items, small.shape, (gray.shape[1], gray.shape[0]))
    rejected_mask = mask(excluded_regions, small.shape, (gray.shape[1], gray.shape[0]))
    ci = np.rint(c).astype(int)
    owned = owned_mask[ci[:,1], ci[:,0]].astype(bool)
    touched = np.bincount(labels.ravel(),weights=owned_mask.ravel(),minlength=len(stats)+1)[ids+1]>0
    # Native physical overlap depth distinguishes a clipped stroke edge from
    # an owned glyph interior. Retain both measurements for review.
    depth = np.zeros(len(stats)+1, np.float32)
    radius = np.zeros(len(stats)+1, np.float32)
    if version >= 4:
        pixels = labels > 0
        np.maximum.at(depth, labels[pixels], cv2.distanceTransform(owned_mask,cv2.DIST_L2,5)[pixels])
        np.maximum.at(radius, labels[pixels], cv2.distanceTransform(ink,cv2.DIST_L2,5)[pixels])
    rejected = rejected_mask[ci[:,1], ci[:,0]].astype(bool)
    bottom = st[:,1]+st[:,3]
    contacts = np.c_[c[:,0], bottom]
    parent = np.arange(len(ids))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    tree = cKDTree(contacts)
    edges = []
    next_node = {}; prev_node = {}
    neighborhoods=tree.query_ball_point(contacts,5*st[:,3],return_sorted=False)
    for i in np.argsort(c[:,0]):
        near = np.asarray(neighborhoods[i], int)
        if not len(near): continue
        dx = c[near,0]-c[i,0]
        hh = np.minimum(st[i,3], st[near,3])
        dy = bottom[near]-bottom[i]
        ok = ((dx > 0) & (dx < 4*hh) & (np.abs(dy) < .28*hh+.10*dx) &
              (np.abs(st[near,3]-st[i,3]) < .65*hh))
        near = near[ok]
        if not len(near): continue
        # The nearest right neighbour in the contact corridor, not a fitted row.
        distances = c[near,0]-c[i,0]+3*np.abs(bottom[near]-bottom[i])
        j = int(near[np.argmin(distances)])
        score = float(distances.min())
        next_node[int(i)] = j
        if j not in prev_node or score < prev_node[j][1]:prev_node[j] = (int(i),score)
    for i,j in next_node.items():
        if version >= 2 and prev_node[j][0] != i:continue
        parent[root(j)] = root(i)
        edges.append([i,j])
    groups = {}
    for i in range(len(ids)): groups.setdefault(root(i), []).append(i)
    bodies = [dict(bbox=[float(a*sx),float(t*sy),float((a+w)*sx),float((t+d)*sy)],
                   centre=[float(cx*sx),float(cy*sy)], owned=bool(o), touched=bool(tt), rejected=bool(r))
              for (a,t,w,d,_),(cx,cy),o,r,tt in zip(st,c,owned,rejected,touched)]
    if version >= 4:
        for b, component in zip(bodies, ids+1):
            b.update(ownership_depth=float(depth[component]*sy),stroke_radius=float(radius[component]*sy),
                     interior_owned=bool(depth[component]>radius[component]))
    rows = []
    for group in groups.values():
        if len(group)<5:continue
        ix = np.array(sorted(group, key=lambda i:c[i,0]))
        scale_evidence = component_extent([bodies[i]["bbox"] for i in ix],
            compatibility="lower-contact chain",evidence_version=f"type-residual.v{version}.step{step}")
        local_h = scale_evidence["value_px"]
        if len(ix) < 5 or np.ptp(c[ix,0])*sx < 4*local_h: continue
        rows.append(dict(components=ix.tolist(), height=local_h, scale_evidence=scale_evidence,
                         free=[int(i) for i in ix if not owned[i] and not rejected[i]],
                         path=[[float(c[i,0]*sx),float(bottom[i]*sy)] for i in ix],
                         bbox=[float(st[ix,0].min()*sx),float(st[ix,1].min()*sy),
                               float((st[ix,0]+st[ix,2]).max()*sx),float(bottom[ix].max()*sy)]))
    return dict(bodies=bodies, rows=rows, edges=edges, height=height, step=step,
                seconds=perf_counter()-start, route=route, version=version,
                semantics='body bottom contacts; neither semantic baseline nor front ownership')


def scout(pm, items, size, *, excluded_regions=(), version=1):
    """Cheap missing localization hypothesis, inspected against body contacts.

    This reuses the already paid-for DB map. It cannot certify front print or
    character identity. Native contacts and regional localization must agree.
    """
    start=perf_counter();w,h=size;ph,pw=pm.shape
    height=height_proxy(items,size);hx=height*pw/w;hy=height*ph/h
    occupied=mask(list(items)+list(excluded_regions),pm.shape,size)
    # Keep a small sampling halo, not an expansion by a whole text-row height.
    occupied=cv2.dilate(occupied,np.ones((max(1,round(.2*hy)),max(1,round(.2*hx))),np.uint8))
    residual=((pm>.10)&(occupied==0)).astype(np.uint8)
    joined=cv2.morphologyEx(residual,cv2.MORPH_CLOSE,np.ones((1,max(1,round(2*hx))),np.uint8))
    _,labels,s,c=cv2.connectedComponentsWithStats(joined,8)
    regions=[]
    for i,(x,y,ww,hh,area) in enumerate(s[1:],1):
        if ww<4*hx or hh<.22*hy or hh>3*hy:continue
        yy,xx=np.nonzero((labels[y:y+hh,x:x+ww]==i)&residual[y:y+hh,x:x+ww].astype(bool))
        if len(xx)<2*hx*hy:continue
        regions.append(dict(bbox=[float(x*w/pw),float(y*h/ph),float((x+ww)*w/pw),float((y+hh)*h/ph)],
                            height=height, source='unowned DB-map support; nomination only'))
    return dict(regions=regions,height=height,seconds=perf_counter()-start,version=version)


def ink_scout(gray, items, *, excluded_regions=(), version=1):
    """Coarse unowned horizontal ink runs, independent of DB-map confidence."""
    start=perf_counter();height=height_proxy(items,(gray.shape[1],gray.shape[0]))
    step=max(1.,height/6);small=obs.resize(gray,(round(gray.shape[1]/step),round(gray.shape[0]/step)),cv2.INTER_LINEAR if version>=4 else cv2.INTER_AREA)
    h=height/step;k=max(1,round(3*h))|1
    ink=obs.ink(small,k,method="closing",threshold=.18,arithmetic="relative")
    owned=mask(list(items)+list(excluded_regions),small.shape,(gray.shape[1],gray.shape[0]))
    residual=ink & (1-owned)
    if version>=5:
        regions=[];width=max(1,round(12*h));stride=max(1,round(6*h))
        scale=np.array([gray.shape[1]/small.shape[1],gray.shape[0]/small.shape[0]])
        for x in range(0,small.shape[1],stride):
            right=min(small.shape[1],x+width)
            profile=gaussian_filter1d(residual[:,x:right].sum(1).astype(float),max(.5,.18*h))
            peaks,_=find_peaks(profile,height=1.5*h,prominence=h,distance=max(1,round(.5*h)))
            for y in peaks:
                regions.append(dict(bbox=[float(x*scale[0]),float(max(0,y-h)*scale[1]),float(right*scale[0]),float(min(small.shape[0],y+h)*scale[1])],height=height,source='local coarse unowned ink ridge'))
        return dict(regions=regions,height=height,seconds=perf_counter()-start,step=step,version=version)
    joined=cv2.morphologyEx(residual,cv2.MORPH_CLOSE,np.ones((max(1,round(.3*h)) if version>=4 else 1,max(1,round(2*h))),np.uint8))
    _,lab,stats,_=cv2.connectedComponentsWithStats(joined,8)
    scale=np.array([gray.shape[1]/small.shape[1],gray.shape[0]/small.shape[0]])
    regions=[]
    for i,(x,y,w,d,area) in enumerate(stats[1:],1):
        if w<4*h or d<.22*h or d>3*h:continue
        count=np.count_nonzero(residual[y:y+d,x:x+w] & (lab[y:y+d,x:x+w]==i))
        if count<.8*h*h:continue
        regions.append(dict(bbox=[*(np.array([x,y])*scale).tolist(),*(np.array([x+w,y+d])*scale).tolist()],height=height,source='coarse horizontal unowned ink run'))
    return dict(regions=regions,height=height,seconds=perf_counter()-start,step=step,version=version)
