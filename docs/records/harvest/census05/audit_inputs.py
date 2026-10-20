"""Read-only frozen-parent, SPLIT2 and expectation-resolution audit; no native I/O."""
import gzip, hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent; R=D.parents[2]; PROJECTS=R.parent
P=D/'package/projects/greek-ocr-toolkit-pipe032';sys.path.insert(0,str(P))
from greekocr.harvest.line_pipeline_census04 import load_split
from greekocr.harvest.line_pipeline_sources import canonicalize
from greekocr.harvest.line_pipeline import canonical, expectations

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def spec(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def main():
 config=json.loads((R/'docs/harvest/seg_census/census04_config.json').read_text())
 fp3=PROJECTS/'greek-page-ocr-wave2/out/fp3'
 meta=fp3/'prepared/87407ec7430a375f/metadata.json'
 assert sha(meta)=='dd2da6548a2dd6ed5624299be552e32204efb85220f4463590fb4c8e3ddd3bf5'
 metadata=json.loads(meta.read_text())
 splitdir=PROJECTS/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/split2'
 split=splitdir/'row_split.jsonl.gz'; splitsha='7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82'
 assert sha(split)==splitsha
 blob=subprocess.check_output(['git','-C',str(PROJECTS/'greek-ocr-toolkit-sol-recut'),'show','aa860af55:docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz'])
 assert split.read_bytes()==blob
 assignments=load_split(dict(path=str(split),sha256=splitsha))
 schema=json.loads((R/'docs/harvest/seg_census/split_input.schema.json').read_text())
 import jsonschema
 validator=jsonschema.Draft202012Validator(schema)
 with gzip.open(split,'rt') as f:
  for s in f:
   validator.validate(json.loads(s))
 editions={}; counts=Counter(); forced=set()
 for s in (splitdir/'edition_map.jsonl').open():
  rec=json.loads(s);editions[rec['edition_id']]=rec['split']
  if rec['forced']:forced.add(rec['edition_id']);assert rec['split']=='test'
 assert len(editions)==1359 and len(forced)==99
 observed=set(); parents=[]; totals=Counter(); levels=Counter(); forced_rows=0
 for parent in config['parents']:
  path=(PROJECTS/'greek-ocr-toolkit/docs/harvest/collection/v2'/Path(parent['path']).name
   if parent['format']=='collection-v2' else PROJECTS/'collect-v3-data/snapshots'/Path(parent['path']).name)
  assert sha(path)==parent['sha256']
  n=0; assigned=Counter(); missing=[]; lc=Counter()
  with path.open() as f:
   for line in f:
    rec=json.loads(line);n+=1;row=canonicalize(rec,parent,metadata)
    key=(parent['id'],row['id'])
    if key in assignments:
     a=assignments[key];observed.add(key);assigned[a['split']]+=1
     assert editions[a['edition_id']]==a['split']
     if a['edition_id'] in forced:
      assert a['split']=='test';forced_rows+=1
    elif parent['format']=='collect-v3-features':missing.append(row['id'])
    pagekey=canonical([row['source'],row['book_id'],row['page_id']])
    try:expectations(row,metadata)
    except (ValueError,KeyError) as e:level='unresolved:'+str(e)
    else:level=('page_override' if metadata.get('pages',{}).get(pagekey) else 'book_declaration' if metadata.get('books',{}).get(row['book_id']) else 'source_policy')
    lc[level]+=1;levels[level]+=1
  assert n==parent['rows']; assert not missing
  totals.update(assigned)
  parents.append(dict(parent_id=parent['id'],remote_path=parent['path'],**spec(path),rows=n,split_counts=dict(assigned),parent_rows_without_split=len(missing) if parent['format']=='collect-v3-features' else 'not applicable: frozen v2 cohorts',expectation_resolution=dict(lc)))
 assert len(assignments)==len(observed)==320479
 assert totals==dict(train=253402,dev=7007,test=60070)
 assert {a['edition_id'] for a in assignments.values()}==set(editions)
 result=dict(status='PASS',split=spec(split),git_commit='aa860af55',compressed_bytes_equal_git_blob=True,
  schema_path='docs/harvest/seg_census/split_input.schema.json',loader=str(P/'greekocr/harvest/line_pipeline_census04.py'),loader_sha256=sha(P/'greekocr/harvest/line_pipeline_census04.py'),
  loader_rows=len(assignments),schema_rows=len(assignments),split_counts=dict(totals),editions=len(editions),one_split_per_edition=True,
  forced_test_editions=len(forced),forced_test_rows=forced_rows,all_forced_test=True,unmatched_split_rows=0,unmatched_W1_W2_parent_rows=0,
  parents=parents,metadata=spec(meta),expectation_resolution=dict(levels),
  heldout_crops=len(config['final_policy']['heldout_crop_sha256']),heldout_editions=len(config['final_policy']['heldout_editions']),
  neighboring_split_evidence=[spec(splitdir/n) for n in ['edition_map.jsonl','receipt.json','SPLIT2.md']],
  late_BSB_pages='436 post-snapshot pages are outside the frozen parents; no assignments created')
 (D/'input_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','loader_rows','split_counts','editions','forced_test_editions','expectation_resolution']},indent=2))
if __name__=='__main__':main()
