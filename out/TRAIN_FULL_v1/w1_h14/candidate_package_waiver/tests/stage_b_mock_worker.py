"""Offline only: substitute the stochastic toy model, retain S1 training/CTC."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mock_worker  # installs the existing toy model; production CLI never imports this
from stage_b_trial import lane

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--trial', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    raise SystemExit(lane(a.trial, a.out, fixture=True))
