"""Compatibility pointer to greekocr.train.detector_common; no trainer implementation here."""
import sys
from greekocr.train import detector_common as _implementation
sys.modules[__name__] = _implementation
