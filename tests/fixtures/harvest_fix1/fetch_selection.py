"""Offline archived-fetcher selection fixture. See manifest.json for custody."""
import json, re
from pathlib import Path

def selected_indices(record, page_range=None):
    if page_range is None:
        return {v['volume_id']: list(range(v['pages'] or 0)) for v in record['volumes']}
    match = re.fullmatch(r'middle:([1-9][0-9]*)', page_range)
    if not match or any(v['pages'] is None for v in record['volumes']):
        raise ValueError('page-range requires middle:N and known volume lengths')
    count = int(match[1]); total = sum(v['pages'] for v in record['volumes'])
    start = max(0, (total - count) // 2); end = min(total, start + count)
    result = {}; offset = 0
    for v in record['volumes']:
        result[v['volume_id']] = [i for i in range(v['pages']) if start <= offset+i < end]
        offset += v['pages']
    return result

def select_records(plan, selection):
    chosen = json.loads(Path(selection).read_text())
    if isinstance(chosen, dict): chosen = chosen['records']
    ids = [r if isinstance(r, str) else r.get('record_id', r.get('document_id')) for r in chosen]
    by_id = {r['record_id']:r for r in plan}
    if len(set(ids)) != len(ids) or any(i not in by_id for i in ids):
        raise ValueError('selection has duplicate or unknown record IDs')
    return [by_id[i] for i in ids]
