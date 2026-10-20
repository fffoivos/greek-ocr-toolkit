"""Independent crop readings preserve rejections and record failures."""
from __future__ import annotations
from typing import Iterable, Sequence
from pathlib import Path
from greekocr.types import CropReader, PathLike, Record
from greekocr._vendor.bench.o4b_adjudicate import adjudicate as _adjudicate, run as _run
__all__ = ['adjudicate_lines', 'adjudicate_file']

def adjudicate_lines(rows: Iterable[Record], reader: CropReader, teacher: CropReader | None,
                     *, supported: Sequence[str] = ('greek_poly', 'greek_mono'),
                     teacher_binding: Record | None = None) -> list[Record]:
    return list(_adjudicate(rows, reader, teacher, supported, teacher_binding))


def adjudicate_file(records: PathLike, out: PathLike, reader: CropReader, teacher: CropReader | None,
                    *, supported: Sequence[str] = ('greek_poly', 'greek_mono'),
                    teacher_binding: Record | None = None, reader_binding: Record | None = None) -> Record:
    return _run(Path(records), Path(out), reader, teacher, supported, teacher_binding, reader_binding)
