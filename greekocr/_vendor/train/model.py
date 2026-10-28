"""Compatibility pointer to greekocr.train.model; no trainer implementation here."""
import sys
from greekocr.train import model as _implementation
sys.modules[__name__] = _implementation
