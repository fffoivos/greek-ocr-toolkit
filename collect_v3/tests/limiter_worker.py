"""Two independent mocked HTTP processes; no socket or provider access."""
import sys,time
from pathlib import Path
from collect_v3.transport import HTTP,HostBucket,AccessStopped
from collect_v3.offline import no_network
from collect_v3.common import write_json

root,barrier,destination=sys.argv[1:];retry=0;actual=[]
def sender(url):
    global retry
    actual.append(dict(url=url,time=time.time()))
    if url.endswith('/robots.txt'):return 200,{},b'User-agent: *\nAllow: /'
    if url.endswith('/metadata'):return 302,{'Location':'/retry'},b''
    if url.endswith('/retry'):
        retry+=1
        if retry==1:return 429,{'Retry-After':'2'},b''
    return 200,{},b'ok'
http=HTTP(Path(root)/('cache-'+Path(destination).stem),sender=sender,bucket=HostBucket(Path(root)/'hosts'))
Path(destination+'.ready').touch()
deadline=time.monotonic()+20
while not Path(barrier).exists():
    if time.monotonic()>deadline:raise RuntimeError('barrier timeout')
    time.sleep(.01)
with no_network():
    try:http.get('https://shared.invalid/metadata')
    except AccessStopped:pass
    assert http.get('https://shared.invalid/metadata')==b'ok'
write_json(destination,dict(pid=__import__('os').getpid(),events=http.events,actual=actual))
