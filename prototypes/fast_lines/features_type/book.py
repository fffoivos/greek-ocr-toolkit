"""Explicit/fast same-book views on three allowlisted pages, no broader search."""
import json
import cv2,numpy as np
from ..round2 import manifest
from ..shared.manifest import ROOT
from ..shared.type_book import summarize
from ..shared.review import save_image
from ..shared.timing import dump
from .reference import DEST,label
from .study import draw

PAGES=['an-1ba3fdb1436b-p000009','an-1ba3fdb1436b-p000012','an-1ba3fdb1436b-p000015']

def run():
    source=ROOT/json.loads((DEST/'active-type.json').read_text())['directory'];dest=DEST/'book-v1';dest.mkdir(exist_ok=True)
    rows={r['page']:r for r in manifest()['pages']};data={p:json.loads((source/(p+'.json')).read_text()) for p in PAGES}
    result={}
    for route in ['slow','explicit','heuristic']:
        result[route]=summarize([dict(page=p,width=rows[p]['image_size'][0],lines=data[p][route]['lines']) for p in PAGES])
        for rec in result[route]['pages']:
            p=rec['page'];g=cv2.imread(str(ROOT/rows[p]['path']),0);im=draw(g,data[p][route],'font')
            text=f"{p} {route}: body/page {rec['body_page_width']:.5f}; /other pages {rec['relative_to_other_pages']:.3f}; N {rec['support']}"
            save_image(dest/(p+'.'+route+'.jpg'),label(im,text))
    dump(dest/'book.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':run()
