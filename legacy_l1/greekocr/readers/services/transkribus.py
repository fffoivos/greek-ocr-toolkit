"""Sequential Transkribus processing reader with a credit floor and durable SHA cache.

Credentials and OAuth tokens stay in memory. Uncertain submissions are never
automatically repeated; a saved process ID may be polled again without billing.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Iterable, Iterator
import unicodedata
import uuid
import xml.etree.ElementTree as ET

from .google_docai import _atomic_json, _canonical, _lock
from greekocr.types import PathLike

TOKEN_URL = 'https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token'
DEFAULT_BASE_URL = 'https://transkribus.eu/processing/v1'
CREDITS_URL = 'https://transkribus.eu/TrpServer/rest/credits'
DEFAULT_MODEL_ID = 148525
DEFAULT_LAYOUT_MODEL_ID = 49272  # published legacy API example; defaults for its other parameters
__all__ = ['TranskribusReader', 'Reading', 'TranskribusError', 'CreditFloorError', 'load_transkribus', 'DEFAULT_MODEL_ID']


class TranskribusError(RuntimeError):
    pass


class CreditFloorError(TranskribusError):
    pass


@dataclass(frozen=True)
class Reading:
    text: str
    raw_text: str
    lines: list[str]
    line_confidences: list[float | None]
    symbol_confidences: list[dict]
    token_confidences: list[dict]
    mean_symbol_conf: float | None
    min_symbol_conf: float | None
    raw_json_path: str
    request_id: str | None
    latency_s: float
    crop_sha256: str = ''
    cached: bool = False
    receipt_id: str = ''
    line_count_source: str = 'PAGE TextLine'


def _confidence(value):
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('confidence must be finite and within [0, 1]')
    return value


def parse_token(raw: dict, now: float) -> tuple[str, str | None, float]:
    """Parse in memory only; callers must never persist the response."""
    token = raw.get('access_token')
    expiry = float(raw.get('expires_in', 0))
    if not isinstance(token, str) or not token or not math.isfinite(expiry) or expiry <= 0:
        raise TranskribusError('invalid OAuth token response')
    return token, raw.get('refresh_token'), now + expiry


def parse_balance(raw: dict) -> float:
    """overallBalance with onlyActive=true/includeExpired=false is authoritative."""
    if not isinstance(raw, dict) or 'overallBalance' not in raw:
        raise TranskribusError('credit response lacks overallBalance')
    value = float(raw['overallBalance'])
    if not math.isfinite(value) or value < 0:
        raise TranskribusError('invalid credit balance')
    return value


def _equiv(node):
    choices = node.findall('{*}TextEquiv')
    if not choices:
        return '', None
    best = min(choices, key=lambda x: int(x.get('index', '0')))
    return best.findtext('{*}Unicode', default=''), _confidence(best.get('conf'))


def parse_page(xml: str) -> dict:
    """Preserve emitted Unicode and PAGE order; never infer char confidence."""
    if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
        raise ValueError('PAGE DTD/entities are not accepted')
    root = ET.fromstring(xml)
    pages = [root] if root.tag.rsplit('}', 1)[-1] == 'Page' else root.findall('.//{*}Page')
    if len(pages) != 1:
        raise ValueError('one-image result must contain exactly one PAGE page')
    page = pages[0]
    regions = page.findall('{*}TextRegion')
    # Honour explicit region reading order, when supplied, with DOM fallback.
    refs = page.findall('.//{*}RegionRefIndexed')
    if refs:
        rank = {r.get('regionRef'): int(r.get('index', '0')) for r in refs}
        regions.sort(key=lambda r: rank.get(r.get('id'), len(rank)))
    lines, line_confidences, symbols, words = [], [], [], []
    for region in regions:
        for line in region.findall('{*}TextLine'):
            text, conf = _equiv(line)
            lines.append(text)
            line_confidences.append(conf)
            for word in line.findall('{*}Word'):
                text, conf = _equiv(word)
                words.append(dict(text=text, confidence=conf, line_id=line.get('id')))
                for glyph in word.findall('{*}Glyph'):
                    text, conf = _equiv(glyph)
                    symbols.append(dict(text=text, confidence=conf, line_id=line.get('id')))
            for glyph in line.findall('{*}Glyph'):
                text, conf = _equiv(glyph)
                symbols.append(dict(text=text, confidence=conf, line_id=line.get('id')))
    return dict(text='\n'.join(lines), lines=lines, line_confidences=line_confidences,
                symbol_confidences=symbols, token_confidences=words, line_count_source='PAGE TextLine')


def parse_result(raw: dict) -> dict:
    if raw.get('page_xml') is not None:
        return parse_page(raw['page_xml'])
    job = raw.get('job', raw)
    if job.get('status') != 'FINISHED':
        raise TranskribusError('processing result is not FINISHED')
    content = job.get('content')
    if not isinstance(content, dict):
        raise ValueError('finished process has no content')
    items = [line for region in content.get('regions', []) for line in region.get('lines', [])]
    lines = [line.get('text', '') for line in items]
    return dict(text=content.get('text', '\n'.join(lines)), lines=lines,
        line_confidences=[_confidence(line.get('confidence')) for line in items],
        symbol_confidences=[], token_confidences=[], line_count_source='content.regions[].lines')


def _reading(raw: dict, metadata: dict, *, cached=False) -> Reading:
    result = parse_result(raw)
    confidences = [s['confidence'] for s in result['symbol_confidences'] if s['confidence'] is not None]
    return Reading(text=unicodedata.normalize('NFD', result['text']), raw_text=result['text'],
        lines=result['lines'], line_confidences=result['line_confidences'],
        symbol_confidences=result['symbol_confidences'], token_confidences=result['token_confidences'],
        mean_symbol_conf=sum(confidences)/len(confidences) if confidences else None,
        min_symbol_conf=min(confidences) if confidences else None,
        raw_json_path=metadata.get('raw_json_path', ''), request_id=metadata.get('request_id'),
        latency_s=metadata.get('latency_s', 0), crop_sha256=metadata.get('crop_sha256', ''),
        receipt_id=metadata.get('receipt_id', ''), cached=cached,
        line_count_source=result['line_count_source'])


def request_payload(image: bytes, model_id: int, mode: str,
                    layout_model_id: int = DEFAULT_LAYOUT_MODEL_ID) -> dict:
    value = dict(config=dict(textRecognition=dict(htrId=model_id)),
                 image=dict(base64=base64.b64encode(image).decode('ascii')))
    if mode == 'single_line':
        from PIL import Image
        import io
        with Image.open(io.BytesIO(image)) as crop:
            w, h = crop.size
        coords = f'0,0 {w-1},0 {w-1},{h-1} 0,{h-1}'
        value['content'] = dict(regions=[dict(id='crop-region', coords=dict(points=coords),
            lines=[dict(id='crop-line', coords=dict(points=coords),
                        baseline=dict(points=f'0,{round((h-1)*.75)} {w-1},{round((h-1)*.75)}'))])])
    elif mode == 'default':
        value['config']['lineDetection'] = dict(modelId=layout_model_id)
    else:
        raise ValueError('unknown layout mode')
    return value


class TranskribusReader:
    def __init__(self, model_id=DEFAULT_MODEL_ID, *, responses_dir,
                 base_url=DEFAULT_BASE_URL, mode='default', credit_floor=50,
                 layout_model_id=DEFAULT_LAYOUT_MODEL_ID,
                 max_page_credits=1.0, max_wait_s=180, poll_interval_s=2,
                 http_timeout_s=30, session=None, clock=time.monotonic, sleep=time.sleep):
        if int(model_id) <= 0 or mode not in ('default', 'single_line'):
            raise ValueError('invalid model or layout mode')
        if not all(math.isfinite(x) for x in (credit_floor,max_page_credits,max_wait_s,poll_interval_s,http_timeout_s)) or credit_floor < 50 or max_page_credits < 1 or max_wait_s <= 0 or poll_interval_s <= 0 or http_timeout_s <= 0:
            raise ValueError('invalid credit/polling limits')
        if base_url.rstrip('/') not in (DEFAULT_BASE_URL, 'https://transkribus.eu/processing/v2',
                                        'https://api.transkribus.org/v2', 'https://api-staging.transkribus.org/v2'):
            raise ValueError('base URL must be an official Transkribus endpoint')
        self.model_id, self.mode = int(model_id), mode
        self.layout_model_id = int(layout_model_id)
        if self.layout_model_id <= 0:
            raise ValueError('layout model ID must be positive')
        self.responses_dir = Path(responses_dir).resolve()
        self.output_dir = self.responses_dir.parent
        self.base_url = base_url.rstrip('/')
        self.credit_floor, self.max_page_credits = credit_floor, max_page_credits
        self.max_wait_s, self.poll_interval_s, self.http_timeout_s = max_wait_s, poll_interval_s, http_timeout_s
        self.session, self.clock, self.sleep = session, clock, sleep
        self._token = self._refresh_token = None
        self._expires_at = 0.0
        self.calls = []
        self.balance_snapshots = []
        self.ledger_path = self.output_dir / 'ledger.jsonl'

    def binding(self) -> dict[str, Any]:
        return dict(engine='transkribus', base_url=self.base_url, model_id=self.model_id,
                    mode=self.mode, language_model=None, layout=f'lineDetection modelId={self.layout_model_id}; default detection parameters' if self.mode == 'default' else 'supplied whole-crop polygon; horizontal baseline at 75% height')

    def _redact(self, text):
        for value in (os.environ.get('TRANSKRIBUS_USERNAME'), os.environ.get('TRANSKRIBUS_PASSWORD'),
                      self._token, self._refresh_token):
            if value:
                text = text.replace(value, '[REDACTED]')
        return text

    def _save(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_json(path, self._sanitize(value))

    def _sanitize(self, value):
        if isinstance(value,str):return self._redact(value)
        if isinstance(value,list):return [self._sanitize(v) for v in value]
        if isinstance(value,dict):return {self._redact(k):self._sanitize(v) for k,v in value.items()}
        return value

    def _transport(self, method, url, role, **kwargs):
        if self.session is None:
            import requests
            self.session = requests.Session()
        started = self.clock()
        try:
            r = self.session.request(method, url, timeout=self.http_timeout_s, allow_redirects=False, **kwargs)
        except Exception:
            self.calls.append(dict(call_id=uuid.uuid4().hex, role=role, method=method, status='transport_error'))
            raise TranskribusError(f'{role}: transport error; outcome may be unknown') from None
        self.calls.append(dict(call_id=uuid.uuid4().hex, role=role, method=method, http_status=r.status_code,
                               latency_s=round(self.clock()-started, 3)))
        if r.status_code in (402, 429):
            raise CreditFloorError(f'{role}: HTTP {r.status_code}; depleted credits or rate limit; stop')
        if not 200 <= r.status_code < 300:
            raise TranskribusError(f'{role}: HTTP {r.status_code}')
        return r

    def _access_token(self):
        if self._token and self.clock() < self._expires_at - 30:
            return self._token
        if self._refresh_token:
            data = dict(grant_type='refresh_token', client_id='processing-api-client', refresh_token=self._refresh_token)
        else:
            username, password = os.environ.get('TRANSKRIBUS_USERNAME'), os.environ.get('TRANSKRIBUS_PASSWORD')
            if not username or not password:
                raise TranskribusError('TRANSKRIBUS_USERNAME and TRANSKRIBUS_PASSWORD must be set in the environment')
            data = dict(grant_type='password', client_id='processing-api-client', username=username, password=password)
        r = self._transport('POST', TOKEN_URL, 'token', data=data)
        self._token, self._refresh_token, self._expires_at = parse_token(r.json(), self.clock())
        return self._token

    def _request(self, method, url, role, **kwargs):
        return self._transport(method, url, role,
            headers={'Authorization': 'Bearer ' + self._access_token(), 'Accept': 'application/json' if role != 'page' else 'application/xml'}, **kwargs)

    def credit_balance(self) -> float:
        r = self._request('GET', CREDITS_URL, 'balance',
                          params=dict(onlyActive='true', includeExpired='false', nValues=1000))
        balance = parse_balance(r.json())
        self.balance_snapshots.append(dict(timestamp=datetime.now(timezone.utc).isoformat(), balance=balance))
        return balance

    def _ledger(self, value):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open('a') as stream:
            stream.write(_canonical(self._sanitize(value))+'\n')

    def _page_charge(self, process):
        url=f'https://transkribus.eu/TrpServer/rest/jobs/{int(process)}/creditTransactions'
        raw=self._request('GET',url,'page_credit',params=dict(nValues=1000)).json()
        rows=raw.get('trpCreditTransaction',[]) if isinstance(raw,dict) else raw
        if not isinstance(rows,list):
            raise TranskribusError('invalid per-job credit transactions')
        records=[{k:r.get(k) for k in ('jobId','creditValue','costFactor','nrOfPages','time')}
                 for r in rows if str(r.get('jobId'))==str(process) and r.get('creditValue',0)<0]
        if not records:
            raise TranskribusError('no matching per-page credit transaction; stop')
        return -sum(float(r['creditValue']) for r in records),records

    def read_many(self, rows: Iterable[dict[str, Any]], *, offline: bool = False,
                  window: int = 6) -> Iterator[tuple[dict[str, Any], Reading]]:
        """Bounded one-image queue, reserving one maximum charge per pending job.

        Yields (input row, Reading). One source must be fully drained before a
        caller passes the next source. All requests remain single-threaded.
        """
        if not 1<=window<=8:
            raise ValueError('queue window must be within 1..8')
        self.responses_dir.mkdir(parents=True,exist_ok=True)
        iterator=iter(rows)
        pending=[]
        exhausted=False
        stop_error=None
        with _lock(self.output_dir/'reader.lock'):
            while pending or not exhausted:
                while not exhausted and stop_error is None and len(pending)<window:
                    try:row=next(iterator)
                    except StopIteration:
                        exhausted=True
                        break
                    sha=row['crop_sha256']
                    image=Path(row['crop_path']).read_bytes()
                    if len(image)>20*1024*1024:
                        raise ValueError('crop exceeds 20 MB')
                    if hashlib.sha256(image).hexdigest()!=sha:
                        raise ValueError('crop changed; refusing submission')
                    path=self.responses_dir/(sha+'.json')
                    if path.exists():
                        value=json.loads(path.read_text())
                        if value['binding']!=self.binding() or value['crop_sha256']!=sha or hashlib.sha256(_canonical(value['response']).encode()).hexdigest()!=value['response_sha256']:
                            raise ValueError('cache binding/hash mismatch')
                        yield row,_reading(value['response'],value,cached=True)
                        continue
                    if offline:
                        continue
                    # Duplicate SHA rows wait for the first pending result.
                    same=next((p for p in pending if p['sha']==sha),None)
                    if same:
                        same['rows'].append(row)
                        continue
                    attempt=self.output_dir/'attempts'/(sha+'.json')
                    call_start=len(self.calls)
                    try:
                        if attempt.exists():
                            metadata=json.loads(attempt.read_text())
                            if metadata['binding']!=self.binding():raise ValueError('attempt binding mismatch')
                            if not metadata.get('request_id') or metadata.get('terminal_failure'):
                                raise TranskribusError('uncertain or failed prior submission; refusing duplicate')
                            process=metadata['request_id']
                        else:
                            before=self.credit_balance()
                            reserve=(len(pending)+1)*self.max_page_credits
                            if before-reserve<self.credit_floor:
                                raise CreditFloorError(f'credit floor: balance {before:g}; reserve {reserve:g} for pending+next pages; floor {self.credit_floor:g}')
                            metadata=dict(crop_sha256=sha,binding=self.binding(),receipt_id=uuid.uuid4().hex,
                                request_id=None,credits_before=before,status='submitting',credentials='environment credentials used')
                            self._save(attempt,metadata)
                            job=self._request('POST',self.base_url+'/processes','submit',json=request_payload(image,self.model_id,self.mode,self.layout_model_id)).json()
                            process=str(int(job['processId']))
                            metadata.update(request_id=process,status='submitted',submission_calls=self.calls[call_start:])
                            self._save(attempt,metadata)
                        pending.append(dict(rows=[row],sha=sha,path=path,attempt=attempt,metadata=metadata,
                                            process=process,started=self.clock(),deadline=self.clock()+self.max_wait_s))
                    except BaseException as exc:
                        # Persist safe call metadata even on an interrupted POST.
                        if attempt.exists():
                            state=json.loads(attempt.read_text())
                            state.update(error=self._redact(str(exc)) or type(exc).__name__,
                                         interrupted=isinstance(exc,KeyboardInterrupt),
                                         attempt_calls=self.calls[call_start:])
                            self._save(attempt,state)
                        if not isinstance(exc,Exception):raise
                        stop_error=exc
                        exhausted=True
                        break
                for p in list(pending):
                    call_start=len(self.calls)
                    try:
                        if self.clock()>=p['deadline']:
                            raise TranskribusError('bounded wait expired; saved process may be resumed')
                        job=self._request('GET',self.base_url+'/processes/'+p['process'],'poll').json()
                        p.setdefault('poll_calls',[]).extend(self.calls[call_start:])
                        if job.get('status') in ('CREATED','WAITING','RUNNING'):
                            continue
                        if job.get('status')!='FINISHED':
                            p['metadata'].update(status='failed',terminal_failure=True)
                            self._save(p['attempt'],p['metadata'])
                            raise TranskribusError('process failed; no further submissions')
                        call_start=len(self.calls)
                        xml=self._request('GET',self.base_url+'/processes/'+p['process']+'/page','page').text
                        raw=self._sanitize(dict(job=job,page_xml=xml))
                        parse_result(raw)
                        charge,transactions=self._page_charge(p['process'])
                        after=self.credit_balance()
                        metadata=p['metadata']
                        metadata.update(status='ok',credits_after=after,credits_used=charge,
                            credit_measurement='per-job debit transaction; account snapshots overlap queued jobs',
                            credit_transactions=transactions,latency_s=round(self.clock()-p['started'],3),
                            raw_json_path=str(p['path']),response=raw,
                            response_sha256=hashlib.sha256(_canonical(raw).encode()).hexdigest(),
                            calls=metadata.get('submission_calls',[])+p.get('poll_calls',[])+self.calls[call_start:])
                        self._save(p['path'],metadata)
                        self._save(p['attempt'],{k:v for k,v in metadata.items() if k not in ('response','calls')})
                        self._ledger({k:v for k,v in metadata.items() if k!='response'})
                        pending.remove(p)
                        for row in p['rows']:yield row,_reading(raw,metadata)
                        if after<self.credit_floor or charge>self.max_page_credits:
                            stop_error=CreditFloorError('balance floor/maximum charge exceeded; stop new submissions')
                            exhausted=True
                    except Exception as exc:
                        stop_error=exc
                        exhausted=True
                        if p in pending:pending.remove(p)
                if pending:
                    self.sleep(self.poll_interval_s)
                if stop_error is not None and not pending:
                    raise stop_error

    def read_annotation(self, crop: PathLike, *, expected_sha256: str | None = None,
                        offline: bool = False) -> Reading:
        image = Path(crop).read_bytes()
        sha = hashlib.sha256(image).hexdigest()
        if expected_sha256 is not None and sha != expected_sha256:
            raise ValueError('crop changed; refusing submission')
        if len(image) > 20 * 1024 * 1024:
            raise ValueError('crop exceeds 20 MB')
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        path = self.responses_dir / (sha + '.json')
        with _lock(self.output_dir/'reader.lock'):
            if path.exists():
                value = json.loads(path.read_text())
                if value['binding'] != self.binding() or value['crop_sha256'] != sha:
                    raise ValueError('cache binding/SHA mismatch; no re-call')
                if hashlib.sha256(_canonical(value['response']).encode()).hexdigest() != value['response_sha256']:
                    raise ValueError('cache response hash changed')
                return _reading(value['response'], value, cached=True)
            if offline:
                raise TranskribusError('offline cache miss')
            attempt = self.output_dir/'attempts'/(sha+'.json')
            before_call_count = len(self.calls)
            started = self.clock()
            if attempt.exists():
                metadata = json.loads(attempt.read_text())
                if metadata['binding'] != self.binding():
                    raise ValueError('attempt binding mismatch')
                if not metadata.get('request_id'):
                    raise TranskribusError('uncertain prior submission; refusing duplicate')
                if metadata.get('terminal_failure'):
                    raise TranskribusError('prior process failed; no repeat submission')
                before = metadata['credits_before']
                process = metadata['request_id']
            else:
                before = self.credit_balance()
                if before - self.max_page_credits < self.credit_floor:
                    raise CreditFloorError(f'credit floor: {before:g} credits; next page reserves {self.max_page_credits:g}; floor {self.credit_floor:g}')
                metadata = dict(crop_sha256=sha, binding=self.binding(), receipt_id=uuid.uuid4().hex,
                    request_id=None, credits_before=before, status='submitting',
                    credentials='environment credentials used')
                self._save(attempt, metadata)
                job = self._request('POST', self.base_url+'/processes', 'submit',
                                    json=request_payload(image, self.model_id, self.mode, self.layout_model_id)).json()
                process = str(int(job['processId']))
                metadata.update(request_id=process, status='submitted')
                self._save(attempt, metadata)
            deadline = self.clock() + self.max_wait_s
            while True:
                if self.clock() >= deadline:
                    raise TranskribusError('bounded polling wait expired; saved process may be resumed')
                job = self._request('GET', self.base_url+'/processes/'+process, 'poll').json()
                if job.get('status') == 'FINISHED':
                    break
                if job.get('status') in ('FAILED', 'CANCELLED'):
                    metadata.update(status='failed', terminal_failure=True)
                    self._save(attempt, metadata)
                    raise TranskribusError('process '+job['status']+'; run stopped')
                if job.get('status') not in ('CREATED', 'WAITING', 'RUNNING'):
                    raise TranskribusError('unknown process status')
                self.sleep(min(self.poll_interval_s, max(0, deadline-self.clock())))
            xml = self._request('GET', self.base_url+'/processes/'+process+'/page', 'page').text
            raw = self._sanitize(dict(job=job, page_xml=xml))
            parse_result(raw)
            charge, transactions = self._page_charge(process)
            after = self.credit_balance()
            metadata.update(status='ok', credits_after=after, credits_used=charge,
                credit_measurement='per-job debit transaction', credit_transactions=transactions,
                latency_s=round(self.clock()-started, 3), raw_json_path=str(path),
                calls=self.calls[before_call_count:], response=raw,
                response_sha256=hashlib.sha256(_canonical(raw).encode()).hexdigest())
            self._save(path, metadata)
            self._save(attempt, {k:v for k,v in metadata.items() if k not in ('response', 'calls')})
            self._ledger({k:v for k,v in metadata.items() if k != 'response'})
            if after < self.credit_floor:
                raise CreditFloorError('observed credit balance below floor; no later submission')
            if charge > self.max_page_credits:
                raise CreditFloorError('observed page charge exceeds reserved maximum; no later submission')
            return _reading(raw, metadata)

    def read(self, crop: PathLike, *, expected_sha256: str | None = None,
             fresh: bool = False, offline: bool = False) -> Reading:
        if fresh:
            raise ValueError('fresh submissions are disabled; preserve at-most-once cache')
        return self.read_annotation(crop, expected_sha256=expected_sha256, offline=offline)


def load_transkribus(*, enabled: bool = False, responses_dir: PathLike,
                     **kwargs: Any) -> TranskribusReader:
    if not enabled:
        raise TranskribusError('Transkribus must be explicitly enabled')
    return TranskribusReader(responses_dir=responses_dir, **kwargs)
