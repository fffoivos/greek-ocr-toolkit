"""Injectable Prime Intellect operations with explicit state and environment-only secrets.

The original side-effecting pi_pod.py is preserved under _vendor/pods. This facade
retains its offer ordering, reuse decisions and create payload; it has no import-time I/O.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import json
from pathlib import Path
import time
from typing import Callable, Mapping, Any
import urllib.request
from greekocr.types import PathLike, Record
from greekocr.ops.secrets import require_env
from greekocr.ops.receipts import write_receipt
__all__ = ['PodClient', 'pod_client', 'select_offer', 'create_pod', 'pod_status', 'terminate_pod', 'ensure_pod']
_PREFS = [('A100_80GB','massedcompute'),('A100_80GB','runpod'),('L40S_48GB','massedcompute'),
          ('L40S_48GB','runpod'),('L40_48GB','runpod'),('RTX6000Ada_48GB','massedcompute'),
          ('RTX6000Ada_48GB','runpod'),('A6000_48GB','massedcompute'),('A100_40GB','lambdalabs')]
Transport = Callable[[str, str, Record | None], Record]

@dataclass
class PodClient:
    transport: Transport = field(repr=False)
    def request(self, method: str, path: str, body: Record | None = None) -> Record:
        return self.transport(method, path, body)


def pod_client(*, env: Mapping[str, str] | None = None, timeout: float = 60) -> PodClient:
    key = require_env(['PRIME_INTELLECT_CONTROL_KEY'], env=env)['PRIME_INTELLECT_CONTROL_KEY']
    def request(method: str, path: str, body: Record | None) -> Record:
        req = urllib.request.Request('https://api.primeintellect.ai'+path, method=method,
                headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'},
                data=json.dumps(body).encode() if body else None)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read() or b'{}')
    return PodClient(request)


def select_offer(offers: list[Record]) -> Record:
    """Preserved GPU/provider priority, then lowest on-demand price per priority."""
    for gpu, prov in _PREFS:
        candidates = [o for o in offers if o.get('gpuType') == gpu and o.get('provider') == prov and
                      str(o.get('stockStatus','')).lower() not in ('unavailable','none','')]
        candidates.sort(key=lambda o: float((o.get('prices') or {}).get('onDemand') or 99))
        if candidates: return candidates[0]
    raise ValueError('no offer matched')


def _offers(client: PodClient) -> list[Record]:
    out = []
    def walk(x: Any) -> None:
        if isinstance(x, dict):
            if 'gpuType' in x and 'cloudId' in x: out.append(x)
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(client.request('GET', '/api/v1/availability/gpus?gpu_count=1'))
    return out


def create_pod(client: PodClient, *, name: str = 'greek-ocr-e2-20261008',
               public_key: str | None = None) -> Record:
    offer = select_offer(_offers(client))
    image = next((i for i in (offer.get('images') or []) if 'cuda' in str(i).lower()),
                 (offer.get('images') or ['ubuntu_22_cuda_12'])[0])
    pod = dict(name=name, cloudId=offer['cloudId'], gpuType=offer['gpuType'], socket=offer.get('socket') or 'PCIe',
               gpuCount=1, image=image, security=offer.get('security') or 'secure_cloud', autoRestart=False, diskSize=100)
    if offer.get('dataCenterId') or offer.get('dataCenter'): pod['dataCenterId'] = offer.get('dataCenterId') or offer.get('dataCenter')
    if offer.get('country'): pod['country'] = offer['country']
    if public_key:
        keys = client.request('GET', '/api/v1/ssh_keys/?offset=0&limit=100').get('data') or []
        key = next((k.get('id') for k in keys if (k.get('publicKey') or '').strip() == public_key.strip()), None)
        if key: pod['sshKeyId'] = key
    created = client.request('POST', '/api/v1/pods/', dict(pod=pod, provider=dict(type=offer['provider'])))
    return dict(pod_id=created.get('id'), created=created, offer=offer)


def pod_status(client: PodClient, pod_id: str) -> Record:
    return client.request('GET', '/api/v1/pods/'+pod_id)


def terminate_pod(client: PodClient, pod_id: str) -> Record:
    return client.request('DELETE', '/api/v1/pods/'+pod_id)


def ensure_pod(client: PodClient, state: PathLike, *, name: str = 'greek-ocr-e2-20261008',
               public_key: str | None = None, timeout: float = 1500, poll_seconds: float = 20,
               emit: Callable[[str], None] = print, clock: Callable[[], float] = time.monotonic,
               sleep: Callable[[float], None] = time.sleep) -> Record:
    """Reuse or create, record each poll, and emit ACTIVE/FAILED/TIMEOUT liveness."""
    if timeout <= 0 or poll_seconds <= 0: raise ValueError('positive pod wait bounds required')
    path = Path(state)
    def status(p: Record) -> str: return str(p.get('status') or (p.get('pod') or {}).get('status') or '').upper()
    previous = json.loads(path.read_text()) if path.exists() else None
    current = pod_status(client, previous['pod_id']) if previous else None
    if current is None or status(current) in ('TERMINATED','ERROR','DELETING',''):
        previous = create_pod(client, name=name, public_key=public_key)
        write_receipt(path, previous)
    deadline = clock()+timeout
    emit('START pod '+str(previous['pod_id']))
    while True:
        try: pod = pod_status(client, previous['pod_id'])
        except Exception:
            emit('LOST pod '+str(previous['pod_id']))
            raise
        state_row = dict(pod_id=previous['pod_id'], pod=pod, offer=previous.get('offer'))
        write_receipt(path, state_row)
        st = status(pod)
        emit('PROGRESS pod '+str(previous['pod_id'])+' '+st)
        if st == 'ACTIVE' and (pod.get('sshConnection') or pod.get('ip')):
            emit('DONE POD_ACTIVE '+str(previous['pod_id']))
            return state_row
        if st in ('ERROR','TERMINATED','DELETING'):
            emit('FAILED POD_FAILED '+st)
            raise RuntimeError('POD_FAILED '+st)
        if clock() >= deadline:
            emit('TIMEOUT POD_TIMEOUT')
            raise TimeoutError('POD_TIMEOUT')
        sleep(min(poll_seconds, deadline-clock()))
