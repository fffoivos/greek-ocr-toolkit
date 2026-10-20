"""Verify selected R2 readback payloads and explicitly separate envelope hashes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def verify(root, envelope_manifest, started, remote=None, selection=None):
    expected={}; sources={}
    def bind(name, value, source):
        if name in expected and expected[name]!=value: raise ValueError('conflicting receipt hashes: '+name)
        expected[name]=value;sources.setdefault(name,[]).append(source)
    for p in sorted(root.glob('stage_*.json')):
        r=json.loads(p.read_text())
        if not r['complete']: raise ValueError('incomplete stage')
        for name,h in r['sha256'].items(): bind(name,h,p.name)
    for p in sorted((root/'B').glob('chunk-*.receipt.json')):
        r=json.loads(p.read_text())
        if not r['complete']: raise ValueError('incomplete chunk')
        for name,h in r['sha256'].items(): bind('B/'+name,h,str(p.relative_to(root)))
    for p in sorted((root/'C').glob('*/DONE')):
        r=json.loads(p.read_text());prefix=str(p.parent.relative_to(root))+'/'
        bind(prefix+'best.pt',r['best_sha256'],str(p.relative_to(root)))
        bind(prefix+'heldout_predictions.jsonl',r['predictions_sha256'],str(p.relative_to(root)))
    for p in sorted(root.rglob('*_predictions.receipt.json')):
        r=json.loads(p.read_text())
        name=str(p.relative_to(root)).replace('_predictions.receipt.json','_predictions.jsonl')
        bind(name,r['prediction_sha256'],str(p.relative_to(root)))
    envelopes={}
    for line in envelope_manifest.read_text().splitlines():
        h,name=line.split(maxsplit=1)
        name=name.strip()
        envelopes[name.removeprefix('output_3681404/').removeprefix('logs/')]=h
    files=[];failures=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name=='READBACK_RECEIPT.json': continue
        name=str(p.relative_to(root));actual=sha(p)
        wanted=expected.get(name,envelopes.get(name))
        match=actual==wanted
        files.append(dict(path=name,size_bytes=p.stat().st_size,sha256=actual,
            receipt_match='yes' if name in expected and match else 'no',
            receipt_sources=sources.get(name,[]),
            verification='stage/chunk receipt' if name in expected else 'remote envelope SHA256',
            sha256_verified=match))
        if not match: failures.append(name)
    selected=set(selection) if selection is not None else set(expected)
    missing=sorted(selected-{r['path'] for r in files})
    failures+=missing
    if selection is not None:
        failures+=sorted({r['path'] for r in files}-selected)
    result=dict(schema='r2-readback-v1',pull_start_time=started,pull_end_time=datetime.now(timezone.utc).isoformat(),
        remote=remote or '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/',
        files=files,file_count=len(files),total_bytes=sum(r['size_bytes'] for r in files),
        receipt_matched=sum(r['receipt_match']=='yes' for r in files),
        sha256_verified=sum(r['sha256_verified'] for r in files),failures=failures,
        envelope_note='Root stage/run/input receipts and Slurm log have no parent stage/chunk hash; verified against separately captured remote SHA256 manifest. receipt_match=no means no parent receipt, not a hash mismatch.',
        coordinator_accepted_deviation="R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)",
        missing_stage_payloads=missing,
        intentionally_not_pulled=sorted(set(expected)-selected) if selection is not None else [])
    (root/'READBACK_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    if failures: raise ValueError('READBACK VERIFICATION FAILED: '+repr(failures))
    return {k:v for k,v in result.items() if k!='files'}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root',type=Path);ap.add_argument('envelope_manifest',type=Path);ap.add_argument('start',type=Path)
    ap.add_argument('--remote',help='Readback source metadata; receipt schema unchanged')
    ap.add_argument('--selection',type=Path,help='Explicit selected-file list; unselected stage payloads are recorded, not required')
    a=ap.parse_args();print(json.dumps(verify(a.root,a.envelope_manifest,a.start.read_text().strip(),a.remote,a.selection.read_text().splitlines() if a.selection else None),indent=2))
