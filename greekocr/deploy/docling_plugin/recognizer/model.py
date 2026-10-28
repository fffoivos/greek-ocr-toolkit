"""Compatibility pointer; maintained model is greekocr.train.model."""
import sys
from greekocr.train import model as _implementation
sys.modules[__name__] = _implementation
