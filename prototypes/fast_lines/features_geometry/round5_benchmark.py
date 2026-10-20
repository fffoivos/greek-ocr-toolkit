"""Fresh public Stack benchmark for the explicitly supplied 195+5 cohort.

No detector result is reused in the measured path. Exporting/numbering is outside
latency. Each receipt is append-only; repeat two validates reverse-order identity.
"""
import argparse,json
from pathlib import Path
from time import perf_counter
import cv2,numpy as np
from .round5_data import rows,load,DEST,ROOT
from ..stack.pipeline import Stack
from ..evidence.__main__ import signature
from ..shared.review import detector_record
from ..shared.timing import dump
from ..shared.contracts import bbox


def reading_order(items,columns=None):
    """Geometric XY display order; spanning headings precede separate columns.

    Small erosion is ONLY for display ordering of pieces sharing a cut edge.
    The detector polygons, ancestry and returned list order are untouched.
    """
    boxes=np.array([bbox(q) for q in items]).reshape(-1,4)
    def order(ids):
        if len(ids)<2:return ids
        bs=boxes[ids];h=float(np.median(bs[:,3]-bs[:,1]));gaps=[]
        for axis in (0,1):
            intervals=sorted((b[axis]+(.12*h if axis==0 else 0),b[axis+2]-(.12*h if axis==0 else 0)) for b in bs)
            edge=intervals[0][1]
            for lo,hi in intervals[1:]:
                if lo-edge>(.1*h if axis==0 else 1.5*h):gaps.append((axis,lo-edge,(lo+edge)/2))
                edge=max(edge,hi)
        for axis,_,cut in sorted(gaps,key=lambda q:(q[0],-q[1])):
            left=[i for i in ids if (boxes[i,axis]+boxes[i,axis+2])/2<cut];right=[i for i in ids if i not in left]
            if left and right:return order(left)+order(right)
        return sorted(ids,key=lambda i:((boxes[i,1]+boxes[i,3])/2,boxes[i,0]))
    def ruled_order(ids,rules):
        for k,r in enumerate(rules):
            path=np.asarray(r['path']);middle=[];above=[];below=[]
            for i in ids:
                cy=(boxes[i,1]+boxes[i,3])/2
                (above if cy<r['y0'] else below if cy>r['y1'] else middle).append(i)
            left=[i for i in middle if (boxes[i,0]+boxes[i,2])/2<np.interp((boxes[i,1]+boxes[i,3])/2,path[:,1],path[:,0])]
            right=[i for i in middle if i not in left]
            if not left or not right:continue
            remaining=rules[:k]+rules[k+1:]
            return sum((ruled_order(part,remaining) for part in [above,left,right,below]),[])
        return order(ids)
    rules=sorted([r['rule'] for r in (columns or {}).get('rules',[]) if r['accepted']],key=lambda r:-(r['y1']-r['y0']))
    return ruled_order(list(range(len(items))),rules)


def render(gray,result,path):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);original=result['original'];polys=[q['polygon'] for q in original]
    def draw(q,c,w=1):
        if not q.get('discounted'):cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,c,w,cv2.LINE_AA)
    for q in original:draw(q,(170,170,170))
    for q in result.get('removed',[]):draw(q,(0,0,220),2)
    active=[q for q in result['items'] if not q.get('discounted')]
    ordered=reading_order(active,(result.get('geometry') or {}).get('columns'))
    labels=[]
    for rank,i in enumerate(ordered,1):
        q=active[i];new=q.get('type_slot') is not None or q in result.get('added',[])
        color=(180,0,180) if q.get('row_partition') else ((0,155,0) if new else ((220,60,20) if q['polygon'] in polys else (180,0,180)))
        draw(q,color,2);a,b,c,d=bbox(q);x=int(a+min(12,(c-a)/4));y=int((b+d)/2)
        labels.append((rank,x,y,color))
    sc=min(1,1700/im.shape[1]);im=cv2.resize(im,None,fx=sc,fy=sc)
    # Display labels have a fixed readable size, independent of scan DPI.
    # This affects only export drawing, never detector geometry or timing.
    for rank,x,y,color in labels:
        point=(round(x*sc),round(y*sc))
        cv2.putText(im,str(rank),point,cv2.FONT_HERSHEY_SIMPLEX,.48,(255,255,255),3,cv2.LINE_AA)
        cv2.putText(im,str(rank),point,cv2.FONT_HERSHEY_SIMPLEX,.48,color,1,cv2.LINE_AA)
    cv2.imwrite(str(path),im,[cv2.IMWRITE_JPEG_QUALITY,90])
    return [dict(number=k+1,item_index=i) for k,i in enumerate(ordered)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='composed-v1');ap.add_argument('--repeat',type=int,default=1);ap.add_argument('--pages',nargs='+');a=ap.parse_args()
    out=DEST/a.version;out.mkdir(parents=True,exist_ok=True);rr=rows()
    if a.pages:rr=[r for r in rr if any(k in r['page'] for k in a.pages)]
    if a.repeat%2==0:rr=list(reversed(rr))
    key,files=signature();dump(out/f'source-r{a.repeat}.json',dict(key=key,files=files))
    stack=Stack();stack.detector.infer(cv2.imread(str(ROOT/rr[0]['path']),0))
    for row in rr:
        p=row['page'];receipt=out/f'{p}.r{a.repeat}.json'
        if receipt.exists():raise RuntimeError('Receipt already exists '+str(receipt))
        result=stack(ROOT/row['path'],parked=row['parked']);gray,old,_=load(row)
        assert result['original']==old['original'],(p,'fresh Paddle identity')
        record=detector_record(row,result['items'],result['timing']['total_s'])
        target=out/(p+'.json')
        if target.exists():assert json.load(open(target))['items']==record['items'],(p,'fresh repeat identity')
        else:
            dump(target,record);dump(out/(p+'.evidence.json'),{k:v for k,v in result.items() if k!='items'})
            order=render(gray,result,out/(p+'.jpg'));dump(out/(p+'.order.json'),order)
        dump(receipt,dict(page=p,group=row['group'],direction=row['direction'],image_sha256=row['sha256'],source=key,
             counts=result['counts'],stages=result['stages'],**result['timing']))
        print(p,result['counts'],round(result['timing']['correction_s']*1000,2),flush=True)
    assert signature()[0]==key,'Sources changed during run'

if __name__=='__main__':main()
