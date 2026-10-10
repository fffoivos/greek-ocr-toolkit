"""A02 owns rules, whitespace corridors, block/cell graph and crossing splits."""
import cv2,numpy as np
from scipy.ndimage import uniform_filter1d
from ..shared.geometry import quantize,roi
from ..shared.image_evidence import runs,components
from ..shared.contracts import bbox,rect,result

def detect(ctx):
    e=ctx.ev; ink=(e.persistence>=2).astype(np.uint8); h=e.body; H,W=ink.shape
    horizontal=runs(ink,12*h); vertical=runs(ink,12*h,True)
    barriers=[]; rules=[]
    for array,direction in ((horizontal,'horizontal'),(vertical,'vertical')):
        _,stats,_=components(array)
        for x,y,w,rh,a in stats:
            b=[x/e.sx,y/e.sy,(x+w)/e.sx,(y+rh)/e.sy]
            rules.append(dict(bbox=b,direction=direction))
            if direction=='vertical' and rh>12*h and w<.5*h: barriers.append(dict(bbox=b,kind='rule',support=float(rh/h)))
    # Skewed long rules are lost by an axis-aligned opening. Hough only nominates;
    # continuous sampled ink support verifies the segment before it is a barrier.
    segments=cv2.HoughLinesP(ink*255,1,np.pi/720,threshold=quantize(8*h),
                            minLineLength=quantize(12*h),maxLineGap=quantize(2*h))
    retained=[]
    proposed=[] if segments is None else sorted(np.asarray(segments).reshape(-1,4).tolist(),key=lambda p:-np.hypot(p[2]-p[0],p[3]-p[1]))
    for ax,ay,bx,by in proposed:
        if abs(by-ay)<12*h or abs(bx-ax)>.15*abs(by-ay): continue
        if by<ay: ax,ay,bx,by=bx,by,ax,ay
        t=np.linspace(0,1,200); xx=ax+t*(bx-ax); yy=ay+t*(by-ay)
        samples=[]
        for offset in (-.15*h,0,.15*h):
            samples.append(cv2.remap(ink.astype(np.float32),(xx+offset)[None].astype(np.float32),yy[None].astype(np.float32),cv2.INTER_LINEAR)[0])
        support=float(np.max(samples,axis=0).mean())
        if support<.75: continue
        slope=(bx-ax)/max(by-ay,1); intercept=ax-slope*ay
        duplicate=False
        for q in retained:
            overlap=min(by,q['by'])-max(ay,q['ay']); mid=(max(ay,q['ay'])+min(by,q['by']))/2
            if overlap>0 and abs(intercept+slope*mid-(q['intercept']+q['slope']*mid))<.5*h:
                duplicate=True; break
        if duplicate: continue
        retained.append(dict(ay=ay,by=by,slope=slope,intercept=intercept))
        b=[(min(ax,bx)-.1*h)/e.sx,ay/e.sy,(max(ax,bx)+.1*h)/e.sx,by/e.sy]
        path=[[ax/e.sx,ay/e.sy],[bx/e.sx,by/e.sy]]
        barriers.append(dict(bbox=b,kind='sloped rule',support=support,path=path))
        rules.append(dict(bbox=b,direction='vertical',path=path))
    # Independent local whitespace, with populated flanks; no page-wide split.
    band=quantize(12*h); stride=quantize(6*h)
    for y in range(0,H,max(1,stride)):
        a=ink[y:min(H,y+band)]; p=a.mean(0); low=uniform_filter1d(p,size=quantize(.4*h))<.008
        edges=np.diff(np.r_[False,low,False].astype(int)); starts=np.flatnonzero(edges==1); ends=np.flatnonzero(edges==-1)
        for x0,x1 in zip(starts,ends):
            if not .6*h<=x1-x0<=7*h: continue
            l=a[:,max(0,x0-quantize(6*h)):x0]; r=a[:,x1:min(W,x1+quantize(6*h))]
            if not l.size or not r.size: continue
            left=l.mean(1)>.025; right=r.mean(1)>.025
            if (left & right).sum()<2*h: continue
            barriers.append(dict(bbox=[x0/e.sx,y/e.sy,x1/e.sx,min(H,y+band)/e.sy],kind='whitespace',support=float((left&right).sum()/h)))
    # A grid requires intersections at distinct row/column positions. Pieces of
    # one newspaper header rule do not become three table rows.
    horizontal_rules=[r for r in rules if r['direction']=='horizontal']
    vertical_rules=[r for r in rules if r['direction']=='vertical']
    intersection_rows=[]; intersection_cols=[]
    for hr in horizontal_rules:
        a,b,c,d=hr['bbox']; cy=(b+d)/2; cols=[]
        for vr in vertical_rules:
            x0,y0,x1,y1=vr['bbox']; cx=(x0+x1)/2
            if a-ctx.height<=cx<=c+ctx.height and y0-ctx.height<=cy<=y1+ctx.height:
                if all(abs(cx-x)>ctx.height for x in cols): cols.append(cx)
        if len(cols)>=2:
            if all(abs(cy-y)>ctx.height for y in intersection_rows): intersection_rows.append(cy)
            intersection_cols.extend(cols)
    table=len(intersection_rows)>=3
    return barriers,rules,table

def run(ctx,phase=3):
    barriers,rules,table=detect(ctx); changed=[]; uncertain=[]; output=[]; assignments=[]
    sy=max(1,ctx.gray.shape[0]//96); sx=max(1,ctx.gray.shape[1]//96)
    raw_reference=np.quantile(ctx.gray[::sy,::sx],.2)
    for i,item in enumerate(ctx.items):
        b=bbox(item); candidates=[]
        for j,r in enumerate(barriers):
            x0,y0,x1,y1=r['bbox']; cx=(x0+x1)/2
            if 'path' in r:
                (xa,ya),(xb,yb)=r['path']; cy=(b[1]+b[3])/2
                cx=xa+(xb-xa)*(cy-ya)/max(yb-ya,1e-6)
                x0,x1=cx-.12*ctx.height,cx+.12*ctx.height
            if b[0]+2*ctx.height<cx<b[2]-2*ctx.height and y0<=b[1] and b[3]<=y1:
                # Full raw-image crossing check excludes text actually spanning the corridor.
                width=max(.25*ctx.height,x1-x0); rx0,ry0,rx1,ry1=roi([cx-width/2,b[1],cx+width/2,b[3]],ctx.gray.shape)
                raw=ctx.gray[ry0:ry1,rx0:rx1]; dark=float(np.mean(raw<raw_reference)) if raw.size else 1.
                if r['kind'] in ('rule','sloped rule') or dark<.02: candidates.append((cx,j,x0,x1))
                else: uncertain.append(dict(line=i,barrier=j,reason='spanning ink',raw_fraction=dark))
        # Ruled tables preserve supplied Paddle text; splitting prose corridors only.
        if candidates and not table and phase>=2:
            cuts=sorted(candidates); pieces=[]; left=b[0]
            for cx,j,x0,x1 in cuts:
                if x0-left<2*ctx.height: continue
                pieces.append([left,b[1],x0,b[3]]); left=x1
            if b[2]-left>=2*ctx.height: pieces.append([left,b[1],b[2],b[3]])
            if len(pieces)>1:
                for p in pieces: output.append(dict(item,polygon=rect(p),source_ids=[i],provenance='barrier split'))
                changed.append(dict(line=i,bbox=b,pieces=pieces,barriers=[c[1] for c in cuts])); continue
        output.append(item); assignments.append(dict(line=i,cell='unresolved' if table else 'provisional text block'))
    # A column boundary is a candidate leaf boundary; physical leaf identity remains unknown.
    xs=sorted(set(round((r['bbox'][0]+r['bbox'][2])/2,3) for r in barriers if r['bbox'][3]-r['bbox'][1]>.25*ctx.size[1]))
    blocks=[]; left=0
    for x in xs:
        if x-left>8*ctx.height: blocks.append([left,0,x,ctx.size[1]]); left=x
    blocks.append([left,0,ctx.size[0],ctx.size[1]])
    return result(output,barriers=barriers,rules=rules,table=table,blocks=blocks,cells=assignments,
                  changes=changed,uncertain=uncertain,regions=barriers,paths=[q['path'] for q in barriers if 'path' in q],
                  status='table preservation' if table else 'block-local barriers')
