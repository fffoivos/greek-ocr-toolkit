"""Local F2 path adapter for the copied, hash-identical P1 processing routines."""
from f2lib import BASE,ROOT,sha,write,append,rows
import pathlib,time,json,hashlib
MAIN=ROOT.parent/'greek-ocr-toolkit'
LONG_SIDE=3500
