"""Compatibility pointer to greekocr.train.data; no trainer implementation here."""
import sys
from greekocr.train import data as _implementation
sys.modules[__name__] = _implementation
