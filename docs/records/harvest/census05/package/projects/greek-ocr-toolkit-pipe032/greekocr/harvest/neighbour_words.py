"""Read-only original-crop geometry and historical component-run diagnostics.

The components/runs proxy is unqualified and never an admission predicate.
No recognizer, painting, recropping, network, or collector cache writes.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from greekocr.glyphs.foreign_ink import PARAMETERS, prepare_mask_page, _centre_fit
from greekocr.glyphs.components import EIGHT
HISTORICAL_LINE_GAP_XH = 3.  # archival diagnostic only; never a word boundary

PARAMS_SHA = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'
DEFAULTS = dict(min_components=4, min_width_xh=3., min_height_xh=.6)
RUN_ROOT = Path.home() / 'Projects/collect-v3-data/run'
CACHE = Path(__file__).resolve().parents[2] / 'docs/records/harvest/collect_v3_admission/nw1b/cache'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen():
    actual = hashlib.sha256(json.dumps(PARAMETERS, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if actual != PARAMS_SHA:
        raise ValueError('foreign-ink parameters changed')
    return actual


def components(page, own, others, box):
    """Historical clipped-CC diagnostic; not a whole-word measurement."""
    from .geometry_observations import measure_foreign
    observation = measure_foreign(page, own, others, box)
    if observation['status'] != 'measured':
        raise ValueError(observation['reason'])
    mask = observation['mask']
    labels, _ = ndi.label(mask, structure=EIGHT)
    result = []
    for label_id, sl in enumerate(ndi.find_objects(labels), 1):
        sy, sx = sl
        x0, y0, x1, y1 = sx.start+box[0], sy.start+box[1], sx.stop+box[0], sy.stop+box[1]
        native_ids = np.unique(page.labels[y0:y1, x0:x1][labels[sy, sx] == label_id])
        native = [page.objects[int(i)-1] for i in native_ids if i]
        full_height = max((s[0].stop-s[0].start for s in native), default=y1-y0)
        half_only = (y0 == box[1] or y1 == box[3]) and (y1-y0) <= .5*full_height
        result.append(dict(box=[x0, y0, x1, y1], height_xh=(y1-y0)/own.xh,
                           half_only=half_only))
    return result


def runs(measurement, *, min_components=4, min_width_xh=3., min_height_xh=.6):
    """Historical F2 proxy for calibration diagnostics only; no qualification."""
    if min_components < 1 or min_width_xh <= 0 or min_height_xh <= 0:
        raise ValueError('positive neighbour_words thresholds required')
    xh = measurement.get('xheight')
    if not xh:
        return []
    eligible = [c for c in measurement['components']
                if not c['half_only']]
    # Horizontal component graph: overlapping vertical extents, separated by no
    # more than the archival line-following stop. Never used by CP4.
    parents = list(range(len(eligible)))
    def root(i):
        while parents[i] != i:
            i = parents[i]
        return i
    for i, a in enumerate(eligible):
        ax0, ay0, ax1, ay1 = a['box']
        for j in range(i):
            bx0, by0, bx1, by1 = eligible[j]['box']
            if min(ay1, by1) > max(ay0, by0) and max(ax0-bx1, bx0-ax1, 0) <= HISTORICAL_LINE_GAP_XH*xh:
                parents[root(i)] = root(j)
    groups = {}
    for i, c in enumerate(eligible):
        groups.setdefault(root(i), []).append(c)
    result = []
    for group in groups.values():
        box = [min(c['box'][0] for c in group), min(c['box'][1] for c in group),
               max(c['box'][2] for c in group), max(c['box'][3] for c in group)]
        width = (box[2]-box[0])/xh
        median_height = float(np.median([c['height_xh'] for c in group]))
        if len(group) >= min_components and width >= min_width_xh and median_height >= min_height_xh:
            result.append(dict(components=len(group), width_xh=width,
                               median_height_xh=median_height,
                               min_height_xh=min(c['height_xh'] for c in group), box=box))
    return sorted(result, key=lambda r: (-r['components'], -r['width_xh'], r['box']))


def page_measurements(records, *, run_root=RUN_ROOT, cache=None):
    """Consume completed geometry only. Missing preparation is never performed."""
    from .geometry_observations import load_cached_page, observe_crop
    frozen()
    page_id = records[0]['page_id']
    if Path(page_id).name != page_id:
        raise ValueError('unsafe page_id')
    if any(r['page_id'] != page_id for r in records):
        raise ValueError('mixed page identities')
    candidates = list(Path(run_root).glob('*/pages/' + page_id + '.json'))
    if len(candidates) != 1:
        raise ValueError('missing/ambiguous page metadata: ' + page_id)
    metadata = json.loads(candidates[0].read_text())
    if metadata['id'] != page_id or metadata['status'] != 'completed':
        raise ValueError('incomplete/mismatched page metadata')
    cache_root = Path(cache) if cache is not None else Path(run_root)/'cache/g1b'
    page = load_cached_page(metadata['image'], cache_root/page_id, metadata['image_sha256'])
    result = {}
    for r in records:
        if r.get('image_sha256', metadata['image_sha256']) != metadata['image_sha256']:
            raise ValueError('record source hash mismatch')
        result[r['row_id']] = observe_crop(page, r['crop_bbox'],
                                          target_row_id=r.get('geometry_row_id'))
    return result


def measure_rows(records, **kwargs):
    groups, result = {}, {}
    for index, row in enumerate(records):
        key = str(row.get('row_id', row.get('id', f'missing:{index}')))
        if not all(row.get(k) is not None for k in ('row_id','page_id','crop_bbox')):
            result[key] = dict(status='unavailable', matched=False,
                               reason='missing_record_fields', components=[], xheight=None)
        else:
            groups.setdefault(row['page_id'], []).append(row)
    for rows in groups.values():
        try:
            result.update(page_measurements(rows, **kwargs))
        except (ValueError, OSError, KeyError, TypeError) as error:
            for row in rows:
                result[row['row_id']] = dict(status='unavailable', matched=False,
                    reason=f'{type(error).__name__}: {error}', components=[], xheight=None)
    return result


# Explicit development word proxy, NOT lexical truth or a qualified setting.
# The gap scale is the
# existing oriented_page._word_boxes empty-gap scale, applied to the saved
# row's original body profile rather than thresholding a crop again.
WORD_PROXY = dict(min_bodies=1, min_width_xh=.2, min_body_height_xh=.8,
                  word_gap_xh=.35)


def validate_recorded_word(page,row,record):
    """Verify an existing response token's geometry; no recognition or text rule.

    Recorded geometry corroborates a complete native body when saved guides
    pass through only part of a capital. It cannot override clipping or joins.
    """
    from .geometry_observations import sha
    binding=page['binding']
    if (record['source_sha256']!=binding['source_sha256'] or
            Path(record['source']).resolve()!=Path(binding['source']) or
            sha(record['response'])!=record['response_sha256'] or
            record['geometry_row_id']!=row['row_id']):
        raise ValueError('recorded_word_binding_mismatch')
    document=json.loads(Path(record['response']).read_text())['document']
    token=document['pages'][0]['tokens'][record['token_index']]
    vertices=token['layout']['boundingPoly']['vertices']
    box=[min(v['x'] for v in vertices),min(v['y'] for v in vertices),
         max(v['x'] for v in vertices),max(v['y'] for v in vertices)]
    if box!=record['recorded_box']: raise ValueError('recorded_word_geometry_mismatch')
    return dict(response_sha256=record['response_sha256'],token_index=record['token_index'],
                source_sha256=binding['source_sha256'],row_id=row['row_id'],box=box)


def row_word_evidence(page, row, box, row_support, *, params=None, foreign_mask=None, recorded_word=None):
    """Letters in THIS neighbour's saved row context, before crop clipping.

    No fit, binarization, clipped-CC relabel or target-line letter count. Native
    parent ids survive letter_boxes' middle-region split/merge machinery.
    Guide visibility and original letter extent must BOTH be complete. Gaps
    come from BoundaryEvidence on assigned body ink; a whole group is tested,
    so clipping one end cannot turn an interior substring into a whole word.
    """
    from greekocr.glyphs.components import Band, Component, LineGlyphs
    from greekocr.glyphs.letters import letter_boxes
    from greekocr.glyphs.lines_api import straighten_edges
    from greekocr.pages.boundaries import BoundaryEvidence
    params = dict(WORD_PROXY if params is None else params)
    if (set(params) != set(WORD_PROXY) or any(v <= 0 for v in params.values())
            or params['min_bodies'] != 1):
        raise ValueError('invalid_word_proxy_parameters')
    a,b = row['x0'],row['x1']; xh = row['xheight']
    yy,xx = row['_y'],row['_x']-a
    if not len(xx):
        return dict(row_id=row['row_id'], xheight=xh, groups=[], profile_runs=[], profile_gaps=[])
    # Full original assigned extent, not the crop. CP3's existing boundary
    # rule criteria exclude native rules/tall non-text, shared with this screen.
    t,bot = int(yy.min()),int(yy.max())+1
    labels = np.zeros((bot-t,b-a),dtype=page['labels'].dtype)
    excluded = set(row_support['excluded_component_ids'])
    ids = page['labels'][yy,xx+a]
    good = ~np.isin(ids,list(excluded))
    labels[yy[good]-t,xx[good]] = ids[good]
    comps=[]
    for cid, sl in enumerate(ndi.find_objects(labels),1):
        if sl is None: continue
        sy,sx=sl
        comps.append(Component(cid,sx.start,sy.start,sx.stop,sy.stop,
            int((labels[sl]==cid).sum()),0,0,0.,0.,0.,(),role='letter'))
    band=Band(row['meanline']-t,row['baseline']-t,xh,0,xh_source='recorded_row')
    ink=labels>0
    glyphs=LineGlyphs(np.where(ink,0.,255.),ink,labels,comps,band,255.,0.,1.,xh,
                      np.empty((0,0)))
    letters=letter_boxes(glyphs)
    # A middle-region split is not necessarily two native letters: e.g. the
    # two arcs of Ο. Unite unsplit boxes sharing parents; retain actual toolkit
    # bridge splits (merged>1) and partition their full parent ink explicitly.
    from dataclasses import replace
    split_parents={cid for l in letters if l.merged>1 for cid in l.components}
    united=[]
    for letter in letters:
        matches=[i for i,l in enumerate(united) if l.merged==letter.merged==1
                 and not (set(l.components)|set(letter.components))&split_parents
                 and set(l.components)&set(letter.components)]
        if matches:
            at=matches[0]; old=united[at]
            united[at]=replace(old,x0=min(old.x0,letter.x0),x1=max(old.x1,letter.x1),
                y0=min(old.y0,letter.y0),y1=max(old.y1,letter.y1),
                components=tuple(sorted(set(old.components)|set(letter.components))),
                pieces=old.pieces+letter.pieces,resolved=old.resolved and letter.resolved)
        else: united.append(letter)
    letters=sorted(united,key=lambda l:l.x0)
    # Assign every original parent pixel once. Shared-parent bridge splits use
    # their toolkit cut intervals, extended to infinity at the outer edges.
    # Thus overhang is preserved and no joined parent is required to fit each
    # individual child. Per-child provenance conserves the full parent ink.
    assigned=[np.zeros_like(labels,dtype=bool) for _ in letters]
    pixels=[[] for _ in letters]
    if '_native_objects' not in page:
        page['_native_objects']=ndi.find_objects(page['labels'])
    for cid in {c for l in letters for c in l.components}:
        owners=[i for i,l in enumerate(letters) if cid in l.components]
        sy,sx=page['_native_objects'][cid-1]
        py,px=np.nonzero(page['labels'][sy,sx]==cid)
        py+=sy.start; px+=sx.start
        if len(owners)==1:
            pixels[owners[0]].append((py,px))
        else:
            edges=[a+letters[i].x1 for i in owners[:-1]]
            slots=np.searchsorted(edges,px,side='right')
            for j,i in enumerate(owners):
                at=slots==j; pixels[i].append((py[at],px[at]))
    native_by_letter={}
    for i,l in enumerate(letters):
        py=np.concatenate([v[0] for v in pixels[i]])
        px=np.concatenate([v[1] for v in pixels[i]])
        inside=(py>=t)&(py<bot)&(px>=a)&(px<b)
        assigned[i][py[inside]-t,px[inside]-a]=True
        native_by_letter[id(l)]=(assigned[i],py,px)
    word_binding = validate_recorded_word(page,row,recorded_word) if recorded_word else None
    local_row=dict(row,x0=0,x1=b-a,meanline=band.top,baseline=band.bottom,
                   top=row['top']-t,bottom=row['bottom']-t)
    profile=BoundaryEvidence(glyphs.gray,[local_row],original_ink=ink)
    occupied,gaps=profile.profile(0)
    # Ordered, adjacent letters in ONE row only. No anonymous pairwise graph.
    groups=[]
    for letter in letters:
        if groups:
            left=groups[-1][-1]
            boundary=any(e-s >= params['word_gap_xh']*xh and
                         s >= left.x1 and e <= letter.x0 for s,e in gaps)
        else: boundary=True
        if boundary: groups.append([])
        groups[-1].append(letter)
    evidence=[]
    for group in groups:
        details=[]
        for letter in group:
            lx0,lx1=letter.x0,letter.x1
            native,ny,nx=native_by_letter[id(letter)]
            native_box=([int(nx.min()),int(ny.min()),int(nx.max())+1,int(ny.max())+1]
                        if len(nx) else [a+lx0,t+letter.y0,a+lx1,t+letter.y1])
            parent=native[:,lx0:lx1]
            ys,xs=np.nonzero(parent & (np.arange(bot-t)[:,None]>=band.top[lx0:lx1]) &
                             (np.arange(bot-t)[:,None]<band.bottom[lx0:lx1]))
            cols=np.unique(xs)+lx0
            body_height=(int(np.ptp(ys))+1)/xh if len(ys) else 0.
            guide_complete=bool(len(cols) and np.all(row['meanline'][cols]>=box[1]) and
                                 np.all(row['baseline'][cols]<=box[3]))
            extent_complete=(bool(len(nx)) and box[0]<=native_box[0] and native_box[2]<=box[2] and
                             box[1]<=native_box[1] and native_box[3]<=box[3])
            # Response vertices are pixel endpoints; native boxes are half-open.
            word_supported=bool(word_binding and
                word_binding['box'][0]<=native_box[0] and native_box[2]<=word_binding['box'][2]+1 and
                word_binding['box'][1]<=native_box[1] and native_box[3]<=word_binding['box'][3]+1 and
                (native_box[3]-native_box[1])>=params['min_body_height_xh']*xh)
            # Frozen ownership is diagnostic, not a short-word veto: its
            # existing neighbour selector can exclude narrow row extents.
            foreign_fraction = None
            if foreign_mask is not None and guide_complete and extent_complete and len(ys):
                py,px=ys+t,xs+lx0+a
                inside=(px>=box[0])&(px<box[2])&(py>=box[1])&(py<box[3])
                foreign_fraction=float(foreign_mask[py[inside]-box[1],px[inside]-box[0]].sum()/len(ys))
            details.append(dict(foreign_body_fraction=foreign_fraction,box=native_box,
                middle_box=[a+lx0,t+letter.y0,a+lx1,t+letter.y1],
                assigned_native_pixels=len(ny),
                assigned_native_sha256=hashlib.sha256(np.column_stack((ny,nx)).tobytes()).hexdigest(),
                shared_parent_split=bool(letter.split),recorded_word_support=word_supported,
                native_component_ids=list(map(int,letter.components)),
                resolved=bool(letter.resolved and len(nx)),merged=int(letter.merged),pieces=int(letter.pieces),
                body_height_xh=body_height,guide_complete=guide_complete,
                extent_complete=bool(extent_complete),
                complete=bool(guide_complete and extent_complete and
                              (body_height>=params['min_body_height_xh'] or word_supported))))
        extent=[min(d['box'][0] for d in details),min(d['box'][1] for d in details),
                max(d['box'][2] for d in details),max(d['box'][3] for d in details)]
        intersects=extent[0]<box[2] and box[0]<extent[2] and extent[1]<box[3] and box[1]<extent[3]
        if not intersects: continue
        complete=all(d['complete'] for d in details)
        resolved=all(d['resolved'] for d in details)
        width=(extent[2]-extent[0])/xh
        evidence.append(dict(box=extent,letters=details,body_count=len(details),width_xh=width,
            complete=complete,resolved=resolved,
            positive=bool(complete and resolved and len(details)>=params['min_bodies'] and
                          width>=params['min_width_xh']),
            unresolved=bool(any(not d['assigned_native_pixels'] for d in details) or
                            (all(d['guide_complete'] and d['extent_complete'] for d in details) and
                            (not complete or not resolved or width<params['min_width_xh'])))))
    shared=slice(max(0,box[0]-a),min(b-a,box[2]-a))
    above,below=(straighten_edges(row['baseline'][shared]-box[1],xh,box[3]-box[1])
                 if shared.stop>shared.start else (np.zeros(0,bool),np.zeros(0,bool)))
    return dict(row_id=row['row_id'],column_id=row['column_id'],block_id=row['block_id'],
        xheight=float(xh),groups=evidence,excluded_component_ids=sorted(excluded),
        recorded_word_binding=word_binding,
        profile_runs=[[s+a,e+a] for s,e in occupied],profile_gaps=[[s+a,e+a] for s,e in gaps],
        directional_missing=dict(above=int(above.sum()),below=int(below.sum())))


def neighbour_word_evidence(page, box, *, target_row_id=None, params=None):
    """CP4 candidate only. Missing/ambiguous evidence never certifies KEEP.

    Structural multi-row positives can resolve the union before an owner is
    selected. For neighbour evidence, require one explicit/unique complete
    target and a supported same-column neighbour. Ownership remains frozen
    inferred geometry; this function makes no independent semantic truth claim.
    """
    from .row_inclusion import supported_rows
    frozen()
    structural=supported_rows(page,box)
    result=dict(status='unresolved',reason=None,neighbour_drop=None,
        merged=structural.get('merged'),union_drop=None,row_inclusion=structural,
        rows=[],params=dict(WORD_PROXY if params is None else params),
        decision_status='unqualified_cp4')
    if structural['status']!='measured':
        return dict(result,status='unavailable',reason=structural['reason'])
    if target_row_id is None:
        candidates=structural['supported_row_ids']
        if len(candidates)!=1:
            return dict(result,reason='ambiguous_target' if candidates else 'missing_target',
                        union_drop=True if structural['merged'] else None)
        target_row_id=candidates[0]
    own=[r for r in page['rows'] if r['row_id']==target_row_id]
    if len(own)!=1:
        return dict(result,reason='missing_or_ambiguous_target')
    own=own[0]
    if not page['ownership'].box_hits(own,box).any():
        return dict(result,reason='unsupported_target')
    from .geometry_observations import invalid_geometry_dependencies
    if invalid_geometry_dependencies(page,box,target_row_id=target_row_id):
        return dict(result,status='unavailable',reason='invalid_geometry')
    side=page['structure'][target_row_id].get('page_side')
    candidates=[r for r in page['rows'] if r['row_id']!=target_row_id and
        r['column_id']==own['column_id'] and page['structure'][r['row_id']].get('page_side')==side]
    if not candidates:
        return dict(result,reason='missing_neighbour')
    supports={r['row_id']:r for r in structural['rows']}
    from .geometry_observations import measure_foreign
    foreign=measure_foreign(page,own,candidates,box)
    if foreign['status']!='measured':
        return dict(result,status='unavailable',reason=foreign['reason'])
    rows=[row_word_evidence(page,r,box,supports[r['row_id']],params=params,foreign_mask=foreign['mask']) for r in candidates
          if page['ownership'].box_hits(r,box).any()]
    positive=any(g['positive'] for r in rows for g in r['groups'])
    unresolved=any(g['unresolved'] for r in rows for g in r['groups'])
    drop=True if positive else None if unresolved else False
    return dict(result,status='unresolved' if unresolved and not positive else 'measured',
        reason='ambiguous_letters_or_extent' if unresolved and not positive else None,
        target_row_id=target_row_id,rows=rows,neighbour_drop=drop,
        foreign_mask_sha256=hashlib.sha256(foreign['mask'].tobytes()).hexdigest(),
        union_drop=True if structural['merged'] or positive else drop)
