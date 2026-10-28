"""C hardware accounting: measured worker ends or uniquely matched sacct ends.

Original allocation records remain unchanged. No guessed controller upper bounds.
"""
import argparse
import math
from pathlib import Path
from common import atomic,read,sha,spec


def reconcile(plan, capture=None, expected_sha=None):
    from stage_c import checked
    p=checked(plan)
    records=[]
    if capture:
        if not expected_sha or sha(capture)!=expected_sha:
            raise ValueError('sacct SHA mismatch')
        for number,line in enumerate(Path(capture).read_text().splitlines(),1):
            fields=line.split('|')
            if len(fields)!=11:
                raise ValueError('sacct schema mismatch')
            job,_,state,_,start,end,elapsed,host,restart,_,tres=fields
            if not all(x.isdigit() for x in (start,end,elapsed)) or int(end)-int(start)!=int(elapsed):
                raise ValueError('nonterminal/unmeasured accounting interval')
            if state.split()[0] not in {'COMPLETED','CANCELLED','FAILED','NODE_FAIL','PREEMPTED','TIMEOUT','REQUEUED','OUT_OF_MEMORY'}:
                raise ValueError('nonterminal accounting')
            records.append(dict(job=job,start=int(start),end=int(end),host=host,restart=restart,
                                tres=dict(x.split('=',1) for x in tres.split(',') if '=' in x),line=number))
    active=[];matches=[]
    for e in p['runs']:
        for path in Path(e['output']).glob('ALLOCATION_*.json'):
            a=read(path)
            if not a.get('physical_host') or not a.get('step_id') or not a.get('gpu_uuid') or len(a.get('cpu_affinity',[]))<24 or not a.get('cuda_visible_devices'):
                raise ValueError('missing physical host/step/GPU/CPU attestation: '+str(path))
            if 'ended_unix' not in a:
                parents=[r for r in records if r['job']==a['job_id'] and r['restart']==str(a['restart_count'])
                    and r['host']==a['physical_host'] and r['start']<=a['started_unix']<=r['end']]
                if len(parents)!=1:
                    raise ValueError('nonunique sacct parent/restart/host: '+str(path))
                parent=parents[0]
                steps=[r for r in records if r['job']==a['job_id']+'.'+a['step_id']
                    and r['host']==a['physical_host'] and parent['start']<=r['start']<=a['started_unix']<=r['end']
                    and r['end']<=parent['end'] and r['tres'].get('gres/gpu')=='1' and r['tres'].get('cpu')=='24']
                if len(steps)!=1:
                    raise ValueError('nonunique measured step/start: '+str(path))
                a['ended_unix']=steps[0]['end']
                matches.append(dict(allocation=spec(path),parent_line=parent['line'],step_line=steps[0]['line'],
                                    measured_end_unix=a['ended_unix']))
            if not all(math.isfinite(a[k]) for k in ('started_unix','ended_unix')) or a['ended_unix']<a['started_unix']:
                raise ValueError('invalid allocation interval: '+str(path))
            for b,bpath in active:
                if max(a['started_unix'],b['started_unix'])<min(a['ended_unix'],b['ended_unix']):
                    if a['gpu_uuid']==b['gpu_uuid']:
                        raise ValueError('GPU_GLOBAL overlap: %s <> %s'%(path,bpath))
                    if a['physical_host']==b['physical_host'] and set(a['cpu_affinity'])&set(b['cpu_affinity']):
                        raise ValueError('CPU_SAME_HOST overlap: %s <> %s'%(path,bpath))
            active.append((a,path))
    if not active:
        raise ValueError('no lane attestations')
    return dict(status='PASS',plan=spec(plan),sacct=spec(capture) if capture else None,
        allocations=len(active),measured_recoveries=matches,
        policy='global GPU UUID and same-host CPU intersections across temporal overlaps; no guesses')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',required=True);p.add_argument('--out',required=True)
    p.add_argument('--sacct');p.add_argument('--sacct-sha')
    a=p.parse_args();atomic(a.out,reconcile(a.plan,a.sacct,a.sacct_sha))
