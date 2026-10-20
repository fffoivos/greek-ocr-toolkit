"""Mark-shape classifier: features, training, calibration, and the ink-decisive rule variant."""
import numpy as np

from greekocr.labelfix.ink import Blob, MarkEvidence
from greekocr.labelfix.markshape import FEATURES, calibrate, features, fit, fit_mlp, mark_class
from greekocr.labelfix.rules import Candidate, InkSummary, decide
from tests.labelfix.test_rules import N, cand, ink


def blob(x0, y0, x1, y1, angle=0.0, elong=1.0, hook=0.0):
    b = Blob(x0, y0, x1, y1, (x1 - x0) * (y1 - y0) // 2, 'detached', angle, elong)
    b.hook = hook
    b.grid = tuple([0.5] * 64)
    return b


def test_feature_vector_matches_schema():
    ev = MarkEvidence([blob(10, 2, 16, 9, -60, 2.5)], [], (0, 30), 20.0, 12.0, 32.0, (8.0, 20.0), 'letter', 1)
    x = features(ev)
    assert len(x) == len(FEATURES) == 159
    assert x[0] == 1.0 and x[1] == 0.0 and x[FEATURES.index('b1_angle')] == -60 / 90


def test_mark_class_scheme():
    assert mark_class(N('ἅ')[1:]) == 'dasia+acute' and mark_class('') == 'none'
    assert mark_class(N('ᾠ')[1:]) == 'psili+subscript' and mark_class(N('ϊ')[1:]) == 'dialytika'
    assert mark_class('\u0304') is None


def _synthetic(n=600, seed=0):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for k in range(n):
        c = ['acute', 'grave', 'none'][k % 3]
        base = np.zeros(len(FEATURES))
        if c != 'none':
            base[0] = 1.0
            base[FEATURES.index('b1_angle')] = -0.7 if c == 'acute' else 0.7
            base[FEATURES.index('b1_elong')] = 0.5
        X.append(base + rng.normal(0, 0.05, len(FEATURES)))
        y.append(c)
    return X, y


def test_softmax_and_mlp_learn_a_separable_problem_and_calibrate():
    X, y = _synthetic()
    classes = ['acute', 'grave', 'none']
    for model in (fit(X, y, classes, epochs=300), fit_mlp(X, y, classes, epochs=40)):
        cal = calibrate(model, X, y)
        assert cal['accuracy'] > 0.98 and cal['threshold'] is not None
        pred, p, dist = model.predict(X[0])
        assert pred == 'acute' and p > 0.9 and abs(sum(dist.values()) - 1) < 1e-6


def test_ink_decisive_only_when_lexicon_neutral_and_shape_confident():
    # both forms attested -> lexicon neutral; ordinary rule rejects (both_attested)
    c = cand('βήμα', 'βῆμα', mf=400, gf=75, ink=ink(above=1))
    c.shape_pred, c.shape_prob, c.shape_tau, c.shape_google_prob = 'circumflex', 0.999, 0.998, 0.0005
    d = decide(c)
    assert not d.accept and d.lexicon_neutral and d.ink_decisive and 'shape=circumflex' in d.ink_decisive_reason
    c.shape_prob = 0.9
    assert not decide(c).ink_decisive
    c.shape_prob, c.shape_pred = 0.999, 'acute'          # the classifier reads Google's mark
    assert 'shape_predicts_acute' in decide(c).ink_decisive_reason
    # a breathing-kind change on a fused (sliced) mark is never decisive: the hook is truncated
    c = cand('ὁ', 'ὀ', mf=100, gf=100, ink=ink(above=1))
    c.ink.attached = True
    c.shape_pred, c.shape_prob, c.shape_tau = 'psili', 0.9999, 0.998
    assert decide(c).ink_decisive_reason == 'attached_breathing_not_decisive'
    # lexicon supports the model (Google unattested): accepted by the ordinary rule, variant not needed
    d = decide(cand('βήμα', 'βῆμα', mf=400, gf=0, ink=ink(above=1)))
    assert d.accept and not d.lexicon_neutral and not d.ink_decisive
    # lexicon contradicts (model unattested, Google attested): never ink-decisive
    c = cand('βήμα', 'βῆμα', mf=0, gf=75, ink=ink(above=1))
    c.shape_pred, c.shape_prob, c.shape_tau = 'circumflex', 0.999, 0.998
    assert not decide(c).lexicon_neutral and not decide(c).ink_decisive
