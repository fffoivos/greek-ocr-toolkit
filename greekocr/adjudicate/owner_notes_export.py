"""Export a lead-supplied artifact-db dump; this module never reads a live db."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path

__all__ = ['owner_notes_export']


def owner_notes_export(documents: list[dict], cards: list[dict], sheets: dict[str, dict], output: str | Path) -> dict:
    """Join notes to sheet/card ids and write JSONL exclusively.

    Dump records are {sheet, db_id, note?, printed?, ...}, or {id, data: {...}}
    with one supplied sheet convention. Cards carry the same
    sheet/db_id plus arbitrary local evidence. Every sheet must explicitly set
    `no_note_status` (e.g. accepted or unreviewed) and `note_status`. A note is
    flagged for review, never automatically interpreted as a rejection. Unknown
    notes, duplicate identities and undocumented status conventions fail closed.
    """
    card_map = {(c['sheet'], c['db_id']): c for c in cards}
    if len(card_map) != len(cards):
        raise ValueError('duplicate card identity')
    notes = {}
    for raw in documents:
        document = deepcopy(raw.get('data',raw))
        document.setdefault('sheet',raw.get('sheet',next(iter(sheets)) if len(sheets)==1 else None))
        document.setdefault('db_id',raw.get('db_id',raw.get('id')))
        key = document['sheet'], document['db_id']
        if key not in card_map or key in notes:
            raise ValueError('unknown or duplicate note identity')
        notes[key] = document
    result = []
    for key, card in card_map.items():
        convention = sheets[key[0]]
        if not all(isinstance(convention.get(k),str) and convention[k] for k in ('no_note_status','note_status')):
            raise ValueError('explicit sheet status convention required')
        note = deepcopy(notes.get(key, {}))
        if not isinstance(note.get('note',''),str):
            raise ValueError('note must be text')
        has_edits = bool(note.get('note','').strip() or note.get('printed_edited'))
        result.append(dict(sheet=key[0], db_id=key[1], status=convention['note_status' if has_edits else 'no_note_status'],
                           convention=deepcopy(convention), card=deepcopy(card), document=note))
    with Path(output).open('x') as stream:
        for row in result:
            stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
    return dict(rows=len(result), notes=len(notes), output=str(output))
