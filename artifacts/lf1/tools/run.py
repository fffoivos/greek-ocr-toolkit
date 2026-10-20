"""Lead-operated LF1 fleet. Building/testing this module never launches a model."""
import argparse
import concurrent.futures
import fcntl
import glob
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
import scan_rollout
from lf1 import BASE, SCANNER_SHA, sha, rows, dump, require_budget, map_context

EXTRA_CONTEXTS = {
    'candidate_w2_00004': 'coordinator 20 Oct ~06:20 (VOID is a reader-process failure)',
    'candidate_w2_00013': 'coordinator 20 Oct ~06:20 (VOID is a reader-process failure)',
    'candidate_w1b_00008': 'coordinator 20 Oct ~06:27 GO (then the VOID re-reads)',
}
LOCK = threading.Lock()
FLAGS = ['-c','approval_policy=never','-c','project_doc_max_bytes=0',
         '-c','features.multi_agent=false','-c','features.remote_plugin=false',
         '-c','features.apps=false','-c','sandbox_workspace_write.network_access=false',
         '-c','web_search="disabled"','--skip-git-repo-check']

def metadata(log):
    cleaned=re.sub(r'\x1b\[[0-9;]*m','',log)
    match=re.search(r'session id: ([0-9a-f-]+)',cleaned)
    if not match: raise ValueError('session id missing')
    files=glob.glob(str(Path.home()/'.codex/sessions/*/*/*'/('rollout-*'+match[1]+'.jsonl')))
    if len(files)!=1: raise ValueError('unique rollout not found')
    rollout=Path(files[0]); records=rows(rollout); model=None;effort=None;usage=None;weekly=None;limits=None
    for record in records:
        p=record.get('payload') or {}
        if not isinstance(p,dict):continue
        if record.get('type')=='turn_context':
            model=p.get('model',model);effort=p.get('effort',p.get('reasoning_effort',effort))
        if p.get('type')=='token_count':
            usage=(p.get('info') or {}).get('total_token_usage') or usage
            rl=p.get('rate_limits') or {}
            if rl.get('limit_id')=='codex':
                for bucket in (rl.get('primary'),rl.get('secondary')):
                    if bucket and bucket.get('window_minutes')==10080:
                        weekly=bucket['used_percent'];limits=rl
    return dict(rollout=str(rollout),rollout_sha256=sha(rollout),model=model,effort=effort,
                usage=usage,weekly_used=weekly,rate_limits=limits)

def probe(tag):
    # Same one-word, non-ephemeral probe as TR2; no credits/provider API.
    dest=BASE/'runs/probes'/tag;dest.mkdir(parents=True,exist_ok=False)
    for n in range(3):
        completed=subprocess.run(['codex','exec','-m','gpt-6.1-sol','-c','model_reasoning_effort=low',
                 *FLAGS,'--sandbox','read-only','-C',str(dest),'Reply with the single word ok.'],
                 stdin=subprocess.DEVNULL,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (dest/f'p{n}.log').write_text(completed.stdout)
        try:
            result=metadata(completed.stdout)
            if completed.returncode==0 and result['weekly_used'] is not None:
                result.update(tag=tag,time=time.time());dump(dest/'receipt.json',result);return result
        except ValueError:pass
    raise RuntimeError('no codex 10080-minute bucket; probe unavailable')

def verify(context):
    if sha(BASE/'tools/scan_rollout.py')!=SCANNER_SHA:raise ValueError('scanner hash changed')
    dependency_hashes=json.loads((BASE/'receipts/build.json').read_text())['scanner_dependencies']
    for name,digest in dependency_hashes.items():
        if sha(BASE/'tools'/name)!=digest:raise ValueError('scanner dependency changed: '+name)
    if sha(context['manifest'])!=context['manifest_sha256']:raise ValueError('manifest custody changed')
    if sha(context['key'])!=context['key_sha256']:raise ValueError('key custody changed')
    errors,skipped=scan_rollout.integrity(Path(context['directory']))
    if errors or skipped:raise ValueError('pack integrity: '+str(errors))

def fresh(context, number=2):
    # Re-read uses originals only, never the previous answers/zoom tree.
    old=Path(context['directory']);directory=old.with_name(old.name+('_retry' if number==2 else f'_retry{number}'))
    directory.mkdir(exist_ok=False)
    manifest=json.loads(Path(context['manifest']).read_text())
    for rel in manifest['files']:
        dest=directory/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(old/rel,dest)
    mp=directory.parent/f'MANIFEST.{directory.name}.json';dump(mp,manifest)
    return context|dict(directory=str(directory),manifest=str(mp),manifest_sha256=sha(mp))

def prompt_for(context):
    prompt=Path(context.get('prompt', BASE/'prompts/lf1.md'))
    expected=context.get('prompt_sha256') if 'prompt' in context else json.loads(
        (BASE/'receipts/prompt_receipt.json').read_text())['prompt_sha256']
    if sha(prompt)!=expected:raise ValueError('prompt custody changed')
    return prompt


def attempt(context, number, probe_fn=probe, read_fn=None, scan_fn=None):
    tag=context['name']+f'.attempt{number}';destination=BASE/'runs'/tag
    destination.mkdir(parents=True,exist_ok=False)
    receipt=dict(context=context['name'],attempt=number,status='VOID',directory=context['directory'],
                 cards=context['cards'],bed=context['bed'],controls=context['controls'],
                 scanner_sha256=SCANNER_SHA,started_at=time.time())
    if number==3:receipt['authorised_by']=EXTRA_CONTEXTS[context['name']]
    try:
        verify(context)
        with LOCK:
            receipt['before']=probe_fn(tag+'_before')
            require_budget(receipt['before']['weekly_used'])
    except Exception as exc:
        receipt.update(status='REFUSED',reason=str(exc),finished_at=time.time())
        dump(destination/'receipt.json',receipt);return receipt
    try:
        prompt=prompt_for(context)
        receipt.update(prompt=str(prompt),prompt_sha256=sha(prompt))
        if read_fn:
            meta=read_fn(context,destination)
        else:
            started=time.monotonic()
            with prompt.open() as stdin, (destination/'codex.log').open('w') as log:
                completed=subprocess.run(['codex','exec','-m','gpt-6.1-sol','-c','model_reasoning_effort=medium',
                    *FLAGS,'--sandbox','workspace-write','-C',context['directory'],
                    '-o',str(destination/'final.md'),'-'],stdin=stdin,stdout=log,stderr=subprocess.STDOUT)
            meta=metadata((destination/'codex.log').read_text())
            meta.update(rc=completed.returncode,wall_s=time.monotonic()-started)
        receipt['run']=meta
        # Scan every located reader rollout, including failed CLI contexts.
        scan=(scan_fn or scan_rollout.inspect)(Path(meta['rollout']),Path(context['directory']))
        scan['scanner_sha256']=SCANNER_SHA;dump(destination/'scan.json',scan)
        receipt['scan_sha256']=sha(destination/'scan.json')
        if not scan['ok'] or meta['rc']!=0:raise ValueError('VOID rollout: scan or CLI failure')
        if meta['model']!='gpt-6.1-sol' or meta['effort']!='medium':raise ValueError('wrong model or effort')
        mapped=map_context(context['directory'],context['key'],destination)
        receipt.update(status='VALID',mapping=mapped)
    except Exception as exc:
        receipt['reason']=str(exc)
    finally:
        try:
            with LOCK:receipt['after']=probe_fn(tag+'_after')
        except Exception as exc:
            receipt.update(status='VOID',reason='post-probe failed: '+str(exc))
        receipt['finished_at']=time.time()
        if receipt['status']=='VOID' and number in (2,3):
            receipt['no_verdict']=f'no verdict (reader VOID x{number})'
        dump(destination/'receipt.json',receipt)
    return receipt

def worker(context, extra_attempt=False):
    records=[]
    # Existing attempt 3 is history even on a later default invocation.
    third=BASE/'runs'/(context['name']+'.attempt3')/'receipt.json'
    numbers=(1,2,3) if extra_attempt or third.exists() else (1,2)
    for number in numbers:
        path=BASE/'runs'/(context['name']+f'.attempt{number}')/'receipt.json'
        if path.exists():
            record=json.loads(path.read_text())
        else:
            current=(fresh(context) if number==2 else fresh(context,3)) if number>1 else context
            record=attempt(current,number)
        records.append(record)
        # Default: one fresh retry. Named coordinator authorization allows one more.
        if record['status']!='VOID':break
    return records

def control_review():
    path=BASE/'keys/control_pixel_review.json'
    if not path.exists():raise ValueError('lead pixel check pending; see DRYRUN_PLAN.md')
    review=json.loads(path.read_text());pool=json.loads((BASE/'keys/control_pool.json').read_text())
    if review.get('pool_sha256')!=sha(BASE/'keys/control_pool.json'):raise ValueError('pixel review pool hash differs')
    if set(review.get('approved_pool_ids',[]))!={p['pool_id'] for p in pool}:raise ValueError('lead must review all frozen controls')

def main():
    p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--contexts',type=Path,default=BASE/'contexts.json')
    p.add_argument('--extra-attempt',nargs='+',default=[],help='authorized attempt 3; run only these named contexts')
    args=p.parse_args()
    if set(args.extra_attempt)-EXTRA_CONTEXTS.keys():p.error('attempt 3 is authorized only for '+', '.join(sorted(EXTRA_CONTEXTS)))
    if not 1<=args.jobs<=24:p.error('--jobs must be 1..24')
    control_review()
    (BASE/'runs').mkdir(exist_ok=True)
    # Single fleet writer across invocations; prevents duplicate runs/retries.
    with (BASE/'runs/fleet.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        contexts=json.loads(args.contexts.read_text())
        if set(args.extra_attempt)-{c['name'] for c in contexts}:p.error('extra-attempt context absent from roster')
        if args.extra_attempt:contexts=[c for c in contexts if c['name'] in args.extra_attempt]
        names={c['name'] for c in contexts}
        historical=json.loads((BASE/'ledger.json').read_text()) if (BASE/'ledger.json').exists() else []
        historical=[r for r in historical if r['context'] not in names]
        for c in contexts:verify(c)
        ledgers=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures={executor.submit(worker,c,c['name'] in args.extra_attempt):c for c in contexts}
            for future in concurrent.futures.as_completed(futures):
                ledgers.append(future.result())
                dump(BASE/'ledger.json',historical+[r for group in ledgers for r in group])
        ledgers.sort(key=lambda group:next(i for i,c in enumerate(contexts) if c['name']==group[-1]['context']))
        ledger=historical+[r for group in ledgers for r in group];dump(BASE/'ledger.json',ledger)
        # Aggregate only the terminal VALID attempt per logical context; preserve all receipts.
        verdicts=[]
        for context,group in zip(contexts,ledgers):
            last=group[-1]
            if last['status']=='VALID' and context.get('reread')!='vertical_turned':
                for r in rows(BASE/'runs'/(context['name']+f'.attempt{last["attempt"]}')/'verdicts.jsonl'):
                    verdicts.append(r|dict(context=context['name']))
        from lf1 import jsonl
        if any(c.get('reread')!='vertical_turned' for c in contexts):
            jsonl(BASE/'verdicts.jsonl',verdicts)
        vertical_contexts=[c for c in contexts if c.get('reread')=='vertical_turned']
        if vertical_contexts:
            from prod_map import map_lines, merge_vertical
            first_rosters={p for c in vertical_contexts for p in c['first_rosters']}
            first_contexts=[c for p in sorted(first_rosters) for c in json.loads(Path(p).read_text())]
            _,paired=merge_vertical(map_lines(first_contexts,ledger,BASE/'runs'),
                                   map_lines(vertical_contexts,ledger,BASE/'runs'))
            output=BASE/'prod/vertical_reread_verdicts.jsonl'
            previous={r['line_id']:r for r in rows(output)} if output.exists() else {}
            previous.update({r['line_id']:r for r in paired})
            jsonl(output,list(previous.values()))
        print(json.dumps(dict(contexts=len(contexts),statuses=[group[-1]['status'] for group in ledgers])))

if __name__=='__main__':main()
