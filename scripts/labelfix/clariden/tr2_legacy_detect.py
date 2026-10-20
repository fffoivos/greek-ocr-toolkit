"""Invoke byte-frozen L1 S6 code in a separate interpreter; no model changes."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'legacy_l1'))
import argparse
from scripts.labelfix.clariden.l1_detect import run
if __name__=='__main__':
 ap=argparse.ArgumentParser()
 for k in ('selection','alignments','out','crop-root'):ap.add_argument('--'+k,type=Path,required=True)
 ap.add_argument('--workers',type=int,required=True);a=ap.parse_args()
 run(a.selection,[a.alignments],a.out,a.crop_root,'e3',workers=a.workers)
