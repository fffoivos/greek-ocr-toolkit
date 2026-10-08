"""Explicit service hooks; cloud dependencies are loaded only when called."""
from greekocr.types import Record, Reader

__all__ = ['load_service']


def load_service(name: str, spec: Record, *, enabled: bool = False) -> Reader:
    from greekocr._vendor.bench.e2_teachers import reader
    return reader(dict(spec, kind='service', service=name), service=enabled)
