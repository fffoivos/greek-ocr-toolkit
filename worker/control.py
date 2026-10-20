#!/usr/bin/env python3
"""Detached W1 launcher and PID-reuse-safe status; secrets stay in environment."""
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import lock,read_json,write_json,rows,scrub
from collect_v3.config import SPECS
from worker.runtime import ROOT,settings


def process_id(pid):
    try:
        value=Path('/proc')/str(pid)/'stat'
        tail=value.read_text().rsplit(')',1)[1].split()
        if tail[0]=='Z':return None
        return Path('/proc/sys/kernel/random/boot_id').read_text().strip()+':'+tail[19]  # boot ID + /proc field 22
    except (OSError,ValueError,IndexError):return None


def alive(out):
    try:
        pid=int((out/'collector.pid').read_text().strip());identity=read_json(out/'collector_identity.json')
        if pid<=1 or identity['pid']!=pid:return None
        if process_id(pid)!=identity['start_ticks']:return None
        return pid
    except (OSError,ValueError,KeyError):return None


def launch(c,tranche='W1'):
    if tranche!='W1':raise ValueError('worker launcher accepts --tranche W1 only; W2 requires c1_gate.json and a separate coordinator launch')
    out=Path(c['output_root']);out.mkdir(parents=True,exist_ok=True)
    with lock(out/'launch.lock',blocking=False):
        pid=alive(out)
        if pid:return dict(status='already_running',pid=pid)
        from worker.preflight import check,bounded_dns
        check(c,resolver=bounded_dns)
        from worker.prepare import prepare
        prepare(out)
        # Check the runner lock before spawning; the runner acquires it itself.
        with lock(out/'run.lock',blocking=False):pass
        cfg=dict(c,network_enabled=True)
        write_json(out/'runtime_config.json',cfg)
        (out/'collector.exit').unlink(missing_ok=True)
        cmd=[sys.executable,str(ROOT/'collect_v3/detach.py'),str(out),str(ROOT),
             '--config',str(out/'runtime_config.json'),'run','--tranche','W1',
             '--execution-host','worker','--enable-network','--sources',*SPECS]
        child=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,close_fds=True,start_new_session=True)
        ticks=process_id(child.pid)
        if not ticks:raise RuntimeError('detached supervisor failed to start')
        write_json(out/'collector_identity.json',dict(pid=child.pid,start_ticks=ticks))
        from collect_v3.common import atomic_bytes
        atomic_bytes(out/'collector.pid',(str(child.pid)+'\n').encode())
        # No automatic respawn; uncertain reads remain held in the ledger.
        time.sleep(.25)
        if not alive(out):raise RuntimeError('detached collector exited; inspect scrubbed collector.log and status')
        return dict(status='started',pid=child.pid,tranche='W1')


def status(c):
    import sqlite3
    out=Path(c['output_root']);pid=alive(out);result=dict(status='running' if pid else 'stopped',pid=pid)
    if (out/'collector.exit').exists():result['last_exit_code']=(out/'collector.exit').read_text().strip()
    state=out/'W1/state.json'
    if state.exists():
        s=read_json(state);result['W1_state']=s.get('status');result['completed_pages']=sum(v=='completed' for v in s.get('pages',{}).values())
    ledger=out/'ledger.sqlite3'
    if ledger.exists():
        db=sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
        try:
            result['ledger']=[dict(tranche=t,state=s,reads=n,reserved_usd=m/1e6) for t,s,n,m in db.execute('SELECT tranche,state,COUNT(*),SUM(micro_usd) FROM reads GROUP BY tranche,state')]
        finally:db.close()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['launch','status','stop']);p.add_argument('--tranche',default='W1');a=p.parse_args()
    try:
        c=settings()
        if a.command=='launch':result=launch(c,a.tranche)
        elif a.command=='stop':
            pid=alive(Path(c['output_root']))
            if pid:os.kill(pid,signal.SIGTERM)
            result=dict(status='termination_requested' if pid else 'stopped',pid=pid)
        else:result=status(c)
        print(json.dumps(result))
    except Exception as e:print('worker: '+scrub(e),file=sys.stderr);sys.exit(1)
