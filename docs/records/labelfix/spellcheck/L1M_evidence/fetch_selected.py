"""Read-only, bounded Clariden extraction. No remote files or jobs created."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
REMOTE = r'''
import base64,gzip,hashlib,json,pathlib,re,signal,sys,time
request=json.loads(base64.b64decode("REQUEST"))
ids=set(request['ids']); missing_al=set(request['missing_alignment_ids'])
started=time.monotonic(); signal.alarm(210)
b=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
found={}; align={}; provenance=[]; shardmap={}
pattern=re.compile(rb'"id"\s*:\s*"([^"]+)"')
for p in sorted((b/'l1e_20261017/output_3679545/inference').glob('shard-*-combined.jsonl.gz')):
    used=[]
    with gzip.open(p,'rb') as f:
        for line in f:
            m=pattern.search(line[:160])
            if m and m[1].decode() in ids:
                r=json.loads(line); key=r['id']
                assert key not in found
                found[key]=r;used.append(key);shardmap.setdefault(p.name,[]).append(key)
    if used:
        rp=p.with_name(p.name.replace('-combined.jsonl.gz','-receipt.json'))
        provenance.append(dict(kind='BE',path=str(p),file_bytes=p.stat().st_size,
            selected_ids=used,receipt=json.loads(rp.read_text()),receipt_sha256=hashlib.sha256(rp.read_bytes()).hexdigest()))
    if len(found)==len(ids):break
assert set(found)==ids, ('missing runtime',sorted(ids-set(found)))
for name, keys in shardmap.items():
    p=b/'output_3679313/combined'/name; seen=set()
    with gzip.open(p,'rb') as f:
        for line in f:
            m=pattern.search(line[:160])
            if m and m[1].decode() in keys:
                old=json.loads(line);key=old['id'];seen.add(key)
                for field in ('recogniser_text','recogniser_nfd','detector','coverage','r1_predictions'):
                    assert old[field]==found[key][field], (key,field,'historical A mismatch')
                found[key]['historical_A_verified']=True
    assert seen==set(keys)
    rp=p.with_name(p.name.replace('-combined.jsonl.gz','-receipt.json'))
    provenance.append(dict(kind='A',path=str(p),file_bytes=p.stat().st_size,
        selected_ids=keys,receipt=json.loads(rp.read_text()),receipt_sha256=hashlib.sha256(rp.read_bytes()).hexdigest()))
for p in sorted((b/'output_3679313/alignment').glob('worker_*.jsonl.gz')):
    if not missing_al:break
    used=[]
    with gzip.open(p,'rt') as f:
        for line in f:
            # Alignment rows are small; avoid decoding all C1 alignments remotely.
            r=json.loads(line); crop='docs/harvest/'+r['crop'].split('docs/harvest/',1)[1]
            key=request['crop_to_id'].get(crop)
            if key in missing_al:
                align[key]=r;used.append(key);missing_al.remove(key)
    if used:provenance.append(dict(kind='alignment',path=str(p),selected_ids=used,file_bytes=p.stat().st_size))
assert not missing_al,('missing alignment',sorted(missing_al))
result=dict(schema='l1m-selected-readonly-v1',complete=True,elapsed_seconds=time.monotonic()-started,
    ids=sorted(ids),runtime=found,alignments=align,provenance=provenance,
    custody_limit='Shard receipts read and selected A fields compared exactly; full remote shard hashes not recomputed.',
    remote_writes=0,submitted_jobs=0)
sys.stdout.buffer.write(gzip.compress(json.dumps(result,ensure_ascii=False).encode()))
'''


def fetch(sample):
    suffix = '_vouli' if sample == 'vouli' else ''
    ids = (HERE.parent / f'L1M_masking_sample_ids{suffix}.txt').read_text().split()
    dest = HERE / f'remote_{sample}.json.gz'
    if dest.exists():
        data = json.loads(gzip.decompress(dest.read_bytes()))
        assert data['complete'] and set(data['ids']) == set(ids)
        return dest
    local = {}
    cache = HERE / 'c1_selected_alignments.jsonl.gz'
    if cache.exists():
        for line in gzip.open(cache, 'rt'):
            r = json.loads(line)
            local[r['id']] = r
    selected={}
    source_path=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl')
    for line in source_path.open():
        r=json.loads(line)
        if r['id'] in ids:selected[r['id']]=r
    assert set(selected)==set(ids)
    req = dict(ids=ids, missing_alignment_ids=sorted(set(ids)-set(local)),
        crop_to_id={r['crop']:key for key,r in selected.items()})
    source = REMOTE.replace('REQUEST', base64.b64encode(json.dumps(req).encode()).decode())
    logs = []
    for attempt in range(1, 5):  # initial attempt plus at most three transient retries
        start = time.monotonic()
        try:
            p = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',
                '-o','ServerAliveInterval=10','-o','ServerAliveCountMax=2','clariden','python3 -'],
                input=source.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=235)
        except subprocess.TimeoutExpired:
            raise SystemExit('STOP: bounded Clariden extraction exceeded 235 seconds; no retry')
        stderr = p.stderr.decode(errors='replace')
        logs.append(dict(attempt=attempt,seconds=time.monotonic()-start,returncode=p.returncode,stderr=stderr))
        logpath=HERE / f'fetch_{sample}_log.json'
        prior=json.loads(logpath.read_text()) if logpath.exists() else []
        logpath.write_text(json.dumps(prior+[logs[-1]],indent=2))
        if p.returncode == 0:
            data = json.loads(gzip.decompress(p.stdout))
            assert data['complete'] and set(data['ids']) == set(ids)
            dest.write_bytes(p.stdout)
            print(json.dumps(dict(sample=sample,lines=len(ids),bytes=len(p.stdout),remote_seconds=data['elapsed_seconds'])))
            return dest
        if any(x in stderr.lower() for x in ('permission denied','certificate','authentication','host key verification')):
            raise SystemExit('STOP: authentication/certificate/host-key failure; certificate not refreshed')
        transient = any(x in stderr.lower() for x in ('connection reset','connection timed out','connection closed','broken pipe','could not resolve hostname'))
        if not transient or attempt == 4:
            raise SystemExit('STOP: Clariden extraction failed: '+stderr[-2000:])
    raise AssertionError('unreachable')


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sample',choices=['200','vouli'],default='200')
    fetch(ap.parse_args().sample)
