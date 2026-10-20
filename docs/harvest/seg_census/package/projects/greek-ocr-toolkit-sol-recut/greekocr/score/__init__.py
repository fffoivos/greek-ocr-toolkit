"""Separate strict atom evaluation from the bake-off's canonical NFD inputs."""
from __future__ import annotations
from typing import Sequence
from greekocr.types import PathLike, Record
from greekocr._vendor.train.cer import levenshtein as _edits, cer_line as _cer
from greekocr._vendor.bench.e2_bakeoff import score as _score
from greekocr._vendor.bench.e1_readout import clean_row, summarize, readout as _readout
__all__ = ['strict_cer', 'edit_distance', 'score_readings', 'summarize_predictions', 'write_readout']

def strict_cer(reference: str, prediction: str) -> float:
    """Score codepoints as supplied; predictions are never renormalized."""
    return _cer(reference, prediction)


def edit_distance(reference: str, prediction: str) -> int:
    return _edits(reference, prediction)


def score_readings(readings: Sequence[Record]) -> Record:
    """Bake-off NFD decomposition of both inputs, with marks and homoglyphs."""
    return _score(readings)


def summarize_predictions(rows: Sequence[Record]) -> Record:
    """Strict E1 readout, including overlapping diagnostic by_category strata."""
    return summarize([clean_row(r) for r in rows])


def write_readout(predictions: Sequence[PathLike], out: PathLike, *, require_complete: bool = False,
                  transfer_enabled: bool | None = None, title: str = 'E1') -> Record:
    return _readout(predictions, out, require_complete=require_complete, transfer_enabled=transfer_enabled, title=title)
