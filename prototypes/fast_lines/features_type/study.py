"""Foreground, source-keyed feature studies and review artifacts."""
import argparse,json
from pathlib import Path
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,OUT,digest
from ..shared.type_profiles import analyze
from ..shared.review import save_image
from ..shared.timing import dump
from .reference import NAMED,DEST,COLORS,label

GC={'body_top':(210,130,0),'body_bottom':(20,70,220),'tall_top':(30,150,30),
    'descender_bottom':(170,60,180),'mark_top':(0,140,240),'mark_bottom':(0,195,245)}

def draw(gray,data,kind='guides'):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    for r in data['lines']:
        axis=r['axis'];a,b=r['xrange'];xh=r['xheight']
        if kind=='font':
            col=COLORS[r['size_group']%len(COLORS)]
            for c in r.get('components',[]):
                if c['role']=='body':cv2.polylines(im,[np.rint(c['polygon']).astype(np.int32)],True,col,1)
            for gap in r.get('gap_segments',[]):cv2.polylines(im,[np.rint(gap).astype(np.int32)],False,(200,70,150),1)
            y=axis[0]+axis[1]*a
            cv2.putText(im,f"{r['line']}:S{r['size_group']} h{xh:.1f}",(int(a),int(y)),cv2.FONT_HERSHEY_SIMPLEX,.42,col,1)
        else:
            for name,offset in r['guides'].items():
                p=np.array([[a,axis[0]+axis[1]*a+offset],[b,axis[0]+axis[1]*b+offset]],np.int32)
                cv2.polylines(im,[p],False,GC[name],1,cv2.LINE_AA)
            for c in r.get('components',[]):
                if c['role']=='mark':cv2.polylines(im,[np.rint(c['polygon']).astype(np.int32)],True,(0,140,240),1)
    return im


def typography(rows,version):
    key=digest(ROOT/'prototypes/fast_lines/shared/type_profiles.py')[:12]
    dest=DEST/f'type-v{version}-{key}';dest.mkdir(parents=True,exist_ok=True)
    for row in rows:
        name=row['page']; path=dest/(name+'.json')
        if path.exists():continue
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        slow=analyze(gray,items,route='slow',detail=True,version=version)
        routes={'slow':slow}
        # Explicit slow rendering is written first; fast execution can be a later command.
        for feature in ['font','guides']:
            save_image(dest/(name+f'.slow.{feature}.jpg'),label(draw(gray,slow,feature),name+' | original-pixel component contacts'))
        dump(path,dict(page=name,input_sha256=row['sha256'],source=key,slow=slow))
        print(name,'slow',round(slow['seconds'],3),'groups',len(slow['size_groups']),flush=True)
    dump(DEST/'active-type.json',dict(directory=str(dest.relative_to(ROOT)),version=version))
    return dest


def fast(rows,dest,version):
    for row in rows:
        name=row['page'];path=dest/(name+'.json');data=json.loads(path.read_text())
        if 'explicit' in data:continue
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        for route in ['explicit','heuristic']:
            data[route]=analyze(gray,items,route=route,detail=True,version=version)
        perline=[]
        for a,b,c in zip(data['slow']['lines'],data['explicit']['lines'],data['heuristic']['lines']):
            perline.append(dict(line=a['line'],slow_height=a['xheight'],route1_height=b['xheight'],route2_height=c['xheight'],
                route1_delta_xh=(b['xheight']-a['xheight'])/a['xheight'],route2_delta_xh=(c['xheight']-a['xheight'])/a['xheight'],
                slow_guides=a['guides'],route1_guides=b['guides'],route2_guides=c['guides'],
                route1_guide_errors={k:(b['guides'][k]-v)/a['xheight'] for k,v in a['guides'].items() if k in b['guides']},
                slow_marks=a['mark_count'],fast_marks=b['mark_count']))
        data['per_line']=perline;dump(path,data)
        for feature in ['font','guides']:
            ims=[draw(gray,data[r],feature) for r in ['slow','explicit','heuristic']]
            for r,im in zip(['slow','explicit','heuristic'],ims):
                save_image(dest/(name+f'.{r}.{feature}.jpg'),label(im,name+' | '+r+' '+feature))
            # Review all detector lines against the explicit rendering, not ours list.
            from ..shared.contracts import bbox
            tiles=[]
            for i,it in enumerate(items):
                a,t,b,d=bbox(it);pad=.4*data['slow']['lines'][i]['xheight']
                a=max(0,int(a));b=min(gray.shape[1],int(b)+1);t=max(0,int(t-pad));d=min(gray.shape[0],int(d+pad)+1)
                crops=[]
                for im in [cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)]+ims:
                    crop=im[t:d,a:b];sc=min(1.,1000/max(1,b-a));crops.append(cv2.resize(crop,None,fx=sc,fy=sc))
                q=perline[i];tile=label(np.vstack(crops),f"line {i} raw/slow/R1/R2; h {q['slow_height']:.1f}/{q['route1_height']:.1f}/{q['route2_height']:.1f}")
                canvas=np.full((tile.shape[0]+5,1100,3),255,np.uint8);canvas[:tile.shape[0],:tile.shape[1]]=tile;tiles.append(canvas)
            for start in range(0,len(tiles),5):save_image(dest/(name+f'.{feature}.detail-{start//5:02d}.jpg'),np.vstack(tiles[start:start+5]))
        print(name,[(r,round(data[r]['seconds'],3)) for r in ['slow','explicit','heuristic']],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);p.add_argument('--pages',nargs='*');args=p.parse_args()
    names=args.pages or NAMED; rows=[r for r in manifest()['pages'] if r['page'] in names]
    cv2.setNumThreads(1)
    if args.action=='slow':typography(rows,args.version)
    else:fast(rows,ROOT/json.loads((DEST/'active-type.json').read_text())['directory'],args.version)
