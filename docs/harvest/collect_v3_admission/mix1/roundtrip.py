"""Bounded 1000-row all-parent factory check. No scheduler or full input scan.

Writes only the explicitly authorized new evidence directory and retains it.
No scheduler, cleanup, or production export is run.
"""
from core import *
import argparse
from export import export_real,WAVE2
from pipeline import SUBSET,SUBSET_SHA

def check(destination, *, code_shas=None):
    folder=Path(destination)
    require(folder.parent==WAVE2.parents[2]/'scaling_w3/mix1_scratch' and folder.name.startswith('roundtrip_'),'unauthorized evidence path')
    folder.mkdir(parents=True,exist_ok=False)
    require(sha(SUBSET)==SUBSET_SHA,'subset receipt SHA')
    entry=json.loads(SUBSET.read_text())['subsets']['ref_364871']['output']
    require(sha(entry['path'])==entry['sha256'],'ref SHA')
    targets={'collect-v3-W1-20261018-0524':334,'collect-v3-W2-20261018-0524':334,'collection-v2-train':332}
    sample=[];counts=Counter()
    for row in rows(entry['path']):
        p=row['key'][0]
        if counts[p]<targets[p]:
            row=dict(row,line_id=row['row_id'],final_text=row['label']);sample.append(row);counts[p]+=1
        if counts==targets:break
    require(counts==targets,'sample three-parent coverage')
    selected={tuple(r['key']):r for r in sample};joined=set()
    tags=SUBSET.parents[2]/'tags/scale1-c05-002/train_tags.jsonl.gz'
    # Tags supply the same edition mapping used by pipeline.load_real.
    for tag in rows(tags):
        key=tuple(tag['key'])
        if key in selected:
            require(tag['crop_sha256']==selected[key]['crop_sha256'],'sample tag crop binding')
            selected[key]['edition_id']=tag['edition_id'];joined.add(key)
        if len(joined)==1000:break
    require(len(joined)==1000,'sample edition join')
    result=export_real(sample,folder/'export')
    require(result['round_trip'] and result['full_validate_ok'] and result['rows']==1000,'round trip failed')
    result.update(loader_root=str(WAVE2),subset_receipt_sha256=SUBSET_SHA,evidence_directory=str(folder),
        evidence_retained=True,mix1c_code=code_shas or {n:sha(Path(__file__).parent/n) for n in ('export.py','roundtrip.py')})
    result['contents_sha256']={str(p.relative_to(folder)):sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
    result['contents_bytes']=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
    dump(folder/'ROUNDTRIP_RECEIPT.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('evidence_directory');a=p.parse_args();print(json.dumps(check(a.evidence_directory),sort_keys=True))
