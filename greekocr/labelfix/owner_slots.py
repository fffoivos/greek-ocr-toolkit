"""Owner slot identities are pinned to v8 ink, independent of later detectors."""
from __future__ import annotations


def overlap_slots(x0, x1, slots):
    """Return every overlapping slot and the unique largest-overlap owner.

    No nearest-letter fallback: a removed component remains unresolved.
    """
    hits=[]
    for s in slots:
        b=s['bbox']
        ov=max(0,min(x1,b[2])-max(x0,b[0]))
        if ov:
            hits.append((s['slot'],ov))
    hits.sort(key=lambda p:(-p[1],p[0]))
    owner=hits[0][0] if hits and (len(hits)==1 or hits[0][1]>hits[1][1]) else None
    return owner,[s for s,_ in hits]
