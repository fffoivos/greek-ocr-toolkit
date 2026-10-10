"""Q8 offline evidence and fresh runtime harness; never imports the page API."""
import argparse
import json
import random
import html
import platform
import shutil
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import Image

from .shared.manifest import ROOT, OUT, MODEL, PARKED, digest
from .shared.context import Context
from .shared.detector import Detector, postprocess
from .shared.timing import Registry, dump, append, key, summary
from .shared.review import overlay, save_image, detector_record
from .shared.contracts import bbox
from .shared.geometry import roi
from .layout_barriers.run import run as dense_layout

DEST = OUT / 'round2/rule_separators'
COMMON = OUT / 'round2/shared'
OLD = OUT / 'shared/cache'


def manifest():
    path = COMMON / 'manifest.json'
    if path.exists():
        return json.loads(path.read_text())
    labels_path = ROOT / '.astra/fast_lines/discrepancy/directions.json'
    labels = json.loads(labels_path.read_text())['pages']
    dev = sorted((ROOT / '.astra/pages').glob('*.png'))
    supplied = ROOT / '.astra/fast_lines/discrepancy/pages'
    assert len(dev) == 54 and len(labels) == 141
    assert {p.stem for p in supplied.glob('*.png')} == set(labels)
    entries = [(p, dict(set='development', direction='development')) for p in dev]
    entries += [(supplied / (p + '.png'), meta) for p, meta in sorted(labels.items())]
    assert len({p.stem for p, _ in entries}) == 195
    rows = []
    for p, meta in entries:
        with Image.open(p) as im:
            size = list(im.size)
        rows.append(dict(page=p.stem, path=str(p.relative_to(ROOT)), sha256=digest(p),
                         image_size=size, group=meta['set'], direction=meta['direction'],
                         labels=meta, parked=p.stem == PARKED))
    data = dict(pages=rows, model_sha256=digest(MODEL), directions_sha256=digest(labels_path),
                scope='exactly 54 dev + 141 direction-labelled supplied pages; orientation parked')
    dump(path, data)
    return data


def baseline_path(row):
    p = OLD / (row['page'] + '.json')
    return p if p.exists() else COMMON / 'baseline' / (row['page'] + '.json')


def get_baseline(row):
    return json.loads(baseline_path(row).read_text())['items']


def references(rows):
    directory = DEST / 'references'
    registry = Registry(COMMON / 'registry')
    d = None
    old_manifest = {r['page']: r for r in json.loads((OUT/'shared/manifest.json').read_text())['pages']}
    for n, row in enumerate(rows):
        p = row['page']
        record = directory / (p + '.json')
        if record.exists():
            continue
        gray = cv2.imread(str(ROOT / row['path']), 0)
        if p in old_manifest:
            assert old_manifest[p]['sha256'] == row['sha256']
        else:
            if d is None:
                d = Detector()
            with registry.claim('R2-new-baseline', row['sha256'], {'model': digest(MODEL)},
                                digest(ROOT/'prototypes/fast_lines/shared/detector.py')) as event:
                if event is not None:
                    pm, meta = d.infer(gray)
                    items = postprocess(pm, row['image_size'])
                    dump(COMMON/'baseline'/(p+'.json'), dict(items=items, timings=meta, event=event['id']))
                    np.save(COMMON/'baseline'/(p+'.npy'), pm)
        items = get_baseline(row)
        previous = OUT/'layout_barriers'/(p+'.evidence.json')
        if previous.exists():
            evidence = json.loads(previous.read_text())
            source = dict(reused=str(previous.relative_to(ROOT)), sha256=digest(previous))
        elif row['parked']:
            evidence = dict(rules=[], barriers=[], changes=[], table=False)
            source = dict(parked=True)
        else:
            with registry.claim('R2-new-dense-layout', row['sha256'], {'baseline': digest(baseline_path(row))},
                                key(digest(ROOT/'prototypes/fast_lines/layout_barriers/run.py'),
                                    digest(ROOT/'prototypes/fast_lines/shared/image_evidence.py'))) as event:
                assert event is not None, 'missing artifact from completed reference run'
                ctx = Context(gray, np.zeros((1,1), np.float32), items)
                t = perf_counter(); data = dense_layout(ctx, 2); elapsed = perf_counter()-t
                evidence = {k:v for k,v in data.items() if k != 'items'}
                source = dict(event=event['id'], seconds=elapsed)
        dump(record, dict(page=p, source=source, evidence=evidence))
        paths = [r.get('path', [[(r['bbox'][0]+r['bbox'][2])/2,r['bbox'][1]],
                                [(r['bbox'][0]+r['bbox'][2])/2,r['bbox'][3]]])
                 for r in evidence.get('rules', []) if r['direction']=='vertical']
        save_image(directory/(p+'.jpg'), overlay(gray, paths=paths,
                   title=p+' | dense Q7 rule hypotheses (cyan); raw ink remains the referee', width=1500))
        if (n+1)%20==0 or n==len(rows)-1:
            print('references', n+1, len(rows), flush=True)
    contacts(rows, directory, suffix='.jpg', destination=directory/'sheets', per_sheet=6)


def contacts(rows, directory, suffix, destination, per_sheet=6):
    destination.mkdir(parents=True, exist_ok=True)
    for start in range(0,len(rows),per_sheet):
        cells=[]
        for r in rows[start:start+per_sheet]:
            im=cv2.imread(str(directory/(r['page']+suffix)))
            scale=min(580/im.shape[1],760/im.shape[0])
            im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
            tile=np.full((815,600,3),255,np.uint8)
            tile[50:50+im.shape[0],:im.shape[1]]=im
            cv2.putText(tile,r['page'],(4,18),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1)
            cv2.putText(tile,r['group']+' / '+r['direction'],(4,37),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
            cells.append(tile)
        while len(cells)%3:
            cells.append(np.full_like(cells[0],255))
        save_image(destination/f'{start//per_sheet:02d}.jpg',np.vstack([np.hstack(cells[i:i+3]) for i in range(0,len(cells),3)]))


def study(rows):
    from .layout_barriers.fast import run
    from .shared.review import change_overlay
    registry=Registry(COMMON/'registry')
    source=key(digest(ROOT/'prototypes/fast_lines/layout_barriers/fast.py'),
               digest(ROOT/'prototypes/fast_lines/shared/geometry.py'),
               digest(ROOT/'prototypes/fast_lines/shared/image_evidence.py'))
    directory=DEST/('study-'+source[:12])
    directory.mkdir(parents=True,exist_ok=True)
    dump(DEST/'active-study.json',dict(directory=str(directory.relative_to(ROOT)),source=source))
    counts=[]
    for n,row in enumerate(rows):
        p=row['page']
        with registry.claim('R2-separator-study',row['sha256'],{'baseline':digest(baseline_path(row))},source) as event:
            if event is None:
                counts.append(json.loads((directory/(p+'.evidence.json')).read_text()))
                continue
            gray=cv2.imread(str(ROOT/row['path']),0)
            items=get_baseline(row)
            product=run(gray,items) if not row['parked'] else dict(items=items,changes=[],rules=[],decisions=[],
                         protected_rules=[],witness={'candidates':[],'seconds':0.},correction_s=0.,added_s=0.)
            evidence={k:v for k,v in product.items() if k!='items'}
            evidence.update(page=p,group=row['group'],direction=row['direction'],parked=row['parked'],event=event['id'])
            dump(directory/(p+'.evidence.json'),evidence)
            dump(directory/(p+'.json'),detector_record(row,product['items'],product['added_s']))
            save_image(directory/(p+'.jpg'),change_overlay(gray,items,product['items'],product['changes'],
                       title=p+' | old grey; new green; removed ink red'))
            counts.append(evidence)
        if (n+1)%20==0 or n==len(rows)-1:
            print('study',n+1,len(rows),flush=True)
    contacts(rows,directory,'.jpg',directory/'sheets')
    dump(directory/'counts.json',[dict(page=r['page'],group=r['group'],direction=r['direction'],
         candidates=len(r['witness']['candidates']),changes=len(r['changes']),added_s=r['added_s']) for r in counts])
    print('changed',[(r['page'],len(r['changes'])) for r in counts if r['changes']],flush=True)


def active_study():
    active=json.loads((DEST/'active-study.json').read_text())
    source=key(digest(ROOT/'prototypes/fast_lines/layout_barriers/fast.py'),
               digest(ROOT/'prototypes/fast_lines/shared/geometry.py'),
               digest(ROOT/'prototypes/fast_lines/shared/image_evidence.py'))
    assert source==active['source'], 'study is stale'
    return ROOT/active['directory'],source


def review(rows):
    """Render saved evidence only; no algorithm experiments or inference here."""
    from .shared.review import change_overlay
    directory,_=active_study()
    destination=directory/'seams'
    destination.mkdir(exist_ok=True)
    pages=[]; all_lines=[]
    for row in rows:
        p=row['page']; before=get_baseline(row)
        ev=json.loads((directory/(p+'.evidence.json')).read_text())
        ref=json.loads((DEST/'references'/(p+'.json')).read_text())['evidence']
        vertical=[r for r in ref.get('rules',[]) if r['direction']=='vertical']
        candidate_lines={i for c in ev['witness']['candidates'] for i in c['lines']}
        changed={c['line']:c for c in ev['changes']}
        # Every original line is explicitly accounted for, including no-op paths.
        lines=[]
        for i,item in enumerate(before):
            x0,y0,x1,y1=bbox(item); ym=(y0+y1)/2
            matches=[]
            for j,r in enumerate(vertical):
                path=r.get('path',[[sum(r['bbox'][::2])/2,r['bbox'][1]],
                                   [sum(r['bbox'][::2])/2,r['bbox'][3]]])
                a,b=np.asarray(path)[[0,-1]]
                if abs(b[1]-a[1])<1e-6:
                    continue
                x=a[0]+(b[0]-a[0])*(ym-a[1])/(b[1]-a[1])
                if x0<x<x1 and max(y0,min(a[1],b[1]))<min(y1,max(a[1],b[1])):
                    matches.append(j)
            lines.append(dict(line=i,dense_rule_crossings=matches,fast_nominated=i in candidate_lines,
                              action='split' if i in changed else 'unchanged',
                              decisions=[d for d in ev['decisions'] if d.get('line')==i or i in d.get('lines',[])]))
        dump(directory/(p+'.comparison.json'),dict(page=p,lines=lines,
             warning='Dense crossings are geometric hypotheses, not correct-line labels.'))
        all_lines.append(dict(page=p,lines=len(lines),nominated=len(candidate_lines),changed=len(changed),
                              dense_crossing_lines=sum(bool(x['dense_rule_crossings']) for x in lines)))
        if not changed:
            continue
        gray=cv2.imread(str(ROOT/row['path']),0)
        height=ev['witness']['height']; tiles=[]; crop_records=[]
        for i,change in changed.items():
            decision=next(d for d in ev['decisions'] if d.get('line')==i and d['decision']=='split')
            rule=ev['rules'][decision['rule']]
            b=bbox(before[i]); cy=(b[1]+b[3])/2
            cx=rule['intercept']+rule['slope']*cy
            x0,y0,x1,y1=roi([cx-3*height,b[1]-.4*height,cx+3*height,b[3]+.4*height],gray.shape)
            raw=gray[y0:y1,x0:x1]
            shift=np.array([x0,y0])
            old=dict(before[i],polygon=(np.asarray(change['old'])-shift).tolist())
            new=[dict(before[i],polygon=(np.asarray(q)-shift).tolist()) for q in change['new']]
            delta=[dict(line=0,old=old['polygon'],new=[q['polygon'] for q in new])]
            drawn=change_overlay(raw,[old],new,delta,width=raw.shape[1])
            pair=np.hstack([cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR),drawn])
            scale=min(580/pair.shape[1],160/pair.shape[0])
            pair=cv2.resize(pair,None,fx=scale,fy=scale,interpolation=cv2.INTER_LINEAR)
            tile=np.full((190,600,3),255,np.uint8)
            cv2.putText(tile,f'line {i}: raw | old grey, new green, removed red',(4,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
            tile[27:27+pair.shape[0],:pair.shape[1]]=pair
            tiles.append(tile)
            crop_records.append(dict(line=i,bbox=[x0,y0,x1,y1],sheet=len(tiles[:-1])//20))
        sheets=[]
        for start in range(0,len(tiles),20):
            batch=tiles[start:start+20]
            while len(batch)%2:
                batch.append(np.full_like(batch[0],255))
            board=np.vstack([np.hstack(batch[j:j+2]) for j in range(0,len(batch),2)])
            name=f'{p}-{start//20:02d}.jpg'
            save_image(destination/name,board); sheets.append(name)
        dump(destination/(p+'.json'),dict(page=p,crops=crop_records,sheets=sheets))
        pages.append(dict(page=p,changes=len(changed),sheets=sheets))
    dump(destination/'index.json',pages)
    dump(directory/'line-comparison-summary.json',all_lines)
    print('review',len(rows),'pages;',sum(p['changes'] for p in pages),'changed lines;',
          sum(len(p['sheets']) for p in pages),'seam sheets',flush=True)


def benchmark(rows):
    from .layout_barriers.fast import run
    directory,source=active_study()
    registry=Registry(COMMON/'registry')
    config=dict(repetitions=3,seed=81010,model=digest(MODEL),opencv_threads=1,
                onnx_threads=1,detector_source=digest(ROOT/'prototypes/fast_lines/shared/detector.py'),
                db_source=digest(ROOT/'prototypes/fast_lines/shared/paddle_db.py'),
                harness_source=digest(Path(__file__)))
    receipt=DEST/'benchmark.json'
    with registry.claim('R2-fresh-runtime',key([r['sha256'] for r in rows]),config,source) as event:
        if event is None:
            print('completed benchmark already exists; no rerun',flush=True)
            return
        assert not receipt.exists(), 'final benchmark exists; do not repeat without a new documented question'
        t=perf_counter(); detector=Detector(); startup=perf_counter()-t
        warm=cv2.imread(str(ROOT/rows[0]['path']),0)
        t=perf_counter(); pm,_=detector.infer(warm); postprocess(pm,rows[0]['image_size']); warmup=perf_counter()-t
        records=[]; order=[]
        for repetition in range(3):
            shuffled=list(rows); random.Random(81010+repetition).shuffle(shuffled)
            order.append([r['page'] for r in shuffled])
            for n,row in enumerate(shuffled):
                p=row['page']; t=perf_counter()
                gray=cv2.imread(str(ROOT/row['path']),0); decode=perf_counter()-t
                t=perf_counter(); pm,meta=detector.infer(gray)
                pt=perf_counter(); items=postprocess(pm,row['image_size']); post=perf_counter()-pt
                baseline=perf_counter()-t
                at=perf_counter()
                if row['parked']:
                    product=dict(items=items,changes=[],witness={'candidates':[],'seconds':0.},correction_s=0.,added_s=0.)
                else:
                    product=run(gray,items)
                added=perf_counter()-at; total=perf_counter()-t
                # Assertions and serialization occur after timing, never substitute caches.
                assert items==get_baseline(row), f'baseline drift: {p}'
                expected=json.loads((directory/(p+'.json')).read_text())['items']
                record=detector_record(row,product['items'],total)
                assert record['items']==expected, f'product drift: {p}'
                timing=dict(page=p,group=row['group'],direction=row['direction'],parked=row['parked'],
                            repetition=repetition,decode_s=decode,baseline_s=baseline,
                            preprocess_s=meta['preprocess_s'],inference_s=meta['inference_s'],postprocess_s=post,
                            scout_s=product['witness']['seconds'],correction_s=product['correction_s'],
                            added_s=added,total_s=total,end_to_end_s=decode+total,
                            candidates=len(product['witness']['candidates']),changes=len(product['changes']))
                records.append(timing)
                append(DEST/'benchmark.raw.jsonl',timing)
                if repetition==0:
                    record['timing_note']='fresh first measured repetition; decode and review serialization excluded; see benchmark.json'
                    dump(DEST/(p+'.json'),record)
                    shutil.copyfile(directory/(p+'.jpg'),DEST/(p+'.jpg'))
                    shutil.copyfile(directory/(p+'.evidence.json'),DEST/(p+'.evidence.json'))
                    shutil.copyfile(directory/(p+'.comparison.json'),DEST/(p+'.comparison.json'))
                if (n+1)%40==0 or n==len(rows)-1:
                    print('benchmark',repetition+1,n+1,len(rows),flush=True)
        cohorts={name:[r for r in records if r['group']==name and not r['parked']]
                 for name in ('development','agreement','discrepancy','discrepancy_extra')}
        cohorts.update({name:[r for r in records if r['direction']==name and not r['parked']]
                        for name in ('ours_more','paddle_more','both','neither')})
        cohorts['activated']=[r for r in records if r['candidates']]
        summaries={name:{metric:summary([r[metric] for r in rr])
                        for metric in ('decode_s','baseline_s','scout_s','correction_s','added_s','total_s','end_to_end_s')}
                   for name,rr in cohorts.items()}
        dump(receipt,dict(source=source,event=event['id'],config=config,machine=platform.platform(),
                          processor=platform.processor(),opencv=cv2.__version__,startup_s=startup,warmup_s=warmup,
                          order=order,records=records,summaries=summaries,
                          timing='195 pages x 3 fresh passes; one parked page excluded from upright summaries; warm CPU session; decode separate'))
        print(json.dumps(summaries,indent=2),flush=True)


def publish(rows):
    directory,_=active_study()
    bench=json.loads((DEST/'benchmark.json').read_text())
    parts=['<!doctype html><meta charset="utf-8"><title>Q8 rule separators</title>',
           '<style>body{font:16px system-ui;margin:24px;background:#faf8f4}article{display:inline-block;width:350px;vertical-align:top;margin:12px}img{width:100%}a{color:#145278}</style>',
           '<h1>Q8: conditional rule separators</h1><p>195 supplied pages. Original Paddle boxes: grey-blue. Changed old boxes: grey. New polygons: green. Removed ink: red. No discounted lines rendered. A separator fix does not certify the rest of a page.</p>',
           '<p><a href="benchmark.json">All measured timings</a> · <a href="benchmark.raw.jsonl">Raw timing rows</a></p>']
    for row in rows:
        p=row['page']; ev=json.loads((DEST/(p+'.evidence.json')).read_text())
        samples=[r for r in bench['records'] if r['page']==p]
        added=np.median([r['added_s'] for r in samples])*1000
        links=''
        seams=directory/'seams'/(p+'.json')
        if seams.exists():
            for name in json.loads(seams.read_text())['sheets']:
                links+=f' · <a href="{directory.name}/seams/{name}">Seams {name[-6:-4]}</a>'
        parts.append(f'<article><b>{html.escape(p)}</b><p>{row["group"]} / {row["direction"]}; {len(ev["changes"])} cuts; +{added:.2f} ms median</p><a href="{p}.jpg"><img loading="lazy" src="{p}.jpg"></a><p><a href="{p}.json">Lines</a> · <a href="{p}.evidence.json">Decisions</a> · <a href="{p}.comparison.json">Every source line</a> · <a href="references/{p}.jpg">Explicit reference</a>{links}</p></article>')
    (DEST/'index.html').write_text('\n'.join(parts))
    contacts(rows,DEST,'.jpg',DEST/'sheets')
    print('published',DEST/'index.html')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['references','study','review','benchmark','publish'])
    args=parser.parse_args()
    cv2.setNumThreads(1)
    rows=manifest()['pages']
    globals()[args.phase](rows)

if __name__=='__main__':
    main()
