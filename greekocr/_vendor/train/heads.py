"""Compatibility pointer to greekocr.train.heads; no trainer implementation here."""
import sys
from greekocr.train import heads as _implementation
sys.modules[__name__] = _implementation
