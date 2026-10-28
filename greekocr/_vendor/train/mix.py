"""Compatibility pointer to greekocr.train.mix; no trainer implementation here."""
import sys
from greekocr.train import mix as _implementation
if __name__ == "__main__":
    raise SystemExit(_implementation.main())
sys.modules[__name__] = _implementation
