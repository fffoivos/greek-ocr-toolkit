"""Independent skew audit: original-ink contacts versus map paths and box axes.

Only the central observed span is fitted. Low residual is rendered as evidence,
not a certificate of straightness or an instruction to rotate the whole page.
"""
import argparse,json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.geometry import robust_fit,line_axis,roi
from ..shared.manifest import ROOT
from ..shared.timing import dump
from ..shared.review import save_image
from .reference import DEST,save,line


def fit(q,trim=.15,version=1):
    p=np.asarray(q['path']);b=q['bbox'];good=np.asarray(q['observed'])&(p[:,0]>b[0]+trim*(b[2]-b[0]))&(p[:,0]<b[2]-trim*(b[2]-b[0]))
    if good.sum()<15:return None
    x,y=p[good].T;a,s=robust_fit(x,y);res=np.quantile(abs(y-a-s*x),.9)/q['height']
    all_good=np.asarray(q['observed'])
    residual=abs(p[:,1]-a-s*p[:,0])/q['height']
    outer=all_good&((p[:,0]<x.min())|(p[:,0]>x.max()))
    outer_error=float(np.quantile(residual[outer],.9)) if outer.any() else None
    compatible=bool(res<.25)
    if version>=2:compatible=compatible and outer_error is not None and outer_error<.35
    return dict(outer_residual_h=outer_error,intercept=float(a),slope=float(s),angle_deg=float(np.degrees(np.arctan(s))),residual_h=float(res),
        span=[float(x.min()),float(x.max())],path=[[float(x.min()),float(a+s*x.min())],[float(x.max()),float(a+s*x.max())]],
        provisional_straight=compatible,contacts=int(good.sum()))


def run(rows,version):
    out=DEST/f'round4/skew-v{version}';out.mkdir(parents=True,exist_ok=True)
    for r in rows:
        p=r['page'];body=json.loads((DEST/'round4/body-slow-v7'/(p+'.json')).read_text());maps=json.loads((DEST/'routes-v4'/(p+'.json')).read_text())
        original=get_baseline(r);gray=cv2.imread(str(ROOT/r['path']),0);im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);records=[]
        maplines={q['line']:q for q in maps['route1']['lines']}
        for q in body['lines']:
            native=fit(q,.15,version)
            if native is None:continue
            b=q['bbox'];h=q['height'];m=maplines.get(q['line']);r1=None
            if m and m.get('path'):
                mp=np.asarray(m['path']);good=(mp[:,0]>=native['span'][0])&(mp[:,0]<=native['span'][1])
                if good.sum()>=8:
                    a,s=robust_fit(mp[good,0],mp[good,1]);r1=dict(slope=float(s),angle_deg=float(np.degrees(np.arctan(s))))
            a,s=line_axis(original[q['line']]);r2=dict(slope=float(s),angle_deg=float(np.degrees(np.arctan(s))))
            # Compare slopes at the same centre; centre offsets are a separate feature.
            centre=np.mean(native['path'],axis=0);xs=np.asarray(native['span'])
            line(im,q['path'],(170,170,170),1);line(im,native['path'],(30,170,20) if native['provisional_straight'] else (0,150,230),3)
            if r1:line(im,np.c_[xs,centre[1]+r1['slope']*(xs-centre[0])],(190,30,180),1)
            line(im,np.c_[xs,centre[1]+r2['slope']*(xs-centre[0])],(220,140,0),1)
            records.append(dict(line=q['line'],native=native,route1=r1,route2=r2,
                r1_end_error_h=abs(r1['slope']-native['slope'])*np.ptp(xs)/h if r1 else None,
                r2_end_error_h=float(abs(r2['slope']-native['slope'])*np.ptp(xs)/h)))
        save(out/(p+'.jpg'),im,p+' | contact fit green/uncertain amber; map purple; box cyan (common centre)')
        dump(out/(p+'.json'),dict(page=p,lines=records,version=version))
        # First six strongest apparent pure-skew spans, for raw visual validation.
        ranked=sorted([q for q in records if q['native']['provisional_straight']],key=lambda q:abs(q['native']['angle_deg']),reverse=True)[:6]
        tiles=[]
        for q in ranked:
            bodyline=next(x for x in body['lines'] if x['line']==q['line']);b=np.array(bodyline['bbox']);h=bodyline['height'];x0,y0,x1,y1=roi(b+[-h,-h,h,h],gray.shape)
            tile=np.vstack([cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR),im[y0:y1,x0:x1]]);scale=min(1,1400/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale)
            panel=np.full((tile.shape[0]+25,1400,3),255,np.uint8);panel[25:,:tile.shape[1]]=tile
            label=f"source{q['line']} native {q['native']['angle_deg']:.3f} deg; residual {q['native']['residual_h']:.3f}h"
            cv2.putText(panel,label,(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1);tiles.append(panel)
        if tiles:save_image(out/(p+'.detail.jpg'),np.vstack(tiles))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,default=1);p.add_argument('--pages',nargs='*');a=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages']
    if a.pages:rows=[r for r in rows if r['page'] in a.pages]
    run(rows,a.version)
