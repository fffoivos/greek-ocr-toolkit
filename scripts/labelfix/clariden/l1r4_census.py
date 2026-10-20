"""L1R4 job 2: original/joined inventories, censuses and bound L1R3 deltas."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import time

from scripts.labelfix.clariden import l1c_census as c, l1r2_changes as changes
from scripts.labelfix.clariden import l1r3_evidence as evidence


def joined_inventory(root, out, verification, specs):
    waves = {}; seen = set(); totals = evidence.empty_counts(); counts = defaultdict(evidence.empty_counts)
    hashes = {}
    for spec in specs:
        directory = Path(spec['directory'])
        for row in c.rows(directory / 'selection.jsonl'):
            if row['id'] in waves: raise ValueError('duplicate joined inventory selection ID')
            waves[row['id']] = row['wave']
        p = directory / 'joined-runtime.jsonl.gz'
        if str(p) not in verification['hashes']: raise ValueError('unbound joined runtime')
        for rt in c.rows(p):
            lid = rt['id']
            if lid in seen or lid not in waves: raise ValueError('duplicate/unselected joined runtime ID')
            seen.add(lid); observed, _ = evidence.observe(rt)
            totals.update(observed); counts[waves[lid]].update(observed)
        hashes[str(p)] = c.sha256(p)
        if hashes[str(p)] != verification['hashes'][str(p)]: raise ValueError('joined runtime changed')
    if seen != set(waves) or len(seen) != verification['lines']: raise ValueError('joined inventory population mismatch')
    result = dict(schema='l1r4-joined-inventory-v1', complete=True, **evidence.summarize(totals),
                  per_wave={w: evidence.summarize(v) for w,v in sorted(counts.items())},
                  compressed_sha256=hashes, gate_sha256=c.GATE_SHA256_BY_POLICY['sf6-release-v1'],
                  l1f_join_receipt_sha256=c.sha256(Path(root) / 'l1f_join_receipt.json'))
    c.atomic_json(out, result)
    return result


def verify_baseline(spec, new_root, workers):
    root = Path(spec['release_root']); census = Path(spec['census_root'])
    verified, _, receipt = c.verify_inputs(root, min(workers, 8))
    if c.sha256(root / 'receipt.json') != spec['release_receipt_sha256']:
        raise ValueError('L1R3 baseline release receipt changed')
    combined = c.load(census / 'receipt.json')
    if (combined.get('complete') is not True or Path(combined['input_directory']).resolve() != root.resolve()
            or c.sha256(census / 'receipt.json') != spec['census_receipt_sha256']):
        raise ValueError('L1R3 census incomplete/unbound')
    for name, wanted in combined['outputs'].items():
        if c.sha256(c.confined(census, name)) != wanted: raise ValueError('L1R3 combined output changed')
    for folder in ('hold', 'changes'):
        sr = c.load(census / folder / 'receipt.json')
        if sr.get('complete') is not True: raise ValueError('L1R3 incomplete census')
        for name, wanted in sr['outputs'].items():
            if c.sha256(c.confined(census / folder, name)) != wanted: raise ValueError('L1R3 census payload changed')
        for name, wanted in sr['partial_receipts'].items():
            if c.sha256(c.confined(census / folder, name)) != wanted: raise ValueError('L1R3 census partial changed')
    change_ver = c.load(census / 'changes/input_verification.json')
    if change_ver['hashes'] != verified['hashes']: raise ValueError('L1R3 census differs from baseline release')
    old = c.load(root / 'input_verification.json'); new = c.load(Path(new_root) / 'input_verification.json')
    if (old['lines'] != new['lines'] or old['shards'] != new['shards']
            or any(new['inputs'].get(p) != h for p,h in old['inputs'].items())):
        raise ValueError('L1R3/L1R4 upstream population differs')
    return c.load(census / 'changes/CHANGES.json'), census / 'changes/real_mark_correction_lines.jsonl'


def compare(old, new, old_list, new_list, destination):
    def population(path, counts):
        records = list(c.rows(path)); keyed = {(r['mode'], r['line_id']): r for r in records}
        if len(keyed) != len(records): raise ValueError('duplicate comparison audit row')
        observed = Counter((r['mode'], r['wave']) for r in records)
        for mode, groups in counts['modes'].items():
            if sum(v for (m,w),v in observed.items() if m == mode) != groups['overall']['real_mark_correction_lines']:
                raise ValueError('comparison audit total differs')
            for wave, values in groups['per_wave'].items():
                if observed[mode,wave] != values['real_mark_correction_lines']: raise ValueError('comparison audit wave differs')
        return keyed
    before = population(old_list, old); after = population(new_list, new)
    if any(before[k]['wave'] != after[k]['wave'] for k in before.keys() & after.keys()):
        raise ValueError('comparison wave identity changed')
    newly = [after[k] for k in sorted(after.keys() - before.keys())]
    changes.write_audit_list(destination, newly)
    def difference(a,b):
        result = {}
        for key in ('total_lines','corrected_status_lines','real_mark_correction_lines','sf6_deletion_held_lines'):
            result[key] = dict(l1r3=a[key], l1r4=b[key], delta=b[key]-a[key])
        result['sf6_deletion_holds_by_class'] = {
            kind: {key: dict(l1r3=a['sf6_deletion_holds_by_class'][kind][key],
                             l1r4=b['sf6_deletion_holds_by_class'][kind][key],
                             delta=b['sf6_deletion_holds_by_class'][kind][key]-a['sf6_deletion_holds_by_class'][kind][key])
                   for key in ('lines','checks')}
            for kind in a['sf6_deletion_holds_by_class']}
        return result
    modes = {}
    for mode in c.MODES:
        a,b=old['modes'][mode],new['modes'][mode]
        waves = sorted(set(a['per_wave']) | set(b['per_wave']))
        modes[mode] = dict(overall=difference(a['overall'],b['overall']),
            per_wave={w:difference(a['per_wave'][w],b['per_wave'][w]) for w in waves},
            newly_real_mark_correction_lines=sum(r['mode']==mode for r in newly),
            no_longer_real_mark_correction_lines=sum(k[0]==mode for k in before.keys()-after.keys()))
    return dict(schema='l1r4-vs-l1r3-v1', complete=True, modes=modes,
                newly_real_mark_correction_rows=len(newly),
                newly_real_mark_correction_unique_lines=len({r['line_id'] for r in newly}),
                newly_real_mark_correction_list=Path(destination).name,
                new_list_sha256=c.sha256(new_list), old_list_sha256=c.sha256(old_list))


def run(root, out, workers, config):
    started = time.monotonic(); root=Path(root); out=Path(out); cfg=c.load(config)
    if workers < 1:
        raise ValueError('positive workers required')
    for original in (root, cfg['input_run'], cfg['ensemble_run'], cfg['l1f']['root'],
                     cfg['baseline']['release_root'], cfg['baseline']['census_root']):
        p=Path(original).resolve(); destination=out.resolve()
        if p == destination or p in destination.parents or destination in p.parents:
            raise ValueError('census output must be separate from all input trees')
    if not __import__('os').environ.get('SLURM_JOB_ID') and not cfg.get('verification_only'):
        raise ValueError('production census requires Slurm allocation')
    code = {Path(p).name:c.sha256(p) for p in (__file__, c.__file__, changes.__file__, evidence.__file__)}
    config_sha = c.sha256(config)
    # Inventories precede the release censuses, as in L1R3.
    evidence.inventory_release(root, out / 'evidence_availability_original.json', config)
    verification,specs,receipt = c.verify_inputs(root,min(workers,8))
    if 'l1f_join' not in receipt['binding']: raise ValueError('L1R4 joined output required')
    joined_inventory(root,out/'evidence_availability.json',verification,specs)
    c.census(root,out/'hold',workers)
    changes.census(root,out/'changes',workers)
    old,old_list=verify_baseline(cfg['baseline'],root,workers)
    result=compare(old,c.load(out/'changes/CHANGES.json'),old_list,out/'changes/real_mark_correction_lines.jsonl',
                   out/'newly_real_mark_correction_lines.jsonl')
    result['baseline']=cfg['baseline']
    c.atomic_json(out/'L1R3_DELTA.json',result)
    text=['# L1R4 versus L1R3','', '| Mode | Wave | Real mark lines L1R3 → L1R4 | SF6 deletion HOLD L1R3 → L1R4 |', '|---|---|---:|---:|']
    for mode, groups in result['modes'].items():
        for wave, b in {'*':groups['overall'],**groups['per_wave']}.items():
            real=b['real_mark_correction_lines']; held=b['sf6_deletion_held_lines']
            text.append(f'| {mode} | {wave} | {real["l1r3"]} → {real["l1r4"]} | {held["l1r3"]} → {held["l1r4"]} |')
    text += ['', 'Per-class distinct line and blocked-atom deltas are in L1R3_DELTA.json; classes overlap.',
             'The new audit list is a mode/line set difference, not a count difference.']
    (out/'L1R3_DELTA.md').write_text('\n'.join(text)+'\n')
    if code != {name:c.sha256(Path(__file__).with_name(name)) for name in code} or c.sha256(config)!=config_sha:
        raise ValueError('L1R4 census code/config changed')
    outputs=('evidence_availability_original.json','evidence_availability.json','hold/receipt.json',
             'changes/receipt.json','L1R3_DELTA.json','L1R3_DELTA.md','newly_real_mark_correction_lines.jsonl')
    final=dict(schema='l1r4-combined-census-v1',complete=True,analysis_only=True,
        input_directory=str(root.resolve()), input_receipt_sha256=c.sha256(root/'receipt.json'),
        config_sha256=config_sha,code_sha256=code,baseline=cfg['baseline'],
        outputs={p:c.sha256(out/p) for p in outputs},elapsed_seconds=time.monotonic()-started)
    c.atomic_json(out/'receipt.json',final)
    print('L1R4_CENSUS_COMPLETE '+c.canonical(final),flush=True)
    return final


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True); ap.add_argument('--input-dir',required=True)
    ap.add_argument('--out',required=True); ap.add_argument('--workers',type=int,default=16)
    a=ap.parse_args(); run(a.input_dir,a.out,a.workers,a.config)
