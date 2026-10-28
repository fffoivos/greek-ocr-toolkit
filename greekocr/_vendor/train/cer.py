"""Compatibility pointer to greekocr.train.cer; no trainer implementation here."""
import sys
from greekocr.train import cer as _implementation
sys.modules[__name__] = _implementation
