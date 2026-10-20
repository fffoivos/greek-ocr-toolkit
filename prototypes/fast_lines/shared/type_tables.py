"""Regional table evidence. Protection only: existing detector items never change.

Rules are geometry; repeated short-cell alignment is layout. Neither supplies
semantic cells. Both routes explicitly retain uncertain/borderless regions.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from .geometry import height_proxy
from .contracts import bbox
from .type_dot_runs import chains


def box_grid(items,height,version=1):
    b=np.asarray([bbox(q) for q in items],float).reshape(-1,4)
    if not len(b):return [],[]
    cy=(b[:,1]+b[:,3])/2; cx=(b[:,0]+b[:,2])/2
    widths=b[:,2]-b[:,0];heights=b[:,3]-b[:,1]
    short=np.flatnonzero((widths<8*height)&(heights<3*height)&(widths>.25*height))
    # Complete-span x alignment, keeping min/max endpoints (no transitive drift).
    columns=[]
    for i in sorted(short,key=lambda i:cx[i]):
        if not columns or cx[i]-columns[-1]['xmin']>.8*height:
            columns.append(dict(xmin=float(cx[i]),members=[]))
        columns[-1]['members'].append(int(i))
    columns=[dict(c,x=float(np.median(cx[c['members']]))) for c in columns if len(c['members'])>=3]
    regions=[]
    for j,left in enumerate(columns):
        for right in columns[j+1:]:
            li=np.array(left['members']);ri=np.array(right['members'])
            if version>=2 and b[ri,0].min()-b[li,2].max()>4*height:continue
            matches=[(int(a),int(ri[np.argmin(abs(cy[ri]-cy[a]))])) for a in li if np.min(abs(cy[ri]-cy[a]))<.6*height]
            if len(matches)<3:continue
            ids=sorted(set(i for pair in matches for i in pair))
            y0=float(b[ids,1].min());y1=float(b[ids,3].max())
            if y1-y0<3*height:continue
            # The object is regional: no page-wide "table" switch.
            regions.append(dict(bbox=[float(b[ids,0].min()),y0,float(b[ids,2].max()),y1],
                                cells=ids,aligned_pairs=matches,source='two repeated short-cell columns'))
    # A pair of distant columns may be two independent pages. V2 only connects
    # within a normal text measure; wider grids require intervening cells/rules.
    if version>=2:
        regions=[r for r in regions if r['bbox'][2]-r['bbox'][0]<35*height or len(r['cells'])>=12]
    merged=[]
    for r in regions:
        targets=[q for q in merged if len(set(q['cells'])&set(r['cells']))>=3]
        if not targets:merged.append(r);continue
        q=targets[0];a=q['bbox'];d=r['bbox'];q['bbox']=[min(a[0],d[0]),min(a[1],d[1]),max(a[2],d[2]),max(a[3],d[3])]
        q['cells']=sorted(set(q['cells']+r['cells']));q['aligned_pairs']+=r['aligned_pairs']
    if version>=3:
        changed=True
        while changed:
            changed=False
            for i in range(len(merged)):
                if changed:break
                for j in range(i+1,len(merged)):
                    a=merged[i];b2=merged[j]
                    if len(set(a['cells'])&set(b2['cells']))<3:continue
                    q=a['bbox'];r=b2['bbox'];a['bbox']=[min(q[0],r[0]),min(q[1],r[1]),max(q[2],r[2]),max(q[3],r[3])]
                    a['cells']=sorted(set(a['cells']+b2['cells']));a['aligned_pairs']+=b2['aligned_pairs'];merged.pop(j);changed=True;break
    return merged,columns


def rule_segments(gray,height,*,slow=False):
    factor=1 if slow else max(1,int(np.ceil(max(gray.shape)/1400)),int(np.floor(height/10)))
    g=gray if factor==1 else cv2.resize(gray,(int(np.ceil(gray.shape[1]/factor)),int(np.ceil(gray.shape[0]/factor))),interpolation=cv2.INTER_AREA)
    sx=gray.shape[1]/g.shape[1];sy=gray.shape[0]/g.shape[0];h=height/sy
    # LSD resolves separate long edges at original pixels for the slow rendering.
    if slow:
        raw=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(g)[0]
        seg=[] if raw is None else raw.reshape(-1,4).tolist()
    else:
        k=max(1,int(round(3*h)))|1
        paper=cv2.boxFilter(g,cv2.CV_32F,(k,k));ink=(paper-g>255*.06).astype(np.uint8)
        # Bridge only short print breaks before long-run morphology.
        seg=[]
        for vertical in [False,True]:
            size=(max(1,int(.3*h)),1) if vertical else (1,max(1,int(.3*h)))
            mask=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones(size,np.uint8))
            size=(max(1,int(8*h)),1) if vertical else (1,max(1,int(8*h)))
            mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones(size,np.uint8))
            n,lab,stats,cc=cv2.connectedComponentsWithStats(mask,8)
            for x,y,w,hh,area in stats[1:]:
                if vertical:seg.append([x+w/2,y,x+w/2,y+hh])
                else:seg.append([x,y+hh/2,x+w,y+hh/2])
    out=[]
    for x0,y0,x1,y1 in seg:
        dx=x1-x0;dy=y1-y0
        if np.hypot(dx,dy)<8*h:continue
        direction='horizontal' if abs(dy)<.1*abs(dx) else 'vertical' if abs(dx)<.1*abs(dy) else None
        if direction is None:continue
        p=np.array([[x0*sx,y0*sy],[x1*sx,y1*sy]])
        if p[1,0]+p[1,1]<p[0,0]+p[0,1]:p=p[::-1]
        # Deduplicate the two edges of a rule, not its full thickness as ink.
        duplicate=False
        for q in out:
            qp=np.asarray(q['path']);short_axis=1 if direction=='horizontal' else 0;long_axis=1-short_axis
            if q['direction']==direction and abs(p[:,short_axis].mean()-qp[:,short_axis].mean())<.3*height:
                overlap=min(p[:,long_axis].max(),qp[:,long_axis].max())-max(p[:,long_axis].min(),qp[:,long_axis].min())
                if overlap>.7*min(np.ptp(p[:,long_axis]),np.ptp(qp[:,long_axis])):duplicate=True;break
        if not duplicate:out.append(dict(path=p.tolist(),direction=direction))
    return out


def intersections(rules,height):
    pairs=[]
    for i,a in enumerate(rules):
        if a['direction']!='horizontal':continue
        p=np.array(a['path']);xmin,xmax=sorted(p[:,0]);y=p[:,1].mean()
        for j,b in enumerate(rules):
            if b['direction']!='vertical':continue
            q=np.array(b['path']);ymin,ymax=sorted(q[:,1]);x=q[:,0].mean()
            if xmin-height*.5<x<xmax+height*.5 and ymin-height*.5<y<ymax+height*.5:pairs.append([i,j])
    return pairs


def analyze(gray,items,*,route='explicit',version=2):
    start=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0]))
    grid,columns=box_grid(items,h,version)
    rules=[];pairs=[];regions=[]
    if route!='heuristic':
        rules=rule_segments(gray,h,slow=route=='slow');pairs=intersections(rules,h)
        if pairs:
            mat=np.zeros((len(rules),len(rules)),bool)
            for i,j in pairs:mat[i,j]=mat[j,i]=True
            _,labels=connected_components(csr_matrix(mat))
            bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4)
            for group in np.unique(labels):
                ids=np.flatnonzero(labels==group).tolist()
                nh=sum(rules[i]['direction']=='horizontal' for i in ids);nv=len(ids)-nh
                if nh<2 or nv<2:continue
                pts=np.concatenate([rules[i]['path'] for i in ids]);a,t=pts.min(0);b,d=pts.max(0)
                cells=np.flatnonzero((bounds[:,0]>=a-h)&(bounds[:,2]<=b+h)&(bounds[:,1]>=t-h)&(bounds[:,3]<=d+h)&((bounds[:,2]-bounds[:,0])<8*h)).tolist()
                if len(cells)>=6:
                    regions.append(dict(bbox=[float(a),float(t),float(b),float(d)],rules=ids,cells=cells,source='intersecting rules with short cells'))
    # Repeated cell lattice is visible evidence even with broken/unprinted rules.
    # R1 labels this uncertain unless a rule actually runs through the region.
    for r in grid:
        backed=False
        for rule in rules:
            p=np.array(rule['path']).mean(0);a,t,b,d=r['bbox']
            if a-h<p[0]<b+h and t-h<p[1]<d+h:backed=True
        regions.append(dict(r,status='protect' if route=='heuristic' or backed else 'alignment hypothesis'))
    leaders=[]
    if version>=2:
        leaders,lr=leader_rows(gray,items,h,slow=route=='slow',heuristic=route=='heuristic',version=version)
        regions.extend(lr)
    for r in regions:r.setdefault('status','protect')
    return dict(regions=regions,rules=rules,intersections=pairs,columns=columns,height=h,seconds=perf_counter()-start,
                route=route,leaders=leaders,protected_indices=sorted(set(i for r in regions if r['status']=='protect' for i in r['cells'])),
                semantics='no semantic cells; protects new type corrections only')


def leader_rows(gray,items,height,*,slow=False,heuristic=False,version=2):
    """Repeated dots are rendered as individual centres before table inference."""
    factor=1 if slow else max(1,int(np.floor(height/(8 if heuristic else 16))))
    g=gray if factor==1 else cv2.resize(gray,(gray.shape[1]//factor,gray.shape[0]//factor),interpolation=cv2.INTER_AREA)
    sx=gray.shape[1]/g.shape[1];sy=gray.shape[0]/g.shape[0];h=height/sy
    k=max(1,int(3*h))|1;paper=cv2.boxFilter(g,cv2.CV_32F,(k,k))
    ink=(paper-g>255*.08).astype(np.uint8)
    n,labels,s,c=cv2.connectedComponentsWithStats(ink,8);s=s[1:];c=c[1:]
    dot_max=(.65 if version>=3 else .4)*h
    ids=np.flatnonzero((s[:,2]<dot_max)&(s[:,3]<dot_max)&(s[:,2]>.035*h)&(s[:,3]>.035*h)&(s[:,4]>.008*h*h))
    points=np.zeros_like(ink)
    if not len(ids):return [],[]
    if version>=5:
        # The localized route replaces the older flood-filled row census.
        rows=localized_leaders(c[ids],items,sx,sy,height)
    else:
        xy=np.rint(c[ids]).astype(int);points[xy[:,1],xy[:,0]]=1
        joined=cv2.dilate(points,np.ones((max(1,int(.4*h)),max(1,int(2*h))),np.uint8))
        _,groups=cv2.connectedComponents(joined,8)
        memberships=groups[xy[:,1],xy[:,0]];rows=[]
        for v in np.unique(memberships):
            ii=ids[memberships==v]
            if len(ii)<6:continue
            cc=c[ii];cc=cc[np.argsort(cc[:,0])];gaps=np.diff(cc[:,0]);pitch=float(np.median(gaps))
            if pitch<.35*h or pitch>2*h or np.median(abs(gaps-pitch))>.2*pitch:continue
            if np.ptp(cc[:,0])<6*h:continue
            coef=np.polyfit(cc[:,0],cc[:,1],1)
            if np.quantile(abs(cc[:,1]-np.polyval(coef,cc[:,0])),.9)>.18*h:continue
            rows.append(dict(points=(cc*[sx,sy]).tolist(),pitch=pitch*sx,
                bbox=[float(cc[:,0].min()*sx),float(cc[:,1].min()*sy-height*.3),float(cc[:,0].max()*sx),float(cc[:,1].max()*sy+height*.3)]))
    bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4);clusters=[]
    for row in sorted(rows,key=lambda r:r['bbox'][1]):
        a,t,b,d=row['bbox'];match=None
        for q in clusters:
            qa,qt,qb,qd=q['bbox'];overlap=min(b,qb)-max(a,qa)
            if overlap>.5*min(b-a,qb-qa) and t-qd<4*height:match=q;break
        if match is None:clusters.append(dict(bbox=list(row['bbox']),leader_rows=[row]));continue
        q=match;q['leader_rows'].append(row);q['bbox']=[min(a,q['bbox'][0]),q['bbox'][1],max(b,q['bbox'][2]),max(d,q['bbox'][3])]
    regions=[]
    for q in clusters:
        if len(q['leader_rows'])<3:continue
        a,t,b,d=q['bbox']
        if version>=4:
            yc=(bounds[:,1]+bounds[:,3])/2
            row_y=np.asarray([np.median(np.asarray(r['points'])[:,1]) for r in q['leader_rows']])
            near=np.min(abs(yc[:,None]-row_y),axis=1)<.6*height if len(yc) else np.empty(0,bool)
            ids=np.flatnonzero(near&(bounds[:,0]<b)&(bounds[:,2]>a)).tolist()
        else:
            ids=np.flatnonzero((bounds[:,1]<d+height)&(bounds[:,3]>t-height)&(bounds[:,0]<b)&(bounds[:,2]>a)).tolist()
        if ids:
            q['bbox']=[float(min(a,bounds[ids,0].min())),float(min(t,bounds[ids,1].min())),float(max(b,bounds[ids,2].max())),float(max(d,bounds[ids,3].max()))]
        q.update(cells=ids,source='repeated dot leaders on at least three rows',status='protect');regions.append(q)
    return rows,regions


def localized_leaders(centres,items,sx,sy,height):
    """Explicit dot-run chains inside each localized row; do not flood-fill
    punctuation into neighbouring rows. Candidate dots still come from pixels.
    """
    from .geometry import line_axis
    c=centres*np.array([sx,sy]);found=[];found_y=[]
    for it in items:
        a,t,b,d=bbox(it)
        if b-a<6*height:continue
        pts=c[(c[:,0]>=a)&(c[:,0]<=b)&(c[:,1]>=t)&(c[:,1]<=d)]
        if len(pts)<6:continue
        _,slope=line_axis(it);pts=pts[np.argsort(pts[:,0])]
        used=set();accepted_seeds=set()
        for i,j,chain,pitch in chains(pts,slope,height,pitch_max=2,vertical=.2,horizontal=.2,lookahead=5,min_remaining=6):
            if i in used or i in accepted_seeds:continue
            if len(chain)<6 or pts[chain[-1],0]-pts[i,0]<6*height:continue
            cc=pts[chain];cy=float(np.median(cc[:,1]))
            if any(abs(cy-ry)<.3*height and
                   min(cc[-1,0],r['bbox'][2])-max(cc[0,0],r['bbox'][0])>.5*(cc[-1,0]-cc[0,0]) for r,ry in zip(found,found_y)):continue
            found.append(dict(points=cc.tolist(),pitch=float(pitch),bbox=[float(cc[:,0].min()),float(cc[:,1].min()-.3*height),float(cc[:,0].max()),float(cc[:,1].max()+.3*height)]));found_y.append(cy);used.update(chain);accepted_seeds.add(i)
    return found
