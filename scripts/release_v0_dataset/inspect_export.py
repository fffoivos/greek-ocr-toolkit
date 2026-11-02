#!/usr/bin/env python3
"""Read-only export diagnosis; pipe over SSH, never imports the deployed builder."""
import argparse
import json
from pathlib import Path
import sqlite3
import time


def inspect(root, log):
    root = Path(root)
    db = sqlite3.connect((root / 'work/joins.sqlite').as_uri() + '?mode=ro', uri=True)
    db.execute('PRAGMA query_only=ON')
    db.execute('PRAGMA temp_store=MEMORY')
    db.execute('PRAGMA cache_size=-131072')
    result = {'root': str(root), 'log': str(log), 'read_only': True,
              'sqlite_version': sqlite3.sqlite_version}
    result['sizes'] = {str(p.relative_to(root)): p.stat().st_size
                       for p in root.rglob('*') if p.is_file() and '/slices/' not in str(p)}
    result['counts'] = dict(db.execute('SELECT t,COUNT(*) FROM records GROUP BY t'))
    result['indexes'] = list(db.execute("SELECT name,sql FROM sqlite_master WHERE type='index' AND tbl_name='records'"))
    old = "SELECT j FROM records WHERE t='label_versions' AND json_extract(j,'$.row_key')=? ORDER BY k"
    forced = old.replace('FROM records WHERE', 'FROM records INDEXED BY records_row WHERE')
    keys = [json.loads(j)['row_key'] for j, in db.execute("SELECT j FROM records WHERE t='rows' ORDER BY page,k LIMIT 2")]
    result['lookups'] = {}
    for name, query in [('old', old), ('existing_index_forced', forced)]:
        started = time.monotonic()
        db.set_progress_handler(lambda: int(time.monotonic() - started > 5), 1000)
        try:
            rows = [list(db.execute(query, (key,))) for key in keys]
        except sqlite3.OperationalError as exc:
            rows = None
            result[name + '_error'] = str(exc)
        finally:
            db.set_progress_handler(None, 0)
        result['lookups'][name] = {'plan': list(db.execute('EXPLAIN QUERY PLAN ' + query, (keys[0],))),
                                  'seconds': time.monotonic() - started, 'queries': len(keys),
                                  'returned_rows': sum(map(len, rows)) if rows is not None else None}
        if name == 'old':
            before = rows
        else:
            result['identical_query_results'] = before == rows if before is not None and rows is not None else None
    result['log_events'] = []
    for line in Path(log).read_text().splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and ('stage' in value or 'stages' in value):
            result['log_events'].append(value)
    db.close()
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root'); p.add_argument('log')
    args = p.parse_args()
    print(json.dumps(inspect(args.root, args.log), indent=2))
