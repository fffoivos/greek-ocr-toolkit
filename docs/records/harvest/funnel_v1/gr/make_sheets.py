from funnellib import *
from collections import defaultdict
from PIL import ImageDraw
import sys

def make(source=None,suffix='',bound_only=False):
    groups=defaultdict(dict)
    for r in rows(BASE/'probe_pages.jsonl'):
        if source and source!=r['source']:continue
        if bound_only and not r.get('link_table_bound'):continue
        item=r.get('book_key',r['item']) if r['source']=='anemi' else r['item']
        groups[r['source']].setdefault(item,[]).append(r)
    for src,items in groups.items():
        sample=[]
        for item,pages in list(items.items())[:24]:
            pages.sort(key=lambda r:r.get('source_page',r['page']))
            r=pages[len(pages)//2];sample.append((item,r))
        for part in range((len(sample)+19)//20):
            batch=sample[part*20:(part+1)*20];canvas=Image.new('L',(2000,700*((len(batch)+3)//4)),255);draw=ImageDraw.Draw(canvas)
            for j,(item,r) in enumerate(batch):
                im=Image.open(BASE/r['image']);im.thumbnail((480,660));x=j%4*500;y=j//4*700
                canvas.paste(im,(x+(500-im.width)//2,y+30));n=r.get('source_page',r['page'])
                draw.text((x+8,y+8),f'{j+1+part*20}: {item[:31]} p{n}',fill=0)
            name=f'{src}{suffix}-{part+1}';dest=BASE/'bulk/review'/(name+'.jpg');dest.parent.mkdir(exist_ok=True);canvas.save(dest,quality=90)
            write(BASE/'receipts/review'/(name+'.json'),dict(source=src,sheet=str(dest.relative_to(BASE)),sheet_sha256=sha(dest.read_bytes()),entries=[dict(position=j+1+part*20,item=item,page=r.get('source_page',r['page']),image=r['image'],image_sha256=r['image_sha256']) for j,(item,r) in enumerate(batch)]))

if __name__=='__main__':make(sys.argv[1] if len(sys.argv)>1 else None,sys.argv[2] if len(sys.argv)>2 else '',len(sys.argv)>3 and sys.argv[3]=='bound')
