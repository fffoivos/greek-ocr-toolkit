#!/usr/bin/env python3
"""Run all tests with a process-wide audit denying filesystem writes outside bench02."""
import os
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parent
checked=0

def inside(path):
    global checked
    if isinstance(path,int) or path is None:return
    p=Path(os.fsdecode(path)).resolve()
    if not p.is_relative_to(ROOT):raise RuntimeError('audit rejected write outside bench02: '+str(p))
    checked+=1

def audit(event,args):
    if event=='open':
        path,mode,flags=args
        if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC):inside(path)
    elif event=='sqlite3.connect':inside(args[0])
    elif event=='os.mkdir':inside(args[0])

sys.addaudithook(audit)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT),pattern='test_*.py'))
print(f'Filesystem audit: {checked} write operations checked; outside writes: 0')
sys.exit(not result.wasSuccessful())
