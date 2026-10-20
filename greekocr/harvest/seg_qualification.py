"""Shared CP5/CP7 acceptance: resolved, passing composed witnesses.

Unknown orientation is allowed only by CP5c's orientation-only policy. Missing
structural/separator evidence is never a passing KEEP. The CP4c explicit
geometry-unavailable DROP policy remains a resolved policy loss, not detection.
"""

def composed_requirements(truth, composed, crossings):
    required = {r for r, t in truth.items() if t in ('keep', 'drop', 'challenge')}
    keeps = {r for r, t in truth.items() if t == 'keep'}
    positives = {r for r, t in truth.items() if t in ('drop', 'challenge')}
    return dict(
        union_resolved=bool(required) and all(
            composed.get(r, {}).get('drop') is not None for r in required),
        union_keep_preserved=bool(keeps) and all(
            composed.get(r, {}).get('drop') is False and
            composed[r].get('geometry_unavailable') is False for r in keeps),
        union_positives_caught=bool(positives) and all(
            composed.get(r, {}).get('drop') is True for r in positives),
        separator_coverage=bool(required) and all(
            crossings.get(r, {}).get('status') == 'measured' and
            crossings[r].get('drop') is not None
            for r in required if not composed.get(r, {}).get('geometry_unavailable')))
