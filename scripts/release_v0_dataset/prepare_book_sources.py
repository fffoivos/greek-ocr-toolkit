#!/usr/bin/env python3
"""Prepare portable bibliography from registry-cited, byte-identical repo records.

Small metadata preparation only. Never open a provenance path outside this repo,
fetch a URL, read crops, or substitute a different receipt with a similar name.
"""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import canonical, info, sha, digest

ROOT = Path(__file__).resolve().parents[2]


def prepare(registry, output, receipt):
    import pyarrow.parquet as pq
    code = ROOT / 'docs/programme_20261019/registry/book_registry/build_book_registry.py'
    module = importlib.util.spec_from_file_location('registry_alias_definition', code)
    definition = importlib.util.module_from_spec(module)
    module.loader.exec_module(definition)
    books = pq.read_table(registry).to_pylist()
    registry_sha256 = sha(registry)
    refs, alias_index = defaultdict(dict), defaultdict(set)
    for b in books:
        for a in b['aliases']:
            if a['namespace'] not in definition.REFERENCE_NAMESPACES:
                alias_index[a['namespace'], a['value']].add(b['book_id'])
        for e in b['identity_provenance']:
            refs[e['file'], e['sha256']][b['book_id']] = e
    records, inspected = {}, []
    for (original, expected), members in sorted(refs.items()):
        # The registry names pre-cleanup paths. Only the repo's retained
        # docs/records/harvest copy is eligible, and only with identical bytes.
        if '/docs/harvest/' not in original:
            continue
        relative = Path('docs/records/harvest') / original.split('/docs/harvest/', 1)[1]
        path = ROOT / relative
        entry = {'registry_path': original, 'path': str(relative), 'expected_sha256': expected}
        if not path.is_file():
            entry['status'] = 'missing'
            inspected.append(entry)
            continue
        entry.update(info(path), path=str(relative))
        if entry['sha256'] != expected:
            entry['status'] = 'different_bytes'
            inspected.append(entry)
            continue
        if path.suffix not in ('.json', '.jsonl'):
            continue
        entry['status'] = 'verified'
        inspected.append(entry)
        if path.suffix == '.jsonl':
            data = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        else:
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                data = data.get('pages', data.get('books', []))
        for ordinal, record in enumerate(data):
            if not isinstance(record, dict):
                continue
            record = dict(record)
            if record.get('image'):
                # Registry build_book_registry.py:359-364, retained verbatim.
                record['book_key'] = re.sub(r'-\d{6}$', '', Path(record['image']).stem)
            aa = definition.aliases(record, record.get('source', path.parent.name), path.parent.name)
            bids = set().union(*(alias_index.get(a, set()) for a in aa)) & members.keys()
            if len(bids) != 1:
                continue
            bid = next(iter(bids))
            fields = {k: record[k] for k in ('source', 'item', 'year', 'edition', 'volume',
                'catalogue_url', 'manifest_url', 'source_url') if record.get(k) is not None}
            if record.get('title'):
                fields['source_title'] = record['title']
            if record.get('provider'):
                fields['provider'] = record['provider']
            fields = {k: v for k, v in fields.items() if isinstance(v, (str, int))}
            if not fields:
                continue
            key = canonical([bid, fields])
            item = records.setdefault(key, {'book_id': bid, 'registry_sha256': registry_sha256,
                                            'source_record_id': digest(key),
                                            'fields': fields, 'evidence': []})
            item['evidence'].append({'path': str(relative), 'sha256': expected,
                                    'ordinal': ordinal, 'registry_provenance': members[bid]})
    output.write_text(''.join(canonical(records[k]) + '\n' for k in sorted(records)))
    receipt.write_text(json.dumps({'registry': info(registry), 'alias_definition': info(code),
        'code': info(__file__), 'output': info(output), 'records': len(records),
        'books': len({r['book_id'] for r in records.values()}), 'inspected': inspected,
        'rule': 'Only registry-cited sources with byte-identical repo copies and one exact alias book match. '
                'No URL template expansion; page values are not promoted to book bibliography.'}, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    prepare(a.registry, a.output, a.receipt)
