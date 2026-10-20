#!/usr/bin/env python3
"""Checksum transfer of an explicit retained set, under the stopped-run lock."""
import argparse,os,shutil,sqlite3,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import lock,read_json,write_json,sha,atomic_bytes,scrub
from worker.runtime import ROOT,settings

TOP=('runtime_config.json','collector.log','collector.exit','c1_gate.json','ledger.jsonl','retention_projection.json')
TREES=('responses','resolution','cache/pages','cache/render_bindings','cache/resolved')


def retained(out):
    out=Path(out).resolve();names=set(read_json(ROOT/'worker/planned_inputs.json')['sha256'])
    names.update(name for name in TOP if (out/name).is_file())
    for tree in (*TREES,*(wave+'/'+name for wave in ('W1','W2') for name in ('pages','errors','audits','c1','c2'))):
        for p in (out/tree).rglob('*'):
            if p.is_symlink():raise ValueError('retained symlink refused')
            if p.is_file():names.add(str(p.relative_to(out)))
    for wave in ('W1','W2'):
        for name in ('state.json','receipt.json','resolved_manifest.jsonl'):
            p=out/wave/name
            if p.is_file():names.add(str(p.relative_to(out)))
        for path in (out/wave/'pages').glob('*.json'):
            page=read_json(path)
            analysis=page.get('analysis_page',page)
            if analysis.get('source_pdf_retained'):
                pdf=Path(analysis['source_pdf_cache']).resolve()
                if not pdf.is_relative_to(out) or not pdf.is_file():raise ValueError('retained PDF exception missing/outside run root')
                names.add(str(pdf.relative_to(out)))
    result=[];credential=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    for name in sorted(names):
        p=out/name
        if not p.exists():continue
        if p.is_symlink() or not p.resolve().is_relative_to(out) or not p.is_file():raise ValueError('invalid retained path')
        if credential and p.resolve()==Path(credential).resolve():raise ValueError('credential file encountered; sync refused')
        if '\n' in name or '\r' in name or '\\' in name:raise ValueError('unsafe checksum path')
        result.append(p)
    return result


def transfer(c,destination,execute=False):
    if not destination or destination.startswith('-') or '\n' in destination:raise ValueError('invalid destination')
    out=Path(c['output_root']).resolve()
    if Path(c['cache']).resolve()!=out/'cache':raise ValueError('sync requires cache inside output root')
    from worker.control import alive
    if alive(out):raise ValueError('stop the collector before a consistent sync')
    with lock(out/'run.lock',blocking=False),lock(out/'launch.lock',blocking=False):
        files=retained(out)
        # Stage on the same filesystem: hardlinks cost no second raster copy.
        stage=Path(tempfile.mkdtemp(prefix='.sync-',dir=out))
        try:
            for src in files:
                dst=stage/src.relative_to(out);dst.parent.mkdir(parents=True,exist_ok=True);os.link(src,dst)
            if (out/'ledger.sqlite3').exists():
                source=sqlite3.connect((out/'ledger.sqlite3').as_uri()+'?mode=ro',uri=True)
                target=sqlite3.connect(stage/'ledger.sqlite3')
                try:source.backup(target)
                finally:target.close();source.close()
            limiter=Path(c['limiter_root'])
            for source in sorted(limiter.glob('*.json')):
                if source.is_symlink():raise ValueError('limiter symlink refused')
                target=stage/'shared_limiter'/source.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target)
            hashes={str(p.relative_to(stage)):sha(p) for p in sorted(stage.rglob('*')) if p.is_file()}
            checksum=''.join(digest+'  '+name+'\n' for name,digest in hashes.items())
            (stage/'retained_SHA256SUMS').write_text(checksum)
            command=['rsync','-a','--checksum','--itemize-changes']
            if not execute:command.append('--dry-run')
            command+=['--',str(stage)+'/',destination]
            result=subprocess.run(command,capture_output=True,text=True)
            if result.returncode:raise RuntimeError('rsync failed: '+scrub(result.stderr))
            print(scrub(result.stdout),end='')
            if execute:
                check=subprocess.run(['rsync','-rcn','--itemize-changes','--',str(stage)+'/',destination],capture_output=True,text=True)
                if check.returncode or check.stdout.strip():raise RuntimeError('post-sync checksum comparison failed')
            atomic_bytes(out/'retained_SHA256SUMS',checksum.encode())
            receipt=dict(status='ok',created_utc=datetime.now(timezone.utc).isoformat(),destination=scrub(destination),execute=execute,dry_run=not execute,files=len(hashes),bytes=sum((stage/name).stat().st_size for name in hashes),checksum_manifest_sha256=sha(stage/'retained_SHA256SUMS'),post_sync_checksum_match=True if execute else None)
            write_json(out/'sync_receipt.json',receipt)
            print('retained sync: '+('verified' if execute else 'dry run only'))
            return receipt
        finally:shutil.rmtree(stage)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('destination');a=p.parse_args()
    try:transfer(settings(),a.destination,a.execute)
    except Exception as e:print('sync: '+scrub(e),file=sys.stderr);sys.exit(1)
