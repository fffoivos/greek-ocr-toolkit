"""Receipt-bound Document AI REST reader. No implicit retries or client library."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import math
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable, Iterable
import uuid

DEFAULT_VERSION = 'pretrained-ocr-v2.1-2024-08-07'
PRICE_PER_PAGE_USD = 1.50 / 1000
__all__ = ['DocAIReader', 'Reading', 'DocAIError', 'DEFAULT_VERSION']


@dataclass(frozen=True)
class Reading:
    text: str
    lines: list[str]
    token_confidences: list[dict[str, Any]]
    symbol_confidences: list[dict[str, Any]]
    mean_symbol_conf: float | None
    min_symbol_conf: float | None
    raw_json_path: str
    request_id: str | None
    latency_s: float
    crop_sha256: str = ''
    cached: bool = False
    receipt_id: str = ''


class DocAIError(RuntimeError):
    """A service failure, with its response retained when available."""


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(_canonical(value) + '\n', encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _confidence_items(page: dict, kind: str, text: str, page_number: int) -> list[dict]:
    items = []
    for item in page.get(kind, []):
        layout = item.get('layout', {})
        segments = layout.get('textAnchor', {}).get('textSegments', [])
        spans = []
        for segment in segments:
            start, end = int(segment.get('startIndex', 0)), int(segment['endIndex'])
            if not 0 <= start <= end <= len(text):
                raise ValueError('Document AI text anchor is outside document.text')
            spans.append(dict(start=start, end=end))
        confidence = layout.get('confidence')
        if confidence is not None:
            confidence = float(confidence)
            if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise ValueError('Document AI confidence must be finite and in [0, 1]')
        items.append(dict(text=''.join(text[s['start']:s['end']] for s in spans),
                          confidence=confidence, segments=spans, page=page_number))
    return items


def _reading(raw: dict, metadata: dict, *, cached: bool = False) -> Reading:
    if raw.get('error'):
        raise DocAIError('Document AI returned an error: ' + _canonical(raw['error']))
    document = raw.get('document')
    if not isinstance(document, dict) or not isinstance(document.get('text'), str):
        raise ValueError('Document AI response is missing document.text')
    if document.get('error'):
        raise DocAIError('Document AI document error: ' + _canonical(document['error']))
    pages = document.get('pages', [])
    if len(pages) != 1:
        raise ValueError('line-crop response must contain exactly one page')
    text = document['text']
    tokens = _confidence_items(pages[0], 'tokens', text, 1)
    symbols = _confidence_items(pages[0], 'symbols', text, 1)
    confidences = [s['confidence'] for s in symbols if s['confidence'] is not None]
    # splitlines keeps internal blank lines, but does not invent a line for a terminal LF.
    return Reading(text=text, lines=text.splitlines(), token_confidences=tokens,
                   symbol_confidences=symbols,
                   mean_symbol_conf=sum(confidences) / len(confidences) if confidences else None,
                   min_symbol_conf=min(confidences) if confidences else None,
                   raw_json_path=metadata['raw_json_path'], request_id=metadata['request_id'],
                   latency_s=metadata['latency_s'], crop_sha256=metadata['crop_sha256'],
                   receipt_id=metadata['receipt_id'], cached=cached)


class DocAIReader:
    def __init__(self, project: str, location: str, processor_id: str, version: str | None = None,
                 language_hints: Iterable[str] = ('el',), enable_symbol: bool = True,
                 user_project: str | None = None, *, receipts_dir: str | Path = 'docai_receipts',
                 fresh: bool = False, timeout: float = 60.0,
                 transport: Callable | None = None, credentials: Any = None):
        for name, value in [('project', project), ('location', location), ('processor_id', processor_id),
                            ('version', version), ('user_project', user_project)]:
            pattern = r'[A-Za-z0-9_.-]+' if name == 'version' else r'[A-Za-z0-9_-]+'
            if value is not None and (not isinstance(value, str) or not re.fullmatch(pattern, value)):
                raise ValueError(f'{name} must be a nonempty resource ID')
        if any(value is None for value in (project, location, processor_id)):
            raise ValueError('project, location and processor_id are required')
        if isinstance(language_hints, str):
            raise ValueError('language_hints must be a sequence of language codes')
        hints = tuple(language_hints)
        if any(not isinstance(h, str) or not h for h in hints):
            raise ValueError('language hints must be nonempty strings')
        if not isinstance(enable_symbol, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('enable_symbol must be boolean and timeout must be positive')
        self.project, self.location, self.processor_id = project, location, processor_id
        self.version, self.language_hints, self.enable_symbol = version, hints, enable_symbol
        self.user_project = user_project or project
        self.receipts_dir = Path(receipts_dir).resolve()
        self.ledger_path = self.receipts_dir / 'ledger.jsonl'
        self.fresh, self.timeout = fresh, timeout
        self._transport, self._credentials = transport, credentials
        self._auth_lock = threading.Lock()

    def binding(self) -> dict:
        """Return a new deterministic JSON object; None version means unpinned default."""
        return dict(project=self.project, location=self.location, processor=self.processor_id,
                    version=self.version, user_project=self.user_project,
                    options=dict(ocrConfig=dict(enableSymbol=self.enable_symbol,
                                                hints=dict(languageHints=list(self.language_hints)))))

    @property
    def endpoint(self) -> str:
        resource = f'projects/{self.project}/locations/{self.location}/processors/{self.processor_id}'
        if self.version is not None:
            resource += '/processorVersions/' + self.version
        return f'https://{self.location}-documentai.googleapis.com/v1/{resource}:process'

    def _headers(self) -> dict:
        from google.auth.transport.requests import Request
        headers = {'Content-Type': 'application/json', 'x-goog-user-project': self.user_project}
        with self._auth_lock:
            if self._credentials is None:
                import google.auth
                self._credentials, _ = google.auth.default(
                    scopes=['https://www.googleapis.com/auth/cloud-platform'],
                    quota_project_id=self.user_project)
            self._credentials.before_request(Request(), 'POST', self.endpoint, headers)
        headers['x-goog-user-project'] = self.user_project
        return headers

    def _ledger(self, row: dict) -> None:
        with _lock(self.receipts_dir / 'ledger.lock'):
            with self.ledger_path.open('a', encoding='utf-8') as stream:
                stream.write(_canonical(row) + '\n')

    def read(self, path: str | Path, *, fresh: bool | None = None,
             expected_sha256: str | None = None) -> Reading:
        data = Path(path).read_bytes()
        crop_sha = _sha(data)
        if expected_sha256 is not None and crop_sha != expected_sha256:
            raise ValueError('crop changed since manifest validation; no call made')
        from PIL import Image
        with Image.open(io.BytesIO(data)) as image:
            mime = {'PNG': 'image/png', 'JPEG': 'image/jpeg', 'TIFF': 'image/tiff'}.get(image.format)
            if mime is None or getattr(image, 'n_frames', 1) != 1:
                raise ValueError('a crop must be a single-page PNG, JPEG or TIFF image')
        binding = self.binding()
        binding_sha = _sha(_canonical(binding).encode('utf-8'))
        directory = self.receipts_dir / binding_sha / (crop_sha + '-' + (self.version or 'default'))
        with _lock(directory / 'receipt.lock'):
            cache = directory / 'cache.json'
            use_fresh = self.fresh if fresh is None else fresh
            if cache.is_file() and not use_fresh:
                metadata = json.loads(cache.read_text(encoding='utf-8'))
                if metadata['binding'] != binding or metadata['crop_sha256'] != crop_sha:
                    raise ValueError('receipt binding mismatch; inspect cache or request --fresh')
                raw_path = Path(metadata['raw_json_path'])
                if raw_path.parent != directory or _sha(raw_path.read_bytes()) != metadata['raw_sha256']:
                    raise ValueError('raw receipt changed; inspect cache or request --fresh')
                reading = _reading(json.loads(raw_path.read_text(encoding='utf-8')), metadata, cached=True)
                self._ledger(dict(metadata, timestamp=_timestamp(), cached=True, status='cache_hit',
                                  pages_billed=0, latency_s=0.0,
                                  mean_symbol_conf=reading.mean_symbol_conf, min_symbol_conf=reading.min_symbol_conf))
                return reading
            headers = self._headers()
            transport = self._transport
            if transport is None:
                import requests
                transport = requests.post
            payload = dict(rawDocument=dict(content=base64.b64encode(data).decode('ascii'), mimeType=mime),
                           processOptions=binding['options'])
            receipt_id = uuid.uuid4().hex
            raw_path = directory / (receipt_id + '.json')
            metadata = dict(crop_sha256=crop_sha, version=self.version, binding=binding,
                            timestamp=_timestamp(), receipt_id=receipt_id, request_id=None,
                            raw_json_path=str(raw_path), latency_s=0.0)
            start = time.perf_counter()
            status_code = None
            try:
                response = transport(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
                status_code = response.status_code
                metadata['latency_s'] = time.perf_counter() - start
                metadata['request_id'] = (response.headers.get('x-goog-request-id') or
                                          response.headers.get('x-request-id'))
                try:
                    raw = response.json()
                except ValueError:
                    raw = dict(error=dict(http_status=response.status_code, body=response.text))
                _atomic_json(raw_path, raw)
                metadata['raw_sha256'] = _sha(raw_path.read_bytes())
                if not 200 <= response.status_code < 300:
                    raise DocAIError(f'Document AI HTTP {response.status_code}; raw response: {raw_path}')
                reading = _reading(raw, metadata)
            except Exception as error:
                metadata['latency_s'] = time.perf_counter() - start
                if not raw_path.is_file():
                    metadata['raw_json_path'] = None
                self._ledger(dict(metadata, cached=False, status='error',
                                  pages_billed=1 if status_code is not None and 200 <= status_code < 300 else None,
                                  page_units_reserved=1, error=str(error),
                                  mean_symbol_conf=None, min_symbol_conf=None))
                raise DocAIError(str(error)) from error
            self._ledger(dict(metadata, cached=False, status='ok', pages_billed=1,
                              mean_symbol_conf=reading.mean_symbol_conf, min_symbol_conf=reading.min_symbol_conf))
            _atomic_json(cache, metadata)
            return reading

    def read_batch(self, paths: Iterable[str | Path], concurrency: int = 4, *,
                   fresh: bool | None = None) -> list[Reading]:
        if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
            raise ValueError('concurrency must be a positive integer')
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            return list(pool.map(lambda path: self.read(path, fresh=fresh), paths))
