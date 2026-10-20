"""Read the deck's localStorage decisions from a Firefox profile (second fallback).

    python -m greekocr.labelfix.pull_firefox [--profile <dir>] [--out docs/records/labelfix/decisions/firefox_<date>.json]

Firefox keeps localStorage per origin in
`<profile>/storage/default/<origin>/ls/data.sqlite`, table `data(key, utf16_length,
conversion_type, compression_type, last_access_time, value)`; `compression_type` 1 = snappy
(decoded with `cramjam.snappy.decompress_raw`), `conversion_type` 1 = UTF-8. The deck's key is
`labelfix-deck-v1` and its value is `{card_id: {d: 'y'|'n'|'u', t: iso_time}}`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

DECK_KEY = 'labelfix-deck-v1'
PROFILES = Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'


def decode_value(value: bytes, compression_type: int, conversion_type: int) -> str:
    if compression_type == 1:
        import cramjam
        value = bytes(cramjam.snappy.decompress_raw(value))
    elif compression_type != 0:
        raise ValueError(f'unknown compression_type {compression_type}')
    if conversion_type == 1:
        return value.decode('utf-8')
    if conversion_type == 0:
        return value.decode('utf-16-le', errors='strict') if len(value) % 2 == 0 else value.decode('utf-8')
    raise ValueError(f'unknown conversion_type {conversion_type}')


def read_ls_sqlite(path: Path, key: str = DECK_KEY) -> dict | None:
    """Copy the sqlite (Firefox may hold a lock) and return the decoded JSON value of `key`."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / 'data.sqlite'
        shutil.copyfile(path, copy)
        for extra in ('-wal', '-shm'):
            src = Path(str(path) + extra)
            if src.exists():
                shutil.copyfile(src, Path(str(copy) + extra))
        con = sqlite3.connect(copy)
        try:
            row = con.execute('select value, compression_type, conversion_type from data where key = ?', (key,)).fetchone()
        finally:
            con.close()
    if row is None:
        return None
    return json.loads(decode_value(row[0], row[1], row[2]))


def find_deck_stores(profiles: Path = PROFILES, needle: str = 'review_deck') -> list[Path]:
    return [Path(p) for p in sorted(glob.glob(str(profiles / '*' / 'storage' / 'default' / f'*{needle}*' / 'ls' / 'data.sqlite')),
                                    key=os.path.getmtime)]


def decisions_from_store(store: dict) -> list[dict]:
    return [dict(id=cid, decision=v.get('d'), time=v.get('t'), source='firefox-localstorage') for cid, v in store.items()
            if isinstance(v, dict)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', type=Path, default=None, help='a Firefox profile dir (default: search all)')
    ap.add_argument('--out', type=Path, default=None)
    a = ap.parse_args(argv)
    stores = find_deck_stores(a.profile.parent if a.profile else PROFILES) if a.profile is None else \
        [Path(p) for p in glob.glob(str(a.profile / 'storage' / 'default' / '*review_deck*' / 'ls' / 'data.sqlite'))]
    if not stores:
        print('FIREFOX_LS: no deck store found')
        return 3
    store = read_ls_sqlite(stores[-1])
    if not store:
        print(f'FIREFOX_LS: key {DECK_KEY} not in {stores[-1]}')
        return 3
    decisions = decisions_from_store(store)
    out = a.out or Path('docs/records/labelfix/decisions') / f'firefox_{dt.date.today().strftime("%Y%m%d")}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(decisions, ensure_ascii=False, indent=1))
    print(f'FIREFOX_LS: {len(decisions)} decisions from {stores[-1]} -> {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
