"""Read-only local crop inventory and supplemental numeric box measurements.
No census/tool population execution: the frozen table is read only to bind SHA/text
for the finite list of PNGs already present under segeval1/cells_opus/crops.
"""
from replay import *
import gzip
common=module('cells_output_common',BASE/'cells_opus/scripts/common.py')

def run():
 known={r['line_id'] for r in read(D.parent/'s3/inputs.jsonl')}|{r['line_id'] for r in read(SS/'samples.jsonl')}
 local={p.stem:p for p in (BASE/'cells_opus/crops').glob('*.png')}
 samples={r['line_id']:r for r in read(BASE/'cells_opus/samples.jsonl')}
 wanted={rid for rid,p in local.items() if rid not in known and rid in samples and common.output_type(samples[rid]['text'])=='numeric' and s1.character_count(samples[rid]['text'])<=8 and max(samples[rid]['width'],samples[rid]['height'])/min(samples[rid]['width'],samples[rid]['height'])<=6}
 meta={}
 with gzip.open(BASE/'cells/population_cells.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line)
   if r['row_id'] in wanted:meta[r['row_id']]=r
 assert set(meta)==wanted
 w=worker('s3');signal.signal(signal.SIGALRM,s1.timeout);out=[]
 try:
  for rid,r in sorted(meta.items()):
   p=local[rid];assert sha(p)==r['crop_sha256'];assert r['raw_text']==samples[rid]['text']
   row=dict(id=rid,parent_id=r['parent_id'],split='unassigned',crop_path=str(p),crop_sha256=r['crop_sha256'],raw_text=r['raw_text'],script_class=r['script_class'],primary_class=r['primary_class'])
   inp=dict(cohort='cells_opus',line_id=rid,row=row);orig=w.crop_tools.line_inventory
   z,geo=measure(w,inp);w.crop_tools.line_inventory=orig
   out.append(dict(inp,before=z,geometry=geo,chars=s1.character_count(row['raw_text']),A=max(r['width_px'],r['height_px'])/min(r['width_px'],r['height_px']),small=True))
 finally:w.close()
 write(D/'extra_numeric.jsonl',out)
 inventory=Counter(str(p.parent.relative_to(BASE)) for p in BASE.rglob('*.png'))
 dump(D/'local_crop_inventory.json',dict(png_directories=inventory,extra_numeric=len(out),extra_numeric_candidate_ids=sorted(wanted),metadata_sha256=sha(BASE/'cells/population_cells.jsonl.gz'),sources=['150','888','250','small_segments/crops (437)','cells_opus/crops (266 files, overlapping the preceding sets)'],excluded_images='contact sheets, report illustrations, and test_tmp SHA-mismatch fixture have no independent crop/text/hash manifest; not crop fitting inputs',network='OFF',census_execution=False))
 print('extra numeric',len(out),flush=True)
if __name__=='__main__':run()
