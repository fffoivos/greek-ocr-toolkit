"""Reproducible one-shot diagnostics; refuses to overwrite completed experiments."""
import argparse,json
import cv2,numpy as np
from .round5_data import rows,load,DEST
from ..shared.geometry_envelopes import analyze,guided
from ..shared.timing import dump

def draw(gray,items,data,path):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);h=data['height']
    for q in items:
        if not q.get('discounted'):cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(165,165,165),1)
    for r in data['lines']:
        p=np.rint(r['path']).astype(np.int32);s=np.asarray(r['observed'])
        for j in range(len(p)-1):
            if s[j] and s[j+1]:cv2.line(im,tuple(p[j]),tuple(p[j+1]),(0,150,0),2)
        for c in r['contacts']:
            a,b,z,w=map(round,c['bbox']);cv2.rectangle(im,(a,b),(z,w),(0,150,220),1)
        if r.get('polygon'):cv2.polylines(im,[np.rint(r['polygon']).astype(np.int32)],True,(180,0,180) if not r.get('ambiguous') else (0,0,220),2)
        cv2.putText(im,str(r['line']),(int(p[len(p)//2,0]),int(p[len(p)//2,1])),0,.5,(180,0,180),1)
    s=min(1.,1700/im.shape[1]);im=cv2.resize(im,None,fx=s,fy=s);cv2.imwrite(str(path),im)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,default=1);ap.add_argument('--route',default='slow');ap.add_argument('--pages',nargs='+');a=ap.parse_args()
    out=DEST/f'shapes-v{a.version}-{a.route}';out.mkdir(parents=True,exist_ok=True)
    for r in rows():
        if a.pages and not any(k in r['page'] for k in a.pages):continue
        dst=out/(r['page']+'.json')
        if dst.exists():raise RuntimeError('experiment already recorded '+str(dst))
        gray,obj,pm=load(r);result=(analyze(gray,obj['items'],a.route,a.version) if a.version==1 else guided(gray,pm,obj['items'],obj['original'],a.route,a.version))
        dump(dst,result);draw(gray,obj['items'],result,dst.with_suffix('.jpg'));print(r['page'],len(result['lines']),round(result['seconds'],3),flush=True)
if __name__=='__main__':main()
