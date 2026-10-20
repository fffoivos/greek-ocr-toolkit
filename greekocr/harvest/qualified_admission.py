"""Accepted CP8 composed admission policy. No detector, reader or cache preparation.

Replay acquires bound observations in compose(); qualification supplies frozen
observations to evaluate_evidence(). Both execute exactly the same policy.
"""
import hashlib
from pathlib import Path
import sys
from . import admission as adm, orientation_screen as orient
from .neighbour_words import neighbour_word_evidence
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'docs/records/harvest/collect_v3_admission/seg'))
from calibrate_cp5pb import component_hits
DROP_ORDER=('text_rules','merged','neighbour_words','orientation','geometry_unavailable','crossing','unresolved')


def evaluate_evidence(row, *, structural, axis, crossing, edge=None, page_median_height=None, screen_only=False):
    """Single policy boundary; unknown axis remains separate from unavailable geometry."""
    # Geometry-only historical witnesses must opt in explicitly. Replay always
    # requires the complete text/metadata record.
    text=None if screen_only else adm.evaluate(row,page_median_height=page_median_height)
    eligibility=adm.non_segmentation_eligibility(text['checks']) if text else dict(passed=True,rejections=[])
    composed=orient.compose_cp5(axis,structural,crossing)
    hits=dict(text_rules=not eligibility['passed'],merged=structural.get('merged') is True,
        neighbour_words=structural.get('neighbour_drop') is True,orientation=axis.get('rotated') is True,
        geometry_unavailable=composed['geometry_unavailable'],crossing=crossing.get('drop') is True,
        unresolved=composed['drop'] is None)
    failures=[k for k in DROP_ORDER if hits[k]]
    return dict(composed=composed,hits=hits,rules_failed=failures,
        **{'pass':eligibility['passed'] and composed['drop'] is False},
        screen_drop=composed['drop'],admission_drop=True if not eligibility['passed'] else composed['drop'],
        edge_clip_candidate=(edge or {}).get('candidate'),edge_clip_diagnostic=edge,
        orientation_unknown=axis.get('status')=='orientation_unknown',text=text,eligibility=eligibility)


def edge_diagnostic(page, structural, box, tolerance):
    target_id=structural.get('target_row_id')
    if target_id is None or structural['status']=='unavailable':
        return dict(status='unavailable',candidate=None)
    target=next(r for r in page['rows'] if r['row_id']==target_id)
    extents=[dict(letter,role='letter') for support in structural['row_inclusion']['rows']
             for group in support['local_groups'] for letter in group['letters']]
    hits=component_hits(extents,box,target)
    value=max((h['overflow_xh'] for h in hits),default=0)
    return dict(status='measured',candidate=value>tolerance,max_xh=value,tolerance_xh=tolerance)


def compose(row, median, page, context, tolerance):
    structural=dict(status='unavailable',reason='missing_or_invalid_cache',merged=None,neighbour_drop=None,union_drop=None)
    axis=dict(status='not_run',rotated=None,reason='geometry_unavailable')
    crossing=dict(status='unavailable',drop=None,reason='geometry_unavailable')
    edge=dict(status='unavailable',candidate=None)
    if page is not None:
        structural=neighbour_word_evidence(page,row['crop_bbox'],target_row_id=row.get('measured_row_id'))
        # Verify exact crop bytes in memory with the byte-exact interpreter.
        import io
        image=context['image'].crop(row['crop_bbox'])
        buffer=io.BytesIO(); image.save(buffer,format='PNG',compress_level=3)
        if hashlib.sha256(buffer.getvalue()).hexdigest()!=row['crop_sha256']:
            raise ValueError('crop byte mismatch: '+row['id'])
        axis=orient.observe_orientation(image)
        if axis['status']=='orientation_unknown':
            if 'regions' not in context: context['regions']=orient.measure_page_regions(context['image'])
            axis=orient.inherit_regional_axis(axis,row['crop_bbox'],context['regions'],page_binding=dict(
                source=row['crop_source_image'],source_sha256=row['crop_source_sha256'],frame=0))
        crossing=orient.column_crossings(page,row['crop_bbox'],context['separators']['boundaries'])
        edge=edge_diagnostic(page,structural,row['crop_bbox'],tolerance)
    decision=evaluate_evidence(row, page_median_height=median, structural=structural,
        axis=axis, crossing=crossing, edge=edge)
    text=decision['text'];eligibility=decision['eligibility']
    hits=decision['hits']; failures=decision['rules_failed']
    passed=decision['pass']
    return dict(row_id=row['id'],source=row['source'],primary_class=row['primary_class'],
        **{'class':text['class'],'pass':passed},label=text['label'],rules_failed=failures,
        text_rules_failed=eligibility['rejections'],text_checks={k:v for k,v in text['checks'].items() if k not in adm.SEGMENTATION_CHECKS},
        geometry_status=structural['status'],geometry_reason=structural.get('reason'),
        geometry_binding=page['binding'] if page else None,geometry_unavailable=hits['geometry_unavailable'],
        merged=structural.get('merged'),neighbour_words=structural.get('neighbour_drop'),
        orientation=axis.get('rotated'),orientation_status=axis['status'],orientation_unknown=axis['status']=='orientation_unknown',
        orientation_decision_source=axis.get('decision_source'),crossing=crossing.get('drop'),
        edge_clip_candidate=edge['candidate'],edge_clip_diagnostic=edge,
        crop_bbox=row['crop_bbox'],crop_sha256=row['crop_sha256'],page_id=row['page_id'])


