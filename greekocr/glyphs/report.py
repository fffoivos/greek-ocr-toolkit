"""JSON-ready per-line records (skew line, cut-offs, letters with ink scores) for review pages, with a document prior.

The document prior: a crop whose letters are mostly clipped cannot measure its own x-height, so it borrows the median
x-height of complete crops from the same document (line ids are `s2-<document>-p<page>-l<line>`).
"""
from __future__ import annotations

import base64
import io
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
from PIL import Image

from greekocr.glyphs.baseline import skew_line, text_lines
from greekocr.glyphs.columns import column_segments
from greekocr.glyphs.components import LineGlyphs, line_glyphs
from greekocr.glyphs.ink import FAINT, ink_profile
from greekocr.glyphs.letters import letter_boxes
from greekocr.types import PathLike

__all__ = ['clipped_fraction', 'document_of', 'document_priors', 'line_record']

LINE_ID = re.compile(r'((?:s2|an)-[0-9a-f]+)-p(\d+)-l(\d+)')   # s2: Vouli; an: Anemi


def document_of(name: str) -> str | None:
    m = LINE_ID.search(name)
    return m.group(1) if m else None


def clipped_fraction(glyphs: LineGlyphs) -> float:
    """Share of letter boxes whose ink touches the top or bottom crop edge."""
    boxes = letter_boxes(glyphs)
    if not boxes:
        return 1.0
    return sum(b.y0 == 0 or b.y1 == glyphs.height for b in boxes) / len(boxes)


def _complete(glyphs: LineGlyphs) -> bool:
    return (glyphs.band.xh_source in ('free_letters', 'substantial_letters') and glyphs.band.n_support >= 15
            and clipped_fraction(glyphs) < .3)


def document_priors(paths: Iterable[PathLike]) -> dict[str, dict[str, float]]:
    """Median x-height per document over its complete crops: {document: {'xh': .., 'n': ..}}."""
    per: dict[str, list[float]] = {}
    for p in paths:
        doc = document_of(Path(p).name)
        if not doc:
            continue
        g = line_glyphs(Image.open(p))
        if _complete(g):
            per.setdefault(doc, []).append(g.band.xh)
    return {d: {'xh': float(np.median(v)), 'n': len(v)} for d, v in per.items()}


def needs_prior(glyphs: LineGlyphs) -> bool:
    return glyphs.band.n_support < 8 or clipped_fraction(glyphs) >= .35


def _png(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.convert('L').save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def _sample(values: np.ndarray, step: int) -> list[float]:
    idx = list(range(0, len(values), step)) + [len(values) - 1]
    return [round(float(values[i]), 2) for i in idx]


def _segment_record(g: LineGlyphs, x_offset: int, step: int) -> dict[str, Any]:
    """Everything measured for one column segment, in the segment's own coordinates (x_offset into the crop)."""
    boxes = letter_boxes(g)
    sk = skew_line(g, boxes)
    ink = ink_profile(g, boxes)
    lines = text_lines(g)
    return dict(
        x_offset=x_offset, width=g.width,
        xh=round(g.band.xh, 1), xh_source=g.band.xh_source,
        angle_deg=sk.angle_deg, trail_px=sk.trail_px, degree=sk.degree, confidence=sk.confidence,
        n_support=sk.n_support, residual_px=sk.residual_px, support_x=[round(v) for v in sk.support_x],
        baseline=_sample(sk.baseline, step), meanline=_sample(sk.meanline, step), visible=_sample(sk.visible, step),
        crossings=[dict(x=round(c.x), line=c.line, edge=c.edge, meaning=c.meaning) for c in sk.crossings],
        cut_spans=[dict(x0=s.x0, x1=s.x1, edge=s.edge, min_visible=s.min_visible) for s in sk.cut_spans],
        cut_letters=[dict(x0=c.x0, x1=c.x1, edge=c.edge, body_cut=c.body_cut, touches=c.touches)
                     for c in sk.cut_letters],
        letters=[dict(x0=l.x0, x1=l.x1, y0=l.y0, y1=l.y1, score=l.score, state=l.state, pieces=l.pieces,
                      merged=l.merged, contrast=l.contrast) for l in ink.letters],
        marks=[[c.x0, c.y0, c.x1, c.y1] for c in g.components if c.role == 'mark'],
        n_broken=sum(l.state == 'broken' for l in ink.letters), n_faint=sum(l.state == 'faint' for l in ink.letters),
        n_merged=sum(l.state == 'merged' for l in ink.letters),
        double_line=sk.double_line,
        lines=[dict(side=t.side, shift_xh=t.shift_xh, x0=t.x0, x1=t.x1, votes=t.votes, visible=t.visible,
                    kind='main' if t.side == 'main' else ('full' if t.visible >= .5 else 'edges'),
                    ascender=_sample(t.ascender, step), mean=_sample(t.mean, step), base=_sample(t.base, step),
                    descender=_sample(t.descender, step)) for t in lines],
    )


def line_record(path: PathLike, *, priors: Mapping[str, Mapping[str, float]] | None = None,
                label: str = '', step: int = 4) -> dict[str, Any]:
    """JSON-ready record of a crop: one entry per column segment (columns split at rules / unaligned wide gaps), each
    with its skew, bends, guide lines, neighbour lines, cut-offs and letter states in LOCAL coordinates (x_offset into
    the crop). Top-level measurements repeat the main segment (most baseline support; `main_segment`, `main_x_offset`);
    top-level letters / cut_spans / cut_letters / lines are flattened in CROP coordinates with a `segment` field
    (guide-line arrays stay in the segments)."""
    path = Path(path)
    image = Image.open(path)
    probe = line_glyphs(image)
    prior_used = None
    doc = document_of(path.name)
    kw: dict[str, Any] = {}
    if priors and doc in priors and needs_prior(probe):
        prior_used = dict(priors[doc])
        kw['xh_prior'] = prior_used['xh']
    segs = [sg for sg in column_segments(image, **kw) if sg.glyphs is not None]
    records = [_segment_record(sg.glyphs, sg.x0, step) for sg in segs]
    if records:
        main_i = max(range(len(records)), key=lambda i: records[i]['n_support'])
        main = records[main_i]
    else:
        main_i, main = 0, _segment_record(probe, 0, step)
    kinds = [l['kind'] for r in records for l in r['lines']]
    out = dict(id=path.stem, label=label, document=doc, width=image.width, height=image.height, png=_png(image),
               prior=prior_used, step=step, segments=records or [main], n_columns=max(1, len(records)),
               n_lines=len(kinds), n_full_lines=kinds.count('main') + kinds.count('full'), n_edge_lines=kinds.count('edges'),
               faint_threshold=FAINT)
    for k in ('xh', 'xh_source', 'angle_deg', 'trail_px', 'degree', 'confidence', 'n_support', 'residual_px',
              'support_x', 'double_line'):
        out[k] = main[k]
    for k in ('n_broken', 'n_faint', 'n_merged'):
        out[k] = sum(r[k] for r in records) if records else main[k]
    # flattened spatial entries are in CROP coordinates and name their segment (CP-G3 F3); the nested segment
    # records keep local coordinates plus x_offset
    def shifted(entry: dict, k: int, off: int) -> dict:
        e = dict(entry, segment=k)
        for key in ('x0', 'x1', 'x'):
            if key in e:
                e[key] = e[key] + off
        return e
    out['main_segment'] = main_i
    out['main_x_offset'] = main['x_offset']
    out['support_x'] = [v + main['x_offset'] for v in main['support_x']]
    out['cut_spans'] = [shifted(c, k, r['x_offset']) for k, r in enumerate(records) for c in r['cut_spans']]
    out['cut_letters'] = [shifted(c, k, r['x_offset']) for k, r in enumerate(records) for c in r['cut_letters']]
    out['letters'] = [shifted(l, k, r['x_offset']) for k, r in enumerate(records) for l in r['letters']]
    out['lines'] = [{key: val for key, val in shifted(l, k, r['x_offset']).items()
                     if key not in ('ascender', 'mean', 'base', 'descender')} for k, r in enumerate(records) for l in r['lines']]
    return out
