"""Compatibility import; implementation lives in greekocr.pages.pixels."""
import sys
from greekocr.pages import pixels as _implementation

sys.modules[__name__] = _implementation
