"""Reproducible R6 review crops and strict saved-artifact validation.

Owner labels and page names occur only in this offline review/export code.
They never enter Stack or correction modules.
"""
import argparse,json,re
from pathlib import Path
from collections import Counter
import cv2,numpy as np
from shapely.geometry import Polygon
from ..features_ink.round6_faintness import cohort,ROOT,REVIEW
from ..features_geometry.round6_rows_export import ocr_crop
from ..shared.timing import dump
from ..shared.manifest import digest
from .__main__ import review

BASE=ROOT.parent/'greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round6/C_curvature/final-v2'
OWNERS=REVIEW.parent/'review_r5_rows/owner_marks.json'


def sheets(files,out,prefix,per=4):
    for offset in range(0,len(files),per):
        panels=[]
        for f in files[offset:offset+per]:
            g=cv2.imread(str(f));scale=min(1,1500/g.shape[1]);g=cv2.resize(g,None,fx=scale,fy=scale)
            p=np.full((g.shape[0],1500,3),255,np.uint8);p[:,:g.shape[1]]=g;panels.append(p)
        cv2.imwrite(str(out/f'{prefix}-{offset//per:02}.jpg'),np.vstack(panels))


def controls(out):
    from ..features_ink.test_round6 import page
    from ..shared.ink_faintness import analyze
    panels=[];records=[]
    for name,value,font,scale,thick,blur in [('grey rubric',90,0,.85,2,False),('light grey',140,0,.85,2,False),('light italic',95,16,.8,1,False),('blurred small footnote',80,0,.5,1,True),('red rubric luminance',76,0,.85,2,False)]:
        g,qs=page('grey');g[390:]=245;cv2.putText(g,'REAL FRONT PRINT',(18,430),font,scale,value,thick,cv2.LINE_AA)
        if blur:g[390:]=cv2.GaussianBlur(g[390:],(3,3),.6)
        e=analyze(g,qs,height=30);dropped=7 in e['suppress_indices'];im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
        cv2.polylines(im,[np.rint(qs[-1]['polygon']).astype(int)],True,(0,0,230) if dropped else (0,150,0),2)
        bar=np.full((35,720,3),255,np.uint8);cv2.putText(bar,name+(': FALSE REMOVAL' if dropped else ': kept'),(8,24),0,.55,(0,0,0),1);panels.append(np.vstack([bar,im]));records.append(dict(control=name,known_front=True,removed=dropped,evidence=e))
    cv2.imwrite(str(out/'faint-front-controls.jpg'),np.hstack(panels));dump(out/'faint-front-controls.json',records)


def build(out):
    rows=cohort();marked=[m for m in json.loads(OWNERS.read_text()) if m['mark'] is not None];ledger=[];deltas=[];duplicates=[];removed=[];returns=[]
    owner_files=[];duplicate_files=[];removal_files=[];return_files=[]
    for row in rows:
        p=row['page'];new=json.loads((out/f'{p}.json').read_text())['items'];e=json.loads((out/f'{p}.evidence.json').read_text());prior=json.loads((BASE/f'{p}.json').read_text())['items'];pe=json.loads((BASE/f'{p}.evidence.json').read_text());gray=None
        def pixels():
            nonlocal gray
            if gray is None:gray=cv2.imread(str(ROOT/row['path']),0)
            return gray
        shapes=[Polygon(q['polygon']) for q in new];lookup={json.dumps(q['polygon']):i for i,q in enumerate(new)};order={r['item_index']:r['number'] for r in json.loads((out/f'{p}.order.json').read_text())}
        marks=[m for m in marked if m['page']==p]
        if marks:
            r5=json.loads((out.parent/'r5'/f'{p}.json').read_text())['items']
            for m in marks:
                q=r5[m['segment']];shape=Polygon(q['polygon']);exact=lookup.get(json.dumps(q['polygon']))
                ids=[exact] if exact is not None else [i for i,s in enumerate(shapes) if s.intersects(shape) and s.intersection(shape).area>.2*min(s.area,shape.area)]
                name=f'{p}.owner-{m["segment"]}.jpg';ocr_crop(pixels(),q,[new[i] for i in ids],out/name,f'{len(ledger)} {p} R5 index {m["segment"]} owner {m["mark"]}');owner_files.append(out/name)
                ledger.append(dict(m,polygon=q['polygon'],indices=ids,numbers=[order[i] for i in ids],exact=exact is not None,image=name,review='pending'))
        ow=e.get('row_ownership',{});duplicates.append(dict(page=p,before=ow.get('duplicate_pairs_before',0),after=ow.get('duplicate_pairs_after',0),changes=ow.get('changes',[])))
        for j,c in enumerate(ow.get('changes',[])):
            children=[dict(polygon=c['owner_polygon'])]+[dict(polygon=v) for v in c['new']]
            name=f'{p}.duplicate-{j}.jpg';ocr_crop(pixels(),dict(polygon=c['old']),children,out/name,f'{p} duplicate {j}: before / existing owner / unique pieces');duplicate_files.append(out/name)
        oldremoved=[q['polygon'] for q in pe.get('removed',[])];newremoved=[q['polygon'] for q in e.get('removed',[])]
        for j,q in enumerate(e.get('removed',[])):
            if q['polygon'] in oldremoved:continue
            name=f'{p}.removal-{j}.jpg';ocr_crop(pixels(),q,[],out/name,f'{p} new removal {j} {q["removal"]}');removal_files.append(out/name);removed.append(dict(page=p,item=q,image=name,review='pending'))
        for j,q in enumerate(pe.get('removed',[])):
            if q['polygon'] in newremoved:continue
            name=f'{p}.returned-{j}.jpg';ocr_crop(pixels(),q,[],out/name,f'{p} prior removal retained {j}');return_files.append(out/name);returns.append(dict(page=p,item=q,image=name,review='pending'))
        deltas.append(dict(page=p,changed=[q['polygon'] for q in new]!=[q['polygon'] for q in prior],counts=e['counts'],before=len(prior),after=len(new)))
    dump(out/'owner-marks.json',ledger);dump(out/'duplicate-audit.json',duplicates);dump(out/'new-removals.json',removed);dump(out/'returned-removals.json',returns);dump(out/'changes-vs-C.json',deltas)
    sheets(owner_files,out,'owner-sheet');sheets(duplicate_files,out,'duplicate-sheet');sheets(removal_files,out,'removal-sheet',8);sheets(return_files,out,'returned-sheet',8);controls(out)
    review(argparse.Namespace(version=out.name))
    print(dict(owner_marks=len(ledger),duplicates_before=sum(r['before'] for r in duplicates),duplicates_after=sum(r['after'] for r in duplicates),new_removals=len(removed),returned_removals=len(returns)))


def validate(out):
    rows=cohort();checks=0;counts=Counter();s1=json.loads((out/'source-r1.json').read_text());s2=json.loads((out/'source-r2.json').read_text());assert s1==s2;checks+=1
    for name,sha in s1['files'].items():assert digest(ROOT/name)==sha and digest(out/'source'/name)==sha;checks+=2
    notes={q['page']:q for q in json.loads((out/'review.json').read_text())};assert len(notes)==208
    for row in rows:
        p=row['page'];r=json.loads((out/f'{p}.json').read_text());e=json.loads((out/f'{p}.evidence.json').read_text());pe=json.loads((BASE/f'{p}.evidence.json').read_text());assert e['original']==pe['original'];checks+=1
        assert r['unit']=='line' and r['image_size']==row['image_size'] and r['seconds']==e['timing']['total_s'];assert digest(ROOT/row['path'])==row['sha256'];checks+=2
        for q in r['items']:
            v=np.asarray(q['polygon']);assert v.ndim==2 and v.shape[1]==2 and len(v)>=3 and np.isfinite(v).all();assert (v>=0).all() and (v[:,0]<=row['image_size'][0]).all() and (v[:,1]<=row['image_size'][1]).all();assert q.get('baseline') is None and not q.get('discounted');assert Polygon(v).is_valid;checks+=4
        c=e['counts'];counts.update(c)
        if not row['parked']:
            source={i for q in r['items']+e.get('removed',[]) for i in q.get('source_ids',[])};assert source==set(range(len(e['original']))),(p,'source ledger');checks+=1
            fields=[e.get('page_field',{}).get(key) or {} for key in ('early_replacement','replacement')];delta=sum(len(f.get('replacements',[]))-len(f.get('changed_indices',[])) for f in fields)
            split=sum(len(q['new'])-1 for q in e['rows']['changes']);dedup=sum(len(q['new'])-1 for q in e['row_ownership']['changes'])
            expected=len(e['original'])+c['q8']+c['curved']+c.get('columns',0)-c['back']-c['ornaments']-c['seals']+c['added']-c['joined_reduction']-c['faint']+delta+split+dedup
            assert len(r['items'])==expected,(p,'count ledger',len(r['items']),expected);assert e['row_ownership']['duplicate_pairs_after']==0;checks+=2
        else:assert r['items']==e['original'];checks+=1
        for rep in (1,2):
            t=json.loads((out/f'{p}.r{rep}.json').read_text());assert t['source']==s1['key'] and t['counts']==c and t['image_sha256']==row['sha256'];checks+=3
        order=json.loads((out/f'{p}.order.json').read_text());assert sorted(q['item_index'] for q in order)==list(range(len(r['items'])));checks+=1
        for ext in ('.jpg','.paddle.jpg'):assert (out/(p+ext)).stat().st_size>0;checks+=1
        assert notes[p]['review']!='pending' and notes[p]['observation'];checks+=1
    marks=json.loads((out/'owner-marks.json').read_text());assert len(marks)==256 and all(m['review']!='pending' for m in marks);checks+=257
    comments=(out/'COMMENTS.md').read_text();raw=REVIEW.joinpath('REVIEW.md').read_text();blocks=re.split(r'^## ',raw,flags=re.M)[1:];n=0
    for block in blocks:
        quote='\n'.join(l for l in block.splitlines() if l.startswith('>'))
        if quote:assert quote in comments;n+=1;checks+=1
    assert n==73;checks+=1
    links=re.findall(r'\]\(([^)]+)\)',comments+(out/'ROWS.md').read_text());assert all((out/q).exists() for q in links);checks+=len(links)
    for name in ('new-removals','returned-removals'):
        for q in json.loads((out/(name+'.json')).read_text()):assert q['review']!='pending';checks+=1
    result=dict(pages=208,repeats=2,checks=checks,counts=dict(counts),owner_comments=73,owner_segments=256,held_out_accessed=False,production_pages_changed=False)
    dump(out/'validation.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['build','validate']);ap.add_argument('--version',default='r6');a=ap.parse_args();globals()[a.action](ROOT/'.astra/fast_lines/out/stack'/a.version)
