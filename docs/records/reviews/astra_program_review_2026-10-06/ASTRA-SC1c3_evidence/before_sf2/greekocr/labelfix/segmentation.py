"""Font-scaled CTC letter regions; component labels and native ink stay immutable."""
from types import SimpleNamespace
import numpy as np
from . import ink as I
from .ctc_align import transfer_alignment
from .text import clusters, nfd, tokenize


def expected_width(ink, base=''):
    width = getattr(ink, 'font_width', .85*ink.xh)
    return width * (.55 if base.lower() in 'ι' else 1.25 if base.lower() in 'ωμ' else 1.)


def _region(ink, cs, left, right):
    """Bounding box of owned pixels in a horizontal partition, without altering labels."""
    left, right = max(0, int(left)), min(ink.width, int(right))
    ids = [c.index for c in cs]
    ys, xs = np.nonzero(np.isin(ink.labels[:, left:right], ids))
    if not len(xs):
        return None
    x0, x1 = left+int(xs.min()), left+int(xs.max())+1
    y0, y1 = int(ys.min()), int(ys.max())+1
    mask=np.isin(ink.labels[y0:y1,x0:x1],ids)
    mask.setflags(write=False)
    return SimpleNamespace(index=ids[0], component_ids=tuple(ids), mask=mask, x0=x0, x1=x1, y0=y0, y1=y1,
                           cx=(x0+x1)/2, w=x1-x0, h=y1-y0, role='letter')


def recogniser_slots(ink, text, alignment):
    """Every recognised letter gets one region, including touching/split glyphs.

    Shared components are partitioned at cached span boundaries, refined by the
    minimum *body* ink column within a quarter font-scaled letter width. A zero
    gap is neither required nor used as evidence of a separate character.
    """
    text = nfd(text)
    alignment = transfer_alignment(text, alignment)
    letters = sorted((c for c in ink.components if c.role == 'letter'), key=lambda c:c.x0)
    tokens = tokenize(text)
    slots, owners = [], {}
    for cl in clusters(text):
        if not cl.base.isalpha():
            continue
        sp = alignment.span(cl.start)
        # CTC spikes lean into the preceding letter. Absolute overlap alone
        # sends a narrow iota to its wide neighbour. Normalize by pixel width
        # on the font scale before deciding that a component is truly shared.
        ovs = [I._overlap(sp.x0, sp.x1, c.x0, c.x1)/np.sqrt(max(c.w,.35*ink.xh)) for c in letters]
        k = max(range(len(letters)), key=lambda k:ovs[k]) if letters else None
        if k is not None and ovs[k] <= 0:
            k = None
        s = dict(base=cl.base, start=cl.start, end=cl.end, locator_span=[sp.x0, sp.x1],
                 primary=k, indices=[], component_ids=[], component=None,
                 word_final=any(cl.end==t.core_end for t in tokens),
                 word_index=next((t.index for t in tokens if t.core_start<=cl.start<t.core_end), -1),
                 fused=False, split_union=False, localisation_unknown=False)
        slots.append(s)
        if k is not None:
            owners.setdefault(k, []).append(len(slots)-1)
    claimed = set(owners)
    for k, indices in owners.items():
        c = letters[k]
        ss = [slots[i] for i in indices]
        if len(ss)>1:
            width = float(np.mean([expected_width(ink,s['base']) for s in ss]))
            cuts = [c.x0]
            top, bottom = ink.band(c.cx)
            mask = ink.labels[max(0,int(top)):min(ink.height,int(np.ceil(bottom))),c.x0:c.x1]==c.index
            mass = mask.sum(axis=0)
            for j, (a,b) in enumerate(zip(ss,ss[1:]), 1):
                target = (a['locator_span'][1]+b['locator_span'][0])/2
                # Ordering and a small pixel support floor prevent zero-width
                # partitions when transferred CTC spans coincide.
                target = np.clip(target, cuts[-1]+1, c.x1-(len(ss)-j))
                lo = max(cuts[-1]+1, int(np.ceil(target-.25*width)))
                hi = min(c.x1-(len(ss)-j), int(np.floor(target+.25*width)))
                choices = range(lo, hi+1)
                cut = min(choices, key=lambda x:(mass[x-c.x0],abs(x-target))) if lo<=hi else int(target)
                cuts.append(cut)
            cuts.append(c.x1)
            for j,s in enumerate(ss):
                s.update(component=_region(ink,[c],cuts[j],cuts[j+1]), component_ids=[c.index], indices=[k],
                         fused=True, fusion_size=len(ss), region_bounds=[cuts[j],cuts[j+1]],
                         segmentation_source='font_ctc_split' if c.w>1.3*width else 'ctc_shared_narrow',
                         expected_width=width, segmentation_uncertain=c.w<=1.3*width)
        else:
            s = ss[0]; members=[k]; a,b=s['locator_span']
            extra=[j for j in (k-1,k+1) if 0<=j<len(letters) and j not in claimed
                   and I._overlap(a,b,letters[j].x0,letters[j].x1)>0]
            # S4 union: disconnected strokes under one character are retained.
            if len(extra)==1 and c.w<1.3*expected_width(ink,s['base']):
                j=extra[0]
                if max(c.x1,letters[j].x1)-min(c.x0,letters[j].x0)<=1.6*ink.xh:
                    members.append(j);claimed.add(j)
            cs=[letters[j] for j in members]
            left,right=min(q.x0 for q in cs),max(q.x1 for q in cs)
            s.update(component=_region(ink,cs,left,right),component_ids=[q.index for q in cs],indices=members,
                     region_bounds=[left,right],split_union=len(cs)>1,segmentation_source='component_union' if len(cs)>1 else 'component',
                     expected_width=expected_width(ink,s['base']),segmentation_uncertain=False)
    for s in slots:
        if s['component'] is None:
            # Still search the font-sized CTC region: lack of a letter-role
            # component is a quality flag, never a reason to suppress all marks.
            a,b=s['locator_span']; mid=(a+b)/2; w=expected_width(ink,s['base'])
            left=max(0,int(mid-w/2));right=min(ink.width,max(left+1,int(mid+w/2)))
            top,bottom=ink.band(mid)
            s.update(component=SimpleNamespace(index=-s['start']-1,x0=left,x1=right,y0=int(top),y1=int(bottom),cx=(left+right)/2,w=right-left,h=bottom-top,role='letter'),
                     region_bounds=[left,right],localisation_unknown=True,segmentation_uncertain=True,segmentation_source='font_ctc_fallback')
    return slots
