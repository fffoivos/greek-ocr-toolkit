"""Receipt-bound SF7 recomposition. CPU/saved evidence only; never submits."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import time

from scripts.labelfix import release_gate_sf7 as gate
from scripts.labelfix.clariden import l1r_recompose_ext as old
from scripts.labelfix.clariden.l1_common import canonical, rows, sha256, write_json, STATUSES


def receipt(path, value):
    write_json(path, dict(value, preregistration_sha256=gate.PREREGISTRATION_SHA256))


_RECORDS = {}


def initialise(records):
    global _RECORDS
    _RECORDS = records


def process_shard(task):
    path, out, binding, wanted_sha, limit = task
    selected = _RECORDS
    if sha256(path) != wanted_sha:
        raise ValueError('runtime changed: '+str(path))
    seen = set(); counts = {v: Counter({s:0 for s in STATUSES}) for v in ('A',)}
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    handles = {v:gzip.open(out/f'overlay_{v}.jsonl.gz', 'wt', encoding='utf-8', compresslevel=3) for v in ('A',)}
    controls = {v:gzip.open(out/f'ctrl_subset_{v}.jsonl.gz', 'wt', encoding='utf-8', compresslevel=3) for v in ('A',)}
    kept = {v:[] for v in ('A',)}
    try:
        for runtime in rows(path):
            lid = runtime['id']
            if lid not in selected:
                if limit:
                    continue
                raise ValueError('unselected runtime '+lid)
            if lid in seen:
                raise ValueError('duplicate runtime '+lid)
            seen.add(lid); record = selected[lid]
            for v in ('A',):
                value = gate.overlay(record, runtime, v, binding)
                handles[v].write(canonical(value)+'\n'); counts[v][value['status']] += 1
                if value['status'] in ('corrected', 'unchanged'):
                    kept[v].append(lid)
                    controls[v].write(canonical(dict(line_id=lid, label=record['label'],
                        original_label_sha256=value['original_label_sha256']))+'\n')
    finally:
        for h in [*handles.values(), *controls.values()]:
            h.close()
    if sha256(path) != wanted_sha:
        raise ValueError('runtime changed during composition')
    result = dict(complete=True, input=str(path), input_sha256=wanted_sha, ids=sorted(seen),
                  counts={v:dict(c) for v,c in counts.items()}, kept=kept,
                  outputs={p.name:sha256(p) for p in sorted(out.glob('*.gz'))})
    receipt(out/'receipt.json',result)
    return str(out)


def runtime_slice(tasks, selected, limit):
    """Saved shard order can differ from selection order. Join by exact ID."""
    by={r['id']:r for r in selected}; chosen=[]; seen=set(); used=[]
    for task in tasks:
        used.append(task)
        for runtime in rows(task['runtime']):
            lid=runtime['id']
            if lid not in by or lid in seen:
                raise ValueError('unselected/duplicate runtime in slice: '+lid)
            seen.add(lid);chosen.append(by[lid])
            if len(chosen)==limit:
                return used,chosen
    raise ValueError('insufficient saved runtime for slice')


def recompose(config, out, workers=1, limit=None):
    started = time.monotonic(); config = Path(config); cfg = json.loads(config.read_text())
    out = Path(out)
    if out.exists():
        raise ValueError('output already exists; use a new run directory')
    old.separate_output(out, cfg['input_run'], cfg['ensemble_run'], cfg['selection'], cfg['source'])
    binding_policy = gate.policy_binding()
    if old.policy_binding()['sha256'] != gate.SF6_SHA256:
        raise ValueError('frozen sf6 changed')
    verification, tasks, selected, binding, inp = old.verify_inputs(
        cfg['input_run'],cfg['selection'],cfg['binding_dir'],cfg['source'],cfg['ensemble_run'],
        expected=cfg.get('expected_sha256'),workers=min(workers,4))
    if cfg.get('sf6_run'):
        prior = Path(cfg['sf6_run'])/'receipt.json'
        if sha256(prior) != cfg['sf6_receipt_sha256']:
            raise ValueError('L1R3 receipt changed')
        baseline = json.loads(prior.read_text())
        prior_inputs = Path(cfg['sf6_run'])/'input_verification.json'
        if sha256(prior_inputs) != baseline['input_verification_sha256']:
            raise ValueError('L1R3 input verification changed')
        if not baseline['complete'] or json.loads(prior_inputs.read_text())['inputs'] != verification['inputs']:
            raise ValueError('SF7 inputs differ from saved L1R3 inputs')
    if not cfg.get('verification_only') and len(selected) != cfg['lines']:
        raise ValueError('selection differs from configured split population')
    if limit is not None:
        if limit != 2000 or cfg.get('verification_only'):
            raise ValueError('real-input dry run must be exactly 2000 lines')
        tasks, selected = runtime_slice(tasks, selected, limit)
    out.mkdir(parents=True, exist_ok=False)
    receipt(out/'input_verification.json',verification)
    binding = dict(binding, policy_sha256=binding_policy['sha256'], policy_binding=binding_policy,
                   code_sha256=binding_policy['sources'], checkpoint_sha256=verification['checkpoint_sha256'])
    records = {r['id']:r for r in selected}; pending = []
    initialise(records)
    for t in tasks:
        # Dry-run IDs were joined from the exact runtime shard order.
        pending.append((t['runtime'], out/'shards'/f"shard-{t['shard']:05d}", binding,
                        verification['inputs'][t['runtime']], limit))
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers, initializer=initialise, initargs=(records,)) as pool:
            shard_dirs = list(pool.map(process_shard, pending))
    else:
        shard_dirs = list(map(process_shard,pending))
    release = out/'release'; release.mkdir()
    all_seen = []; counts = {v:Counter({s:0 for s in STATUSES}) for v in ('A',)}; kept = {v:[] for v in ('A',)}
    for directory in shard_dirs:
        sr = json.loads((Path(directory)/'receipt.json').read_text()); all_seen += sr['ids']
        for name,h in sr['outputs'].items():
            if sha256(Path(directory)/name) != h:
                raise ValueError('shard output changed')
        for v in ('A',):
            counts[v].update(sr['counts'][v]); kept[v] += sr['kept'][v]
    if len(all_seen)!=len(set(all_seen)) or set(all_seen)!=set(records):
        raise ValueError('runtime/selection mismatch')
    for v in ('A',):
        for prefix in ('overlay','ctrl_subset'):
            target = release/f'{prefix}_{v}.jsonl.gz'
            # Concatenated gzip members preserve each verified shard payload.
            with target.open('xb') as dst:
                for directory in shard_dirs:
                    with (Path(directory)/target.name).open('rb') as src:
                        import shutil
                        shutil.copyfileobj(src,dst)
        idsfile = release/f'kept_{v}_line_ids.txt'
        idsfile.write_text(''.join(i+'\n' for i in sorted(kept[v])))
        coverage = {dim:{} for dim in ('wave','source')}; aliases = 0
        for row in rows(release/f'overlay_{v}.jsonl.gz'):
            r = records[row['line_id']]
            aliases += bool(row.get('alias_only') and row['status']=='unchanged')
            if row['original_label_sha256'] != hashlib.sha256(r['label'].encode()).hexdigest():
                raise ValueError('source label mismatch')
            for dim in coverage:
                key = r.get(dim,r.get('source_dataset','UNKNOWN'))
                bucket=coverage[dim].setdefault(key,Counter({s:0 for s in STATUSES}))
                bucket[row['status']] += 1
                bucket['alias_only'] += bool(row.get('alias_only') and row['status']=='unchanged')
        for dim in coverage.values():
            for bucket in dim.values():
                bucket['total'] = sum(bucket[s] for s in STATUSES)
                bucket['kept'] = bucket['corrected'] + bucket['unchanged']
                bucket['kept_fraction'] = bucket['kept']/bucket['total']
        manifest = dict(schema='l1r-release-v1', release_policy=gate.POLICY, policy=gate.POLICY,
            variant=v, release='sf7-rc1-'+v, policy_binding=binding_policy, policy_sha=binding_policy['sha256'],
            overlay=f'overlay_{v}.jsonl.gz', overlay_sha256=sha256(release/f'overlay_{v}.jsonl.gz'),
            source_label_file=cfg['source'],source_sha256=verification['inputs'][cfg['source']],
            selection_sha256=verification['inputs'][cfg['selection']],counts_by_status=dict(counts[v]),
            kept_line_ids=idsfile.name,kept_line_ids_sha256=sha256(idsfile),kept_lines=len(kept[v]),
            coverage_per_wave=coverage['wave'],coverage_per_source=coverage['source'],alias_only=aliases,
            exclusion_receipts=inp['exclusions'],out_of_scope=inp['out_of_scope'],r0_policy=inp['r0_policy'],
            input_documents_sha256=inp['input_documents_sha256'],code_commit='GC1-source-bound-uncommitted',
            detector_commit=binding['detector_commit'],detector_version=binding['detector'],r1_sha=binding['r1_sha256'],
            checkpoint_sha256=binding['checkpoint_sha256'],code_sha256=binding_policy['sources'],
            original_labels_unchanged=True,hold_policy='HOLD and out_of_scope excluded',
            ensemble_caveat=old.ENSEMBLE_CAVEAT,verification_only=cfg.get('verification_only',False),
            dry_run=limit is not None,lines=len(records))
        receipt(release/f'release_{v}.json',manifest)
        control = release/f'ctrl_subset_{v}.jsonl.gz'
        actual = [r['line_id'] for r in rows(control)]
        if len(actual)!=len(set(actual)) or set(actual)!=set(kept[v]):
            raise ValueError('control line sets differ')
        receipt(release/f'release_ctrl_subset_{v}.json',dict(manifest, release='sf7-rc1-ctrl-subset-'+v, labels='ORIGINAL',
            labels_file=control.name,labels_sha256=sha256(control),paired_release='sf7-rc1-'+v,
            corrected_and_control_line_sets_equal=True))
    # Revalidate every verified historical input, including original labels.
    for name,h in verification['inputs'].items():
        if sha256(name)!=h:
            raise ValueError('input changed during run: '+name)
    result = dict(schema='sf7-recomposition-v1', complete=True, policy=binding_policy,
        config_sha256=sha256(config), inputs=verification['inputs'], lines=len(records),
        population_lines=verification['lines'], slice_rule='first saved runtime IDs in numeric shard order' if limit else None,
        dry_run=limit is not None,verification_only=cfg.get('verification_only',False),
        counts={v:dict(c) for v,c in counts.items()}, elapsed_seconds=time.monotonic()-started,
        detector_runs=0,reader_runs=0,recogniser_runs=0,submitted=False,
        outputs={str(p.relative_to(out)):sha256(p) for p in sorted(out.rglob('*')) if p.is_file()})
    receipt(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','outputs','policy')},indent=2))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=1);ap.add_argument('--limit',type=int)
    a=ap.parse_args();recompose(a.config,a.out,a.workers,a.limit)


if __name__=='__main__':main()
