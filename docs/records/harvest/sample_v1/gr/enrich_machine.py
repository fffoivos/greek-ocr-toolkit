"""Additional suspicion flags from the existing page detector, without re-OCR."""
from f2lib import *
import gzip,statistics
def main():
 for manifest in BASE.glob('pages_*.jsonl'):
  for p in rows(manifest):
   path=BASE/'receipts/machine'/(p['id']+'.json')
   if not path.exists():continue
   r=json.loads(path.read_text());cache=BASE/'cache/g1b'/r['id']/'detector.json.gz'
   if not cache.exists():continue
   d=json.loads(gzip.decompress(cache.read_bytes()));rr=d.get('rows',[]);xh=np.array([x['xheight'] for x in rr if x.get('xheight',0)>0]);residual=[]
   for x in rr:
    y=np.asarray(x['baseline']);n=len(y)
    if n<100:continue
    xx=np.arange(n);fit=np.polyfit(xx,y,1);residual.append(float(np.std(y-np.polyval(fit,xx)))/max(1,x['xheight']))
   cv=float(xh.std()/max(1,xh.mean())) if len(xh) else None;irregular=float(statistics.median(residual)) if residual else None
   suspicion=bool(len(rr)>=5 and cv is not None and irregular is not None and cv>.55 and irregular>.30)
   r['machine'].update(handwriting_suspicion=suspicion,handwriting_test=dict(method='high row xheight variation AND high detrended baseline irregularity; suspicion only, not a handwriting classifier',xheight_cv=cv,median_baseline_residual_xh=irregular,xheight_cv_threshold=.55,baseline_residual_threshold=.30,conclusive=False),cover_suspicion=bool(r['role']=='band' and len(rr)<=12),plate_suspicion=bool(len(rr)<5 and r['machine'].get('ink_fraction',0)>.01))
   write(path,r)
 print('enriched suspicion fields; read eligibility unchanged')
if __name__=='__main__':main()
