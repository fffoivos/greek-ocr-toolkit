"""S5: dense raw-ink supports independent of the learned map; old guides are hypotheses."""
import cv2,numpy as np,json
from pathlib import Path
from scipy.ndimage import gaussian_filter1d
from .geometry import sample_strip,robust_fit,roi,height_proxy,continuous_path
from .contracts import bbox,rect
from .image_evidence import ImageEvidence,profile_features,stroke_features
from .review import overlay,save_image,atlas
from .timing import dump
from .manifest import ROOT

def import_ours(path):
    out=[]
    for i,q in enumerate(json.loads(Path(path).read_text())):
        if q.get('discounted'): continue
        x=np.linspace(q['x0'],q['x1'],len(q['top']))
        poly=np.vstack([np.c_[x,q['top']],np.c_[x[::-1],q['bottom'][::-1]]])
        out.append(dict(polygon=poly.tolist(),baseline=np.c_[x,q['baseline']].tolist(),score=None,source_id=i,
                        guides={k:q[k] for k in ('meanline','font_top','font_bottom','accent_top','accent_bottom') if k in q},
                        provenance={k:q.get(k) for k in ('xheight','column','support','geometry_source','borrowed','contrast','ink_classes')}))
    return out

def build(gray,items,row,directory):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True); page=row['page']; size=row['image_size']
    height=height_proxy(items,size); ev=ImageEvidence(gray,height,long_side=1600)
    # Dense independent raw ink, not a rendering of the map-derived heuristic.
    rows=[]; gx,gy=ev.gradients
    for i,item in enumerate(items):
        b=bbox(item); h=max(height*.5,min((b[3]-b[1])*.5,2*height))
        strip,x,y,offset=sample_strip(ev.contrast,item,size,h,nx=81,ny=81,extend=1.)
        smooth=gaussian_filter1d(gaussian_filter1d(strip,2.,axis=0),3.,axis=1)
        # Independent raw-ink objective plus continuity. The failed v1 argmax
        # jumped between rows; a weak centre prior does not establish truth.
        objective=smooth-.06*(offset[:,None]/h)**2
        ids=continuous_path(objective,step=1); signal=smooth[ids,np.arange(len(ids))]
        path=np.c_[x,y+offset[ids]]
        feat=profile_features(ev.crop(ev.contrast,b),ev.crop(gx,b),ev.crop(gy,b),ev.crop(ev.persistence,b))
        normal=strip.mean(1); normal/=max(float(normal.max()),1e-6)
        rows.append(dict(id=i,bbox=b,path=path.tolist(),support=signal.tolist(),height=h,profile=normal.tolist(),features=feat,
                         status='independent raw-ink hypothesis; unadjudicated'))
    ours=import_ours(ROOT/row['ours'])
    save_image(directory/f'{page}_raw.jpg',overlay(gray,title=page+' | raw pixels (faded overview)'))
    save_image(directory/f'{page}_dense.jpg',overlay(gray,paths=[q['path'] for q in rows],title=page+' | R03/R04 independent dense raw-ink ridges'))
    save_image(directory/f'{page}_ours.jpg',overlay(gray,ours,title=page+' | cached ours, all discounted removed; hypothesis only'))
    save_image(directory/f'{page}_photometry.jpg',np.hstack([cv2.cvtColor(ev.gray,cv2.COLOR_GRAY2BGR),cv2.applyColorMap(np.uint8(ev.contrast*255),cv2.COLORMAP_TURBO),cv2.applyColorMap(np.uint8(ev.persistence*85),cv2.COLORMAP_VIRIDIS)]))
    # Exact original-pixel crops, across every line, with independent support next to raw.
    cropdir=directory/page; cropdir.mkdir(exist_ok=True)
    for q in rows:
        x0,y0,x1,y1=roi(np.array(q['bbox'])+[-height,-height,height,height],gray.shape)
        crop=gray[y0:y1,x0:x1]; path=np.asarray(q['path'])-[x0,y0]
        save_image(cropdir/f"line-{q['id']:04d}.jpg",np.hstack([cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR),overlay(crop,paths=[path.tolist()],width=crop.shape[1])[38:]]))
    # Original-size glyph/stroke referee selected by uniform positions (not page names).
    patches=[]
    for idx in np.linspace(0,len(items)-1,min(6,len(items)),dtype=int) if items else []:
        b=bbox(items[idx]); cx=(b[0]+b[2])/2; b[0]=max(b[0],cx-3*height); b[2]=min(b[2],cx+3*height)
        x0,y0,x1,y1=roi(b,gray.shape); crop=gray[y0:y1,x0:x1]
        if not crop.size: continue
        pe=ImageEvidence(crop,height,long_side=max(crop.shape)); st=stroke_features(pe.ink)
        panels=[crop,np.uint8(pe.contrast*255),pe.persistence*85,np.uint8(np.clip(st['distance']/height,0,1)*255),st['skeleton']*255,st['endpoints']*255]
        panels=[cv2.cvtColor(p,cv2.COLOR_GRAY2BGR) for p in panels]
        save_image(cropdir/f'patch-{idx}.jpg',np.hstack(panels)); patches.append(dict(line=int(idx),bbox=[x0,y0,x1,y1],file=f'{page}/patch-{idx}.jpg',holes=st['holes']))
    data=dict(page=page,lines=rows,patches=patches,ours_count=len(ours),reference_scale=[ev.sx,ev.sy],height_proxy=height)
    dump(directory/f'{page}.json',data)
    links=''.join(f'<p><a href="{page}/line-{q["id"]:04d}.jpg">Line {q["id"]}: original pixels + independent support</a></p>' for q in rows)
    patchlinks=''.join(f'<p><a href="{q["file"]}">R10 original / contrast / persistence / width / skeleton / endpoints</a></p>' for q in patches)
    (directory/f'{page}.html').write_text(f'<!doctype html><meta charset="utf-8"><h1>{page}</h1><p>Dense supports are hypotheses, not reference labels. All line crops use original pixels. Discounted old lines never drawn.</p><a href="{page}_dense.jpg"><img width="700" src="{page}_dense.jpg"></a><a href="{page}_photometry.jpg">R05 photometry</a> · <a href="{page}_ours.jpg">Old guides hypothesis</a>{patchlinks}{links}')
    return data
