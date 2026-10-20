#!/usr/bin/env python3
"""Read-only 60-crop acceptance probe using the production subset resolver."""
from collections import Counter
import json
import scale as s


def check():
    releases={s.key(r):r for r in s.rows(s.HERE/'fixtures/real_release.jsonl')}
    counts=Counter(); results=[]
    for r in s.rows(s.HERE/'fixtures/real_admitted_train.jsonl'):
        resolved=s.resolve_crop(r,releases.get(s.key(r)))
        p=s.Path(resolved['crop_path'])
        s.require(p.is_file(),'missing crop '+str(p))
        actual=s.sha(p)
        s.require(actual==resolved['crop_sha256'],'crop SHA mismatch '+str(p))
        counts[r['parent_id']]+=1
        results.append(dict(key=list(s.key(r)),**resolved,actual_sha256=actual))
    s.require(len(counts)==3 and all(n>=20 for n in counts.values()),'insufficient real crops')
    return dict(counts=counts,rows=results,all_byte_exact=True)


if __name__=='__main__':
    print(json.dumps(check(),sort_keys=True,indent=2))
