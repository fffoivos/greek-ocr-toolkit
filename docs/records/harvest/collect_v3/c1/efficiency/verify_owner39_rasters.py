#!/usr/bin/env python3
"""Pixel comparison against read-only R2 rendering blocks and private QA panels.

Requires Pillow. Run with the local x86_64 Python when its Pillow is x86_64.
No source module is imported; only the five rendering statements are compiled.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode=True
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[5]/'greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_prepare.py'


def verify():
    tree=ast.parse(SOURCE.read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render_deck')
    loop=next(n for n in fn.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='w')
    selected=[];start=False
    for n in loop.body:
        if isinstance(n,ast.With):start=True
        if not start:continue
        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='linefile':break
        selected.append(n)
    assert len(selected)==5  # with-open; crop; scale; integer scale; zoom
    code=compile(ast.Module(body=selected,type_ignores=[]),str(SOURCE),'exec')
    mapping=json.loads((ROOT/'keys/owner39/input_mapping.json').read_text())
    truth=json.loads((ROOT/'keys/owner39/truth.json').read_text())
    control=ROOT/'packs/owner39/E0a/r1/img';e2=ROOT/'packs/owner39/E2/r1/img'
    checks=[]
    for cid,m in mapping.items():
        scope={'Image':Image,'math':math,'w':{'crop':m['crop'],'word_box':m['word_box']}}
        exec(code,scope)
        with Image.open(m['crop']) as src:line=src.convert('RGB')
        # Independent transcription of the owner-page geometry, including //2.
        w,h=line.size;wx0=max(0,m['word_bbox'][0]-6);wx1=min(w,m['word_bbox'][2]+6)
        word=line.crop((wx0,0,wx1,h)).resize(((wx1-wx0)*3,h*3),Image.Resampling.LANCZOS)
        x0,_,x1,_=m['letter_bbox'];pad=max(6,(x1-x0)//2)
        vx0=max(0,x0-pad);vx1=min(w,x1+pad)
        letter=line.crop((vx0,0,vx1,h)).resize(((vx1-vx0)*8,h*8),Image.Resampling.NEAREST)
        for kind,folder,expected in [('word',control,scope['zoom']),('line',control,scope['line']),('e2word',e2,word),('letter',e2,letter)]:
            path=folder/m['images'][kind]
            with Image.open(path) as actual:
                assert actual.mode=='RGB' and actual.size==expected.size
                assert not actual.info, (path,actual.info.keys())
                assert ImageChops.difference(actual,expected).getbbox() is None, (cid,kind)
            checks.append(dict(card_id=cid,kind=kind,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pixels='identical'))
    qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    chosen=[next(i for i,t in truth.items() if t['owner_status']=='noted'),
            next(i for i,t in truth.items() if t['db_id']=='177b717d-p000030-l0004:s14'),
            next(i for i,t in truth.items() if t['db_id']=='384c3f89-p000096-l0004:s15')]
    panels=[]
    for cid in chosen:
        m=mapping[cid];images=[]
        for folder,kind in [(control,'word'),(e2,'letter'),(control,'line')]:
            with Image.open(folder/m['images'][kind]) as im:images.append(im.copy())
        panel=Image.new('RGB',(max(i.width for i in images)+20,sum(i.height for i in images)+90),'white')
        draw=ImageDraw.Draw(panel);draw.text((10,8),truth[cid]['db_id']+' | word, letter, native line (private construction QA)',fill='black')
        y=35
        for im in images:panel.paste(im,(10,y));y+=im.height+15
        path=qa/('owner39_'+cid+'.png');panel.save(path)
        panels.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),card_id=cid))
    receipt=dict(cards=39,comparisons=len(checks),pixel_identity='all identical',metadata='none',
                 reference='R2 render_deck AST: only open/convert/crop/scale/resize statements; source read-only',
                 e2_reference='independent exact build_r1a_errors.py geometry/filter formulas',checks=checks,qa=panels)
    (ROOT/'keys/owner39/raster_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='checks'},indent=2))


if __name__=='__main__':verify()
