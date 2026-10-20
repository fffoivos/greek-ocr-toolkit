from __future__ import annotations
import json, math, sys
from bs4 import BeautifulSoup
from contextlib import closing
import pypdfium2 as pdfium
from pilotlib import *

def render(pdf,pilot,item,ns,**extra):
    with pdfium.PdfDocument(pdf) as d:
        for n in ns:
            ident=f'{pilot}--{item}--{n:06d}';receipt=BASE/'receipts/pages'/(ident+'.json')
            if receipt.exists():continue
            with closing(d[n-1]) as p:
                w,h=p.get_size();scale=min(200/72,(LONG_SIDE-.001)/max(w,h))
                with closing(p.render(scale=scale,grayscale=True)) as bitmap:im=bitmap.to_pil().copy().convert('L')
                path=BASE/'bulk/pages'/(ident+'.png');path.parent.mkdir(parents=True,exist_ok=True);im.save(path,compress_level=3)
                write(receipt,dict(id=ident,pilot=pilot,item=item,page=n,role='front' if n<=6 else 'back' if n>len(d)-6 else 'body',image=str(path.relative_to(BASE)),image_sha256=sha(path),width=im.width,height=im.height,long_side_cap=LONG_SIDE,pdf=str(pdf),pdf_sha256=sha(pdf),pdf_points=[w,h],effective_dpi=scale*72,**extra))
            print(pilot,item,n,'rendered',flush=True)

def elstat():
    c=client('elstat')
    urls=['https://dlib.statistics.gr/Book/GRESYE_01_0002_00001.pdf','http://dlib.statistics.gr/Book/GRESYE_01_0002_00001.pdf',
          'https://web.archive.org/web/20160303225708id_/http://dlib.statistics.gr/Book/GRESYE_01_0002_00001.pdf']
    for url in urls:
        try:
            p=fetch(c,url,BASE/'bulk/pdf/elstat1930.pdf',200_000_000)
            with pdfium.PdfDocument(p) as d:total=len(d)
            write(BASE/'receipts/items/elstat1930.json',dict(pilot='elstat',item='elstat1930',title='Στατιστική Επετηρίς της Ελλάδος 1930',source_url=url,pages=total,rights=dict(scan='ELSTAT scan declaration unresolved',text='General Statistical Service of Greece',cloud_ocr='owner P1 authorisation',retention='pilot evidence',training='not released',redistribution='unresolved')))
            render(p,'elstat','elstat1930',positions(total,50),url=url);return
        except Exception as e:print('elstat',type(e).__name__,str(e)[:180],flush=True)

def kosmopolis():
    c=client('kosmopolis');seen={};retained=0
    for issue in [4162,4161,4160]:
        try:p=fetch(c,f'https://kosmopolis.library.upatras.gr/index.php/xrysallis/issue/view/{issue}',BASE/'bulk/metadata'/f'kosmo-issue-{issue}.html')
        except Exception as e:print('kosmo issue',issue,type(e).__name__,flush=True);continue
        soup=BeautifulSoup(p.read_text(),'html.parser');links=[]
        for a in soup.select('a[href]'):
            url=a['href']
            if '/article/view/' in url and len(url.rstrip('/').split('/'))==9:links.append(url)
        # Article galley links carry both an article and a galley number.
        import re
        links=sorted(set(a['href'] for a in soup.select('a[href]') if re.search(r'/article/view/\d+/\d+$',a['href'])))
        for link in links:
            if retained>=50:break
            item='xrysallis-'+link.split('/')[-2]
            try:
                article=link.rsplit('/',1)[0];meta=fetch(c,article,BASE/'bulk/metadata'/(item+'.html'))
                ms=BeautifulSoup(meta.read_text(),'html.parser');licence=ms.select_one('.item.license')
                url=link.replace('/article/view/','/article/download/')
                pdf=fetch(c,url,BASE/'bulk/pdf'/(item+'.pdf'),50_000_000)
                with pdfium.PdfDocument(pdf) as d:total=len(d)
                write(BASE/'receipts/items'/(item+'.json'),dict(pilot='kosmopolis',item=item,issue=issue,title=ms.title.get_text(),source_url=article,pages=total,rights=dict(scan=licence.get_text(' ',strip=True) if licence else 'item licence unresolved',text='per author/edition in metadata',cloud_ocr='owner authorised P1',retention='pilot evidence',training='not released',redistribution='per item declaration')))
                render(pdf,'kosmopolis',item,range(1,total+1),url=url,issue=issue)
                for n in range(1,total+1):
                    f=BASE/'receipts/pages'/f'kosmopolis--{item}--{n:06d}.json';r=json.loads(f.read_text())
                    # Exact raster dedupe only. Visually different rescans are flagged later.
                    h=r['image_sha256']
                    if h in seen:r.update(excluded='duplicate_page_pixels',duplicate_of=seen[h])
                    elif retained>=50:r.update(excluded='beyond_50_page_sample')
                    else:seen[h]=r['id'];retained+=1
                    write(f,r)
                print('kosmopolis retained',retained,flush=True)
            except Exception as e:print('kosmopolis',item,type(e).__name__,str(e)[:180],flush=True)
        if retained>=50:break

if __name__=='__main__':globals()[sys.argv[1]]()
