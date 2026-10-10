"""Slow normal profiles versus dense/reduced sparse measurements, per line."""
import json,argparse
import cv2,numpy as np
from PIL import Image,ImageDraw
from ..round2 import ROOT,manifest,get_baseline
from ..shared.geometry import height_proxy,roi
from ..shared.contracts import bbox
from ..shared.ink_edges import profiles
from ..shared.timing import dump
from .study import DEST


def run(version='edge-profiles-v2'):
    wanted=['s2-0ce9d1025b3f23c7119e-p00001','s2-09f5dfca4af4d74173c6-p00005',
            'an-1be60011c435-p000215','s2-86865c33eef5932c013b-p00005']
    cv2.setNumThreads(1);dest=DEST/version;dest.mkdir(parents=True,exist_ok=True)
    for row in manifest()['pages']:
        if row['page'] not in wanted:continue
        p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size']);records=[];tiles=[]
        for i,q in enumerate(items):
            b=bbox(q);slow=profiles(gray,b,h,detail=True,budget=256)
            explicit=profiles(gray,b,h,budget=48,samples=41);heur=profiles(gray,b,h,budget=8,samples=25)
            records.append(dict(line=i,bbox=b,slow=slow,route1=explicit,route2=heur))
            x,y,z,t=roi(b,gray.shape);raw=Image.fromarray(gray[y:t,x:z]).convert('RGB');raw.thumbnail((1000,140))
            tile=Image.new('RGB',(1400,max(150,raw.height+38)),'white');tile.paste(raw,(0,30));d=ImageDraw.Draw(tile)
            d.text((5,4),f"line {i}: 20-80 edge width/body slow {slow['edge_width_h']} / R1 {explicit['edge_width_h']} / R2 {heur['edge_width_h']}",fill='black')
            sx=raw.width/(z-x);sy=raw.height/(t-y)
            for j,r in enumerate(slow['profiles'][::max(1,len(slow['profiles'])//5)][:5]):
                xx,yy=r['point'];d.ellipse(((xx-x)*sx-2,(yy-y)*sy+28,(xx-x)*sx+2,(yy-y)*sy+32),fill='blue')
                vv=np.array(r['gray']);vv=(vv-vv.min())/max(np.ptp(vv),1)
                pts=[(1030+k*340/(len(vv)-1),130-float(v)*90) for k,v in enumerate(vv)]
                d.line(pts,fill=['blue','green','red','purple','orange'][j],width=1)
            tiles.append(tile)
        for off in range(0,len(tiles),6):
            group=tiles[off:off+6];out=Image.new('RGB',(1400,sum(t.height for t in group)),'white');y=0
            for tile in group:out.paste(tile,(0,y));y+=tile.height
            out.save(dest/f'{p}.{off//6:02d}.jpg',quality=93)
        dump(dest/(p+'.json'),dict(page=p,lines=records,meaning='Profile crossings separate spread from amplitude; peaks can belong to paper or overlapping strokes'))
        print('edges',p,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='edge-profiles-v2');args=ap.parse_args();run(args.version)
