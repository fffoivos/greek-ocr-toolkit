"""Per-segment route audit, owner ledger, full-image and OCR review artifacts."""
import argparse,html,json,re,shutil
from collections import Counter
from pathlib import Path
import cv2,numpy as np
from .round6_rows import ROOT,DEST,BASE,cohort,inputs,draw
from ..shared.geometry import roi
from ..shared.contracts import bbox
from .round6_rows_export import conservation,ocr_crop
from ..shared.geometry_rows import confirmed_partition
from ..shared.timing import dump,summary


def sheets(files,out,prefix,per=6,width=1500,max_height=400):
    order=[]
    for n in range(0,len(files),per):
        images=[]
        for file in files[n:n+per]:
            im=cv2.imread(str(file));assert im is not None,file
            s=min(width/im.shape[1],max_height/im.shape[0],1.)
            im=cv2.resize(im,None,fx=s,fy=s);canvas=np.full((im.shape[0],width,3),255,np.uint8);canvas[:,:im.shape[1]]=im;images.append(canvas)
        path=out/f'{prefix}-{n//per:03d}.jpg';cv2.imwrite(str(path),np.vstack(images));order.append(dict(path=str(path),sources=[str(f) for f in files[n:n+per]]))
    dump(out/(prefix+'-order.json'),order)
    return order


def audit(final,native):
    out=DEST/final;ref=DEST/native;review=out/'review';review.mkdir(exist_ok=True)
    owner=json.load(open(BASE/'owner-marks.json'));ledger=[];totals=Counter();page_summary=[];checks=0;native_images=[];final_images=[];ocr_images=[];owner_images=[]
    for row in cohort():
        p=row['page'];gray,old=inputs(row);record=json.load(open(out/(p+'.json')));e=json.load(open(out/(p+'.evidence.json')));new=record['items']
        base_e=json.load(open(BASE/(p+'.evidence.json')));assert e.get('removed',[])==base_e.get('removed',[])
        assert all(e['counts'][k]==v for k,v in base_e['counts'].items());checks+=2
        state=e.get('rows',{});changes=state.get('changes',[]);check=conservation(old,new,changes);checks+=check['checks']
        slow=json.load(open(ref/(p+'.slow.json')));fast=json.load(open(ref/(p+'.explicit.json')))
        ss={r['line']:r for r in slow['records']};ff={r['line']:r for r in fast['records']};runtime={r['line']:r for r in state.get('records',[])}
        scouted=set(state.get('scout',{}).get('candidates',[]));changed={c['line'] for c in changes};comparisons=[]
        for i,q in enumerate(old):
            a,ar=confirmed_partition(q,ss[i]);b,br=confirmed_partition(q,ff[i]);r=runtime.get(i,{})
            rec=dict(line=i,slow_children=len(a),reduced_children=len(b),scout=i in scouted,installed=i in changed,
                     reason=r.get('reason','parked orientation' if row['parked'] else 'no broad separated body bands'),
                     native_reason=ar,reduced_reason=br,orientation_ambiguous=ss[i].get('orientation_ambiguous',False))
            if a and b:
                errors=[]
                for v in [v for v in ss[i]['valleys'] if v['accepted']]:
                    x,y=np.asarray(v['path']).T;others=[v for v in ff[i]['valleys'] if v['accepted']]
                    if others:
                        delta=min((abs(y-np.interp(x,*np.asarray(t['path']).T))/slow['height'] for t in others),key=lambda z:np.median(z));errors.extend(delta.tolist())
                if errors:rec['cut_difference_h']=dict(median=float(np.median(errors)),max=float(max(errors)))
            comparisons.append(rec);checks+=1
            totals['segments']+=1;totals['native_positive']+=bool(a);totals['reduced_positive']+=bool(b);totals['scouted']+=i in scouted;totals['split']+=i in changed
            totals['native_missed_by_scout']+=bool(a) and i not in scouted and not row['parked']
            totals['native_missed_by_window']+=bool(a) and i in scouted and i not in changed and not row['parked']
            totals['route1_different_decision']+=bool(a)!=bool(b)
        dump(out/(p+'.comparison.json'),dict(page=p,segments=comparisons))
        small=cv2.cvtColor(cv2.resize(gray,None,fx=1500/gray.shape[1],fy=1500/gray.shape[1]),cv2.COLOR_GRAY2BGR);s=1500/gray.shape[1]
        for i,q in enumerate(old):
            cv2.polylines(small,[np.rint(np.asarray(q['polygon'])*s).astype(int)],True,(0,140,230) if i in scouted else (180,180,180),1)
        for rec in state.get('scout',{}).get('records',[]):
            for x,y in rec['peaks']:cv2.circle(small,(round(x*s),round(y*s)),2,(0,0,220),-1)
        cv2.imwrite(str(out/(p+'.scout.jpg')),small)
        # Separate comparison panels keep both physical measurements legible.
        panels=[]
        for route,title in [('slow','native bodies and valleys'),('explicit','reduced explicit route 1')]:
            im=cv2.imread(str(ref/(p+'.'+route+'.jpg')));im=cv2.resize(im,(1000,round(im.shape[0]*1000/im.shape[1])));bar=np.full((30,1000,3),255,np.uint8);cv2.putText(bar,title,(4,20),0,.6,(0,0,0),1);panels.append(np.vstack([bar,im]))
        cv2.imwrite(str(out/(p+'.routes.jpg')),np.hstack(panels));native_images.append(ref/(p+'.slow.jpg'));final_images.append(out/(p+'.jpg'))
        order=json.load(open(out/(p+'.order.json')));number={q['item_index']:q['number'] for q in order}
        lookup={json.dumps(q['polygon']):i for i,q in enumerate(old)};source_to_final={};pos=0
        for i,q in enumerate(old):
            count=len(next(c for c in changes if c['line']==i)['new']) if i in changed else 1
            source_to_final[i]=list(range(pos,pos+count));pos+=count
        for mark in owner:
            if mark['page']!=p:continue
            i=lookup[json.dumps(mark['polygon'])];indices=source_to_final[i];touched=i in changed
            crop=out/f'{p}.owner-{mark["segment"]}.jpg';ocr_crop(gray,old[i],[new[j] for j in indices] if touched else [],crop,f'{p} R5 {mark["segment"]} owner {mark["mark"]}');owner_images.append(crop)
            # Full-row resolution is judged from the crops, not inferred merely
            # because a cut happened. A child can retain another clipped row.
            outcome='one internal gap partitioned; children visually reviewed, but no claim that every child holds only one row' if touched else 'identical segment retained; '+comparisons[i]['reason']
            ledger.append(dict(mark,taskB_index=i,taskB_touched=touched,final_indices=indices,final_numbers=[number[j] for j in indices],outcome_B=outcome,
                               curvature_book=any(k in p for k in ('s2-3229200bf47ca465a42d','s2-49598b2e848ab1f0ee1e','s2-86865c33eef5932c013b')),image=crop.name))
        ocr_images.extend(out/f'{p}.split-{c["line"]}.jpg' for c in changes)
        native_only=[r['line'] for r in comparisons if r['slow_children'] and not r['installed'] and not row['parked']]
        page_summary.append(dict(page=p,group=row['group'],old=len(old),new=len(new),partitions=len(changes),native_only=native_only,scout_candidates=len(scouted),vector=check))
    dump(out/'owner-marks.json',ledger);dump(out/'pages.json',page_summary);dump(out/'comparison-summary.json',dict(totals))
    # Every original comment stays verbatim; B conserves the vector footprint.
    # Integer rasterization has a separate boundary audit in details().
    comments=(BASE/'COMMENTS.md').read_text();comments=comments.replace('# Owner comments — task A and the retained R5 result','# Owner comments — retained A result plus task B')
    for delta in BASE.glob('*.delta.json'):
        shutil.copyfile(delta,out/delta.name)
    comments+='\n\n# Task B: vertical partitions only\n\nB partitions existing vector footprints; it does not recover endpoints or remove segments. Integer rasterization changes some one-pixel outer-boundary samples; see raster-audit.json. The 73 verbatim comments above retain their A/R5 status. R4 numbers are not remapped to the R5 owner-row indices. See owner-marks.json for every marked segment.\n\n'
    for p in page_summary:
        if p['partitions']:comments+=f"- `{p['page']}`: {p['partitions']} existing polygons partitioned into rows/fragments; no new endpoint, faintness, ornament, missed-line or column-boundary fix is claimed. [Numbered result]({p['page']}.jpg).\n"
    (out/'COMMENTS.md').write_text(comments)
    timing=[]
    for repeat in (1,2):
        recs=[json.load(open(out/f'{r["page"]}.r{repeat}.json')) for r in cohort()]
        for group in ('agreement','discrepancy','all'):
            part=[r for r in recs if group=='all' or r['group']==group]
            for stage in ('rows_s','rows_scout_s','rows_native_s','correction_s','total_s'):
                vals=[r.get(stage,r['stages'].get(stage,0))*1000 for r in part]
                timing.append(dict(repeat=repeat,group=group,stage=stage,**summary(vals)))
    dump(out/'timings.json',timing)
    sets=dict(native=sheets(native_images,review,'native',6,1500,500),final=sheets(final_images,review,'final',6,1500,500),
              ocr=sheets(ocr_images,review,'ocr',4,1500,600),owner=sheets(owner_images,review,'owner',8,1500,300))
    dump(review/'inventory.json',sets)
    lines=['<!doctype html><meta charset="utf-8"><title>Round 6 B — rows</title><style>body{font:16px system-ui;max-width:1400px;margin:30px auto}td{padding:8px}img{max-width:380px}table{border-collapse:collapse}tr{border-bottom:1px solid #bbb}</style>',
           '<h1>Rows inside OCR segments</h1><p>Native bodies, route 1 at reduced resolution, route 2 scout, and final guarded partitions. Purple: cut; grey: original; blue: unchanged; green: inherited recovery; red: removed by retained ink stages.</p>',
           '<p><a href="COMMENTS.md">Owner comments</a> · <a href="owner-marks.json">All owner-marked rows</a> · <a href="timings.json">Two fresh timing passes</a> · <a href="comparison-summary.json">Route comparison</a></p><table>']
    for p in page_summary:
        key=p['page'];lines.append(f'<tr><td>{html.escape(key)}<br>{p["partitions"]} partitions; {p["scout_candidates"]} nominations<br><a href="{key}.json">detector JSON</a> · <a href="{key}.comparison.json">every segment</a><br><a href="{key}.routes.jpg">native / route 1</a> · <a href="{key}.scout.jpg">route 2</a></td><td><a href="{key}.jpg"><img loading="lazy" src="{key}.jpg"></a></td></tr>')
    lines.append('</table>');(out/'index.html').write_text('\n'.join(lines))
    links=re.findall(r'(?:href|src)="([^"]+)"',(out/'index.html').read_text());assert all((out/f).exists() for f in links);checks+=len(links)
    comment_links=re.findall(r'\]\(([^)]+)\)',comments);assert all((out/f).exists() for f in comment_links);checks+=len(comment_links)
    dump(out/'validation.json',dict(checks=checks,pages=len(page_summary),owner_records=len(ledger),marked=sum(m['mark'] is not None for m in ledger),links=len(links),totals=dict(totals)))
    print(dict(totals));print('checks',checks,'owner marks',Counter((m['mark'],m['taskB_touched']) for m in ledger))



def details(final,native):
    """Audit rasterization and expose every route disagreement as a native crop."""
    out=DEST/final;ref=DEST/native;review=out/'review';raster=[];diagnostics=[];matrix=Counter();distances=[];checks=0
    for row in cohort():
        p=row['page'];gray,old=inputs(row);e=json.load(open(out/(p+'.evidence.json')))
        slow=json.load(open(ref/(p+'.slow.json')));fast=json.load(open(ref/(p+'.explicit.json')))
        ss={r['line']:r for r in slow['records']};ff={r['line']:r for r in fast['records']}
        comparisons=json.load(open(out/(p+'.comparison.json')))['segments']
        for q in comparisons:
            matrix[bool(q['slow_children']),bool(q['reduced_children'])]+=1
            if q.get('cut_difference_h'):distances.append(q['cut_difference_h'])
            if bool(q['slow_children'])!=bool(q['reduced_children']) or q['slow_children'] and not q['installed']:
                i=q['line'];a,b,c,d=bbox(old[i]);h=slow['height'];crop=roi([a-h,b-h,c+h,d+h],gray.shape);panels=[]
                for label,record in [('native',ss[i]),('reduced',ff[i])]:
                    f=review/f'{p}.{i}.{label}.jpg';draw(gray,old,dict(records=[record]),f,crop=crop,title=f'{p} A {i} {label}')
                    panels.append(cv2.imread(str(f)))
                path=review/f'{p}.{i}.routes.jpg';cv2.imwrite(str(path),np.vstack(panels))
                diagnostics.append(dict(page=p,**q,image=path.name))
        for c in e.get('rows',{}).get('changes',[]):
            i=c['line'];parent=old[i];a,b,cc,d=roi([*np.asarray(parent['polygon']).min(0)-2,*np.asarray(parent['polygon']).max(0)+3],gray.shape)
            def mask(poly):
                m=np.zeros((d-b,cc-a),np.uint8);cv2.fillPoly(m,[np.rint(np.asarray(poly)-[a,b]).astype(int)],1);return m
            before=mask(parent['polygon']);after=np.zeros_like(before);overlap=np.zeros_like(before)
            for child in c['new']:
                m=mask(child);after|=m;overlap+=m
            changed=before!=after;yy,xx=np.nonzero(changed)
            boundary=cv2.morphologyEx(before,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))
            radius=cv2.distanceTransform((boundary==0).astype(np.uint8),cv2.DIST_L2,5)
            local=gray[b:d,a:cc];threshold,_=cv2.threshold(local,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            raster.append(dict(page=p,line=i,lost_pixels=int(np.sum((before>0)&(after==0))),gained_pixels=int(np.sum((before==0)&(after>0))),
                               changed_otsu_ink=int(np.sum(changed&(local<threshold))),max_distance_from_parent_boundary=float(radius[changed].max()) if changed.any() else 0.,
                               shared_cut_pixels=int(np.sum(overlap>1))))
            checks+=1
    dump(out/'raster-audit.json',raster);dump(out/'route-disagreements.json',diagnostics)
    sheets([review/d['image'] for d in diagnostics],review,'route-disagreements',4,1500,600)
    decoded=[]
    for root in (out,ref):
        for file in root.glob('*.jpg'):
            assert cv2.imread(str(file)) is not None,file;decoded.append(str(file));checks+=1
    receipts=[]
    for row in cohort():
        p=row['page'];a=json.load(open(out/(p+'.r1.json')));b=json.load(open(out/(p+'.r2.json')))
        assert a['source']==b['source'] and a['counts']==b['counts'] and a['image_sha256']==b['image_sha256'];checks+=3
        receipts.extend([dict(a,repeat=1),dict(b,repeat=2)])
    # The original manifest separates 80 discrepancy pages and 21 additional
    # discrepancy pages. Include both in the complete discrepancy timing set.
    timing=[]
    for repeat in (1,2):
        part=[r for r in receipts if r['repeat']==repeat and r['group'] in ('discrepancy','discrepancy_extra')]
        for stage in ('rows_s','rows_scout_s','rows_native_s','correction_s','total_s'):
            vals=[r.get(stage,r['stages'].get(stage,0))*1000 for r in part]
            timing.append(dict(repeat=repeat,group='all_discrepancy',stage=stage,**summary(vals)))
    dump(out/'discrepancy-timings.json',timing)
    dump(out/'detail-validation.json',dict(checks=checks,decoded_images=len(decoded),fresh_receipts=416,runtime_source_equal=True,
         route_matrix=[dict(native=a,reduced=b,count=v) for (a,b),v in sorted(matrix.items())],
         median_segment_cut_difference_h=float(np.median([d['median'] for d in distances])),max_cut_difference_h=max(d['max'] for d in distances),
         raster_totals={k:sum(r[k] for r in raster) for k in ('lost_pixels','gained_pixels','changed_otsu_ink','shared_cut_pixels')},
         max_raster_boundary_distance=max(r['max_distance_from_parent_boundary'] for r in raster)))
    print('detail checks',checks,'route diagnostics',len(diagnostics))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('final');p.add_argument('--native',default='native-final-v16');p.add_argument('--details',action='store_true');a=p.parse_args();(details if a.details else audit)(a.final,a.native)
