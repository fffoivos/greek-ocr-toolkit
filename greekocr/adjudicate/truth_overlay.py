"""Validated versioned truth deltas and symmetric rescoring against frozen truth."""
from __future__ import annotations
from collections.abc import Callable
from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from ._files import sha

__all__ = ['add', 'symmetric_rescore']
_HEADS = ('breathing','accent','dialytika','subscript')


def _tuple(value: list, unknown: list[str]) -> None:
    if not isinstance(value,list) or len(value)!=4 or len(unknown)!=len(set(unknown)) or set(unknown)-set(_HEADS):
        raise ValueError('invalid four-head tuple/unknown list')
    for i,(v,size) in enumerate(zip(value,(3,4,2,2))):
        if (v is None) != (_HEADS[i] in unknown) or (v is not None and (type(v) is not int or not 0<=v<size)):
            raise ValueError('tuple domain/unknown mismatch')


def add(parent: dict, entry: dict, *, version: str, evidence_paths: list[str | Path], expected_parent: str) -> dict:
    """Add/replace a slot delta, retaining its original frozen previous_tuple.

    A child replaces an existing delta rather than applying v1.1 on top of v1:
    both are overlays against the same frozen truth. Evidence paths are explicit
    local files; no symlinks. Returned receipt hashes evidence and parent data.
    """
    if parent['version']!=expected_parent or not version or version==expected_parent:
        raise ValueError('overlay parent/version mismatch')
    if not re.fullmatch(r'.+:s\d+',entry.get('id','')):
        raise ValueError('overlay id must be line_id:s<slot>')
    previous = entry.get('previous_tuple')
    _tuple(previous,[])
    _tuple(entry.get('new_tuple'),entry.get('unknown',[]))
    if not all(isinstance(entry.get(k),str) and entry[k].strip() for k in ('source','date','status','evidence')):
        raise ValueError('source/date/status/evidence required')
    try:
        date.fromisoformat(entry['date'])
    except ValueError as exc:
        raise ValueError('valid ISO date required') from exc
    paths = [Path(p) for p in evidence_paths]
    if not paths or len(set(paths))!=len(paths):
        raise ValueError('unique local evidence paths required')
    for p in paths:
        if not p.is_file() or any(q.is_symlink() for q in [p,*p.parents]):
            raise ValueError('evidence file missing or symlinked')
    # Historical evidence notation uses a directory once followed by basenames.
    names = [s.strip() for s in entry['evidence'].split(',')]
    if len(names)!=len(paths):
        raise ValueError('entry evidence does not match supplied files')
    directory = Path(names[0]).parent
    for name, path in zip(names, paths):
        reference = Path(name)
        if '..' in reference.parts:
            raise ValueError('unsafe evidence reference')
        if reference.parent == Path('.'):
            reference = directory/reference
        if (reference.is_absolute() and reference.resolve()!=path.resolve()) or (not reference.is_absolute() and path.parts[-len(reference.parts):]!=reference.parts):
            raise ValueError('entry evidence does not match supplied files')
    entries = deepcopy(parent['entries'])
    ids = [e['id'] for e in entries]
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate parent overlay identity')
    if entry['id'] in ids:
        index = ids.index(entry['id'])
        if entries[index]['previous_tuple']!=previous:
            raise ValueError('frozen previous tuple differs from parent')
        entries[index] = deepcopy(entry)
    else:
        entries.append(deepcopy(entry))
    overlay = dict(version=version,parent=expected_parent,entries=entries)
    return dict(overlay=overlay, parent_sha256=hashlib.sha256(json.dumps(parent,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                evidence=[dict(name=n,sha256=sha(p)) for n,p in zip(names,paths)])


def symmetric_rescore(lines: list[dict], overlay: dict, predictions: dict[str, list[dict]], scorer: Callable[[list[dict], list[dict]], object]) -> dict:
    """Apply one overlay to frozen print_slots and score every arm on identical truth.

    Require every overlay id in this cohort and exact previous tuples. Each arm
    gets its own deep copy; scorer mutations cannot contaminate another arm.
    """
    updated = deepcopy(lines)
    entries = {e['id']:e for e in overlay['entries']}
    if len(entries)!=len(overlay['entries']):
        raise ValueError('duplicate overlay identity')
    seen = set()
    for line in updated:
        for slot in line['print_slots']:
            e = entries.get(slot['id'])
            if e is None:
                continue
            if slot['id'] in seen or slot['targets']!=e['previous_tuple']:
                raise ValueError('duplicate slot or previous tuple mismatch')
            _tuple(e['new_tuple'],e.get('unknown',[]))
            slot.update(targets=deepcopy(e['new_tuple']),unknown=deepcopy(e.get('unknown',[])))
            # Keep the physical adapter consistent when both instruments are present.
            if line.get('slots'):
                from scripts.labelfix.clariden.r1_common import compose
                from scripts.labelfix.clariden.r1_score import mark_set
                for physical in line['slots']:
                    if physical['slot']==slot.get('physical_slot'):
                        physical['truth']=None if e.get('unknown') else sorted(mark_set(compose(e['new_tuple'])))
            seen.add(slot['id'])
    if seen!=set(entries) or len(predictions)<2:
        raise ValueError('overlay coverage and at least two comparison arms required')
    digest = hashlib.sha256(json.dumps(updated,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return dict(truth_sha256=digest, arms={name:dict(truth_sha256=digest, score=scorer(deepcopy(updated),deepcopy(pred))) for name,pred in predictions.items()}, applied=sorted(seen))
