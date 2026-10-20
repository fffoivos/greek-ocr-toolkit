"""Anonymous repeated-glyph witnesses per page and per supplied book pages."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_identity import extract,sample,witnesses,tile
from ..shared.timing import dump
from ..shared.review import save_image
from .reference import DEST,label

NAMES=['an-d83e7a198ade-p000099','an-ffccc97c07de-p000152','an-d3237d690aa0-p000138']

def run(action,version):
    rows=[r for r in manifest()['pages'] if r['page'] in NAMES or 'an-1ba3' in r['page']]
    dest=DEST/f'round4-identity-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_identity.py")[:12]}';dest.mkdir(exist_ok=True)
    pages={}
    for row in rows:
        g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);allglyphs,sec=extract(g,items,version=version);glyphs=sample(allglyphs)
        pages[row['page']]=(g,glyphs,allglyphs,sec,row)
        if action=='slow':
            im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
            for q in allglyphs:
                a,t,b,d=q['bbox'];cv2.rectangle(im,(a,t),(b,d),(20,140,30),1)
            save_image(dest/(row['page']+'.components.jpg'),label(im,row['page']+' original components, not recognized characters'))
    pairs=[(p,p) for p in pages]+[(p,q) for p in pages for q in pages if p<q and 'an-1ba3' in p and 'an-1ba3' in q]
    for p,q in pairs:
        pg,pp,allp,ps,pr=pages[p];qg,qq,allq,qs,qr=pages[q];stem=p+'__'+q;f=dest/(stem+'.json')
        if action=='slow':data=dict(query=p,atlas=q,input_sha256=[pr['sha256'],qr['sha256']],glyphs=[[{k:v for k,v in g.items() if k!='ink'} for g in arr] for arr in [pp,qq]],extraction_s=[ps,qs],slow=witnesses(pp,qq,same_page=p==q,route='slow',version=version))
        else:
            data=json.loads(f.read_text())
            for r in ['explicit','heuristic']:data[r]=witnesses(pp,qq,same_page=p==q,route=r,version=version)
            if version>=3:
                from .identity_routes import heuristic
                data['heuristic']=heuristic(pp,qq,same_page=p==q)
        data['study_sha256']=digest(Path(__file__))
        dump(f,data)
        routes=['slow'] if action=='slow' else ['slow','explicit','heuristic']
        # Cover each line having a candidate; show strongest plus an alternate.
        chosen={}
        for match in data['slow']['pairs']:
            line=pp[match['query']]['line'];old=chosen.get(line)
            if old is None or match['alternatives'][0]['similarity']>old['alternatives'][0]['similarity']:chosen[line]=match
        tiles=[]
        for line,match in sorted(chosen.items()):
            i=match['query'];a,t,b,d=pp[i]['bbox'];raw=pg[t:d,a:b];panels=[];caption=[]
            for route in routes:
                m=next((m for m in data[route]['pairs'] if m['query']==i),None)
                for z in ([] if m is None else m['alternatives'][:2]):
                    j=z['atlas'];aa,tt,bb,dd=qq[j]['bbox'];target=qg[tt:dd,aa:bb]
                    panel=np.full((100,210,3),255,np.uint8)
                    for im,x in [(raw,0),(target,110)]:
                        scale=min(90/im.shape[0],90/im.shape[1]);r=cv2.resize(im,None,fx=scale,fy=scale);panel[5:5+r.shape[0],x+5:x+5+r.shape[1]]=cv2.cvtColor(r,cv2.COLOR_GRAY2BGR)
                    panels.append(panel);caption.append(f'{route} line{qq[j]["line"]} {z["similarity"]:.3f}')
            if not panels:continue
            board=np.hstack(panels)
            if board.shape[1]>1050:board=cv2.resize(board,None,fx=1050/board.shape[1],fy=1050/board.shape[1])
            tiles.append(label(board,f'line{line} glyph{i} | '+ ' / '.join(caption)))
        for i in range(0,len(tiles),8):save_image(dest/(stem+f'.{action}.pairs-{i//8:02d}.jpg'),np.vstack(tiles[i:i+8]))
        print(p,q,len(pp),len(qq),len(data['slow']['pairs']),flush=True)
    dump(DEST/'active-identity4.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version)
