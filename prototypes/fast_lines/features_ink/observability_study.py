"""Native glyph-local noise and stroke renderings, with both fast routes."""
import argparse,cv2,json
import numpy as np
from PIL import Image,ImageDraw
from time import perf_counter
from ..round2 import manifest,ROOT,get_baseline
from ..shared.ink_type_identity import extract,sample,witnesses
from ..shared.ink_observability import measure
from ..shared.timing import dump
from .study import DEST

def run(version):
    cv2.setNumThreads(1);dest=DEST/'round4'/version;dest.mkdir(parents=True,exist_ok=True);summary=[]
    rows=[r for r in manifest()['pages'] if r['page']=='an-1be60011c435-p000215' or r['page'].startswith(('s2-77d1','s2-0ce9','an-ef481610a820-p000150','an-778126cc8c2b-p000011'))]
    for row in rows:
        p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        atlas,extraction_s=extract(gray,items,version=2);glyphs=sample(atlas,per_line=4);records=[];maps=[];timings={}
        for route in ('slow','explicit','heuristic'):
            start=perf_counter();values=[]
            for g in glyphs:values.append(measure(gray,g['bbox'],g['height'],route=route,detail=True,version=int(version[-1])))
            timings[route]=perf_counter()-start
            for i,v in enumerate(values):
                if route=='slow':records.append(dict(glyph=i,bbox=glyphs[i]['bbox'],owners=glyphs[i]['owners']));maps.append({})
                records[i][route]={k:x for k,x in v.items() if k not in ('raw','masks','certain','possible')};maps[i][route]=v
        # Own physical coordinates may not be an independent witness.
        shape=witnesses(glyphs,atlas,route='slow',same_page=True,version=2)
        for rec in records:rec['alternatives']=next((r['alternatives'] for r in shape['pairs'] if r['query']==rec['glyph']),[])
        selected=sorted(range(len(records)),key=lambda i:records[i]['slow']['core_snr'])[:16]
        selected+=sorted(range(len(records)),key=lambda i:-np.ptp([t['components']+t['holes'] for t in records[i]['slow']['thresholds']]))[:16]
        selected=list(dict.fromkeys(selected));panels=[]
        for i in selected:
            r=records[i];tile=Image.new('RGB',(1400,230),'white');dr=ImageDraw.Draw(tile)
            dr.text((5,5),f'{p} component{i} owners{r["owners"]} bbox{r["bbox"]} | readability UNKNOWN; slow noise-topology stable {r["slow"]["topology_stable"]}',fill='black')
            for col,route in enumerate(('slow','explicit','heuristic')):
                v=maps[i][route];x=col*460
                dr.text((x+5,28),f'{route}: depth{v["depth_dn"]:.1f} noise{v["noise_dn"]:.2f} SNR{v["core_snr"]:.1f}',fill='black')
                raw=Image.fromarray(v['raw']).convert('RGB');raw.thumbnail((120,120));raw=raw.resize((max(1,raw.width*min(3,120//max(raw.width,raw.height))),max(1,raw.height*min(3,120//max(raw.width,raw.height)))))
                tile.paste(raw,(x+5,60))
                for j,b in enumerate(v['masks']):
                    im=Image.fromarray(255-b*255).convert('RGB');im.thumbnail((90,120));im=im.resize((max(1,im.width*min(3,120//max(im.width,im.height))),max(1,im.height*min(3,120//max(im.width,im.height)))))
                    tile.paste(im,(x+135+j*100,60))
                    t=v['thresholds'][j];dr.text((x+135+j*100,185),f'{t["level"]} c{t["components"]} h{t["holes"]}',fill='black')
                dr.text((x+5,210),v['faintness'],fill='black')
            panels.append(tile)
        for off in range(0,len(panels),4):
            out=Image.new('RGB',(1400,230*len(panels[off:off+4])),'white')
            for j,im in enumerate(panels[off:off+4]):out.paste(im,(0,230*j))
            out.save(dest/f'{p}.glyphs-{off//4:02d}.jpg',quality=95)
        for feature in ('faintness','inkiness'):
            s=min(1.,1500/max(gray.shape));im=Image.fromarray(gray).convert('RGB').resize((round(gray.shape[1]*s),round(gray.shape[0]*s)));dr=ImageDraw.Draw(im)
            for r in records:
                v=r['slow'];b=[x*s for x in r['bbox']]
                color=('orange' if v['core_snr']<4 else 'teal') if feature=='faintness' else ('magenta' if len({(t['components'],t['holes']) for t in v['thresholds']})>1 else 'royalblue')
                dr.rectangle(b,outline=color,width=2)
            im.save(dest/f'{p}.{feature}.jpg',quality=93)
        dump(dest/(p+'.json'),dict(page=p,records=records,extracted=len(atlas),sampled=len(glyphs),selected=selected,extraction_s=extraction_s,timings=timings,shape_s=shape['seconds']))
        summary.append(dict(page=p,extracted=len(atlas),sampled=len(glyphs),extraction_s=extraction_s,timings=timings));print(p,len(glyphs),timings,flush=True)
    dump(dest/'summary.json',summary)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='observability-v1');run(ap.parse_args().version)
