"""Render the checked-in data spec with the standard owner-sheet renderer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.review.owner_sheets import build
if __name__=='__main__': print(build('failure_modes_per_class'))
