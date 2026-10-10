"""Dense displacement field, reduced field, projection proxy, original witnesses."""
import argparse,cv2,json
import numpy as np
from PIL import Image,ImageDraw
from ..round2 import ROOT,manifest
from ..shared.ink_repeat_field import analyze,bands
from ..shared.timing import dump
from .study import DEST


def run(version='repeat-field-v2'):
    cv2.setNumThreads(1);dest=DEST/'round4'/version;dest.mkdir(parents=True,exist_ok=True);records=[];tiles=[]
    for row in manifest()['pages']:
        p=row['page'];d=json.loads((DEST/'study-v1'/(p+'.evidence.json')).read_text())
        selected=[m for m in d['motifs'] if 'remaining_glyphs' in m]
        if not selected:continue
        gray=cv2.imread(str(ROOT/row['path']),0);h=d['ownership']['height']
        for m in selected:
            i=m['line'];item=d['r2']['items'][i];dense=analyze(gray,item,h,samples=h,detail=True);fast=analyze(gray,item,h,samples=8,detail=True)
            rec=dict(page=p,line=i,old_accepted=m['drop'])
            sub=bands(gray,item,h,samples=8,detail=True);ds=bands(gray,item,h,samples=h,detail=True)
            rec['subband']={k:v for k,v in sub['best'].items() if k!='field'};rec['subband_dense']={k:v for k,v in ds['best'].items() if k!='field'};rec['nominate']=sub['nominate']
            for name,v in [('dense',dense),('route1',fast)]:rec[name]={k:x for k,x in v.items() if k not in ('raw','field','scale')}
            records.append(rec);raw=Image.fromarray(dense['raw']).convert('RGB');raw.thumbnail((1400,180))
            tile=Image.new('RGB',(1400,raw.height+210),'white');tile.paste(raw,(0,40));dr=ImageDraw.Draw(tile)
            dr.text((5,5),f'{p} L{i} accepted{m["drop"]} band dense{ds["best"]["repeat"]:.3f} R1{sub["best"]["repeat"]:.3f} consecutive{ds["best"]["consecutive"]}/{sub["best"]["consecutive"]} gate{sub["nominate"]}',fill='black')
            for j,v in enumerate([ds['best'],sub['best']]):
                if 'field' not in v:continue
                heat=cv2.applyColorMap(np.uint8(np.clip(v['field'],0,1)*255),cv2.COLORMAP_TURBO)[:,:,::-1]
                tile.paste(Image.fromarray(heat).resize((650,130)),(j*700,raw.height+60))
                dr.text((j*700+5,raw.height+195),f'lag0.7..8h / vertical +-.65h: peak {v["lag_h"]:.2f}, {v["dy_h"]:.2f}',fill='black')
            tiles.append(tile)
    for off in range(0,len(tiles),4):
        group=tiles[off:off+4];out=Image.new('RGB',(1400,sum(x.height for x in group)),'white');y=0
        for im in group:out.paste(im,(0,y));y+=im.height
        out.save(dest/f'{off//4:02d}.jpg',quality=93)
    dump(dest/'records.json',records)
    for r in records:print(r['page'],r['line'],r['old_accepted'],r['nominate'],round(r['subband']['repeat'],3),r['subband']['consecutive'],flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='repeat-field-v2');a=ap.parse_args();run(a.version)
