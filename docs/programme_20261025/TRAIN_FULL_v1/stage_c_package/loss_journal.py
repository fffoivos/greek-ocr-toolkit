"""Append-only JSONL index of immutable per-point loss records.

Point files publish first. A crash before index append is reconciled from them.
A torn final append is preserved, newline-terminated and explicitly witnessed by
a recovery record; no existing byte is overwritten or truncated.
"""
import hashlib
import json
import os
from pathlib import Path
from common import read, spec


def records(path):
    path = Path(path)
    lines = path.read_bytes().splitlines(keepends=True) if path.exists() else []
    entries, pending = [], None
    for line in lines:
        try:
            item = json.loads(line)
        except ValueError:
            if pending is not None:
                raise ValueError('multiple corrupt loss-journal records')
            pending = line.rstrip(b'\n')
            continue
        if pending is not None:
            if item != dict(torn_append_sha256=hashlib.sha256(pending).hexdigest()):
                raise ValueError('unwitnessed corrupt loss-journal record')
            pending = None
        else:
            entries.append(item)
    return entries, pending


def append_point(journal, point):
    journal, point = Path(journal), Path(point)
    prior, torn = records(journal)
    value = read(point)
    entry = dict(step=value['step'], drawn_lines=value['drawn_lines'],
                 instruments=value['instruments'], record=spec(point))
    if 'train_loss_at_step' in value:
        entry['train_loss_at_step'] = value['train_loss_at_step']
    if 'checkpoint' in value:
        entry['checkpoint'] = value['checkpoint']
    matches = [v for v in prior if v['step'] == entry['step']]
    if matches and matches != [entry]:
        raise ValueError('duplicate/changed loss-journal point')
    if prior and not matches and prior[-1]['step'] >= entry['step']:
        raise ValueError('out-of-order loss-journal append')
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open('ab') as stream:
        raw = journal.read_bytes()
        if raw and not raw.endswith(b'\n'):
            stream.write(b'\n')
        if torn is not None:
            stream.write((json.dumps(dict(torn_append_sha256=hashlib.sha256(torn).hexdigest())) + '\n').encode())
        if not matches:
            stream.write((json.dumps(entry, sort_keys=True, allow_nan=False) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
