"""Compatibility import; implementation lives in greekocr.pages.statistics."""
import sys
from greekocr.pages import statistics as _implementation

sys.modules[__name__] = _implementation
