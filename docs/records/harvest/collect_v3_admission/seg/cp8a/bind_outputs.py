"""Issue identity sidecars and certify unchanged native outputs under final closure.

Only identity metadata changes. compare_admw2.py must pass after this step.
"""
import gzip,json,sys
from pathlib import Path
from qualify import HERE,BASE,ROOT,dump,sha
from greekocr.harvest.application_identity import identity
sys.path.insert(0,str(BASE))
from build_release_admission import Jsonl

def bind(root=Path('/tmp/segcp8a-admw2')):
    application=identity()
    for name in ('w1_originals_v3_screened','w2_originals_v3','gazette_w2_originals_v3'):
        receipt=json.loads((root/(name+'_receipt.json')).read_text());files=[]
        for kind in ('admission','admitted'):
            p=root/(name+'_'+kind+'.jsonl')
            source=p if p.exists() else Path(str(p)+'.gz')
            w=Jsonl(p)
            with (gzip.open(source,'rt') if source.suffix=='.gz' else source.open()) as f:
                for line in f:
                    r=json.loads(line)
                    if kind=='admission':r['application_manifest_sha256']=application
                    else:r['admission']['application_manifest_sha256']=application
                    w.write(r)
            files.append(w.finish())
        receipt.update(application_manifest_sha256=application,files=files,
            qualification_identity_issuance='final closure after native parity; identity metadata only')
        dump(root/(name+'_receipt.json'),receipt)
    products=[p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.json','.log')
        and p.name not in ('application_manifest.json','application_outputs.json')
        and not p.name.endswith('.application.json')]
    products.extend(root.glob('*_receipt.json'))
    dump(HERE/'application_outputs.json',dict(application_manifest_sha256=application,
        files={str(p):sha(p) for p in products},
        final_identity_issued_after_native_parity=True))
    for p in products:
        dump(p.with_suffix(p.suffix+'.application.json'),dict(application_manifest_sha256=application,output_sha256=sha(p),output=p.name))
    print(application)
if __name__=='__main__':bind()
