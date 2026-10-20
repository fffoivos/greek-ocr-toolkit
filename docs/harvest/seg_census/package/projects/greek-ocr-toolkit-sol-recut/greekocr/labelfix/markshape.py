"""Mark-shape classifier for the ink-decisive variant (pass 4).

For the vowel the CTC alignment locates, the ink evidence (`ink.mark_evidence`) is turned into a
fixed feature vector (blob counts, sizes, principal-axis slope, elongation, hook direction, skew,
position) and a softmax (multinomial logistic) classifier predicts the vowel's mark set, e.g.
`psili+acute`, `dasia`, `circumflex`, `acute+subscript`, `dialytika`, `none`.

Training data: vowels of the three-way Wikisource lines in words where Google = human = model
(unambiguous marks). Book-separated: fit on the dev books, calibrate on the held-out books; the
confidence threshold `tau` is the smallest probability at which the held-out predictions are at
least 99 % correct (reported per mark class as well).

Use: a lexicon-NEUTRAL candidate (both forms attested, or both unattested) is `ink_decisive` when
the classifier gives the model's mark set probability >= tau, the Google mark set is not the
prediction, and the ordinary ink conjunction and abstentions hold. It is a separate column,
never folded into `accept`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from .ink import MarkEvidence
from .text import ACCENTS, BREATHINGS, DIALYTIKA, SUBSCRIPT, ACUTE, GRAVE, CIRCUMFLEX, OTHER_MARKS, clusters, nfd

FEATURES = ['n_above', 'n_below', 'width_above',
            'b1_w', 'b1_h', 'b1_area', 'b1_angle', 'b1_elong', 'b1_hook', 'b1_skew', 'b1_top', 'b1_cx', 'b1_gap', 'b1_aspect',
            'b2_w', 'b2_h', 'b2_area', 'b2_angle', 'b2_elong', 'b2_hook', 'b2_skew', 'b2_top', 'b2_cx', 'b2_gap', 'b2_aspect',
            'bl_w', 'bl_h', 'bl_area', 'bl_cx', 'bl_gap', 'merged_wide'] + \
           [f'g1_{i}' for i in range(64)] + [f'g2_{i}' for i in range(64)]


def mark_class(marks: str) -> str | None:
    """Class string of a cluster's combining marks; None for marks outside the scheme."""
    parts = []
    if any(m in OTHER_MARKS for m in marks):
        return None
    if '̓' in marks:
        parts.append('psili')
    if '̔' in marks:
        parts.append('dasia')
    if any(m in DIALYTIKA for m in marks):
        parts.append('dialytika')
    acc = [m for m in marks if m in ACCENTS]
    if len(acc) > 1:
        return None
    if acc:
        parts.append({ACUTE: 'acute', GRAVE: 'grave', CIRCUMFLEX: 'circumflex'}[acc[0]])
    if any(m in SUBSCRIPT for m in marks):
        parts.append('subscript')
    return '+'.join(parts) if parts else 'none'


def features(ev: MarkEvidence) -> list[float]:
    xh = max(ev.xh, 1.0)
    body_c = (ev.body[0] + ev.body[1]) / 2 if ev.body else (ev.window[0] + ev.window[1]) / 2
    above = sorted(ev.above, key=lambda b: b.x0)[:2]
    f = [float(len(ev.above)), float(len(ev.below)),
         (max(b.x1 for b in ev.above) - min(b.x0 for b in ev.above)) / xh if ev.above else 0.0]
    for k in range(2):
        if k < len(above):
            b = above[k]
            f += [b.w / xh, b.h / xh, b.area / (xh * xh), b.angle_deg / 90.0, min(b.elongation, 6.0) / 6.0, b.hook, b.skew,
                  b.top_heavy, (b.cx - body_c) / xh, (ev.meanline - b.y1) / xh, b.w / max(b.h, 1)]
        else:
            f += [0.0] * 11
    if ev.below:
        b = ev.below[0]
        f += [b.w / xh, b.h / xh, b.area / (xh * xh), (b.cx - body_c) / xh, (b.y0 - ev.baseline) / xh]
    else:
        f += [0.0] * 5
    f.append(1.0 if any(b.w > 0.5 * xh for b in ev.above) else 0.0)
    for k in range(2):
        g = list(above[k].grid) if k < len(above) and len(above[k].grid) == 64 else [0.0] * 64
        f += g
    return f


class SoftmaxModel:
    """Multinomial logistic regression on standardised features (numpy, L2-regularised)."""

    def __init__(self, classes: list[str], mean, std, W, b, tau: float = 1.0, meta: dict | None = None):
        self.classes = list(classes)
        self.mean = np.asarray(mean, float)
        self.std = np.asarray(std, float)
        self.W = np.asarray(W, float)
        self.b = np.asarray(b, float)
        self.tau = float(tau)
        self.meta = meta or {}

    def probs(self, X) -> np.ndarray:
        X = (np.asarray(X, float) - self.mean) / self.std
        z = X @ self.W + self.b
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def predict(self, x: list[float]) -> tuple[str, float, dict]:
        p = self.probs(np.asarray([x]))[0]
        k = int(p.argmax())
        return self.classes[k], float(p[k]), {c: float(p[i]) for i, c in enumerate(self.classes)}

    def save(self, path: Path) -> None:
        Path(path).write_text(json.dumps(dict(classes=self.classes, mean=self.mean.tolist(), std=self.std.tolist(),
                                              W=self.W.tolist(), b=self.b.tolist(), tau=self.tau, features=FEATURES,
                                              meta=self.meta), indent=1))

    @classmethod
    def load(cls, path: Path) -> 'SoftmaxModel':
        d = json.loads(Path(path).read_text())
        return cls(d['classes'], d['mean'], d['std'], d['W'], d['b'], d['tau'], d.get('meta'))


class MLPModel(SoftmaxModel):
    """One hidden layer (tanh) on standardised features; same interface as SoftmaxModel."""

    def __init__(self, classes, mean, std, W1, b1, W2, b2, tau: float = 1.0, meta=None):
        super().__init__(classes, mean, std, W2, b2, tau, meta)
        self.W1 = np.asarray(W1, float)
        self.b1 = np.asarray(b1, float)

    def probs(self, X) -> np.ndarray:
        X = (np.asarray(X, float) - self.mean) / self.std
        H = np.tanh(X @ self.W1 + self.b1)
        z = H @ self.W + self.b
        z -= z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def save(self, path: Path) -> None:
        Path(path).write_text(json.dumps(dict(kind='mlp', classes=self.classes, mean=self.mean.tolist(), std=self.std.tolist(),
                                              W1=self.W1.tolist(), b1=self.b1.tolist(), W=self.W.tolist(), b=self.b.tolist(),
                                              tau=self.tau, features=FEATURES, meta=self.meta)))

    @classmethod
    def load(cls, path: Path) -> 'MLPModel':
        d = json.loads(Path(path).read_text())
        return cls(d['classes'], d['mean'], d['std'], d['W1'], d['b1'], d['W'], d['b'], d['tau'], d.get('meta'))


def load_model(path: Path):
    d = json.loads(Path(path).read_text())
    return MLPModel.load(path) if d.get('kind') == 'mlp' else SoftmaxModel.load(path)


def fit_mlp(X, y, classes: list[str], hidden: int = 96, l2: float = 1e-4, epochs: int = 400, lr: float = 0.003,
            seed: int = 0) -> MLPModel:
    """Adam-trained one-hidden-layer network with class-balanced loss; small enough for a few thousand samples."""
    X = np.asarray(X, float)
    idx = {c: i for i, c in enumerate(classes)}
    Y = np.zeros((len(y), len(classes)))
    for i, c in enumerate(y):
        Y[i, idx[c]] = 1.0
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0
    Xs = (X - mean) / std
    rng = np.random.default_rng(seed)
    d, k = X.shape[1], len(classes)
    W1 = rng.normal(0, 1 / math.sqrt(d), (d, hidden))
    b1 = np.zeros(hidden)
    W2 = rng.normal(0, 1 / math.sqrt(hidden), (hidden, k))
    b2 = np.zeros(k)
    freq = Y.sum(axis=0)
    wts = len(y) / (k * np.maximum(freq, 1.0))
    sw = (Y * np.sqrt(wts)).sum(axis=1)
    sw = sw / sw.mean()
    params = [W1, b1, W2, b2]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    n = len(y)
    bs = 128
    t = 0
    for ep in range(epochs):
        order = rng.permutation(n)
        for s0 in range(0, n, bs):
            sel = order[s0:s0 + bs]
            xb, yb, wb = Xs[sel], Y[sel], sw[sel]
            H = np.tanh(xb @ W1 + b1)
            z = H @ W2 + b2
            z -= z.max(axis=1, keepdims=True)
            P = np.exp(z)
            P /= P.sum(axis=1, keepdims=True)
            G = (P - yb) * wb[:, None] / len(sel)
            gW2 = H.T @ G + l2 * W2
            gb2 = G.sum(axis=0)
            dH = (G @ W2.T) * (1 - H * H)
            gW1 = xb.T @ dH + l2 * W1
            gb1 = dH.sum(axis=0)
            t += 1
            for i, (p, g) in enumerate(zip(params, [gW1, gb1, gW2, gb2])):
                m[i] = 0.9 * m[i] + 0.1 * g
                v[i] = 0.999 * v[i] + 0.001 * g * g
                mh = m[i] / (1 - 0.9 ** t)
                vh = v[i] / (1 - 0.999 ** t)
                p -= lr * mh / (np.sqrt(vh) + 1e-8)
    return MLPModel(classes, mean, std, W1, b1, W2, b2)


def fit(X, y, classes: list[str], l2: float = 1e-3, epochs: int = 600, lr: float = 0.5, seed: int = 0) -> SoftmaxModel:
    X = np.asarray(X, float)
    idx = {c: i for i, c in enumerate(classes)}
    Y = np.zeros((len(y), len(classes)))
    for i, c in enumerate(y):
        Y[i, idx[c]] = 1.0
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0
    Xs = (X - mean) / std
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.01, (X.shape[1], len(classes)))
    b = np.zeros(len(classes))
    # class-balanced weights so rare marks (dialytika, subscript) are not drowned by 'none'
    freq = Y.sum(axis=0)
    wts = (len(y) / (len(classes) * np.maximum(freq, 1.0)))
    sw = (Y * wts).sum(axis=1)
    sw = sw / sw.mean()
    n = len(y)
    for _ in range(epochs):
        z = Xs @ W + b
        z -= z.max(axis=1, keepdims=True)
        P = np.exp(z)
        P /= P.sum(axis=1, keepdims=True)
        G = (P - Y) * sw[:, None] / n
        W -= lr * (Xs.T @ G + l2 * W)
        b -= lr * G.sum(axis=0)
    return SoftmaxModel(classes, mean, std, W, b)


def calibrate(model: SoftmaxModel, X, y, target: float = 0.99) -> dict:
    """Smallest tau such that predictions with p >= tau are >= `target` correct on (X, y); per-class detail."""
    P = model.probs(X)
    pred = P.argmax(axis=1)
    conf = P.max(axis=1)
    truth = np.asarray([model.classes.index(c) for c in y])
    out = dict(n=len(y), accuracy=float((pred == truth).mean()))
    best = None
    grid = list(np.arange(0.50, 0.99, 0.005)) + list(np.arange(0.99, 0.9951, 0.001)) + [0.996, 0.997, 0.998, 0.999, 0.9995, 0.9998]
    for tau in grid:
        sel = conf >= tau
        if sel.sum() == 0:
            continue
        prec = float((pred[sel] == truth[sel]).mean())
        if prec >= target:
            best = dict(tau=round(float(tau), 4), precision=prec, coverage=float(sel.mean()), n=int(sel.sum()))
            break
    out['threshold'] = best
    out['curve'] = [dict(tau=t, n=int((conf >= t).sum()), precision=float((pred[conf >= t] == truth[conf >= t]).mean()) if (conf >= t).any() else None)
                    for t in (0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 0.9995)]
    mark_none = model.classes.index('none') if 'none' in model.classes else -1
    both_marks = (truth != mark_none) & (pred != mark_none)
    out['marks_only'] = [dict(tau=t, n=int(((conf >= t) & both_marks).sum()),
                              precision=float((pred[(conf >= t) & both_marks] == truth[(conf >= t) & both_marks]).mean()) if ((conf >= t) & both_marks).any() else None)
                         for t in (0.95, 0.99, 0.995)]
    per = {}
    for i, c in enumerate(model.classes):
        m = truth == i
        if m.sum() == 0:
            continue
        sel = (pred == i) & (conf >= (best['tau'] if best else 1.0))
        per[c] = dict(n=int(m.sum()), recall=float((pred[m] == i).mean()),
                      precision_at_tau=float((truth[sel] == i).mean()) if sel.sum() else None, n_at_tau=int(sel.sum()))
    out['per_class'] = per
    return out
