"""Read-only crop evidence adapter around existing Greek OCR component tools.

No OCR, new binariser, ownership rule, font-family training or admission policy.
The default command is a preflight. Actual crop processing requires --execute.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import math
import os
from pathlib import Path
import signal
import sys
import time
import warnings

ROOT = Path(__file__).resolve().parents[2]
TEXT_ROLES = frozenset({'letter', 'fragment', 'mark', 'punct'})
BODY_ROLES = frozenset({'letter', 'fragment'})


def line_inventory(glyphs, lines, components, angle_deg):
    """Inventory existing bands/roles; no fitting, relabelling or page context."""
    from dataclasses import asdict
    import numpy as np
    from greekocr.glyphs.baseline import skew_line
    from greekocr.harvest.neighbour_words import WORD_PROXY

    xh, width = glyphs.band.xh, glyphs.width
    assigned = [[] for _ in lines]
    for c in components:
        x0, y0, x1, y1 = c['bbox']
        x = int(np.clip((x0+x1)/2, 0, width-1))
        if lines:
            at = min(range(len(lines)), key=lambda i: abs((y0+y1)/2 - (lines[i].mean[x]+lines[i].base[x])/2))
            assigned[at].append(c)

    def body(c, line):
        x0, y0, x1, y1 = c['bbox']
        x = int(np.clip((x0+x1)/2, 0, width-1))
        # Exactly second_line's per-band body overlap/width/role criteria.
        return (c['role'] not in ('mark', 'rule') and x1-x0 <= 2*xh
                and min(y1, line.base[x])-max(y0, line.mean[x]) >= .6*xh)

    inventory = []
    for index, (line, owned) in enumerate(zip(lines, assigned)):
        bodies = [c['index'] for c in owned if body(c, line)]
        coverage = (line.x1-line.x0+1)/width
        groups = []
        if line.side != 'main':
            # Same empty-gap scale as neighbour_words.row_word_evidence, within
            # ONE existing band. Retain partial tips; they are cut-off groups.
            for c in sorted((c for c in owned if c['role'] == 'neighbour'), key=lambda c: (c['bbox'][0], c['index'])):
                if not groups or c['bbox'][0]-max(p['bbox'][2] for p in groups[-1]) >= WORD_PROXY['word_gap_xh']*xh:
                    groups.append([])
                groups[-1].append(c)
        words = []
        for group in groups:
            bbox = [min(c['bbox'][0] for c in group), min(c['bbox'][1] for c in group),
                    max(c['bbox'][2] for c in group), max(c['bbox'][3] for c in group)]
            body_ids = [c['index'] for c in group if body(c, line)]
            edge = bbox[0] == 0 or bbox[2] == width
            words.append(dict(bbox=bbox, component_ids=[c['index'] for c in group],
                body_ids=body_ids, bodies=len(body_ids), touches_horizontal_edge=edge,
                whole=len(body_ids) >= 2 and not edge))
        inventory.append(dict(index=index, side=line.side, votes=float(line.votes), visible=float(line.visible),
            x0=int(line.x0), x1=int(line.x1), coverage=coverage, bodies=len(bodies), body_ids=bodies,
            complete=bool(line.votes >= 6 and len(bodies) >= 6 and line.visible >= .9 and coverage >= .6),
            component_ids=[c['index'] for c in owned], whole_words=sum(w['whole'] for w in words),
            cutoff_words=sum(not w['whole'] for w in words), word_groups=words,
            context_whole_words=None, context_cutoff_words=None, context_count_resolved=None))
    main = next((l for l in lines if l.side == 'main' and l.votes > 0), None)
    # skew_line and the measured heights are diagnostics only, never gate inputs.
    cut = dict(angle_deg=None, crossings=[], cut_spans=[], cut_letters=[], baseline_exit=False,
        low_visibility_span=False, upright_box_height=None, row_frame_height=None)
    if main is not None:
        skew = skew_line(glyphs)
        cut.update(angle_deg=skew.angle_deg, crossings=[asdict(c) for c in skew.crossings],
            cut_spans=[asdict(s) for s in skew.cut_spans], cut_letters=[asdict(c) for c in skew.cut_letters])
        cut['baseline_exit'] = any(c.line == 'baseline' and 'leaves the crop' in c.meaning for c in skew.crossings)
        cut['low_visibility_span'] = any(s.min_visible < .6 for s in skew.cut_spans)
        text = [c for c in components if c['role'] in TEXT_ROLES]
        upright = tight_box(text)
        row = tight_box(text, labels=glyphs.labels, angle_deg=angle_deg, centre=(glyphs.width/2, glyphs.height/2))
        if upright is not None:
            cut.update(upright_box_height=upright[3]-upright[1], row_frame_height=row[3]-row[1])
    cut['cut'] = cut['baseline_exit'] or cut['low_visibility_span']
    return inventory, cut


def orient_crop(image, content_class, measure_orientation, QuarterTurn, visual_review=None):
    """Use existing orientation evidence and an exact quarter-turn pixel frame.

    A long-axis preview is allowed when polarity is unknown, but its box
    judgement must abstain. No aspect ratio is treated as proof of uprightness.
    """
    observation = None
    angle = 0
    resolved = True
    if image.height > image.width:
        observation = measure_orientation(image, use_osd=False, unit='block',
            content_kind='numbers' if content_class == 'numerics_tables' else 'unknown').to_record()
        resolved = observation['orientation_cw'] is not None
        angle = observation['orientation_cw'] if resolved else 90
        if visual_review is not None:
            angle = visual_review['normalization_cw']
            resolved = visual_review['orientation_resolved']
    frame = QuarterTurn(image.width, image.height, angle)
    return frame.image(image), dict(source_width=image.width, source_height=image.height,
        width=int(frame.size[0]), height=int(frame.size[1]), normalization_cw=angle,
        source_to_measurement=frame.matrix.tolist(), orientation_resolved=resolved,
        status='native_horizontal' if observation is None else 'visual_review' if visual_review is not None and resolved else 'guide_supported' if resolved else 'axis_preview_only',
        orientation=observation, visual_review=visual_review)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tight_box(components, *, labels=None, angle_deg=0, centre=None):
    if not components:
        return None
    if angle_deg != 0:
        import numpy as np
        # Rotate only the selected components' ink, not their upright envelopes.
        # Pixel cells have unit area; their projected half-width bounds the ink
        # without resampling or rounding a continuous row-frame measurement.
        yy, xx = np.nonzero(np.isin(labels, [c['index'] for c in components]))
        if not len(xx):
            raise ValueError('text components have no labelled ink')
        cx, cy = centre
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        dx, dy = xx + .5 - cx, yy + .5 - cy
        u, v = c*dx + s*dy + cx, -s*dx + c*dy + cy
        half = (abs(c) + abs(s))/2
        return [float(u.min()-half), float(v.min()-half),
                float(u.max()+half), float(v.max()+half)]
    # Preserve the original integer box exactly for the identity transform.
    return [min(c['bbox'][0] for c in components), min(c['bbox'][1] for c in components),
            max(c['bbox'][2] for c in components), max(c['bbox'][3] for c in components)]


def box_metrics(box, width, height, xheight):
    if box is None:
        return None
    x0, y0, x1, y1 = box
    if not 0 <= x0 < x1 <= width or not 0 <= y0 < y1 <= height:
        raise ValueError('support box outside native crop')
    w, h = x1-x0, y1-y0
    margins = dict(left=x0, top=y0, right=width-x1, bottom=height-y1)
    return dict(bbox=box, width=w, height=h, aspect=w/h,
                width_fraction=w/width, height_fraction=h/height,
                box_area_fraction=w*h/(width*height),
                aspect_relative_to_segment=(w/h)/(width/height),
                margins_px=margins,
                margins_fraction=dict(left=x0/width, right=(width-x1)/width,
                                      top=y0/height, bottom=(height-y1)/height),
                margins_xheight={k:v/xheight for k,v in margins.items()} if xheight else None,
                width_xheight=w/xheight if xheight else None,
                height_xheight=h/xheight if xheight else None,
                touches_edges=[k for k,v in margins.items() if v == 0])


def features_from_observation(*, width, height, components, ink_box, ink_pixels,
                              xheight, xheight_source, support_count, chars,
                              labels=None, angle_deg=0):
    """Geometry arithmetic only; components/roles come from the existing tool."""
    if width <= 0 or height <= 0 or chars < 0:
        raise ValueError('invalid native dimensions or character count')
    if not xheight or not math.isfinite(xheight) or xheight <= 0:
        xheight = None
    if len({c['index'] for c in components}) != len(components):
        raise ValueError('duplicate native component identities')
    text = [c for c in components if c['role'] in TEXT_ROLES]
    bodies = [c for c in components if c['role'] in BODY_ROLES]
    neighbours = [c for c in components if c['role'] == 'neighbour']
    area_by_role = collections.Counter()
    count_by_role = collections.Counter()
    for c in components:
        box_metrics(c['bbox'], width, height, xheight)
        area_by_role[c['role']] += c['area']
        count_by_role[c['role']] += 1
    if sum(area_by_role.values()) > ink_pixels:
        raise ValueError('component census exceeds observed ink')
    text_pixels = sum(c['area'] for c in text)
    text_box = box_metrics(tight_box(text), width, height, xheight)
    row_box = tight_box(text, labels=labels, angle_deg=angle_deg, centre=(width/2, height/2))
    row_frame = None
    if row_box is not None:
        x0, y0, x1, y1 = row_box
        corners = [[x0,y0], [x1,y0], [x1,y1], [x0,y1]]
        if angle_deg != 0:
            c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
            corners = [[c*(x-width/2)-s*(y-height/2)+width/2,
                        s*(x-width/2)+c*(y-height/2)+height/2] for x,y in corners]
        row_frame = dict(angle_deg=angle_deg, length=x1-x0, height=y1-y0, corners=corners)
    body_box = box_metrics(tight_box(bodies), width, height, xheight)
    letters = [c for c in components if c['role'] == 'letter']
    def median(values):
        values = sorted(values)
        if not values:
            return None
        n = len(values)
        return (values[(n-1)//2]+values[n//2])/2
    letter_width = median([c['bbox'][2]-c['bbox'][0] for c in letters])
    letter_height = median([c['bbox'][3]-c['bbox'][1] for c in letters])
    warnings = []
    if height > width:
        warnings.append('vertical_shaped_crop: horizontal band interpretation is unqualified')
    if xheight_source in ('prior', 'letter_width'):
        warnings.append('xheight_is_prior_or_width_proxy')
    if support_count < 4:
        warnings.append('sparse_band_support')
    if not letters:
        warnings.append('no_letter_components')
    if neighbours:
        warnings.append('neighbour_roles_are_tool_hypotheses_not_certified_ownership')
    return dict(segment=dict(width=width, height=height, aspect=width/height,
                             short_long=min(width,height)/max(width,height)),
                all_ink_box=box_metrics(ink_box,width,height,xheight),
                candidate_text_box=text_box, row_frame_text_box=row_frame, letter_component_box=body_box,
                neighbour_box=box_metrics(tight_box(neighbours),width,height,xheight),
                xheight_px=xheight, xheight_source=xheight_source, band_support=support_count,
                median_letter_component_width_px=letter_width,
                median_letter_component_height_px=letter_height,
                role_counts=dict(count_by_role), role_pixels=dict(area_by_role),
                total_ink_pixels=ink_pixels, candidate_text_pixels=text_pixels,
                text_ink_fraction_of_segment=text_pixels/(width*height),
                neighbour_ink_fraction=sum(c['area'] for c in neighbours)/ink_pixels if ink_pixels else None,
                rule_ink_fraction=area_by_role['rule']/ink_pixels if ink_pixels else None,
                unclassified_ink_pixels=ink_pixels-sum(area_by_role.values()),
                chars_per_text_width_xheight=chars/(text_box['width']/xheight)
                    if text_box and xheight else None,
                chars_times_typical_component_width_over_text_width=chars*letter_width/text_box['width']
                    if text_box and letter_width else None,
                warnings=warnings,
                interpretation='component roles and target band are hypotheses; no KEEP/DROP decision')


def preflight(review, population, toolkit):
    rows = review['reviewed']
    if len(rows) != 136 or len({r['index'] for r in rows}) != 136:
        raise ValueError('this bounded run requires the frozen 136-row reviewed frame')
    if any(r['verdict'] not in ('KEEP','DROP') for r in rows):
        raise ValueError('unresolved owner verdict')
    paths = []
    for row in rows:
        image = population['inspection_images'][str(row['index'])]
        path = ROOT/'population-images'/(image['sha256']+'.png')
        if not path.is_file():
            raise ValueError('missing native inspection image: '+str(path))
        paths.append(path)
    source_files = [toolkit/name for name in ['greekocr/glyphs/components.py', 'greekocr/annotate/font.py',
        'greekocr/glyphs/orientation.py', 'greekocr/glyphs/orientation_guides.py',
        'greekocr/glyphs/page_font.py', 'greekocr/pages/font.py']]
    return dict(rows=len(rows), owner_verdicts=dict(collections.Counter(r['verdict'] for r in rows)),
                total_native_pixels=int(sum(r['width']*r['height'] for r in rows)),
                maximum_crop_pixels=int(max(r['width']*r['height'] for r in rows)),
                source_files={str(p):sha(p) for p in source_files},
                image_paths=[str(p) for p in paths],
                reused_functions=['greekocr.glyphs.components.line_glyphs',
                                  'greekocr.glyphs.orientation.measure_orientation (no OSD/OCR)',
                                  'greekocr.glyphs.orientation.QuarterTurn.image / matrix',
                                  'greekocr.annotate.font.font_estimate (abstains without model)'])


def run(args):
    review_path = ROOT/args.review
    population_path = ROOT/'review-data/population.json'
    review = json.loads(review_path.read_text())
    population = json.loads(population_path.read_text())
    toolkit = Path(args.toolkit).resolve()
    orientation_review_path=ROOT/'review-data/glyph-orientation-review.json'
    orientation_review=json.loads(orientation_review_path.read_text())
    orientation_rows={r['id']:r for r in orientation_review['rows']}
    if len(orientation_rows)!=len(orientation_review['rows']):
        raise ValueError('duplicate orientation review identities')
    plan = preflight(review,population,toolkit)
    receipt = dict(schema='segment-glyph-box-experiment-v2', status='prepared',
                   review_sha256=sha(review_path), population_sha256=sha(population_path),
                   adapter_sha256=sha(__file__), toolkit=str(toolkit), plan=plan,
                   orientation_review_sha256=sha(orientation_review_path),
                   no_new_ocr=True, no_admission_changes=True,
                   limits=dict(single_worker=True, seconds=args.time_limit_seconds, rows=136))
    if not args.execute:
        print(json.dumps({k:v for k,v in receipt.items() if k!='plan'} |
                         {'plan':{k:v for k,v in plan.items() if k!='image_paths'}},indent=2))
        return
    for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        os.environ[variable]='1'
    sys.path.insert(0,str(toolkit))
    import cv2
    import numpy as np
    import scipy
    from PIL import Image, __version__ as pillow_version
    from greekocr.glyphs.components import line_glyphs
    from greekocr.annotate.font import font_estimate
    from greekocr.glyphs.orientation import measure_orientation, QuarterTurn
    cv2.setNumThreads(1)
    receipt['dependencies']=dict(python=sys.version.split()[0],numpy=np.__version__,
                                 scipy=scipy.__version__,pillow=pillow_version,opencv=cv2.__version__)
    def timeout(signum,frame):
        raise TimeoutError('bounded experiment time limit reached')
    signal.signal(signal.SIGALRM,timeout)
    signal.setitimer(signal.ITIMER_REAL,args.time_limit_seconds)
    started=time.perf_counter();results=[]
    try:
        for row,path in zip(review['reviewed'],plan['image_paths']):
            record=population['inspection_images'][str(row['index'])]
            if sha(path)!=record['sha256']:
                raise ValueError('native image hash mismatch: '+str(path))
            with Image.open(path) as image:
                image.load()
                if list(image.size)!=[int(row['width']),int(row['height'])]:
                    raise ValueError('native crop dimensions disagree with frozen box')
                with warnings.catch_warnings(record=True) as tool_warnings:
                    warnings.simplefilter('always')
                    reviewed_orientation=orientation_rows.get(row['id'])
                    if reviewed_orientation and reviewed_orientation['image_sha256']!=record['sha256']:
                        raise ValueError('orientation review native hash mismatch: '+row['id'])
                    normalized, measurement_frame = orient_crop(image, row['class'], measure_orientation, QuarterTurn,reviewed_orientation)
                    g=line_glyphs(normalized)
                yy,xx=np.nonzero(g.ink)
                ink_box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None
                components=[dict(index=int(c.index),bbox=[int(c.x0),int(c.y0),int(c.x1),int(c.y1)],role=c.role,area=int(c.area),
                                 touches=list(c.touches)) for c in g.components]
                features=features_from_observation(width=g.width,height=g.height,components=components,
                    ink_box=ink_box,ink_pixels=int(g.ink.sum()),xheight=float(g.band.xh),
                    xheight_source=g.band.xh_source,support_count=g.band.n_support,chars=row['chars'])
                font=font_estimate(normalized).to_dict()
                results.append(dict(index=row['index'],id=row['id'],key=row['key'],book_id=row['id'].rsplit('--s',1)[0],
                    owner_verdict=row['verdict'],verdict_basis=row['verdict_basis'],
                    source=row['source'],content_class=row['class'],google_characters=row['chars'],
                    previous_deviation=row['deviations'][0],image=record,
                    font_family=font,font_family_reason='No qualified real-scan font model supplied',
                    tool_warnings=[dict(kind=w.category.__name__,message=str(w.message)) for w in tool_warnings],
                    measurement_frame=measurement_frame,features=features,components=components))
        receipt['status']='measured'
    except Exception as exc:
        receipt['status']='incomplete';receipt['error']=str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        receipt.update(elapsed_seconds=time.perf_counter()-started,measured_rows=len(results),rows=results)
        output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('rows','plan')},indent=2))
    if receipt['status']!='measured':
        raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--review',default='.local/reviewed-rejection-counts.json')
    p.add_argument('--toolkit',default=str(ROOT.parent/'greek-ocr-toolkit-sol-recut'))
    p.add_argument('--output',default='qa/glyph-box-experiment.json')
    p.add_argument('--time-limit-seconds',type=int,default=120)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    if not 1<=args.time_limit_seconds<=120:
        p.error('time limit must be 1–120 seconds')
    run(args)
