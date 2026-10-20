"""Bound F2 image storage; full native Google rasters are never recompressed."""
from f2lib import *
def main():
 changed={};before=0;after=0
 for p in (BASE/'bulk/review').glob('*.jpg'):
  before+=p.stat().st_size
  with Image.open(p) as im:
   b=io.BytesIO();im.save(b,format='JPEG',quality=75,optimize=True)
  data=b.getvalue()
  if len(data)<p.stat().st_size:
   tmp=p.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(p)
  after+=p.stat().st_size;changed[str(p.relative_to(BASE))]=sha(p)
 # Update custody of the explicitly lossy review derivative. Native image hashes
 # and native line-crop hashes are untouched.
 for folder in ['pages','machine','verify-pages']:
  for p in (BASE/'receipts'/folder).glob('*.json'):
   r=json.loads(p.read_text());path=r.get('review_image')
   if path in changed:r['review_sha256']=changed[path];r['review_jpeg_quality']=75;write(p,r)
 for p in BASE.glob('pages*.jsonl'):
  rr=rows(p)
  for r in rr:
   if r.get('review_image') in changed:r['review_sha256']=changed[r['review_image']];r['review_jpeg_quality']=75
  jsonl(p,rr)
 # This provisional blind set is rebuilt only from final pages by handoff.py.
 removed=[]
 for p in (BASE/'blind_pages').glob('*.jpg'):
  removed.append(dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size));p.unlink()
 write(BASE/'receipts/review-storage.json',dict(review_bytes_before=before,review_bytes_after=after,native_rasters_changed=0,review_long_side_cap=1600,review_quality=75,provisional_blind_files_removed=len(removed),provisional_blind_bytes_removed=sum(r['bytes'] for r in removed),rebuild='handoff.py copies final review images in the recorded global shuffle',at=stamp()))
 print('review MB',before/1e6,'->',after/1e6,'provisional blind MB removed',sum(r['bytes'] for r in removed)/1e6)
if __name__=='__main__':main()
