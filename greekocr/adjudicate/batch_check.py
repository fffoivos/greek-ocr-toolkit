"""Validate a completed dealt batch through protocol.resolve without publishing truth."""
from __future__ import annotations
import json
from pathlib import Path
from ._files import hashes
from .protocol import resolve

__all__ = ['batch_check']


def batch_check(folder: str | Path, assignment: dict, answers: list[dict], keys: list[dict], *, adapter: str = 'canonical', gate_spec: dict | None = None) -> dict:
    """Check exact assigned order, hash custody, schema and controls via a dry run.

    The one batch is mirrored for resolve's two-input validation interface. This
    is expressly NOT two-reader agreement and returns no truth or consensus.
    Keys are supplied privately by the coordinator, never copied to the folder.
    Answer files must be kept outside the immutable assignment tree.
    """
    root = Path(folder)
    if hashes(root)!=assignment['files']:
        raise ValueError('assignment hash mismatch')
    cards = json.loads((root/'items_blind.json').read_text())
    ids = [c['id'] for c in cards]
    answer_ids = [a.get('id',a.get('card_id')) for a in answers]
    if ids!=assignment['ids'] or answer_ids!=ids:
        raise ValueError('answer coverage/order mismatch')
    selected = [k for k in keys if k['id'] in set(ids)]
    if len(selected)!=len(cards):
        raise ValueError('private key coverage mismatch')
    # The dry run uses this folder's assigned order as its canonical first input.
    result = resolve(cards,selected,answers,list(reversed(answers)),adapter=adapter,gate_spec=gate_spec)
    return dict(status='BATCH_CHECK_PASSED' if result['gate']['passed'] else 'CONTROLS_FAILED',
                gate=result['gate'], checked=len(cards), dry_run=True, independent_readers=1,
                truth_written=False)
