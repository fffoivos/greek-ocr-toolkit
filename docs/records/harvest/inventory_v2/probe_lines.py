"""Count bounded probe pages with the unchanged greekocr.pages line detector."""
import datetime, hashlib, json, pathlib, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from PIL import Image, ImageOps, ImageDraw
from greekocr.pages.lines import page_line_segments
BASE=pathlib.Path(__file__).resolve().parent
for p in sorted((BASE/'receipts').glob('*/probe-*.json')):
    r=json.loads(p.read_text())
    if not r.get('image_path') or 'label' not in r:continue
    target=p.with_name(p.stem+'-lines.json')
    if target.exists():continue
    im=Image.open(BASE/r['image_path']).convert('RGB');start=time.monotonic()
    lines=page_line_segments(im)
    rows=[]
    for k,line in enumerate(lines):
        rows.append(dict(index=k,bbox=[int(line.x0),max(0,int(line.top.min())),int(line.x1),min(im.height,int(line.bottom.max())+1)],discounted=line.discounted))
    out=dict(source=r['source'],image_path=r['image_path'],image_sha256=hashlib.sha256((BASE/r['image_path']).read_bytes()).hexdigest(),width=im.width,height=im.height,detector='greekocr.pages.lines.page_line_segments',detector_sha256=hashlib.sha256((ROOT/'greekocr/pages/lines.py').read_bytes()).hexdigest(),raw_segments=len(rows),non_discounted_lines=sum(x['discounted'] is None for x in rows),lines=rows,seconds=round(time.monotonic()-start,3),target_class_lines=None,target_class_note='Visual classification required; detector counts do not determine script, admission, codec or usable yield.')
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    # Thumbnail is for navigation; native image remains the classification witness.
    thumb=ImageOps.contain(im,(600,1000));thumb.save(p.with_name(p.stem+'-preview.jpg'))
    print(r['source'],r['label'],out['non_discounted_lines'],flush=True)
