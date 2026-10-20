"""Audit all physical source labels, preserving pool/split scope."""
import gzip,json,time,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from build_c2 import codec_map,project,projection_sha,sha,dump
P=Path(__file__).resolve().parent

def audit():
 codec=codec_map(P/'evidence/wave2/codec/v2.1.json');alphabet=set();empty=Counter();counts=Counter();examples=defaultdict(list);timings=[]
 start=time.perf_counter()
 with gzip.open(P/'evidence/labels.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);t=time.perf_counter();base=project(r['gt_nfd'],codec);timings.append(time.perf_counter()-t)
   scope=r['pool']+'/'+r['shard'].split('/')[0];counts[scope]+=1;empty[scope]+=not base;alphabet.update(base.replace(' ',''))
   cls={'greek_poly':'Greek polytonic','greek_mono':'Greek monotonic','latin':'Latin','cyrillic':'Cyrillic'}.get(r['script_class'])
   if cls and len(examples[cls])<20:
    examples[cls].append(dict(pool=r['pool'],line_id=r['line_id'],label=r['gt_nfd'],base_label=base,base_label_ids=[codec[c] for c in base]))
 elapsed=time.perf_counter()-start
 result=dict(rows=sum(counts.values()),counts=dict(counts),empty=sum(empty.values()),empty_by_scope=dict(empty),alphabet=sorted(alphabet),alphabet_size=len(alphabet),examples=dict(examples),projection_seconds=sum(timings),projection_rows_per_second=len(timings)/sum(timings),audit_seconds=elapsed,labels_sha256=sha(P/'evidence/labels.jsonl.gz'),projection_source_sha256=projection_sha(),unicode_version=unicodedata.unidata_version)
 assert all(len(examples[c])==20 for c in ('Greek polytonic','Greek monotonic','Latin','Cyrillic'))
 dump(P/'LABEL_AUDIT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='examples'},ensure_ascii=False))
if __name__=='__main__':audit()
