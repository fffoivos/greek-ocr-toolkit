"""Offline N1 fitting exclusions, loaded from the original lock filenames.

The sourcing lead chooses which evaluation draw to register. The reserved-line
list protects every line of the reserved documents for either draw.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Locks:
    locked_line_ids: frozenset[str]
    reserved_line_ids: frozenset[str]
    reserved_docs: frozenset[str]

    def is_locked_line(self, id: str) -> bool:
        return id in self.locked_line_ids

    def is_reserved_line(self, id: str) -> bool:
        return id in self.reserved_line_ids

    def assert_fit_rows(self, ids: Iterable[str]) -> None:
        """Reject a batch before reading fitting data, including unselected lines."""
        forbidden = sorted(self.reserved_line_ids.intersection(ids))
        if forbidden:
            raise ValueError(
                f'N1 fitting contains {len(forbidden)} reserved line(s): '
                + ', '.join(forbidden)
            )


def _load_ids(path: Path) -> frozenset[str]:
    rows = path.read_text(encoding='utf-8').splitlines()
    if not rows or any(not row or row != row.strip() or any(c.isspace() for c in row)
                       for row in rows):
        raise ValueError(f'Empty or malformed N1 lock file: {path}')
    if len(rows) != len(set(rows)):
        raise ValueError(f'Duplicate entries in N1 lock file: {path}')
    return frozenset(rows)


def load_locks(dir: str | Path) -> Locks:
    """Load all three files; missing or inconsistent exclusions fail closed."""
    root = Path(dir)
    locked = _load_ids(root / 'n1_locked_eval_line_ids.txt')
    reserved = _load_ids(root / 'n1_reserved_doc_line_ids.txt')
    docs = _load_ids(root / 'n1_reserved_docs.txt')
    if any(':' not in doc or not all(doc.split(':', 1)) for doc in docs):
        raise ValueError('Reserved documents must use source:item identity')
    if not locked <= reserved:
        raise ValueError('Every locked evaluation line must be reserved from fitting')
    return Locks(locked, reserved, docs)
