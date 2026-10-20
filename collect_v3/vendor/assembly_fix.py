"""Offline T4b assembly overlay. Does not import or modify shipped processing.

Suppress competing tokens with native AABB IoU > 0.10, vertical overlap
>= 0.80 of the smaller height, and center separation <= 0.45 smaller heights.
Horizontal intersection must cover >= 0.60 of the shorter token width.
Each geometric overlap component must contain a text-compatible pair
(substring or SequenceMatcher similarity >= 0.40); all its geometric conflicts
then compete, including incompatible alternative readings of the same ink.
Choose a non-conflicting set maximizing base-letter/digit count times provider
confidence. This retains complete readings over contained fragments, and can
retain two genuine words over one hallucinated combined token. Distinct,
nonoverlapping repeated words are untouched. Original text-anchor slices are
deleted, so retained punctuation and order are not re-tokenized.
"""
from __future__ import annotations
import base64
import math
import unicodedata as ud
import numpy as np

IOU_THRESHOLD = 0.10
VERTICAL_OVERLAP = 0.80
CENTER_SEPARATION = 0.45
HORIZONTAL_OVERLAP = 0.60


def spans(node):
    return [(int(s.get('startIndex', 0)), int(s['endIndex']))
            for s in node.get('layout', {}).get('textAnchor', {}).get('textSegments', [])]


def normalise(text):
    return ' '.join(ud.normalize('NFC', text.replace('\u02d9', '\u00b7')).split())


def inverse_frame(page, native_size):
    total = np.eye(3)
    dim = page.get('dimension', {})
    returned = (dim.get('width', native_size[0]), dim.get('height', native_size[1]))
    for m in page.get('transforms', []):
        if m['type'] not in (5, 6):
            raise ValueError('unsupported matrix')
        a = np.frombuffer(base64.b64decode(m['data']), dtype='<f4' if m['type'] == 5 else '<f8').reshape(m['rows'], m['cols'])
        if m['rows'] == 2:
            a = np.vstack((a, [0, 0, 1]))
        total = a @ total
    if not page.get('transforms') and tuple(returned) != tuple(native_size):
        raise ValueError('different frame without transform')
    return np.linalg.inv(total), returned


def box(node, inverse, returned):
    poly = node.get('layout', {}).get('boundingPoly', {})
    points = poly.get('vertices')
    if not points:
        points = [dict(x=v.get('x', 0)*returned[0], y=v.get('y', 0)*returned[1])
                  for v in poly.get('normalizedVertices', [])]
    if not points:
        return None
    a = np.array([[v.get('x', 0), v.get('y', 0), 1.] for v in points])
    a = (inverse @ a.T).T
    a = a[:, :2] / a[:, 2:]
    if not np.isfinite(a).all():
        raise ValueError('nonfinite geometry')
    return [float(a[:, 0].min()), float(a[:, 1].min()), float(a[:, 0].max()), float(a[:, 1].max())]


def overlap(a, b):
    if a is None or b is None:
        return 0., 0.
    w = max(0., min(a[2], b[2])-max(a[0], b[0]))
    h = max(0., min(a[3], b[3])-max(a[1], b[1]))
    aa = max(0., a[2]-a[0])*max(0., a[3]-a[1])
    bb = max(0., b[2]-b[0])*max(0., b[3]-b[1])
    return w*h/max(1e-12, aa+bb-w*h), h/max(1e-12, min(a[3]-a[1], b[3]-b[1]))


def page_tokens(document, native_size):
    page = document['pages'][0]
    inv, returned = inverse_frame(page, native_size)
    text = document['text']
    tokens = []
    for i, node in enumerate(page.get('tokens', [])):
        ss = spans(node)
        tokens.append(dict(token_id=i, spans=ss, text=''.join(text[a:b] for a, b in ss),
                           bbox=box(node, inv, returned), confidence=node['layout'].get('confidence', 0.)))
    return tokens, inv, returned


def assemble_line(document, line_index, tokens, *, iou_threshold=IOU_THRESHOLD):
    """Return fixed label, original tokens, retained tokens, and lossless audit."""
    line = document['pages'][0]['lines'][line_index]
    ss = spans(line)
    own = [t for t in tokens if t['spans'] and all(any(a <= x < y <= b for a, b in ss) for x, y in t['spans'])]
    def count(t):
        return sum(c.isalnum() for c in ud.normalize('NFD', t['text']))
    def compatible(a, b):
        from difflib import SequenceMatcher
        base = lambda s: ''.join(c for c in ud.normalize('NFD', s.casefold()) if c.isalnum())
        sa, sb = base(a['text']), base(b['text'])
        return sa in sb or sb in sa or SequenceMatcher(None, sa, sb, autojunk=False).ratio() >= .40
    def conflict(a, b):
        # Letter-vs-punctuation overlap is normal in tight printing. Punctuation
        # can only compete with the identical punctuation, never another glyph.
        if not count(a) or not count(b):
            if a['text'].strip() != b['text'].strip():
                return False
        iou, vertical = overlap(a['bbox'], b['bbox'])
        if not a['bbox'] or not b['bbox']:
            return False
        ah, bh = a['bbox'][3]-a['bbox'][1], b['bbox'][3]-b['bbox'][1]
        aw, bw = a['bbox'][2]-a['bbox'][0], b['bbox'][2]-b['bbox'][0]
        shared = max(0., min(a['bbox'][2], b['bbox'][2])-max(a['bbox'][0], b['bbox'][0]))
        separation = abs(sum(a['bbox'][1::2])-sum(b['bbox'][1::2]))/2
        return iou > iou_threshold and vertical >= VERTICAL_OVERLAP and separation <= CENTER_SEPARATION*min(ah, bh) and shared/max(1e-12,min(aw,bw)) >= HORIZONTAL_OVERLAP
    graph = {i: set() for i in range(len(own))}
    for i, a in enumerate(own):
        for j in range(i):
            if conflict(a, own[j]):
                graph[i].add(j)
                graph[j].add(i)
    # Exact maximum-weight independent set within each small overlap component.
    # No text equality or dictionary is used for word suppression.
    from functools import lru_cache
    # Identical punctuation has no alternative spelling to choose; keep the
    # earliest anchor on an equal-weight tie to preserve surrounding spacing.
    weights = [count(t)*max(.01, t['confidence']) if count(t) else .1 for t in own]
    @lru_cache(None)
    def choose(available):
        if not available:
            return 0., ()
        i = max(available, key=lambda j: len(graph[j] & set(available)))
        without = choose(tuple(j for j in available if j != i))
        score, selected = choose(tuple(j for j in available if j != i and j not in graph[i]))
        with_i = score+weights[i], tuple(sorted(selected+(i,)))
        return with_i if with_i[0] > without[0]+1e-12 or (abs(with_i[0]-without[0]) <= 1e-12 and with_i[1] < without[1]) else without
    kept_indices, visited = set(), set()
    for i in graph:
        if i in visited:
            continue
        component, todo = set(), [i]
        while todo:
            j = todo.pop()
            if j not in component:
                component.add(j)
                todo.extend(graph[j]-component)
        visited.update(component)
        if any(compatible(own[j], own[k]) for j in component for k in graph[j] & component):
            kept_indices.update(choose(tuple(sorted(component)))[1])
        else:
            kept_indices.update(component)
    kept = [t for i, t in enumerate(own) if i in kept_indices]
    drops = []
    for i, token in enumerate(own):
        if i in kept_indices:
            continue
        hits = [(overlap(token['bbox'], own[j]['bbox'])[0], own[j]) for j in graph[i] & kept_indices]
        assert hits, 'every suppressed token must overlap a retained token'
        iou, winner = max(hits, key=lambda x: x[0])
        drops.append(dict(dropped_token_id=token['token_id'], kept_token_id=winner['token_id'],
                          competing_kept_ids=[k['token_id'] for _, k in hits],
                          iou=iou, dropped_text=token['text'], kept_text=winner['text'],
                          dropped_bbox=token['bbox'], kept_bbox=winner['bbox']))
    removed = {i for d in drops for t in own if t['token_id'] == d['dropped_token_id']
               for a, b in t['spans'] for i in range(a, b)}
    original = ''.join(document['text'][a:b] for a, b in ss)
    # Preserve whitespace from suppressed punctuation: deleting a duplicated comma
    # must not join the surviving words on either side of its anchor.
    punctuation_space = {i for d in drops for t in own if t['token_id'] == d['dropped_token_id'] and not count(t)
                         for a, b in t['spans'] for i in range(a, b) if document['text'][i].isspace()}
    fixed = ''.join(document['text'][i] for a, b in ss for i in range(a, b)
                    if i not in removed or i in punctuation_space)
    return dict(old_label=normalise(original), fixed_label=normalise(fixed),
                tokens=own, kept_tokens=sorted(kept, key=lambda t: t['token_id']), drops=drops,
                line_index=line_index, line_spans=ss, changed=normalise(original) != normalise(fixed))
