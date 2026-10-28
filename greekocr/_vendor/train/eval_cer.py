"""Compatibility pointer to greekocr.train.eval_cer; no trainer implementation here."""
import sys
from greekocr.train import eval_cer as _implementation
if __name__ == "__main__":
    raise SystemExit(_implementation.main())
sys.modules[__name__] = _implementation
