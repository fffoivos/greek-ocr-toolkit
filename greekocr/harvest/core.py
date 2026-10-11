"""Offline geometry, list-output handling and provisional label contracts."""
from __future__ import annotations
from collections import Counter
import math, re, unicodedata
import cv2
import numpy as np

STACK_COMMIT = '52cee3bcc882e7426bdc1018d892cd9b1bf9feac'
SCHEMA = 'greekocr-harvest-1'
RARE = 'ϗȣϛϲϹϝϙϡ'
# Explicit observed word substitutions only; no general sigma/accent folding.
SUBSTITUTIONS = {'κὶ': ('καὶ',), 'κὰ': ('καὶ',), 'κὴ': ('καὶ',),
                 'χείριςον': ('χείρισον', 'χείρισὸν')}

def normalise(text):
    return ' '.join(unicodedata.normalize('NFD', text).split())

def edits(a, b):
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        row = [i]
        for j, cb in enumerate(b, 1):
            row.append(min(row[-1]+1, prev[j]+1, prev[j-1]+(ca != cb)))
        prev = row
    return prev[-1]

def tier(vision, docai, layer=None):
    a, b = normalise(vision), normalise(docai)
    result = dict(tier='rejected', label=None, tags=[], nfd_edits=None,
                  raw_exact_agreement=bool(a and b and a == b))
    if not a or not b:
        result['tags'] = ['empty_reader']; return result
    distance = edits(a, b); result['nfd_edits'] = distance
    if a == b:
        result.update(tier='tier1', label=vision); return result
    candidates = {b}
    for old, replacements in SUBSTITUTIONS.items():
        pattern = r'(?<![\w\u0300-\u036f])'+re.escape(normalise(old))+r'(?![\w\u0300-\u036f])'
        candidates |= {re.sub(pattern, normalise(new), value)
                       for value in list(candidates) for new in replacements}
    if a in candidates:
        result.update(tier='tier1', label=vision, tags=['rare_glyph_substitution']); return result
    if distance <= 2 or (layer and normalise(layer) in (a,b)):
        result.update(tier='tier2', label=vision if not layer or normalise(layer)==a else docai)
        if layer and normalise(layer) in (a,b): result['tags'].append('weak_text_layer_agreement')
    else: result['tier'] = 'tier3'
    return result

def bbox(poly):
    p = np.asarray(poly, float)
    return [float(p[:,0].min()), float(p[:,1].min()), float(p[:,0].max()), float(p[:,1].max())]

def foreign(text):
    return any(c.isalpha() and not any(k in unicodedata.name(c, '') for k in ('GREEK','LATIN')) for c in text)

def list_return(pieces):
    """Pieces are text + pixel bbox + confidence. Join one overlapping vertical band."""
    pieces = [p for p in pieces if p.get('text','').strip()]
    if not pieces: return dict(text='', flags=['empty'], rejected=True, pieces=[], dropped=[])
    good, bad = [], []
    for p in pieces:
        if foreign(p['text']) or not any(c.isalnum() for c in p['text']): bad.append(p)
        else: good.append(p)
    if not good: return dict(text='', flags=['garbage'], rejected=True, pieces=pieces, dropped=bad)
    heights = [p['bbox'][3]-p['bbox'][1] for p in good]
    main = max(good, key=lambda p: sum(c.isalpha() for c in p['text']))
    mb = main['bbox']; flags = ['list_return'] if len(pieces)>1 else []
    for p in good:
        b = p['bbox']; overlap = max(0, min(b[3],mb[3])-max(b[1],mb[1]))
        if overlap/max(1,min(b[3]-b[1],mb[3]-mb[1])) < .35:
            return dict(text='',flags=flags+['stacked_bands'],rejected=True,pieces=pieces,dropped=bad)
    x0=min(p['bbox'][0] for p in good); x1=max(p['bbox'][2] for p in good)
    for p in bad:
        b=p['bbox']; cy=(b[1]+b[3])/2
        if x0 < (b[0]+b[2])/2 < x1 and mb[1] <= cy <= mb[3]:
            return dict(text='',flags=flags+['obstructed'],rejected=True,pieces=pieces,dropped=bad)
    if bad: flags.append('garbage_piece_dropped')
    if len(good)>1: flags.append('horizontal_pieces_joined')
    return dict(text=' '.join(p['text'].strip() for p in sorted(good,key=lambda p:p['bbox'][0])),
                flags=flags,rejected=False,pieces=pieces,dropped=bad)

def column_bands(boxes, width):
    long=[b for b in boxes if b[2]-b[0] >= .2*width]
    if not long: return []
    centres=np.array([(b[0]+b[2])/2 for b in long]); left=centres<width/2
    if left.sum()>=5 and (~left).sum()>=5 and np.median(centres[~left])-np.median(centres[left])>.3*width:
        groups=[[b for b,c in zip(long,left) if c==side] for side in (True,False)]
        bands=[[float(np.percentile([b[0] for b in g],5)),float(np.percentile([b[2] for b in g],95))] for g in groups]
        if bands[0][1] < bands[1][0]+.03*width: return bands
    return [[float(np.percentile([b[0] for b in long],5)),float(np.percentile([b[2] for b in long],95))]]

def page_gate(gray, items, *, bend_fired=False):
    h,w=gray.shape; boxes=[bbox(q['polygon']) for q in items]; flags=[]
    angles=[]
    for q,b in zip(items,boxes):
        (_, _),(rw,rh),ang=cv2.minAreaRect(np.asarray(q['polygon'],np.float32))
        if max(rw,rh)<4*max(1,min(rw,rh)): continue
        ang = ang if rw>=rh else ang+90
        ang=(ang+90)%180-90; angles.append(float(ang))
    rotated = bool(angles and np.mean(np.abs(angles)>5)>.6)
    if rotated: flags.append('rotated')
    ink=(gray < min(220,float(np.percentile(gray,50))-35)).astype(np.uint8)
    horizontal=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((1,max(20,w//3)),np.uint8))
    vertical=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((max(20,h//5),1),np.uint8))
    def count(mask):
        return cv2.connectedComponentsWithStats(mask)[0]-1
    nh,nv=count(horizontal),count(vertical)
    short=[b for b in boxes if b[2]-b[0]<.18*w]
    rowbins=Counter(round((b[1]+b[3])/2/20) for b in short)
    lattice=sum(n>=3 for n in rowbins.values())>=5 and len(short)>.55*max(1,len(boxes))
    if (nh>=3 and nv>=2) or lattice: flags.append('table')
    if bend_fired: flags.append('bend_scout')
    bands=column_bands(boxes,w)
    # Three sustained narrow-column centre clusters are outside H1's body gate.
    centres=sorted((b[0]+b[2])/2 for b in boxes if .12*w<=b[2]-b[0]<=.38*w)
    clusters=[]
    for centre in centres:
        if not clusters or centre-np.median(clusters[-1])>.15*w: clusters.append([centre])
        else: clusters[-1].append(centre)
    if sum(len(c)>=5 for c in clusters)>2: flags.append('more_than_two_columns')
    if len(items)<6 or not bands: flags.append('non_body_page')
    pitches=[]
    for band in bands:
        centres=sorted((b[1]+b[3])/2 for b in boxes if band[0]-10<=(b[0]+b[2])/2<=band[1]+10 and b[2]-b[0]>.2*w)
        delta=np.diff(centres); body_h=np.median([b[3]-b[1] for b in boxes]) if boxes else 10
        usable=delta[(delta>.65*body_h)&(delta<4*body_h)]
        pitches.extend(usable.tolist())
    pitch=float(np.median(pitches)) if pitches else float(np.median([b[3]-b[1] for b in boxes])*1.5) if boxes else 0
    return dict(accepted=not flags,flags=flags,page_class=f'body_{len(bands)}column' if not flags else 'excluded',
                column_bands=bands,body_pitch=pitch,angle_histogram=np.histogram(angles,bins=[-90,-10,-5,0,5,10,90])[0].tolist(),
                rule_counts=dict(horizontal=nh,vertical=nv),box_lattice=bool(lattice),bend_scout_fired=bool(bend_fired))

def crop_gate(box, boxes, pg, size, item=None, *, long_complete=False):
    x0,y0,x1,y1=box; w,h=size; flags=[]; height=y1-y0
    if not pg['accepted']: flags += ['page_'+s for s in pg['flags']]
    if height>1.5*pg['body_pitch']: flags.append('height_over_body_pitch')
    neighbours=[b[3]-b[1] for b in boxes if b!=box and abs((b[1]+b[3]-y0-y1)/2)<3*pg['body_pitch'] and min(b[2],x1)>max(b[0],x0)]
    if neighbours and height>1.6*np.median(neighbours): flags.append('taller_than_neighbours')
    band=next((i for i,b in enumerate(pg['column_bands']) if x0>=b[0]-max(10,.02*w) and x1<=b[1]+max(10,.02*w)),None)
    if band is None: flags.append('outside_column_band')
    if x0<.01*w or x1>.99*w or y0<2 or y1>h-2: flags.append('page_edge_touch')
    if x1-x0<max(12,height*1.1): flags.append('ornament_or_short_fragment')
    if item and item.get('removal'): flags.append('catalogue_'+item['removal'].replace(' ','_'))
    ratio=None; paragraph_position='unknown'
    if band is not None:
        cb=pg['column_bands'][band]; ratio=(x1-x0)/max(1,cb[1]-cb[0])
        # A text band is the observed ink extent, not the physical column edge.
        # Guard the surrounding whitespace/gutter, not the ends of full rows.
        pad=max(.015*w,.5*pg['body_pitch'])
        boundaries=[max(.01*w,cb[0]-pad),min(.99*w,cb[1]+pad)]
        if len(pg['column_bands'])==2:
            gutter=sum((pg['column_bands'][0][1],pg['column_bands'][1][0]))/2
            boundaries[1 if band==0 else 0]=gutter
        if long_complete and (x0<=boundaries[0]+2 or x1>=boundaries[1]-2): flags.append('column_edge_touch')
        same=[b for b in boxes if cb[0]-10 <= (b[0]+b[2])/2 <= cb[1]+10 and b!=box]
        before=[b for b in same if (b[1]+b[3])/2 < (y0+y1)/2]
        after=[b for b in same if (b[1]+b[3])/2 > (y0+y1)/2]
        prev=max(before,key=lambda b:b[3],default=None); nxt=min(after,key=lambda b:b[1],default=None)
        first=prev is None or y0-prev[3]>.9*pg['body_pitch'] or x0-cb[0]>.06*(cb[1]-cb[0])
        last=nxt is None or nxt[1]-y1>.9*pg['body_pitch']
        paragraph_position='first_last' if first and last else 'first' if first else 'last' if last else 'interior'
        if long_complete and ratio<.8: flags.append('short_paragraph_boundary' if first or last else 'width_under_80pct_band')
        elif long_complete and (first or last) and ratio<.9: flags.append('short_paragraph_boundary')
    return dict(accepted=not flags,flags=flags,column=band,width_band_ratio=ratio,paragraph_position=paragraph_position)

def body_font_gate(records, pg):
    """Exclude small-type furniture using per-column cheap component x-heights."""
    heights={}
    for col in range(len(pg['column_bands'])):
        values=[r['features']['x_height_estimate'] for r in records
                if r['gates']['accepted'] and r['gates']['column']==col
                and r['features'].get('x_height_estimate')]
        heights[str(col)]=float(np.median(values)) if values else None
    pg['body_x_height_by_column']=heights
    for r in records:
        ref=heights.get(str(r['gates']['column']));xh=r['features'].get('x_height_estimate')
        r['features']['body_x_height_estimate']=ref
        if r['gates']['accepted'] and ref and xh and xh<.65*ref:
            r['gates']['flags'].append('small_type_furniture');r['gates']['accepted']=False
            r.update(tier='rejected',label=None)

def validate_record(r):
    required={'schema','id','source','book','decade','page','page_id','provenance','stack_commit','polygon','bbox','gates','features','readers','tier','label','raw_crop','straight_crop'}
    missing=required-r.keys()
    if missing: raise ValueError('missing fields: '+','.join(sorted(missing)))
    if not isinstance(r['readers'],dict) or not isinstance(r['features'],dict): raise ValueError('record objects required')
    poly=np.asarray(r['polygon'],float); box=np.asarray(r['bbox'],float)
    if poly.ndim!=2 or poly.shape[1]!=2 or len(poly)<4 or not np.isfinite(poly).all(): raise ValueError('invalid polygon')
    if box.shape!=(4,) or not np.isfinite(box).all() or box[2]<=box[0] or box[3]<=box[1]: raise ValueError('invalid bbox')
    if r['schema']!=SCHEMA or r['stack_commit']!=STACK_COMMIT: raise ValueError('schema/stack mismatch')
    if r['tier'] not in ('tier1','tier2','tier3','rejected','unread'): raise ValueError('invalid tier')
    if r['tier'] in ('tier1','tier2') and not r['label']: raise ValueError('label required')
    if r['tier'] in ('tier3','rejected','unread') and r['label'] is not None: raise ValueError('unlabelled tier')
    if not re.fullmatch(r'[0-9a-f]{64}',r['provenance'].get('pdf_sha256','')): raise ValueError('source SHA-256 required')
    if r['tier'] in ('tier1','tier2') and not r['gates']['accepted']: raise ValueError('gated line has label')
    if r.get('sampled'):
        if r['source']!='Anemi' or not r['gates']['accepted']: raise ValueError('only surviving Anemi may be sampled')
        if not r['straight_crop'] or not r['raw_crop']: raise ValueError('sample needs both crop paths')
        if r['features'].get('width_band_ratio',0)<.8: raise ValueError('sample must be a long line')
        if r['text_layer'] is not None: raise ValueError('Anemi has no text-layer third vote')
    return r
