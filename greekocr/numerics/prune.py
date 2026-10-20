"""Conservative component-geometry screen; no glyph classification or fitting."""
import hashlib

AUDIT_SEED = '20261017:N1Tb:geometry-audit'


def has_gap_component(slot):
    """Keep any component intersecting positive-width gap outside flank boxes.

    Crossing components count too: their overhang may be a mark. Bounding-box
    intersection is conservative, and may retain extra slots rather than drop ink.
    The exact gap is between the digit-box edges, so digit boxes cover none of it.
    """
    g = slot['geometry']
    if g['geom_status'] != 'ok':
        raise ValueError('geometry must be ok')
    x0, x1 = g['gap']
    return x1 > x0 and any(c['bbox'][2] > x0 and c['bbox'][0] < x1
                         for c in slot['measurements']['components'])


def prune(slots, audit_size=30):
    records = []
    for slot in slots:
        if slot['geometry']['geom_status'] != 'ok': reason = 'geom-fail'
        elif slot['glyph'] != '': reason = 'google-mark'
        elif has_gap_component(slot): reason = 'ink-only'
        else: reason = 'geometry-only'
        records.append(dict(slot, read_reason=reason))
    pool = [s for s in records if s['read_reason']=='geometry-only']
    audit = sorted(pool, key=lambda s: hashlib.sha256((AUDIT_SEED+':'+s['slot_id']).encode()).hexdigest())[:audit_size]
    for slot in audit: slot['read_reason'] = 'audit'
    return records
