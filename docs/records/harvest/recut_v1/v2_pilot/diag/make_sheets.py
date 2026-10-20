"""Contact sheets plus native, unaltered raster witnesses for every unmatched line."""
from __future__ import annotations
import os
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import gzip
import html

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from run_diag import install_guard, PILOT, sha


def main():
    install_guard()
    from PIL import Image,ImageDraw,ImageFont
    import numpy as np
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
    small=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
    palette=['#0072b2','#009e73','#cc79a7','#d55e00','#56b4e9','#f0a000']
    classifications={r['id']:r for r in json.loads((BASE/'classifications.json').read_text())}
    (BASE/'sheets').mkdir(exist_ok=True)
    (BASE/'witnesses').mkdir(exist_ok=True)
    links=[];manifest=[]
    for page in json.loads((BASE/'pages.json').read_text()):
        name=page['wave']+'--'+page['page_id']
        records=json.loads((BASE/(name+'.matches.json')).read_text())
        value=json.loads(gzip.decompress(Path(page['curves_origin']).read_bytes()))
        curves=value if isinstance(value,list) else value['curves']
        with Image.open(page['raster']) as im:
            native=im.convert('RGB')
        overview=native.copy();overview.thumbnail((1600,2400))
        overview.save(BASE/'sheets'/(name+'--page.jpg'),quality=95)
        links.append((f"{name}: unmarked complete page",'sheets/'+name+'--page.jpg'))
        failures=[r for r in records if r['before']!='matched' or r['after']!='matched']
        for start in range(0,len(failures),4):
            sheet=Image.new('RGB',(1800,min(4,len(failures)-start)*620+65),'#f2f2f2');d=ImageDraw.Draw(sheet)
            d.text((14,10),f"{name} failures {start+1}-{min(start+4,len(failures))} / {len(failures)} | original 50% -> opt-in 50%",font=font,fill='black')
            d.text((14,35),'RED = crop_bbox; colours = eligible curves; grey = nearby rejected; PURPLE = highlighted rejected evidence; mean/base + thick centre',font=small,fill='black')
            for slot,r in enumerate(failures[start:start+4]):
                y=65+slot*620;x0,y0,x1,y1=r['crop_bbox'];eligible=[c['index'] for c in r['before_candidates']]
                d.text((12,y+5),f"{r['id']} | {r['before']} -> {r['after']} | crop_bbox={r['crop_bbox']}",font=font,fill='black')
                labels=[f"c{c['index']} x=[{curves[c['index']]['x0']},{curves[c['index']]['x1']}) d={c['distance_xh']:.4f}xh o={c['overlap']:.3f}" for c in r['before_candidates']]
                d.text((12,y+31),'Eligible: '+('; '.join(labels) if labels else 'NONE'),font=small,fill='black')
                # Full page width guarantees that no curve extent is clipped by
                # a column-local diagnostic viewport.
                a=max(0,y0-200);b=min(native.height,y1+200)
                raw=native.crop((0,a,native.width,b));overlay=raw.copy();od=ImageDraw.Draw(overlay)
                nearby={c['index'] for c in r['nearby']}
                indices=sorted(nearby|set(eligible))
                for idx in indices:
                    c=curves[idx];cx0,cx1=c['x0'],c['x1'];step=max(1,(cx1-cx0)//1500)
                    xx=np.arange(cx0,cx1,step);base=np.asarray(c['baseline'])[::step];mean=np.asarray(c['meanline'])[::step]
                    colour=palette[eligible.index(idx)%len(palette)] if idx in eligible else '#8a8a8a'
                    if idx in classifications.get(r['id'],{}).get('highlight_curves',[]):
                        colour='#b000c0'
                    for yy,width in ((mean,2),(base,2),((mean+base)/2,5 if idx in eligible else 2)):
                        od.line(list(zip(xx.tolist(),(yy-a).tolist())),fill=colour,width=width)
                    centre=(base+mean)/2
                    for ex,ey in ((cx0,centre[0]),(cx1-1,centre[-1])):
                        od.line((ex,ey-a-13,ex,ey-a+13),fill=colour,width=4)
                    od.text((cx0+2,max(0,min(b-a-20,float(centre[0])-a-23))),f'c{idx}',font=small,fill=colour,stroke_width=1,stroke_fill='white')
                od.rectangle((x0,y0-a,x1-1,y1-1-a),outline='#e00000',width=5)
                # Two identical coordinate windows: raw, then annotated. These
                # display at reduced scale; native witnesses below are lossless.
                scale=min(1760/native.width,180/(b-a))
                size=(round(native.width*scale),round((b-a)*scale))
                sheet.paste(raw.resize(size,Image.Resampling.LANCZOS),(20,y+72))
                sheet.paste(overlay.resize(size,Image.Resampling.LANCZOS),(20,y+278))
                d.text((20,y+53),f'Unaltered full-width raster strip: x=[0,{native.width}), y=[{a},{b})',font=small,fill='black')
                d.text((20,y+259),'Same strip with crop and full horizontal curve extents:',font=small,fill='black')
                # Show the exact target crop at a more legible scale too.
                target=native.crop(tuple(r['crop_bbox']));ts=min(1,1700/target.width,95/target.height)
                target=target.resize((round(target.width*ts),round(target.height*ts)),Image.Resampling.LANCZOS)
                sheet.paste(target,(20,y+487));d.text((20,y+466),'Exact crop_bbox raster (unaltered):',font=small,fill='black')
                if not eligible:
                    review=classifications[r['id']]
                    d.text((20,y+591),review['cause'].upper()+': '+review['sheet_note'],font=small,fill='#9b0000')
                if r['before']=='unmatched' or r['after']=='unmatched':
                    # Focus on the entire target column at native raster size.
                    # Endpoints beyond this focus are still in the full-width sheet.
                    left=0 if (x0+x1)/2<native.width/2 else max(0,x0-180)
                    right=min(native.width,max(x1+180,int(native.width*.46))) if left==0 else min(native.width,max(x1+180,int(native.width*.87)))
                    focus=native.crop((left,a,right,b));fo=overlay.crop((left,0,right,b-a))
                    review=classifications[r['id']]
                    witness=Image.new('RGB',(max(focus.width,2200),2*focus.height+150),'#f2f2f2');wd=ImageDraw.Draw(witness)
                    wd.text((10,5),r['id']+' | UNMATCHED | crop_bbox='+str(r['crop_bbox']),font=font,fill='black')
                    wd.text((10,30),f'Native raster pixels; context x=[{left},{right}), y=[{a},{b}). TOP raw; BOTTOM crop red + rejected curves (purple = evidence).',font=small,fill='black')
                    wd.text((10,52),review['cause'].upper()+': '+review['sheet_note'],font=small,fill='#9b0000')
                    witness.paste(focus,(0,90));witness.paste(fo,(0,focus.height+120))
                    path='witnesses/'+r['id']+'.png';witness.save(BASE/path)
                    rawpath='witnesses/'+r['id']+'--crop.png';native.crop(tuple(r['crop_bbox'])).save(BASE/rawpath)
                    links.append((r['id']+' native raw + rejected detector curves',path))
                    manifest.append(dict(id=r['id'],kind='unmatched_native',path=path,sha256=sha(BASE/path),source_window=[left,a,right,b]))
            path='sheets/'+name+f'--failures-{start//4+1:02d}.jpg';sheet.save(BASE/path,quality=96,subsampling=0)
            links.append((f'{name}: failures {start+1}-{min(start+4,len(failures))}',path))
            manifest.append(dict(kind='contact_sheet',path=path,sha256=sha(BASE/path),ids=[r['id'] for r in failures[start:start+4]]))
        print(name,'sheets',len(failures),'failures',flush=True)
    (BASE/'sheets_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    content='<!doctype html><html lang="en"><meta charset="utf-8"><title>T6c1b evidence index</title><style>body{font:18px system-ui;max-width:1100px;margin:40px auto}li{margin:12px 0}a{color:#056}</style><h1>T6c1b raster evidence</h1><p>Every original failure is retained, including all eligible curve extents. Native unmatched witnesses preserve the source raster pixels. See <a href="DIAG.md">DIAG.md</a> for findings.</p><ul>'
    content+=''.join('<li><a href="'+html.escape(p)+'">'+html.escape(label)+'</a></li>' for label,p in links)
    content+='</ul></html>'
    (BASE/'index.html').write_text(content)


if __name__=='__main__':
    main()
