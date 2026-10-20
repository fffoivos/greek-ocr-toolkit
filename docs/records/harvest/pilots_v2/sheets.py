"""Deterministic 20-page source contact sheets with machine-readable custody."""
import json,sys
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont,ImageOps
from pilotlib import *

def make(pilot,pages):
    dest=BASE/'contact_sheets';dest.mkdir(parents=True,exist_ok=True)
    groups=defaultdict(list)
    for p in pages:groups[str(p.get('issue')) if pilot=='kosmopolis' else p['item']].append(p)
    allocations={k:min(len(v),20//len(groups)) for k,v in groups.items()}
    while sum(allocations.values())<min(20,len(pages)):
        for k in sorted(groups):
            if sum(allocations.values())>=min(20,len(pages)):break
            if allocations[k]<len(groups[k]):allocations[k]+=1
    selected=[]
    for key,ps in sorted(groups.items()):
        n=allocations[key];chosen=[]
        if pilot!='kosmopolis':
            contents=[p for p in ps if p.get('role')=='contents']
            front=[p for p in ps if p.get('role')=='front'];front=sorted(front,key=lambda p:(p['page']<6,p['page']))
            back=[p for p in ps if p.get('role')=='back']
            chosen=contents[:1]+front[:min(2,max(0,n-2))]+back[:1]
        remaining=[p for p in ps if p['id'] not in {r['id'] for r in chosen}]
        chosen += [remaining[i-1] for i in positions(len(remaining),n-len(chosen))]
        selected.extend(chosen[:n])
    cell_w,cell_h=440,650;out=Image.new('RGB',(cell_w*5,cell_h*4+70),'#eef1f4');draw=ImageDraw.Draw(out)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    draw.text((18,15),f'P1 / {pilot} / 20-page contact sheet / native page files linked in map',fill='#172536',font=font)
    mapping=[]
    for i,r in enumerate(selected):
        with Image.open(BASE/r['image']) as im:im=im.convert('RGB');im.thumbnail((cell_w-14,cell_h-54),Image.Resampling.LANCZOS)
        x=(i%5)*cell_w;y=(i//5)*cell_h+70
        draw.rectangle((x+3,y+3,x+cell_w-3,y+cell_h-3),fill='white')
        out.paste(im,(x+(cell_w-im.width)//2,y+42))
        draw.text((x+9,y+8),f'{i+1:02d}  {r["item"][:30]} / {r["page"]}',fill='#172536',font=font)
        mapping.append(dict(card=i+1,page_id=r['id'],image=r['image'],sha256=r['image_sha256'],page=r['page'],item=r['item']))
    path=dest/(pilot+'-20-pages.jpg');out.save(path,quality=91)
    write(BASE/'receipts/sheets'/(pilot+'.json'),dict(pilot=pilot,path=str(path.relative_to(BASE)),sha256=sha(path),pages=len(mapping),mapping=mapping))
    return path

if __name__=='__main__':
    groups=defaultdict(list)
    for p in sorted((BASE/'receipts/pages').glob('*.json')):
        r=json.loads(p.read_text())
        if not r.get('excluded'):groups[r['pilot']].append(r)
    for group,pages in groups.items():print(make(group,pages),flush=True)
