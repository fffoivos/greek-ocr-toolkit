"""Test only: real S1 training/CTC with stochastic toy model."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import mock_worker
from stage_c import lane
p=argparse.ArgumentParser()
p.add_argument('--config'); p.add_argument('--out')
a=p.parse_args()
raise SystemExit(lane(a.config,a.out,fixture=True))
