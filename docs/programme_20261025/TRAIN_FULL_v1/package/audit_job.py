"""CPU-only union audit. Read releases in place; publish no training data on conflicts.

On scheduler requeue preserve partial diagnostics and start the deterministic scan
again; reuse only a completed audit with the same config, package and file hashes.
"""
import argparse
import fcntl
import os
from pathlib import Path
import time
import traceback

from common import atomic, bound, read, sha, spec
from manifest import build
from prepare_job import existing_or_preserve


def execute(config, output, *, fixture=False):
    from verify import verify
    verify()
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'AUDIT.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = time.monotonic()
        atomic(root / ('AUDIT_ALLOCATION_%s_%s.json' % (
            os.environ.get('SLURM_JOB_ID', 'offline'), os.environ.get('SLURM_RESTART_COUNT', '0'))),
            dict(config=spec(config), job_id=os.environ.get('SLURM_JOB_ID'),
                 restart_count=os.environ.get('SLURM_RESTART_COUNT', '0')))
        try:
            if not existing_or_preserve(root / 'manifest', 'MANIFEST.json', config):
                build(config, root / 'manifest', fixture=fixture, audit=True)
            result = read(root / 'manifest/MANIFEST.json')
            if not result.get('audit'):
                raise ValueError('manifest has no CPU audit receipt')
            bound(result['audit'])
            audit = read(result['audit']['path'])
            if audit['status'] != 'PASS' or audit['fixture'] != fixture:
                raise ValueError('audit not a PASS for the requested production/fixture mode')
            for value in [*result['files'].values(), audit['collision_file'], audit['duplicate_file']]:
                bound(value)
            atomic(root / 'AUDIT_COMPLETE.json', dict(status='PASS', fixture=fixture,
                config=spec(config), audit=result['audit'], manifest=spec(root / 'manifest/MANIFEST.json'),
                elapsed_seconds=time.monotonic() - started, job_id=os.environ.get('SLURM_JOB_ID'),
                package=spec(Path(__file__).with_name('PAYLOAD.json'))))
            return result
        except Exception as exc:
            # A complete collision scan emits AUDIT.json; path/hash failures also
            # leave a durable failure record and cannot be mistaken for clearance.
            atomic(root / ('AUDIT_FAILED_%s.json' % time.time_ns()), dict(status='BLOCKED',
                error=str(exc), traceback=traceback.format_exc(), config=spec(config),
                elapsed_seconds=time.monotonic() - started,
                audit=spec(root / 'manifest/AUDIT.json') if (root / 'manifest/AUDIT.json').exists() else None))
            raise


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    execute(a.config, a.out)
