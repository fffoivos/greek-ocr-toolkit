"""Compatibility import; implementation lives in greekocr.pages.structure."""
import sys
from greekocr.pages import structure as _implementation

sys.modules[__name__] = _implementation
