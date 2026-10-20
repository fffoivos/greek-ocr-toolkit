#!/usr/bin/env python3
"""Readiness only: filesystem checks and allowlisted DNS; never HTTP/auth."""
import json,os,platform,socket,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import scrub
from collect_v3.egress import HOSTS
from worker.runtime import settings,PYTHON_VERSION,ROOT

MIN_FREE_BYTES=60_000_000_000

def check(c,*,system=None,machine=None,version=None,disk=None,resolver=None):
    import shutil
    system=system or platform.system();machine=machine or platform.machine()
    version=version or sys.version_info[:3];disk=disk or shutil.disk_usage
    resolver=resolver or socket.getaddrinfo
    if system!='Linux' or machine not in ('x86_64','AMD64'):raise ValueError('requires Linux x86_64')
    if tuple(version)!=PYTHON_VERSION:raise ValueError('requires CPython 3.11.3')
    if platform.python_implementation()!='CPython':raise ValueError('requires CPython')
    roots=[Path(c[k]).resolve() for k in ('output_root','cache','limiter_root')]
    for root in roots:
        root.mkdir(parents=True,exist_ok=True)
        usage=disk(root)
        if usage.free<MIN_FREE_BYTES or usage.total<MIN_FREE_BYTES:raise ValueError('requires >=60 GB total and free disk on every data filesystem')
    token=bool(os.environ.get('COLLECT_V3_ACCESS_TOKEN'))
    adc=bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    if token==adc:raise ValueError('set exactly one credential variable; values suppressed')
    if adc:
        credential=Path(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        # Never include credential paths/content in exceptions or output.
        try:
            if not credential.is_absolute() or credential.is_symlink() or not credential.is_file():raise ValueError()
            if any(credential.resolve().is_relative_to(p) for p in (ROOT,*roots)):raise ValueError()
            if credential.stat().st_mode & 0o077:raise ValueError()
            with credential.open() as stream:obj=json.load(stream)
            if obj.get('type') not in ('authorized_user','service_account'):raise ValueError()
            if obj.get('token_uri','https://oauth2.googleapis.com/token')!='https://oauth2.googleapis.com/token':raise ValueError()
        except Exception:raise ValueError('credential file must be private, readable, external to checkout/data, and OAuth2 ADC/service-account format; details suppressed') from None
    with tempfile.TemporaryFile(dir=roots[-1]) as probe:probe.write(b'limiter-write-probe');probe.flush();os.fsync(probe.fileno())
    # Use a bounded resolver subprocess in CLI; injectable resolver in unit tests.
    for host in HOSTS:
        try:
            if not resolver(host,443,type=socket.SOCK_STREAM):raise OSError()
        except Exception:raise ValueError('DNS resolution failed for allowlisted host: '+host) from None
    return dict(status='ok',os='Linux x86_64',python='3.11.3',minimum_free_bytes=MIN_FREE_BYTES,
                credential='set (value suppressed)',dns_hosts=list(HOSTS),http_requests=0,limiter_writable=True)

def bounded_dns(host,port,**kwargs):
    import subprocess
    code='import socket,sys; assert socket.getaddrinfo(sys.argv[1],443,type=socket.SOCK_STREAM)'
    p=subprocess.run([sys.executable,'-c',code,host],capture_output=True,timeout=15)
    if p.returncode:raise OSError('DNS failed')
    return True

if __name__=='__main__':
    try:print(json.dumps(check(settings(),resolver=bounded_dns)))
    except Exception as e:print('preflight: '+scrub(e),file=sys.stderr);sys.exit(1)
