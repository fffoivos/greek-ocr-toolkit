"""Render cached slow-model evidence without treating it as a reference answer."""
import json
from pathlib import Path
import cv2
import numpy as np
import pyarrow.parquet as pq
from ..round2 import manifest, get_baseline
from ..shared.manifest import ROOT, OUT, digest
from ..shared.review import save_image
from ..shared.timing import dump

DEST = OUT/'features_type'
GUIDES = {'baseline':(20,80,220),'meanline':(210,130,0),
          'font_top':(30,165,30),'font_bottom':(170,60,180),
          'accent_top':(0,140,240),'accent_bottom':(0,195,245)}
COLORS = [(30,140,225),(205,100,20),(40,160,50),(175,65,180),(20,170,170),(160,80,80)]
NAMED = ['an-ffccc97c07de-p000152','an-d83e7a198ade-p000099',
         'an-d3237d690aa0-p000138','s2-77d1bd63d5babbe0df73-p00001',
         'an-e74539ae215c-p000338','an-1f8e7d022643-p000003']

def label(im,text):
    if im.shape[1]<1100:
        canvas=np.full((im.shape[0],1100,3),255,np.uint8);canvas[:,:im.shape[1]]=im;im=canvas
    bar=np.full((35,im.shape[1],3),255,np.uint8)
    cv2.putText(bar,text,(5,24),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1,cv2.LINE_AA)
    return np.vstack([bar,im])

def run(pages=NAMED):
    rows={r['page']:r for r in manifest()['pages']}
    for name in pages:
        row=rows[name]; gray=cv2.imread(str(ROOT/row['path']),0)
        base=ROOT/'.astra/out'; lp=base/(name+'.lines.json'); sp=base/(name+'.stats.json')
        if not sp.exists():
            base=ROOT/'.astra/q3b-equality/measurements/default'; sp=base/(name+'.stats.json')
        stats=json.loads(sp.read_text()); lines=json.loads(lp.read_text())
        if 'source_sha256' in stats: assert stats['source_sha256']==row['sha256']
        if 'lines_file_sha256' in stats: assert stats['lines_file_sha256']==digest(lp)
        glyph_path=base/(name+'.glyphs.parquet')
        glyphs=pq.read_table(glyph_path).to_pylist()
        # Stats may contain residuals: never draw geometry from discounted lines.
        glyphs=[g for g in glyphs if g['line_index'] is not None and
                not lines[g['line_index']].get('discounted')]
        guides=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR); fonts=guides.copy()
        for i,l in enumerate(lines):
            if l.get('discounted'): continue
            xs=np.arange(l['x0'],l['x1']); stride=max(1,len(xs)//250)
            for key,color in GUIDES.items():
                points=np.c_[xs[::stride],np.array(l[key])[::stride]].astype(np.int32)
                cv2.polylines(guides,[points],False,color,1,cv2.LINE_AA)
            cv2.putText(guides,str(i),(l['x0'],int(np.median(l['baseline']))),cv2.FONT_HERSHEY_SIMPLEX,.38,(0,0,0),1)
        groups={g['id']:j for j,g in enumerate(stats['font_groups'])}
        for g in glyphs:
            if g['body_box'] is None: continue
            x0,y0,x1,y1=g['body_box']; col=COLORS[groups[g['font_group']]%len(COLORS)]
            cv2.rectangle(fonts,(x0,y0),(x1,y1),col,1)
            marks=g['attached_marks']; marks=json.loads(marks) if isinstance(marks,str) else marks
            for m in marks:
                a,b,c,d=m['box'];cv2.rectangle(guides,(a,b),(c,d),(0,140,240),1)
        dest=DEST/'model';dest.mkdir(parents=True,exist_ok=True)
        save_image(dest/(name+'.font.jpg'),label(fonts,name+' | slow model body size groups; no font-name claim'))
        save_image(dest/(name+'.guides.jpg'),label(guides,name+' | six model guides; borrowed guides remain hypotheses'))
        # Original-pixel triplets, every active line, split into manageable boards.
        tiles=[]; ledger=[]
        for i,l in enumerate(lines):
            if l.get('discounted'): continue
            x0=max(0,l['x0']);x1=min(gray.shape[1],l['x1'])
            y0=max(0,int(min(l['top'])-l['xheight']*.4));y1=min(gray.shape[0],int(max(l['bottom'])+l['xheight']*.4))
            scale=min(1.,1000/max(1,x1-x0));gh=[]
            for im in [cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR),fonts,guides]:
                crop=im[y0:y1,x0:x1];gh.append(cv2.resize(crop,None,fx=scale,fy=scale))
            tile=label(np.vstack(gh),f'{name} line {i} xh={l["xheight"]:.1f} borrowed={",".join(l["borrowed"])}')
            pad=np.full((tile.shape[0]+6,1100,3),255,np.uint8);pad[:tile.shape[0],:tile.shape[1]]=tile;tiles.append(pad)
            ledger.append(dict(line=i,xheight=l['xheight'],borrowed=l['borrowed'],ink_classes=l['ink_classes']))
        for start in range(0,len(tiles),6): save_image(dest/(name+f'.detail-{start//6:02d}.jpg'),np.vstack(tiles[start:start+6]))
        old=OUT/'font_guides'/(name+'.evidence.json')
        old=json.loads(old.read_text())
        items=get_baseline(row); a07=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        for l in old['lines']:
            pts=np.rint(items[l['line']]['polygon']).astype(np.int32);col=COLORS[l['family']%len(COLORS)]
            cv2.polylines(a07,[pts],True,col,2)
            cv2.putText(a07,f"{l['line']}:F{l['family']}",tuple(pts[0]),cv2.FONT_HERSHEY_SIMPLEX,.45,col,1)
        save_image(dest/(name+'.a07.jpg'),label(a07,name+' | A07 families; same colour repeats every six IDs'))
        dump(dest/(name+'.json'),dict(page=name,source_sha256=row['sha256'],lines_path=str(lp.relative_to(ROOT)),
             statistics_path=str(sp.relative_to(ROOT)),statistics_sha256=digest(sp),glyph_sha256=digest(glyph_path),
             active=ledger,model_groups=stats['font_groups'],a07_families=len(old['families']),
             caveat='slow model hypotheses; residual and discounted lines never rendered'))
        print(name,len(ledger),len(glyphs),flush=True)

if __name__=='__main__': run()
