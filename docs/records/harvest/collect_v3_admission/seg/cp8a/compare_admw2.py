"""Compare full native rerun against original ADMW2, allowing identity schema only."""
import gzip,json,sys,hashlib
from pathlib import Path
from qualify import BASE,HERE,sha,dump
NEW=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/segcp8a-admw2')
def stream(path):
    if not path.exists():path=Path(str(path)+'.gz')
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as f:
        for l in f:
            if l.strip():yield json.loads(l)
def strip(r):
    if isinstance(r,dict):return {k:strip(v) for k,v in r.items() if k!='application_manifest_sha256'}
    if isinstance(r,list):return [strip(v) for v in r]
    return r

def main():
    from itertools import zip_longest
    report={}
    for prefix in ('w1_originals_v3_screened','w2_originals_v3','gazette_w2_originals_v3'):
        entry={}
        for kind in ('admission','admitted'):
            name=prefix+'_'+kind+'.jsonl';count=0;deltas=[];semantic=hashlib.sha256()
            for a,b in zip_longest(stream(BASE/name),stream(NEW/name)):
                if strip(a)!=strip(b):deltas.append(dict(row=count,old=a,new=b))
                semantic.update((json.dumps(strip(b),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode())
                count+=1
            entry[kind]=dict(rows=count,decision_deltas=len(deltas),semantic_sha256=semantic.hexdigest(),examples=deltas[:10])
            assert not deltas,(name,len(deltas))
        old=json.loads((BASE/(prefix+'_receipt.json')).read_text());new=json.loads((NEW/(prefix+'_receipt.json')).read_text())
        assert old['totals']==new['totals'] and old['counts_per_source_class']==new['counts_per_source_class']
        entry['receipt_field_deltas']={k:dict(old=old.get(k),new=new.get(k)) for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)}
        entry['counts_identical']=True;entry['schema_delta']='application_manifest_sha256 added to decision rows and nested admitted admission; receipt adds identity and changes builder_sha256'
        report[prefix]=entry
    dump(HERE/'admw2_comparison.json',report)
    dump(HERE/'admw2_native_qualification.json',dict(passed=True,views={n:{k:v[k] for k in ('admission','admitted','counts_identical')} for n,v in report.items()},scope='all original decision fields; only application identity metadata excluded',builder_sha256=sha(BASE/'build_release_admission.py')))
    print(json.dumps(report))
if __name__=='__main__':main()
