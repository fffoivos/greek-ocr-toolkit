"""Shared real/synthetic strata and floor-constrained per-line sampling weights."""
from __future__ import annotations

from collections import Counter
import math
from typing import Any, Iterable, Mapping, TypeAlias

StratumKey: TypeAlias = tuple[str | None, bool | None, str | None, str, str, str, str | None]
__all__ = ['stratum_key', 'stratum_counts', 'sampling_weights']


def _bucket(value: Any, thresholds: tuple[float, ...], labels: tuple[str, ...]) -> str:
    if value is None:
        return 'unknown'
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('stratification values must be finite numbers or null')
    return labels[sum(value >= threshold for threshold in thresholds)]


def stratum_key(record: Mapping[str, Any]) -> StratumKey:
    """Return script/polytonic/document/year/contrast/ink/font axes with explicit unknown bins."""
    features = record.get('line_features', record)
    source = record.get('source_metadata', record)
    density = features.get('polytonic_mark_density')
    poly = None
    if density is not None:
        _bucket(density, (), ('valid',))
        if density < 0:
            raise ValueError('polytonic density must be nonnegative')
        poly = density > 0
    if poly is None and features.get('script_class') == 'greek_poly':
        poly = True
    elif poly is None and features.get('script_class') == 'greek_mono':
        poly = False
    return (features.get('script_class'), poly, source.get('doc_type'),
            _bucket(source.get('year'), (1800, 1900, 1950, 2000), ('pre1800', '1800_1899', '1900_1949', '1950_1999', '2000_plus')),
            _bucket(features.get('contrast'), (.2, .5), ('low', 'medium', 'high')),
            _bucket(features.get('ink_coverage'), (.05, .2), ('sparse', 'medium', 'dense')),
            features.get('font_style'))


def stratum_counts(records: Iterable[Mapping[str, Any]]) -> dict[StratumKey, int]:
    """Count existing supply only; missing strata are never fabricated."""
    return dict(Counter(stratum_key(row) for row in records))


def sampling_weights(records: Iterable[Mapping[str, Any]], *, floor: float = 0.0,
                     floors: Mapping[StratumKey, float] | None = None,
                     targets: Mapping[StratumKey, float] | None = None) -> list[float]:
    """Return normalized per-record probabilities with guaranteed per-stratum mass floors."""
    rows = list(records)
    keys = [stratum_key(row) for row in rows]
    counts = Counter(keys)
    if not math.isfinite(floor) or floor < 0:
        raise ValueError('floor must be finite and nonnegative')
    for values in (floors, targets):
        if values is not None:
            if any(not math.isfinite(v) or v < 0 for v in values.values()):
                raise ValueError('floors/targets must be finite and nonnegative')
            if any(k not in counts and v > 0 for k, v in values.items()):
                raise ValueError('positive floor/target requests an absent stratum')
    if not rows:
        return []
    minimum = {k: max(floor, (floors or {}).get(k, 0.)) for k in counts}
    if math.fsum(minimum.values()) > 1:
        raise ValueError('stratum floors sum to more than one')
    scores = {k: 1.0 if targets is None else targets.get(k, 0.) for k in counts}
    # Normalize before summing so very large finite relative targets cannot
    # overflow to infinity and silently produce zero/NaN probabilities.
    scale = max(scores.values())
    if scale:
        scores = {k: value / scale for k, value in scores.items()}
    mass: dict[StratumKey, float] = {}
    active = list(counts)
    remaining = 1.0
    # Water filling preserves target ratios among unbound strata while fixing
    # each undersupplied target to its requested probability floor.
    while active:
        total = math.fsum(scores[k] for k in active)
        proposed = {k: remaining * scores[k] / total if total else remaining / len(active) for k in active}
        bound = [k for k in active if proposed[k] < minimum[k]]
        if not bound:
            mass.update(proposed)
            break
        for k in bound:
            mass[k] = minimum[k]
        remaining = max(0., 1 - math.fsum(mass.values()))
        active = [k for k in active if k not in bound]
    return [mass[k] / counts[k] for k in keys]
