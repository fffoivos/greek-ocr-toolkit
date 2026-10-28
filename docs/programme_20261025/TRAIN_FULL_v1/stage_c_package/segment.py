"""Single allocation entry; lock output, run/resume, attest yield/completion."""
import argparse
import fcntl
import os
from pathlib import Path
import sys

from common import atomic, read, spec


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--mode', choices=('train', 'smoke-control', 'smoke-requeue'), required=True)
    a = p.parse_args()
    output = Path(a.out)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'RUN.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (output / 'COMPLETE.json').exists():
            from common import bound
            complete = read(output / 'COMPLETE.json')
            bound(complete['checkpoint'])
            for entry in complete['evaluations']:
                bound(entry)
            for entry in complete['loss_evaluations']:
                bound(entry)
            bound(complete['loss_journal'])
            if complete['binding']['runtime'] != spec(a.runtime):
                raise ValueError('completed runtime changed')
            return 0
        atomic(output / ('ALLOCATION_%s_%s.json' % (os.environ['SLURM_JOB_ID'], os.environ.get('SLURM_RESTART_COUNT', '0'))),
               dict(job_id=os.environ['SLURM_JOB_ID'], restart_count=os.environ.get('SLURM_RESTART_COUNT', '0'),
                    runtime=spec(a.runtime), mode=a.mode))
        if a.mode == 'smoke-requeue' and int(os.environ.get('SLURM_RESTART_COUNT', '0')) == 0:
            os.environ['S1_FORCE_SPLIT_STEP'] = '3'
        else:
            os.environ.pop('S1_FORCE_SPLIT_STEP', None)
        os.environ['S1_TRACE'] = '1' if a.mode.startswith('smoke') else '0'
        from run import execute
        status = execute(a.runtime, a.out, smoke=a.mode.startswith('smoke'))
        if status == 75:
            atomic(output / 'SEGMENT_YIELD.json', dict(job_id=os.environ['SLURM_JOB_ID'],
                   restart_count=os.environ.get('SLURM_RESTART_COUNT', '0'), checkpoint=spec(output / 'segment.pt')))
        return status


if __name__ == '__main__':
    raise SystemExit(main())
