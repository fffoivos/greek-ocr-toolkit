"""Compatibility pointer to greekocr.train.ckpt_io; no trainer implementation here."""
import sys
from greekocr.train import ckpt_io as _implementation
sys.modules[__name__] = _implementation
