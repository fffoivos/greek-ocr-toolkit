"""Unchanged T6a2/T6d component_audit, copied from the shared audited implementation."""
import numpy as np


def component_audit(prepared, labels, box, mask, owner_row, box_hits):
    """Measure actual native changes against detector-assigned components.

    Shared by the original dev audit and T6d. Unknown owners stay unknown;
    unassigned foreground is never silently called foreign text.
    """
    x0,y0,x1,y1=box
    own=prepared.get(owner_row)
    own_ids_before=set();own_ids_lost=set();lost=own_pixels=0
    if own is not None:
        before=box_hits(own,box)
        yy,xx=own['_y'][before],own['_x'][before];hit=mask[yy-y0,xx-x0]
        own_ids_before=set(labels[yy,xx]);own_ids_lost=set(labels[yy[hit],xx[hit]])
        own_ids_before.discard(0);own_ids_lost.discard(0)
        own_pixels=int(before.sum());lost=int(hit.sum())
    foreign_ids_before=set();foreign_ids_removed=set();foreign_ids_touched=set()
    foreign_before=foreign_removed=0
    for row in prepared.values():
        if own is None or row['row_id']==own['row_id']:continue
        before=box_hits(row,box);yy,xx=row['_y'][before],row['_x'][before]
        if not len(yy):continue
        ids=labels[yy,xx];hit=mask[yy-y0,xx-x0]
        foreign_before+=len(yy);foreign_removed+=int(hit.sum())
        for ident in np.unique(ids):
            if ident==0:continue
            sel=ids==ident;foreign_ids_before.add(int(ident))
            if hit[sel].any():foreign_ids_touched.add(int(ident))
            if hit[sel].all():foreign_ids_removed.add(int(ident))
    known=own is not None
    counts=dict(own_component_pixels_lost=lost if known else None,
        own_pixels=own_pixels if known else None,
        own_components_before=len(own_ids_before) if known else None,
        own_components_touched=len(own_ids_lost) if known else None,
        foreign_pixels_before=foreign_before if known else None,
        foreign_pixels_removed=foreign_removed if known else None,
        foreign_components_before=len(foreign_ids_before) if known else None,
        foreign_components_touched=len(foreign_ids_touched) if known else None,
        foreign_components_removed_from_crop=len(foreign_ids_removed) if known else None)
    return counts,own_ids_lost
