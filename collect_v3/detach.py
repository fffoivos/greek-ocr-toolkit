"""Portable setsid supervisor; scrub every child output line before disk."""
import os,signal,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import scrub

def main():
    out,root,*args=sys.argv[1:]
    if os.getsid(0)!=os.getpid():os.setsid()
    signal.signal(signal.SIGHUP,signal.SIG_IGN)
    # The supervisor PID owns the session. Forward termination to the child.
    child=subprocess.Popen([sys.executable,'-u',str(Path(root)/'collect_v3/run.py'),'--output-root',out,*args],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    # collector.pid is this supervisor (it owns the session and forwards SIGTERM/SIGINT); the worker that
    # holds run.lock is recorded too, so a stop or a stale-lock check can address it directly.
    import json
    (Path(out)/'collector.worker.pid').write_text(str(child.pid)+'\n')
    (Path(out)/'collector_pids.json').write_text(json.dumps(dict(supervisor=os.getpid(),worker=child.pid,stop='kill -TERM <supervisor> (forwarded; stops at a page boundary)'))+'\n')
    def terminate(sig,frame):child.send_signal(sig)
    signal.signal(signal.SIGTERM,terminate);signal.signal(signal.SIGINT,terminate)
    with (Path(out)/'collector.log').open('a',buffering=1) as f:
        for line in child.stdout:f.write(scrub(line))
    code=child.wait();(Path(out)/'collector.exit').write_text(str(code)+'\n');sys.exit(code)
if __name__=='__main__':main()
