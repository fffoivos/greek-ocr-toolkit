from __future__ import annotations
import argparse, json, re, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
from pilotlib import *

IA=[('ia1850','b33028709',34),('ia1850','neoellnikaanale00unkngoog',33),
    ('ia1850','8ZSUP92_18',33),('ia1900','greekboyathomest01rousuoft',30),('ia1900','historiatsnsouke00psyl',30)]

def ia(pilot,item,count):
    c=client('ia');meta=fetch(c,'https://archive.org/metadata/'+item,BASE/'bulk/metadata'/(item+'.json'))
    d=json.loads(meta.read_text());m=d['metadata'];total=int(m['imagecount'])
    write(BASE/'receipts/items'/(item+'.json'),dict(pilot=pilot,item=item,metadata=m,metadata_sha256=sha(meta),total_pages=total,pages_requested=count,
          rights=dict(scan=m.get('rights',m.get('licenseurl',m.get('possible-copyright-status','unresolved'))),text='item author and edition recorded; jurisdiction assessment unresolved',cloud_ocr='owner authorised P1 2026-10-16',retention='local pilot evidence',training='pilot only; no release',redistribution='no permission inferred'),source_url='https://archive.org/details/'+item))
    for n in positions(total,count):
        try:
            raster(pilot,item,n,'https://archive.org/download/'+item+'/page/n'+str(n-1)+'.jpg',c,
                   'front' if n<=5 else 'back' if n>total-5 else 'body')
            print(pilot,item,n,'ok',flush=True)
        except Exception as e:print(pilot,item,n,type(e).__name__,str(e)[:130],flush=True)

def bsb():
    c=client('bsb');item='bsb11189761'
    p=fetch(c,'https://api.digitale-sammlungen.de/iiif/presentation/v2/'+item+'/manifest',BASE/'bulk/metadata/bsb-manifest.json')
    d=json.loads(p.read_text());canvases=d['sequences'][0]['canvases'];ns=positions(len(canvases),50)
    if 10 not in ns:ns[5]=10
    write(BASE/'receipts/items'/f'{item}.json',dict(pilot='bsb',item=item,metadata=d.get('metadata'),source_url=d.get('@id'),manifest_sha256=sha(p),total_pages=len(canvases),pages_requested=50,rights=dict(scan=d.get('license',d.get('rights','see S1 NoC-NC')),text='Philologus 33 (1874), authors per article unresolved',cloud_ocr='owner authorised P1',retention='pilot evidence',training='not released',redistribution='item NoC-NC recorded')))
    for n in sorted(ns):
        url=canvases[n-1]['images'][0]['resource']['@id']
        try:raster('bsb',item,n,url,c,'contents' if n==10 else 'front' if n<=5 else 'back' if n>len(canvases)-5 else 'body');print('bsb',n,'ok',flush=True)
        except Exception as e:print('bsb',n,type(e).__name__,str(e)[:130],flush=True)

def ajax():
    revision=json.loads((S1/'receipts/ajax-commentaries/tree.txt').read_text())['sha'];c=client('ajax')
    p=fetch(c,'https://codeload.github.com/AjaxMultiCommentary/GT-commentaries-OCR/zip/'+revision,BASE/'bulk/ajax.zip',200_000_000)
    dest=BASE/'bulk/ajax';dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p) as z:
        for entry in z.infolist():
            if entry.is_dir():continue
            rel=pathlib.PurePosixPath(entry.filename);assert '..' not in rel.parts
            target=dest/pathlib.Path(*rel.parts[1:]);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(entry))
    write(BASE/'receipts/ajax-acquisition.json',dict(repository='AjaxMultiCommentary/GT-commentaries-OCR',revision=revision,archive_sha256=sha(p),files=sum(1 for p in dest.rglob('*') if p.is_file()),gt_lines=len(list(dest.rglob('*.gt.txt'))),rights='CC BY 4.0 dataset; original editions recorded in README',google_reads=0))
    print('ajax done',flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='ia':
        for args in IA:ia(*args)
    elif mode=='bsb':bsb()
    elif mode=='ajax':ajax()
