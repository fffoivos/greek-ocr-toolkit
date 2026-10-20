"""Losslessly archive completed T23 raw JSON; no network or provider calls.

Parsed response and cache must already be committed. Exact embedded copies of
the input PNG become SHA-bound references. Reconstruct and verify every original
byte before removing a redundant copy. Use --restore for the original raw JSON.
"""
from __future__ import annotations

import argparse
import base64
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import time

from scripts.harvest.parliament import GOOGLE, OUT, REPO, relative, sha
from greekocr.harvest.readers import read_jsonl


def canonical(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')


def restore_deduplicated(data):
    packed=json.loads(data)
    response=packed['response']
    for ref in packed['image_references']:
        image=(REPO/ref['path']).read_bytes()
        if hashlib.sha256(image).hexdigest()!=ref['sha256']:raise ValueError('referenced input PNG changed')
        response['document']['pages'][ref['page']]['image']['content']=base64.b64encode(image).decode('ascii')
    restored=canonical(response)
    if hashlib.sha256(restored).hexdigest()!=packed['raw_sha256']:
        raise ValueError('raw reconstruction changed original response bytes')
    return restored


def raw_bytes(path):
    path=Path(path);dedup=path.with_suffix(path.suffix+'.dedup.gz');full=path.with_suffix(path.suffix+'.gz')
    if dedup.exists():return restore_deduplicated(gzip.decompress(dedup.read_bytes())),dedup
    if full.exists():return gzip.decompress(full.read_bytes()),full
    return path.read_bytes(),None


def compact(root=GOOGLE, *, image_paths=None):
    root=Path(root)
    archived,saved=0,0
    if image_paths is None:
        image_paths={p['image_sha256']:REPO/p['image'] for p in json.loads((OUT/'plan.json').read_text())['pages']} if (OUT/'plan.json').exists() else {}
    with (root/'archive.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for parsed_path in (root/'parsed/docai').glob('*.json'):
            parsed=json.loads(parsed_path.read_text())
            if parsed['status']!='ok':continue
            raw=Path(parsed['raw_json_path'])
            full=raw.with_suffix(raw.suffix+'.gz');dedup=raw.with_suffix(raw.suffix+'.dedup.gz')
            if dedup.exists() or (not raw.exists() and not full.exists()):continue
            if not raw.exists() and parsed['image_sha256'] not in image_paths:continue
            cache=json.loads((raw.parent/'cache.json').read_text())
            data=raw.read_bytes() if raw.exists() else gzip.decompress(full.read_bytes())
            digest=hashlib.sha256(data).hexdigest()
            if digest!=cache['raw_sha256'] or cache['crop_sha256']!=parsed['image_sha256']:
                raise ValueError('raw/cache custody changed before archive')
            original_size=len(data);stored_size=raw.stat().st_size if raw.exists() else full.stat().st_size
            target=full;payload=data;references=[]
            image_path=image_paths.get(parsed['image_sha256'])
            if image_path is not None:
                response=json.loads(data)
                for index,page in enumerate(response.get('document',{}).get('pages',[])):
                    content=page.get('image',{}).get('content')
                    if content and hashlib.sha256(base64.b64decode(content)).hexdigest()==parsed['image_sha256']:
                        if sha(image_path)!=parsed['image_sha256']:raise ValueError('native PNG changed before deduplication')
                        references.append(dict(page=index,path=str(Path(image_path).relative_to(REPO)),sha256=parsed['image_sha256']))
                        del page['image']['content']
                if references:
                    packed=canonical(dict(schema='t23-raw-dedup-1',raw_sha256=digest,response=response,image_references=references))
                    if restore_deduplicated(packed)==data:
                        payload=packed;target=dedup
            temp=target.with_suffix(target.suffix+'.tmp')
            with temp.open('wb') as stream:
                with gzip.GzipFile(filename='',mode='wb',fileobj=stream,compresslevel=6,mtime=0) as gz:
                    gz.write(payload)
                stream.flush();os.fsync(stream.fileno())
            with gzip.open(temp,'rb') as stream:
                restored_data=stream.read()
            if target==dedup:restored_data=restore_deduplicated(restored_data)
            if hashlib.sha256(restored_data).hexdigest()!=digest:raise ValueError('lossless raw archive verification failed')
            temp.replace(target)
            receipt=dict(raw_json_path=str(raw),raw_sha256=digest,raw_bytes=original_size,
                gzip_path=str(target),gzip_sha256=sha(target),gzip_bytes=target.stat().st_size,
                image_sha256=parsed['image_sha256'],receipt_id=parsed['receipt_id'],
                storage='deduplicated-image-reference' if target==dedup else 'full-gzip')
            with (root/'raw_archives.jsonl').open('a') as stream:
                stream.write(json.dumps(receipt,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())
            raw.unlink(missing_ok=True)
            if target==dedup:full.unlink(missing_ok=True)
            archived+=1;saved+=stored_size-target.stat().st_size
    return archived,saved


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--watch',action='store_true')
    p.add_argument('--restore',type=Path,help='reconstruct one original raw JSON file offline')
    args=p.parse_args()
    if args.restore:
        data,_=raw_bytes(args.restore);args.restore.write_bytes(data)
        print(f'restored {len(data)} original bytes; sha256 {hashlib.sha256(data).hexdigest()}',flush=True)
        return
    total=0
    while True:
        count,saved=compact();total+=count
        if count:print(f'archived {count}; total this process {total}; freed {saved/1e6:.1f} MB',flush=True)
        completed=len(list((GOOGLE/'parsed/docai').glob('*.json')))
        expected=json.loads((OUT/'plan.json').read_text())['max_calls']
        if not args.watch or completed>=expected:break
        time.sleep(5)


if __name__=='__main__':main()
