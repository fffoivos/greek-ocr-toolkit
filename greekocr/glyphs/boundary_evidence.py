"""Compatibility import; implementation lives in greekocr.pages.boundaries."""
import sys
from greekocr.pages import boundaries as _implementation

sys.modules[__name__] = _implementation
