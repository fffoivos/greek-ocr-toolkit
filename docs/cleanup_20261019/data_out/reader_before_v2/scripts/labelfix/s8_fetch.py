"""S8a: bounded read-only Clariden saved-evidence extraction; never infer."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/labelfix/spellcheck/S8_DEV'
REMOTE = r'''
import base64,gzip,hashlib,json,pathlib,re,signal,sys,time
req=json.loads(base64.b64decode('REQUEST'))
ids=set(req['ids']); start=time.monotonic(); signal.alarm(80)
b=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
runtime={}; als={}; decisions={}; provenance=[]; shardmap={}
pat=re.compile(rb'"(?:id|line_id)"\s*:\s*"([^"]+)"')
def selected(p,wanted):
    full=p.name.startswith('overlay_')
    with gzip.open(p,'rb') as f:
        for line in f:
            m=pat.search(line if full else line[:180])
            if m and m[1].decode() in wanted: yield json.loads(line)
def receipt(p,used,kind):
    rp=p.with_name(p.name.replace('-combined.jsonl.gz','-receipt.json'))
    entry=dict(kind=kind,path=str(p),file_bytes=p.stat().st_size,selected_ids=sorted(used))
    if rp!=p and rp.exists():
        entry.update(receipt=json.loads(rp.read_text()),receipt_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    provenance.append(entry)
for p in sorted((b/'l1e_20261017/output_3679545/inference').glob('shard-*-combined.jsonl.gz')):
    used=[]
    for r in selected(p,ids):
        key=r['id']; assert key not in runtime
        runtime[key]=r; used.append(key)
    if used:shardmap[p.name]=used;receipt(p,used,'BE')
    if set(runtime)==ids:break
assert set(runtime)==ids,('missing runtime',sorted(ids-set(runtime)))
for name,keys in shardmap.items():
    p=b/'output_3679313/combined'/name; seen=set()
    for old in selected(p,set(keys)):
        key=old['id'];seen.add(key)
        for field in ('recogniser_text','recogniser_nfd','detector','coverage','r1_predictions'):
            assert old[field]==runtime[key][field],(key,field,'historical A differs')
        runtime[key]['historical_A_verified']=True
    assert seen==set(keys);receipt(p,keys,'A')
missing=set(req['missing_alignment_ids'])
for p in sorted((b/'output_3679313/alignment').glob('worker_*.jsonl.gz')):
    if not missing:break
    used=[]
    with gzip.open(p,'rt') as f:
        for line in f:
            r=json.loads(line); crop='docs/harvest/'+r['crop'].split('docs/harvest/',1)[1]
            key=req['crop_to_id'].get(crop)
            if key in missing:als[key]=r;used.append(key);missing.remove(key)
    if used:receipt(p,used,'alignment')
assert not missing,('missing alignment',sorted(missing))
release=b/'l1e_20261017/l1r_sf4_3679725'
for mode in ('ensemble_ab','presence'):
    p=release/'release'/('overlay_'+mode+'.jsonl.gz')
    found={r['line_id']:r for r in selected(p,ids)}
    assert set(found)==ids,('missing decisions',mode,sorted(ids-set(found)))
    decisions[mode.upper()]=found;receipt(p,ids,'sf4_'+mode)
for p in (b/'output_3679313/run_receipt.json',b/'l1e_20261017/output_3679545/r1e_receipt.json',release/'receipt.json'):
    if p.exists():provenance.append(dict(kind='run_receipt',path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),receipt=json.loads(p.read_text())))
result=dict(schema='s8-selected-readonly-v1',complete=True,ids=sorted(ids),runtime=runtime,alignments=als,
    decisions=decisions,provenance=provenance,elapsed_seconds=time.monotonic()-start,
    remote_writes=0,submitted_jobs=0,inference_runs=0,
    custody_limit='Selected A fields compared exactly; shard receipts captured, full shard hashes not recomputed.')
sys.stdout.buffer.write(gzip.compress(json.dumps(result,ensure_ascii=False).encode()))
'''


def fetch(sources):
    dest = OUT / 'evidence/remote.json.gz'
    ids = sorted(sources)
    if dest.exists():
        data = json.loads(gzip.decompress(dest.read_bytes()))
        assert data['complete'] and set(data['ids']) == set(ids)
        return data
    if (dest.parent/'extraction_stop.json').exists():
        raise SystemExit('STOP: prior bounded extraction exhausted; no further SSH in S8a. See extraction_stop.json.')
    local_path=OUT/'evidence/local_alignments.json.gz'
    local=json.loads(gzip.decompress(local_path.read_bytes())) if local_path.exists() else {}
    req = dict(ids=ids, missing_alignment_ids=sorted(set(ids)-set(local)),crop_to_id={r['crop']:k for k,r in sources.items()})
    code = REMOTE.replace('REQUEST',base64.b64encode(json.dumps(req).encode()).decode())
    logpath=dest.parent/'fetch_log.json'
    logs=json.loads(logpath.read_text()) if logpath.exists() else []
    dest.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(1,5):
        start=time.monotonic()
        try:
            p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',
                '-o','ServerAliveInterval=10','-o','ServerAliveCountMax=2',
                '-o','StrictHostKeyChecking=yes','clariden','python3 -'],input=code.encode(),
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=105)
        except subprocess.TimeoutExpired:
            raise SystemExit('STOP: extraction exceeded 105 seconds; no retry')
        err=p.stderr.decode(errors='replace')
        logs.append(dict(attempt=attempt,seconds=time.monotonic()-start,returncode=p.returncode,stderr=err))
        logpath.write_text(json.dumps(logs,indent=2)+'\n')
        if p.returncode==0:
            data=json.loads(gzip.decompress(p.stdout))
            assert data['complete'] and set(data['ids'])==set(ids)
            data['alignments'].update(local)
            assert set(data['alignments'])==set(ids)
            data['local_alignment_custody']=dict(path=str(local_path),sha256=hashlib.sha256(local_path.read_bytes()).hexdigest(),
                source='.cache/labelfix/clariden/C1_alignments.jsonl.gz',lines=len(local))
            dest.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode()))
            print(json.dumps(dict(lines=len(ids),bytes=len(p.stdout),remote_seconds=data['elapsed_seconds'])),flush=True)
            return data
        if any(s in err.lower() for s in ('permission denied','certificate','authentication','host key verification')):
            raise SystemExit('STOP: auth/certificate/host-key failure; certificate not refreshed')
        transient=any(s in err.lower() for s in ('connection reset','connection timed out','connection closed','broken pipe','could not resolve hostname'))
        if not transient or attempt==4:raise SystemExit('STOP: Clariden extraction failed: '+err[-2000:])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True)
    fetch(json.loads(p.parse_args().sources.read_text()))
