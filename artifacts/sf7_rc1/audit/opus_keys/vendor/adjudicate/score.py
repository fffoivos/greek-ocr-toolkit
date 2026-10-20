"""One offline statistical implementation; cluster estimator ported from S8."""
from __future__ import annotations
import math
from typing import Callable
import numpy as np
from scipy.stats import beta

__all__ = ['wilson', 'score', 'clopper_pearson_lb95', 'named_slices']


def wilson(p: float, n: float) -> list[float] | None:
    """Return the two-sided Wilson 95% interval using z=1.959963984540054."""
    if not math.isfinite(p) or not math.isfinite(n) or not 0 <= p <= 1 or n < 0:
        raise ValueError('invalid proportion/effective n')
    if not n:
        return None
    z = 1.959963984540054
    d = 1 + z*z/n
    mid = (p + z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0., mid-half), min(1., mid+half)]


def clopper_pearson_lb95(successes: int, total: int) -> float:
    """Return the one-sided exact 95% lower bound (zero for no successes/trials)."""
    if type(successes) is not int or type(total) is not int or not 0 <= successes <= total:
        raise ValueError('invalid binomial counts')
    return float(beta.ppf(.05, successes, total-successes+1)) if successes else 0.


def score(rows: list[dict], numer: Callable[[dict], float], denom: Callable[[dict], float], seed: int = 20261017, *, replicates: int = 4000) -> dict:
    """S8 weighted event estimate, document/line bootstrap and Wilson-Kish fallback.

    Rows carry weight and line_id; document defaults to line_id before '-p'.
    Explicit document overrides that convention. Fixed inclusion weights persist
    through resampling. Boundary Wilson ignores clustering and is diagnostic.
    """
    if type(replicates) is not int or replicates <= 0:
        raise ValueError('positive bootstrap replicate count required')
    if not rows:
        return dict(value=None, raw_num=0, raw_den=0, weighted_num=0., weighted_den=0., ci=None)
    w = np.array([r['weight'] for r in rows], dtype=float)
    a = np.array([numer(r) for r in rows], dtype=float)
    b = np.array([denom(r) for r in rows], dtype=float)
    if not (np.isfinite(w).all() and np.isfinite(a).all() and np.isfinite(b).all()) or (w <= 0).any() or (a < 0).any() or (b < a).any():
        raise ValueError('finite positive weights and 0 <= numerator <= denominator required')
    num, den = float(w@a), float(w@b)
    out = dict(raw_num=int(a.sum()), raw_den=int(b.sum()), weighted_num=num, weighted_den=den,
               value=num/den if den else None, ci=None)
    if not den:
        return out
    neff = den*den / float((w*w)@b)
    out.update(effective_event_n=neff, wilson95=wilson(num/den, neff))
    for level in ('document', 'line'):
        def cluster(row):
            return row.get('document', row['line_id'].split('-p')[0]) if level == 'document' else row['line_id']
        ids = sorted({cluster(r) for r in rows})
        ix = {k: i for i, k in enumerate(ids)}
        matrix = np.zeros((len(ids), 2))
        for r, wa, wb in zip(rows, w*a, w*b):
            matrix[ix[cluster(r)]] += (wa, wb)
        rng = np.random.default_rng(seed)
        counts = rng.multinomial(len(ids), np.full(len(ids), 1/len(ids)), size=replicates)
        totals = counts @ matrix
        valid = totals[:, 1] > 0
        ratios = totals[valid, 0] / totals[valid, 1]
        out[level+'_clusters'] = len(ids)
        out[level+'_bootstrap_valid'] = int(valid.sum())
        out[level+'_bootstrap95'] = np.quantile(ratios, [.025, .975]).tolist() if len(ratios) else None
    interval = out['document_bootstrap95']
    degenerate = interval is None or interval[1]-interval[0] < 1e-12
    out.update(ci=out['wilson95'] if degenerate else interval, ci_method='Wilson-Kish' if degenerate else 'document-bootstrap')
    return out


# Slice predicates operate on truth-side context only, never prediction text.
# Missing context does not become a negative/positive stratum by inference.
import unicodedata as _ud
from types import MappingProxyType as _MappingProxyType


def _base(row: dict) -> str:
    return ''.join(c for c in _ud.normalize('NFD',row.get('base','')) if not _ud.combining(c))


def _word(row: dict) -> str:
    return ''.join(c for c in _ud.normalize('NFD',row.get('word','')) if c.isalpha())


SLICE_REGISTRY = _MappingProxyType({
    'capital': lambda r: _base(r).isupper(),
    'ALL-CAPS': lambda r: len(_word(r))>1 and _word(r).isupper(),
    'numeral': lambda r: bool(r.get('numeral',False)) or any(c in r.get('word','') for c in ('\u0374','\u02b9','\u2032')),
    'ο-monotonic': lambda r: _base(r)=='ο' or _word(r) in ('ο','οι') or r.get('orthography')=='monotonic',
    'subscript': lambda r: _base(r).lower() in ('α','η','ω') or bool((r.get('truth') or [0]*4)[3]) or '\u0345' in _ud.normalize('NFD',r.get('word','')),
    'exact-name': lambda r: r.get('exact_name') is True or any(v is not None and v != 0 and h not in r.get('unknown',[]) for h,v in zip(('breathing','accent','dialytika'),(r.get('truth') or [0]*4)[:3])),
})


def named_slices(rows: list[dict]) -> dict[str, list[dict]]:
    """Select overlapping R2 truth-context slices with an immutable registry.

    Rows use base, word (printed token), orthography, numeral, exact_name and
    truth[breathing, accent, diaeresis, subscript]. Numeral/monotonic/name context
    may be annotated explicitly. Subscript includes bare α/η/ω negatives;
    exact-name means named MARK contrasts, including any known positive accent,
    breathing or dialytika, not proper nouns. ο/οι and annotated monotonic
    contexts overlap. Missing word context is excluded, never guessed.
    """
    return {name:[r for r in rows if predicate(r)] for name,predicate in SLICE_REGISTRY.items()}
