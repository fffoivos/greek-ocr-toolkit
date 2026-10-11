#!/usr/bin/env python3
"""Tiny T10 CLI; run from any directory with the toolkit environment."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prototypes.harvest.google_failed_lines import main
if __name__ == '__main__':
    raise SystemExit(main())
