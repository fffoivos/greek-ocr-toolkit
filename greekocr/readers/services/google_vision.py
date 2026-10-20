"""Explicit, ADC-authenticated Cloud Vision REST reader with at-most-once caching."""
from __future__ import annotations

import base64
from dataclasses import dataclass
import io
import json
import math
import os
from pathlib import Path
import threading
import time
from typing import Any, Callable, Iterable
import unicodedata
import uuid

from .google_docai import _atomic_json, _canonical, _lock, _sha, _timestamp

__all__ = ['VisionReader', 'VisionReading', 'VisionError', 'load_google_vision']
ENDPOINT = 'https://vision.googleapis.com/v1/images:annotate'
DEFAULT_RESPONSES = Path(__file__).resolve().parents[3] / 'docs/records/harvest/vision_failed_lines/responses'


class VisionError(RuntimeError):
    """A retained service failure; the same crop is never automatically retried."""


@dataclass(frozen=True)
class VisionReading:
    text: str  # NFD public reader text
    raw_text: str
    lines: list[str]
    line_confidences: list[float | None]
    annotation: dict[str, Any]  # unchanged fullTextAnnotation, including hierarchy
    blocks: list[dict[str, Any]]
    paragraphs: list[dict[str, Any]]
    token_confidences: list[dict[str, Any]]
    symbol_confidences: list[dict[str, Any]]
    detected_languages: list[dict[str, Any]]
    mean_symbol_conf: float | None
    min_symbol_conf: float | None
    line_count_source: str
    raw_json_path: str
    request_id: str | None
    latency_s: float
    crop_sha256: str = ''
    cached: bool = False
    receipt_id: str = ''


def _confidence(value: Any) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Vision confidence must be finite and in [0, 1]')
    return value


def _piece(symbol: dict) -> str:
    br = symbol.get('property', {}).get('detectedBreak', {})
    # HYPHEN is a detected line-end hyphen absent from symbol text. Preserve
    # its structural break without fabricating an emitted glyph.
    separator = {'SPACE': ' ', 'SURE_SPACE': ' ', 'EOL_SURE_SPACE': '\n',
                 'LINE_BREAK': '\n', 'HYPHEN': '\n'}.get(br.get('type'), '')
    text = symbol.get('text', '')
    if not isinstance(text, str):
        raise ValueError('Vision symbol text must be a string')
    return separator + text if br.get('isPrefix') else text + separator


def _reading(raw: dict, metadata: dict, *, cached: bool = False) -> VisionReading:
    if raw.get('error'):
        raise VisionError('Vision error: ' + _canonical(raw['error']))
    responses = raw.get('responses')
    if not isinstance(responses, list) or len(responses) != 1:
        raise ValueError('Vision response must contain exactly one image response')
    response = responses[0]
    if response.get('error'):
        raise VisionError('Vision image error: ' + _canonical(response['error']))
    annotation = response.get('fullTextAnnotation', {})
    raw_text = annotation.get('text', '')
    if not isinstance(raw_text, str):
        raise ValueError('Vision annotation.text must be a string')
    pages = annotation.get('pages', [])
    if len(pages) > 1:
        raise ValueError('line crop must not contain multiple Vision pages')
    blocks, paragraphs, words, symbols, languages, lines, line_conf = [], [], [], [], [], [], []

    def record(node: dict, level: str, address: list[int], text: str) -> dict:
        detected = [dict(languageCode=x.get('languageCode', ''), confidence=_confidence(x.get('confidence')))
                    for x in node.get('property', {}).get('detectedLanguages', [])]
        languages.extend(dict(x, level=level, address=address) for x in detected)
        return dict(text=text, confidence=_confidence(node.get('confidence')),
                    bounding_box=node.get('boundingBox', {}), detected_languages=detected,
                    property=node.get('property', {}), address=address)

    for pi, page in enumerate(pages):
        record(page, 'page', [pi], raw_text)
        for bi, block in enumerate(page.get('blocks', [])):
            block_text = []
            for qi, paragraph in enumerate(block.get('paragraphs', [])):
                paragraph_text = []
                for wi, word in enumerate(paragraph.get('words', [])):
                    word_text = []
                    for si, symbol in enumerate(word.get('symbols', [])):
                        piece = _piece(symbol)
                        word_text.append(piece)
                        symbols.append(record(symbol, 'symbol', [pi, bi, qi, wi, si], symbol.get('text', '')))
                    text = ''.join(word_text)
                    words.append(record(word, 'word', [pi, bi, qi, wi], text))
                    paragraph_text.append(text)
                text = ''.join(paragraph_text)
                entry = record(paragraph, 'paragraph', [pi, bi, qi], text)
                paragraphs.append(entry)
                # Paragraph boundaries are explicit. Within them, only reported
                # symbol breaks split lines; no geometric or whitespace repair.
                current_lines = text.splitlines() if text else []
                lines.extend(current_lines)
                line_conf.extend([entry['confidence']] * len(current_lines))
                block_text.append(text)
            blocks.append(record(block, 'block', [pi, bi], ''.join(block_text)))
    if symbols and 'text' not in annotation:
        raise ValueError('Vision nonempty hierarchy is missing annotation.text')
    source = 'fullTextAnnotation paragraphs / symbol detectedBreak (line confidence = paragraph confidence)'
    if not paragraphs and raw_text:
        lines, line_conf = raw_text.splitlines(), [None] * len(raw_text.splitlines())
        source = 'fullTextAnnotation.text.splitlines fallback (no paragraphs)'
    confidences = [s['confidence'] for s in symbols if s['confidence'] is not None]
    return VisionReading(text=unicodedata.normalize('NFD', raw_text), raw_text=raw_text,
        lines=lines, line_confidences=line_conf, annotation=annotation, blocks=blocks,
        paragraphs=paragraphs, token_confidences=words, symbol_confidences=symbols,
        detected_languages=languages,
        mean_symbol_conf=sum(confidences) / len(confidences) if confidences else None,
        min_symbol_conf=min(confidences) if confidences else None, line_count_source=source,
        raw_json_path=metadata.get('raw_json_path', ''), request_id=metadata.get('request_id'),
        latency_s=metadata.get('latency_s', 0), crop_sha256=metadata.get('crop_sha256', ''),
        cached=cached, receipt_id=metadata.get('receipt_id', ''))


class VisionReader:
    """Construct explicitly; ADC and requests are loaded only on a cache miss."""

    def __init__(self, user_project: str, *, language_hints: Iterable[str] = ('el', 'grc'),
                 responses_dir: str | Path = DEFAULT_RESPONSES, timeout: float = 60,
                 credentials: Any = None, transport: Callable | None = None) -> None:
        if not isinstance(user_project, str) or not user_project:
            raise ValueError('a quota project is required')
        if isinstance(language_hints, str):
            raise ValueError('language_hints must be a sequence')
        hints = tuple(language_hints)
        if any(not isinstance(x, str) or not x for x in hints):
            raise ValueError('language hints must be nonempty strings')
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout must be positive')
        self.user_project, self.language_hints, self.timeout = user_project, hints, timeout
        self.responses_dir = Path(responses_dir).resolve()
        self.receipts_dir = self.responses_dir.parent / 'adapter_receipts'
        self.ledger_path = self.receipts_dir / 'ledger.jsonl'
        self._credentials, self._transport = credentials, transport
        self._auth_lock = threading.Lock()

    def binding(self) -> dict[str, Any]:
        """Return defensive request settings, including hints and unpinned model."""
        return dict(engine='vision', endpoint=ENDPOINT, user_project=self.user_project,
                    feature='DOCUMENT_TEXT_DETECTION', model='provider default (unpinned)',
                    language_hints=list(self.language_hints))

    def _headers(self) -> dict:
        from google.auth.transport.requests import Request
        headers = {'Content-Type': 'application/json', 'x-goog-user-project': self.user_project}
        with self._auth_lock:
            if self._credentials is None:
                import google.auth
                self._credentials, _ = google.auth.default(
                    scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=self.user_project)
            self._credentials.before_request(Request(), 'POST', ENDPOINT, headers)
        headers['x-goog-user-project'] = self.user_project
        return headers

    def _ledger(self, row: dict) -> None:
        with _lock(self.receipts_dir / 'ledger.lock'):
            with self.ledger_path.open('a', encoding='utf-8') as stream:
                stream.write(_canonical(row) + '\n')

    def read(self, path: str | Path) -> str:
        """Return NFD text, retaining whitespace and all reported lines."""
        return self.read_annotation(path).text

    def read_annotation(self, path: str | Path, *, expected_sha256: str | None = None) -> VisionReading:
        """Return full annotation, flattened hierarchy, confidence and receipt."""
        data = Path(path).read_bytes()
        crop_sha = _sha(data)
        if expected_sha256 is not None and crop_sha != expected_sha256:
            raise ValueError('crop changed since manifest validation; no call made')
        from PIL import Image
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ('PNG', 'JPEG', 'TIFF') or getattr(image, 'n_frames', 1) != 1:
                raise ValueError('a crop must be a single-page PNG, JPEG or TIFF image')
        binding = self.binding()
        cache = self.responses_dir / (crop_sha + '.json')
        with _lock(self.receipts_dir / (crop_sha + '.lock')):
            self.responses_dir.mkdir(parents=True, exist_ok=True)
            if cache.exists():
                value = json.loads(cache.read_text())
                if value['binding'] != binding or value['crop_sha256'] != crop_sha:
                    raise ValueError('crop cache SHA/options mismatch; refusing re-call')
                if _sha(_canonical(value['response']).encode()) != value['response_sha256']:
                    raise ValueError('raw response envelope changed; refusing re-call')
                raw_path = Path(value['raw_json_path'])
                if raw_path.parent != self.receipts_dir or _sha(raw_path.read_bytes()) != value['raw_sha256']:
                    raise ValueError('raw receipt changed; refusing re-call')
                reading = _reading(value['response'], value, cached=True)
                self._ledger(dict(value, response=None, status='cache_hit', cached=True,
                                  pages_billed=0, images_billed=0, timestamp=_timestamp(), latency_s=0))
                return reading
            attempt = self.receipts_dir / (crop_sha + '.attempt.json')
            if attempt.exists():
                raise VisionError('prior attempt has no successful cache; refusing automatic re-call')
            # Auth failure is not a submitted API request. Let the driver stop;
            # no access token or headers are retained in any receipt.
            headers = self._headers()
            payload = dict(requests=[dict(image=dict(content=base64.b64encode(data).decode('ascii')),
                features=[dict(type='DOCUMENT_TEXT_DETECTION')],
                imageContext=dict(languageHints=list(self.language_hints)))])
            receipt_id = uuid.uuid4().hex
            raw_path = self.receipts_dir / (crop_sha + '.raw.json')
            metadata = dict(schema_version=1, crop_sha256=crop_sha, binding=binding,
                language_hints=list(self.language_hints), timestamp=_timestamp(), receipt_id=receipt_id,
                request_id=None, raw_json_path=str(raw_path), latency_s=0.0)
            _atomic_json(attempt, metadata)
            start, status_code = time.perf_counter(), None
            try:
                transport = self._transport
                if transport is None:
                    import requests
                    transport = requests.post
                response = transport(ENDPOINT, json=payload, headers=headers, timeout=self.timeout)
                status_code = response.status_code
                metadata['latency_s'] = time.perf_counter() - start
                metadata['request_id'] = response.headers.get('x-goog-request-id') or response.headers.get('x-request-id')
                try:
                    raw = response.json()
                except ValueError:
                    raw = dict(error=dict(http_status=status_code, body=response.text))
                _atomic_json(raw_path, raw)
                metadata['raw_sha256'] = _sha(raw_path.read_bytes())
                if not 200 <= status_code < 300:
                    raise VisionError(f'Vision HTTP {status_code}: {_canonical(raw)}; raw response: {raw_path}')
                reading = _reading(raw, metadata)
                value = dict(metadata, response=raw, response_sha256=_sha(_canonical(raw).encode()))
                _atomic_json(cache, value)
            except Exception as error:
                metadata['latency_s'] = time.perf_counter() - start
                if not raw_path.exists():
                    metadata['raw_json_path'] = None
                self._ledger(dict(metadata, cached=False, status='error', pages_billed=None,
                                  images_billed=None, image_units_reserved=1, error=str(error)))
                raise VisionError(str(error)) from error
            self._ledger(dict(metadata, cached=False, status='ok', pages_billed=1, images_billed=1,
                              mean_symbol_conf=reading.mean_symbol_conf, min_symbol_conf=reading.min_symbol_conf))
            return reading


def load_google_vision(*, enabled: bool = False, user_project: str | None = None,
                       language_hints: Iterable[str] = ('el', 'grc'),
                       responses_dir: str | Path = DEFAULT_RESPONSES) -> VisionReader:
    """Factory gated by explicit opt-in or GREEKOCR_ENABLE_GOOGLE_VISION=1, then ADC."""
    if not enabled and os.environ.get('GREEKOCR_ENABLE_GOOGLE_VISION') != '1':
        raise ValueError('Google Vision is disabled; explicitly enable service calls')
    project = user_project or os.environ.get('GOOGLE_CLOUD_QUOTA_PROJECT')
    if not project:
        raise ValueError('set GOOGLE_CLOUD_QUOTA_PROJECT or pass user_project')
    return VisionReader(project, language_hints=language_hints, responses_dir=responses_dir)
