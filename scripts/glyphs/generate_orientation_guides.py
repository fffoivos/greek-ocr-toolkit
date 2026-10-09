"""Generate development-only quarter turns and labelled two-orientation pastes.

No fitting or decision thresholds are learned here. Existing research images
are never rewritten. PNG rotations are exact; composite resizes are recorded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
PAGES=ROOT/'.astra/pages'
OUT=ROOT/'.astra/out/orientation_eval'
REAL='s2-6419488b7f8e69fd20da-p00001'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(out=OUT):
    out.mkdir(parents=True,exist_ok=True); images=out/'images';images.mkdir(exist_ok=True)
    cases=[]
    def save(im, row):
        path=images/(row['id']+'.png');im.save(path)
        row.update(path=str(path.relative_to(ROOT)),sha256=sha(path),size=list(im.size))
        cases.append(row)
    sources=sorted(PAGES.glob('*.png'))
    if len(sources)!=54:raise ValueError(f'expected 54 development pages, got {len(sources)}')
    for path in sources:
        im=Image.open(path).convert('L')
        for a in (0,90,180,270):
            save(im.rotate(-a,expand=True),dict(id=path.stem+f'__cw{a}',kind='whole',source=path.stem,
                 source_sha256=sha(path),applied_cw=a,truth_cw=(a+(270 if path.stem==REAL else 0))%360,
                 mixed=path.stem==REAL))
        print('GENERATED',path.stem,flush=True)
    # Different-page donor crops: fixed existing pixel annotations, never
    # chosen by whether an orientation implementation succeeds on them.
    donors=[('prose','an-d6fd2cf2f618-p000047',[75,330,1100,710]),
            ('prose','s2-3229200bf47ca465a42d-p00004',[100,540,1320,990]),
            ('label','an-d6fd2cf2f618-p000047',[130,328,550,390]),
            ('label','s2-3229200bf47ca465a42d-p00004',[105,546,600,642])]
    for p in sorted((ROOT/'docs/tables/annotations').glob('*.json')):
        annotation=json.loads(p.read_text())
        if annotation['key']==REAL:continue  # already contains several readings
        if annotation.get('tables'):
            donors.append(('table',annotation['key'],annotation['tables'][0]['extent']))
    basepath=PAGES/'an-d83e7a198ade-p000099.png';base=Image.open(basepath).convert('L');base.thumbnail((1400,1400))
    blocks=[]
    for kind,source,box in donors:
        original=Image.open(PAGES/(source+'.png')).convert('L').crop(box)
        block=original.copy();block.thumbnail((600,600))
        blocks.append((kind,source,box,block,list(original.size)))
    # Controlled digits include punctuation and 6/9. The truth does not depend
    # on trusting another OCR system to identify a figures-only crop.
    for header in (False,True):
        block=Image.new('L',(560,290),255);draw=ImageDraw.Draw(block)
        font=ImageFont.truetype(str(ROOT/'tests/fixtures/fonts/GFSDidot-Regular.ttf'),32)
        if header:draw.text((15,5),'ἀριθμοὶ καὶ ποσὰ ἐτῶν',font=font,fill=0)
        for y in (80,140,200):draw.text((15,y),'369.69   129,60   800.09',font=font,fill=0)
        blocks.append(('numbers-header' if header else 'numbers','rendered-GFSDidot',None,block,list(block.size)))
    for i,(kind,source,box,block,original_size) in enumerate(blocks):
        for angle in (90,270,180):
            turned=block.rotate(-angle,expand=True)
            # A pasted block in an added paper margin leaves the donor and main
            # ink independently scoreable. No ground-truth box enters detection.
            gap=80; x=base.width+gap; y=100
            composite=Image.new('L',(x+turned.width+gap,max(base.height,y+turned.height+gap)),255)
            composite.paste(base,(0,0));composite.paste(turned,(x,y))
            save(composite,dict(id=f'paste_{i:02d}_{kind}_cw{angle}',kind='composite',source=basepath.stem,
                 donor=source,donor_box=box,donor_original_size=original_size,donor_resized_size=list(block.size),
                 truth_cw=0,applied_cw=0,mixed=True,roi=[x,y,x+turned.width,y+turned.height],
                 roi_truth_cw=angle,roi_unit=kind,numbers_only=kind=='numbers'))
    manifest=dict(schema_version=1,angle_convention='observed clockwise; Pillow +angle normalizes',
                  source_scope='54 development pages only; no held-out pages',
                  whole_rotations='exact full-resolution quarter turns',cases=cases)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=OUT)
    args=ap.parse_args();result=generate(args.out);print('CASES',len(result['cases']))
