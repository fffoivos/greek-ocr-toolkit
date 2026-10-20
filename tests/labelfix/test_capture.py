"""Server capture of decisions, Firefox localStorage pull, and ingestion of the captured jsonl."""
import json
import sqlite3
import threading
import urllib.request

import pytest

from greekocr.labelfix.deck_serve import make_server, read_decisions
from greekocr.labelfix.pull_firefox import DECK_KEY, decisions_from_store, read_ls_sqlite


@pytest.fixture
def served(tmp_path, monkeypatch):
    deck = tmp_path / 'deck'
    deck.mkdir()
    (deck / 'index.html').write_text('<html>deck</html>')
    try:
        srv = make_server(deck, tmp_path / 'decisions', port=0)
    except PermissionError as exc:
        pytest.skip(f'loopback server binding is unavailable in this sandbox: {exc}')
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    # the offline fixture blocks socket.connect; restore the real one for loopback in this test
    import socket
    monkeypatch.setattr(socket.socket, 'connect', _real_connect)
    yield srv, srv.server_address[1], tmp_path / 'decisions'
    srv.shutdown()


_real_connect = None


def _capture_real_connect():
    global _real_connect
    import socket
    if _real_connect is None:
        _real_connect = socket.socket.connect


_capture_real_connect()


def test_server_appends_each_decision_and_serves_static(served):
    srv, port, ddir = served
    body = json.dumps(dict(id='accent-000', rule='accent', line_id='l1', word_index=0, decision='y')).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/decision', data=body, headers={'Content-Type': 'application/json'})
    import urllib.request as ur
    opener = ur.build_opener()
    r = opener.open(req)
    assert json.loads(r.read())['ok']
    bad = urllib.request.Request(f'http://127.0.0.1:{port}/decision', data=b'{"id":"x"}', headers={'Content-Type': 'application/json'})
    with pytest.raises(urllib.error.HTTPError):
        opener.open(bad)
    rows = read_decisions(ddir)
    assert len(rows) == 1 and rows[0]['decision'] == 'y' and 'received' in rows[0]
    page = opener.open(f'http://127.0.0.1:{port}/index.html').read()
    assert b'deck' in page
    listed = json.loads(opener.open(f'http://127.0.0.1:{port}/decisions').read())
    assert listed[0]['id'] == 'accent-000'


def _make_ls_sqlite(path, value: bytes, compression_type: int, conversion_type: int = 1):
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE data( key TEXT PRIMARY KEY, utf16_length INTEGER NOT NULL, conversion_type INTEGER NOT NULL, '
                'compression_type INTEGER NOT NULL, last_access_time INTEGER NOT NULL DEFAULT 0, value BLOB NOT NULL)')
    con.execute('insert into data values (?,?,?,?,?,?)', (DECK_KEY, 10, conversion_type, compression_type, 0, value))
    con.commit()
    con.close()


def test_firefox_pull_raw_and_snappy(tmp_path):
    store = {'breathing-000': {'d': 'y', 't': '2026-10-16T14:00:00Z'}, 'breathing-001': {'d': 'u', 't': '2026-10-16T14:00:05Z'}}
    raw = json.dumps(store).encode('utf-8')
    _make_ls_sqlite(tmp_path / 'raw.sqlite', raw, compression_type=0)
    assert read_ls_sqlite(tmp_path / 'raw.sqlite') == store
    cramjam = pytest.importorskip('cramjam')
    comp = bytes(cramjam.snappy.compress_raw(raw))
    _make_ls_sqlite(tmp_path / 'snappy.sqlite', comp, compression_type=1)
    assert read_ls_sqlite(tmp_path / 'snappy.sqlite') == store
    rows = decisions_from_store(store)
    assert {r['id']: r['decision'] for r in rows} == {'breathing-000': 'y', 'breathing-001': 'u'}


def test_ingest_reads_captured_jsonl(tmp_path):
    from tests.labelfix.test_ingest import make_deck
    from greekocr.labelfix.ingest_decisions import main
    deck, dec = make_deck(tmp_path)
    ddir = tmp_path / 'out' / 'decisions'
    ddir.mkdir(parents=True)
    (ddir / '20261016.jsonl').write_text('\n'.join(json.dumps(r) for r in [
        dict(id='accent-000', line_id='l1', word_index=0, decision='n'),
        dict(id='accent-000', line_id='l1', word_index=0, decision='y'),   # later record wins
        dict(id='final_grave-000', line_id='l6', word_index=3, decision='y')]) + '\n')
    assert main(['--deck', str(deck), '--out', str(tmp_path / 'out'), '--date', '20261016']) == 0
    s = (tmp_path / 'out' / 'owner_review_summary.md').read_text()
    assert '| accent | 1 | 1 | 0 | 0 |' in s and '| final_grave | 1 |' in s and 'Sources:' in s
