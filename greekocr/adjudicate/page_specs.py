"""Versioned data specs for the four historical R2 owner-page builders."""
from __future__ import annotations
import json
from pathlib import Path
from .owner_sheet import render

__all__ = ['load_spec', 'render_spec']


def load_spec(path: str | Path) -> dict:
    """Read JSON owner-sheet data; source builders are never imported or executed."""
    spec = json.loads(Path(path).read_text())
    if not isinstance(spec.get('title'),str) or not isinstance(spec.get('lines'),list):
        raise ValueError('owner spec requires title and lines')
    if not all(isinstance(c,dict) and isinstance(c.get('line_id'),str) for c in spec['lines']):
        raise ValueError('owner cards require line_id')
    return spec


def render_spec(path: str | Path) -> str:
    """Render staged JSON data through the shared owner_sheet renderer."""
    spec = load_spec(path)
    return render(spec['lines'],spec)
