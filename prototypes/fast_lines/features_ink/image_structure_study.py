"""Image/stamp evidence on native pixels, reduced explicit and heuristic routes."""
import argparse,json,cv2
import numpy as np
from PIL import Image,ImageDraw
from time import perf_counter
from ..round2 import manifest,ROOT,get_baseline
from ..shared.geometry import height_proxy
from ..shared.ink_image_structure import render as structure
from ..shared.ink_stamp_field import render as polar
from ..shared.ink_type_identity import extract
from ..shared.ink_images import render as area_ink
from ..shared.timing import dump
from .study import DEST


def run(version):
    cv2.setNumThreads(1);dest=DEST/'round4'/f'image-structure-v{version}';dest.mkdir(parents=True,exist_ok=True)
    wanted=['an-d6002cf45e4d-p000058','an-1f8e7d022643-p000003','an-1be60011c435-p000215','an-778126cc8c2b-p000011','s2-77d1bd63d5babbe0df73-p00001','s2-09f5dfca4af4d74173c6-p00005','s2-200e977f2dab5291c42c-p00035']
    for row in manifest()['pages']:
        p=row['page']
        if p not in wanted:continue
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size']);records={};products={}
        glyphs,extraction_s=extract(gray,items,version=2)
        area=area_ink(gray,h) if version>=3 else None
        for route in ('slow','explicit','heuristic'):
            t=perf_counter();v=structure(gray,h,route=route,version=version);seconds=perf_counter()-t;products[route]=v
            records[route]={k:x for k,x in v.items() if k not in ('raw','mask')};records[route]['seconds']=seconds
            rgb=np.repeat(v['raw'][:,:,None],3,2);rgb[v['mask']>0]=(255,0,160)
            im=Image.fromarray(rgb);s=min(1.,1500/max(im.size));im=im.resize((round(im.width*s),round(im.height*s)));dr=ImageDraw.Draw(im)
            if version>=3:
                candidate=cv2.resize(area['mask'],v['raw'].shape[::-1],interpolation=cv2.INTER_NEAREST)>0
                conflict=[]
                for g in glyphs:
                    b=[x*v['scale']*s for x in g['bbox']]
                    x0,y0,x1,y1=[round(x*v['scale']) for x in g['bbox']];overlap=bool(candidate[y0:y1,x0:x1].any())
                    dr.rectangle(b,outline=(255,140,0) if overlap else (0,160,80),width=1)
                    if overlap:conflict.append(dict(bbox=g['bbox'],owners=g['owners']))
                records[route]['potential_text_intersections']=conflict
            dr.text((10,10),route+' edges magenta; components green; area/component conflict amber; ownership unknown',fill='blue')
            im.save(dest/f'{p}.{route}.jpg',quality=93)
        refs=[DEST/v/(p+'.json') for v in ('reference-v3','reference-v4-controls')]
        rings=[]
        for ref in refs:
            if ref.exists():rings=json.loads(ref.read_text()).get('stamps',{}).get('rings',[]);break
        polar_records=[]
        for i,ring in enumerate(rings):
            panels=[];rrec=[]
            for route in ('slow','explicit','heuristic'):
                t=perf_counter();v=polar(gray,ring,h,route=route,version=version);seconds=perf_counter()-t
                raw=Image.fromarray(v['raw']).convert('RGB').resize((1400,220));tile=Image.new('RGB',(1400,340),'white');tile.paste(raw,(0,40));dr=ImageDraw.Draw(tile)
                dr.text((5,5),f'{p} ring{i} {route}: angle left to right, radius .5 to1.25 top to bottom; no ownership at crossings',fill='black')
                profile=v['profile'];mx=max(float(max(profile)),1e-6)
                for k in range(len(profile)-1):
                    x0=k*1400/(len(profile)-1);x1=(k+1)*1400/(len(profile)-1);dr.line((x0,330-profile[k]/mx*60,x1,330-profile[k+1]/mx*60),fill='purple',width=2)
                for r in v['rings']:
                    y=40+(r['radius_factor']-.5)/.75*220;dr.line((0,y,1400,y),fill='cyan',width=1)
                panels.append(tile);rrec.append(dict(route=route,seconds=seconds,rings=v['rings'],source=ring,ownership=v['ownership'],safe_exclusions=[]))
            out=Image.new('RGB',(1400,1020),'white')
            for j,im in enumerate(panels):out.paste(im,(0,j*340))
            out.save(dest/f'{p}.polar-{i}.jpg',quality=94);polar_records.append(rrec)
        records.update(page=p,height=h,component_extraction_s=extraction_s,components=len(glyphs),polar=polar_records)
        dump(dest/(p+'.json'),records);print(p,[len(records[r]['segments']) for r in ('slow','explicit')],flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,default=1);run(ap.parse_args().version)
