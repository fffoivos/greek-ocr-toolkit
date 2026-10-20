"""Serve the review deck on localhost and capture every decision as it is made.

    python -m greekocr.labelfix.deck_serve docs/records/labelfix/review_deck [--port 8765] [--decisions docs/records/labelfix/decisions]

The page (deck.py) posts each answer to `/decision` when it is served over http; the server
appends one JSON object per line to `<decisions>/<YYYYMMDD>.jsonl` (stdlib only, no download
click needed). localStorage in the browser remains the fallback; `GET /decisions` returns
everything captured so far (used by the page to re-sync on load).
"""
from __future__ import annotations

import argparse
import datetime as dt
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading


class DeckHandler(SimpleHTTPRequestHandler):
    decisions_dir: Path = Path('decisions')
    lock = threading.Lock()

    def log_message(self, fmt, *args):   # quiet
        pass

    def _json(self, code: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.rstrip('/') != '/decision':
            self._json(404, dict(error='unknown endpoint'))
            return
        n = int(self.headers.get('Content-Length') or 0)
        try:
            rec = json.loads(self.rfile.read(n).decode('utf-8'))
        except ValueError:
            self._json(400, dict(error='bad json'))
            return
        if not isinstance(rec, dict) or 'id' not in rec or rec.get('decision') not in ('y', 'n', 'u'):
            self._json(400, dict(error='need id and decision in y/n/u'))
            return
        rec.setdefault('time', dt.datetime.now().astimezone().isoformat(timespec='seconds'))
        rec['received'] = dt.datetime.now().astimezone().isoformat(timespec='seconds')
        path = self.decisions_dir / (dt.date.today().strftime('%Y%m%d') + '.jsonl')
        with self.lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'a', encoding='utf-8') as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
        self._json(200, dict(ok=True, file=str(path)))

    def do_GET(self):
        if self.path.split('?')[0].rstrip('/') == '/decisions':
            self._json(200, read_decisions(self.decisions_dir))
            return
        super().do_GET()


def read_decisions(directory: Path) -> list[dict]:
    """All captured decisions, newest last; the last record per card id wins when re-played."""
    out = []
    for path in sorted(Path(directory).glob('*.jsonl')):
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    return out


def make_server(deck_dir: Path, decisions_dir: Path, port: int = 8765, host: str = '127.0.0.1') -> ThreadingHTTPServer:
    handler = partial(DeckHandler, directory=str(deck_dir))
    DeckHandler.decisions_dir = Path(decisions_dir)
    return ThreadingHTTPServer((host, port), handler)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('deck', type=Path)
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--decisions', type=Path, default=None, help='default: <deck>/../decisions')
    a = ap.parse_args(argv)
    decisions = a.decisions or (a.deck.resolve().parent / 'decisions')
    srv = make_server(a.deck, decisions, a.port)
    print(f'serving {a.deck} at http://127.0.0.1:{a.port}/index.html — decisions -> {decisions}/<date>.jsonl', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
