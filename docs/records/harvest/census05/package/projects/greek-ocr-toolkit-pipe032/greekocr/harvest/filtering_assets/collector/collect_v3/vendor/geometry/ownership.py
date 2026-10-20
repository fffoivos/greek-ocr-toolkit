"""Map Google boxes to the stable detector's tessellated row ribbons."""
from __future__ import annotations

import numpy as np

CURVES = ("baseline", "meanline", "font_top", "font_bottom", "accent_top",
          "accent_bottom", "top", "bottom")


def prepare_row(record: dict, ink: np.ndarray, labels: np.ndarray | None = None) -> dict:
    """Use the detector's assigned components, including any clipped by its band.

    Synthetic fixtures may supply a ribbon mask alone. Production caches must
    carry component IDs and the label plane; ribbon residuals never own text.
    """
    row = dict(record)
    for key in CURVES:
        row[key] = np.asarray(row[key], dtype=float)
    n = row["x1"] - row["x0"]
    if (n <= 0 or row["xheight"] <= 0 or
            any(len(row[k]) != n or not np.isfinite(row[k]).all() for k in CURVES) or
            np.any(row["bottom"] <= row["top"])):
        raise ValueError("invalid_detector_geometry")
    h, w = ink.shape
    if not 0 <= row['x0'] < row['x1'] <= w:
        raise ValueError("detector_x_out_of_page")
    y0 = max(0, int(np.floor(row.get('owned_box',[0,row['top'].min(),0,0])[1])))
    y1 = min(h, int(np.ceil(row.get('owned_box',[0,0,0,row['bottom'].max()])[3])))
    mask=ink[y0:y1, row['x0']:row['x1']]
    if 'component_ids' in row:
        if labels is None:
            raise ValueError('missing_detector_component_labels')
        mask=mask & np.isin(labels[y0:y1,row['x0']:row['x1']],row['component_ids'])
    yy, xx = np.nonzero(mask)
    yy = yy + y0
    good = np.ones(len(xx),bool) if labels is not None else ((yy >= row["top"][xx]) & (yy < row["bottom"][xx]))
    row['_y'], row['_x'] = yy[good], xx[good] + row['x0']
    row['_ink_columns'] = np.unique(row['_x'])
    local=row['_x']-row['x0']
    row['_geometry_cut_pixels']=int(((row['_y']<row['top'][local]) | (row['_y']>=row['bottom'][local])).sum())
    return row


def box_hits(row: dict, box) -> np.ndarray:
    x0, y0, x1, y1 = box
    return ((row['_x'] >= x0) & (row['_x'] < x1) &
            (row['_y'] >= y0) & (row['_y'] < y1))


def ownership(box, rows: list[dict]) -> dict:
    """Mean vertical overlap on shared X columns; width is not the threshold.

    The 50% boundary is inclusive. Two rows at that boundary are ambiguous.
    No candidate/no detected row is cross_row with an explicit missing reason.
    """
    x0, y0, x1, y1 = map(float, box)
    if not np.isfinite(box).all() or x1 <= x0 or y1 <= y0:
        raise ValueError("invalid_box")
    hits = []
    for row in rows:
        a, b = max(row['x0'], int(np.floor(x0))), min(row['x1'], int(np.ceil(x1)))
        if b <= a:
            continue
        s = slice(a - row['x0'], b - row['x0'])
        overlap = np.maximum(0, np.minimum(y1, row['bottom'][s]) - np.maximum(y0, row['top'][s]))
        fraction = float(np.mean(overlap) / (y1 - y0))
        if fraction > 0:
            hits.append(dict(row_id=row['row_id'], fraction=fraction,
                             horizontal_overlap=b-a))
    hits.sort(key=lambda h: (-h['fraction'], -h['horizontal_overlap'], h['row_id']))
    owners = [h for h in hits if h['fraction'] >= .5]
    # Separate columns can share Y. Require an unambiguous row, never guess a
    # full-width multi-column box's owner using its text length.
    owned = len(owners) == 1
    return dict(row_id=owners[0]['row_id'] if owned else None,
                box_in_row_fraction=hits[0]['fraction'] if hits else 0.,
                row_overlaps=hits, ownership_status='owned' if owned else 'cross_row',
                ownership_reason=None if owned else ('no_detector_row' if not hits else
                    'multiple_owners' if len(owners) > 1 else 'under_half_height'))
