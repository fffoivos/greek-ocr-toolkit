"""Compose A6 operators after removals while retaining original DB ancestry.

Adapted orchestration from shared.geometry_feature_correct.run(version=6).
The feature witnesses/thresholds and retention operators are unchanged.
"""
from time import perf_counter
import numpy as np
from ..shared.contracts import bbox
from ..shared.geometry import line_axis
from ..shared.geometry_feature_paths import bands
from .geometry_scout import sparse_fast as sparse
from ..shared.geometry_feature_correct import retention, keep_nearby_ink
from ..shared.geometry_feature_rules import refine, split_items


def run(gray, pm, original, current, witness, primitive):
    start = perf_counter()
    s = sparse(pm, original, (gray.shape[1], gray.shape[0]), 3)
    scout_s = perf_counter() - start
    t = perf_counter()
    out = list(current)
    decisions, changes = [], []
    rule_lines = {i for c in witness['candidates'] for i in c['lines']}
    # Only intact one-source survivors can acquire the original contour.
    owners = {}
    for j, q in enumerate(out):
        for i in q['source_ids']:
            owners.setdefault(i, []).append(j)
    if s['trigger']:
        explicit = bands(pm, original, (gray.shape[1], gray.shape[0]), 4)
        h = s['height']
        for a in explicit['lines']:
            i = a['line']
            if i not in s['nominated'] and a.get('bend_h', 0) < .4:
                continue
            ids = owners.get(i, [])
            reason = None
            if i in rule_lines:
                reason = 'separator corridor takes priority'
            elif len(ids) != 1 or out[ids[0]]['polygon'] != original[i]['polygon']:
                reason = 'removed or already separated source'
            elif not a.get('polygon'):
                reason = 'no native polygon'
            elif a.get('source_boxes') != 1:
                reason = 'shared band topology'
            elif a.get('multi_run_fraction', 1) > .08:
                reason = 'multiple map ridges'
            elif len(a['path']) < 8:
                reason = 'short band'
            elif a['bend_h'] < .25 and abs(np.tan(np.radians(a['angle_deg'])) - line_axis(original[i])[1]) * (bbox(original[i])[2] - bbox(original[i])[0]) / h < .5:
                reason = 'dense geometry does not corroborate'
            if reason:
                decisions.append(dict(source=i, decision='preserve', reason=reason))
                continue
            j = ids[0]
            p = a['polygon']
            audit = retention(gray, out, j, p, h)
            if audit['lost_ink']:
                p, repair = keep_nearby_ink(gray, out, j, p, h)
                if p is None:
                    decisions.append(dict(source=i, decision='preserve', reason='loss is not nearby envelope ink', retention=audit, repair=repair))
                    continue
                audit = retention(gray, out, j, p, h)
            assert audit['lost_ink'] == 0
            out[j] = dict(out[j], polygon=p, baseline=None, centreline=a['path'], provenance='exact DB contour geometry')
            changes.append(dict(source=i, old=original[i]['polygon'], new=[p], retention=audit))
    geometry_s = perf_counter() - t
    t = perf_counter()
    curved = None
    if witness['candidates']:
        # Whole-rule ownership still sees ALL original crossings, including
        # removed boxes: deletion cannot make a back rule look front-owned.
        curved = refine(gray, original, witness, primitive, apply=False, ownership=True, wide_paper=True)
        split = split_items(gray, out, curved['rules'], witness['height']) if curved['rules'] else dict(items=out, changes=[], decisions=[])
        curved.update(applied=split['changes'], applied_decisions=split['decisions'])
        out = split['items']
    return dict(items=out, changes=changes, decisions=decisions, witness=s, curved=curved,
                scout_s=scout_s, geometry_s=geometry_s, curved_s=perf_counter()-t, seconds=perf_counter()-start)
