"""Compatibility import; implementation lives in greekocr.pages.tables."""
import sys
from greekocr.pages import tables as _implementation

sys.modules[__name__] = _implementation
