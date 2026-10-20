"""Offline whole-cohort retention, owner ledgers and source-bound validation.

Only this evidence package knows historical page names and owner numbers.
Found ink is native grey <200 inside old crops, excluding only OLD exclusions.
New removals do not excuse loss. Equality is not a claim of OCR correctness.
"""
import argparse,html,importlib.util,json,re,shutil
from collections import Counter
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import Polygon
from ..features_ink.round6_faintness import cohort,ROOT,REVIEW
from ..shared.geometry import height_proxy
from ..shared.manifest import digest
from ..shared.timing import dump
from .__main__ import review,signature
from .review_r6 import controls

DEFAULT=ROOT.parent/'greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink/final-v1'
R6=ROOT/'.astra/fast_lines/out/stack/r6'


def read(path):return json.loads(path.read_text())


def raster(items,shape):
    m=np.zeros(shape,np.uint8)
    for q in items:
        if not q.get('discounted'):cv2.fillPoly(m,[np.rint(q['polygon']).astype(int)],1)
    return m


def native_panel(gray,before,after,loss,bounds,title):
    l,t,r,b=map(int,bounds);w=r-l;h=b-t
    im=Image.new('RGB',(3*w,h+25),'white');draw=ImageDraw.Draw(im)
    for k,qs in enumerate(([],before,after)):
        crop=cv2.cvtColor(gray[t:b,l:r],cv2.COLOR_GRAY2RGB)
        for q in qs:
            if not q.get('discounted'):cv2.polylines(crop,[np.rint(np.asarray(q['polygon'])-[l,t]).astype(int)],True,(0,110,220) if k==1 else (180,0,180),1)
        if k==2:crop[loss[t:b,l:r]]=[255,0,0]
        im.paste(Image.fromarray(crop),(k*w,25));draw.text((k*w+3,3),title+' | '+('raw','current default','r7 / red lost')[k],fill='black')
    return im


def crop_bounds(polygon,shape,h):
    a=np.asarray(polygon);lo=np.maximum(0,np.floor(a.min(0)-h)).astype(int);hi=np.minimum(shape[::-1],np.ceil(a.max(0)+h)).astype(int)
    return [*lo,*hi]


def loss_clusters(gray,loss,h,owner_mask,all_required,before,after,out,page):
    k=max(1,round(h/2));n,lab,stats,_=cv2.connectedComponentsWithStats(cv2.dilate(loss.astype(np.uint8),np.ones((k,k),np.uint8)),8)
    counts=np.bincount(lab[loss],minlength=n);marked=np.bincount(lab[loss&((owner_mask>0)|all_required)],minlength=n);records=[]
    for j in np.flatnonzero((counts>=h*h/40)|(marked>0)):
        if not j:continue
        x,y,w,z,_=stats[j];bounds=[max(0,x-round(h)),max(0,y-round(h)),min(gray.shape[1],x+w+round(h)),min(gray.shape[0],y+z+round(h))]
        image=f'{page}.loss-{j}.png';native_panel(gray,before,after,loss,bounds,f'{page} cluster {j} / {counts[j]} px').save(out/image)
        records.append(dict(pixels=int(counts[j]),bounds=bounds,image=image,review='pending'))
    return records


def comparison(gray,original,before,after,path):
    panels=[]
    for label,qs,color in [('Paddle alone',original,(220,110,0)),('current default',before,(220,110,0)),('task 4',after,(180,0,180))]:
        s=min(1.,1000/gray.shape[1]);im=cv2.cvtColor(cv2.resize(gray,None,fx=s,fy=s),cv2.COLOR_GRAY2BGR)
        for q in qs:
            if not q.get('discounted'):cv2.polylines(im,[np.rint(np.asarray(q['polygon'])*s).astype(int)],True,color,1)
        bar=np.full((30,im.shape[1],3),255,np.uint8);cv2.putText(bar,label,(4,22),0,.55,(0,0,0),1);panels.append(np.vstack([bar,im]))
    cv2.imwrite(str(path),np.hstack(panels))


def build(out):
    dest=out/'acceptance';dest.mkdir(exist_ok=True);catalog=read(ROOT/'docs/research/FAST_LINES_ROUND7_MECHANISMS.json')
    comments=catalog['current_owner_comments']+catalog['all73_prior_comments'];marks=catalog['owner_row_marks']['records'];commented={r['page'] for r in comments}
    orderfile=REVIEW.parent/'review_r6/reading_order.py';spec=importlib.util.spec_from_file_location('owner_order',orderfile);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    protected={'s2-c0b02fe229794d2fe76d-p00010':118,'an-d83e7a198ade-p000099':108,'s2-3229200bf47ca465a42d-p00006':26}
    pages=[];mark_records=[];protected_records=[];reviews=[]
    for row in cohort():
        p=row['page'];after=read(out/f'{p}.json')['items'];e=read(out/f'{p}.evidence.json');before=read(DEFAULT/f'{p}.json')['items'];old_e=read(DEFAULT/f'{p}.evidence.json');r6=read(R6/f'{p}.json')['items'];r6e=read(R6/f'{p}.evidence.json')
        gray=cv2.imread(str(ROOT/row['path']),0);h=height_proxy(e['original'],gray.shape[::-1]);oldmask=raster(before,gray.shape);mask=raster(after,gray.shape);ex=raster(old_e.get('removed',[]),gray.shape)
        found=(gray<200)&(oldmask>0)&(ex==0);lost=found&(mask==0);r6mask=raster(r6,gray.shape);r6ex=raster(r6e.get('removed',[]),gray.shape);r6loss=(gray<200)&(r6mask>0)&(r6ex==0)&(mask==0)
        local=[m for m in marks if m['page']==p];marked=raster(local,gray.shape);exact=after==before
        clusters=loss_clusters(gray,lost,h,marked,p in commented,before,after,dest,p)
        rec=dict(page=p,group=row['group'],exact_current_default=exact,found_pixels=int(found.sum()),lost_pixels=int(lost.sum()),lost_below128=int((lost&(gray<128)).sum()),r6_lost_pixels=int(r6loss.sum()),required_clusters=clusters,old_count=len(before),new_count=len(after),missing_exact_exclusions=[i for i,q in enumerate(old_e.get('removed',[])) if not any(q['polygon']==v['polygon'] and q['removal']==v['removal'] for v in e.get('removed',[]))],new_intrusion_pixels=int(((gray<200)&(ex>0)&(mask>0)&(oldmask==0)).sum()),columns_exact=e.get('geometry',{}).get('columns',{}).get('changes')==old_e.get('geometry',{}).get('columns',{}).get('changes'))
        if not exact:
            rec['comparison']=f'{p}.comparison.jpg';comparison(gray,e['original'],before,after,dest/rec['comparison'])
        if np.any(r6loss):
            # Exact T3 output permits carrying its already-reviewed native
            # whole-deletion sheets; counts above are nevertheless remeasured.
            inherited=DEFAULT/'acceptance';files=sorted(inherited.glob(p+'.loss*'))
            for f in files:shutil.copyfile(f,dest/('r6-'+f.name))
            rec['r6_loss_views']=['r6-'+f.name for f in files if 'loss-view' in f.name]
        for m in local:
            name=f'{p}.mark-{m["segment"]}.png';native_panel(gray,before,after,lost,crop_bounds(m['polygon'],gray.shape,h),f'owner {m["mark"]}; historical #{m["segment"]}').save(dest/name)
            mm=raster([m],gray.shape);mark_records.append(dict(m,image='acceptance/'+name,review='inherited exact output' if exact else 'pending',r7_observation=('Current default items are identical; the prior native-crop disposition remains: '+m.get('observation','')) if exact else 'Changed page: inspect this native crop before assigning a verdict.',lost_pixels=int((lost&(mm>0)).sum())))
        if p in protected:
            number=protected[p];q=owner.reading_order(r6)[number-1];name=f'{p}.control-{number}.png';native_panel(gray,before,after,lost,crop_bounds(q['polygon'],gray.shape,h),f'approved recovery #{number}').save(dest/name)
            mm=raster([q],gray.shape);protected_records.append(dict(page=p,number=number,image='acceptance/'+name,polygon=q['polygon'],found_pixels=int((found&(mm>0)).sum()),lost_pixels=int((lost&(mm>0)).sum()),r6_lost_pixels=int((r6loss&(mm>0)).sum())))
        reviews.append(dict(page=p,group=row['group'],review='exact current-default comparison' if exact else 'pending',observation='All final items equal the current default. Its known errors remain; equality is not a new correctness verdict.' if exact else 'Changed output requires native review.',image=p+'.jpg'))
        pages.append(rec);print(p,exact,int(lost.sum()),int(r6loss.sum()),flush=True)
    dump(dest/'pages.json',pages);dump(out/'owner-marks.json',mark_records);dump(dest/'controls.json',protected_records);dump(out/'review.json',reviews)
    inherited=read(DEFAULT/'acceptance/verdicts.json');dump(dest/'r6-deletion-verdicts-inherited.json',inherited)
    comment_records=[]
    for q in comments:
        page=next(p for p in pages if p['page']==q['page']);comment_records.append(dict(q,current_default_exact=page['exact_current_default'],r7_status=q.get('status','open'),r7_observation=q.get('observation',''),r7_image=q['page']+'.jpg',review='inherited exact output' if page['exact_current_default'] else 'pending'))
    dump(out/'comments.json',comment_records);write_ledgers(out,comment_records,mark_records)
    controls(out);review(argparse.Namespace(version=out.name));gallery(out,pages)
    receipt=dict(pages=len(pages),comments=len(comments),marks=len(mark_records),exact_current_default=sum(p['exact_current_default'] for p in pages),lost_pixels=sum(p['lost_pixels'] for p in pages),r6_lost_pixels=sum(p['r6_lost_pixels'] for p in pages),required_clusters=sum(len(p['required_clusters']) for p in pages),missing_prior_exclusions=sum(bool(p['missing_exact_exclusions']) for p in pages),new_intrusion_pixels=sum(p['new_intrusion_pixels'] for p in pages),changed_column_results=sum(not p['columns_exact'] for p in pages),P0_definition='native grey <200 inside old final crop union, excluding only that baseline prior exclusions; absent r7 union',baseline_current=str(DEFAULT),baseline_r6=str(R6))
    dump(dest/'receipt.json',receipt)


def write_ledgers(out,comments,marks):
    lines=['# Owner comments — r7','', 'Owner words and historical numbers are unchanged. Exact output carries prior review evidence; it does not close unresolved curvature, faintness or recovery issues.','']
    for q in comments:
        lines += [f'## {q["id"]}: {q["page"]}', '', q.get('quote',q.get('owner_comment','')), '',f'**{q["r7_status"]}.** {q["r7_observation"]}',f'Output vs current default: {"exact" if q["current_default_exact"] else "changed"}. Review basis: {q["review"]}.',f'[Final page]({q["r7_image"]})','']
    (out/'COMMENTS.md').write_text('\n'.join(lines)+'\n')
    lines=['# Owner-marked segments — r7','', 'All 256 original marks remain bound to their original polygons. Spatial intersections are context, never an automatic row-count verdict.','']
    for m in marks:
        lines += [f'## {m["page"]}: historical segment {m["segment"]}', '',f'Owner mark: **{m["mark"]}**',f'{m["r7_observation"]}',f'New missing found-ink pixels: {m["lost_pixels"]}. Review: {m["review"]}.',f'[Native context]({m["image"]})','']
    (out/'ROWS.md').write_text('\n'.join(lines)+'\n')


def gallery(out,pages):
    changed=[q for q in pages if not q['exact_current_default']]
    text=['<!doctype html><meta charset="utf-8"><title>r7 output differences</title><style>body{font:16px system-ui;margin:25px}img{max-width:100%}</style><h1>Current default vs task 4</h1>',f'<p>{len(changed)} changed pages out of 208. Paddle alone / current default / task 4. Only retained final lines are rendered in the final panel.</p>']
    for q in changed:
        p=q['page'];text.append(f'<h2>{html.escape(p)}</h2><a href="acceptance/{q["comparison"]}"><img src="acceptance/{q["comparison"]}"></a><p>New missing found-ink pixels: {q["lost_pixels"]}.</p>')
        for c in q['required_clusters']:text.append(f'<a href="acceptance/{c["image"]}">Native loss: {c["pixels"]} pixels</a> ')
    (out/'changed.html').write_text('\n'.join(text))


def validate(out):
    pages=read(out/'acceptance/pages.json');comments=read(out/'comments.json');marks=read(out/'owner-marks.json');notes=read(out/'review.json');checks=0;totals=Counter()
    s1=read(out/'source-r1.json');s2=read(out/'source-r2.json');assert s1==s2;checks+=1
    for name,sha in s1['files'].items():assert digest(ROOT/name)==sha and digest(out/'source'/name)==sha;checks+=2
    assert len(pages)==208 and len(comments)==104 and len(marks)==256;checks+=3
    for row in cohort():
        p=row['page'];record=read(out/f'{p}.json');e=read(out/f'{p}.evidence.json');old=read(DEFAULT/f'{p}.evidence.json');rec=next(r for r in pages if r['page']==p)
        assert e['original']==old['original'];assert digest(ROOT/row['path'])==row['sha256'];assert record['unit']=='line' and record['image_size']==row['image_size'];checks+=3
        for q in record['items']:
            poly=np.asarray(q['polygon']);assert poly.ndim==2 and poly.shape[1]==2 and len(poly)>=3 and np.isfinite(poly).all();assert (poly>=0).all() and (poly[:,0]<=row['image_size'][0]).all() and (poly[:,1]<=row['image_size'][1]).all();assert q.get('baseline') is None and not q.get('discounted') and Polygon(poly).is_valid;checks+=3
        if not row['parked']:
            sources={i for q in record['items']+e.get('removed',[]) for i in q.get('source_ids',[])};assert sources==set(range(len(e['original'])));checks+=1
            c=e['counts'];fields=[e.get('page_field',{}).get(k) or {} for k in ('early_replacement','replacement')];field_delta=sum(len(f.get('replacements',[]))-len(f.get('changed_indices',[])) for f in fields);split=sum(len(q['new'])-1 for q in e['rows']['changes']);dedup=sum(len(q['new'])-1 for q in e['row_ownership']['changes'])
            expected=len(e['original'])+c['q8']+c['curved']+c['columns']-c['back']-c['ornaments']-c['seals']-c['blobs']-c['frames']+c['added']-c['joined_reduction']-c['faint']+field_delta+split+dedup
            assert len(record['items'])==expected,(p,len(record['items']),expected);assert e['row_ownership']['duplicate_pairs_after']==0;checks+=2
        for rep in (1,2):
            t=read(out/f'{p}.r{rep}.json');assert t['source']==s1['key'] and t['counts']==e['counts'] and t['image_sha256']==row['sha256'];checks+=3
        assert not rec['missing_exact_exclusions'] and rec['new_intrusion_pixels']==0 and rec['columns_exact'];checks+=3
        assert next(q for q in notes if q['page']==p)['review']!='pending';checks+=1
        for c in rec['required_clusters']:assert c['review']!='pending';checks+=1
        order=read(out/f'{p}.order.json');assert sorted(q['item_index'] for q in order)==list(range(len(record['items'])));checks+=1
        for ext in ('.jpg','.paddle.jpg'):assert (out/(p+ext)).stat().st_size>0;checks+=1
        totals.update(e['counts'])
    for q in comments:
        assert q['review']!='pending';assert q.get('quote',q.get('owner_comment','')) in (out/'COMMENTS.md').read_text();checks+=2
    for q in marks:assert q['review']!='pending' and (out/q['image']).exists();checks+=2
    links=re.findall(r'\]\(([^)]+)\)',(out/'COMMENTS.md').read_text()+(out/'ROWS.md').read_text());assert all((out/q).exists() for q in links);checks+=len(links)
    receipt=dict(pages=208,repeats=2,checks=checks,counts=dict(totals),comments=104,marks=256,held_out_accessed=False,production_pages_changed=False)
    dump(out/'validation.json',receipt);print(json.dumps(receipt,indent=2))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['build','validate']);ap.add_argument('--version',default='r7');a=ap.parse_args();globals()[a.action](ROOT/'.astra/fast_lines/out/stack'/a.version)

if __name__=='__main__':main()
