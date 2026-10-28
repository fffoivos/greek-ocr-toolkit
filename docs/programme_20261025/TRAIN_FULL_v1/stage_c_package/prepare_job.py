"""Requeue-safe preparation without deleting an interrupted attempt."""
import argparse
import os
from pathlib import Path
import time

from common import atomic, bound, read, sha, spec


def existing_or_preserve(folder, terminal, config):
    if not folder.exists():
        return False
    if (folder / terminal).exists():
        result = read(folder / terminal)
        if result['config']['sha256'] != sha(config):
            raise ValueError('existing preparation uses another data config')
        if result.get('package_sha256') != sha(Path(__file__).with_name('PAYLOAD.json')):
            raise ValueError('existing preparation uses another package; use a new attempt')
        return True
    # Keep every interrupted byte; rebuild from the same hash-bound input config.
    folder.rename(folder.with_name(folder.name + '.interrupted-' + str(time.time_ns())))
    return False


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    root = Path(a.out)
    root.mkdir(parents=True, exist_ok=True)
    from verify import verify
    verify()
    from manifest import build
    from prepare import prepare
    audit = read(root / 'AUDIT_COMPLETE.json')
    if (audit['status'] != 'PASS' or audit['fixture']
            or audit['config']['sha256'] != sha(a.config)
            or audit['package']['sha256'] != sha(Path(__file__).with_name('PAYLOAD.json'))):
        raise ValueError('CPU audit required for this production config/package')
    bound(audit['manifest'])
    bound(audit['audit'])
    if not existing_or_preserve(root / 'manifest', 'MANIFEST.json', a.config):
        raise ValueError('audited manifest missing')
    m = read(root / 'manifest/MANIFEST.json')
    for value in m['files'].values():
        bound(value)
    if not existing_or_preserve(root / 'prepared', 'runtime.json', a.config):
        prepare(a.config, root / 'manifest', root / 'prepared')
    rt = read(root / 'prepared/runtime.json')
    if rt['mock']:
        raise ValueError('mock runtime cannot complete production preparation')
    for pool in rt['pools'].values():
        for file in pool['files']:
            bound(file)
    atomic(root / 'PREPARE_COMPLETE.json', dict(config=spec(a.config),
        manifest=spec(root / 'manifest/MANIFEST.json'), runtime=spec(root / 'prepared/runtime.json'),
        job_id=os.environ.get('SLURM_JOB_ID'), package=spec(Path(__file__).with_name('PAYLOAD.json'))))
