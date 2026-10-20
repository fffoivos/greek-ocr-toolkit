"""CP3 candidate: supported structural rows in an unchanged native crop.

Consumes CP2 prepared rows only. No owner selection, detection, painting, or
legacy projection/token predicate. This is geometric support, not word truth;
publication/qualification remains blocked until the native witness gate passes.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np
from greekocr.pages.boundaries import (OCCUPIED_COLUMN_INK_XH,
    RULE_REMNANT_LENGTH_XH, RULE_REMNANT_WIDTH_XH, RULE_REMNANT_ASPECT,
    HORIZONTAL_RULE_MAX_HEIGHT_XH, CROSSING_MAX_COMPONENT_HEIGHT_XH)
from greekocr.pages.structure import TABLE_BODY_HEIGHT_XH


def validate_box(page, box):
    if (len(box) != 4 or any(not isinstance(v, (int, np.integer)) for v in box)
            or not (0 <= box[0] < box[2] <= page['ink'].shape[1]
                    and 0 <= box[1] < box[3] <= page['ink'].shape[0])):
        raise ValueError('invalid_native_crop_box')


def _runs(columns):
    """Contiguous occupied columns; never bridge a word space or a column."""
    if not len(columns):
        return []
    return np.split(columns, np.flatnonzero(np.diff(columns) != 1)+1)


def supported_rows(page, box, *, magnitude_loader=None):
    """Count physical row ids per structural column before choosing an owner.

    Complete means zero guide-band cut over a LOCAL occupied run, corroborated
    by assigned body ink of existing toolkit body scale. It does not mean that
    a lexical word or the entire printed row has been recovered. Native ids and
    rejected-rule diagnostics survive. Pieces with one row_id count once.
    Separate columns never supply the second row for a merged-row positive.
    """
    validate_box(page, box)
    from .geometry_observations import vendor_magnitude, invalid_geometry_dependencies
    invalid = invalid_geometry_dependencies(page, box)
    if invalid:
        return dict(status='unavailable', reason='invalid_geometry',
            invalid_row_ids=invalid, invalid_geometry_count=page.get('invalid_geometry_count', 0),
            crop_box=list(box), decision_status='unqualified_cp3', merged=None)
    band_cut = (magnitude_loader or vendor_magnitude)()['band_cut']
    x0, y0, x1, y1 = box
    observations = []
    addresses = {}
    for row in page['rows']:
        rid = row['row_id']
        structural = page['structure'].get(rid)
        if structural is None or any(structural[k] != row[k] for k in ('column_id', 'block_id')):
            raise ValueError('inconsistent_structural_row')
        address = (structural.get('page_side'), structural['column_id'])
        if rid in addresses and addresses[rid] != address:
            raise ValueError('inconsistent_row_pieces')
        addresses[rid] = address
        xx, yy = row['_x'], row['_y']
        local = xx-row['x0']
        top, bottom = row['meanline'], row['baseline']
        if np.any(bottom <= top):
            raise ValueError('invalid_body_guides')
        hits = page['ownership'].box_hits(row, box)
        body = (yy >= top[local]) & (yy < bottom[local])
        # Exclude original elongated components using the existing boundary
        # evidence rule/text-scale criteria; a clipped rule is not a body.
        native_ids = page['labels'][yy, xx]
        excluded = []
        for cid in row['component_ids']:
            at = native_ids == cid
            if not at.any():
                continue
            height = int(np.ptp(yy[at]))+1
            width = int(np.ptp(xx[at]))+1
            xh = row['xheight']
            rule = ((height >= RULE_REMNANT_LENGTH_XH*xh and
                     (width <= RULE_REMNANT_WIDTH_XH*xh or height >= RULE_REMNANT_ASPECT*width)) or
                    (width >= RULE_REMNANT_LENGTH_XH*xh and
                     (height <= HORIZONTAL_RULE_MAX_HEIGHT_XH*xh or width >= RULE_REMNANT_ASPECT*height)))
            if rule or height > CROSSING_MAX_COMPONENT_HEIGHT_XH*xh:
                body &= ~at
                excluded.append(int(cid))
        shared = body & (xx >= x0) & (xx < x1)
        mass = np.bincount(xx[shared]-row['x0'], minlength=row['x1']-row['x0'])
        occupied = np.flatnonzero(mass >= max(1, OCCUPIED_COLUMN_INK_XH*row['xheight']))
        runs = []
        for cols in _runs(occupied):
            cut = band_cut(top[cols], bottom[cols], y0, y1)
            at = shared & np.isin(local, cols)
            visible = at & hits
            extent = int(np.ptp(yy[visible]))+1 if visible.any() else 0
            complete = cut == 0. and extent >= TABLE_BODY_HEIGHT_XH*row['xheight']
            runs.append(dict(x0=int(cols[0]+row['x0']), x1=int(cols[-1]+1+row['x0']),
                body_cut_fraction=cut, body_pixels=int(visible.sum()),
                body_extent_px=extent, complete=bool(complete),
                native_component_ids=sorted(map(int, np.unique(native_ids[visible])))))
        # CP4 reconciliation: vertical support alone cannot turn a horizontally
        # clipped group into a complete row. Reuse the local full-native group
        # evidence, before owner selection, in CP3's own row receipt.
        from .neighbour_words import row_word_evidence
        words=(row_word_evidence(page,row,box,dict(excluded_component_ids=excluded))
               if hits.any() else dict(groups=[]))
        complete_groups=[g for g in words['groups'] if g['resolved'] and
            all(l['guide_complete'] and l['extent_complete'] for l in g['letters']) and
            any(run['complete'] and run['x0']<g['box'][2] and g['box'][0]<run['x1']
                for run in runs)]
        observations.append(dict(row_id=rid, column_id=row['column_id'],
            block_id=row['block_id'], page_side=address[0], xheight=float(row['xheight']),
            assigned_pixels=int(hits.sum()), excluded_component_ids=excluded,
            runs=runs, local_groups=words['groups'],
            supported_complete=bool(complete_groups)))
    grouped = defaultdict(set)
    for r in observations:
        if r['supported_complete']:
            grouped[(r['page_side'], r['column_id'])].add(r['row_id'])
    ids = sorted({rid for group in grouped.values() for rid in group})
    return dict(status='measured', decision_status='unqualified_cp3', crop_box=list(box),
        invalid_geometry_count=page.get('invalid_geometry_count', 0),
        rows=observations, supported_row_ids=ids, supported_row_count=len(ids),
        columns=[dict(page_side=side, column_id=column, row_ids=sorted(rows), count=len(rows))
                 for (side,column), rows in sorted(grouped.items(), key=lambda p: str(p[0]))],
        merged=any(len(rows) >= 2 for rows in grouped.values()))


def screen_merged(page, box, *, legacy_features=None):
    """Replacement candidate; legacy features cannot affect its decision.

    Always explicitly unqualified until CP3's real-witness acceptance passes.
    No caller may interpret unavailable/unqualified as a verified admission.
    """
    result = supported_rows(page, box)
    if legacy_features is not None:
        result['legacy_diagnostics'] = dict(legacy_features)
    return result
