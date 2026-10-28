"""External retry adapter; never installed under a sealed greekocr code directory.

Default is read-only test-only. Execution reuses census04.run and its exact ledger
binding, retry_errors=True and retry_holds=False. No configuration is rewritten.
"""
import argparse
import hashlib
import importlib
import json
import pathlib
import sqlite3
import subprocess
import sys

BINDING_SHA = '3e05d2f2b5b908f11e20010c7f85dc046920717590f82ba1520f7b0df92febe4'
TERMINAL = {'COMPLETED','FAILED','TIMEOUT','CANCELLED','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE','REVOKED'}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def snapshot(attempt):
    db = sqlite3.connect(f'file:{pathlib.Path(attempt)}/ledger.sqlite?mode=ro', uri=True, timeout=10)
    try:
        db.execute('PRAGMA query_only=ON'); db.execute('BEGIN')
        binding = db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0]
        generation = int(db.execute("SELECT value FROM run WHERE key='generation'").fetchone()[0])
        total = db.execute('SELECT count(*) FROM observations').fetchone()[0]
        counts = dict(db.execute('SELECT disposition,count(*) FROM decisions GROUP BY disposition'))
        errors = {}; stable = hashlib.sha256(); keys = hashlib.sha256()
        # The comparison fixes the former error set, including errors that recover.
        for parent, rid, disposition, payload in db.execute('SELECT parent,id,disposition,payload FROM decisions ORDER BY parent,id'):
            keys.update((canonical([parent,rid])+'\n').encode())
            if disposition == 'INFRA_ERROR': errors[(parent,rid)] = sha(payload.encode())
            else: stable.update((canonical([parent,rid,payload])+'\n').encode())
        return dict(binding=json.loads(binding),binding_sha256=sha(binding.encode()),generation=generation,total=total,counts=counts,errors=errors,nonerror_sha256=stable.hexdigest(),keys_sha256=keys.hexdigest())
    finally:
        db.close()

def check_ended(job):
    # Finished jobs can leave Slurm's live cache before sacct retention ends.
    # An unfiltered queue query remains valid when that job ID has expired.
    queue = subprocess.check_output(['squeue','-h','-o','%i|%T'], text=True)
    queued = '\n'.join(line for line in queue.splitlines() if line.split('|')[0] == str(job))
    if queued.strip(): raise ValueError('original job remains in queue: '+queued.strip())
    rows = subprocess.check_output(['sacct','-X','-n','-P','-j',str(job),'--format=JobIDRaw,State,ExitCode'],text=True)
    found = [line.split('|') for line in rows.splitlines() if line.split('|')[0] == str(job)]
    if len(found)!=1 or found[0][1].split()[0] not in TERMINAL:
        raise ValueError('original job not confirmed terminal: '+rows)
    return found[0]

def preflight(config, attempt, module, expected_binding):
    before = snapshot(attempt)
    if before['binding_sha256'] != expected_binding: raise ValueError('unexpected ledger binding')
    effective = dict(config, routes_out_of_scope=module.census.validate_routes_out_of_scope(config.get('routes_out_of_scope', [])))
    if effective != before['binding']['config']: raise ValueError('configuration differs from original ledger')
    if module.census.code_binding() != before['binding']['code']: raise ValueError('sealed code binding differs')
    for field, key in [('versions','versions_sha256'),('metadata','metadata_sha256'),('predictor','predictor_sha256')]:
        if before['binding'][key] is not None and module.census.file_sha(config[field]) != before['binding'][key]: raise ValueError(field+' differs')
    if sum(before['counts'].values()) != before['total']:
        raise ValueError('UNPROCESSED rows remain; retry_errors would also process them. Resume original execution first.')
    if not before['errors']: raise ValueError('no INFRA_ERROR rows to retry')
    return before

def compare(attempt, before, result):
    db = sqlite3.connect(f'file:{pathlib.Path(attempt)}/ledger.sqlite?mode=ro',uri=True)
    stable = hashlib.sha256(); keys = hashlib.sha256(); changed = []; unexpected = []
    try:
        for parent,rid,disposition,payload in db.execute('SELECT parent,id,disposition,payload FROM decisions ORDER BY parent,id'):
            key = (parent,rid); keys.update((canonical([parent,rid])+'\n').encode())
            if key in before['errors']:
                if sha(payload.encode()) != before['errors'][key]: changed.append(list(key))
            else: stable.update((canonical([parent,rid,payload])+'\n').encode())
        binding = db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0]
        generation = int(db.execute("SELECT value FROM run WHERE key='generation'").fetchone()[0])
    finally: db.close()
    checks = dict(binding_unchanged=sha(binding.encode())==before['binding_sha256'],
                  generation_plus_one=generation==before['generation']+1,
                  decision_keys_unchanged=keys.hexdigest()==before['keys_sha256'],
                  former_nonerrors_byte_unchanged=stable.hexdigest()==before['nonerror_sha256'],
                  infra_error_zero=not result['dispositions'].get('INFRA_ERROR'),
                  unprocessed_zero=not result['dispositions'].get('UNPROCESSED'),complete=result['complete'])
    return dict(status='PASS' if all(checks.values()) else 'HOLD',checks=checks,
                before_generation=before['generation'],after_generation=generation,
                binding_sha256=sha(binding.encode()),former_errors=len(before['errors']),changed_former_errors=changed,
                dispositions=result['dispositions'])

def retry(config, attempt, module, before, **test_kwargs):
    # No patching or wrapper inside the sealed package; forwarding is supported.
    result = module.run(config, str(attempt), execute=True, retry_errors=True, retry_holds=False, **test_kwargs)
    return compare(attempt,before,result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--code-root',type=pathlib.Path,required=True)
    p.add_argument('--config',type=pathlib.Path,required=True)
    p.add_argument('--attempt',type=pathlib.Path,required=True)
    p.add_argument('--original-job',required=True)
    p.add_argument('--expect-binding-sha256',default=BINDING_SHA)
    p.add_argument('--test-only',action='store_true')
    p.add_argument('--execute',action='store_true')
    p.add_argument('--receipt',type=pathlib.Path)
    a=p.parse_args()
    if a.test_only and a.execute: p.error('choose test-only or execute')
    if a.execute and not a.receipt: p.error('--execute requires an external --receipt')
    root=a.code_root.resolve()
    if a.receipt and (a.receipt.resolve().is_relative_to(root) or a.receipt.resolve().is_relative_to(a.attempt.resolve())):
        p.error('receipt must be outside sealed code and attempt')
    if any(k=='greekocr' or k.startswith('greekocr.') for k in sys.modules): raise RuntimeError('greekocr imported before selecting sealed root')
    sys.path.insert(0,str(root))
    module=importlib.import_module('greekocr.harvest.line_pipeline_census04')
    if not pathlib.Path(module.__file__).resolve().is_relative_to(root): raise RuntimeError('wrong census04 import')
    config=json.loads(a.config.read_text())
    before=preflight(config,a.attempt,module,a.expect_binding_sha256)
    receipt=dict(status='TEST_ONLY_PASS',processing_started=False,config_path=str(a.config),config_sha256=sha(a.config.read_bytes()),
                 code_root=str(root),census04_path=module.__file__,binding_sha256=before['binding_sha256'],generation=before['generation'],
                 former_errors=len(before['errors']),dispositions=before['counts'],execute_kwargs=dict(execute=True,retry_errors=True,retry_holds=False))
    if a.execute:
        receipt['original_job_terminal']=check_ended(a.original_job)
        # A single coordinator-launched writer; never execute concurrently with the original job.
        receipt.update(retry(config,a.attempt,module,before),processing_started=True)
        a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if receipt['status']=='HOLD': raise SystemExit(2)

if __name__=='__main__': main()
