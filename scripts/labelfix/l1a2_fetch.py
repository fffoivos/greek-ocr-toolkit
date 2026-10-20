"""Bounded, read-only extraction of exactly the L1A2 overlay selection."""
from greekocr.ops.data_root import input_path as _data_input
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ROOT / 'docs/records/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl'
OUT = ROOT / 'docs/records/labelfix/spellcheck/S8_DEV/private/audit100'
REMOTE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'selected_overlays.json.gz'
    if _data_input(dest).exists():
        raise SystemExit('Existing extraction retained; no SSH repeated.')
    if (OUT / 'extraction_stop.json').exists():
        raise SystemExit('STOP: prior extraction stopped; no SSH repeated.')
    rows = [json.loads(s) for s in SELECTION.read_text().splitlines()]
    ids = sorted(r['line_id'] for r in rows)
    assert len(ids) == len(set(ids)) == 100
    selection_sha = hashlib.sha256(SELECTION.read_bytes()).hexdigest()
    assert selection_sha == json.loads(SELECTION.with_name('audit100_receipt.json').read_text())['sha256']
    req = base64.b64encode(json.dumps(dict(ids=ids, path=REMOTE, selection_sha256=selection_sha)).encode()).decode()
    code = '''import base64,gzip,hashlib,json,pathlib,re,signal,sys,time
req=json.loads(base64.b64decode('REQUEST'))
signal.alarm(150)
start=time.monotonic(); p=pathlib.Path(req['path']); before=p.stat()
wanted=set(req['ids']); found={}; scanned=0; selected_raw=hashlib.sha256()
pat=re.compile(rb'"line_id"\\s*:\\s*"([^"\\n]+)"')
with gzip.open(p,'rb') as f:
    for raw in f:
        scanned+=1
        match=pat.search(raw)
        if not match: raise RuntimeError('line_id missing from overlay record')
        ident=match[1].decode()
        if ident in wanted:
            assert ident not in found, ('duplicate selected line',ident)
            found[ident]=json.loads(raw); selected_raw.update(raw)
        if len(found)==len(wanted): break
assert set(found)==wanted, ('missing selected lines',sorted(wanted-set(found)))
after=p.stat(); assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
receipt=dict(remote_path=str(p),remote_bytes=before.st_size,remote_mtime_ns=before.st_mtime_ns,
    selection_sha256=req['selection_sha256'],selected_count=len(found),records_scanned=scanned,
    selected_raw_sha256=selected_raw.hexdigest(),elapsed_seconds=time.monotonic()-start,
    scan='gzip stream; stopped after final selected record; full source hash not recomputed',
    remote_writes=0,submitted_jobs=0,inference_runs=0)
sys.stdout.buffer.write(gzip.compress(json.dumps(dict(records=[found[k] for k in req['ids']],receipt=receipt),ensure_ascii=False).encode()))
'''.replace('REQUEST', req)
    logpath = OUT / 'extraction_log.json'
    logs = json.loads(logpath.read_text()) if logpath.exists() else []
    # Bound total SSH invocations across restarts as well as transient retries.
    if len(logs) >= 3:
        raise SystemExit('STOP: three recorded SSH invocations exhausted')
    for attempt in range(len(logs)+1, 4):
        start = time.monotonic()
        try:
            p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                '-o', 'ConnectionAttempts=1', '-o', 'ServerAliveInterval=10',
                '-o', 'ServerAliveCountMax=2', '-o', 'StrictHostKeyChecking=yes',
                '-o', 'UpdateHostKeys=no', 'clariden', 'python3 -'],
                input=code.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        except subprocess.TimeoutExpired:
            (OUT / 'extraction_stop.json').write_text(json.dumps(dict(reason='180-second extraction timeout; no retry'))+'\n')
            raise SystemExit('STOP: extraction time limit exceeded')
        err = p.stderr.decode(errors='replace')
        logs.append(dict(attempt=attempt, elapsed_seconds=time.monotonic()-start, returncode=p.returncode, stderr=err))
        (OUT / 'extraction_log.json').write_text(json.dumps(logs, indent=2)+'\n')
        if p.returncode == 0:
            data = json.loads(gzip.decompress(p.stdout))
            assert {r['line_id'] for r in data['records']} == set(ids)
            dest.write_bytes(p.stdout)
            receipt = dict(data['receipt'], local_sha256=hashlib.sha256(p.stdout).hexdigest(), local_bytes=len(p.stdout))
            (OUT / 'extraction_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
            print(json.dumps(receipt))
            return
        auth = any(s in err.lower() for s in ('permission denied', 'certificate', 'authentication', 'host key verification'))
        transient = any(s in err.lower() for s in ('connection reset', 'connection timed out', 'connection closed', 'broken pipe', 'could not resolve hostname'))
        if auth or not transient or attempt == 3:
            (OUT / 'extraction_stop.json').write_text(json.dumps(dict(reason=err, returncode=p.returncode, auth_or_cert=auth))+'\n')
            raise SystemExit('STOP: '+err[-2000:])


if __name__ == '__main__':
    main()
