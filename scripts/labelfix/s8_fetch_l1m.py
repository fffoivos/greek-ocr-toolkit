"""S8a2: adapt L1M's crop-key join and streaming shard selection, no inference.

Only the dedicated s8_dev_extract directory is writable remotely. Each shard
checkpoint survives a failed attempt; the partial payload is pulled in finally.
"""
from greekocr.ops.data_root import input_path as _data_input
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
import re

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/records/labelfix/spellcheck/S8_DEV/evidence'
L1 = ROOT.parent / 'greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence'

# S8a3's compute-only wrapper reuses the L1M selection and custody contract.
# Importing these helpers never invokes fetch() or supersedes its STOP marker.
S8_FIELDS = ('recogniser_text', 'recogniser_nfd', 'coverage', 'r1_predictions')
S8_KEEP = ('id',) + S8_FIELDS + ('peer_predictions', 'peer_coverage', 'k1_flags')
S8_ID = re.compile(rb'"id"\s*:\s*"([^\"]+)"')


def s8_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def s8_read_shard(task):
    """Read one saved shard; workers return results without writing any file."""
    kind, filename, wanted, crop_to_id = task
    path = Path(filename)
    before = path.stat()
    records = {}
    with gzip.open(path, 'rb') as stream:
        for line in stream:
            if kind == 'alignment':
                row = json.loads(line)
                crop = 'docs/harvest/' + row['crop'].split('docs/harvest/', 1)[1]
                key = crop_to_id.get(crop)
                if key not in wanted:
                    continue
                value = row
            else:
                match = S8_ID.search(line[:160])
                if not match or match[1].decode() not in wanted:
                    continue
                row = json.loads(line)
                key = row['id']
                hashes = {field: s8_digest(row[field]) for field in S8_FIELDS}
                if kind == 'BE':
                    value = {field: row[field] for field in S8_KEEP if field in row}
                    value.update(historical_field_sha256=hashes, BE_shard=path.name)
                else:
                    value = hashes
            if key in records:
                raise ValueError('duplicate selected ID in {}: {}'.format(path, key))
            records[key] = value
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('input changed during read: {}'.format(path))
    provenance = dict(kind=kind, path=str(path), file_bytes=after.st_size,
                      mtime_ns=after.st_mtime_ns, selected_ids=sorted(records))
    receipt = path.with_name(path.name.replace('-combined.jsonl.gz', '-receipt.json'))
    if records and receipt != path and receipt.exists():
        raw = receipt.read_bytes()
        provenance.update(receipt=json.loads(raw), receipt_sha256=hashlib.sha256(raw).hexdigest())
    return kind, path.name, records, provenance


REMOTE = r'''
import base64,gzip,hashlib,json,os,pathlib,re,signal,sys,time
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
request=json.loads(base64.b64decode('REQUEST'))
ids=set(request['ids']);missing_al=set(request['missing_alignment_ids']);started=time.monotonic()
b=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017')
out=b/'s8_dev_extract';out.mkdir(exist_ok=True)
fingerprint=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
identity=out/'request.json'
if identity.exists():assert json.loads(identity.read_text())==request,'scratch request differs'
else:identity.write_text(json.dumps(request,sort_keys=True))
checkpoint=out/'partial.json.gz'
data=json.loads(gzip.decompress(checkpoint.read_bytes())) if checkpoint.exists() else dict(
    schema='s8a2-l1m-selected-v1',runtime={},alignments={},provenance=[],BE_done=[],A_done=[],alignment_done=[],
    request_sha256=fingerprint,remote_scratch=str(out),submitted_jobs=0,inference_runs=0,workers=1,threads=1,
    custody_limit='Selected historical A fields compared exactly; shard receipts read; full shard hashes not recomputed.')
assert data['request_sha256']==fingerprint
pat=re.compile(rb'"id"\s*:\s*"([^\"]+)"')
fields=('recogniser_text','recogniser_nfd','coverage','r1_predictions')
keep=('id','recogniser_text','recogniser_nfd','coverage','r1_predictions','peer_predictions','peer_coverage','k1_flags')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def save():
    data['missing_runtime_ids']=sorted(ids-set(data['runtime']))
    data['missing_A_ids']=sorted(k for k in ids if not data['runtime'].get(k,{}).get('historical_A_verified'))
    data['missing_alignment_ids']=sorted(missing_al-set(data['alignments']))
    data['complete']=not any(data[k] for k in ('missing_runtime_ids','missing_A_ids','missing_alignment_ids'))
    tmp=out/'partial.tmp';tmp.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode(),compresslevel=3));tmp.replace(checkpoint)
def provenance(p,used,kind):
    e=dict(kind=kind,path=str(p),file_bytes=p.stat().st_size,selected_ids=sorted(used))
    rp=p.with_name(p.name.replace('-combined.jsonl.gz','-receipt.json'))
    if rp!=p and rp.exists():e.update(receipt=json.loads(rp.read_text()),receipt_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    data['provenance'].append(e)
def selected(p,wanted):
    with gzip.open(p,'rb') as f:
        for line in f:
            m=pat.search(line[:160])
            if m and m[1].decode() in wanted:yield json.loads(line)
def alarm(*args):raise TimeoutError('210 second extraction budget reached')
signal.signal(signal.SIGALRM,alarm);signal.alarm(210)
try:
    for p in sorted((b/'l1e_20261017/output_3679545/inference').glob('shard-*-combined.jsonl.gz')):
        if p.name in data['BE_done']:continue
        used=[]
        for r in selected(p,ids):
            key=r['id'];assert key not in data['runtime']
            # Remote detector evidence is neither fetched nor used. Recreate S6 locally.
            rr={k:r[k] for k in keep if k in r}
            rr['historical_field_sha256']={k:digest(r[k]) for k in fields}
            rr['BE_shard']=p.name;data['runtime'][key]=rr;used.append(key)
        if used:provenance(p,used,'BE')
        data['BE_done'].append(p.name);save()
        if set(data['runtime'])==ids:break
    assert set(data['runtime'])==ids,('missing runtime',sorted(ids-set(data['runtime'])))
    for name in sorted({r['BE_shard'] for r in data['runtime'].values()}):
        if name in data['A_done']:continue
        keys={k for k,r in data['runtime'].items() if r['BE_shard']==name};p=b/'output_3679313/combined'/name;seen=set()
        for old in selected(p,keys):
            key=old['id'];seen.add(key)
            for field in fields:assert digest(old[field])==data['runtime'][key]['historical_field_sha256'][field],(key,field,'historical A mismatch')
            data['runtime'][key]['historical_A_verified']=True
        assert seen==keys;provenance(p,keys,'A');data['A_done'].append(name);save()
    for p in sorted((b/'output_3679313/alignment').glob('worker_*.jsonl.gz')):
        if not missing_al-set(data['alignments']):break
        if p.name in data['alignment_done']:continue
        used=[]
        with gzip.open(p,'rt') as f:
            for line in f:
                r=json.loads(line);crop='docs/harvest/'+r['crop'].split('docs/harvest/',1)[1]
                key=request['crop_to_id'].get(crop)
                if key in missing_al and key not in data['alignments']:
                    data['alignments'][key]=r;used.append(key)
        if used:provenance(p,used,'alignment')
        data['alignment_done'].append(p.name);save()
    assert not missing_al-set(data['alignments']),('missing alignment',sorted(missing_al-set(data['alignments'])))
except Exception as exc:
    data['last_error']=repr(exc)
finally:
    signal.alarm(0);data['last_attempt_seconds']=time.monotonic()-started;save()
    sys.stdout.buffer.write(checkpoint.read_bytes())
'''


def fetch():
    ids=(E.parent/'S8_DEV_ids.txt').read_text().split()
    assert len(ids)==len(set(ids))==600
    sources=json.loads((E/'sources.json').read_text())
    local=json.loads(gzip.decompress((_data_input(E/'dev_c1_alignments.json.gz')).read_bytes()))
    request=dict(ids=sorted(ids),missing_alignment_ids=sorted(set(ids)-set(local)),
        crop_to_id={sources[k]['crop']:k for k in ids})
    logpath=E/'fetch_log.json';logs=json.loads(logpath.read_text())
    if not any(r.get('event')=='S8a2_supersedes_STOP' for r in logs):
        stop=E/'extraction_stop.json'
        logs.append(dict(event='S8a2_supersedes_STOP',brief='docs/records/briefs/S8a2_dev_evidence_resume.md',
            prior_stop=json.loads(stop.read_text()) if stop.exists() else None,
            budget=dict(attempts=3,seconds_per_attempt=240,remote_alarm=210,workers=1,threads=1),
            local_DEV_alignments=len(local),missing_DEV_alignments=len(request['missing_alignment_ids']),
            count_correction='Prior 441 cache records included 7 audit rows: actual DEV cache is 434, requiring 166, not 159.',
            extractor_source=str(L1/'fetch_selected.py'),
            extractor_source_sha256=hashlib.sha256((L1/'fetch_selected.py').read_bytes()).hexdigest()))
        logpath.write_text(json.dumps(logs,indent=2)+'\n')
        if stop.exists():stop.rename(E/'extraction_stop_S8a_superseded.json')
    dest=E/'remote.json.gz'
    if _data_input(dest).exists():
        data=json.loads(gzip.decompress(_data_input(dest).read_bytes()))
        assert data['complete'] and set(data['ids'])==set(ids)
        return
    if (E/'extraction_stop.json').exists():
        raise SystemExit('STOP: S8a2 fetch is stopped; a new coordinator budget is required.')
    attempts=sum(r.get('event')=='S8a2_attempt_started' for r in logs)
    code=REMOTE.replace('REQUEST',base64.b64encode(json.dumps(request).encode()).decode())
    data=None
    for attempt in range(attempts+1,4):
        logs.append(dict(event='S8a2_attempt_started',attempt=attempt,unix_time=time.time()))
        logpath.write_text(json.dumps(logs,indent=2)+'\n')
        started=time.monotonic();p=None;failure=None
        try:
            p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',
                '-o','ServerAliveInterval=10','-o','ServerAliveCountMax=2','-o','StrictHostKeyChecking=yes',
                'clariden','python3 -'],input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=238)
            error=p.stderr.decode(errors='replace')
        except subprocess.TimeoutExpired as exc:
            error=(exc.stderr or b'').decode(errors='replace');failure='local 238-second timeout'
        entry=dict(event='S8a2_attempt_result',attempt=attempt,seconds=time.monotonic()-started,
            returncode=p.returncode if p else None,stderr=error,failure=failure)
        data=None
        if p and p.stdout:
            try:
                data=json.loads(gzip.decompress(p.stdout))
                (E/f'remote_partial_attempt_{attempt}.json.gz').write_bytes(p.stdout)
                entry.update({k:data[k] for k in ('complete','missing_runtime_ids','missing_A_ids','missing_alignment_ids','last_attempt_seconds')})
                entry['last_error']=data.get('last_error')
            except (ValueError,OSError,EOFError) as exc:entry['payload_error']=repr(exc)
        logs.append(entry);logpath.write_text(json.dumps(logs,indent=2)+'\n')
        print(json.dumps({k:v for k,v in entry.items() if k!='stderr'}),flush=True)
        if any(s in error.lower() for s in ('permission denied','certificate','authentication','host key verification')):
            raise SystemExit('STOP: authentication/certificate failure; no refresh')
        if data and data['complete']:
            data['alignments'].update(local);data['ids']=sorted(ids)
            assert set(data['alignments'])==set(data['runtime'])==set(ids)
            data['local_alignment_custody']=dict(path=str(E/'dev_c1_alignments.json.gz'),
                sha256=hashlib.sha256((_data_input(E/'dev_c1_alignments.json.gz')).read_bytes()).hexdigest())
            dest.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode()))
            print('COMPLETE: 600 DEV runtimes, 600 alignments; no SF4 overlays fetched',flush=True)
            return
    missing={k:data[k] for k in ('missing_runtime_ids','missing_A_ids','missing_alignment_ids')} if data else dict(
        missing_runtime_ids=sorted(ids),missing_A_ids=sorted(ids),missing_alignment_ids=request['missing_alignment_ids'])
    (E/'extraction_stop.json').write_text(json.dumps(dict(status='STOP',budget='S8a2 exhausted',
        blocking_stage='SSH transport / no successfully pulled payload',missing_locally=missing,
        remote_checkpoint_state='unknown; do not probe after budget exhaustion',local_partial_payloads=bool(data)),indent=2)+'\n')
    raise SystemExit('STOP: three S8a2 attempts exhausted; see exact locally missing stage/ID lists. Remote checkpoint state is unknown if no payload arrived.')


if __name__=='__main__':fetch()
