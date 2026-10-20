"""Exact Mac mock / Clariden R2 A-D entry point. Never submits or allocates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from scripts.labelfix.clariden.r1_common import sha256, verify_receipt, write_json, rows, canonical_doc, canonical_line
from scripts.labelfix.clariden.r2_teacher import export, code_binding, TEACHER_SHA, ROLES
from greekocr.labelfix.release_gate import policy_binding

from scripts.labelfix.clariden.r2_util import atomic_json as write_json

def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def validate(cfg,mock):
    if bool(cfg['mock'])!=mock: raise ValueError('mock/production configuration mismatch')
    for p,h in cfg['sha256'].items():
        if sha256(p)!=h: raise ValueError('input hash mismatch: '+p)
    if policy_binding()!=cfg['policy']: raise ValueError('frozen release policy changed')
    for path in ('data','heldout'): verify_receipt(cfg[path])
    if sha256(cfg['teacher'])!=TEACHER_SHA: raise ValueError('not frozen R1-A teacher')
    if cfg.get('manifest') and cfg['manifest'] not in cfg['sha256']: raise ValueError('unbound R2a manifest')
    if not cfg.get('line_list'): raise ValueError('PENDING: lead-supplied R2C line list / roles required')
    if cfg['line_list'] not in cfg['sha256']: raise ValueError('unbound population')
    population=list(rows(cfg['line_list']))
    if mock and len(population)>64: raise ValueError('Mac line budget exceeded')
    if not mock:
        if not cfg.get('roles') or cfg['roles'] not in cfg['sha256']: raise ValueError('missing hash-bound R2C roles')
        rb=json.loads(Path(cfg['roles']).read_text())
        if {r['line_id'] for r in population}!=set(rb['eligible_line_ids']) or len(population)!=len(rb['eligible_line_ids']): raise ValueError('incomplete R2C population')
        for r in population:
            role=rb['documents'].get(r['doc'],{})
            if not role.get('eligible') or r['role']!=role['role'] or r['source']!=role['source']: raise ValueError('R2C document roles mismatch')
    roles={}
    excluded_docs={d.split(':')[-1] for d in cfg.get('excluded_documents',[])}
    excluded_lines=set(cfg.get('excluded_lines',[]))
    for r in population:
        if r['doc'].split(':')[-1] in excluded_docs or r['line_id'] in excluded_lines: raise ValueError('excluded population line/document')
        if sha256(r['image'])!=r['crop_sha256']: raise ValueError('population crop hash mismatch')
        if r['role'] not in ROLES: raise ValueError('invalid document role')
        if r['doc'] in roles and roles[r['doc']]!=r['role']: raise ValueError('document role conflict')
        roles[r['doc']]=r['role']
    if cfg.get('native'):
        path=cfg['native']['line_list']
        if path not in cfg['sha256']: raise ValueError('unbound native line list')
        allowed={r['line_id']:r for r in population}
        native=list(rows(path))
        if len({r['line_id'] for r in native})!=len(native): raise ValueError('duplicate native line')
        for r in native:
            if r.get('role')!='train' or r!=allowed.get(r['line_id']): raise ValueError('native line outside bound training population')
    if cfg.get('manifest'):
        if cfg['inventory'] not in cfg['sha256']: raise ValueError('unbound crop inventory')
        forbidden=set(cfg['excluded_documents']) | set(verify_receipt(cfg['data'])['document_split']['validation'])
        forbidden={canonical_doc(d) for d in forbidden}
        forbidden_lines={canonical_line(i) for i in cfg.get('excluded_lines',[])}
        population_by_id={r['line_id']:r for r in population}
        for r in rows(cfg['manifest']):
            if r.get('role','train')!='train' or (r.get('doc') in roles and roles[r['doc']]!='train'): raise ValueError('manifest requires train role')
            bound=population_by_id.get(r.get('line_id'))
            if bound and bound.get('teacher_seen_document',False) and r.get('teacher_seen_document') is not True: raise ValueError('missing teacher_seen_document provenance')
            if r.get('provenance')!='old' and 'removes' not in r:
                if canonical_doc(r['doc']) in forbidden or canonical_line(r['line_id']) in forbidden_lines or roles.get(r['doc'])!='train': raise ValueError('supervision leakage')
                if r.get('pool')=='native':
                    if not cfg.get('native') or cfg['native']['line_list'] not in cfg['sha256']: raise ValueError('unbound native line list')
                elif r.get('pool'):
                    verify_receipt(r['pool'])
                    if str(Path(r['pool'])/'extraction_receipt.json') not in cfg['sha256']: raise ValueError('unbound extra extraction')
    return dict(inputs=len(cfg['sha256']),population_lines=len(population),document_roles=roles,policy=policy_binding())


def run(config,out,mock=False):
    if not mock and not os.environ.get('SLURM_JOB_ID'): raise ValueError('production work requires Clariden job')
    cfg=json.loads(Path(config).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True)
    identity=digest(dict(config=sha256(config),code=code_binding(),job=sha256('scripts/labelfix/clariden/r2_job.sbatch')))
    root_binding=out/'input_binding.json'
    if root_binding.exists() and json.loads(root_binding.read_text())['binding']!=identity:
        raise ValueError('output belongs to different configuration/code')
    write_json(root_binding,dict(binding=identity))
    def stage(name,fn):
        receipt=out/f'stage_{name}.json'
        if receipt.exists():
            rr=json.loads(receipt.read_text())
            if rr['binding']!=identity: raise ValueError('resume binding changed')
            for p,h in rr['sha256'].items():
                if sha256(out/p)!=h: raise ValueError('resume output changed: '+p)
            print('RESUME '+name,flush=True);return rr['result']
        started=time.monotonic();result=fn()
        files=[p for p in (out/name).rglob('*') if p.is_file()] if (out/name).exists() else []
        write_json(receipt,dict(stage=name,binding=identity,complete=True,elapsed_seconds=time.monotonic()-started,
            result=result,sha256={str(p.relative_to(out)):sha256(p) for p in files}))
        print('STAGE_DONE '+name,flush=True);return result
    # Always revalidate inputs, even when Stage A is resumed.
    checked=validate(cfg,mock);stage('A',lambda:checked)
    def teacher_stage():
        result=export(cfg['line_list'],cfg['teacher'],cfg['recognizer'],out/'B','cpu' if mock else 'cuda:0',mock,
                           recognizer_sha256=cfg['sha256'][cfg['recognizer']])
        if cfg.get('native'):
            from scripts.labelfix.clariden.r2_native import native_pool
            native=cfg['native']
            result['native']=native_pool(native['line_list'],out/'B',out/'B/native',native['crop_root'],native.get('layout','e3'),mock)
        return result
    stage('B',teacher_stage)
    def train_group(name,seeds,manifest):
        root=out/name;root.mkdir(exist_ok=True)
        def one(item):
            gpu,seed=item;dest=root/str(seed)
            if (dest/'DONE').exists():
                done=json.loads((dest/'DONE').read_text())
                if done['best_sha256']!=sha256(dest/'best.pt') or done['predictions_sha256']!=sha256(dest/'heldout_predictions.jsonl'): raise ValueError('invalid completed seed')
                return json.loads((dest/'training_receipt.json').read_text())
            if dest.exists(): dest.rename(root/f'{seed}.interrupted.{time.time_ns()}')
            cmd=[sys.executable,'-B','-u','scripts/labelfix/clariden/r1_train.py','--data',cfg['data'],'--heldout',cfg['heldout'],
                '--out',str(dest),'--arm','A','--device','cpu' if mock else f'cuda:{gpu}','--seed',str(seed),'--sampler-seed',str(seed),
                '--epochs','15','--batch-size','16' if mock else '512','--workers','0' if mock else '4',
                '--threads','2' if mock else '8','--source-commit',cfg['source_commit']]
            if mock:cmd+=['--steps','1']
            if manifest:
                cmd+=['--manifest',manifest,'--inventory',cfg['inventory']]
                if cfg.get('native'):cmd+=['--native-pool',str(out/'B/native')]
            subprocess.run(cmd,check=True)
            return json.loads((dest/'training_receipt.json').read_text())
        if mock: result=[one(x) for x in enumerate(seeds)]
        else:
            with ThreadPoolExecutor(len(seeds)) as pool: result=list(pool.map(one,enumerate(seeds)))
        return dict(seeds=seeds,runs=result)
    stage('C',lambda:train_group('C',[20261017,20261018],None))
    stage('D',lambda:train_group('D',[20261016,20261017,20261018],cfg['manifest']) if cfg.get('manifest') else dict(skipped=True,reason='no hash-bound R2a manifest'))
    if policy_binding()!=cfg['policy']:raise ValueError('release policy changed during run')
    write_json(out/'run_receipt.json',dict(binding=identity,mock=mock,stages=['A','B','C','D'],complete=True,policy=policy_binding()))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mock',action='store_true')
    run(**vars(ap.parse_args()))

if __name__=='__main__':main()
