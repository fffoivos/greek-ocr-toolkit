"""Offline, text-independent N1 ink classification and conservative label policy.

Input is n1_render.render's side record, made with glyphs.components.line_glyphs.
No OCR character is used to classify ink. Character custody only gates edits.
"""
from greekocr.ops.data_root import input_path as _data_input
import hashlib
import itertools
import json
import math
from pathlib import Path
from statistics import median

CLASSES = ('raised dot', 'baseline dot', 'comma', 'hyphen', 'en dash', 'em dash',
           'space', 'nothing', 'unsure')
DASHES = ('hyphen', 'en dash', 'em dash')
FEATURES = ('height_relative_digit', 'centre_y_relative_band', 'width_relative_digit')


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()


def freeze(path, config):
    """The hash is SHA256 of the exact immutable JSON bytes (no circular field)."""
    path = Path(path)
    data = canonical(config) + b'\n'
    with path.open('xb') as f:
        f.write(data)
    digest = hashlib.sha256(data).hexdigest()
    path.with_suffix('.sha256').write_text(digest + '  ' + path.name + '\n')
    return load_rule(path)


def load_rule(path):
    path = Path(path)
    expected = path.with_suffix('.sha256').read_text().split()[0]
    if sha(path) != expected:
        raise ValueError('frozen rule hash mismatch')
    config = json.loads(path.read_text())
    if config.get('schema') != 'n1-ink-rule-v1':
        raise ValueError('unknown ink rule schema')
    return dict(config=config, rule_hash=expected)


def measurements(slot):
    """Preserve every intersecting component, including crossing digit ink.

    Crossing small marks may be candidates; crossing full-height digits cannot.
    A horizontal stroke is a hard veto even when it crosses a Google box.
    """
    g = slot.get('geometry', {})
    m = slot.get('measurements', {})
    width = slot.get('dash', {}).get('median_digit_width')
    if not width:
        widths = [b[2]-b[0] for b in (g.get('left_digit'), g.get('right_digit')) if b]
        width = median(widths) if widths else None
    h = m.get('digit_height', 0)
    out = dict(geometry_status=g.get('geom_status', 'missing'), component_count=0,
               bbox=None, height_relative_digit=None, centre_y_relative_band=None,
               width_relative_digit=None, gap_width=m.get('gap_width'),
               median_digit_width=width, digit_height=h, digit_top=m.get('digit_top'),
               baseline=m.get('baseline'), helper_band=m.get('helper_band'), components=[],
               candidate_count=0, hyphen_length_stroke=False)
    if g.get('geom_status') != 'ok' or h <= 0 or not width or width <= 0:
        return out
    for c in m.get('components', []):
        out['components'].append(dict(c, height_relative_digit=c['height']/h,
            width_relative_digit=c['width']/width))
    out['component_count'] = len(out['components'])
    if out['components']:
        boxes = [c['bbox'] for c in out['components']]
        out['bbox'] = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                       max(b[2] for b in boxes), max(b[3] for b in boxes)]
    out['hyphen_length_stroke'] = any(c['width'] >= max(3, 2*c['height']) for c in out['components'])
    # Fixed custody screen, declared before fitting. No clipping or invented ink.
    candidates = [c for c in out['components'] if c['height_relative_digit'] <= .55]
    out['candidate_count'] = len(candidates)
    if len(candidates) == 1:
        out.update({k: candidates[0][k] for k in FEATURES})
        out['candidate_bbox'] = candidates[0]['bbox']
    return out


def raised_margin(m, thresholds):
    if m['candidate_count'] != 1 or m['hyphen_length_stroke']:
        return -1.0
    if any(m[k] is None or not math.isfinite(m[k]) for k in FEATURES):
        return -1.0
    lo, hi = thresholds['raised_centre']
    return min(m['centre_y_relative_band']-lo, hi-m['centre_y_relative_band'],
               thresholds['raised_height_max']-m['height_relative_digit'],
               thresholds['raised_width_max']-m['width_relative_digit'])


def classify(m, cfg):
    t = cfg['thresholds']
    if m['geometry_status'] != 'ok' or not m['digit_height'] or not m['median_digit_width']:
        return 'unsure', 0.0, 'geometry_unavailable'
    if m['hyphen_length_stroke']:
        strokes = [c for c in m['components'] if c['width'] >= max(3, 2*c['height'])]
        if len(strokes) != 1:
            return 'unsure', 0.0, 'multiple_strokes'
        w = strokes[0]['width_relative_digit']; a,b = t['dash_width_cuts']
        return ('hyphen' if w < a else 'en dash' if w < b else 'em dash'), min(abs(w-a),abs(w-b)), 'stroke_veto_tag_only'
    if not m['component_count']:
        # Overlapping symbol boxes cannot prove the absence of printed ink.
        if m['gap_width'] is None or m['gap_width'] <= 0:
            return 'unsure', 0.0, 'overlapping_digit_boxes'
        kind = 'space' if m['gap_width']/m['median_digit_width'] >= t['space_gap_min'] else 'nothing'
        return kind, 1.0, 'empty_gap'
    margin = raised_margin(m, t)
    if margin >= cfg['edit_margin_min']:
        return 'raised dot', margin, 'raised_box'
    if m['candidate_count'] != 1:
        return 'unsure', 0.0, 'ambiguous_components'
    y=m['centre_y_relative_band']; h=m['height_relative_digit']
    if y >= t['baseline_centre_min']:
        return ('comma' if h >= t['comma_height_min'] else 'baseline dot'), abs(y-t['baseline_centre_min']), 'low_mark'
    return 'unsure', max(0.0, margin), 'outside_fitted_bands'


def decide(slot, rule, text=None):
    m = measurements(slot)
    kind, margin, reason = classify(m, rule['config'])
    a,b = slot['start'],slot['end']; glyph=slot.get('glyph',slot.get('google_glyph',''))
    # No grammar restriction: release brief authorizes the physical rule between digits.
    between = slot.get('boundary') is None
    if text is not None:
        if not 0 <= a <= b <= len(text) or text[a:b] != glyph:
            raise ValueError('slot text custody mismatch')
        between = between and a > 0 and b < len(text) and text[a-1] in '0123456789' and text[b] in '0123456789'
    edit = None
    if between and glyph in ('-', '.') and kind == 'raised dot' and margin >= rule['config']['edit_margin_min'] and not m['hyphen_length_stroke']:
        edit = dict(start=a,end=b,original=glyph,replacement='·')
    return dict(slot_id=slot['slot_id'],line_id=slot['line_id'],measurements=m,
                **{'class':kind},margin=margin,reason=reason,rule_hash=rule['rule_hash'],
                edit=edit,tags=[kind] if kind in (*DASHES,'unsure') else [])


def best_cut(values, labels, choices, default):
    if not values:
        return default
    cuts=sorted(set(values));cuts=[cuts[0]-1e-6]+[(a+b)/2 for a,b in zip(cuts,cuts[1:])]+[cuts[-1]+1e-6]
    return max(cuts,key=lambda cut:(sum((choices[0] if v<cut else choices[1])==y for v,y in zip(values,labels)),-abs(cut-default)))


def fit(records):
    """Fit ONLY the document training half; deterministic precision-first grid.

    Fixed screens: horizontal stroke veto, <=.55 digit-height candidate. All
    numerical class boundaries below are selected from the training records.
    """
    pairs=[(measurements(s),s['truth']) for s in records]
    positive=[m for m,y in pairs if y=='raised dot' and m['candidate_count']==1 and not m['hyphen_length_stroke']]
    if not positive:
        raise ValueError('no measurable raised-dot fitting truth; cannot fit')
    # Candidate boxes are centered on fit positives, with a preregistered grid of padding.
    boxes=[]
    for pad in (.01,.03,.06,.10):
        boxes.append(dict(raised_centre=[min(m['centre_y_relative_band'] for m in positive)-pad,max(m['centre_y_relative_band'] for m in positive)+pad],
                          raised_height_max=max(m['height_relative_digit'] for m in positive)+pad,
                          raised_width_max=max(m['width_relative_digit'] for m in positive)+pad))
    choices=[]
    for t,margin in itertools.product(boxes,(0.0,.01,.02,.04)):
        pred=[y for m,y in pairs if raised_margin(m,t)>=margin]
        tp=pred.count('raised dot');fp=len(pred)-tp
        choices.append(((int(tp>0 and fp==0),tp/(tp+fp) if tp+fp else 0,tp,-fp,-t['raised_height_max'],margin),t,margin))
    _,t,margin=max(choices,key=lambda x:x[0]);t=dict(t)
    dash=[(m,y) for m,y in pairs if y in DASHES and m['candidate_count']==1 and m['hyphen_length_stroke']]
    t['dash_width_cuts']=[best_cut([m['width_relative_digit'] for m,y in dash if y in kinds],
         [y for m,y in dash if y in kinds],kinds,default) for kinds,default in ((DASHES[:2],.75),(DASHES[1:],1.45))]
    t['dash_width_cuts'].sort()
    dots=[(m,y) for m,y in pairs if y in ('raised dot','baseline dot') and m['candidate_count']==1 and not m['hyphen_length_stroke']]
    t['baseline_centre_min']=best_cut([m['centre_y_relative_band'] for m,y in dots],[y for m,y in dots],('raised dot','baseline dot'),.83)
    lows=[(m,y) for m,y in pairs if y in ('baseline dot','comma') and m['candidate_count']==1]
    t['comma_height_min']=best_cut([m['height_relative_digit'] for m,y in lows],[y for m,y in lows],('baseline dot','comma'),.25)
    empty=[(m,y) for m,y in pairs if y in ('nothing','space') and not m['component_count'] and m['gap_width'] is not None and m['median_digit_width']]
    t['space_gap_min']=best_cut([m['gap_width']/m['median_digit_width'] for m,y in empty],[y for m,y in empty],('nothing','space'),.5)
    return dict(schema='n1-ink-rule-v1',algorithm='component-bands-v1',thresholds=t,edit_margin_min=margin,
                fixed_screens=dict(candidate_height_max=.55,stroke_min_pixels=3,stroke_aspect_min=2),
                fitting=dict(rows=len(records),measurable_raised=len(positive),objective='nonempty zero-false-positive raised box, precision, recall; training only'))


def metrics(truths, decisions):
    matrix={k:{p:0 for p in CLASSES} for k in (*CLASSES,'any dash')}
    for truth,d in zip(truths,decisions):
        matrix[truth][d['class']]+=1
    tp=sum(t=='raised dot' and d['class']=='raised dot' for t,d in zip(truths,decisions))
    predicted=sum(d['class']=='raised dot' for d in decisions)
    actual=truths.count('raised dot')
    false_range=sum(t in (*DASHES,'any dash') and d['class']=='raised dot' for t,d in zip(truths,decisions))
    return dict(confusion_matrix=matrix,rows=len(truths),raised_tp=tp,raised_predicted=predicted,raised_truth=actual,
                raised_precision=tp/predicted if predicted else None,raised_recall=tp/actual if actual else None,
                hyphen_to_raised_false=false_range,
                raised_vs_hyphen_baseline_false=sum(t in (*DASHES,'any dash','baseline dot') and d['class']=='raised dot' for t,d in zip(truths,decisions)),
                unsure_rate=sum(d['class']=='unsure' for d in decisions)/len(decisions) if decisions else None)
