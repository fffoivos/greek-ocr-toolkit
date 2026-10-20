"""Read-only independent byte-patch/readback check; run on Clariden after dry run."""
import json,gzip,hashlib
from pathlib import Path
ROOT=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019')
RUN=ROOT/'dryrun_500_legacy_v3'
def rows(p):
 with (gzip.open if str(p).endswith('.gz') else open)(p,'rt',encoding='utf8') as f:return [json.loads(x) for x in f if x.strip()]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={'complete':True,'run':str(RUN),'receipt':load(RUN/'receipt.json'),'splits':{}}
assert result['receipt']['complete'] and result['receipt']['inference_executed']
cfg=load(ROOT/'config/tr2_job.json')
for split in ('test','dev'):
 base=RUN/split;selection=rows(base/'selection.jsonl');ids={r['id'] for r in selection};assert len(ids)==250
 raw={r['id']:r for r in rows(Path(cfg['splits'][split]['source']))};r=load(base/f'RELEASE_RECEIPT_{split}.json')
 p=base/f'release_edits_only_{split}_A.jsonl';assert sha(p)==r['sha256'];actual=rows(p)
 assert len(actual)==r['row_count'] and len({v['line_id'] for v in actual})==len(actual)
 for v in actual:
  assert v['line_id'] in ids and v['parent']=='google_raw_v2_import' and v['split']==split
  a=raw[v['line_id']]['label'].encode();b=v['text'].encode();assert a!=b and hashlib.sha256(a).hexdigest()==v['parent_text_sha256']
  forward=a;back=b
  for patch in reversed(v['byte_patches']):
   x,y=patch['raw_byte_start'],patch['raw_byte_end'];u,w=patch['output_byte_start'],patch['output_byte_end']
   assert a[x:y]==patch['before'].encode() and b[u:w]==patch['after'].encode()
   forward=forward[:x]+patch['after'].encode()+forward[y:]
   back=back[:u]+patch['before'].encode()+back[w:]
  assert forward==b and back==a
 manifest=load(base/'sf7/release/release_A.json');overlay=rows(base/'sf7/release/overlay_A.jsonl.gz')
 assert len(overlay)==250 and {v['line_id'] for v in overlay}==ids
 assert sha(base/'sf7/release/overlay_A.jsonl.gz')==manifest['overlay_sha256']
 controls=rows(base/'sf7/release/ctrl_subset_A.jsonl.gz')
 assert {v['line_id'] for v in controls}=={v['line_id'] for v in overlay if v['status'] in ('corrected','unchanged')}
 scores=load(base/'scores_receipt.json');assert scores['lines']==250 and scores['counts']['alignment_identity_matches']==250
 assert sha(base/'recogniser_scores.jsonl.gz')==scores['sha256']
 result['splits'][split]={'release':r,'composer_counts':manifest['counts_by_status'],'scores':scores,'selection_sha256':sha(base/'selection.jsonl'),'independent_forward_reverse_byte_check':True,'overlay_control_membership_check':True}
assert not {v['id'] for v in rows(RUN/'test/selection.jsonl')}&{v['id'] for v in rows(RUN/'dev/selection.jsonl')}
print(json.dumps(result,indent=2,ensure_ascii=False))
