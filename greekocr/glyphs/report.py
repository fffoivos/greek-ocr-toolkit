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

from greekocr.glyphs.baseline import skew_line
from greekocr.glyphs.components import LineGlyphs, line_glyphs
from greekocr.glyphs.ink import FAINT, ink_profile
from greekocr.glyphs.letters import letter_boxes
from greekocr.types import PathLike

__all__ = ['clipped_fraction', 'document_of', 'document_priors', 'line_record']

LINE_ID = re.compile(r'(s2-[0-9a-f]+)-p(\d+)-l(\d+)')


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


def line_record(path: PathLike, *, priors: Mapping[str, Mapping[str, float]] | None = None,
                label: str = '', step: int = 4) -> dict[str, Any]:
    path = Path(path)
    image = Image.open(path)
    g = line_glyphs(image)
    prior_used = None
    doc = document_of(path.name)
    if priors and doc in priors and needs_prior(g):
        prior_used = dict(priors[doc])
        g = line_glyphs(image, xh_prior=prior_used['xh'])
    boxes = letter_boxes(g)
    sk = skew_line(g, boxes)
    ink = ink_profile(g, boxes)
    return dict(
        id=path.stem, label=label, document=doc, width=g.width, height=g.height, png=_png(image),
        xh=round(g.band.xh, 1), xh_source=g.band.xh_source, prior=prior_used,
        angle_deg=sk.angle_deg, trail_px=sk.trail_px, degree=sk.degree, confidence=sk.confidence,
        n_support=sk.n_support, residual_px=sk.residual_px, support_x=[round(v) for v in sk.support_x],
        step=step, baseline=_sample(sk.baseline, step), meanline=_sample(sk.meanline, step),
        visible=_sample(sk.visible, step),
        crossings=[dict(x=round(c.x), line=c.line, edge=c.edge, meaning=c.meaning) for c in sk.crossings],
        cut_spans=[dict(x0=s.x0, x1=s.x1, edge=s.edge, min_visible=s.min_visible) for s in sk.cut_spans],
        cut_letters=[dict(x0=c.x0, x1=c.x1, edge=c.edge, body_cut=c.body_cut, touches=c.touches)
                     for c in sk.cut_letters],
        letters=[dict(x0=l.x0, x1=l.x1, y0=l.y0, y1=l.y1, score=l.score, state=l.state, pieces=l.pieces,
                      merged=l.merged, contrast=l.contrast) for l in ink.letters],
        marks=[[c.x0, c.y0, c.x1, c.y1] for c in g.components if c.role == 'mark'],
        n_broken=sum(l.state == 'broken' for l in ink.letters), n_faint=sum(l.state == 'faint' for l in ink.letters),
        n_merged=sum(l.state == 'merged' for l in ink.letters), faint_threshold=FAINT,
        double_line=sk.double_line,
        second=None if sk.second is None else dict(support=sk.second.support, ratio=sk.second.ratio,
                                                    offset_xh=sk.second.offset_xh, visible=sk.second.visible,
                                                    baseline=_sample(sk.second.baseline, step)),
    )
