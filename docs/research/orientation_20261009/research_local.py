"""Blind local text-axis proposals; uses no manifest ROI until scoring."""
from research_orientation import *
from scipy import ndimage as ndi
def propose(im):
    start=time.perf_counter();small=thumb(im,2000);scale=im.width/small.width;m=ink(small,2000)
    n,l,s,c=cv2.connectedComponentsWithStats(m,8);s=s[1:];c=c[1:]
    eligible=(s[:,4]>=8)&(s[:,2]>=2)&(s[:,3]>=2)&(s[:,2]<150)&(s[:,3]<150);s=s[eligible];c=c[eligible]
    h=float(np.median(np.maximum(s[:,2],s[:,3]))) if len(s) else 10.
    body=(np.maximum(s[:,2],s[:,3])>.65*h)&(np.maximum(s[:,2],s[:,3])<2*h)&(s[:,4]>.15*h*h);s=s[body];c=c[body]
    if len(c)<3:return [],time.perf_counter()-start
    ds,js=cKDTree(c).query(c,k=min(12,len(c)));vertical=np.zeros(len(c),bool)
    for i,ids in enumerate(js):
        dd=c[np.atleast_1d(ids)]-c[i];dx=abs(dd[:,0]);dy=abs(dd[:,1]);hx=dx[(dy<.35*h)&(dx>.4*h)&(dx<5*h)];vy=dy[(dx<.35*h)&(dy>.4*h)&(dy<5*h)]
        hv=h/float(hx.min()) if len(hx) else 0.;vv=h/float(vy.min()) if len(vy) else 0.
        vertical[i]=vv>1.25*hv and vv>0
    ids=np.flatnonzero(vertical);pts=c[ids];parent=list(range(len(ids)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    if len(pts):
        for a,b in cKDTree(pts).query_pairs(3*h):
            if abs(pts[a,0]-pts[b,0])<.8*h and abs(pts[a,1]-pts[b,1])<3*h:parent[find(b)]=find(a)
    groups={}
    for i in range(len(ids)):groups.setdefault(find(i),[]).append(ids[i])
    boxes=[]
    for members in groups.values():
        if len(members)<3:continue
        q=s[members];box=[int(q[:,0].min()),int(q[:,1].min()),int((q[:,0]+q[:,2]).max()),int((q[:,1]+q[:,3]).max())]
        if box[3]-box[1]<1.5*(box[2]-box[0]):continue
        boxes.append(dict(box=[x*scale for x in box],components=len(members),axis_cw=90))
    return boxes,time.perf_counter()-start
def iou(a,b):
    area=lambda a:max(0,a[2]-a[0])*max(0,a[3]-a[1]);inter=area([max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]);return inter/max(1,area(a)+area(b)-inter)
def main():
    out=[]
    for case in load('testset/manifest.json')['cases']:
        if case['kind']!='composite':continue
        im=Image.open(ROOT/case['path']).convert('RGB');boxes,sec=propose(im)
        best=max((iou(x['box'],case['roi']) for x in boxes),default=0.)
        # Additional ink-coverage diagnostic: many valid chains in a block need
        # not form one large proposal. This threshold mask is not word truth.
        mask=ink(im,2000)>0;sc=mask.shape[1]/im.width;covered=np.zeros_like(mask)
        for p in boxes:
            l,t,r,b=[round(v*sc) for v in p['box']];covered[t:b,l:r]=True
        l,t,r,b=[round(v*sc) for v in case['roi']];den=mask[t:b,l:r].sum();coverage=float((mask[t:b,l:r]&covered[t:b,l:r]).sum()/max(1,den))
        out.append(dict(id=case['id'],roi_unit=case['roi_unit'],truth_cw=case['roi_truth_cw'],seconds=sec,proposals=boxes,best_iou=best,detected=best>=.3,inserted_threshold_ink_covered=coverage,outside_roi=sum(iou(x['box'],case['roi'])==0 for x in boxes)))
        view=thumb(im,1200);d=ImageDraw.Draw(view);sc=view.width/im.width
        for p in boxes:d.rectangle([x*sc for x in p['box']],outline='red',width=2)
        d.rectangle([x*sc for x in case['roi']],outline='blue',width=2);view.save(ROOT/'testset'/f"{case['id']}_local.jpg")
        print(case['id'],len(boxes),best,sec,flush=True)
    save('local_results.json',dict(method='component-local nearest-neighbour axis votes, vertical chains >=3 bodies; IoU>=.3 oracle only in evaluator',cases=out))
if __name__=='__main__':main()
