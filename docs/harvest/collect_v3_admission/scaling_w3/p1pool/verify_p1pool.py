import argparse,json,hashlib
from pathlib import Path
import build_p1pool as p
ROOT=Path(__file__).resolve().parent

def package():
    entries=json.loads((ROOT/'PACKAGE_FILES.json').read_text())
    for name,h in entries.items():
        f=ROOT/name
        assert f.resolve().is_relative_to(ROOT) and p.rel4.sha(f)==h, 'package drift: '+name
    for r in json.loads((ROOT/'VENDOR_SHA256.json').read_text()):assert p.rel4.sha(ROOT/r['path'])==r['sha256']
    print('VERIFY package ok',len(entries),'files')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['package','inputs']);a.add_argument('--rel4-config',type=Path);v=a.parse_args();package()
    if v.mode=='inputs':
        if v.rel4_config:
            root,cfg=p.rel4.load_config(v.rel4_config);_,ok,pending=p.rel4.input_check(root,cfg,light=True)
            print('inputs',len(ok),'checked; pending',pending)
            assert not pending,'census_06/REL4 inputs PENDING'
        else:
            cfg=json.loads((ROOT/'vendor/INPUTS.json').read_text());bound=[x for x in cfg['inputs'] if x.get('sha256')];pending=[x['name'] for x in cfg['inputs'] if not x.get('sha256')]
            for x in bound:
                if not Path(x['path']).is_absolute():assert p.rel4.sha(ROOT/'vendor'/x['path'])==x['sha256']
            checked=0
            for x in bound:
                f=p.rel4.resolve(ROOT/'vendor',x['path'])
                if not f.exists():continue
                if x['kind']=='large':assert f.stat().st_size==x['bytes']
                else:assert p.rel4.sha(f)==x['sha256'],x['name']
                checked+=1
            print('inputs',str(checked)+'/'+str(len(cfg['inputs'])),'checked (large: size only); census_06 PENDING:',','.join(pending))
