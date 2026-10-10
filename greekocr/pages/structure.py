"""Addresses over frozen line geometry, in TOPLEFT source-image pixels.

IDs are local to one image. A row is a printed line inside one physical leaf,
column and block, not a semantic table grid row. Null lateral neighbours mean
the end of that row. No text, PDF layer, or evaluation annotations are read.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw

from .lines import CURVES

__all__ = ['build_structure', 'join_pieces', 'delivery_records', 'render_structure']
ADDRESS = ('page_side', 'column_id', 'block_id', 'row_id', 'piece_index', 'reading_order')


TABLE_BODY_HEIGHT_XH = 0.5  # x-heights: require a body-sized component to establish a table row.
BINARIZE_MIN_PIXELS = 15  # source pixel samples: minimum odd threshold window on small images.
HOUGH_HALF_TURN_STEPS = 1800  # angular samples per half-turn: resolve long thin table separators.
RULE_VOTE_LENGTH_XH = 4  # x-heights: require sustained votes before promoting a separator.
RULE_MIN_LENGTH_XH = 8  # x-heights: exclude individual stems from table rules.
RULE_MAX_GAP_XH = 0.3  # x-heights: bridge short breaks in a printed rule.
RULE_MAX_SLOPE = 0.12  # page x units per y unit: table columns need near-vertical rules.
RULE_SEARCH_RADIUS_XH = 0.2  # x-heights: inspect original ink around the Hough path.
RULE_MIN_INK_SHARE = 0.85  # dimensionless path share: rule evidence must be continuous original ink.
RULE_RADIUS_XH = 0.16  # x-heights: record a narrow printed-rule corridor.
RULE_DUPLICATE_DISTANCE_XH = 0.5  # x-heights: consolidate nearby observations of one printed rule.
GUTTER_MIN_WIDTH_XH = 0.75  # x-heights: a persistent table gutter must exceed a narrow word slit.
GUTTER_COMMON_WIDTH_XH = 0.25  # x-heights: require a shared lane across consecutive whitespace windows.
GUTTER_MIN_HEIGHT_XH = 18  # x-heights: narrow lanes need repeated rows before becoming column boundaries.
GUTTER_WIDE_WIDTH_XH = 2  # x-heights: a wider lane can use shorter vertical support.
GUTTER_WIDE_HEIGHT_XH = 8  # x-heights: still require multiple rows for a wide lane.
GUTTER_HEADER_PADDING_XH = 0.5  # x-heights: keep whitespace boundaries clear of a spanning header.
GUTTER_REMAINDER_HEIGHT_XH = 4  # x-heights: retain only useful gutter fragments after splitting at headers.
ROW_BASELINE_SLACK_XH = 0.55  # x-heights: facing endpoints must agree before sharing a printed row.
ROW_HORIZONTAL_REACH_XH = 15  # x-heights: row linking requires local horizontal support.
XHEIGHT_DENOMINATOR_FLOOR = 1e-09  # source pixel units: protect a ratio for degenerate caller-supplied geometry.
ROW_GAP_COST = 0.01  # dimensionless distance weight: prefer nearby pieces among matching baselines.
TRACK_REQUIRED_WIDTH_OVERLAP = 0.25  # dimensionless lane width fraction: preserve a shared whitespace corridor.
TRACK_DISTANCE_XH = 0.65  # x-heights: finite observations may describe one separator track.
FOLD_MIN_PAGE_ASPECT = 1.1  # page width per page height: only infer facing leaves on a wide raster.
FOLD_CENTRE_MIN_PAGE = 0.3  # fraction of page width: the inferred fold must be near the scan centre.
FOLD_CENTRE_MAX_PAGE = 0.7  # fraction of page width: upper bound of the central fold search.
REVIEW_HUE_STEP = 0.61803398875  # dimensionless hue turn: separate neighboring row colors in review images.
REVIEW_SATURATION = 0.85  # dimensionless HSV saturation: distinguish row overlays from grayscale ink.
BINARIZE_WINDOW_PAGE = 0.04  # fraction of shorter page dimension: estimate the local paper level.
REVIEW_VALUE = 0.75  # dimensionless HSV value: keep row outlines legible on white paper.

FOLD_STROKE_PAGE_RATIO = 600  # page-width units per stroke width: make the fold visible in a review overlay.
BOUNDARY_STROKE_PAGE_RATIO = 1200  # page-width units per stroke width: draw other separators less prominently.


def _table_structure(page, regions):
    """Recover splitting provenance and stops, without fitting any line curves."""
    from .tables import table_pixels, _row_groups, split_group, rule_ink
    from ..glyphs.components import binarise
    import cv2
    sources = {}; boundaries = []
    gray = np.asarray(page)
    height,width=gray.shape[:2]
    for tid,box in regions:
        a,t,b,bot=map(int,(max(0,np.floor(box[0])),max(0,np.floor(box[1])),
                          min(width,np.ceil(box[2])),min(height,np.ceil(box[3]))))
        p=table_pixels(gray[t:bot,a:b])
        local_boxes=[]
        for ri,row in enumerate(_row_groups(p.components,p.xheight)):
            for group in split_group(row,p.barriers,p.xheight):
                q=np.asarray(group)
                if not np.any(q[:,3]-q[:,1]>=TABLE_BODY_HEIGHT_XH*p.xheight):
                    continue
                bounds=(int(q[:,0].min())+a,int(q[:,1].min())+t,
                        int(q[:,2].max())+a,int(q[:,3].max())+t)
                sources[(str(tid),bounds)]=f'{tid}:component-row-{ri}'
                local_boxes.append(bounds)
        boundaries.extend(_table_gutters(p,a,t,str(tid),local_boxes))
        ink=binarise(p.gray,window=max(BINARIZE_MIN_PIXELS,round(BINARIZE_WINDOW_PAGE*min(p.gray.shape)))|1)
        mask=rule_ink(ink,p.xheight)
        paths=cv2.HoughLinesP(mask.astype('uint8'),1,np.pi/HOUGH_HALF_TURN_STEPS,
            threshold=max(2,round(RULE_VOTE_LENGTH_XH*p.xheight)), minLineLength=RULE_MIN_LENGTH_XH*p.xheight,maxLineGap=RULE_MAX_GAP_XH*p.xheight)
        kept=[]
        for x0,y0,x1,y1 in sorted([] if paths is None else paths.reshape(-1,4).tolist(),
                                   key=lambda q:-abs(q[3]-q[1])):
            if abs(y1-y0)<RULE_MIN_LENGTH_XH*p.xheight or abs(x1-x0)>RULE_MAX_SLOPE*abs(y1-y0):
                continue
            if y1<y0:x0,y0,x1,y1=x1,y1,x0,y0
            yy=np.arange(y0,y1+1)
            xx=np.rint(x0+(x1-x0)*(yy-y0)/(y1-y0)).astype(int)
            hits=np.zeros(len(yy),bool)
            for dx in range(-max(1,round(RULE_SEARCH_RADIUS_XH*p.xheight)),max(1,round(RULE_SEARCH_RADIUS_XH*p.xheight))+1):
                at=np.clip(xx+dx,0,ink.shape[1]-1)
                hits |= ink[yy,at]
            # The split mask also contains safe proposals through aligned
            # letter stems. A column rule needs continuous original ink.
            if hits.mean()<RULE_MIN_INK_SHARE:
                continue
            r=_boundary('rule',x0+a,y0+t,x1+a,y1+t,
                radius=RULE_RADIUS_XH*p.xheight,source='table-rule',table_id=str(tid))
            if any(abs(_x(q,(y0+y1)/2+t)-(x0+x1)/2-a)<RULE_DUPLICATE_DISTANCE_XH*p.xheight
                   and q['path'][0][1]<=y0+t+p.xheight
                   and q['path'][-1][1]>=y1+t-p.xheight for q in kept):
                continue
            kept.append(r)
        boundaries.extend(kept)
    return sources,boundaries


def _table_gutters(p,dx,dy,tid,boxes):
    """Promote persistent whitespace lanes, not every conservative word split."""
    xh=p.xheight;groups=[]
    for rect in sorted(p.gutters,key=lambda r:r[1]):
        a,t,b,bot=rect
        if b-a<GUTTER_MIN_WIDTH_XH*xh:
            continue
        found=None
        for group in groups:
            # A common horizontal interval prevents a chain of moving word
            # gaps from becoming a fictitious broad column gutter.
            left=max(r[0] for r in group);right=min(r[2] for r in group)
            if min(right,b)-max(left,a)>=GUTTER_COMMON_WIDTH_XH*xh and t<=max(r[3] for r in group):
                found=group;break
        if found is None:groups.append([rect])
        else:found.append(rect)
    result=[]
    for group in groups:
        top=min(r[1] for r in group);bottom=max(r[3] for r in group)
        left=max(r[0] for r in group);right=min(r[2] for r in group)
        if bottom-top<GUTTER_MIN_HEIGHT_XH*xh and not (right-left>=GUTTER_WIDE_WIDTH_XH*xh and bottom-top>=GUTTER_WIDE_HEIGHT_XH*xh):
            continue
        centre=(left+right)/2+dx
        # A spanning header interrupts whitespace evidence. Preserve that
        # interruption rather than extrapolating a gutter through its letters.
        spans=[(top+dy,bottom+dy)]
        for a,t,b,bot in boxes:
            if not a<centre<b:continue
            lo,hi=t-GUTTER_HEADER_PADDING_XH*xh,bot+GUTTER_HEADER_PADDING_XH*xh
            spans=[v for start,end in spans for v in ((start,min(end,lo)),(max(start,hi),end)) if v[1]>v[0]]
        for top,bottom in spans:
            if bottom-top<GUTTER_REMAINDER_HEIGHT_XH*xh:continue
            result.append(_boundary('gutter',centre,top,centre,bottom,width=right-left,
                source='persistent-table-whitespace',table_id=tid,
                supporting_windows=[list(r) for r in group]))
    return result


def _attach_structure(result, pieces=(), *, boundaries=()):
    """Attach the same record-level schema to the in-memory detector objects."""
    height,width=result.pixels.gray.shape
    lines=[l.to_record() for l in result.lines]
    cells=[p.to_record(i,(width,height),(width,height)) for i,p in enumerate(pieces)]
    result.structure=build_structure(lines,cells,(width,height),gutters=result.pixels.gutters,
                                    rules=result.pixels.column_boundaries,boundaries=boundaries,
                                    page=result.pixels.gray)
    for obj,record in zip(result.lines,lines):
        obj.address={k:record[k] for k in ADDRESS}
        obj.neighbours.update({k:record['neighbours'][k] for k in ('left','right')})
    for obj,record in zip(pieces,cells):
        obj.address={k:record[k] for k in (*ADDRESS,'neighbours')}


def _x(boundary, y):
    return np.interp(y, [p[1] for p in boundary['path']], [p[0] for p in boundary['path']])


def _boundary(kind, x0, y0, x1, y1, **extra):
    return dict(kind=kind, path=[[float(x0), float(y0)], [float(x1), float(y1)]], **extra)


def _crosses(line, boundary):
    """Test the complete curved ribbon against a finite boundary centre path.

    Curve samples represent pixel centres; x1 is exclusive. Boundary thickness
    is retained as evidence but crossing means occupying both sides, not merely
    touching the edge of a stroke or a whitespace lane.
    """
    top, bottom = boundary['path'][0][1], boundary['path'][-1][1]
    a = max(top, min(line['top']))
    b = min(bottom, max(line['bottom']))
    if b <= a:
        return False
    ys = np.linspace(a, b, max(2, int(np.ceil(b-a))+1))
    xs = _x(boundary, ys)
    sample = np.arange(line['x0'], line['x1'])
    return bool(np.any((xs > line['x0']) & (xs < line['x1']-1)
        & (ys >= np.interp(xs, sample, line['top']))
        & (ys < np.interp(xs, sample, line['bottom']))))


def _combine(ordered):
    joined=deepcopy(ordered[0])
    if len(ordered)==1:
        return joined
    a,b=ordered[0]['x0'],max(p['x1'] for p in ordered)
    for name in CURVES:
        curve=np.full(b-a,np.nan)
        for p in ordered:
            sl=slice(p['x0']-a,p['x1']-a);values=np.asarray(p[name])
            old=curve[sl];overlap=np.isfinite(old)
            if np.any(old[overlap]!=values[overlap]):
                raise ValueError('inconsistent overlapping piece geometry')
            curve[sl]=values
        known=np.flatnonzero(np.isfinite(curve));missing=np.flatnonzero(~np.isfinite(curve))
        curve[missing]=np.interp(missing,known,curve[known])
        joined[name]=curve.tolist()
    joined.update(x0=a,x1=b,piece_index=0)
    joined['neighbours']=dict(left=None,right=None)
    for direction in ('above','below'):
        neighbours=[-1]*(b-a)
        for p in ordered:
            values=p.get('neighbours',{}).get(direction)
            if isinstance(values,list) and len(values)==p['x1']-p['x0']:
                neighbours[p['x0']-a:p['x1']-a]=values
        joined['neighbours'][direction]=neighbours
    joined['geometry_source']='joined-piece-curves'
    joined['xheight']=float(np.median(np.asarray(joined['baseline'])-joined['meanline']))
    joined['support']=sum(p.get('support',0) for p in ordered)
    for key in ('segment_indices','hint_indices','borrowed'):
        joined[key]=sorted({v for p in ordered for v in p.get(key,[])})
    joined['segment_positions']=[list(v) for v in sorted({tuple(v) for p in ordered for v in p.get('segment_positions',[])})]
    return joined


def _row_distance(line, members):
    """Compare facing baseline endpoints, so a curled row can stay curved."""
    distances=[]
    for peer in members:
        left,right=(peer,line) if peer['x0']<=line['x0'] else (line,peer)
        gap=right['x0']-left['x1']
        if gap<0:
            continue
        xh=min(left['xheight'],right['xheight'])
        delta=abs(left['baseline'][-1]-right['baseline'][0])
        if delta<=ROW_BASELINE_SLACK_XH*xh and gap<=ROW_HORIZONTAL_REACH_XH*xh:
            distances.append(delta/max(xh,XHEIGHT_DENOMINATOR_FLOOR)+ROW_GAP_COST*gap/max(xh,XHEIGHT_DENOMINATOR_FLOOR))
    return min(distances,default=float('inf'))


def _tracks(stops, lines):
    """Link overlapping observations of the same separator, preserving paths.

    Windowed whitespace observations must not invent a new column every few
    rows. Tracks only establish identity; all original finite boundary paths
    remain available to the crossing guard and in the structure output.
    """
    xh=float(np.median([l['xheight'] for l in lines])) if lines else 1.
    tracks=[]
    for b in sorted(stops,key=lambda b:(b['kind']!='rule',b['path'][0][1])):
        match=None
        for group in tracks:
            if b.get('table_id')!=group[0].get('table_id') or (b['kind']=='fold')!=(group[0]['kind']=='fold'):
                continue
            for q in group:
                top=max(q['path'][0][1],b['path'][0][1]);bottom=min(q['path'][-1][1],b['path'][-1][1])
                if top>bottom:
                    continue
                ys=np.array([top,(top+bottom)/2,bottom])
                distance=np.max(abs(_x(q,ys)-_x(b,ys)))
                same_whitespace=(b['kind']==q['kind']=='gutter' and
                    distance <= .5*(b.get('width',0)+q.get('width',0))-
                    TRACK_REQUIRED_WIDTH_OVERLAP*min(b.get('width',0),q.get('width',0)))
                if distance<=TRACK_DISTANCE_XH*xh or same_whitespace:
                    match=group;break
            if match is not None:break
        if match is None:
            match=[];tracks.append(match)
        match.append(b)
    for i,group in enumerate(tracks):
        for b in group:b['track_id']=f'separator-{i:04d}'
    return tracks


def _fold(lines, width, height, boundaries):
    # A wide image plus a persistent central separation is evidence of facing
    # leaves, not proof. Callers with scan metadata should supply an explicit
    # fold (or False for a landscape single leaf).
    if width < FOLD_MIN_PAGE_ASPECT*height:
        return None
    candidates = [b for b in boundaries if b['kind'] == 'gutter'
                  and b['path'][0][1] == 0 and b['path'][-1][1] == height
                  and FOLD_CENTRE_MIN_PAGE*width < _x(b, height/2) < FOLD_CENTRE_MAX_PAGE*width]
    active = [l for l in lines if l.get('discounted') is None]
    # Tables discard page gutters in legacy delivery. Derive a persistent
    # empty central lane from the frozen text extents in that case.
    intervals = sorted((l['x0'], l['x1']) for l in active)
    end = 0
    for a, b in intervals:
        if a > end and FOLD_CENTRE_MIN_PAGE*width < (a+end)/2 < FOLD_CENTRE_MAX_PAGE*width:
            candidates.append(_boundary('gutter', (a+end)/2, 0, (a+end)/2, height,
                                        width=a-end, source='frozen-line-extents'))
        end = max(end, b)
    candidates = [b for b in candidates if
                  sum(l['x1'] <= _x(b, height/2) for l in active) >= 3
                  and sum(l['x0'] >= _x(b, height/2) for l in active) >= 3]
    if not candidates:
        return None
    chosen = min(candidates, key=lambda b: abs(_x(b,height/2)/width-.5))
    return dict(deepcopy(chosen), kind='fold', source='inferred-wide-scan-central-separation')


def build_structure(lines: list[dict], pieces: list[dict], image_size: Sequence[int], *,
                    gutters: Sequence = (), rules: Sequence[dict] = (),
                    boundaries: Sequence[dict] = (), fold: dict | bool | None = None,
                    page: Image.Image | np.ndarray | None = None) -> dict:
    """Add addresses to line/cell records in place without changing geometry.

    Gutters are x0,y0,x1,y1 rectangles; rules use centre+slope*(y-height/2).
    Additional boundaries have a kind and a y-ordered pixel path. An explicit
    fold uses that same schema; False forces a single leaf. None infers a fold
    only for a wide scan with a persistent central separation. Table row_source
    is retained before splitting, but hard boundaries always override it.
    With page pixels, proposals must pass line-local spacing or original rule
    ink validation before grouping. Without pixels boundaries are caller-
    supplied constraints, explicitly marked unverified (useful for geometry
    consumers with external boundary annotations).
    """
    width, height = map(int, image_size)
    stops = [deepcopy(b) for b in boundaries if fold is not False or b['kind']!='fold']
    stops += [_boundary('gutter', (a+b)/2, t, (a+b)/2, bot, width=b-a,
                        extent=[a,t,b,bot], source='detector') for a,t,b,bot in gutters]
    stops += [_boundary('rule', r['centre']+r['slope']*(r['top']-height/2), r['top'],
                        r['centre']+r['slope']*(r['bottom']-height/2), r['bottom'],
                        radius=r['radius'], source=r['kind']) for r in rules]
    supplied_fold = next((b for b in stops if b['kind']=='fold'), None)
    leaf_fold = supplied_fold or (None if fold is False else deepcopy(fold) if fold else _fold(lines,width,height,stops))
    if leaf_fold:
        leaf_fold['kind'] = 'fold'
        stops.append(leaf_fold)
    # Remove exact duplicates without merging finite or slanted boundaries.
    unique = []
    for b in stops:
        if not any(b['kind'] == q['kind'] and b['path'] == q['path'] for q in unique):
            unique.append(b)
    stops = unique
    validator = None
    rejected = []
    if page is not None:
        from .boundaries import BoundaryEvidence
        validator = BoundaryEvidence(page, lines)
        if validator.ink.shape != (height,width):
            raise ValueError('page pixels must match image_size')
        for i,b in enumerate(stops):
            b['proposal_id'] = b.get('id', f'proposal-{i:04d}')
        stops, rejected = validator.validate(stops)
    for i,b in enumerate(stops):
        b['id'] = f'boundary-{i:04d}'
    tracks=_tracks(stops,lines)
    line_y=[float(np.median(l['baseline'])) for l in lines]
    active=[(l,y) for l,y in zip(lines,line_y) if l.get('discounted') is None]
    lane_stops=[]
    for b in stops:
        peers=[(l,y) for l,y in active if b['path'][0][1] <= y < b['path'][-1][1]]
        # Marginal whitespace and binding shadows remain recorded evidence,
        # but only separators with text on both sides define text columns.
        if b['kind']=='fold' or (any(l['x1']<=_x(b,y) for l,y in peers)
            and any(l['x0']>=_x(b,y) for l,y in peers)):
            lane_stops.append(b)
    if leaf_fold:
        leaf_fold = next(b for b in stops if b['kind']=='fold')
    pages = []
    for side in (('left','right') if leaf_fold else ('single',)):
        edge_left=[[0.,0.],[0.,float(height)]]
        edge_right=[[float(width),0.],[float(width),float(height)]]
        if side=='left':edge_right=leaf_fold['path']
        if side=='right':edge_left=leaf_fold['path']
        pages.append(dict(id=side,page_side=side,
            boundary_ids=[leaf_fold['id']] if leaf_fold else [],
            polygon=edge_left+edge_right[::-1]))
    by_line = defaultdict(list)
    for i,p in enumerate(pieces):
        li = p['line_index']
        if not 0 <= li < len(lines):
            raise ValueError(f'piece {i}: invalid line_index {li}')
        by_line[li].append(i)
    columns, blocks, rows = {}, {}, {}
    block_rows=defaultdict(list)
    violations = []
    for i,l in enumerate(lines):
        y = line_y[i]
        mid = (l['x0']+l['x1'])/2
        side = ('left' if mid < _x(leaf_fold,y) else 'right') if leaf_fold else 'single'
        relevant = [b for b in lane_stops if b['path'][0][1] <= y < b['path'][-1][1]]
        # Every record is addressed, including rejected audit candidates. A
        # crossing remains an explicit violation, never a fabricated safe lane.
        crossed = [b['id'] for b in stops if _crosses(l,b)]
        if crossed:
            violations.append(dict(line_index=i, boundary_ids=crossed,
                                   discounted=l.get('discounted')))
        left = max((b for b in relevant if _x(b,y) <= mid),
                   key=lambda b: _x(b,y), default=None)
        right = min((b for b in relevant if _x(b,y) > mid),
                    key=lambda b: _x(b,y), default=None)
        # Explicit boundary pair defines the lane; legacy column labels are
        # used only if no boundary exists on either side (indent preservation).
        signature = (side, left['track_id'] if left else 'image-left',
                     right['track_id'] if right else 'image-right')
        if not left and not right and validator is None:
            signature += (l.get('column',0),)
        if signature not in columns:
            cid = f'{side}:column-{len(columns):04d}'
            columns[signature] = dict(id=cid,page_side=side,
                boundary_ids=[b['id'] for b in (left,right) if b],
                left_boundary=deepcopy(left) if left else _boundary('image_edge',0,0,0,height),
                right_boundary=deepcopy(right) if right else _boundary('image_edge',width,0,width,height),
                line_indices=[])
        c = columns[signature]; c['line_indices'].append(i)
        for boundary in (left,right):
            if boundary and boundary['id'] not in c['boundary_ids']:
                c['boundary_ids'].append(boundary['id'])
        tids = {pieces[p].get('table_id') for p in by_line[i] if pieces[p].get('table_id') is not None}
        if len(tids)>1:
            raise ValueError('one line belongs to multiple table regions')
        tid = next(iter(tids),None)
        diagnostic = l.get('discounted') is not None
        block_key = (c['id'],tid,diagnostic)
        if block_key not in blocks:
            blocks[block_key] = dict(id=f"{c['id']}:block-{len(blocks):04d}",
                                    column_id=c['id'],page_side=side,table_id=tid,
                                    kind='diagnostic' if diagnostic else 'table' if tid else 'text',
                                    line_indices=[])
        block = blocks[block_key]; block['line_indices'].append(i)
        # Ordinary frozen whole lines retain one-to-one identity. Pre-split
        # component groups are provenance, not a final row classification:
        # separate seeds on the same printed baseline may regroup in a column.
        source = l.get('row_source') if tid and not diagnostic else None
        row_key = (block['id'],i)
        # A source row is only a proposal. Check the gap geometry as well as
        # each piece before accepting a join; finite/slanted stops can lie in
        # the gap even when the two endpoint addresses agree.
        candidates=[]
        if tid is not None and not diagnostic:
            for key in block_rows[block['id']]:
                members=[lines[j] for j in rows[key]['line_indices']]
                distance=_row_distance(l,members)
                if np.isfinite(distance):
                    candidates.append((source not in rows[key]['row_sources'],distance,key))
        for _,_,key in sorted(candidates):
            candidate=sorted([lines[j] for j in rows[key]['line_indices']]+[l],key=lambda r:r['x0'])
            try:
                merged=_combine(candidate)
                safe=not any(_crosses(merged,b) for b in stops)
            except ValueError:
                safe=False
            if safe:
                row_key=key;break
        if row_key not in rows:
            rows[row_key] = dict(id=f'row-{len(rows):05d}', page_side=side,
                column_id=c['id'],block_id=block['id'],table_id=tid,
                row_source=source,row_sources=[],discounted=diagnostic,line_indices=[],piece_indices=[])
            block_rows[block['id']].append(row_key)
        row = rows[row_key]; row['line_indices'].append(i); row['piece_indices'] += by_line[i]
        if source is not None and source not in row['row_sources']:
            row['row_sources'].append(source)
    col_list = sorted(columns.values(),key=lambda c:(['single','left','right'].index(c['page_side']),
        min(lines[i]['x0'] for i in c['line_indices']), min(min(lines[i]['top']) for i in c['line_indices'])))
    col_order = {c['id']:i for i,c in enumerate(col_list)}
    row_list = sorted(rows.values(),key=lambda r:(col_order[r['column_id']],r['discounted'],
        min(float(np.median(lines[i]['baseline'])) for i in r['line_indices']),
        min(lines[i]['x0'] for i in r['line_indices'])))
    order = 0
    for ri,row in enumerate(row_list):
        row['reading_order'] = ri
        row['line_indices'].sort(key=lambda i:(lines[i]['x0'],i))
        row['piece_indices'].sort(key=lambda i:(pieces[i]['box_pixels'][0],i))
        row['box_pixels'] = [min(lines[i]['x0'] for i in row['line_indices']),
            min(min(lines[i]['top']) for i in row['line_indices']),
            max(lines[i]['x1'] for i in row['line_indices']),
            max(max(lines[i]['bottom']) for i in row['line_indices'])]
        for pi,i in enumerate(row['line_indices']):
            l=lines[i]
            l.update({k:row[k] for k in ('page_side','column_id','block_id')})
            l.update(row_id=row['id'],piece_index=pi,reading_order=order)
            order += 1
            l.setdefault('neighbours',{}).update(
                left=row['line_indices'][pi-1] if pi else None,
                right=row['line_indices'][pi+1] if pi+1<len(row['line_indices']) else None)
        for pi,i in enumerate(row['piece_indices']):
            p=pieces[i];l=lines[p['line_index']]
            p.update({k:l[k] for k in ADDRESS});p['piece_index']=pi
            p['neighbours']=dict(left=row['piece_indices'][pi-1] if pi else None,
                right=row['piece_indices'][pi+1] if pi+1<len(row['piece_indices']) else None)
    for c in col_list:
        c['reading_order']=col_order[c['id']]
    crossings = [dict(validator.crossing(v['line_index'], b), discounted=v['discounted'])
                 for v in violations for b in stops if b['id'] in v['boundary_ids']] if validator else []
    return dict(schema_version=1,image_size=[width,height],units='source pixels',coord_origin='TOPLEFT',
                id_scope='one source image',neighbour_indices=dict(lines='lines.json',cells='cells.json'),
                fold=leaf_fold,pages=pages,boundaries=stops,columns=col_list,
                blocks=list(blocks.values()),rows=row_list,violations=violations,
                boundary_validation='pixel-validated' if validator else 'caller-supplied-unverified',
                rejected_boundaries=rejected,crossing_evidence=crossings,
                boundary_tracks=[dict(id=g[0]['track_id'],boundary_ids=[b['id'] for b in g]) for g in tracks])


def join_pieces(pieces: Sequence[dict], *, structure: dict) -> dict:
    """Join one addressed row, rejecting mixed addresses and boundary crossings.

    Input records contain line curves (select them using cells' line_index).
    Original samples are copied exactly; only gaps are linearly interpolated.
    The result includes the original records in pieces. A singleton retains all
    original geometry and metadata exactly. Discounted records cannot be joined.
    """
    if not pieces:
        raise ValueError('at least one piece is required')
    ordered=sorted(pieces,key=lambda p:p['x0'])
    key=tuple(ordered[0][k] for k in ('page_side','column_id','block_id','row_id'))
    if any(tuple(p[k] for k in ('page_side','column_id','block_id','row_id')) != key for p in ordered):
        raise ValueError('pieces must share page, column, block and row')
    if any(p.get('discounted') is not None for p in ordered):
        raise ValueError('discounted diagnostic records are not deliverable')
    row=next((r for r in structure['rows'] if r['id']==key[-1]),None)
    if row is None or any(row[k]!=ordered[0][k] for k in ('page_side','column_id','block_id')):
        raise ValueError('row is absent from this structure')
    if len({p['piece_index'] for p in ordered})!=len(ordered):
        raise ValueError('duplicate piece index')
    joined=_combine(ordered)
    if any(_crosses(joined,b) for b in structure['boundaries']):
        raise ValueError('joined geometry crosses a boundary')
    joined['pieces']=deepcopy(ordered)
    return joined


def delivery_records(lines: Sequence[dict], *, structure: dict,
                     granularity: str = 'default') -> list[dict]:
    """Return whole ordinary rows and table pieces; optionally all rows or pieces."""
    if granularity not in ('default','rows','pieces'):
        raise ValueError('granularity must be default, rows or pieces')
    result=[]
    for row in structure['rows']:
        if row['discounted']:
            continue
        records=[lines[i] for i in row['line_indices']]
        if granularity=='pieces' or (granularity=='default' and row['table_id'] is not None):
            result.extend(deepcopy(records))
        else:
            result.append(join_pieces(records,structure=structure))
    return result


def render_structure(page: Image.Image, lines: Sequence[dict], structure: dict) -> Image.Image:
    """Draw row colours, piece order, finite column boundaries and the fold."""
    import colorsys
    overlay=Image.new('RGBA',page.size);d=ImageDraw.Draw(overlay)
    for ri,row in enumerate(structure['rows']):
        if row['discounted']:
            continue
        colour=tuple(round(v*255) for v in colorsys.hsv_to_rgb((ri*REVIEW_HUE_STEP)%1,REVIEW_SATURATION,REVIEW_VALUE))
        for i in row['line_indices']:
            l=lines[i];xs=np.unique(np.r_[np.arange(l['x0'],l['x1'],3),l['x1']-1])
            top=[(int(x),l['top'][x-l['x0']]) for x in xs]
            bottom=[(int(x),l['bottom'][x-l['x0']]) for x in xs]
            d.polygon(top+bottom[::-1],fill=colour+(45,),outline=colour+(230,))
            d.text((l['x0'],min(l['top'])),str(l['piece_index']),fill=colour+(255,))
    for b in structure['boundaries']:
        fold=b['kind']=='fold'
        d.line([tuple(p) for p in b['path']],fill=(255,0,180,255) if fold else (0,150,180,190),
               width=max(2,round(page.width/FOLD_STROKE_PAGE_RATIO)) if fold else max(1,round(page.width/BOUNDARY_STROKE_PAGE_RATIO)))
        if fold:
            d.text(tuple(b['path'][0]),'FOLD',fill=(255,0,180,255))
    return Image.alpha_composite(page.convert('RGBA'),overlay).convert('RGB')
