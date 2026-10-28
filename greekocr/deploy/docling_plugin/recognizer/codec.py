"""Compatibility pointer; maintained codec/scorer is greekocr.train.cer."""
import sys
from greekocr.train import cer as _implementation
sys.modules[__name__] = _implementation
