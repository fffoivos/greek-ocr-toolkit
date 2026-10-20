"""Offline SR-B3 audit/build/resolve/score driver; never launches readers."""
from common import *
from scan_rollout import inspect
from scan_packs import scan
from build_tiebreak import build
from b2_common import disagreements,load_run,source_items
from resolve import resolve
from score_all import run

def main():
    scans=[]
    for entry in rows_ledger():
        bed,reader=entry['bed'],entry['reader'];p=ROOT/f'answers/{bed}/{reader}.scan.json'
        if p.exists():
            old=json.loads(p.read_text());version=old.get('scanner_version',1);backup=p.with_name(f'{reader}.scan.v{version}.json')
            if not backup.exists():backup.write_bytes(p.read_bytes())
            elif backup.read_bytes()!=p.read_bytes():raise ValueError('different existing scan backup: '+str(backup))
        result=inspect(entry['rollout'],PACK_ROOT/bed/reader);dump(p,result)
        summary=dict(bed=bed,reader=reader,ok=result['ok'],violations=len(result['violations']),returned_images=result['returned_images'])
        scans.append(summary);print(json.dumps(summary),flush=True)
    ties=[]
    for bed in FIELDS:
        left,s1=load_run(bed,'r1');right,s2=load_run(bed,'r2')
        if left and right:
            disputes=disagreements(bed,left,right,source_items(bed));receipt=build(bed)
            receipt.update(disputed_items=len(disputes),disputed_units=sum(map(len,disputes.values())))
            folder=PACK_ROOT/bed/'r3'
            if folder.exists():
                check=scan(folder,bed);dump(ROOT/f'validation/{bed}_r3.pack_scan.json',check);receipt.update(items=check['items'],scan_ok=check['ok'])
            ties.append(receipt);print(json.dumps(receipt),flush=True)
        print(json.dumps(resolve(bed)),flush=True)
    dump(ROOT/'validation/B3_AUDIT.json',dict(scans=scans,tiebreaks=ties));run()

def rows_ledger():return json.loads((ROOT/'usage_ledger.json').read_text())
if __name__=='__main__':main()
