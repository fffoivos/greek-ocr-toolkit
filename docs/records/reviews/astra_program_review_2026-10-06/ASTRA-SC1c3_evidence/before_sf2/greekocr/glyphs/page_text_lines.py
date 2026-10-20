"""Compatibility import; implementation lives in greekocr.pages.lines."""
import sys
from greekocr.pages import lines as _implementation

sys.modules[__name__] = _implementation
