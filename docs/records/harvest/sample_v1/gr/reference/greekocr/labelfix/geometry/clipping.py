"""Crop clipping against fitted body and upper-accent guides and actual ink."""
from __future__ import annotations

import numpy as np


def clipping(row: dict | None, crop_box) -> dict:
    if row is None:
        return dict(clip_top=None, clip_bottom=None, clip_status='ok',
                    clip_evaluable=False, clip_detail=None)
    x0, y0, x1, y1 = crop_box
    a, b = max(row['x0'], x0), min(row['x1'], x1)
    if b <= a:
        return clipping(None, crop_box)
    s = slice(int(a-row['x0']), int(b-row['x0']))
    # accent_bottom is the LOWER edge of the UPPER accent band, not a
    # descender guide. Descenders are included by font_bottom.
    detail = dict(body_top_px=float(max(0., np.max(y0-row['font_top'][s]))),
                  body_bottom_px=float(max(0., np.max(row['font_bottom'][s]-y1))),
                  accent_top_px=float(max(0., np.max(y0-row['accent_top'][s]))),
                  accent_bottom_px=float(max(0., np.max(row['accent_bottom'][s]-y1))))
    xx, yy = row['_x'], row['_y']
    local = xx-row['x0']
    outside = (xx >= x0) & (xx < x1) & ((yy < y0) | (yy >= y1))
    body = (yy >= row['font_top'][local]) & (yy < row['font_bottom'][local])
    accent = (yy >= row['accent_top'][local]) & (yy < row['accent_bottom'][local])
    detail.update(body_ink_cut=int((outside & body).sum()),
                  accent_ink_cut=int((outside & accent & ~body).sum()),
                  other_row_ink_cut=int((outside & ~body & ~accent).sum()))
    status = ('body_cut' if detail['body_ink_cut'] else
              'accents_cut' if detail['accent_ink_cut'] else 'ok')
    return dict(clip_top=max(detail['body_top_px'], detail['accent_top_px']),
                clip_bottom=max(detail['body_bottom_px'], detail['accent_bottom_px']),
                clip_status=status, clip_evaluable=True, clip_detail=detail)
