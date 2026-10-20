"""Ink spans and admitted-fragment assembly, independent of model text."""
from __future__ import annotations

import numpy as np
from .ownership import box_hits


def runs(xs) -> list[list[int]]:
    values = np.unique(xs)
    if not len(values):
        return []
    groups = np.split(values, np.flatnonzero(np.diff(values) > 1) + 1)
    return [[int(g[0]), int(g[-1]) + 1] for g in groups]


def span_audit(box, owner: dict | None, rows: list[dict], siblings: list[dict]) -> dict:
    if owner is None:
        return dict(span_status='cross_row', ink_outside_box=None, neighbour_ink=[])
    x0, _, x1, _ = box
    xs = owner['_ink_columns']
    left, right = xs[xs < x0], xs[xs >= x1]
    # Extent and number of occupied columns are both retained; whitespace is
    # never treated as a missing character or a missing line.
    outside = dict(left_xheight=float((x0-left.min()) / owner['xheight']) if len(left) else 0.,
                   right_xheight=float((right.max()+1-x1) / owner['xheight']) if len(right) else 0.,
                   left_pixels=int(np.sum(owner['_x'] < x0)),
                   right_pixels=int(np.sum(owner['_x'] >= x1)))
    neighbours = [dict(row_id=r['row_id'], ink_pixels=int(box_hits(r, box).sum()))
                  for r in rows if r['row_id'] != owner['row_id'] and box_hits(r, box).any()]
    status = ('overrun' if neighbours else 'fragment' if len(left) or len(right) or
              siblings else 'whole_row')
    return dict(span_status=status, ink_outside_box=outside, neighbour_ink=neighbours)


def assemble(row: dict, fragments: list[dict]) -> dict:
    """X-order text assembly; refuse uncovered ink and duplicated ink custody.

    Coverage is horizontal, because clipping is measured separately. A single
    vertically clipped fragment may still supply a whole-row label. Text is
    never inferred for uncovered ink, including at the two ends of a row.
    """
    ordered = sorted(fragments, key=lambda f: (f['bbox'][0], f['bbox'][2], f['id']))
    xs = row['_ink_columns']
    coverage = np.zeros(len(xs), dtype=np.int32)
    for f in ordered:
        coverage += (xs >= f['bbox'][0]) & (xs < f['bbox'][2])
    missing = xs[coverage == 0]
    repeated = xs[coverage > 1]
    return dict(row_label=' '.join(f['fragment_text'].strip() for f in ordered),
                fragment_ids=[f['id'] for f in ordered],
                gap=bool(len(missing)), gap_ink_runs=runs(missing),
                overlapping_fragment_ink=bool(len(repeated)), overlap_ink_runs=runs(repeated),
                label_source='v2_admitted_google_fragments_x_order_preserving_existing_cleaning',
                join_policy='single_space_between_stripped_fragment_texts')
