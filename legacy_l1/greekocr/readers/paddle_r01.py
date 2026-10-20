"""Offline, pinned upstream native-framework references; node runtimes are separate."""
from greekocr.types import Record, NativeReference
__all__ = ['load_paddle_r01', 'load_r03']

def load_paddle_r01(spec: Record) -> NativeReference:
    from greekocr._vendor.bench.e2_native import r01_paddle
    return r01_paddle(spec)


def load_r03(spec: Record) -> NativeReference:
    from greekocr._vendor.bench.e2_native import r03_openocr
    return r03_openocr(spec)
