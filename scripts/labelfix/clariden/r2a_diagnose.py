"""Read-only full old-pool collision audit; verifies actual crop bytes on login CPU."""
import json
from collections import defaultdict,Counter
import numpy as np
from scripts.labelfix.clariden.r1_train import Shards
from scripts.labelfix.clariden.r1_common import rows,sha256
def main():
    cfg=json.load(open('config/r2a_job.json')); ds=Shards(cfg['data'],'A','train')
    lines={r['line']:r for r in rows(ds.path/'lines.jsonl.gz')}; inv={r['crop']:r for r in rows(cfg['inventory'])}; crops={p:r['sha256'] for p,r in inv.items()}; hashcache={}
    groups=defaultdict(list)
    for i,r in enumerate(ds.index):
     l=lines[int(r['line'])];groups[(crops[l['crop']],int(r['start']))].append(i)
    counts=Counter();targetcounts=Counter();examples=[];allgroups=[]
    for key,ii in groups.items():
     if len(ii)<2:continue
     records=[]
     for i in ii:
      r=ds.index[i];l=lines[int(r['line'])]
      records.append(dict(index=i,line=int(r['line']),line_id=l['id'],crop=l['crop'],doc=l['doc'],start=int(r['start']),target=r['target'].tolist(),letter=int(r['letter']),mask=r['mask'].tolist(),recogniser_text=l.get('recogniser_text')))
     # Same line/start represented repeatedly is repeated extraction. Different line/path with verified same bytes is image reuse.
     if len({r['line'] for r in records})==1:
      cls='b' if len({(r['letter'],json.dumps(r['mask'])) for r in records})==1 else 'c'
     elif len({(r['crop'],r['line_id']) for r in records})>1:cls='a'
     elif len({(r['letter'],json.dumps(r['mask'])) for r in records})==1:cls='b'
     else:cls='c'
     actual={}
     for p in {r['crop'] for r in records}:
      if p not in hashcache:hashcache[p]=sha256(inv[p]['path'])
      actual[p]=hashcache[p]
     if any(h!=key[0] for h in actual.values()):cls='d'
     same=len({tuple(r['target']) for r in records})==1
     counts[cls]+=1;targetcounts['identical' if same else 'different']+=1
     allgroups.append(dict(slot_id=key,classification=cls,targets_identical=same,rows=records,verified_crop_sha256=actual))
    overlay={tuple(r['slot_id']) for r in rows(cfg['manifest'])};dupkeys={k for k,v in groups.items() if len(v)>1}
    result=dict(old_rows=len(ds),old_unique_keys=len(groups),old_duplicate_rows=sum(len(v) for v in groups.values() if len(v)>1),old_excess_rows=len(ds)-len(groups),old_duplicate_groups={c:counts[c] for c in 'abcd'},repeated_keys=len(dupkeys),target_groups=dict(targetcounts),overlay_hits_on_duplicated_keys=len(overlay&dupkeys),overlay_hits_on_old_keys=len(overlay&set(groups)),classification_rules=dict(a='different crop paths or line ids; actual crop bytes SHA verified',b='same extracted line/start and slot geometry repeated',c='same line/start with distinct slot geometry or letter',d='inventory hash does not match crop bytes'),groups=allgroups,examples=allgroups[:10])
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
