"""Serial, cached, >=2-second public Parliament transport, including redirects."""
from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import urljoin

from .parliament import local_url, MAX_PDF
from .readers import atomic, read_jsonl

UA = 'GreekOCR-research-harvest/1.0 (public CC-BY proceedings; polite 2s)'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class ParliamentHTTP:
    def __init__(self, root, offline=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.offline = offline

    def _request(self, url, target, limit, depth=0):
        url = local_url(url)
        if self.offline:
            raise RuntimeError('offline Parliament cache miss')
        if depth > 5:
            raise ValueError('too many redirects')
        state = self.root / 'rate_state.json'
        with (self.root / 'http.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            last = json.loads(state.read_text())['started'] if state.exists() else 0
            time.sleep(max(0, 2.01 - (time.time() - last)))
            started = time.time()
            atomic(state, dict(started=started))
            headers_path = self.root / 'headers.tmp'
            proc = subprocess.run(['/usr/bin/curl', '--silent', '--show-error', '--max-time', '600',
                '--connect-timeout', '35', '--max-filesize', str(limit), '-A', UA,
                '-H', 'Accept-Encoding: identity', '-D', str(headers_path), '-o', str(target), url],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw = headers_path.read_text(encoding='iso-8859-1') if headers_path.exists() else ''
            blocks = [b for b in raw.split('\n\n') if b.startswith('HTTP/')]
            lines = blocks[-1].splitlines() if blocks else []
            status = int(lines[0].split()[1]) if lines else None
            headers = {k.lower(): v.strip() for l in lines[1:] if ':' in l for k,v in [l.split(':',1)]}
            size = target.stat().st_size if target.exists() else 0
            receipt = dict(url=url, started=started, finished=time.time(), status=status,
                curl_exit=proc.returncode, bytes=size, sha256=sha(target) if target.exists() else None,
                headers=headers, user_agent=UA, limit=limit)
            with (self.root / 'requests.jsonl').open('a') as stream:
                stream.write(json.dumps(receipt, ensure_ascii=False)+'\n')
                stream.flush()
            if proc.returncode:
                raise RuntimeError(f'Parliament transport failed: curl={proc.returncode}, status={status}')
        if status in (301,302,303,307,308):
            return self._request(urljoin(url, headers['location']), target, limit, depth+1)
        if status != 200:
            raise RuntimeError(f'Parliament HTTP {status}')
        if size > limit:
            raise ValueError('response exceeds size bound')
        return receipt

    def json(self, url):
        key = hashlib.sha256(url.encode()).hexdigest()
        path = self.root / 'json' / (key+'.json')
        if path.exists():
            cache = json.loads(path.read_text())
            if cache['url'] != url:
                raise ValueError('metadata cache identity changed')
            return cache['body']
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.body.tmp')
        receipt = self._request(url, temp, 20_000_000)
        body = json.loads(temp.read_text())
        atomic(path, dict(url=url, body=body, receipt=receipt))
        temp.unlink()
        return body

    def download(self, url, path, expected_size=None, checksum=None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.part')
        try:
            receipt = self._request(url, temp, MAX_PDF)
            if expected_size is not None and receipt['bytes'] != expected_size:
                raise ValueError('bitstream size disagrees with metadata')
            with temp.open('rb') as stream:
                if stream.read(5) != b'%PDF-':
                    raise ValueError('bitstream is not a PDF')
            if checksum:
                algorithm = checksum.get('checkSumAlgorithm', '').lower().replace('-', '')
                value = checksum.get('value')
                if algorithm in hashlib.algorithms_available and value:
                    with temp.open('rb') as stream:
                        digest = hashlib.file_digest(stream, algorithm).hexdigest()
                    if digest.lower() != value.lower():
                        raise ValueError('source bitstream checksum disagrees')
            temp.replace(path)
            return receipt
        finally:
            if temp.exists():
                temp.unlink()

    def receipt(self):
        rows = read_jsonl(self.root / 'requests.jsonl')
        gaps = [b['started']-a['started'] for a,b in zip(rows, rows[1:])]
        return dict(request_count=len(rows), min_gap_s=min(gaps) if gaps else None,
                    required_gap_s=2, gap_passed=all(g>=2 for g in gaps),
                    bytes=sum(r['bytes'] for r in rows), redirects=sum(r['status'] in (301,302,303,307,308) for r in rows),
                    ledger=str(self.root / 'requests.jsonl'), retries=0)
