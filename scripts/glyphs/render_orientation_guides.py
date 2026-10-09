"""Draw the two newly fitted guide hypotheses, with measured/borrowed labels."""
from pathlib import Path
import sys
import json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from greekocr.glyphs.orientation import _pixels
from greekocr.glyphs.orientation_guides import _windows,_line_fit
from greekocr.glyphs.page_font import GUIDES

OUT=ROOT/'.astra/out/orientation_eval'
COLORS=dict(baseline='red',meanline='blue',font_top='green',font_bottom='purple',accent_bottom='orange',accent_top='cyan')


def render(source,name,axis=0):
    im=Image.open(source).convert('L');small,mask,_,height=_pixels(im)
    gray=np.rot90(np.asarray(small),axis//90).copy();mask=np.rot90(mask,axis//90).copy()
    windows=_windows(gray,mask,height)
    if not windows:return
    x,t,r,b,centre=windows[0];crop=gray[t:b,x:r];panels=[];rows=[]
    for half in (False,True):
        g=np.rot90(crop,2).copy() if half else crop
        cy=len(g)-1-centre if half else centre
        line=_line_fit(g,cy,height);panel=Image.fromarray(g).convert('RGB');d=ImageDraw.Draw(panel)
        for k in GUIDES:
            pts=list(zip(range(line.x1),getattr(line,k)))
            if k in line.borrowed:
                for j in range(0,len(pts)-1,8):d.line(pts[j:j+4],fill=COLORS[k],width=1)
            else:d.line(pts,fill=COLORS[k],width=1)
        panel=panel.resize((panel.width*2,panel.height*2))
        rows.append(dict(orientation_cw=(axis+180*half)%360,borrowed=list(line.borrowed),classes=line.ink_classes,contacts=line.guide_residuals))
        panels.append(panel)
    canvas=Image.new('RGB',(max(p.width for p in panels),sum(p.height for p in panels)+180),'white');d=ImageDraw.Draw(canvas)
    y=0
    for panel,row in zip(panels,rows):
        d.text((5,y+3),f"NEW fit: CW {row['orientation_cw']} reading; dashed = borrowed",fill='black')
        d.text((5,y+20),'Red baseline; blue mean; green capital; purple descender; orange/cyan accents',fill='black')
        canvas.paste(panel,(0,y+40));y+=panel.height+80
    canvas.save(OUT/(name+'.png'))
    (OUT/(name+'.json')).write_text(json.dumps(dict(source=str(source),window=[x,t,r,b],readings=rows),indent=2)+'\n')


def render_errors():
    summary=json.loads((OUT/'summary.json').read_text())
    cases={c['id']:c for c in json.loads((OUT/'manifest.json').read_text())['cases']}
    panels=[]
    for err in summary['region_errors']:
        if '__cw0' not in err['id'] or err['id'] not in cases:continue
        row=json.loads((OUT/'decisions'/f"{err['id']}.json").read_text())
        region=next(r for r in row['regions'] if r['id']==err['region'])
        crop=Image.open(ROOT/cases[err['id']]['path']).convert('RGB').crop(region['box'])
        crop.thumbnail((1000,500));panels.append((err,crop))
    if not panels:return
    canvas=Image.new('RGB',(1050,sum(im.height+55 for _,im in panels)),'white');d=ImageDraw.Draw(canvas);y=0
    for err,im in panels:
        d.text((5,y+3),f"NEW decision: {err['id']} {err['region']} CW{err['decision']}; expected CW{err['truth']}",fill='black')
        canvas.paste(im,(5,y+35));y+=im.height+55
    canvas.save(OUT/'error-regions.jpg')


if __name__=='__main__':
    render(ROOT/'.astra/pages/an-d6fd2cf2f618-p000047.png','guides-prose')
    render(ROOT/'.astra/pages/an-7a2b17a3fb0f-p000200.png','guides-navigation')

    render_errors()
