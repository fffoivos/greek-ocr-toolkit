from pathlib import Path
import os
import sys
import pytest
PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG))
from common import atomic,read,spec
from memory_diagnostics import cgroups,read_cgroup,tree_pss,MemoryMonitor,summarize


def fixture_proc(tmp_path):
    proc=tmp_path/'proc';(proc/'self').mkdir(parents=True)
    mount=tmp_path/'cgroup';job=mount/'uid_1/job_123';step=job/'step_0';step.mkdir(parents=True)
    (proc/'self/cgroup').write_text('0::/slurm/uid_1/job_123/step_0\n')
    (proc/'self/mountinfo').write_text(f'29 23 0:26 /slurm {mount} rw - cgroup2 cgroup rw\n')
    for p in (step,job,mount/'uid_1',mount):
        for key,value in {'memory.peak':'9000','memory.max':'110000','memory.current':'8000','memory.events':'low 0\nhigh 0\nmax 0\noom 0\noom_kill 0'}.items():
            (p/key).write_text(value)
    for pid,children,pss in [(os.getpid(),'42',200),(42,'',100)]:
        task=proc/str(pid)/'task'/str(pid);task.mkdir(parents=True)
        (task/'children').write_text(children)
        (proc/str(pid)/'smaps_rollup').write_text(f'Rss: 999 kB\nPss: {pss} kB\n')
    return proc,job


def test_job_scope_mount_root_mapping_PSS_shared_RSS_and_yield_end_receipts(tmp_path):
    proc,job=fixture_proc(tmp_path)
    found=cgroups(proc,'123')
    assert [p for p,v,is_job in found if is_job]==[job]
    assert tree_pss(os.getpid(),proc)['pss_bytes']==300*1024
    output=tmp_path/'out';output.mkdir()
    m=MemoryMonitor(output,dict(job_id='123',restart_count=0),proc=proc,interval=.01)
    m.start();m.sample('periodic');m.sample('yield');path=m.close()
    assert {s['reason'] for s in read(path)['samples']} >= {'start','periodic','yield','end'}
    r=summarize([spec(path)])
    assert r['job_peak_bytes']==9000 and r['job_limit_bytes']==110000
    assert r['aggregate_pss_bytes_max']==300*1024 and r['events_max']==dict(oom=0,oom_kill=0)
    assert r['capacity_qualified'] is False
    (job/'memory.events').write_text('oom 1\noom_kill 1')
    assert read_cgroup(job,'cgroup2',True)['events']['oom_kill']==1


def test_missing_counters_or_unreadable_PSS_never_fabricate_memory(tmp_path):
    proc,job=fixture_proc(tmp_path)
    (job/'memory.peak').unlink()
    r=read_cgroup(job,'cgroup2',True)
    assert 'memory.peak' in r['errors'] and r['peak_bytes'] is None
    output=tmp_path/'out';output.mkdir()
    m=MemoryMonitor(output,dict(job_id='123',restart_count=1),proc=proc)
    m.start();path=m.close()
    partial=summarize([spec(path)])
    assert partial['capture_status']=='PARTIAL' and partial['job_peak_bytes'] is None
    assert partial['diagnostic_problems']
    (proc/'42/smaps_rollup').unlink()
    assert tree_pss(os.getpid(),proc)['errors'][0]['pid']==42


def test_unlimited_job_cgroup_is_reported_not_mislabelled_enforced(tmp_path):
    proc,job=fixture_proc(tmp_path)
    (job/'memory.max').write_text('max')
    output=tmp_path/'out';output.mkdir()
    m=MemoryMonitor(output,dict(job_id='123',restart_count=1),proc=proc)
    m.start();path=m.close()
    r=summarize([spec(path)])
    assert r['job_limit_bytes'] is None and r['job_headroom_bytes'] is None
    assert r['job_limits_observed']==['max'] and r['capacity_qualified'] is False
