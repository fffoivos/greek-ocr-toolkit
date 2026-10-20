"""Compatibility import; implementation lives in greekocr.pages.font."""
import sys
from greekocr.pages import font as _implementation

sys.modules[__name__] = _implementation
