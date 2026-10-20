"""Font-size estimation and fused-ink diagnostics, independent of ink.py/SciPy.

Components are NEVER an acceptance test. No horizontal gap or column test is used.
"""
from collections import Counter
import math
import numpy as np

FONT_RULE = dict(confidence_min=.5, width_over_median_ctc=[.2, 2.0],
                 width_over_pixel_height=[.1, 2.0],
                 pixel_height='median per-letter 5th--95th ink-row mass extent; prefer alpha epsilon omicron sigma pi nu omega upsilon',
                 fallback='all alphabetic spans; if blank, median CTC width / 0.6',
                 margins_font_heights=dict(left=1.5, narrow_left=.75, right=.75),
                 vertical='entire original line crop, including all available mark zone',
                 fused='8-connected Otsu components >=0.45 font-height; multiple CTC character primary owners by largest horizontal overlap; diagnostic only')


def threshold_image(image):
    a=np.asarray(image,dtype=np.uint8)
    hist=np.bincount(a.ravel(),minlength=256).astype(float)
    p=hist/max(1,a.size);omega=np.cumsum(p);mu=np.cumsum(p*np.arange(256))
    between=(mu[-1]*omega-mu)**2/np.maximum(omega*(1-omega),1e-12)
    threshold=min(220,max(40,int(np.argmax(between))))
    return a<=threshold,threshold


def font_size(binary, letters):
    """Robust pixel body height, with independent median CTC width reference.

    Per-letter vertical ink quantiles discard sparse detached marks. Medians of
    short lowercase bodies limit capitals/ascenders, without any ink ownership
    or gap requirement. Fused letters contribute their pixels just like others.
    """
    heights=[];preferred=[];widths=[]
    for base,_,(a,b) in letters:
        if b>a:widths.append(b-a)
        lo,hi=max(0,math.floor(a)),min(binary.shape[1],math.ceil(b))
        mass=binary[:,lo:hi].sum(axis=1)
        if not mass.sum():continue
        cumulative=np.cumsum(mass)
        h=float(np.searchsorted(cumulative,.95*cumulative[-1])-np.searchsorted(cumulative,.05*cumulative[-1])+1)
        heights.append(h)
        if base in 'αεοσπνωυ':preferred.append(h)
    median=float(np.median(widths)) if widths else 1.
    chosen=preferred if len(preferred)>=3 else heights
    height=float(np.median(chosen)) if chosen else median/.6
    return dict(pixel_height=max(1.,height),median_ctc_width=max(.1,median),
                pixel_measurements=len(chosen),preferred_measurements=len(preferred),
                pixel_fallback=not bool(chosen))


def plausible_span(span, size):
    w=span[1]-span[0]
    if not .2*size['median_ctc_width']<=w<=2.*size['median_ctc_width']:
        return False,'width_outside_0.2_2.0_median_ctc'
    if not .1*size['pixel_height']<=w<=2.*size['pixel_height']:
        return False,'width_outside_0.1_2.0_pixel_height'
    return True,'scored'


def component_boxes(binary):
    """8-connected row-run union-find; only used to describe fused cases."""
    parent=[];runs=[];previous=[]
    def root(k):
        while parent[k]!=k:
            parent[k]=parent[parent[k]];k=parent[k]
        return k
    for y,row in enumerate(binary):
        edges=np.diff(np.r_[False,row,False].astype(np.int8))
        current=[];j=0
        for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            a,b=int(a),int(b);k=len(parent);parent.append(k);runs.append((a,y,b,y+1));current.append((a,b,k))
            while j<len(previous) and previous[j][1]<a:j+=1
            t=j
            while t<len(previous) and previous[t][0]<=b:
                parent[root(previous[t][2])]=root(k);t+=1
        previous=current
    boxes={}
    for k,(a,y,b,z) in enumerate(runs):
        r=root(k)
        if r not in boxes:boxes[r]=[a,y,b,z]
        else:
            q=boxes[r];q[0]=min(q[0],a);q[1]=min(q[1],y);q[2]=max(q[2],b);q[3]=max(q[3],z)
    return list(boxes.values())


def fused_slots(binary, letters, height):
    boxes=[b for b in component_boxes(binary) if b[3]-b[1]>=.45*height]
    owners={};primary={}
    for base,start,(a,b) in letters:
        overlaps=[max(0.,min(b,q[2])-max(a,q[0])) for q in boxes]
        if overlaps and max(overlaps)>0:
            k=max(range(len(boxes)),key=lambda i:overlaps[i]);primary[start]=k
            owners.setdefault(k,[]).append(start)
    return {s:dict(fused=len(owners[k])>1,component_bbox=boxes[k],component_owners=owners[k])
            for s,k in primary.items()}
