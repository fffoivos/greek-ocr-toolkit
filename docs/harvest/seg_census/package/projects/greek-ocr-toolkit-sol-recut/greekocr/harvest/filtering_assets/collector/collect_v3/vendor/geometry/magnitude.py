"""Physical magnitudes, independent of flags and threshold selection.

Lengths count occupied columns rather than the distance to a remote speck.
Fractions are dimensionless; pixel coordinates remain in the detector frame.
"""
from __future__ import annotations

import unicodedata
import numpy as np


FEATURES = ('ink_outside_box_left', 'ink_outside_box_right', 'body_cut_fraction',
            'accent_cut_fraction', 'box_height_in_row', 'label_vs_ink_ratio',
            'neighbour_body_ink_xh', 'row_ink_extent_xh', 'label_atoms',
            'body_ink_cut_fraction', 'accent_ink_cut_fraction')


def column_profile(row: dict) -> tuple[np.ndarray, float]:
    """Nonzero median mass; a column qualifies inclusively at 30 percent."""
    if '_column_profile' in row:
        return row['_column_profile']
    mass = np.bincount(row['_x']-row['x0'], minlength=row['x1']-row['x0'])
    median = float(np.median(mass[mass > 0])) if np.any(mass) else 0.
    row['_column_profile'] = mass, median
    return mass, median


def band_cut(top, bottom, y0, y1) -> float:
    """Fraction of guide-band area outside vertical crop, on sampled columns."""
    height = np.maximum(0., np.asarray(bottom)-np.asarray(top))
    retained = np.maximum(0., np.minimum(bottom, y1)-np.maximum(top, y0))
    return float(np.clip(1.-retained.sum()/height.sum(), 0., 1.)) if height.sum() else 0.


def measured_owner(old: dict, rows: list[dict]) -> tuple[dict | None, str | None]:
    """Keep multiple owners ambiguous; measure the best partial-height owner.

    The partial owner is diagnostic only. Original G1 cross ownership remains
    a strict recut blocker, regardless of the calibrated audit decision.
    """
    by_id = {r['row_id']: r for r in rows}
    if old.get('ownership_reason') == 'multiple_owners':
        return None, 'multiple_owners'
    if old.get('row_id') in by_id:
        return by_id[old['row_id']], None
    overlaps = old.get('row_overlaps', [])
    if overlaps and overlaps[0]['row_id'] in by_id:
        return by_id[overlaps[0]['row_id']], None
    return None, 'detector_failure:no_row'


def measure(old: dict, row: dict | None, rows: list[dict]) -> dict:
    """Measure every line before thresholding, without a model prediction."""
    result = dict.fromkeys(FEATURES)
    result['label_atoms'] = len(unicodedata.normalize('NFD', old['old_label']))
    if row is None:
        return result
    x0, y0, x1, y1 = old['bbox']
    cx0, cy0, cx1, cy1 = old['crop_bbox']
    xh = float(row['xheight'])
    mass, median = column_profile(row)
    strong = np.flatnonzero((mass > 0) & (mass >= .3*median)) + row['x0']
    result.update(ink_outside_box_left=float(np.count_nonzero(strong < x0)/xh),
                  ink_outside_box_right=float(np.count_nonzero(strong >= x1)/xh),
                  row_ink_extent_xh=float((strong[-1]+1-strong[0])/xh) if len(strong) else 0.,
                  row_xheight=xh, median_column_mass=median,
                  strong_ink_columns=len(strong), column_mass_min_fraction=.3,
                  measured_row_id=row['row_id'])
    a,b = max(row['x0'],int(x0)),min(row['x1'],int(x1))
    local = np.arange(a,b)-row['x0']
    result['box_height_in_row'] = (float(np.mean(np.maximum(0.,
        np.minimum(y1,row['bottom'][local])-np.maximum(y0,row['top'][local])))/(y1-y0))
        if len(local) else 0.)
    cols = strong[(strong >= cx0) & (strong < cx1)]-row['x0']
    result['body_cut_fraction'] = band_cut(row['meanline'][cols],row['baseline'][cols],cy0,cy1)
    result['accent_cut_fraction'] = band_cut(row['accent_top'][cols],row['accent_bottom'][cols],cy0,cy1)
    xx,yy = row['_x'],row['_y']; lx=xx-row['x0']
    shared = (xx >= cx0) & (xx < cx1)
    outside = (yy < cy0) | (yy >= cy1)
    body = shared & (yy >= row['meanline'][lx]) & (yy < row['baseline'][lx])
    accent = shared & (yy >= row['accent_top'][lx]) & (yy < row['accent_bottom'][lx])
    result.update(body_ink_cut_fraction=float(np.count_nonzero(body & outside)/max(1,np.count_nonzero(body))),
                  accent_ink_cut_fraction=float(np.count_nonzero(accent & outside)/max(1,np.count_nonzero(accent))),
                  body_ink_pixels=int(np.count_nonzero(body)), accent_ink_pixels=int(np.count_nonzero(accent)))
    # Neighbor intrusion must contain BODY ink. A fitted ribbon or isolated
    # borrowed accent guide touching this box supplies no material overrun.
    neighbour=[]
    for other in rows:
        if other['row_id']==row['row_id']:
            continue
        if (other['x1']<=x0 or other['x0']>=x1 or
                np.min(other['meanline'])>=y1 or np.max(other['baseline'])<=y0):
            continue
        ox,oy=other['_x'],other['_y'];ol=ox-other['x0']
        inside = ((ox>=x0)&(ox<x1)&(oy>=y0)&(oy<y1)&
                  (oy>=other['meanline'][ol])&(oy<other['baseline'][ol]))
        if not np.any(inside):
            continue
        _, omedian=column_profile(other)
        counts=np.bincount(ox[inside]-other['x0'],minlength=other['x1']-other['x0'])
        amount=float(np.count_nonzero((counts>0)&(counts>=.3*omedian))/other['xheight'])
        neighbour.append(dict(row_id=other['row_id'],body_ink_xh=amount))
    result.update(neighbour_body_ink_xh=max((n['body_ink_xh'] for n in neighbour),default=0.),
                  neighbour_body_magnitudes=neighbour)
    return result


def page_ratios(records: list[dict]) -> float | None:
    """Normalize NFD atoms per full row extent by page median, before scoring.

    Spaces and combining marks each count as NFD atoms, consistently with E3.
    Unmeasured and empty rows do not contribute to the median.
    """
    ratios = [r['label_atoms']/r['row_ink_extent_xh'] for r in records
              if r['row_ink_extent_xh'] and r['label_atoms']]
    median = float(np.median(ratios)) if ratios else None
    for r in records:
        extent=r['row_ink_extent_xh']
        r['label_vs_ink_ratio']=(float(r['label_atoms']/extent/median) if extent and median else None)
        r['page_median_atoms_per_xh']=median
    return median


def decision(features: dict, thresholds: dict) -> dict:
    """Two independently visible families; unresolved is never a positive."""
    if features.get('measurement_failure'):
        return dict(span_defect=None,clip_defect=None,geometry_positive=None,
                    span_status='unresolved',clip_status='unresolved')
    t=thresholds
    left,right=features['ink_outside_box_left'],features['ink_outside_box_right']
    ratio=features['label_vs_ink_ratio']
    fragment=max(left,right)>t['ink_out']
    # Oversplit physical rows can make large apparent neighbor magnitudes.
    # Density corroborates intrusion/cross; it never creates a defect alone.
    density_support = ratio is not None and ratio<t['label_ratio_support_max']
    overrun=features['neighbour_body_ink_xh']>t['ink_out'] and density_support
    cross=features['box_height_in_row']<t['box_height_min'] and density_support
    body=(features['body_cut_fraction']>t['body_cut'] and features['body_ink_cut_fraction']>0)
    accent=(features['accent_cut_fraction']>t['accent_cut'] and features['accent_ink_cut_fraction']>0)
    span=fragment or overrun or cross
    return dict(span_defect=bool(span),clip_defect=bool(body or accent),
                geometry_positive=bool(span or body or accent),
                span_status='cross' if cross else 'overrun' if overrun else 'fragment' if fragment else 'whole_row',
                clip_status='body_cut' if body else 'accents_cut' if accent else 'ok',
                span_components=dict(fragment=fragment,overrun=overrun,cross=cross,density_support=density_support),
                clip_components=dict(body=bool(body),accent=bool(accent)))
