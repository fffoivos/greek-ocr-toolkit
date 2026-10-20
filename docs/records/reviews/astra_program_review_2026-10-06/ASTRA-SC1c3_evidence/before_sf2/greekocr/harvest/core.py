"""Offline geometry, list-output handling and provisional label contracts."""
from __future__ import annotations
from collections import Counter
import math, re, unicodedata
import cv2
import numpy as np

STACK_COMMIT = '52cee3bcc882e7426bdc1018d892cd9b1bf9feac'
SCHEMA = 'greekocr-harvest-1'
GATE_REVISION = 'H1-fix2'
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

def list_return(pieces, *, column_bands=None, x_offset=0):
    """Pieces are text + pixel bbox + confidence. Join one overlapping vertical band."""
    pieces = [p for p in pieces if p.get('text','').strip()]
    if not pieces: return dict(text='', flags=['empty'], rejected=True, pieces=[], dropped=[])
    good, bad = [], []
    for p in pieces:
        if foreign(p['text']) or not any(c.isalnum() for c in p['text']): bad.append(p)
        else: good.append(p)
    if not good: return dict(text='', flags=['garbage'], rejected=True, pieces=pieces, dropped=bad)
    # Reader boxes are in crop coordinates; physical bands are in page coordinates.
    # The union also guards two individually valid pieces on opposite sides.
    extent = [min(p['bbox'][0] for p in good) + x_offset, 0,
              max(p['bbox'][2] for p in good) + x_offset, 1]
    if column_bands and (crosses_column(extent,column_bands) or
                        (len(good)>1 and sum(f>0 for f in column_coverage(extent,column_bands))>1)):
        return dict(text='', flags=['crosses_column'], rejected=True, pieces=pieces, dropped=bad)
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

def column_bands(boxes, width, gray=None):
    """Physical text bands, using repeated page-ink gutters before fused boxes.

    A gutter must recur in at least five rows and 20% of eligible boxes, with
    substantial ink on both sides. This tolerates occasional spanning headings
    and commentary. Word spaces in one row cannot supply page column evidence.
    """
    long=[b for b in boxes if b[2]-b[0] >= .2*width]
    if not long: return []
    if gray is not None:
        ink=gray < min(220, float(np.percentile(gray,50))-35)
        height=float(np.median([b[3]-b[1] for b in long]))
        profiles=[]; gaps=[]; votes=np.zeros(width, dtype=int)
        # Duplicate/fused detections on one physical row supply only one vote.
        row_boxes={}
        for box in sorted(long,key=lambda b:b[2]-b[0],reverse=True):
            row=round((box[1]+box[3])/2/max(1,.5*height))
            row_boxes.setdefault(row,box)
        for x0,y0,x1,y1 in row_boxes.values():
            if y1-y0 > 2*height: continue
            a,b=max(0,math.floor(x0)),min(width,math.ceil(x1))
            on=np.flatnonzero(ink[max(0,math.floor(y0)):min(len(gray),math.ceil(y1)),a:b].any(axis=0))+a
            if not on.size: continue
            profiles.append(on)
            row_gaps=[]
            for left,right in zip(on[:-1],on[1:]):
                if right-left > max(.018*width,.6*height) and left-on[0]>.15*width and on[-1]-right>.15*width:
                    row_gaps.append((int(left+1),int(right)))
            for a,b in row_gaps: votes[a:b]+=1
            gaps.extend(row_gaps)
        threshold=max(5,math.ceil(.2*len(profiles)))
        candidates=[]
        while votes.size and votes.max() >= threshold:
            x=int(votes.argmax())
            support=[g for g in gaps if g[0]<=x<g[1]]
            a=float(np.median([g[0] for g in support])); b=float(np.median([g[1] for g in support]))
            candidates.append((a,b))
            votes[max(0,int(x-.15*width)):min(width,int(x+.15*width)+1)]=0
        if candidates:
            gutters=sorted(candidates)
            cuts=[0]+[(a+b)/2 for a,b in gutters]+[width]
            bands=[]
            for col,(left,right) in enumerate(zip(cuts[:-1],cuts[1:])):
                spans=[on[(on>=left)&(on<right)] for on in profiles]
                spans=[on for on in spans if on.size and on[-1]-on[0]>=.12*width]
                if len(spans)>=5:
                    start=float(np.percentile([on[0] for on in spans],5))
                    end=float(np.percentile([on[-1]+1 for on in spans],95))
                    if col: start=max(start,gutters[col-1][1])
                    if col<len(gutters): end=min(end,gutters[col][0])
                    if end>start: bands.append([start,end])
            if len(bands)>=2: return bands
    # Spanning headings and a minority of fused rows must not stretch the
    # independently supported x-extent clusters back into one column.
    narrow=[b for b in long if b[2]-b[0]<=.6*width]
    centres=np.array([(b[0]+b[2])/2 for b in narrow]); left=centres<width/2
    if left.sum()>=5 and (~left).sum()>=5 and np.median(centres[~left])-np.median(centres[left])>.3*width:
        groups=[[b for b,c in zip(narrow,left) if c==side] for side in (True,False)]
        bands=[[float(np.percentile([b[0] for b in g],5)),float(np.percentile([b[2] for b in g],95))] for g in groups]
        if bands[0][1] < bands[1][0]: return bands
    return [[float(np.percentile([b[0] for b in long],5)),float(np.percentile([b[2] for b in long],95))]]

def column_coverage(box, bands):
    return [max(0.,min(box[2],b[1])-max(box[0],b[0]))/max(1.,b[1]-b[0]) for b in bands]

def crosses_column(box, bands):
    return sum(f>.15 for f in column_coverage(box,bands))>1

def column_regions(items, gray):
    """Consecutive physical rows with the same ink/box column pattern.

    A broad row is spanning only when it has no sustained internal gutter.
    Thus a fused pair's outer extent cannot masquerade as spanning prose.
    Isolated word spaces cannot establish a multi-column region.
    """
    h,w=gray.shape
    boxes=[bbox(q['polygon']) for q in items]
    if not boxes: return []
    height=float(np.median([b[3]-b[1] for b in boxes]))
    ink=gray<min(220,float(np.percentile(gray,50))-35)
    rows=[]
    for index in sorted(range(len(boxes)),key=lambda i:(boxes[i][1]+boxes[i][3])/2):
        box=boxes[index];cy=(box[1]+box[3])/2
        if not rows or abs(cy-np.median(rows[-1]['centres']))>.55*height:
            rows.append(dict(indices=[],centres=[]))
        rows[-1]['indices'].append(index);rows[-1]['centres'].append(cy)
    for row in rows:
        on=np.zeros(w,bool)
        # Small ornaments on the opposite facing page must not stretch a
        # body row's apparent ink span into a full-width region.
        structural=[i for i in row['indices'] if boxes[i][2]-boxes[i][0]>max(.03*w,3*height)
                    and boxes[i][3]-boxes[i][1]<=1.5*height]
        for i in structural or row['indices']:
            x0,y0,x1,y1=boxes[i]
            a,b=max(0,math.floor(x0)),min(w,math.ceil(x1))
            t,d=max(0,math.floor(y0)),min(h,math.ceil(y1))
            if b>a and d>t:
                mask=np.zeros((d-t,b-a),np.uint8)
                cv2.fillPoly(mask,[np.rint(np.asarray(items[i]['polygon'])-[a,t]).astype(np.int32)],1)
                on[a:b]|=(ink[t:d,a:b]&mask.astype(bool)).any(axis=0)
        xs=np.flatnonzero(on)
        gaps=[]
        bs=[boxes[i] for i in row['indices']]
        for a,b in zip(xs[:-1],xs[1:]):
            if b-a<=max(.018*w,.6*height): continue
            # Independent detections establish the same column pattern when
            # one side is a short paragraph ending. Their outer union is not
            # a continuous full-width row.
            paired=(any(q[2]<=a+1+.25*height and q[2]-q[0]>1.1*height for q in bs) and
                    any(q[0]>=b-.25*height and q[2]-q[0]>1.1*height for q in bs))
            minimum=.03*w if paired else .12*w
            if a-xs[0]>minimum and xs[-1]-b>minimum: gaps.append((a+1,b))
        row['gutter']=max(gaps,key=lambda g:g[1]-g[0],default=None)
        row['span']=float(xs[-1]-xs[0]+1)/w if xs.size else 0.
        row['extent']=(int(xs[0]),int(xs[-1])+1) if xs.size else (0,0)
    for i,row in enumerate(rows):
        gap=row['gutter']
        support=1 if gap else 0
        if gap:
            for direction in (-1,1):
                a,b=gap;skipped=0
                for j in range(i+direction,i+9*direction,direction):
                    if not 0<=j<len(rows): break
                    other=rows[j];candidate=other['gutter']
                    if candidate and min(b,candidate[1])>max(a,candidate[0]):
                        a,b=max(a,candidate[0]),min(b,candidate[1]);support+=1;skipped=0
                    elif candidate or other['span']>.70 or skipped>=2: break
                    else: skipped+=1
        row['multi']=support>=3
    # Partial continuation rows in a glossary retain the nearby established
    # pattern; a continuous spanning row always terminates that region.
    for i,row in enumerate(rows):
        if row['multi'] or row['span']>.70 or row['gutter']: continue
        nearby=[r for r in rows[max(0,i-2):i+3] if r['multi'] and
                (row['extent'][1]<=r['gutter'][0]+.02*w or row['extent'][0]>=r['gutter'][1]-.02*w)]
        if nearby:
            row['multi']=True;row['gutter']=min((r['gutter'] for r in nearby),key=lambda g:g[1]-g[0])
    groups=[]
    for row in rows:
        pattern=row['gutter'] if row['multi'] else None
        full=row['span']>.70 and not row['multi']
        cy=float(np.median(row['centres']))
        same=groups and cy-groups[-1]['last_y']<=1.8*height and not full and not groups[-1]['full_width'] and (
            (pattern is None and groups[-1]['pattern'] is None) or
            (pattern is not None and groups[-1]['pattern'] is not None and
             min(pattern[1],groups[-1]['pattern'][1])>max(pattern[0],groups[-1]['pattern'][0])))
        if not same: groups.append(dict(indices=[],pattern=pattern,full_width=full,gaps=[]))
        groups[-1]['last_y']=cy
        groups[-1]['indices'].extend(row['indices'])
        if row['multi']:
            groups[-1]['gaps'].append(row['gutter'])
            groups[-1]['pattern']=(max(pattern[0],groups[-1]['pattern'][0]),min(pattern[1],groups[-1]['pattern'][1]))
    regions=[]
    for index,group in enumerate(groups):
        bs=[boxes[i] for i in group['indices']]
        structural=[b for b in bs if b[2]-b[0]>max(.03*w,3*height) and b[3]-b[1]<=1.5*height]
        bs=structural or bs
        if group['gaps']:
            # Each physical row supplies its own gutter evidence; even a short
            # local glossary must not borrow bands from prose elsewhere.
            a,b=group['pattern']
            spans=[[],[]]
            for box in bs:
                for col,(lo,hi) in enumerate(((box[0],min(box[2],a)),(max(box[0],b),box[2]))):
                    if hi-lo>=.12*w: spans[col].append((lo,hi))
            bands=[[float(np.percentile([p[0] for p in sp],5)),float(np.percentile([p[1] for p in sp],95))]
                   for sp in spans if sp]
        else:
            bands=[[float(min(p[0] for p in bs)),float(max(p[2] for p in bs))]]
        regions.append(dict(id=index,y0=min(b[1] for b in bs),y1=max(b[3] for b in bs),
            item_indices=group['indices'],column_bands=bands,full_width=group['full_width'],
            pattern='multi_column' if len(bands)>1 else 'full_width' if group['full_width'] else 'single_column'))
    return regions

def region_for_box(box, pg, item=None):
    regions=pg.get('column_regions',[])
    if not regions: return None
    if item and 'harvest_region' in item:
        return next(r for r in regions if r['id']==item['harvest_region'])
    cy=(box[1]+box[3])/2
    return min(regions,key=lambda r:(abs(cy-(r['y0']+r['y1'])/2)
                                   if r['y0']<=cy<=r['y1'] else h_distance(cy,r)+1e6))

def h_distance(cy, region):
    return min(abs(cy-region['y0']),abs(cy-region['y1']))

def split_columns(items, bands, gray=None, *, _ink=None):
    """Split fused polygons at the gutter before any crop gate.

    The gutter whitespace is omitted so new pieces retain a margin to the
    physical column edge. With page pixels, use that polygon's blank corridor
    around the page gutter: a median gutter edge must not trim a tilted letter.
    Original geometry remains attached for provenance.
    """
    if isinstance(bands,dict):
        pg=bands;result=[]
        ink=_ink if _ink is not None else gray < min(220,float(np.percentile(gray,50))-35) if gray is not None else None
        for index,item in enumerate(items):
            region=region_for_box(bbox(item['polygon']),pg,item)
            local=region['column_bands'] if region else pg['column_bands']
            for piece in split_columns([item],local,gray,_ink=ink):
                piece['harvest_parent_index']=index
                if region: piece['harvest_region']=region['id']
                result.append(piece)
        return result
    def clip(poly, edge, keep_right):
        out=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ia=a[0]>=edge if keep_right else a[0]<=edge
            ib=b[0]>=edge if keep_right else b[0]<=edge
            if ia: out.append(a)
            if ia!=ib:
                t=(edge-a[0])/(b[0]-a[0]); out.append([edge,a[1]+t*(b[1]-a[1])])
        return out
    result=[]
    ink=_ink if _ink is not None else gray < min(220,float(np.percentile(gray,50))-35) if gray is not None else None
    for index,item in enumerate(items):
        box=bbox(item['polygon'])
        if sum(f>0 for f in column_coverage(box,bands))<=1:
            result.append(dict(item,harvest_parent_index=index)); continue
        gutters=[(left[1],right[0]) for left,right in zip(bands[:-1],bands[1:])]
        cuts_ink=False
        if ink is not None:
            x0,y0=max(0,math.floor(box[0])),max(0,math.floor(box[1]))
            x1,y1=min(ink.shape[1],math.ceil(box[2])),min(ink.shape[0],math.ceil(box[3]))
            mask=np.zeros((max(0,y1-y0),max(0,x1-x0)),np.uint8)
            if mask.size:
                cv2.fillPoly(mask,[np.rint(np.asarray(item['polygon'])-[x0,y0]).astype(np.int32)],1)
                on=np.flatnonzero((ink[y0:y1,x0:x1]&mask.astype(bool)).any(axis=0))+x0
                for i,(a,b) in enumerate(gutters):
                    centre=(a+b)/2
                    left=on[on<centre];right=on[on>=centre]
                    if not left.size or not right.size: continue
                    lo,hi=float(left[-1]+1),float(right[0])
                    if hi-lo>=5: gutters[i]=(lo,hi)
                    else: cuts_ink=True
        for col,band in enumerate(bands):
            if column_coverage(box,[band])[0]<=0: continue
            # Clip only internal sides. Preserve original exterior ink extents.
            poly=[list(p) for p in item['polygon']]
            if col: poly=clip(poly,gutters[col-1][1],True)
            if col<len(bands)-1 and poly: poly=clip(poly,gutters[col][0],False)
            if len(poly)>=3 and cv2.contourArea(np.asarray(poly,np.float32))>0:
                if len(poly)==3: poly.append(poly[-1])
                result.append(dict(item,polygon=poly,harvest_parent_index=index,
                    harvest_column_piece=col,harvest_parent_polygon=item['polygon'],
                    harvest_split_cuts_ink=cuts_ink))
    return result

def box_lattice(boxes, width):
    """At least five rows share at least three sustained short-box x clusters."""
    short=[b for b in boxes if b[2]-b[0]<.18*width]
    if len(short)<=.55*max(1,len(boxes)): return False
    def clusters(values,tolerance):
        groups=[]
        for value,index in sorted(values):
            if not groups or value-np.median([v for v,_ in groups[-1]])>tolerance: groups.append([])
            groups[-1].append((value,index))
        return groups
    xs=clusters([((b[0]+b[2])/2,i) for i,b in enumerate(short)],max(6,.025*width))
    sustained={i:col for col,g in enumerate(xs) if len(g)>=5 for _,i in g}
    ys=clusters([((b[1]+b[3])/2,i) for i,b in enumerate(short)],max(4,.65*np.median([b[3]-b[1] for b in short])))
    return sum(len({sustained[i] for _,i in g if i in sustained})>=3 for g in ys)>=5

def ruled_cells(ink):
    """Long near-axis rules enclosing at least two internal cells, skew allowed."""
    h,w=ink.shape;scale=min(h,w)
    lines=cv2.HoughLinesP(ink,1,np.pi/360,threshold=max(25,int(.025*scale)),
        minLineLength=max(20,int(.04*scale)),maxLineGap=max(4,int(.025*scale)))
    masks=[np.zeros_like(ink),np.zeros_like(ink)];counts=[0,0]
    for x0,y0,x1,y1 in lines.reshape(-1,4) if lines is not None else []:
        dx,dy=abs(x1-x0),abs(y1-y0)
        col=0 if dx>=.05*w and dy<=.09*dx else 1 if dy>=.08*h and dx<=.09*dy else None
        if col is not None:
            # Hough votes from a text baseline are discontinuous. A rule must
            # have actual ink along at least three quarters of its length.
            xx=np.rint(np.linspace(x0,x1,max(dx,dy)+1)).astype(int)
            yy=np.rint(np.linspace(y0,y1,max(dx,dy)+1)).astype(int)
            if np.mean(ink[yy,xx])<.75: continue
            cv2.line(masks[col],(x0,y0),(x1,y1),1,max(3,round(.002*scale)));counts[col]+=1
    rules=masks[0]|masks[1]
    contours,hierarchy=cv2.findContours(rules,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    cells=[]
    for i,contour in enumerate(contours):
        if hierarchy[0,i,3]<0: continue
        x,y,cw,ch=cv2.boundingRect(contour);area=cv2.contourArea(contour)
        # Remove only speck-sized closures. Large table cells remain cells;
        # a single surrounding frame cannot reach the two-cell threshold.
        if .0003*w*h<area and .04*w<cw and .01*h<ch:
            cells.append([x,y,x+cw,y+ch])
    return dict(closed_cells=len(cells),cells=cells,horizontal_segments=counts[0],vertical_segments=counts[1])

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
    lattice=box_lattice(boxes,w)
    cells=ruled_cells(ink)
    if (nh>=3 and nv>=2 and lattice) or (cells['horizontal_segments'] and cells['vertical_segments'] and cells['closed_cells']>=2): flags.append('table')
    if bend_fired: flags.append('bend_scout')
    bands=column_bands(boxes,w,gray)
    regions=column_regions(items,gray)
    if len(bands)>2: flags.append('more_than_two_columns')
    # Three sustained narrow-column centre clusters are outside H1's body gate.
    centres=sorted((b[0]+b[2])/2 for b in boxes if .12*w<=b[2]-b[0]<=.38*w)
    clusters=[]
    for centre in centres:
        if not clusters or centre-np.median(clusters[-1])>.15*w: clusters.append([centre])
        else: clusters[-1].append(centre)
    if sum(len(c)>=5 for c in clusters)>2 and 'more_than_two_columns' not in flags: flags.append('more_than_two_columns')
    if len(items)<6 or not bands: flags.append('non_body_page')
    pitches=[]
    pitch_boxes=[bbox(q['polygon']) for q in split_columns(items,dict(column_bands=bands,column_regions=regions))]
    for band in bands:
        centres=sorted((b[1]+b[3])/2 for b in pitch_boxes if band[0]-10<=(b[0]+b[2])/2<=band[1]+10 and b[2]-b[0]>.2*w)
        delta=np.diff(centres); body_h=np.median([b[3]-b[1] for b in boxes]) if boxes else 10
        usable=delta[(delta>.65*body_h)&(delta<4*body_h)]
        pitches.extend(usable.tolist())
    pitch=float(np.median(pitches)) if pitches else float(np.median([b[3]-b[1] for b in boxes])*1.5) if boxes else 0
    return dict(accepted=not flags,flags=flags,page_class=f'body_{len(bands)}column' if not flags else 'excluded',
                column_bands=bands,column_regions=regions,body_pitch=pitch,angle_histogram=np.histogram(angles,bins=[-90,-10,-5,0,5,10,90])[0].tolist(),
                rule_counts=dict(horizontal=nh,vertical=nv),ruled_cells=cells,box_lattice=bool(lattice),bend_scout_fired=bool(bend_fired))

def crop_gate(box, boxes, pg, size, item=None, *, long_complete=False):
    x0,y0,x1,y1=box; w,h=size; flags=[]; height=y1-y0
    region=region_for_box(box,pg,item)
    if region: pg=dict(pg,column_bands=region['column_bands'])
    if not pg['accepted']: flags += ['page_'+s for s in pg['flags']]
    if height>1.5*pg['body_pitch']: flags.append('height_over_body_pitch')
    neighbours=[b[3]-b[1] for b in boxes if b!=box and abs((b[1]+b[3]-y0-y1)/2)<3*pg['body_pitch'] and min(b[2],x1)>max(b[0],x0)]
    if neighbours and height>1.6*np.median(neighbours): flags.append('taller_than_neighbours')
    coverage=column_coverage(box,pg['column_bands'])
    if crosses_column(box,pg['column_bands']): flags.append('crosses_column')
    if item and item.get('harvest_split_cuts_ink'): flags.append('column_split_cuts_ink')
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
    return dict(accepted=not flags,flags=flags,column=band,column_coverage=coverage,gate_revision=GATE_REVISION,
                width_band_ratio=ratio,paragraph_position=paragraph_position,column_bands=pg['column_bands'],
                column_region=region['id'] if region else None,region_pattern=region['pattern'] if region else None)

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
