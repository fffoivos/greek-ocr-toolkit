"""Offline explicit geometry from active six-guide records and original pixels.

Saved guides are expensive model hypotheses, not truth. This module never runs
in the correction path. The exact Q8 manifest is the only page allowlist.
"""
import argparse
import json
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from ..round2 import manifest, contacts, get_baseline
from ..shared.manifest import ROOT, OUT, digest
from ..shared.geometry import robust_fit, quantize
from ..shared.review import save_image
from ..shared.timing import dump

DEST = OUT/'features_geometry'
FEATURES = ('curvature', 'skew', 'separation')
COLORS = {'baseline':(30,155,20), 'meanline':(220,140,0),
          'font_top':(220,100,210), 'font_bottom':(180,80,160),
          'accent_top':(0,145,230), 'accent_bottom':(0,200,230)}


def ours_path(row):
    return (ROOT/'.astra/fast_lines/ours_lines'/(row['page']+'.lines.json')
            if row['group']=='development' else (ROOT/row['path']).with_name(row['page']+'.ours.lines.json'))


def active_guides(row):
    qs=json.loads(ours_path(row).read_text()); rows=[]
    for i,q in enumerate(qs):
        if q.get('discounted'): continue
        x=np.arange(q['x0'],q['x1'],dtype=float)
        if len(x)<3: continue
        step=max(1,quantize(q['xheight']/3)); ids=np.unique(np.r_[np.arange(0,len(x),step),len(x)-1])
        mid=(np.asarray(q['baseline'])+np.asarray(q['meanline']))/2
        centre=(x>x[0]+.25*np.ptp(x))&(x<x[0]+.75*np.ptp(x))
        if centre.sum()<3: centre=np.ones(len(x),bool)
        a,b=robust_fit(x[centre],mid[centre]); affine=a+b*x
        rows.append(dict(id=i,height=q['xheight'],column=q.get('column'),
            support=q.get('support'),borrowed=q.get('borrowed'),
            source=q.get('geometry_source'),guides={k:np.c_[x[ids],np.asarray(q[k])[ids]].tolist() for k in COLORS},
            centre=np.c_[x[ids],mid[ids]].tolist(),affine=np.c_[x[ids],affine[ids]].tolist(),
            angle_deg=float(np.degrees(np.arctan(b))),
            bend_h=float(np.max(abs(mid-affine))/q['xheight'])))
    return rows


def corridors(gray,height,version=1):
    """Dense pixel whitespace in overlapping layout bands; no box/line truth.

    Persistent absence is rendered, not declared a physical leaf. A print rule
    intentionally does not count as whitespace; it is rendered separately.
    """
    h=height; H,W=gray.shape
    paper=cv2.boxFilter(gray,cv2.CV_32F,(quantize(4*h)|1,quantize(4*h)|1))
    ink=(paper-gray>255*.06).astype(np.uint8)
    integral=cv2.integral(ink,sdepth=cv2.CV_32S)
    support_integral=integral
    if version>=2:
        _,labels,stats,_=cv2.connectedComponentsWithStats(ink,8)
        valid=((stats[:,3]>=.2*h)&(stats[:,3]<=2.5*h)&
               (stats[:,2]<=4*h)&(stats[:,4]>=.035*h*h))
        valid[0]=False
        support_integral=cv2.integral(valid[labels].astype(np.uint8),sdepth=cv2.CV_32S)
    bands=[]
    for y0 in range(0,H,quantize(6*h)):
        y1=min(H,y0+quantize(12*h))
        if y1-y0<6*h: continue
        density=np.diff(integral[y1]-integral[y0])/(y1-y0)
        support=np.diff(support_integral[y1]-support_integral[y0])/(y1-y0)
        clear=density<(.015 if version==1 else .008)
        edges=np.diff(np.r_[False,clear,False].astype(int))
        for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            if b-a<1.5*h or a<6*h or b>W-6*h: continue
            left=support[max(0,a-quantize(6*h)):a];right=support[b:min(W,b+quantize(6*h))]
            if min(left.mean(),right.mean())<.025:continue
            bands.append(dict(bbox=[int(a),int(y0),int(b),int(y1)],width_h=float((b-a)/h),
                              flank_density=[float(left.mean()),float(right.mean())]))
    return bands


def line(im,path,color,width=1):
    if len(path)>=2:cv2.polylines(im,[np.rint(path).astype(np.int32)],False,color,width,cv2.LINE_AA)


def canvas(gray,title):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    # Titles are attached on save, outside the page coordinate system.
    return im


def save(path,im,title,width=1400):
    s=min(1,width/im.shape[1]); im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    out=np.full((im.shape[0]+50,im.shape[1],3),255,np.uint8);out[50:]=im
    cv2.putText(out,title,(8,19),cv2.FONT_HERSHEY_SIMPLEX,.44,(20,20,20),1,cv2.LINE_AA)
    cv2.putText(out,'Hypotheses on original pixels; discounted lines omitted; see README legend',(8,39),cv2.FONT_HERSHEY_SIMPLEX,.40,(30,30,30),1,cv2.LINE_AA)
    save_image(path,out)


def render(gray,ref,feature,version=1):
    im=canvas(gray,feature)
    if feature=='separation':
        for c in ref['corridors']:
            x0,y0,x1,y1=c['bbox'];p=im[y0:y1,x0:x1]
            p[:]=(.75*p+.25*np.array([255,180,0])).astype(np.uint8)
        for r in ref['rules']:
            if r['direction']=='vertical':
                b=r['bbox'];line(im,r.get('path',[[sum(b[::2])/2,b[1]],[sum(b[::2])/2,b[3]]]),(0,130,240),2)
        return im
    for q in ref['lines']:
        if feature=='curvature':
            if version==1:
                for k in COLORS:line(im,q['guides'][k],COLORS[k])
            else:
                line(im,q['guides']['baseline'],COLORS['baseline'],2)
                line(im,q['guides']['meanline'],COLORS['meanline'])
                line(im,q['affine'],(140,140,210))
                a=np.asarray(q['centre']);b=np.asarray(q['affine'])
                for j in np.linspace(0,len(a)-1,9).astype(int):
                    line(im,[a[j],b[j]],(0,125,240),2)
        else:
            line(im,q['centre'],(80,170,80))
            line(im,q['affine'],(210,30,180),2)
            a=np.asarray(q['affine']);x,y=a[len(a)//2]
            cv2.putText(im,f"{q['id']}:{q['angle_deg']:+.2f}",(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,.45,(160,0,150),1)
    return im


def run(rows,version):
    dest=DEST/f'explicit-v{version}';dest.mkdir(parents=True,exist_ok=True)
    for i,r in enumerate(rows):
        p=r['page'];fp=dest/(p+'.json')
        if fp.exists():continue
        gray=cv2.imread(str(ROOT/r['path']),0);t=perf_counter()
        guides=active_guides(r) if not r['parked'] else []
        heights=[q['height'] for q in guides];height=float(np.median(heights)) if heights else min(gray.shape)/100
        previous=OUT/'round2/rule_separators/references'/(p+'.json')
        rules=json.loads(previous.read_text())['evidence'].get('rules',[]) if not r['parked'] else []
        ref=dict(page=p,lines=guides,corridors=corridors(gray,height,version) if not r['parked'] else [],
                 rules=rules,height=height,parked=r['parked'],image_sha256=digest(ROOT/r['path']),
                 guides_sha256=digest(ours_path(r)),guides_source=str(ours_path(r).relative_to(ROOT)),
                 rules_source=str(previous.relative_to(ROOT)),seconds=perf_counter()-t,
                 warning='Active cached model guides and dense pixels; neither is ground truth.')
        dump(fp,ref)
        for feature in FEATURES:
            save(dest/(p+'.'+feature+'.jpg'),render(gray,ref,feature,version),p+' | explicit '+feature)
        if (i+1)%20==0:print('explicit',version,i+1,len(rows),flush=True)
    for feature in FEATURES:
        contacts(rows,dest,'.'+feature+'.jpg',dest/'sheets'/feature)
    print('complete',dest,len(rows),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,default=1);p.add_argument('--pages',nargs='*');args=p.parse_args()
    cv2.setNumThreads(1);rows=manifest()['pages']
    if args.pages: rows=[r for r in rows if r['page'] in args.pages]
    run(rows,args.version)
