"""Exact DocAI character-anchor custody; no approximate alignment or box guesses."""
import math


def spans(obj):
    return [(int(s.get('startIndex', 0)), int(s['endIndex'])) for s in
            obj.get('layout', {}).get('textAnchor', {}).get('textSegments', [])]


def locate_slot(row, slot, document, *, exact_boundary=False):
    out = dict(geom_status='no_symbols')
    pages = document.get('pages', [])
    if not pages or not pages[0].get('symbols'):
        return out
    page = pages[0]
    lines = page.get('lines', [])
    i = row['docai_line_index']
    if i >= len(lines):
        return dict(geom_status='misaligned', reason='missing line index')
    text = document.get('text', '')
    anchors = [p for a, b in spans(lines[i]) for p in range(a, b)]
    # Collector inspect strips line-edge whitespace only. Preserve interior offsets.
    while anchors and text[anchors[-1]].isspace(): anchors.pop()
    while anchors and text[anchors[0]].isspace(): anchors.pop(0)
    label = row.get('label', row['text'])
    if ''.join(text[p] for p in anchors) != label or row['text'] != label:
        return dict(geom_status='misaligned', reason='line text differs from frame label')
    a, b = slot['start'], slot['end']
    if not 0 <= a <= b <= len(label) or label[a:b] != slot['glyph']:
        return dict(geom_status='misaligned', reason='slot offsets/glyph differ')
    bypos = {}
    anchor_set = set(anchors)
    cb = row['crop_bbox']
    for symbol in page['symbols']:
        ps = [p for x, y in spans(symbol) for p in range(x, y)]
        if not anchor_set.intersection(ps): continue
        verts = symbol.get('layout', {}).get('boundingPoly', {}).get('vertices', [])
        if not verts: continue
        box = [min(v.get('x', 0) for v in verts)-cb[0], min(v.get('y', 0) for v in verts)-cb[1],
               max(v.get('x', 0) for v in verts)-cb[0], max(v.get('y', 0) for v in verts)-cb[1]]
        for p in ps: bypos.setdefault(p, []).append((ps, box))
    def digit(pos):
        if not 0 <= pos < len(label) or not label[pos].isascii() or not label[pos].isdigit():
            raise ValueError('flank is not digit')
        hits = bypos.get(anchors[pos], [])
        if not hits: raise LookupError('missing digit symbol')
        if len(hits) != 1 or len(hits[0][0]) != 1: raise ValueError('ambiguous digit anchor')
        box = hits[0][1]
        if not (0 <= box[0] < box[2] <= cb[2]-cb[0] and 0 <= box[1] < box[3] <= cb[3]-cb[1]):
            raise ValueError('digit box outside crop')
        return box
    try:
        side = slot.get('boundary')
        left = digit(a-1) if side != 'left' else None
        right = digit(b) if side != 'right' else None
        boxes = [v for v in (left, right) if v]
        top = min(v[1] for v in boxes); baseline = max(v[3] for v in boxes)
        h = baseline-top
        if left and right:
            x0, x1 = left[2], right[0]
            z0, z1 = left[0], right[2]
            if right[0] < left[0]: raise ValueError('reversed digit boxes')
        else:
            d = boxes[0]; width = d[2]-d[0]
            candidates = [v[1] for values in bypos.values() for v in values]
            if side == 'left':
                adjacent = [v[2] for v in candidates if v[2] <= d[0] and v != d]
                x0, x1 = max(adjacent) if adjacent else (0 if exact_boundary else max(0, d[0]-1.5*width)), d[0]
                z0, z1 = x0, d[2]
            else:
                adjacent = [v[0] for v in candidates if v[0] >= d[2] and v != d]
                x0, x1 = d[2], min(adjacent) if adjacent else (cb[2]-cb[0] if exact_boundary else min(cb[2]-cb[0], d[2]+1.5*width))
                z0, z1 = d[0], x1
        return dict(geom_status='ok', left_digit=left, right_digit=right, digit_top=top,
                    baseline=baseline, digit_height=h, gap=[x0, x1], gap_width=x1-x0,
                    gap_center=(x0+x1)/2, zoom_bbox=[math.floor(z0-.3*h), math.floor(top-.3*h),
                    math.ceil(z1+.3*h), math.ceil(baseline+.3*h)])
    except LookupError as e:
        return dict(geom_status='no_symbols', reason=str(e))
    except ValueError as e:
        return dict(geom_status='misaligned', reason=str(e))
