"""Geometry-only integration with original contour ancestry and retained ownership.

The caller owns separators. Optional scouts must describe the SAME original item
list and page; supplied scout cost belongs to the caller's shared timing receipt.
No B-removed polygon participates in ink conservation. This is the R3 geometry
operator, not a new acceptance rule or a detector for missing lines.
"""
from time import perf_counter
import numpy as np
from .contracts import bbox
from .geometry import line_axis
from .geometry_feature_paths import sparse, bands
from .geometry_feature_correct import retention, keep_nearby_ink
from ..layout_barriers.fast import scout


def correct_geometry(gray, pm, original_items, *, retained_source_indices=None,
                     rule_witness=None, geometry_scout=None):
    start = perf_counter()
    n = len(original_items)
    retained = list(range(n)) if retained_source_indices is None else list(retained_source_indices)
    if any(not isinstance(i, (int, np.integer)) or i < 0 or i >= n for i in retained):
        raise ValueError('Retained source indices must address original_items')
    if len(set(retained)) != len(retained):
        raise ValueError('Duplicate retained source index')
    retained = sorted(retained)
    provided_rule = rule_witness is not None
    provided_geometry = geometry_scout is not None
    if rule_witness is None:
        rule_witness, _ = scout(gray, original_items)
    if geometry_scout is None:
        geometry_scout = sparse(pm, original_items, (gray.shape[1], gray.shape[0]), 3)
    scout_s = perf_counter() - start
    working = [dict(original_items[i], source_ids=[int(i)]) for i in retained]
    positions = {source: i for i, source in enumerate(retained)}
    decisions, changes = [], []
    t = perf_counter()
    if geometry_scout['trigger'] and retained:
        explicit = bands(pm, original_items, (gray.shape[1], gray.shape[0]), 4)
        h = geometry_scout['height']
        nominated = set(geometry_scout['nominated'])
        rule_lines = {i for q in rule_witness['candidates'] for i in q['lines']}
        for a in explicit['lines']:
            source = a['line']
            if source not in positions:
                continue
            if source not in nominated and a.get('bend_h', 0) < .4:
                continue
            reason = None
            if source in rule_lines:
                reason = 'separator corridor takes priority'
            elif not a.get('polygon'):
                reason = 'no native polygon'
            elif a.get('source_boxes') != 1:
                reason = 'shared band topology'
            elif a.get('multi_run_fraction', 1) > .08:
                reason = 'multiple map ridges'
            elif len(a['path']) < 8:
                reason = 'short band'
            else:
                old = original_items[source]
                slope_error = abs(np.tan(np.radians(a['angle_deg'])) - line_axis(old)[1])
                if a['bend_h'] < .25 and slope_error * (bbox(old)[2] - bbox(old)[0]) / h < .5:
                    reason = 'dense geometry does not corroborate'
            if reason:
                decisions.append(dict(line=source, decision='preserve', reason=reason))
                continue
            local = positions[source]
            polygon = a['polygon']
            audit = retention(gray, working, local, polygon, h)
            if audit['lost_ink']:
                repaired, detail = keep_nearby_ink(gray, working, local, polygon, h)
                if repaired is None:
                    decisions.append(dict(line=source, decision='preserve',
                        reason='loss is not nearby envelope ink', retention=audit, repair=detail))
                    continue
                polygon = repaired
                audit = retention(gray, working, local, polygon, h)
            if audit['lost_ink']:
                decisions.append(dict(line=source, decision='preserve',
                    reason='unique original ink would be removed', retention=audit))
                continue
            working[local] = dict(original_items[source], polygon=polygon, baseline=None,
                centreline=a['path'], source_ids=[int(source)], provenance='exact DB contour geometry')
            changes.append(dict(line=source, old=original_items[source]['polygon'],
                                new=[polygon], kind='geometry'))
            decisions.append(dict(line=source, decision='native geometry', retention=audit))
    geometry_s = perf_counter() - t
    return dict(items=working, geometry_changes=changes, geometry_decisions=decisions,
        retained_source_indices=retained, witness=geometry_scout, rule_witness=rule_witness,
        scout_s=scout_s, geometry_s=geometry_s, added_s=perf_counter()-start,
        reused=dict(rule_scout=provided_rule, geometry_scout=provided_geometry),
        timing_note='Supplied scout costs must be charged by the composing caller; separators excluded.')
