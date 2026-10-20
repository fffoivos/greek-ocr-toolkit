"""Spatial orientation regions, explicit group inheritance, and a two-angle cap."""
from __future__ import annotations

from dataclasses import replace
from typing import Sequence
from PIL import Image
import numpy as np

from .orientation import Orientation, discover_directions, measure_orientation

__all__ = ['axis_regions', 'resolve_regions', 'page_regions']


def axis_regions(proposals: Sequence[dict]) -> list[dict]:
    """Join same-axis chains by typographic whitespace; reject crossing fragments.

    Three body heights along and four across permit word gaps and normal line
    leading. Opposite chains overlapping most of a proposed chain indicate a
    spurious cross-line alignment, not a separate printed block.
    """
    if not proposals:
        return []
    parent = list(range(len(proposals)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i,a in enumerate(proposals):
        aa = a.get('box')
        if aa is None:
            continue
        for j in range(i):
            b = proposals[j]
            if a['axis'] != b['axis'] or 'box' not in b:
                continue
            bb = b['box']; h = max(a['xheight'], b['xheight'])
            gap = [max(aa[k]-bb[k+2], bb[k]-aa[k+2], 0) for k in (0,1)]
            axis = int(a['axis']=='vertical')
            if gap[axis] <= 3*h and gap[1-axis] <= 4*h:
                parent[root(i)] = root(j)
    grouped = {}
    for i,p in enumerate(proposals):
        if 'box' in p:
            grouped.setdefault(root(i), []).append(p)
    out = []
    for members in grouped.values():
        q = np.array([p['box'] for p in members]); support = sum(p['components'] for p in members)
        axis = members[0]['axis']; overlaps = total = 0.
        for p in members:
            a = p['box']; area = (a[2]-a[0])*(a[3]-a[1]); total += area
            overlap = 0.
            for other in proposals:
                if other['axis'] == axis or 'box' not in other:
                    continue
                b = other['box']
                overlap += max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
            overlaps += min(area, overlap)
        if overlaps > total/2:
            continue
        out.append(dict(box=[*q[:,:2].min(0),*q[:,2:].max(0)],axis=axis,
                        components=support,xheight=float(np.median([p['xheight'] for p in members])),
                        chains=len(members), chain_boxes=q.tolist(),
                        axis_confidence=float(np.median([p['axis_confidence'] for p in members]))))
    return sorted(out, key=lambda p:(-p['components'], p['box'][1], p['box'][0]))


def resolve_regions(regions: Sequence[dict], *, main_id: str | None = None) -> list[dict]:
    """Inherit within explicit groups, then retain at most two accepted angles.

    Each record contains an Orientation decision. Numeric rows can receive but
    never supply a decision, including when a caller supplied one accidentally.
    Input records and decisions are not mutated. Conflicting headers abstain.
    """
    rows = [{**r, 'decision':replace(r['decision'], evidence=dict(r['decision'].evidence))} for r in regions]
    for row in rows:
        if row.get('content_kind') == 'numbers':
            row['decision'].orientation_cw = None
            row['decision'].polarity_confidence = 0.
            row['decision'].evidence['polarity_source'] = 'numbers-require-header'
    for row in rows:
        d = row['decision']
        if d.orientation_cw is not None or not row.get('orientation_group'):
            continue
        peers = [r for r in rows if r['id'] != row['id'] and
                 r.get('orientation_group') == row['orientation_group'] and
                 r.get('content_kind') != 'numbers' and r['decision'].axis == d.axis and
                 r['decision'].orientation_cw is not None and not r['decision'].evidence.get('inherited_from')]
        angles = {r['decision'].orientation_cw for r in peers}
        if len(angles) == 1:
            peer = peers[0]
            d.orientation_cw = peer['decision'].orientation_cw
            d.polarity_confidence = peer['decision'].polarity_confidence
            d.evidence.update(polarity_source='orientation-group-header', inherited_from=peer['id'])
    ordered = sorted(rows, key=lambda r:(r['id'] != main_id, -r.get('components',0)))
    allowed = []
    for row in ordered:
        d = row['decision']; angle = d.orientation_cw
        if angle is None or angle in allowed:
            continue
        if len(allowed) < 2:
            allowed.append(angle)
        else:
            d.evidence.update(rejected_orientation_cw=angle, polarity_source='third-orientation-unknown')
            d.orientation_cw = None; d.polarity_confidence = 0.
    # An inherited child must not retain an angle removed from its header.
    for row in rows:
        d = row['decision']
        if d.orientation_cw is not None and d.orientation_cw not in allowed:
            d.evidence.update(rejected_orientation_cw=d.orientation_cw, polarity_source='third-orientation-unknown')
            d.orientation_cw = None; d.polarity_confidence = 0.
    return rows


def page_regions(image: Image.Image, *, proposals: list[dict] | None = None,
                 dominant: Orientation | None = None, use_osd: bool = False) -> tuple[Orientation, list[dict], list[dict]]:
    """Discover before fitting; compare both readings of main and minority regions."""
    proposals = discover_directions(image) if proposals is None else proposals
    blocks = axis_regions(proposals)
    main = blocks[0] if blocks else None
    if dominant is None:
        # Main writing is pooled over the page, including its headers. A
        # dense numeric sub-block must not exclude the words that orient it.
        # This is also the exact path used by the pre-layout adapter.
        dominant = measure_orientation(image, use_osd=use_osd, unit='page')
    reference = None
    for reading in dominant.evidence.get('guide_test',{}).get('readings',[]):
        if reading['orientation_cw'] == dominant.orientation_cw:
            reference = reading['proportions']
    rows = [dict(id='page',box=[0,0,*image.size],axis=dominant.axis,
                 components=main['components'] if main else 0,decision=dominant)]
    for block in blocks[1:]:
        decision = measure_orientation(image.crop(block['box']), axis_hint=block['axis'],
                                       font_reference=reference, use_osd=use_osd)
        rows.append(dict(id=f'region-{len(rows)}', **block, decision=decision))
    return dominant, resolve_regions(rows, main_id='page'), proposals
