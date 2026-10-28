"""Compatibility pointer to greekocr.train.ctc_health; no trainer implementation here."""
import sys
from greekocr.train import ctc_health as _implementation
sys.modules[__name__] = _implementation
