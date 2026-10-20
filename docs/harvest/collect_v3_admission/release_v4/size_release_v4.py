#!/usr/bin/env python3
"""Conservative resource estimate from bound bytes; no data scans."""
import argparse
import math
from pathlib import Path
import build_release_v4 as b


def size(cfg):
    b.require(all(i.get('sha256') and i.get('bytes') is not None for i in cfg['inputs'] if i['kind']=='large'), 'sizing requires bound input sizes')
    large_bytes=sum(i['bytes'] for i in cfg['inputs'] if i['kind']=='large')
    ledger_bytes=sum(cfg['sf7'].get('ledger_sizes',{}).get(x['sha256'],x.get('bytes',0)) for x in cfg['sf7']['ledgers'] if x['parent_id'] in cfg['parents'])
    # REL3 THROUGHPUT.json: both hash passes included, 265.03 MB/s.
    # 20x allowance; 300s crops + 900s extra ledger parsing/flips/receipts.
    seconds=large_bytes/265026561.40263772*20+1200
    minutes=max(60,math.ceil(seconds/900)*15)
    b.require(minutes<=720, 'estimated release exceeds normal 12h limit')
    # REL3 compact maps + old/new keys <= 2 GiB conservative base; 4x JSON
    # expansion for retained W1/W2 sf7 records, doubled for allocator headroom.
    memory_gib=max(8,math.ceil((2*1024**3+ledger_bytes*4)*2/1024**3))
    return dict(input_bytes=large_bytes,selected_sf7_ledger_bytes=ledger_bytes,seconds_model=seconds,
                time=f'{minutes//60:02d}:{minutes%60:02d}:00',memory_gib=memory_gib)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--field',choices=['time','memory_gib'])
    a=p.parse_args();_,cfg=b.load_config(a.config);r=size(cfg);print(r[a.field] if a.field else b.canonical(r))
