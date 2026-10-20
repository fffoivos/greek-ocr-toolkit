"""CP5 measure-only candidate. Axis exclusion and horizontal defects stay separate.

No public admission qualification, recognizer, OSD, repair, or detector preparation.
Saved local observations bind native pixels, options and all orientation code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from copy import deepcopy
import numpy as np
from PIL import Image
from greekocr.glyphs.orientation import measure_orientation, discover_directions, canonical_word_crop
from greekocr.glyphs.orientation_regions import axis_regions, resolve_regions
from greekocr.pages.boundaries import BoundaryEvidence


def orientation_binding(image, *, isolated_line=False, content_kind='unknown'):
    from .geometry_observations import code_identity, implementation_binding, sha
    gray = image.convert('L')
    return dict(pixels_sha256=hashlib.sha256(gray.tobytes()).hexdigest(),
                size=list(gray.size), mode='L', unit='line' if isolated_line else 'block',
                content_kind=content_kind, use_osd=False,
                code_sha256=code_identity(Path(__file__).resolve().parents[1]),
                adapter_sha256=sha(__file__), dependencies=implementation_binding()['dependencies'])


def decision_sha(decision):
    return hashlib.sha256(json.dumps(decision, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def observe_orientation(image, *, isolated_line=False, content_kind='unknown', saved=None):
    """Block evidence decides; line extent is a veto/diagnostic only.

    Compact ink and line/block disagreement abstain. Unknown polarity never
    suppresses a supported vertical axis. Saved evidence is local,
    never a page-level axis inherited across arbitrary crops. Stale saved
    evidence fails closed rather than silently being accepted or remeasured.
    """
    binding = orientation_binding(image, isolated_line=isolated_line, content_kind=content_kind)
    if saved is not None:
        if saved.get('binding') != binding:
            return dict(status='unavailable', reason='stale_local_orientation', rotated=None,
                        binding=binding, decision=None)
        decision = saved.get('decision')
        if not isinstance(decision, dict) or decision.get('axis') not in ('horizontal','vertical','unknown'):
            return dict(status='unavailable', reason='invalid_local_orientation', rotated=None,
                        binding=binding, decision=None)
        if saved.get('decision_sha256') != decision_sha(decision):
            return dict(status='unavailable', reason='corrupt_local_orientation', rotated=None,
                        binding=binding, decision=None)
        if decision.get('evidence',{}).get('page_regional_inheritance') is not None:
            return dict(status='unavailable', reason='regional_context_requires_revalidation',
                        rotated=None, binding=binding, decision=None)
        axis = decision['axis']
        return dict(saved, status='orientation_unknown' if axis=='unknown' else 'measured',
                    rotated=None if axis=='unknown' else axis=='vertical',
                    decision_source='unknown' if axis=='unknown' else 'measured', source='saved_local')
    block = measure_orientation(image, use_osd=False, unit='block',
                                content_kind=content_kind)
    line = measure_orientation(image, use_osd=False, unit='line',
                               content_kind=content_kind)
    regions = axis_regions(discover_directions(image))
    # The toolkit's existing 1.5 extent boundary is used only to ABSTAIN.
    # It can never establish either final axis.
    tight = canonical_word_crop(image)
    compact = max(tight.size) < 1.5 * max(1, min(tight.size))
    decision = block.to_record()
    reason = None
    if compact:
        reason = 'compact_ink'
    elif block.axis != line.axis:
        reason = 'line_block_disagreement'
    elif regions and any(r['axis'] != block.axis for r in regions):
        reason = 'mixed_region_axes'
    elif block.axis == 'unknown':
        reason = 'unknown_axis'
    if reason:
        decision.update(axis='unknown', orientation_cw=None, polarity_confidence=0.,
                        alternatives=[0,90,180,270])
    decision['evidence'].update(block_diagnostic=block.to_record(),
        line_diagnostic=line.to_record(), regional_context=regions,
        compact_ink=compact, abstention_reason=reason,
        final_axis_source='block-with-diagnostic-vetoes')
    axis = decision['axis']
    return dict(status='orientation_unknown' if axis=='unknown' else 'measured',
                reason=reason,
                rotated=None if axis=='unknown' else axis=='vertical',
                binding=binding, decision=decision, decision_sha256=decision_sha(decision),
                decision_source='unknown' if axis=='unknown' else 'measured',
                source='native_crop_toolkit')


def measure_page_regions(image):
    """Existing region discovery and block measurement, without axis hints/OSD."""
    rows = [dict(id=f'region-{i}', **region,
                 decision=measure_orientation(image.crop(region['box']), use_osd=False,
                                              unit='block'))
            for i, region in enumerate(axis_regions(discover_directions(image)))]
    return [{**row, 'decision': row['decision'].to_record()}
            for row in resolve_regions(rows)]


def inherit_regional_axis(observation, box, regions, *, page_binding):
    """Unknown-only inheritance from an unmixed, measured vertical page region.

    Region envelopes describe ink, not crop padding: membership uses the line
    centre. Every region intersecting the crop must agree, and at least one
    must contain its centre. No horizontal or unavailable decision is replaced.
    The source/box and complete regional records remain attached to the result.
    """
    out = deepcopy(observation)
    decision = out.get('decision')
    if decision is None or decision['axis'] != 'unknown':
        return out
    x0,y0,x1,y1 = box
    overlaps = [r for r in regions if r['box'][0] < x1 and x0 < r['box'][2]
                and r['box'][1] < y1 and y0 < r['box'][3]]
    inside = any(r['box'][0] <= (x0+x1)/2 <= r['box'][2] and
                 r['box'][1] <= (y0+y1)/2 <= r['box'][3] for r in overlaps)
    vertical = inside and all(r['axis'] == 'vertical' and
                             r['decision']['axis'] == 'vertical' for r in overlaps)
    decision['evidence']['page_regional_inheritance'] = dict(
        page_binding=page_binding, crop_bbox=list(box), regions=overlaps,
        membership='crop-centre-contained; all intersecting regions agree', inherited=vertical)
    if vertical:
        decision.update(axis='vertical', orientation_cw=None, polarity_confidence=0.,
                        alternatives=[90,270])
        decision['evidence']['final_axis_source'] = 'regional'
        out.update(status='measured', rotated=True, decision_source='regional',
                   reason='vertical_unmixed_page_region')
    out['decision_sha256'] = decision_sha(decision)
    return out


def regional_context(proposals, decisions):
    """Existing adapters only, for explicitly supplied mixed/ambiguous context.

    These diagnostic proposals do not silently replace a crop's local axis.
    """
    return dict(axis_regions=axis_regions(proposals), resolved=resolve_regions(decisions))


def column_crossings(page, box, boundaries):
    """Validate recorded separator proposals, then measure original crop ink.

    Envelope overlap alone cannot DROP. No inferred separator from column ids.
    Absence of recorded boundary proposals is reported as coverage unavailable.
    """
    from .row_inclusion import validate_box
    validate_box(page, box)
    if boundaries is None:
        return dict(status='unavailable', reason='no_recorded_boundaries', drop=None, crossings=[])
    if not boundaries:
        return dict(status='measured', reason=None, drop=False, crossings=[])
    from .geometry_observations import invalid_geometry_dependencies
    if invalid_geometry_dependencies(page, box):
        return dict(status='unavailable', reason='invalid_geometry', drop=None, crossings=[])
    with Image.open(page['source']) as image:
        original = np.asarray(image.convert('L'))
    evidence = BoundaryEvidence(original, page['rows'], original_ink=page['ink'])
    kept, rejected = evidence.validate(boundaries)
    local = []
    x0,y0,x1,y1 = box
    for row in page['rows']:
        a,b = max(x0,row['x0']),min(x1,row['x1'])
        if b<=a or not page['ownership'].box_hits(row,box).any():
            continue
        r = dict(row, x0=a,x1=b)
        for key in page['ownership'].CURVES:
            r[key] = np.asarray(row[key])[a-row['x0']:b-row['x0']]
        local.append(r)
    crop_ink = page['ink'].copy()
    crop_ink[:y0] = False; crop_ink[y1:] = False
    crop_ink[:,:x0] = False; crop_ink[:,x1:] = False
    local_evidence = BoundaryEvidence(original, local, original_ink=crop_ink)
    local_evidence.validated_rules = evidence.validated_rules
    crossings = []
    for boundary in kept:
        if boundary['kind'] not in ('gutter','rule'):
            continue
        for i,row in enumerate(local):
            crossing = local_evidence.crossing(i,boundary)
            crossings.append(dict(crossing,row_id=row['row_id']))
    return dict(status='measured', reason=None,
                drop=any(c['classification']=='real crossing' for c in crossings),
                crossings=crossings, validated=kept, rejected=rejected)


def compose_cp5(orientation, structural, crossing):
    """Tri-state measured union; unknown axis never becomes horizontal.

    CP4c policy loss stays separate. Horizontal structural positives remain
    positives regardless of orientation or missing column coverage.
    """
    # Orientation unknown admits only for this screen; measurement stays unknown.
    orientation_drop = False if orientation.get('status') == 'orientation_unknown' else orientation.get('rotated')
    independent = [structural.get('union_drop'), crossing.get('drop')]
    def union(values):
        return True if True in values else None if None in values else False
    measured = union([orientation.get('rotated'), *independent])
    admitted = union([orientation_drop, *independent])
    from .admission import compose_segmentation_decision
    policy = compose_segmentation_decision(structural)
    return dict(measured_drop=measured, geometry_unavailable=policy['geometry_unavailable'],
                drop=True if policy['geometry_unavailable'] else admitted,
                orientation_status=orientation['status'],
                verified_keep=measured is False and orientation.get('rotated') is False,
                crossing_status=crossing['status'])
