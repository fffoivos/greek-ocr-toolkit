"""Pinned Kalchas native registry with preserved MPS-to-CPU loading workaround."""
from greekocr.types import Record, Reader
__all__ = ['load_kalchas']

def load_kalchas(spec: Record) -> Reader:
    from greekocr._vendor.bench.e2_teachers import Kalchas, validate_files
    validate_files(spec)
    return Kalchas(spec)
