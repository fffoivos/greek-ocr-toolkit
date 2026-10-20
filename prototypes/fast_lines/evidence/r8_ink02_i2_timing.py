"""Fixed both-order development clocks with no audit/render instrumentation."""
import argparse,json
from pathlib import Path
from . import r8_ink02 as runner
from .r8_ink02_i2 import O,I
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
 runner.OUT=O
 runner.load=lambda:json.loads((I/'INK02_COHORT.json').read_text())
 runner.timing(a.baseline)
