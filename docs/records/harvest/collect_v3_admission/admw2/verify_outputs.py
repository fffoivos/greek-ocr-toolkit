"""Read-only full-output reconciliation and staged-byte audit after ADMW2."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
import build_release_admission as b


def records(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as stream:
        for line in stream:
            if line.strip():yield json.loads(line)


def check():
    reports={};whole_gaz=[];admitted_by_id={}
    for prefix in ('w1_originals_v3_screened','w2_originals_v3','gazette_w2_originals_v3'):
        receipt=json.loads((BASE/(prefix+'_receipt.json')).read_text())
        totals=b.bucket();groups={}; admitted_ids=set();decisions=[]
        for info in receipt['files']:
            path=BASE/info['path'];assert b.sha(path)==info['sha256']
            h=hashlib.sha256();n=0
            opener=gzip.open if path.suffix=='.gz' else open
            with opener(path,'rb') as stream:
                for line in stream:h.update(line);n+=1
            assert h.hexdigest()==info['uncompressed_sha256'] and n==info['rows']
        for d in records(BASE/receipt['files'][0]['path']):
            b.count(totals,d);b.count(groups.setdefault(d['source']+'|'+d['primary_class'],b.bucket()),d)
            assert not (d['pass'] and d['geometry_unavailable'])
            if d['pass']:admitted_ids.add(d['row_id'])
            if prefix=='w2_originals_v3' and d['source']=='gazette_modern':whole_gaz.append(d)
            if prefix=='gazette_w2_originals_v3':decisions.append(d)
        assert b.finish_bucket(totals)==receipt['totals']
        assert {k:b.finish_bucket(v) for k,v in groups.items()}==receipt['counts_per_source_class']
        actual=set()
        for r in records(BASE/receipt['files'][1]['path']):
            assert r['row_id'] not in actual;actual.add(r['row_id'])
            assert r['admission']['pass'] is True
            if prefix!='gazette_w2_originals_v3':admitted_by_id[r['row_id']]=r
        assert actual==admitted_ids
        if prefix=='gazette_w2_originals_v3':assert decisions==whole_gaz
        for p,h in receipt['inputs'].items():assert b.sha(p)==h,('input drift',p)
        reports[prefix]=dict(rows=totals['pre_screen_n'],admitted=len(actual),files_verified=True,counts_reconcile=True)
    manifest=list(records(BASE/'crops_manifest.jsonl'));byid={r['row_id']:r for r in manifest}
    assert len(byid)==len(manifest)
    staged=[];missing=[]
    for rid,r in admitted_by_id.items():
        if rid not in byid:missing.append(rid);continue
        m=byid[rid];path=BASE/m['path']
        assert m['path']==f"crops/{r['source']}/{rid}.png"
        assert b.sha(path)==m['sha256']==r['crop_sha256']
        assert path.stat().st_size==m['bytes']
        staged.append(m)
    old=BASE/'w1_originals_v3_admitted.jsonl'
    assert b.sha(old)=='b6d13fa8bb4b07be632e299fd650cd75dd80348ecf0e0fd9e5cb34bdb6c72bfe'
    # Record current old-release identity; compare to its committed artifact.
    reports['staging']=dict(admitted_union=len(admitted_by_id),staged=len(staged),
        staged_bytes=sum(r['bytes'] for r in staged),missing=len(missing),
        manifest_rows=len(manifest),manifest_sha256=b.sha(BASE/'crops_manifest.jsonl'),
        old_w1_admitted_sha256=b.sha(old))
    (BASE/'admw2/verification.json').write_text(json.dumps(reports,indent=2,sort_keys=True)+'\n')
    print(json.dumps(reports,indent=2))
    return reports

if __name__=='__main__':check()
