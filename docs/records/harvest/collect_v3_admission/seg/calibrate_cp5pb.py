"""One-round CP5pb native component diagnostic; offline, read-only replay.

H2 letter extents only: no raw-component fallback that would promote marks or
noise. Target guides are sampled at the cut column (endpoint-clamped outside
its recorded x span); no refit or reassignment.
"""
import json
import contextlib
import io
import sys
from pathlib import Path
import numpy as np
SEG = Path(__file__).resolve().parent
sys.path.insert(0, str(SEG))
import calibrate_cp5p as prior


def component_hits(extents, box, target):
    hits = []
    for extent in extents:
        if extent.get('role', 'letter') != 'letter':
            continue
        x, y, z, bottom = extent['box']
        height = bottom-y
        if height < .5*target['xheight'] or not (y < box[3] and bottom > box[1]):
            continue
        for side, edge in [('left', box[0]), ('right', box[2])]:
            if not x < edge < z:
                continue
            col = int(np.clip(edge-target['x0'], 0, len(target['meanline'])-1))
            top, base = float(target['meanline'][col]), float(target['baseline'][col])
            overlap = max(0., min(bottom, base)-max(y, top))/height
            if overlap < .5:
                continue
            overflow = edge-x if side == 'left' else z-edge
            hits.append(dict(extent, side=side, body_band=[top, base],
                band_overlap_fraction=overlap, overflow_px=overflow,
                overflow_xh=overflow/target['xheight']))
    return hits


def measure(case, observation, box, binding):
    if observation['status'] == 'unavailable':
        return dict(row_id=case, status='unavailable', max_px=None, max_xh=None)
    page = prior.load_cached_page(binding['source'], binding['cache_directory'], binding['source_sha256'])
    target = next(r for r in page['rows'] if r['row_id'] == observation['target_row_id'])
    extents = []
    for support in observation['row_inclusion']['rows']:
        for group in support['local_groups']:
            for letter in group['letters']:
                extents.append(dict(box=letter['box'], role='letter', kind='H2_letter',
                    assigned_row_id=support['row_id'], parent_ids=letter['native_component_ids'],
                    resolved=letter['resolved'], shared_parent_split=letter['shared_parent_split']))
    hits = component_hits(extents, box, target)
    cut_candidates = []
    for extent in extents:
        x, y, z, bottom = extent['box']
        for side, edge in [('left', box[0]), ('right', box[2])]:
            if x < edge < z and y < box[3] and bottom > box[1]:
                col = int(np.clip(edge-target['x0'], 0, len(target['meanline'])-1))
                top, base = float(target['meanline'][col]), float(target['baseline'][col])
                cut_candidates.append(dict(extent, side=side, body_band=[top, base],
                    height_xh=(bottom-y)/target['xheight'],
                    band_overlap_fraction=max(0., min(bottom, base)-max(y, top))/(bottom-y)))
    return dict(row_id=case, status='measured', target_row_id=target['row_id'],
        cut_candidates=cut_candidates, target_guides=dict(x0=target['x0'],
            xheight=float(target['xheight']), meanline=target['meanline'].tolist(),
            baseline=target['baseline'].tolist()),
        crop_box=box, xheight=float(target['xheight']), examined_extents=extents, hits=hits,
        max_px=max((h['overflow_px'] for h in hits), default=0),
        max_xh=max((h['overflow_xh'] for h in hits), default=0))


def replay_counts(rows, tolerance, unit='xh'):
    """Non-gating edge_clip_candidate counts per source × frozen clip class.

    This hook never returns an admission/drop decision. Unavailable is separate.
    """
    counts = {}
    for row in rows:
        source = row['row_id'].split('--')[0]
        klass = 'clip' if row['row_id'] in prior.CLIPS else 'non_clip'
        out = counts.setdefault(source, {}).setdefault(klass,
            dict(total=0, measured=0, unavailable=0, edge_clip_candidate=0))
        out['total'] += 1
        if row['status'] == 'unavailable':
            out['unavailable'] += 1
        else:
            out['measured'] += 1
            out['edge_clip_candidate'] += int(row['max_'+unit] > tolerance)
    return counts


def main():
    # The prior driver installs the filesystem/network/detector audit before
    # cache access. Capture only its JSON stdout, then add diagnostic metadata.
    prior.measure = measure
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        prior.main()
    report = json.loads(buffer.getvalue())
    passing = [c for c in report['curve_xh'] if c['passes']]
    report['schema'] = 'SEG-CP5pb-component-calibration-v1'
    report['status'] = 'pass' if passing else 'stopped->diagnostic'
    report['gating'] = False
    report['diagnostic_name'] = 'edge_clip_candidate'
    # Best separation = maximize clip recall minus measurable-nonclip FPR;
    # ties minimize owner false positives, then choose the lowest interval.
    best = max(report['curve_xh'], key=lambda c: (
        c['clips']/4-c['nonclip_false_drops']/94,
        -c['owner_keep_false_drops'], -c['lower_inclusive']))
    upper = best['upper_exclusive']
    tolerance = ((best['lower_inclusive']+upper)/2 if upper is not None
                 else best['lower_inclusive'])
    report['selected_tolerance'] = dict(unit='xh', value=tolerance,
        interval=[best['lower_inclusive'], upper],
        purpose='non-gating diagnostic; maximum recall minus nonclip FPR, owner FP tie break',
        px_conversion='row-specific: tolerance_xh * target_xheight')
    report['replay_counts'] = replay_counts(report['rows'], tolerance)
    report['diagnostic_px_by_row'] = {
        r['row_id']: tolerance*r['xheight'] for r in report['rows']+report['owner_keeps']
        if r['status']=='measured'}
    report['input_sha256'][str(Path(__file__).relative_to(prior.ROOT))] = prior.sha(__file__)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
