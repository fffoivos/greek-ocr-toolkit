"""Explicit switches for page analysis and optional artifact writing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

__all__ = ['PageOptions', 'OutputOptions']

OutputName = Literal['lines', 'segments', 'structure', 'cells', 'delivery', 'rows', 'checks',
                     'statistics', 'lines_image', 'unrolled_image', 'structure_image',
                     'glyphs_image', 'book_image', 'orientation']
OUTPUT_NAMES = frozenset(OutputName.__args__)
GEOMETRY_OUTPUTS = frozenset({'lines', 'segments', 'structure', 'cells', 'checks'})


@dataclass(frozen=True)
class OutputOptions:
    """Files to write; no directory means an in-memory call with no file writes."""

    directory: Path | str | None = None
    files: frozenset[OutputName] = GEOMETRY_OUTPUTS

    def __post_init__(self) -> None:
        object.__setattr__(self, 'files', frozenset(self.files))
        unknown = self.files - OUTPUT_NAMES
        if unknown:
            raise ValueError(f'Unknown page outputs: {sorted(unknown)}')
        if self.directory is not None:
            object.__setattr__(self, 'directory', Path(self.directory))


@dataclass(frozen=True)
class PageOptions:
    """Pipeline switches; defaults preserve ordinary Q2 page delivery."""

    tables: bool = False
    orientation: bool = False
    join_lines: bool = False
    granularity: Literal['default', 'rows', 'pieces'] = 'default'
    statistics: bool = False
    discounted: Literal['keep', 'drop'] = 'keep'
    strict_geometry: bool = False
    outputs: OutputOptions = OutputOptions()

    def __post_init__(self) -> None:
        if self.granularity not in ('default', 'rows', 'pieces'):
            raise ValueError('granularity must be default, rows or pieces')
        if self.discounted not in ('keep', 'drop'):
            raise ValueError('discounted must be keep or drop')
        if not self.join_lines and self.granularity != 'default':
            raise ValueError('Set join_lines=True when choosing a granularity')
        if self.outputs.directory is not None:
            if 'rows' in self.outputs.files and (not self.join_lines or self.granularity != 'rows'):
                raise ValueError('The rows file requires join_lines=True and granularity="rows"')
            if not self.statistics and self.outputs.files & {'statistics', 'glyphs_image', 'book_image'}:
                raise ValueError('Statistics outputs require statistics=True')
            if not self.orientation and 'orientation' in self.outputs.files:
                raise ValueError('Orientation output requires orientation=True')
