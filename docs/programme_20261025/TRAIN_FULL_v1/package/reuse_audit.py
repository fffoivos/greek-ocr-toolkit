"""Rebind the e3a02365 PASS audit across this preparation-only fix.

No data scan is represented as new. The original PASS, files and package remain
immutable; new receipts retain their hashes and the compatibility proof.
"""
import argparse
from pathlib import Path

from common import atomic, bound, read, sha, spec

ROOT = Path(__file__).resolve().parent
PARENT_SHA = 'e3a023657d27bae8ec219afe25289ba7a14fdaee2af35b510131a028efa5079b'


def compatible():
    from verify import verify
    current = verify()
    from verify import PARENT_SHA as launch_parent, data_compatibility
    if sha(ROOT / 'PAYLOAD.json') != launch_parent:
        data_compatibility()
        current = read(ROOT / 'launch_parent_payload.json')
    parent_path = ROOT / 'audit_parent_payload.json'
    if sha(parent_path) != PARENT_SHA:
        raise ValueError('unrecognized audit parent payload')
    parent = read(parent_path)
    changed = {name for name, value in parent['files'].items()
               if current['files'].get(name) != value}
    if changed != {'prepare.py'}:
        raise ValueError('audit compatibility refused: changed parent files ' + str(sorted(changed)))
    additions = set(current['files']) - set(parent['files'])
    if additions != {'reuse_audit.py', 'audit_parent_payload.json', 'tests/test_prepare_fix.py'}:
        raise ValueError('audit compatibility refused: unexpected added code')
    return dict(parent_payload=spec(parent_path), unchanged_parent_files=len(parent['files']) - 1,
                changed_parent_files=sorted(changed), added_files=sorted(additions),
                policy='reuse original PASS; audit, data identity, horizon and all numerical runtime code unchanged')


def reuse(config, prior, output, *, fixture=False):
    proof = compatible()
    config, prior, output = Path(config), Path(prior), Path(output)
    if output.exists():
        raise ValueError('reuse output exists; preserve it and choose a fresh attempt')
    complete = read(prior / 'AUDIT_COMPLETE.json')
    if complete['status'] != 'PASS' or complete['fixture'] != fixture:
        raise ValueError('prior audit mode/status mismatch')
    if complete['package']['sha256'] != PARENT_SHA:
        raise ValueError('prior audit package is not the qualified parent')
    bound(complete['package'])
    bound(complete['config'])
    if complete['config']['sha256'] != sha(config):
        raise ValueError('config changed; re-audit required')
    old_manifest = bound(complete['manifest'])
    m = read(old_manifest)
    old_audit = bound(complete['audit'])
    a = read(old_audit)
    if (m['package_sha256'] != PARENT_SHA or a['package']['sha256'] != PARENT_SHA
            or m['audit']['sha256'] != complete['audit']['sha256']
            or a['status'] != 'PASS' or a['fixture'] != fixture or m['fixture'] != fixture
            or m['config']['sha256'] != sha(config) or a['config']['sha256'] != sha(config)):
        raise ValueError('inconsistent parent audit/manifest binding')
    cfg = read(config)
    if m['inputs'] != {k: cfg[k] for k in m['inputs']}:
        raise ValueError('manifest inputs differ from config')
    # All old immutable identities are checked, including the original config,
    # audit diagnostics, release transfer seal and source authority receipts.
    for value in [*m['files'].values(), *m['inputs'].values(), m['harvest_transfer'],
                  a['collision_file'], a['duplicate_file'], a['train_eval_removal_file'],
                  a['eval_crop_repeat_file']]:
        bound(value)
    proof.update(prior_complete=spec(prior / 'AUDIT_COMPLETE.json'),
                 prior_manifest=spec(old_manifest), prior_audit=spec(old_audit),
                 config=spec(config), new_package=spec(ROOT / 'PAYLOAD.json'), fixture=fixture)
    folder = output / 'manifest'
    folder.mkdir(parents=True)
    atomic(output / 'AUDIT_REUSE.json', proof)
    reuse_spec = spec(output / 'AUDIT_REUSE.json')
    a.update(package=spec(ROOT / 'PAYLOAD.json'), config=spec(config), audit_reuse=reuse_spec)
    atomic(folder / 'AUDIT.json', a)
    # Large rows/trains and diagnostics stay in place with their original hashes.
    m.update(package_sha256=sha(ROOT / 'PAYLOAD.json'), package=spec(ROOT / 'PAYLOAD.json'), config=spec(config),
             audit=spec(folder / 'AUDIT.json'), audit_reuse=reuse_spec)
    atomic(folder / 'MANIFEST.json', m)
    atomic(output / 'AUDIT_COMPLETE.json', dict(status='PASS', fixture=fixture,
        config=spec(config), audit=spec(folder / 'AUDIT.json'),
        manifest=spec(folder / 'MANIFEST.json'), package=spec(ROOT / 'PAYLOAD.json'),
        audit_reuse=reuse_spec, job_id=complete.get('job_id'),
        note='Inherited audit, not a newly executed scan'))
    return m


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--prior', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    reuse(args.config, args.prior, args.out)
    print('AUDIT_REUSED_WITH_UNCHANGED_IDENTITY')
