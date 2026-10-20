#!/usr/bin/env python3
"""Resolve S2, retaining undecided units when a third answer is absent/different."""
import argparse
from b2_common import *
def resolve(bed):
    left,s1=load_run(bed,'r1');right,s2=load_run(bed,'r2')
    if s1!='OK' or s2!='OK':return dict(bed=bed,status='missing or excluded primaries',r1=s1,r2=s2)
    third,s3=load_run(bed,'r3');items=source_items(bed)
    output,unresolved=resolve_records(bed,left,right,third,items)
    dest=ROOT/'answers'/bed;jsonl(dest/'S2.mapped.jsonl',output)
    receipt=dict(bed=bed,used_readers=['r1','r2']+(['r3'] if s3=='OK' else []),r3_status=s3,missing_r1=sorted(set(items)-set(left)),missing_r2=sorted(set(items)-set(right)),unresolved=unresolved,unresolved_units=len([u for u in unresolved if u['unit']!='missing_primary']))
    dump(dest/'S2.unresolved.json',receipt);return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bed',choices=FIELDS);print(json.dumps(resolve(p.parse_args().bed),ensure_ascii=False,indent=2))
