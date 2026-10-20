"""Offline native geometry review and ordered, one-to-one row correspondence.

No runtime imports this file. Matching is a diagnostic of crop support, not a
font/ownership certificate. Unmatched rows on both sides are retained.
"""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from ..shared.geometry import height_proxy
from ..shared.contracts import bbox


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')


def centre_at(q,x):
    """Vertical polygon-section midpoint; explicitly NOT a baseline."""
    p=np.asarray(q['polygon']);out=[]
    for xx in np.asarray(x):
        ys=[]
        for a,b in zip(p,np.roll(p,-1,axis=0)):
            if min(a[0],b[0])<=xx<=max(a[0],b[0]) and a[0]!=b[0]:
                ys.append(a[1]+(xx-a[0])*(b[1]-a[1])/(b[0]-a[0]))
        out.append((min(ys)+max(ys))/2 if ys else np.nan)
    return np.asarray(out)


def correspond(reference,items):
    groups=defaultdict(list)
    for i,r in enumerate(reference):
        if not r['discounted']:groups[(r['page_side'],r['column_id'],r['block_id'])].append((i,r))
    domains={g:[min(r['x0'] for _,r in rs),min(min(r['top']) for _,r in rs),max(r['x1'] for _,r in rs),max(max(r['bottom']) for _,r in rs)] for g,rs in groups.items()}
    assigned=defaultdict(list);outside=[];ambiguous=[]
    for i,q in enumerate(items):
        b=bbox(q);cy=(b[1]+b[3])/2;hits=[]
        for g,(a,y,c,z) in domains.items():
            width=max(0,min(b[2],c)-max(b[0],a))
            if width and y<=cy<=z:hits.append((width,g))
        if not hits:outside.append(i);continue
        hits.sort(reverse=True);assigned[hits[0][1]].append((i,q))
        if len(hits)>1:ambiguous.append(dict(item=i,domains=[list(g) for _,g in hits],assigned=list(hits[0][1]),reason='largest horizontal overlap; possible mixed domain, requires visual review'))
    matches=[];unref=[];unfast=list(outside)
    for g,rs in groups.items():
        rs=sorted(rs,key=lambda t:float(np.median(t[1]['baseline'])));qs=sorted(assigned[g],key=lambda t:sum(bbox(t[1])[1::2])/2);n,m=len(rs),len(qs)
        cost=np.full((n,m),np.inf);details={}
        for j,(rid,r) in enumerate(rs):
            for k,(qid,q) in enumerate(qs):
                b=bbox(q);a=max(r['x0'],b[0]);z=min(r['x1']-1,b[2])
                if z<=a:continue
                x=np.linspace(a,z,19);cy=centre_at(q,x);rx=np.arange(r['x0'],r['x1']);body=(np.asarray(r['baseline'])+np.asarray(r['meanline']))/2;error=cy-np.interp(x,rx,body)
                if not np.isfinite(error).all():continue
                h=max(1,float(r['xheight']));dx=[b[0]-r['x0'],b[2]-r['x1']]
                # 2h is an OFFLINE matching deletion cost, not a runtime or
                # correctness tolerance. All numerical pairings need raw review.
                cost[j,k]=float(np.median(abs(error))/h)
                details[j,k]=dict(reference=rid,item=qid,domain=list(g),body_centre_error_px_median=float(np.median(abs(error))),body_centre_error_px_max=float(max(abs(error))),body_centre_error_h_median=float(np.median(abs(error))/h),endpoint_dx_px=dx,endpoint_dx_h=[d/h for d in dx],semantic_guide_error=None,guide_status='fast polygon midpoint is not a font guide; guides unavailable',reference_borrowed=r.get('borrowed',[]))
        dp=np.full((n+1,m+1),np.inf);dp[:,0]=np.arange(n+1)*2;dp[0,:]=np.arange(m+1)*2;back=np.zeros((n+1,m+1),np.int8)
        for j in range(1,n+1):
            for k in range(1,m+1):
                options=[dp[j-1,k-1]+cost[j-1,k-1],dp[j-1,k]+2,dp[j,k-1]+2];v=int(np.argmin(options));dp[j,k]=options[v];back[j,k]=v
        j,k=n,m
        while j or k:
            v=back[j,k] if j and k else (1 if j else 2)
            if v==0:matches.append(details[j-1,k-1]);j-=1;k-=1
            elif v==1:unref.append(rs[j-1][0]);j-=1
            else:unfast.append(qs[k-1][0]);k-=1
    assert len({r['reference'] for r in matches})==len(matches)==len({r['item'] for r in matches})
    return dict(matches=matches,unmatched_reference=sorted(unref),unmatched_fast=sorted(unfast),domain_ambiguity=ambiguous,reference_active=sum(not r['discounted'] for r in reference),fast_items=len(items),method='Ordered one-to-one DP within reference leaf/column/block; polygon-section midpoint vs reference body centre; gap cost 2h. Diagnostic only. No multiple-to-one matches. Reference domain errors remain possible.')


def draw_crop(gray,items,bounds,title,historical=None,reference=None):
    a,b,c,d=map(int,bounds);raw=Image.fromarray(gray[b:d,a:c]).convert('RGB');im=Image.new('RGB',(raw.width,2*raw.height+48),'white');im.paste(raw,(0,24));tile=raw.copy();dr=ImageDraw.Draw(tile)
    for i,q in enumerate(items):
        if q.get('discounted'):continue
        bb=bbox(q)
        if bb[2]<a or bb[0]>c or bb[3]<b or bb[1]>d:continue
        pp=[(x-a,y-b) for x,y in q['polygon']];dr.line(pp+[pp[0]],fill=(0,140,35),width=1)
    if historical is not None:
        pp=[(x-a,y-b) for x,y in historical];dr.line(pp+[pp[0]],fill=(210,130,0),width=1)
    if reference is not None:
        r=reference;xx=np.arange(r['x0'],r['x1']);cy=(np.asarray(r['baseline'])+np.asarray(r['meanline']))/2
        dr.line([(float(x-a),float(y-b)) for x,y in zip(xx,cy)],fill='blue',width=1)
    im.paste(tile,(0,48+raw.height));dr=ImageDraw.Draw(im);dr.text((3,3),title+' | RAW',fill='black');dr.text((3,27+raw.height),'final green; historical mark amber / reference body centre blue (not fast guides)',fill='black');return im


def run(inputs,slow,baseline,candidate,marks,out):
    inputs,slow,baseline,candidate,marks,out=map(Path,(inputs,slow,baseline,candidate,marks,out));out.mkdir(exist_ok=True,parents=True);(out/'marks').mkdir(exist_ok=True);(out/'pages').mkdir(exist_ok=True)
    rows=json.loads(inputs.read_text())['pages'];allmarks=json.loads(marks.read_text());records=[];markrecords=[];sheets=[]
    for row in rows:
        page=row['page'];gray=cv2.imread(row['path'],0);assert sha(row['path'])==row['sha256'];r=json.loads((slow/page/'reference.json').read_text());assert r['input_sha256']==row['sha256'];a=json.loads((baseline/f'{page}.json').read_text());v=json.loads((candidate/f'{page}.json').read_text());h=height_proxy(a['original'],gray.shape[::-1]);match=correspond(r['rows'],v['items']);dump(out/'pages'/f'{page}.matches.json',match)
        local=[m for m in allmarks if m['page']==page]
        for m in local:
            p=np.asarray(m['polygon']);lo=np.maximum(0,np.floor(p.min(0)-h)).astype(int);hi=np.minimum(gray.shape[::-1],np.ceil(p.max(0)+h)).astype(int);b=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])];name=f'{page}.mark-{m["segment"]}.png';im=draw_crop(gray,v['items'],b,f'{page} owner #{m["segment"]}: {m["mark"]}',historical=m['polygon']);im.save(out/'marks'/name)
            # Native per-mark files are preserved; review sheets only arrange
            # them, with at most 1200px width (not full-page thumbnails).
            im.thumbnail((1200,900));sheets.append((name,im));markrecords.append(dict(m,r8_03_i1=dict(image='marks/'+name,bounds=b,exported_items_equal=a['items']==v['items'],status='pending native inspection')))
        active=[(i,q) for i,q in enumerate(r['rows']) if not q['discounted']];choose=np.unique(np.linspace(0,len(active)-1,min(4,len(active))).round().astype(int));pageimgs=[]
        for j in choose:
            i,q=active[j];b=[max(0,int(q['x0']-h)),max(0,int(min(q['top'])-h)),min(gray.shape[1],int(q['x1']+h)),min(gray.shape[0],int(max(q['bottom'])+h))];im=draw_crop(gray,v['items'],b,f'{page} slow row {i}',reference=q);name=f'{page}.reference-{i}.png';im.save(out/'pages'/name);pageimgs.append('pages/'+name)
        records.append(dict(page=page,input_sha256=row['sha256'],reference_sha256=sha(slow/page/'reference.json'),baseline_sha256=sha(baseline/f'{page}.json'),candidate_sha256=sha(candidate/f'{page}.json'),exact_items=a['items']==v['items'],match_file='pages/'+page+'.matches.json',images=pageimgs,reference_active=match['reference_active'],fast_items=match['fast_items'],matched=len(match['matches']),unmatched_reference=len(match['unmatched_reference']),unmatched_fast=len(match['unmatched_fast']),status='pending native inspection'))
        print(page,len(local),len(match['matches']),len(match['unmatched_reference']),len(match['unmatched_fast']),flush=True)
    for start in range(0,len(sheets),4):
        subset=sheets[start:start+4];im=Image.new('RGB',(max(x.width for _,x in subset),sum(x.height for _,x in subset)+20*len(subset)),'white');y=0
        for name,x in subset:ImageDraw.Draw(im).text((3,y),name,fill='black');im.paste(x,(0,y+20));y+=x.height+20
        im.save(out/f'marks-sheet-{start//4:02d}.jpg',quality=94)
    dump(out/'pilot-pages.json',records);dump(out/'pilot-marks.json',markrecords);dump(out/'receipt.json',dict(inputs_sha256=sha(inputs),marks_sha256=sha(marks),source_sha256=sha(__file__),pages=len(records),marks=len(markrecords),matched=sum(r['matched'] for r in records),unmatched_reference=sum(r['unmatched_reference'] for r in records),unmatched_fast=sum(r['unmatched_fast'] for r in records),reference_source='Unmodified pixel-seeded saved segment_page output; no Paddle box substitution. Known slow failures remain. Crop-support comparison does not validate font guides.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('slow');p.add_argument('baseline');p.add_argument('candidate');p.add_argument('marks');p.add_argument('out');a=p.parse_args();run(**vars(a))
