"""Distinguish padded M35 feature masks from exact clipped export-crop support."""
import json,hashlib
import cv2,numpy as np
from .r8_ink02_i2 import O,dump,sha,roi,bbox,crop_mask
from .r8_ink02_i2_panels import stack,label_image,bar

def run():
 cases=json.loads((O/'OBSERVATION_COMPARISON.json').read_text());ledger=json.loads((O/'M35_REMOVALS.json').read_text());by={r['id']:r for r in ledger['records']};reviews=json.loads((O/'ADJUDICATION.json').read_text());receipts=[];pages={}
 for r in cases:
  page=r['page']
  if page not in pages:
   data=json.loads((O/'audit'/(page+'.json')).read_text());gray=cv2.imread(data['input']['path'],0);coverage=np.zeros(gray.shape,np.uint16)
   for q in data['final_items']:
    a,b,c,d=roi(bbox(q),gray.shape);coverage[b:d,a:c]+=crop_mask((d-b,c-a),q,(a,b))
   pages[page]=(gray,coverage)
  gray,coverage=pages[page];q=r['actual_item'];a,b,c,d=r['geometry']['roi'];m=crop_mask((d-b,c-a),q,(a,b));assert hashlib.sha256(m.tobytes()).hexdigest()==r['geometry']['mask_sha256']
  x,y,z,w=r['context_roi'];context=gray[y:w,x:z];actual=np.zeros(context.shape,np.uint8);actual[b-y:d-y,a-x:c-x]=m;feature=crop_mask(context.shape,q,(x,y));assert np.all(actual<=feature),r['id']
  present=coverage[b:d,a:c]>0;raw=gray[b:d,a:c];metrics=dict(mask_pixels=int(m.sum()),mask_pixels_still_in_final=int(((m>0)&present).sum()),missing_mask_pixels=int(((m>0)&~present).sum()),raw_lt200_missing=int(((raw<200)&(m>0)&~present).sum()),raw_lt200_retained=int(((raw<200)&(m>0)&present).sum()),audit_threshold='raw<200 diagnostic only, not certified ink/source',scope='official clipped native ROI crop_mask for the would-be removed strip; padded feature-domain mask is separate')
  overlay=cv2.cvtColor(context,cv2.COLOR_GRAY2BGR);cv2.drawContours(overlay,cv2.findContours(actual,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0],-1,(0,0,255),1)
  target=O/'actual_masks'/f"{r['panel_index']:03}.png";target.parent.mkdir(exist_ok=True);cv2.imwrite(str(target),stack([bar(max(900,context.shape[1]),f"{r['panel_index']:03} {page} {r['id']} | clipped removed crop ROI {a},{b},{c},{d}"),label_image(context,'ORIGINAL native context',1),label_image(overlay,'RED: actual clipped crop_mask of would-be removed strip',1),label_image(actual*255,'BINARY actual clipped crop_mask; padded M35 feature domain is separate',1)]))
  old=r['coverage'];r['padded_M35_feature_coverage']=old;r['coverage']=metrics;r['actual_mask_file']=str(target.relative_to(O));by[r['id']].update(coverage=metrics,padded_M35_feature_coverage=old,actual_mask_file=r['actual_mask_file']);receipts.append(dict(id=r['id'],page=page,index=r['panel_index'],official_mask_sha256=r['geometry']['mask_sha256'],official_mask_pixels=int(m.sum()),padded_feature_mask_pixels=int(feature.sum()),extra_feature_boundary_pixels=int((feature-actual).sum()),official_support_is_subset=True,actual_mask_file=r['actual_mask_file'],note='M35 components observes padded polygon/final_band. Final strip crop clips to its ROI. Boundary scope is not a source label. Native content already reviewed; narrower crop support cannot create an additional loss.'))
  n=r['panel_index'];a_note=reviews[str(n)]
  if n in [6,7,90]:a_note['current_leaf_text']=f"official clipped selected raw<200 retained{metrics['raw_lt200_retained']}, missing{metrics['raw_lt200_missing']}; earlier numeric note referred to padded feature mask";a_note['native_reason']+=' Official clipped-crop support is a subset of the reviewed padded feature footprint; exact counts are in MASK_SCOPE_CORRECTION.'
  by[r['id']]['disposition']=a_note
 dump(O/'MASK_SCOPE_CORRECTION.json',receipts);dump(O/'OBSERVATION_COMPARISON.json',cases);dump(O/'M35_REMOVALS.json',ledger);dump(O/'ADJUDICATION.json',reviews)
 (O/'MASK_SCOPE_CORRECTION.md').write_text('''# Mask scope correction

All153 removals bind the official clipped native ROI crop_mask hash frozen before editing. M35 components uses a padded native ROI and rasterizes the item polygon there; that feature footprint can include boundary pixels clipped out of an exported strip. Earlier contextual red/binary panels depict that M35 feature footprint. The actual_masks/001…153 panels now show the exact would-be removed strip mask in native context. Both scopes remain recorded, rather than silently equated. All153 clipped supports are subsets of the already inspected native feature masks. Source dispositions remain unknown and zero confirmed losses is not proved zero. Query/exemplar B5 diagnostics use rectangles, a third expressly recorded scope.

No runtime masks, image inputs or decisions changed. Official crop masks/coverage remain source-bound208 exact. Numerical selected/missing support counts now explicitly use clipped export-crop masks; padded feature counts remain alongside. The final panel index links both.
''')
 print('exact clipped masks',len(receipts),'boundary-only supersets',sum(r['extra_feature_boundary_pixels']>0 for r in receipts),flush=True)
if __name__=='__main__':run()
