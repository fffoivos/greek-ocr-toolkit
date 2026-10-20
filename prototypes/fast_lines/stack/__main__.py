"""CLI: python -m prototypes.fast_lines.stack IMAGE --output result.json

Use benchmark/review/summary for the fixed supplied cohort. Rendering and JSON
serialization are outside the file-to-lines latency timer.
"""
import argparse
import hashlib
import html
import json
import platform
import shutil
from pathlib import Path
import cv2
import numpy as np
from .pipeline import Stack
from ..round2 import manifest, get_baseline
from ..shared.manifest import ROOT, OUT, MODEL, digest
from ..shared.timing import dump
from ..shared.review import detector_record, save_image

DEST=OUT/'stack'


def signature():
    files=sorted((ROOT/'prototypes/fast_lines').rglob('*.py'))
    hashes={str(p.relative_to(ROOT)):digest(p) for p in files}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),hashes


def label(im,text):
    bar=np.full((34,im.shape[1],3),255,np.uint8)
    cv2.putText(bar,text,(8,23),cv2.FONT_HERSHEY_SIMPLEX,.45,(25,25,25),1,cv2.LINE_AA)
    return np.vstack([bar,im])


def render(gray,result,path):
    scale=min(1.,1500/gray.shape[1]);g=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    final=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR);base=final.copy()
    def poly(im,q,color,width=1):
        if not q.get('discounted'):
            cv2.polylines(im,[np.rint(np.asarray(q['polygon'])*scale).astype(np.int32)],True,color,width,cv2.LINE_AA)
    for q in result['original']:
        poly(base,q,(170,135,65));poly(final,q,(165,165,165))
    for q in result.get('removed',[]):poly(final,q,(25,25,230),2)
    for q in result['items']:
        color=(40,165,35) if q in result.get('added',[]) or q.get('type_slot') is not None else ((185,105,20) if q.get('provenance') else (170,135,65))
        poly(final,q,color,2 if q.get('provenance') else 1)
    fired=', '.join(f'{k}:{v}' for k,v in result.get('counts',{}).items() if v) or ('orientation parked' if result.get('parked') else 'none')
    save_image(path,label(final,path.stem+' | '+fired))
    save_image(path.with_name(path.stem+'.paddle.jpg'),label(base,path.stem+' | Paddle v6 small'))


def benchmark(args):
    directory=DEST/args.version;directory.mkdir(parents=True,exist_ok=True)
    key,hashes=signature();dump(directory/f'source-r{args.repeat}.json',dict(key=key,files=hashes,model=digest(MODEL),platform=platform.platform()))
    rows=manifest()['pages']
    if args.group:rows=[r for r in rows if r['group']==args.group]
    rows=rows[args.offset:args.offset+args.limit]
    if args.repeat%2==0:rows=list(reversed(rows))
    source_dir=directory/'source'
    if not source_dir.exists():
        for name in hashes:
            dst=source_dir/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
    else:
        assert all(digest(source_dir/name)==sha for name,sha in hashes.items()),'Snapshot differs from current sources'
    stack=Stack()
    # Explicit untimed warmup on the first allowed input; no hidden model startup.
    warm=cv2.imread(str(ROOT/rows[0]['path']),0);stack.detector.infer(warm)
    for row in rows:
        page=row['page'];receipt=directory/f'{page}.r{args.repeat}.json'
        if receipt.exists():raise RuntimeError('Refusing to overwrite timing receipt '+str(receipt))
        result=stack(ROOT/row['path'],parked=row['parked'])
        assert result['original']==get_baseline(row),(page,'fresh baseline mismatch')
        target=directory/f'{page}.json'
        record=detector_record(row,result['items'],result['timing']['total_s'])
        if target.exists():assert record['items']==json.loads(target.read_text())['items'],(page,'repeat output mismatch')
        else:
            dump(target,record)
            dump(directory/f'{page}.evidence.json',{k:v for k,v in result.items() if k!='items'})
            g=cv2.imread(str(ROOT/row['path']),0);render(g,result,directory/f'{page}.jpg')
        dump(receipt,dict(page=page,group=row['group'],direction=row['direction'],repeat=args.repeat,
            image_sha256=row['sha256'],source=key,counts=result['counts'],stages=result['stages'],
            unchanged=[q['polygon'] for q in result['items']]==[q['polygon'] for q in result['original']],**result['timing']))
        print(page,result['counts'],round(result['timing']['correction_s']*1000,2),flush=True)
    assert signature()[0]==key,'Sources changed during timed run'


def summary(args):
    directory=DEST/args.version;rows=[json.loads(p.read_text()) for p in sorted(directory.glob('*.r[0-9].json'))]
    out={}
    for repeat in sorted({r['repeat'] for r in rows}):
        for name,pred in [('agreement',lambda r:r['group']=='agreement'),('discrepancy',lambda r:r['group'].startswith('discrepancy')),('changed',lambda r:any(r['counts'].values())),('all',lambda r:True)]:
            rr=[r for r in rows if r['repeat']==repeat and pred(r)]
            if not rr:continue
            fields={}
            for key in ('decode_s','detector_s','paddle_file_s','correction_s','total_s'):
                v=np.array([r[key] for r in rr])*1000
                fields[key]=dict(median=float(np.median(v)),p95=float(np.percentile(v,95)),max=float(v.max()),max_page=rr[int(v.argmax())]['page'])
            for key in sorted({k for r in rr for k in r['stages']}):
                v=np.array([r['stages'].get(key,0) for r in rr])*1000
                fields[key]=dict(median=float(np.median(v)),p95=float(np.percentile(v,95)),max=float(v.max()),max_page=rr[int(v.argmax())]['page'])
            out[f'{name}_r{repeat}']=dict(n=len(rr),milliseconds=fields)
    dump(directory/'summary.json',out)
    print(json.dumps({k:{f:v['milliseconds'][f] for f in ('correction_s','total_s','ink_s')} for k,v in out.items()},indent=2))


def review(args):
    directory=DEST/args.version;rows=manifest()['pages'];tiles=[];ledger=[];links=[]
    for i,row in enumerate(rows):
        p=row['page'];im=cv2.imread(str(directory/f'{p}.jpg'));assert im is not None,p
        scale=600/im.shape[1];im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        canvas=np.full((1060,600,3),255,np.uint8)
        if im.shape[0]>1060:im=cv2.resize(im,(round(600*1060/im.shape[0]),1060))
        canvas[:im.shape[0],:im.shape[1]]=im;tiles.append(canvas)
        evidence=json.loads((directory/f'{p}.evidence.json').read_text())
        ledger.append(dict(page=p,group=row['group'],sheet=i//6,image_sha256=row['sha256'],counts=evidence['counts'],review='pending'))
        links.append(f'<article><h3>{html.escape(p)}</h3><p>{html.escape(str(evidence["counts"]))}</p><a href="{p}.jpg"><img loading="lazy" src="{p}.jpg"></a><a href="{p}.paddle.jpg">Paddle</a> · <a href="{p}.json">detector JSON</a> · <a href="{p}.evidence.json">evidence</a></article>')
        if len(tiles)==6 or i==len(rows)-1:
            tiles += [np.full((1060,600,3),255,np.uint8)]*(6-len(tiles))
            save_image(directory/f'overview-{i//6:02d}.jpg',np.vstack([np.hstack(tiles[:3]),np.hstack(tiles[3:])]))
            tiles=[]
    if not (directory/'review.json').exists():dump(directory/'review.json',ledger)
    (directory/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Combined fast lines</title><style>body{font:16px system-ui;margin:24px;background:#f4f2ed}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}img{width:100%}article{background:white;padding:12px}h3{overflow-wrap:anywhere}@media(max-width:900px){main{grid-template-columns:1fr}}</style><h1>Combined fast lines</h1><p>Added lines green; removed Paddle boxes red; reshaped/cut line blue over old grey; retained Paddle blue-grey. Only active lines rendered. Click to enlarge; Paddle output is separate.</p><p>Timing: <a href="summary.json">repeated raw summary</a>. Review: <a href="review.json">per-page ledger</a>.</p><main>'+''.join(links)+'</main>')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',help='image path, benchmark, summary or review');ap.add_argument('--output',type=Path);ap.add_argument('--version',default='v1');ap.add_argument('--repeat',type=int,default=1);ap.add_argument('--group');ap.add_argument('--offset',type=int,default=0);ap.add_argument('--limit',type=int,default=195);args=ap.parse_args()
    if args.action in ('benchmark','summary','review'):globals()[args.action](args)
    else:
        result=Stack()(args.action);row=dict(page=Path(args.action).stem,image_size=result['image_size'])
        record=detector_record(row,result['items'],result['timing']['total_s']);record.update(timing=result['timing'],corrections=result['counts'])
        if args.output:dump(args.output,record)
        else:print(json.dumps(record))

if __name__=='__main__':main()
