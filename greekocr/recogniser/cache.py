"""Strict crop identity and record-normalized first-run/replay results."""
from __future__ import annotations
from collections.abc import Iterable
from typing import TYPE_CHECKING

import json
from pathlib import Path
from scripts.labelfix.clariden.c1_common import crop_key
from .alignment import Alignment, align

if TYPE_CHECKING:
    from .api import Recogniser

__all__ = ['AlignmentCache']


class AlignmentCache:
    def __init__(self, path: str | Path, recogniser: Recogniser) -> None:
        self.path = Path(path)
        self.recogniser = recogniser
        self.records = {}
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                r = json.loads(line)
                key = crop_key(r['crop'])
                if key in self.records:
                    raise ValueError(f'duplicate crop key: {key}')
                self.records[key] = r

    def get(self, crops: Iterable[str | Path], *, bs: int = 16) -> dict[str, Alignment]:
        crops = list(crops)
        keys = [crop_key(p) for p in crops]
        missing = dict((k, p) for k, p in zip(keys, crops) if k not in self.records)
        if missing:
            readings = self.recogniser.read(missing.values(), profile='labelfix', bs=bs)
            if len(readings) != len(missing):
                raise ValueError('recogniser result count mismatch')
            records = [dict(crop=k, alignment=align(r).to_record(), provenance=r.provenance)
                       for k, r in zip(missing, readings)]
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('a') as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False)+'\n')
                    self.records[r['crop']] = r
        return {k: Alignment.from_record(self.records[k]['alignment']) for k in keys}
